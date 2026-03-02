# BharatCode CLI

An AI-powered coding agent that builds software projects from scratch.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r src/requirements.txt
   ```

2. Configure environment:
   Edit `src/.env` to set your API keys and select your engine.

## Configuration

In `src/.env`, you can choose your LLM engine and specific models for each agent:

```bash
LLM_ENGINE="ollama" # Options: 'zhipu' or 'ollama'

# Global Default Model for Ollama
OLLAMA_MODEL="starcoder2"

# Per-Agent Model Overrides (Ollama only)
PLANNER_MODEL="starcoder2"
EXECUTOR_MODEL="starcoder2"
REVIEWER_MODEL="starcoder2"
```

## Usage

Run the orchestrator:

```bash
python3 src/main.py
```
