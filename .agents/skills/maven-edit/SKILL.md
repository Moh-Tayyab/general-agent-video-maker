---
name: maven-edit
description: "Re-edit raw video clips in the Maven-Edit style: 9:16 crop, cinematic color grade, BG music with audio ducking, word-by-word karaoke captions (Bangers font, yellow highlights), linear wipe transitions. Use when: user says 'edit this like maven edits', 'make it like @Maven-Edits', 'maven edit', 'linear wipe transition tutorial', 'add reaction video captions', 're-edit this clip'. Style: Bangers 96px font, yellow highlights for emphasis words, black 6px stroke outline, word-by-word karaoke animation with \\k tags. Tech: ffmpeg (crop/grade/mix/burn) + infsh (upscale/STT) + production/bridges/* Python wrappers."
allowed-tools: Bash(ffmpeg *), Bash(infsh *)
---

# Maven-Edit Skill

Re-edit raw video clips with the Maven-Edit style: cinematic crop to 9:16 vertical, color grade, BG music ducking, and word-by-word karaoke captions.

## What This Skill Does

Takes a raw source video and produces a Shorts-ready Maven-Edit:

```
Input: source_video.mp4 [+ bg_music.aac] [+ narration.txt]
  │
  ▼
[Step 1] Crop & Trim → 9:16 vertical, best speech window
  │
  ▼
[Step 2] Color Grade → contrast +8%, saturation -5%, gamma 0.9
  │
  ▼
[Step 3] BG Music Mix → looped track, -18dB ducking during speech
  │
  ▼
[Step 4] Caption Generation → SRT via STT → ASS karaoke
  │
  ▼
[Step 5] Burn Captions → Bangers 96px, yellow highlights, black stroke
  │
  ▼
[Step 6] Upscale (optional) → 2x via falai/topaz-video-upscaler
  │
  ▼
Output: final_maven_edit.mp4
```

## Step-by-Step

### Step 1: Crop & Trim (MediaBridge)

```python
from production.bridges.media import MediaBridge

bridge = MediaBridge()
result = bridge.crop_to_vertical(
    video_path="path/to/source.mp4",
    project_id="my-project",
    target_duration=45.0,      # target Shorts length
    crop_mode="center-pan"     # or "face-detect", "left", "right"
)
# Output: production/output/my-project/step1_cropped.mp4
```

### Step 2: Color Grade (ColorBridge)

```python
from production.bridges.color import ColorBridge

bridge = ColorBridge()
lut_path = bridge.create_cube_lut("my-project", "Cinematic_Shorts_v1",
                                  contrast=1.08, saturation=0.95, gamma=0.9)
result = bridge.apply_lut("production/output/my-project/step1_cropped.mp4",
                           "my-project", lut_path)
# Output: step2_graded.mp4 (or use apply_cinematic_grade without LUT)
```

### Step 3: BG Music Mix (MediaBridge)

```python
result = bridge.mix_bg_music(
    video_path="production/output/my-project/step2_graded.mp4",
    project_id="my-project",
    bg_music_path="path/to/bg_music.aac",
    duck_amount=-18.0,       # Maven-Edit default
    music_volume=0.3
)
# Output: step3_with_music.mp4
```

### Step 4: Speech-to-Text → SRT (CaptionBridge)

```python
from production.bridges.captions import CaptionBridge

caption = CaptionBridge()
# Extract audio from video
audio_path = bridge.extract_audio("production/output/my-project/step3_with_music.mp4",
                                   "my-project")
# Transcribe via ElevenLabs Scribe (infsh elevenlabs/stt)
stt_result = caption.transcribe_audio(audio_path, "my-project")
# srt_path: production/output/my-project/captions.srt
```

### Step 4b: SRT → ASS Karaoke (CaptionBridge)

```python
highlight_words = ["WAIT", "NO", "MIND", "THIS", "ACTUALLY", "BEST", "PERFECT", "SUBSCRIBE"]
ass_result = caption.srt_to_ass(stt_result.srt_path, "my-project", highlight_words)
# Output: production/output/my-project/maven_captions.ass
```

### Step 5: Burn Captions (RenderBridge)

