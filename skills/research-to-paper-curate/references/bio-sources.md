# Biology public interfaces (literature + resources)

`bio_search.py` searches biology public databases with the standard library only — no external skill, no
third-party package. It complements `search_papers.py` (which covers literature): use this when the user needs
**resources** (sequences, structures, genes, taxa, assemblies) as well as papers.

```
python scripts/bio_search.py <db> "<query>" [--retmax 20] [--out results.json]
python scripts/bio_search.py --list          # known interfaces
python scripts/bio_search.py entrez-dbs       # live list of every NCBI database (einfo)
```

## NCBI Entrez (any database)

One generic wrapper covers **every** NCBI Entrez database via E-utilities (esearch → esummary), so the same call
works for literature, sequences, genes, taxa, structures, and more:

| db | holds |
|---|---|
| `pubmed`, `pmc` | literature, full text |
| `protein`, `nucleotide` / `nuccore`, `ipg` | sequences |
| `gene`, `genome`, `assembly` | genes / genomes / assemblies |
| `taxonomy` | organisms |
| `sra`, `bioproject`, `biosample` | sequencing projects / samples |
| `structure` | macromolecular structures (MMDB) |
| `protfam`, `cdd`, `clinvar`, `snp`, ... | families / domains / variants |

`--fetch fasta` (or `gb`) runs efetch instead of esummary to pull the raw records, e.g.
`bio_search.py protein "pediocin PA-1" --fetch fasta --out seqs.fasta`.

## Non-NCBI interfaces

| name | source | returns |
|---|---|---|
| `uniprot` | UniProtKB REST | proteins (accession, name, organism, length) |
| `pdb` | RCSB PDB search + data API | experimental structures (PDB id + title) |
| `alphafold` | AlphaFold DB API | predicted structures for a **UniProt accession** (model + cif/pdb URLs) |
| `europepmc` | Europe PMC | literature; `preprints` filters to preprints (SRC:PPR) |

`alphafold`'s "query" is a UniProt accession (e.g. `bio_search.py alphafold P29430`), not free text.

## API access at a glance

Every search/lookup interface below is a **free, public API** — none require a key to read. Keys are optional and
only raise rate limits. The single exception is the Zotero *write* import, which needs a key because it writes into
your account.

| Interface | For | Key to read? | Without a key | With a key | Where to get the key |
|---|---|---|---|---|---|
| OpenAlex | literature | No | free; add an email (`CROSSREF_MAILTO`) for the faster polite pool | optional token | openalex.org |
| Crossref | literature / DOI verify | No | free; email → polite pool (faster) | — | — (just the email) |
| Europe PMC | literature + preprints | No | free, generous limits | — | — |
| PubMed / **NCBI Entrez** (every db) | papers + protein / nucleotide / gene / taxonomy / assembly / structure / SRA … | No | **3 requests/sec** (add `NCBI_EMAIL`) | **10 requests/sec** | ncbi.nlm.nih.gov account → Settings → API Key Management |
| Semantic Scholar | literature | No | shared public pool (can be throttled) | higher, dedicated rate limit | semanticscholar.org/product/api |
| UniProtKB | proteins | No | free; no key exists | — | — |
| RCSB PDB | experimental structures | No | free; no key exists | — | — |
| AlphaFold DB | predicted structures | No | free; no key exists | — | — |
| **Zotero** (direct import) | write refs into your library | **Yes — write** | n/a; falls back to a `.ris` file | one collection per category, pushed straight in | zotero.org/settings/keys (write access) + your numeric userID |
| EndNote | reference manager | No public API | always a `.ris` file (File → Import) | — | — (no public item-creation API) |

Bottom line: you can run **every search** — papers, sequences, structures, genomes, taxa — with **no keys at all**
(this is exactly how the live tests in this repo were run). A key only buys speed (NCBI / Semantic Scholar) or
unlocks the Zotero direct-push.

## API credentials (all optional)

Credentials are read from a `.env` file by `_env.py`, searched in this order — the first that exists wins, and a
real exported environment variable always beats the file:

1. `$RESEARCH_TO_PAPER_ENV` (explicit path)
2. `./.env` (current/working folder)
3. `~/.config/research-to-paper/keys.env`

Copy `.env.example` to one of those and fill in what you have. Nothing here requires a key:

| variable | effect |
|---|---|
| `CROSSREF_MAILTO`, `NCBI_EMAIL` | join the faster "polite pool" (just an email, no signup) |
| `NCBI_API_KEY` | NCBI 3 → 10 requests/sec across every Entrez db |
| `S2_API_KEY` | higher Semantic Scholar rate limit |
| `OPENALEX_API_KEY` | optional; a mailto already gets the polite pool |
| `ZOTERO_API_KEY` + `ZOTERO_USER_ID` (or `ZOTERO_GROUP_ID`) | enable direct import into Zotero (`push_zotero.py`) |

EndNote exposes no public item-creation API, so there is no direct-push for it — `export_refs.py` writes a `.ris`
that EndNote imports natively (File → Import).

## Bring your own key — never commit one

API keys are **personal credentials tied to your account**; never paste one into the repo or any committed file.
A key pushed to a public repo is scraped within minutes, auto-revoked by GitHub secret-scanning or the provider,
and — if it were shared — throttled or banned because everyone would hammer it at once (the exact shared-pool
problem a key is meant to avoid). The whole `.env` design exists to keep keys **out of version control**:

- The skill works with **no key at all** — four key-free literature sources (OpenAlex, Crossref, Europe PMC, and
  NCBI's no-key tier) plus every key-free resource source (UniProt, RCSB PDB, AlphaFold) cover a query even when
  Semantic Scholar's shared pool is throttling and returns 0.
- Each user supplies **their own free key** in a local, gitignored `.env` — never a shared one.
- A Semantic Scholar key takes ~2 minutes: request it at <https://www.semanticscholar.org/product/api>, then put it
  in `.env` as `S2_API_KEY=...`. Same idea for `NCBI_API_KEY`.

For zero-setup "just works" behaviour, lean on the always-key-free sources and treat the S2 / NCBI keys as an
optional speed-up, not a requirement.
