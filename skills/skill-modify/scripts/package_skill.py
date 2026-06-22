#!/usr/bin/env python3
"""
// Input: skill 目录路径（必填）+ 可选输出目录。
// Output: 生成 .skill 打包文件；失败时返回非 0。
// Pos: skill-modify/scripts - 交付前打包与分发助手。
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
from pathlib import Path

try:
    from scripts.quick_validate import validate_skill
except Exception:
    # Support direct execution: python scripts/package_skill.py ...
    from quick_validate import validate_skill


EXCLUDE_DIRS = {"__pycache__", "node_modules"}
ROOT_EXCLUDE_DIRS = {"evals"}
EXCLUDE_FILES = {".DS_Store"}
EXCLUDE_GLOBS = {"*.pyc"}


def should_exclude(archive_rel_path: Path) -> bool:
    parts = archive_rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True

    # archive_rel_path is relative to skill_path.parent.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True

    name = archive_rel_path.name
    if name in EXCLUDE_FILES:
        return True

    return any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_GLOBS)


def package_skill(skill_path: Path, output_dir: Path | None = None) -> Path | None:
    skill_path = skill_path.resolve()
    if not skill_path.exists():
        print(f"[ERROR] Skill directory not found: {skill_path}")
        return None
    if not skill_path.is_dir():
        print(f"[ERROR] Not a directory: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md not found in {skill_path}")
        return None

    print("[INFO] Validating skill before packaging...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"[ERROR] Validation failed: {message}")
        return None
    print(f"[OK] {message}")

    if output_dir is None:
        output_dir = Path.cwd()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    archive_path = output_dir / f"{skill_path.name}.skill"
    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as bundle:
            for file_path in skill_path.rglob("*"):
                if not file_path.is_file():
                    continue
                archive_rel_path = file_path.relative_to(skill_path.parent)
                if should_exclude(archive_rel_path):
                    print(f"[SKIP] {archive_rel_path}")
                    continue
                bundle.write(file_path, archive_rel_path)
                print(f"[ADD]  {archive_rel_path}")
    except Exception as exc:
        print(f"[ERROR] Failed to create archive: {exc}")
        return None

    print(f"[OK] Packaged skill: {archive_path}")
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Package a skill directory into a .skill archive."
    )
    parser.add_argument("skill_dir", help="Path to the target skill directory.")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Optional output directory for the .skill file.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    output_dir = Path(args.output_dir) if args.output_dir else None

    archive_path = package_skill(skill_dir, output_dir)
    return 0 if archive_path else 1


if __name__ == "__main__":
    raise SystemExit(main())
