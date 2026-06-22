#!/usr/bin/env python3
"""Convert a source card candidate into a Kun registry draft."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


class Blocked(RuntimeError):
    """Raised when a registry draft cannot be produced."""


VALID_ROUTES = {
    "official-adopt",
    "official-overlay",
    "kun-modify",
    "kun-create",
    "blocked",
    "needs-review",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "skill-candidate"


def split_markdown_row(line: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [part.strip().replace("\\|", "|") for part in line.strip("|").split("|")]


def parse_source_card(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    meta_match = re.search(r"```text\n(.*?)\n```", text, flags=re.DOTALL)
    if meta_match:
        for line in meta_match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip().lower().replace(" ", "_")] = value.strip()

    candidates: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("| Rank | Source | Skill |"):
            in_table = True
            headers = [slugify(item).replace("-", "_") for item in split_markdown_row(line)]
            continue
        if in_table and line.strip().startswith("|---"):
            continue
        if in_table:
            cells = split_markdown_row(line.strip())
            if not cells or len(cells) != len(headers):
                if candidates:
                    break
                continue
            item = dict(zip(headers, cells))
            if item.get("rank") and item.get("rank") != "-":
                candidates.append(item)

    if not candidates:
        raise Blocked(f"no candidates found in source card: {path}")
    return meta, candidates


def github_url(source: str) -> str:
    if source.startswith("https://github.com/"):
        return source
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source):
        return f"https://github.com/{source}"
    return source


def source_repo(source: str) -> str:
    if source.startswith("https://github.com/"):
        parts = source.removeprefix("https://github.com/").strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    return source


def default_skill_id(source: str, skill: str) -> str:
    repo = source_repo(source).split("/", 1)
    owner = repo[0] if repo else "upstream"
    raw = f"{owner}-{skill}" if skill else "-".join(repo)
    return slugify(raw)


def source_kind(source: str) -> str:
    if source.startswith("https://github.com/") or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source):
        return "github"
    if source.startswith("http://") or source.startswith("https://"):
        return "web"
    return "unknown"


def normalized_route(candidate: dict[str, str]) -> str:
    route = candidate.get("suggested_route", "").strip()
    return route if route in VALID_ROUTES else "needs-review"


def build_draft(
    source_card: Path,
    meta: dict[str, str],
    candidate: dict[str, str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source = candidate.get("source", "")
    skill = candidate.get("skill", "")
    route = normalized_route(candidate)
    skill_id = args.skill_id or default_skill_id(source, skill)
    repo_url = github_url(source)
    skill_path = args.skill_path or "<fill-after-skill-md-inspection>"
    target_root = args.target_root
    install_path = f"{target_root.rstrip('/')}/{skill_id}"

    adopt_cmd = [
        "python3",
        "<kun-skill-toolkit>/skills/skill-adopter/scripts/adopt_skill.py",
        "--source",
        repo_url,
        "--skill-path",
        skill_path,
        "--target-root",
        target_root,
        "--lock-file",
        "skills-lock.json",
    ]
    if args.ref:
        adopt_cmd.extend(["--ref", args.ref])
    if args.skill_id:
        adopt_cmd.extend(["--skill-id", args.skill_id])

    status = "candidate_needs_skill_md_review"
    if args.skill_path and args.ref:
        status = "candidate_ready_for_adopt_smoke"

    return {
        "version": 1,
        "generated_at": now_iso(),
        "source_card": source_card.as_posix(),
        "query": meta.get("query", ""),
        "lifecycle_task": meta.get("lifecycle_task", ""),
        "legacy_asset": meta.get("legacy_asset", ""),
        "decision": route,
        "candidate": {
            "rank": candidate.get("rank", ""),
            "source": source,
            "skill": skill,
            "source_tier": candidate.get("source_tier", candidate.get("trust", "")),
            "coverage": candidate.get("coverage", ""),
            "health": candidate.get("health", ""),
            "evidence": candidate.get("evidence", ""),
            "suggested_route": candidate.get("suggested_route", ""),
        },
        "registry_entry": {
            "id": skill_id,
            "type": "adopted_skill_candidate",
            "route": route,
            "status": status,
            "invocation_policy": {
                "atomic_skill": "on_demand",
                "installability": "single-skill",
                "group_callable": False,
                "facade": "blocked_unless_runtime_or_user_requested",
            },
            "source": {
                "kind": source_kind(source),
                "repo": source_repo(source),
                "url": repo_url,
                "skill_name": skill,
                "skill_path": skill_path,
                "ref": args.ref or "<fill-tag-or-commit-sha>",
            },
            "install": {
                "codex": install_path,
                "claude_code": f".claude/skills/{skill_id}",
            },
            "lock_required": {
                "commit": True,
                "tree_sha256": True,
                "files_sha256": True,
                "skills_lock_json": True,
            },
            "verification_required": [
                "read candidate SKILL.md",
                "inspect scripts/references/assets",
                "check license or reuse boundary",
                "check GitHub health: stars, forks, open issues, license, archived/disabled state, default branch, latest push, latest update, canonical repo redirect",
                "run quick_validate.py",
                "run audit_skill.py",
            ],
            "adoption_command": " ".join(adopt_cmd),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a source card candidate into a registry draft.")
    parser.add_argument("source_card", help="path to research/source-cards/*.md")
    parser.add_argument("--rank", type=int, default=1, help="candidate rank to convert")
    parser.add_argument("--output", default="", help="draft output path")
    parser.add_argument("--draft-dir", default="registry-drafts", help="output directory when --output is omitted")
    parser.add_argument("--skill-id", default="", help="override registry skill id")
    parser.add_argument("--skill-path", default="", help="confirmed path to the upstream skill directory")
    parser.add_argument("--ref", default="", help="confirmed upstream tag or commit SHA")
    parser.add_argument("--target-root", default=".agents/skills")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if yaml is None:
            raise Blocked("PyYAML is required to write registry draft YAML")
        source_card = Path(args.source_card).expanduser().resolve()
        meta, candidates = parse_source_card(source_card)
        index = args.rank - 1
        if index < 0 or index >= len(candidates):
            raise Blocked(f"candidate rank out of range: {args.rank}; found {len(candidates)} candidates")
        draft = build_draft(source_card, meta, candidates[index], args)
        skill_id = draft["registry_entry"]["id"]
        output = Path(args.output) if args.output else Path(args.draft_dir) / f"{skill_id}.yaml"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"registry_draft: {output.resolve()}")
        print(f"skill_id: {skill_id}")
        print(f"status: {draft['registry_entry']['status']}")
        print(f"adoption_command: {draft['registry_entry']['adoption_command']}")
        return 0
    except Blocked as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
