# DishuAi CLI

An AI-powered coding agent that builds software projects from scratch.

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Usage

To build a project:
```bash
dishu build "Create a python script that counts words in a text file"
```
