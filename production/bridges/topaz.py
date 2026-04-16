"""
Topaz bridge — video upscaling and enhancement via inference.sh CLI.
Wraps falai/topaz-video-upscaler (inference.sh native, not topaz-cli.exe).
"""
import subprocess
import os
import json
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("TopazBridge")


@dataclass
class UpscaleResult:
    success: bool
    output_path: str
    resolution: str
    message: str


class TopazBridge:
    """
    Video enhancement via inference.sh's Topaz Video Upscaler app.
    This uses falai/topaz-video-upscaler via infsh, NOT topaz-cli.exe.
    """

    def __init__(self, workspace: str = "/home/muhammad_tayyab/bootlogix/production/output"):
        self.workspace = workspace

    def upscale(
        self,
        video_path: str,
        project_id: str,
        scale: int = 2,
        model: str = "Proteus",
        output_name: str = "upscaled.mp4"
    ) -> UpscaleResult:
        """
        Upscale video using Topaz Video Upscaler via infsh.
        scale: 2 (2x = 1080→2160 or 4K) or 4 (4x = 1080→4K)
        model: 'Proteus' (default), 'Iris', 'Artemis'
        """
        if not os.path.exists(video_path):
            return UpscaleResult(False, "", "", f"Video not found: {video_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, output_name)

        # Build infsh command for Topaz upscaler
        input_payload = json.dumps({
            "input": video_path,
            "model": model,
            "scale": scale
        })

        cmd = [
            "infsh", "app", "run",
            "falai/topaz-video-upscaler",
            "--input", input_payload,
            "--output", output_path
        ]

        logger.info(f"Running Topaz upscale: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            logger.info(f"Topaz stdout: {result.stdout}")
            logger.info(f"Topaz stderr: {result.stderr}")

            if result.returncode == 0 and os.path.exists(output_path):
                resolution = f"{1080*scale}x{1920*scale}"
                return UpscaleResult(True, output_path, resolution, f"Upscaled to {resolution}")
            else:
                return UpscaleResult(False, "", "", f"Upscale failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return UpscaleResult(False, "", "", "Upscale timed out (>10min)")
        except Exception as e:
            return UpscaleResult(False, "", "", f"Upscale error: {e}")

    def enhance_denoise(
        self,
        video_path: str,
        project_id: str,
        model: str = "Iris",
        output_name: str = "denoised.mp4"
    ) -> UpscaleResult:
        """
        Denoise and enhance video quality using Topaz via infsh.
        """
        if not os.path.exists(video_path):
            return UpscaleResult(False, "", "", f"Video not found: {video_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, output_name)

        input_payload = json.dumps({
            "input": video_path,
            "model": model,
            "denoise_level": 50
        })

        cmd = [
            "infsh", "app", "run",
            "falai/topaz-video-upscaler",
            "--input", input_payload,
            "--output", output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0 and os.path.exists(output_path):
                return UpscaleResult(True, output_path, "enhanced", "Denoise complete")
            return UpscaleResult(False, "", "", f"Denoise failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return UpscaleResult(False, "", "", "Denoise timed out")
        except Exception as e:
            return UpscaleResult(False, "", "", f"Denoise error: {e}")
