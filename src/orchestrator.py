import os
from agents.planner import planner
from agents.executor import executor
from agents.reviewer import reviewer
from brain.router import route_chat

SIMPLE_PATTERNS = [
    "hello",
    "hi",
    "hey",
    "help",
    "how are",
    "what's up",
    "who are you",
    "what can you",
    "thanks",
    "thank you",
    "exit",
    "quit",
    "bye",
]


def is_simple_query(user_input):
    text = user_input.lower().strip()
    for pattern in SIMPLE_PATTERNS:
        if pattern in text:
            return True
    if len(text.split()) <= 3:
        return True
    return False


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
        if is_simple_query(user_input):
            print("⚡ [Fast Mode] Processing...")
            model = os.getenv("DEFAULT_MODEL")
            response = route_chat(
                [
                    {
                        "role": "system",
                        "content": "You are a helpful coding assistant. Give brief, friendly responses.",
                    },
                    {"role": "user", "content": user_input},
                ],
                model=model,
            )
            return response

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
