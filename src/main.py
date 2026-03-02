import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from brain.models import get_available_models, FREE_CODING_MODELS
from orchestrator import Orchestrator

console = Console()

BANNER = """
 ██████╗ ██████╗ ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗███████╗██╗ ██████╗ 
██╔════╝██╔═══██╗██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║██╔════╝ 
██║     ██║   ██║█████╗  ██╔████╔██║███████║██████╔╝   ██║   ███████╗██║██║      
██║     ██║   ██║██╔══╝  ██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ╚════██║██║██║      
╚██████╗╚██████╔╝███████╗██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ███████║██║╚██████╗ 
 ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝ ╚═════╝ 
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
        console.print(
            Panel.fit(
                Text(BANNER, style="bold yellow"),
                border_style="yellow",
                subtitle="[dim]Open Source AI Coding Agent[/dim]",
                subtitle_align="center",
            )
        )
        console.print(
            f"\n[dim]Model:[/dim] {self.current_model}  [dim]Mode:[/dim] {self.mode.upper()}\n"
        )

    def print_help(self):
        console.print("\n[bold]Commands:[/bold]")
        console.print("  [cyan]/models[/cyan]  - List available free models")
        console.print("  [cyan]/set[/cyan]     - Set default model")
        console.print("  [cyan]/mode[/cyan]    - Choose workflow mode")
        console.print("  [cyan]/clear[/cyan]   - Clear chat")
        console.print("  [cyan]/help[/cyan]    - Show this help")
        console.print("  [cyan]exit[/cyan]     - Exit\n")

    def print_models(self):
        console.print("\n[bold]Available Free Models:[/bold]\n")
        for provider, info in FREE_CODING_MODELS.items():
            console.print(f"[bold cyan]{provider.upper()}:[/bold cyan]")
            for model in info["models"]:
                console.print(f"  • {model}")
            console.print()

    def set_model(self, model_id):
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

    def process_message(self, user_input):
        if self.mode == "plan":
            console.print("\n[bold cyan]🧠 Planning...[/bold cyan]")
            result = self.orch.planner(user_input)
        elif self.mode == "execute":
            console.print("\n[bold cyan]⚙️  Executing...[/bold cyan]")
            result = self.orch.executor(user_input)
        elif self.mode == "review":
            console.print("\n[bold cyan]🧐 Reviewing...[/bold cyan]")
            result = self.orch.reviewer(user_input)
        else:
            console.print("\n[bold cyan]🚀 Running Auto Mode...[/bold cyan]")
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
                elif cmd in ["/help", "/h"]:
                    self.print_help()
                else:
                    console.print(f"[red]Unknown command:[/red] {cmd}")
                continue

            self.conversation.append(("user", user_input))
            result = self.process_message(user_input)
            self.conversation.append(("assistant", result))
            console.print(Panel(result, border_style="green"))
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
