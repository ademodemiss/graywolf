
import os
import sys
import json

# Ensure GrayWolf root is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir # Assuming this script is at /home/adem/graywolf/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from verification.verification_manager import VerificationManager
from verification.test_runner import TestRunner # To create mock test files if needed
from verification.security_scan import SecurityScanner # To create mock scan files if needed

def setup_mock_files():
    # Setup mock test files for TestRunner
    test_dir = os.path.join(project_root, "verification", "mock_tests")
    os.makedirs(test_dir, exist_ok=True)
    
    with open(os.path.join(test_dir, "test_passing.py"), "w") as f:
        f.write("import sys\nprint('PASSED')\nsys.exit(0)")
        
    with open(os.path.join(test_dir, "test_failing.py"), "w") as f:
        f.write("import sys\nprint('FAILED')\nsys.exit(1)")
        
    # Setup mock scan files for SecurityScanner
    mock_scan_dir = os.path.join(project_root, "verification", "mock_scan_files")
    os.makedirs(mock_scan_dir, exist_ok=True)
    
    with open(os.path.join(mock_scan_dir, "clean_code.py"), "w") as f:
        f.write("def hello():\n    print('Hello World')")
        
    with open(os.path.join(mock_scan_dir, "vulnerable_code.py"), "w") as f:
        f.write("API_KEY = \'my_super_secret_api_key\'\ndef connect():\n    passwords = \'root123\'")
        
    with open(os.path.join(mock_scan_dir, "another_clean.py"), "w") as f:
        f.write("config = {\'debug\': True}")

def run_verification_pipeline_test():
    setup_mock_files()
    
    manager = VerificationManager(output_dir=os.path.join(project_root, "reports", "evidence", "phase256"))
    
    files_to_check = [
        os.path.join(project_root, "core", "autonomous_loop.py"),
        os.path.join(project_root, "verification", "mock_tests", "test_passing.py"),
        os.path.join(project_root, "verification", "mock_tests", "test_failing.py"),
        os.path.join(project_root, "verification", "mock_scan_files", "vulnerable_code.py"),
        os.path.join(project_root, "verification", "mock_scan_files", "clean_code.py")
    ]
    
    print("--- Running Phase 256 Verification Pipeline Test ---")
    results = manager.run_checks(files_to_check)
    print(json.dumps(results, indent=2))

    # Determine final status for the overall test of Phase 256
    overall_test_status = "FAILED"
    # Expected: syntax passed for valid files, one test passed, one test failed, one scan vulnerable, one clean
    if (results["checks"]["syntax"]["status"] == "passed" and 
        results["checks"]["tests"]["status"] == "failed" and # Because test_failing.py is present
        results["checks"]["security"]["status"] == "failed" and # Because vulnerable_code.py is present
        results["status"] == "failed"): # Overall status should be failed due to test/security failures
        overall_test_status = "VERIFIED"
    
    if overall_test_status == "VERIFIED":
        print("Phase 256 Verification Test PASSED ✅")
    else:
        print("Phase 256 Verification Test FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    run_verification_pipeline_test()
