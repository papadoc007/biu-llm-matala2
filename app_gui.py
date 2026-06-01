from __future__ import annotations

from io import BytesIO
from pathlib import Path

import streamlit as st
from openai import OpenAI

from src.config import AppConfig, get_openai_api_key, load_config
from src.io_utils import write_markdown
from src.pipeline import run_translation_pipeline


def _inject_style() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: radial-gradient(circle at top right, #10243d 0%, #081321 45%, #060c16 100%);
            color: #f3f6fb;
        }
        .stTextArea textarea {
            background-color: #111a2a !important;
            color: #f8fafc !important;
            border: 1px solid #2f4a72 !important;
        }
        .stTextArea textarea:disabled {
            -webkit-text-fill-color: #f8fafc !important;
            color: #f8fafc !important;
            opacity: 1 !important;
        }
        .metric-card {
            border: 1px solid #36557f;
            border-radius: 14px;
            padding: 12px 14px;
            background: linear-gradient(180deg, #0e1a2b, #0b1322);
            margin-bottom: 10px;
        }
        .stage-block {
            border: 1px solid #2f4a72;
            border-radius: 12px;
            background: #0f1b2d;
            padding: 10px;
            margin-bottom: 10px;
        }
        .stage-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #8bc6ff;
            margin-top: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _save_env_file(
    *,
    api_key: str,
    chat_model: str,
    embedding_model: str,
    transcription_model: str,
    output_dir: str,
) -> None:
    env_path = Path(".env")
    env_text = (
        f'OPENAI_API_KEY="{api_key}"\n'
        f'OPENAI_CHAT_MODEL="{chat_model}"\n'
        f'OPENAI_EMBEDDING_MODEL="{embedding_model}"\n'
        f'OPENAI_TRANSCRIPTION_MODEL="{transcription_model}"\n'
        f'PIPELINE_OUTPUT_DIR="{output_dir}"\n'
    )
    env_path.write_text(env_text, encoding="utf-8")


def _transcribe_audio(
    *,
    api_key: str,
    transcription_model: str,
    file_name: str,
    file_bytes: bytes,
) -> str:
    client = OpenAI(api_key=api_key)
    audio_stream = BytesIO(file_bytes)
    audio_stream.name = file_name
    response = client.audio.transcriptions.create(
        model=transcription_model,
        file=audio_stream,
    )
    return (response.text or "").strip()


def _read_skill_file(path: str) -> str:
    skill_path = Path(path)
    if not skill_path.exists():
        return "Skill file not found."
    try:
        return skill_path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return skill_path.read_text(encoding="latin-1").strip()


def main() -> None:
    st.set_page_config(
        page_title="Multi-Agent Translation System",
        page_icon="🌍",
        layout="wide",
    )
    _inject_style()

    st.title("🌍 Multi-Agent Translation System")
    st.caption("Production-like flow: Input / Transcription -> Translation Agents -> Vector Similarity")

    with st.expander("Skills used in this pipeline", expanded=False):
        skill_tabs = st.tabs(
            [
                "EN -> FR skill",
                "FR -> HE skill",
                "HE -> EN skill",
                "Vector comparison skill",
            ]
        )
        with skill_tabs[0]:
            st.markdown(_read_skill_file("skills/en_to_fr.md"))
        with skill_tabs[1]:
            st.markdown(_read_skill_file("skills/fr_to_he.md"))
        with skill_tabs[2]:
            st.markdown(_read_skill_file("skills/he_to_en.md"))
        with skill_tabs[3]:
            st.markdown(_read_skill_file("skills/vector_comparison.md"))

    config = load_config()
    env_api_key = get_openai_api_key() or ""
    if "runtime_api_key" not in st.session_state:
        st.session_state.runtime_api_key = env_api_key
    if "source_text" not in st.session_state:
        st.session_state.source_text = (
            "Artificial intelligence can accelerate medical diagnosis, but responsible use "
            "requires careful validation, transparent communication, and strong human oversight."
        )

    st.markdown("## 1) Runtime Setup")
    st.info("Fill the runtime settings below. You can also save them to `.env` from this screen.")
    cfg1, cfg2 = st.columns(2)
    with cfg1:
        runtime_api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.runtime_api_key,
            type="password",
            help="Required for real translation, embeddings, and transcription.",
        )
        chat_model = st.text_input("Chat model", value=config.chat_model)
        embedding_model = st.text_input("Embedding model", value=config.embedding_model)
    with cfg2:
        transcription_model = st.text_input("Transcription model", value=config.transcription_model)
        output_dir = st.text_input("Output directory", value=config.output_dir)
        save_env = st.button("Save settings to .env", use_container_width=True)
        if save_env:
            if not runtime_api_key.strip():
                st.warning("Cannot save `.env` without API key.")
            else:
                _save_env_file(
                    api_key=runtime_api_key.strip(),
                    chat_model=chat_model.strip(),
                    embedding_model=embedding_model.strip(),
                    transcription_model=transcription_model.strip(),
                    output_dir=output_dir.strip(),
                )
                st.success("Saved runtime settings to `.env`.")

    st.session_state.runtime_api_key = runtime_api_key

    st.markdown("## 2) Input (Text or Audio)")
    input_mode = st.radio(
        "Input source",
        options=["Text", "Audio (transcribe with OpenAI)"],
        horizontal=True,
    )
    default_text = (
        "Artificial intelligence can accelerate medical diagnosis, but responsible use "
        "requires careful validation, transparent communication, and strong human oversight."
    )
    if input_mode == "Text":
        st.session_state.source_text = st.text_area(
            "Enter your source text (English)",
            value=st.session_state.source_text or default_text,
            height=180,
        )
    else:
        audio_file = st.file_uploader(
            "Upload audio file for transcription",
            type=["mp3", "wav", "m4a", "mp4", "webm"],
        )
        transcribe_clicked = st.button("Transcribe Audio", use_container_width=True)
        if transcribe_clicked:
            if not runtime_api_key.strip():
                st.error("API key is required for transcription.")
            elif not audio_file:
                st.error("Please upload an audio file first.")
            else:
                with st.spinner("Transcribing audio..."):
                    try:
                        transcript = _transcribe_audio(
                            api_key=runtime_api_key.strip(),
                            transcription_model=transcription_model.strip(),
                            file_name=audio_file.name,
                            file_bytes=audio_file.getvalue(),
                        )
                    except Exception as exc:
                        st.error(f"Transcription failed: {exc}")
                    else:
                        st.session_state.source_text = transcript
                        st.success("Transcription completed. Review/edit the text below.")
        st.session_state.source_text = st.text_area(
            "Transcribed / editable text",
            value=st.session_state.source_text or default_text,
            height=180,
        )

    st.markdown("## 3) Run Full Translation Pipeline")
    run_clicked = st.button("Run Full Pipeline (Real API)", type="primary", use_container_width=True)

    if not run_clicked:
        st.info("Configure settings, provide input, then click the run button.")
        return

    if not runtime_api_key.strip():
        st.error("API key is required. Fill it in Runtime Setup.")
        return

    if not st.session_state.source_text.strip():
        st.error("Input text is empty. Please enter a source paragraph.")
        return

    runtime_config = AppConfig(
        chat_model=chat_model.strip() or config.chat_model,
        embedding_model=embedding_model.strip() or config.embedding_model,
        transcription_model=transcription_model.strip() or config.transcription_model,
        default_input_path=config.default_input_path,
        output_dir=output_dir.strip() or config.output_dir,
    )

    effective_mode = "openai"
    input_path = Path("input") / "01_original.md"
    write_markdown(input_path, "Original Text (English)", st.session_state.source_text)

    with st.status("Running agents and vector comparison...", expanded=True) as status:
        st.write(f"Mode selected: `{effective_mode}`")
        st.write(f"Chat model: `{runtime_config.chat_model}`")
        st.write(f"Embedding model: `{runtime_config.embedding_model}`")
        st.write("Saving input markdown...")
        try:
            result = run_translation_pipeline(
                config=runtime_config,
                input_path=str(input_path),
                output_dir=runtime_config.output_dir,
                mode=effective_mode,
                api_key=runtime_api_key.strip(),
            )
        except Exception as exc:
            status.update(label="Pipeline failed", state="error")
            st.error(f"Pipeline failed: {exc}")
            return

        st.write("All translation stages completed.")
        st.write("Vector comparison report generated.")
        status.update(label="Pipeline completed successfully", state="complete")

    col1, col2, col3 = st.columns(3)
    col1.metric("Cosine Similarity", f"{result.comparison.similarity:.4f}")
    col2.metric("Cosine Distance", f"{result.comparison.cosine_distance:.4f}")
    col3.metric("Mode", result.mode.upper())

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"**Interpretation:** {result.comparison.explanation}")
    st.markdown(f"**Method:** `{result.comparison.method}`")
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="stage-title">01 Original (English)</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage-block">', unsafe_allow_html=True)
        st.text_area("Original", value=result.original_text, height=180, disabled=True, key="orig")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="stage-title">02 French Translation</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage-block">', unsafe_allow_html=True)
        st.text_area("French", value=result.french_text, height=180, disabled=True, key="fr")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="stage-title">03 Hebrew Translation</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage-block">', unsafe_allow_html=True)
        st.text_area("Hebrew", value=result.hebrew_text, height=180, disabled=True, key="he")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="stage-title">04 Back to English</div>', unsafe_allow_html=True)
        st.markdown('<div class="stage-block">', unsafe_allow_html=True)
        st.text_area(
            "Back to English",
            value=result.back_to_english_text,
            height=180,
            disabled=True,
            key="back_en",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Generated Files")
    st.code(
        "\n".join(
            [
                f"- {input_path}",
                f"- {result.stage2_path}",
                f"- {result.stage3_path}",
                f"- {result.stage4_path}",
                f"- {result.stage5_path}",
            ]
        )
    )


if __name__ == "__main__":
    main()
