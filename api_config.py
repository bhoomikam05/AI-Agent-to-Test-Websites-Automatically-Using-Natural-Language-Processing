"""
API Configuration and Utilities
Handles Groq API integration for AI-based automation parsing
"""

import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GroqAPI:
    """Groq API client for automation step generation"""
    
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"  # Updated to active valid model
    TIMEOUT = 15
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.available = bool(self.api_key)
        
        if self.available:
            logger.info("[API] Groq API initialized successfully")
        else:
            logger.warning("[API] No GROQ_API_KEY found - AI parsing will be unavailable")
    
    def is_available(self):
        """Check if API is available"""
        return self.available
    
    def call(self, system_prompt, user_message):
        """
        Make API call to Groq
        
        Args:
            system_prompt (str): System message for the AI
            user_message (str): User input message
            
        Returns:
            str: AI response or None if failed
        """
        if not self.available:
            logger.warning("[API] API call attempted but not available")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            logger.debug("[API] Calling Groq API...")
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"].strip()
            logger.info("[API] API call successful")
            return content
            
        except requests.exceptions.Timeout:
            logger.debug("[API] Timeout - Groq API took too long to respond")
            return None
        except requests.exceptions.ConnectionError:
            logger.debug("[API] Connection error - Unable to reach Groq API")
            return None
        except requests.exceptions.HTTPError as e:
            logger.debug(f"[API] HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except ValueError as e:
            logger.debug(f"[API] JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.debug(f"[API] Unexpected error: {e}")
            return None


def get_groq_client():
    """Get or create Groq API client"""
    return GroqAPI()


def check_api_status():
    """Check if API is available"""
    client = get_groq_client()
    return {
        "available": client.is_available(),
        "api_key_set": bool(os.getenv("GROQ_API_KEY")),
        "model": GroqAPI.MODEL
    }
