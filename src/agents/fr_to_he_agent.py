from __future__ import annotations

from src.agents.base_translator import BaseTranslatorAgent, TranslationDirection


class FrToHeAgent(BaseTranslatorAgent):
    def __init__(self, *, model: str, mode: str = "openai", api_key: str | None = None) -> None:
        super().__init__(
            direction=TranslationDirection("French", "Hebrew"),
            system_prompt=(
                "You are Translation Agent 2. Translate French text to natural Hebrew "
                "while preserving factual meaning and tone."
            ),
            model=model,
            mode=mode,
            api_key=api_key,
        )
