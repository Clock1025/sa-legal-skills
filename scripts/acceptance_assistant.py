#!/usr/bin/env python3
"""離線操作卡、UTF-8 TXT 證據匯入與摘要；不呼叫模型或自動判分。"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

from check_acceptance_evidence import check, require

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('regulation-review', 'large-scale-reform', 'amendment-drafting')


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]+', value), '識別碼只允許英數字、底線與連字號')
    return value


def git_bytes(repo, commit, path):
    require(re.fullmatch(r'[0-9a-f]{40}', commit) is not None, '候選必須是完整40字元 Git SHA')
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=repo, stderr=subprocess.PIPE)


def load_plan(repo, commit):
    return json.loads(git_bytes(repo, commit, 'docs/acceptance/model-matrix.json'))


def selected_case(repo, commit, case_id):
    identifier(case_id)
    case = next((c for c in load_plan(repo, commit)['cases'] if c['id'] == case_id), None)
    require(case is not None, '案例不在指定候選的既有矩陣')
    return case


def store(repo):
    base = Path(repo).resolve()
    for name in ('test-output', 'acceptance', 'assistant'):
        base = base / name
        require(not base.is_symlink(), '輸出目錄不能是 symlink')
        base.mkdir(exist_ok=True)
    return base


def child(base, name):
    identifier(name)
    path = base / name
    require(not path.is_symlink(), '輸出路徑不能是 symlink')
    return path


@contextmanager
def new_directory(base, name):
    path = child(base, name)
    path.mkdir()  # Exclusive: never overwrite an existing plan, run or FAIL.
    try:
        yield path
    except BaseException:
        shutil.rmtree(path)
        raise


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def artifact(id, path, kind, origin, content):
    return dict(id=id, path=path, kind=kind, origin=origin,
                sha256=hashlib.sha256(content).hexdigest(), byte_size=len(content))


def rubric(repo, commit, case):
    source = git_bytes(repo, commit, case['source']).decode('utf-8')
    if case['id'].startswith('P0-CASE-'):
        marker = '## ' + case['id'] + '：'
        require(marker in source, '找不到原始 P0 判準')
        return marker + source.split(marker, 1)[1].split('\n## ', 1)[0]
    return f"來源：{case['source']}\n\n期待：{case['expected']}\n\n禁止：{case['forbidden']}\n"


def docx_inputs(repo, commit):
    # Reuse existing expansion only; never call the reference DOCX writer.
    spec = importlib.util.spec_from_file_location('docx_expansion', ROOT / 'tests/docx_reference.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixtures = json.loads(git_bytes(repo, commit, 'tests/fixtures/docx/cases.json'))
    outputs = {}
    for case in fixtures['cases']:
        identifier(case['id'])
        rows = []
        for row in case['rows']:
            new, old, reason = module.expand_row(row)
            rows.append(dict(row_id=row['id'], new=new, old=old, reason=reason))
        outputs[case['id'] + '.json'] = dict(kind='FICTIONAL_USER_INPUT', version=fixtures['version'],
                                            instrument=fixtures['instrument'], rows=rows)
    return outputs


def prepare(repo, commit, bundle_id, cases=None):
    matrix = load_plan(repo, commit)
    ids = cases or [c['id'] for c in matrix['cases']]
    require(len(ids) == len(set(ids)), '不要重複選擇案例')
    recipes_path = ROOT / 'docs/acceptance/case-inputs.json'
    recipes_bytes = recipes_path.read_bytes()
    recipes = json.loads(recipes_bytes)
    canonical = git_bytes(repo, commit, 'START-HERE.md').decode('utf-8').split('```text\n', 1)[1].split('\n```', 1)[0] + '\n'
    prepared = []
    for id in ids:
        case = selected_case(repo, commit, id)
        require(id in recipes, '此案例尚無整理好的輸入配方')
        prepared.append((case, recipes[id], rubric(repo, commit, case)))
    base = child(store(repo), 'plans'); base.mkdir(exist_ok=True)
    with new_directory(base, bundle_id) as directory:
        index = {'candidate_commit': commit, 'execution': 'PLANNED', 'status': 'NOT TESTED',
                 'recipe_sha256': hashlib.sha256(recipes_bytes).hexdigest(), 'files': []}
        def save(path, content, source):
            relative = PurePosixPath(path)
            require(not relative.is_absolute() and '..' not in relative.parts and '\\' not in path
                    and str(relative) == path, '不安全的產物路徑')
            dest = directory / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            index['files'].append(dict(path=path, source=source, sha256=hashlib.sha256(content).hexdigest(), byte_size=len(content)))
        save('reviewer/case-inputs.json', recipes_bytes, '工具目前實際輸入配方，非候選Skill')
        for filename in ('scripts/acceptance_assistant.py', 'tests/docx_reference.py'):
            save('reviewer/tool-' + Path(filename).name, (ROOT / filename).read_bytes(), '工具目前實際bytes：' + filename)
        for case, recipe, expected in prepared:
            prefix = case['id']
            save(prefix + '/model/canonical-prompt.txt', canonical.encode(), 'START-HERE.md @ ' + commit)
            for i, prompt in enumerate(recipe['prompts'], 1):
                save(f'{prefix}/model/turn-{i:02d}.txt', (prompt + '\n').encode(), 'case-inputs.json（人工整理輸入，不是預期答案）')
            for skill in case['skills']:
                require(skill in SKILLS, '未知 Skill')
                name = f'skills/{skill}/SKILL.md'
                # Anonymous bytes in CASE-02: commit belongs in reviewer index only.
                save(f'{prefix}/model/skills/{skill}.md', git_bytes(repo, commit, name), name + ' @ ' + commit)
            if prefix == 'C-DOCX':
                for filename, value in docx_inputs(repo, commit).items():
                    save(f'{prefix}/model/{filename}', (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode(), '既有 DOCX fixture 全文展開；非模型產物')
            operator = ('# 操作者專用：不要上傳此檔或整個案例資料夾\n\n'
                        '每案新隔離對話；只依階段逐份送 model/ 內材料。先選 Skill，再提供本階段全文；讀完才給案件。\n'
                        'model/skills 有多份時，不要一次提供；P0-CASE-01 不提供 drafting。CASE-02 不把 index 的 SHA 給模型。\n'
                        'turn 檔是依序的使用者輸入，須等待真實回覆並符合下列 setup；不得插入合成 assistant 歷史。\n\n'
                        + '\n'.join(f'{i}. {step}' for i, step in enumerate(case['steps'], 1))
                        + '\n\n' + recipe['operator_notes'] + '\n\n原始判準：\n\n' + expected)
            save(prefix + '/reviewer/操作與判準.md', operator.encode(), case['source'] + ' @ ' + commit)
        save('README.md', '只送指定 model/ 材料，不送 reviewer/、index.json 或整包。\n沒有模型執行；全部 NOT TESTED。配方由工具整理，候選原文固定SHA。\n'.encode(), '工具操作說明')
        write_json(directory / 'index.json', index)
    return directory


def read_txt(path):
    path = Path(path)
    require(not path.is_symlink() and path.is_file(), 'TXT 必須是實際檔案，不接受 symlink')
    content = path.read_bytes()
    text = content.decode('utf-8-sig')  # Preserve original bytes, including BOM/CRLF.
    require(text.strip() and '\x00' not in text, 'TXT 不得空白或含 NUL')
    return content, len(text.splitlines())


def escaped(value):
    text = str(value).replace('\r', ' ').replace('\n', ' ')
    return re.sub(r'([\\`*_{}\[\]()#+.!|<>])', r'\\\1', text)


def gaps(record):
    missing = list(record['missing_evidence'])
    if not record['inputs']: missing.append('尚未標出實際使用者輸入範圍')
    if not record['execution']['actual_model_call']: missing.append('尚未由操作者核對實際呼叫')
    if record['isolation']['fresh_conversation'] is not True: missing.append('隔離條件尚待核對')
    if record['model']['version'] == 'UNVERIFIED': missing.append('模型精確版本無法核對（限制，非自動行為 FAIL）')
    if not record['skill_sources'] or any(s['read_status'] != 'FULL' for s in record['skill_sources']):
        missing.append('Skill 提供／讀取及來源範圍待核對')
    if not record['adjudication']['verifier']: missing.append('尚待獨立人工行為判定')
    return list(dict.fromkeys(missing))


def summary(records):
    require(len(records) == len({Path(p).resolve() for p in records}), '不要重複指定同一份紀錄')
    lines = ['# 驗收摘要（離線彙整，不是自動判分）', '',
             '| Run / 案例 / 候選 | 平台 / 模型 / 版本 | 執行 / 規則狀態 | 檔案一致性 | 缺漏與限制 |',
             '| --- | --- | --- | --- | --- |']
    for path in records:
        try:
            require(not path.is_symlink() and not path.parent.is_symlink(), '紀錄不能是 symlink')
            record = json.loads(path.read_text(encoding='utf-8'))
            check(record, path.parent)
            fields = [record['run_id'] + ' / ' + record['case_id'] + ' / ' + record['candidate_commit'][:12],
                      record['platform']['product'] + ' ' + record['platform']['surface'] + ' / ' + record['model']['name'] + ' / ' + record['model']['version'],
                      record['execution']['kind'] + ' / ' + record['status'], 'PASS（僅一致性）',
                      '；'.join(gaps(record)) or '依紀錄未列缺漏；仍需核對證據真實性']
        except (ValueError, KeyError, TypeError, OSError) as error:
            fields = [path.parent.name, 'UNKNOWN', '未核對；不重寫原判定', 'FAIL', str(error)]
        lines.append('| ' + ' | '.join(escaped(f) for f in fields) + ' |')
    lines += ['', '待人工審查：原始輸入／輸出範圍、真實性、隔離、Skill 讀取及原案判準；不採模型自評。',
              '缺底層工具日誌不自動否定已可觀察行為；未核對的讀取／工具能力另列限制。',
              '實際風險與規則符合、證據完整性分開；此工具不給風險等級或法律結論。',
              'DOCX 未實際看頁面維持 VISUAL QA: NOT TESTED；不得以 TXT 或 checksum 代替。',
              '摘要不含原始對話正文，但 metadata／人工備註仍可能敏感；不得未經授權公開。']
    return '\n'.join(lines) + '\n'


def import_txt(repo, commit, run_id, case_id, transcript, platform='UNKNOWN', surface='UNKNOWN', model='UNKNOWN',
               version='UNVERIFIED', origin='SELF_REPORTED', observed_call=False, inputs=None, skills=()):
    case = selected_case(repo, commit, case_id)
    identifier(run_id)
    require(origin in ('PLATFORM_EXPORT', 'MODEL_OUTPUT', 'SELF_REPORTED', 'SYNTHETIC'), '來源宣告不合法')
    require(not observed_call or origin != 'SYNTHETIC', '合成資料不能宣告真人呼叫')
    content, count = read_txt(transcript)
    input_bytes = read_txt(inputs)[0] if inputs else None
    sources = []
    for name, filename in skills:
        require(name in SKILLS and name not in [s[0] for s in sources], '未知或重複 Skill')
        raw, _ = read_txt(filename)
        matched = raw == git_bytes(repo, commit, f'skills/{name}/SKILL.md')
        sources.append((name, raw, commit if matched else 'UNVERIFIED'))
    record = json.loads(git_bytes(repo, commit, 'docs/acceptance/run-template.json'))
    record.update(run_id=run_id, case_id=case_id, candidate_commit=commit,
                  expected_behavior=rubric(repo, commit, case), forbidden_behavior=case['forbidden'])
    for key, value in [('product', platform), ('surface', surface)]: record['platform'][key] = value
    record['platform']['evidence'] = 'SELF_REPORTED: 匯入者提供；尚未獨立核對 UI'
    record['model'].update(name=model, version=version, evidence='SELF_REPORTED: 匯入者提供；不是模型自述核實')
    record['execution'] = dict(kind='HUMAN_MODEL_RUN' if observed_call else ('SYNTHETIC' if origin == 'SYNTHETIC' else 'PLANNED'),
                               actual_model_call=observed_call, call_evidence=None)
    record['artifacts'] = [artifact('transcript', 'transcript.txt', 'transcript', origin, content)]
    anchor = dict(artifact_id='transcript', anchor=f'原始 TXT 全檔 lines 1–{count}；角色／回合邊界待核對')
    record['outputs'] = [anchor]
    if observed_call: record['execution']['call_evidence'] = anchor
    record['inputs'] = []
    if input_bytes:
        record['artifacts'].append(artifact('input', 'inputs.txt', 'input', 'USER_INPUT', input_bytes))
        record['inputs'] = [dict(artifact_id='input', anchor='匯入的使用者輸入全檔；範圍待人工核對')]
    record['skill_sources'] = []
    for name, raw, source_commit in sources:
        path = f'skills/{name}.md'
        record['artifacts'].append(artifact('skill-' + name, path, 'skill', 'SELF_REPORTED', raw))
        record['skill_sources'].append(dict(name=name, path=f'skills/{name}/SKILL.md', commit=source_commit,
                                            read_status='UNVERIFIED', artifact_id='skill-' + name, evidence_anchor=None))
    record['status'] = 'NOT TESTED'  # Pending independent adjudication, never auto-promote.
    record['adjudication'] = dict(verifier=None, basis='已保存 TXT；尚未獨立判定模型行為。不是自動真人驗收。',
                                  evidence_anchors=[], limitations=['TXT 來源及範圍由匯入者宣告；工具不驗證真實性',
                                  '不猜角色、訊息ID、時間或缺失對話；Skill 讀取不採模型自評',
                                  '底層工具日誌非通用聊天行為判定的必要條件；可用可見逐字稿作觀察依據'])
    record['missing_evidence'] = gaps(record)
    base = child(store(repo), 'runs'); base.mkdir(exist_ok=True)
    lock = base / '.import.lock'
    require(not lock.is_symlink(), '匯入鎖不能是 symlink')
    with lock.open('x'):
        pass
    try:
        digest = record['artifacts'][0]['sha256']
        for existing in sorted(base.glob('*/record.json')):
            require(not existing.parent.is_symlink() and not existing.is_symlink(), '既有紀錄不能是 symlink')
            previous = check(json.loads(existing.read_text(encoding='utf-8')), existing.parent)
            require(not any(a['kind'] == 'transcript' and a['sha256'] == digest for a in previous['artifacts']),
                    f'相同 TXT 已匯入 {previous["run_id"]}；不重複建立或增加覆蓋')
        with new_directory(base, run_id) as directory:
            (directory / 'transcript.txt').write_bytes(content)
            if input_bytes: (directory / 'inputs.txt').write_bytes(input_bytes)
            if sources: (directory / 'skills').mkdir()
            for name, raw, _ in sources: (directory / f'skills/{name}.md').write_bytes(raw)
            check(record, directory)
            write_json(directory / 'record.json', record)
            index = ['# 本地來源索引', '', f'候選：{commit}', '',
                     '來源為匯入者宣告；Hash 只證明保存bytes一致，不核實平台或模型。', '']
            for a in record['artifacts']:
                index.append(f'- {a["id"]}：{a["path"]}；{a["origin"]}；{a["byte_size"]} bytes；SHA-256 {a["sha256"]}')
            (directory / 'sources-index.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
            (directory / 'summary.md').write_text(summary([directory / 'record.json']), encoding='utf-8')
    finally:
        lock.unlink()
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare', help='從矩陣產生分離的模型輸入與操作者判準')
    p.add_argument('--commit', required=True); p.add_argument('--bundle-id', required=True)
    p.add_argument('--case', action='append')
    p = commands.add_parser('import-txt', help='保存原始 TXT，不自動評分或推論完整性')
    for option in ('commit', 'run-id', 'case', 'transcript'): p.add_argument('--' + option, required=True)
    for option in ('platform', 'surface', 'model'): p.add_argument('--' + option, default='UNKNOWN')
    p.add_argument('--model-version', default='UNVERIFIED')
    p.add_argument('--origin', choices=('PLATFORM_EXPORT', 'MODEL_OUTPUT', 'SELF_REPORTED', 'SYNTHETIC'), default='SELF_REPORTED')
    p.add_argument('--observed-call', action='store_true', help='操作者宣告已核對真實呼叫；不是工具認證')
    p.add_argument('--inputs'); p.add_argument('--skill', action='append', default=[], metavar='NAME=FILE')
    p = commands.add_parser('summary', help='彙整本地 runs；不包含原始正文')
    p.add_argument('--record', action='append', type=Path, default=[], help='另指定既有schema的紀錄，可重複選不同檔案')
    args = parser.parse_args()
    try:
        if args.command == 'prepare': print(prepare(ROOT, args.commit, args.bundle_id, args.case))
        elif args.command == 'import-txt':
            skills = [s.split('=', 1) for s in args.skill]
            require(all(len(s) == 2 for s in skills), '--skill 必須是 NAME=FILE')
            print(import_txt(ROOT, args.commit, args.run_id, args.case, args.transcript,
                             args.platform, args.surface, args.model, args.model_version,
                             args.origin, args.observed_call, args.inputs, skills))
        else:
            records = args.record or sorted(child(store(ROOT), 'runs').glob('*/record.json'))
            print(summary(records), end='')
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError, IndexError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
