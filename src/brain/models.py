FREE_CODING_MODELS = {
    "ollama": {
        "provider": "ollama",
        "models": [
            "deepseek-coder-v2",
            "qwen2.5-coder",
            "codellama",
            "starcoder2",
            "phi4",
            "mistral",
            "llama3.3",
            "granite3.3",
            "WizardCoder",
            "SantaCoder",
        ],
    },
    "openrouter": {
        "provider": "openrouter",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": [
            "deepseek/deepseek-coder",
            "qwen/qwen-coder-turbo",
            "meta-llama/codellama-70b",
            "google/gemma-2-27b",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o-mini",
        ],
    },
    "siliconflow": {
        "provider": "siliconflow",
        "api_key_env": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": [
            "deepseek-ai/DeepSeek-Coder-V2-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "THUDM/GLM-4-Code-Assistant",
            "01-ai/Yi-34B-Coder",
            "meta-llama/Llama-3.3-70B-Instruct",
            "microsoft/WizardCoder-Python-34B-V1.0",
        ],
    },
    "zhipu": {
        "provider": "zhipu",
        "api_key_env": "ZHIPU_API_KEY",
        "models": [
            "glm-4",
            "glm-4-flash",
            "glm-4-plus",
            "glm-4-code",
        ],
    },
    "moonshot": {
        "provider": "moonshot",
        "api_key_env": "MOONSHOT_API_KEY",
        "models": [
            "kimi-k2.5",
            "kimi-k2.5-pro",
        ],
    },
    "minimax": {
        "provider": "minimax",
        "api_key_env": "MINIMAX_API_KEY",
        "models": [
            "MiniMax-M2.1",
            "MiniMax-M2.2",
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
            }
    return None
