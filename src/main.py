import os
import sys
import subprocess
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from brain.models import get_available_models, FREE_CODING_MODELS
from orchestrator import Orchestrator

console = Console()

INTENT_KEYWORDS = {
    "generate": ["create", "write", "make", "generate", "build", "add", "new"],
    "run": ["run", "execute", "start", "launch", "test"],
    "debug": ["debug", "fix", "error", "bug", "issue", "problem"],
    "refactor": ["refactor", "improve", "optimize", "clean", "simplify"],
    "explain": ["explain", "what", "how", "why", "describe", "understand"],
    "review": ["review", "check", "verify", "validate", "audit"],
}

ONBOARDING_TIPS = [
    "💡 Tip: Type /help to see all commands",
    "💡 Tip: Use /set ollama:modelname to switch models",
    "💡 Tip: Ollama must be running: run 'ollama serve' in another terminal",
    "💡 Tip: Install models: run 'ollama pull modelname' in another terminal",
    "💡 Tip: /models shows available models you can use",
    "💡 Tip: /mode lets you choose between Plan/Execute/Review/Auto modes",
]

ERROR_HELP = {
    "not found": "🔧 The model is not installed. Run 'ollama pull <model-name>' in a separate terminal, then restart BharatCode.",
    "ollama serve": "🔧 Ollama is not running. Open a new terminal and run: ollama serve",
    "invalid api key": "🔧 Your API key is invalid. Get a new key from the provider's website.",
    "api key not set": "🔧 API key not found. Add it to the .env file or use Ollama (free, no key needed).",
    "connection": "🔧 Cannot connect. Make sure Ollama is running: 'ollama serve'",
    "timeout": "⏱️ Request timed out. Try again or use a smaller model.",
}

GUIDE_MESSAGES = {
    "ollama": """
🤖 [bold]Using Ollama (Local Models)[/bold]

Ollama runs models locally on your computer - 100% free, no API keys needed!

[green]✓[/green] Advantages:
  • Free forever
  • No internet needed
  • Your data stays private

[yellow]![/yellow] To use:
  1. Make sure Ollama is installed
  2. Run [cyan]ollama serve[/cyan] in a separate terminal
  3. Install models: [cyan]ollama pull <model-name>[/cyan]
  4. Use in BharatCode: /set ollama:starcoder2

[bold]Popular Models:[/bold]
  • starcoder2 - Great for code
  • llama3.2 - General purpose
  • deepseek-coder-v2 - Coding focused
""",
    "first_time": """
👋 [bold]Welcome to BharatCode![/bold]

I'm your coding assistant. Here's how to get started:

[bold]Quick Start:[/bold]
  1. Type any coding question or task
  2. I'll help you write, debug, or explain code

[bold]Commands:[/bold]
  • /help - Show all commands
  • /models - See available models  
  • /set ollama:starcoder2 - Switch to local model
  • /mode - Choose workflow mode

[bold]Need Help?[/bold]
  Just ask! I'll guide you through any issues.
""",
}

