# src/bharatcode/brain/glm.py

import os
import requests

def glm_chat(messages):
    api_key = os.getenv("ZHIPU_API_KEY")
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "GLM-4.7-Flash",
        "messages": messages
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = res.json()
        if "choices" not in res_json:
            print(f"❌ API Error: {res_json}")
            return f"Error: {res_json.get('error', 'Unknown API error')}"
        return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return f"Error: {str(e)}"