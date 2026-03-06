"""
LangGraph Module
Multi-agent system with typed state, checkpointing, and LangChain tools

Main Components:
- state: AgentState TypedDict for state management
- llm: LLM wrapper for LangChain integration
- tools: LangChain tools for file operations
- nodes: Planner, Executor, Reviewer, Designer nodes
- edges: Conditional routing logic
- graph: StateGraph construction
- memory: Checkpointing and long-term memory
- orchestrator: Main entry point
"""

from .state import AgentState, get_initial_state, should_continue_loop
from .llm import (
    SimpleChatModel,
    get_chat_model,
    chat_with_model,
    chat_with_model_json,
    stream_chat,
    DEFAULT_MODEL,
)
from .tools import (
    write_file,
    read_file,
    list_files,
    create_dir,
    delete_file,
    search_files,
    run_shell_command,
    get_tools,
    get_tools_dict,
)
from .nodes import (
    planner_node,
    analyze_dependencies,
    executor_node,
    execute_single_task,
    reviewer_node,
    check_quality_threshold,
    apply_improvements,
    designer_node,
    generate_html,
)
from .edges import (
    should_continue,
    route_phase,
    check_human_feedback,
    should_retry_execution,
    is_human_review_needed,
)
from .graph import create_graph, get_compiled_graph, run_workflow, LANGGRAPH_AVAILABLE
from .memory import (
    create_sqlite_checkpointer,
    create_memory_checkpointer,
    get_default_checkpointer,
    LongTermMemory,
    get_longterm_memory,
)
from .orchestrator import (
    LangGraphOrchestrator,
    create_orchestrator,
    get_orchestrator,
    USE_LANGGRAPH,
)

__version__ = "1.0.0"

__all__ = [
    # State
    "AgentState",
    "get_initial_state",
    "should_continue_loop",
    # LLM
    "SimpleChatModel",
    "get_chat_model",
    "chat_with_model",
    "chat_with_model_json",
    "stream_chat",
    "DEFAULT_MODEL",
    # Tools
    "write_file",
    "read_file",
    "list_files",
    "create_dir",
    "delete_file",
    "search_files",
    "run_shell_command",
    "get_tools",
    "get_tools_dict",
    # Nodes
    "planner_node",
    "analyze_dependencies",
    "executor_node",
    "execute_single_task",
    "reviewer_node",
    "check_quality_threshold",
    "apply_improvements",
    "designer_node",
    "generate_html",
    # Edges
    "should_continue",
    "route_phase",
    "check_human_feedback",
    "should_retry_execution",
    "is_human_review_needed",
    # Graph
    "create_graph",
    "get_compiled_graph",
    "run_workflow",
    "LANGGRAPH_AVAILABLE",
    # Memory
    "create_sqlite_checkpointer",
    "create_memory_checkpointer",
    "get_default_checkpointer",
    "LongTermMemory",
    "get_longterm_memory",
    # Orchestrator
    "LangGraphOrchestrator",
    "create_orchestrator",
    "get_orchestrator",
    "USE_LANGGRAPH",
]
