import os
from typing import Dict, List

from .llm_adapter import LLMAdapter


class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Gemini API Key not found. Please set GOOGLE_API_KEY environment variable or provide it.")

        # New SDK (google.genai)
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_response(self, prompt: str, **kwargs) -> str:
        response = self.client.models.generate_content(
            model=kwargs.get("model", self.model_name),
            contents=prompt,
        )
        return getattr(response, "text", "") or ""

    def get_model_info(self) -> dict:
        return {
            "name": self.model_name,
            "provider": "Google Gemini",
            "capabilities": ["text-generation", "chat-completion"],
        }

    def stream_response(self, prompt: str, **kwargs):
        stream = self.client.models.generate_content_stream(
            model=kwargs.get("model", self.model_name),
            contents=prompt,
        )
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

    def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        # Minimal chat mapping: flatten into a single prompt
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        full_prompt += "\nassistant:"
        return self.generate_response(full_prompt, **kwargs)


if __name__ == "__main__":
    print("GeminiAdapter hazır (google.genai).")
