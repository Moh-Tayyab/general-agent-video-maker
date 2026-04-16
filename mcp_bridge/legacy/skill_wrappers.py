import os
import subprocess
import json
from typing import Dict, Any, Optional
from .agents import BaseAgent, SkillResult

class SkillWrapper:
    """
    Handles the translation of logical skills to system commands.
    Implements the logic for triggering external software.
    """
    @staticmethod
    def run_command(command: str, shell: bool = True) -> tuple[bool, str]:
        try:
            # Use shell=True for Windows-specific command strings
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    @staticmethod
    def run_jsx(jsx_path: str, project_path: str) -> tuple[bool, str]:
        """
        Executes an Adobe ExtendScript (.jsx) file on a project.
        """
        # This would normally use a bridge like 'estk' or a specific Adobe API
        # For this framework, we's simulate the trigger call
        print(f"TRIGGER: Executing Adobe Script {jsx_path} on {project_path}")
        return True, "Script executed successfully"

    @staticmethod
    def run_topaz_cli(model: str, input_path: str, output_path: str) -> tuple[bool, str]:
        """
        Triggers Topaz Video AI CLI.
        """
        cmd = f'topaz-cli.exe --model {model} --input "{input_path}" --output "{output_path}"'
        return SkillWrapper.run_command(cmd)

    @staticmethod
    def run_ae_render(project_path: str, comp_name: str, output_path: str) -> tuple[bool, str]:
        """
        Triggers the aerender command for After Effects.
        """
        cmd = f'aerender -project "{project_path}" -comp "{comp_name}" -output "{output_path}"'
        return SkillWrapper.run_command(cmd)
