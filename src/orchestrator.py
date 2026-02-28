from agents.planner import planner
from agents.executor import executor
from agents.reviewer import reviewer

class Orchestrator:
    def run(self, user_input):
        # 1. Planning
        plan = planner(user_input)
        if plan.startswith("Error:"):
            return plan
        
        # 2. Execution
        result = executor(plan)
        if result.startswith("Error:"):
            return result
        
        # 3. Review
        final = reviewer(result)
        return final