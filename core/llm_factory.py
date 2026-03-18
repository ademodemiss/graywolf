import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.expanduser('~/.graywolf/.env'))

def create_llm(provider: str = "gemini"):
    p = (provider or "gemini").lower()
    if p == "codex":
        from adapters.llm.codex_adapter import CodexAdapter

        return CodexAdapter()

    if p == "gemini":
        from adapters.llm.gemini_adapter import GeminiAdapter

        return GeminiAdapter()

    raise ValueError(f"Unknown provider: {provider}")
