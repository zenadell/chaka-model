import os
import time
from groq import Groq, RateLimitError

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
API_KEY = "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"
client = Groq(api_key=API_KEY)

# ---------------------------------------------------------
# THE MEMORY BANK
# ---------------------------------------------------------
conversation_history = [
    {
        "role": "system", 
        "content": "You are Chaka AI, a helpful and intelligent assistant built by Temple. You are witty, concise, and smart."
    }
]

# ---------------------------------------------------------
# MODEL SELECTOR
# ---------------------------------------------------------
MODELS = {
    "1": {"id": "llama-3.1-8b-instant", "name": "⚡ Fast Mode"},
    "2": {"id": "llama-3.3-70b-versatile", "name": "🧠 Smart Mode"}
}

def chat_with_chaka(user_input, model_id):
    conversation_history.append({"role": "user", "content": user_input})

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"   (Thinking with {model_id}...)")
            completion = client.chat.completions.create(
                model=model_id,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=1024,
            )
            ai_response = completion.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
        except RateLimitError:
            print(f"⚠️ Rate Limit hit. Waiting 2s...")
            time.sleep(2)
        except Exception as e:
            return f"❌ Error: {str(e)}"
    return "I am currently at maximum capacity."

if __name__ == "__main__":
    print("CHAKA AI v2.0 - CLI")
    choice = input("Select: 1 (Fast) or 2 (Smart): ")
    selected_model = MODELS.get(choice, MODELS["2"])["id"]
    
    while True:
        try:
            user_text = input("You: ")
            if user_text.lower() in ["exit", "quit"]: break
            print(f"Chaka: {chat_with_chaka(user_text, selected_model)}\n")
        except KeyboardInterrupt: break
