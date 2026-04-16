import json
import logging
from typing import Dict, Any, Optional, List
from mcp_bridge.state_manager import ManifestManager, ProjectManifest
from mcp_bridge.manifest_tool import ManifestTool
from production.bridges.payload import BridgeManager, TTSPayload, VideoPrompt
from production.adobe.jsx_gen import AdobeBridge
from production.validation.quality import ValidationEngine

# Setup logging for the Orchestrator
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ORCHESTRATOR] - %(levelname)s - %(message)s',
    filename='/home/muhammad_tayyab/bootlogix/mcp_bridge/orchestrator.log'
)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    """
    The Brain of the system.
    Responsible for reading the workflow spec, managing the agentic manifest,
    and dispatching work to specialized agents based on SSD phases.
    """
    def __init__(self, workflow_spec_path: str):
        with open(workflow_spec_path, 'r') as f:
            self.workflow = json.load(f)

        self.validation_engine = ValidationEngine()
        self.manifest_manager = ManifestManager()
        self.manifest_tool = ManifestTool()
        self.bridge_manager = BridgeManager()
        self.adobe_bridge = AdobeBridge()

    def create_project(self, project_id: str, metadata: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Initializes a new project and returns the tool result."""
        return self.manifest_tool.init_project(project_id, metadata)

    def get_project_state(self, project_id: str) -> Dict[str, Any]:
        """Provides the current state of the project for the Brain."""
        return self.manifest_tool.get_current_state(project_id)

    def update_project_metadata(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates project metadata (e.g. from /interview)."""
        return self.manifest_tool.update_metadata(project_id, updates)

    def record_project_artifact(self, project_id: str, phase: str, key: str, content: Any) -> Dict[str, Any]:
        """Records an artifact produced by a specialist."""
        return self.manifest_tool.record_artifact(project_id, phase, key, content)

    def transition_project_phase(self, project_id: str, target_phase: str) -> Dict[str, Any]:
        """Transitions the project to the next SSD phase."""
        return self.manifest_tool.transition_to_phase(project_id, target_phase)

    def bridge_and_execute(self, project_id: str, bridge_type: str, input_artifact: str, config: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        The core agentic loop: Read Artifact -> Transform via Bridge -> Execute Skill.
        """
        # 1. Retrieve artifact from manifest
        manifest = self.manifest_manager.load_manifest(project_id)
        if not manifest:
            return {"status": "error", "message": "Project manifest not found."}

        # Find the artifact path across all phases
        artifact_path = None
        for phase in manifest.phases.values():
            if input_artifact in phase.artifacts:
                artifact_path = phase.artifacts[input_artifact]
                break

        if not artifact_path:
            return {"status": "error", "message": f"Artifact {input_artifact} not found in manifest."}

        # 2. Transform using the BridgeManager
        try:
            if bridge_type == "TTS":
                with open(artifact_path, 'r') as f:
                    content = f.read()
                payload = self.bridge_manager.prepare_tts_payload(content, config)
            elif bridge_type == "VIDEO":
                with open(artifact_path, 'r') as f:
                    content = f.read()
                payload = self.bridge_manager.prepare_video_prompts(content, config)
            elif bridge_type == "REMOTION":
                # Remotion bridge requires a list of paths
                payload = self.bridge_manager.generate_remotion_metadata(
                    project_id,
                    config.get('audio_paths', []),
                    config.get('video_paths', []),
                    config.get('fps', 30)
                )
            else:
                return {"status": "error", "message": f"Unsupported bridge type: {bridge_type}"}
        except Exception as e:
            return {"status": "error", "message": f"Bridge transformation failed: {str(e)}"}

        # 3. Execute Skill (Simulated)
        logger.info(f"Executing {bridge_type} skill with payload: {payload}")
        simulated_result_path = f"/tmp/{project_id}_{bridge_type}_output.wav" if bridge_type == "TTS" else f"/tmp/{project_id}_{bridge_type}_output.mp4"

        with open(simulated_result_path, 'w') as f:
            f.write("SIMULATED OUTPUT")

        # 4. Record the new artifact back to the manifest
        phase_map = {"TTS": "GENERATE", "VIDEO": "GENERATE", "REMOTION": "GENERATE"}
        target_phase = phase_map.get(bridge_type, "GENERATE")

        self.manifest_tool.record_artifact(project_id, target_phase, f"{bridge_type}_output", simulated_result_path)

        return {
            "status": "success",
            "artifact_path": simulated_result_path,
            "payload": payload
        }

    def run_qa_cycle(self, project_id: str, qa_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates the QA loop by processing a QAAgent report and triggering re-generations.
        """
        if not qa_report or not isinstance(qa_report, dict):
            return {"status": "error", "message": "Invalid QA report format."}

        overall_pass = qa_report.get("overall_pass", False)
        failed_scenes = qa_report.get("failed_scenes", [])

        if overall_pass:
            logger.info(f"Project {project_id} passed QA cycle.")
            return {"status": "success", "message": "Project passed QA."}

        # Process failed scenes
        reset_count = 0
        for failure in failed_scenes:
            scene_id = failure.get("scene_id")
            issue = failure.get("issue")
            severity = failure.get("severity")

            if not scene_id: continue

            # We assume the artifact key is based on scene_id (e.g. 'scene_2_video')
            artifact_key = f"scene_{scene_id}_video"

            # Call ManifestTool to surgically reset the artifact
            res = self.manifest_tool.reset_artifact_status(project_id, "GENERATE", artifact_key, feedback=issue)

            if res['status'] == 'success':
                reset_count += 1
                logger.info(f"Surgically reset {artifact_key} due to: {issue}")

        if reset_count > 0:
            return {
                "status": "retry_triggered",
                "reset_artifacts": reset_count,
                "message": f"Triggered re-generation for {reset_count} scenes."
            }

        return {"status": "error", "message": "QA report indicated failure but no artifacts were reset."}

    def execute_adobe_command(self, app: str, jsx_code: str, script_name: str = "cmd.jsx") -> Dict[str, Any]:
        """
        Sends an ExtendScript command to Adobe Premiere or After Effects via the AdobeBridge.
        """
        try:
            file_path = self.adobe_bridge.execute_jsx(app, jsx_code, script_name)
            return {
                "status": "success",
                "script_path": file_path,
                "message": f"Command successfully delivered to {app} drop-zone."
            }
        except Exception as e:
            logger.error(f"Adobe Bridge execution failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def run_pipeline(self, project_id: str) -> Dict[str, Any]:
        """
        Executes the full SSD pipeline for a project.
        Iterates through phases, executes each via bridge_and_execute(), and transitions on success.
        """
        logger.info(f"Starting pipeline for project: {project_id}")

        manifest = self.manifest_manager.load_manifest(project_id)
        if not manifest:
            return {"status": "error", "message": f"Project {project_id} not found."}

        phase_order = ["SEARCH", "SCRIPT", "DESIGN", "GENERATE"]
        results = {}

        for phase_name in phase_order:
            if phase_name not in manifest.phases:
                logger.warning(f"Phase {phase_name} not in manifest, skipping.")
                continue

            phase_state = manifest.phases[phase_name]
            if phase_state.status == "COMPLETED":
                logger.info(f"Phase {phase_name} already complete, skipping.")
                continue

            logger.info(f"Executing phase: {phase_name}")

            # Get phase config for required artifacts
            phase_config = self._get_phase_config(phase_name)
            required_artifacts = phase_config.get("required_artifacts", []) if phase_config else []

            # Determine bridge type for this phase
            bridge_type = self._get_bridge_type_for_phase(phase_name)

            # Execute the phase
            if bridge_type:
                result = self.bridge_and_execute(
                    project_id,
                    bridge_type,
                    f"{phase_name.lower()}_input",
                    {"phase": phase_name}
                )
            else:
                # Phases without bridge execution (e.g., DESIGN outputs storyboard)
                result = {"status": "success"}

            if result.get("status") == "success":
                self.manifest_manager.complete_phase(project_id, phase_name)
                results[phase_name] = {"status": "completed", "artifacts": result}
                logger.info(f"Phase {phase_name} completed successfully.")
            else:
                results[phase_name] = {"status": "failed", "error": result.get("message")}
                logger.error(f"Phase {phase_name} failed: {result.get('message')}")
                return {
                    "status": "failed",
                    "phase": phase_name,
                    "results": results
                }

        # Load final manifest state
        final_manifest = self.manifest_manager.load_manifest(project_id)
        return {
            "status": "completed",
            "project_id": project_id,
            "results": results,
            "artifacts": final_manifest.phases["GENERATE"].artifacts if "GENERATE" in final_manifest.phases else {}
        }

    def _get_bridge_type_for_phase(self, phase_name: str) -> Optional[str]:
        """Maps SSD phases to their corresponding bridge type."""
        bridge_map = {
            "SEARCH": None,      # No bridge - research is manual/LLM-driven
            "SCRIPT": "TTS",     # Script generates TTS payload
            "DESIGN": "VIDEO",    # Design generates video prompts
            "GENERATE": "REMOTION"  # Generate uses Remotion bridge
        }
        return bridge_map.get(phase_name)

    def _get_phase_config(self, phase_name: str) -> Optional[Dict]:
        # Aligns with the updated workflow_spec.json structure
        for phase in self.workflow.get('ssd_phases', []):
            if phase['name'] == phase_name:
                return phase
        return None
