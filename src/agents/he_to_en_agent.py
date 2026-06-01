from __future__ import annotations

from src.agents.base_translator import BaseTranslatorAgent, TranslationDirection


class HeToEnAgent(BaseTranslatorAgent):
    def __init__(self, *, model: str, mode: str = "openai", api_key: str | None = None) -> None:
        super().__init__(
            direction=TranslationDirection("Hebrew", "English"),
            system_prompt=(
                "You are Translation Agent 3. Translate Hebrew text into clear, fluent "
                "English while preserving the original semantic intent."
            ),
            model=model,
            mode=mode,
            api_key=api_key,
        )
