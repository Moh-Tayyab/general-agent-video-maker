import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("TimingBridge")

@dataclass
class CutSegment:
    scene_id: int
    start_time: float
    end_time: float
    description: str
    pacing: str # "fast", "steady", "slow"

class TimingBridge:
    """
    The Timing Bridge translates a reference video into a machine-readable cutlist.
    It leverages multimodal AI to identify scene boundaries and pacing.
    """
    def __init__(self):
        pass

    def extract_cutlist(self, video_path: str, multimodal_client: Any) -> Dict[str, Any]:
        """
        Analyzes a reference video and returns a cutlist JSON.

        Args:
            video_path: Path to the reference mp4.
            multimodal_client: An AI client capable of video analysis.
        """
        logger.info(f"Extracting timing from reference video: {video_path}")

        # 1. Construct a prompt for the multimodal model to identify cuts
        prompt = (
            "Analyze this video and identify all scene cuts. "
            "For each cut, provide: \n"
            "1. Scene ID\n"
            "2. Exact start timestamp (seconds)\n"
            "3. Exact end timestamp (seconds)\n"
            "4. A brief description of the visual action\n"
            "5. The pacing (fast, steady, or slow).\n"
            "Return the result as a JSON array of objects."
        )

        try:
            # This is where the call to the actual Multimodal AI happens
            # For the implementation, we call the client's analyze method
            raw_result = multimodal_client.analyze_video(video_path, prompt)
            cutlist = self._parse_multimodal_output(raw_result)

            # Calculate total reference duration
            total_duration = sum([(c['end_time'] - c['start_time']) for c in cutlist['cuts']])
            cutlist['reference_duration'] = total_duration

            return cutlist
        except Exception as e:
            logger.error(f"Failed to extract timing: {str(e)}")
            raise

    def _parse_multimodal_output(self, output: str) -> Dict[str, Any]:
        """Parses the AI's string output into a structured cutlist."""
        try:
            # Try to find the JSON array within the string
            start_idx = output.find('[')
            end_idx = output.rfind(']') + 1
            json_str = output[start_idx:end_idx]

            cuts = json.loads(json_str)
            return {"cuts": cuts}
        except Exception as e:
            logger.error(f"JSON parsing of multimodal output failed: {e}")
            # Fallback: return an empty cutlist to avoid crashing the pipeline
            return {"cuts": []}

    def validate_cutlist(self, cutlist: Dict[str, Any], reference_duration: float) -> bool:
        """Verifies that the sum of cuts matches the reference duration within a 1s margin."""
        calculated_duration = sum([(c['end_time'] - c['start_time']) for c in cutlist['cuts']])
        diff = abs(calculated_duration - reference_duration)

        if diff <= 1.0:
            return True

        logger.warning(f"Cutlist duration mismatch: Calculated {calculated_duration}s, Ref {reference_duration}s")
        return False
