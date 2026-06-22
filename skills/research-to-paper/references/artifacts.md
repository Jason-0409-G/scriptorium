# Workspace & key artifacts

A complete run should leave more than a final paper: it should leave an auditable trail showing how the
manuscript was reasoned into existence — which direction was chosen, which references were verified, why each
unit was written the way it was, what review caught, and what de-AI changed. That trail lives in a single working
directory, `manuscript_workspace/`, so any stage (or the user) can pick up where another left off.

Scaffold it once at the start of a run:

```
python <plugin>/skills/research-to-paper/scripts/new_workspace.py manuscript_workspace
```

When the skills are installed under `~/.claude/skills/` (or `~/.codex/skills/`), call the scripts from there, e.g.
`~/.claude/skills/research-to-paper/scripts/new_workspace.py`.

## The artifact set

| Artifact | Stage | What it records |
|---|---|---|
| `scope_brief.md` | scope | The direction contract: angle, target journal + its author requirements, word count, core themes. |
| `library/library.ris` | curate | Reference library for Zotero/EndNote (single-file import). |
| `library/library.bib` | curate | BibTeX for pandoc/LaTeX citation resolution. |
| `library/library.xlsx` (or `.csv`) | curate | By-category, color-coded library for the human to prune. |
| `library/doi_report.md` | curate | Per-reference DOI verification status and any corrected DOIs. |
| `writing_rationale_matrix.md` | write | Per-unit reasoning: claim, evidence, rhetorical move, hedge level, source. |
| `draft.md` | write | The working manuscript, with `[@key]` citation markers. |
| `audit_report.md` | audit | The three independent reviews + Editor Synthesis, one block per round, until clean. |
| `humanize_matrix.md` | humanize | Every de-AI change, tagged by dimension (D1–D5) with the reason. |
| `final/main.tex`, `final/manuscript.docx`, `final/manuscript.pdf` | build | Rendered submission formats. |
| `artifact_manifest.md` | (generated) | Index of which artifacts exist, written by `artifact_check.py`. |

The two artifacts that carry the most reasoning are `writing_rationale_matrix.md` (why the manuscript is shaped
the way it is) and `audit_report.md` (what independent review found and how it was resolved). A run that produces
a polished `draft.md` but an empty rationale matrix has skipped the part that makes the writing defensible.

## Check commands

Each check is a standard-library Python script; run the ones relevant to the stage you are verifying.

- **Reference DOIs resolve and match** (curate):
  `python skills/research-to-paper-curate/scripts/verify_doi.py <papers.json> <verified.json>`
- **Citations in the draft resolve to the library** (write → build):
  `python skills/research-to-paper/scripts/cite_check.py manuscript_workspace/draft.md manuscript_workspace/library/library.bib`
- **De-AI signature is within human range** (humanize):
  `python skills/research-to-paper-humanize/scripts/humanize_check.py manuscript_workspace/draft.md --lang zh`
- **Artifact trail is complete** (orchestrator):
  `python skills/research-to-paper/scripts/artifact_check.py manuscript_workspace --write`
- **Unit tests for the check scripts**:
  `python -m unittest discover -s tests`

## What this prevents

The workspace and the checks exist to make specific failure modes impossible to pass silently:

- A draft that reads well but rests on an unverified or mis-attributed reference → caught by `verify_doi.py` and the curate review gate.
- A citation marker with no matching bibliography entry → caught by `cite_check.py` before build.
- Prose uniform enough to read as machine-generated → caught by `humanize_check.py`.
- A "finished" run that quietly skipped the rationale matrix or the audit → caught by `artifact_check.py`.
- Editing only sentences while leaving the argument's logic unexamined → the audit writes `audit_report.md`, and the rationale matrix forces per-unit justification, so the logic is reviewed, not just the surface.
