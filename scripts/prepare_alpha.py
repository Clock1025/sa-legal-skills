#!/usr/bin/env python3
"""Prepare v0.2.0-alpha.2 artifacts from an integrated commit; never publish."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TAG = 'v0.2.0-alpha.2'
INTEGRATION_REF = 'refs/remotes/origin/develop-0.2'


def git(source, *args):
    return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()


def validate_source(source, commit):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('source commit must be a full lowercase 40-character SHA')
    if git(source, 'rev-parse', '--is-shallow-repository') != 'false':
        raise ValueError('complete Git history is required')
    if git(source, 'rev-parse', '--verify', 'HEAD^{commit}') != commit:
        raise ValueError('checkout HEAD does not match the selected source commit')
    git(source, 'rev-parse', '--verify', INTEGRATION_REF + '^{commit}')
    if subprocess.run(['git', '-C', str(source), 'merge-base', '--is-ancestor',
                       commit, INTEGRATION_REF], check=False).returncode != 0:
        raise ValueError('source commit is not integrated in origin/develop-0.2')
    if git(source, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('source checkout has tracked or untracked changes')


def prepare(source, commit, output):
    source = source.resolve()
    output = output.resolve()
    validate_source(source, commit)
    if output.exists():
        raise ValueError('output already exists; choose a fresh artifact directory')
    # Frozen source supplies its validator/tests; no v0.1 Beta tag/develop gate.
    subprocess.run([sys.executable, 'scripts/validate.py'], cwd=source, check=True)
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                   cwd=source, check=True)
    subprocess.run(['git', '-C', str(source), 'diff', '--check'], check=True)
    validate_source(source, commit)
    output.mkdir(parents=True)
    archive = output / 'sa-legal-skills.zip'
    shutil.copyfile(source / archive.name, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    (output / 'SOURCE_COMMIT.txt').write_text(commit + '\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'docs/releases' / (TAG + '.md'), output / 'RELEASE-NOTES.md')
    print(f'PREPARED (not published): {TAG}, source {commit}, SHA-256 {digest}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare(args.source, args.commit, args.output)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
