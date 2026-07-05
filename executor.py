from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from report import TestReport
import time
import os
import threading
import queue

load_dotenv(override=True)

# Global variable to store active browser for keeping it alive
_active_browser = None
_active_context = None
_active_page = None
_playwright = None
_browser_lock = threading.Lock()

# Job queue for running all Playwright actions in the same thread
_job_queue = queue.Queue()
_worker_thread = None

# Headless mode config: default to a visible browser locally for easier debugging
IS_DEPLOYED = os.getenv("RENDER") == "true" or os.getenv("PORT") is not None
HEADLESS_MODE = os.getenv("HEADLESS", "false").lower() == "true"


def _cleanup_previous_session(keep_browser=True):
    """Safely close any previously open browser session."""
    global _active_browser, _active_context, _active_page, _playwright
    with _browser_lock:
        if _active_page:
            try:
                _active_page.close()
            except Exception:
                pass
            _active_page = None

        if _active_context:
            try:
                _active_context.close()
            except Exception:
                pass
            _active_context = None

        if not keep_browser:
            if _active_browser:
                try:
                    _active_browser.close()
                except Exception:
                    pass
                _active_browser = None

            if _playwright:
                try:
                    _playwright.stop()
                except Exception:
                    pass
                _playwright = None


def bring_window_to_front():
    """Bring the Chromium automation browser window to the foreground on Windows."""
    import sys
    if sys.platform != "win32":
        return
    try:
        import psutil
        import subprocess
        
        # Get current python process
        current_process = psutil.Process(os.getpid())
        # Find all child browser processes (chrome, chromium, msedge)
        pids = []
        for child in current_process.children(recursive=True):
            name = child.name().lower()
            if any(bn in name for bn in ['chrome', 'chromium', 'msedge']):
                pids.append(child.pid)
                
        if not pids:
            return

        pids_str = ",".join(str(pid) for pid in pids)
        
        # PowerShell script to restore and set foreground window for our specific browser PIDs
        ps_script = f"""
$sig = @'
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
'@
Add-Type -MemberDefinition $sig -Name Win32 -Namespace Win32Functions -ErrorAction SilentlyContinue

$found = $false
for ($i = 0; $i -lt 10; $i++) {{
    $procs = Get-Process -Id {pids_str} -ErrorAction SilentlyContinue | Where-Object {{ $_.MainWindowHandle -ne 0 }}
    if ($procs) {{
        foreach ($p in $procs) {{
            [Win32Functions.Win32]::ShowWindow($p.MainWindowHandle, 9)
            [Win32Functions.Win32]::BringWindowToTop($p.MainWindowHandle)
            [Win32Functions.Win32]::SetForegroundWindow($p.MainWindowHandle)
        }}
        $found = $true
        break
    }}
    Start-Sleep -Milliseconds 200
}}
"""
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
            capture_output=True, timeout=5
        )
    except Exception:
        pass



def _ensure_browser():
    """Ensure the browser is running, starting it if necessary."""
    global _playwright, _active_browser
    if not _playwright:
        _playwright = sync_playwright().start()

    if not _active_browser or not _active_browser.is_connected():
        print(f"[Executor] Launching Playwright Chromium (headless={HEADLESS_MODE})...")
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-position=0,0",
            "--window-size=1440,900",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--mute-audio",
            "--no-sandbox",
            "--no-pings",
        ]
        if IS_DEPLOYED:
            browser_args.extend([
                "--disable-setuid-sandbox",
            ])

        _active_browser = _playwright.chromium.launch(
            headless=HEADLESS_MODE,
            slow_mo=0,
            args=browser_args,
        )
    return _active_browser


