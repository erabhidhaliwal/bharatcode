from brain.router import route_chat
from tools.registry import TOOLS

def executor(plan):
    response = route_chat([
        {"role": "system", "content": "You can generate code or call tools."},
        {"role": "user", "content": plan}
    ])

    # SIMPLE TOOL DETECTION (upgrade later)
    if "run_shell:" in response:
        cmd = response.split("run_shell:")[1].strip()
        return TOOLS["shell"](cmd)

    return response