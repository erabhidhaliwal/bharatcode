import os
from brain.glm import glm_chat
from brain.ollama import ollama_chat

def route_chat(messages):
    engine = os.getenv("LLM_ENGINE", "zhipu").lower()
    
    if engine == "ollama":
        model = os.getenv("OLLAMA_MODEL", "starcoder2")
        return ollama_chat(messages, model=model)
    else:
        return glm_chat(messages)
