import os
import requests
from brain.models import get_model_by_id, get_default_model

DEFAULT_MODEL = "openrouter/free"


def chat_completion(messages, model=None, api_key=None, provider="openrouter"):
    if not model:
        model = DEFAULT_MODEL

    if provider == "openrouter":
        return openrouter_chat(messages, model, api_key)
    elif provider == "cohere":
        return cohere_chat(messages, model, api_key)
    else:
        return openrouter_chat(messages, model, api_key)


def openrouter_chat(messages, model, api_key):
    if not api_key:
        return {
            "error": True,
            "message": "API key required. Get free key: https://openrouter.ai/settings/keys\n\nFree $1 credit on signup!",
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
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            try:
                error_data = response.json()
                return {
                    "error": True,
                    "message": f"API Error ({response.status_code}): {error_data.get('error', {}).get('message', 'Unknown error')}",
                }
            except:
                return {
                    "error": True,
                    "message": f"HTTP {response.status_code}: {response.text[:200]}",
                }

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return {
                "error": False,
                "content": result["choices"][0]["message"]["content"],
            }
        else:
            return {"error": True, "message": f"Unexpected response: {result}"}

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "Request timed out. Try again or use a different model.",
        }
    except Exception as e:
        return {"error": True, "message": f"Error: {str(e)}"}


def cohere_chat(messages, model, api_key):
    if not api_key:
        return {
            "error": True,
            "message": "API key required. Get free key: https://cohere.ai/",
        }

    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    chat_history = []
    system = None
    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            chat_history.append({"role": msg["role"], "message": msg["content"]})

    data = {
        "model": model,
        "chat_history": chat_history,
    }
    if system:
        data["system_prompt"] = system

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            return {"error": True, "message": "API Error: " + response.text[:200]}

        result = response.json()
        return {"error": False, "content": result.get("text", str(result))}
    except Exception as e:
        return {"error": True, "message": f"Error: {str(e)}"}


def route_chat(messages, model=None):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not model:
        model = DEFAULT_MODEL

    result = openrouter_chat(messages, model, api_key)

    if result.get("error"):
        return result["message"]

    return result["content"]
