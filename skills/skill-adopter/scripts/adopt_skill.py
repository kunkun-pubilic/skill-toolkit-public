#!/usr/bin/env python3
"""Adopt an upstream Agent Skill and write a reproducible skills-lock.json."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


IGNORED_NAMES = {".git", "__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}


class Blocked(RuntimeError):
    """Raised when adoption cannot be proven."""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    except FileNotFoundError as exc:
        raise Blocked(f"required command missing: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise Blocked(f"command failed: {' '.join(cmd)}\n{detail}") from exc
    return completed.stdout.strip()


def is_remote_source(source: str) -> bool:
    return bool(re.match(r"^(https?|ssh)://", source)) or source.startswith("git@") or source.endswith(".git")


def clone_or_resolve_source(source: str, ref: str, temp_root: Path) -> tuple[Path, str, str]:
    local = Path(source).expanduser()
    if local.exists():
        local_repo = local.resolve()
        if (local_repo / ".git").exists() and ref:
            repo = temp_root / "local-source"
            run(["git", "clone", local_repo.as_posix(), repo.as_posix()])
            run(["git", "checkout", ref], cwd=repo)
            commit = run(["git", "rev-parse", "HEAD"], cwd=repo)
            return repo, "local-git", commit
        repo = local_repo
        commit = ""
        if (repo / ".git").exists():
            commit = run(["git", "rev-parse", "HEAD"], cwd=repo)
        return repo, "local", commit

    if not is_remote_source(source):
        raise Blocked(f"source is neither an existing path nor a Git URL: {source}")

    repo = temp_root / "source"
    run(["git", "clone", source, repo.as_posix()])
    if ref:
        run(["git", "checkout", ref], cwd=repo)
    commit = run(["git", "rev-parse", "HEAD"], cwd=repo)
    return repo, "git", commit


def should_ignore(path: Path) -> bool:
    if any(part in IGNORED_NAMES for part in path.parts):
        return True
    return path.suffix in IGNORED_SUFFIXES


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if should_ignore(rel):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hash(root: Path) -> tuple[str, list[dict[str, Any]]]:
    digest = sha256()
    files: list[dict[str, Any]] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        file_hash = hash_file(path)
        size = path.stat().st_size
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
        files.append({"path": rel, "sha256": file_hash, "bytes": size})
    return digest.hexdigest(), files


def classify_source_file(path: str) -> str:
    parts = path.split("/")
    suffix = Path(path).suffix.lower()
    if path == "SKILL.md" or suffix in {".md", ".markdown", ".txt", ".yaml", ".yml", ".json"}:
        return "rule_text"
    if "scripts" in parts or suffix in {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".ts", ".tsx"}:
        return "executable_script"
    if "assets" in parts:
        return "runtime_asset"
    if "fixtures" in parts or "examples" in parts or "templates" in parts:
        return "fixture_or_template"
    return "source_payload"


def payload_role_counts(files: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        role = classify_source_file(str(item["path"]))
        counts[role] = counts.get(role, 0) + 1
    return dict(sorted(counts.items()))


def parse_skill_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise Blocked(f"SKILL.md missing YAML frontmatter: {skill_md}")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise Blocked(f"SKILL.md has invalid YAML frontmatter: {skill_md}")
    raw = text[4:end]
    if yaml is not None:
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise Blocked(f"SKILL.md frontmatter must be a mapping: {skill_md}")
        name = data.get("name")
        description = data.get("description")
        if not isinstance(name, str) or not name.strip():
            raise Blocked(f"SKILL.md frontmatter missing name: {skill_md}")
        if not isinstance(description, str) or not description.strip():
            raise Blocked(f"SKILL.md frontmatter missing description: {skill_md}")
        return {"name": name.strip(), "description": " ".join(description.strip().split())}

    result: dict[str, str] = {}
    for key in ("name", "description"):
        match = re.search(rf"^{key}:\s*(.+)$", raw, flags=re.MULTILINE)
        if match:
            result[key] = match.group(1).strip().strip('"').strip("'")
    if not result.get("name"):
        raise Blocked(f"SKILL.md frontmatter missing name: {skill_md}")
    if not result.get("description"):
        raise Blocked(f"SKILL.md frontmatter missing description: {skill_md}")
    return result


def copy_skill(source_skill: Path, target_skill: Path, force: bool) -> None:
    if target_skill.exists():
        if not force:
            raise Blocked(f"target skill already exists: {target_skill}. Use --force to overwrite.")
        shutil.rmtree(target_skill)

    def ignore(_dir: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            path = Path(name)
            if name in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES:
                ignored.add(name)
        return ignored

    target_skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_skill, target_skill, ignore=ignore)


def load_lock(lock_file: Path) -> dict[str, Any]:
    if not lock_file.exists():
        return {"version": 1, "updated_at": "", "skills": {}}
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise Blocked(f"lock file must contain a JSON object: {lock_file}")
    if data.get("version") != 1:
        raise Blocked(f"unsupported lock version in {lock_file}: {data.get('version')}")
    skills = data.setdefault("skills", {})
    if not isinstance(skills, dict):
        raise Blocked(f"lock file skills must be an object: {lock_file}")
    return data


def write_lock(lock_file: Path, skill_id: str, entry: dict[str, Any]) -> None:
    data = load_lock(lock_file)
    data["updated_at"] = now_iso()
    data["skills"][skill_id] = entry
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_entry(
    args: argparse.Namespace,
    source_kind: str,
    commit: str,
    frontmatter: dict[str, str],
    source_tree_sha: str,
    installed_tree_sha: str,
    installed_files: list[dict[str, Any]],
    target_skill: Path,
) -> dict[str, Any]:
    skill_id = args.skill_id or frontmatter["name"]
    return {
        "id": skill_id,
        "name": frontmatter["name"],
        "description": frontmatter["description"],
        "adopted_at": now_iso(),
        "route": "official-adopt",
        "source": {
            "type": source_kind,
            "url": args.source,
            "skill_path": args.skill_path,
            "ref_requested": args.ref,
            "commit": commit,
        },
        "install": {
            "target_root": Path(args.target_root).as_posix(),
            "path": target_skill.as_posix(),
            "mode": "copy",
        },
        "hashes": {
            "source_tree_sha256": source_tree_sha,
            "installed_tree_sha256": installed_tree_sha,
        },
        "payload_roles": payload_role_counts(installed_files),
        "files": installed_files,
        "validation": {
            "suggested_commands": [
                f"python3 <kun-skill-toolkit>/skills/skill-modify/scripts/quick_validate.py {target_skill.as_posix()}",
                f"python3 <kun-skill-toolkit>/skills/skill-modify/scripts/audit_skill.py {target_skill.as_posix()}",
            ]
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adopt an upstream Agent Skill into a project and lock it.")
    parser.add_argument("--source", required=True, help="Git URL or local repo/path that contains the skill")
    parser.add_argument("--skill-path", required=True, help="path to the skill directory inside source")
    parser.add_argument("--skill-id", default="", help="installed skill id; defaults to SKILL.md frontmatter name")
    parser.add_argument("--ref", default="", help="optional Git tag, branch, or commit to checkout")
    parser.add_argument("--target-root", default=".agents/skills", help="directory that will contain installed skills")
    parser.add_argument("--lock-file", default="skills-lock.json", help="project lock file to update")
    parser.add_argument("--force", action="store_true", help="overwrite existing target skill directory")
    parser.add_argument("--dry-run", action="store_true", help="verify and print the planned adoption without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="skill-adopter-") as tmp:
            source_root, source_kind, commit = clone_or_resolve_source(args.source, args.ref, Path(tmp))
            source_skill = (source_root / args.skill_path).resolve()
            if not source_skill.is_dir():
                raise Blocked(f"source skill directory missing: {source_skill}")
            if not (source_skill / "SKILL.md").is_file():
                raise Blocked(f"source skill missing SKILL.md: {source_skill}")

            frontmatter = parse_skill_frontmatter(source_skill / "SKILL.md")
            skill_id = args.skill_id or frontmatter["name"]
            target_skill = (Path(args.target_root).expanduser().resolve() / skill_id).resolve()
            source_tree_sha, _source_files = tree_hash(source_skill)

            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "route": "official-adopt",
                            "source": args.source,
                            "source_kind": source_kind,
                            "commit": commit,
                            "skill_path": args.skill_path,
                            "skill_id": skill_id,
                            "target": target_skill.as_posix(),
                            "source_tree_sha256": source_tree_sha,
                            "payload_roles": payload_role_counts(_source_files),
                            "lock_file": Path(args.lock_file).resolve().as_posix(),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                return 0

            copy_skill(source_skill, target_skill, args.force)
            installed_tree_sha, installed_files = tree_hash(target_skill)
            if source_tree_sha != installed_tree_sha:
                raise Blocked("installed tree hash differs from source tree hash")

            entry = build_entry(
                args,
                source_kind,
                commit,
                frontmatter,
                source_tree_sha,
                installed_tree_sha,
                installed_files,
                target_skill,
            )
            lock_file = Path(args.lock_file).expanduser().resolve()
            write_lock(lock_file, skill_id, entry)

            print(f"route: official-adopt")
            print(f"source: {args.source}")
            print(f"source_kind: {source_kind}")
            if commit:
                print(f"commit: {commit}")
            print(f"skill_path: {args.skill_path}")
            print(f"installed: {target_skill}")
            print(f"lock_file: {lock_file}")
            print(f"tree_sha256: {installed_tree_sha}")
            print(f"files: {len(installed_files)}")
            print(f"payload_roles: {json.dumps(entry['payload_roles'], sort_keys=True)}")
            print(f"validate: {entry['validation']['suggested_commands'][0]}")
            print(f"audit: {entry['validation']['suggested_commands'][1]}")
            return 0
    except Blocked as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
