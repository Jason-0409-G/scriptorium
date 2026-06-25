#!/usr/bin/env python3
"""Scaffold a manuscript_workspace: standard dirs + a scope_brief.md template.

This is the pipeline's configuration entry point. The SCOPE stage fills in the
template; the resulting scope_brief.md then serves as the direction contract that
every later stage follows. Stdlib only — no third-party dependency.
"""
from __future__ import annotations
import argparse
import os

SCOPE_TEMPLATE = """\
# Scope brief: <short title>

Entry mode: <Rewrite Existing | Build From Materials>
Target scene: <journal | conference | report | review | competition>
Research question / angle: <the specific question or claim, not the broad topic>
Scope:
  - in:  <what's included>
  - out: <what's explicitly excluded>
Target journal / venue: <name>
  Article type: <...>   Length limit: <...>   Structure: <...>   Citation style: <...>   Scope fit: <...>
Research depth: <flash | pro>
Target word count: <...>
Output language: <English | Chinese>
Core themes (-> literature categories):
  1) <...>
  2) <...>
  3) <...>
Key sources read for orientation: <a few, with DOIs>
Open questions still to resolve: <...>
"""

README_TEMPLATE = """\
# manuscript_workspace

The auditable trail of one research-to-paper run. Each file is produced by a stage:

- `scope_brief.md` — scope: the direction contract (angle / target journal + requirements / word count / themes)
- `library/` — curate: `library.ris` (Zotero/EndNote), `library.bib`, `library.xlsx`
- `writing_rationale_matrix.md` — write: 论证脉络矩阵 (red-thread doublet 要/禁止论证 + per-unit anchors); gate with `check_argument_matrix.py`
- `draft.md` — write: the working manuscript (with `[@key]` citations)
- `audit_report.md` — audit: three independent reviews + Editor Synthesis, round by round until clean
- `humanize_matrix.md` — humanize: every de-AI change, recorded
- `final/` — build: `main.tex` / `manuscript.docx` / `manuscript.pdf`
- `artifact_manifest.md` — index written by artifact_check.py

Run `artifact_check.py <this dir> --write` to verify completeness and refresh the manifest.
"""

RATIONALE_TEMPLATE = """\
# 论证脉络矩阵 (argument-thread matrix)

## 红线动机 (controlling motivation)
红线动机 (one sentence): <the single controlling claim of this paper>
- 要论证 (prioritized claims): <2-4 specific claims this paper makes>
- 禁止论证 (claims to avoid): <what to NOT claim — overclaim guardrails, e.g. stay candidate, no n=1 extrapolation>

<!-- One row per smallest writing unit. F1 = whole-work framework row (2-4 sentences per cell).
     Every row must fill 动机链接 / 证据·引用锚 / 文字动作 with something specific, never a bare label.
     Offline gate (no network):  python <research-to-paper-write>/scripts/check_argument_matrix.py writing_rationale_matrix.md -->

| 行号 | 写作单元 Unit | 论点/功能 Claim | 动机链接 Motivation link | 证据/引用锚 Evidence·cite | 措辞强度 Hedge | 结构模式 Pattern/SOTA | 文字动作 Text move | 落点检查 Final check |
|---|---|---|---|---|---|---|---|---|
| F1 | <whole-work framework> | <...> | <...> | <...> | <...> | <...> | <...> | |
"""

SUBDIRS = ["library", "final"]


def scaffold(workspace: str, force: bool = False) -> list[str]:
    """Create the workspace dirs and seed templates; return created file paths."""
    created: list[str] = []
    os.makedirs(workspace, exist_ok=True)
    for d in SUBDIRS:
        os.makedirs(os.path.join(workspace, d), exist_ok=True)
    for name, content in (("scope_brief.md", SCOPE_TEMPLATE), ("README.md", README_TEMPLATE),
                          ("writing_rationale_matrix.md", RATIONALE_TEMPLATE)):
        path = os.path.join(workspace, name)
        if os.path.exists(path) and not force:
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        created.append(path)
    return created


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Initialize a manuscript_workspace directory.")
    ap.add_argument("workspace", nargs="?", default="manuscript_workspace")
    ap.add_argument("--force", action="store_true", help="overwrite existing template files")
    args = ap.parse_args(argv)
    created = scaffold(args.workspace, force=args.force)
    print(f"[new_workspace] 工作区就绪 → {os.path.abspath(args.workspace)}")
    if created:
        print("[new_workspace] 已创建:")
        for p in created:
            print(f"  - {p}")
    else:
        print("[new_workspace] 模板已存在,未覆盖(如需重置加 --force)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
