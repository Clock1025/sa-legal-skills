#!/usr/bin/env python3
"""Fresh-checkout static/package checks; no model or legal-quality claims."""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zipfile import BadZipFile, ZipFile

SKILLS = ('regulation-review', 'large-scale-reform', 'amendment-drafting')
MEMBERS = ('START-HERE.md', 'LICENSE', *(f'skills/{s}/SKILL.md' for s in SKILLS))
BETA = re.compile(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)-beta\.(0|[1-9][0-9]*)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_sources(root):
    for name in (*MEMBERS, 'README.md', 'scripts/package-release.sh'):
        require((root / name).is_file(), f'missing required file: {name}')
        require(bool((root / name).read_text(encoding='utf-8').strip()), f'empty file: {name}')
    for skill in SKILLS:
        path = f'skills/{skill}/SKILL.md'
        text = (root / path).read_text(encoding='utf-8')
        parts = text.split('---\n', 2)
        require(text.startswith('---\n') and len(parts) == 3, f'invalid frontmatter: {path}')
        header = parts[1].splitlines()
        require(f'name: {skill}' in header, f'Skill name mismatch: {path}')
        require(any(line.startswith('description: ') and line[13:].strip() for line in header),
                f'missing description: {path}')
        require(parts[2].strip().startswith('# '), f'missing Skill heading: {path}')
        for entry in ('README.md', 'START-HERE.md'):
            require(skill in (root / entry).read_text(encoding='utf-8'),
                    f'{entry} does not reference {skill}')
        require(path in (root / 'README.md').read_text(encoding='utf-8'),
                f'README does not link to {path}')
    entry = (root / 'START-HERE.md').read_text(encoding='utf-8')
    require(entry.count('## 可複製提示詞') == 1, 'expected one canonical prompt heading')
    require('https://github.com/Clock1025/sa-legal-skills' in entry, 'missing repository URL')


def validate_zip(root, archive):
    with ZipFile(archive) as zipped:
        names = zipped.namelist()
        require(len(names) == len(MEMBERS) and set(names) == set(MEMBERS),
                f'ZIP members mismatch: {names}')
        require(zipped.testzip() is None, 'ZIP CRC integrity failure')
        for name in MEMBERS:
            info = zipped.getinfo(name)
            require(not info.is_dir() and not info.flag_bits & 1, f'invalid ZIP member: {name}')
            require(zipped.read(name) == (root / name).read_bytes(), f'ZIP content mismatch: {name}')
        with tempfile.TemporaryDirectory(prefix='sa-unzip-') as directory:
            zipped.extractall(directory)
            for name in MEMBERS:
                require((Path(directory) / name).read_bytes() == (root / name).read_bytes(),
                        f'extracted content mismatch: {name}')


def validate_package(root):
    validate_sources(root)
    subprocess.run(['bash', '-n', 'scripts/package-release.sh'], cwd=root, check=True)
    output = root / 'sa-legal-skills.zip'
    digests = []
    for _ in range(2):
        # Each build starts without an output from a previous invocation.
        output.unlink(missing_ok=True)
        subprocess.run(['bash', 'scripts/package-release.sh'], cwd=root, check=True)
        validate_zip(root, output)
        digests.append(hashlib.sha256(output.read_bytes()).hexdigest())
    require(digests[0] == digests[1], 'independent package SHA-256 values differ')
    print(f'PASS: sources, ZIP members/bytes/CRC/extraction, deterministic SHA-256 {digests[0]}')


def validate_beta(root, tag, main_ref='refs/remotes/origin/main'):
    require(BETA.fullmatch(tag) is not None, f'illegal Beta tag: {tag!r}')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    commit = git('rev-parse', '--verify', f'refs/tags/{tag}^{{commit}}')
    require(git('rev-parse', 'HEAD') == commit, 'checkout HEAD is not the Beta tag commit')
    result = subprocess.run(['git', 'merge-base', '--is-ancestor', commit, main_ref], cwd=root)
    require(result.returncode == 0, 'Beta tag commit is not in main history (or history unavailable)')
    print(f'PASS: Beta tag {tag} resolves to checked-out main-history commit {commit}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--beta-tag')
    args = parser.parse_args()
    try:
        if args.beta_tag is not None:
            validate_beta(args.root, args.beta_tag)
        validate_package(args.root)
    except (ValueError, OSError, BadZipFile, subprocess.SubprocessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
