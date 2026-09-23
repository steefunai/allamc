#!/usr/bin/env python3
"""Validates NOW.md's machine-readable header (kit-owned). Stdlib only.

The portfolio script reads this header from every product, so its shape is a contract.
Usage: python scripts/check_now.py [path/to/NOW.md]   → exit 1 on a malformed header.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = {
    "product": "text", "mode": ("discovery", "active", "maintain", "paused"), "stage": "stage",
    "gate_blockers": "int", "in_progress": "text", "verify": ("green", "red", "unknown"),
    "ui_debt": "int", "last_user_session": "date_or_never", "last_weekly_review": "date_or_never",
    "waiting_on_owner": "int", "updated": "date",
}


def parse_header(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        raise ValueError("NOW.md must start with a --- header block")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line).strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"bad header line: {line!r}")
        out[key.strip()] = value.strip().strip("'\"")
    return out


def _is_date(v: str) -> bool:
    try:
        date.fromisoformat(v)
        return True
    except ValueError:
        return False


def validate(h: dict[str, str]) -> list[str]:
    errs = []
    for key, kind in REQUIRED.items():
        v = h.get(key)
        if v is None or v == "":
            errs.append(f"missing '{key}'")
            continue
        if isinstance(kind, tuple) and v not in kind:
            errs.append(f"'{key}' must be one of {kind}, got '{v}'")
        elif kind == "int" and not v.isdigit():
            errs.append(f"'{key}' must be a non-negative integer, got '{v}'")
        elif kind == "stage" and not (v.isdigit() and 0 <= int(v) <= 6):
            errs.append(f"'stage' must be 0–6, got '{v}'")
        elif kind == "date" and not _is_date(v):
            errs.append(f"'{key}' must be YYYY-MM-DD, got '{v}'")
        elif kind == "date_or_never" and v != "never" and not _is_date(v):
            errs.append(f"'{key}' must be YYYY-MM-DD or never, got '{v}'")
    if h.get("product", "").startswith("{{"):
        errs.append("'product' still has the template placeholder — run scripts/new-product.sh")
    return errs


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    if (root / ".kit-template").exists():
        print("NOW.md header: skipped (this is the kit template repo).")
        return 0
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "NOW.md"
    try:
        errs = validate(parse_header(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        errs = [str(e)]
    for e in errs:
        print(f"VIOLATION: NOW.md header: {e}")
    print("NOW.md header OK." if not errs else "NOW.md header INVALID.")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
