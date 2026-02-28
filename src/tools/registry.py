# tools/registry.py

from tools.shell import run_shell
from tools.file import write_file, read_file

TOOLS = {
    "shell": run_shell,
    "write_file": write_file,
    "read_file": read_file
}