BANNER = """
[bold yellow]BBBBBBBBBBBBBBBBBB   HHHHHHHHH     HHHHHHHHH               AAA               RRRRRRRRRRRRRRRRR                  AAA         TTTTTTTTTTTTTTTTTTTTTTT[/]
[bold yellow]B::::::::::::::::B  H:::::::H     H:::::::H              A:::A              R::::::::::::::::R                A:::A        T:::::::::::::::::::::T[/]
[bold yellow]B::::::BBBBBB:::::B H:::::::H     H:::::::H             A:::::A             R::::::RRRRRR:::::R              A:::::A       T:::::::::::::::::::::T[/]
[bold yellow]BB:::::B     B:::::BHH::::::H     H::::::HH            A:::::::A            RR:::::R     R:::::R            A:::::::A      T:::::TT:::::::TT:::::T[/]
[bold yellow]  B::::B     B:::::B  H:::::H     H:::::H             A:::::::::A             R::::R     R:::::R           A:::::::::A     TTTTTT  T:::::T  TTTTTT[/]
[bold yellow]  B::::B     B:::::B  H:::::H     H:::::H            A:::::A:::::A            R::::R     R:::::R          A:::::A:::::A            T:::::T[/]
[bold yellow]  B::::BBBBBB:::::B   H::::::HHHHH::::::H           A:::::A A:::::A           R::::RRRRRR:::::R          A:::::A A:::::A           T:::::T[/]
[bold yellow]  B:::::::::::::BB    H:::::::::::::::::H          A:::::A   A:::::A          R:::::::::::::RR          A:::::A   A:::::A          T:::::T[/]
[bold yellow]  B::::BBBBBB:::::B   H:::::::::::::::::H         A:::::A     A:::::A         R::::RRRRRR:::::R        A:::::A     A:::::A         T:::::T[/]
[bold yellow]  B::::B     B:::::B  H::::::HHHHH::::::H        A:::::AAAAAAAAA:::::A        R::::R     R:::::R      A:::::AAAAAAAAA:::::A        T:::::T[/]
[bold yellow]  B::::B     B:::::B  H:::::H     H:::::H       A:::::::::::::::::::::A       R::::R     R:::::R     A:::::::::::::::::::::A       T:::::T[/]
[bold yellow]  B::::B     B:::::B  H:::::H     H:::::H      A:::::AAAAAAAAAAAAA:::::A      R::::R     R:::::R    A:::::AAAAAAAAAAAAA:::::A      T:::::T[/]
[bold yellow]BB:::::BBBBBB::::::BHH::::::H     H::::::HH   A:::::A             A:::::A   RR:::::R     R:::::R   A:::::A             A:::::A   TT:::::::TT[/]
[bold yellow]B:::::::::::::::::B H:::::::H     H:::::::H  A:::::A               A:::::A  R::::::R     R:::::R  A:::::A               A:::::A  T:::::::::T[/]
[bold yellow]B::::::::::::::::B  H:::::::H     H:::::::H A:::::A                 A:::::A R::::::R     R:::::R A:::::A                 A:::::A T:::::::::T[/]
[bold yellow]BBBBBBBBBBBBBBBBB   HHHHHHHHH     HHHHHHHHHAAAAAAA                   AAAAAAARRRRRRRR     RRRRRRRAAAAAAA                   AAAAAAATTTTTTTTTTT[/]

[bold cyan]CCCCCCCCCCCCCCCC   OOOOOOOOO     DDDDDDDDDDDDD      EEEEEEEEEEEEEEEEEEEEEE[/]
[bold cyan]CCC::::::::::::C   OO:::::::::OO   D::::::::::::DDD   E::::::::::::::::::::E[/]
[bold cyan]CC:::::::::::::::C OO:::::::::::::OO D:::::::::::::::DD E::::::::::::::::::::E[/]
[bold cyan]C:::::CCCCCCCC::::CO:::::::OOO:::::::ODDD:::::DDDDD:::::DEE::::::EEEEEEEEE::::E[/]
[bold cyan]C:::::C       CCCCCCO::::::O   O::::::O  D:::::D    D:::::DE:::::E       EEEEEE[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE:::::E[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE::::::EEEEEEEEEE[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE:::::::::::::::E[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE:::::::::::::::E[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE::::::EEEEEEEEEE[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE:::::E[/]
[bold cyan]C:::::C       CCCCCCO::::::O   O::::::O  D:::::D    D:::::DE:::::E       EEEEEE[/]
[bold cyan]C:::::CCCCCCCC::::CO:::::::OOO:::::::ODDD:::::DDDDD:::::DEE::::::EEEEEEEEE::::E[/]
[bold cyan]CC:::::::::::::::C OO:::::::::::::OO D:::::::::::::::DD E::::::::::::::::::::E[/]
[bold cyan]CCC::::::::::::C   OO:::::::::OO   D::::::::::::DDD   E::::::::::::::::::::E[/]
[bold cyan]CCCCCCCCCCCCCCCC     OOOOOOOOO     DDDDDDDDDDDDD      EEEEEEEEEEEEEEEEEEEEEE[/]
"""

MODES = {
    "1": ("Plan", "Break down tasks into steps"),
    "2": ("Execute", "Generate code and run tools"),
    "3": ("Review", "Review and finalize code"),
    "4": ("Auto", "Full agentic workflow (Plan → Execute → Review)"),
}


