from brain.glm import glm_chat

def planner(user_input):
    return glm_chat([
        {"role": "system", "content": "You are a planner agent. Break tasks into steps."},
        {"role": "user", "content": user_input}
    ])