import subprocess
import os
import json
from typing import Dict, Any
from datetime import datetime

class TestRunner:
    def run(self, test_dir: str, evidence_dir: str) -> bool:
        """
        Discovers and runs tests in a directory using unittest, and generates a JSON evidence report.
        """
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, "test_runner_evidence.json")
        
        command_run = f"python3 -m unittest discover -s {test_dir}"
        
        try:
            process = subprocess.run(
                command_run.split(),
                capture_output=True,
                text=True,
                check=False, # We handle the exit code manually
                cwd=os.path.dirname(os.path.dirname(test_dir)) # Run from project root for better discovery
            )
            
            exit_code = process.returncode
            # unittest prints to stderr for both success and failure, so we combine them.
            output_details = f"--- STDOUT ---\n{process.stdout}\n--- STDERR ---\n{process.stderr}"

        except Exception as e:
            exit_code = -1
            output_details = f"Failed to execute test runner: {str(e)}"

        # Generate evidence
        evidence = {
            "check_name": "test_runner",
            "command_run": command_run,
            "exit_code": exit_code,
            "timestamp": datetime.now().isoformat(),
            "details": output_details
        }
        
        with open(evidence_path, "w") as f:
            json.dump(evidence, f, indent=2)
            
        return exit_code == 0

if __name__ == "__main__":
    print("Running Refactored TestRunner Smoke Test...")
    runner = TestRunner()

    test_evidence_dir = "/home/adem/graywolf/reports/evidence/phase256_test_run"
    mock_test_dir = "/home/adem/graywolf/verification/mock_tests_refactored"

    # Clean up and create mock test files with unittest framework
    if os.path.exists(mock_test_dir):
        import shutil
        shutil.rmtree(mock_test_dir)
    os.makedirs(mock_test_dir)
    
    with open(os.path.join(mock_test_dir, "test_success.py"), "w") as f:
        f.write("import unittest\n\nclass SuccessTest(unittest.TestCase):\n    def test_pass(self):\n        self.assertEqual(1, 1)\n")

    with open(os.path.join(mock_test_dir, "test_failure.py"), "w") as f:
        f.write("import unittest\n\nclass FailureTest(unittest.TestCase):\n    def test_fail(self):\n        self.assertEqual(1, 0) # This will fail\n")

    # Run the test discovery
    # We expect this to fail because one of the tests will fail
    overall_success = runner.run(test_dir=mock_test_dir, evidence_dir=test_evidence_dir)
    
    evidence_file = os.path.join(test_evidence_dir, "test_runner_evidence.json")
    print(f"Evidence file generated at: {evidence_file}")
    
    if not overall_success and os.path.exists(evidence_file):
        with open(evidence_file, "r") as f:
            data = json.load(f)
            print("Evidence file content:")
            print(json.dumps(data, indent=2))
            if data["exit_code"] != 0 and "FAILED" in data["details"]:
                print("TestRunner Smoke Test PASSED ✅ (Correctly identified test failure and created evidence)")
            else:
                print("TestRunner Smoke Test FAILED ❌ (Evidence content is incorrect)")
                exit(1)
    else:
        print("TestRunner Smoke Test FAILED ❌ (Did not fail as expected or evidence file not created)")
        exit(1)