class BharatCodeTUI:
    def __init__(self):
        self.orch = Orchestrator()
        self.mode = "auto"
        self.current_model = os.getenv("DEFAULT_MODEL", "ollama:starcoder2")
        self.conversation = []

    def print_banner(self):
        console.clear()
        console.print(BANNER, justify="center")
        console.print(
            Panel.fit(
                "[dim]Open Source AI Coding Agent[/dim]",
                border_style="yellow",
                width=60,
            )
        )
        console.print(
            f"\n[dim]Model:[/dim] {self.current_model}  [dim]Mode:[/dim] {self.mode.upper()}\n"
        )
        console.print(GUIDE_MESSAGES["first_time"])

    def show_guide(self, topic=None):
        if topic and topic in GUIDE_MESSAGES:
            console.print(Panel(GUIDE_MESSAGES[topic], border_style="cyan"))
        else:
            console.print(Panel(GUIDE_MESSAGES["ollama"], border_style="cyan"))

    def handle_error(self, error_msg):
        error_lower = error_msg.lower()

        for key, help_msg in ERROR_HELP.items():
            if key in error_lower:
                console.print(
                    Panel(help_msg, title="🔧 Need Help?", border_style="yellow")
                )
                return

        if "model" in error_lower and "not found" in error_lower:
            console.print(
                Panel(
                    "The model you're trying to use is not installed.\n\n"
                    "Options:\n"
                    "1. Install it: [cyan]ollama pull <model-name>[/cyan] (in separate terminal)\n"
                    "2. Use a different model: [cyan]/set ollama:starcoder2[/cyan]\n"
                    "3. List installed models: [cyan]ollama list[/cyan]",
                    title="🔧 Model Not Found",
                    border_style="yellow",
                )
            )
            return

        console.print(
            Panel(
                "Something went wrong. Here's what might help:\n\n"
                "• Make sure Ollama is running: [cyan]ollama serve[/cyan]\n"
                "• Check model is installed: [cyan]ollama list[/cyan]\n"
                "• Type /help for general help\n"
                "• Type /guide for setup guide",
                title="❌ Error",
                border_style="red",
            )
        )

    def print_help(self):
        console.print("\n[bold]Commands:[/bold]")
        console.print("  [cyan]/guide[/cyan]   - Setup guide & help")
        console.print("  [cyan]/models[/cyan]  - List available models")
        console.print(
            "  [cyan]/set[/cyan]     - Set model (e.g., /set ollama:starcoder2)"
        )
        console.print("  [cyan]/mode[/cyan]    - Choose workflow mode")
        console.print("  [cyan]/clear[/cyan]   - Clear chat history")
        console.print("  [cyan]/history[/cyan] - Show conversation history")
        console.print("  [cyan]/help[/cyan]   - Show this help")
        console.print("  [cyan]exit[/cyan]    - Exit\n")

        console.print("\n[bold]Quick Tips:[/bold]")
        console.print("  • Ollama must be running: [cyan]ollama serve[/cyan]")
        console.print(
            "  • Install models in separate terminal: [cyan]ollama pull <name>[/cyan]"
        )
        console.print("  • /guide - Full setup guide\n")

        console.print("\n[bold]Intent Detection:[/bold]")
        console.print("  🔨 generate - create, write, make, build")
        console.print("  ▶️  run      - run, execute, test")
        console.print("  🐛 debug    - fix, error, bug, issue")
        console.print("  ♻️  refactor - improve, optimize, clean")
        console.print("  📖 explain  - explain, what, how, why\n")

    def print_models(self):
        console.print("\n[bold]=== Available Ollama Models (No API Key) ===[/bold]\n")
        console.print("[dim]Run 'ollama list' to see installed models[/dim]\n")

        from brain.models import FREE_CODING_MODELS

        for provider, info in FREE_CODING_MODELS.items():
            if not info.get("api_key_required", False):
                console.print(f"[bold green]✓ {provider.upper()}:[/bold green]")
                for model in info["models"]:
                    console.print(f"  • {model}")
                console.print()

        console.print(
            "\n[dim]Install more:[/dim] [cyan]ollama pull <model-name>[/cyan]"
        )
        console.print("[dim]Start Ollama:[/dim] [cyan]ollama serve[/cyan]\n")

    def set_model(self, model_id):
        if model_id.startswith("openrouter:"):
            console.print("[yellow]Note:[/yellow] OpenRouter requires API key.")
            console.print("Get free key: https://openrouter.ai/settings/keys")
            console.print("Then add to .env: OPENROUTER_API_KEY=your-key\n")
        os.environ["DEFAULT_MODEL"] = model_id
        self.current_model = model_id
        console.print(f"[green]✓[/green] Model set to: [bold]{model_id}[/bold]")

    def choose_mode(self):
        console.print("\n[bold]Select Mode:[/bold]")
        for key, (name, desc) in MODES.items():
            console.print(f"  [cyan]{key}[/cyan]. {name} - {desc}")
        choice = input("\n>> ")
        choice = choice.strip() or "4"
        if choice in MODES:
            self.mode = MODES[choice][0].lower()
            console.print(
                f"[green]✓[/green] Mode set to: [bold]{self.mode.upper()}[/bold]"
            )
        else:
            console.print("[red]Invalid choice, using Auto mode[/red]")
            self.mode = "auto"

    def detect_intent(self, user_input):
        user_input_lower = user_input.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    return intent
        return "generate"

    def format_code_output(self, result):
        if "```" in result:
            parts = result.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    code = part.split("\n", 1)
                    if len(code) > 1:
                        lang, code_block = code[0].strip(), code[1].rstrip("```")
                        syntax = Syntax(
                            code_block, lang, theme="monokai", line_numbers=True
                        )
                        console.print(syntax)
                    else:
                        console.print(part)
                else:
                    if part.strip():
                        console.print(part)
        else:
            console.print(result)

    def process_message(self, user_input):
        intent = self.detect_intent(user_input)

        intent_icons = {
            "generate": "🔨",
            "run": "▶️",
            "debug": "🐛",
            "refactor": "♻️",
            "explain": "📖",
            "review": "👀",
        }

        icon = intent_icons.get(intent, "🤖")

        if self.mode == "plan":
            console.print(f"\n{icon} [bold cyan]Planning...[/bold cyan]")
            result = self.orch.planner(user_input)
        elif self.mode == "execute":
            console.print(f"\n{icon} [bold cyan]Executing...[/bold cyan]")
            result = self.orch.executor(user_input)
        elif self.mode == "review":
            console.print(f"\n{icon} [bold cyan]Reviewing...[/bold cyan]")
            result = self.orch.reviewer(user_input)
        else:
            console.print(f"\n{icon} [bold cyan]Auto Mode ({intent})...[/bold cyan]")
            result = self.orch.run(user_input)
        return result

    def run(self, initial_message=None):
        self.print_banner()
        self.print_help()

        if initial_message:
            self.conversation.append(("user", initial_message))
            console.print(f"[yellow]>>>[/yellow] {initial_message}")
            result = self.process_message(initial_message)
            self.conversation.append(("assistant", result))
            console.print(Panel(result, border_style="green"))
            console.print()

        while True:
            try:
                user_input = input(f"{self.mode.upper()} >> ")
            except EOFError:
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if cmd == "/models":
                    self.print_models()
                elif cmd == "/set" and arg:
                    self.set_model(arg)
                elif cmd == "/mode":
                    self.choose_mode()
                elif cmd == "/clear":
                    self.conversation = []
                    self.print_banner()
                elif cmd == "/guide":
                    self.show_guide()
                elif cmd == "/history":
                    console.print("\n[bold]Conversation History:[/bold]")
                    for i, (role, msg) in enumerate(self.conversation):
                        role_icon = "👤" if role == "user" else "🤖"
                        console.print(f"{role_icon} {role.upper()}: {msg[:100]}...")
                    console.print()
                elif cmd in ["/help", "/h"]:
                    self.print_help()
                else:
                    console.print(f"[red]Unknown command:[/red] {cmd}")
                continue

            self.conversation.append(("user", user_input))
            result = self.process_message(user_input)
            self.conversation.append(("assistant", result))
            if result and not result.startswith("Error:"):
                console.print(
                    Panel(result, border_style="green", width=min(console.width, 100))
                )
            else:
                console.print(
                    Panel(result, border_style="red", width=min(console.width, 100))
                )
                if result:
                    self.handle_error(result)
            console.print()


def main():
    import typer

    app = typer.Typer()

    from typing import Optional

    @app.command(name="run")
    def run(
        message: Optional[str] = typer.Option(
            None, "--message", "-m", help="Initial message"
        ),
    ):
        """Start BharatCode CLI"""
        tui = BharatCodeTUI()
        tui.run(message)

    @app.command(name="models")
    def models():
        """List available models"""
        console.print("\n[bold]Available Free Models:[/bold]\n")
        for provider, info in FREE_CODING_MODELS.items():
            console.print(f"[bold cyan]{provider.upper()}:[/bold cyan]")
            for model in info["models"]:
                console.print(f"  • {model}")
            console.print()

    if len(sys.argv) == 1:
        sys.argv.append("run")

    app()


if __name__ == "__main__":
    main()
