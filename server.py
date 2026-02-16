import os
import re
import time
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq, RateLimitError

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Validates existence of GROQ_API_KEY in environment, falls back to hardcoded if missing (for local dev)
API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=API_KEY)

AUTHORIZED_KEYS = {
    "Chaka_Supreme_Access": "Chaka Admin Panel",
    "temple-project-alpha": "Temple Project Alpha"
}

# ... (skipped lines) ...

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    session_id = request.json.get('session_id', 'default')
    if session_id in sessions:
        # Reset to just the system prompt if possible, or just empty list to trigger regeneration
        del sessions[session_id] 
    return jsonify({"status": "Chat history cleared"})

if __name__ == '__main__':
    # Use PORT from environment for Render/Railway compatibility
    port = int(os.environ.get("PORT", 5001))
    # Disable debug in production
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
