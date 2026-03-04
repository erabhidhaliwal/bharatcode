import os
import requests
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

DEFAULT_MODEL = "minimax/MiniMax-M2.1"


def chat_completion(messages, model=None, api_key=None):
    if not model:
        model = DEFAULT_MODEL

    return openrouter_chat(messages, model, api_key)


def openrouter_chat(messages, model, api_key):
    if not api_key:
        return {
            "error": True,
            "content": "API key required. Get free key: https://openrouter.ai/settings/keys",
        }

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://bharatcode.local",
        "X-Title": "BharatCode",
    }
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code != 200:
            try:
                error_data = response.json()
                return {
                    "error": True,
                    "content": f"API Error: {error_data.get('error', {}).get('message', 'Unknown')}",
                }
            except:
                return {
                    "error": True,
                    "content": f"HTTP {response.status_code}: {response.text[:200]}",
                }

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return {
                "error": False,
                "content": result["choices"][0]["message"]["content"],
            }
        else:
            return {"error": True, "content": f"Unexpected response: {result}"}

    except requests.exceptions.Timeout:
        return {"error": True, "content": "Request timed out. Try again."}
    except Exception as e:
        return {"error": True, "content": f"Error: {str(e)}"}


def route_chat(messages, model=None):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not model:
        model = DEFAULT_MODEL

    result = openrouter_chat(messages, model, api_key)

    if result.get("error"):
        return result["content"]

    return result["content"]