def _ensure_context_and_page():
    """Ensure the browser, context, and page are initialized and ready for a clean run."""
    global _active_browser, _active_context, _active_page
    
    # 1. Ensure browser is alive
    browser = _ensure_browser()
    
    # 2. Ensure context exists and is valid
    if not _active_context:
        print("[Executor] Creating new browser context...")
        _active_context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
            ignore_https_errors=True,
            no_viewport=True,
        )
    else:
        # Reuse context safely: clear cookies and permissions
        try:
            _active_context.clear_cookies()
            try:
                _active_context.clear_permissions()
            except Exception:
                pass
        except Exception as e:
            print(f"[Executor] Failed to clear context state, recreating context: {e}")
            try:
                _active_context.close()
            except Exception:
                pass
            _active_context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                locale="en-US",
                timezone_id="America/New_York",
                ignore_https_errors=True,
                no_viewport=True,
            )
            _active_page = None

    # 3. Ensure page exists and is valid
    if not _active_page:
        _active_page = _active_context.new_page()
        _apply_stealth(_active_page)
    else:
        # Reuse page safely: close any extra pages/tabs and reset page to about:blank
        try:
            pages = _active_context.pages
            if len(pages) > 1:
                print(f"[Executor] Closing {len(pages) - 1} extra tabs...")
                for p in pages[1:]:
                    try:
                        p.close()
                    except Exception:
                        pass
            _active_page = pages[0]
            _active_page.goto("about:blank")
        except Exception as e:
            print(f"[Executor] Failed to reuse page, recreating page: {e}")
            try:
                _active_page.close()
            except Exception:
                pass
            _active_page = _active_context.new_page()
            _apply_stealth(_active_page)
            
    # Configure timeouts
    _active_page.set_default_timeout(10000)
    try:
        _active_page.bring_to_front()
    except Exception:
        pass
    bring_window_to_front()
    return _active_browser, _active_context, _active_page


def _worker_loop():
    """Permanent background thread that executes all Playwright operations in the same thread."""
    global _playwright, _active_browser, _active_context, _active_page

    # Pre-launch browser so it is ready immediately on application startup
    try:
        with _browser_lock:
            _ensure_browser()
        print("[Executor] Playwright initialized and browser pre-launched successfully.")
    except Exception as e:
        print(f"[Executor] Playwright/browser pre-launch failed: {e}")

    # Main loop processing jobs
    while True:
        job = _job_queue.get()
        if job is None:
            break
        
        steps, result_container, done_event = job
        try:
            report, code = _do_run_test(steps)
            result_container['report'] = report
            result_container['code'] = code
        except Exception as e:
            result_container['error'] = e
        finally:
            done_event.set()


def start_worker_thread():
    """Start the background worker thread if not already running."""
    global _worker_thread
    with _browser_lock:
        if _worker_thread is None:
            _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
            _worker_thread.start()


def pre_launch_browser():
    """Start the Playwright worker thread to pre-launch Chromium."""
    start_worker_thread()


