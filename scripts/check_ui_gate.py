#!/usr/bin/env python3
"""UI gate (kit-owned) — makes "backend without frontend" un-committable. Paths come from kit.json.

Run from the repo root (verify.sh does this). Stdlib only. Exit 1 on any violation.

Rules (docs/DEFINITION_OF_DONE.md "UI surface gate", made mechanical):
  R1  UI debt blocks progress: if any slice is `backend-complete, UI pending`, no LATER slice in
      docs/screen-registry.json may be IN_PROGRESS or ACCEPTED. Pay the UI debt first.
  R2  At most one UI slice IN_PROGRESS at a time (backend-only/infra slices such as OPS-001 may run
      alongside).
  R3  A UI slice may not start (IN_PROGRESS/ACCEPTED) until its SCR-ids are defined in the registry
      and in docs/PRODUCT_EXPERIENCE_SPEC.md.
  R4  Every screen of an ACCEPTED slice:
        a) is rendered by a component under frontend/src with the root marker data-screen="SCR-…",
        b) has a Playwright spec under frontend/e2e tagged @SCR-… .
  R5  Playwright config defines both a "phone" and a "desktop" project (every spec runs at both).
  R6  e2e specs never mock the API (no page.route / route.fulfill / context.route / msw).
  R8  Every screen of an ACCEPTED slice has committed screenshots
      frontend/e2e/screens/<SCR-id>--phone.png and --desktop.png (written by the e2e helper), so the
      owner can look at the real UI each slice without running anything.
  R7  PROGRESS.md statuses are one of the allowed values, and every registry slice appears in it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = json.loads((ROOT / "kit.json").read_text(encoding="utf-8"))
_UG = KIT.get("ui_gate", {})
REGISTRY = ROOT / KIT["docs"]["screen_registry"]
PES = ROOT / KIT["docs"]["experience_spec"]
PROGRESS = ROOT / "PROGRESS.md"
FE_SRC = ROOT / _UG.get("frontend_src", "frontend/src")
FE_E2E = ROOT / _UG.get("frontend_e2e", "frontend/e2e")
SHOTS = ROOT / _UG.get("screenshots", "frontend/e2e/screens")
PW_CONFIGS = [ROOT / p for p in _UG.get("playwright_configs", ["frontend/playwright.config.ts"])]
SLICE_RE = KIT.get("slice_id_pattern", r"(BOOT|OPS|VS)-\d{3}")

ALLOWED = {"NOT_STARTED", "IN_PROGRESS", "ACCEPTED", "backend-complete, UI pending"}
STARTED = {"IN_PROGRESS", "ACCEPTED", "backend-complete, UI pending"}
UI_PENDING = "backend-complete, UI pending"
MOCK_PATTERNS = re.compile(r"\b(page|context)\.route\(|\broute\.fulfill\(|from ['\"]msw|setupServer\(|setupWorker\(")

violations: list[str] = []
notes: list[str] = []


def bad(msg: str) -> None:
    violations.append(msg)


def read_texts(base: Path, exts: tuple[str, ...]) -> dict[Path, str]:
    if not base.is_dir():
        return {}
    out: dict[Path, str] = {}
    for p in base.rglob("*"):
        if p.suffix in exts and p.is_file() and "node_modules" not in p.parts:
            out[p] = p.read_text(encoding="utf-8", errors="replace")
    return out


def parse_progress() -> dict[str, str]:
    statuses: dict[str, str] = {}
    if not PROGRESS.is_file():
        bad("PROGRESS.md missing")
        return statuses
    for line in PROGRESS.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and re.fullmatch(SLICE_RE, cells[0]):
            statuses[cells[0]] = cells[3]
    return statuses


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["slices"]
    order = [s["id"] for s in registry]
    statuses = parse_progress()
    pes_text = PES.read_text(encoding="utf-8") if PES.is_file() else ""

    # R7
    for sid, st in statuses.items():
        if st not in ALLOWED:
            bad(f"R7 PROGRESS.md: {sid} has status '{st}' — allowed: {sorted(ALLOWED)}")
    for sid in order:
        if sid not in statuses:
            bad(f"R7 PROGRESS.md: slice {sid} from screen-registry.json is missing")

    # R1
    pending = [sid for sid in order if statuses.get(sid) == UI_PENDING]
    if pending:
        first = order.index(pending[0])
        for sid in order[first + 1:]:
            if statuses.get(sid) in {"IN_PROGRESS", "ACCEPTED", UI_PENDING}:
                bad(f"R1 UI debt: {pending[0]} is '{UI_PENDING}' but later slice {sid} is "
                    f"'{statuses[sid]}'. Build {pending[0]}'s screens before moving on.")

    # R2
    ui_ids = {s["id"] for s in registry if s["ui"]}
    in_progress = [sid for sid in order if statuses.get(sid) == "IN_PROGRESS" and sid in ui_ids]
    if len(in_progress) > 1:
        bad(f"R2 more than one UI slice IN_PROGRESS: {in_progress}")

    src = read_texts(FE_SRC, (".tsx", ".ts", ".jsx", ".js"))
    e2e = read_texts(FE_E2E, (".ts", ".tsx", ".js", ".mts"))
    src_all = "\n".join(src.values())
    e2e_all = "\n".join(e2e.values())

    for s in registry:
        sid, st = s["id"], statuses.get(s["id"], "NOT_STARTED")
        if not s["ui"] or st not in STARTED:
            continue
        # R3
        if not s["screens"]:
            bad(f"R3 {sid} is '{st}' but has no SCR-ids — define its screens in "
                f"PRODUCT_EXPERIENCE_SPEC.md and docs/screen-registry.json before starting.")
            continue
        for scr in s["screens"]:
            if scr not in pes_text:
                bad(f"R3 {sid}: {scr} is not described in PRODUCT_EXPERIENCE_SPEC.md")
        # R4 (enforced for ACCEPTED; reported as progress for IN_PROGRESS)
        missing = []
        for scr in s["screens"]:
            has_marker = re.search(r"data-screen\s*=\s*[{]?\s*['\"]" + re.escape(scr) + r"['\"]", src_all)
            has_e2e = re.search(r"@" + re.escape(scr) + r"\b", e2e_all)
            if not has_marker:
                missing.append(f"{scr}: no component with data-screen=\"{scr}\" in frontend/src")
            if not has_e2e:
                missing.append(f"{scr}: no Playwright spec tagged @{scr} in frontend/e2e")
            for proj in ("phone", "desktop"):
                if not (SHOTS / f"{scr}--{proj}.png").is_file():
                    missing.append(f"{scr}: no screenshot frontend/e2e/screens/{scr}--{proj}.png")
        if st == "ACCEPTED":
            for m in missing:
                bad(f"R4 {sid} is ACCEPTED but {m}")
        elif st == "IN_PROGRESS" and missing:
            notes.append(f"{sid} UI still to build ({len(missing)} item(s)): " + "; ".join(missing))

    # R5 (once any UI slice has started)
    if any(s["ui"] and statuses.get(s["id"]) in STARTED for s in registry):
        cfg = next((p for p in PW_CONFIGS if p.is_file()), None)
        if cfg is None:
            bad("R5 no frontend/playwright.config.* found")
        else:
            text = cfg.read_text(encoding="utf-8")
            for proj in ("phone", "desktop"):
                if not re.search(r"name\s*:\s*['\"]" + proj + r"['\"]", text):
                    bad(f"R5 playwright config has no project named '{proj}' — every screen must be "
                        f"tested at phone (360px) and desktop (1280px)")

    # R6
    for path, text in e2e.items():
        for i, line in enumerate(text.splitlines(), 1):
            if MOCK_PATTERNS.search(line):
                bad(f"R6 {path.relative_to(ROOT)}:{i}: e2e must hit the real API — no route mocking")

    for n in notes:
        print(f"  (in progress) {n}")
    for v in violations:
        print(f"VIOLATION: {v}")
    print("UI gate PASSED." if not violations else f"UI gate FAILED ({len(violations)} violation(s)).")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
