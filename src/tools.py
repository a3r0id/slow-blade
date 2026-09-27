from ollama import chat
import re
import subprocess
from datetime import datetime
from logging import getLogger
from pathlib import Path
from constants import COMMAND_PREFIX, DEFAULT_CONTAINER, DEFAULT_MODEL, REPORTS_DIR

logger = getLogger(__name__)

class Tools:

    def __init__(self, model=DEFAULT_MODEL, docker_container_name=DEFAULT_CONTAINER, reports_dir=REPORTS_DIR):
        self.model = model
        self.docker_container_name = docker_container_name
        self.reports_dir = Path(reports_dir)
        self.is_complete = False
        self.last_report_path = None

    # Lightweight response generator for quick, non-interactive use
    def get_response_light(self, prompt, system_prompt=""):
        print("get_response_light locals: ", locals())
        messages = [
            {'role': 'user', 'content': prompt},
            {'role': 'system', 'content': system_prompt},
        ]
        return chat(model=self.model, messages=messages, think='high')

    # Ask the user for input and return the input
    def ask_user_for_input(self, prompt):
        return input(prompt + " (Type your response and press Enter): ")      

    # Run a shell command and return the output
    def run_shell_command(self, command):
        # If a Docker container name is provided, prefix the command with 'docker exec <container_name>' otherwise run the command directly in the shell
        docker_command = COMMAND_PREFIX + f" {self.docker_container_name} " if self.docker_container_name else ""
        result = subprocess.run(docker_command + command, shell=True, capture_output=True, text=True)
        logger.info(f"Shell Command: {command}")
        logger.info(f"Command Return Code: {result.returncode}")
        logger.info(f"Command Standard Output: {result.stdout}")
        logger.info(f"Command Standard Error: {result.stderr}")
        return result

    def _resolve_report_path(self, report_filename=None):
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        if report_filename:
            name = Path(str(report_filename)).name
            if not name.lower().endswith(".md"):
                name = f"{name}.md"
            name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
            if name in {".md", "_.md"}:
                name = ""
        else:
            name = ""

        if not name:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            name = f"after-action-report-{stamp}.md"

        return self.reports_dir / name

    def complete_engagement(self, after_action_report, final_closing_message="Engagement completed.", report_filename=None):
        """Write a markdown after-action report and mark the engagement complete.

        Args:
            after_action_report: Full markdown after-action report covering overview,
                methodology, findings with evidence, and recommendations. Required.
            final_closing_message: Short closing message for the CLI.
            report_filename: Optional filename under the reports directory.
        """
        report = (after_action_report or "").strip()
        if not report:
            return (
                "complete_engagement failed: after_action_report is required "
                "(markdown). Engagement is NOT complete."
            )

        report_path = self._resolve_report_path(report_filename)
        report_path.write_text(report + "\n", encoding="utf-8")

        self.last_report_path = str(report_path)
        self.is_complete = True

        logger.info(f"After-action report written to {report_path}")
        return f"{final_closing_message}\nAfter-action report written to {report_path}"

    # Helper function to return the list of tools for the agent
    def get_tools_list(self):
        return [
            self.run_shell_command,
            self.complete_engagement,
            # self.get_response_light,
            self.ask_user_for_input,
        ]