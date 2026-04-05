"""Quick API test for the UAT generation engine using Ollama LLaMA 3."""
import requests
import json
import time

BASE = "http://localhost:8001"

print("1. Authenticating as admin...")
r = requests.post(f"{BASE}/auth/login", json={
    "email": "admin@firstfintech.com",
    "password": "admin123"
})
if r.status_code != 200:
    print(f"Failed to login: {r.text}")
    exit(1)
token = r.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print("   [OK] Token received")

print("\n2. Configuring 'ollama' as the AI API Key...")
config_req = requests.post(
    f"{BASE}/config/save",
    json={"llm_api_key": "ollama"},
    headers=headers
)
if config_req.status_code != 200:
    print(f"Failed to update config: {config_req.text}")
    exit(1)
print("   [OK] Configuration updated!")

print("\n3. Sending LLM Test Case Request to local Ollama...")
t0 = time.time()
formdata = {
    "text": "As a premium subscriber, I want to download video courses for offline viewing so that I can learn without an internet connection.",
    "generation_method": "llm"
}

try:
    # Use the /generate/story endpoint for a faster test run using LLM
    r2 = requests.post(f"{BASE}/generate/story", data=formdata, headers=headers, timeout=60)
    
    if r2.status_code != 200:
        print(f"   [FAIL] API Error {r2.status_code}: {r2.text}")
        exit(1)
        
    resp = r2.json()
    t1 = time.time()
    
    print(f"   [OK] Success: {resp['success']}")
    print(f"   [OK] Total Generated: {resp.get('total_generated', len(resp.get('testCases', [])))}")
    print(f"   [OK] Method Used: {resp['method_used']}")
    if resp.get('fallback_triggered', False):
        print(f"   [WARNING] Fallback was triggered! Reason: {resp.get('fallback_reason')}")
    else:
        print(f"   [OK] Generation Time: {t1 - t0:.2f}s")
        print(f"   [OK] LLM Tokens Evaluated: {resp.get('token_usage', 0)}")

    print(f"\n--- First 3 Generated Test Cases ---")
    for i, tc in enumerate(resp.get("testCases", [])[:3]):
        print(f"  {i+1}. {tc.get('id', 'N/A')} [{tc.get('test_type', 'N/A')}] - {tc.get('title', 'N/A')}")
        
except requests.exceptions.Timeout:
    print("\n   [TIMEOUT] The request took longer than 60 seconds! Is Ollama actively downloading the Llama3 model or heavily using CPU?")
except requests.exceptions.ConnectionError:
    print("\n   [CONNECTION ERROR] Could not connect to the backend server. Is it running?")
