# Skill-to-Command Mapping

This document maps the high-level logical skills defined in `workflow_spec.json` to the actual executable commands, scripts, and parameters required by the local software.

## 1. VideoEditingSpecialist (Adobe Premiere Pro)
| Logical Skill | Execution Method | Command/Script Detail |
| :--- | :--- | :--- |
| `trim_video` | ExtendScript (`.jsx`) | Execute `trim_to_reference.jsx` passing `ref_audio_path` and `footage_path`. Logic: Match audio peaks to reference. |
| `integrate_audio` | ExtendScript (`.jsx`) | Execute `mix_bg_music.jsx` with `bg_music_path`. Logic: Set volume to -12db, apply fade-in/out. |

## 2. AIEnhancementSpecialist (Topaz AI)
| Logical Skill | Execution Method | Command/Script Detail |
| :--- | :--- | :--- |
| `upscale_resolution` | CLI / Python Bridge | `topaz-cli.exe --input [path] --model "Proteus" --scale 4 --output [path]` |
| `reduce_noise` | CLI / Python Bridge | `topaz-cli.exe --input [path] --model "Iris" --denoise-level 50 --output [path]` |

## 3. GraphicsAndVFXSpecialist (Adobe After Effects)
| Logical Skill | Execution Method | Command/Script Detail |
| :--- | :--- | :--- |
| `generate_captions` | ExtendScript (`.jsx`) | Execute `create_srt_overlays.jsx`. Logic: Import SRT $\rightarrow$ Create text layers $\rightarrow$ Sync with audio markers. |
| `apply_color_grade` | ExtendScript (`.jsx`) | Execute `apply_lut.jsx` with `lut_file_path`. Logic: Add Adjustment Layer $\rightarrow$ Apply Lumetri Color LUT. |
| `final_export` | AE Render Queue | `aerender -project [path] -comp [comp_name] -output [path]` (H.264 preset). |

## 4. Validation Logic
| Check Type | Tool | Success Criteria |
| :--- | :--- | :--- |
| `duration_check` | `ffprobe` | `output_duration` $\approx$ `reference_duration` ($\pm 0.5s$). |
| `resolution_check` | `ffprobe` | `width == 3840` && `height == 2160` (for 4K). |
| `file_exists` | `os.path.exists` | Artifact found at designated `artifact_path`. |
