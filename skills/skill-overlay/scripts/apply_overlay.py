#!/usr/bin/env python3
"""Replay a pinned upstream Skill overlay into a project skill directory."""

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
from string import Template
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


IGNORED_NAMES = {".git", "__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}
REF_DIR = "references"
OFFICIAL_BASIS_REF = REF_DIR + "/official-basis.md"
RUNTIME_RULES_REF = REF_DIR + "/runtime-rules.md"
UPSTREAM_FRONTMATTER_REF = REF_DIR + "/upstream-frontmatter.yaml"
UPSTREAM_README_REF = REF_DIR + "/upstream-readme.md"


class Blocked(RuntimeError):
    """Raised when an overlay cannot be replayed safely."""


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
            run(["git", "clone", "--quiet", local_repo.as_posix(), repo.as_posix()])
            run(["git", "checkout", "--quiet", ref], cwd=repo)
            return repo, "local-git", run(["git", "rev-parse", "HEAD"], cwd=repo)
        commit = run(["git", "rev-parse", "HEAD"], cwd=local_repo) if (local_repo / ".git").exists() else ""
        return local_repo, "local", commit

    if not is_remote_source(source):
        raise Blocked(f"source is neither an existing path nor a Git URL: {source}")

    repo = temp_root / "source"
    run(["git", "clone", "--quiet", source, repo.as_posix()])
    if ref:
        run(["git", "checkout", "--quiet", ref], cwd=repo)
    return repo, "git", run(["git", "rev-parse", "HEAD"], cwd=repo)


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.suffix in IGNORED_SUFFIXES


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and not should_ignore(path.relative_to(root)):
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
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
        files.append({"path": rel, "sha256": file_hash, "bytes": path.stat().st_size})
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


def source_file_inventory(files: list[dict[str, Any]]) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {}
    lines: list[str] = []
    for item in files:
        path = str(item["path"])
        role = classify_source_file(path)
        counts[role] = counts.get(role, 0) + 1
        lines.append(f"- `{path}`: {role}, sha256 `{item['sha256']}`, bytes {item['bytes']}")
    return counts, lines


def read_frontmatter(skill_md: Path) -> tuple[dict[str, Any], str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise Blocked(f"SKILL.md missing YAML frontmatter: {skill_md}")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise Blocked(f"SKILL.md has invalid YAML frontmatter: {skill_md}")
    if yaml is None:
        raise Blocked("PyYAML is required")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise Blocked(f"SKILL.md frontmatter must be a mapping: {skill_md}")
    body = text[end + len("\n---\n") :]
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not name.strip():
        raise Blocked("upstream SKILL.md frontmatter missing name")
    if not isinstance(description, str) or not description.strip():
        raise Blocked("upstream SKILL.md frontmatter missing description")
    return data, body


def write_frontmatter(skill_md: Path, frontmatter: dict[str, Any], body: str) -> None:
    raw = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    skill_md.write_text(f"---\n{raw}\n---\n\n{body.lstrip()}", encoding="utf-8")


def insert_overlay_note(body: str, note: str) -> str:
    if "## Kun Overlay Basis" in body:
        return body
    if body.startswith("# "):
        first_newline = body.find("\n")
        if first_newline != -1:
            return body[: first_newline + 1] + "\n" + note.strip() + "\n\n" + body[first_newline + 1 :].lstrip()
    return note.strip() + "\n\n" + body.lstrip()


def render_template(text: str, values: dict[str, str]) -> str:
    return Template(text).safe_substitute(values)


def write_openai_yaml(target_skill: Path, skill_id: str, description: str, config: dict[str, Any]) -> None:
    data = {
        "interface": {
            "display_name": config.get("display_name") or skill_id.replace("-", " ").title(),
            "short_description": config.get("short_description") or description[:160],
            "default_prompt": config.get("default_prompt") or f"Use ${skill_id} when the task matches this Skill.",
        },
        "policy": {"allow_implicit_invocation": bool(config.get("allow_implicit_invocation", True))},
    }
    out = target_skill / "agents" / "openai.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_official_basis(
    target_skill: Path,
    manifest_label: str,
    source: dict[str, str],
    commit: str,
    source_tree_sha: str,
    source_files: list[dict[str, Any]],
    original_frontmatter: dict[str, Any],
    operations: list[str],
) -> None:
    references = target_skill / REF_DIR
    references.mkdir(parents=True, exist_ok=True)
    (references / "upstream-frontmatter.yaml").write_text(
        yaml.safe_dump(original_frontmatter, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    operation_lines = "\n".join(f"- {item}" for item in operations)
    frontmatter_yaml = yaml.safe_dump(original_frontmatter, allow_unicode=True, sort_keys=False).strip()
    payload_counts, payload_lines = source_file_inventory(source_files)
    payload_count_lines = "\n".join(f"- {role}: {count}" for role, count in sorted(payload_counts.items()))
    payload_inventory = "\n".join(payload_lines)
    body = f"""# Official Overlay Basis

This Skill was generated through `official-overlay`.

## Upstream

- Source: {source.get("url", "")}
- Ref requested: {source.get("ref", "")}
- Commit: {commit}
- Skill path: {source.get("skill_path", "")}
- Source tree SHA-256: {source_tree_sha}
- Overlay manifest: {manifest_label}

## Upstream Source Tree Payload

The upstream Skill is a source tree, not only Markdown. Payload roles:

{payload_count_lines}

Operational scripts or runtime assets must be projected into local `scripts/`
or `assets/` before use. Files kept only under `references/upstream/` are
evidence for audit, provenance, license, and update review unless
`runtime-rules.md` explicitly says otherwise.

## Upstream Source Tree Inventory

{payload_inventory}

## Applied Operations

{operation_lines}

## Original Frontmatter

```yaml
{frontmatter_yaml}
```
"""
    (references / "official-basis.md").write_text(body, encoding="utf-8")


def collect_upstream_mirror_refs(target_skill: Path) -> list[str]:
    upstream_dir = target_skill / REF_DIR / "upstream"
    if not upstream_dir.exists():
        return []
    refs: list[str] = []
    for path in iter_files(upstream_dir):
        refs.append(path.relative_to(target_skill).as_posix())
    return refs


def write_runtime_rules(
    target_skill: Path,
    source: dict[str, str],
    commit: str,
    source_tree_sha: str,
    contract: dict[str, Any],
) -> None:
    references = target_skill / REF_DIR
    references.mkdir(parents=True, exist_ok=True)

    upstream_refs = collect_upstream_mirror_refs(target_skill)
    upstream_lines = "\n".join(f"- `{ref}` ({classify_source_file(ref)})" for ref in upstream_refs) or "- none"
    triggers = contract.get("full_read_triggers") or [
        "ambiguity",
        "exact_upstream_behavior",
        "upstream_update_review",
        "license_or_provenance",
        "user_requests_source",
    ]
    trigger_lines = "\n".join(f"- {item}" for item in triggers)
    ordinary_runtime = contract.get("ordinary_runtime") or "digest-plus-scoped-upstream"
    maintenance_runtime = contract.get("maintenance_runtime") or "full-upstream-mirror"

    body = f"""# Runtime Rules

This file is the ordinary-runtime extraction for an `official-overlay` Skill.
It is not a replacement for the pinned upstream source mirror.

## Source Policy

- ordinary_runtime: {ordinary_runtime}
- maintenance_runtime: {maintenance_runtime}
- official_basis: `{OFFICIAL_BASIS_REF}`
- upstream_frontmatter: `{UPSTREAM_FRONTMATTER_REF}`
- upstream_source: {source.get("url", "")}
- upstream_ref_requested: {source.get("ref", "")}
- upstream_commit: {commit}
- upstream_skill_path: {source.get("skill_path", "")}
- upstream_tree_sha256: {source_tree_sha}

## Ordinary Runtime

Before executing the Skill, read `{OFFICIAL_BASIS_REF}` and this file. Use this
file as the executable ordinary-runtime rule layer. Treat upstream rules as
inherited defaults only where this file or `{OFFICIAL_BASIS_REF}` marks them
adopted.

## Full-Read Triggers

Read the scoped upstream file(s) under `references/upstream/` before deciding
when the task crosses any of these boundaries:

{trigger_lines}
- conflict between this file, `{OFFICIAL_BASIS_REF}`, and local Skill rules
- model uncertainty about which upstream rule applies

If a full-read trigger is active and the needed upstream file cannot be found,
return `blocked` or `needs-user` instead of guessing.

## Source Map

Use `{OFFICIAL_BASIS_REF}` for source identity, trust, adoption status, and
overlay boundaries. Use the upstream mirror files below as the full proof source
for maintenance, adoption, audit, update review, license/provenance, exact
upstream behavior, and unresolved ambiguity:

{upstream_lines}

## Script And Asset Payloads

Upstream scripts, assets, templates, fixtures, or binary payloads under
`references/upstream/` are evidence-only unless the overlay projects them into
local `scripts/` or `assets/` and records matching lock/hash evidence. Do not
execute code or depend on media directly from `references/upstream/`.

If an upstream script or asset is necessary for the Skill's behavior and no
local projection exists, return `blocked_until_projected` instead of claiming
the official capability is fully adopted.

## Overlay Boundary

Apply Kun overlay rules only where this Skill explicitly narrows upstream
behavior. Do not rewrite, summarize away, or silently override upstream rules
inside `references/upstream/`.
"""
    (references / "runtime-rules.md").write_text(body, encoding="utf-8")


def move_files(target_skill: Path, moves: list[dict[str, str]], operations: list[str]) -> None:
    for item in moves:
        src_rel = item.get("from")
        dst_rel = item.get("to")
        if not src_rel or not dst_rel:
            raise Blocked(f"move_files entries require from/to: {item}")
        src = target_skill / src_rel
        dst = target_skill / dst_rel
        if not src.exists():
            operations.append(f"skip missing move source {src_rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            raise Blocked(f"move target already exists: {dst_rel}")
        shutil.move(src.as_posix(), dst.as_posix())
        operations.append(f"moved {src_rel} to {dst_rel}")


def apply_replacements(text: str, replacements: list[dict[str, str]], operations: list[str]) -> str:
    for item in replacements:
        old = item.get("from")
        new = item.get("to")
        if old is None or new is None:
            raise Blocked(f"replacement entries require from/to: {item}")
        if old not in text:
            operations.append(f"skip missing SKILL.md replacement source {old!r}")
            continue
        text = text.replace(old, new)
        operations.append(f"replaced SKILL.md text {old!r}")
    return text


def load_lock(lock_file: Path) -> dict[str, Any]:
    if not lock_file.exists():
        return {"version": 1, "updated_at": "", "skills": {}}
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise Blocked(f"unsupported lock file: {lock_file}")
    data.setdefault("skills", {})
    return data


def write_lock(lock_file: Path, skill_id: str, entry: dict[str, Any]) -> None:
    data = load_lock(lock_file)
    data["updated_at"] = now_iso()
    data["skills"][skill_id] = entry
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay an official-overlay manifest.")
    parser.add_argument("manifest", type=Path, help="overlay manifest YAML")
    parser.add_argument("--manifest-label", default="", help="stable manifest label to write into official-basis.md")
    parser.add_argument("--target-root", default="", help="override target root")
    parser.add_argument("--lock-file", default="skills-lock.json", help="lock file to update")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated skill")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if yaml is None:
            raise Blocked("PyYAML is required")
        manifest_label = args.manifest.as_posix()
        manifest_path = args.manifest.expanduser().resolve()
        if args.manifest_label:
            manifest_label = args.manifest_label
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("version") != 1:
            raise Blocked("overlay manifest must be a YAML object with version: 1")
        if manifest.get("route") != "official-overlay":
            raise Blocked("overlay manifest route must be official-overlay")

        source = manifest.get("source") or {}
        overlay_source = manifest.get("overlay_source") or {}
        target = manifest.get("target") or {}
        overlay = manifest.get("overlay") or {}
        runtime_source_contract = overlay.get("runtime_source_contract") or {}
        if not isinstance(source, dict) or not isinstance(target, dict) or not isinstance(overlay, dict):
            raise Blocked("source, target, and overlay must be mappings")
        if runtime_source_contract and not isinstance(runtime_source_contract, dict):
            raise Blocked("overlay.runtime_source_contract must be a mapping when provided")
        if overlay_source and not isinstance(overlay_source, dict):
            raise Blocked("overlay_source must be a mapping when provided")
        for key in ("url", "ref", "skill_path"):
            if not source.get(key):
                raise Blocked(f"source.{key} is required")
        if overlay_source:
            for key in ("url", "skill_path"):
                if not overlay_source.get(key):
                    raise Blocked(f"overlay_source.{key} is required")

        with tempfile.TemporaryDirectory(prefix="skill-overlay-") as tmp:
            source_root, source_kind, commit = clone_or_resolve_source(source["url"], source["ref"], Path(tmp))
            source_skill = (source_root / source["skill_path"]).resolve()
            if not (source_skill / "SKILL.md").is_file():
                raise Blocked(f"source skill missing SKILL.md: {source_skill}")
            source_tree_sha, _source_files = tree_hash(source_skill)
            original_frontmatter, body = read_frontmatter(source_skill / "SKILL.md")

            skill_id = target.get("skill_id") or original_frontmatter["name"]
            if not re.match(r"^[a-z0-9-]+$", skill_id):
                raise Blocked(f"target.skill_id must be kebab-case: {skill_id}")
            target_root = Path(args.target_root or target.get("target_root") or ".agents/skills").expanduser().resolve()
            target_skill = target_root / skill_id
            if target_skill.exists():
                if not args.force:
                    raise Blocked(f"target skill already exists: {target_skill}. Use --force to overwrite.")
                shutil.rmtree(target_skill)
            target_skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_skill, target_skill, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store"))

            operations: list[str] = []
            overlay_source_entry: dict[str, Any] | None = None
            if overlay_source:
                overlay_ref = str(overlay_source.get("ref") or "")
                overlay_temp_root = Path(tmp) / "overlay"
                overlay_temp_root.mkdir(parents=True, exist_ok=True)
                overlay_root, overlay_kind, overlay_commit = clone_or_resolve_source(
                    str(overlay_source["url"]),
                    overlay_ref,
                    overlay_temp_root,
                )
                overlay_skill = (overlay_root / str(overlay_source["skill_path"])).resolve()
                if not (overlay_skill / "SKILL.md").is_file():
                    raise Blocked(f"overlay source skill missing SKILL.md: {overlay_skill}")
                overlay_tree_sha, _overlay_files = tree_hash(overlay_skill)
                overlay_source_entry = {
                    "type": overlay_kind,
                    "url": str(overlay_source["url"]),
                    "ref_requested": overlay_ref,
                    "commit": overlay_commit,
                    "skill_path": str(overlay_source["skill_path"]),
                    "tree_sha256": overlay_tree_sha,
                }
                if overlay.get("replace_with_overlay_source_tree"):
                    shutil.rmtree(target_skill)
                    shutil.copytree(
                        overlay_skill,
                        target_skill,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store"),
                    )
                    operations.append(
                        "replaced generated upstream copy with overlay_source skill tree "
                        f"{overlay_source_entry['skill_path']}"
                    )
                    overlay_frontmatter, body = read_frontmatter(target_skill / "SKILL.md")
                    if not overlay.get("description"):
                        original_frontmatter = overlay_frontmatter

            description = str(overlay.get("description") or original_frontmatter["description"]).strip()
            preserve_skill_markdown = bool(
                overlay_source
                and overlay.get("replace_with_overlay_source_tree")
                and overlay.get("preserve_overlay_source_skill_markdown")
                and not overlay.get("description")
                and not overlay.get("inject_skill_note", True)
                and not overlay.get("skill_markdown_replacements")
                and not overlay.get("append_skill_markdown")
                and not overlay.get("normalize_frontmatter", True)
            )

            if overlay.get("normalize_frontmatter", True):
                new_frontmatter = {"name": skill_id, "description": description}
                operations.append("normalized SKILL.md frontmatter to name and description")
                if description != str(original_frontmatter["description"]).strip():
                    operations.append("overrode SKILL.md description from overlay manifest")
            else:
                new_frontmatter = dict(original_frontmatter)

            if overlay.get("inject_skill_note", True):
                moved_readme = any((item or {}).get("to") == UPSTREAM_README_REF for item in (overlay.get("move_files") or []))
                readme_sentence = f" If the upstream README context is needed, read `{UPSTREAM_README_REF}`." if moved_readme else ""
                note = f"""## Kun Overlay Basis

This is an upstream Skill with a Kun compatibility overlay. For ordinary runtime, read `{OFFICIAL_BASIS_REF}` and `{RUNTIME_RULES_REF}` before executing this Skill. Before changing, auditing, adopting, updating, resolving exact upstream behavior, checking license/provenance, or handling unresolved ambiguity, read the scoped full upstream source files under `references/upstream/` before deciding.{readme_sentence}

Treat upstream rules as inherited defaults; apply Kun overlay rules only where this Skill explicitly narrows them.
"""
                body = insert_overlay_note(body, note)
                operations.append("inserted Kun overlay basis note into SKILL.md")

            body = apply_replacements(body, overlay.get("skill_markdown_replacements") or [], operations)

            if overlay.get("append_skill_markdown"):
                values = {
                    "skill_id": skill_id,
                    "source_url": str(source.get("url", "")),
                    "source_ref": str(source.get("ref", "")),
                    "source_skill_path": str(source.get("skill_path", "")),
                    "commit": commit,
                    "source_tree_sha256": source_tree_sha,
                    "official_basis_ref": OFFICIAL_BASIS_REF,
                    "upstream_frontmatter_ref": UPSTREAM_FRONTMATTER_REF,
                }
                body = body.rstrip() + "\n\n" + render_template(str(overlay["append_skill_markdown"]).strip(), values) + "\n"
                operations.append("appended overlay markdown to SKILL.md")

            if preserve_skill_markdown:
                operations.append("preserved overlay_source SKILL.md without frontmatter rewrite")
            else:
                write_frontmatter(target_skill / "SKILL.md", new_frontmatter, body)

            move_files(target_skill, overlay.get("move_files") or [], operations)

            if "openai_yaml" in overlay:
                write_openai_yaml(target_skill, skill_id, description, overlay.get("openai_yaml") or {})
                operations.append("wrote agents/openai.yaml")

            if overlay.get("official_basis", True):
                operations.append(f"wrote {OFFICIAL_BASIS_REF} and {UPSTREAM_FRONTMATTER_REF}")
                write_official_basis(
                    target_skill=target_skill,
                    manifest_label=manifest_label,
                    source={k: str(v) for k, v in source.items()},
                    commit=commit,
                    source_tree_sha=source_tree_sha,
                    source_files=_source_files,
                    original_frontmatter=original_frontmatter,
                    operations=operations,
                )
                write_runtime_rules(
                    target_skill=target_skill,
                    source={k: str(v) for k, v in source.items()},
                    commit=commit,
                    source_tree_sha=source_tree_sha,
                    contract=runtime_source_contract,
                )
                operations.append(f"wrote {RUNTIME_RULES_REF}")

            installed_tree_sha, installed_files = tree_hash(target_skill)
            entry = {
                "id": skill_id,
                "name": skill_id,
                "description": description,
                "generated_at": now_iso(),
                "route": "official-overlay",
                "source": {
                    "type": source_kind,
                    "url": source["url"],
                    "ref_requested": source["ref"],
                    "commit": commit,
                    "skill_path": source["skill_path"],
                },
                "overlay_source": overlay_source_entry,
                "overlay": {
                    "manifest": manifest_label,
                    "operations": operations,
                    "runtime_source_contract": runtime_source_contract
                    or {
                        "ordinary_runtime": "digest-plus-scoped-upstream",
                        "runtime_rules": RUNTIME_RULES_REF,
                        "maintenance_runtime": "full-upstream-mirror",
                    },
                },
                "install": {
                    "target_root": target_root.as_posix(),
                    "path": target_skill.as_posix(),
                    "mode": "copy-plus-overlay",
                },
                "hashes": {
                    "source_tree_sha256": source_tree_sha,
                    "installed_tree_sha256": installed_tree_sha,
                },
                "files": installed_files,
                "validation": {
                    "suggested_commands": [
                        f"python3 <kun-skill-toolkit>/skills/skill-modify/scripts/quick_validate.py {target_skill.as_posix()}",
                        f"python3 <kun-skill-toolkit>/skills/skill-modify/scripts/audit_skill.py {target_skill.as_posix()}",
                    ]
                },
            }
            write_lock(Path(args.lock_file).expanduser().resolve(), skill_id, entry)

            print("route: official-overlay")
            print(f"source: {source['url']}")
            print(f"commit: {commit}")
            print(f"skill_path: {source['skill_path']}")
            print(f"installed: {target_skill}")
            print(f"lock_file: {Path(args.lock_file).expanduser().resolve()}")
            print(f"source_tree_sha256: {source_tree_sha}")
            print(f"installed_tree_sha256: {installed_tree_sha}")
            print(f"files: {len(installed_files)}")
            for operation in operations:
                print(f"operation: {operation}")
            return 0
    except Blocked as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
