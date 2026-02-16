import os
import base64
from groq import Groq

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Paste your FREE Groq key here
API_KEY = "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"
# Path to the local test image
IMAGE_PATH = "/Users/mac/.gemini/antigravity/brain/56129b0e-c405-46d6-8f44-f585f793ea22/test_cat_1771174268977.png"

client = Groq(api_key=API_KEY)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_intelligence():
    print("\n🧠 Testing Intelligence (Llama 3.3 70B)...")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Very smart reasoning model
            messages=[
                {
                    "role": "user",
                    "content": "I am a developer building an AI called Chaka. Prove you are smart: Explain the difference between 'quantization' and 'distillation' in 1 sentence."
                }
            ],
            temperature=0.5,
        )
        print(f"🤖 Answer: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_vision():
    print("\n👁️ Testing Vision/Multimodal (Llama 4 Scout 17B)...")
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: Local image not found at {IMAGE_PATH}")
        return

    try:
        base64_image = encode_image(IMAGE_PATH)
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # The Multimodal model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image? Be specific."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=1,
            max_tokens=1024,
        )
        print(f"🤖 Vision Description: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_intelligence()
    test_vision()
