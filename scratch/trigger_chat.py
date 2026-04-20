import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def trigger_chat():
    payload = {
        "user_id": "user_123",
        "session_id": "sess_456",
        "feature": "search",
        "message": "test message"
    }
    try:
        r = httpx.post(f"{BASE_URL}/chat", json=payload, timeout=20.0)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_chat()
