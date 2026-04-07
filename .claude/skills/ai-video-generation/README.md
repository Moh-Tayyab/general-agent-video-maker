# ai-video-generation

**Hub group:** `video-production`
**Type:** Bash/CLI documentation
**Entry:** `SKILL.md`

---

## What This Is

A guide for generating AI videos using 40+ models via the [inference.sh](https://inference.sh) CLI (`infsh`). Covers text-to-video, image-to-video, avatar animation, lipsync, video upscaling, and foley sound.

## Quick Start

```bash
# Login
infsh login

# Text-to-video with Veo 3.1
infsh app run google/veo-3-1-fast --input '{"prompt": "drone shot flying over a forest"}'

# Image-to-video with Wan 2.5
infsh app run falai/wan-2-5 --input '{"image_url": "https://your-image.jpg"}'

# List all video apps
infsh app list --category video
```

## Key Models

| Model | App ID | Best For |
|-------|--------|---------|
| Veo 3.1 Fast | `google/veo-3-1-fast` | Fast generation, optional audio |
| Veo 3.1 | `google/veo-3-1` | Best quality, frame interpolation |
| Seedance 1.5 Pro | `bytedance/seedance-1-5-pro` | First-frame control |
| Wan 2.5 | `falai/wan-2-5` | Image animation |
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | Multi-character avatar |
| Fabric 1.0 | `falai/fabric-1-0` | Image talks with lipsync |

## Integration Points

| Connected Skill | How |
|-----------------|-----|
| `elevenlabs-tts` | Generate VO narration → feed to avatar/lipsync apps |
| `copywriting` | Write the script/copy *before* generating the video |

## Pipeline Example

```
copywriting → write script
       ↓
elevenlabs-tts → generate narration VO
       ↓
ai-video-generation → create video (text-to-video or avatar)
       ↓
ai-video-generation (hunyuanvideo-foley) → add sound effects
       ↓
ai-video-generation (topaz-upscaler) → enhance quality
```

## When to Use This

- Short-form social media content (YouTube Shorts, TikTok, Reels)
- Product demos and explainer videos
- AI avatars and talking-head content
- Visualizing concepts or scenes described in copy
- **Not** for live-action production — this is AI-generated content
