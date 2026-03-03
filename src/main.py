import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from rich.console import Console
from rich.panel import Panel
from brain.models import FREE_CODING_MODELS, get_default_model
from brain.router import route_chat

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
    "4": ("Auto", "Full agentic workflow"),
}

INTENT_KEYWORDS = {
    "generate": ["create", "write", "make", "generate", "build", "add", "new"],
    "run": ["run", "execute", "start", "test"],
    "debug": ["debug", "fix", "error", "bug", "issue"],
    "refactor": ["refactor", "improve", "optimize", "clean"],
    "explain": ["explain", "what", "how", "why", "describe"],
    "review": ["review", "check", "verify", "audit"],
}


class BharatCodeTUI:
    def __init__(self):
        self.model = os.getenv("DEFAULT_MODEL", get_default_model())
        self.mode = "auto"
        self.conversation = []
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

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
                    "[yellow]⚠️  No API Key configured![/yellow]\n\n"
                    "Get free key: [cyan]https://openrouter.ai/settings/keys[/cyan]\n"
                    "Then run: [cyan]/setkey YOUR_API_KEY[/cyan]\n\n"
                    "[dim]Or ask the developer for the shared key[/dim]",
                    title="🔑 Setup Required",
                    border_style="yellow",
                    width=60,
                )
            )
        else:
            console.print(
                Panel(
                    f"[green]✓[/green] Using: [bold]{self.model}[/bold]",
                    border_style="green",
                    width=60,
                )
            )

        console.print(
            f"\n[dim]Mode:[/dim] {self.mode.upper()}  [dim]Intent:[/dim] Auto\n"
        )

    def print_help(self):
        console.print("""
[bold]Commands:[/bold]
  /setkey <key>   - Set OpenRouter API key
  /models         - List available models  
  /set <model>    - Switch model (e.g., /set minimax/MiniMax-M2.1)
  /mode           - Choose workflow mode
  /clear          - Clear chat
  /help           - Show this help
  exit            - Exit

[bold]Quick:[/bold]
  Just type your coding question!
  I'll auto-detect if you want to generate, debug, or explain code.
""")

    def print_models(self):
        console.print("\n[bold]Available Free Models (via OpenRouter):[/bold]\n")

        for provider, info in FREE_CODING_MODELS.items():
            console.print(f"[cyan]{provider.upper()}:[/cyan]")
            for model in info["models"]:
                icon = "💻" if model.get("type") == "coding" else "🧠"
                console.print(f"  {icon} {model['name']} ({model['id']})")
            console.print()

    def set_api_key(self, key):
        self.api_key = key.strip()
        os.environ["OPENROUTER_API_KEY"] = key.strip()
        console.print(f"[green]✓[/green] API key set! ({len(key)} chars)")

    def set_model(self, model_id):
        self.model = model_id
        os.environ["DEFAULT_MODEL"] = model_id
        console.print(f"[green]✓[/green] Model set to: [bold]{model_id}[/bold]")

    def process_message(self, user_input):
        intent = self.detect_intent(user_input)

        icons = {
            "generate": "🔨",
            "run": "▶️",
            "debug": "🐛",
            "refactor": "♻️",
            "explain": "📖",
            "review": "👀",
        }
        icon = icons.get(intent, "🤖")

        if self.mode == "plan":
            console.print(f"\n{icon} Planning...")
        elif self.mode == "execute":
            console.print(f"\n{icon} Executing...")
        elif self.mode == "review":
            console.print(f"\n{icon} Reviewing...")
        else:
            console.print(f"\n{icon} {intent.title()}...")

        result = route_chat(
            [
                {
                    "role": "system",
                    "content": "You are BharatCode, an expert coding assistant. Provide clear, concise answers. Include code examples when helpful.",
                },
                {"role": "user", "content": user_input},
            ],
            model=self.model,
        )

        return result

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
                    self.set_api_key(arg)
                elif cmd == "/setkey":
                    console.print("Usage: /setkey YOUR_API_KEY")
                elif cmd == "/models":
                    self.print_models()
                elif cmd == "/set" and arg:
                    self.set_model(arg)
                elif cmd == "/mode":
                    console.print("\n[bold]Select Mode:[/bold]")
                    for k, (n, d) in MODES.items():
                        console.print(f"  {k}. {n} - {d}")
                    choice = input(">> ") or "4"
                    if choice in MODES:
                        self.mode = MODES[choice][0].lower()
                elif cmd == "/clear":
                    self.conversation = []
                    self.print_banner()
                elif cmd in ["/help", "/h"]:
                    self.print_help()
                else:
                    console.print(f"[red]Unknown:[/red] {cmd}")
                continue

            result = self.process_message(user_input)

            if result and "Error" in result:
                console.print(Panel(result, border_style="red", width=80))
                if "API key" in result:
                    console.print(
                        "\n[yellow]Get free key:[/yellow] https://openrouter.ai/settings/keys"
                    )
            else:
                console.print(Panel(result, border_style="green", width=80))


def main():
    tui = BharatCodeTUI()
    tui.run()


if __name__ == "__main__":
    main()
