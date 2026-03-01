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
            timeout=120, # Higher timeout for stability
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ ZhipuAI SDK Error: {e}")
        return f"Error: {str(e)}"