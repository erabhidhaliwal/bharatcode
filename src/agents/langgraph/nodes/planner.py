"""
LangGraph Planner Node
Converts ExpertPlanner logic to LangGraph node
"""

import json
from typing import Dict, Any
from ..state import AgentState
from ..llm import chat_with_model_json, chat_with_model


PLANNER_SYSTEM_PROMPT = """You are an EXPERT LEVEL planner and task decomposition agent.

Your expertise:
- Breaking complex projects into optimal execution steps
- Identifying dependencies and critical paths
- Optimizing for efficiency and parallelization
- Recognizing architectural patterns and best practices
- Planning for scalability, security, and maintainability
- Risk identification and mitigation

TASK DECOMPOSITION FRAMEWORK:
1. ANALYSIS PHASE - Understand requirements and constraints
2. ARCHITECTURE PHASE - Design high-level architecture
3. IMPLEMENTATION PHASES - Break into logical chunks
4. OPTIMIZATION PHASE - Add performance optimization steps
5. DELIVERY PHASE - Documentation and deployment

Provide your plan in JSON format."""


def planner_node(state: AgentState) -> AgentState:
    """
    Planner node - decomposes user request into execution plan.
    """
    user_request = state.get("user_request", "")
    iteration = state.get("iteration", 0)

    print(f"\n{'='*60}")
    print(f"PLANNER NODE - Iteration {iteration + 1}")
    print(f"{'='*60}")
    print(f"User Request: {user_request[:100]}...")

    # Build prompt
    prompt = f"""{PLANNER_SYSTEM_PROMPT}

User Request: {user_request}

Provide your plan in this JSON structure:
{{
  "project_name": "extracted name",
  "complexity_level": "simple|moderate|complex|expert",
  "estimated_effort": "hours",
  "phases": [
    {{
      "phase_name": "name",
      "priority": "critical|high|medium|low",
      "dependencies": ["other phases"],
      "steps": [
        {{
          "step": "description",
          "action_type": "analysis|design|implement|test|optimize|document",
          "estimated_time": "minutes",
          "tools_needed": ["list of tools"],
          "success_criteria": ["criterion 1"],
          "risk_level": "low|medium|high"
        }}
      ]
    }}
  ],
  "critical_path": ["step1", "step2"],
  "parallelizable_tasks": [["task1", "task2"]],
  "risks": [
    {{
      "risk": "description",
      "impact": "high|medium|low",
      "mitigation": "strategy"
    }}
  ],
  "success_metrics": ["metric1"],
  "documentation_needed": ["doc1"]
}}"""

    # Call LLM
    response = chat_with_model_json(
        [{"role": "user", "content": prompt}],
        system_prompt=PLANNER_SYSTEM_PROMPT,
    )

    # Update state
    state["plan"] = response if isinstance(response, dict) else {}
    state["phases"] = response.get("phases", []) if isinstance(response, dict) else []
    state["complexity_level"] = response.get("complexity_level", "moderate")
    state["estimated_effort"] = response.get("estimated_effort", "1 hour")
    state["current_phase"] = "designing"

    # Add message to history
    state["messages"] = state.get("messages", []) + [
        {"role": "assistant", "content": f"Plan created: {response.get('project_name', 'Unknown')}"}
    ]

    print(f"✓ Plan created: {response.get('project_name', 'Unknown')}")
    print(f"  Complexity: {response.get('complexity_level', 'N/A')}")
    print(f"  Phases: {len(state.get('phases', []))}")

    return state


def analyze_dependencies(state: AgentState) -> AgentState:
    """
    Analyze dependencies and risks for the plan.
    """
    plan = state.get("plan", {})

    if not plan:
        state["error"] = "No plan to analyze"
        return state

    prompt = f"""Analyze dependencies and risks for this project plan:

{json.dumps(plan, indent=2)}

Provide analysis as JSON:
{{
  "components": {{"component_name": ["dependencies"]}},
  "critical_path": ["ordered list of critical tasks"],
  "parallelizable": [["task1", "task2"]],
  "technical_risks": [{{"risk": "description", "mitigation": "solution"}}],
  "architecture_patterns": ["pattern1"],
  "performance_bottlenecks": ["bottleneck1"]
}}"""

    response = chat_with_model_json(
        [{"role": "user", "content": prompt}],
        system_prompt="You are a dependency analysis expert.",
    )

    if isinstance(response, dict):
        state["plan"]["dependency_analysis"] = response

    return state


__all__ = ["planner_node", "analyze_dependencies"]
