#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required to create sa-legal-skills.zip." >&2
  exit 1
fi

python3 - "$REPO_ROOT" <<'PY'
from pathlib import Path
import os
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(sys.argv[1]).resolve()
members = (
    "START-HERE.md",
    "LICENSE",
    "skills/regulation-review/SKILL.md",
    "skills/large-scale-reform/SKILL.md",
    "skills/amendment-drafting/SKILL.md",
)
missing = [name for name in members if not (root / name).is_file()]
if missing:
    for name in missing:
        print(f"Error: required release file is missing: {name}", file=sys.stderr)
    raise SystemExit(1)

output = root / "sa-legal-skills.zip"
temporary_path = None
try:
    with tempfile.NamedTemporaryFile(
        prefix=".sa-legal-skills-", suffix=".tmp", dir=root, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)

    with ZipFile(temporary_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in members:
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / name).read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)

    os.replace(temporary_path, output)
    temporary_path = None
except Exception as exc:
    print(f"Error: could not create {output.name}: {exc}", file=sys.stderr)
    raise SystemExit(1)
finally:
    if temporary_path is not None:
        temporary_path.unlink(missing_ok=True)

print(f"Created {output}")
PY
