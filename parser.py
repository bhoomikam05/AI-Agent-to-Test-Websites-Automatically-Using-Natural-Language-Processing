import os
import requests
import json
import re
from dotenv import load_dotenv
from api_config import get_groq_client

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = get_groq_client()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# =========================
# 🌐 WEBSITE CONFIGURATIONS
# =========================
WEBSITE_CONFIG = {
    "youtube": {
        "url": "https://www.youtube.com",
        "keywords": ["youtube", "youtu.be"],
        "search_selector": "input[name='search_query']",
        "result_selector": "ytd-video-renderer a#video-title",
        "first_result": "ytd-video-renderer a#video-title",
    },
    "google": {
        "url": "https://www.google.com",
        "keywords": ["google"],
        "search_selector": "input[name='q']",
        "result_selector": "h3.LC20lb",
        "first_result": "h3.LC20lb",
    },
    "github": {
        "url": "https://www.github.com",
        "keywords": ["github"],
        "search_selector": "input[placeholder*='search' i]",
        "result_selector": "a[data-testid='results-item']",
        "first_result": "a[data-testid='results-item']",
    },
    "wikipedia": {
        "url": "https://www.wikipedia.org",
        "keywords": ["wikipedia", "wiki"],
        "search_selector": "input#searchInput",
        "result_selector": "div.mw-search-result-heading",
        "first_result": "div.mw-search-result-heading a",
    },
    "amazon": {
        "url": "https://www.amazon.com",
        "keywords": ["amazon"],
        "search_selector": "input#twotabsearchtextbox",
        "result_selector": "h2 a",
        "first_result": "h2 a",
    },
    "linkedin": {
        "url": "https://www.linkedin.com",
        "keywords": ["linkedin"],
        "search_selector": "input.search-global-typeahead__input",
        "result_selector": "a[data-test-link]",
        "first_result": "a[data-test-link]",
    },
    "chatgpt": {
        "url": "https://chat.openai.com",
        "keywords": ["chatgpt", "chat gpt", "openai"],
        "search_selector": "textarea[placeholder*='message' i]",
        "result_selector": "div[role='article']",
        "first_result": "div[role='article']",
    },
    "flipkart": {
        "url": "https://www.flipkart.com",
        "keywords": ["flipkart"],
        "search_selector": "input[placeholder*='Search' i]",
        "result_selector": "a[href*='/p/']",
        "first_result": "a[href*='/p/']",
    },
    "bing": {
        "url": "https://www.bing.com",
        "keywords": ["bing"],
        "search_selector": "input#sb_form_q",
        "result_selector": "h2 a",
        "first_result": "h2 a",
    },
    "twitter": {
        "url": "https://www.twitter.com",
        "keywords": ["twitter", "x.com"],
        "search_selector": "input[placeholder*='search' i]",
        "result_selector": "article",
        "first_result": "article",
    },
    "instagram": {
        "url": "https://www.instagram.com",
        "keywords": ["instagram"],
        "search_selector": "input[placeholder*='search' i]",
        "result_selector": "div[role='button']",
        "first_result": "div[role='button']",
    },
    "facebook": {
        "url": "https://www.facebook.com",
        "keywords": ["facebook"],
        "search_selector": "input[placeholder*='search' i]",
        "result_selector": "h3",
        "first_result": "h3",
    },
    "stackoverflow": {
        "url": "https://stackoverflow.com",
        "keywords": ["stackoverflow", "stack overflow"],
        "search_selector": "input#search",
        "result_selector": "a.s-link",
        "first_result": "a.s-link",
    },
    "reddit": {
        "url": "https://www.reddit.com",
        "keywords": ["reddit"],
        "search_selector": "input[placeholder*='Search' i]",
        "result_selector": "a[data-click-id='body']",
        "first_result": "a[data-click-id='body']",
    },
    "claude": {
        "url": "https://claude.ai/new",
        "keywords": ["claude"],
        "search_selector": "div[contenteditable='true']",
        "result_selector": "div.font-claude-message",
        "first_result": "div.font-claude-message",
    },
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "keywords": ["whatsapp", "wa"],
        "search_selector": "div[contenteditable='true'][data-tab='3']",
        "result_selector": "div[role='listitem']",
        "first_result": "div[role='listitem']",
    },
}

