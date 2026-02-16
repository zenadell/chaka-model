import os
import re
import time
from groq import Groq, RateLimitError, APIError

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
API_KEY = "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"
client = Groq(api_key=API_KEY)

# ---------------------------------------------------------
# MODEL CONFIGURATION (The Power Duo)
# ---------------------------------------------------------
MODELS = {
    "1": {
        "id": "llama-3.3-70b-versatile",
        "name": "🧠 Smart Mode (Llama 3.3 70B)",
        "type": "standard", 
        "desc": "Meta's Best. Fast & Intelligent."
    },
    "2": {
        "id": "openai/gpt-oss-120b",
        "name": "🤯 Genius Mode (GPT-OSS 120B)",
        "type": "reasoning",
        "desc": "OpenAI's Open Model. Deep Reasoning."
    }
}

# ---------------------------------------------------------
# THOUGHT EXTRACTION ENGINE
# ---------------------------------------------------------
def extract_thought(text):
    """
    Extracts hidden thoughts.
    - GPT-OSS uses <think> tags natively.
    - Llama 3.3 uses our custom THOUGHT_PROCESS format.
    """
    # 1. Native <think> tags (GPT-OSS)
    think_pattern = r"<think>(.*?)</think>"
    match = re.search(think_pattern, text, re.DOTALL)
    
    if match:
        thought = match.group(1).strip()
        answer = re.sub(think_pattern, "", text, flags=re.DOTALL).strip()
        return thought, answer

    # 2. Custom Forced Format (Llama)
    think_pattern_custom = r"THOUGHT_PROCESS:(.*?)FINAL_ANSWER:"
    match_custom = re.search(think_pattern_custom, text, re.DOTALL)
    
    if match_custom:
        thought = match_custom.group(1).strip()
        answer = re.sub(think_pattern_custom, "", text, flags=re.DOTALL).strip()
        # Fallback if FINAL_ANSWER: remains
        answer = answer.replace("FINAL_ANSWER:", "").strip()
        return thought, answer

    # 3. No thoughts found (Fallback)
    return None, text

