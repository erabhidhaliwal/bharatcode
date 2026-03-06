"""
LangGraph Graph
Build the StateGraph with all nodes and conditional edges
"""

import os
from typing import Optional, Any, Dict
from typing_extensions import TypedDict


# Try to import LangGraph, but make it optional
LANGGRAPH_AVAILABLE = False

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback for when LangGraph is not available
    StateGraph = None
    MemorySaver = None
    END = None


from .state import AgentState, get_initial_state
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
    route_after_design,
    route_after_review,
    is_human_review_needed,
)


def create_graph(checkpointer: Optional[Any] = None) -> Optional[Any]:
    """
    Create the main LangGraph workflow.

    Args:
        checkpointer: Optional checkpoint saver for human-in-the-loop

    Returns:
        Compiled StateGraph or None if LangGraph not available
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    # Create the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("analyze_deps", analyze_dependencies)
    graph.add_node("designer", designer_node)
    graph.add_node("executor", executor_node)
    graph.add_node("execute_task", execute_single_task)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("check_quality", check_quality_threshold)
    graph.add_node("apply_improvements", apply_improvements)
    graph.add_node("human_review", human_review_node)
    graph.add_node("complete", complete_node)

    # Set entry point
    graph.set_entry_point("planner")

    # Add edges
    # Planning phase
    graph.add_edge("planner", "analyze_deps")
    graph.add_edge("analyze_deps", "designer")

    # Design to execution
    graph.add_edge("designer", "executor")

    # Execution to review
    graph.add_edge("executor", "reviewer")

    # Review quality check
    graph.add_edge("reviewer", "check_quality")

    # Conditional routing after quality check
    graph.add_conditional_edges(
        "check_quality",
        should_retry_execution,
        {
            "execute": "executor",
            "complete": "human_review",
        },
    )

    # Human review node
    graph.add_edge("human_review", "complete")

    # Add conditional edges for phase routing
    graph.add_conditional_edges(
        "planner",
        should_continue,
        {
            "execute": "designer",
            "review": "reviewer",
            "complete": "complete",
        },
    )

    # Compile with optional checkpointer
    if checkpointer:
        compiled = graph.compile(checkpointer=checkpointer)
    else:
        compiled = graph.compile()

    return compiled


def human_review_node(state: AgentState) -> AgentState:
    """
    Human review node - pauses for human input if needed.
    """
    requires_human_review = state.get("requires_human_review", False)
    quality_score = state.get("quality_score", 0)

    if not requires_human_review and quality_score >= 80:
        # Auto-approve high quality
        state["human_approved"] = True
        print("\n✓ Auto-approved (high quality)")
    else:
        print(f"\n⚠ Human review needed")
        print(f"  Quality score: {quality_score:.1f}/100")
        print(f"  Requires review: {requires_human_review}")

    return state


def complete_node(state: AgentState) -> AgentState:
    """
    Complete node - finalizes the workflow.
    """
    from datetime import datetime

    state["current_phase"] = "complete"
    state["end_time"] = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"Files created: {len(state.get('files_created', []))}")
    print(f"Quality score: {state.get('quality_score', 0):.1f}/100")

    return state


def get_compiled_graph(checkpointer: Optional[Any] = None):
    """
    Get a compiled graph instance.
    """
    if not LANGGRAPH_AVAILABLE:
        return None
    graph = create_graph(checkpointer)
    return graph


def run_workflow(
    user_request: str,
    project_name: Optional[str] = None,
    checkpointer: Optional[Any] = None,
    config: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Run the complete workflow.

    Args:
        user_request: The user's request
        project_name: Optional project name
        checkpointer: Optional checkpointer for state persistence
        config: Optional configuration dict

    Returns:
        Final state after workflow completion
    """
    if not LANGGRAPH_AVAILABLE:
        return {
            "error": "LangGraph not available",
            "user_request": user_request,
        }

    # Create initial state
    initial_state = get_initial_state(
        user_request=user_request,
        project_name=project_name,
        max_iterations=config.get("max_iterations", 5) if config else 5,
    )

    # Get compiled graph
    graph = get_compiled_graph(checkpointer)

    if graph is None:
        return {"error": "Could not create graph", **initial_state}

    # Run the graph
    config = config or {}
    thread_id = config.get("thread_id", "default")

    result = graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )

    return result


__all__ = [
    "create_graph",
    "get_compiled_graph",
    "run_workflow",
    "human_review_node",
    "complete_node",
    "LANGGRAPH_AVAILABLE",
]
