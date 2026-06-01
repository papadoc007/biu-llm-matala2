from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.agents.en_to_fr_agent import EnToFrAgent
from src.agents.fr_to_he_agent import FrToHeAgent
from src.agents.he_to_en_agent import HeToEnAgent
from src.config import AppConfig
from src.io_utils import read_markdown_body, write_markdown
from src.tools.vector_compare import ComparisonResult, VectorComparator


@dataclass(frozen=True)
class PipelineResult:
    mode: str
    input_path: str
    output_dir: str
    original_text: str
    french_text: str
    hebrew_text: str
    back_to_english_text: str
    comparison: ComparisonResult
    stage2_path: str
    stage3_path: str
    stage4_path: str
    stage5_path: str


def run_translation_pipeline(
    *,
    config: AppConfig,
    input_path: str,
    output_dir: str,
    mode: str,
    api_key: str | None,
) -> PipelineResult:
    comparison_mode = "openai" if mode == "openai" else "local"

    input_file = Path(input_path)
    output_dir_path = Path(output_dir)
    stage2_path = output_dir_path / "02_french_translation.md"
    stage3_path = output_dir_path / "03_hebrew_translation.md"
    stage4_path = output_dir_path / "04_back_to_english.md"
    stage5_path = output_dir_path / "05_vector_comparison_report.md"

    original_text = read_markdown_body(input_file)
    if not original_text:
        raise ValueError(f"Input file is empty: {input_file}")

    en_to_fr = EnToFrAgent(model=config.chat_model, mode=mode, api_key=api_key)
    fr_to_he = FrToHeAgent(model=config.chat_model, mode=mode, api_key=api_key)
    he_to_en = HeToEnAgent(model=config.chat_model, mode=mode, api_key=api_key)

    french_text = en_to_fr.translate(original_text)
    write_markdown(stage2_path, "French Translation", french_text)

    hebrew_text = fr_to_he.translate(french_text)
    write_markdown(stage3_path, "Hebrew Translation", hebrew_text)

    back_to_english_text = he_to_en.translate(hebrew_text)
    write_markdown(stage4_path, "Back To English", back_to_english_text)

    comparator = VectorComparator(
        mode=comparison_mode,
        embedding_model=config.embedding_model,
        api_key=api_key,
    )
    comparison = comparator.compare_files(
        original_path=str(input_file),
        final_path=str(stage4_path),
        report_path=str(stage5_path),
    )

    return PipelineResult(
        mode=mode,
        input_path=str(input_file),
        output_dir=str(output_dir_path),
        original_text=original_text,
        french_text=french_text,
        hebrew_text=hebrew_text,
        back_to_english_text=back_to_english_text,
        comparison=comparison,
        stage2_path=str(stage2_path),
        stage3_path=str(stage3_path),
        stage4_path=str(stage4_path),
        stage5_path=str(stage5_path),
    )
