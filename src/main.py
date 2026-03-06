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
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich.color import Color
from brain.models import FREE_CODING_MODELS, get_default_model
from brain.router import route_chat
from agents.autonomous_expert import (
    ExpertAutonomousAgent,
    ProjectMemory,
    get_memory,
    AdvancedExecutor,
)
from agents.orchestrator_expert import ExpertAgentOrchestrator
from agents.design_orchestrator import create_design_orchestrator

console = Console()

# ──────────────────────────────────────────────────────────────
# BHARAT CODE SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are **BharatCode** — an expert AI coding assistant built for developers.

PERSONALITY:
- Friendly, conversational, and approachable
- Technically sharp but never condescending
- You explain things simply when asked
- You ask clarifying questions before jumping into big tasks

BEHAVIOR RULES:
1. For casual messages (greetings, small talk, thanks), respond warmly and briefly.
2. For coding questions, explain clearly with examples.
3. For task requests (create, build, debug, fix, review), FIRST ask clarifying questions before doing any work.
4. If the user says "go ahead", "yes", "do it", "proceed" — then proceed with the work.
5. Keep responses concise but helpful.
6. When creating files or running commands, show what you're doing.

CAPABILITIES:
- Create complete projects (websites, apps, scripts)
- Debug and fix code
- Explain programming concepts
- Review and analyze code
- Refactor and optimize
- Run terminal commands
- Read, write, and edit files

You are chatting in a terminal CLI. Keep formatting clean and readable.
"""

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────
BHARAT_CONFIG_DIR = Path.home() / ".bharat"
BHARAT_SESSIONS_DIR = BHARAT_CONFIG_DIR / "sessions"
BHARAT_SETTINGS_FILE = BHARAT_CONFIG_DIR / "settings.json"
BHARAT_MEMORY_FILE = BHARAT_CONFIG_DIR / "memory.md"

# Ensure directories exist
BHARAT_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Default settings
DEFAULT_SETTINGS = {
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "verbose": False,
    "theme": "default",
    "hooks": {},
    "permissions": {
        "allow": [],
        "deny": [],
    },
}

# ──────────────────────────────────────────────────────────────
# SESSION MANAGEMENT
# ──────────────────────────────────────────────────────────────
class SessionManager:
    """Manages conversation sessions with persistence"""

    def __init__(self):
        self.sessions = {}
        self.load_sessions()

    def load_sessions(self):
        """Load all session files"""
        if not BHARAT_SESSIONS_DIR.exists():
            return

        for session_file in BHARAT_SESSIONS_DIR.glob("*.json"):
            try:
                with open(session_file) as f:
                    session = json.load(f)
                    session_id = session_file.stem
                    self.sessions[session_id] = session
            except Exception:
                pass

    def save_session(self, session_id, data):
        """Save session to file"""
        session_file = BHARAT_SESSIONS_DIR / f"{session_id}.json"
        with open(session_file, "w") as f:
            json.dump(data, f, indent=2)

    def create_session(self, name=None):
        """Create a new session"""
        session_id = name if name else str(uuid.uuid4())[:8]
        if session_id in self.sessions:
            session_id = f"{session_id}_{int(time.time())}"

        self.sessions[session_id] = {
            "id": session_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "current_project": None,
        }
        self.save_session(session_id, self.sessions[session_id])
        return session_id

    def get_session(self, session_id):
        """Get a session by ID or name"""
        return self.sessions.get(session_id)

    def get_recent_session(self):
        """Get the most recently used session"""
        if not self.sessions:
            return None

        # Sort by last updated
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].get("updated_at", x[1].get("created_at", "")),
            reverse=True,
        )
        return sorted_sessions[0] if sorted_sessions else None

    def list_sessions(self):
        """List all sessions"""
        return [
            {
                "id": sid,
                "name": s.get("name", sid),
                "created_at": s.get("created_at", ""),
                "message_count": len(s.get("messages", [])),
            }
            for sid, s in sorted(
                self.sessions.items(),
                key=lambda x: x[1].get("updated_at", ""),
                reverse=True,
            )
        ]

    def delete_session(self, session_id):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            session_file = BHARAT_SESSIONS_DIR / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()


class SettingsManager:
    """Manages BharatCode settings"""

    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Load settings from file"""
        if BHARAT_SETTINGS_FILE.exists():
            try:
                with open(BHARAT_SETTINGS_FILE) as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception:
                pass

    def save(self):
        """Save settings to file"""
        BHARAT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(BHARAT_SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key, default=None):
        """Get a setting"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting"""
        self.settings[key] = value
        self.save()

    def get_model(self):
        """Get the current model"""
        return self.settings.get("model") or os.getenv("DEFAULT_MODEL") or get_default_model()

    def set_model(self, model):
        """Set the current model"""
        self.settings["model"] = model
        self.save()


