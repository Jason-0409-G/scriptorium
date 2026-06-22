#!/usr/bin/env python3
"""Render the finished manuscript markdown into LaTeX (.tex) and Word (.docx), and optionally PDF, via pandoc.

Self-contained except for the external tool `pandoc` (the standard markdown→LaTeX/Word converter) and, for PDF,
a TeX engine (xelatex/pdflatex). No other skill is required.

Citations: if a `.bib` is given (e.g. the `library.bib` from research-to-paper-curate) and the manuscript uses
`[@citekey]` markers whose keys match the bib, pandoc `--citeproc` resolves them and appends a formatted reference
list. Without a bib, the prose is rendered as-is.

Usage: python build_formats.py <manuscript.md> <outdir> [--bib library.bib] [--pdf] [--reference-docx tmpl.docx]
"""
import sys, os, shutil, subprocess, argparse


def have(tool):
    return shutil.which(tool) is not None


def run(cmd):
    print("  $ " + " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("outdir")
    ap.add_argument("--bib", default=None, help="library.bib for [@key] citations")
    ap.add_argument("--pdf", action="store_true", help="also compile PDF (needs a TeX engine)")
    ap.add_argument("--reference-docx", default=None, help="a .docx whose styles Word output should inherit")
    a = ap.parse_args()

    if not have("pandoc"):
        sys.exit("[build] 需要 pandoc(md→LaTeX/Word 的标准工具)。安装: brew install pandoc / apt install pandoc, 再重试。")
    if not os.path.exists(a.manuscript):
        sys.exit(f"[build] 找不到稿件: {a.manuscript}")
    os.makedirs(a.outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.manuscript))[0]

    cite = []
    if a.bib and os.path.exists(a.bib):
        cite = ["--citeproc", "--bibliography", a.bib]
    elif a.bib:
        print(f"[build] 注: 未找到 bib {a.bib}, 引用不解析")

    outs = []
    # Word
    docx = os.path.join(a.outdir, base + ".docx")
    ref = ["--reference-doc", a.reference_docx] if a.reference_docx and os.path.exists(a.reference_docx) else []
    r = run(["pandoc", a.manuscript, *cite, *ref, "-o", docx])
    outs.append((docx, r.returncode == 0, r.stderr.strip()))
    # LaTeX (standalone article)
    tex = os.path.join(a.outdir, base + ".tex")
    r = run(["pandoc", a.manuscript, "-s", *cite, "-o", tex])
    outs.append((tex, r.returncode == 0, r.stderr.strip()))
    # PDF (optional)
    if a.pdf:
        engine = "xelatex" if have("xelatex") else ("pdflatex" if have("pdflatex") else None)
        if engine:
            pdf = os.path.join(a.outdir, base + ".pdf")
            r = run(["pandoc", a.manuscript, *cite, f"--pdf-engine={engine}", "-o", pdf])
            outs.append((pdf, r.returncode == 0, r.stderr.strip()))
        else:
            print("  [build] 无 TeX 引擎(xelatex/pdflatex)→ 跳过 PDF(.tex 已生成, 可在有 TeX 的机器上编译)")

    print("\n[build] 产物:")
    fail = 0
    for path, ok, err in outs:
        print(f"  {'✓' if ok else '✗'} {path}" + ("" if ok else f"   ERR: {err[:140]}"))
        fail += 0 if ok else 1
    print(f"[build] {'全部成功' if not fail else f'{fail} 个失败'}; "
          "引用未解析时检查 manuscript 是否用 [@key] 且 key 对应 library.bib")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
