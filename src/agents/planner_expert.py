"""
Expert-Level Planner Agent
Advanced task decomposition, optimization, and execution planning
"""

import os
import json
from typing import List, Dict, Tuple
from datetime import datetime
from brain.router import route_chat


EXPERT_PLANNER_PROMPT = """You are an EXPERT LEVEL planner and task decomposition agent.

Your expertise:
- Breaking complex projects into optimal execution steps
- Identifying dependencies and critical paths
- Optimizing for efficiency and parallelization
- Recognizing architectural patterns and best practices
- Planning for scalability, security, and maintainability
- Risk identification and mitigation

TASK DECOMPOSITION FRAMEWORK:
1. ANALYSIS PHASE
   - Understand requirements and constraints
   - Identify scope and complexity
   - Extract key technical challenges

2. ARCHITECTURE PHASE
   - Design high-level architecture
   - Identify major components
   - Plan data flows and integrations

3. IMPLEMENTATION PHASES
   - Break into logical chunks
   - Identify parallelizable tasks
   - Sequence dependencies

4. OPTIMIZATION PHASE
   - Add performance optimization steps
   - Security hardening
   - Code quality and testing

5. DELIVERY PHASE
   - Documentation
   - Deployment considerations
   - Monitoring and maintenance

RESPONSE FORMAT:
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
          "success_criteria": ["criterion 1", "criterion 2"],
          "risk_level": "low|medium|high"
        }}
      ]
    }}
  ],
  "critical_path": ["step1", "step2"],
  "parallelizable_tasks": [["task1", "task2"], ["task3"]],
  "risks": [
    {{
      "risk": "description",
      "impact": "high|medium|low",
      "mitigation": "strategy"
    }}
  ],
  "success_metrics": ["metric1", "metric2"],
  "documentation_needed": ["doc1", "doc2"]
}}

User Request: {user_input}"""


DEPENDENCY_ANALYZER_PROMPT = """Analyze dependencies for this project:

{project_details}

Provide analysis as JSON:
{{
  "components": {{"component_name": ["dependencies"]}},
  "critical_path": ["ordered list of critical tasks"],
  "parallelizable": [["task1", "task2"], ["task3"]],
  "technical_risks": [{{"risk": "description", "mitigation": "solution"}}],
  "architecture_patterns": ["pattern1", "pattern2"],
  "performance_bottlenecks": ["bottleneck1", "bottleneck2"]
}}"""


