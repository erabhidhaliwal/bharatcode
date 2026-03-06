"""
LangGraph Orchestrator
Main entry point with execute() and resume methods
Toggle between LangGraph and legacy modes
"""

import os
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime

from .state import AgentState, get_initial_state
from .graph import create_graph, get_compiled_graph, run_workflow, LANGGRAPH_AVAILABLE
from .memory import (
    create_sqlite_checkpointer,
    create_memory_checkpointer,
    get_default_checkpointer,
    get_longterm_memory,
    get_project_memory,
)
from .llm import get_chat_model, chat_with_model, stream_chat


class LangGraphOrchestrator:
    """
    Main orchestrator using LangGraph architecture.
    Provides human-in-the-loop capabilities and checkpointing.
    """

    def __init__(
        self,
        use_checkpointer: bool = True,
        use_longterm_memory: bool = True,
        project_name: Optional[str] = None,
    ):
        """
        Initialize the LangGraph orchestrator.

        Args:
            use_checkpointer: Enable checkpointing for human-in-the-loop
            use_longterm_memory: Enable long-term memory
            project_name: Optional project name
        """
        self.project_name = project_name
        self.use_checkpointer = use_checkpointer and LANGGRAPH_AVAILABLE
        self.use_longterm_memory = use_longterm_memory

        # Set up checkpointer
        self.checkpointer = None
        if self.use_checkpointer:
            try:
                self.checkpointer = get_default_checkpointer()
            except Exception as e:
                print(f"Warning: Could not create checkpointer: {e}")

        # Set up long-term memory
        self.longterm_memory = None
        if self.use_longterm_memory:
            try:
                self.longterm_memory = get_longterm_memory()
            except Exception as e:
                print(f"Warning: Could not create longterm memory: {e}")

        # Set up project memory (legacy compatibility)
        self.project_memory = get_project_memory()

        # Thread ID for checkpointing
        self.thread_id = project_name or "default"

        # Current state
        self.current_state: Optional[AgentState] = None

    def execute(
        self,
        user_request: str,
        project_name: Optional[str] = None,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute a task using the LangGraph workflow.

        Args:
            user_request: The user's request
            project_name: Optional project name
            max_iterations: Maximum iterations for quality improvement

        Returns:
            Final state with results
        """
        if not LANGGRAPH_AVAILABLE:
            return {
                "error": "LangGraph not available. Please install langgraph.",
                "user_request": user_request,
            }

        project_name = project_name or self.project_name or "Project"

        print("\n" + "=" * 60)
        print("LANGGRAPH ORCHESTRATOR")
        print("=" * 60)
        print(f"Project: {project_name}")
        print(f"Request: {user_request[:80]}...")

        # Create initial state
        initial_state = get_initial_state(
            user_request=user_request,
            project_name=project_name,
            max_iterations=max_iterations,
        )

        # Get compiled graph
        graph = get_compiled_graph(self.checkpointer)

        if graph is None:
            return {"error": "Could not create graph", **initial_state}

        # Run the workflow
        config = {"configurable": {"thread_id": self.thread_id}}

        try:
            result = graph.invoke(initial_state, config=config)
            self.current_state = result

            # Save to long-term memory
            if self.longterm_memory and result.get("files_created"):
                self.longterm_memory.add_project(
                    project_name,
                    {
                        "request": user_request,
                        "files": result.get("files_created", []),
                        "quality_score": result.get("quality_score", 0),
                    },
                )

            return result

        except Exception as e:
            print(f"Error in workflow: {e}")
            return {
                **initial_state,
                "error": str(e),
                "current_phase": "error",
            }

    def resume(
        self,
        feedback: str,
        checkpoint_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resume from a human review checkpoint.

        Args:
            feedback: Human feedback to incorporate
            checkpoint_id: Optional checkpoint ID to resume from

        Returns:
            Updated state after resuming
        """
        if not self.checkpointer:
            return {"error": "No checkpointer available"}

        thread_id = checkpoint_id or self.thread_id

        # Create state with feedback
        state = self.current_state or get_initial_state(
            user_request="",
            project_name=self.project_name,
        )

        state["human_feedback"] = feedback
        state["current_phase"] = "executing"

        # Get graph and continue
        graph = get_compiled_graph(self.checkpointer)

        if graph is None:
            return {"error": "Could not create graph"}

        result = graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
        self.current_state = result

        return result

    async def execute_streaming(
        self,
        user_request: str,
        project_name: Optional[str] = None,
        max_iterations: int = 5,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute with streaming events.

        Args:
            user_request: The user's request
            project_name: Optional project name
            max_iterations: Maximum iterations

        Yields:
            Event dictionaries with updates
        """
        # Streaming implementation would go here
        # For now, yield nothing
        return
        yield

    def get_checkpoint_list(self) -> list:
        """Get list of available checkpoints"""
        if not self.checkpointer:
            return []
        return []

    def get_state(self) -> Optional[AgentState]:
        """Get current state"""
        return self.current_state


def create_orchestrator(
    use_langgraph: bool = True,
    project_name: Optional[str] = None,
) -> "LangGraphOrchestrator":
    """
    Factory function to create an orchestrator.

    Args:
        use_langgraph: Whether to use LangGraph (True) or legacy (False)
        project_name: Optional project name

    Returns:
        Orchestrator instance
    """
    if use_langgraph and LANGGRAPH_AVAILABLE:
        return LangGraphOrchestrator(project_name=project_name)

    # Legacy fallback
    return LangGraphOrchestrator(project_name=project_name)


# Check environment variable for toggle
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "false").lower() == "true"


def get_orchestrator(
    project_name: Optional[str] = None,
    use_langgraph: Optional[bool] = None,
) -> "LangGraphOrchestrator":
    """
    Get an orchestrator based on environment settings.

    Args:
        project_name: Optional project name
        use_langgraph: Override USE_LANGGRAPH setting

    Returns:
        LangGraphOrchestrator instance
    """
    if use_langgraph is None:
        use_langgraph = USE_LANGGRAPH and LANGGRAPH_AVAILABLE

    return create_orchestrator(
        use_langgraph=use_langgraph,
        project_name=project_name,
    )


__all__ = [
    "LangGraphOrchestrator",
    "create_orchestrator",
    "get_orchestrator",
    "USE_LANGGRAPH",
    "LANGGRAPH_AVAILABLE",
]
