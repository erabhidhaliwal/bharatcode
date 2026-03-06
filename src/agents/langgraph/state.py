"""
LangGraph State Definition
Typed state management for the multi-agent system
"""

import os
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    """State definition for LangGraph multi-agent system"""

    # Core message handling
    messages: List[Dict[str, str]]

    # Current execution phase
    current_phase: str  # planning, designing, executing, reviewing, human_review, complete

    # User request
    user_request: str
    project_name: str

    # Planning phase data
    plan: Dict[str, Any]
    phases: List[Dict[str, Any]]
    complexity_level: str
    estimated_effort: str

    # Design phase data
    design: Dict[str, Any]
    design_components: Dict[str, Any]

    # Execution phase data
    execution_results: List[Dict[str, Any]]
    current_task: str
    tasks_completed: List[str]
    tasks_pending: List[str]

    # Review phase data
    review: Dict[str, Any]
    quality_score: float
    issues_found: List[Dict[str, Any]]
    improvements_applied: List[Dict[str, Any]]

    # Files created during execution
    files_created: List[str]
    project_path: str

    # Human-in-the-loop data
    human_feedback: Optional[str]
    checkpoint_id: Optional[str]
    requires_human_review: bool
    human_approved: bool

    # Error handling
    error: Optional[str]
    error_phase: Optional[str]
    retry_count: int

    # Metadata
    iteration: int
    max_iterations: int
    start_time: str
    end_time: Optional[str]

    # Memory/Context
    context: Dict[str, Any]
    knowledge_retrieved: List[Dict[str, Any]]


def get_initial_state(
    user_request: str,
    project_name: Optional[str] = None,
    max_iterations: int = 5,
) -> AgentState:
    """Create initial state for a new workflow execution"""
    from datetime import datetime

    # Extract project name from request if not provided
    if not project_name:
        # Try to extract from request
        words = user_request.split()
        for i, word in enumerate(words):
            if word.lower() in ["create", "build", "make", "develop"]:
                if i + 1 < len(words):
                    project_name = words[i + 1].strip(".,!?")
                    break
        if not project_name:
            project_name = "Project"

    return AgentState(
        messages=[],
        current_phase="planning",
        user_request=user_request,
        project_name=project_name,
        plan={},
        phases=[],
        complexity_level="moderate",
        estimated_effort="1 hour",
        design={},
        design_components={},
        execution_results=[],
        current_task="",
        tasks_completed=[],
        tasks_pending=[],
        review={},
        quality_score=0.0,
        issues_found=[],
        improvements_applied=[],
        files_created=[],
        project_path="",
        human_feedback=None,
        checkpoint_id=None,
        requires_human_review=False,
        human_approved=False,
        error=None,
        error_phase=None,
        retry_count=0,
        iteration=0,
        max_iterations=max_iterations,
        start_time=datetime.now().isoformat(),
        end_time=None,
        context={},
        knowledge_retrieved=[],
    )


def should_continue_loop(state: AgentState) -> bool:
    """Determine if the workflow should continue iterating"""
    if state.get("error"):
        return True
    if state.get("current_phase") == "complete":
        return False
    if state.get("iteration", 0) >= state.get("max_iterations", 5):
        return False
    return True
