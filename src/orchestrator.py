import os
from agents.planner import planner
from agents.executor import executor
from agents.reviewer import reviewer


class Orchestrator:
    def planner(self, user_input):
        model = os.getenv("PLANNER_MODEL") or os.getenv("DEFAULT_MODEL")
        return planner(user_input, model=model)

    def executor(self, plan):
        model = os.getenv("EXECUTOR_MODEL") or os.getenv("DEFAULT_MODEL")
        return executor(plan, model=model)

    def reviewer(self, result):
        model = os.getenv("REVIEWER_MODEL") or os.getenv("DEFAULT_MODEL")
        return reviewer(result, model=model)

    def run(self, user_input):
        print("🧠 [Planner] Thinking...")
        plan = self.planner(user_input)
        if plan and plan.startswith("Error:"):
            return plan

        print("⚙️  [Executor] Working...")
        result = self.executor(plan)
        if result and result.startswith("Error:"):
            return result

        print("🧐 [Reviewer] Finalizing...")
        final = self.reviewer(result)
        return final
