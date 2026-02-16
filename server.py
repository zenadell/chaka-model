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
API_KEY = "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"
client = Groq(api_key=API_KEY)

AUTHORIZED_KEYS = {
    "Chaka_Supreme_Access": "Chaka Admin Panel",
    "temple-project-alpha": "Temple Project Alpha"
}

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
        while True:
            try:
                # Replace with your actual deployed URL if needed
                requests.get("http://localhost:5001/health")
                print("✅ Self-ping successful")
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

    # Model-Specific Logic (Force Audit Monologue)
    if model_id in ["llama-3.3-70b-versatile", "meta-llama/llama-4-maverick-17b-128e-instruct", "chaka-medium", "chaka-high"]:
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
            
            # Save only the CLEAN string answer to history (Vision models sometimes return complex objects)
            history.append({"role": "assistant", "content": answer})
            
            if len(history) > 20:
                sessions[session_id] = [history[0]] + history[-19:] # Preserve dynamic system prompt
            
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
    sessions[session_id] = [SYSTEM_PROMPT]
    return jsonify({"status": "Chat history cleared"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
