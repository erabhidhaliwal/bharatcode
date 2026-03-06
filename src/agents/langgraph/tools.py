"""
LangGraph Tools
Convert file operations to LangChain @tool decorators
"""

import os
import json
import subprocess
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

# Import existing tools
from tools.file import (
    write_file as _write_file,
    read_file as _read_file,
    browse_folder,
    list_directory,
    read_file_details,
    write_file_content,
    create_directory,
    delete_item,
)


@tool
def write_file(path: str, content: str) -> str:
    """
    Write content to a file at the specified path.

    Args:
        path: The full path to the file (e.g., "src/main.py")
        content: The content to write to the file

    Returns:
        A success message with the file path
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Successfully wrote to {path}"


@tool
def read_file(path: str) -> str:
    """
    Read the content of a file.

    Args:
        path: The full path to the file

    Returns:
        The content of the file
    """
    with open(path, "r") as f:
        return f.read()


@tool
def list_files(path: str = ".") -> str:
    """
    List files in a directory.

    Args:
        path: The directory path to list (defaults to current directory)

    Returns:
        A JSON string with the list of files and their details
    """
    try:
        result = list_directory(path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def create_dir(path: str) -> str:
    """
    Create a directory.

    Args:
        path: The path of the directory to create

    Returns:
        A success message
    """
    os.makedirs(path, exist_ok=True)
    return f"Directory created: {path}"


@tool
def delete_file(path: str) -> str:
    """
    Delete a file or directory.

    Args:
        path: The path to delete

    Returns:
        A success message
    """
    try:
        result = delete_item(path)
        return json.dumps(result)
    except Exception as e:
        return f"Error deleting {path}: {str(e)}"


@tool
def search_files(path: str, pattern: str) -> str:
    """
    Search for files matching a pattern.

    Args:
        path: The directory to search in
        pattern: The search pattern (e.g., "*.py")

    Returns:
        A JSON string with matching files
    """
    try:
        from tools.file import search_files as _search_files
        result = _search_files(path, pattern)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def run_shell_command(command: str, timeout: int = 60) -> str:
    """
    Run a shell command and return the output.

    Args:
        command: The shell command to run
        timeout: Timeout in seconds (default: 60)

    Returns:
        The command output or error message
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nStderr: {result.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running command: {str(e)}"


@tool
def get_file_info(path: str) -> str:
    """
    Get information about a file.

    Args:
        path: The path to the file

    Returns:
        A JSON string with file information
    """
    try:
        result = get_file_info(path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def browse_directory() -> str:
    """
    Open a directory browser dialog to select a folder.

    Returns:
        The selected path or error message
    """
    try:
        result = browse_folder()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# Tool list for easy binding
TOOL_LIST = [
    write_file,
    read_file,
    list_files,
    create_dir,
    delete_file,
    search_files,
    run_shell_command,
    get_file_info,
    browse_directory,
]


def get_tools():
    """Get all available tools as a list"""
    return TOOL_LIST


def get_tools_dict():
    """Get tools as a dictionary for easy access"""
    return {tool.name: tool for tool in TOOL_LIST}


__all__ = [
    "write_file",
    "read_file",
    "list_files",
    "create_dir",
    "delete_file",
    "search_files",
    "run_shell_command",
    "get_file_info",
    "browse_directory",
    "TOOL_LIST",
    "get_tools",
    "get_tools_dict",
]
