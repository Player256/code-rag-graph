import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import WordCompleter
from langchain_core.messages import HumanMessage

from ..agents.orchestrator import Orchestrator


class CodeNavigatorCLI:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.session = PromptSession()
        self.commands = ["index", "ask", "help", "exit"]
        self.completer = WordCompleter(self.commands, ignore_case=True)

    def print_help(self):
        print("\nAvailable Commands:")
        print(
            "  index <repo_url>   - Clones and indexes a Git repository into the knowledge graph."
        )
        print("  ask <question>       - Asks a question about the indexed codebase.")
        print("  help                 - Displays this help message.")
        print("  exit                 - Exits the application.\n")

    async def handle_command(self, user_input: str):
        command, *args = user_input.strip().split(" ", 1)
        arg = args[0] if args else ""

        if command == "index":
            if not arg:
                print("Usage: index <repository_url>")
                return
            message = HumanMessage(content=f"Please index the repository at {arg}")
            response = self.orchestrator.invoke([message])
            print(response["messages"][-1])

        elif command == "ask":
            if not arg:
                print("Usage: ask <your_question>")
                return
            message = HumanMessage(content=arg)
            response = self.orchestrator.invoke([message])
            print(response["messages"][-1])

        elif command == "help":
            self.print_help()

        else:
            print(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

    async def run(self):
        print(
            "Welcome to the Code Navigator CLI. Type 'help' to see available commands."
        )
        while True:
            try:
                with patch_stdout():
                    user_input = await self.session.prompt_async(
                        "> ", completer=self.completer
                    )

                if user_input.lower() == "exit":
                    print("Exiting Code Navigator.")
                    break

                if user_input.strip():
                    await self.handle_command(user_input)

            except (KeyboardInterrupt, EOFError):
                print("\nExiting Code Navigator.")
                break


def start_cli():
    asyncio.run(CodeNavigatorCLI().run())
