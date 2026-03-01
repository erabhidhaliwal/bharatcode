import requests
import json

def ollama_chat(messages, model="starcoder2"):
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return f"Error: {str(e)}"
