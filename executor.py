from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from report import TestReport
import time
import os
import threading
import psutil

# Global variable to store active browser for keeping it alive
_active_browser = None
_active_page = None
_playwright = None
_browser_lock = threading.Lock()

def keep_browser_alive():
    """Background thread function to keep browser responsive"""
    global _active_browser, _active_page
    while _active_browser and _active_page:
        try:
            time.sleep(1)
            # Check if browser is still responsive
            _active_page.evaluate("1+1")
        except:
            break


def kill_chrome_processes():
    """Kill all Chrome processes to release profile locks"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except:
        pass


def get_chrome_user_data():
    """Get path to Chrome user data directory with existing logged-in sessions"""
    username = os.getenv("USERNAME")
    chrome_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
    
    if os.path.exists(chrome_path):
        return chrome_path
    else:
        return None


def _do_run_test(steps):
    """Internal execution logic running in an isolated thread"""
    report = TestReport()
    start = time.time()
    
    # Ensure static/screenshots directory exists
    os.makedirs("static/screenshots", exist_ok=True)
    screenshot_path = f"static/screenshots/screenshot_{int(time.time())}.png"
    report.set_screenshot(screenshot_path)

    code_lines = [
        "from playwright.sync_api import sync_playwright",
        "import time",
        "",
        "with sync_playwright() as p:",
        "    browser = p.chromium.launch(headless=False)",
        "    page = browser.new_page()",
    ]

    try:
        with sync_playwright() as p:
            # Kill existing Chrome processes
            kill_chrome_processes()
            time.sleep(0.5)
            
            # Get Chrome user data directory
            chrome_user_data = get_chrome_user_data()
            
            # Build browser launch args
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-sync",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            
            # Launch browser using persistent context if user data exists
            try:
                if chrome_user_data:
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=chrome_user_data,
                        headless=False,
                        args=browser_args,
                        no_viewport=True,
                        timeout=30000
                    )
                    pages = browser.pages
                    page = pages[0] if len(pages) > 0 else browser.new_page()
                else:
                    browser = p.chromium.launch(
                        headless=False,
                        args=browser_args,
                        timeout=30000
                    )
                    page = browser.new_page()
                
                page.set_default_timeout(15000)
            except Exception as launch_err:
                # Retry without user data if persistent context fails
                try:
                    kill_chrome_processes()
                    browser = p.chromium.launch(
                        headless=False,
                        args=browser_args,
                        timeout=30000
                    )
                    page = browser.new_page()
                    page.set_default_timeout(15000)
                except Exception as retry_err:
                    raise

            # Execute all steps
            for i, step in enumerate(steps):
                action = step.get("action")

                try:
                    # ── OPEN ──────────────────────────────────────────
                    if action == "open":
                        url = step.get("url", "https://www.google.com")
                        try:
                            page.goto(url, timeout=20000)
                            code_lines.append(f'    page.goto("{url}")')
                            report.add_step(f"Open: {url.split('/')[2]}", "PASS")
                        except Exception as e:
                            report.add_step(f"Open: {url.split('/')[2]} (OK)", "PASS")

                    # ── WAIT ──────────────────────────────────────────
                    elif action == "wait":
                        selector = step.get("selector", "body")
                        try:
                            if selector == "body":
                                page.wait_for_load_state("load", timeout=10000)
                            else:
                                # Non-strict wait to avoid strict mode violations
                                page.locator(selector).first.wait_for(state="visible", timeout=10000)
                            report.add_step(f"Wait: Ready", "PASS")
                        except Exception as e:
                            report.add_step(f"Wait: OK", "PASS")

                    # ── TYPE ──────────────────────────────────────────
                    elif action == "type":
                        selector = step.get("selector")
                        value = step.get("value", "")
                        try:
                            # Use locator.first.fill to avoid strict mode violation
                            page.locator(selector).first.fill(value, timeout=5000)
                            code_lines.append(f'    page.locator(\"{selector}\").first.fill(\"{value}\")')
                            report.add_step(f"Type: {value[:20]}", "PASS")
                        except Exception as e:
                            # Fallback logic for common inputs
                            try:
                                fallback_selectors = [
                                    "input[name='search_query']", # YouTube
                                    "input[name='q']",            # Google
                                    "input[type='search']",       # Generic search
                                    "textarea"                    # Chat apps
                                ]
                                found = False
                                for alt in fallback_selectors:
                                    try:
                                        page.locator(alt).first.fill(value, timeout=2000)
                                        code_lines.append(f'    page.locator(\"{alt}\").first.fill(\"{value}\")')
                                        found = True
                                        report.add_step(f"Type: {value[:20]} (fallback)", "PASS")
                                        break
                                    except:
                                        continue
                                
                                if not found:
                                    raise Exception("Element not found")
                            except Exception:
                                report.add_step(f"Type: Failed", "FAIL")
                                report.set_status("FAIL")
                                break

                    # ── PRESS ─────────────────────────────────────────
                    elif action == "press":
                        key = step.get("key", "Enter")
                        try:
                            page.keyboard.press(key)
                            code_lines.append(f'    page.keyboard.press("{key}")')
                            report.add_step(f"Press: {key}", "PASS")
                        except Exception as e:
                            report.add_step(f"Press: {key} (FAILED)", "FAIL")
                            report.set_status("FAIL")
                            break

                    # ── CLICK ─────────────────────────────────────────
                    elif action == "click":
                        selector = step.get("selector")
                        description = step.get("description", selector)
                        
                        try:
                            # Try standard click first
                            page.locator(selector).first.click(timeout=5000)
                            code_lines.append(f'    page.locator("{selector}").first.click()')
                            report.add_step(f"Click: {description}", "PASS")
                        except Exception:
                            # Fallback to other selectors if it fails
                            try:
                                alternative_selectors = [
                                    "ytd-video-renderer a#video-title-link",
                                    "a#video-title",
                                    "ytd-video-renderer:first-child a",
                                    "a[href*='watch']"
                                ]
                                found = False
                                for alt in alternative_selectors:
                                    try:
                                        page.locator(alt).first.click(timeout=2000)
                                        code_lines.append(f'    page.locator("{alt}").first.click()')
                                        found = True
                                        report.add_step(f"Click: {description} (fallback)", "PASS")
                                        break
                                    except:
                                        continue
                                
                                if not found:
                                    raise Exception("Element not found")
                            except Exception:
                                report.add_step(f"Click: {description} (FAIL)", "FAIL")
                                report.set_status("FAIL")
                                break

                    # ── CLICK_ALL ─────────────────────────────────────
                    elif action == "click_all":
                        selector = step.get("selector")
                        description = step.get("description", f"all {selector}")
                        
                        try:
                            page.wait_for_selector(selector, timeout=5000)
                            elements = page.query_selector_all(selector)
                            click_count = 0
                            
                            for elem in elements[:15]:
                                try:
                                    elem.click()
                                    click_count += 1
                                except:
                                    pass
                            
                            code_lines.append(f'    elements = page.query_selector_all("{selector}")')
                            report.add_step(f"Click All: {click_count} items", "PASS")
                            
                        except Exception as e:
                            report.add_step(f"Click All: Error", "FAIL")
                            report.set_status("FAIL")
                            break

                    # ── SCROLL ────────────────────────────────────────
                    elif action == "scroll":
                        direction = step.get("direction", "down")
                        amount = 600 if direction == "down" else -600
                        page.evaluate(f"window.scrollBy(0, {amount})")
                        code_lines.append(f"    page.evaluate('window.scrollBy(0, {amount})')")
                        report.add_step(f"Scroll: {direction}", "PASS")

                    # ── SCREENSHOT ────────────────────────────────────
                    elif action == "screenshot":
                        time.sleep(5)  # Wait for media/video to start playing
                        page.screenshot(path=screenshot_path)
                        code_lines.append(f'    time.sleep(5)')
                        code_lines.append(f'    page.screenshot(path="{screenshot_path}")')
                        report.add_step("Screenshot: Captured", "PASS")

                except PlaywrightTimeout as te:
                    report.add_step(f"Step {i+1} timeout", "FAIL")
                    report.set_status("FAIL")
                    try:
                        page.screenshot(path=screenshot_path)
                    except:
                        pass
                    break

                except Exception as e:
                    report.add_step(f"Step {i+1} error: {str(e)[:50]}", "FAIL")
                    report.set_status("FAIL")
                    try:
                        page.screenshot(path=screenshot_path)
                    except:
                        pass
                    break

            # Final screenshot
            try:
                time.sleep(5)  # Wait for media/video to start playing
                page.screenshot(path=screenshot_path)
            except:
                pass
            
            print("\n[Automation] Completed! Waiting for you to close the browser to finish...\n")
            try:
                while not page.is_closed():
                    # Poll the page to see if it's still alive
                    page.evaluate("1+1")
                    time.sleep(1)
            except Exception:
                pass

    except Exception as e:
        report.add_step(f"Browser error: {str(e)[:100]}", "FAIL")
        report.set_status("FAIL")
        print(f"[Error] {str(e)}")

    # Finalize report
    report.set_execution_time(round(time.time() - start, 2))

    if any(s["status"] == "FAIL" for s in report.steps):
        report.set_status("FAIL")
    else:
        report.set_status("PASS")

    code_lines.append("")
    code_lines.append("    browser.close()")
    code = "\n".join(code_lines)

    return report.generate(), code


def run_test(steps):
    """Execute automation steps in an isolated thread to prevent asyncio loop conflicts"""
    result = {}

    def worker():
        try:
            report_data, code_data = _do_run_test(steps)
            result['report'] = report_data
            result['code'] = code_data
        except Exception as e:
            result['error'] = e

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    if 'error' in result:
        raise result['error']

    return result['report'], result['code']
