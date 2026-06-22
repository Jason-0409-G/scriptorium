# Writing craft

The reference for understanding-to-draft (steps 1-3 of the write workflow). Two things make academic prose
defensible at the drafting stage: claims hedged to their evidence, and structure that fits the scene. Review and
de-AI come afterward and live in their own sub-skills (`research-to-paper-audit`, `research-to-paper-humanize`).

## 1. Hedging ladder — match the verb to the evidence

The single most common reviewer objection is a claim stronger than its evidence. Pick the verb from the rung your
evidence actually reaches:

```
is consistent with < is compatible with < may / could reflect < appears to <
points to < suggests < is predicted to < indicates < is characteristic of < supports
────────────────────────── RED LINE for predictions ──────────────────────────
demonstrates / confirms / proves / establishes / validates
```

- A **prediction** (from a model, a genome, a computation) stops at **"is predicted to" / "is consistent with"**.
- An **observed whole-system result** (you ran it and saw it) may **"confirm"** that system's behavior.
- A **proposed indicator / marker / mechanism** stays **"candidate / proposed / putative"** until validated.
- The rule of thumb: the *organism / experiment* can confirm; the *gene / model* can only predict.

## 2. Writing rationale matrix (plan before drafting)

`writing_rationale_matrix.md` — one row per real unit (claim, evidence block, synthesis move, heading, caption).
Not a fixed IMRaD checklist. Columns:

| Unit | Claim it makes | Evidence behind it | Rhetorical move | Hedge level | Source / SOTA |
|---|---|---|---|---|---|

Row 1 justifies the whole-work framing: why this angle, for this journal and reader. Every later row must carry a
concrete claim, its evidence, and the move it performs — not a label like "background paragraph". A generic matrix
produces a generic paper, so push each row to be specific before any prose is written.

## 3. Per-scene structure

**论文 / paper (IMRaD).**
- *Title*: descriptive, evidence-level honest; no claim the data don't support.
- *Abstract*: background → gap (the "yet … has not …" hinge) → method → results (each with a number) → hedged
  conclusion.
- *Introduction*: establish the field → name the unfilled gap → state this study's question, ending on a sharp
  research-question sentence.
- *Results*: one subsection per main figure. Topic sentence = the claim; body = numbers/evidence; **no
  interpretation** — say "we observed / X carries", never "suggests/implies". All interpretation moves to Discussion.
- *Discussion*: claim + supporting evidence + explicit counter-boundary, per axis; numbered limitations; no new data.
- *Methods*: tool + version + thresholds in every sentence; flag power limits and negatives up front.

**综述 / review.** Organize by **theme, not by paper**. Each section advances a position and synthesizes multiple
works toward it; do not march paper-by-paper. Open on the field-level tension, end each section on what is settled
vs contested. Close on the open questions that motivate future work.

**报告 / report.** Problem → approach → findings → implications. Plainer register for a non-specialist or internal
reader; lead with the takeaway, support with evidence, keep methods brief but reproducible.

**会议论文 / conference.** A tighter journal paper under a hard page/length limit: state the contribution in the
abstract and the first paragraph, compress Related Work and Methods to what is needed to reproduce the core result,
and foreground the one or two results that carry the claim. Cut, don't shrink uniformly — keep the contribution sharp.

**竞赛 / competition.** Judged against the competition's rubric, so map the writing to its scoring axes (novelty,
results, impact, clarity). Lead with the problem and the contribution, make the results and their significance
unmissable, and state limitations honestly — a hedged, defensible claim scores better than an over-claim.

---

After drafting, run the review (`research-to-paper-audit`) until a round is clean, then the de-AI pass
(`research-to-paper-humanize`). Drafting sets up both; it does not replace them.
