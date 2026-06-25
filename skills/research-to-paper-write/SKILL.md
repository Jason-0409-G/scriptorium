---
name: research-to-paper-write
description: >-
  Draft and revise an academic manuscript end to end in either of two modes — Build From Materials or Rewrite
  Existing — across scenes journal/论文, conference/会议论文, report/报告, review/综述, competition/竞赛, at a flash or
  pro research depth. It understands the content first,
  plans a per-unit writing rationale (not a generic IMRaD template), and drafts with evidence-matched hedging,
  then runs the review and de-AI passes through its companion sub-skills research-to-paper-audit (independent
  multi-reviewer rounds) and research-to-paper-humanize (five-dimension de-AI incl. 长短句), discussing with the
  user at each round. Depends on no skill outside this plugin. Use whenever the user wants to write or rewrite a
  paper, review, or report, says 帮我写论文/综述/报告, 把这些内容写成稿子, 改写这篇草稿, 按我的写作纪律来,
  写会议论文/竞赛论文, 从素材构建, "draft this into a paper", "build a paper from these materials", "rewrite this
  manuscript", "write up these results". Reads an optional scope_brief.md
  (angle/journal/word-count) and a curated reference library if present; works standalone otherwise. For ONLY a
  review pass use research-to-paper-audit; for ONLY de-AI use research-to-paper-humanize.
---

# Write — draft and revise (self-contained, orchestrates audit + humanize)

This is the writing engine. It owns the parts unique to drafting — understanding the content, planning the
rationale, and writing prose hedged to its evidence — and hands the two reusable passes to companion sub-skills:
review to `research-to-paper-audit`, de-AI to `research-to-paper-humanize`. Splitting them out means each can also
be used alone, but here they are run in sequence.

The discipline rests on one idea: **good academic writing is a checklist applied in rounds, with the user in the
loop.** Never draft before understanding, never finish after one pass, never hand over prose that still reads as
machine-generated. This is adversarial collaboration, not one-shot generation.

## Two entry modes

The engine starts from one of two places — name which at the outset:

- **Rewrite Existing** — the user brings an existing paper/report/draft. Understand it, then strengthen it through
  the audit (argument, hedging, structure, citations). Do NOT downgrade the task to surface polish — the audit
  explicitly rejects shallow/append-only edits.
- **Build From Materials** — the user brings a materials folder (notes, data/results, figures, PDFs, partial drafts,
  experiment descriptions). Understand the materials, plan the rationale matrix, and draft from scratch.

Both modes then run the same Workflow below (understand → rationale → draft → audit → de-AI → build).

## Workflow (run every time, in order)

1. **Understand first — do not draft yet.**
   Read the user's materials: their data/results, any draft, the `scope_brief.md` (angle, target journal + limits,
   word count, themes) and the curated reference library if they exist. Note the **entry mode** (Rewrite Existing vs
   Build From Materials) and read the **scene**, **research depth**, and **output language** from the `scope_brief.md`.
   Restate, in your own words, the single core
   argument and the 3-5 supporting claims, and confirm them with the user. A beautiful paragraph built on the wrong
   claim is wasted; if you cannot restate the argument crisply, read more or ask before continuing.

2. **Lock the controlling motivation, then plan the 论证脉络矩阵 (argument-thread matrix) — not a generic template.**
   First state the paper's one-sentence red thread and split it both ways — 要论证 (the prioritized claims) and
   禁止论证 (what to NOT claim; the overclaim guardrails). Then split the work into real units (a claim, an evidence
   block, a synthesis move, a heading, a caption) and write one row each in `writing_rationale_matrix.md`, every row
   physically linked to the red thread through three non-empty anchors — 动机链接, 证据/引用锚, 文字动作 — plus its
   evidence-matched 措辞强度. Row F1 justifies the whole-work framing. **Before drafting, run the offline gate**
   `python scripts/check_argument_matrix.py writing_rationale_matrix.md` (pure stdlib, no network — works on a plain
   DeepSeek / no-VPN setup); it rejects empty anchors, generic-phrase reasons, a thin matrix, and a missing 禁止论证
   side. Do not draft until it passes. See `references/writing-craft.md` §2 for the column spec and the bar.

3. **Draft section by section, with evidence-matched hedging.**
   Write each unit to its matrix row. Match every verb to the strength of its evidence, and keep interpretation in
   Discussion, not Results — see `references/writing-craft.md` for the hedging ladder and the per-scene structures.
   The non-negotiable: a prediction stops at "predicted to / consistent with"; only a measured whole-system result
   may "confirm".

4. **Review — hand to `research-to-paper-audit`.**
   Do not self-approve. Run the audit sub-skill: three independent reviewers (claim-support, logic, citation
   integrity) plus Editor Synthesis, re-run until a round is clean. Pass the scene (journal/conference/report/review/
   competition, from the user or the `scope_brief.md` per "Target scenes") to the audit so reviewers apply
   scene-appropriate structural criteria. Apply its fixes before moving on.

5. **De-AI — hand to `research-to-paper-humanize`.**
   Run the humanize sub-skill on the reviewed draft: the five-dimension pass (长短句 / paragraph variety / density /
   connectors / term variation), a recorded humanize_matrix, and the quantitative check. Iterate until it passes.

6. **Discuss with the user at each round.**
   After understanding (step 1), after each audit round (step 4), and after de-AI (step 5), show what changed and
   what was flagged, and let the user steer. The user has the final say on every claim and edit — this is the
   "多轮对抗审查" the workflow promises.

7. **Render to output formats.** Once the user approves the final draft, hand it to **`research-to-paper-build`** to
   produce LaTeX (`.tex`), Word (`.docx`), and optionally PDF, resolving citations from the `library.bib`.

## Target scenes

The same engine produces several scenes; the structure differs (details in `references/writing-craft.md`). Pick the
scene from the user or the `scope_brief.md`, and apply that venue's length and structure limits:

- **`journal` / 论文** — IMRaD with strict Results-vs-Discussion separation, structured abstract, reproducible Methods.
- **`conference` / 会议论文** — tighter and page/length-limited; the contribution stated up front, a condensed Methods.
- **`report` / 报告** — problem → approach → findings → implications; plainer, audience-facing register.
- **`review` / 综述** — argument-driven synthesis organized by theme, not by paper; each section advances a position.
- **`competition` / 竞赛** — the novel contribution, results, and impact foregrounded against the competition's rubric.

Two more knobs come from the `scope_brief.md`:

- **Research depth** — `flash` (3 scene exemplars + 3 recent in-field papers + the venue's requirements) or `pro`
  (6 + 6); deeper orientation reading and exemplar learning at `pro`.
- **Output language** — `English` or `Chinese`; draft in it, and run `humanize_check.py --lang` to match.

## Files

- `references/writing-craft.md` — the hedging ladder, the per-scene section structures, and the 论证脉络矩阵 format (§2).
- `scripts/check_argument_matrix.py` — offline gate for the 论证脉络矩阵 (controlling-motivation doublet + per-row
  anchors + no generic reasons + row-count floor); pure stdlib, runs with no network (DeepSeek / no-VPN friendly).
- Review and de-AI live in their own sub-skills: `research-to-paper-audit` and `research-to-paper-humanize`.
