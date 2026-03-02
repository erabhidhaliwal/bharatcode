import os
from brain.router import route_chat


def planner(user_input, model=None):
    model = model or os.getenv("PLANNER_MODEL") or os.getenv("DEFAULT_MODEL")
    return route_chat(
        [
            {
                "role": "system",
                "content": "You are a planner agent. Break tasks into clear, executable steps.",
            },
            {"role": "user", "content": user_input},
        ],
        model=model,
    )
