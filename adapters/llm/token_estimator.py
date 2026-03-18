"""Basit bir token tahmin modülü; gerçek servislerde daha rafine hesaplama gerekebilir."""
from __future__ import annotations

from typing import Mapping

def estimate_basic_tokens(text: str) -> int:
    """Kelime sayısına dayalı kaba token tahmini yap."""
    cleaned = text.strip()
    if not cleaned:
        return 0
    words = len(cleaned.split())
    # Her kelime 1.15 token'a denk geliyor varsayımı + başlangıç 2
    return max(1, int(words * 1.15) + 2)

def estimate_usage(prompt: str, response: str) -> Mapping[str, int]:
    """Prompt ve response için ayrı token sayıları ve toplamı döndür."""
    prompt_tokens = estimate_basic_tokens(prompt)
    response_tokens = estimate_basic_tokens(response)
    return {
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": prompt_tokens + response_tokens,
    }
