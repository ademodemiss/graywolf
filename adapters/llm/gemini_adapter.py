import os
from typing import Dict, List

from .llm_adapter import LLMAdapter


class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Gemini API Key not found. Please set GOOGLE_API_KEY environment variable or provide it.")

        # Prefer new SDK (google.genai). Legacy fallback is opt-in only.
        self._use_new_sdk = False
        try:
            from google import genai  # type: ignore
            self.client = genai.Client(api_key=api_key)
            self._use_new_sdk = True
        except Exception as e:
            allow_legacy = os.getenv("GRAYWOLF_ALLOW_LEGACY_GEMINI", "0") == "1"
            if not allow_legacy:
                raise RuntimeError(
                    "google.genai initialization failed. Install/repair google-genai or set "
                    "GRAYWOLF_ALLOW_LEGACY_GEMINI=1 to allow deprecated fallback."
                ) from e
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)
            self.client = genai

        self.model_name = model_name

    def generate_response(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        model_name = kwargs.get("model", self.model_name)
        
        if self._use_new_sdk:
            prompt_token_count = self.client.models.count_tokens(model=model_name, contents=prompt).total_tokens
            response = self.client.models.generate_content(model=model_name, contents=prompt)
            response_text = getattr(response, "text", "") or ""
            completion_token_count = self.client.models.count_tokens(model=model_name, contents=response_text).total_tokens
            return response_text, prompt_token_count, completion_token_count

        # google-generativeai fallback
        response = self.client.GenerativeModel(model_name).generate_content(prompt)
        response_text = getattr(response, "text", "") or ""
        return response_text, 0, 0

    def get_model_info(self) -> dict:
        return {
            "name": self.model_name,
            "provider": "Google Gemini",
            "capabilities": ["text-generation", "chat-completion"],
        }

    def stream_response(self, prompt: str, **kwargs):
        if self._use_new_sdk:
            stream = self.client.models.generate_content_stream(
                model=kwargs.get("model", self.model_name),
                contents=prompt,
            )
            for chunk in stream:
                text = getattr(chunk, "text", None)
                if text:
                    yield text
            return

        stream = self.client.GenerativeModel(kwargs.get("model", self.model_name)).generate_content(prompt, stream=True)
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

    def chat_completion(self, messages: List[Dict], **kwargs) -> tuple[str, int, int]:
        model_name = kwargs.get("model", self.model_name)

        # Minimal chat mapping: flatten into a single prompt for now
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        full_prompt += "\nassistant:"

        if self._use_new_sdk:
            prompt_token_count = self.client.models.count_tokens(model=model_name, contents=full_prompt).total_tokens
            response = self.client.models.generate_content(model=model_name, contents=full_prompt)
            response_text = getattr(response, "text", "") or ""
            completion_token_count = self.client.models.count_tokens(model=model_name, contents=response_text).total_tokens
            return response_text, prompt_token_count, completion_token_count

        response = self.client.GenerativeModel(model_name).generate_content(full_prompt)
        response_text = getattr(response, "text", "") or ""
        return response_text, 0, 0


if __name__ == "__main__":
    print("GeminiAdapter hazır (google.genai).")