class ExpertPlanner:
    """Expert-level task planner with advanced decomposition"""

    def __init__(self, model=None):
        self.model = model or os.getenv("PLANNER_MODEL") or os.getenv("DEFAULT_MODEL")
        self.planning_history = []

    def decompose_project(self, user_input: str) -> Dict:
        """Decompose project into expert-level plan"""
        response = route_chat(
            [
                {"role": "system", "content": "You are an expert project planner."},
                {
                    "role": "user",
                    "content": EXPERT_PLANNER_PROMPT.format(user_input=user_input),
                },
            ],
            model=self.model,
        )

        plan = self._parse_plan(response)

        self.planning_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "plan": plan,
        })

        return plan

    def analyze_dependencies(self, project_details: Dict) -> Dict:
        """Analyze project dependencies and critical path"""
        response = route_chat(
            [
                {"role": "system", "content": "You are a dependency analysis expert."},
                {
                    "role": "user",
                    "content": DEPENDENCY_ANALYZER_PROMPT.format(
                        project_details=json.dumps(project_details, indent=2)
                    ),
                },
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def optimize_execution_order(self, plan: Dict) -> List[Dict]:
        """Optimize task execution order"""
        prompt = f"""Given this project plan:
{json.dumps(plan, indent=2)}

Optimize the execution order for maximum efficiency:
1. Identify critical path
2. Find parallelizable tasks
3. Minimize dependencies
4. Optimize resource usage
5. Consider risk mitigation

Return optimized step list as JSON array of steps with execution_priority."""

        response = route_chat(
            [
                {
                    "role": "system",
                    "content": "You are an execution planning expert.",
                },
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def estimate_effort(self, plan: Dict) -> Dict:
        """Estimate effort and resource requirements"""
        prompt = f"""Estimate effort for this plan:
{json.dumps(plan, indent=2)}

Provide estimates as JSON:
{{
  "total_hours": number,
  "by_phase": {{"phase_name": hours}},
  "resource_requirements": ["resource1"],
  "critical_skills": ["skill1", "skill2"],
  "bottlenecks": ["bottleneck1"],
  "buffer_percentage": 20
}}"""

        response = route_chat(
            [
                {"role": "system", "content": "You are an estimation expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def identify_risks(self, plan: Dict) -> List[Dict]:
        """Identify and mitigate risks"""
        prompt = f"""Identify risks for this project:
{json.dumps(plan, indent=2)}

Return as JSON array:
[
  {{
    "risk": "description",
    "probability": "high|medium|low",
    "impact": "high|medium|low",
    "mitigation": "strategy",
    "owner": "team or person",
    "monitoring": "how to monitor"
  }}
]"""

        response = route_chat(
            [
                {"role": "system", "content": "You are a risk management expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def plan_testing_strategy(self, plan: Dict) -> Dict:
        """Create comprehensive testing strategy"""
        prompt = f"""Create testing strategy for:
{json.dumps(plan, indent=2)}

Include:
- Unit test coverage targets
- Integration tests
- Performance tests
- Security tests
- User acceptance tests
- Test automation

Return as JSON."""

        response = route_chat(
            [
                {"role": "system", "content": "You are a testing strategy expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def plan_architecture(self, user_input: str) -> Dict:
        """Plan detailed architecture"""
        prompt = f"""Design architecture for:
{user_input}

Include:
- System design diagram (as text)
- Component breakdown
- Data flow
- Technology stack
- Scalability strategy
- Security architecture
- Deployment strategy

Return as structured JSON."""

        response = route_chat(
            [
                {"role": "system", "content": "You are a solution architect."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json_response(response)

    def _parse_plan(self, response: str) -> Dict:
        """Parse plan response"""
        try:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass

        # Fallback to structured response
        return {
            "raw_plan": response,
            "parsed": False,
        }

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON response"""
        try:
            start = response.find("{")
            if start >= 0:
                end = response.rfind("}") + 1
                return json.loads(response[start:end])

            start = response.find("[")
            if start >= 0:
                end = response.rfind("]") + 1
                return json.loads(response[start:end])
        except:
            pass

        return {"raw": response, "parsed": False}


class AdaptivePlanner:
    """Planner that adapts based on learning"""

    def __init__(self):
        self.planner = ExpertPlanner()
        self.execution_history = []
        self.learned_patterns = {}

    def plan_with_learning(self, user_input: str) -> Dict:
        """Plan using learned patterns"""
        base_plan = self.planner.decompose_project(user_input)

        # Apply learned patterns
        enhanced_plan = self._apply_learned_patterns(base_plan, user_input)

        return enhanced_plan

    def record_execution(self, plan: Dict, execution_result: Dict):
        """Record execution for learning"""
        self.execution_history.append({
            "plan": plan,
            "result": execution_result,
            "timestamp": datetime.now().isoformat(),
            "success": execution_result.get("success", False),
            "duration": execution_result.get("duration"),
        })

        self._extract_patterns(plan, execution_result)

    def _apply_learned_patterns(self, plan: Dict, context: str) -> Dict:
        """Apply learned patterns to plan"""
        # Analyze similar past projects
        for pattern_name, pattern_data in self.learned_patterns.items():
            if self._matches_pattern(context, pattern_name):
                # Apply pattern optimization
                if "optimizations" in pattern_data:
                    plan["learned_optimizations"] = pattern_data["optimizations"]

        return plan

    def _extract_patterns(self, plan: Dict, result: Dict):
        """Extract and learn patterns"""
        if result.get("success"):
            project_type = plan.get("project_type", "generic")

            if project_type not in self.learned_patterns:
                self.learned_patterns[project_type] = {
                    "count": 0,
                    "avg_duration": 0,
                    "optimizations": [],
                }

            self.learned_patterns[project_type]["count"] += 1

    def _matches_pattern(self, context: str, pattern_name: str) -> bool:
        """Check if context matches pattern"""
        return pattern_name.lower() in context.lower()


def create_expert_planner(model=None):
    """Factory for expert planner"""
    return ExpertPlanner(model)


def plan_project(user_input: str, model=None) -> Dict:
    """Plan a project"""
    planner = ExpertPlanner(model)
    return planner.decompose_project(user_input)
