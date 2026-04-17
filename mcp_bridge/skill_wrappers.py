import os
import subprocess
import json
import logging
from typing import Dict, Any, Optional, Tuple

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FORMAT = "[SkillWrapper] %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("SkillWrapper")

class SkillWrapper:
    """
    Handles the translation of logical skills to system commands.
    Implements the logic for triggering external software.
    """
    @staticmethod
    def run_command(command: str, shell: bool = True) -> Tuple[bool, str]:
        try:
            logger.info(f"Running command: {command}")
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
            logger.error(f"Command failed: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            logger.exception("Unexpected error running command")
            return False, str(e)

    @staticmethod
    def run_jsx(jsx_path: str, project_path: str) -> Tuple[bool, str]:
        """
        Executes an Adobe ExtendScript (.jsx) file on a project.
        """
        # This would normally use a bridge like 'estk' or a specific Adobe API
        # For this framework, we simulate the trigger call
        logger.info(f"TRIGGER: Executing Adobe Script {jsx_path} on {project_path}")
        return True, "Script executed successfully"

    @staticmethod
    def run_topaz_cli(model: str, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Triggers Topaz Video AI CLI.
        """
        # In a real scenario, this would use the actual CLI path
        cmd = f'topaz-cli --model {model} --input "{input_path}" --output "{output_path}"'
        return SkillWrapper.run_command(cmd)

    @staticmethod
    def run_ae_render(project_path: str, comp_name: str, output_path: str) -> Tuple[bool, str]:
        """
        Triggers the aerender command for After Effects.
        """
        cmd = f'aerender -project "{project_path}" -comp "{comp_name}" -output "{output_path}"'
        return SkillWrapper.run_command(cmd)
