---
name: research-to-paper-curate
description: >-
  Build a trustworthy literature library with NO dependency on any other skill: search five literature databases
  (OpenAlex, Europe PMC, PubMed, Semantic Scholar, CrossRef), verify every DOI against CrossRef (catching dead DOIs
  and the worse case of a DOI that resolves to the wrong paper), run a multi-agent adversarial review to reject
  fabricated or mis-attributed references, then either import straight into Zotero (via its Web API, one collection
  per category, when ZOTERO_API_KEY is set) or export a single RIS that imports into both Zotero and EndNote, plus
  BibTeX and a by-category, color-coded Excel. It also searches biology RESOURCE databases — any NCBI Entrez db
  (protein, nucleotide, gene, taxonomy, assembly, structure, SRA, BioProject, ...) plus UniProt, RCSB PDB, AlphaFold
  and Europe PMC. Use whenever the user wants to collect, check, search, or export references or bio records, e.g.
  整理文献库, 把这批参考文献核对一下DOI, 核对引用是否真实, 导成能进EndNote或Zotero的库, 直接导入Zotero, 给文献配个分类Excel,
  搜NCBI/蛋白/序列/结构数据库, "verify these DOIs", "check these citations are real", "export these papers to EndNote",
  "search UniProt/PDB/NCBI", "build me a reference library". Runs the bundled scripts search_papers.py, verify_doi.py,
  export_refs.py, bio_search.py and push_zotero.py; takes optional category themes from a scope_brief.md.
---

# Curate — build a DOI-verified literature library

A reference list is trusted by default in peer review, so a single wrong DOI or fabricated paper does real damage
and is hard to spot later. This stage makes the library trustworthy before it reaches the user's reference
manager. Everything runs from bundled scripts — no other skill is required. Run the steps in order; never skip the
DOI gate or the review gate.

If a `scope_brief.md` exists (from `research-to-paper-scope`), use its core themes as the categories and its angle
to judge relevance. Otherwise infer reasonable categories from the topic and confirm them with the user.

## Step 1 — Search

Run `scripts/search_papers.py "<query>" <papers.json>`. It queries five sources — OpenAlex, Europe PMC, PubMed,
Semantic Scholar, and CrossRef — then merges and de-duplicates by DOI → normalized title, all with stdlib, no
installs, no external skill. Then assign each paper a `category` from the scope themes. If the user already pasted a
reference list, skip the search and start from their list.

For biology **resource** databases (sequences, structures, genes, taxa — not just papers), use
`scripts/bio_search.py <db> "<query>"`: any NCBI Entrez database (protein, nucleotide, gene, taxonomy, assembly,
structure, SRA, BioProject, ...) plus UniProt, RCSB PDB, AlphaFold and Europe PMC. `bio_search.py --list` shows the
interfaces; `--fetch fasta` pulls sequences. Details in `references/bio-sources.md`.

API credentials are optional and read from a `.env` file (see `.env.example` + `references/bio-sources.md`): setting
`CROSSREF_MAILTO` / `NCBI_EMAIL` joins the faster polite pool, and `NCBI_API_KEY` / `S2_API_KEY` raise rate limits.
Nothing here requires a key.

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

## Step 4 — Import or export (branch on credentials)

Two paths, chosen by whether Zotero credentials are present:

- **Direct import to Zotero** — if `ZOTERO_API_KEY` + `ZOTERO_USER_ID` (or `ZOTERO_GROUP_ID`) are set, run
  `scripts/push_zotero.py <verified>`. It creates one Zotero collection per category and pushes the verified items
  straight into the user's library through the Zotero Web API. This writes to their library, so confirm first;
  `--dry-run` previews the payload without posting.
- **Import file** — otherwise (and always for EndNote, which exposes no public item-creation API), run
  `scripts/export_refs.py <verified> <outdir>`. It writes `library.ris` (imports natively into both Zotero and
  EndNote), `library.bib` (LaTeX), and `library.xlsx` (by-category, color-coded; falls back to `.csv` if openpyxl is
  missing). Tell the user to import `library.ris` (File → Import) into whichever manager they use.

## Deliver

Report how many papers passed, how many DOIs were corrected (before/after), and what the reviewers rejected and
why, then point to the three library files. If this was part of the full workflow, pass the verified library to
`research-to-paper-write` together with the `scope_brief.md`.

## Files

- `scripts/search_papers.py` — five-source literature search (OpenAlex + Europe PMC + PubMed + Semantic Scholar + CrossRef).
- `scripts/bio_search.py` — biology resource search: any NCBI Entrez db + UniProt / RCSB PDB / AlphaFold / Europe PMC.
- `scripts/verify_doi.py` — CrossRef DOI cross-verification.
- `scripts/export_refs.py` — RIS + BibTeX + by-category Excel (the no-credentials import file).
- `scripts/push_zotero.py` — direct import into Zotero via its Web API (when credentials are set).
- `scripts/_env.py` — loads optional API credentials from a `.env` file.
- `references/adversarial-review.md` — reviewer-agent prompts, lenses, pass/fail rule.
- `references/bio-sources.md` — every integrated interface + credentials setup.