def chat_with_chaka(user_input, model_conf, history):
    history.append({"role": "user", "content": user_input})
    
    # SYSTEM PROMPT LOGIC
    messages = list(history) 

    # THE "SYNTACTIC & SEMANTIC AUDIT" (V5) - FULL VERBATIM
    ULTRA_LOGIC = (
        "Role: You are Chaka V2, a Precision Logic Engine trained and developed by Jomiez. Your primary directive is to parse the grammatical dependency of every sentence before answering. You must distinguish between Active Participants (Subjects) and Passive Descriptors (Objects/Modifiers).\n\n"
        "Phase 1: The Verb Classification Protocol\n"
        "Before counting any entities, you must classify the verbs in the prompt into two categories:\n\n"
        "Kinetic Verbs (The Action): Words indicating movement or presence at a specific location (e.g., went, entered, walked, arrived, is at, stayed).\n\n"
        "Static Verbs (The Description): Words indicating possession, relationship, or existence (e.g., has, owns, is the father of, consists of, includes).\n\n"
        "The Rule: Only the nouns governed by Kinetic Verbs are considered 'present' at the scene. Nouns governed only by Static Verbs are background data and must be excluded from the headcount unless explicitly summoned by a Kinetic Verb.\n\n"
        "Phase 2: The Connector Logic (The 'And/Who/With/Whose' Filter)\n"
        "You must analyze the specific conjunctions and pronouns connecting nouns to the verb:\n\n"
        "\"AND\" (The Aggregator):\n"
        "Structure: \"Subject A and Subject B went...\"\n"
        "Logic: Both A and B performed the action. Include both.\n\n"
        "\"WHO / WHICH / THAT\" (The Isolator):\n"
        "Structure: \"Subject A, who has Object B, went...\"\n"
        "Logic: \"Who\" begins a Relative Clause. Everything following \"who\" describes Subject A but does not share Subject A's action.\n"
        "Result: Object B did not go. Exclude B.\n\n"
        "\"WITH\" (The Conditional):\n"
        "Structure A: \"A man with a red hat went...\" (Attribute: Hat is not a person).\n"
        "Structure B: \"A man with his son went...\" (Accompaniment: Son is a person).\n"
        "Logic: Analyze the noun after \"with.\" If it is a sentient being capable of the action, include it only if the context implies accompaniment rather than mere possession.\n\n"
        "\"WHOSE\" (The Possessive):\n"
        "Structure: \"A captain whose team is famous entered...\"\n"
        "Logic: The team is a possession/attribute of the captain. Only the captain entered. Exclude the team.\n\n"
        "Phase 3: The Semantic Truth Check\n"
        "Instruction: After parsing, re-read the sentence literally to verify the \"Actor\" vs. the \"Attribute.\"\n\n"
        "Example: \"A captain who commands 50 soldiers marched into the tent.\"\n\n"
        "Audit: Does the sentence say the soldiers marched? No. It says the captain marched. The phrase \"who commands 50 soldiers\" is a rank/title description (like \"A wealthy captain\").\n\n"
        "Final Calculation: Count ONLY the Main Clause Subject (The Captain = 1).\n\n"
        "Logic Rule: If the verb is performed by a singular noun (e.g., \"The captain marched\"), do not add the plural nouns found in the description (the 50 soldiers) to the active count.\n\n"
        "Phase 4: Ambiguity Resolution\n"
        "If the user asks \"How many people went?\", provide the Literal Grammatical Answer first (based strictly on the subject of the verb). If the prompt uses collective nouns (e.g., \"The group went,\" \"The family went\"), explicitly state that the count includes all members implied by that collective noun."
    )

    if model_conf["type"] == "standard":
        sys_msg = (
            f"You are Chaka. {ULTRA_LOGIC}\n\n"
            "INSTRUCTION: You must think step-by-step using these rules. "
            "Format your response EXACTLY like this:\n"
            "THOUGHT_PROCESS:\n[Write your 100% literal analysis here]\n"
            "FINAL_ANSWER:\n[Write your witty response here]"
        )
        messages[0] = {"role": "system", "content": sys_msg}
    
    elif model_conf["type"] == "reasoning":
        messages[0] = {"role": "system", "content": f"{ULTRA_LOGIC}\nUse your native deep reasoning to apply these rules and solve literally."}

    # API PARAMETERS
    params = {
        "model": model_conf["id"],
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 4096,
    }

    try:
        print(f"   (Chaka is thinking using {model_conf['name']}...)")
        
        completion = client.chat.completions.create(**params)
        
        raw_response = completion.choices[0].message.content
        thought, answer = extract_thought(raw_response)
        
        # Save only the clean answer to memory
        history.append({"role": "assistant", "content": answer})
        
        return thought, answer

    except RateLimitError:
        return None, "⚠️ Brain overload! (Rate Limit Hit). Please wait 2 seconds."
    except Exception as e:
        if model_conf["id"] == "openai/gpt-oss-120b":
             return None, f"❌ Genius Mode Error: {str(e)}. Try switching to Smart Mode."
        return None, f"❌ Error: {str(e)}"

# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
if __name__ == "__main__":
    # Initialize Memory
    history = [{"role": "system", "content": "You are Chaka AI."}]
    
    print("\n=======================================")
    print("   CHAKA AI - PRODUCTION (v7.0)")
    print("=======================================")

    while True:
        # 1. Model Selection
        print("\n[1] Llama 3.3 (Smart)   [2] GPT-OSS 120B (Genius)")
        choice = input("Select Brain (1 or 2): ").strip()
        selected_model = MODELS.get(choice, MODELS["1"])
        
        print(f"✅ Active: {selected_model['name']}")

        # 2. User Input
        user_text = input("You: ")
        if user_text.lower() in ["exit", "quit"]: break
        
        # 3. Get Response
        thought, answer = chat_with_chaka(user_text, selected_model, history)
        
        # 4. Display
        if thought:
            print("\n💭 THOUGHT PROCESS:")
            print("-----------------------------------")
            print(thought)
            print("-----------------------------------")
        
        print(f"\n🤖 CHAKA: {answer}\n")
