---
name: research-to-paper-curate
description: >-
  Build a trustworthy literature library with NO dependency on any other skill: search several databases, verify
  every DOI against CrossRef (catching dead DOIs and the worse case of a DOI that resolves to the wrong paper),
  run a multi-agent adversarial review to reject fabricated or mis-attributed references, then export a single RIS
  that imports into both Zotero and EndNote, plus BibTeX and a by-category, color-coded Excel. Use whenever the
  user wants to collect, check, or export references, e.g. 整理文献库, 把这批参考文献核对一下DOI, 核对引用是否真实,
  导成能进EndNote或Zotero的库, 给文献配个分类Excel, "verify these DOIs", "check these citations are real",
  "export these papers to EndNote", "build me a reference library". Runs the bundled scripts search_papers.py,
  verify_doi.py and export_refs.py; takes optional category themes from a scope_brief.md.
---

# Curate — build a DOI-verified literature library

A reference list is trusted by default in peer review, so a single wrong DOI or fabricated paper does real damage
and is hard to spot later. This stage makes the library trustworthy before it reaches the user's reference
manager. Everything runs from bundled scripts — no other skill is required. Run the steps in order; never skip the
DOI gate or the review gate.

If a `scope_brief.md` exists (from `research-to-paper-scope`), use its core themes as the categories and its angle
to judge relevance. Otherwise infer reasonable categories from the topic and confirm them with the user.

## Step 1 — Search

Run `scripts/search_papers.py "<query>" <papers.json>`. It queries PubMed, Semantic Scholar, and CrossRef, then
merges and de-duplicates by DOI → normalized title — all with stdlib, no installs, no external skill. Set
`CROSSREF_MAILTO` / `NCBI_EMAIL` to be polite to the APIs. Then assign each paper a `category` from the scope
themes. If the user already pasted a reference list, skip the search and start from their list.

## Step 2 — Verify every DOI

Run `scripts/verify_doi.py <papers> <verified>`. It queries CrossRef for each DOI, confirms the record resolves,
and compares the returned title against the claimed title — so a DOI that resolves to the *wrong* paper is caught,
not just a dead one. For missing/dead/mismatched DOIs it searches CrossRef by title and proposes the correct DOI.
Treat any row that is not `verified` as unresolved until the review gate or the user confirms it.

## Step 3 — Adversarial review gate

Before exporting, spawn 2-3 independent reviewer agents, each with a different lens (existence/fabrication,
DOI-attribution, relevance/categorization). The exact prompts and the pass/fail rule are in
`references/adversarial-review.md`. A paper advances only if no reviewer flags it as fabricated or DOI-mismatched;
off-topic or mis-categorized papers are demoted (kept, marked "needs user confirmation"), not silently dropped.
Show the user a verdict table with a reason for every rejection — the gate informs the user; the user decides.

## Step 4 — Export

Run `scripts/export_refs.py <verified> <outdir>`. It writes `library.ris` (imports natively into both Zotero and
EndNote — no API or credentials needed), `library.bib` (LaTeX), and `library.xlsx` (by-category, color-coded; falls
back to `.csv` if openpyxl is missing). Tell the user to import `library.ris` into whichever manager they use.

## Deliver

Report how many papers passed, how many DOIs were corrected (before/after), and what the reviewers rejected and
why, then point to the three library files. If this was part of the full workflow, pass the verified library to
`research-to-paper-write` together with the `scope_brief.md`.

## Files

- `scripts/search_papers.py` — self-contained multi-database search (PubMed + Semantic Scholar + CrossRef).
- `scripts/verify_doi.py` — CrossRef DOI cross-verification.
- `scripts/export_refs.py` — RIS + BibTeX + by-category Excel export.
- `references/adversarial-review.md` — reviewer-agent prompts, lenses, pass/fail rule.
