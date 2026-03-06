import os
import sys
import time
import json
import re
import uuid
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────
BHARAT_CONFIG_DIR = Path.home() / ".bharat"
BHARAT_SESSIONS_DIR = BHARAT_CONFIG_DIR / "sessions"
BHARAT_SETTINGS_FILE = BHARAT_CONFIG_DIR / "settings.json"

BHARAT_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
}

# ──────────────────────────────────────────────────────────────
# SESSION MANAGEMENT
# ──────────────────────────────────────────────────────────────
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.load_sessions()

    def load_sessions(self):
        if not BHARAT_SESSIONS_DIR.exists():
            return
        for session_file in BHARAT_SESSIONS_DIR.glob("*.json"):
            try:
                with open(session_file) as f:
                    self.sessions[session_file.stem] = json.load(f)
            except Exception:
                pass

    def save_session(self, session_id, data):
        with open(BHARAT_SESSIONS_DIR / f"{session_id}.json", "w") as f:
            json.dump(data, f, indent=2)

    def create_session(self, name=None):
        sid = name or str(uuid.uuid4())[:8]
        if sid in self.sessions:
            sid = f"{sid}_{int(time.time())}"
        self.sessions[sid] = {"id": sid, "messages": [], "created_at": datetime.now().isoformat()}
        self.save_session(sid, self.sessions[sid])
        return sid

    def get_session(self, sid):
        return self.sessions.get(sid)

    def get_recent(self):
        if not self.sessions:
            return None
        return sorted(self.sessions.items(), key=lambda x: x[1].get("created_at", ""), reverse=True)[0]


class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if BHARAT_SETTINGS_FILE.exists():
            try:
                with open(BHARAT_SETTINGS_FILE) as f:
                    self.settings.update(json.load(f))
            except:
                pass

    def save(self):
        BHARAT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(BHARAT_SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get_model(self):
        return self.settings.get("model") or os.getenv("DEFAULT_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")

    def set_model(self, m):
        self.settings["model"] = m
        self.save()


# ──────────────────────────────────────────────────────────────
# TOOL EXECUTOR - For AI to use
# ──────────────────────────────────────────────────────────────
class ToolExecutor:
    """Tools available to the AI"""

    def run_shell(self, command: str) -> str:
        """Run a shell command"""
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return result.stdout or "Done"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, path: str) -> str:
        """Read a file"""
        try:
            with open(path) as f:
                content = f.read()
            return f"File: {path}\n\n{content[:2000]}"
        except Exception as e:
            return f"Error: {e}"

    def write_file(self, path: str, content: str) -> str:
        """Write a file"""
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Created: {path}"
        except Exception as e:
            return f"Error: {e}"

    def list_files(self, path: str = ".") -> str:
        """List directory"""
        try:
            files = os.listdir(path)
            if not files:
                return "Empty"
            return "\n".join(f"  • {f}" for f in files[:20])
        except Exception as e:
            return f"Error: {e}"

    def glob(self, pattern: str) -> str:
        """Find files matching pattern"""
        from glob import glob
        files = glob(pattern, recursive=True)[:20]
        if not files:
            return "No matches"
        return "\n".join(f"  • {f}" for f in files)


TOOL_EXECUTOR = ToolExecutor()

# ──────────────────────────────────────────────────────────────
# SYSTEM PROMPT - Claude Code style
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are BharatCode, an AI coding assistant.

When a user asks you to create something:
1. Create the necessary files using the write_file tool
2. Show what you created

Available tools:
- run_shell(command) - Run terminal commands
- read_file(path) - Read a file
- write_file(path, content) - Write/create a file
- list_files(path) - List directory contents
- glob(pattern) - Find files by pattern

Example:
User: create a website
You: I'll create a simple website for you.

```python
# index.html
<html>...</html>
```

Then use write_file to save it.

