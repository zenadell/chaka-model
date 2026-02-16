import os
from openai import OpenAI
import sys

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Replace this with your actual OpenRouter Key
API_KEY = "YOUR_OPENROUTER_KEY_HERE" 

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "https://chaka-ai.com",
        "X-Title": "Chaka AI Test"
    }
)

def talk_to_kimi(prompt):
    print(f"⚡ Connecting to Kimi K2.5 with prompt: '{prompt}'...")
    print("   (This may take a moment as the model 'thinks')...\n")

    try:
        completion = client.chat.completions.create(
            # The specific ID for Kimi K2.5
            model="moonshotai/kimi-k2.5", 
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # This extra body parameter ensures reasoning/thinking is enabled
            extra_body={
                "include_reasoning": True
            }
        )
        
        # Extracting the response
        answer = completion.choices[0].message.content
        
        print("🤖 Kimi K2.5 says:")
        print("---------------------------------------------------")
        print(answer)
        print("---------------------------------------------------")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    # A riddle to test its reasoning logic
    riddle = "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?"
    talk_to_kimi(riddle)
