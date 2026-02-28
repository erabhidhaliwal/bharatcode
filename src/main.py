import os
from dotenv import load_dotenv

# Load environment variables from src/.env BEFORE other imports
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from orchestrator import Orchestrator


def main():
    orch = Orchestrator()

    print("🚀 BharatCode Orchestrator Ready\n")

    while True:
        user = input(">> ")

        if user == "exit":
            break

        result = orch.run(user)
        print(result)


if __name__ == "__main__":
    main()