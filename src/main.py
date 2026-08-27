## COPYRIGHT (C) 2026 CHAD GROOM
import asyncio
import json
from bootstrap import bootstrap_cli_style
from ollama import chat, Message
from logging import basicConfig, log, INFO
from rich import print
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.console import Console
from rich.table import Table
from clypi import (
    Command,
    arg
)

from aesthetic import play_blade_frames
from tools import Tools
from constants import (
    SYSTEM_PROMPT, 
    DEFAULT_MODEL, 
    PROGRAM_NAME, 
    DEFAULT_CONTAINER, 
    VERSION
)

def parse_options(options_json: str | None) -> dict:
    if not options_json or not str(options_json).strip():
        return {}

    try:
        parsed = json.loads(options_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for --options: {options_json!r}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("--options must be a JSON object, for example '{\"temperature\": 0.5}'")

    return parsed


# One-Stop-Shop for logging to the CLI with a consistent format
def cli_log(message: str):
    print(f"[bold green][AGENT][/bold green] {message}")

basicConfig(level="INFO", format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename="agent.log", filemode="a")

class PenTestAgent:
    model: str
    messages: list[dict]
    tools: Tools
    prompt: str
    show_thinking: bool
    max_iterations: int
    docker_container_name_or_id: str # Default Docker container name or id

    def __init__(self, 
                 model=DEFAULT_MODEL, 
                 prompt="", 
                 show_thinking=False,
                 max_iterations=100, 
                 docker_container_name_or_id=DEFAULT_CONTAINER,
                 options=None,
                ):
        self.model = model
        self.messages = []
        self.docker_container_name_or_id = docker_container_name_or_id
        self.tools = Tools(model=self.model, docker_container_name=self.docker_container_name_or_id)
        self.prompt = prompt
        self.show_thinking = show_thinking
        self.max_iterations = max_iterations
        self.docker_container_name = docker_container_name_or_id
        self.options = options or {}

    # Begin the agent's engagement loop
    async def begin(self, prompt=None):

        if prompt:
            self.prompt = prompt

        self.tools.is_complete = False

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": self.prompt,
            },
        ]

        await self.get_response()

        cli_log("Engagement completed. Exiting the agent.")

    async def get_response(self):

        for iteration in range(self.max_iterations):

            cli_log(
                f"Agent iteration "
                f"{iteration + 1}/{self.max_iterations}"
            )

            spinner_task = asyncio.create_task(
                self.spinner_task("Thinking...")
            )

            try:
                response = await asyncio.to_thread(
                    chat,
                    model=self.model,
                    messages=self.messages,
                    tools=self.tools.get_tools_list(),
                    think="high",
                    options=self.options,
                )

                log(INFO, json.dumps(response.message.model_dump_json()))

            finally:
                spinner_task.cancel()

                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass

            self.agent_message_log(response.message)

            # IMPORTANT: preserve the exact assistant message
            self.messages.append(response.message)

            if not response.message.tool_calls:
                if self.tools.is_complete:
                    return "Engagement completed."
                continue

            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                cli_log(
                    f"[yellow]Tool:[/yellow] "
                    f"{tool_name}"
                    f"{arguments}"
                )

                result = await self.execute_tool(
                    tool_name,
                    arguments
                )

                self.messages.append(
                    Message(
                        role="tool",
                        content=str(result),
                        tool_name=tool_name,
                    )
                )

            if self.tools.is_complete:
                return "Engagement completed."

        return "Maximum agent iterations reached."

    async def spinner_task(self, message: str):

        spinner = Spinner(
            "dots",
            text=message,
        )

        with Live(
            spinner,
            refresh_per_second=10,
        ):

            while True:
                await asyncio.sleep(0.1)

    def agent_message_log(self, agent_message: Message):
        thinking = getattr(agent_message, "thinking", None)
        content = getattr(agent_message, "content", None)

        if self.show_thinking and thinking:
            print(f"[bold green][🧠][/bold green] {thinking}")

        if content:
            print(f"[bold green][⚡][/bold green] {content}")

    async def execute_tool(self, tool_name, arguments):

        try:

            match tool_name:

                case "run_shell_command":
                    return await asyncio.to_thread(
                        self.tools.run_shell_command,
                        **arguments
                    )

                case "get_response_light":
                    return await asyncio.to_thread(
                        self.tools.get_response_light,
                        **arguments
                    )

                case "ask_user_for_input":
                    return await asyncio.to_thread(
                        self.tools.ask_user_for_input,
                        **arguments
                    )

                case "complete_engagement":
                    return await asyncio.to_thread(
                        self.tools.complete_engagement,
                        **arguments
                    )

                case _:
                    return (
                        f"Unknown tool: {tool_name}"
                    )

        except Exception as e:

            return (
                f"Tool execution failed: "
                f"{type(e).__name__}: {e}"
            )            

class SlowBladeCLI(Command):
    """CLI"""
    prompt: str = arg(
        default="",
        help="The prompt to use for the agent",
    )
    model: str = arg(
        default=DEFAULT_MODEL,
        help="The model to use for the agent",
    )
    show_thinking: bool = arg(
        default=False,
        help="Whether or not to show thinking on the CLI output"
    )
    max_iterations: int = arg(
        default=100,
        help="Maximum number of reasoning/tool loops the agent will run before stopping"
    )
    docker_container: str = arg(
        default=DEFAULT_CONTAINER,
        help="The docker container to run commands from; if empty we will run commands from the host system"
    )
    model_options: str = arg(
        default="{}",
        help="Optional JSON model options to pass to Ollama, e.g. '{\"temperature\": 0.5}'"
    )

    # The main execution method required by clypi.Command
    async def run(self) -> None:

        with open("data/logo.ascii", "r") as f:
            logo = f.read()

        play_blade_frames()

        print(logo)

        table = Table(title=f"{PROGRAM_NAME} v{VERSION}")

        table.add_column("Parameter", justify="right", style="purple", no_wrap=True)
        table.add_column("Value", style="purple")

        parsed_options = parse_options(self.model_options)

        table.add_row("Prompt", self.prompt)
        table.add_row("Model", self.model)
        table.add_row("Container", self.docker_container)
        table.add_row("Options", json.dumps(parsed_options, separators=(",", ":")))

        console = Console()
        console.print(table)

        if not "y" in input("\r\n Are you sure you want to continue? [y/n]:").strip().lower():
            print("Exiting...")
            exit(0)

        agent = PenTestAgent(
            model=self.model,
            show_thinking=self.show_thinking,
            max_iterations=self.max_iterations,
            docker_container_name_or_id=self.docker_container,
            options=parsed_options,
        )
        await agent.begin(prompt=self.prompt)

def main() -> None:
    bootstrap_cli_style()
    cli = SlowBladeCLI.parse()
    cli.start()


if __name__ == "__main__":
    main()