import os
import re
import time
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq, RateLimitError

app = Flask(__name__, static_folder='.', static_url_path='')
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

# ---------------------------------------------------------
# FRONTEND SERVING
# ---------------------------------------------------------
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

# ---------------------------------------------------------
# DEPLOYMENT CONFIG (Hugging Face / Self-Ping)
# ---------------------------------------------------------
# Set to a specific model ID to force all users to use it (ignoring their selection)
# Example: LOCKED_MODEL = "llama-3.1-8b-instant"
LOCKED_MODEL = None 

# Custom Model Mapping
MODEL_MAPPING = {
    "chaka-low": "llama-3.1-8b-instant",
    "chaka-medium": "llama-3.3-70b-versatile",
    "chaka-high": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "chaka-image": "meta-llama/llama-4-scout-17b-16e-instruct",
    "chaka-ultimate": "openai/gpt-oss-120b"
}

def self_ping():
    """Background thread to keep the server alive on platforms like Hugging Face"""
    import threading
    import requests
    import time
    
    def ping_loop():
        time.sleep(10) # Initial delay
        port = os.environ.get("PORT", 5001) # Dynamically get port
        while True:
            try:
                # Replace with your actual deployed URL if needed
                requests.get(f"http://127.0.0.1:{port}/health")
                print(f"✅ Self-ping successful on port {port}")
            except Exception as e:
                print(f"⚠️ Self-ping failed: {e}")
            time.sleep(600) # Ping every 10 minutes

    threading.Thread(target=ping_loop, daemon=True).start()

# Start self-ping checks
self_ping()

# ---------------------------------------------------------
# THOUGHT EXTRACTION ENGINE
# ---------------------------------------------------------
def extract_thought(text):
    # 1. Native <think> tags (GPT-OSS / DeepSeek / Reasoning models)
    think_pattern = r"<think>(.*?)</think>"
    match = re.search(think_pattern, text, re.DOTALL)
    
    if match:
        thought = match.group(1).strip()
        answer = re.sub(think_pattern, "", text, flags=re.DOTALL).strip()
        return thought, answer

    # 2. Custom Forced Format (Llama models)
    think_pattern_custom = r"THOUGHT_PROCESS:(.*?)FINAL_ANSWER:"
    match_custom = re.search(think_pattern_custom, text, re.DOTALL)
    
    if match_custom:
        thought = match_custom.group(1).strip()
        answer = re.sub(think_pattern_custom, "", text, flags=re.DOTALL).strip()
        answer = answer.replace("FINAL_ANSWER:", "").strip()
        return thought, answer

    return None, text

# ---------------------------------------------------------
# THE CHAKA V2 CORE (Identity & Logic Engine)
# ---------------------------------------------------------
CHAKA_IDENTITY = (
    "Role: You are Chaka, a charming, intelligent, and witty AI assistant developed by Jomiez. "
    "You are friendly, concise, and helpful. You speak naturally like a human friend, avoiding robotic jargon. "
    "However, behind the scenes, you operate with extreme precision using the Logic Engine."
)

CHAKA_LOGIC_ENGINE = (
    "INTERNAL INSTRUCTION: You MUST perform the 4-Phase Logic Audit internally before answering. "
    "Do NOT reveal these phases to the user. Use them to ensure your answer is technically perfect.\n\n"
    "Phase 1: Verb Classification (Kinetic vs Static)\n"
    "Phase 2: Connector Logic (And/Who/With/Whose)\n"
    "Phase 3: Semantic Truth Check (Actor vs Attribute)\n"
    "Phase 4: Ambiguity Resolution\n\n"
    "Output Format:\n"
    "THOUGHT_PROCESS: [Your full 4-Phase Logic Audit goes here]\n"
    "FINAL_ANSWER: [Your natural, human-like response to the user goes here. Do not mention phases or logic.]"
)

# Combined fallback for internal use
ULTRA_LOGIC = f"{CHAKA_IDENTITY}\n\n{CHAKA_LOGIC_ENGINE}"

sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "alive", "engine": "Chaka V2"}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    # 1. API Key Validation
    api_key = request.headers.get('X-Chaka-API-Key')
    if api_key not in AUTHORIZED_KEYS:
        return jsonify({"error": "Unauthorized: Invalid or missing API Key."}), 401

    data = request.json
    user_input = data.get('message')
    session_id = data.get('session_id', 'default')
    
    # Model Selection Logic
    requested_model = data.get('model', "chaka-medium") # Default to medium
    
    if LOCKED_MODEL:
        model_id = LOCKED_MODEL
        print(f"🔒 Usage Locked to Model: {model_id}")
    else:
        # Resolve custom name to actual ID, or use as-is if not in mapping
        model_id = MODEL_MAPPING.get(requested_model, requested_model)
        print(f"🔄 Resolved Model: {requested_model} -> {model_id}")

    image_data = data.get('image') 
    custom_prompt = data.get('custom_prompt', "")
    
    if not user_input and not image_data:
        return jsonify({"error": "No message or image provided"}), 400

    # 2. Dynamic Identity & Logic Construction
    # RULE: If custom_prompt exists, it is the PRIMARY identity.
    # FALLBACK: Use Chaka V2 Identity.
    primary_identity = custom_prompt if custom_prompt else CHAKA_IDENTITY
    
    final_system_content = (
        f"{primary_identity}\n\n"
        "--- INTERNAL LOGIC ENGINE (HIDDEN) ---\n"
        f"{CHAKA_LOGIC_ENGINE}\n\n"
        "REMINDER: Your response must be natural and human. Hide the logic."
    )

    system_msg = {"role": "system", "content": final_system_content}

    if session_id not in sessions:
        sessions[session_id] = [system_msg]

    history = sessions[session_id]
    history[0] = system_msg # Update to latest prompt construction
    
    # Construct Content
    content = []
    if user_input:
        content.append({"type": "text", "text": user_input})
    
    if image_data:
        content.append({
            "type": "image_url",
            "image_url": { "url": image_data }
        })

    # Add to history
    history.append({"role": "user", "content": content})

    messages = list(history)
    params = {
        "model": model_id,
        "temperature": 0.7, # Slightly higher for creativity
        "max_tokens": 4096,
    }

    # Model-Specific Logic (Force Audit Monologue for Reasoning models)
    if requested_model in ["chaka-medium", "chaka-high", "chaka-ultimate"] or model_id in ["llama-3.3-70b-versatile", "meta-llama/llama-4-maverick-17b-128e-instruct", "openai/gpt-oss-120b"]:
        # We enforce the format so we can extract thoughts properly
        audit_instruction = "\nIMPORTANT: Start your response with THOUGHT_PROCESS: ... followed by FINAL_ANSWER: ..."
        messages[0] = {"role": "system", "content": final_system_content + audit_instruction}
    
    params["messages"] = messages

    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(**params)
            raw_response = completion.choices[0].message.content
            thought, answer = extract_thought(raw_response)
            
            # Save CLEAN answer to history. 
            # STRATEGY: Strip the image data from the user message we just sent to prevent 413 errors on next turn.
            # The AI already "saw" it and its text response now provides the context for future messages.
            last_user_msg = history[-1]
            if isinstance(last_user_msg['content'], list):
                # Replace list content with just the text part for history persistence
                text_only = ""
                for part in last_user_msg['content']:
                    if part['type'] == 'text':
                        text_only += part['text']
                last_user_msg['content'] = text_only if text_only else "Sent an image."
            
            history.append({"role": "assistant", "content": answer})
            
            if len(history) > 20:
                sessions[session_id] = [history[0]] + history[-19:] 
            
            return jsonify({
                "response": answer, 
                "thought": thought,
                "project": AUTHORIZED_KEYS[api_key],
                "engine": "Chaka V2 (Logic Powered)"
            })

        except RateLimitError:
            time.sleep(2)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "I am currently at maximum capacity."}), 429

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
