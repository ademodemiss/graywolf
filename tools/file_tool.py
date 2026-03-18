import os
import glob
import json
import datetime
from pathlib import Path

class FileTool:
    def __init__(self, base_dir: str = "/home/adem/graywolf"):
        self.base_dir = Path(base_dir).expanduser()
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "file_tool.log"

    def _log(self, message: str):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        log_entry = f"{timestamp} - {message}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def _get_full_path(self, file_path: str) -> Path:
        # Ensure path is relative to base_dir or absolute
        if os.path.isabs(file_path):
            return Path(file_path)
        return self.base_dir / file_path

    def read(self, file_path: str) -> dict:
        full_path = self._get_full_path(file_path)
        try:
            if not full_path.exists():
                self._log(f"Read failed: File not found at {full_path}")
                return {"status": "error", "message": f"File not found: {file_path}"}
            
            content = full_path.read_text(encoding="utf-8")
            self._log(f"Successfully read: {file_path}")
            return {"status": "success", "content": content}
        except Exception as e:
            self._log(f"Read failed for {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def write(self, file_path: str, content: str) -> dict:
        full_path = self._get_full_path(file_path)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            self._log(f"Successfully wrote to: {file_path}")
            return {"status": "success", "message": f"Successfully wrote to {file_path}"}
        except Exception as e:
            self._log(f"Write failed for {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def list(self, dir_path: str) -> dict:
        full_path = self._get_full_path(dir_path)
        try:
            if not full_path.is_dir():
                self._log(f"List failed: Path is not a directory: {full_path}")
                return {"status": "error", "message": f"Path is not a directory: {dir_path}"}
            
            files = [f for f in os.listdir(full_path)]
            self._log(f"Successfully listed directory: {dir_path}")
            return {"status": "success", "files": files}
        except Exception as e:
            self._log(f"List failed for {dir_path}: {e}")
            return {"status": "error", "message": str(e)}

    def exists(self, file_path: str) -> dict:
        full_path = self._get_full_path(file_path)
        try:
            result = full_path.exists()
            self._log(f"Checked existence of {file_path}: {result}")
            return {"status": "success", "exists": result}
        except Exception as e:
            self._log(f"Exists check failed for {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def delete(self, file_path: str) -> dict:
        full_path = self._get_full_path(file_path)
        try:
            if not full_path.exists():
                self._log(f"Delete failed: File not found: {full_path}")
                return {"status": "error", "message": f"File not found: {file_path}"}
            full_path.unlink()
            self._log(f"Successfully deleted: {file_path}")
            return {"status": "success", "message": f"Successfully deleted {file_path}"}
        except Exception as e:
            self._log(f"Delete failed for {file_path}: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Starting FileTool tests...")
    # Ensure necessary dirs exist for testing
    os.makedirs("tasks/queue", exist_ok=True)
    os.makedirs("tasks/processed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Mocking datetime for consistent test logs if needed, but using real for simplicity here.
    import datetime 

    tool = FileTool()

    # Test write
    write_res = tool.write("test_file.txt", "Hello, FileTool!")
    print(f"Write test: {write_res}")
    assert write_res["status"] == "success"

    # Test read
    read_res = tool.read("test_file.txt")
    print(f"Read test: {read_res}")
    assert read_res["status"] == "success" and read_res["content"] == "Hello, FileTool!"
    
    # Test list
    list_res = tool.list(".") # List current directory
    print(f"List test: {list_res}")
    assert list_res["status"] == "success" and "test_file.txt" in list_res["files"]

    # Test exists
    exists_res_true = tool.exists("test_file.txt")
    print(f"Exists test (true): {exists_res_true}")
    assert exists_res_true["status"] == "success" and exists_res_true["exists"] is True
    
    exists_res_false = tool.exists("non_existent_file.txt")
    print(f"Exists test (false): {exists_res_false}")
    assert exists_res_false["status"] == "success" and exists_res_false["exists"] is False

    # Test delete
    delete_res = tool.delete("test_file.txt")
    print(f"Delete test: {delete_res}")
    assert delete_res["status"] == "success"
    
    read_after_delete = tool.read("test_file.txt")
    print(f"Read after delete test: {read_after_delete}")
    assert read_after_delete["status"] == "error"
    
    print("FileTool tests completed.")
