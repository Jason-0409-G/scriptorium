---
name: research-to-paper-humanize
description: >-
  Reduce the AI-detection signature of academic prose and make it read like careful human writing, with no
  dependency on any other skill. It works across five dimensions — D1 sentence-length variation (长短句结合),
  D2 paragraph-structure variety, D3 information-density alternation, D4 connector control (removing 首先/其次/
  此外/值得注意的是 and other AI-frequent connectors), D5 term-context variation — at a light/medium/heavy tier,
  records every change in a humanize_matrix.md, and verifies the result with a quantitative checker. Use whenever
  the user wants to de-AI text or lower an AI-detection rate, says 降AI率, 去AI腔, 去除AI痕迹, 这段太像AI改一下,
  长短句结合, 学术润色降AI, "reduce AI detection", "humanize this draft", "make this sound less like ChatGPT",
  "vary the sentence length". Works on a whole paper or a single paragraph; called by research-to-paper-write as
  its final pass, or invoked directly on any text.
---

# Humanize — reduce AI tells (self-contained)

AI prose is flagged not for what it says but for how even it is: one sentence length, one paragraph shape, a
steady density, connectors at every paragraph start. The fix is not to disguise AI use but to write the way
careful humans write — with variation. This skill pushes each axis back toward a human distribution, records what
it changed so the user can audit it, and measures the result.

The goal is credibility and readability, not fooling a detector. Uniform, connector-heavy prose is simply weaker
academic writing; varying it makes a stronger argument that also happens to read as human.

## Workflow

1. **Pick the tier.** Default **medium**. Use light for a quick pass, heavy when the text must be maximally
   human-like (and the user accepts more aggressive rewording). The tiers are cumulative.

2. **Apply the five-dimension rules** in `references/humanize-rules.md`:
   - **D1 sentence length (长短句)** (light+) — every 3-4 sentences, one deviates sharply (very short or long); never
     three sentences in a row within a narrow length band. A long clause-stacked setup followed by a short pivot is
     the signature rhythm.
   - **D2 paragraph structure** (medium+) — rotate paragraph templates; adjacent paragraphs must differ in shape.
   - **D3 information density** (medium+) — dense claim paragraphs alternate with light transition paragraphs.
   - **D4 connectors** (light+) — drop the AI-frequent connectors; keep ≤6 (light/medium) or ≤4 (heavy) per 1000
     chars, and never at a paragraph's first word.
   - **D5 term-context** (heavy) — occasionally substitute an accurate synonym for a standard term.

3. **Record every change in `humanize_matrix.md`** — one row per unit (unit, AI pattern, dimension, severity,
   change, expected effect, teaching note). Never edit silently; the matrix is how the user sees and judges each
   move, and it doubles as a teaching record.

4. **Preserve meaning exactly.** Touch only the prose. Never alter numbers, citations, equations, labels, file
   paths, or a term's meaning, and never add a fact the user did not provide — humanizing is rewording, not
   inventing. Remove any long dash/line separators (academic papers don't decorate with them).

5. **Verify quantitatively.** Run the checker and iterate until it passes:

   ```
   python scripts/humanize_check.py <draft.md> --lang zh --tier medium   # or en; --tier {light,medium,heavy}, default medium
   ```

   The checker auto-verifies only **D1** (sentence-length stddev — human prose runs > ~10 for Chinese characters;
   flatter = AI) and **D4** (connector density against the tier threshold; `--tier heavy` lowers the connector
   ceiling to ≤4/1000), plus dash separators and (with `--matrix humanize_matrix.md`) whether the matrix covers the
   paragraphs. It does **not** check D2, D3, or D5 — verify those by reading the `humanize_matrix.md` rows and the
   prose itself. The numbers are a floor, not the goal — read the result aloud; if it sounds like a person making an
   argument, it has passed.

## Files

- `references/humanize-rules.md` — the five dimensions with light/medium/heavy rules and concrete thresholds.
- `scripts/humanize_check.py` — quantitative de-AI checker (sentence-length stddev, connector density, dashes, matrix coverage).
