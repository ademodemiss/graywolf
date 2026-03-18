import os
import json
import subprocess
from datetime import datetime

# Import Core Modules (Using the actual GrayWolf stack)
from core.rc_packager import RCPackager
from core.pr_bundle import PRBundleGenerator

TASK_ID = "TASK-251-README"
BRANCH_NAME = "task/TASK-251-readme-installation"
README_PATH = "README.md"
EVIDENCE_DIR = "reports/evidence/phase251"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def run_command(cmd, check=True):
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result

def main():
    print("=== Starting Phase 251: First Real End-to-End Task ===")
    
    # 1. Create Git Branch
    print("\n--- Step 1: Git Branch ---")
    # Check if branch exists, if so delete it for fresh run (idempotency)
    run_command(f"git branch -D {BRANCH_NAME}", check=False)
    run_command(f"git checkout -b {BRANCH_NAME}")
    print(f"Switched to branch: {BRANCH_NAME}")

    # 2. Modify README.md
    print("\n--- Step 2: Modify README.md ---")
    if not os.path.exists(README_PATH):
        # Create if missing (edge case)
        with open(README_PATH, "w") as f:
            f.write("# GrayWolf Project\n")
            
    with open(README_PATH, "r") as f:
        content = f.read()
        
    if "## Installation" in content:
        print("Installation section already exists. Updating...")
        # Simple replace or append logic could go here. For now, we append if missing.
    else:
        installation_text = """
## Installation

To set up GrayWolf locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/graywolf.git
    cd graywolf
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **OpenClaw Integration:**
    Ensure OpenClaw Gateway is running and connected.
"""
        with open(README_PATH, "a") as f:
            f.write(installation_text)
        print("Appended Installation section to README.md")

    # 3. Verify Changes (Diff)
    print("\n--- Step 3: Verify Changes ---")
    diff_res = run_command("git diff README.md")
    print(diff_res.stdout)
    
    if not diff_res.stdout.strip():
        print("No changes detected! Aborting.")
        return

    # 4. Commit Changes
    print("\n--- Step 4: Commit ---")
    run_command("git add README.md")
    commit_msg = f"{TASK_ID}: add Installation section to README [evidence:{TASK_ID}]"
    run_command(f"git commit -m '{commit_msg}'")
    
    # Get Commit Hash
    commit_hash = run_command("git rev-parse HEAD").stdout.strip()
    print(f"Committed with hash: {commit_hash}")

    # 5. Generate Evidence
    print("\n--- Step 5: Generate Evidence ---")
    evidence_data = {
        "task_id": TASK_ID,
        "branch": BRANCH_NAME,
        "commit_hash": commit_hash,
        "changed_files": [README_PATH],
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    
    evidence_path = os.path.join(EVIDENCE_DIR, "task_execution_evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence_data, f, indent=2)
    print(f"Evidence saved to: {evidence_path}")

    # 6. Generate PR Bundle (Using Core Module)
    print("\n--- Step 6: PR Bundle Generation ---")
    pr_gen = PRBundleGenerator(output_dir="reports")
    bundle = pr_gen.generate_bundle(
        task_id=TASK_ID,
        summary="Added Installation instructions to README.md",
        risks=["Low risk documentation change"],
        verify_steps=["Check README formatting", "Verify commands"],
        evidence_path=evidence_path
    )
    print(f"PR Bundle generated: reports/pr_bundle_{TASK_ID}.json")
    
    # 7. Generate RC Manifest (Using Core Module)
    print("\n--- Step 7: RC Manifest ---")
    rc_pack = RCPackager(output_dir="reports")
    rc_pack.generate_manifest(
        task_id=TASK_ID,
        commit_sha=commit_hash,
        evidence_files=[evidence_path],
        version="v1.0.0-rc1"
    )
    print(f"RC Manifest generated for {commit_hash}")
    
    print("\n=== Phase 251 COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        exit(1)
