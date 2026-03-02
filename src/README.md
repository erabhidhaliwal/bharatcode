# BharatCode CLI

Open-source, model-agnostic AI coding agent for terminal-based agentic engineering. Built similar to KILO CLI with support for 500+ free coding models.

## Features

- **Multi-Provider Model Support**: Ollama, OpenRouter, SiliconFlow, Zhipu (GLM), Moonshot, MiniMax
- **500+ Free Models**: Access to the best open-source coding models
- **Flexible Workflow Modes**: Plan, Execute, Review, or Auto (full pipeline)
- **Model Switching**: Change models on-the-fly with `/set` command
- **Keyboard-First CLI**: Terminal-native experience with rich UI

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bharatcode.git
cd bharatcode

# Install dependencies
pip install -r requirements.txt
pip install -r src/requirements.txt
```

## Configuration

Edit `src/.env` to configure your API keys and default model:

```bash
# Default model (format: provider:model)
DEFAULT_MODEL="ollama:starcoder2"

# Optional API Keys for cloud providers
ZHIPU_API_KEY="your-zhipu-key"
OPENROUTER_API_KEY="your-openrouter-key"
SILICONFLOW_API_KEY="your-siliconflow-key"
MOONSHOT_API_KEY="your-moonshot-key"
MINIMAX_API_KEY="your-minimax-key"
```

### Available Free Models

#### Ollama (Local)
- deepseek-coder-v2
- qwen2.5-coder
- codellama
- starcoder2
- phi4
- mistral
- llama3.3
- granite3.3
- WizardCoder
- SantaCoder

#### SiliconFlow (Free Tier)
- deepseek-ai/DeepSeek-Coder-V2-Instruct
- Qwen/Qwen2.5-Coder-32B-Instruct
- THUDM/GLM-4-Code-Assistant
- 01-ai/Yi-34B-Coder
- microsoft/WizardCoder-Python-34B-V1.0

#### Zhipu (GLM - Free)
- glm-4-flash
- glm-4-plus
- glm-4-code

#### OpenRouter (Free Tier)
- deepseek/deepseek-coder
- qwen/qwen-coder-turbo
- meta-llama/codellama-70b

## Usage

```bash
cd src && python main.py
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `/models` | List all available free models |
| `/set <model>` | Set default model (e.g., `/set ollama:deepseek-coder-v2`) |
| `/mode` | Choose workflow mode |
| `/clear` | Clear screen |
| `/help` | Show help |
| `exit` | Exit the CLI |

### Workflow Modes

- **Plan**: Break down tasks into steps
- **Execute**: Generate code and run tools
- **Review**: Review and finalize code
- **Auto**: Full agentic workflow (Plan → Execute → Review)

## Examples

```
# Set a specific model
/set siliconflow:deepseek-ai/DeepSeek-Coder-V2-Instruct

# List all models
/models

# Change to plan mode
/mode
```

## Architecture

```
src/
├── main.py           # CLI entry point
├── orchestrator.py   # Agent workflow orchestration
├── brain/
│   ├── router.py     # Model routing
│   ├── models.py     # Model registry
│   ├── ollama.py     # Ollama integration
│   └── glm.py        # Zhipu GLM integration
├── agents/
│   ├── planner.py    # Planning agent
│   ├── executor.py   # Execution agent
│   └── reviewer.py   # Review agent
└── tools/
    ├── registry.py   # Tool registry
    ├── file.py       # File operations
    └── shell.py      # Shell commands
```

## Requirements

- Python 3.8+
- Ollama (for local models)
- API keys for cloud providers (optional)

## License

MIT

## Inspired by

[KILO CLI](https://kilo.ai/cli) - Open-source AI coding agent
