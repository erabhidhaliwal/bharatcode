"""
BharatCode Orchestrator
Lightweight orchestrator that routes between fast chat and full expert workflow.
Uses the expert agent system for complex tasks.
Supports both legacy and LangGraph modes.
"""

import os
from brain.router import route_chat
from agents.orchestrator_expert import ExpertAgentOrchestrator

# Check for LangGraph mode
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "false").lower() == "true"

# Import LangGraph components if available
if USE_LANGGRAPH:
    try:
        from agents.langgraph import LangGraphOrchestrator, get_orchestrator
        LANGGRAPH_AVAILABLE = True
    except ImportError as e:
        LANGGRAPH_AVAILABLE = False
        print(f"Warning: LangGraph not available ({e}), using legacy mode")
else:
    LANGGRAPH_AVAILABLE = False
    LangGraphOrchestrator = None
    get_orchestrator = None


SIMPLE_PATTERNS = [
    "hello", "hi", "hey", "help",
    "how are", "what's up", "who are you", "what can you",
    "thanks", "thank you",
    "exit", "quit", "bye",
]


def is_simple_query(user_input):
    """Check if the input is a simple conversational query."""
    text = user_input.lower().strip()
    for pattern in SIMPLE_PATTERNS:
        if pattern in text:
            return True
    if len(text.split()) <= 3:
        return True
    return False


class Orchestrator:
    """Routes user input to appropriate agent based on complexity."""

    def __init__(self, project_name=None):
        self.expert_orchestrator = None
        self.project_name = project_name
        self.langgraph_orchestrator = None

    def _get_expert(self):
        """Lazy-init the expert orchestrator."""
        if self.expert_orchestrator is None:
            self.expert_orchestrator = ExpertAgentOrchestrator(self.project_name)
        return self.expert_orchestrator

    def _get_langgraph_orchestrator(self):
        """Lazy-init the LangGraph orchestrator."""
        if self.langgraph_orchestrator is None and LANGGRAPH_AVAILABLE:
            self.langgraph_orchestrator = get_orchestrator(self.project_name)
        return self.langgraph_orchestrator

    def run(self, user_input):
        """Route input to fast chat or expert workflow."""
        if is_simple_query(user_input):
            print("⚡ [Fast Mode] Processing...")
            model = os.getenv("DEFAULT_MODEL")
            response = route_chat(
                [
                    {
                        "role": "system",
                        "content": "You are BharatCode, a helpful and friendly AI coding assistant. Give brief, warm responses.",
                    },
                    {"role": "user", "content": user_input},
                ],
                model=model,
            )
            return response

        # Complex task → use expert workflow
        # Check if LangGraph mode is enabled
        if USE_LANGGRAPH and LANGGRAPH_AVAILABLE:
            print("🔄 [LangGraph Mode] Starting workflow...")
            langgraph = self._get_langgraph_orchestrator()
            if langgraph:
                result = langgraph.execute(user_input, self.project_name)
                return result

        # Fall back to legacy expert orchestrator
        print("🚀 [Expert Mode] Starting full workflow...")
        expert = self._get_expert()
        result = expert.execute_expert_workflow(user_input)
        return result
