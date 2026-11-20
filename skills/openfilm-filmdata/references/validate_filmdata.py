"""Read-only FilmData structural validator for Video-hoat-hinh hybrid pipeline.

No network or imports beyond Python standard library. This does not render video,
validate a TTS voice, or claim asset licenses. All errors print to stderr.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


def _integer(value: Any, minimum: int = 0) -> bool:
    return type(value) is int and value >= minimum


def _safe_relative(path: Any) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    a, w = PurePosixPath(path), PureWindowsPath(path)
    return not a.is_absolute() and not w.is_absolute() and not w.drive and all(
        part not in ("", "..", ".") for part in path.split("/")
    ) and ":" not in path


def validate(data: Any, assets_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["FilmData: expected JSON object"]
    expected = {"schemaVersion", "filmId", "masterEngine", "fps", "width", "height", "durationInFrames", "shots", "dialogues"}
    missing = expected - data.keys()
    if missing:
        errors.append("missing required fields: " + ", ".join(sorted(missing)))
    if data.get("schemaVersion") != 1 or type(data.get("schemaVersion")) is not int:
        errors.append("schemaVersion must equal integer 1")
    if not isinstance(data.get("filmId"), str) or not data.get("filmId"):
        errors.append("filmId must be a nonempty string")
    if data.get("masterEngine") not in ("openfilm", "remotion"):
        errors.append("masterEngine must be openfilm/remotion")
    for field in ("fps", "width", "height", "durationInFrames"):
        if not _integer(data.get(field), 1):
            errors.append(f"{field} must be positive integer")
    shots = data.get("shots")
    dialogues = data.get("dialogues")
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty array")
        shots = []
    if not isinstance(dialogues, list):
        errors.append("dialogues must be an array")
        dialogues = []
    shot_map: dict[str, dict] = {}
    expected_next = 0
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict):
            errors.append(f"shots[{i}] expected object")
            continue
        sid = shot.get("id")
        start, duration = shot.get("startFrame"), shot.get("durationInFrames")
        if not isinstance(sid, str) or not sid:
            errors.append(f"shots[{i}] id missing")
        elif sid in shot_map:
            errors.append(f"duplicate shot ID: {sid}")
        else:
            shot_map[sid] = shot
        if not _integer(start) or not _integer(duration, 1):
            errors.append(f"shots[{i}] startFrame/durationInFrames invalid")
            continue
        if start < expected_next:
            errors.append(f"shots[{i}] overlap: starts {start}, expected {expected_next}")
        elif start > expected_next:
            errors.append(f"shots[{i}] gap: starts {start}, expected {expected_next}")
        expected_next = start + duration
        if shot.get("type") not in ("2d", "3d") or not isinstance(shot.get("scene"), str) or not shot.get("scene"):
            errors.append(f"shots[{i}] invalid type or scene")
    if _integer(data.get("durationInFrames"), 1) and expected_next != data["durationInFrames"]:
        errors.append(f"film duration mismatch: shots end {expected_next}, film {data['durationInFrames']}")
    dialog_ids: set[str] = set()
    for i, dial in enumerate(dialogues):
        if not isinstance(dial, dict):
            errors.append(f"dialogues[{i}] expected object")
            continue
        did, sid = dial.get("id"), dial.get("shotId")
        if not isinstance(did, str) or not did:
            errors.append(f"dialogues[{i}] id missing")
        elif did in dialog_ids:
            errors.append(f"duplicate dialogue ID: {did}")
        else:
            dialog_ids.add(did)
        if sid not in shot_map:
            errors.append(f"dialogues[{i}] unknown shotId: {sid}")
        for field in ("speaker", "text"):
            if not isinstance(dial.get(field), str) or not dial[field]:
                errors.append(f"dialogues[{i}] missing {field}")
        start, end = dial.get("startFrame"), dial.get("endFrame")
        if not _integer(start) or not _integer(end, 1) or (type(start) is int and type(end) is int and start >= end):
            errors.append(f"dialogues[{i}] invalid frame interval")
        elif sid in shot_map and _integer(shot_map[sid].get("startFrame")) and _integer(shot_map[sid].get("durationInFrames"), 1):
            s = shot_map[sid]
            if start < s["startFrame"] or end > s["startFrame"] + s["durationInFrames"]:
                errors.append(f"dialogues[{i}] outside shot {sid}")
        audio = dial.get("audio")
        if not _safe_relative(audio):
            errors.append(f"dialogues[{i}] invalid audio path: {audio!r}")
        elif assets_root is not None:
            base = Path(assets_root).resolve()
            dest = (base / audio).resolve()
            if not dest.is_relative_to(base):
                errors.append(f"dialogues[{i}] escaped assets path")
            elif not dest.is_file():
                errors.append(f"dialogues[{i}] missing asset: {audio}")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("film_json", type=Path)
    p.add_argument("--check-assets", type=Path, metavar="PROJECT_ROOT", default=None)
    args = p.parse_args()
    try:
        film = json.loads(args.film_json.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(film, args.check_assets)
    if errors:
        for err in errors:
            print("FAIL: " + err, file=sys.stderr)
        return 1
    print("PASS: FilmData structure valid" + ("; referenced WAV files exist" if args.check_assets else "; assets NOT checked"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
