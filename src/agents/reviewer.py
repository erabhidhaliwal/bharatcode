import os
from brain.router import route_chat


def reviewer(output, model=None):
    model = model or os.getenv("REVIEWER_MODEL") or os.getenv("DEFAULT_MODEL")
    return route_chat(
        [
            {"role": "system", "content": "Review and improve code. Provide feedback."},
            {"role": "user", "content": output},
        ],
        model=model,
    )
