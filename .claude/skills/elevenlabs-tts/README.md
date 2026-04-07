# elevenlabs-tts

**Hub group:** `video-production`
**Type:** Bash/CLI documentation
**Entry:** `SKILL.md`

---

## What This Is

A guide for generating premium text-to-speech using ElevenLabs via the [inference.sh](https://inference.sh) CLI (`infsh`). 22+ voices, 32 languages, voice tuning (stability, similarity, style).

## Quick Start

```bash
infsh login

# Basic speech
infsh app run elevenlabs/tts --input '{"text": "Hello, welcome to our demo.", "voice": "aria"}'

# Best quality, multilingual
infsh app run elevenlabs/tts --input '{
  "text": "Bonjour, bienvenue à notre démonstration.",
  "voice": "alice",
  "model": "eleven_multilingual_v2"
}'
```

## Voice Library

**Female:** `aria`, `alice`, `bella`, `jessica`, `laura`, `lily`, `sarah`, `matilda`
**Male:** `george`, `adam`, `bill`, `brian`, `callum`, `charlie`, `chris`, `daniel`, `eric`, `harry`, `liam`, `river`, `roger`, `will`

## Tuning Parameters

| Param | Range | Effect |
|-------|-------|--------|
| `stability` | 0–1 | Higher = more consistent, lower = more expressive |
| `similarity_boost` | 0–1 | Higher = closer to original voice character |
| `style` | 0–1 | Higher = more style exaggeration |

## Integration Points

| Connected Skill | How |
|-----------------|-----|
| `ai-video-generation` | VO narration → feed to avatar/lipsync apps (OmniHuman, Fabric) |
| `copywriting` | Write the script first, then generate speech |

## Complete Pipeline

```bash
# 1. Write script (copywriting skill)
# 2. Generate VO
infsh app run elevenlabs/tts --input '{
  "text": "Introducing the future of AI-powered content creation.",
  "voice": "george"
}' > voiceover.json

# 3. Create avatar video with audio
infsh app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "<audio-url-from-step-2>"
}'
```

## When to Use This

- Video narration and voiceovers
- Audiobooks and podcasts
- E-learning course narration
- Accessibility content
- **Not** for real-time conversation — use a streaming TTS API for that
