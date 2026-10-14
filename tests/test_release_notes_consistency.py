"""Check concise GitHub Release headings without rerunning model tests."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs" / "releases"


class ReleaseNotesTests(unittest.TestCase):
    def test_one_title_per_release_and_no_body_duplicate(self):
        titles = json.loads((NOTES / "titles.json").read_text(encoding="utf-8"))
        versions = {p.stem for p in NOTES.glob("v*.md")}
        self.assertEqual(set(titles), versions)
        for tag, title in titles.items():
            with self.subTest(tag=tag):
                self.assertTrue(title.startswith(tag + " — "), title)
                self.assertTrue(title[len(tag) + 3:].strip(), title)
                body = (NOTES / (tag + ".md")).read_text(encoding="utf-8").strip()
                self.assertTrue(body, tag)
                self.assertFalse(body.startswith("# "), tag)
                self.assertFalse(body.startswith(title), tag)
                self.assertNotIn("\\n# " + tag, body)


if __name__ == "__main__":
    unittest.main()
