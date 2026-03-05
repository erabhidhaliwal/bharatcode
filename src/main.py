import os
import sys
import time
import json
import re
import uuid
import argparse
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
# BHARAT CODE SYSTEM PROMPT  — gives the AI its personality
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are **BharatCode** — an expert AI coding assistant built for developers.

PERSONALITY:
- Friendly, conversational, and approachable
- Technically sharp but never condescending
- You explain things simply when asked
- You ask clarifying questions before jumping into big tasks
- You use emojis sparingly to keep the tone warm 🙂

BEHAVIOR RULES:
1. For casual messages (greetings, small talk, thanks), respond warmly and briefly.
2. For questions about coding concepts, explain clearly with examples.
3. For task requests (create, build, debug, fix, review, refactor, run), FIRST ask clarifying questions before doing any work:
   - What tech stack / language?
   - What features or requirements?
   - Any design preferences?
   - Confirm understanding before proceeding.
4. If the user says "go ahead", "yes", "do it", "proceed" — then describe what you'll build and confirm.
5. Keep responses concise but helpful. No walls of text.
6. When the user explicitly asks you to create/build something with enough detail, you may proceed.
7. If you need more info, ask — don't guess.

CAPABILITIES:
- Create complete projects (websites, apps, scripts)
- Debug and fix code
- Explain programming concepts
- Review and analyze code
- Refactor and optimize
- Run terminal commands
- Remember projects for future improvements

You are chatting in a terminal CLI. Keep formatting clean and readable.
"""

# ──────────────────────────────────────────────────────────────
# INTENT CLASSIFICATION — uses LLM for smart classification
# ──────────────────────────────────────────────────────────────
INTENT_PROMPT = """Classify this user message into ONE of these categories:

- "chat" → casual conversation, greetings, small talk, thanks, general questions
- "ask" → asking about coding concepts, "how does X work", "what is Y"
- "create" → wants to BUILD or CREATE something new (website, app, project, script)
- "design" → wants to design UI/UX, generate aesthetic templates or design systems
- "debug" → wants to FIX a bug, error, or issue
- "review" → wants CODE REVIEW or analysis
- "refactor" → wants to IMPROVE, OPTIMIZE, or REFACTOR existing code
- "run" → wants to EXECUTE a command or run something
- "improve" → wants to ADD features or UPDATE an existing project
- "confirm" → user is saying "yes", "go ahead", "do it", "proceed", "sure"

IMPORTANT RULES:
- Short casual messages like "hi", "hello", "thanks" → "chat"
- Questions about concepts → "ask"
- Only classify as "create" if user CLEARLY wants something built
- If ambiguous, default to "chat"

User message: "{user_input}"

Respond with ONLY the category name, nothing else."""

# ──────────────────────────────────────────────────────────────
# SMALLER, CLEANER BANNER
# ──────────────────────────────────────────────────────────────
BANNER = """
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


# ──────────────────────────────────────────────────────────────
# KEYWORD-BASED FAST INTENT (fallback when LLM is slow/unavailable)
# ──────────────────────────────────────────────────────────────
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
    # Order matters! More specific intents first, broader ones later.
    ("run", ["run ", "execute ", "start ", "install ", "test "]),
    ("debug", ["debug", "fix ", "error", "bug", "issue", "broken", "crash", "not working"]),
    ("refactor", ["refactor", "optimize", "clean up", "restructure"]),
    ("review", ["review", "analyze", "look at", "check my"]),
    ("improve", ["improve", "add feature", "update", "upgrade", "enhance"]),
    ("design", ["design", " ui ", " ux ", "template", "aesthetic", "ui design", "ux design"]),
    ("create", ["create ", "build ", "make ", "generate ", "new project", "write a "]),
]


