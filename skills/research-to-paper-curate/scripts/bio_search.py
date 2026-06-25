#!/usr/bin/env python3
"""Self-contained search across biology public interfaces — literature AND resources.

Covers, with no external skill and no third-party package:
  - NCBI Entrez (E-utilities): ANY NCBI database via one generic wrapper — pubmed, pmc, protein,
    nucleotide, gene, genome, taxonomy, sra, bioproject, biosample, assembly, structure, and more.
  - UniProtKB (proteins), RCSB PDB (experimental structures), AlphaFold DB (predicted structures),
    Europe PMC (literature, with a preprint filter).

Every function returns normalized dict records (id + a human label + source + the raw summary) so the
curate pipeline can ingest them. Stdlib only (urllib, json). Optional API creds come from a .env file
via _env.py: NCBI_API_KEY / NCBI_EMAIL raise NCBI from 3 to 10 requests/sec.

Usage:
  python bio_search.py <db> "<query>" [--retmax 20] [--out results.json]
  python bio_search.py protein "class IIa bacteriocin" --retmax 10
  python bio_search.py uniprot "pediocin" --out hits.json
  python bio_search.py pdb "bacteriocin"
  python bio_search.py alphafold P29430                 # query = a UniProt accession
  python bio_search.py protein "pediocin PA-1" --fetch fasta --out seqs.fasta
  python bio_search.py --list                           # known interfaces
  python bio_search.py entrez-dbs                        # live list of every NCBI database
"""
from __future__ import annotations
import sys, os, json, re, time, argparse, urllib.request, urllib.parse, urllib.error

try:                                    # optional: load API creds from a .env-style file
    from _env import load_env; load_env()
except Exception:
    pass

UA = {"User-Agent": "research-to-paper (https://github.com/Jason-0409-G/scriptorium)"}
TIMEOUT = 30
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# NCBI databases routed through the generic Entrez wrapper (any other db name also works).
NCBI_DBS = ["pubmed", "pmc", "protein", "nucleotide", "nuccore", "gene", "genome", "taxonomy",
            "sra", "bioproject", "biosample", "assembly", "structure", "ipg", "protfam",
            "cdd", "clinvar", "snp", "popset", "gds", "geoprofiles"]
# Non-NCBI bio interfaces (handled by their own functions).
OTHER = ["uniprot", "pdb", "alphafold", "europepmc", "preprints"]


def _get(url, headers=None, raw=False, tries=3):
    h = dict(UA)
    if headers:
        h.update(headers)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=TIMEOUT) as r:
                data = r.read().decode("utf-8", "replace")
            return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            # 429/403/408 are commonly transient rate-limits — EBI/AlphaFold and Cloudflare-fronted
            # services return 403 when throttled, so back-to-back agent-driven calls silently 0 out
            # if we treat 403 as permanent. Other 4xx are genuine client errors — don't retry those.
            if 400 <= e.code < 500 and e.code not in (403, 408, 429):
                return None
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    return None


# ---------------- NCBI Entrez (generic: any database) ----------------
def _ncbi_auth():
    email = os.environ.get("NCBI_EMAIL", "")
    key = os.environ.get("NCBI_API_KEY", "")
    return ("&tool=research-to-paper"
            + (f"&email={urllib.parse.quote(email)}" if email else "")
            + (f"&api_key={urllib.parse.quote(key)}" if key else ""))


_LABEL_FIELDS = ["title", "Title", "caption", "Caption", "name", "Name", "description",
                 "assemblyname", "AssemblyName", "scientificname", "ScientificName",
                 "organism_name", "organism", "subname", "expxml"]


def _summ_label(d):
    """Pick a readable label from a heterogeneous Entrez esummary record."""
    for f in _LABEL_FIELDS:
        v = d.get(f)
        if isinstance(v, str) and v.strip():
            if v.lstrip().startswith("<"):           # e.g. SRA 'expxml' is an XML blob, not a label
                m = re.search(r"<Title[^>]*>([^<]+)", v)
                if m:
                    return m.group(1).strip()
                continue                             # no <Title> → skip raw markup, try next field
            return v.strip()
        if isinstance(v, dict):                      # e.g. gene 'organism': {'scientificname': ...}
            for k in ("scientificname", "ScientificName", "name"):
                if v.get(k):
                    return str(v[k])
    return d.get("uid", "")


