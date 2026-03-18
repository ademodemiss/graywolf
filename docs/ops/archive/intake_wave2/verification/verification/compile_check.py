import py_compile
import os
import json
from typing import List, Dict, Any
from datetime import datetime

class CompileCheck:
    def run(self, files: List[str], evidence_dir: str) -> bool:
        """
        Checks Python syntax for a list of files and generates a JSON evidence report.
        """
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, "compile_check_evidence.json")
        
        all_success = True
        evidence_records = []

        for file_path in files:
            command_run = f"python3 -m py_compile {file_path}"
            record = {
                "check_name": "compile_check",
                "command_run": command_run,
                "timestamp": datetime.now().isoformat(),
                "file": file_path,
            }
            try:
                py_compile.compile(file_path, doraise=True)
                record["status"] = "success"
                record["exit_code"] = 0
                record["details"] = "Compilation successful."
            except py_compile.PyCompileError as e:
                all_success = False
                record["status"] = "failed"
                record["exit_code"] = 1 # Convention for failure
                record["details"] = str(e)

            evidence_records.append(record)
            
        # Write the evidence file
        with open(evidence_path, "w") as f:
            json.dump(evidence_records, f, indent=2)
            
        return all_success

if __name__ == "__main__":
    # This smoke test demonstrates the new functionality
    print("Running Refactored CompileCheck Smoke Test...")
    checker = CompileCheck()
    
    # Define a dedicated directory for test evidence
    test_evidence_dir = "/home/adem/graywolf/reports/evidence/phase256_test_run"
    if os.path.exists(test_evidence_dir):
        # Clean up old test files
        for f in os.listdir(test_evidence_dir):
            os.remove(os.path.join(test_evidence_dir, f))
    
    # Create mock files for testing
    mock_files_dir = "/home/adem/graywolf/verification/mock_compile_files"
    os.makedirs(mock_files_dir, exist_ok=True)
    good_file = os.path.join(mock_files_dir, "good.py")
    bad_file = os.path.join(mock_files_dir, "bad.py")

    with open(good_file, "w") as f:
        f.write("print('hello')\n")
    with open(bad_file, "w") as f:
        f.write("print('hello'\n") # Syntax error
    
    test_files_to_check = [good_file, bad_file]
    
    # Run the check
    overall_success = checker.run(files=test_files_to_check, evidence_dir=test_evidence_dir)
    
    # Verify the outcome
    evidence_file = os.path.join(test_evidence_dir, "compile_check_evidence.json")
    print(f"Evidence file generated at: {evidence_file}")

    if not overall_success and os.path.exists(evidence_file):
        with open(evidence_file, "r") as f:
            data = json.load(f)
            print("Evidence file content:")
            print(json.dumps(data, indent=2))
            if len(data) == 2 and data[1]["status"] == "failed":
                 print("CompileCheck Smoke Test PASSED ✅ (Correctly identified failure and created evidence)")
            else:
                print("CompileCheck Smoke Test FAILED ❌ (Evidence content is incorrect)")
                exit(1)
    else:
        print("CompileCheck Smoke Test FAILED ❌ (Did not fail as expected or evidence file not created)")
        exit(1)
