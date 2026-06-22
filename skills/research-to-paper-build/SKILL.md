---
name: research-to-paper-build
description: >-
  Render a finished manuscript into submission formats — LaTeX (.tex), Word (.docx), and optionally PDF —
  depending on no other skill. It runs pandoc on the manuscript markdown, resolving [@citekey] citations from a
  library.bib into a formatted reference list, and can inherit a Word template's styles or compile a PDF when a TeX
  engine is present. Use whenever the user wants the writeup in a specific output format, says 导出成LaTeX, 生成Word,
  转成docx, 排版成论文/PDF, 输出tex, 这个稿子转成latex和word, "export to LaTeX", "give me a Word doc", "render to
  PDF", "build the .tex". Runs the bundled scripts/build_formats.py; takes the manuscript from research-to-paper-write
  and the library.bib from research-to-paper-curate.
---

# Build — render to LaTeX / Word / PDF (self-contained)

This is the last step: turn the finished, reviewed, de-AI'd manuscript into the formats a journal or a reader
needs. It is a thin wrapper around **pandoc**, the standard markdown→LaTeX/Word converter — pandoc is an external
tool, not a skill, so the skill stays self-contained while leaning on the right tool for the job rather than
reimplementing document conversion.

## Workflow

1. **Confirm the inputs.** You need the manuscript as markdown (from `research-to-paper-write`). If the manuscript
   cites with `[@citekey]` markers, point at the `library.bib` (from `research-to-paper-curate`) so citations
   resolve into a reference list; the keys in the prose must match the bib keys (export_refs.py builds them as
   surname+year). If there are no `[@key]` markers, build without a bib and the prose renders as-is.

2. **Run the build.**

   ```
   python scripts/build_formats.py <manuscript.md> <outdir> --bib <library.bib> --pdf
   ```

   It produces `<name>.docx` and `<name>.tex` always, and `<name>.pdf` when `--pdf` is set and a TeX engine
   (xelatex/pdflatex) is installed. Drop `--pdf` if you only need the editable formats; drop `--bib` if there are
   no citations to resolve. To match a target journal's Word styling, pass `--reference-docx <template.docx>`.

3. **Report and hand back.** Tell the user which files were produced and where. If pandoc is missing, say so and
   give the one-line install (`brew install pandoc` / `apt install pandoc`) — do not try to hand-build a .docx, a
   half-correct document is worse than a clear "install pandoc first". If PDF was skipped for lack of a TeX engine,
   note that the `.tex` is ready to compile elsewhere.

## Notes

- The `.tex` is a standalone pandoc `article`. For a specific journal class (e.g. `elsarticle`, `IEEEtran`), the
  user can swap the document class in the generated `.tex`, or supply a pandoc template; this skill produces a clean
  general-purpose source rather than guessing a journal class.
- For journal submission that requires live `\cite` + a `.bib` (natbib/biblatex) rather than pandoc's inlined
  references, regenerate the `.tex` with pandoc's `--natbib`; the default `--citeproc` is best for a self-contained
  draft and for Word.

## Files

- `scripts/build_formats.py` — pandoc wrapper producing `.docx`, `.tex`, and optional `.pdf`.