```python
from production.bridges.render import RenderBridge

render = RenderBridge()
result = render.burn_captions(
    video_path="production/output/my-project/step3_with_music.mp4",
    ass_path="production/output/my-project/maven_captions.ass",
    project_id="my-project",
    output_name="final_video.mp4",
    quality="high"       # crf 17
)
# Output: production/output/my-project/final_video.mp4
```

### Step 6: Upscale (Optional, TopazBridge)

```python
from production.bridges.topaz import TopazBridge

topaz = TopazBridge()
result = topaz.upscale(
    video_path="production/output/my-project/final_video.mp4",
    project_id="my-project",
    scale=2,            # 1080x1920 → 2160x3840 (4K)
    model="Proteus"
)
# Output: production/output/my-project/upscaled.mp4
```

## Maven-Edit Visual Spec

| Property | Value |
|----------|-------|
| Resolution | 1080x1920 (9:16) |
| Frame Rate | 30fps |
| Duration | 30-60s (Shorts) |
| Caption Font | Bangers |
| Caption Size | 96px |
| Caption Position | 75% from top (lower third) |
| Caption Style | Bold, white fill, black 6px stroke |
| Highlight Color | Yellow (&H0000FFFF) |
| Color Grade | Contrast +8%, Sat -5%, Gamma 0.9 |
| BG Music Volume | 30% |
| Speech Ducking | -18dB |

## ASS Karaoke Style

The caption style uses Aegisub's `\k` karaoke tag for word-by-word timing:
- `\k100` = 100ms per word (adjust based on actual word duration)
- Yellow words use `MavenHighlight` style
- Black outline via ASS BorderStyle=1 with Outline=6

## Optional: AE MCP Server for Professional Captions

The ffmpeg ASS burn-in uses simple \k karaoke tags (color highlight only).
For **full word-by-word animation** (scale pop, drop-in, easing, glow), use the AE MCP server:

```json
// In settings.json — add MCP server (run on machine with After Effects)
{
  "mcpServers": {
    "adobe-after-effects": {
      "command": "node",
      "args": ["/path/to/production/adobe/ae_mcp_server/index.js"]
    }
  }
}
```

Then use the bridge:
```python
from production.adobe.ae_bridge import AEBridge

bridge = AEBridge()  # local MCP, or AEBridge(host="remote-ip", port=8765)

# Import video → create composition → add captions → render
bridge.create_composition("MavenEdit")
bridge.import_video("/path/to/clip.mp4")
bridge.create_karaoke_captions([
    {"text": "SICK", "start": 0.0, "end": 2.0, "highlight": False},
    {"text": "WAIT", "start": 4.5, "end": 7.0, "highlight": True},
])
bridge.render_composition("MavenEdit", "/tmp/final.mp4")
```

### AE Karaoke Animation Spec

| Property | Value |
|----------|-------|
| Animation | Scale 80→100%, position drop from +20px Y, opacity 0→100 |
| Easing | Ease-out on scale + position |
| Timing | Word animates 50ms BEFORE audio timestamp |
| Font | Bangers, 96px |
| Colors | White fill + black stroke (6px), yellow highlights |
| Position | Lower third (75% from top), centered |

## Files Generated Per Project

```
production/output/<project_id>/
├── audio_extract.aac          # Extracted audio for STT
├── step1_cropped.mp4          # After 9:16 crop
├── step2_graded.mp4           # After color grade
├── step3_with_music.mp4       # After BG music mix
├── captions.srt              # STT output (raw)
├── maven_captions.ass         # Final ASS karaoke captions
├── final_video.mp4            # Final output (after burn)
├── upscaled.mp4               # Optional 4K upscale
└── PRODUCTION_SUMMARY.md      # Technical spec + pipeline notes
```

## Quality Checks

Run after each step:
```python
from production.validation.quality import ValidationEngine
validate = ValidationEngine()
validate.verify_artifact("path/to/video.mp4", "resolution")   # >= 1080x1920
validate.verify_artifact("path/to/video.mp4", "duration")     # 30-60s
validate.verify_artifact("path/to/video.mp4", "file_exists")  # exists
```

## Dependencies

- `ffmpeg` (static 7.0.2+) — crop, grade, mix, burn
- `infsh` — ElevenLabs STT, Topaz upscaler
- Python 3.12+
- `Bangers` font installed on system
