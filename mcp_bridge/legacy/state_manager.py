import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class PhaseState:
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    agent: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class ProjectManifest:
    project_id: str
    version: str = "2.0"
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    current_phase: str = "SEARCH"
    phases: Dict[str, PhaseState] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ManifestManager:
    """
    Handles the persistence of agentic project manifests to disk.
    Supports the SSD (Search -> Script -> Design -> Generate) pipeline.
    """
    def __init__(self, storage_path: str = "/home/muhammad_tayyab/bootlogix/projects/manifests/"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_file_path(self, project_id: str) -> str:
        return os.path.join(self.storage_path, f"{project_id}.json")

    def create_manifest(self, project_id: str, metadata: Dict[str, Any]) -> ProjectManifest:
        """Initializes a new SSD project manifest."""
        phases = {
            "SEARCH": PhaseState(status="PENDING", dependencies=[]),
            "SCRIPT": PhaseState(status="PENDING", dependencies=["SEARCH"]),
            "DESIGN": PhaseState(status="PENDING", dependencies=["SCRIPT"]),
            "GENERATE": PhaseState(status="PENDING", dependencies=["SCRIPT", "DESIGN"]),
        }

        manifest = ProjectManifest(
            project_id=project_id,
            status="IN_PROGRESS",
            current_phase="SEARCH",
            phases=phases,
            metadata=metadata
        )

        # Mark first phase as in progress
        manifest.phases["SEARCH"].status = "IN_PROGRESS"

        self.save_manifest(manifest)
        return manifest

    def save_manifest(self, manifest: ProjectManifest) -> None:
        """Saves the manifest to disk."""
        file_path = self._get_file_path(manifest.project_id)
        # Use a helper to convert nested dataclasses to dict
        def custom_asdict(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {k: custom_asdict(v) for k, v in asdict(obj).items()}
            return obj

        # Simplified approach for the purpose of this implementation
        # asdict() already handles nested dataclasses
        with open(file_path, 'w') as f:
            json.dump(asdict(manifest), f, indent=2)

    def load_manifest(self, project_id: str) -> Optional[ProjectManifest]:
        """Reads the current manifest from disk."""
        file_path = self._get_file_path(project_id)
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

            # Manually reconstruct PhaseState objects from dicts
            phases_data = data.pop('phases', {})
            phases = {k: PhaseState(**v) for k, v in phases_data.items()}

            return ProjectManifest(phases=phases, **data)

    def update_artifact(self, project_id: str, phase: str, artifact_key: str, path: Any) -> None:
        """Atomically updates a specific artifact path within a phase."""
        manifest = self.load_manifest(project_id)
        if not manifest or phase not in manifest.phases:
            raise ValueError(f"Project {project_id} or phase {phase} not found.")

        manifest.phases[phase].artifacts[artifact_key] = path
        self.save_manifest(manifest)

    def transition_phase(self, project_id: str, next_phase: str, agent_id: str) -> bool:
        """
        Moves the project to the next phase if dependencies are met.
        """
        manifest = self.load_manifest(project_id)
        if not manifest or next_phase not in manifest.phases:
            return False

        phase_state = manifest.phases[next_phase]

        # Check if all dependencies are COMPLETED
        for dep in phase_state.dependencies:
            if manifest.phases[dep].status != "COMPLETED":
                return False

        # Transition logic
        manifest.current_phase = next_phase
        phase_state.status = "IN_PROGRESS"
        phase_state.agent = agent_id
        phase_state.started_at = datetime.utcnow().isoformat()

        self.save_manifest(manifest)
        return True

    def complete_phase(self, project_id: str, phase: str) -> None:
        """Marks a phase as COMPLETED and timestamps it."""
        manifest = self.load_manifest(project_id)
        if not manifest or phase not in manifest.phases:
            raise ValueError(f"Project {project_id} or phase {phase} not found.")

        manifest.phases[phase].status = "COMPLETED"
        manifest.phases[phase].completed_at = datetime.utcnow().isoformat()

        self.save_manifest(manifest)
