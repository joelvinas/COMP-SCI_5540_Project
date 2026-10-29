"""Guard: version literals live only in config/spark_versions.toml."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VERSION_FILE = REPO_ROOT / "config" / "spark_versions.toml"

SCAN_GLOBS = [
    "src/**/*.py",
    "config/**/*",
    "**/Dockerfile*",
    "requirements*.txt",
    "scripts/**/*",
]
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "docs", "tests"}

# A pyspark/spark/hadoop token followed within a short span by a dotted version number.
LITERAL = re.compile(r"(?i)(pyspark|spark|hadoop)[^\n]{0,20}?\d+\.\d+")


def find_offenders(root: Path, globs=SCAN_GLOBS, exempt=VERSION_FILE) -> list[Path]:
    offenders = set()
    for pattern in globs:
        for path in root.glob(pattern):
            rel_parts = set(path.relative_to(root).parts)
            if not path.is_file() or path == exempt or rel_parts & EXCLUDED_PARTS:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if LITERAL.search(text):
                offenders.add(path)
    return sorted(offenders)


def test_repository_has_no_stray_version_literals():
    assert find_offenders(REPO_ROOT) == []


def test_guard_flags_a_planted_literal_and_exempts_version_file(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "config").mkdir()
    bad = tmp_path / "src" / "bad.py"
    bad.write_text('SPARK = "spark 3.5.1"\n', encoding="utf-8")
    pin = tmp_path / "config" / "spark_versions.toml"
    pin.write_text('spark = "3.5.1"\n', encoding="utf-8")
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("RUN pip install pyspark==3.5.1\n", encoding="utf-8")
    assert find_offenders(tmp_path, exempt=pin) == sorted([dockerfile, bad])
