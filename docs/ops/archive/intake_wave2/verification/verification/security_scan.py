import os
import json
from typing import List, Dict, Any
from datetime import datetime

class SecurityScanner:
    def __init__(self, sensitive_keywords: List[str] = None):
        self.sensitive_keywords = sensitive_keywords or ["secret_key", "private_key", "token"]

    def run(self, files: List[str], evidence_dir: str) -> bool:
        """
        Scans files for sensitive keywords and generates a JSON evidence report.
        Returns True if no vulnerabilities are found, False otherwise.
        """
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, "security_scan_evidence.json")
        
        findings = []
        vulnerabilities_found = 0

        for f in files:
            if not os.path.exists(f):
                findings.append({"file": f, "finding": "File not found"})
                continue

            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as file_obj:
                    content = file_obj.read()
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for keyword in self.sensitive_keywords:
                            if keyword in line.lower():
                                findings.append({
                                    "file": f,
                                    "line": line_num,
                                    "finding": f"Found sensitive keyword: '{keyword}'"
                                })
                                vulnerabilities_found += 1
            except Exception as e:
                findings.append({"file": f, "finding": f"Error reading file: {str(e)}"})

        # Generate evidence
        exit_code = 1 if vulnerabilities_found > 0 else 0
        evidence = {
            "check_name": "security_scan",
            "command_run": "Internal scan function on specified files",
            "exit_code": exit_code,
            "timestamp": datetime.now().isoformat(),
            "details": findings
        }
        
        with open(evidence_path, "w") as f:
            json.dump(evidence, f, indent=2)
            
        return exit_code == 0

if __name__ == "__main__":
    print("Running Refactored SecurityScanner Smoke Test...")
    scanner = SecurityScanner()

    test_evidence_dir = "/home/adem/graywolf/reports/evidence/phase256_test_run"
    mock_scan_dir = "/home/adem/graywolf/verification/mock_scan_files"

    # We reuse the mock files created by previous steps
    files_to_scan = [
        os.path.join(mock_scan_dir, "clean_code.py"),
        os.path.join(mock_scan_dir, "vulnerable_code.py"),
    ]
    
    # We expect this to fail because vulnerable_code.py has secrets
    scan_successful = scanner.run(files=files_to_scan, evidence_dir=test_evidence_dir)
    
    evidence_file = os.path.join(test_evidence_dir, "security_scan_evidence.json")
    print(f"Evidence file generated at: {evidence_file}")
    
    if not scan_successful and os.path.exists(evidence_file):
        with open(evidence_file, "r") as f:
            data = json.load(f)
            print("Evidence file content:")
            print(json.dumps(data, indent=2))
            if data["exit_code"] == 1 and len(data["details"]) > 0:
                print("SecurityScanner Smoke Test PASSED ✅ (Correctly identified vulnerabilities and created evidence)")
            else:
                print("SecurityScanner Smoke Test FAILED ❌ (Evidence content is incorrect)")
                exit(1)
    else:
        print("SecurityScanner Smoke Test FAILED ❌ (Did not fail as expected or evidence file not created)")
        exit(1)
