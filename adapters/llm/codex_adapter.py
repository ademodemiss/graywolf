import subprocess

from .llm_adapter import LLMAdapter


class CodexAdapter(LLMAdapter):
    def __init__(self, model_name: str = "default", codex_cli_path: str = "codex"):
        self.model_name = model_name
        self.codex_cli_path = codex_cli_path

    def _run_codex_command(self, args: list[str]) -> dict:
        command = [self.codex_cli_path] + args
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )
            return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "returncode": 0}
        except subprocess.CalledProcessError as e:
            return {
                "stdout": (e.stdout or "").strip(),
                "stderr": (e.stderr or "").strip(),
                "returncode": e.returncode,
            }
        except FileNotFoundError:
            return {
                "stdout": "",
                "stderr": f"Codex CLI not found at {self.codex_cli_path}.",
                "returncode": 127,
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}

    def generate_response(self, prompt: str, **kwargs) -> str:
        codex_args = ["exec", prompt]

        if kwargs.get("full_auto"):
            codex_args.append("--full-auto")
        if kwargs.get("yolo"):
            codex_args.append("--yolo")
        if kwargs.get("model"):
            codex_args.extend(["--model", str(kwargs["model"])])

        response = self._run_codex_command(codex_args)
        if response.get("returncode", 0) != 0:
            raise RuntimeError(f"Codex command failed: {response.get('stderr', '')}")
        return response.get("stdout", "")

    def get_model_info(self) -> dict:
        info = self._run_codex_command(["--version"])
        version_str = info.get("stdout", "Unknown Codex Version").split("\n")[0]
        return {
            "name": self.model_name,
            "provider": "Codex",
            "capabilities": ["code-generation", "code-review"],
            "version": version_str,
        }

    def stream_response(self, prompt: str, **kwargs):
        yield self.generate_response(prompt, **kwargs)

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        full_prompt += "\nassistant:"
        return self.generate_response(full_prompt, **kwargs)


if __name__ == "__main__":
    adapter = CodexAdapter()
    test_prompt = "Python'da iki sayıyı toplayan bir fonksiyon yaz."
    try:
        print(adapter.generate_response(test_prompt, full_auto=True))
    except Exception as e:
        print(f"CodexAdapter test failed: {e}")
