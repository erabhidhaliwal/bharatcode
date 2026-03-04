import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from brain.models import FREE_CODING_MODELS, get_default_model
from brain.router import route_chat
from agents.autonomous import AutonomousAgent, TaskExecutor

console = Console()

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
[bold cyan]C:::::C              O:::::O     O::::::O  D:::::D     D:::::DE:::::::::::::::E[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE::::::EEEEEEEEEE[/]
[bold cyan]C:::::C              O:::::O     O:::::O  D:::::D     D:::::DE:::::E[/]
[bold cyan]C:::::C       CCCCCCO::::::O   O::::::O  D:::::D    D:::::DE:::::E       EEEEEE[/]
[bold cyan]C:::::CCCCCCCC::::CO:::::::OOO:::::::ODDD:::::DDDDD:::::DEE::::::EEEEEEEEE::::E[/]
[bold cyan]CC:::::::::::::::C OO:::::::::::::OO D:::::::::::::::DD E::::::::::::::::::::E[/]
[bold cyan]CCC::::::::::::C   OO:::::::::OO   D::::::::::::DDD   E::::::::::::::::::::E[/]
[bold cyan]CCCCCCCCCCCCCCCC     OOOOOOOOO     DDDDDDDDDDDDD      EEEEEEEEEEEEEEEEEEEEEE[/]
"""

INTENT_KEYWORDS = {
    "generate": ["create", "write", "make", "build", "add", "new", "website", "app"],
    "run": ["run", "execute", "start", "install", "test"],
    "debug": ["debug", "fix", "error", "bug", "issue"],
    "refactor": ["refactor", "improve", "optimize"],
    "explain": ["explain", "what", "how", "why"],
    "review": ["review", "check", "verify"],
}


class BharatCode:
    def __init__(self):
        self.model = os.getenv("DEFAULT_MODEL", get_default_model())
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.mode = "auto"
        self.conversation = []

    def detect_intent(self, text):
        text_lower = text.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return intent
        return "generate"

    def print_banner(self):
        console.clear()
        console.print(BANNER, justify="center")

        if not self.api_key:
            console.print(
                Panel(
                    "[yellow]⚠️  No API Key![/yellow]\n\n"
                    "Get free key: [cyan]https://openrouter.ai/settings/keys[/cyan]\n"
                    "Then: [cyan]/setkey YOUR_KEY[/cyan]",
                    title="🔑 Setup",
                    border_style="yellow",
                    width=60,
                )
            )
        else:
            console.print(
                Panel(
                    f"[green]✓[/green] Autonomous Agent Ready\nModel: {self.model}",
                    border_style="green",
                    width=60,
                )
            )

        console.print(f"\n[dim]Mode:[/dim] {self.mode.upper()}")
        console.print(
            "[dim]I can:[/dim] create files, run commands, build projects, debug & more!\n"
        )

    def print_help(self):
        console.print("""
[bold cyan]═══ Commands ═══[/bold cyan]
  /setkey <key>   Set OpenRouter API key
  /models         List available models
  /set <model>    Switch AI model
  /mode           Choose mode (auto/plan/execute/review)
  /shell <cmd>    Run terminal command
  /read <file>    Read a file
  /ls             List files
  /help           Show this help
  exit            Quit

[bold cyan]═══ What I can do ═══[/bold cyan]
  • Create websites, apps, scripts
  • Run terminal commands  
  • Debug errors
  • Read/write files
  • Build complete projects

[bold cyan]═══ Example Tasks ═══[/bold cyan]
  "create a Python calculator app"
  "build a todo list website"
  "install node modules for my project"
  "fix this bug in my code"
""")

    def print_models(self):
        console.print("\n[bold]Available Models:[/bold]\n")
        for provider, info in FREE_CODING_MODELS.items():
            console.print(f"[cyan]{provider.upper()}:[/cyan]")
            for model in info["models"]:
                console.print(f"  • {model['name']} ({model['id']})")

    def run_task(self, task):
        intent = self.detect_intent(task)
        icons = {"generate": "🔨", "run": "▶️", "debug": "🐛", "refactor": "♻️", "explain": "📖", "review": "👀"}
        icon = icons.get(intent, "🤖")
        
        console.print(f"\n{icon} [{intent.upper()}] {task[:50]}...")
        
        project_name = self._extract_project_name(task)
        agent = AutonomousAgent(project_name=project_name)
        result = agent.run(task, mode=self.mode)
        
        return result
    
    def _extract_project_name(self, task):
        """Extract project name from task"""
        words = task.lower().split()
        for word in ["called", "named", "name"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip(".,!?)
                    if name and len(name) > 1:
                        return name
        return None

    def handle_shell(self, command):
        executor = TaskExecutor()
        result = executor.run_command(command, timeout=60)

        if result["success"]:
            output = result.get("stdout", "") or result.get("stderr", "")
            return f"✓ Command executed successfully!\n\n{output[:500]}"
        else:
            return f"✗ Error: {result.get('stderr', 'Unknown error')}"

    def handle_read(self, filepath):
        executor = TaskExecutor()
        result = executor.read_file(filepath)

        if result["success"]:
            content = result["content"]
            if len(content) > 2000:
                return f"```\n{content[:2000]}\n... (truncated)\n```"
            return f"```\n{content}\n```"
        return f"✗ {result.get('message', 'Error')}"

    def handle_ls(self, directory="."):
        executor = TaskExecutor()
        result = executor.list_files(directory)

        if result["success"]:
            files = result.get("files", [])
            return f"Files in {directory}:\n" + "\n".join(
                f"  • {f}" for f in files[:20]
            )
        return f"✗ {result.get('message', 'Error')}"

    def run(self):
        self.print_banner()
        self.print_help()

        while True:
            try:
                user_input = input(f"\n{self.mode.upper()} >> ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=2)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if cmd == "/setkey" and arg:
                    self.api_key = arg
                    os.environ["OPENROUTER_API_KEY"] = arg
                    console.print("[green]✓[/green] API key set!")
                elif cmd == "/models":
                    self.print_models()
                elif cmd == "/set" and arg:
                    self.model = arg
                    os.environ["DEFAULT_MODEL"] = arg
                    console.print(f"[green]✓[/green] Model: {arg}")
                elif cmd == "/shell" and arg:
                    result = self.handle_shell(arg)
                    console.print(Panel(result, border_style="cyan"))
                elif cmd == "/read":
                    result = self.handle_read(arg or ".")
                    console.print(Panel(result, border_style="cyan"))
                elif cmd == "/ls":
                    result = self.handle_ls(arg or ".")
                    console.print(Panel(result, border_style="cyan"))
                elif cmd == "/mode":
                    console.print("Select: auto, plan, execute, review")
                    choice = input(">> ").strip().lower()
                    if choice in ["auto", "plan", "execute", "review"]:
                        self.mode = choice
                elif cmd in ["/help", "/h"]:
                    self.print_help()
                else:
                    console.print(f"[red]Unknown:[/red] {cmd}")
                continue

            result = self.run_task(user_input)
            console.print(Panel(result, border_style="green", width=80))
            console.print()


def main():
    app = BharatCode()
    app.run()


if __name__ == "__main__":
    main()
