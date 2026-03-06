"""
LangGraph LLM Wrapper
Simple wrapper for existing route_chat function
"""

import os
import json
from typing import List, Dict, Any, Optional, Callable, Generator

# Import the existing router
from brain.router import route_chat, chat_stream


DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def get_chat_model(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
):
    """
    Factory function to create a chat model (returns simple wrapper).
    """
    model = model or os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)
    return SimpleChatModel(
        model_name=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


class SimpleChatModel:
    """Simple chat model wrapper"""

    def __init__(self, model_name: str = DEFAULT_MODEL, temperature: float = 0.7, max_tokens: int = 4096):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        """Simple invoke method"""
        return route_chat(messages, model=self.model_name)

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """Callable interface"""
        return self.invoke(messages)


def create_chat_model(
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> SimpleChatModel:
    """Create a simple chat model"""
    return SimpleChatModel(
        model_name=model,
        temperature=temperature,
    )


# Convenient function to use in nodes
def chat_with_model(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Simple function to chat with the model.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (defaults to DEFAULT_MODEL)
        system_prompt: Optional system prompt to prepend

    Returns:
        The model's response content
    """
    model = model or os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)

    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    return route_chat(messages, model=model)


def chat_with_model_json(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Chat with the model and parse JSON response.
    """
    response = chat_with_model(messages, model, system_prompt)

    # Try to parse JSON from response
    try:
        # Find JSON in response
        start = response.find("{")
        if start >= 0:
            end = response.rfind("}") + 1
            if end > start:
                return json.loads(response[start:end])

        start = response.find("[")
        if start >= 0:
            end = response.rfind("]") + 1
            if end > start:
                return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass

    return {"raw": response, "parsed": False}


# Streaming version
def stream_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> Generator:
    """
    Stream chat responses.

    Returns:
        A generator that yields response chunks
    """
    model = model or os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)
    return chat_stream(messages, model=model)


__all__ = [
    "SimpleChatModel",
    "get_chat_model",
    "create_chat_model",
    "chat_with_model",
    "chat_with_model_json",
    "stream_chat",
    "DEFAULT_MODEL",
]
