from ollama import chat
import subprocess
from logging import getLogger
from constants import COMMAND_PREFIX, DEFAULT_CONTAINER, DEFAULT_MODEL

logger = getLogger(__name__)

class Tools:

    def __init__(self, model=DEFAULT_MODEL, docker_container_name=DEFAULT_CONTAINER):
        self.model = model
        self.docker_container_name = docker_container_name
        self.is_complete = False

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

    # Mark the engagement as complete
    def complete_engagement(self, final_closing_message="Engagement completed."):
        self.is_complete = True
        return final_closing_message

    # Helper function to return the list of tools for the agent
    def get_tools_list(self):
        return [
            self.run_shell_command,
            self.complete_engagement,
            # self.get_response_light,
            self.ask_user_for_input,
        ]