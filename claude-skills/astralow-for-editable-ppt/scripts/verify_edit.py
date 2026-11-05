#!/usr/bin/env python3
"""Roundtrip edit verification for a single-slide editable PPTX.

Replacement for the Windows-only verify-edit.ps1 in the Claude Code port.

The test edits a COPY of the deck with python-pptx, saves it, reopens it,
and checks that the edited text persisted. It also confirms the source file
hash is unchanged.

This verifies the file roundtrips through python-pptx and that text objects
are genuinely editable. It is NOT Office rendering verification; it does not
prove how PowerPoint/WPS will render the file, and it does not test chart
data series, formulas, or pixels inside cropped images.

Usage:
    python verify_edit.py --deck <final.pptx> --out <dir> --edits <edits.json>

edits.json format:
    [{"old": "当前标题", "new": "编辑测试标题"}, {"old": "12.5", "new": "13.5"}]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pptx import Presentation


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_text_shapes(shapes: Any, path_prefix: str = "slide:1"):
    """Yield (object_path, shape) for every shape with a text frame,
    including group children and table cells, exactly once each."""

    for index, shape in enumerate(shapes, start=1):
        object_path = f"{path_prefix}/shape:{index}"
        try:
            if shape.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
                yield from iter_text_shapes(shape.shapes, f"{object_path}/group")
            elif shape.has_table:
                table = shape.table
                for r in range(len(table.rows)):
                    for c in range(len(table.columns)):
                        cell = table.cell(r, c)
                        yield f"{object_path}/cell:{r + 1},{c + 1}", cell
            elif shape.has_text_frame and str(shape.text_frame.text).strip():
                yield object_path, shape
        except Exception:
            continue


def find_and_edit(shape: Any, old: str, new: str) -> tuple[bool, str]:
    """Replace ``old`` with ``new`` inside a shape's text, preserving run
    formatting. Returns (matched, full_text_before)."""

    frame = shape.text_frame
    full_before = str(frame.text)

    # 1. Exact match inside a single run: replace the run text in place.
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            if run.text == old:
                run.text = new
                return True, full_before

    # 2. Substring match inside a single run.
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            if old in run.text:
                run.text = run.text.replace(old, new)
                return True, full_before

    # 3. Whole-frame exact match spanning multiple runs: collapse into the
    # first run and drop the rest, so the edit persists as one run.
    if full_before == old:
        for paragraph in frame.paragraphs:
            runs = list(paragraph.runs)
            if runs:
                runs[0].text = new
                for extra in runs[1:]:
                    extra._r.getparent().remove(extra._r)
                return True, full_before

    return False, full_before


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--edits", type=Path, required=True)
    args = parser.parse_args()

    rules = json.loads(args.edits.read_text(encoding="utf-8"))
    if not isinstance(rules, list) or not rules:
        raise SystemExit("edits JSON must be a non-empty array")
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict) or not rule.get("old") or not rule.get("new"):
            raise SystemExit(f"edit rule {i} must contain old and new strings")
        if rule["old"] == rule["new"]:
            raise SystemExit(f"edit rule {i} has identical old and new values")

    args.out.mkdir(parents=True, exist_ok=True)
    run_dir = args.out / f"run-{uuid.uuid4().hex[:12]}"
    run_dir.mkdir(parents=True, exist_ok=True)
    copy_path = run_dir / "edited-copy.pptx"
    result_path = args.out / "real-edit-verification.json"

    source_hash_before = sha256(args.deck)
    result: dict[str, Any] = {
        "source": str(args.deck),
        "editsPath": str(args.edits),
        "outputDirectory": str(args.out),
        "runDirectory": str(run_dir),
        "editedCopy": str(copy_path),
        "passed": False,
        "sourceUnchanged": False,
        "rules": rules,
        "changes": [],
        "objects": [],
        "objectChecks": [],
        "error": None,
        "testedAt": None,
        "note": "python-pptx roundtrip verification; not Office rendering verification.",
    }

    objects: list[dict[str, Any]] = []
    try:
        shutil.copyfile(args.deck, copy_path)
        prs = Presentation(str(copy_path))
        slide = prs.slides[0]

        matched = [False] * len(rules)
        expected_by_path: dict[str, str] = {}

        for object_path, shape in iter_text_shapes(slide.shapes):
            text_before = str(shape.text_frame.text)
            objects.append(
                {"path": object_path, "name": shape.name, "textBefore": text_before}
            )
            for index, rule in enumerate(rules):
                if matched[index]:
                    continue
                ok, full_before = find_and_edit(shape, rule["old"], rule["new"])
                if not ok:
                    continue
                matched[index] = True
                full_after = str(shape.text_frame.text)
                expected_by_path[object_path] = full_after
                result["changes"].append(
                    {
                        "ruleIndex": index,
                        "objectPath": object_path,
                        "objectName": shape.name,
                        "before": rule["old"],
                        "after": rule["new"],
                        "fullTextBefore": full_before,
                        "fullTextAfterThisRule": full_after,
                    }
                )

        prs.save(str(copy_path))

        # Reopen and check the edited text persisted.
        reopened = Presentation(str(copy_path))
        reopened_slide = reopened.slides[0]
        reopened_texts: dict[str, str] = {}
        for object_path, shape in iter_text_shapes(reopened_slide.shapes):
            reopened_texts[object_path] = str(shape.text_frame.text)

        for object_path, expected in expected_by_path.items():
            actual = reopened_texts.get(object_path)
            result["objectChecks"].append(
                {
                    "objectPath": object_path,
                    "expectedFullText": expected,
                    "actualFullText": actual,
                    "matched": actual == expected,
                }
            )

        missing = [i for i, found in enumerate(matched) if not found]
        bad = [c for c in result["objectChecks"] if not c["matched"]]
        if missing:
            raise RuntimeError(
                "At least one occurrence was not found for rule index: "
                + ", ".join(str(i) for i in missing)
            )
        if bad:
            raise RuntimeError(
                "Reopened object text did not match expected text for: "
                + ", ".join(c["objectPath"] for c in bad)
            )
        result["passed"] = True
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        source_hash_after = sha256(args.deck)
        result["sourceUnchanged"] = source_hash_before == source_hash_after
        result["objects"] = objects
        result["testedAt"] = datetime.now(timezone.utc).isoformat()
        if not result["sourceUnchanged"]:
            result["passed"] = False
            if not result["error"]:
                result["error"] = "Source PPTX hash changed."
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