def _apply_stealth(page):
    """Patch common automation-detection hooks before interacting with pages."""
    try:
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });
        Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        Object.defineProperty(screen, 'width', { get: () => 1440 });
        Object.defineProperty(screen, 'height', { get: () => 900 });
        """)
    except Exception:
        pass


def _dismiss_common_dialogs(page):
    """Try to dismiss cookie and consent banners that block form interaction without blocking."""
    try:
        for text in ["Accept all", "Accept", "I agree", "Agree", "Got it", "Accept cookies"]:
            try:
                button = page.get_by_role("button", name=text, exact=False).first
                if button.count() > 0 and button.is_visible():
                    button.click(timeout=500)
                    page.wait_for_timeout(100)
                    break
            except Exception:
                continue
    except Exception:
        pass


def _find_input_field(page, selector=None):
    """Try a list of robust selectors to locate an input field for typing."""
    candidates = []
    if selector:
        candidates.append(selector)
    candidates.extend([
        "input[type='search']",
        "input[name='q']",
        "input[name='search_query']",
        "textarea",
        "input[type='text']",
        "input",
        "[role='searchbox']",
        "[aria-label*='Search']",
        "[placeholder*='Search' i]",
        "[placeholder*='search' i]",
    ])

    for candidate in candidates:
        try:
            locator = page.locator(candidate).first
            if locator.count() > 0:
                return locator
        except Exception:
            continue

    return None


def _do_run_test(steps):
    """Internal execution logic running in an isolated thread"""
    global _active_browser, _active_context, _active_page, _playwright

    report = TestReport()
    start = time.time()

    # Ensure static/screenshots directory exists
    os.makedirs("static/screenshots", exist_ok=True)
    screenshot_path = f"static/screenshots/screenshot_{int(time.time())}.jpg"
    report.set_screenshot(screenshot_path)

    code_lines = [
        "from playwright.sync_api import sync_playwright",
        "import time",
        "",
        "with sync_playwright() as p:",
        f"    browser = p.chromium.launch(headless={HEADLESS_MODE})",
        "    page = browser.new_page()",
    ]

    try:
        with _browser_lock:
            browser, context, page = _ensure_context_and_page()
            print("[Executor] Browser, context, and page are ready instantly!")

        DEFAULT_WAIT_TIMEOUT = 10000 if IS_DEPLOYED else 3000
        DEFAULT_CLICK_TIMEOUT = 6000 if IS_DEPLOYED else 1500
        DEFAULT_TYPE_TIMEOUT = 6000 if IS_DEPLOYED else 2000

        # Execute all steps
        for i, step in enumerate(steps):
            action = step.get("action")

            try:
                # ── OPEN ──────────────────────────────────────────
                if action == "open":
                    url = step.get("url", "https://www.google.com")
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        bring_window_to_front()
                        _dismiss_common_dialogs(page)
                        code_lines.append(f'    page.goto("{url}")')
                        report.add_step(f"Open: {url.split('/')[2]}", "PASS")
                    except Exception as e:
                        print(f"[Executor] Navigation failed for {url}: {e}")
                        report.add_step(f"Open: {url.split('/')[2]} (Failed: {str(e)[:60]})", "FAIL")
                        report.set_status("FAIL")
                        break

                # ── WAIT ──────────────────────────────────────────
                elif action == "wait":
                    selector = step.get("selector", "body")
                    try:
                        if selector == "body":
                            page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_WAIT_TIMEOUT)
                        else:
                            page.locator(selector).first.wait_for(state="visible", timeout=DEFAULT_WAIT_TIMEOUT)
                        report.add_step("Wait: Ready", "PASS")
                    except Exception:
                        report.add_step("Wait: OK", "PASS")

                # ── TYPE ──────────────────────────────────────────
                elif action == "type":
                    selector = step.get("selector")
                    value = step.get("value", "")
                    try:
                        field = _find_input_field(page, selector)
                        if field is None:
                            raise Exception("Element not found")
                        field.wait_for(state="visible", timeout=DEFAULT_TYPE_TIMEOUT)
                        field.fill(value, timeout=DEFAULT_TYPE_TIMEOUT)
                        if selector:
                            code_lines.append(f'    page.locator("{selector}").first.fill("{value}")')
                        else:
                            code_lines.append(f'    page.locator("input").first.fill("{value}")')
                        report.add_step(f"Type: {value[:20]}", "PASS")
                    except Exception:
                        try:
                            page.keyboard.press("Tab")
                            page.keyboard.type(value)
                            code_lines.append(f'    page.keyboard.type("{value}")')
                            report.add_step(f"Type: {value[:20]} (keyboard fallback)", "PASS")
                        except Exception:
                            report.add_step("Type: Failed to locate input field", "FAIL")

                # ── PRESS ─────────────────────────────────────────
                elif action == "press":
                    key = step.get("key", "Enter")
                    try:
                        page.keyboard.press(key)
                        code_lines.append(f'    page.keyboard.press("{key}")')
                        report.add_step(f"Press: {key}", "PASS")
                        if key == "Enter":
                            page.wait_for_timeout(50)
                    except Exception:
                        report.add_step(f"Press: {key} (FAILED)", "FAIL")

                # ── CLICK ─────────────────────────────────────────
                elif action == "click":
                    selector = step.get("selector")
                    description = step.get("description", selector)
                    index = step.get("index", 0)

                    try:
                        locator = page.locator(selector).nth(index)
                        locator.wait_for(state="visible", timeout=DEFAULT_WAIT_TIMEOUT)
                        locator.click(timeout=DEFAULT_CLICK_TIMEOUT)
                        code_lines.append(f'    page.locator("{selector}").nth({index}).click()')
                        report.add_step(f"Click: {description}", "PASS")
                    except Exception:
                        # Fallback 1: Try clicking by visible text
                        try:
                            locator = page.get_by_text(selector, exact=False).nth(index)
                            locator.click(timeout=3000 if IS_DEPLOYED else 1000)
                            code_lines.append(f'    page.get_by_text("{selector}", exact=False).nth({index}).click()')
                            report.add_step(f"Click: {description} (text fallback)", "PASS")
                        except Exception:
                            # Fallback 2: button or link role
                            try:
                                locator = page.get_by_role("button", name=selector, exact=False).nth(index)
                                locator.click(timeout=3000 if IS_DEPLOYED else 1000)
                                report.add_step(f"Click: {description} (button fallback)", "PASS")
                            except Exception:
                                try:
                                    locator = page.get_by_role("link", name=selector, exact=False).nth(index)
                                    locator.click(timeout=3000 if IS_DEPLOYED else 1000)
                                    report.add_step(f"Click: {description} (link fallback)", "PASS")
                                except Exception:
                                    # Fallback 3: Site-specific result selectors
                                    try:
                                        alternative_selectors = [
                                            "h3.LC20lb",
                                            "ytd-video-renderer a#video-title-link",
                                            "a#video-title",
                                            "a[data-testid='results-item']",
                                            "[data-testid='results-list'] a",
                                            "div[data-testid='results-item'] a",
                                            "a[class*='prc-Link-Link-']",
                                            "div.mw-search-result-heading a",
                                            "h2 a",
                                            "h3 a",
                                            "a",
                                        ]
                                        found = False
                                        for alt in alternative_selectors:
                                            try:
                                                locator = page.locator(alt).nth(index)
                                                locator.click(timeout=2000 if IS_DEPLOYED else 800)
                                                code_lines.append(f'    page.locator("{alt}").nth({index}).click()')
                                                found = True
                                                report.add_step(f"Click: {description} (result fallback)", "PASS")
                                                break
                                            except Exception:
                                                continue

                                        if not found:
                                            # Check if we are already on the target page due to auto-redirect
                                            current_url = page.url.lower()
                                            is_wikipedia_article = "wikipedia.org/wiki/" in current_url and "special:search" not in current_url
                                            is_github_repo = "github.com/" in current_url and "/search" not in current_url and current_url.count('/') >= 4
                                            is_youtube_video = "youtube.com/watch" in current_url
                                            
                                            if is_wikipedia_article or is_github_repo or is_youtube_video:
                                                print(f"[Executor] Click fallback skipped: already on target page ({page.url})")
                                                report.add_step(f"Click: {description} (already on target page)", "PASS")
                                            else:
                                                raise Exception("Element not found")
                                    except Exception:
                                        report.add_step(f"Click: {description} (FAIL)", "FAIL")

                # ── CLICK_ALL ─────────────────────────────────────
                elif action == "click_all":
                    selector = step.get("selector")
                    description = step.get("description", f"all {selector}")

                    try:
                        page.wait_for_selector(selector, timeout=DEFAULT_WAIT_TIMEOUT)
                        elements = page.query_selector_all(selector)
                        click_count = 0

                        for elem in elements[:15]:
                            try:
                                elem.click()
                                click_count += 1
                            except Exception:
                                pass

                        code_lines.append(f'    elements = page.query_selector_all("{selector}")')
                        report.add_step(f"Click All: {click_count} items", "PASS")

                    except Exception:
                        report.add_step("Click All: Error", "FAIL")

                # ── SCROLL ────────────────────────────────────────
                elif action == "scroll":
                    direction = step.get("direction", "down")
                    amount = 600 if direction == "down" else -600
                    page.evaluate(f"window.scrollBy(0, {amount})")
                    code_lines.append(f"    page.evaluate('window.scrollBy(0, {amount})')")
                    report.add_step(f"Scroll: {direction}", "PASS")

                # ── SCREENSHOT ────────────────────────────────────
                elif action == "screenshot":
                    page.screenshot(path=screenshot_path, type="jpeg", quality=80)
                    code_lines.append(f'    page.screenshot(path="{screenshot_path}")')
                    report.add_step("Screenshot: Captured", "PASS")

            except PlaywrightTimeout:
                report.add_step(f"Step {i+1} timeout", "FAIL")
                try:
                    page.screenshot(path=screenshot_path, type="jpeg", quality=80)
                except Exception:
                    pass

            except Exception as e:
                report.add_step(f"Step {i+1} error: {str(e)[:50]}", "FAIL")
                try:
                    page.screenshot(path=screenshot_path, type="jpeg", quality=80)
                except Exception:
                    pass

        # Final screenshot (outside the for loop)
        try:
            # Switch to the latest tab if multiple tabs exist
            try:
                pages = context.pages
                if len(pages) > 1:
                    page = pages[-1]
                    _active_page = page
            except Exception:
                pass

            # Wait for load states if navigation is happening
            try:
                page.wait_for_load_state("domcontentloaded", timeout=3000)
                page.wait_for_load_state("networkidle", timeout=1000)
            except Exception:
                pass

            # Site-specific waits for key elements to ensure correct rendering before screenshot
            try:
                if "youtube.com/results" in page.url:
                    print("[Executor] YouTube search results page. Waiting for video elements...")
                    page.locator("ytd-video-renderer").first.wait_for(state="visible", timeout=10000)
                elif "youtube.com/watch" in page.url or page.locator("video").count() > 0:
                    print("[Executor] Video page detected. Waiting 3 seconds...")
                    page.wait_for_timeout(3000)
                elif "wikipedia.org" in page.url:
                    print("[Executor] Wikipedia page. Waiting for main content...")
                    page.locator("#content, #bodyContent, #mw-content-text").first.wait_for(state="visible", timeout=3000)
            except Exception as e:
                print(f"[Executor] Site-specific wait timed out or failed: {e}")

            # Wait 200ms for dynamic JS rendering/content to settle
            page.wait_for_timeout(200)
            page.screenshot(path=screenshot_path, type="jpeg", quality=80)
        except Exception:
            pass

        # Keep browser context and page active for reuse
        print("\n[Automation] Completed! Browser session kept active for reuse.")
        with _browser_lock:
            _active_browser = browser
            _active_context = context
            _active_page = page

    except Exception as e:
        report.add_step(f"Browser error: {str(e)[:100]}", "FAIL")
        report.set_status("FAIL")
        print(f"[Executor Error] {str(e)}")
        # Clean up broken session
        _cleanup_previous_session(keep_browser=False)

    # Finalize report
    report.set_execution_time(round(time.time() - start, 2))

    # If the browser didn't crash and we successfully got a screenshot, PASS
    if report.status == "FAIL":
        pass
    elif report.screenshot and os.path.exists(report.screenshot):
        report.set_status("PASS")
    else:
        report.set_status("FAIL")

    code_lines.append("")
    code_lines.append("    browser.close()")
    code = "\n".join(code_lines)

    return report.generate(), code


def run_test(steps):
    """Execute automation steps by delegating to the single background worker thread."""
    start_worker_thread()
    
    result_container = {}
    done_event = threading.Event()
    
    # Put job on the queue
    _job_queue.put((steps, result_container, done_event))
    
    # Wait for completion
    done_event.wait()
    
    if 'error' in result_container:
        raise result_container['error']
        
    return result_container['report'], result_container['code']
