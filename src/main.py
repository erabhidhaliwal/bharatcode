import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from brain.models import get_available_models, FREE_CODING_MODELS
from orchestrator import Orchestrator

console = Console()

MODES = {
    "1": ("Plan", "Break down tasks into steps"),
    "2": ("Execute", "Generate code and run tools"),
    "3": ("Review", "Review and finalize code"),
    "4": ("Auto", "Full agentic workflow (Plan → Execute → Review)"),
}


def print_header():
    console.print(
        Panel.fit(
            "[bold yellow]BharatCode[/bold yellow] - Open Source AI Coding Agent",
            border_style="yellow",
            subtitle="[dim]Model-agnostic CLI for agentic engineering[/dim]",
        )
    )


def print_models():
    console.print("\n[bold]Available Free Models:[/bold]\n")

    for provider, info in FREE_CODING_MODELS.items():
        console.print(f"[bold cyan]{provider.upper()}:[/bold cyan]")
        for model in info["models"]:
            console.print(f"  • {model}")
        console.print()


def print_help():
    console.print("\n[bold]Commands:[/bold]")
    console.print("  [cyan]/models[/cyan]     - List available free models")
    console.print(
        "  [cyan]/set <model>[/cyan] - Set default model (e.g., /set ollama:deepseek-coder-v2)"
    )
    console.print("  [cyan]/mode[/cyan]       - Choose workflow mode")
    console.print("  [cyan]/clear[/cyan]      - Clear screen")
    console.print("  [cyan]exit[/cyan]        - Exit")
    console.print()


def set_model(model_id):
    os.environ["DEFAULT_MODEL"] = model_id
    console.print(f"[green]✓[/green] Default model set to: [bold]{model_id}[/bold]")


def choose_mode():
    console.print("\n[bold]Select Mode:[/bold]")
    for key, (name, desc) in MODES.items():
        console.print(f"  [cyan]{key}[/cyan]. {name} - {desc}")

    choice = console.input("\n>> ")
    return MODES.get(choice, MODES["4"])[0].lower()


def main():
    print_header()

    current_model = os.getenv("DEFAULT_MODEL", "ollama:starcoder2")
    console.print(f"[dim]Using model:[/dim] [bold]{current_model}[/bold]\n")

    print_help()

    orch = Orchestrator()
    mode = "auto"

    while True:
        try:
            user = console.input(f"[yellow]{mode.upper()}[/yellow] >> ")
        except EOFError:
            break

        user = user.strip()

        if not user:
            continue

        if user.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Goodbye![/yellow]")
            break

        if user.startswith("/"):
            parts = user.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/models":
                print_models()
            elif cmd == "/set" and arg:
                set_model(arg)
                current_model = arg
            elif cmd == "/mode":
                mode = choose_mode()
            elif cmd == "/clear":
                console.clear()
                print_header()
            elif cmd == "/help":
                print_help()
            else:
                console.print(f"[red]Unknown command:[/red] {cmd}")
                console.print("Type /help for available commands")
            continue

        if mode == "plan":
            console.print("\n[bold cyan]🧠 Planning...[/bold cyan]")
            result = orch.planner(user)
        elif mode == "execute":
            console.print("\n[bold cyan]⚙️  Executing...[/bold cyan]")
            result = orch.executor(user)
        elif mode == "review":
            console.print("\n[bold cyan]🧐 Reviewing...[/bold cyan]")
            result = orch.reviewer(user)
        else:
            console.print("\n[bold cyan]🚀 Running Auto Mode...[/bold cyan]")
            result = orch.run(user)

        if result:
            console.print(
                Panel(result, title="[green]Result[/green]", border_style="green")
            )
        console.print()


if __name__ == "__main__":
    main()
