#!/usr/bin/env python3
"""Offline supplied-data packer. No platform APIs, private history access or upload."""
import argparse
import copy
from datetime import date, datetime
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import secrets
import string
import sys
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED

SCHEMA_VERSION = '1.0'
PLATFORMS = {
    'OC': ('ChatGPT', 'Chat'), 'OX': ('Codex', 'Codex'), 'OW': ('ChatGPT', 'Work'),
    'AC': ('Claude', 'Chat'), 'AK': ('Claude', 'Code'), 'GC': ('Gemini', 'Gemini'),
    'GS': ('Google AI Studio', 'Studio'), 'GL': ('Gemini', 'CLI'),
    'GN': ('NotebookLM', 'NotebookLM'), 'HI': ('Copilot', 'IDE'), 'UU': ('UNKNOWN', 'UNKNOWN'),
}
LABELS = ('OBSERVED', 'SELF_REPORTED', 'UNVERIFIED')
BASE_FILES = ('report.md', 'transcript.md', 'sources-index.md', 'attachments/INDEX.md', 'outputs/INDEX.md')
REQUIRED = ('schema_version', 'conversation_id', 'report_id', 'generated_at', 'naming_date',
            'platform', 'model_segments', 'skill_reads', 'transcript', 'sources', 'attachments',
            'outputs', 'limitations', 'redactions', 'report', 'files', 'delivery')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_name(name):
    require(isinstance(name, str) and name and '\\' not in name,
            f'unsafe package path: {name!r}')
    path = PurePosixPath(name)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == name,
            f'unsafe package path: {name!r}')


def platform_ok(value):
    require(isinstance(value, dict) and value.get('code') in PLATFORMS, 'unknown platform code')
    require((value.get('product'), value.get('surface')) == PLATFORMS[value['code']],
            'platform product/surface does not match declared code')
    require(value.get('evidence_status') in LABELS, 'platform evidence_status missing')
    require(value.get('evidence'), 'platform evidence required (or explicit UNKNOWN explanation)')
    if value['code'] == 'UU':
        require(value['evidence_status'] == 'UNVERIFIED', 'unknown platform must be UNVERIFIED')


