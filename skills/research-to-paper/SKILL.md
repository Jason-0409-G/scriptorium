---
name: research-to-paper
description: >-
  Umbrella, fully self-contained workflow that takes a research idea all the way to a submission-ready manuscript,
  depending on NO other skill. It chains stages you can also run on their own: SCOPE (research the field, discuss
  directions one question at a time, lock angle/target journal/word count), CURATE (build a DOI-verified library —
  RIS for Zotero/EndNote + by-category Excel — behind a multi-agent review), WRITE (draft, then review and de-AI),
  and BUILD (render to LaTeX/Word/PDF). WRITE is backed by an AUDIT step (independent multi-reviewer rounds) and a
  HUMANIZE step (five-dimension de-AI incl. 长短句). Use whenever a request spans more than one stage, for example
  帮我从定方向到写出来, 做文献综述, 整理文献库并核对DOI再写论文, 从一个想法做到初稿, 我想投某期刊先定方向再建库再写,
  按我的流程写论文/综述/报告, "take this idea to a written, formatted paper". For a single piece, use the sub-skill
  directly — angle/journal → research-to-paper-scope; verify references / export a library → research-to-paper-curate;
  draft or rewrite → research-to-paper-write; review/audit a draft → research-to-paper-audit; de-AI / 降AI率 →
  research-to-paper-humanize; export to LaTeX/Word/PDF → research-to-paper-build.
---

# Research-to-Paper (orchestrator)

Entry point for a self-contained workflow. Nothing here calls another plugin — search, verification, review,
writing, de-AI, and format rendering all live in this skill's seven sub-skills, so it works standalone (a
collaborator installs this one plugin and has everything). Find which stage the user is at, run the stages they
need in order, and pass each stage's output into the next.

## The stages

1. **SCOPE — decide the direction** → **`research-to-paper-scope`**.
   Reads authoritative literature, then confirms an angle, scope, **target journal**, and **word count** one step at
   a time, and looks up the journal's author requirements once chosen. Output: `scope_brief.md`. Skip only if the
   user already has a confirmed direction.

2. **CURATE — build a verified library** → **`research-to-paper-curate`**.
   Built-in five-source search, per-paper CrossRef DOI verification, a multi-agent adversarial review gate, then
   export to RIS (Zotero/EndNote) + BibTeX + a by-category Excel. The SCOPE themes become the categories.

3. **WRITE — draft, review, de-AI** → **`research-to-paper-write`**, which orchestrates two companion sub-skills:
   **`research-to-paper-audit`** (independent multi-reviewer rounds) and **`research-to-paper-humanize`**
   (five-dimension de-AI incl. 长短句). Understands the content first, plans a per-unit rationale, drafts with
   evidence-matched hedging, then audits until clean and de-AIs — discussing with the user each round. Scenes:
   `review` (综述) / `report` (报告) / `journal` (论文).

4. **BUILD — render to formats** → **`research-to-paper-build`**.
   Turns the approved manuscript into LaTeX (`.tex`), Word (`.docx`), and optionally PDF via pandoc, resolving
   citations from the `library.bib`.

## How to route

- Vague idea → SCOPE → CURATE → WRITE → BUILD.
- Has a direction, needs references → CURATE → WRITE → BUILD.
- Has direction + library, wants to write → WRITE → BUILD.
- "Verify these DOIs" / "export to EndNote" → CURATE.
- "Help me figure out the angle / which journal" → SCOPE.
- "Draft / rewrite this" → WRITE.
- "Review / audit this draft" / "查无据claim" → research-to-paper-audit.
- "降AI率 / de-AI this" / "长短句" → research-to-paper-humanize.
- "导出 LaTeX/Word/PDF" / "转成 docx" → research-to-paper-build.

Each stage is independently useful, so don't force the full pipeline when the user asked for one piece. Hand off
cleanly and tell the user what each produced before moving on.
