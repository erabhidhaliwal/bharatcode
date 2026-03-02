import ollama

def ollama_chat(messages, model="starcoder2"):
    try:
        # Use the official Ollama client for better performance and streaming support if needed later.
        response = ollama.chat(
            model=model,
            messages=messages,
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ Ollama SDK Error: {e}")
        return f"Error: {str(e)}"
