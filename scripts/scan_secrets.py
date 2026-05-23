from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_SUFFIXES = {
    ".lock",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pyc",
}
SKIP_PARTS = {
    ".git",
    ".next",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
}
SAFE_VALUES = {
    "",
    "changeme",
    "development",
    "dummy",
    "example",
    "localhost",
    "nettrace",
    "sample",
    "test",
}
PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?([^'\"\s#]+)"
    ),
)


def main() -> int:
    findings = scan_tracked_files()
    if findings:
        for finding in findings:
            print(finding)
        return 1
    print("No secrets found in tracked files.")
    return 0


def scan_tracked_files() -> list[str]:
    findings: list[str] = []
    for path in _tracked_files():
        if _should_skip(path):
            continue
        text = _read_text(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _line_has_secret(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: possible secret")
    return findings


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / item for item in result.stdout.splitlines()]


def _should_skip(path: Path) -> bool:
    relative_parts = set(path.relative_to(ROOT).parts)
    return bool(relative_parts & SKIP_PARTS) or path.suffix.lower() in SKIP_SUFFIXES


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _line_has_secret(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False

    for pattern in PATTERNS:
        match = pattern.search(stripped)
        if match is None:
            continue
        if match.groups() and _is_safe_value(match.group(1)):
            continue
        return True
    return False


def _is_safe_value(value: str) -> bool:
    normalized = value.strip().strip("'\"").lower()
    normalized = normalized.split(":", maxsplit=1)[0]
    return normalized in SAFE_VALUES or normalized.startswith("${")


if __name__ == "__main__":
    sys.exit(main())
