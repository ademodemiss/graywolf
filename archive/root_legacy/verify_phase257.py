
import os
import sys
import json
import glob

# Ensure GrayWolf root is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir # Assuming this script is at /home/adem/graywolf/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from memory.lesson_manager import LessonManager

def run_memory_lessons_test():
    # Define output directory for evidence within phase257
    evidence_output_dir = os.path.join(project_root, "reports", "evidence", "phase257", "memory")
    manager = LessonManager(memory_dir=evidence_output_dir)

    # Clear previous lessons/failures for a clean test run
    for f in glob.glob(os.path.join(manager.lessons_dir, '*.json')):
        os.remove(f)
    for f in glob.glob(os.path.join(manager.failures_dir, '*.json')):
        os.remove(f)

    print("--- Running Phase 257 Memory & Lessons System Test ---")
    
    # 1. Test learning a SUCCESS lesson
    success_task_id = "TASK-S-001"
    success_takeaway = "Successfully implemented new feature."
    success_path = manager.learn(success_task_id, "success", success_takeaway, {"feature": "new_feature_x"})
    print(f"Learned success lesson: {success_path}")

    # 2. Test learning a FAILURE lesson
    failure_task_id = "TASK-F-001"
    failure_takeaway = "Failed due to API rate limit."
    failure_context = {"error_type": "rate_limit", "model": "gemini-2.5-flash"}
    failure_path = manager.learn(failure_task_id, "failure", failure_takeaway, failure_context)
    print(f"Learned failure lesson: {failure_path}")

    # 3. Test recalling lessons
    all_lessons = manager.recall()
    search_success_lessons = manager.recall("feature")
    search_failure_lessons = manager.recall("rate limit")
    
    print(f"Total lessons recalled: {len(all_lessons)}")
    print(f"Success lessons (feature search): {len(search_success_lessons)}")
    print(f"Failure lessons (rate limit search): {len(search_failure_lessons)}")

    # Determine overall test status
    overall_test_status = "FAILED"
    if (len(all_lessons) == 2 and 
        len(search_success_lessons) == 1 and 
        len(search_failure_lessons) == 1 and
        os.path.exists(success_path) and
        os.path.exists(failure_path)):
        overall_test_status = "VERIFIED"
    
    if overall_test_status == "VERIFIED":
        print("Phase 257 Verification Test PASSED ✅")
    else:
        print("Phase 257 Verification Test FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    run_memory_lessons_test()
