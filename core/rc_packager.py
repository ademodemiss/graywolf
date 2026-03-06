import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Any

class RCPackager:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_manifest(self, task_id: str, commit_sha: str, evidence_files: List[str], version: str) -> Dict[str, Any]:
        manifest = {
            "task_id": task_id,
            "version": version,
            "commit_sha": commit_sha,
            "timestamp": datetime.now().isoformat(),
            "artifacts": [],
            "integrity_status": "ok"
        }

        for file_path in evidence_files:
            if not os.path.exists(file_path):
                manifest["integrity_status"] = "failed"
                manifest["error"] = f"Missing artifact: {file_path}"
                return manifest
            
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            manifest["artifacts"].append({
                "path": file_path,
                "sha256": file_hash
            })
        
        manifest_path = os.path.join(self.output_dir, f"rc_manifest_{task_id}_{version}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        return manifest

if __name__ == "__main__":
    # Smoke test for RCPackager
    print("Starting RCPackager Smoke Test...")
    
    # Create dummy artifacts
    dummy_artifact = "reports/dummy_evidence.json"
    with open(dummy_artifact, "w") as f:
        json.dump({"test": "data"}, f)
        
    packager = RCPackager()
    result = packager.generate_manifest(
        task_id="TASK-SMOKE-245",
        commit_sha="a1b2c3d4",
        evidence_files=[dummy_artifact],
        version="1.0.0-rc1"
    )
    
    print(f"Manifest Result: {json.dumps(result, indent=2)}")
    
    # Verify result
    if result["integrity_status"] == "ok" and len(result["artifacts"]) == 1:
        print("Smoke Test PASSED ✅")
        
        # Generate official report
        report = {
            "phase": 245,
            "status": "completed",
            "module": "core/rc_packager.py",
            "manifest_sample": result,
            "timestamp": datetime.now().isoformat()
        }
        with open("reports/release_candidate_packager_report.json", "w") as f:
            json.dump(report, f, indent=2)
    else:
        print("Smoke Test FAILED ❌")
        exit(1)
