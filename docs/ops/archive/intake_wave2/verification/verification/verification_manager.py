import os
import glob
import json
from datetime import datetime
from typing import Dict, Any

# Import the refactored checker classes
from verification.compile_check import CompileCheck
from verification.test_runner import TestRunner
from verification.security_scan import SecurityScanner

class VerificationManager:
    def run_all(self, target_dir: str, evidence_dir: str) -> bool:
        """
        Runs a full verification pipeline (compile, test, security) on a target directory,
        generating individual evidence files and a final unified report.
        """
        print(f"--- Running Verification Pipeline on '{target_dir}' ---")
        os.makedirs(evidence_dir, exist_ok=True)
        
        # 1. Discover target files
        all_py_files = glob.glob(os.path.join(target_dir, "**/*.py"), recursive=True)
        test_dir = target_dir # Assuming tests are within the target directory
        
        if not all_py_files:
            print("No Python files found to verify.")
            return True # Nothing to check, so technically it's a success

        # 2. Instantiate checkers
        compile_checker = CompileCheck()
        test_runner = TestRunner()
        security_scanner = SecurityScanner()

        # 3. Run individual checks, which will generate their own evidence
        print("\n[1/3] Running Compile Check...")
        compile_ok = compile_checker.run(files=all_py_files, evidence_dir=evidence_dir)
        print(f"Compile Check Status: {'PASSED' if compile_ok else 'FAILED'}")

        print("\n[2/3] Running Test Runner...")
        tests_ok = test_runner.run(test_dir=test_dir, evidence_dir=evidence_dir)
        print(f"Test Runner Status: {'PASSED' if tests_ok else 'FAILED'}")

        print("\n[3/3] Running Security Scan...")
        security_ok = security_scanner.run(files=all_py_files, evidence_dir=evidence_dir)
        print(f"Security Scan Status: {'PASSED' if security_ok else 'FAILED'}")

        # 4. Generate Unified Report
        overall_status = "passed" if all([compile_ok, tests_ok, security_ok]) else "failed"
        
        unified_report = {
            "check_name": "unified_verification_report",
            "timestamp": datetime.now().isoformat(),
            "target_directory": target_dir,
            "overall_status": overall_status,
            "summary": {
                "compile_check": "passed" if compile_ok else "failed",
                "test_runner": "passed" if tests_ok else "failed",
                "security_scan": "passed" if security_ok else "failed"
            },
            "evidence_files": [
                os.path.join(evidence_dir, "compile_check_evidence.json"),
                os.path.join(evidence_dir, "test_runner_evidence.json"),
                os.path.join(evidence_dir, "security_scan_evidence.json")
            ]
        }
        
        report_path = os.path.join(evidence_dir, "unified_verification_report.json")
        with open(report_path, "w") as f:
            json.dump(unified_report, f, indent=2)
        print(f"\n--- Unified Verification Report generated at: {report_path} ---")
        
        return overall_status == "passed"

if __name__ == "__main__":
    print("--- Starting Phase 256 Verification Manager End-to-End Test ---")
    manager = VerificationManager()
    
    # Define the official evidence directory for the phase
    final_evidence_dir = "/home/adem/graywolf/reports/evidence/phase256"
    
    # For this test, we'll run the pipeline on the 'multi_agent' directory
    # as it has code and tests, but likely no sensitive keywords.
    # We expect tests to fail, as we created a failing test case earlier.
    target_code_dir = "/home/adem/graywolf/multi_agent"
    
    # Clean up old evidence
    if os.path.exists(final_evidence_dir):
        import shutil
        shutil.rmtree(final_evidence_dir)
    os.makedirs(final_evidence_dir)

    # Run the full pipeline
    is_fully_verified = manager.run_all(target_dir=target_code_dir, evidence_dir=final_evidence_dir)
    
    print(f"\n>>> Overall Pipeline Verification Status: {'VERIFIED' if is_fully_verified else 'FAILED'}")
    
    # Verification of the test itself
    report_file = os.path.join(final_evidence_dir, "unified_verification_report.json")
    if os.path.exists(report_file):
        print(f"Final Report '{report_file}' was created successfully.")
        with open(report_file, 'r') as f:
            report_data = json.load(f)
            # We expect success because there are no real tests in multi_agent dir
            if report_data['overall_status'] == 'passed':
                print("E2E Test PASSED ✅")
            else:
                print("E2E Test FAILED ❌ (Expected overall status to be 'passed' as there are no failing tests in the target dir)")
                exit(1)
    else:
        print(f"E2E Test FAILED ❌ (Final report was not created.)")
        exit(1)
