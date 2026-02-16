import os
import re
import time
from groq import Groq, RateLimitError

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
API_KEY = "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"
client = Groq(api_key=API_KEY)

# ---------------------------------------------------------
# MODEL MENU
# ---------------------------------------------------------
MODELS = {
    "1": {
        "id": "llama-3.1-8b-instant",
        "name": "⚡ Fast Mode (Llama 8B)",
        "type": "standard",
        "desc": "Speed. Good for chit-chat."
    },
    "2": {
        "id": "llama-3.3-70b-versatile",
        "name": "🧠 Smart Mode (Llama 3.3 70B)",
        "type": "standard",
        "desc": "Raw Intelligence. We will FORCE this one to think."
    },
    "3": {
        "id": "deepseek-r1-distill-llama-70b",
        "name": "🤯 Genius Mode (DeepSeek R1)",
        "type": "reasoning",
        "desc": "Native Reasoning. Born to think."
    }
}

# ---------------------------------------------------------
# THE THOUGHT ENGINE
# ---------------------------------------------------------
def extract_thought(text):
    """
    Parses out the thought process from the final answer.
    Works for both DeepSeek (Native) and Llama (Forced).
    """
    # Pattern 1: DeepSeek native style <think>...</think>
    think_pattern = r"<think>(.*?)</think>"
    match = re.search(think_pattern, text, re.DOTALL)
    
    # Pattern 2: Our Custom "Forced" style (for Smart Mode)
    if not match:
        think_pattern = r"THOUGHT_PROCESS:(.*?)FINAL_ANSWER:"
        match = re.search(think_pattern, text, re.DOTALL)

    if match:
        thought = match.group(1).strip()
        answer = re.sub(think_pattern, "", text, flags=re.DOTALL).strip()
        # Fallback if FINAL_ANSWER: prefix remains
        answer = answer.replace("FINAL_ANSWER:", "").strip()
        return thought, answer
    else:
        return None, text

def chat_with_chaka(user_input, model_conf, history):
    # Add user input
    history.append({"role": "user", "content": user_input})
    
    # SYSTEM PROMPT INJECTION (The Magic Trick)
    if model_conf["type"] == "standard" and model_conf["id"] == "llama-3.3-70b-versatile":
        system_instruction = (
            "You are Chaka. IMPORTANT: Before answering, you must "
            "think step-by-step. Format your response exactly like this:\n"
            "THOUGHT_PROCESS:\n[Write your hidden reasoning here]\n"
            "FINAL_ANSWER:\n[Write your response to the user here]"
        )
        messages = [{"role": "system", "content": system_instruction}] + history[1:]
    else:
        messages = history

    try:
        print(f"   (Chaka is thinking using {model_conf['name']}...)")
        
        completion = client.chat.completions.create(
            model=model_conf["id"],
            messages=messages,
            temperature=0.6,
            max_tokens=2048,
            stop=None
        )
        
        raw_response = completion.choices[0].message.content
        thought, answer = extract_thought(raw_response)
        
        # Save only the CLEAN answer to history to save space
        history.append({"role": "assistant", "content": answer})
        
        return thought, answer

    except RateLimitError:
        return None, "⚠️ Brain overload! Give me 2 seconds..."
    except Exception as e:
        return None, f"❌ System Error: {str(e)}"

# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
if __name__ == "__main__":
    history = [{"role": "system", "content": "You are Chaka AI."}]
    
    print("\n=======================================")
    print("   CHAKA AI - ULTIMATE (v4.0)")
    print("=======================================")

    # 1. Select Model
    print("\nSELECT BRAIN TYPE:")
    for key, val in MODELS.items():
        print(f"{key}. {val['name']}")
    
    choice = input("\nChoose (1-3): ").strip()
    selected_model = MODELS.get(choice, MODELS["2"])
    
    print(f"\n✅ SYSTEM ACTIVE: {selected_model['name']}")
    if selected_model["type"] == "standard" and choice == "2":
        print("   (Note: 'Synthetic Thought' Engine Enabled)")

    # 2. Loop
    while True:
        try:
            user_text = input("\nYou: ")
            if user_text.lower() in ["exit", "quit"]: break
            
            thought, answer = chat_with_chaka(user_text, selected_model, history)
            
            if thought:
                print("\n💭 THOUGHT PROCESS (Hidden):")
                print("-----------------------------------")
                print(thought)
                print("-----------------------------------")
            
            print(f"\n🤖 CHAKA: {answer}")
            
        except KeyboardInterrupt:
            break
