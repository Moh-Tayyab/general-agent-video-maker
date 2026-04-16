#!/usr/bin/env python3
"""Generate kinetic ASS captions for Tom Cruise Shorts video."""

def ts(seconds: float) -> str:
    """Convert decimal seconds to ASS timestamp format h:mm:ss.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def karaoke_line(text: str, start: float, end: float) -> str:
    """Generate a karaoke-style ASS Dialogue line with per-character timing."""
    total = end - start
    words = text.split()
    n = len(words)
    if n == 0:
        return ""
    # Distribute time evenly per word
    per_word = total / n
    parts = []
    for i, word in enumerate(words):
        w_start = start + i * per_word
        w_end = w_start + per_word
        dur_ms = int((per_word) * 1000)
        parts.append(f"{{\\k{dur_ms}}}{word}")
    return "".join(parts)

# ---------------------------------------------------------------------------
# Caption definitions: (start_sec, end_sec, style, text)
# ---------------------------------------------------------------------------
captions = [
    # SCENE 1 — cold open (0–9s)
    (0.0, 2.5,  "MavenMain",    "MISSION"),
    (2.5, 5.0,  "MavenMain",    "IMPOSSIBLE"),
    (5.0, 8.0,  "MavenHighlight","RUSSIA INFILTRATION"),
    (7.5, 9.0,  "MavenMain",    "TOM CRUISE"),

    # SCENE 2 — action beat (9–18s)
    (9.0, 11.5, "MavenHighlight","CRAZY STUNTS"),
    (11.5,14.0, "MavenMain",    "PURE ACTION"),
    (14.0,17.0, "MavenHighlight","NO CGI"),
    (17.0,19.0, "MavenMain",    "ALL HIM"),

    # SCENE 3 — infiltration (18–27s)
    (18.0, 21.0,"MavenMain",    "INFILTRATING"),
    (21.0, 24.0,"MavenHighlight","THE MISSION BEGINS"),
    (24.0, 27.0,"MavenMain",    "HE NEVER QUITS"),

    # SCENE 4 — cliffhanger (27–36s)
    (27.0, 30.0,"MavenHighlight","EXTREME"),
    (30.0, 33.0,"MavenMain",    "THE FALL"),
    (33.0, 36.0,"MavenHighlight","BUT HE GETS UP"),

    # SCENE 5 — high action (36–45s)
    (36.0, 39.0,"MavenMain",    "NEXT LEVEL"),
    (39.0, 42.0,"MavenHighlight","INTENSITY"),
    (42.0, 45.0,"MavenMain",    "UNSTOPPABLE FORCE"),

    # SCENE 6 — climax (45–54s)
    (45.0, 48.0,"MavenHighlight","FINAL MOMENT"),
    (48.0, 51.0,"MavenMain",    "THE CRUISE"),
    (51.0, 54.0,"MavenHighlight","IRREPLACEABLE"),
]

# ---------------------------------------------------------------------------
# Build ASS file
# ---------------------------------------------------------------------------
lines = [
    "[Script Info]",
    "Title: Tom Cruise Shorts Captions",
    "ScriptType: v4.00+",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "ScaledBorderAndShadow: yes",
    "",
    "[V4+ Styles]",
    "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
    "Style: MavenMain,Bangers,96,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,10,10,480,1",
    "Style: MavenHighlight,Bangers,96,&H0002C8F5,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,10,10,480,1",
    "",
    "[Events]",
    "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
]

for start, end, style, text in captions:
    kline = karaoke_line(text, start, end)
    t_start = ts(start)
    t_end = ts(end)
    lines.append(f"Dialogue: 0,{t_start},{t_end},{style},,0,0,0,,{kline}")

ass_content = "\r\n".join(lines) + "\r\n"

out_path = "/home/muhammad_tayyab/bootlogix/production/output/tom-cruise-shorts/public/audio/tom_captions.ass"
with open(out_path, "w") as f:
    f.write(ass_content)

print(f"Written: {out_path}")
print(f"Caption lines: {len(captions)}")