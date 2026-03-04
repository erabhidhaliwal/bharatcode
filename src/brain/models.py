import os
import sys
import subprocess
import tempfile
from pathlib import Path

FREE_CODING_MODELS = {
    "openrouter": {
        "provider": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": [
            {"id": "minimax/MiniMax-M2.1", "name": "MiniMax-M2.1", "type": "coding"},
            {
                "id": "deepseek/deepseek-coder",
                "name": "DeepSeek-Coder",
                "type": "coding",
            },
            {
                "id": "qwen/qwen-coder-turbo",
                "name": "Qwen-Coder-Turbo",
                "type": "coding",
            },
            {"id": "openrouter/free", "name": "Free-Router", "type": "auto"},
        ],
    },
}


def get_default_model():
    return "minimax/MiniMax-M2.1"


def get_model_by_id(model_id):
    for provider, info in FREE_CODING_MODELS.items():
        for model in info["models"]:
            if model["id"] == model_id:
                return {
                    "provider": info["provider"],
                    "model": model["id"],
                    "base_url": info.get("base_url"),
                    "api_key_env": info.get("api_key_env"),
                }
    return None


def get_all_models():
    models = []
    for provider, info in FREE_CODING_MODELS.items():
        for model in info["models"]:
            models.append(
                {
                    "id": f"{provider}:{model['id']}",
                    "name": model["name"],
                    "type": model.get("type", "general"),
                }
            )
    return models
