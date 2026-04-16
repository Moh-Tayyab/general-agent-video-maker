# youtube-audio-analyzer

Extracts high-fidelity transcripts and a "vibe" analysis (pacing, tone, hooks) from YouTube videos.

## Workflow
1. Extract audio using `yt-dlp`.
2. Analyze audio via Gemini Multimodal API.
3. Output a structured report.

## Analysis Parameters
- **Full Transcript**: Timestamped text.
- **Pacing**: Words per minute, silence gaps, cut frequency.
- **Hook Analysis**: First 3-5 seconds psychological trigger.
- **Vibe**: Energy level, background music style, emotional tone.
