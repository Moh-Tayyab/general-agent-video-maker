import os
import subprocess
import json
from pathlib import Path

def extract_audio(url):
    """
    Extracts audio from a YouTube URL using yt-dlp in native format.
    Gemini supports native webm/m4a audio, so we avoid ffmpeg post-processing.
    """
    temp_dir = Path("/tmp/yt_audio_extract")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    unique_id = abs(hash(url))
    output_template = str(temp_dir / f"audio_{unique_id}.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "ba", # Best Audio only
        "-o", output_template,
        url
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)

        # Find the actual file created (it could be .m4a, .webm, etc.)
        files = list(temp_dir.glob(f"audio_{unique_id}.*"))
        if not files:
            raise RuntimeError("Failed to extract audio file.")

        return str(files[0])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"yt-dlp error: {e.stderr.decode()}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: python analyzer.py <url>"}))
        sys.exit(1)

    url = sys.argv[1]
    try:
        path = extract_audio(url)
        print(json.dumps({"success": True, "file_path": path}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