# ---- CAZy abbreviation → NCBI's spelled-out vocabulary (validated against live NCBI counts) ----
# NCBI esearch does literal AND-matching and does NOT index CAZy abbreviations as synonyms,
# so a natural query like "Shewanella GH3 beta-glucosidase" returns 0 even though hundreds of
# such proteins exist (their deflines read "glycoside hydrolase family 3 protein"). GH/GT need
# BOTH spellings OR'd — glycoside vs glycosyl, one word vs two — each carries records the other
# misses; PL/CE/CBM need only one form (NCBI normalizes the hyphen, counts were identical); AA
# keeps only the canonical name (adding LPMO would wrongly broaden AA1/AA2 = laccase/peroxidase).
_CAZY_EXPAND = {
    "GH":  lambda n: f'("glycoside hydrolase family {n}" OR "glycosyl hydrolase family {n}")',
    "GT":  lambda n: f'("glycosyltransferase family {n}" OR "glycosyl transferase family {n}")',
    "PL":  lambda n: f'"polysaccharide lyase family {n}"',
    "CE":  lambda n: f'"carbohydrate esterase family {n}"',
    "CBM": lambda n: f'"carbohydrate-binding module family {n}"',
    "AA":  lambda n: f'"auxiliary activity family {n}"',
}
_CAZY_RE = re.compile(r"\b(GH|GT|CBM|PL|CE|AA)(\d+)\b", re.IGNORECASE)


def _expand_cazy(term):
    """Return (expanded_term, [(abbrev, expansion), ...]); ('', []) if no CAZy token present."""
    notes = []
    def repl(m):
        cls, n = m.group(1).upper(), m.group(2)
        rew = _CAZY_EXPAND[cls](n)
        notes.append((m.group(0), rew))
        return rew
    new = _CAZY_RE.sub(repl, term)
    return (new, notes) if notes else ("", [])


def _entrez_esearch(db, term, retmax):
    r = _get(f"{EUTILS}/esearch.fcgi?db={urllib.parse.quote(db)}&retmax={retmax}"
             f"&retmode=json&term={urllib.parse.quote(term)}" + _ncbi_auth())
    es = ((r or {}).get("esearchresult") or {})
    notfound = ((es.get("errorlist") or {}).get("phrasesnotfound")) or []
    return (es.get("idlist") or []), int(es.get("count") or 0), notfound


def entrez_search(db, term, retmax=20):
    """esearch -> esummary on ANY NCBI database; returns normalized records.

    On a 0-result query containing a CAZy abbreviation (GH3, CBM20…), retry once with the
    abbreviation expanded to NCBI's spelled-out vocabulary — transparent and meaning-preserving.
    Never broadens beyond that: a still-empty result gets a diagnostic, not a blind term-drop."""
    idlist, count, notfound = _entrez_esearch(db, term, retmax)
    if not idlist:
        expanded, notes = _expand_cazy(term)
        if not expanded:
            return []
        idlist, count, notfound = _entrez_esearch(db, expanded, retmax)
        if not idlist:
            print(f"[bio] NCBI:{db} '{term}' 及展开后均 0 条。NCBI 为字面 AND 匹配、deflines 用全称；"
                  f"试着泛化某个具体词(物种限定、beta- 前缀等)再查。", file=sys.stderr)
            return []
        rew = "; ".join(f"{a}→{b}" for a, b in notes)
        print(f"[bio] NCBI:{db} '{term}' 命中 0；已展开 CAZy 缩写({rew}) 重查 → {count} 条", file=sys.stderr)
    if notfound:                                          # NCBI silently dropped unmatchable terms
        # Its automatic term mapping discards words it can't index and broadens the rest (an organism
        # name alone becomes "X"[Organism] OR X[All Fields] → millions of loose hits). The dropped
        # terms are reported in errorlist.phrasesnotfound — surface them so a relaxed result set is
        # never mistaken for a precise match. We warn rather than suppress: a real query can carry one
        # junk token among good ones, where the remaining terms still constrain the result correctly.
        print(f"[bio] NCBI:{db} 忽略了无法匹配的词 {notfound}（NCBI 索引里没有）；返回的是去掉这些词后的"
              f"宽结果(约 {count} 条命中)，可能与本意不符——请核对相关性，或改用能匹配的词。", file=sys.stderr)
    time.sleep(0.34)
    summ = _get(f"{EUTILS}/esummary.fcgi?db={urllib.parse.quote(db)}"
                f"&id={','.join(idlist)}&retmode=json" + _ncbi_auth())
    res = (summ or {}).get("result") or {}
    out = []
    for uid in res.get("uids", idlist):
        d = res.get(uid)
        if not isinstance(d, dict):
            continue
        out.append(dict(id=uid, label=_summ_label(d),
                        accession=d.get("caption") or d.get("accessionversion") or "",
                        source=f"NCBI:{db}", summary=d))
    return out


