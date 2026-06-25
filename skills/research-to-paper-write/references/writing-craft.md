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

## 2. 论证脉络矩阵 (argument-thread matrix) — plan before drafting

Before any prose, lock the controlling motivation, then compile it into a per-unit matrix in
`writing_rationale_matrix.md`. This is the execution plan, not a post-hoc summary — the manuscript is drafted row by
row from it, and every paragraph in the final draft should trace back to one row.

**2a. Controlling motivation (双向门).** At the top of the file, state the paper's one-sentence red thread, then split
it both ways — what the paper WILL argue and, just as important, what it must NOT argue:

```
红线动机 (one sentence): <the single controlling claim>
- 要论证 (prioritized claims): <2-4 specific claims this paper makes>
- 禁止论证 (claims to avoid): <what to NOT claim — the overclaim guardrails>
```

The 禁止论证 side is what stops later sections from drifting into generic claims or overreaching the evidence. For a
deep-sea / 生信 indicator paper that means things like: stay candidate/proposed and never "validated"; do not
extrapolate an absolute carbon flux from n=1; do not claim an ecosystem-scale effect off a single strain's abundance.

**2b. The matrix.** One row per smallest writing unit that needs a deliberate choice (a claim, an evidence block, a
synthesis move, a heading, a caption). If one paragraph has two functions, split it into two rows. Columns:

| 行号 Row | 写作单元 Unit | 论点/功能 Claim | 动机链接 Motivation link | 证据/引用锚 Evidence·cite | 措辞强度 Hedge | 结构模式 Pattern/SOTA | 文字动作 Text move | 落点检查 Final check |
|---|---|---|---|---|---|---|---|---|

Row **F1** is the framework row: it argues the whole-work control structure (why this angle, for this venue and
reader) in 2-4 sentences per cell — a design memo, not a one-liner. Every later row must physically connect to the
red thread through three non-empty, specific anchors: **动机链接** (how this unit serves the motivation),
**证据/引用锚** (the specific datum or the one reference it leans on — move evidence next to the claim it supports),
and **文字动作** (the concrete move to make). 措辞强度 carries the evidence-matched hedge (predicted vs confirmed, §1).

**2c. Reason quality bar.** A generic reason ("提升清晰度 / 润色 / make academic / improve clarity") is not a reason and
fails the gate. Write 2-4 sentences in the important cells, not keywords. Use at least 8 rows for an ordinary paper; a
complex one often needs 20-60. Where evidence or a citation is missing, write `[需要数据: …]` / `[需要引用: …]` rather
than inventing one. A generic matrix produces a generic paper.

**2d. Gate before drafting (offline).** Run the local validator — pure stdlib, no network, so it works on a plain
DeepSeek setup with no VPN/proxy:

    python scripts/check_argument_matrix.py writing_rationale_matrix.md   # --min-rows N raises the floor

It checks the doublet (both 要/禁止 sides present), the F1 framework row, the row-count floor, every row's three
anchors non-empty and specific, and rejects generic-phrase cells. Do not draft until it passes — a matrix that
passes is the proof the paper has a spine before a single sentence is written.

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
