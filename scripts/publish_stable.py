#!/usr/bin/env python3
"""One-time, fixed-source v0.1.4 release. No overwrite or automatic recovery."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.error
import urllib.request

REPO = 'Clock1025/sa-legal-skills'
COMMIT = '6aa5c775d8ea011ea4b2380ef467591a6966070a'
TAG = 'v0.1.4'
TITLE = 'v0.1.4 — 決策管理與修法文件品質改善'
SHA256 = 'ee933fe8fd06f50a6d7ea42d5a5164586cf08a825b1a3fb68d6f33c17a34152b'
ASSETS = ('sa-legal-skills.zip', 'SHA256SUMS.txt')
PROTECTED = ('v0.1.3', 'v0.1.4-rc.1')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validation(source):
    source = Path(source).resolve()
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    require(actual == COMMIT, 'candidate checkout is not the fixed accepted Commit')
    spec = importlib.util.spec_from_file_location('stable_candidate_validation', source / 'scripts/validate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in module.MEMBERS:
        original = subprocess.check_output(['git', 'show', f'{COMMIT}:{name}'], cwd=source)
        require((source / name).read_bytes() == original, f'candidate source changed: {name}')
    return module


def check_package(source, package):
    package = Path(package)
    require({p.name for p in package.iterdir()} == set(ASSETS), 'unexpected or missing artifact files')
    archive = package / ASSETS[0]
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == SHA256, 'ZIP SHA-256 mismatch')
    require((package / ASSETS[1]).read_bytes() == f'{SHA256}  {ASSETS[0]}\n'.encode(),
            'checksum file mismatch')
    validation(source).validate_zip(Path(source).resolve(), archive)
    subprocess.run(['sha256sum', '--check', ASSETS[1]], cwd=package, check=True)


def prepare(source, package):
    source, package = Path(source).resolve(), Path(package).resolve()
    module = validation(source)
    module.validate_package(source)
    package.mkdir(exist_ok=False)
    (package / ASSETS[0]).write_bytes((source / ASSETS[0]).read_bytes())
    digest = hashlib.sha256((package / ASSETS[0]).read_bytes()).hexdigest()
    (package / ASSETS[1]).write_text(f'{digest}  {ASSETS[0]}\n', encoding='utf-8')
    check_package(source, package)


class GitHub:
    def __init__(self):
        self.token = os.environ['GH_TOKEN']

    def request(self, method, path, data=None, absent_ok=False):
        body = None if data is None else json.dumps(data).encode()
        request = urllib.request.Request(f'https://api.github.com/repos/{REPO}/{path}',
            data=body, method=method, headers={
                'Authorization': 'Bearer ' + self.token,
                'Accept': 'application/vnd.github+json',
                'Content-Type': 'application/json',
                'X-GitHub-Api-Version': '2022-11-28',
            })
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if absent_ok and error.code == 404:
                return None
            raise ValueError(f'GitHub {method} {path}: HTTP {error.code}') from None
        except urllib.error.URLError:
            raise ValueError('GitHub API connection failed; stopped without retry') from None

    def upload(self):
        subprocess.run(['gh', 'release', 'upload', TAG, *ASSETS, '--repo', REPO], check=True)

    def download(self, directory):
        subprocess.run(['gh', 'release', 'download', TAG, '--repo', REPO,
                        '--dir', str(directory), '--pattern', ASSETS[0], '--pattern', ASSETS[1]], check=True)


def ensure_absent(api):
    require(api.request('GET', f'git/ref/tags/{TAG}', absent_ok=True) is None,
            'Tag already exists; inspect it manually, do not overwrite')
    # List authenticated releases too, to include unpublished drafts.
    page = 1
    while True:
        releases = api.request('GET', f'releases?per_page=100&page={page}')
        require(not any(r['tag_name'] == TAG for r in releases),
                'Release or draft already exists; inspect it manually, do not overwrite')
        if len(releases) < 100:
            break
        page += 1


def verify_release(api, release_id, source, draft, notes):
    release = api.request('GET', f'releases/{release_id}')
    require(release['tag_name'] == TAG and release['draft'] is draft
            and release['prerelease'] is False, 'Release tag or visibility mismatch')
    require(release['name'] == TITLE and release['body'] == notes, 'Release notes/title mismatch')
    assets = release['assets']
    require(len(assets) == 2 and {a['name'] for a in assets} == set(ASSETS), 'Release assets mismatch')
    with tempfile.TemporaryDirectory(prefix='stable-download-') as directory:
        api.download(directory)
        check_package(source, directory)
        for asset in assets:
            require(asset['state'] == 'uploaded'
                    and asset['size'] == (Path(directory) / asset['name']).stat().st_size,
                    'Release asset state or size mismatch')
    return release


def publish(api, source, package, notes):
    check_package(source, package)
    require(bool(notes.strip()), 'empty Release Notes')
    ensure_absent(api)
    protected = {tag: api.request('GET', f'git/ref/tags/{tag}')['object'] for tag in PROTECTED}
    ref = api.request('POST', 'git/refs', {'ref': f'refs/tags/{TAG}', 'sha': COMMIT})
    require(ref['object']['type'] == 'commit' and ref['object']['sha'] == COMMIT, 'created Tag mismatch')
    draft = api.request('POST', 'releases', {'tag_name': TAG, 'target_commitish': COMMIT,
        'name': TITLE, 'body': notes, 'draft': True, 'prerelease': False, 'make_latest': 'false'})
    # Failure leaves the Tag/draft for manual inspection. Never delete, clobber or resume automatically.
    previous = Path.cwd()
    try:
        os.chdir(package)
        api.upload()
    finally:
        os.chdir(previous)
    release_id = draft['id']
    verify_release(api, release_id, source, True, notes)
    require(api.request('GET', f'git/ref/tags/{TAG}')['object'] == ref['object'], 'Tag changed before publication')
    api.request('PATCH', f'releases/{release_id}', {'draft': False, 'prerelease': False, 'make_latest': 'true'})
    release = verify_release(api, release_id, source, False, notes)
    require(api.request('GET', 'releases/latest')['id'] == release_id, 'Latest mismatch')
    require(api.request('GET', f'git/ref/tags/{TAG}')['object'] == ref['object'], 'Tag changed after publication')
    for tag, obj in protected.items():
        require(api.request('GET', f'git/ref/tags/{tag}')['object'] == obj, f'protected Tag changed: {tag}')
    print('PASS: public Stable Release, fixed Tag, downloaded assets/checksum and Latest')
    print(release['html_url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'publish'))
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--notes', type=Path)
    args = parser.parse_args()
    try:
        if args.mode == 'prepare':
            prepare(args.source, args.package)
        else:
            require(os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
                    and os.environ.get('GITHUB_REF') == 'refs/heads/main'
                    and os.environ.get('GITHUB_REPOSITORY') == REPO,
                    'publication is only allowed by manual dispatch on repository main')
            require(args.notes is not None, 'Release Notes path required')
            publish(GitHub(), args.source.resolve(), args.package.resolve(), args.notes.read_text(encoding='utf-8'))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'FAIL: {error}\n')


if __name__ == '__main__':
    main()