Be direct and helpful. When you create something, show the user what was created."""


# ──────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────
from brain.router import route_chat


class BharatCode:
    def __init__(self, session_name=None, continue_session=False, resume_session=None):
        self.session_mgr = SessionManager()
        self.settings = SettingsManager()

        if resume_session:
            self.session_id = resume_session
        elif continue_session:
            recent = self.session_mgr.get_recent()
            self.session_id = recent[0] if recent else self.session_mgr.create_session(session_name)
        else:
            self.session_id = self.session_mgr.create_session(session_name)

        self.session = self.session_mgr.get_session(self.session_id)
        self.model = self.settings.get_model()
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.messages = self.session.get("messages", [])

    def save(self):
        self.session["messages"] = self.messages
        self.session_mgr.save_session(self.session_id, self.session)

    # ──────────────────────────────────────────────────────────
    # CHAT - Direct conversation
    # ──────────────────────────────────────────────────────────
    def chat(self, user_input: str) -> str:
        """Send a message and get response"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.messages[-20:])
        messages.append({"role": "user", "content": user_input})

        result = route_chat(messages, model=self.model)

        if result:
            self.messages.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": result}
            ])
            if len(self.messages) > 50:
                self.messages = self.messages[-50:]
            self.save()

        return result

    # ──────────────────────────────────────────────────────────
    # COMMANDS
    # ──────────────────────────────────────────────────────────
    def process_command(self, user_input: str):
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/help":
            console.print("""
[bold]Commands:[/]
  /help       Show help
  /clear      Clear screen
  /model [m]  Show/set model
  /shell <c> Run command
  /read <f>  Read file
  /ls [d]    List directory
  /exit      Exit
""")
        elif cmd == "/clear":
            console.clear()
            self.print_banner()
        elif cmd == "/exit":
            return "exit"
        elif cmd == "/model":
            if arg:
                self.model = arg
                self.settings.set_model(arg)
            console.print(f"[dim]Model:[/] {self.model}")
        elif cmd == "/shell" and arg:
            return f"```\n{TOOL_EXECUTOR.run_shell(arg)}\n```"
        elif cmd == "/read" and arg:
            return TOOL_EXECUTOR.read_file(arg)
        elif cmd == "/ls":
            return TOOL_EXECUTOR.list_files(arg or ".")
        elif cmd == "/glob" and arg:
            return TOOL_EXECUTOR.glob(arg)
        else:
            return f"Unknown: {cmd}"

    # ──────────────────────────────────────────────────────────
    # BANNER
    # ──────────────────────────────────────────────────────────
    def print_banner(self):
        console.print("""
[bold bright_yellow]╔══════════════════════════════════════════════════════════════╗[/]
[bold bright_yellow]║[/]  [bold bright_cyan]██████╗ ██╗  ██╗ █████╗ ██████╗  █████╗ ████████╗[/]          [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold bright_cyan]██╔══██╗██║  ██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝[/]          [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold bright_cyan]██████╔╝███████║███████║██████╔╝███████║   ██║[/]             [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold bright_cyan]██╔══██╗██╔══██║██╔══██║██╔══██╗██╔══██║   ██║[/]             [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold bright_cyan]██████╔╝██║  ██║██║  ██║██║  ██║██║  ██║   ██║[/]             [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold bright_cyan]╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝[/]             [bold bright_yellow]║[/]
[bold bright_yellow]║[/]                                                              [bold bright_yellow]║[/]
[bold bright_yellow]║[/]  [bold white]C O D E[/]   [dim]•[/dim]   [italic bright_green]Your AI Coding Companion[/]                    [bold bright_yellow]║[/]
[bold bright_yellow]╚══════════════════════════════════════════════════════════════╝[/]
""")
        status = "[green]●[/]" if self.api_key else "[yellow]⚠[/]"
        console.print(f"  [dim]session:[/] {self.session_id}   [dim]model:[/] {self.model}   {status}\n")

    # ──────────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────────
    def run(self, initial_prompt=None):
        self.print_banner()

        if initial_prompt:
            result = self.chat(initial_prompt)
            if result:
                console.print(Markdown(result))
            return

        console.print("[bold bright_cyan]Hey![/] Type naturally or /help\n")

        while True:
            try:
                user = console.input("[bold bright_cyan]you ›[/] ").strip()
            except:
                console.print("\n[bold]👋[/]\n")
                break

            if not user:
                continue

            if user.lower() in ["exit", "quit"]:
                break

            if user.startswith("/"):
                result = self.process_command(user)
                if result == "exit":
                    break
                elif result:
                    console.print(Panel(result, border_style="bright_black"))
                continue

            # Chat
            result = self.chat(user)
            if result:
                console.print()
                try:
                    console.print(Markdown(result))
                except:
                    console.print(Panel(result, border_style="bright_black"))
                console.print()


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
def main():
    import argparse
    p = argparse.ArgumentParser(prog="bharat")
    p.add_argument("prompt", nargs="?", help="Prompt")
    p.add_argument("-p", "--print", action="store_true")
    p.add_argument("-c", "--continue", dest="c", action="store_true")
    p.add_argument("-r", "--resume", dest="r")
    p.add_argument("-m", "--model", dest="m")
    p.add_argument("--version", action="store_true")
    a = p.parse_args()

    if a.version:
        console.print("[bold]BharatCode[/] v1.0.0")
        return

    app = BharatCode(
        continue_session=a.c,
        resume_session=a.r
    )

    if a.m:
        app.model = a.m
        app.settings.set_model(a.m)

    if a.prompt:
        result = app.chat(a.prompt)
        if result:
            console.print(Markdown(result))
        return

    app.run()


if __name__ == "__main__":
    main()