SYSTEM_PROMPT = """You are a Playwright automation expert. Convert natural language instructions into JSON steps.

CRITICAL RULES:
1. Return ONLY a valid JSON array - no explanation
2. Always start with {"action": "open", "url": "..."}
3. Always end with {"action": "screenshot"}
4. Add minimal wait times between actions (0.5-1 second)
5. For "click all X" requests, use click_all action
6. ALWAYS USE THE EXACT SELECTORS PROVIDED IN THE DIRECTORY FOR THE TARGET WEBSITE! Do not guess.

KNOWN WEBSITE SELECTORS:
- youtube: search="input[name='search_query']", result="ytd-video-renderer a#video-title"
- google: search="input[name='q']", result="h3.LC20lb"
- github: search="input[placeholder*='search' i]", result="a[data-testid='results-item']"
- wikipedia: search="input#searchInput", result="div.mw-search-result-heading a"
- amazon: search="input#twotabsearchtextbox", result="h2 a"
- linkedin: search="input.search-global-typeahead__input", result="a[data-test-link]"
- chatgpt: search="textarea[placeholder*='message' i]", result="div[role='article']"
- flipkart: search="input[placeholder*='Search' i]", result="a[href*='/p/']"
- bing: search="input#sb_form_q", result="h2 a"
- twitter: search="input[placeholder*='search' i]", result="article"
- instagram: search="input[placeholder*='search' i]", result="div[role='button']"
- facebook: search="input[placeholder*='search' i]", result="h3"
- stackoverflow: search="input#search", result="a.s-link"
- reddit: search="input[placeholder*='Search' i]", result="a[data-click-id='body']"
- claude: search="div[contenteditable='true']", result="div.font-claude-message"
- whatsapp: search="div[contenteditable='true'][data-tab='3']", result="div[role='listitem']"

SUPPORTED ACTIONS:
- {"action": "open", "url": "<full https url>"}
- {"action": "wait", "selector": "<css selector>"}
- {"action": "type", "selector": "<css selector>", "value": "<text>"}
- {"action": "press", "key": "<key name>"}
- {"action": "click", "selector": "<css selector>", "description": "<label>"}
- {"action": "click_all", "selector": "<css selector>", "description": "<label>"}
- {"action": "scroll", "direction": "<down|up>"}
- {"action": "screenshot"}"""


# =========================
# 🤖 AI PARSER (Groq)
# =========================
def parse_with_ai(text):
    """Parse text using Groq AI API"""
    if not groq_client.is_available():
        return None

    try:
        # Call the API
        response = groq_client.call(SYSTEM_PROMPT, text)
        
        if not response:
            # Silently fail and fall back to rule-based
            return None

        # Clean up markdown code blocks if present
        content = re.sub(r"```json|```", "", response).strip()

        # Try to parse as JSON
        steps = json.loads(content)

        # Validate it's a list
        if not isinstance(steps, list):
            return None

        # Ensure screenshot at end
        if not steps or steps[-1].get("action") != "screenshot":
            steps.append({"action": "screenshot"})

        return steps

    except json.JSONDecodeError as e:
        # Silently fail
        return None
    except ValueError as e:
        # Silently fail
        return None
    except Exception as e:
        # Silently fail
        return None


# =========================
# 🔧 RULE-BASED PARSER (Fallback)
# =========================
def get_website_config(text):
    """Detect website from text and return configuration"""
    text_lower = text.lower()
    
    # Check for explicit website mentions
    for site_key, config in WEBSITE_CONFIG.items():
        for keyword in config["keywords"]:
            if keyword in text_lower:
                return config, site_key
    
    # Check for URL in text
    url_match = re.search(r'https?://([^\s"\']+)', text)
    if url_match:
        domain = url_match.group(1).lower()
        for site_key, config in WEBSITE_CONFIG.items():
            if any(keyword in domain for keyword in config["keywords"]):
                return config, site_key
    
    # Default to YouTube
    return WEBSITE_CONFIG["youtube"], "youtube"

