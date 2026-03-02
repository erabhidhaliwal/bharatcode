from agents.planner import planner
from agents.executor import executor
from agents.reviewer import reviewer

class Orchestrator:
    def run(self, user_input):
        # 1. Planning
        print("🧠 [Planner] Thinking...")
        plan = planner(user_input)
        if plan.startswith("Error:"):
            return plan
        
        # 2. Execution
        print("⚙️  [Executor] Working...")
        result = executor(plan)
        if result.startswith("Error:"):
            return result
        
        # 3. Review
        print("🧐 [Reviewer] Finalizing...")
        final = reviewer(result)
        return final