import os
from zhipuai import ZhipuAI

def glm_chat(messages):
    api_key = os.getenv("ZHIPU_API_KEY")
    client = ZhipuAI(api_key=api_key)
    
    try:
        # Using the official SDK for better stability and automatic retries.
        response = client.chat.completions.create(
            model="GLM-4.7-Flash",
            messages=messages,
            timeout=60, 
        )
        return response.choices[0].message.content
    except Exception as e:
        if "429" in str(e) or "1302" in str(e):
            print("⚠️  ZhipuAI Rate Limit reached. Please wait a moment or switch to Ollama.")
            return "Error: ZhipuAI Rate Limit reached."
        print(f"❌ ZhipuAI SDK Error: {e}")
        return f"Error: {str(e)}"