def parse_with_rules(text):
    text_lower = text.lower()
    steps = []

    # Get website configuration
    website_config, site_name = get_website_config(text)
    url = website_config["url"]
    search_selector = website_config["search_selector"]
    result_selector = website_config["result_selector"]
    first_result = website_config["first_result"]

    steps.append({"action": "open", "url": url})
    steps.append({"action": "wait", "selector": "body"})

    # Extract search term - improved regex
    search_term = None
    search_patterns = [
        r'search\s+(?:for\s+)?["\']?([^"\'.,;]+?)(?:\s+on\s+|\s+at\s+|\s+click|\s+and|\s+in|\s*$)',
        r'find\s+(?:for\s+)?["\']?([^"\'.,;]+?)(?:\s+on\s+|\s+at\s+|\s+click|\s+and|\s*$)',
        r'look(?:ing)?\s+for\s+["\']?([^"\'.,;]+?)(?:\s+on\s+|\s+at\s+|\s+click|\s+and|\s*$)',
        r'(?:search|find|look)\s+["\']?([^"\'.,;]+?)(?:\s+on\s+)',
    ]
    
    for pattern in search_patterns:
        search_match = re.search(pattern, text_lower)
        if search_match:
            search_term = search_match.group(1).strip().strip("for").strip()
            break

    if search_term and len(search_term) > 1:
        steps.append({"action": "type", "selector": search_selector, "value": search_term})
        steps.append({"action": "press", "key": "Enter"})
        steps.append({"action": "wait", "selector": "body"})
        
        # ONLY click if user explicitly asks for it - check for clear click/result intent
        # Don't click just because "click" or "open" appears anywhere in the text
        explicit_click_patterns = [
            r'click\s+(?:the\s+)?(?:first|top|1st|result|video|link|item)',
            r'(?:open|visit|go to)\s+(?:the\s+)?(?:first|top|1st|result|video|link|item)',
            r'(?:first|top)\s+(?:result|video|link|item)',
        ]
        
        should_click = False
        for pattern in explicit_click_patterns:
            if re.search(pattern, text_lower):
                should_click = True
                break
        
        # Check for click all pattern (explicit)
        if any(phrase in text_lower for phrase in ["click all", "click every", "click all the", "click each"]):
            steps.append({"action": "click_all", "selector": result_selector, "description": f"all results on {site_name}"})
            steps.append({"action": "wait", "selector": "body"})
        # Only click if explicitly requested
        elif should_click:
            steps.append({"action": "click", "selector": first_result, "description": f"first result on {site_name}"})
            steps.append({"action": "wait", "selector": "body"})

    # Check for scroll action
    if "scroll" in text_lower:
        direction = "down" if "down" in text_lower else "up"
        steps.append({"action": "scroll", "direction": direction})

    # Always ensure screenshot at end
    steps.append({"action": "screenshot"})

    return steps


# =========================
# 🚀 MAIN ENTRY POINT
# =========================
def parse_input(text):
    """Parse user input and return automation steps."""
    
    if not text or not text.strip():
        return [
            {"action": "open", "url": "https://www.google.com"},
            {"action": "screenshot"}
        ]
    
    # Try AI first if API is available (silently, no output)
    api_available = groq_client.is_available()
    
    if api_available:
        ai_steps = parse_with_ai(text)
        if ai_steps:
            return ai_steps
    
    # Fallback to rule-based parsing
    try:
        steps = parse_with_rules(text)
        return steps if steps else get_default_steps()
    except Exception as e:
        return get_default_steps()

def get_default_steps():
    """Return default steps when parsing fails."""
    return [
        {"action": "open", "url": "https://www.google.com"},
        {"action": "wait", "selector": "input[name='q']"},
        {"action": "screenshot"}
    ]