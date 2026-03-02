import os
from brain.router import route_chat

def reviewer(output):
    model = os.getenv("REVIEWER_MODEL")
    return route_chat([
        {"role": "system", "content": "Fix errors and improve code."},
        {"role": "user", "content": output}
    ], model=model)