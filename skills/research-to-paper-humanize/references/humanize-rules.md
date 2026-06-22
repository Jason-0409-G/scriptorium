# De-AI / humanize rules

AI-generated academic prose is detectable not because of *what* it says but *how* it says it: it is too even.
The fix is not to hide AI use but to write the way careful humans write — with variation. The five dimensions
below are the axes on which AI text is too regular; each rule pushes one axis back toward a human distribution.
Apply them with the tier the user asked for (default **medium**), record every change in `humanize_matrix.md`,
and verify with `scripts/humanize_check.py`.

**Universal rules (all tiers):**
- Touch only the prose. Never alter numbers, citations, equations, labels, file paths, or technical terms' meaning.
- Add no facts and no evidence the user did not provide. Humanizing is rewording, never inventing.
- Keep an academic register throughout — no colloquialisms, no internet slang.
- **No long dash/line separators** (no runs of 3+ — or ——). Use a blank line or a heading instead; academic papers
  do not decorate with dashes.
- Write one `humanize_matrix.md` row per unit you process (8 columns: unit, AI pattern, dimension D1-D5, severity,
  change applied, expected effect, teaching note). Record as you go, never retroactively — the matrix is how the
  user audits each move.

## The five dimensions

| Dim | AI signature | Human target |
|---|---|---|
| **D1 sentence length (长短句)** | one peak at ~15-25 chars | multi-peak: short (5-12) + medium (15-25) + long (30-50) |
| **D2 paragraph structure** | every paragraph topic→explain→example→summarize | mixed templates; adjacent paragraphs differ |
| **D3 information density** | flat ~70% throughout | alternating high / low (claims dense, transitions light) |
| **D4 connectors** | many, at paragraph starts (8-15 / 1k chars) | few, at real turns only (≤6 / 1k) |
| **D5 term-context** | the same standard term every time | occasional accurate synonym variation |

## light — D4 + D1 (the minimum)

**D4 connectors.** Ban the AI-frequent connectors and let logic carry the transition instead:
首先 / 其次 / 再次 / 最后 · 综上所述 / 总而言之 · 此外 / 另外 / 不仅如此 · 值得注意的是 / 需要指出的是
(EN: firstly/secondly, moreover, furthermore, in addition, it is worth noting, it is important to note).
Replace by letting the previous paragraph's conclusion raise the next paragraph's question, or with grounded
moves like 在此基础上 / 进一步而言 / from this angle. Keep ≤ 6 connectors per 1000 chars, and never at a paragraph's
first word — connectors belong at the actual logical turn.

**D1 sentence length.** Every 3-4 sentences, one must deviate sharply — either short (≤ 10 chars / ~6 words) or
long (≥ 35 chars / ~25 words). Never let 3 sentences in a row sit within 8 chars of each other. Do not open
consecutive sentences with the same structure. This is "长短句结合": a long, clause-stacked setup followed by a
short, punchy pivot is the signature rhythm of strong academic prose.

## medium — light + D2 + D3 + first person (default)

**D2 paragraph structure.** Do not reuse one paragraph template throughout. Draw from these and use each at most
twice; adjacent paragraphs must differ:
- question-driven: pose the question → analyze in layers → conclude;
- contrast-judgment: view A → view B → analyze the gap → take a position;
- causal chain: observation → cause → inference → check;
- point-then-stop: argue deeply → state the judgment → no summary sentence;
- thesis-antithesis: claim → counter → reconcile.

**D3 information density.** Core-argument paragraphs run dense (70-85%, every claim with concrete evidence);
transition paragraphs run light (40-50%, one or two sentences). Make adjacent paragraphs differ by ≥ 15% so the
text breathes in a high-low-high rhythm rather than a flat wall.

**D1 reinforced.** Ensure the length distribution has at least two clear peaks (a short band and a long band), mix
in an occasional rhetorical question (1-2 per section), and keep short sentences at ≥ 15% of each section.

**First-person academic voice.** In methods and results analysis, use 我们 / 本研究发现 / 实验结果表明 (we / this
study finds / results show), at least twice per ~2000 chars, but do not start consecutive sentences with 我们.

## heavy — medium + D5 + structural irregularity

**D5 term-context.** At least once per ~800 chars, substitute an accurate synonym for a standard term
(该方法论框架 → 这一分析路径; 呈现显著统计学差异 → 差异达到统计显著水平). Reach for precise but less-common academic
words occasionally; do not overdo it.

**Structural irregularity (still rigorous).** The introduction may invert (lead with the core question, then
背景); methods may interleave the reasoning behind a design choice with its description; the discussion may leave
one or two questions openly unresolved.

**Connectors tightened.** ≤ 4 per 1000 chars, clustered at only 2-3 key logical turns.

## What "passing" means

`humanize_check.py` flags a draft when: sentence-length stddev is too low (human prose runs > 10; uniform AI prose
is lower), connector density exceeds the tier threshold, dash separators appear, or the matrix does not cover the
paragraphs. Iterate until those clear. But the numbers are a floor, not the goal — read the prose aloud; if it
sounds like a person making an argument, it will also pass.
