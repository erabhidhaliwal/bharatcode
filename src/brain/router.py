import os
from brain.glm import glm_chat
from brain.ollama import ollama_chat

def route_chat(messages, model=None):
    engine = os.getenv("LLM_ENGINE", "zhipu").lower()
    
    if engine == "ollama":
        # Use provided model or fallback to env variable or default
        selected_model = model or os.getenv("OLLAMA_MODEL", "starcoder2")
        return ollama_chat(messages, model=selected_model)
    else:
        # Note: Zhipu model override could be added to glm_chat similarly if needed
        return glm_chat(messages)
