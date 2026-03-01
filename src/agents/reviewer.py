from brain.router import route_chat

def reviewer(output):
    return route_chat([
        {"role": "system", "content": "Fix errors and improve code."},
        {"role": "user", "content": output}
    ])