#!/usr/bin/env python3
"""Check that citation keys in a draft resolve against a library.bib, and report unused entries.

Prevents two common errors before BUILD: a citation marker in the prose that has no matching
bibliography entry (pandoc/LaTeX would drop or fail to render it), and library entries that the
manuscript never actually cites. Stdlib only — no third-party dependency.
"""
from __future__ import annotations
import argparse
import re
import sys

# pandoc citation key: @key, where @ is NOT preceded by an alphanumeric. The negative lookbehind
# excludes emails like user@host, whose @ follows a word character.
_PANDOC = re.compile(r"(?<![A-Za-z0-9])@([A-Za-z0-9][A-Za-z0-9_:.\-]*)")
# LaTeX \cite / \citep / \citet{a,b}
_LATEX = re.compile(r"\\cite[a-zA-Z]*\{([^}]*)\}")
# bibtex entry key: @article{key,
_BIBKEY = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def cited_keys(text: str) -> set[str]:
    keys = set(_PANDOC.findall(text))
    for grp in _LATEX.findall(text):
        for k in grp.split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


def bib_keys(text: str) -> set[str]:
    return set(_BIBKEY.findall(text))


def check(draft_text: str, bib_text: str) -> dict:
    cited = cited_keys(draft_text)
    defined = bib_keys(bib_text)
    return {
        "cited": cited,
        "defined": defined,
        "unresolved": sorted(cited - defined),
        "unused": sorted(defined - cited),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check draft citation keys against library.bib.")
    ap.add_argument("draft", help="draft file (markdown or .tex)")
    ap.add_argument("bib", help="library.bib")
    ap.add_argument("--warn-only", action="store_true", help="return 0 even if there are unresolved citations")
    args = ap.parse_args(argv)

    try:
        with open(args.draft, encoding="utf-8") as fh:
            draft_text = fh.read()
        with open(args.bib, encoding="utf-8") as fh:
            bib_text = fh.read()
    except OSError as e:
        print(f"[cite_check] 读取失败 → {e}", file=sys.stderr)
        return 2

    res = check(draft_text, bib_text)
    print(f"[cite_check] 正文引用 {len(res['cited'])} 键 · 库中定义 {len(res['defined'])} 键")
    if res["unresolved"]:
        print(f"[cite_check] ✗ 未解析(正文引用但库中缺失)共 {len(res['unresolved'])}:")
        for k in res["unresolved"]:
            print(f"  - @{k}")
    else:
        print("[cite_check] ✓ 所有正文引用均可在 library.bib 中解析")
    if res["unused"]:
        print(f"[cite_check] · 未被引用的库条目 {len(res['unused'])}(仅提示):")
        for k in res["unused"]:
            print(f"  - {k}")

    if res["unresolved"] and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
