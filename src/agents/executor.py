import os
from brain.router import route_chat
from tools.registry import TOOLS

def executor(plan):
    model = os.getenv("EXECUTOR_MODEL")
    response = route_chat([
        {"role": "system", "content": "You can generate code or call tools."},
        {"role": "user", "content": plan}
    ], model=model)

    # SIMPLE TOOL DETECTION (upgrade later)
    if "run_shell:" in response:
        cmd = response.split("run_shell:")[1].strip()
        return TOOLS["shell"](cmd)

    return response