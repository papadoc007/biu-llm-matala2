from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class TranslationDirection:
    source_language: str
    target_language: str


class BaseTranslatorAgent:
    def __init__(
        self,
        *,
        direction: TranslationDirection,
        system_prompt: str,
        model: str,
        mode: str = "openai",
        api_key: str | None = None,
    ) -> None:
        self.direction = direction
        self.system_prompt = system_prompt
        self.model = model
        self.mode = mode
        self.client = OpenAI(api_key=api_key) if mode == "openai" else None

    def translate(self, text: str) -> str:
        if self.mode == "mock":
            return (
                f"[MOCK TRANSLATION {self.direction.source_language} -> "
                f"{self.direction.target_language}]\n{text.strip()}"
            )

        if not self.client:
            raise RuntimeError("OpenAI client is not initialized.")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Translate the following text from {self.direction.source_language} "
                        f"to {self.direction.target_language}. Return only the translated text:\n\n"
                        f"{text}"
                    ),
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()
