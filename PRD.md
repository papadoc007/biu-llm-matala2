# PRD - Assignment 02 (Multi-Agent Translation Drift)

## 1) Product Purpose
Build an end-to-end AI agent pipeline that translates a source text through three translation agents and returns to the original language, then quantifies semantic drift with vector similarity.

## 2) Problem Statement
A sentence can lose or shift meaning when translated across multiple language hops. The system should provide both:
- A reproducible translation chain.
- A measurable semantic comparison between original and back-translated text.

## 3) Target Audience
- Course lecturer/reviewer.
- Student development team preparing submission and demo.

## 4) Core User Story
As a reviewer, I want to run one command (or GUI flow) that executes the entire translation chain and generates stage-by-stage outputs and a final semantic similarity report, so I can evaluate implementation quality and understanding of AI agent architecture.

## 5) Functional Requirements
1. Read source text from markdown input file.
2. Execute 3 dedicated translation agents in sequence.
3. Save intermediate outputs after each translation step.
4. Compare original vs back-translated text using vector embeddings.
5. Produce a markdown report with similarity and distance metrics.
6. Support real API mode and mock mode.
7. Provide reusable skill files for each agent/tool prompt role.
8. Provide an optional GUI to demonstrate full flow visually.

## 6) Non-Functional Requirements
1. Clear modular architecture (agents, tools, orchestrator, config).
2. Reproducible run instructions in README.
3. Graceful handling of missing configuration and API errors.
4. Submission-ready documentation with screenshots placeholders.

## 7) In Scope
- Multi-hop translation pipeline.
- Vector comparison (cosine similarity/distance).
- CLI + optional GUI demonstration.
- Documentation artifacts: PRD, PLAN, TODO, README.

## 8) Out of Scope
- Production-grade multilingual quality benchmarking.
- Human evaluation platform.
- Dataset-scale batch experimentation.

## 9) Inputs and Outputs
### Input
- `input/01_original.md`

### Outputs
- `output/02_french_translation.md`
- `output/03_hebrew_translation.md`
- `output/04_back_to_english.md`
- `output/05_vector_comparison_report.md`

## 10) Success Criteria
1. Full pipeline runs successfully.
2. All expected output files are generated.
3. Vector report includes numeric similarity and interpretation.
4. Architecture and trade-offs are documented clearly.
5. README includes screenshots and submission checklist.

## 11) Acceptance Criteria
- Running `python run_pipeline.py --mode mock` completes with all output files.
- Running `python run_pipeline.py --mode openai` (with valid key) completes with real translations.
- `README.md` explains setup, architecture, execution, and analysis.
- Required docs exist in repo root: `PRD.md`, `PLAN.md`, `TODO.md`.
