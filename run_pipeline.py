from __future__ import annotations

import argparse

from src.config import get_openai_api_key, load_config
from src.pipeline import run_translation_pipeline


def resolve_mode(requested_mode: str, api_key: str | None) -> str:
    if requested_mode in {"openai", "mock"}:
        return requested_mode
    return "openai" if api_key else "mock"


def main() -> None:
    config = load_config()
    parser = argparse.ArgumentParser(description="Run the multi-agent translation pipeline.")
    parser.add_argument("--input", default=config.default_input_path, help="Path to 01_original.md")
    parser.add_argument("--output-dir", default=config.output_dir, help="Directory for output markdown files")
    parser.add_argument(
        "--mode",
        choices=["auto", "openai", "mock"],
        default="auto",
        help="Execution mode. 'auto' uses OpenAI when API key exists, otherwise mock mode.",
    )
    args = parser.parse_args()

    api_key = get_openai_api_key()
    mode = resolve_mode(args.mode, api_key)

    print(f"[Pipeline] Input: {args.input}")
    print(f"[Pipeline] Output directory: {args.output_dir}")
    print(f"[Pipeline] Mode: {mode}")

    print("[Stage 1-4] Running full translation and vector comparison pipeline")
    result = run_translation_pipeline(
        config=config,
        input_path=args.input,
        output_dir=args.output_dir,
        mode=mode,
        api_key=api_key,
    )
    print(f"[Saved] {result.stage2_path}")
    print(f"[Saved] {result.stage3_path}")
    print(f"[Saved] {result.stage4_path}")
    print(f"[Saved] {result.stage5_path}")
    print(
        "[Result] Similarity score: "
        f"{result.comparison.similarity:.4f} ({result.comparison.explanation})"
    )


if __name__ == "__main__":
    main()
