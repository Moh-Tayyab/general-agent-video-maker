import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FORMAT = "[ManifestManager] %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("ManifestManager")

@dataclass
class PhaseState:
    status: str  # PENDING, IN_PROGRESS, GENERATING, BAKING, COMPLETED, FAILED
    agent: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    feedback: Optional[str] = None

@dataclass
class ProjectManifest:
    project_id: str
    version: str = "2.1"
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    current_phase: str = "SEARCH"
    quality_target: str = "standard"  # standard (Remotion), cinematic (After Effects)
    phases: Dict[str, PhaseState] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class ManifestManager:
    """
    Handles the persistence of agentic project manifests to disk.
    Supports the SSD (Search -> Script -> Design -> Generate) pipeline.
    """
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to projects/manifests/ in the workspace root
            self.storage_path = Path(__file__).parent.parent / "projects" / "manifests"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Manifest storage initialized at: {self.storage_path}")

    def _get_file_path(self, project_id: str) -> Path:
        return self.storage_path / f"{project_id}.json"

    def create_manifest(self, project_id: str, metadata: Dict[str, Any], quality_target: str = "standard") -> ProjectManifest:
        """Initializes a new SSD project manifest."""
        phases = {
            "SEARCH": PhaseState(status="PENDING", dependencies=[]),
            "SCRIPT": PhaseState(status="PENDING", dependencies=["SEARCH"]),
            "DESIGN": PhaseState(status="PENDING", dependencies=["SCRIPT"]),
            "GENERATE": PhaseState(status="PENDING", dependencies=["SCRIPT", "DESIGN"]),
            "CRITIQUE": PhaseState(status="PENDING", dependencies=["GENERATE"]),
        }

        manifest = ProjectManifest(
            project_id=project_id,
            status="IN_PROGRESS",
            current_phase="SEARCH",
            quality_target=quality_target,
            phases=phases,
            metadata=metadata
        )

        # Mark first phase as in progress
        manifest.phases["SEARCH"].status = "IN_PROGRESS"
        manifest.phases["SEARCH"].started_at = datetime.utcnow().isoformat()

        self.save_manifest(manifest)
        return manifest

    def save_manifest(self, manifest: ProjectManifest) -> None:
        """Saves the manifest to disk."""
        file_path = self._get_file_path(manifest.project_id)
        manifest.updated_at = datetime.utcnow().isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(manifest), f, indent=2)
        logger.debug(f"Manifest saved: {file_path}")

    def load_manifest(self, project_id: str) -> Optional[ProjectManifest]:
        """Reads the current manifest from disk."""
        file_path = self._get_file_path(project_id)
        if not file_path.exists():
            logger.warning(f"Manifest not found for project: {project_id}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Reconstruct PhaseState objects
            phases_data = data.pop('phases', {})
            phases = {k: PhaseState(**v) for k, v in phases_data.items()}

            return ProjectManifest(phases=phases, **data)

    def update_artifact(self, project_id: str, phase: str, artifact_key: str, path: Any) -> None:
        """Atomically updates a specific artifact path within a phase."""
        manifest = self.load_manifest(project_id)
        if not manifest:
            raise ValueError(f"Project {project_id} not found.")
        
        if phase not in manifest.phases:
             raise ValueError(f"Phase {phase} not found in project {project_id}.")

        manifest.phases[phase].artifacts[artifact_key] = path
        self.save_manifest(manifest)
        logger.info(f"Artifact '{artifact_key}' recorded for project '{project_id}' in phase '{phase}'")

    def transition_phase(self, project_id: str, next_phase: str, agent_id: str) -> bool:
        """
        Moves the project to the next phase if dependencies are met.
        """
        manifest = self.load_manifest(project_id)
        if not manifest or next_phase not in manifest.phases:
            return False

        current_phase_state = manifest.phases.get(manifest.current_phase)
        if current_phase_state and current_phase_state.status != "COMPLETED":
             logger.warning(f"Cannot transition to {next_phase}: current phase {manifest.current_phase} is {current_phase_state.status}")
             return False

        phase_state = manifest.phases[next_phase]

        # Check if all dependencies are COMPLETED
        for dep in phase_state.dependencies:
            if manifest.phases[dep].status != "COMPLETED":
                logger.warning(f"Dependency {dep} for phase {next_phase} is not COMPLETED.")
                return False

        # Transition logic
        manifest.current_phase = next_phase
        phase_state.status = "IN_PROGRESS"
        phase_state.agent = agent_id
        phase_state.started_at = datetime.utcnow().isoformat()

        self.save_manifest(manifest)
        logger.info(f"Project '{project_id}' transitioned to phase '{next_phase}' by agent '{agent_id}'")
        return True

    def complete_phase(self, project_id: str, phase: str) -> None:
        """Marks a phase as COMPLETED and timestamps it."""
        manifest = self.load_manifest(project_id)
        if not manifest or phase not in manifest.phases:
            raise ValueError(f"Project {project_id} or phase {phase} not found.")

        manifest.phases[phase].status = "COMPLETED"
        manifest.phases[phase].completed_at = datetime.utcnow().isoformat()

        self.save_manifest(manifest)
        logger.info(f"Phase '{phase}' completed for project '{project_id}'")
