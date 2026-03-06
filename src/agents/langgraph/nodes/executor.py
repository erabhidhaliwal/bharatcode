"""
LangGraph Executor Node
Converts ExpertAutonomousAgent logic to LangGraph node with tools
"""

import json
from typing import Dict, Any, Optional
from langchain_core.utils.function_calling import convert_to_openai_function
from ..state import AgentState
from ..llm import chat_with_model, chat_with_model_json
from ..tools import get_tools


# Executor system prompt
EXECUTOR_SYSTEM_PROMPT = """You are an EXPERT EXECUTOR - a senior engineer executing complex tasks.

Your execution style:
- Write production-ready code
- Handle edge cases
- Implement error handling
- Add logging and monitoring
- Consider performance
- Ensure security
- Follow best practices

When given a task, you should:
1. Understand the requirements
2. Plan the implementation
3. Write the code
4. Handle errors gracefully

Use the available tools to create files and run commands."""


def executor_node(state: AgentState) -> AgentState:
    """
    Executor node - executes tasks using available tools.
    """
    user_request = state.get("user_request", "")
    plan = state.get("plan", {})
    project_name = state.get("project_name", "Project")
    current_task = state.get("current_task", user_request)
    iteration = state.get("iteration", 0)

    print(f"\n{'='*60}")
    print(f"EXECUTOR NODE - Iteration {iteration + 1}")
    print(f"{'='*60}")
    print(f"Project: {project_name}")
    print(f"Task: {current_task[:80]}...")

    # Build context from plan
    context_parts = []
    if plan:
        context_parts.append(f"Project Plan: {json.dumps(plan)[:500]}")
    if state.get("phases"):
        context_parts.append(f"Phases: {len(state['phases'])} phases defined")

    context = "\n\n".join(context_parts) if context_parts else "No plan available"

    # Executor prompt
    prompt = f"""{EXECUTOR_SYSTEM_PROMPT}

Project: {project_name}
User Request: {user_request}

Context:
{context}

Execute this task and create the necessary files.
Return your response in this format:
ACTION: <CODE|COMMAND|ANALYSIS>

For CODE action:
LANGUAGE: <python|javascript|go|rust>
FILENAME: path/to/file
```language
[complete code]
```

For COMMAND action:
COMMAND: [shell command]
EXPLANATION: why this command

For ANALYSIS action:
ANALYSIS: [detailed analysis]"""

    # Call LLM
    response = chat_with_model(
        [{"role": "user", "content": prompt}],
        system_prompt=EXECUTOR_SYSTEM_PROMPT,
    )

    # Parse response and extract code/commands
    execution_result = _parse_execution_response(response, project_name)

    # Update state
    state["execution_results"] = state.get("execution_results", []) + [execution_result]

    if execution_result.get("files_created"):
        state["files_created"] = state.get("files_created", []) + execution_result.get("files_created", [])

    if execution_result.get("project_path"):
        state["project_path"] = execution_result["project_path"]

    state["current_phase"] = "reviewing"

    # Add message
    state["messages"] = state.get("messages", []) + [
        {"role": "assistant", "content": f"Execution completed: {execution_result.get('summary', 'Done')}"}
    ]

    print(f"✓ Execution completed")
    if execution_result.get("files_created"):
        print(f"  Files created: {len(execution_result['files_created'])}")

    return state


def _parse_execution_response(response: str, project_name: str) -> Dict[str, Any]:
    """Parse the execution response to extract code/commands"""
    result = {
        "raw_response": response,
        "action": None,
        "files_created": [],
        "commands_run": [],
        "project_path": "",
        "summary": "Execution completed",
    }

    # Determine action type
    if "ACTION: CODE" in response.upper():
        result["action"] = "code"
    elif "ACTION: COMMAND" in response.upper():
        result["action"] = "command"
    elif "ACTION: ANALYSIS" in response.upper():
        result["action"] = "analysis"
    else:
        result["action"] = "unknown"

    # Extract code blocks
    import re
    code_blocks = re.findall(r"```(\w+)?\n(.*?)\n```", response, re.DOTALL)

    for lang, code in code_blocks:
        # Try to extract filename
        filename_match = re.search(r"FILENAME:\s*(.+?)(?:\n|$)", response)
        if filename_match:
            filepath = filename_match.group(1).strip()
            # Write the file
            try:
                import os
                os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
                with open(filepath, "w") as f:
                    f.write(code)
                result["files_created"].append(filepath)
            except Exception as e:
                result["error"] = f"Error writing file: {e}"

    # Extract commands
    cmd_match = re.search(r"COMMAND:\s*(.+?)(?:\n|$)", response)
    if cmd_match:
        result["commands_run"].append(cmd_match.group(1).strip())

    return result


def execute_single_task(state: AgentState) -> AgentState:
    """
    Execute a single task from the pending tasks list.
    """
    tasks_pending = state.get("tasks_pending", [])

    if not tasks_pending:
        state["current_phase"] = "reviewing"
        return state

    # Get next task
    current_task = tasks_pending[0]
    remaining_tasks = tasks_pending[1:]

    state["current_task"] = current_task
    state["tasks_pending"] = remaining_tasks

    # Execute the task
    user_request = state.get("user_request", "")
    project_name = state.get("project_name", "Project")

    prompt = f"""Execute this task:

Task: {current_task}

Project: {project_name}
Original Request: {user_request}

Create the necessary code files. Use CODE format with FILENAME."""

    response = chat_with_model(
        [{"role": "user", "content": prompt}],
        system_prompt=EXECUTOR_SYSTEM_PROMPT,
    )

    # Parse and create files
    execution_result = _parse_execution_response(response, project_name)

    # Update state
    state["execution_results"] = state.get("execution_results", []) + [execution_result]
    state["tasks_completed"] = state.get("tasks_completed", []) + [current_task]

    if execution_result.get("files_created"):
        state["files_created"] = state.get("files_created", []) + execution_result["files_created"]

    # Check if more tasks remain
    if not remaining_tasks:
        state["current_phase"] = "reviewing"

    return state


__all__ = ["executor_node", "execute_single_task"]
