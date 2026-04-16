import os
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from mcp_bridge.state_manager import ManifestManager, ProjectManifest, PhaseState

# --- Pydantic Models for Type-Safe Hand-offs ---

class ProjectMetadata(BaseModel):
    target_platform: str = "YouTube Shorts"
    aspect_ratio: str = "9:16"
    target_duration: int = 60
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    goals: List[str] = Field(default_factory=list)

class Artifact(BaseModel):
    key: str
    content: Any
    timestamp: str = Field(default_factory=lambda: os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip())

# --- ManifestTool Implementation ---

class ManifestTool:
    """
    The high-level tool interface for the SSD Orchestrator (The Brain).
    Wraps ManifestManager to provide atomic, project-centric operations.
    """
    def __init__(self, storage_path: str = "/home/muhammad_tayyab/bootlogix/projects/manifests/"):
        self.manager = ManifestManager(storage_path=storage_path)

    def init_project(self, project_id: str, metadata: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Initializes a new SSD project manifest."""
        manifest = self.manager.create_manifest(project_id, metadata)
        return {
            "status": "success",
            "project_id": project_id,
            "current_phase": manifest.current_phase,
            "phases": list(manifest.phases.keys())
        }

    def get_current_state(self, project_id: str) -> Dict[str, Any]:
        """Returns the current state of the project manifest."""
        manifest = self.manager.load_manifest(project_id)
        if not manifest:
            return {"status": "error", "message": f"Project {project_id} not found."}

        return {
            "status": "success",
            "project_id": manifest.project_id,
            "current_phase": manifest.current_phase,
            "overall_status": manifest.status,
            "phase_details": {
                phase: {
                    "status": state.status,
                    "artifacts": state.artifacts,
                    "agent": state.agent
                }
                for phase, state in manifest.phases.items()
            },
            "metadata": manifest.metadata
        }

    def update_metadata(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merges new metadata (e.g., from an interview) into the project profile."""
        manifest = self.manager.load_manifest(project_id)
        if not manifest:
            return {"status": "error", "message": f"Project {project_id} not found."}

        manifest.metadata.update(updates)
        self.manager.save_manifest(manifest)
        return {"status": "success", "updated_metadata": manifest.metadata}

    def record_artifact(self, project_id: str, phase: str, key: str, content: Any) -> Dict[str, Any]:
        """Stores a produced JSON artifact or file path in the manifest."""
        try:
            self.manager.update_artifact(project_id, phase, key, content)
            return {"status": "success", "artifact": key, "phase": phase}
        except ValueError as e:
            return {"status": "error", "message": str(e)}

    def transition_to_phase(self, project_id: str, target_phase: str) -> Dict[str, Any]:
        """
        Validates prerequisites and transitions the project to the target phase.
        The target_phase should be the next one in the SSD sequence.
        """
        # The agent_id is typically the one requesting the transition
        # For now, we'll use a generic 'Orchestrator' ID or the current agent
        success = self.manager.transition_phase(project_id, target_phase, "SSD_Orchestrator")

        if success:
            return {
                "status": "success",
                "new_phase": target_phase,
                "message": f"Project {project_id} transitioned to {target_phase}."
            }
        else:
            # Identify why it failed (which dependency is missing)
            manifest = self.manager.load_manifest(project_id)
            phase_state = manifest.phases[target_phase]
            missing = [dep for dep in phase_state.dependencies if manifest.phases[dep].status != "COMPLETED"]

            return {
                "status": "error",
                "message": f"Cannot transition to {target_phase}. Missing completed dependencies: {missing}"
            }

    def validate_phase_completion(self, project_id: str, phase: str, required_keys: List[str]) -> Dict[str, Any]:
        """Checks if all mandatory artifacts for a phase are present."""
        manifest = self.manager.load_manifest(project_id)
        if not manifest or phase not in manifest.phases:
            return {"status": "error", "message": "Project or phase not found."}

        artifacts = manifest.phases[phase].artifacts
        missing = [key for key in required_keys if key not in artifacts or not artifacts[key]]

        if not missing:
            return {"status": "success", "message": f"Phase {phase} is complete."}
        else:
            return {"status": "incomplete", "missing_artifacts": missing}

    def reset_artifact_status(self, project_id: str, phase: str, artifact_key: str, feedback: str = "") -> Dict[str, Any]:
        """
        Surgically resets a specific artifact for re-generation.
        Increments retry count and stores QA feedback.
        """
        manifest = self.manager.load_manifest(project_id)
        if not manifest or phase not in manifest.phases:
            return {"status": "error", "message": "Project or phase not found."}

        phase_state = manifest.phases[phase]

        # 1. Remove the failing artifact
        if artifact_key in phase_state.artifacts:
            del phase_state.artifacts[artifact_key]

        # 2. Mark phase as IN_PROGRESS again
        phase_state.status = "IN_PROGRESS"

        # 3. Update retry tracking
        if "retry_counts" not in manifest.metadata:
            manifest.metadata["retry_counts"] = {}

        retry_key = f"{phase}_{artifact_key}"
        current_retries = manifest.metadata["retry_counts"].get(retry_key, 0)
        manifest.metadata["retry_counts"][retry_key] = current_retries + 1

        # 4. Store feedback for the ProductionAgent
        if "qa_feedback" not in manifest.metadata:
            manifest.metadata["qa_feedback"] = {}

        manifest.metadata["qa_feedback"][retry_key] = feedback

        self.manager.save_manifest(manifest)

        return {
            "status": "success",
            "retries": manifest.metadata["retry_counts"][retry_key],
            "message": f"Artifact {artifact_key} reset for re-generation."
        }