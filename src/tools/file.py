# tools/file.py

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Saved {path}"

def read_file(path):
    with open(path, "r") as f:
        return f.read()