def entrez_fetch(db, term, rettype="fasta", retmode="text", retmax=20):
    """esearch -> efetch raw records (e.g. FASTA sequences) from an NCBI database."""
    ids = _get(f"{EUTILS}/esearch.fcgi?db={urllib.parse.quote(db)}&retmax={retmax}"
               f"&retmode=json&term={urllib.parse.quote(term)}" + _ncbi_auth())
    idlist = (((ids or {}).get("esearchresult") or {}).get("idlist")) or []
    if not idlist:
        return ""
    time.sleep(0.34)
    return _get(f"{EUTILS}/efetch.fcgi?db={urllib.parse.quote(db)}&id={','.join(idlist)}"
                f"&rettype={rettype}&retmode={retmode}" + _ncbi_auth(), raw=True) or ""


def entrez_dbs():
    """Live list of every NCBI Entrez database (einfo)."""
    d = _get(f"{EUTILS}/einfo.fcgi?retmode=json" + _ncbi_auth())
    return (((d or {}).get("einforesult") or {}).get("dblist")) or []


# ---------------- UniProtKB (proteins) ----------------
def _uniprot_name(e):
    """Best human label for a UniProt entry. Swiss-Prot has recommendedName, but most
    TrEMBL entries only carry a submissionName — reading recommendedName alone leaves
    ~1/3 of non-model-organism hits (e.g. Shewanella) with a blank label."""
    pd = e.get("proteinDescription") or {}
    v = ((pd.get("recommendedName") or {}).get("fullName") or {}).get("value", "")
    if v:
        return v
    for grp in ("submissionNames", "alternativeNames"):
        for nm in (pd.get(grp) or []):
            v = (nm.get("fullName") or {}).get("value", "")
            if v:
                return v
    for g in (e.get("genes") or []):
        v = (g.get("geneName") or {}).get("value", "")
        if v:
            return v
    return ""


def uniprot(query, size=20):
    d = _get("https://rest.uniprot.org/uniprotkb/search?"
             f"query={urllib.parse.quote(query)}&format=json&size={size}"
             "&fields=accession,protein_name,organism_name,length,gene_names")
    out = []
    for e in ((d or {}).get("results") or []):
        name = _uniprot_name(e)
        out.append(dict(id=e.get("primaryAccession", ""), label=name,
                        organism=(e.get("organism") or {}).get("scientificName", ""),
                        length=(e.get("sequence") or {}).get("length", ""),
                        source="UniProt", summary=e))
    return out


