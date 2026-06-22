#!/usr/bin/env python3
"""Cross-verify each paper's DOI against CrossRef.

Why this exists: a DOI can be (a) missing, (b) dead (resolves to nothing), or
(c) the worst case — resolvable but pointing at the WRONG paper (a transposed or
fabricated DOI). Only (b) is caught by a naive "does it resolve" check; (c) silently
corrupts a bibliography. This script catches all three by comparing the title CrossRef
returns for the DOI against the title we claimed, and by searching CrossRef by title to
propose the correct DOI when ours is missing/dead/mismatched.

Stdlib only (urllib, json, csv, difflib) so it runs anywhere without installs.

Input  : papers file (.json array of objects, or .tsv/.csv with a header row).
         Recognized fields/columns: title, doi, authors, year, journal, category, abstract.
Output : same rows + appended fields:
         doi_status   verified | mismatch | dead | candidate | no_doi
         verified_doi the confirmed-correct DOI (or a proposed candidate)
         cr_title     the title CrossRef returned (for the verified/candidate DOI)
         title_sim    0..1 similarity between claimed and CrossRef title

Usage: python verify_doi.py <papers.json|tsv|csv> <out.json|tsv|csv> [--mailto you@uni.edu]
       (mailto also read from $CROSSREF_MAILTO; CrossRef's "polite pool" is faster/kinder.)
"""
import sys, os, json, csv, time, argparse, urllib.request, urllib.parse, urllib.error
from difflib import SequenceMatcher

try:                                    # optional: load API creds from a .env-style file
    from _env import load_env; load_env()
except Exception:
    pass

CR_WORK = "https://api.crossref.org/works/"
CR_QUERY = "https://api.crossref.org/works"
SIM_OK = 0.85          # title similarity above this = same paper
THROTTLE = 0.4         # seconds between requests (be polite)
TIMEOUT = 25
UNREACHABLE = object()  # sentinel: transient failure (429/5xx) — NOT a dead DOI


def norm(s):
    return " ".join((s or "").lower().split())


def sim(a, b):
    return round(SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


def _get(url, mailto, tries=3):
    """GET JSON with polite-pool mailto + light retry. Returns dict or None."""
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}mailto={urllib.parse.quote(mailto)}"
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"research-to-paper (mailto:{mailto})"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None          # dead DOI / no record
            wait = 2 ** i
            ra = e.headers.get("Retry-After") if e.headers else None
            try:
                wait = max(wait, min(int(ra), 60))
            except (TypeError, ValueError):
                pass
            time.sleep(wait)
        except Exception:
            time.sleep(2 ** i)
    return UNREACHABLE             # exhausted on transient errors — not dead


def cr_title_of(msg):
    t = (msg or {}).get("title") or []
    return t[0] if t else ""


def lookup_doi(doi, mailto):
    """Return (cr_title, ok, reachable) for a DOI.

    ok=False means not verified; reachable=False means CrossRef was never
    reached (transient 429/5xx) so the DOI must NOT be called dead.
    """
    if not doi:
        return "", False, True
    data = _get(CR_WORK + urllib.parse.quote(doi.strip()), mailto)
    if data is UNREACHABLE:
        return "", False, False
    if not data or "message" not in data:
        return "", False, True
    return cr_title_of(data["message"]), True, True


def search_title(title, mailto):
    """Search CrossRef by title; return (best_doi, best_title, similarity)."""
    if not title:
        return "", "", 0.0
    url = f"{CR_QUERY}?query.bibliographic={urllib.parse.quote(title)}&rows=3"
    data = _get(url, mailto)
    items = ((data or {}).get("message") or {}).get("items") or []
    best = ("", "", 0.0)
    for it in items:
        ct = cr_title_of(it)
        s = sim(title, ct)
        if s > best[2]:
            best = (it.get("DOI", ""), ct, s)
    return best


def classify(row, mailto):
    """Decide doi_status + verified_doi + cr_title + title_sim for one paper."""
    title = row.get("title", "")
    doi = (row.get("doi", "") or "").strip()
    if doi:
        ct, ok, reachable = lookup_doi(doi, mailto)
        time.sleep(THROTTLE)
        if ok:
            s = sim(title, ct)
            if s >= SIM_OK:
                return dict(doi_status="verified", verified_doi=doi, cr_title=ct, title_sim=s)
            # resolves but wrong paper → find the right one by title
            bdoi, bct, bs = search_title(title, mailto); time.sleep(THROTTLE)
            return dict(doi_status="mismatch", verified_doi=(bdoi if bs >= SIM_OK else ""),
                        cr_title=ct, title_sim=s)
        # not ok: dead only if CrossRef was actually reached; else merely throttled
        status = "dead" if reachable else "unverified"
        bdoi, bct, bs = search_title(title, mailto); time.sleep(THROTTLE)
        return dict(doi_status=status, verified_doi=(bdoi if bs >= SIM_OK else ""),
                    cr_title=bct, title_sim=bs)
    # no DOI at all → propose one from title search
    bdoi, bct, bs = search_title(title, mailto); time.sleep(THROTTLE)
    if bdoi and bs >= SIM_OK:
        return dict(doi_status="candidate", verified_doi=bdoi, cr_title=bct, title_sim=bs)
    return dict(doi_status="no_doi", verified_doi="", cr_title=bct, title_sim=bs)


# ---- IO: support .json array or .tsv/.csv with header ----
def read_rows(path):
    if path.lower().endswith(".json"):
        data = json.load(open(path, encoding="utf-8"))
        return data if isinstance(data, list) else data.get("papers", [])
    delim = "\t" if path.lower().endswith(".tsv") else ","
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f, delimiter=delim)]


def write_rows(path, rows):
    if path.lower().endswith(".json"):
        json.dump(rows, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return
    delim = "\t" if path.lower().endswith(".tsv") else ","
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=delim)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile"); ap.add_argument("outfile")
    ap.add_argument("--mailto", default=os.environ.get("CROSSREF_MAILTO", "research-to-paper@example.com"))
    a = ap.parse_args()

    rows = read_rows(a.infile)
    if not rows:
        sys.exit("[verify_doi] 输入为空 / empty input")
    print(f"[verify_doi] {len(rows)} 篇 · CrossRef polite pool mailto={a.mailto}")
    counts = {}
    for i, r in enumerate(rows, 1):
        res = classify(r, a.mailto)
        r.update(res)
        counts[res["doi_status"]] = counts.get(res["doi_status"], 0) + 1
        flag = "" if res["doi_status"] == "verified" else "  <-- 需人工确认 review"
        print(f"  [{i}/{len(rows)}] {res['doi_status']:9} sim={res['title_sim']}  "
              f"{(r.get('title','') or '')[:60]}{flag}")
    write_rows(a.outfile, rows)
    print(f"\n[verify_doi] 写出 → {a.outfile}")
    print(f"[verify_doi] 统计: {counts}")
    bad = sum(v for k, v in counts.items() if k != "verified")
    if bad:
        print(f"[verify_doi] ⚠ {bad} 篇非 verified(mismatch/dead/candidate/no_doi)→ 进对抗审查门,勿直接导入")


if __name__ == "__main__":
    main()
