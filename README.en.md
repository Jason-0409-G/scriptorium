# research-to-paper

> English ｜ [中文](README.md)

A fully **self-contained** academic-writing skill that takes a research idea all the way to a submission-ready
manuscript — from **deciding the direction**, to a **DOI-verified reference library**, to a **drafted, reviewed,
de-AI'd** paper, to **LaTeX / Word / PDF** output. It depends on **no other skill**: install this one plugin and
you have the whole pipeline.

Works in **Claude Code** and **Codex**.

---

## Install

### Claude Code

**Option 1 · Plugin marketplace (recommended)**

```
/plugin marketplace add Jason-0409-G/skill_writing
/plugin install research-to-paper@skill-writing
/reload-plugins
```

**Option 2 · Script (clone, then install locally)**

```bash
git clone https://github.com/Jason-0409-G/skill_writing.git
cd skill_writing
bash install.sh claude          # macOS / Linux
# Windows PowerShell:  .\install.ps1 -Target claude
```
Restart Claude Code, then just ask it to "follow the research-to-paper workflow".

### Codex

```bash
git clone https://github.com/Jason-0409-G/skill_writing.git
cd skill_writing
bash install.sh codex           # macOS / Linux
# Windows PowerShell:  .\install.ps1 -Target codex
```
The script copies the seven skills into `~/.codex/skills/` (Claude Code uses `~/.claude/skills/`). Restart Codex to
use them. `bash install.sh all` installs to both at once.

---

## What each sub-skill does

| Sub-skill | Purpose |
|---|---|
| **research-to-paper** | Orchestrator. Detects which stage you're at and routes the request through **scope → curate → write → build** as needed; each stage is also usable on its own. |
| **research-to-paper-scope** | **Decide the direction.** Reads authoritative literature first to understand the field, then confirms — one question at a time — the angle, scope, **target journal**, **word count**, and core themes; once the journal is set it **looks up that journal's author requirements** online (aims & scope, article types, length, structure, citation style). Produces `scope_brief.md`. |
| **research-to-paper-curate** | **Build the library.** Five-source search (OpenAlex / Europe PMC / PubMed / Semantic Scholar / Crossref) → per-paper **CrossRef DOI verification** (catching dead DOIs *and* DOIs that resolve to the wrong paper, recovering the correct one) → **multi-agent adversarial review** that rejects fabricated or mis-attributed references → export to **RIS (Zotero/EndNote) + BibTeX + a by-category, color-coded Excel**. |
| **research-to-paper-write** | **Draft.** Understands the content first and restates the core argument with you, plans a **per-unit rationale matrix** (not a generic IMRaD template), and drafts with **evidence-matched hedging** (a model/gene only "predicts"; a measured whole-system result may "confirm"). Orchestrates the audit and humanize passes. Scenes: review / report / paper. |
| **research-to-paper-audit** | **Multi-round adversarial review.** Spawns **three independent reviewer agents** (claim-support / logic & structure / citation integrity) plus an Editor Synthesis, and re-runs **until a round is clean**. Catches over-claims, unsupported claims, interpretation leaking into Results, shallow edits, and citations that don't support their sentence. Usable standalone ("review this draft"). |
| **research-to-paper-humanize** | **De-AI.** Reworks prose along **five dimensions**: **D1 sentence length (long–short variation)**, D2 paragraph-structure variety, D3 information-density alternation, D4 connector control (removing AI-frequent connectors), D5 term-context variation — at a light/medium/heavy tier, recording every change in `humanize_matrix.md` and verifying with `humanize_check.py`. Usable standalone ("de-AI this paragraph"). |
| **research-to-paper-build** | **Render formats.** Uses pandoc to turn the finished manuscript into **LaTeX (.tex) / Word (.docx) / PDF**, resolving `[@key]` citations from `library.bib` into a reference list. |

Each piece **triggers on its own**: "verify these DOIs", "de-AI this paragraph", "audit my draft", "export to Word"
all hit the right sub-skill directly.

---

## Dependencies

Everything is Python **stdlib** except these optional tools (each step degrades gracefully or tells you what to
install):

- **`openpyxl`** (Python) — for the styled `.xlsx`; without it, curate writes a `.csv` instead (RIS/BibTeX unaffected).
- **`pandoc`** — required by `research-to-paper-build` for LaTeX/Word output (`brew install pandoc` / `apt install pandoc` / winget on Windows).
- **A TeX engine** (xelatex/pdflatex) — only for PDF; without it you still get the `.tex` to compile elsewhere.
- Set **`CROSSREF_MAILTO`** / **`NCBI_EMAIL`** to your email so the APIs put you in their faster polite pool.

---

## Usage

Just ask, for example:

- "I have a research direction but haven't fixed the angle yet — scope it, build a verified library, then write it as a review."
- "Verify the DOIs in these references, drop the fake ones, and give me a RIS for EndNote."
- "De-AI this paragraph, vary the sentence length." / "Audit this draft for over-claims."
- "Export this manuscript to LaTeX and Word."

The orchestrator runs only the stages you need and tells you what each produced before moving on.

---

## Validate (after editing the plugin)

```
claude plugin validate .
```
