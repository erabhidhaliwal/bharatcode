FREE_CODING_MODELS = {
    "ollama": {
        "provider": "ollama",
        "api_key_required": False,
        "models": [
            "deepseek-coder-v2",
            "qwen2.5-coder",
            "codellama",
            "starcoder2",
            "phi4",
            "mistral",
            "llama3.3",
            "llama3.2",
            "llama3.1",
            "llama3",
            "granite3.3",
            "WizardCoder",
            "SantaCoder",
            "command-r",
            "phi3.5",
            "gemma2",
            "aya",
            "codegemma",
        ],
    },
    "openrouter": {
        "provider": "openrouter",
        "api_key_env": "OPENROUTER_API_KEY",
        "api_key_required": True,
        "free_credits": True,
        "models": [
            "deepseek/deepseek-coder",
            "qwen/qwen-coder-turbo",
            "google/gemma-2-27b",
            "microsoft/phi-4",
            "minimax/MiniMax-M2.5",
            "minimax/MiniMax-M2.1",
        ],
    },
    "siliconflow": {
        "provider": "siliconflow",
        "api_key_env": "SILICONFLOW_API_KEY",
        "api_key_required": True,
        "base_url": "https://api.siliconflow.cn/v1",
        "models": [
            "deepseek-ai/DeepSeek-Coder-V2-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "THUDM/GLM-4-Flash",
            "01-ai/Yi-34B-Coder",
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