class BharatCode:
    def __init__(self, session_id=None):
        self.model = os.getenv("DEFAULT_MODEL", get_default_model())
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.conversation_history = []  # Actual conversation memory
        self.memory = get_memory()
        self.current_project = None
        self.pending_task = None  # For tracking tasks awaiting confirmation
        self.max_history = 20  # Keep last N messages for context

        # Pixel Agents JSONL logging support
        self.session_id = session_id or str(uuid.uuid4())
        cwd = os.getcwd()
        dir_name = re.sub(r"[^a-zA-Z0-9\-]", "-", cwd)
        self.log_dir = os.path.expanduser(f"~/.bharatcode/projects/{dir_name}")
        os.makedirs(self.log_dir, exist_ok=True)
        self.jsonl_log = os.path.join(self.log_dir, f"{self.session_id}.jsonl")

        # Write an initial clear text log if we just created it
        if not os.path.exists(self.jsonl_log):
            open(self.jsonl_log, 'w').close()
            
    def _log_event(self, event_type: str, data: dict):
        """Append an event to the JSONL log for pixel-agents."""
        if not getattr(self, "jsonl_log", None):
            return
        
        record = {"type": event_type}
        record.update(data)
        
        try:
            with open(self.jsonl_log, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass
            
    def _log_turn_end(self):
        self._log_event("system", {"subtype": "turn_duration"})
        self.pending_task = None  # Clear pending task after each turn

    # ──────────────────────────────────────────────────────────
    # INTENT DETECTION — smart, multi-layered
    # ──────────────────────────────────────────────────────────
    def detect_intent(self, text):
        """
        Multi-layered intent detection:
        1. Check for confirmation patterns first
        2. Check for casual chat patterns
        3. Keyword-based fast classification
        4. Falls back to LLM classification for ambiguous cases
        """
        text_lower = text.lower().strip()

        # Layer 1: Is this a confirmation?
        if text_lower in CONFIRM_PATTERNS or any(p in text_lower for p in CONFIRM_PATTERNS):
            if self.pending_task:
                return "confirm"

        # Layer 2: Is this casual chat?
        if text_lower in CHAT_PATTERNS or any(
            text_lower.startswith(p) for p in CHAT_PATTERNS
        ):
            return "chat"

        # Layer 2b: Questions → "ask" (check before short-message filter)
        if text_lower.startswith(("what ", "what's ", "how ", "why ", "can you explain", "explain", "tell me about")):
            return "ask"

        # Very short messages (1-3 words) without action keywords → chat
        if len(text_lower.split()) <= 3:
            has_action_keyword = False
            for _intent, keywords in INTENT_KEYWORDS:
                if any(kw in text_lower for kw in keywords):
                    has_action_keyword = True
                    break
            if not has_action_keyword:
                return "chat"

        # Layer 3: Keyword-based classification
        # Check for improvement (must have "improve" + project reference)
        if ("improve" in text_lower or "add" in text_lower or "update" in text_lower) and (
            "project" in text_lower
            or "my " in text_lower
            or "the " in text_lower
            or self.current_project
        ):
            return "improve"

        for intent, keywords in INTENT_KEYWORDS:
            for kw in keywords:
                if kw in text_lower:
                    return intent

        # Default to chat for anything ambiguous
        return "chat"

    # ──────────────────────────────────────────────────────────
    # CONVERSATION MANAGEMENT
    # ──────────────────────────────────────────────────────────
    def add_to_history(self, role, content):
        """Add message to conversation history with trimming"""
        self.conversation_history.append({"role": role, "content": content})
        # Keep history manageable
        if len(self.conversation_history) > self.max_history * 2:
            # Keep system prompt + last N messages
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_chat_messages(self, user_message):
        """Build messages array with system prompt + history + new message"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history for context
        for msg in self.conversation_history[-self.max_history:]:
            messages.append(msg)

        # Add current message
        messages.append({"role": "user", "content": user_message})
        return messages

    # ──────────────────────────────────────────────────────────
    # CHAT WITH AI — conversational, context-aware
    # ──────────────────────────────────────────────────────────
    def chat_with_ai(self, user_message, is_ask=False):
        """Send a conversational message with full history"""
        messages = self.get_chat_messages(user_message)

        with console.status("[bold cyan]Thinking...[/]", spinner="dots"):
            result = route_chat(messages)

        if result:
            self.add_to_history("user", user_message)
            self.add_to_history("assistant", result)
            self._log_event("assistant", {"message": {"content": [{"type": "text", "text": result}]}})

        return result

    # ──────────────────────────────────────────────────────────
    # BANNER & WELCOME
    # ──────────────────────────────────────────────────────────
    def print_banner(self):
        console.clear()
        console.print(BANNER)

        if not self.api_key:
            console.print(
                Panel(
                    "[yellow]⚠️  No API Key set![/]\n\n"
                    "Get a free key → [link=https://openrouter.ai/settings/keys][cyan]openrouter.ai/settings/keys[/cyan][/link]\n"
                    "Then type: [bold cyan]/setkey YOUR_KEY[/]",
                    title="🔑 Quick Setup",
                    border_style="yellow",
                    width=60,
                )
            )
        else:
            status_table = Table(show_header=False, box=None, padding=(0, 1))
            status_table.add_column(style="dim")
            status_table.add_column()
            status_table.add_row("Status", "[green]● Online[/]")
            status_table.add_row("Model", f"[cyan]{self.model}[/]")
            status_table.add_row("Type", "[bold]/help[/] for commands")

            console.print(
                Panel(
                    status_table,
                    title="[bold green]✓ Ready[/]",
                    border_style="green",
                    width=60,
                )
            )

    def print_welcome(self):
        """Friendly welcome message"""
        console.print()
        console.print(
            "[bold bright_cyan]Hey there! 👋[/] I'm [bold]BharatCode[/] — your AI coding companion.\n"
        )
        console.print(
            "  [dim]•[/] Chat with me about anything coding-related\n"
            "  [dim]•[/] Ask me to [bold]create[/], [bold]debug[/], [bold]review[/], or [bold]explain[/] code\n"
            "  [dim]•[/] Type [bold cyan]/help[/] for all commands\n"
        )
        console.print("[dim]Just type naturally — I'll understand what you need.[/]\n")

    def print_help(self):
        console.print()

        # Commands table
        cmd_table = Table(
            title="[bold bright_cyan]⌨️  Commands[/]",
            show_header=True,
            header_style="bold",
            border_style="bright_black",
            width=60,
        )
        cmd_table.add_column("Command", style="cyan", width=20)
        cmd_table.add_column("Description", width=38)
        cmd_table.add_row("/setkey <key>", "Set your OpenRouter API key")
        cmd_table.add_row("/models", "List available AI models")
        cmd_table.add_row("/set <model>", "Switch to a different model")
        cmd_table.add_row("/shell <cmd>", "Run a terminal command")
        cmd_table.add_row("/read <file>", "Read a file's contents")
        cmd_table.add_row("/ls [dir]", "List files in directory")
        cmd_table.add_row("/design", "Start UI/UX expert mode")
        cmd_table.add_row("/projects", "View your saved projects")
        cmd_table.add_row("/use <name>", "Set active project")
        cmd_table.add_row("/clear", "Clear the screen")
        cmd_table.add_row("/help", "Show this help")
        cmd_table.add_row("exit", "Quit BharatCode")

        console.print(cmd_table)

        console.print(
            "\n[dim]💡 Tip: You don't need commands — just chat naturally![/]\n"
            '[dim]   Example: "create a portfolio website with dark theme"[/]\n'
            '[dim]   Example: "explain how async/await works in Python"[/]\n'
            '[dim]   Example: "debug this function that keeps crashing"[/]\n'
        )

    def print_models(self):
        console.print()
        model_table = Table(
            title="[bold bright_cyan]🤖 Available Models[/]",
            show_header=True,
            header_style="bold",
            border_style="bright_black",
        )
        model_table.add_column("Provider", style="cyan")
        model_table.add_column("Model Name")
        model_table.add_column("Model ID", style="dim")

        for provider, info in FREE_CODING_MODELS.items():
            for model in info["models"]:
                model_table.add_row(
                    provider.upper(), model["name"], model["id"]
                )

        console.print(model_table)
        console.print(f"\n[dim]Current model: [bold]{self.model}[/bold][/dim]\n")

    # ──────────────────────────────────────────────────────────
    # TASK HANDLERS — each asks clarifying questions first
    # ──────────────────────────────────────────────────────────
    def handle_chat(self, message):
        """Handle casual conversation"""
        return self.chat_with_ai(message)

    def handle_ask(self, question):
        """Handle concept explanation questions"""
        return self.chat_with_ai(question)

    def handle_create(self, task):
        """Handle creation tasks — ask clarifying questions first, then build"""
        # Check if we already have enough details (task is specific)
        needs_clarification = len(task.split()) < 8 or any(
            word in task.lower() for word in ["something", "stuff", "thing", "website", "app", "project"]
        )

        if needs_clarification and not self.pending_task:
            # First, ask clarifying questions
            clarification_prompt = f"""The user wants to create something: "{task}"

Before building, ask 2-3 brief clarifying questions:
- What exactly they want (features, purpose)
- Any tech stack preferences (React, vanilla JS, Python, etc.)
- Design preferences (modern, minimal, colorful, dark mode, etc.)

Be conversational and friendly. End with "Once you tell me, I'll start building right away!"
"""
            response = self.chat_with_ai(clarification_prompt)

            # Store the pending task for later confirmation
            self.pending_task = {
                "type": "create",
                "original_request": task,
                "clarification_asked": True,
            }
            return response
        else:
            # User already provided details or is confirming — start building
            if self.pending_task and self.pending_task.get("type") == "create":
                # Combine original request with any clarification from conversation
                recent_context = "\n".join(
                    f"{msg['role']}: {msg['content']}"
                    for msg in self.conversation_history[-6:]
                )
                full_task = f"{self.pending_task['original_request']}\n\nRequirements from conversation:\n{recent_context}"
                self.pending_task = None
                return self.handle_create_confirmed(full_task)
            else:
                # Direct creation with full task
                return self.handle_create_confirmed(task)

    def handle_create_confirmed(self, task):
        """Actually execute the creation with full expert agent team"""
        console.print()
        console.print("[bold bright_green]🚀 Building your project with expert AI team...[/]\n")

        project_name = self._extract_project_name(task) or "MyProject"

        # Use the Expert Agent Orchestrator for multi-agent collaboration
        console.print("[dim]📋 Phase 1: Expert Planning...[/]")
        console.print("[dim]🏗️  Phase 2: Architecture Design...[/]")
        console.print("[dim]⚡ Phase 3: Expert Execution...[/]")
        console.print("[dim]🔬 Phase 4: Code Review...[/]")
        console.print("[dim]✨ Phase 5: Continuous Improvement...[/]")
        console.print("[dim]🧠 Phase 6: Auto-Learning & Evolution...[/]\n")

        with console.status("[bold cyan]Expert team building your project...[/]", spinner="dots"):
            # Use ExpertAgentOrchestrator for full multi-agent workflow
            orchestrator = ExpertAgentOrchestrator(project_name=project_name)
            result = orchestrator.execute_expert_workflow(task)

        if project_name:
            self.current_project = project_name

        # Format result for display
        if isinstance(result, dict):
            output = f"\n[bold green]✅ PROJECT COMPLETE: {project_name}[/]\n\n"
            if 'summary' in result:
                output += f"[dim]{result['summary']}[/]\n"
            if 'files_created' in result:
                output += f"\n[bold]📁 Files Created:[/]\n"
                for f in result['files_created'][:10]:
                    output += f"  [cyan]• {f}[/]\n"
            if 'project_path' in result:
                output += f"\n[dim]Location: {result['project_path']}[/]\n"
            return output
        return str(result)

    def handle_debug(self, task):
        """Handle debugging — conversational approach"""
        return self.chat_with_ai(
            f"I need help debugging something: {task}\n\n"
            "Please help me identify and fix the issue. "
            "Ask me for more details if you need them (like error messages, code snippets, etc)."
        )

    def handle_review(self, task):
        """Handle code review — conversational"""
        return self.chat_with_ai(
            f"I'd like you to review: {task}\n\n"
            "Please analyze it and give constructive feedback. "
            "If I haven't shared the code yet, ask me to share it."
        )

    def handle_refactor(self, task):
        """Handle refactoring — conversational"""
        return self.chat_with_ai(
            f"I want to improve/refactor: {task}\n\n"
            "Please suggest improvements. If you need to see the code, ask me to share it."
        )

    def handle_run(self, task):
        """Handle execution tasks"""
        # If it's a clear command, confirm before running
        if "run " in task.lower():
            cmd_part = task.lower().split("run ", 1)[1].strip()

            console.print(
                f"\n[yellow]⚡ You want me to run:[/] [bold cyan]{cmd_part}[/]"
            )

            if Confirm.ask("[dim]Should I go ahead?[/dim]", default=True):
                with console.status("[bold cyan]Running command...[/]", spinner="dots"):
                    executor = AdvancedExecutor()
                    result = executor.run_command(cmd_part, timeout=60)

                if result["success"]:
                    output = result.get("stdout", "") or result.get("stderr", "")
                    return f"[green]✓ Command executed successfully![/]\n\n```\n{output[:1000]}\n```"
                else:
                    return f"[red]✗ Error:[/] {result.get('stderr', 'Unknown error')}"
            else:
                return "[dim]Okay, cancelled.[/dim]"

        # Otherwise, chat about it
        return self.chat_with_ai(
            f"Help me execute this: {task}\n\n"
            "What commands should I run? Walk me through it step by step."
        )

    def handle_design(self, task):
        """Handle UI/UX design requests"""
        console.print()
        console.print("[bold bright_purple]🎨 Launching UI/UX Design Expert...[/]\n")

        project_name = self._extract_project_name(task) or self.current_project or "New Design Project"
        
        tool_id = str(uuid.uuid4())
        self._log_event("assistant", {"message": {"content": [{"type": "tool_use", "id": tool_id, "name": "Task", "input": {"description": f"Design {project_name}"}}]}})

        with console.status(f"[bold purple]Designing {project_name}...[/]", spinner="dots"):
            orchestrator = create_design_orchestrator()
            result = orchestrator.create_complete_design(
                project_name=project_name,
                requirements=task,
                aesthetic="GLASSMORPHISM",
                palette="COOL_TONES"
            )

        html_file = f"{project_name.replace(' ', '_').lower()}.html"
        with open(html_file, "w") as f:
            f.write(result['exports']['html']['content'])

        # Create CSS file next to it for the user
        css_file = f"{project_name.replace(' ', '_').lower()}.css"
        with open(css_file, "w") as f:
            f.write(result['exports']['css']['content'])
            
        self._log_event("user", {"message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "done"}]}})

        return f"[green]✓ Design generated successfully![/]\n\n" \
               f"🎨 A visually stunning, production-ready, watermark-free design was created.\n" \
               f"📁 Saved HTML to: `[cyan]{html_file}[/cyan]`\n" \
               f"📁 Saved CSS to: `[cyan]{css_file}[/cyan]`\n\n" \
               f"You can view this file in your browser!"

    def handle_improve(self, task):
        """Handle project improvement"""
        project_name = self._extract_project_name(task)

        if not project_name:
            project_name = self.current_project

        if not project_name:
            return self.chat_with_ai(
                f"The user wants to improve something: {task}\n\n"
                "Ask which project they want to improve. List any projects you know about."
            )

        # Ask about improvement details first
        return self.chat_with_ai(
            f"The user wants to improve project '{project_name}': {task}\n\n"
            "Discuss what improvements they want, confirm understanding, "
            "and then describe what changes you'd make."
        )

    def handle_confirm(self):
        """Handle user confirmation for pending task"""
        if not self.pending_task:
            return self.chat_with_ai("I'm ready to help! What would you like me to do?")

        task_type = self.pending_task["type"]
        original_request = self.pending_task["original_request"]
        self.pending_task = None  # Clear pending task

        if task_type == "create":
            # Get the full context from conversation history
            recent_context = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in self.conversation_history[-6:]
            )
            full_task = f"{original_request}\n\nAdditional context from our conversation:\n{recent_context}"
            return self.handle_create_confirmed(full_task)

        return "Okay, proceeding!"

    # ──────────────────────────────────────────────────────────
    # MAIN TASK ROUTER
    # ──────────────────────────────────────────────────────────
    def run_task(self, user_input):
        """Route user input to appropriate handler"""
        intent = self.detect_intent(user_input)

        handlers = {
            "chat": self.handle_chat,
            "ask": self.handle_ask,
            "create": self.handle_create,
            "debug": self.handle_debug,
            "review": self.handle_review,
            "refactor": self.handle_refactor,
            "run": self.handle_run,
            "improve": self.handle_improve,
            "design": self.handle_design,
        }

        if intent == "confirm":
            return self.handle_confirm()

        handler = handlers.get(intent, self.handle_chat)
        return handler(user_input)

    # ──────────────────────────────────────────────────────────
    # UTILITIES
    # ──────────────────────────────────────────────────────────
    def _extract_project_name(self, task):
        """Extract project name from task"""
        words = task.lower().split()
        for word in ["called", "named", "name"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip(".,!?\"'")
                    if name and len(name) > 1:
                        return name
        return None

    def handle_shell(self, command):
        tool_id = str(uuid.uuid4())
        self._log_event("assistant", {"message": {"content": [{"type": "tool_use", "id": tool_id, "name": "Bash", "input": {"command": command}}]}})
        
        executor = AdvancedExecutor()
        result = executor.run_command(command, timeout=60)

        self._log_event("user", {"message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "done"}]}})

        if result["success"]:
            output = result.get("stdout", "") or result.get("stderr", "")
            return f"[green]✓ Done![/]\n\n```\n{output[:1000]}\n```"
        else:
            return f"[red]✗ Error:[/] {result.get('stderr', 'Unknown error')}"

    def handle_read(self, filepath):
        tool_id = str(uuid.uuid4())
        self._log_event("assistant", {"message": {"content": [{"type": "tool_use", "id": tool_id, "name": "Read", "input": {"file_path": filepath}}]}})
        
        executor = AdvancedExecutor()
        result = executor.read_file(filepath)
        
        self._log_event("user", {"message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "done"}]}})

        if result["success"]:
            content = result["content"]
            lines = result.get("lines", "?")
            size = result.get("size", "?")
            header = f"[dim]📄 {filepath} ({lines} lines, {size} bytes)[/dim]\n\n"
            if len(content) > 3000:
                return f"{header}```\n{content[:3000]}\n... (truncated)\n```"
            return f"{header}```\n{content}\n```"
        return f"[red]✗[/] {result.get('error', 'File not found')}"

    def handle_ls(self, directory="."):
        tool_id = str(uuid.uuid4())
        self._log_event("assistant", {"message": {"content": [{"type": "tool_use", "id": tool_id, "name": "Glob", "input": {}}]}})
        
        executor = AdvancedExecutor()
        result = executor.list_files(directory)

        self._log_event("user", {"message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "done"}]}})

        if result["success"]:
            files = result.get("files", [])
            if not files:
                return f"[dim]📁 {directory} — empty[/dim]"

            output = f"[bold]📁 {directory}[/] ({len(files)} files)\n\n"
            for f in files[:30]:
                path = f if isinstance(f, str) else f.get("path", str(f))
                output += f"  [cyan]•[/] {path}\n"
            if len(files) > 30:
                output += f"\n  [dim]... and {len(files) - 30} more[/dim]"
            return output
        return f"[red]✗[/] {result.get('error', 'Directory not found')}"

    # ──────────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────────
    def run(self):
        self.print_banner()
        self.print_welcome()

        while True:
            try:
                # Clean, friendly prompt
                prompt_text = "[bold bright_cyan]you ›[/] " if not self.current_project else f"[bold bright_cyan]you[/] [dim]({self.current_project})[/] [bold bright_cyan]›[/] "
                user_input = console.input(prompt_text).strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[bold bright_yellow]👋 See you later![/]\n")
                break

            if not user_input:
                continue
                
            self._log_event("user", {"message": {"content": user_input}})

            # Exit
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print(
                    "\n[bold bright_yellow]👋 Thanks for coding with me! See you next time![/]\n"
                )
                break

            # Slash commands
            if user_input.startswith("/"):
                self._handle_slash_command(user_input)
                self._log_turn_end()
                continue

            # Route to task handler
            try:
                result = self.run_task(user_input)
                self._log_turn_end()

                if result:
                    console.print()
                    # Try to render as markdown for better formatting
                    try:
                        if any(marker in result for marker in ["```", "**", "# ", "- ", "1. "]):
                            console.print(
                                Panel(
                                    Markdown(result),
                                    border_style="bright_black",
                                    padding=(1, 2),
                                )
                            )
                        else:
                            console.print(
                                Panel(
                                    result,
                                    border_style="bright_black",
                                    padding=(1, 2),
                                )
                            )
                    except Exception:
                        console.print(result)
                    console.print()
                else:
                    console.print(
                        "\n[dim]Hmm, I didn't get a response. Try again or rephrase?[/]\n"
                    )

            except Exception as e:
                console.print(
                    f"\n[red]Oops! Something went wrong:[/] [dim]{str(e)}[/]\n"
                    "[dim]Try again or type /help for options.[/]\n"
                )

    def _handle_slash_command(self, user_input):
        """Process slash commands"""
        parts = user_input.split(maxsplit=2)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/setkey" and arg:
            self.api_key = arg
            os.environ["OPENROUTER_API_KEY"] = arg
            console.print("\n[green]✓[/] API key set! You're all set to go. 🎉\n")

        elif cmd == "/models":
            self.print_models()

        elif cmd == "/set" and arg:
            self.model = arg
            os.environ["DEFAULT_MODEL"] = arg
            console.print(f"\n[green]✓[/] Switched to model: [bold cyan]{arg}[/]\n")

        elif cmd == "/shell" and arg:
            console.print(f"\n[dim]Running: {arg}[/dim]")
            result = self.handle_shell(arg)
            console.print(Panel(result, border_style="bright_black"))

        elif cmd == "/read":
            if not arg:
                console.print("\n[yellow]Usage:[/] /read <filepath>\n")
            else:
                result = self.handle_read(arg)
                console.print(Panel(result, border_style="bright_black"))

        elif cmd == "/ls":
            result = self.handle_ls(arg or ".")
            console.print(Panel(result, border_style="bright_black"))

        elif cmd == "/projects":
            projects = self.memory.list_projects()
            if projects:
                console.print("\n[bold]📁 Your Projects:[/]\n")
                for p in projects:
                    name = p.get("name", "unnamed")
                    request = p.get("request", "")[:50]
                    folder = p.get("folder", "")
                    console.print(f"  [cyan]•[/] [bold]{name}[/] — {request}...")
                    console.print(f"    [dim]{folder}[/]")
                console.print()
            else:
                console.print(
                    "\n[dim]No projects yet. Ask me to create one![/]\n"
                )

        elif cmd == "/design":
            task = user_input[7:].strip()
            if not task:
                console.print("\n[yellow]Usage:[/] /design <description of what you want>\n[dim]Example: /design a dark mode SaaS dashboard[/dim]\n")
            else:
                result = self.handle_design(task)
                console.print(Panel(result, border_style="bright_black"))

        elif cmd == "/use" and arg:
            self.current_project = arg.strip()
            console.print(
                f"\n[green]✓[/] Working on project: [bold]{self.current_project}[/]\n"
            )

        elif cmd == "/clear":
            console.clear()
            self.print_banner()

        elif cmd in ["/help", "/h"]:
            self.print_help()

        else:
            console.print(
                f"\n[yellow]Unknown command:[/] {cmd}\n"
                "[dim]Type /help to see available commands.[/]\n"
            )


def main():
    parser = argparse.ArgumentParser(description="BharatCode Dev")
    parser.add_argument("--session-id", type=str, help="Session ID for pixel-agents JSONL tracking")
    args, unknown = parser.parse_known_args()
    
    app = BharatCode(session_id=args.session_id)
    app.run()


if __name__ == "__main__":
    main()