# ──────────────────────────────────────────────────────────────
# BHARAT CODE CLI
# ──────────────────────────────────────────────────────────────
class BharatCode:
    def __init__(self, session_name=None, continue_session=False, resume_session=None):
        self.session_manager = SessionManager()
        self.settings = SettingsManager()

        # Session handling
        if resume_session:
            session = self.session_manager.get_session(resume_session)
            if session:
                self.session_id = resume_session
                self.session = session
            else:
                console.print(f"[yellow]Session not found: {resume_session}[/]")
                self.session_id = self.session_manager.create_session(session_name)
                self.session = self.session_manager.get_session(self.session_id)
        elif continue_session:
            recent = self.session_manager.get_recent_session()
            if recent:
                self.session_id = recent[0]
                self.session = recent[1]
            else:
                self.session_id = self.session_manager.create_session(session_name)
                self.session = self.session_manager.get_session(self.session_id)
        else:
            self.session_id = self.session_manager.create_session(session_name)
            self.session = self.session_manager.get_session(self.session_id)

        # Model and API
        self.model = self.settings.get_model()
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        # Conversation state
        self.conversation_history = self.session.get("messages", [])
        self.current_project = self.session.get("current_project")
        self.pending_task = None

        # Track intent for confirmation
        self.last_intent = None
        self.plan_mode = False

        # Logging
        self.log_session_start()

    def log_session_start(self):
        """Log session start"""
        console.print(f"\n[dim]Session:[/] {self.session_id}")

    def save_session(self):
        """Save current session state"""
        self.session["messages"] = self.conversation_history
        self.session["current_project"] = self.current_project
        self.session["updated_at"] = datetime.now().isoformat()
        self.session_manager.save_session(self.session_id, self.session)

    # ──────────────────────────────────────────────────────────
    # INTENT DETECTION
    # ──────────────────────────────────────────────────────────
    CHAT_PATTERNS = [
        "hello", "hi", "hey", "sup", "yo", "howdy",
        "how are you", "what's up", "whats up",
        "good morning", "good evening", "good night",
        "thanks", "thank you", "thx", "ty",
        "bye", "goodbye", "see you", "later",
        "who are you", "what are you", "what can you do",
        "nice", "cool", "great", "awesome", "ok", "okay",
    ]

    CONFIRM_PATTERNS = [
        "yes", "yeah", "yep", "yup", "sure", "ok", "okay",
        "go ahead", "do it", "proceed", "lets go", "let's go",
        "go for it", "make it", "build it", "start",
    ]

    INTENT_KEYWORDS = [
        ("run", ["run ", "execute ", "start ", "install ", "test "]),
        ("debug", ["debug", "fix ", "error", "bug", "issue", "broken"]),
        ("refactor", ["refactor", "optimize", "clean up", "restructure"]),
        ("review", ["review", "analyze", "look at", "check"]),
        ("improve", ["improve", "add feature", "update", "upgrade"]),
        ("design", ["design", " ui ", " ux ", "template", "aesthetic"]),
        ("create", ["create ", "build ", "make ", "generate ", "new "]),
    ]

    def detect_intent(self, text):
        text_lower = text.lower().strip()

        # Confirmation
        if text_lower in self.CONFIRM_PATTERNS or any(p in text_lower for p in self.CONFIRM_PATTERNS):
            if self.pending_task:
                return "confirm"

        # Chat patterns
        if text_lower in self.CHAT_PATTERNS or any(text_lower.startswith(p) for p in self.CHAT_PATTERNS):
            return "chat"

        # Questions
        if text_lower.startswith(("what ", "what's ", "how ", "why ", "can you", "explain", "tell me")):
            return "ask"

        # Short messages
        if len(text_lower.split()) <= 3:
            has_action = any(kw in text_lower for _, kws in self.INTENT_KEYWORDS for kw in kws)
            if not has_action:
                return "chat"

        # Keyword-based
        for intent, keywords in self.INTENT_KEYWORDS:
            for kw in keywords:
                if kw in text_lower:
                    return intent

        return "chat"

    # ──────────────────────────────────────────────────────────
    # CONVERSATION MANAGEMENT
    # ──────────────────────────────────────────────────────────
    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
        # Keep last 50 messages
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        self.save_session()

    def get_messages(self, user_message):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.conversation_history[-20:])
        messages.append({"role": "user", "content": user_message})
        return messages

    # ──────────────────────────────────────────────────────────
    # AI CHAT
    # ──────────────────────────────────────────────────────────
    def chat(self, user_message, show_thinking=True):
        messages = self.get_messages(user_message)

        if show_thinking:
            with console.status("[bold cyan]Thinking...[/]", spinner="dots"):
                result = route_chat(messages, model=self.model)
        else:
            result = route_chat(messages, model=self.model)

        if result:
            self.add_message("user", user_message)
            self.add_message("assistant", result)

        return result

    # ──────────────────────────────────────────────────────────
    # TASK HANDLERS
    # ──────────────────────────────────────────────────────────
    def handle_create(self, task):
        """Handle project creation"""
        # Check if user is confirming a pending task
        if self.pending_task and self.pending_task.get("type") == "create":
            full_task = f"{self.pending_task['original_request']}\n\n{task}"
            self.pending_task = None
            return self.execute_create(full_task)

        # Check if task needs clarification
        if len(task.split()) < 8 and not any(w in task.lower() for w in ["website", "app", "script", "project"]):
            self.pending_task = {"type": "create", "original_request": task}
            return self.chat(f"User wants to create: {task}. Ask 2-3 clarifying questions about tech stack, features, and design preferences.", show_thinking=True)

        return self.execute_create(task)

    def execute_create(self, task):
        """Execute project creation"""
        console.print()
        console.print("[bold bright_green]Building your project...[/]\n")

        project_name = self._extract_project_name(task) or "MyProject"

        with console.status("[bold cyan]Creating project...[/]", spinner="dots"):
            orchestrator = ExpertAgentOrchestrator(project_name=project_name)
            result = orchestrator.execute_expert_workflow(task)

        if project_name:
            self.current_project = project_name

        if isinstance(result, dict):
            output = f"\n[bold green]Project Complete:[/] {project_name}\n\n"
            if result.get("summary"):
                output += f"[dim]{result['summary']}[/]\n"
            if result.get("files_created"):
                output += f"\n[bold]Files:[/]\n"
                for f in result["files_created"][:10]:
                    output += f"  [cyan]•[/] {f}\n"
            return output
        return str(result)

    def handle_design(self, task):
        """Handle UI/UX design"""
        console.print()
        console.print("[bold bright_purple]Creating design...[/]\n")

        project_name = self._extract_project_name(task) or self.current_project or "Design"

        with console.status("[bold purple]Designing...[/]", spinner="dots"):
            orchestrator = create_design_orchestrator()
            result = orchestrator.create_complete_design(
                project_name=project_name,
                requirements=task,
                aesthetic="GLASSMORPHISM",
                palette="COOL_TONES"
            )

        html_file = f"{project_name.replace(' ', '_').lower()}.html"
        with open(html_file, "w") as f:
            f.write(result["exports"]["html"]["content"])

        css_file = f"{project_name.replace(' ', '_').lower()}.css"
        with open(css_file, "w") as f:
            f.write(result["exports"]["css"]["content"])

        return f"[green]Design saved:[/]\n  [cyan]{html_file}[/]\n  [cyan]{css_file}[/]"

    def handle_debug(self, task):
        """Handle debugging"""
        return self.chat(f"Help debug this: {task}. Ask for error messages or code if not provided.")

    def handle_review(self, task):
        """Handle code review"""
        return self.chat(f"Review this: {task}. Ask for code if not provided.")

    def handle_refactor(self, task):
        """Handle refactoring"""
        return self.chat(f"Refactor this: {task}. Ask for code if not provided.")

    def handle_run(self, task):
        """Handle command execution"""
        cmd = task
        if "run " in task.lower():
            cmd = task.lower().split("run ", 1)[1].strip()

        console.print(f"\n[dim]Running:[/] [cyan]{cmd}[/]")

        if Confirm.ask("[dim]Proceed?[/]", default=True):
            executor = AdvancedExecutor()
            result = executor.run_command(cmd, timeout=60)

            if result["success"]:
                output = result.get("stdout", "") or result.get("stderr", "")
                return f"[green]Done![/]\n\n```\n{output[:1000]}\n```"
            return f"[red]Error:[/] {result.get('stderr', 'Unknown')}"
        return "[dim]Cancelled.[/dim]"

    def handle_improve(self, task):
        """Handle project improvement"""
        return self.chat(f"Improve: {task}. Ask which project and what to improve.")

    # ──────────────────────────────────────────────────────────
    # FILE TOOLS
    # ──────────────────────────────────────────────────────────
    def handle_read(self, filepath):
        """Read a file"""
        executor = AdvancedExecutor()
        result = executor.read_file(filepath)

        if result["success"]:
            content = result["content"]
            lines = result.get("lines", "?")
            header = f"[dim]📄 {filepath} ({lines} lines)[/dim]\n\n"
            if len(content) > 3000:
                return f"{header}```\n{content[:3000]}\n...[/]```"
            return f"{header}```\n{content}\n```"
        return f"[red]Error:[/] {result.get('error', 'File not found')}"

    def handle_shell(self, command):
        """Run a shell command"""
        executor = AdvancedExecutor()
        result = executor.run_command(command, timeout=60)

        if result["success"]:
            output = result.get("stdout", "") or result.get("stderr", "")
            return f"[green]Done![/]\n\n```\n{output[:1000]}\n```"
        return f"[red]Error:[/] {result.get('stderr', 'Unknown')}"

    def handle_ls(self, directory="."):
        """List directory"""
        executor = AdvancedExecutor()
        result = executor.list_files(directory)

        if result["success"]:
            files = result.get("files", [])
            if not files:
                return f"[dim]Empty directory[/]"

            output = f"[bold]📁 {directory}[/] ({len(files)} items)\n\n"
            for f in files[:30]:
                path = f if isinstance(f, str) else f.get("path", str(f))
                output += f"  [cyan]•[/] {path}\n"
            return output
        return f"[red]Error:[/] {result.get('error', 'Directory not found')}"

    def handle_glob(self, pattern):
        """Glob files"""
        from glob import glob
        files = glob(pattern, recursive=True)[:20]
        if files:
            output = f"[bold]Files matching:[/] {pattern}\n\n"
            for f in files:
                output += f"  [cyan]•[/] {f}\n"
            return output
        return f"[dim]No files found[/]"

    def handle_grep(self, pattern, path="."):
        """Grep files"""
        executor = AdvancedExecutor()
        result = executor.search_code(pattern, path)

        if result.get("success") and result.get("matches"):
            output = f"[bold]Matches for:[/] {pattern}\n\n"
            for match in result["matches"][:20]:
                output += f"  [cyan]{match}[/]\n"
            return output
        return f"[dim]No matches found[/]"

    def handle_write(self, filepath, content):
        """Write a file"""
        try:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
            return f"[green]Saved:[/] {filepath}"
        except Exception as e:
            return f"[red]Error:[/] {str(e)}"

    # ──────────────────────────────────────────────────────────
    # UTILITIES
    # ──────────────────────────────────────────────────────────
    def _extract_project_name(self, task):
        words = task.lower().split()
        for word in ["called", "named", "name"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    return words[idx + 1].strip(".,!?\"'")
        return None

    # ──────────────────────────────────────────────────────────
    # SLASH COMMANDS
    # ──────────────────────────────────────────────────────────
    def process_command(self, user_input):
        """Process slash commands"""
        parts = user_input.split(maxsplit=3)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        arg2 = parts[2] if len(parts) > 2 else ""

        # /help - Show help
        if cmd == "/help":
            self.show_help()
            return None

        # /clear - Clear screen
        elif cmd == "/clear":
            console.clear()
            self.print_banner()
            return None

        # /model - Show/set model
        elif cmd == "/model":
            if arg:
                self.model = arg
                self.settings.set_model(arg)
                console.print(f"\n[green]Model set to:[/] {arg}\n")
            else:
                console.print(f"\n[bold]Current model:[/] {self.model}\n")
                console.print("[dim]Available models:[/]")
                for provider, info in FREE_CODING_MODELS.items():
                    for m in info["models"]:
                        console.print(f"  [cyan]{m['id']}[/]")
            return None

        # /models - List models
        elif cmd == "/models":
            self.show_models()
            return None

        # /setkey - Set API key
        elif cmd == "/setkey" and arg:
            os.environ["OPENROUTER_API_KEY"] = arg
            self.api_key = arg
            console.print("\n[green]API key set![/]\n")
            return None

        # /shell - Run command
        elif cmd == "/shell" and arg:
            return self.handle_shell(arg)

        # /read - Read file
        elif cmd == "/read" and arg:
            return self.handle_read(arg)

        # /ls - List directory
        elif cmd == "/ls":
            return self.handle_ls(arg or ".")

        # /glob - Glob files
        elif cmd == "/glob" and arg:
            return self.handle_glob(arg)

        # /grep - Search
        elif cmd == "/grep":
            if arg and arg2:
                return self.handle_grep(arg, arg2)
            elif arg:
                return self.handle_grep(arg)
            return "[yellow]Usage: /grep <pattern> [path][/]"

        # /write - Write file
        elif cmd == "/write":
            if " " in user_input[7:]:
                filepath, content = user_input[7:].split(" ", 1)
                return self.handle_write(filepath, content)
            return "[yellow]Usage: /write <filepath> <content>[/]"

        # /projects - List projects
        elif cmd == "/projects":
            return self.show_projects()

        # /use - Use project
        elif cmd == "/use" and arg:
            self.current_project = arg
            console.print(f"\n[green]Project:[/] {arg}\n")
            return None

        # /sessions - List sessions
        elif cmd == "/sessions":
            return self.show_sessions()

        # /resume - Resume session
        elif cmd == "/resume" and arg:
            return f"[dim]Use: bharat -r {arg} \"task\"[/]"

        # /plan - Toggle plan mode
        elif cmd == "/plan":
            self.plan_mode = not self.plan_mode
            status = "[green]enabled[/]" if self.plan_mode else "[dim]disabled[/]"
            console.print(f"\n[bold]Plan mode:[/] {status}\n")
            return None

        # /cost - Show usage (placeholder)
        elif cmd == "/cost":
            return f"[dim]Messages: {len(self.conversation_history)}[/]"

        # /memory - Edit memory
        elif cmd == "/memory":
            return self.handle_memory()

        # /exit or /quit
        elif cmd in ["/exit", "/quit"]:
            return "exit"

        else:
            return f"[yellow]Unknown command:[/] {cmd}\n[dim]Type /help for available commands[/]"

    def show_help(self):
        """Show help menu"""
        table = Table(title="Commands", border_style="bright_black", width=70)
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", width=48)

        commands = [
            ("/help", "Show this help"),
            ("/clear", "Clear the screen"),
            ("/model [name]", "Show or set model"),
            ("/models", "List available models"),
            ("/setkey <key>", "Set OpenRouter API key"),
            ("/shell <cmd>", "Run shell command"),
            ("/read <file>", "Read a file"),
            ("/ls [dir]", "List directory"),
            ("/glob <pattern>", "Find files by pattern"),
            ("/grep <pattern>", "Search in files"),
            ("/write <file> <content>", "Write file"),
            ("/projects", "List saved projects"),
            ("/use <name>", "Set active project"),
            ("/sessions", "List sessions"),
            ("/plan", "Toggle plan mode"),
            ("/cost", "Show message count"),
            ("/memory", "Edit project memory"),
            ("/exit", "Exit BharatCode"),
        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        console.print(table)

    def show_models(self):
        """Show available models"""
        table = Table(title="Available Models", border_style="bright_black")
        table.add_column("Provider", style="cyan")
        table.add_column("Model", width=40)

        for provider, info in FREE_CODING_MODELS.items():
            for m in info["models"]:
                table.add_row(provider.upper(), f"{m['name']} ({m['id']})")

        console.print(table)

    def show_projects(self):
        """Show saved projects"""
        memory = get_memory()
        projects = memory.list_projects()

        if projects:
            console.print("\n[bold]📁 Your Projects:[/]\n")
            for p in projects[:10]:
                name = p.get("name", "unnamed")
                request = p.get("request", "")[:50]
                console.print(f"  [cyan]•[/] [bold]{name}[/] — {request}...")
        else:
            console.print("\n[dim]No projects yet[/]\n")

    def show_sessions(self):
        """Show sessions"""
        sessions = self.session_manager.list_sessions()

        if sessions:
            console.print("\n[bold]Sessions:[/]\n")
            for s in sessions[:10]:
                console.print(f"  [cyan]•[/] {s['id']} ({s['message_count']} messages)")
        else:
            console.print("\n[dim]No sessions[/]\n")

    def handle_memory(self):
        """Handle memory file"""
        if BHARAT_MEMORY_FILE.exists():
            console.print(f"\n[dim]Memory file:[/] {BHARAT_MEMORY_FILE}\n")
            with open(BHARAT_MEMORY_FILE) as f:
                console.print(f.read())
        else:
            console.print("\n[dim]No memory file. Create one at:[/]")
            console.print(f"  {BHARAT_MEMORY_FILE}\n")

    # ──────────────────────────────────────────────────────────
    # BANNER
    # ──────────────────────────────────────────────────────────
    def print_banner(self):
        banner = """
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
        """
        console.print(banner)

        # Status panel
        status = Table(box=None, padding=(0, 1))
        status.add_column()
        status.add_column()
        status.add_row("[dim]Status[/]", "[green]●[/] Online" if self.api_key else "[yellow]⚠[/] No API key")
        status.add_row("[dim]Model[/]", f"[cyan]{self.model}[/]")
        status.add_row("[dim]Session[/]", f"[cyan]{self.session_id}[/]")

        console.print(Panel(status, border_style="green" if self.api_key else "yellow", width=50))

    def print_welcome(self):
        console.print()
        console.print("[bold bright_cyan]Hey! I'm BharatCode — your AI coding companion.[/]\n")
        console.print("  [dim]•[/] Type naturally to chat or ask questions")
        console.print("  [dim]•[/] Use [bold cyan]/help[/] for commands")
        console.print("  [dim]•[/] Examples:")
        console.print("    [cyan]•[/] [dim]\"create a portfolio website\"[/]")
        console.print("    [cyan]•[/] [dim]\"fix this bug in my code\"[/]")
        console.print("    [cyan]•[/] [dim]\"explain how async works in Python\"[/]\n")

    # ──────────────────────────────────────────────────────────
    # MAIN RUN LOOP
    # ──────────────────────────────────────────────────────────
    def run(self, initial_prompt=None):
        self.print_banner()
        self.print_welcome()

        # If initial prompt provided, run it and exit (like Claude -p)
        if initial_prompt:
            result = self.run_task(initial_prompt)
            if result:
                console.print(Markdown(result))
            return

        # Interactive mode
        while True:
            try:
                prompt_text = "[bold bright_cyan]you ›[/]"
                if self.current_project:
                    prompt_text = f"[bold bright_cyan]you[/] [dim]({self.current_project})[/] [bold bright_cyan]›[/]"

                user_input = console.input(prompt_text).strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[bold bright_yellow]👋 See you later![/]\n")
                break

            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\n[bold bright_yellow]👋 Thanks for coding with me![/]\n")
                break

            # Process command
            if user_input.startswith("/"):
                result = self.process_command(user_input)
                if result == "exit":
                    break
                elif result:
                    console.print(Panel(result, border_style="bright_black"))
                continue

            # Run task
            result = self.run_task(user_input)

            if result:
                console.print()
                try:
                    console.print(Panel(Markdown(result), border_style="bright_black", padding=(1, 2)))
                except Exception:
                    console.print(Panel(result, border_style="bright_black", padding=(1, 2)))

    def run_task(self, user_input):
        """Route user input to appropriate handler"""
        intent = self.detect_intent(user_input)

        handlers = {
            "chat": lambda: self.chat(user_input),
            "ask": lambda: self.chat(user_input),
            "create": lambda: self.handle_create(user_input),
            "design": lambda: self.handle_design(user_input),
            "debug": lambda: self.handle_debug(user_input),
            "review": lambda: self.handle_review(user_input),
            "refactor": lambda: self.handle_refactor(user_input),
            "run": lambda: self.handle_run(user_input),
            "improve": lambda: self.handle_improve(user_input),
        }

        # Handle confirmation
        if intent == "confirm" and self.pending_task:
            return self.handle_create(user_input)

        handler = handlers.get(intent, handlers["chat"])
        return handler()


# ──────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="BharatCode - Your AI Coding Companion",
        prog="bharat"
    )

    # Positional argument for initial prompt
    parser.add_argument("prompt", nargs="?", help="Initial prompt to run")

    # Flags
    parser.add_argument("-p", "--print", action="store_true",
                        help="Print mode: run prompt and exit")
    parser.add_argument("-c", "--continue", dest="continue_session", action="store_true",
                        help="Continue most recent session")
    parser.add_argument("-r", "--resume", dest="resume", metavar="SESSION",
                        help="Resume a specific session")
    parser.add_argument("-m", "--model", dest="model", metavar="MODEL",
                        help="Set model to use")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--version", action="store_true",
                        help="Show version")
    parser.add_argument("--session", dest="session", metavar="NAME",
                        help="Create named session")

    args = parser.parse_args()

    # Version
    if args.version:
        console.print("[bold]BharatCode[/] version 1.0.0")
        return

    # Create app
    app = BharatCode(
        session_name=args.session,
        continue_session=args.continue_session,
        resume_session=args.resume
    )

    # Override model if specified
    if args.model:
        app.model = args.model
        app.settings.set_model(args.model)

    # Run with initial prompt (print mode)
    if args.prompt and args.prompt.strip():
        result = app.run_task(args.prompt.strip())
        if result:
            console.print(Markdown(result))
        return

    # Run with prompt as argument (same as -p)
    if args.prompt:
        result = app.run_task(args.prompt)
        if result:
            console.print(Markdown(result))
        return

    # Interactive mode
    app.run()


if __name__ == "__main__":
    main()
