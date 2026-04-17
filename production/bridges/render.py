"""
Render bridge — final encode, caption burn-in, format conversion.
Uses ffmpeg with libx264 + libass for Maven-Edit output.
"""
import subprocess
import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("RenderBridge")


@dataclass
class RenderResult:
    success: bool
    output_path: str
    file_size_mb: float
    message: str


class RenderBridge:
    """
    Final video rendering: ASS caption burn-in, H.264 encode, format mux.
    Used as the last step before output.
    """

    def __init__(self, workspace: str = "/home/muhammad_tayyab/bootlogix/production/output"):
        self.workspace = workspace
        self.ffmpeg = self._find_ffmpeg()
        self.ffprobe = self._find_ffprobe()

    def _find_ffmpeg(self) -> str:
        try:
            return subprocess.check_output(["which", "ffmpeg"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffmpeg"

    def _find_ffprobe(self) -> str:
        try:
            return subprocess.check_output(["which", "ffprobe"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffprobe"

    def get_duration(self, video_path: str) -> float:
        cmd = [self.ffprobe, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        try:
            return float(subprocess.check_output(cmd).decode().strip())
        except Exception:
            return 0.0

    def get_file_size_mb(self, path: str) -> float:
        return os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0.0

    def burn_captions(
        self,
        video_path: str,
        ass_path: str,
        project_id: str,
        output_name: str = "final_video.mp4",
        quality: str = "high"
    ) -> RenderResult:
        """
        Burn ASS subtitles into video using libass.
        quality: 'high' (crf 17) | 'medium' (crf 20) | 'fast' (crf 23)
        """
        if not os.path.exists(video_path):
            return RenderResult(False, "", 0.0, f"Video not found: {video_path}")
        if not os.path.exists(ass_path):
            return RenderResult(False, "", 0.0, f"ASS not found: {ass_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, output_name)

        crf_map = {"high": "17", "medium": "20", "fast": "23"}
        crf = crf_map.get(quality, "18")

        cmd = [
            self.ffmpeg, "-y",
            "-i", video_path,
            "-vf", f"ass={ass_path}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", crf,
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", "30",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
            size = self.get_file_size_mb(output_path)
            duration = self.get_duration(output_path)
            return RenderResult(True, output_path, size, f"Rendered: {size:.1f}MB, {duration:.1f}s")
        except subprocess.CalledProcessError as e:
            logger.error(f"Burn captions failed: {e.stderr}")
            return RenderResult(False, "", 0.0, f"ffmpeg burn failed: {e.stderr}")

    def start_background_burn(
        self,
        video_path: str,
        ass_path: str,
        project_id: str,
        output_name: str = "final_video.mp4",
        quality: str = "high"
    ) -> str:
        """
        Starts a background ffmpeg process and returns the PID file path.
        """
        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, output_name)
        pid_file = os.path.join(project_dir, f"{output_name}.pid")
        log_file = os.path.join(project_dir, f"{output_name}.log")

        crf_map = {"high": "17", "medium": "20", "fast": "23"}
        crf = crf_map.get(quality, "18")

        # Full command to run in background
        cmd = f"nohup {self.ffmpeg} -y -i {video_path} -vf ass={ass_path} -c:v libx264 -preset fast -crf {crf} -c:a aac -b:a 192k -r 30 {output_path} > {log_file} 2>&1 & echo $! > {pid_file}"
        
        subprocess.run(cmd, shell=True, check=True)
        return pid_file

    def encode_from_frames(
        self,
        frames_dir: str,
        project_id: str,
        output_name: str = "final_video.mp4",
        fps: int = 30
    ) -> RenderResult:
        """
        Encode a directory of frames into a video.
        Useful when AE/Remotion outputs frames instead of video.
        """
        if not os.path.isdir(frames_dir):
            return RenderResult(False, "", 0.0, f"Frames dir not found: {frames_dir}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, output_name)

        cmd = [
            self.ffmpeg, "-y",
            "-framerate", str(fps),
            "-i", f"{frames_dir}/frame_%04d.png",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(fps),
            "-vf", "scale=1080:1920",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            size = self.get_file_size_mb(output_path)
            duration = self.get_duration(output_path)
            return RenderResult(True, output_path, size, f"Encoded: {size:.1f}MB")
        except subprocess.CalledProcessError as e:
            return RenderResult(False, "", 0.0, f"Encode failed: {e.stderr}")

    def add_linear_wipe_transition(
        self,
        video1_path: str,
        video2_path: str,
        project_id: str,
        transition_duration: float = 1.0,
        direction: str = "left"
    ) -> RenderResult:
        """
        Add a linear wipe transition between two clips.
        Uses ffmpeg xfade filter.
        direction: 'left' | 'right' | 'top' | 'bottom'
        """
        if not os.path.exists(video1_path):
            return RenderResult(False, "", 0.0, f"Video1 not found")
        if not os.path.exists(video2_path):
            return RenderResult(False, "", 0.0, f"Video2 not found")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, "transitioned.mp4")

        dur1 = self.get_duration(video1_path)
        dur2 = self.get_duration(video2_path)

        # xfade filter: transition at the overlap point
        offset1 = dur1 - transition_duration

        wipemap = {"left": "h", "right": "h", "top": "v", "bottom": "v"}
        wipe_dir = "wipe" if direction in ("left", "right") else "wiper"

        cmd = [
            self.ffmpeg, "-y",
            "-i", video1_path,
            "-i", video2_path,
            "-filter_complex",
            f"[0:v][1:v]xfade={wipe_dir}=transition={direction}:duration={transition_duration}:offset={offset1}[outv]",
            "-map", "[outv]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            size = self.get_file_size_mb(output_path)
            duration = self.get_duration(output_path)
            return RenderResult(True, output_path, size, f"Wipe transition: {duration:.1f}s")
        except subprocess.CalledProcessError as e:
            return RenderResult(False, "", 0.0, f"Wipe transition failed: {e.stderr}")

    def convert_format(
        self,
        input_path: str,
        project_id: str,
        output_ext: str,
        codec: str = "libx264",
        bitrate: Optional[str] = None
    ) -> RenderResult:
        """Convert video to different format."""
        if not os.path.exists(input_path):
            return RenderResult(False, "", 0.0, "Input not found")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, f"converted.{output_ext}")

        cmd = [
            self.ffmpeg, "-y", "-i", input_path,
            "-c:v", codec, "-preset", "fast", "-crf", "18"
        ]
        if bitrate:
            cmd.extend(["-b:v", bitrate])
        cmd.append(output_path)

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            size = self.get_file_size_mb(output_path)
            return RenderResult(True, output_path, size, f"Converted to {output_ext}")
        except subprocess.CalledProcessError as e:
            return RenderResult(False, "", 0.0, f"Convert failed: {e.stderr}")
