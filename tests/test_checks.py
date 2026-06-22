"""Unit tests for the standard-library check scripts (cite_check, artifact_check, new_workspace).

Run from the repo root:  python -m unittest discover -s tests
"""
import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "research-to-paper", "scripts")


def _load(name):
    path = os.path.join(SCRIPTS, name)
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cite_check = _load("cite_check.py")
artifact_check = _load("artifact_check.py")
new_workspace = _load("new_workspace.py")


class CiteCheckTest(unittest.TestCase):
    def test_pandoc_keys_extracted(self):
        draft = "As shown [@smith2020] and also @doe_2019a here."
        self.assertEqual(cite_check.cited_keys(draft), {"smith2020", "doe_2019a"})

    def test_email_is_not_a_citation(self):
        draft = "Contact me at user@domain.org for details."
        self.assertEqual(cite_check.cited_keys(draft), set())

    def test_latex_cite_is_split_on_commas(self):
        draft = r"text \citep{a2020,b2021} more \cite{c2019}"
        self.assertEqual(cite_check.cited_keys(draft), {"a2020", "b2021", "c2019"})

    def test_bib_keys_and_unresolved_unused(self):
        bib = "@article{smith2020, title={X}}\n@book{doe2019, title={Y}}"
        self.assertEqual(cite_check.bib_keys(bib), {"smith2020", "doe2019"})
        res = cite_check.check("see [@smith2020] and [@ghost2021]", bib)
        self.assertEqual(res["unresolved"], ["ghost2021"])
        self.assertIn("doe2019", res["unused"])


class ArtifactCheckTest(unittest.TestCase):
    def test_scaffold_then_draft_missing(self):
        with tempfile.TemporaryDirectory() as d:
            ws = os.path.join(d, "manuscript_workspace")
            new_workspace.scaffold(ws)
            rows = artifact_check.check_workspace(ws)
            scope_row = next(r for r in rows if r["artifact"] == "scope_brief.md")
            self.assertTrue(scope_row["present"])  # seeded by scaffold
            missing = {r["artifact"] for r in artifact_check.missing_trail(rows)}
            self.assertIn("draft.md", missing)  # not written yet

    def test_xlsx_falls_back_to_csv(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "library"))
            open(os.path.join(d, "library", "library.csv"), "w").close()
            rows = artifact_check.check_workspace(d)
            row = next(r for r in rows if "xlsx" in r["artifact"])
            self.assertTrue(row["present"])
            self.assertEqual(row["found"], "library/library.csv")


if __name__ == "__main__":
    unittest.main()
