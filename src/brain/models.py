FREE_CODING_MODELS = {
    "ollama": {
        "provider": "ollama",
        "api_key_required": False,
        "models": [
            "starcoder2",
            "deepseek-coder-v2",
            "qwen2.5-coder",
            "codellama",
            "llama3.3",
            "llama3.2",
            "phi4",
            "mistral",
            "glm-5",
        ],
    },
}


def get_available_models():
    models = []
    for provider, info in FREE_CODING_MODELS.items():
        for model in info["models"]:
            models.append(
                {
                    "id": f"{provider}:{model}",
                    "name": model,
                    "provider": provider,
                    "free": not info.get("api_key_required", False),
                }
            )
    return models


def get_free_models():
    """Get only models that don't require API key"""
    models = []
    for provider, info in FREE_CODING_MODELS.items():
        if not info.get("api_key_required", False):
            for model in info["models"]:
                models.append(
                    {
                        "id": f"{provider}:{model}",
                        "name": model,
                        "provider": provider,
                    }
                )
    return models


def get_model_by_id(model_id):
    if ":" not in model_id:
        return None
    provider, model = model_id.split(":", 1)
    if provider in FREE_CODING_MODELS:
        info = FREE_CODING_MODELS[provider]
        if model in info.get("models", []):
            return {
                "provider": info["provider"],
                "model": model,
                "api_key_env": info.get("api_key_env"),
                "base_url": info.get("base_url"),
                "api_key_required": info.get("api_key_required", False),
            }
    return None
