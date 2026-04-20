import httpx

BASE_URL = "http://127.0.0.1:8000"

def check_metrics():
    try:
        r = httpx.get(f"{BASE_URL}/metrics", timeout=5.0)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_metrics()
