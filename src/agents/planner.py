import os
from brain.router import route_chat

def planner(user_input):
    model = os.getenv("PLANNER_MODEL")
    return route_chat([
        {"role": "system", "content": "You are a planner agent. Break tasks into steps."},
        {"role": "user", "content": user_input}
    ], model=model)