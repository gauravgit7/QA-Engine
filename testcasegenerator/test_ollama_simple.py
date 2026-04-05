#!/usr/bin/env python3
"""Simple test for Ollama Llama3 integration."""

import requests
import json
import time

def test_ollama():
    print("Testing Ollama Llama3 integration...")

    # Test 1: Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running. Available models: {[m['name'] for m in models]}")

            # Check if llama3:latest is available
            llama3_available = any('llama3' in m['name'] for m in models)
            if llama3_available:
                print("✅ llama3 model is available")
            else:
                print("❌ llama3 model not found. Run: ollama pull llama3")
                return False
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False

    # Test 2: Test generation
    print("\nTesting text generation...")
    try:
        payload = {
            "model": "llama3:latest",
            "prompt": "Say hello in exactly 3 words.",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50
            }
        }

        start_time = time.time()
        response = requests.post("http://localhost:11434/api/generate",
                               json=payload, timeout=60)
        end_time = time.time()

        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').strip()
            print(f"✅ Generation successful in {end_time - start_time:.1f}s")
            print(f"Response: {response_text}")
            return True
        else:
            print(f"❌ Generation failed: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    if success:
        print("\n🎉 Ollama Llama3 integration test PASSED!")
        print("Your Llama3 setup is working correctly.")
    else:
        print("\n❌ Ollama Llama3 integration test FAILED!")
        print("Please check your Ollama setup.")