# ---------------- RCSB PDB (experimental structures) ----------------
def pdb(query, rows=20):
    q = {"query": {"type": "terminal", "service": "full_text", "parameters": {"value": query}},
         "return_type": "entry",
         "request_options": {"paginate": {"start": 0, "rows": rows}}}
    d = _get("https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(q)))
    out = []
    for hit in ((d or {}).get("result_set") or []):
        pid = hit.get("identifier", "")
        title = ""
        if pid and len(out) < min(rows, 25):         # title for every returned hit (cap 25 to bound per-entry calls)
            meta = _get(f"https://data.rcsb.org/rest/v1/core/entry/{pid}")
            title = ((meta or {}).get("struct") or {}).get("title", "")
            time.sleep(0.1)
        out.append(dict(id=pid, label=title, source="RCSB-PDB", summary=hit))
    return out


# ---------------- AlphaFold DB (predicted structures) ----------------
# Official UniProt accession shapes (6 or 10 chars) — used to tell an accession from free text.
_UNIPROT_ACC_RE = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$")


def _alphafold_fetch(acc):
    d = _get(f"https://alphafold.ebi.ac.uk/api/prediction/{urllib.parse.quote(acc)}")
    out = []
    for m in (d or []):
        out.append(dict(id=m.get("uniprotAccession", acc), label=m.get("uniprotDescription", ""),
                        organism=m.get("organismScientificName", ""),
                        pdb_url=m.get("pdbUrl", ""), cif_url=m.get("cifUrl", ""),
                        source="AlphaFoldDB", summary=m))
    return out


def alphafold(query, _n=None):
    """AlphaFold has no text search — it is keyed by UniProt accession. Given an accession,
    fetch directly; given free text, resolve it through UniProt and return the first candidate
    that actually HAS a predicted model (newer TrEMBL entries often have none), so the caller
    never has to look an accession up by hand."""
    q = (query or "").strip()
    first = q.split()[0].upper() if q else ""
    if _UNIPROT_ACC_RE.match(first):                       # already an accession → direct
        res = _alphafold_fetch(first)
        if not res:
            print(f"[bio] AlphaFold 无 {first} 的预测模型。", file=sys.stderr)
        return res
    cands = uniprot(q, size=8)                             # free text → resolve via UniProt
    if not cands:
        print(f"[bio] AlphaFold: '{q}' 在 UniProt 查不到蛋白，无法解析登录号。", file=sys.stderr)
        return []
    skipped = []
    for c in cands:
        acc = (c.get("id") or "").strip()
        if not acc:
            continue
        res = _alphafold_fetch(acc)
        if res:
            note = (f"[bio] AlphaFold: 解析 '{q}' → UniProt {acc} "
                    f"({(c.get('label') or '')[:40]}, {c.get('organism','')})")
            if skipped:
                note += f"；跳过前 {len(skipped)} 个无模型的({', '.join(skipped)})"
            print(note, file=sys.stderr)
            return res
        skipped.append(acc)
        time.sleep(0.2)
    print(f"[bio] AlphaFold: '{q}' 的前 {len(cands)} 个 UniProt 候选都无预测模型"
          f"(可能是较新的 TrEMBL 条目): {', '.join(skipped)}。"
          f"可换更经典的同源蛋白，或拿某个号去 PDB 找实验结构。", file=sys.stderr)
    return []


# ---------------- Europe PMC (literature, incl. preprints) ----------------
def europepmc(query, n=20, preprints_only=False):
    if preprints_only:
        query = f"({query}) AND (SRC:PPR)"
    d = _get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
             f"query={urllib.parse.quote(query)}&format=json&pageSize={n}&resultType=core")
    out = []
    for r in (((d or {}).get("resultList") or {}).get("result") or []):
        out.append(dict(id=r.get("id", ""), label=r.get("title", ""),
                        year=str(r.get("pubYear") or ""), doi=r.get("doi", ""),
                        source="EuropePMC" + (":preprint" if preprints_only else ""), summary=r))
    return out


def preprints(query, n=20):
    return europepmc(query, n, preprints_only=True)


def search(db, query, retmax=20):
    """Route a db name to the right interface."""
    db = db.lower()
    if db == "uniprot":
        return uniprot(query, retmax)
    if db == "pdb":
        return pdb(query, retmax)
    if db == "alphafold":
        return alphafold(query)
    if db == "europepmc":
        return europepmc(query, retmax)
    if db == "preprints":
        return preprints(query, retmax)
    return entrez_search(db, query, retmax)          # any NCBI database


def main():
    ap = argparse.ArgumentParser(description="Search biology public interfaces (NCBI + UniProt/PDB/AlphaFold/EuropePMC).")
    ap.add_argument("db", nargs="?", help="database / interface name, or 'entrez-dbs'")
    ap.add_argument("query", nargs="?", help="search terms (a UniProt accession for alphafold)")
    ap.add_argument("--retmax", type=int, default=20)
    ap.add_argument("--out", help="write results to this JSON (or text, with --fetch)")
    ap.add_argument("--fetch", metavar="RETTYPE", help="NCBI efetch raw records, e.g. fasta/gb (sequence dbs)")
    ap.add_argument("--list", action="store_true", help="list known interfaces and exit")
    a = ap.parse_args()

    if a.list or a.db == "--list":
        print("NCBI Entrez (any db):", ", ".join(NCBI_DBS), "...")
        print("Other interfaces:    ", ", ".join(OTHER))
        return 0
    if a.db == "entrez-dbs":
        dbs = entrez_dbs()
        print(f"[bio] NCBI databases ({len(dbs)}): " + ", ".join(dbs))
        return 0
    if not a.db or not a.query:
        ap.error("need <db> and <query> (see --list)")

    if a.fetch:
        text = entrez_fetch(a.db, a.query, rettype=a.fetch, retmax=a.retmax)
        print(f"[bio] {a.db} efetch {a.fetch}: {len(text)} chars")
        if a.out:
            with open(a.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"[bio] 写出 → {a.out}")
        elif text:
            print(text[:1500])
        return 0

    recs = search(a.db, a.query, a.retmax)
    print(f"[bio] {a.db} '{a.query}' → {len(recs)} 条")
    for r in recs[:10]:
        print(f"  · {r.get('id',''):<16} {r.get('label','')[:80]}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(recs, fh, ensure_ascii=False, indent=2)
        print(f"[bio] 写出 → {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
