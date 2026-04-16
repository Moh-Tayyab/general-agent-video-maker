import subprocess
import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TTSPayload:
    text: str
    voice: str
    model: str
    stability: float
    similarity_boost: float
    style: float


@dataclass
class VideoPrompt:
    scene_id: int
    prompt: str
    duration: float
    motion_bucket: int
    model_id: str


class BridgeManager:
    """
    Translation layer: converts human-readable artifacts into machine-executable payloads.
    """
    def __init__(self):
        self.ffprobe_path = self._find_ffprobe()

    def _find_ffprobe(self) -> str:
        try:
            return subprocess.check_output(["which", "ffprobe"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffprobe"

    def prepare_tts_payload(self, script_content: str, voice_config: Dict[str, Any] = None) -> TTSPayload:
        """
        Extracts narration from Markdown script and formats for ElevenLabs.
        """
        text = script_content
        text = re.sub(r'#+.*', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\*.*?\*', '', text)
        clean_text = " ".join(text.split())

        config = voice_config or {}
        return TTSPayload(
            text=clean_text,
            voice=config.get("voice_id", "george"),
            model=config.get("model", "eleven_multilingual_v2"),
            stability=config.get("stability", 0.5),
            similarity_boost=config.get("similarity_boost", 0.75),
            style=config.get("style", 0.3)
        )

    def prepare_video_prompts(
        self,
        storyboard_content: str,
        model_config: Dict[str, Any] = None,
        style_guide: Dict[str, Any] = None
    ) -> List[VideoPrompt]:
        """
        Parses storyboard/script to create sequence of visual prompts.
        """
        scene_pattern = re.compile(r"Scene\s+(\d+)[:\s]+(.+)", re.IGNORECASE)
        matches = scene_pattern.findall(storyboard_content)
        prompts = []
        config = model_config or {}

        style_prefix = ""
        if style_guide:
            core = style_guide.get("core_descriptors", "")
            env = style_guide.get("environment_rules", "")
            cam = style_guide.get("camera_style", "")
            style_prefix = f"({core}, {env}, {cam})"

        global_style = config.get("global_style", "cinematic, 4k, highly detailed")

        for scene_id, description in matches:
            character_injection = ""
            profiles = style_guide.get("character_profiles", {}) if style_guide else {}
            for char_name, profile in profiles.items():
                if char_name.lower() in description.lower():
                    character_injection += f" {profile['description']}, {', '.join(profile['key_features'])}"

            final_prompt = f"{style_prefix} {description.strip()}, {character_injection}{global_style}"
            prompts.append(VideoPrompt(
                scene_id=int(scene_id),
                prompt=final_prompt.strip(),
                duration=config.get("default_duration", 5.0),
                motion_bucket=config.get("motion_bucket", 127),
                model_id=config.get("model_id", "google/veo-3-1")
            ))

        return prompts

    def _get_duration(self, file_path: str) -> float:
        """Executes ffprobe to get exact file duration in seconds."""
        try:
            cmd = [
                self.ffprobe_path, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ]
            output = subprocess.check_output(cmd).decode().strip()
            return float(output)
        except Exception:
            return 0.0
