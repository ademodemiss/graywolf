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

    def generate_response(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        model_name = kwargs.get("model", self.model_name)
        
        # Prompt tokenlarını say
        prompt_token_count = self.client.models.count_tokens(model=model_name, contents=prompt).total_tokens

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        response_text = getattr(response, "text", "") or ""
        
        # Yanıt tokenlarını say
        # Gemini API genellikle yanıtta token bilgisini doğrudan sağlamaz.
        # Bu nedenle, yanıt metnini saymak için count_tokens kullanacağız.
        completion_token_count = self.client.models.count_tokens(model=model_name, contents=response_text).total_tokens

        return response_text, prompt_token_count, completion_token_count

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

    def chat_completion(self, messages: List[Dict], **kwargs) -> tuple[str, int, int]:
        model_name = kwargs.get("model", self.model_name)

        # Minimal chat mapping: flatten into a single prompt for now
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        full_prompt += "\nassistant:"

        # Prompt tokenlarını say
        prompt_token_count = self.client.models.count_tokens(model=model_name, contents=full_prompt).total_tokens

        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt,
        )
        response_text = getattr(response, "text", "") or ""

        # Yanıt tokenlarını say
        completion_token_count = self.client.models.count_tokens(model=model_name, contents=response_text).total_tokens

        return response_text, prompt_token_count, completion_token_count


if __name__ == "__main__":
    print("GeminiAdapter hazır (google.genai).")
