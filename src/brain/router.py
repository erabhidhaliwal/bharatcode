import os
import json
import requests
from brain.models import get_model_by_id, FREE_CODING_MODELS
from brain.ollama import ollama_chat


def stream_response(response_text):
    """Generator to stream response character by character for better UX"""
    for char in response_text:
        yield char


def openrouter_chat(messages, model, api_key, stream=False):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
    }
    if stream:
        data["stream"] = True
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def siliconflow_chat(
    messages, model, api_key, base_url="https://api.siliconflow.cn/v1", stream=False
):
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
    }
    if stream:
        data["stream"] = True
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def zhipu_chat(messages, model="glm-4-flash"):
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return "Error: ZHIPU_API_KEY not set"

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")

        if response.status_code != 200:
            try:
                error_msg = response.json()
                return f"Error: {response.status_code} - {error_msg}"
            except:
                return f"Error: {response.status_code} - {response.text}"
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def moonshot_chat(messages, model="kimi-k2.5"):
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return "Error: MOONSHOT_API_KEY not set\n\nGet free key: https://platform.moonshot.cn/"

    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            error_msg = response.json()
            return f"Error: {response.status_code} - {error_msg}"
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def minimax_chat(messages, model="MiniMax-M2.1"):
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return "Error: MINIMAX_API_KEY not set\n\nGet free key: https://platform.minimax.ai/"

    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")

        if response.status_code != 200:
            try:
                error_msg = response.json()
                return f"Error: {response.status_code} - {error_msg}"
            except:
                return f"Error: {response.status_code} - {response.text}"
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "completion_message" in result:
            return result["completion_message"]["content"]
        elif "text" in result:
            return result["text"]
        else:
            return f"Error: Unexpected response format: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def route_chat(messages, model=None):
    model_id = model or os.getenv("DEFAULT_MODEL", "ollama:starcoder2")

    if ":" in model_id:
        model_info = get_model_by_id(model_id)
        if model_info:
            provider = model_info["provider"]
            model_name = model_info["model"]

            if provider == "ollama":
                return ollama_chat(messages, model=model_name)
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    return "Error: OPENROUTER_API_KEY not set\n\nGet free key: https://openrouter.ai/settings/keys"
                return openrouter_chat(messages, model=model_name, api_key=api_key)
            elif provider == "siliconflow":
                api_key = os.getenv("SILICONFLOW_API_KEY")
                if not api_key:
                    return "Error: SILICONFLOW_API_KEY not set\n\nGet free key: https://siliconflow.cn/"
                return siliconflow_chat(
                    messages,
                    model=model_name,
                    api_key=api_key,
                    base_url=model_info.get("base_url"),
                )
            elif provider == "zhipu":
                return zhipu_chat(messages, model=model_name)
            elif provider == "moonshot":
                return moonshot_chat(messages, model=model_name)
            elif provider == "minimax":
                api_key = os.getenv("MINIMAX_API_KEY")
                if not api_key:
                    return "Error: MINIMAX_API_KEY not set\n\nGet free key: https://platform.minimax.ai/\n\nThen run: /set MINIMAX_API_KEY=your-key-here"
                return minimax_chat(messages, model=model_name)

    engine = os.getenv("LLM_ENGINE", "ollama").lower()

    if engine == "ollama":
        selected_model = os.getenv("OLLAMA_MODEL", "starcoder2")
        return ollama_chat(messages, model=selected_model)
    elif engine == "zhipu":
        return zhipu_chat(messages)
    elif engine == "minimax":
        return minimax_chat(messages)
    else:
        return glm_chat(messages)


def glm_chat(messages, model="glm-4-flash"):
    return zhipu_chat(messages, model=model)
