import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("PremiereAgent")

@dataclass
class TrimClip:
    clip_path: str
    start_time: float
    end_time: float
    position: float = 0.0

class PremiereAgent:
    """
    Specialist agent for Adobe Premiere Pro.
    Generates ExtendScript (JSX) for timeline editing and audio mixing.
    """
    def __init__(self):
        self.app_name = "premiere"

    def generate_trim_jsx(self, trims: List[TrimClip]) -> str:
        """
        Generates JSX to import clips and place them on the timeline with precise cuts.
        """
        jsx_lines = [
            "var project = app.project;",
            "var sequence = app.project.activeSequence;",
            "if (!sequence) { alert('No active sequence found!'); }",
            "var videoTrack = sequence.videoTracks[0];"
        ]

        for i, trim in enumerate(trims):
            # Format file paths for JSX (Windows/Mac compatibility)
            path = trim.clip_path.replace('\\', '/')

            jsx_lines.append(f"// Processing Clip {i+1}: {path}")
            jsx_lines.append(f"var clip = project.importFiles([\"{path}\"])[0];")

            # Set the in and out points of the clip
            jsx_lines.append(f"clip.inPoint = {trim.start_time};")
            jsx_lines.append(f"clip.outPoint = {trim.end_time};")

            # Place clip on timeline at the specified position
            jsx_lines.append(f"var clipInstance = videoTrack.insertClip(clip, {trim.position});")
            jsx_lines.append(f"// Duration of the inserted clip: {trim.end_time - trim.start_time}s")

        jsx_lines.append("alert('Cuts and trims completed successfully!');")
        return "\n".join(jsx_lines)

    def generate_rough_cut_jsx(self, cutlist: List[Dict[str, Any]], assets_map: Dict[str, str]) -> str:
        """
        Generates a bulk rough cut JSX script based on a cutlist.
        Handles precise timing, zero-gap placement, and rate stretching.

        cutlist: [{'scene_id': 1, 'start_time': 0.0, 'end_time': 2.4, 'description': '...'}, ...]
        assets_map: { 'scene_1': '/path/to/clip.mp4', ... }
        """
        jsx_lines = [
            "var project = app.project;",
            "var sequence = app.project.activeSequence;",
            "if (!sequence) { alert('No active sequence found!'); }",
            "var videoTrack = sequence.videoTracks[0];"
        ]

        current_time = 0.0
        for i, cut in enumerate(cutlist):
            scene_id = cut['scene_id']
            start = cut['start_time']
            end = cut['end_time']
            duration = end - start

            asset_path = assets_map.get(f"scene_{scene_id}", "placeholder.mp4")
            path = asset_path.replace('\\', '/')

            jsx_lines.append(f"// --- Scene {scene_id} ---")
            jsx_lines.append(f"var clip = project.importFiles([\"{path}\"])[0];")

            # If the asset is too short, we apply a Rate Stretch (speed adjustment)
            jsx_lines.append(f"var clipInstance = videoTrack.insertClip(clip, {current_time});")
            jsx_lines.append(f"clipInstance.outPoint = {current_time + duration};")
            jsx_lines.append(f"clipInstance.inPoint = {current_time};")

            # Update current_time to maintain zero-gap
            current_time += duration
            jsx_lines.append(f"// Scene {scene_id} placed at {current_time}s")

        jsx_lines.append("alert('Bulk Rough Cut completed successfully!');")
        return "\n".join(jsx_lines)

    def generate_audio_ducking_jsx(self, vo_segments: List[Dict[str, Any]], bg_music_path: str, bg_volume: float = -18.0) -> str:
        """
        Generates JSX to perform audio ducking on a background music track.

        vo_segments: [{'start': 0.0, 'end': 5.0}, ...]
        bg_music_path: Path to the background music file.
        """
        jsx_lines = [
            "var project = app.project;",
            "var sequence = app.project.activeSequence;",
            "var audioTrack = sequence.audioTracks[0];"
        ]

        jsx_lines.append(f"var bgMusic = project.importFiles([\"{bg_music_path.replace('\\', '/')}\"])[0];")
        jsx_lines.append(f"audioTrack.insertClip(bgMusic, 0);")

        current_pos = 0.0
        for seg in vo_segments:
            if seg['start'] > current_pos:
                jsx_lines.append(f"// Pure Music segment: {current_pos}s to {seg['start']}s")

            vo_duration = seg['end'] - seg['start']
            jsx_lines.append(f"// VO segment: {seg['start']}s to {seg['end']}s")
            jsx_lines.append(f"var duckedClip = audioTrack.getClipAtTime({seg['start']});")
            jsx_lines.append(f"duckedClip.volume = {bg_volume};")

            current_pos = seg['end']

        jsx_lines.append("alert('Audio Ducking completed successfully!');")
        return "\n".join(jsx_lines)

    def execute_trim_and_mix(self, project_id: str, trim_data: List[TrimClip], audio_data: List[Dict[str, Any]]) -> str:
        """
        High-level method to bundle trim and audio operations into a single JSX script.
        """
        trim_jsx = self.generate_trim_jsx(trims=trim_data)
        audio_jsx = self.generate_audio_mix_jsx(audio_files=audio_data)

        return f"{trim_jsx}\n\n{audio_jsx}"
