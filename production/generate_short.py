#!/usr/bin/env python3
"""
generate_short.py
=================
Reusable Short video production pipeline.

Usage:
    python generate_short.py tiny-bike
    python generate_short.py "giant burger" --style energetic --render

Output:
    production/output/<subject>/
        script.txt          — Full 45s script with timings
        cutlist.json        — Structured cut-list (capcut json)
        qa.json             — Q/A section
        capcut_project.json — Import directly into CapCut
        [video.mp4]         — Only if --render and infsh is available
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

CAPTION_STYLES = ["bold_white", "punch_in", "green_checkmark", "yellow_highlight",
                  "italic", "red_underline", "center_dramatic", "subtle_small", "cta_card"]

TRANSITIONS = ["jump_cut", "smooth_zoom", "side_by_side", "slow_mo_zoom",
               "cut_to_detail", "comedic_pop", "wide_to_medium", "stinger_hit",
               "freeze_frame", "slide_up", "fade_graphic", "crossfade",
               "screen_mockup", "fade_to_black"]

MUSIC_CUES = ["build_tension", "beat_drop_ting", "light_swell", "tiny_spin_sfx",
              "mechanical_ambient", "bag_unzip_sfx", "street_ambiance",
              "comedic_stinger", "beat_hit_burst", "stop_scroll_sfx",
              "subtle_whoosh", "cinematic_rumble", "viral_cha_ching",
              "uplift_fadeout"]


@dataclass
class ScriptLine:
    line: int
    start: float
    end: float
    text: str
    caption_style: str
    caption_extra: str = ""          # emoji or keyword highlight
    jump_cut: bool = False
    pattern_interrupt: bool = False

    @property
    def duration(self) -> float:
        return self.end - self.start

    def format_ffmpeg_start(self) -> str:
        mins, secs = divmod(self.start, 60)
        return f"{int(mins):02d}:{secs:05.2f}"


@dataclass
class StoryboardCut:
    time_start: float
    time_end: float
    visual: str
    caption: str
    music_cue: str
    transition: str
    notes: str = ""

    @property
    def duration(self) -> float:
        return self.time_end - self.time_start


@dataclass
class QAItem:
    question: str
    answer: str


@dataclass
class VoiceOverStyle:
    name: str
    description: str
    delivery_tags: list[str]
    recommended_for: list[str]


# ---------------------------------------------------------------------------
# Subject templates — swap these to re-skin for new Shorts
# ---------------------------------------------------------------------------

SUBJECT_TEMPLATES = {
    "tiny-bike": {
        "subject_name": "tiny bike",
        "subject_scale": "fits in the palm of your hand",
        "scale_ref": "smaller than your thumb",
        "carrying_method": "puts it in his bag like a textbook",
        "reaction_context": "on the same roads as cars and trucks",
        "reaction_compound": "Absolute chaos. 😳",
        "build_detail": "custom-built from scratch — every component engineered at micro-scale",
        "science_beat": "unexpected scale",
        "defies_what": "what a bike is supposed to be",
        "why_viral": "it broke the internet",
        "hook_extras": ["😳", "🤯", "🔬"],
        "q1_subject_fact": "real — fully functioning pedals, drivetrain, steering, and brakes",
        "q2_subject_fact": "built from scratch with custom micro-scale components: special bearings, tiny chain or belt drive",
        "q3_safety": "rides on public roads but lacks standard safety features — more spectacle than recommendation",
        "q4_who": "attributed to a Russian builder known for miniature bike projects; @ClpQuips repackages with added commentary",
        "q5_viral": "unexpected scale violation + reaction shots. The brain is wired to notice things that break mental models",
    },
    "giant-burger": {
        "subject_name": "giant burger",
        "subject_scale": "taller than a toddler",
        "scale_ref": "buns the size of dinner plates",
        "carrying_method": "needs two people to carry it to the table",
        "reaction_context": "standing next to regular-sized burgers for comparison",
        "reaction_compound": "Mouths open. Forks frozen. 🍔",
        "build_detail": "hand-crafted from scratch — 20+ ingredients stacked with precision",
        "science_beat": "supersized portions",
        "defies_what": "what a burger is supposed to be",
        "why_viral": "it broke Instagram",
        "hook_extras": ["🍔", "🤯", "👀"],
        "q1_subject_fact": "real — fully edible, crafted over several hours with stacked layers and full-size toppings",
        "q2_subject_fact": "built by stacking 20+ layers: custom-sized buns, oversized patties, and macroscaled vegetables",
        "q3_safety": "purely a food spectacle — not intended to be finished by one person; shareable portions",
        "q4_who": "created by competitive eaters or food stunt creators known for oversized food challenges",
        "q5_viral": "visual absurdity + relatable food envy. Size surprises trigger share reflexes",
    },
    "tiny-house": {
        "subject_name": "tiny house",
        "subject_scale": "fits on a flatbed trailer",
        "scale_ref": "smaller than a parking spot",
        "carrying_method": "gets towed behind a pickup truck like a camper",
        "reaction_context": "pulls up to a regular suburban neighborhood",
        "reaction_compound": "Neighbors stop. Stare. Front doors open. 🏠",
        "build_detail": "fully built out — kitchen, bed, bathroom — in under 200 square feet",
        "science_beat": "spatial efficiency",
        "defies_what": "what a house is supposed to be",
        "why_viral": "it broke Pinterest",
        "hook_extras": ["🏠", "🤯", "🛋️"],
        "q1_subject_fact": "real — fully functional living space with plumbing, electric, and furniture scaled to fit",
        "q2_subject_fact": "every inch maximized: fold-down bed, compact kitchen, wet bath bathroom, and multi-use furniture",
        "q3_safety": "built on a trailer for mobility; subject to trailer towing regulations and height restrictions",
        "q4_who": "popularized by tiny home enthusiasts and van-life communities as an alternative housing movement",
        "q5_viral": "minimalism + aspiration. The dream of owning a home — compressed into something adorable",
    },
    "mini-car": {
        "subject_name": "mini car",
        "subject_scale": "fits in a shopping cart",
        "scale_ref": "wheels no bigger than hockey pucks",
        "carrying_method": "this thing literally folds up and goes in the trunk",
        "reaction_context": "drives down the highway next to semi-trucks",
        "reaction_compound": "Everyone's staring. Horns honking. Chaos. 🚗",
        "build_detail": "street-legal — working headlights, horn, and a 50cc engine",
        "science_beat": "extreme miniaturization",
        "defies_what": "what a car is supposed to be",
        "why_viral": "it broke TikTok",
        "hook_extras": ["🚗", "🤯", "⚡"],
        "q1_subject_fact": "real — legally drivable in many countries with a 50cc engine and proper registration",
        "q2_subject_fact": "engineered with scaled-down drivetrain, working steering, horn, headlights, and full braking",
        "q3_safety": "street-legal in many regions but highly exposed — no airbags or crumple zones at this scale",
        "q4_who": "common in Asian markets as a commuter micro-car; some built as custom kit cars globally",
        "q5_viral": "size + capability mismatch. A car that fits in a cart drives on highways — that contradiction drives shares",
    },
}

# Fallback template for unknown subjects
def build_custom_template(subject: str) -> dict:
    return {
        "subject_name": subject,
        "subject_scale": "fits in the palm of your hand",
        "scale_ref": "smaller than your thumb",
        "carrying_method": "puts it in his bag like a textbook",
        "reaction_context": "on the same roads as cars and trucks",
        "reaction_compound": "Absolute chaos. 😳",
        "build_detail": "custom-built from scratch — every component engineered at micro-scale",
        "science_beat": "unexpected scale",
        "defies_what": f"what a {subject} is supposed to be",
        "why_viral": "it broke the internet",
        "hook_extras": ["😳", "🤯", "🔬"],
        "q1_subject_fact": f"real and fully functional — not a toy",
        "q2_subject_fact": "built from scratch with custom-engineered components",
        "q3_safety": "rides/drives on public roads but lacks standard safety features",
        "q4_who": "built by a hobbyist or craftsman known for micro-scale engineering projects",
        "q5_viral": "unexpected scale violation + reaction shots. The brain is wired to notice things that break mental models",
    }


# ---------------------------------------------------------------------------
# Core generation functions
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def generate_script(template: dict, subject_slug: str) -> list[ScriptLine]:
    s = template

    lines = [
        ScriptLine(1,  0,  3,  f"Okay, you've seen big things. You've seen small things. But have you seen THIS?",
                   "bold_white", jump_cut=True),
        ScriptLine(2,  3,  6,  f"This is literally a {s['subject_name']} that {s['subject_scale']}.",
                   "punch_in", s["hook_extras"][0]),
        ScriptLine(3,  6,  9,  "No tricks. No CGI. A real, fully working build.",
                   "green_checkmark"),
        ScriptLine(4,  9,  12, f"Meet the world's most impossibly small {s['subject_name']}.",
                   "center_dramatic", s["hook_extras"][1], jump_cut=True),
        ScriptLine(5,  12, 15, f"The wheels? {s['scale_ref'].capitalize()}.",
                   "yellow_highlight"),
        ScriptLine(6,  15, 18, s["build_detail"] + ".",
                   "white", jump_cut=True),
        ScriptLine(7,  18, 21, f"It's so small, this guy just {s['carrying_method']}.",
                   "white", "📚"),
        ScriptLine(8,  21, 24, f"Then pulls it out and uses it… {s['reaction_context']}.",
                   "italic", s["hook_extras"][2]),
        ScriptLine(9,  24, 27, f"Yes — {s['reaction_context'].replace('.', '')}.",
                   "red_underline"),
        ScriptLine(10, 27, 30, f"The look on people's faces? {s['reaction_compound']}",
                   "bold_white", jump_cut=True, pattern_interrupt=True),
        ScriptLine(11, 30, 33, "This is the kind of thing that makes you stop scrolling.",
                   "fade_in"),
        ScriptLine(12, 33, 36, f"Science says we're drawn to {s['science_beat']} — and this delivers.",
                   "subtle_small"),
        ScriptLine(13, 36, 39, f"It defies {s['defies_what']}.",
                   "center_dramatic", jump_cut=True),
        ScriptLine(14, 39, 42, f"And honestly? That's exactly why {s['why_viral']}.",
                   "bold_white"),
        ScriptLine(15, 42, 45, "If you found this satisfying — follow for more impossibly cool things.",
                   "cta_card"),
    ]
    return lines


def generate_storyboard(template: dict, script_lines: list[ScriptLine]) -> list[StoryboardCut]:
    cuts = [
        StoryboardCut(0,   5,  "Reaction shot — someone's jaw drops, eyes widen",
                      script_lines[0].text[:50] + "…",
                      "build_tension", "jump_cut",
                      "Pattern interrupt: hook — get attention fast"),
        StoryboardCut(5,   8,  f"Extreme close-up: {template['subject_name']} sitting in an open palm",
                      script_lines[1].text[:50] + "…",
                      "beat_drop_ting", "smooth_zoom",
                      "Scale reveal moment"),
        StoryboardCut(8,   12, "Wide shot: subject next to a pencil/phone for scale comparison",
                      script_lines[2].text[:50] + "…",
                      "light_swell", "side_by_side",
                      "Establish reality — no CGI claim"),
        StoryboardCut(12,  15, f"Close-up: scale reference — {template['scale_ref']}",
                      script_lines[4].text[:50] + "…",
                      "tiny_spin_sfx", "slow_mo_zoom",
                      "Punch line on scale"),
        StoryboardCut(15,  18, "POV shot: build detail — welding, micro-components, precision",
                      script_lines[5].text[:50] + "…",
                      "mechanical_ambient", "cut_to_detail",
                      "Technical credibility beat"),
        StoryboardCut(18,  21, f"Carrying reveal: {template['carrying_method']}",
                      script_lines[6].text[:50] + "…",
                      "comedic_pop", "comedic_pop",
                      "Comedic payoff on portability"),
        StoryboardCut(21,  24, f"Wide shot: tiny subject in use — {template['reaction_context']}",
                      script_lines[7].text[:50] + "…",
                      "street_ambiance", "wide_to_medium",
                      "Action reveal — scale in context"),
        StoryboardCut(24,  27, f"Reaction compilation: bystanders staring, drivers reacting",
                      script_lines[8].text[:50] + "…",
                      "comedic_stinger", "stinger_hit",
                      "Social proof of impact"),
        StoryboardCut(27,  30, "Slow-mo reaction face: pure disbelief",
                      script_lines[9].text[:50] + "…",
                      "beat_hit_burst", "freeze_frame",
                      "Pattern interrupt: reaction break"),
        StoryboardCut(30,  33, "Phone scrolling animation — hand scrolling Shorts",
                      script_lines[10].text[:50] + "…",
                      "stop_scroll_sfx", "slide_up",
                      "Relatability hook — 'this is why you're here'"),
        StoryboardCut(33,  36, "Minimalist graphic: brain + scale icon animation",
                      script_lines[11].text[:50] + "…",
                      "subtle_whoosh", "fade_graphic",
                      "Science beat — why it works"),
        StoryboardCut(36,  39, f"Silhouette against backdrop — defies {template['defies_what']}",
                      script_lines[12].text[:50] + "…",
                      "cinematic_rumble", "crossfade",
                      "Cinematic mood shift"),
        StoryboardCut(39,  42, "Phone screen: viral metrics / view count trending upward",
                      script_lines[13].text[:50] + "…",
                      "viral_cha_ching", "screen_mockup",
                      "Social proof of virality"),
        StoryboardCut(42,  45, "CTA card: subscribe button + channel avatar fade-out",
                      script_lines[14].text[:50] + "…",
                      "uplift_fadeout", "fade_to_black",
                      "Call to action — follow for more"),
    ]
    return cuts


def generate_qa(template: dict) -> list[QAItem]:
    return [
        QAItem(f"Is the {template['subject_name']} real or fake?",
               template["q1_subject_fact"]),
        QAItem(f"How is this even possible?",
               template["q2_subject_fact"]),
        QAItem("Is it safe to use in public?",
               template["q3_safety"]),
        QAItem("Who made it?",
               template["q4_who"]),
        QAItem("Why did this go viral?",
               template["q5_viral"]),
    ]


def generate_vo_styles() -> list[VoiceOverStyle]:
    return [
        VoiceOverStyle(
            "Energetic",
            "Fast-paced, upward inflections, breathy excitement on key punch lines. "
            "高能量, 150–160 BPM delivery. Best for shock-value, reaction-style edits.",
            ["fast_pace", "breathy_excitement", "upward_inflection"],
            ["shock_value", "reaction_clips", "viral_hooks"],
        ),
        VoiceOverStyle(
            "Friendly",
            "Conversational, warm tone, slight natural chuckle on 'chaos' or reaction lines. "
            "Think 'buddy showing you something wild at a garage sale.'",
            ["conversational", "warm", "slight_chuckle", "natural_pacing"],
            ["relatable_shorts", "shareable", "lifestyle_content"],
        ),
        VoiceOverStyle(
            "Professional",
            " steady, measured, documentary-narration tone. Calm confidence on factual claims. "
            "Best for educational or breakdown-style Shorts.",
            ["steady_pace", "measured", "confident", "documentary_tone"],
            ["educational", "breakdown", "explainer"],
        ),
    ]


# ---------------------------------------------------------------------------
# CapCut JSON generation
# ---------------------------------------------------------------------------

def generate_capcut_project(
    subject_slug: str,
    script_lines: list[ScriptLine],
    storyboard: list[StoryboardCut],
) -> dict:
    """
    Generate a CapCut-compatible project.json structure.

    CapCut project structure (simplified, production-Ready):
    - workspace.version, workspace.duration
    - resources[] — media files referenced
    - timeline — videoTrack, audioTrack, textTrack
    - Each segment has id, start, duration, type, content
    """
    total_duration_ms = 45000  # 45s in ms

    # Build text/caption track items
    text_items = []
    for i, line in enumerate(script_lines):
        start_ms = int(line.start * 1000)
        duration_ms = int(line.duration * 1000)
        text_items.append({
            "id": f"text_{i+1}",
            "type": "text",
            "start": start_ms,
            "duration": duration_ms,
            "content": {
                "text": line.text,
                "style": line.caption_style,
                "extras": line.caption_extra,
                "animation": "fade_in" if line.pattern_interrupt else "punch_in",
            },
        })

    # Build video track segments (14 cuts for 45s)
    video_segments = []
    for i, cut in enumerate(storyboard):
        start_ms = int(cut.time_start * 1000)
        duration_ms = int(cut.duration * 1000)
        video_segments.append({
            "id": f"clip_{i+1}",
            "type": "video",
            "start": start_ms,
            "duration": duration_ms,
            "content": {
                "visual": cut.visual,
                "caption": cut.caption,
                "transition": cut.transition,
                "music_cue": cut.music_cue,
                "notes": cut.notes,
            },
        })

    project = {
        "schema": "capcut.project.v1",
        "workspace": {
            "version": "1.0.0",
            "name": f"short-{subject_slug}",
            "duration": total_duration_ms,
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "frame_rate": 30,
            "orientation": "portrait",
        },
        "resources": {
            "placeholder_clips": len(video_segments),
            "placeholder_texts": len(text_items),
            "placeholder_audio": 1,
            "placeholder_music": 1,
            "note": "Replace placeholder values with actual media files in CapCut",
        },
        "timeline": {
            "video_track": {
                "segments": video_segments,
                "track_config": {
                    "locked": False,
                    "visible": True,
                    "muted": False,
                },
            },
            "text_track": {
                "segments": text_items,
                "default_style": "bold_white",
                "default_size": 48,
                "default_color": "#FFFFFF",
                "default_align": "center",
            },
            "audio_track": {
                "segments": [
                    {
                        "id": "vo_main",
                        "type": "voiceover",
                        "start": 0,
                        "duration": total_duration_ms,
                        "content": {
                            "style": "energetic",
                            "file": "vo_energetic.wav",
                            "note": "Replace with recorded VO",
                        },
                    },
                ],
            },
            "music_track": {
                "segments": [
                    {
                        "id": "bg_music",
                        "type": "background_music",
                        "start": 0,
                        "duration": total_duration_ms,
                        "content": {
                            "file": "background_track.mp3",
                            "fade_in": 500,
                            "fade_out": 1500,
                            "note": "Replace with licensed track",
                        },
                    },
                ],
            },
        },
        "production_notes": {
            "pacing": "0-12s hook+reveal, 12-24s build, 24-36s payoff, 36-45s close",
            "jump_cuts_at_lines": [4, 6, 10, 13],
            "pattern_interrupt_at": "27-30s (reaction compilation)",
            "aspect_ratio": "9:16 vertical (native Shorts)",
            "caption_placement": "centered, bottom third, or keyword highlight per line style",
            "music_tips": {
                "0-12s": "build tension — low drone or rising swell",
                "12-24s": "beat drop + comedic swell on reveal",
                "24-30s": "stinger hits on reaction cuts",
                "30-39s": "cinematic rumble or stop-scroll SFX",
                "39-45s": "uplift fade-out for CTA",
            },
        },
    }
    return project


# ---------------------------------------------------------------------------
# Output / rendering
# ---------------------------------------------------------------------------

def write_outputs(
    output_dir: Path,
    subject_slug: str,
    script_lines: list[ScriptLine],
    storyboard: list[StoryboardCut],
    qa_items: list[QAItem],
    capcut_project: dict,
    vo_styles: list[VoiceOverStyle],
    style_arg: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. script.txt
    script_path = output_dir / "script.txt"
    with open(script_path, "w") as f:
        f.write(f"SCRIPT — {subject_slug.upper()} (45s)\n")
        f.write("=" * 60 + "\n\n")
        for line in script_lines:
            flags = []
            if line.jump_cut: flags.append("JUMP_CUT")
            if line.pattern_interrupt: flags.append("PATTERN_INTERRUPT")
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            f.write(f"Line {line.line:02d}  {line.start:5.1f}s–{line.end:5.1f}s  "
                    f"({line.duration:.1f}s){flag_str}\n")
            f.write(f"  {line.text}\n")
            f.write(f"  Caption: {line.caption_style}  |  Extra: {line.caption_extra}\n\n")
        f.write("\nVOICE-OVER OPTIONS\n")
        f.write("=" * 60 + "\n")
        for vo in vo_styles:
            f.write(f"\n  [{vo.name}]\n  {vo.description}\n")
            f.write(f"  Tags: {', '.join(vo.delivery_tags)}\n")
            f.write(f"  Best for: {', '.join(vo.recommended_for)}\n")
    print(f"  ✓ {script_path}")

    # 2. cutlist.json
    cutlist_path = output_dir / "cutlist.json"
    with open(cutlist_path, "w") as f:
        json.dump({
            "subject": subject_slug,
            "script_lines": [
                {
                    "line": l.line,
                    "start": l.start,
                    "end": l.end,
                    "duration": l.duration,
                    "text": l.text,
                    "caption_style": l.caption_style,
                    "caption_extra": l.caption_extra,
                    "jump_cut": l.jump_cut,
                    "pattern_interrupt": l.pattern_interrupt,
                } for l in script_lines
            ],
            "storyboard": [
                {
                    "time_start": c.time_start,
                    "time_end": c.time_end,
                    "duration": c.duration,
                    "visual": c.visual,
                    "caption": c.caption,
                    "music_cue": c.music_cue,
                    "transition": c.transition,
                    "notes": c.notes,
                } for c in storyboard
            ],
            "qa": [{"question": q.question, "answer": q.answer} for q in qa_items],
            "vo_styles": [
                {
                    "name": vo.name,
                    "description": vo.description,
                    "delivery_tags": vo.delivery_tags,
                    "recommended_for": vo.recommended_for,
                } for vo in vo_styles
            ],
            "production_notes": capcut_project["production_notes"],
        }, f, indent=2)
    print(f"  ✓ {cutlist_path}")

    # 3. capcut_project.json
    capcut_path = output_dir / "capcut_project.json"
    with open(capcut_path, "w") as f:
        json.dump(capcut_project, f, indent=2)
    print(f"  ✓ {capcut_path}")

    # 4. qa.txt (human-readable Q/A)
    qa_path = output_dir / "qa.txt"
    with open(qa_path, "w") as f:
        f.write(f"Q&A — {subject_slug.upper()}\n")
        f.write("=" * 60 + "\n\n")
        for i, qa in enumerate(qa_items, 1):
            f.write(f"Q{i}: {qa.question}\n")
            f.write(f"A{i}: {qa.answer}\n\n")
    print(f"  ✓ {qa_path}")

    # 5. Print VO recommendation
    print(f"\n  Recommended VO style: {style_arg.capitalize()}")
    print(f"  Run with --render to generate video via infsh (if installed)")


def render_with_infsh(
    subject_slug: str,
    script_lines: list[ScriptLine],
    style_arg: str,
    output_dir: Path,
) -> bool:
    """
    Attempt to render video via infsh CLI.
    Returns True if successful, False if infsh not available.
    """
    print("\n  [infsh] Checking availability…")
    try:
        result = subprocess.run(
            ["infsh", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        print(f"  [infsh] Found: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("  [infsh] Not installed. Install: https://inference.sh")
        print("  [infsh] Skipping render. File generation complete.")
        return False

    # Build a composite prompt from the script
    hook = script_lines[0].text
    reveal = script_lines[3].text
    punch = script_lines[9].text

    prompt = (
        f"Vertical 9:16 Short. Cinematic. "
        f"Hook: {hook} "
        f"Reveal: {reveal} "
        f"Reaction climax: {punch} "
        f"No music. Real-world setting. "
        f"Shock and awe editing style."
    )

    output_mp4 = output_dir / "video.mp4"
    print(f"  [infsh] Submitting text-to-video job…")
    print(f"  [infsh] Prompt: {prompt[:120]}…")

    try:
        cmd = [
            "infsh", "app", "run", "google/veo-3-1-fast",
            "--input", json.dumps({"prompt": prompt, "duration": 5}),
        ]
        print(f"  [infsh] Running: {' '.join(cmd)}")
        # NOTE: The actual render call — uncomment when ready:
        # result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        # if result.returncode == 0:
        #     print(f"  [infsh] Render complete → {output_mp4}")
        #     return True
        # else:
        #     print(f"  [infsh] Error: {result.stderr}")
        #     return False
        print("  [infsh] Render call prepared but not executed (comment in to enable)")
        return True
    except subprocess.SubprocessError as e:
        print(f"  [infsh] Failed: {e}")
        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="generate_short.py — Reusable Short video production pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python generate_short.py tiny-bike
              python generate_short.py "giant burger" --style friendly
              python generate_short.py mini-car --render

            Output: production/output/<subject>/
        """),
    )
    parser.add_argument(
        "subject", nargs="+", help="Video subject (e.g., tiny-bike, giant-burger)"
    )
    parser.add_argument(
        "--style",
        choices=["energetic", "friendly", "professional"],
        default="energetic",
        help="VO delivery style (default: energetic)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Also submit video render job via infsh (requires infsh CLI)",
    )
    parser.add_argument(
        "--output",
        default="production/output",
        help="Output base directory (default: production/output)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Normalize subject
    subject_raw = " ".join(args.subject)
    subject_slug = slugify(subject_raw)

    # Resolve template
    if subject_slug in SUBJECT_TEMPLATES:
        template = SUBJECT_TEMPLATES[subject_slug]
    else:
        print(f"[warn] No built-in template for '{subject_slug}' — using custom template")
        template = build_custom_template(subject_raw)

    print(f"\n{'='*60}")
    print(f"  GENERATE_SHORT.PY")
    print(f"  Subject: {subject_raw} ({subject_slug})")
    print(f"  VO Style: {args.style}")
    print(f"{'='*60}\n")

    # Generate all content
    script_lines   = generate_script(template, subject_slug)
    storyboard     = generate_storyboard(template, script_lines)
    qa_items       = generate_qa(template)
    vo_styles      = generate_vo_styles()
    capcut_project = generate_capcut_project(subject_slug, script_lines, storyboard)

    # Output directory
    base_out = Path(args.output)
    output_dir = base_out / subject_slug

    # Write all files
    print("Writing output files:")
    write_outputs(
        output_dir, subject_slug,
        script_lines, storyboard, qa_items,
        capcut_project, vo_styles, args.style,
    )

    # Optional render
    if args.render:
        render_with_infsh(subject_slug, script_lines, args.style, output_dir)

    print(f"\n  All files → {output_dir}/")
    print(f"\n  CapCut: import {output_dir}/capcut_project.json")
    print(f"  Next:   drop in footage, record VO, export.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
