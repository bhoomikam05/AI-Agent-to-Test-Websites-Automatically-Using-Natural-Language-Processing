from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import traceback
import os
import webbrowser
import threading
import time
import sys
import logging
from waitress import serve  # Use waitress instead of Flask dev server

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Flask requests
logging.getLogger('urllib3').setLevel(logging.ERROR)   # HTTP requests
logging.getLogger('requests').setLevel(logging.ERROR)  # Requests library

# Load environment variables from .env file
load_dotenv()

# LAZY IMPORT: Import agent and api_config only when routes are called
def get_agent():
    from agent import execute, get_summary
    return execute, get_summary

def get_api_status():
    from api_config import check_api_status
    return check_api_status

app = Flask(__name__)

# Store auto-run command if passed
AUTO_RUN_COMMAND = None


def open_browser():
    """Open browser to localhost after Flask server starts"""
    time.sleep(2)  # Give Flask time to start
    url = "http://127.0.0.1:5000"

    webbrowser.open(url)
    
    # If auto-run command is set, execute it after browser opens
    if AUTO_RUN_COMMAND:
        time.sleep(1)
        print(f"[App] 🤖 Auto-running: {AUTO_RUN_COMMAND}")
        # This will be executed via the web interface via JS
        pass

@app.route("/")
def home():
    return render_template("index.html", auto_run_command=AUTO_RUN_COMMAND)

@app.route("/run", methods=["POST"])
def run():
    try:
        execute, _ = get_agent()
        data = request.get_json()
        instruction = data.get("input", "").strip()

        if not instruction:
            return jsonify({"error": "No instruction provided"}), 400

        # Use agent to execute automation
        result = execute(instruction)

        return jsonify(result)
    
    except Exception as e:
        pass
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/summary", methods=["GET"])
def summary():
    """Get execution summary"""
    try:
        _, get_summary = get_agent()
        return jsonify(get_summary())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api-status", methods=["GET"])
def api_status():
    """Check Groq API status"""
    try:
        check_api_status = get_api_status()
        status = check_api_status()
        return jsonify({
            "status": "ok" if status["available"] else "unavailable",
            "api_key_configured": status["api_key_set"],
            "model": status["model"],
            "message": "AI-based parsing is available" if status["available"] else "Using rule-based parsing fallback"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("\n  AI TEST AUTOMATION AGENT - Starting Server...")
    print("  Server will open in 2 seconds")
    
    # Check if auto-run command is provided
    if len(sys.argv) > 1:
        AUTO_RUN_COMMAND = " ".join(sys.argv[1:])
        print(f"  Auto-running: {AUTO_RUN_COMMAND}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Start browser in background thread (optional, after server starts)
    def delayed_browser():
        time.sleep(2)
        try:
            url = "http://127.0.0.1:5000"
            webbrowser.open(url)
            print(f"\n[Browser] Opening: {url}\n")
        except Exception as e:
            print(f"\n[Browser] Open failed (navigate manually to http://127.0.0.1:5000): {e}\n")
    
    try:
        browser_thread = threading.Thread(target=delayed_browser, daemon=True)
        browser_thread.start()
    except:
        pass
    
    # Print server info
    print("[Server] Flask server is running!")
    print("[Server] URL: http://127.0.0.1:5000")
    print("[Server] Press Ctrl+C to stop\n")
    sys.stdout.flush()
    
    # Start with waitress (more reliable on Windows)
    try:
        serve(app, host='127.0.0.1', port=5000, _quiet=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        traceback.print_exc()