import requests
import json
import time

URL = "http://127.0.0.1:5001/api/chat"
HEADERS = {
    "Content-Type": "application/json",
    "X-Chaka-API-Key": "Chaka_Supreme_Access"
}

def test_pipeline():
    print("--- STARTING PIPELINE TEST ---")
    session_id = f"test_session_{int(time.time())}"
    
    # 1. Successful message
    print("\n1. Sending valid message to set context...")
    payload1 = {
        "message": "Hello! Please remember that my favorite color is Quantum Blue.",
        "model": "chaka-low",
        "session_id": session_id
    }
    res1 = requests.post(URL, headers=HEADERS, json=payload1)
    print(f"Status: {res1.status_code}")
    print(f"Response: {res1.json().get('response', res1.json())}")
    
    # 2. Intentional failure
    print("\n2. Sending intentional failure (invalid model) to test history pop...")
    payload2 = {
        "message": "Can you repeat my favorite color? (This should fail and NOT be appended)",
        "model": "fake-model",
        "session_id": session_id
    }
    res2 = requests.post(URL, headers=HEADERS, json=payload2)
    print(f"Status: {res2.status_code}")
    print(f"Response Error: {res2.json().get('error', 'No error field')}")
    
    # 3. Follow-up successful message
    print("\n3. Sending valid message to see if pipeline is frozen or clean...")
    payload3 = {
        "message": "Can you tell me what my favorite color is?",
        "model": "chaka-low",
        "session_id": session_id
    }
    res3 = requests.post(URL, headers=HEADERS, json=payload3)
    print(f"Status: {res3.status_code}")
    print(f"Final Response: {res3.json().get('response', res3.json())}")
    
    if res3.status_code == 200 and "Quantum Blue" in res3.json().get('response', ''):
        print("\n✅ PIPELINE IS CLEAN! History was successfully managed and context retained.")
    elif res3.status_code == 200:
        print("\n⚠️ PIPELINE CLEAN but context was lost! Check history logic.")
    else:
        print("\n❌ PIPELINE IS STILL FROZEN! Received an error.")

if __name__ == "__main__":
    test_pipeline()
