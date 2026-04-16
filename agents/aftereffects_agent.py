import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("AfterEffectsAgent")

@dataclass
class CaptionData:
    text: str
    start_time: float
    end_time: float
    style: str = "Default"

class AfterEffectsAgent:
    """
    Specialist agent for Adobe After Effects.
    Generates ExtendScript (JSX) for captioning and color grading.
    """
    def __init__(self):
        self.app_name = "aftereffects"

    def generate_caption_jsx(self, captions: List[CaptionData]) -> str:
        """
        Converts a list of caption data into AE text layers with precise timing.
        """
        jsx_lines = [
            "var project = app.project;",
            "var comp = project.activeItem;",
            "if (!(comp instanceof CompItem)) { alert('Please select a composition!'); }"
        ]

        for i, cap in enumerate(captions):
            # Escape double quotes for JSX
            safe_text = cap.text.replace('"', '\\"')

            jsx_lines.append(f"// Caption {i+1}")
            jsx_lines.append(f"var textLayer = comp.layers.addText('{safe_text}');")
            jsx_lines.append(f"textLayer.startTime = {cap.start_time};")
            jsx_lines.append(f"textLayer.outPoint = {cap.end_time};")

            # basic styling (can be expanded with a StyleGuide)
            jsx_lines.append("textLayer.property('Source Text').value.fontSize = 60;")
            jsx_lines.append("textLayer.property('Source Text').value.font = 'Arial-BoldMT';")

        jsx_lines.append("alert('Captions imported successfully!');")
        return "\n".join(jsx_lines)

    def generate_lut_jsx(self, lut_path: str, intensity: float = 1.0) -> str:
        """
        Generates JSX to apply a Color LUT (Cube file) via the Lumetri Color effect.
        """
        jsx_lines = [
            "var comp = app.project.activeItem;",
            "var adjLayer = comp.layers.addSolid([0,0,0], 'ColorGrade_Adjustment', comp.width, comp.height, 1);",
            "adjLayer.canTile = true;"
        ]

        # Apply Lumetri Color effect
        jsx_lines.append("var effect = adjLayer.Bgid('ADBE Lumetri Color');")
        jsx_lines.append(f"effect.property('Input LUT').setValue('{lut_path}');")
        jsx_lines.append(f"effect.property('Intensity').setValue({intensity});")

        jsx_lines.append("alert('Color grade applied successfully!');")
        return "\n".join(jsx_lines)

    def execute_final_polish(self, captions: List[CaptionData], lut_path: Optional[str] = None) -> str:
        """
        Bundles captioning and color grading into a single JSX script.
        """
        jsx_code = self.generate_caption_jsx(captions)
        if lut_path:
            jsx_code += "\n\n" + self.generate_lut_jsx(lut_path)

        return jsx_code
