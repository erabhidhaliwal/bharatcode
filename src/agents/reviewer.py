from brain.glm import glm_chat

def reviewer(output):
    return glm_chat([
        {"role": "system", "content": "Fix errors and improve code."},
        {"role": "user", "content": output}
    ])