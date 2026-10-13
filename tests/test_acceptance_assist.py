"""僅用虛構資料測試離線工具，不呼叫任何模型。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/acceptance_assist.py"


class AcceptanceAssistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.matrix = self.base / "matrix.json"
        self.template = self.base / "template.json"
        self.runs = self.base / "runs"
        self.sha = "a" * 40
        self.matrix.write_text(json.dumps({"cases": [{
            "id": "EXAMPLE-01", "source": "fictional.md",
            "skills": ["regulation-review"], "steps": ["先問「測試字句」", "提供虛構法規"],
            "expected": "正確預期", "forbidden": "不能補造"
        }]}, ensure_ascii=False), encoding="utf-8")
        self.template.write_text(json.dumps({
            "schema_version": "1.0", "run_id": "template", "case_id": "EXAMPLE-01",
            "candidate_commit": self.sha,
            "platform": {"product": "UNKNOWN", "surface": "UNKNOWN", "evidence": "UNVERIFIED"},
            "model": {"name": "UNKNOWN", "version": "UNVERIFIED", "reasoning_effort": "UNKNOWN", "evidence": "UNVERIFIED"},
            "skill_sources": [],
            "isolation": {"fresh_conversation": None, "history_or_memory_disabled": None,
                          "evidence": "UNVERIFIED", "contamination": []},
            "execution": {"kind": "PLANNED", "actual_model_call": False, "call_evidence": None},
            "inputs": [], "outputs": [], "expected_behavior": "來源判準",
            "forbidden_behavior": "來源禁止", "status": "NOT TESTED",
            "adjudication": {"verifier": None, "basis": "尚未測試", "evidence_anchors": [], "limitations": []},
            "quality": {"docx_generation": "NOT TESTED", "source_fidelity": "NOT TESTED",
                        "visual_qa": "NOT TESTED", "visual_evidence": None, "pages_reviewed": []},
            "artifacts": [], "missing_evidence": [], "redactions": []
        }), encoding="utf-8")

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return result

    def import_file(self, run_id, source):
        return self.run_cli("import-txt", "EXAMPLE-01", run_id, source,
                            "--commit", self.sha, "--matrix", self.matrix,
                            "--template", self.template, "--root", self.runs)

    def test_prepare_separates_private_rubric(self):
        plans = self.base / "plans"
        self.run_cli("prepare", "EXAMPLE-01", "--matrix", self.matrix, "--root", plans)
        folder = plans / "EXAMPLE-01"
        public = (folder / "prompt-fragments.md").read_text()
        self.assertIn("測試字句", public)
        self.assertNotIn("正確預期", public)
        self.assertNotIn("不能補造", (folder / "operator.md").read_text())
        self.assertIn("不能補造", (folder / "evaluator-PRIVATE.md").read_text())
        self.run_cli("prepare", "EXAMPLE-01", "--matrix", self.matrix, "--root", plans, ok=False)

    def test_import_integrity_and_no_fake_grading(self):
        original = self.base / "chat.txt"
        original.write_text("user：你好\nassistant：你好\n", encoding="utf-8")
        self.import_file("test01", original)
        saved = (self.runs / "test01/evidence/original.txt").read_bytes()
        record = json.loads((self.runs / "test01/record.json").read_text())
        self.assertEqual(saved, original.read_bytes())
        self.assertEqual(record["artifacts"][0]["sha256"], hashlib.sha256(saved).hexdigest())
        self.assertEqual(record["artifacts"][0]["byte_size"], len(saved))
        self.assertEqual(record["status"], "NOT TESTED")
        self.assertFalse(record["execution"]["actual_model_call"])
        self.assertEqual(record["outputs"], [])

    def test_duplicate_bytes_and_run_id_rejected(self):
        source = self.base / "chat.txt"
        source.write_text("only synthetic text")
        self.import_file("first", source)
        self.run_cli("import-txt", "EXAMPLE-01", "second", source, "--commit", self.sha,
                     "--matrix", self.matrix, "--template", self.template, "--root", self.runs, ok=False)
        self.run_cli("import-txt", "EXAMPLE-01", "first", source, "--commit", self.sha,
                     "--matrix", self.matrix, "--template", self.template, "--root", self.runs, ok=False)
        self.assertFalse((self.runs / "second").exists())

    def test_unsafe_paths_and_non_utf8(self):
        source = self.base / "bad.txt"
        source.write_bytes(b"\xff")
        for run_id in ("../bad", "/absolute", "bad/path", "safe"):
            self.run_cli("import-txt", "EXAMPLE-01", run_id, source, "--commit", self.sha,
                         "--matrix", self.matrix, "--template", self.template, "--root", self.runs, ok=False)
        self.assertFalse((self.runs / "safe").exists())
        valid = self.base / "real.txt"
        valid.write_text("fiction")
        link = self.base / "linked.txt"
        link.symlink_to(valid)
        self.run_cli("import-txt", "EXAMPLE-01", "link", link, "--commit", self.sha,
                     "--matrix", self.matrix, "--template", self.template, "--root", self.runs, ok=False)

    def test_summary_without_run_and_with_run(self):
        output = self.base / "summary.md"
        self.run_cli("summary", "--matrix", self.matrix, "--root", self.runs, "--output", output)
        self.assertIn("NOT TESTED", output.read_text())
        source = self.base / "chat.txt"
        source.write_text("test")
        self.import_file("first", source)
        second = self.base / "summary2.md"
        self.run_cli("summary", "--matrix", self.matrix, "--root", self.runs, "--output", second)
        self.assertIn("first/aaaaaaaa", second.read_text())
        self.assertIn("待人工核對", second.read_text())
        self.run_cli("summary", "--matrix", self.matrix, "--root", self.runs, "--output", second, ok=False)


if __name__ == "__main__":
    unittest.main()
