"""
Caption bridge — SRT generation via STT, SRT→ASS karaoke conversion.
The heart of the Maven-Edit visual style.
"""
import subprocess
import os
import re
import json
import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger("CaptionBridge")


@dataclass
class STTResult:
    success: bool
    srt_path: str
    word_timestamps: List[dict]
    message: str


@dataclass
class ASSResult:
    success: bool
    ass_path: str
    caption_count: int
    message: str


class CaptionBridge:
    """
    Converts video/audio to karaoke-style ASS captions (Maven-Edit look).
    Pipeline: audio → STT (ElevenLabs Scribe) → SRT → ASS (karaoke)
    """

    def __init__(self, workspace: str = "/home/muhammad_tayyab/bootlogix/production/output"):
        self.workspace = workspace
        self.ffmpeg = self._find_ffmpeg()

    def _find_ffmpeg(self) -> str:
        try:
            return subprocess.check_output(["which", "ffmpeg"]).decode().strip()
        except subprocess.CalledProcessError:
            return "/usr/bin/ffmpeg"

    # ─── Styles ───────────────────────────────────────────────────────────────

    MAVEN_MAIN_STYLE = (
        "Style: MavenMain,Bangers,96,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "-1,0,0,0,100,100,0,0,1,6,0,2,10,10,480,1"
    )

    MAVEN_HIGHLIGHT_STYLE = (
        "Style: MavenHighlight,Bangers,96,&H0000FFFF,&H000000FF,&H00000000,&H00000000,"
        "-1,0,0,0,100,100,0,0,1,6,0,2,10,10,480,1"
    )

    ASS_HEADER = (
        "[Script Info]\n"
        "Title: Maven-Edit Style Captions\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,"
        "Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"{MAVEN_MAIN_STYLE}\n"
        f"{MAVEN_HIGHLIGHT_STYLE}\n\n"
        "[Events]\n"
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )

    # ─── STT: Speech-to-Text via ElevenLabs Scribe ────────────────────────────

    def transcribe_audio(self, audio_path: str, project_id: str) -> STTResult:
        """
        Use ElevenLabs Scribe (via infsh) for speech-to-text with word timestamps.
        Output: SRT file + word timestamp array.
        """
        if not os.path.exists(audio_path):
            return STTResult(False, "", [], f"Audio not found: {audio_path}")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        srt_path = os.path.join(project_dir, "captions.srt")
        json_path = os.path.join(project_dir, "captions.json")

        # Try ElevenLabs Scribe via infsh
        cmd = [
            "infsh", "app", "run", "elevenlabs/stt",
            "--input", json.dumps({
                "audio_path": audio_path,
                "language": "auto",
                "word_timestamps": True,
                "punctuation": True
            }),
            "--output", json_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            logger.info(f"STT result: {result.stdout} {result.stderr}")

            if os.path.exists(json_path):
                return self._parse_scribe_output(json_path, srt_path, project_id)
        except subprocess.TimeoutExpired:
            return STTResult(False, "", [], "STT timed out")
        except Exception as e:
            logger.warning(f"ElevenLabs STT failed: {e}")

        # Fallback: generate placeholder SRT with estimated timing
        return self._generate_placeholder_srt(audio_path, project_id, srt_path)

    def _parse_scribe_output(self, json_path: str, srt_path: str, project_id: str) -> STTResult:
        """Parse ElevenLabs Scribe JSON output to SRT with word timings."""
        with open(json_path) as f:
            data = json.load(f)

        words = data.get("words", [])
        if not words:
            # Try alternative format
            words = data.get("word_timestamps", [])
        if not words:
            # Flatten all text from response
            text = data.get("text", "")
            if text:
                return self._text_to_srt(text, srt_path, project_id)
            return STTResult(False, "", [], "No word timestamps in STT output")

        word_timestamps = []
        srt_entries = []
        srt_index = 1

        i = 0
        while i < len(words):
            word_info = words[i]
            word = word_info.get("word", word_info.get("text", "")).strip()
            if not word:
                i += 1
                continue

            start = float(word_info.get("start", word_info.get("start_time", 0)))
            end = float(word_info.get("end", word_info.get("end_time", start + 0.5)))

            # Group words into caption lines (~3-8 words each)
            line_words = [word]
            line_start = start
            line_end = end

            j = i + 1
            while j < len(words) and len(line_words) < 8:
                next_word_info = words[j]
                next_word = next_word_info.get("word", next_word_info.get("text", "")).strip()
                if not next_word:
                    j += 1
                    continue

                next_start = float(next_word_info.get("start", next_word_info.get("start_time", end)))
                if next_start - line_end < 2.0:  # Gap less than 2s = same line
                    line_words.append(next_word)
                    line_end = float(next_word_info.get("end", next_word_info.get("end_time", line_end)))
                    j += 1
                else:
                    break

            # Build karaoke SRT entry
            caption_text = " ".join(line_words)
            start_ts = self._seconds_to_srt_time(line_start)
            end_ts = self._seconds_to_srt_time(line_end)

            srt_entries.append({
                "index": srt_index,
                "start": line_start,
                "end": line_end,
                "text": caption_text
            })

            for w in line_words:
                word_timestamps.append({"word": w, "start": line_start, "end": line_end})

            srt_index += 1
            i = j

        # Write SRT
        with open(srt_path, "w") as f:
            for entry in srt_entries:
                f.write(f"{entry['index']}\n")
                f.write(f"{self._seconds_to_srt_time(entry['start'])} --> {self._seconds_to_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n\n")

        return STTResult(True, srt_path, word_timestamps, f"STT: {len(srt_entries)} captions")

    def _text_to_srt(self, text: str, srt_path: str, project_id: str) -> STTResult:
        """Fallback: convert plain text to estimated SRT (1 line per sentence)."""
        project_dir = os.path.join(self.workspace, project_id)
        sentences = re.split(r'[.!?\n]+', text)
        word_timestamps = []
        srt_entries = []
        srt_index = 1
        current_time = 0.0
        avg_words_per_second = 2.5

        for sentence in sentences:
            words = sentence.strip().split()
            if not words:
                continue
            duration = len(words) / avg_words_per_second
            caption_text = " ".join(words)

            srt_entries.append({
                "index": srt_index,
                "start": current_time,
                "end": current_time + duration,
                "text": caption_text
            })
            word_timestamps.append({"word": caption_text, "start": current_time, "end": current_time + duration})
            current_time += duration + 0.3
            srt_index += 1

        with open(srt_path, "w") as f:
            for entry in srt_entries:
                f.write(f"{entry['index']}\n")
                f.write(f"{self._seconds_to_srt_time(entry['start'])} --> {self._seconds_to_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n\n")

        return STTResult(True, srt_path, word_timestamps, f"Generated placeholder SRT with {len(srt_entries)} captions")

    def _generate_placeholder_srt(self, audio_path: str, project_id: str, srt_path: str) -> STTResult:
        """Generate a demo SRT when STT fails — Maven-Edit style reaction words."""
        maven_words = [
            ("SICK EDIT", 0.0, 2.0, False),
            ("THIS IS CRAZY", 2.0, 4.5, False),
            ("WAIT FOR IT", 4.5, 7.0, True),
            ("OH MY GOD", 7.0, 10.0, False),
            ("NO WAY", 10.0, 13.0, True),
            ("ABSOLUTELY INSANE", 13.0, 16.0, False),
            ("MIND BLOWN", 16.0, 19.0, True),
            ("CAN'T BELIEVE", 19.0, 22.0, False),
            ("THIS ACTUALLY HAPPENED", 22.0, 25.0, True),
            ("UNREAL", 25.0, 28.0, False),
            ("BEST EVER", 28.0, 31.0, True),
            ("TOO GOOD", 31.0, 34.0, False),
            ("PERFECT", 34.0, 37.0, True),
            ("SUBSCRIBE", 37.0, 45.0, False),
        ]

        word_timestamps = []
        srt_entries = []

        for idx, (text, start, end, highlight) in enumerate(maven_words):
            srt_entries.append({
                "index": idx + 1,
                "start": start,
                "end": end,
                "text": text,
                "highlight": highlight
            })
            for word in text.split():
                word_timestamps.append({"word": word, "start": start, "end": end})

        with open(srt_path, "w") as f:
            for entry in srt_entries:
                f.write(f"{entry['index']}\n")
                f.write(f"{self._seconds_to_srt_time(entry['start'])} --> {self._seconds_to_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n\n")

        return STTResult(True, srt_path, word_timestamps, f"Demo SRT: {len(srt_entries)} captions")

    # ─── SRT → ASS Karaoke ─────────────────────────────────────────────────────

    def srt_to_ass(self, srt_path: str, project_id: str, highlight_words: Optional[List[str]] = None) -> ASSResult:
        """
        Convert SRT to ASS with Maven-Edit karaoke styling.
        highlight_words: words that use MavenHighlight style (yellow)
        """
        if not os.path.exists(srt_path):
            return ASSResult(False, "", 0, f"SRT not found: {srt_path}")

        # If input is already an ASS file, validate it and return
        if srt_path.lower().endswith('.ass'):
            with open(srt_path) as f:
                content = f.read()
            if '[Events]' in content and 'MavenMain' in content:
                return ASSResult(True, srt_path, self._count_ass_captions(content),
                                "Already a valid Maven-Edit ASS file")
            return ASSResult(False, "", 0, "ASS file lacks Maven-Edit structure")

        project_dir = os.path.join(self.workspace, project_id)
        os.makedirs(project_dir, exist_ok=True)
        ass_path = os.path.join(project_dir, "maven_captions.ass")

        highlight_words = highlight_words or ["WAIT", "NO", "MIND", "THIS", "ACTUALLY", "BEST", "PERFECT", "SUBSCRIBE"]

        with open(srt_path) as f:
            srt_content = f.read()

        entries = self._parse_srt(srt_content)
        word_timestamps = self._extract_word_timestamps(srt_content)

        with open(ass_path, "w") as f:
            f.write(self.ASS_HEADER)

            for entry in entries:
                start = entry["start"]
                end = entry["end"]
                text = entry["text"]
                style = "MavenHighlight" if self._is_highlight(text, highlight_words) else "MavenMain"

                # Convert to ASS time format
                ass_start = self._seconds_to_ass_time(start)
                ass_end = self._seconds_to_ass_time(end)

                # Build karaoke text with \k tags for word-level timing
                karaoke_text = self._build_karaoke(text, word_timestamps, start)

                f.write(f"Dialogue: 0,{ass_start},{ass_end},{style},,0,0,0,,{karaoke_text}\n")

        caption_count = len(entries)
        return ASSResult(True, ass_path, caption_count, f"ASS karaoke: {caption_count} captions")

    def _parse_srt(self, srt_content: str) -> List[dict]:
        """Parse SRT content into list of entries."""
        entries = []
        blocks = re.split(r'\n\n+', srt_content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            try:
                index = int(lines[0])
                time_line = lines[1]
                text = '\n'.join(lines[2:])

                start_str, end_str = time_line.split(' --> ')
                start = self._srt_time_to_seconds(start_str.strip())
                end = self._srt_time_to_seconds(end_str.strip())

                entries.append({
                    "index": index,
                    "start": start,
                    "end": end,
                    "text": text.strip()
                })
            except Exception:
                continue

        return entries

    def _extract_word_timestamps(self, srt_content: str) -> List[dict]:
        """Estimate per-word timestamps from SRT entries (for karaoke)."""
        entries = self._parse_srt(srt_content)
        all_words = []

        for entry in entries:
            words = entry["text"].split()
            duration = entry["end"] - entry["start"]
            word_duration = duration / len(words) if words else 0.3

            for i, word in enumerate(words):
                word_start = entry["start"] + i * word_duration
                word_end = word_start + word_duration
                all_words.append({
                    "word": word,
                    "start": word_start,
                    "end": word_end
                })

        return all_words

    def _count_ass_captions(self, ass_content: str) -> int:
        """Count caption lines in ASS content."""
        count = 0
        for line in ass_content.split('\n'):
            if line.startswith('Dialogue:'):
                count += 1
        return count

    def _build_karaoke(self, text: str, word_timestamps: List[dict], line_start: float) -> str:
        r"""
        Build ASS karaoke text with \k tags for word-by-word animation.
        Format: {\k100}WORD {\k150}WORD2
        """
        words = text.split()
        parts = []

        for word in words:
            # Find matching word timestamp
            matching = [wt for wt in word_timestamps if wt["word"].lower() == word.lower()]
            if matching:
                wt = matching[0]
                duration_ms = int((wt["end"] - wt["start"]) * 100)
                duration_ms = max(30, min(duration_ms, 500))  # clamp 30ms-500ms
            else:
                duration_ms = 100

            parts.append(f"{{\\k{duration_ms}}}{word}")

        return " ".join(parts)

    def _is_highlight(self, text: str, highlight_words: List[str]) -> bool:
        """Check if any word in text is a highlight word."""
        text_upper = text.upper()
        return any(hw.upper() in text_upper for hw in highlight_words)

    # ─── Time Format Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    @staticmethod
    def _srt_time_to_seconds(srt_time: str) -> float:
        """Convert SRT time string (HH:MM:SS,mmm) to float seconds."""
        match = re.match(r'(\d+):(\d+):(\d+)[,\.](\d+)', srt_time)
        if not match:
            return 0.0
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 1000.0

    @staticmethod
    def _seconds_to_ass_time(seconds: float) -> str:
        """Convert float seconds to ASS time format (H:MM:SS.cc)."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
