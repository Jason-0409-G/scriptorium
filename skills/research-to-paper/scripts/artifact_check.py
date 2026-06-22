#!/usr/bin/env python3
"""Verify the manuscript_workspace artifact trail and (optionally) write a manifest.

A completeness gate for the auditable writing trail: it scans the workspace and reports,
per stage, whether each expected artifact exists, flagging any missing core-trail file.
Stdlib only — no third-party dependency.
"""
from __future__ import annotations
import argparse
import os
import sys

# (relative path, producing stage, level). level: "trail" = auditable reasoning trail that
# a completed run should leave; "output" = final deliverable (depends on whether BUILD ran);
# "optional" = nice-to-have. A "|" in the path means any one of the alternatives satisfies it
# (e.g. the Excel falls back to a .csv when openpyxl is absent).
EXPECTED = [
    ("scope_brief.md", "scope", "trail"),
    ("library/library.ris", "curate", "trail"),
    ("library/library.bib", "curate", "trail"),
    ("library/library.xlsx|library/library.csv", "curate", "trail"),
    ("library/doi_report.md", "curate", "optional"),
    ("writing_rationale_matrix.md", "write", "trail"),
    ("draft.md", "write", "trail"),
    ("audit_report.md", "audit", "trail"),
    ("humanize_matrix.md", "humanize", "trail"),
    ("final/main.tex", "build", "output"),
    ("final/manuscript.docx", "build", "output"),
    ("final/manuscript.pdf", "build", "output"),
]


def _exists(workspace: str, spec: str):
    """Return the first alternative that exists for an artifact spec, else None."""
    for alt in spec.split("|"):
        if os.path.exists(os.path.join(workspace, alt)):
            return alt
    return None


def check_workspace(workspace: str) -> list[dict]:
    rows = []
    for spec, stage, level in EXPECTED:
        found = _exists(workspace, spec)
        rows.append({
            "artifact": spec,
            "stage": stage,
            "level": level,
            "present": found is not None,
            "found": found,
        })
    return rows


def missing_trail(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["level"] == "trail" and not r["present"]]


def render_report(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        flag = "✓" if r["present"] else "—"
        note = ""
        if not r["present"] and r["level"] == "trail":
            note = "  (缺失:核心轨迹)"
        elif not r["present"] and r["level"] == "output":
            note = "  (未排版/可选)"
        lines.append(f"  {flag} [{r['stage']:>7}] {r['artifact']}{note}")
    return "\n".join(lines)


def write_manifest(workspace: str, rows: list[dict], path: str = "artifact_manifest.md") -> str:
    out = os.path.join(workspace, path)
    present = sum(1 for r in rows if r["present"])
    lines = [
        "# Artifact manifest",
        "",
        f"Workspace: `{os.path.abspath(workspace)}`",
        f"Artifacts present: {present}/{len(rows)}; missing core-trail: {len(missing_trail(rows))}.",
        "",
        "| Artifact | Stage | Level | Status |",
        "|---|---|---|---|",
    ]
    for r in rows:
        if r["present"]:
            status = "present"
        else:
            status = "**MISSING**" if r["level"] == "trail" else "not produced"
        shown = r["found"] or r["artifact"]
        lines.append(f"| `{shown}` | {r['stage']} | {r['level']} | {status} |")
    lines.append("")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check manuscript_workspace artifact completeness.")
    ap.add_argument("workspace", help="the manuscript_workspace directory")
    ap.add_argument("--write", action="store_true", help="write artifact_manifest.md")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any core-trail artifact is missing")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.workspace):
        print(f"[artifact_check] 工作区不存在 → {args.workspace}", file=sys.stderr)
        return 2

    rows = check_workspace(args.workspace)
    print(render_report(rows))
    miss = missing_trail(rows)
    present = sum(1 for r in rows if r["present"])
    print()
    print(f"[artifact_check] 小结: {present}/{len(rows)} 产物存在,缺失核心轨迹 {len(miss)} 项")
    if args.write:
        out = write_manifest(args.workspace, rows)
        print(f"[artifact_check] 写出 → {out}")
    if args.strict and miss:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
