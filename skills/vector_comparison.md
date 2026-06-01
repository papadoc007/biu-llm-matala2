# Skill: Semantic Drift Vector Comparison

## Role
Compare original and back-translated English texts by vector similarity.

## Input
- `01_original.md`
- `04_back_to_english.md`

## Method
1. Convert each text into a vector representation (embedding).
2. Calculate cosine similarity.
3. Report cosine distance (`1 - similarity`).
4. Provide a short interpretation for semantic drift.

## Output
- Markdown report in `05_vector_comparison_report.md` containing:
  - method,
  - similarity score,
  - distance score,
  - one-paragraph interpretation.
