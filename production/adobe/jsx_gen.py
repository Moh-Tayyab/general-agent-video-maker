import os
import logging
from typing import Optional

logger = logging.getLogger("AdobeBridge")

class AdobeBridge:
    """
    The communication bridge between the SSD Orchestrator and Adobe Applications.
    Uses a 'Drop-Zone' pattern where JSX scripts are written to monitored folders.
    """
    def __init__(self, bridge_folder: Optional[str] = None):
        self.bridge_folder = bridge_folder or os.path.expanduser("~/AdobeBridge")
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Creates the necessary subfolders for Adobe apps."""
        apps = ["premiere", "aftereffects"]
        for app in apps:
            path = os.path.join(self.bridge_folder, app)
            os.makedirs(path, exist_ok=True)
            logger.info(f"Ensured bridge directory exists: {path}")

    def _wrap_jsx(self, target_app: str, code: str) -> str:
        """Wraps raw JSX with the correct #target directive."""
        app = target_app.lower()
        if "premiere" in app:
            prefix = "#target premiere"
        elif "aftereffects" in app:
            prefix = "#target aftereffects"
        else:
            prefix = ""
        return f"{prefix}\n{code}"

    def execute_jsx(self, target_app: str, jsx_code: str, script_name: str = "cmd.jsx") -> str:
        """
        Writes a JSX script to the drop-zone for the specified Adobe app.
        """
        app_key = "premiere" if "premiere" in target_app.lower() else "aftereffects"
        wrapped_code = self._wrap_jsx(app_key, jsx_code)
        file_path = os.path.join(self.bridge_folder, app_key, script_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(wrapped_code)
        logger.info(f"Successfully wrote JSX command to {file_path}")
        return file_path

    def clear_scripts(self, target_app: Optional[str] = None) -> None:
        """Clears the drop-zone for a specific app or all apps."""
        apps = [target_app.lower()] if target_app else ["premiere", "aftereffects"]
        for app in apps:
            folder = os.path.join(self.bridge_folder, app)
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.endswith(".jsx"):
                        os.remove(os.path.join(folder, file))
                logger.info(f"Cleared JSX scripts for {app}")
