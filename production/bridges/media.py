"""
Media processing bridge — crop, trim, smart pan, audio analysis, music mix.
All operations via ffmpeg. No Adobe required.
"""
import subprocess
import os
import json
import re
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple

logger = logging.getLogger("MediaBridge")


@dataclass
class CropResult:
    success: bool
    output_path: str
    duration: float
    message: str


@dataclass
class MusicMixResult:
    success: bool
    output_path: str
    message: str


class MediaBridge:
    """
    Handles crop, trim, pan, and audio manipulation via ffmpeg.
    Used for the Maven-Edit style: 9:16 vertical, cinematic grade, BG music mix.
    """

    def __init__(self, workspace: str = "/home/muhammad_tayyab/bootlogix/production/output"):
        self.workspace = workspace
        self.ffprobe = self._find_ffprobe()
        self.ffmpeg = self._find_ffmpeg()
        os.makedirs(self.workspace, exist_ok=True)

    def _find_ffprobe(self) -> str:
        try:
            return subprocess.check_output(["which", "ffprobe"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffprobe"

    def _find_ffmpeg(self) -> str:
        try:
            return subprocess.check_output(["which", "ffmpeg"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffmpeg"

    def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        cmd = [self.ffprobe, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        try:
            return float(subprocess.check_output(cmd).decode().strip())
        except Exception:
            return 0.0

    def get_resolution(self, video_path: str) -> Tuple[int, int]:
        """Get (width, height) of video."""
        cmd = [self.ffprobe, "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height",
               "-of", "csv=p=0", video_path]
        try:
            w, h = map(int, subprocess.check_output(cmd).decode().strip().split(','))
            return w, h
        except Exception:
            return 0, 0

    def analyze_audio(self, video_path: str) -> dict:
        """
        Analyze audio track to find speech segments.
        Returns dict with speech windows, peak moments, silence gaps.
        """
        logger.info(f"Analyzing audio in: {video_path}")

        # Use ffmpeg volumedetect to find loud segments
        cmd = [
            self.ffmpeg, "-i", video_path, "-vn", "-af",
            "volumedetect=file=/tmp/volumedetect.txt", "-f", "null", "-"
        ]
        subprocess.run(cmd, capture_output=True, check=False)

        # Also get audio waveform data
        cmd2 = [
            self.ffmpeg, "-i", video_path, "-vn", "-ss", "0", "-t", str(self.get_duration(video_path)),
            "-af", "astat=metadata=1:reset=1,ametadata=print:key=lavfi.astat.peak_level",
            "-f", "null", "-"
        ]
        subprocess.run(cmd2, capture_output=True, check=False)

        # Simple silence detection approach
        cmd3 = [
            self.ffmpeg, "-i", video_path, "-af",
            "silencedetect=n=-30dB:d=0.3", "-f", "null", "-"
        ]
        result = subprocess.run(cmd3, capture_output=True, text=True, check=False)
        silence_output = result.stderr if result.stderr else result.stdout

        # Parse silence regions
        silence_starts = re.findall(r'silence_start: ([\d.]+)', silence_output)
        silence_ends = re.findall(r'silence_end: ([\d.]+)', silence_output)

        speech_windows = []
        if silence_starts:
            prev_end = 0.0
            for start, end in zip(silence_starts, silence_ends):
                start_f, end_f = float(start), float(end)
                if start_f - prev_end > 0.5:
                    speech_windows.append({"start": prev_end, "end": start_f})
                prev_end = end_f

        total_dur = self.get_duration(video_path)
        if speech_windows:
            last_window = speech_windows[-1]
            if total_dur - last_window["end"] > 0.5:
                speech_windows.append({"start": last_window["end"], "end": total_dur})
        else:
            speech_windows.append({"start": 0.0, "end": total_dur})

        return {
            "duration": total_dur,
            "speech_windows": speech_windows,
            "has_speech": len(speech_windows) > 0
        }

    def crop_to_vertical(
        self,
        video_path: str,
        project_id: str,
        target_duration: Optional[float] = None,
        crop_mode: str = "center-pan",
        source_width: int = 0,
        source_height: int = 0
    ) -> CropResult:
        """
        Crop 16:9 landscape video to 9:16 vertical with smart pan.
        crop_mode: 'center-pan' (default), 'face-detect', 'left', 'right'
        """
        if not os.path.exists(video_path):
            return CropResult(False, "", 0.0, f"Source not found: {video_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, "step1_cropped.mp4")

        w, h = self.get_resolution(video_path)
        if w == 0:
            w, h = source_width, source_height
        if w == 0:
            return CropResult(False, "", 0.0, "Could not determine video resolution")

        # Target: 1080x1920 (9:16)
        target_w, target_h = 1080, 1920
        target_dar = target_w / target_h  # 0.5625

        source_dar = w / h
        crop_w, crop_h = w, h

        if source_dar > target_dar:
            # Source is wider than target — crop width
            crop_w = int(h * target_dar)
            crop_h = h
        else:
            # Source is taller — crop height
            crop_w = w
            crop_h = int(w / target_dar)

        # Calculate crop position based on mode
        if crop_mode == "center-pan":
            x_offset = (w - crop_w) // 2
            y_offset = 0
        elif crop_mode == "left":
            x_offset = 0
            y_offset = 0
        elif crop_mode == "right":
            x_offset = w - crop_w
            y_offset = 0
        elif crop_mode == "face-detect":
            # Fallback to center if no face detection
            x_offset = (w - crop_w) // 2
            y_offset = 0
        else:
            x_offset = (w - crop_w) // 2
            y_offset = 0

        cmd = [
            self.ffmpeg, "-y", "-i", video_path,
            "-vf", f"crop={crop_w}:{crop_h}:{x_offset}:{y_offset},scale={target_w}:{target_h}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-r", "30",
            "-an" if target_duration else "",
            output_path
        ]

        # Remove the -an if no target_duration
        cmd = [c for c in cmd if c]

        if target_duration:
            # Select the best speech window around target_duration
            analysis = self.analyze_audio(video_path)
            speech_windows = analysis.get("speech_windows", [])
            start_time = 0.0

            if speech_windows:
                # Find window closest to target_duration from start
                for window in speech_windows:
                    if window["end"] - window["start"] >= target_duration * 0.8:
                        start_time = window["start"]
                        break

            cmd.insert(4, "-ss")
            cmd.insert(5, str(start_time))
            if start_time + target_duration < analysis["duration"]:
                cmd.insert(6, "-t")
                cmd.insert(7, str(target_duration))

        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
            duration = self.get_duration(output_path)
            return CropResult(True, output_path, duration, f"Cropped to 9:16, {duration:.1f}s")
        except subprocess.CalledProcessError as e:
            return CropResult(False, "", 0.0, f"ffmpeg crop failed: {e.stderr}")

    def apply_color_grade(
        self,
        video_path: str,
        project_id: str,
        lut_file: Optional[str] = None,
        contrast: float = 8.0,
        saturation: float = -5.0,
        gamma: float = 0.9
    ) -> CropResult:
        """
        Apply Maven-Edit cinematic color grade.
        Either use a .cube LUT file OR use ffmpeg colorlevels.
        """
        if not os.path.exists(video_path):
            return CropResult(False, "", 0.0, "Source not found")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, "step2_graded.mp4")

        if lut_file and os.path.exists(lut_file):
            # Apply .cube LUT via lut3d filter
            cmd = [
                self.ffmpeg, "-y", "-i", video_path,
                "-vf", f"lut3d={lut_file}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "copy",
                output_path
            ]
        else:
            # Apply programmatic color grade (Maven-Edit style)
            # contrast +8, saturation -5, gamma 0.9
            cmd = [
                self.ffmpeg, "-y", "-i", video_path,
                "-vf", f"colorlevels=contr={contrast/100}:sat={saturation/100}:gamma={gamma},eq=contrast={1+contrast/100}:saturation={1+saturation/100}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "copy",
                output_path
            ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            duration = self.get_duration(output_path)
            return CropResult(True, output_path, duration, "Color graded")
        except subprocess.CalledProcessError as e:
            return CropResult(False, "", 0.0, f"Color grade failed: {e.stderr}")

    def mix_bg_music(
        self,
        video_path: str,
        project_id: str,
        bg_music_path: str,
        duck_amount: float = -18.0,
        music_volume: float = 0.3
    ) -> MusicMixResult:
        """
        Mix BG music with speech ducking.
        - bg_music: looped background track
        - duck_amount: dB reduction during speech (-18dB = Maven-Edit default)
        - music_volume: volume of music track (0.0-1.0)
        """
        if not os.path.exists(video_path):
            return MusicMixResult(False, "", "Source not found")
        if not os.path.exists(bg_music_path):
            return MusicMixResult(False, "", f"BG music not found: {bg_music_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, "step3_with_music.mp4")

        video_duration = self.get_duration(video_path)

        # Build complex filter for ducking
        # 1. Extract speech from video audio
        # 2. Detect speech and create ducking mask
        # 3. Apply ducking to music
        # 4. Mix music + original audio

        filter_complex = f"""
        [1:a]aloop=loop=-1:size=2e9,atrim=0:{video_duration},afade=t=in:st=0:d=0.5,afade=t=out:st={video_duration-0.5}:d=0.5,volume={music_volume}[music];
        [0:a]asplit=2[speech][ref];
        [speech]silencedetect=n=-30dB:d=0.2[sp];
        [sp]volume=0[trigger];
        [music][trigger]sidechaincompr=threshold={duck_amount/3}dB:ratio=4:attack=5:release=50[ducked_music];
        [ref][ducked_music]amix=inputs=2:weights=1 {music_volume}:duration=longest[aout]
        """

        cmd = [
            self.ffmpeg, "-y", "-i", video_path, "-i", bg_music_path,
            "-filter_complex", filter_complex.replace("\n", "").replace("  ", ""),
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
            return MusicMixResult(True, output_path, f"BG music mixed (duck: {duck_amount}dB)")
        except subprocess.CalledProcessError as e:
            # Fallback: simple mix without ducking
            return self._simple_mix(video_path, project_id, bg_music_path, music_volume)

    def _simple_mix(self, video_path: str, project_id: str, bg_music_path: str, music_volume: float) -> MusicMixResult:
        """Fallback simple mix without ducking."""
        project_dir = os.path.join(self.workspace, project_id)
        output_path = os.path.join(project_dir, "step3_with_music.mp4")
        video_duration = self.get_duration(video_path)

        cmd = [
            self.ffmpeg, "-y", "-i", video_path, "-i", bg_music_path,
            "-filter_complex",
            f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{video_duration},afade=t=in:st=0:d=1,afade=t=out:st={video_duration-1}:d=1,volume={music_volume}[music];[0:a][music]amix=inputs=2:weights=1 {music_volume}:duration=longest[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return MusicMixResult(True, output_path, "BG music mixed (simple)")
        except subprocess.CalledProcessError as e:
            return MusicMixResult(False, "", f"Simple mix failed: {e.stderr}")

    def extract_audio(self, video_path: str, project_id: str) -> str:
        """Extract audio track as AAC for STT processing."""
        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        output_path = os.path.join(project_dir, "audio_extract.aac")

        cmd = [
            self.ffmpeg, "-y", "-i", video_path,
            "-vn", "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
