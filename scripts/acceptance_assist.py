#!/usr/bin/env python3
"""離線驗收輔助：不呼叫模型、不進行行為或法律正確性判定。"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

BASE = Path(__file__).resolve().parents[1]
MATRIX = BASE / "docs/acceptance/model-matrix.json"
TEMPLATE = BASE / "docs/acceptance/run-template.json"
ROOT = BASE / "test-output/acceptance"
ID = re.compile(r"[A-Za-z0-9_-]+\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
QUOTE = re.compile(r"[「『](.*?)[」』]")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def destination(root, name):
    if not ID.fullmatch(name):
        raise ValueError("不安全的 ID")
    target = Path(root).resolve() / name
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError("輸出路徑不安全")
    return target


def get_case(path, name):
    found = [item for item in load(path)["cases"] if item["id"] == name]
    if len(found) != 1:
        raise ValueError("案例不存在或重複：" + name)
    return found[0]


def prepare(args):
    case = get_case(args.matrix, args.case_id)
    folder = destination(args.root, args.case_id)
    if folder.exists():
        raise ValueError("操作包已存在，不覆寫")
    steps = "\n".join(f"{i}. {step}" for i, step in enumerate(case["steps"], 1))
    operator = (f"# {case['id']} 操作說明（禁止整份貼給受測模型）\n\n"
                f"原案來源：{case['source']}\n適用 Skill：{', '.join(case['skills']) or '依 START-HERE 選擇'}\n\n"
                + steps + "\n\n僅將已核對的輸入與必要虛構原文送入模型。\n")
    snippets = list(dict.fromkeys(part for step in case["steps"] for part in QUOTE.findall(step)))
    fragments = ("# 候選提示片段（非完整提示詞）\n\n"
                 "僅抽取原矩陣引文，需自行核對上下文和 Skill 讀取前置作業；"
                 "禁止將本檔與評分資料合併送給受測模型。\n\n"
                 + ("\n".join("- " + s for s in snippets) if snippets else "沒有可安全抽取的引文") + "\n")
    private = (f"# {case['id']} 私有評分檔（勿送模型）\n\n"
               f"原案：{case['source']}，矩陣摘要不能取代原判準。\n\n"
               f"期待：{case['expected']}\n\n禁止：{case['forbidden']}\n")
    created = False
    try:
        folder.mkdir(parents=True, exist_ok=False)
        created = True
        write_new(folder / "operator.md", operator)
        write_new(folder / "prompt-fragments.md", fragments)
        write_new(folder / "evaluator-PRIVATE.md", private)
    except Exception:
        if created:
            shutil.rmtree(folder)
        raise
    print("操作包：" + str(folder))


def records(root):
    if not Path(root).exists():
        return
    for path in sorted(Path(root).glob("*/record.json")):
        if not path.is_symlink() and not path.parent.is_symlink():
            yield path


def import_txt(args):
    source = Path(args.input)
    if source.is_symlink() or not source.is_file():
        raise ValueError("TXT 必須是存在且非符號連結的檔案")
    data = source.read_bytes()
    if not data or b"\x00" in data:
        raise ValueError("空檔或包含 NUL")
    data.decode("utf-8")
    if not SHA.fullmatch(args.commit):
        raise ValueError("必須指定完整40字元候選版本 SHA")
    case = get_case(args.matrix, args.case_id)
    folder = destination(args.root, args.run_id)
    if folder.exists():
        raise ValueError("run ID 已存在，不覆寫")
    digest = hashlib.sha256(data).hexdigest()
    for path in records(args.root):
        try:
            if any(a.get("sha256") == digest for a in load(path).get("artifacts", [])):
                raise ValueError("已匯入相同檔案：" + str(path))
        except (OSError, json.JSONDecodeError):
            continue
    record = copy.deepcopy(load(args.template))
    record.update(run_id=args.run_id, case_id=args.case_id,
                  candidate_commit=args.commit, status="NOT TESTED")
    record["platform"] = {"product": args.platform, "surface": args.surface, "evidence": "USER_DECLARED/UNVERIFIED"}
    record["model"] = {"name": args.model, "version": "UNVERIFIED", "reasoning_effort": "UNKNOWN",
                       "evidence": "USER_DECLARED/UNVERIFIED"}
    record["execution"] = {"kind": "PLANNED", "actual_model_call": False, "call_evidence": None}
    record["skill_sources"] = []
    record["inputs"] = []
    record["outputs"] = []
    record["expected_behavior"] = "須另依原案核對：" + case["source"]
    record["forbidden_behavior"] = "須另依原案禁止行為核對：" + case["source"]
    record["adjudication"] = {"verifier": None, "basis": "僅保存使用者提供TXT，未獨立判定",
                              "evidence_anchors": [], "limitations": ["模型呼叫、隔離和來源未經核對"]}
    record["missing_evidence"] = ["未核對逐字稿出處及完整性", "缺獨立行為判定", "未附完整輸入及 Skill 讀取證據"]
    record["artifacts"] = [{"id": "imported-txt", "kind": "transcript",
                            "origin": "PLATFORM_EXPORT", "path": "evidence/original.txt",
                            "sha256": digest, "byte_size": len(data)}]
    created = False
    try:
        folder.mkdir(parents=True, exist_ok=False)
        created = True
        (folder / "evidence").mkdir()
        with (folder / "evidence/original.txt").open("xb") as output:
            output.write(data)
        write_new(folder / "record.json", json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    except Exception:
        if created:
            shutil.rmtree(folder)
        raise
    print(f"已保存 SHA-256 {digest}，狀態仍為 NOT TESTED")


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def summary(args):
    from check_acceptance_evidence import check
    matrix = load(args.matrix)
    cases = {c["id"]: [] for c in matrix["cases"]}
    bad = []
    for path in records(args.root):
        try:
            record = check(load(path), path.parent)
            cases.setdefault(record["case_id"], []).append(record)
        except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
            bad.append((str(path), str(exc)))
    lines = ["# v0.1.4 驗收彙整（非模型驗收）", "",
             "只檢查檔案與聲明一致性；不代表法律、模型行為、DOCX 或 Beta/RC 放行。", "",
             "| 案例 | Run／候選 | 模型／平台 | 狀態 | 缺漏與人工處理 |",
             "| --- | --- | --- | --- | --- |"]
    for case_id, entries in cases.items():
        if not entries:
            lines.append(f"| {cell(case_id)} | — | — | NOT TESTED | 缺有效執行紀錄 |")
        for record in entries:
            tasks = list(record.get("missing_evidence", []))
            if record["status"] == "NOT TESTED":
                tasks.append("待人工核對原始行為")
            if not tasks:
                tasks.append("抽查原始錨點與實際風險")
            columns = (case_id, record["run_id"] + "/" + record["candidate_commit"][:8],
                       record["model"]["name"] + "/" + record["platform"]["product"],
                       record["status"], "；".join(map(str, tasks)))
            lines.append("| " + " | ".join(map(cell, columns)) + " |")
    lines += ["", f"可彙整紀錄：{sum(len(v) for v in cases.values())}；不合格紀錄：{len(bad)}。", "",
              "## 未通過證據格式檢查的紀錄", ""]
    lines += ["- " + p + "：" + err for p, err in bad] if bad else ["無。"]
    text = "\n".join(lines) + "\n"
    if args.output:
        write_new(Path(args.output), text)
        print("已輸出：" + str(args.output))
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="cmd", required=True)
    a = commands.add_parser("prepare")
    a.add_argument("case_id")
    a.add_argument("--matrix", type=Path, default=MATRIX)
    a.add_argument("--root", type=Path, default=ROOT / "plans")
    a.set_defaults(func=prepare)
    a = commands.add_parser("import-txt")
    a.add_argument("case_id")
    a.add_argument("run_id")
    a.add_argument("input", type=Path)
    a.add_argument("--commit", required=True)
    a.add_argument("--platform", default="UNKNOWN")
    a.add_argument("--surface", default="UNKNOWN")
    a.add_argument("--model", default="UNKNOWN")
    a.add_argument("--matrix", type=Path, default=MATRIX)
    a.add_argument("--template", type=Path, default=TEMPLATE)
    a.add_argument("--root", type=Path, default=ROOT)
    a.set_defaults(func=import_txt)
    a = commands.add_parser("summary")
    a.add_argument("--matrix", type=Path, default=MATRIX)
    a.add_argument("--root", type=Path, default=ROOT)
    a.add_argument("--output", type=Path)
    a.set_defaults(func=summary)
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
