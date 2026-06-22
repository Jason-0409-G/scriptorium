# Adversarial review gate

The review gate sits between DOI verification and export. Its job is to make sure nothing fabricated,
mis-attributed, or off-topic reaches the user's reference manager. A single fake-but-plausible reference
can sink a manuscript in peer review, and reviewers trust a bibliography by default — so this is the one
place where being adversarial pays off more than being helpful.

Run it on the output of `verify_doi.py` (which already tagged each paper `verified` / `mismatch` / `dead`
/ `candidate` / `no_doi`). The reviewers focus their energy on everything that is not already `verified`,
and spot-check a sample of the `verified` rows.

## How to run it

Spawn **2–3 independent reviewer agents in parallel**, each with a different lens. Independence matters:
three agents looking for the same thing is one check repeated, not three. Give each agent the full paper
list (title, authors, year, journal, DOI, verified_doi, doi_status, title_sim, category) and one lens.

Then apply the **pass/fail rule**: a paper is rejected if **any** reviewer flags it as fabricated or as a
DOI–title mismatch; it is demoted (kept, but marked "needs user confirmation") if a reviewer flags it as
off-topic or mis-categorized. Only papers with no fabrication/mismatch flag advance to export. Default to
rejecting when reviewers disagree about fabrication — a missing real paper is recoverable, a fake citation
in print is not.

## The three lenses

**Lens 1 — Existence / fabrication skeptic.**
> For each paper, decide whether it is a real, locatable publication. Treat `no_doi`, `dead`, and low
> `title_sim` rows as suspects. A real paper has a resolvable DOI whose CrossRef title matches, OR is clearly
> findable by its exact title in a known journal. Flag as FABRICATED any paper you cannot confirm exists,
> any whose journal/year/author combination looks invented, and any `mismatch` row where the DOI points at a
> different paper. Default to FABRICATED when uncertain — the cost of a fake citation is far higher than
> re-finding a real one.

**Lens 2 — Attribution / DOI-correctness checker.**
> For each paper with a DOI or verified_doi, confirm the DOI actually belongs to *this* title and authors,
> not a neighbouring paper. Catch transposed digits, a DOI copied from an adjacent row, and `candidate` DOIs
> that the title search proposed but that are not actually the same work. Flag MISMATCH with the correct DOI
> if you can find it, or UNRESOLVED if you cannot.

**Lens 3 — Relevance / categorization critic.**
> Ignore DOIs; judge fit. For each paper, decide whether it genuinely supports the user's stated topic or is
> a keyword-match accident, and whether its assigned category is right. Flag OFF-TOPIC (with one sentence of
> reasoning) and RECATEGORIZE (with the better category) as needed. Be strict: padding a reference list with
> loosely-related papers weakens it.

## Output of the gate

Produce a short verdict table the user sees before export:

```
status      title                                   action
FABRICATED  <title>                                 rejected (could not confirm it exists)
MISMATCH    <title>                                 DOI corrected to 10.xxxx/yyyy, kept
OFF-TOPIC   <title>                                 demoted (needs user confirmation)
OK          <title>                                 advances to export
```

Report counts (advanced / corrected / demoted / rejected) and list every rejection with its reason. Never
silently drop a paper — the user must see what was removed and why, so they can override if a reviewer was
wrong. The gate informs the user; it does not get the final say. The user does.