def validate_metadata(data):
    """Validate declared structure/consistency; cannot prove supplied assertions true."""
    platform_ok(data['platform'])
    require(data['generated_at'] is None or isinstance(data['generated_at'], str), 'generated_at must be ISO timestamp or null')
    for key in ('model_segments', 'skill_reads', 'sources', 'attachments', 'outputs', 'limitations', 'redactions'):
        require(isinstance(data[key], list), f'{key} must be an array')
    require(data['limitations'], 'limitations must disclose verification boundaries')
    turns = data['transcript']['turns']
    require(isinstance(turns, list), 'transcript turns must be an ordered array')
    anchors = []
    for turn in turns:
        require(re.fullmatch(r'T[1-9][0-9]*', turn['anchor']) is not None, 'invalid local turn anchor')
        require(turn['role'] in ('user', 'assistant'), 'only user-visible user/assistant turns allowed')
        require(isinstance(turn['text'], str), 'turn text must be supplied text')
        require(turn['representation'] in ('VERBATIM', 'SUMMARY', 'REDACTED'), 'turn representation missing')
        require(turn['origin'], 'turn origin required')
        anchors.append(turn['anchor'])
    require(anchors == [f'T{i + 1}' for i in range(len(turns))], 'local turn anchors must follow supplied order')
    coverage = data['transcript']['coverage']
    require(all(key in coverage for key in ('scope', 'start', 'end', 'evidence', 'missing', 'truncations', 'summary_substitutions')),
            'transcript coverage fields missing')
    require(coverage['scope'] and coverage['evidence'], 'scope and coverage evidence required')
    for key in ('missing', 'truncations', 'summary_substitutions'):
        require(isinstance(coverage[key], list), f'coverage {key} must be an array')
    completeness = data['transcript']['transcript_completeness']
    require(completeness in ('COMPLETE', 'PARTIAL', 'UNVERIFIED'), 'invalid transcript_completeness')
    known_gaps = any(coverage[k] for k in ('missing', 'truncations', 'summary_substitutions')) or bool(data['redactions'])
    known_gaps = known_gaps or any(t['representation'] != 'VERBATIM' for t in turns)
    require(not known_gaps or completeness == 'PARTIAL', 'known gaps/redactions/summaries require PARTIAL')
    for endpoint in ('start', 'end'):
        require(coverage[endpoint] in anchors or coverage[endpoint] in (None, 'UNKNOWN'), 'coverage endpoint unavailable')
    for turn in turns:
        if turn['representation'] == 'REDACTED':
            require(any(r.get('location') == turn['anchor'] for r in data['redactions']), 'redacted turn requires redaction location/reason')
        if turn['representation'] == 'SUMMARY':
            require(coverage['summary_substitutions'], 'summary turn requires disclosed substitution')
    if completeness == 'COMPLETE':
        require(turns and coverage['start'] == anchors[0] and coverage['end'] == anchors[-1],
                'COMPLETE requires declared full-scope endpoints')
        require(coverage.get('verification') == 'CHECKED_USER_VISIBLE_SCOPE',
                'COMPLETE requires explicit checked user-visible scope, not just current window')
    segment_ids = []
    for segment in data['model_segments']:
        require(segment['id'] == f'E{len(segment_ids) + 1}', 'model segments must be E1, E2...')
        platform_ok(segment['platform'])
        require(all(isinstance(segment.get(k), str) and segment[k] for k in ('model', 'reasoning_effort', 'evidence')), 'model provenance missing')
        require(segment['evidence_status'] in LABELS, 'model evidence status invalid')
        require(segment['start'] in anchors and segment['end'] in anchors, 'model segment anchors unavailable')
        require(anchors.index(segment['start']) <= anchors.index(segment['end']), 'model segment order invalid')
        segment_ids.append(segment['id'])
    if turns:
        require(segment_ids, 'visible turns need model segment (UNKNOWN when not known)')
        covered = []
        for segment in data['model_segments']:
            covered.extend(anchors[anchors.index(segment['start']):anchors.index(segment['end']) + 1])
        require(covered == anchors, 'every supplied turn needs segment provenance, including UNKNOWN')
    source_ids = []
    for source in data['sources']:
        require(not any(key in source for key in ('sha256', 'byte_size')), 'source hashes/sizes are not computed by this packer')
        require(re.fullmatch(r'SRC-[0-9]{3,}', source['id']) is not None, 'source ID invalid')
        require(all(source.get(k) for k in ('name', 'kind', 'version', 'location', 'visibility', 'evidence_status')),
                'source provenance fields missing')
        require(source['kind'] in ('skill', 'current_law', 'proposal', 'case_material', 'export', 'other'), 'source kind invalid')
        require(source['evidence_status'] in LABELS, 'source evidence status invalid')
        source_ids.append(source['id'])
    require(len(source_ids) == len(set(source_ids)), 'duplicate source IDs')
    for read in data['skill_reads']:
        require(read['source_id'] in source_ids and read['stage'] and read['name'] and read['path'], 'Skill read provenance missing')
        require(next(source for source in data['sources'] if source['id'] == read['source_id'])['kind'] == 'skill',
                'Skill read must link a Skill source')
        require(isinstance(read['version'], str) and read['version'] and read['version_status'] in ('VERIFIED', 'UNVERIFIED'), 'Skill version state missing')
        require(read['read_status'] in ('FULL', 'PARTIAL', 'UNVERIFIED', 'NOT_READ'), 'Skill read state invalid')
        require(isinstance(read['evidence_anchors'], list) and all(a in anchors for a in read['evidence_anchors']),
                'Skill evidence anchors invalid')
        if read['read_status'] == 'FULL':
            require(read['evidence'] and read['evidence_anchors'], 'full Skill read requires recorded evidence')
        if read['version_status'] == 'VERIFIED':
            require(read['version'] != 'UNVERIFIED' and read['evidence'], 'verified Skill version requires recorded evidence')
        if read['version_status'] == 'UNVERIFIED':
            require(read['version'] == 'UNVERIFIED', 'unverified Skill version cannot pretend to be verified')
    for collection in ('attachments', 'outputs'):
        ids = []
        for entry in data[collection]:
            require(entry['id'] and entry['name'], f'{collection} ID/name required')
            require(entry['availability'] in ('AVAILABLE', 'UNAVAILABLE', 'EXCLUDED'), 'invalid availability')
            require(entry['evidence_status'] in LABELS and entry['verification'], 'file verification disclosure missing')
            require(isinstance(entry['authorized'], bool), 'explicit local packaging authorization required')
            require(entry['reason'], 'file inclusion/missing reason required')
            require(entry['package_path'] is None or entry['package_path'].startswith('files/'), 'raw files must be under files/')
            if entry['package_path'] is not None:
                safe_name(entry['package_path'])
                require(entry['availability'] == 'AVAILABLE' and entry['authorized'], 'file not available/authorized')
            if entry['availability'] == 'AVAILABLE':
                require(entry['package_path'] is not None, 'AVAILABLE file requires a real included local file')
            ids.append(entry['id'])
        require(len(ids) == len(set(ids)), f'duplicate {collection} IDs')
    report = data['report']
    require(all(isinstance(report.get(key), list) for key in ('confirmed_decisions', 'open_questions', 'events', 'validation_limits')), 'report collections must be arrays')
    require(all(key in report for key in ('context', 'task', 'scope', 'confirmed_decisions', 'open_questions', 'events', 'validation_limits')),
            'report fields missing')
    for decision in report['confirmed_decisions']:
        require(re.fullmatch(r'D-[0-9]{3,}', decision['id']) is not None, 'decision ID required')
        require(decision['status'] == 'CONFIRMED' and decision['scope'], 'report decision must preserve confirmed scope')
        require(decision['evidence_anchor'] in anchors or decision['evidence_anchor'] in source_ids,
                'decision evidence anchor missing')
    for event in report['events']:
        require(event['evidence_status'] in LABELS and event['description'], 'event evidence status missing')
        require(event['evidence_anchor'] in anchors or event['evidence_anchor'] in source_ids,
                'event evidence anchor missing')
    for redaction in data['redactions']:
        require(redaction.get('location') and redaction.get('reason'), 'redaction location/reason required')


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def render(data):
    transcript = ['# Available user-visible transcript\n', 'Order follows supplied input, not reconstructed history.\n']
    for turn in data['transcript']['turns']:
        transcript += [f"<a id=\"{turn['anchor']}\"></a>\n",
                       f"## {turn['anchor']} | {turn['role']} | {turn['representation']}\n",
                       f"Message ID: {turn.get('message_id') or 'UNKNOWN'}; timestamp: {turn.get('timestamp') or 'UNKNOWN'}\n",
                       f"Origin: {turn['origin']}\n\n", turn['text'], '\n\n']
    sources = '# Sources index\n\n' + (json_bytes(data['sources']).decode() if data['sources'] else 'No accessible sources recorded.\n')
    report = '# Skill Feedback Package\n\n'
    for key, value in data['report'].items():
        report += f'## {key}\n\n'
        report += (value + '\n' if isinstance(value, str) else '```json\n' + json_bytes(value).decode() + '```\n') + '\n'
    report += '\n## Coverage, model/Skill provenance, outputs and limitations\n\n'
    report += json_bytes({k: data[k] for k in ('platform', 'model_segments', 'skill_reads', 'transcript', 'outputs', 'limitations', 'redactions') if k != 'transcript'}).decode()
    report += json_bytes({k: v for k, v in data['transcript'].items() if k != 'turns'}).decode()
    report += '\nOffline checks validate packaging and declared structure only. REAL-MODEL BEHAVIOR: NOT TESTED / UNVERIFIED.\n'
    report += '\nDelivery: ' + data['delivery'] + '\n'
    files = {'report.md': report.encode(), 'transcript.md': ''.join(transcript).encode(), 'sources-index.md': sources.encode()}
    for collection in ('attachments', 'outputs'):
        text = f'# {collection} index\n\n'
        text += json_bytes(data[collection]).decode() if data[collection] else 'No files available or recorded; this is not proof none existed.\n'
        files[f'{collection}/INDEX.md'] = text.encode()
    return files


