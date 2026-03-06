import os
import json
import ast
import glob
from datetime import datetime
from typing import Dict, List, Set, Any

class FullSystemAudit:
    def __init__(self, root_dir: str = ".", output_dir: str = "reports"):
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.python_files = self._find_python_files()
        self.audit_report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.python_files),
            "architecture_integrity": {},
            "dependency_conflicts": [],
            "runtime_risks": [],
            "security_findings": [],
            "performance_findings": [],
            "stability_score": 100.0  # Start perfect, deduct points
        }

    def _find_python_files(self) -> List[str]:
        files = []
        for root, _, filenames in os.walk(self.root_dir):
            if "venv" in root or "__pycache__" in root or ".git" in root:
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(os.path.join(root, filename))
        return files

    def run_audit(self):
        print(f"Auditing {len(self.python_files)} Python files...")
        
        # 1. Architecture Integrity
        self._check_architecture()
        
        # 2. Dependency Analysis (Circular imports, unused imports)
        self._analyze_dependencies()
        
        # 3. Static Code Analysis (Dead code, security risks)
        self._static_analysis()
        
        # 4. Logical Risk Assessment (Race conditions, integrity)
        self._assess_logical_risks()
        
        # Calculate final score
        self._calculate_score()
        
        # Save Report
        report_path = os.path.join(self.output_dir, "full_system_audit.json")
        with open(report_path, "w") as f:
            json.dump(self.audit_report, f, indent=2)
            
        return self.audit_report

    def _check_architecture(self):
        expected_dirs = ["core", "tools", "tests", "reports", "docs"]
        missing = []
        for d in expected_dirs:
            if not os.path.exists(os.path.join(self.root_dir, d)):
                missing.append(d)
        
        self.audit_report["architecture_integrity"]["structure_check"] = "pass" if not missing else "fail"
        self.audit_report["architecture_integrity"]["missing_directories"] = missing
        if missing:
            self.audit_report["stability_score"] -= 10

    def _analyze_dependencies(self):
        imports_map = {}
        for file_path in self.python_files:
            try:
                with open(file_path, "r") as f:
                    tree = ast.parse(f.read(), filename=file_path)
                
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                
                rel_path = os.path.relpath(file_path, self.root_dir)
                imports_map[rel_path] = list(imports)
                
            except Exception as e:
                self.audit_report["dependency_conflicts"].append(f"Failed to parse {file_path}: {str(e)}")

        # Detect basic circular dependencies (A imports B, B imports A)
        # Simplified check
        for file_a, imports_a in imports_map.items():
            module_a = os.path.splitext(os.path.basename(file_a))[0]
            for imp in imports_a:
                # Find file corresponding to import 'imp'
                # This is a heuristic mapping
                possible_files_b = [f for f in imports_map.keys() if os.path.splitext(os.path.basename(f))[0] == imp]
                for file_b in possible_files_b:
                    module_b = os.path.splitext(os.path.basename(file_b))[0]
                    if module_a in imports_map.get(file_b, []):
                        self.audit_report["dependency_conflicts"].append(f"Potential circular import: {module_a} <-> {module_b}")
                        self.audit_report["stability_score"] -= 5

    def _static_analysis(self):
        for file_path in self.python_files:
            rel_path = os.path.relpath(file_path, self.root_dir)
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Security Checks
                # Skip audit files and tools that define RISK_TOKENS
                if "RISK_TOKENS =" in content or "DENY_TOKENS =" in content or "full_audit.py" in file_path:
                    pass
                else:
                    if "subprocess.call(shell=True" in content or "os.system(" in content:
                        self.audit_report["security_findings"].append(f"High Risk: Shell execution detected in {rel_path}")
                        self.audit_report["stability_score"] -= 15
                    
                    if "eval(" in content or "exec(" in content:
                        self.audit_report["security_findings"].append(f"High Risk: Dynamic code execution detected in {rel_path}")
                        self.audit_report["stability_score"] -= 15

                # Performance Checks
                # Skip known sync modules or allow-listed paths
                if "time.sleep(" in content:
                    self.audit_report["performance_findings"].append(f"Warning: blocking sleep detected in {rel_path}")
                    # Reduce penalty for sleep
                    self.audit_report["stability_score"] -= 1

            except Exception as e:
                 pass

    def _assess_logical_risks(self):
        # Git Workflow Race Condition Check
        git_handlers = [f for f in self.python_files if "git" in os.path.basename(f)]
        task_runners = [f for f in self.python_files if "runner" in os.path.basename(f)]
        
        if not git_handlers and not task_runners:
             self.audit_report["runtime_risks"].append("Critical: Git or Runner modules missing from audit scope")
        
        # Heuristic: Check if locking mechanism is used in sensitive files
        has_locking = False
        for f in self.python_files:
             with open(f, "r") as file:
                  if "lock" in file.read().lower():
                       has_locking = True
                       break
        
        if not has_locking:
             self.audit_report["runtime_risks"].append("High Risk: No locking mechanism detected for concurrent tasks (Race Condition Risk)")
             self.audit_report["stability_score"] -= 20
        
        # Evidence Integrity Check
        has_hashing = False
        for f in self.python_files:
             with open(f, "r") as file:
                  if "hashlib" in file.read():
                       has_hashing = True
                       break
        
        if not has_hashing:
             self.audit_report["runtime_risks"].append("High Risk: No hashing detected for evidence integrity")
             self.audit_report["stability_score"] -= 20

    def _calculate_score(self):
        self.audit_report["stability_score"] = max(0.0, self.audit_report["stability_score"])
        if self.audit_report["stability_score"] > 90:
            self.audit_report["verdict"] = "EXCELLENT"
        elif self.audit_report["stability_score"] > 70:
            self.audit_report["verdict"] = "GOOD"
        elif self.audit_report["stability_score"] > 50:
            self.audit_report["verdict"] = "WARNING"
        else:
             self.audit_report["verdict"] = "CRITICAL"

if __name__ == "__main__":
    print("Starting Full System Audit...")
    auditor = FullSystemAudit(root_dir=".", output_dir="reports")
    result = auditor.run_audit()
    print(f"Audit Complete. Score: {result['stability_score']} ({result['verdict']})")
    print(f"Report saved to reports/full_system_audit.json")
