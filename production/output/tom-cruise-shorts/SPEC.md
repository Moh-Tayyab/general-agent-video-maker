# SPEC: Tom Cruise Mission Impossible 4 — Shorts Edit

> Based on: `/mnt/c/Users/Muhammad Tayyab/Downloads/Tom Cruise infiltrates RUSSIA (Best Mission Impossible 4 Scenes) 🌀 4K - Boxoffice Movie Scenes (1080p, h264) (1).mp4`
> Reference bg music: `../maven-edit-pilot/bg_music_looped.aac`

## 1. Source Analysis

| Property | Value |
|----------|-------|
| Duration | 531.4s (8.8 min compilation) |
| Resolution | 1920×1080 (16:9) |
| Codec | H.264 / AAC |
| Target output | 9:16 vertical (1080×1920) |
| Target duration | 45–60s |

### Detected Scene Boundaries (keyframes)
```
~15s   ~41s   ~55s   ~104s  ~109s  ~115s  ~122s
~136s  ~142s  ~146s  ~172s  ~180s  ~193s  ~197s
~222s  ~273s  ~278s  ~301s  ~303s  ~313s  ~337s
~342s  ~346s  ~359s  ~362s  ~365s  ~369s  ~374s
~379s  ~383s  ~390s  ~393s  ~397s  ~401s  ~404s
~408s  ~411s  ~416s  ~418s  ~422s  ~425s  ~427s
~436s  ~438s  ~440s  ~449s
```

## 2. Style Reference (Maven Edit Pilot)

The `maven-edit-pilot` output shows the target quality:
- step4_base_edit.mp4 — base graded edit
- step5_with_music.mp4 — with bg music
- final_video.mp4 — with captions overlaid
- bg_music_looped.aac — background music track

**Target aesthetic:** Cinematic, high contrast, dramatic lighting
**Caption style:** .ass timed subtitles, white text on dark semi-transparent background
**Music:** Looped energetic bg track at 35% volume

## 3. Clip Selection (6 scenes × 7–10s = ~50s)

| # | Start | End | Duration | Scene Description |
|---|-------|-----|----------|-------------------|
| 1 | 0:14 | 0:23 | 9s | Cold open — title card energy, establishing |
| 2 | 0:53 | 1:02 | 9s | Action beat — intense stunt work |
| 3 | 2:52 | 3:01 | 9s | Infiltration — stealth/mission feel |
| 4 | 4:32 | 4:41 | 9s | Cliffhanger/danger moment |
| 5 | 5:37 | 5:46 | 9s | High action sequence |
| 6 | 6:30 | 6:39 | 9s | Climax — most dramatic beat |

## 4. Workflow

```
Step 1 — Extract clips      : ffmpeg trim each scene → 9:16 crop
Step 2 — Loop bg music     : ffmpeg loop bg_music.aac to ~50s
Step 3 — Remotion compose  : Stack clips, add bg music, add captions
Step 4 — Render            : npx remotion render TomCruiseShorts out/final.mp4
```

## 5. FFmpeg Commands

### Extract + crop + trim each clip
```bash
REF="/mnt/c/Users/Muhammad Tayyab/Downloads/Tom Cruise infiltrates RUSSIA (Best Mission Impossible 4 Scenes) 🌀 4K - Boxoffice Movie Scenes (1080p, h264) (1).mp4"
OUT="/home/muhammad_tayyab/bootlogix/production/output/tom-cruise-shorts/public/video"

# 9:16 crop from 1920x1080: pad to height=1920, width=1080 → x=(1920-1080)/2=420
ffmpeg -ss $START -i "$REF" -t $DURATION \
  -vf "crop=1080:1920:420:0,scale=1080:1920" -r 30 -c:v libx264 -preset fast -crf 18 \
  -an $OUT/clip_$N.mp4
```

### Loop music
```bash
ffmpeg -stream_loop -1 -i ../maven-edit-pilot/bg_music_looped.aac -t 50 -c:a aac -b:a 192k public/audio/bg_music_50s.aac
```

## 6. Remotion Composition

### Timing
```
Scene 1: 0–270f (0–9s)
Scene 2: 270–540f (9–18s)
Scene 3: 540–810f (18–27s)
Scene 4: 810–1080f (27–36s)
Scene 5: 1080–1310f (36–44s)
Scene 6: 1310–1500f (44–50s)
Total: 50s at 30fps
```

### Audio
- bg_music_50s.aac at volume 0.35

## 7. Captions

Caption text per scene (TBD — add kinetic text overlays):
- Scene 1: "INFILTRATING RUSSIA..."
- Scene 2: [Action punch text]
- Scene 3: "THE MISSION BEGINS"
- Scene 4: [Stunt highlight]
- Scene 5: [High octane moment]
- Scene 6: "TOM CRUISE —proves why he's irreplaceable"

## 8. Acceptance Criteria

- [ ] 9:16 vertical format (1080×1920)
- [ ] Total duration 45–60s
- [ ] BG music plays throughout at 35% volume
- [ ] 6 clips seamlessly sequenced
- [ ] Text captions visible and timed
- [ ] No visual artifacts at clip boundaries
- [ ] Matches Maven Edit pilot quality bar