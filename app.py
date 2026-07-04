from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import traceback
import os
import time
import sys
import logging
from waitress import serve  # Use waitress instead of Flask dev server

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Flask requests
logging.getLogger('urllib3').setLevel(logging.ERROR)   # HTTP requests
logging.getLogger('requests').setLevel(logging.ERROR)  # Requests library

# Load environment variables from .env file
load_dotenv(override=True)

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


# Browser opening logic removed for deployment

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
    
    # Check if auto-run command is provided (and ensure it is not standard CLI flags/configs)
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if not first_arg.startswith('-') and not first_arg.isdigit() and not first_arg.endswith('.py'):
            AUTO_RUN_COMMAND = " ".join(sys.argv[1:])
            print(f"  Auto-running: {AUTO_RUN_COMMAND}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Print server info
    port = int(os.environ.get("PORT", 5000))
    print("[Server] Flask server is running!")
    print(f"[Server] Listening on: http://0.0.0.0:{port}")
    print("[Server] Press Ctrl+C to stop\n")
    sys.stdout.flush()
    
    try:
        # Pre-launch the automation background thread (initializes Playwright without opening a window)
        try:
            from executor import pre_launch_browser
            pre_launch_browser()
        except Exception as e:
            print(f"[Server] Could not pre-launch background thread: {e}")

        serve(app, host='0.0.0.0', port=port, _quiet=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        traceback.print_exc()