"""
LangGraph Edges
Conditional routing logic for the multi-agent system
"""

from typing import Literal
from .state import AgentState


def should_continue(state: AgentState) -> Literal["execute", "review", "human_review", "complete"]:
    """
    Determine what to do after planning.

    Returns:
        - "execute": Continue to execution
        - "review": Go directly to review (if no plan)
        - "complete": Mark as complete
    """
    current_phase = state.get("current_phase", "")
    plan = state.get("plan", {})

    if current_phase == "complete":
        return "complete"

    if not plan or not plan.get("phases"):
        # No plan - go to execution anyway
        return "execute"

    # Default to execute
    return "execute"


def route_phase(state: AgentState) -> Literal["planning", "designing", "executing", "reviewing", "human_review", "complete"]:
    """
    Route to the appropriate phase based on current state.

    Returns:
        - "planning": Go to planner
        - "designing": Go to designer
        - "executing": Go to executor
        - "reviewing": Go to reviewer
        - "human_review": Pause for human input
        - "complete": End workflow
    """
    current_phase = state.get("current_phase", "planning")

    # Phase transition logic
    phase_order = ["planning", "designing", "executing", "reviewing", "human_review", "complete"]

    if current_phase not in phase_order:
        current_phase = "planning"

    return current_phase


def check_human_feedback(state: AgentState) -> Literal["continue", "retry", "complete"]:
    """
    Check if human feedback requires action.

    Returns:
        - "continue": Proceed with current quality
        - "retry": Retry execution with feedback
        - "complete": End workflow
    """
    human_feedback = state.get("human_feedback")
    requires_human_review = state.get("requires_human_review", False)
    human_approved = state.get("human_approved", False)

    # If no human review needed, continue
    if not requires_human_review:
        return "continue"

    # If human has approved, complete
    if human_approved:
        return "complete"

    # If human provided feedback, retry with feedback
    if human_feedback:
        # Increment iteration for retry
        state["iteration"] = state.get("iteration", 0) + 1
        return "retry"

    # Wait for human feedback
    return "continue"


def should_retry_execution(state: AgentState) -> Literal["execute", "complete"]:
    """
    Determine if execution should be retried based on review quality.

    Returns:
        - "execute": Retry execution to improve quality
        - "complete": Quality is acceptable, finish
    """
    quality_score = state.get("quality_score", 0)
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 5)
    human_approved = state.get("human_approved", False)

    # If human approved, complete
    if human_approved:
        return "complete"

    # Check iteration limit
    if iteration >= max_iterations - 1:
        return "complete"

    # If quality is good enough, complete
    if quality_score >= 80:
        return "complete"

    # Retry to improve quality
    return "execute"


def route_after_design(state: AgentState) -> Literal["execute", "planning"]:
    """
    Route after design phase.

    Returns:
        - "execute": Proceed to execution
        - "planning": Go back to planning
    """
    design = state.get("design", {})

    if not design or not design.get("components"):
        # No design, go back to planning
        return "planning"

    # Proceed to execution
    return "execute"


def route_after_review(state: AgentState) -> Literal["execute", "complete"]:
    """
    Route after review phase.

    Returns:
        - "execute": Retry execution
        - "complete": Finish workflow
    """
    return should_retry_execution(state)


def is_human_review_needed(state: AgentState) -> bool:
    """
    Check if human review is needed.

    Returns:
        True if human review is needed
    """
    requires_human_review = state.get("requires_human_review", False)
    quality_score = state.get("quality_score", 0)

    # Always review if flagged
    if requires_human_review:
        return True

    # Review if quality is below threshold
    if quality_score < 60:
        return True

    return False


__all__ = [
    "should_continue",
    "route_phase",
    "check_human_feedback",
    "should_retry_execution",
    "route_after_design",
    "route_after_review",
    "is_human_review_needed",
]
