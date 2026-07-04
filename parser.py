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
        "search_selector": "[name='search_query']",
        "result_selector": "ytd-video-renderer a#video-title",
        "first_result": "ytd-video-renderer a#video-title",
    },
    "google": {
        "url": "https://www.google.com",
        "keywords": ["google"],
        "search_selector": "[name='q']",
        "result_selector": "h3.LC20lb",
        "first_result": "h3.LC20lb",
    },
    "github": {
        "url": "https://www.github.com",
        "keywords": ["github"],
        "search_selector": "input[placeholder*='search' i], [placeholder*='search' i]",
        "result_selector": "a[data-testid='results-item']",
        "first_result": "a[data-testid='results-item']",
    },
    "wikipedia": {
        "url": "https://www.wikipedia.org",
        "keywords": ["wikipedia", "wiki"],
        "search_selector": "#searchInput",
        "result_selector": "div.mw-search-result-heading",
        "first_result": "div.mw-search-result-heading a",
    },
    "amazon": {
        "url": "https://www.amazon.com",
        "keywords": ["amazon"],
        "search_selector": "#twotabsearchtextbox",
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
        "search_selector": "#sb_form_q",
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
        "search_selector": "#search",
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
- youtube: search="[name='search_query']", result="ytd-video-renderer a#video-title"
- google: search="[name='q']", result="h3.LC20lb"
- github: search="input[placeholder*='search' i]", result="a[data-testid='results-item']"
- wikipedia: search="#searchInput", result="div.mw-search-result-heading a"
- amazon: search="#twotabsearchtextbox", result="h2 a"
- linkedin: search="input.search-global-typeahead__input", result="a[data-test-link]"
- chatgpt: search="textarea[placeholder*='message' i]", result="div[role='article']"
- flipkart: search="input[placeholder*='Search' i]", result="a[href*='/p/']"
- bing: search="#sb_form_q", result="h2 a"
- twitter: search="input[placeholder*='search' i]", result="article"
- instagram: search="input[placeholder*='search' i]", result="div[role='button']"
- facebook: search="input[placeholder*='search' i]", result="h3"
- stackoverflow: search="#search", result="a.s-link"
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
    url_match = re.search(r'https?://(?:www\.)?([^\s/\.]+)', text)
    if url_match:
        domain = url_match.group(1).lower()
        for site_key, config in WEBSITE_CONFIG.items():
            if any(keyword in domain for keyword in config["keywords"]):
                return config, site_key
    
    return None, None

def extract_ordinal_index(text):
    text_lower = text.lower()
    ordinals = {
        r"\b(first|1st|top)\b": 0,
        r"\b(second|2nd)\b": 1,
        r"\b(third|3rd)\b": 2,
        r"\b(fourth|4th)\b": 3,
        r"\b(fifth|5th)\b": 4,
        r"\b(sixth|6th)\b": 5,
        r"\b(seventh|7th)\b": 6,
        r"\b(eighth|8th)\b": 7,
        r"\b(ninth|9th)\b": 8,
        r"\b(tenth|10th)\b": 9
    }
    for pattern, val in ordinals.items():
        if re.search(pattern, text_lower):
            return val
    return None

def parse_with_rules(text):
    text_lower = text.lower()
    steps = []

    site_name = None
    for candidate, config in WEBSITE_CONFIG.items():
        if any(keyword in text_lower for keyword in config["keywords"]):
            site_name = candidate
            break

    if site_name:
        site_config = WEBSITE_CONFIG[site_name]
        steps.append({"action": "open", "url": site_config["url"]})
        steps.append({"action": "wait", "selector": "body"})

        search_match = re.search(r'(?:search|find|look for|type|enter)\s+([\w\s\-\.\'\"@:/#]+)', text, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip().strip("'\"")
            if query.lower() not in {"for", "the", "a", "an", "on", "in"}:
                steps.append({"action": "type", "selector": site_config["search_selector"], "value": query})
                steps.append({"action": "press", "key": "Enter"})
                steps.append({"action": "wait", "selector": "body"})
                
                # Click first result by default for search-heavy sites (youtube, wikipedia, github) or if requested
                is_click_default_site = site_name in ["youtube", "wikipedia", "github"]
                idx = extract_ordinal_index(text)
                if idx is not None or is_click_default_site or any(kw in text_lower for kw in ["play", "click", "give me", "watch", "open", "show me", "select"]):
                    steps.append({
                        "action": "click",
                        "selector": site_config["first_result"],
                        "index": idx if idx is not None else 0,
                        "description": f"{site_name} search result"
                    })
                    steps.append({"action": "wait", "selector": "body"})

        steps.append({"action": "screenshot"})
        return steps
    
    # Split the input into clauses
    clauses = re.split(r'\bthen\b|\band\b|[,;]|\bnext\b|\bafter\b', text)
    
    # Track the current website context to resolve relative actions
    current_site = None
    
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
            
        # 1. OPEN action
        open_match = re.search(
            r'(?:open|go to|visit|navigate to|show)\s+(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?|[a-zA-Z]+)',
            clause,
            re.IGNORECASE
        )
        if open_match:
            target = open_match.group(1).strip()
            url = target
            # Add https:// if it's a domain without protocol
            if not url.startswith("http"):
                # Check if it matches a known site key
                matching_site = None
                for site_key, config in WEBSITE_CONFIG.items():
                    if site_key in url.lower() or any(kw in url.lower() for kw in config["keywords"]):
                        matching_site = site_key
                        break
                
                if matching_site:
                    url = WEBSITE_CONFIG[matching_site]["url"]
                    current_site = matching_site
                else:
                    url = "https://" + url
            else:
                # Resolve known site from URL
                for site_key, config in WEBSITE_CONFIG.items():
                    if any(keyword in url.lower() for keyword in config["keywords"]):
                        current_site = site_key
                        break
            
            steps.append({"action": "open", "url": url})
            steps.append({"action": "wait", "selector": "body"})
            continue

        # 2. CLICK ALL action
        if any(phrase in clause.lower() for phrase in ["click all", "click every", "click each", "click all the"]):
            target = re.sub(r'click\s+all\s+(?:the\s+)?|click\s+every\s+|click\s+each\s+', '', clause, flags=re.IGNORECASE).strip()
            selector = None
            if current_site and current_site in WEBSITE_CONFIG:
                selector = WEBSITE_CONFIG[current_site]["result_selector"]
            
            if not selector:
                if "link" in target.lower():
                    selector = "a"
                elif "button" in target.lower():
                    selector = "button, input[type='button'], input[type='submit']"
                else:
                    selector = target  # Assume it is a CSS selector
                    
            steps.append({"action": "click_all", "selector": selector, "description": target})
            steps.append({"action": "wait", "selector": "body"})
            continue

        # 3. PLAY / WATCH / GIVE ME / SHOW ME action
        # E.g. "play first video", "give me second result", etc.
        play_match = re.search(
            r'(?:play|watch|give\s+me|show\s+me)\s+(?:a\s+|the\s+)?(first|second|third|fourth|fifth|top|\d+(?:st|nd|rd|th)?)\s*(?:video|result|link)?',
            clause, re.IGNORECASE
        )
        if play_match:
            ordinal_word = play_match.group(1).lower()
            idx = extract_ordinal_index(ordinal_word)
            if idx is None:
                digits = re.search(r'\d+', ordinal_word)
                idx = max(0, int(digits.group(0)) - 1) if digits else 0
            
            selector = None
            if current_site and current_site in WEBSITE_CONFIG:
                selector = WEBSITE_CONFIG[current_site]["first_result"]
            if not selector:
                selector = "a"
                
            steps.append({
                "action": "click",
                "selector": selector,
                "index": idx,
                "description": f"{ordinal_word} video"
            })
            steps.append({"action": "wait", "selector": "body"})
            continue
            
        # Specific play query: e.g. "play python tutorial"
        play_spec_match = re.search(r'(?:play|watch|show\s+me)\s+["\']?([^"\']+)["\']?', clause, re.IGNORECASE)
        if play_spec_match:
            target_text = play_spec_match.group(1).strip()
            if target_text.lower() not in ["video", "result", "link", "first", "second", "third"]:
                search_selector = None
                if current_site and current_site in WEBSITE_CONFIG:
                    search_selector = WEBSITE_CONFIG[current_site]["search_selector"]
                if not search_selector:
                    search_selector = "input[type='text'], input[type='search'], textarea"
                steps.append({"action": "type", "selector": search_selector, "value": target_text})
                steps.append({"action": "press", "key": "Enter"})
                steps.append({"action": "wait", "selector": "body"})
                
                result_selector = None
                if current_site and current_site in WEBSITE_CONFIG:
                    result_selector = WEBSITE_CONFIG[current_site]["first_result"]
                if not result_selector:
                    result_selector = "a"
                
                idx = extract_ordinal_index(clause)
                steps.append({
                    "action": "click",
                    "selector": result_selector,
                    "index": idx if idx is not None else 0,
                    "description": f"video for '{target_text}'"
                })
                steps.append({"action": "wait", "selector": "body"})
                continue

        # 4. CLICK action with ordinal support
        click_match = re.search(
            r'(?:click|press on|tap|go to|open|visit)\s+(?:the\s+)?(first|second|third|fourth|fifth|top|\d+(?:st|nd|rd|th)?)\s*(result|video|link|item|button)?',
            clause, re.IGNORECASE
        )
        if click_match:
            ordinal_word = click_match.group(1).lower()
            idx = extract_ordinal_index(ordinal_word)
            if idx is None:
                digits = re.search(r'\d+', ordinal_word)
                idx = max(0, int(digits.group(0)) - 1) if digits else 0
                
            selector = None
            if current_site and current_site in WEBSITE_CONFIG:
                selector = WEBSITE_CONFIG[current_site]["first_result"]
            if not selector:
                selector = "a"
                
            steps.append({
                "action": "click",
                "selector": selector,
                "index": idx,
                "description": f"{ordinal_word} item"
            })
            steps.append({"action": "wait", "selector": "body"})
            continue

        # General click by text target
        click_text_match = re.search(
            r'(?:click|press on|tap|go to|open|visit)\s+(?:the\s+)?["\']?([^"\']+)["\']?',
            clause, re.IGNORECASE
        )
        if click_text_match:
            target = click_text_match.group(1).strip()
            if target.lower() not in ["first", "second", "third", "result", "video", "link"]:
                selector = None
                if current_site and current_site in WEBSITE_CONFIG and any(x in target.lower() for x in ["result", "video", "link", "item"]):
                    selector = WEBSITE_CONFIG[current_site]["first_result"]
                if not selector:
                    selector = target
                
                idx = extract_ordinal_index(clause)
                steps.append({
                    "action": "click",
                    "selector": selector,
                    "index": idx if idx is not None else 0,
                    "description": target
                })
                steps.append({"action": "wait", "selector": "body"})
                continue

        # 5. TYPE / SEARCH action
        type_match = re.search(r'(?:type|search for|search|enter|input|write)\s+["\']?([^"\']+)["\']?(?:\s+in|\s+into|\s+on)?', clause, re.IGNORECASE)
        if type_match:
            value = type_match.group(1).strip()
            selector = None
            
            # Extract target field if mentioned
            field_match = re.search(r'(?:in|into|on)\s+(?:the\s+)?(?:search\s+)?(?:box|field|input|textarea)\s*["\']?([^"\']*)["\']?', clause, re.IGNORECASE)
            if field_match and field_match.group(1).strip():
                selector = field_match.group(1).strip()
                
            if not selector and current_site and current_site in WEBSITE_CONFIG:
                selector = WEBSITE_CONFIG[current_site]["search_selector"]
                
            if not selector:
                # Executor will fall back to common inputs
                selector = "input[type='text'], input[type='search'], textarea, [contenteditable='true']"
                
            steps.append({"action": "type", "selector": selector, "value": value})
            steps.append({"action": "press", "key": "Enter"})
            steps.append({"action": "wait", "selector": "body"})
            # Click first result by default for search-heavy sites (youtube, wikipedia, github)
            if current_site in ["youtube", "wikipedia", "github"]:
                steps.append({
                    "action": "click",
                    "selector": WEBSITE_CONFIG[current_site]["first_result"],
                    "index": 0,
                    "description": f"{current_site} search result"
                })
                steps.append({"action": "wait", "selector": "body"})
            continue

        # 6. SCROLL action
        if "scroll" in clause.lower():
            direction = "down" if "down" in clause.lower() else "up"
            steps.append({"action": "scroll", "direction": direction})
            continue

        # 7. SCREENSHOT action
        if any(x in clause.lower() for x in ["screenshot", "capture", "take picture", "snap"]):
            steps.append({"action": "screenshot"})
            continue

    # If no open action was added, add a default one based on site context or google
    has_open = any(s["action"] == "open" for s in steps)
    if not has_open:
        # Detect if any site name is mentioned in the whole text
        website_config, site_name = get_website_config(text)
        if website_config:
            steps.insert(0, {"action": "wait", "selector": "body"})
            steps.insert(0, {"action": "open", "url": website_config["url"]})
            current_site = site_name
        else:
            # Check if there is a general URL in the whole text
            url_match = re.search(r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)', text)
            if url_match:
                url = url_match.group(1).strip()
                if not url.startswith("http"):
                    url = "https://" + url
                steps.insert(0, {"action": "wait", "selector": "body"})
                steps.insert(0, {"action": "open", "url": url})
            else:
                # Default fallback to Google
                steps.insert(0, {"action": "wait", "selector": "body"})
                steps.insert(0, {"action": "open", "url": "https://www.google.com"})
                current_site = "google"
        
    # Always ensure a screenshot at the end
    if not steps or steps[-1]["action"] != "screenshot":
        steps.append({"action": "screenshot"})
        
    return steps


# =========================
# 🚀 MAIN ENTRY POINT
# =========================
def should_use_ai_parser(text):
    """Use the AI parser only for longer or more ambiguous requests."""
    if not text or not text.strip():
        return False

    normalized = text.strip()
    if len(normalized.split()) <= 8:
        return False

    if re.search(r"\b(then|after|next|before|while|compare|summarize|explain|if|when)\b", normalized, re.IGNORECASE):
        return True

    return len(normalized.split()) >= 16


def parse_input(text):
    """Parse user input and return automation steps."""
    
    if not text or not text.strip():
        return [
            {"action": "open", "url": "https://www.google.com"},
            {"action": "screenshot"}
        ]
    
    api_available = groq_client.is_available()
    
    if api_available and should_use_ai_parser(text):
        ai_steps = parse_with_ai(text)
        if ai_steps:
            return ai_steps
    
    try:
        steps = parse_with_rules(text)
        return steps if steps else get_default_steps()
    except Exception:
        return get_default_steps()

def get_default_steps():
    """Return default steps when parsing fails."""
    return [
        {"action": "open", "url": "https://www.google.com"},
        {"action": "wait", "selector": "input[name='q']"},
        {"action": "screenshot"}
    ]