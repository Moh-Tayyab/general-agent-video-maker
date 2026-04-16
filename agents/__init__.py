from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SkillResult:
    success: bool
    artifact_path: Optional[str] = None
    error: Optional[str] = None
