---
name: research-to-paper-write
description: >-
  Draft and revise a 综述 (review) / 报告 (report) / 论文 (paper) end to end. It understands the content first,
  plans a per-unit writing rationale (not a generic IMRaD template), and drafts with evidence-matched hedging,
  then runs the review and de-AI passes through its companion sub-skills research-to-paper-audit (independent
  multi-reviewer rounds) and research-to-paper-humanize (five-dimension de-AI incl. 长短句), discussing with the
  user at each round. Depends on no skill outside this plugin. Use whenever the user wants to write or rewrite a
  paper, review, or report, says 帮我写论文/综述/报告, 把这些内容写成稿子, 改写这篇草稿, 按我的写作纪律来,
  "draft this into a paper", "rewrite this manuscript", "write up these results". Reads an optional scope_brief.md
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

## Workflow (run every time, in order)

1. **Understand first — do not draft yet.**
   Read the user's materials: their data/results, any draft, the `scope_brief.md` (angle, target journal + limits,
   word count, themes) and the curated reference library if they exist. Restate, in your own words, the single core
   argument and the 3-5 supporting claims, and confirm them with the user. A beautiful paragraph built on the wrong
   claim is wasted; if you cannot restate the argument crisply, read more or ask before continuing.

2. **Plan a writing rationale matrix — not a generic template.**
   Split the work into real units (a claim, an evidence block, a synthesis move, a heading, a caption), not a fixed
   IMRaD checklist. For each, write one row in `writing_rationale_matrix.md`: the claim, the evidence behind it, the
   rhetorical move, the hedge level its evidence allows, and the source it leans on. Row 1 justifies the whole-work
   framing (why this angle, for this journal/reader). A generic matrix produces a generic paper.

3. **Draft section by section, with evidence-matched hedging.**
   Write each unit to its matrix row. Match every verb to the strength of its evidence, and keep interpretation in
   Discussion, not Results — see `references/writing-craft.md` for the hedging ladder and the per-scene structures.
   The non-negotiable: a prediction stops at "predicted to / consistent with"; only a measured whole-system result
   may "confirm".

4. **Review — hand to `research-to-paper-audit`.**
   Do not self-approve. Run the audit sub-skill: three independent reviewers (claim-support, logic, citation
   integrity) plus Editor Synthesis, re-run until a round is clean. Apply its fixes before moving on.

5. **De-AI — hand to `research-to-paper-humanize`.**
   Run the humanize sub-skill on the reviewed draft: the five-dimension pass (长短句 / paragraph variety / density /
   connectors / term variation), a recorded humanize_matrix, and the quantitative check. Iterate until it passes.

6. **Discuss with the user at each round.**
   After understanding (step 1), after each audit round (step 4), and after de-AI (step 5), show what changed and
   what was flagged, and let the user steer. The user has the final say on every claim and edit — this is the
   "多轮对抗审查" the workflow promises.

7. **Render to output formats.** Once the user approves the final draft, hand it to **`research-to-paper-build`** to
   produce LaTeX (`.tex`), Word (`.docx`), and optionally PDF, resolving citations from the `library.bib`.

## Three versions

The same engine produces three scenes; the structure differs (details in `references/writing-craft.md`):

- **综述 / review** — argument-driven synthesis organized by theme, not by paper; each section advances a position.
- **报告 / report** — problem → approach → findings → implications; plainer, audience-facing register.
- **论文 / paper** — IMRaD with strict Results-vs-Discussion separation, structured abstract, reproducible Methods.

Pick the scene from the user or the `scope_brief.md`, and apply that journal's length and structure limits.

## Files

- `references/writing-craft.md` — the hedging ladder, the per-scene section structures, and the rationale-matrix format.
- Review and de-AI live in their own sub-skills: `research-to-paper-audit` and `research-to-paper-humanize`.