def build_package(metadata, input_root, output_root, *, text_only=False, naming_date=None):
    data = copy.deepcopy(metadata)
    require(not any(key in data for key in ('files', 'report_id', 'naming_date', 'delivery')), 'reserved generated metadata fields')
    require(data['schema_version'] == SCHEMA_VERSION, 'unsupported schema_version')
    validate_metadata(data)
    if data['generated_at'] is not None:
        moment = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
        require(moment.tzinfo is not None, 'generated_at requires timezone or null')
        report_date = moment.date()
        date_source = 'SUPPLIED_GENERATED_AT'
    else:
        require(naming_date is not None, 'unknown time: supply --date YYYY-MM-DD; generated_at remains null')
        report_date = date.fromisoformat(naming_date)
        date_source = 'USER_PROVIDED_NAMING_DATE'
        data['limitations'].append('generated_at UNVERIFIED; date supplied only for naming.')
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    code = data['platform']['code']
    conversation_id = data.get('conversation_id')
    if conversation_id is None:
        existing = {p.name.split('_')[1] for p in output_root.glob('report_*') if len(p.name.split('_')) > 2}
        for _ in range(100):
            conversation_id = code + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
            if conversation_id not in existing:
                break
        else:
            raise ValueError('conversation ID collision limit reached')
        data['limitations'].append('New local conversation ID; reuse this ID explicitly on future reports. No automatic platform persistence.')
    require(re.fullmatch(r'(?:' + '|'.join(PLATFORMS) + r')[a-z0-9]{6}', conversation_id or '') is not None, 'invalid conversation_id')
    # The ID encodes the initial surface; later segments may have different surfaces.
    data['conversation_id'] = conversation_id
    used = {p.name.split('_')[-1].split('.')[0] for p in output_root.glob(f'report_{conversation_id}_*')}
    for _ in range(100):
        suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        if suffix not in used:
            break
    else:
        raise ValueError('report suffix collision limit reached')
    data['report_id'] = f'report_{conversation_id}_{report_date:%y%m%d}_{suffix}'
    data['naming_date'] = {'date': report_date.isoformat(), 'source': date_source}
    data['delivery'] = 'TEXT_FALLBACK' if text_only else 'ZIP'
    if text_only:
        data['limitations'].append('ZIP unavailable/disabled; raw file bytes omitted from text fallback; save sections and package manually.')
    raw = {}
    root = Path(input_root).resolve()
    for collection in ('attachments', 'outputs'):
        for entry in data[collection]:
            local_path = entry.pop('local_path', None)
            for key in ('sha256', 'byte_size'):
                require(key not in entry, 'do not supply invented file hashes/sizes; packer computes them')
            target = entry['package_path']
            if target is not None:
                require(local_path, 'included file requires actual local_path')
                safe_name(local_path)
                source = root / local_path
                require(source.resolve().is_relative_to(root) and source.is_file(), f'file unavailable/outside input root: {local_path}')
                content = source.read_bytes()
                if not text_only:
                    require(target not in raw, 'duplicate raw package path')
                    raw[target] = content
                    entry['sha256'] = hashlib.sha256(content).hexdigest()
                    entry['byte_size'] = len(content)
                else:
                    entry['availability'] = 'EXCLUDED'
                    entry['reason'] += '; TEXT_FALLBACK omits raw bytes'
                    entry['package_path'] = None
            entry.setdefault('sha256', None)
            entry.setdefault('byte_size', None)
    files = {**render(data), **raw}
    data['files'] = [{'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'byte_size': len(content)} for name, content in files.items()]
    # No impossible self-referential hash: integrity of manifest is the container's responsibility.
    data['files'].append({'path': 'manifest.json', 'sha256': None, 'byte_size': None})
    files['manifest.json'] = json_bytes(data)
    validate_files(files)
    if text_only:
        # Length-marked sections allow lossless programmatic/manual recovery without delimiter ambiguity.
        text = '\n'.join(f'===== {name} ({len(content)} UTF-8 bytes) =====\n{content.decode()}' for name, content in files.items())
        path = output_root / (data['report_id'] + '.txt')
        with path.open('x', encoding='utf-8') as handle:
            handle.write(text)
    else:
        buffer = io.BytesIO()
        with ZipFile(buffer, 'w', ZIP_DEFLATED) as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        content = buffer.getvalue()
        validate_zip_bytes(content)
        path = output_root / (data['report_id'] + '.zip')
        with path.open('xb') as handle:
            handle.write(content)
    return path, data


def validate_files(files):
    require(all(name in files for name in (*BASE_FILES, 'manifest.json')), 'required package member missing')
    for name in files:
        safe_name(name)
    manifest = json.loads(files['manifest.json'])
    require(all(key in manifest for key in REQUIRED), 'manifest required fields missing')
    require(manifest['schema_version'] == SCHEMA_VERSION, 'unsupported schema_version')
    validate_metadata(manifest)
    require(manifest['delivery'] in ('ZIP', 'TEXT_FALLBACK'), 'invalid delivery')
    naming = manifest['naming_date']
    report_date = date.fromisoformat(naming['date'])
    if manifest['generated_at'] is None:
        require(naming['source'] == 'USER_PROVIDED_NAMING_DATE', 'unknown timestamp requires supplied naming date')
    else:
        moment = datetime.fromisoformat(manifest['generated_at'].replace('Z', '+00:00'))
        require(moment.tzinfo is not None and naming['source'] == 'SUPPLIED_GENERATED_AT' and moment.date() == report_date,
                'timestamp/naming date mismatch')
    cid = manifest['conversation_id']
    require(re.fullmatch(r'(?:' + '|'.join(PLATFORMS) + r')[a-z0-9]{6}', cid or '') is not None, 'invalid manifest conversation_id')
    require(re.fullmatch(r'report_' + cid + f'_{report_date:%y%m%d}_' + r'[a-z0-9]{4}', manifest['report_id']) is not None, 'invalid report_id')
    index = manifest['files']
    require(len(index) == len(files) and {entry['path'] for entry in index} == set(files), 'manifest file index mismatch')
    for entry in index:
        if entry['path'] == 'manifest.json':
            require(entry['sha256'] is None and entry['byte_size'] is None, 'manifest self hash must be null')
        else:
            content = files[entry['path']]
            require(entry['sha256'] == hashlib.sha256(content).hexdigest() and entry['byte_size'] == len(content), 'file hash/size mismatch')
    declared_raw = set()
    for collection in ('attachments', 'outputs'):
        for entry in manifest[collection]:
            target = entry['package_path']
            if target is not None:
                require(target in files, 'declared raw file missing')
                require(entry['sha256'] == hashlib.sha256(files[target]).hexdigest() and entry['byte_size'] == len(files[target]), 'raw file metadata mismatch')
                require(target not in declared_raw, 'duplicate raw reference')
                declared_raw.add(target)
            else:
                require(entry['sha256'] is None and entry['byte_size'] is None, 'uncopied file must not claim computed bytes')
    require(set(files) == set(BASE_FILES) | {'manifest.json'} | declared_raw, 'undeclared raw file')
    expected = render(manifest)
    require(all(files[name] == content for name, content in expected.items()), 'rendered report/transcript/index differs from manifest')
    return manifest


def validate_zip_bytes(content):
    with ZipFile(io.BytesIO(content)) as archive:
        require(archive.testzip() is None, 'ZIP CRC failure')
        names = archive.namelist()
        require(len(names) == len(set(names)), 'duplicate ZIP members')
        return validate_files({name: archive.read(name) for name in names})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    pack = commands.add_parser('pack')
    pack.add_argument('metadata', type=Path)
    pack.add_argument('--output-dir', type=Path, required=True)
    pack.add_argument('--text-only', action='store_true')
    pack.add_argument('--date', help='explicit YYYY-MM-DD naming date if time is unknown')
    validate = commands.add_parser('validate')
    validate.add_argument('zip', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'pack':
            path, manifest = build_package(json.loads(args.metadata.read_text()), args.metadata.parent,
                                           args.output_dir, text_only=args.text_only, naming_date=args.date)
            print(f'Created {path}; conversation_id={manifest["conversation_id"]}; delivery={manifest["delivery"]}')
        else:
            validate_zip_bytes(args.zip.read_bytes())
            print('PASS: supplied manifest consistency, ZIP members/bytes/hashes (not platform completeness or model behavior)')
    except (ValueError, KeyError, TypeError, OSError, BadZipFile) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
