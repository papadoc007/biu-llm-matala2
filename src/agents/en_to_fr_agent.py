from __future__ import annotations

from src.agents.base_translator import BaseTranslatorAgent, TranslationDirection


class EnToFrAgent(BaseTranslatorAgent):
    def __init__(self, *, model: str, mode: str = "openai", api_key: str | None = None) -> None:
        super().__init__(
            direction=TranslationDirection("English", "French"),
            system_prompt=(
                "You are Translation Agent 1. Produce an accurate French translation "
                "that preserves meaning, register, and key details."
            ),
            model=model,
            mode=mode,
            api_key=api_key,
        )
