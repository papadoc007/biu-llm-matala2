from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    transcription_model: str = "whisper-1"
    default_input_path: str = "input/01_original.md"
    output_dir: str = "output"


def load_config() -> AppConfig:
    _safe_load_dotenv()
    return AppConfig(
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        transcription_model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"),
        default_input_path=os.getenv("PIPELINE_INPUT_PATH", "input/01_original.md"),
        output_dir=os.getenv("PIPELINE_OUTPUT_DIR", "output"),
    )


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def _safe_load_dotenv() -> None:
    """
    Load .env robustly on Windows even if file encoding is not UTF-8.
    """
    dotenv_path = Path(".env")
    if not dotenv_path.exists():
        return

    for encoding in ("utf-8", "utf-8-sig", "cp1255", "cp1252", "latin-1"):
        try:
            load_dotenv(dotenv_path=dotenv_path, encoding=encoding)
            return
        except UnicodeDecodeError:
            continue
