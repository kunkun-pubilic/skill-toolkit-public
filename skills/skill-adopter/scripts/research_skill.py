#!/usr/bin/env python3
"""Research upstream Agent Skill candidates and write a source card."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
SKILLS_FIND_RE = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(.+?)\s+([0-9.]+[KkM]?|\d+)\s+installs$")
URL_RE = re.compile(r"^(https://skills\.sh/\S+)$")
GITHUB_SEARCH_FIELDS = (
    "fullName,url,stargazersCount,watchersCount,forksCount,openIssuesCount,"
    "license,isArchived,isDisabled,isFork,isPrivate,updatedAt,pushedAt,createdAt,"
    "description,defaultBranch,visibility"
)
SKILL_COMMUNITY_SITES = (
    "skills.sh",
    "claudskills.com",
    "claudemarketplaces.com",
    "awesomeskill.ai",
    "mcpmarket.com/tools/skills",
    "lobehub.com/skills",
)
FRESHNESS_DAYS = 30


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "skill-research"


def run_command(cmd: list[str], timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except FileNotFoundError:
        return {"cmd": cmd, "returncode": 127, "stdout": "", "stderr": f"command not found: {cmd[0]}", "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def parse_skills_find(output: str, limit: int) -> list[dict[str, str]]:
    lines = [line.strip() for line in strip_ansi(output).splitlines() if line.strip()]
    candidates: list[dict[str, str]] = []
    pending: dict[str, str] | None = None
    for line in lines:
        match = SKILLS_FIND_RE.match(line)
        if match:
            repo, skill, installs = match.groups()
            pending = {
                "repo": repo,
                "skill": skill,
                "installs": installs,
                "skills_sh_url": "",
                "install_command": f"npx skills add {repo}@{skill}",
            }
            candidates.append(pending)
            if len(candidates) >= limit:
                pending = None
            continue
        if pending and line.startswith("└ "):
            url = line[2:].strip()
            if URL_RE.match(url):
                pending["skills_sh_url"] = url
        if len(candidates) >= limit:
            break
    return candidates[:limit]


def parse_github_search(output: str, limit: int) -> list[dict[str, Any]]:
    if not output.strip():
        return []
    data = json.loads(output)
    if not isinstance(data, list):
        return []
    candidates: list[dict[str, Any]] = []
    for item in data[:limit]:
        health = repo_health_from_search_item(item)
        candidates.append(
            {
                "full_name": item.get("fullName", ""),
                "url": item.get("url", ""),
                "repo_health": health,
                "description": item.get("description", ""),
            }
        )
    return candidates


def parse_doko_search(output: str, limit: int) -> list[str]:
    lines = [line.strip() for line in strip_ansi(output).splitlines() if line.strip()]
    return lines[:limit]


def parse_number(value: Any) -> int:
    if isinstance(value, int):
        return value
    text = str(value or "").strip().lower()
    if not text:
        return 0
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1_000
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1_000_000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def github_repo_name(source: str) -> str:
    if source.startswith("https://github.com/"):
        parts = source.removeprefix("https://github.com/").strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    return source


def iso_days_ago(value: str) -> int | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - parsed).days


def license_key(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, dict):
        return str(value.get("spdxId") or value.get("spdx_id") or value.get("key") or "").strip()
    return str(value).strip()


def has_reuse_license(health: dict[str, Any]) -> bool:
    value = str(health.get("license") or "").strip().lower()
    return bool(value and value not in {"other", "noassertion", "none", "null"})


def repo_health_from_search_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": item.get("fullName", ""),
        "url": item.get("url", ""),
        "stars": item.get("stargazersCount", 0),
        "watchers": item.get("watchersCount", 0),
        "forks": item.get("forksCount", 0),
        "open_issues": item.get("openIssuesCount", 0),
        "license": license_key(item.get("license")),
        "archived": bool(item.get("isArchived", False)),
        "disabled": bool(item.get("isDisabled", False)),
        "fork": bool(item.get("isFork", False)),
        "private": bool(item.get("isPrivate", False)),
        "pushed_at": item.get("pushedAt", ""),
        "updated_at": item.get("updatedAt", ""),
        "created_at": item.get("createdAt", ""),
        "default_branch": item.get("defaultBranch", ""),
        "visibility": item.get("visibility", ""),
    }


def repo_health_from_api_output(output: str) -> dict[str, Any]:
    if not output.strip():
        return {}
    item = json.loads(output)
    return {
        "full_name": item.get("full_name", ""),
        "url": item.get("html_url", ""),
        "stars": item.get("stargazers_count", 0),
        "watchers": item.get("subscribers_count", 0),
        "forks": item.get("forks_count", 0),
        "open_issues": item.get("open_issues_count", 0),
        "license": license_key(item.get("license")),
        "archived": bool(item.get("archived", False)),
        "disabled": bool(item.get("disabled", False)),
        "fork": bool(item.get("fork", False)),
        "private": bool(item.get("private", False)),
        "pushed_at": item.get("pushed_at", ""),
        "updated_at": item.get("updated_at", ""),
        "created_at": item.get("created_at", ""),
        "default_branch": item.get("default_branch", ""),
        "visibility": item.get("visibility", ""),
    }


def fetch_repo_health(repo: str, timeout: int) -> tuple[dict[str, Any], dict[str, Any]]:
    result = run_command(["gh", "api", f"repos/{repo}"], timeout)
    if result["returncode"] != 0:
        return {}, result
    try:
        return repo_health_from_api_output(result["stdout"]), result
    except (json.JSONDecodeError, TypeError):
        return {}, result


def merge_repo_health(candidate: dict[str, Any], health: dict[str, Any]) -> None:
    if not health:
        return
    candidate["repo_health"] = health
    if health.get("full_name"):
        candidate["canonical_repo"] = health["full_name"]
    if health.get("url"):
        candidate["canonical_url"] = health["url"]


def maintenance_label(health: dict[str, Any]) -> str:
    if not health:
        return "unknown"
    if health.get("archived") or health.get("disabled"):
        return "archived-or-disabled"
    pushed_days = iso_days_ago(str(health.get("pushed_at", "")))
    if pushed_days is None:
        return "unknown"
    if pushed_days <= 30:
        return "active-30d"
    if pushed_days <= 90:
        return "warm-90d"
    if pushed_days <= 180:
        return "stale-180d"
    return "dormant-180d-plus"


def format_repo_health(health: dict[str, Any]) -> str:
    if not health:
        return "repo health unavailable"
    pushed_days = iso_days_ago(str(health.get("pushed_at", "")))
    pushed = f"{pushed_days}d since push" if pushed_days is not None else "push unknown"
    license_text = health.get("license") or "no-license"
    flags = []
    if health.get("archived"):
        flags.append("archived")
    if health.get("disabled"):
        flags.append("disabled")
    if health.get("fork"):
        flags.append("fork")
    flag_text = f"; {','.join(flags)}" if flags else ""
    return (
        f"{maintenance_label(health)}; {health.get('stars', 0)} stars; "
        f"{health.get('forks', 0)} forks; {health.get('open_issues', 0)} open issues; "
        f"{license_text}; {pushed}{flag_text}"
    )


def build_doko_sources(query: str) -> list[tuple[str, str]]:
    skill_query = f"{query} Agent Skill SKILL.md"
    recent_date = (datetime.now(timezone.utc) - timedelta(days=FRESHNESS_DAYS)).date().isoformat()
    community_query = " OR ".join(f"site:{site}" for site in SKILL_COMMUNITY_SITES)
    return [
        (
            "general-web",
            f"https://www.google.com/search?q={quote_plus(skill_query)}",
        ),
        (
            "recent-web-30d",
            f"https://www.google.com/search?q={quote_plus(skill_query + ' after:' + recent_date)}",
        ),
        (
            "x-twitter",
            f"https://x.com/search?q={quote_plus(skill_query)}&src=typed_query&f=live",
        ),
        (
            "reddit",
            f"https://www.reddit.com/search/?q={quote_plus(skill_query)}&type=link&sort=relevance",
        ),
        (
            "hacker-news",
            f"https://hn.algolia.com/?q={quote_plus(skill_query)}",
        ),
        (
            "youtube",
            f"https://www.google.com/search?q={quote_plus('site:youtube.com ' + skill_query)}",
        ),
        (
            "github-discussion",
            f"https://www.google.com/search?q={quote_plus('site:github.com ' + skill_query + ' issues OR discussions OR pull')}",
        ),
        (
            "ai-skill-communities",
            f"https://www.google.com/search?q={quote_plus('(' + community_query + ') ' + query + ' Claude Code Skill Agent Skill')}",
        ),
    ]


def build_github_query(query: str) -> str:
    lowered = query.lower()
    parts = [query]
    if "agent skill" not in lowered and "agent skills" not in lowered:
        parts.append("agent skills")
    if "skill.md" not in lowered:
        parts.append("SKILL.md")
    return " ".join(parts)


def source_tier_label(repo: str, health: dict[str, Any] | None = None, installs: Any = 0) -> str:
    owner = repo.split("/", 1)[0].lower()
    if owner in {
        "openai",
        "anthropics",
        "vercel-labs",
        "microsoft",
        "microsoftdocs",
        "google",
        "google-labs-code",
        "elastic",
        "greensock",
        "callstackincubator",
    }:
        return "tier0-official"
    if health and not health.get("archived") and not health.get("disabled"):
        pushed_days = iso_days_ago(str(health.get("pushed_at", "")))
        has_adoption = parse_number(installs) >= 100 or int(health.get("stars") or 0) >= 50 or int(health.get("forks") or 0) >= 5
        if pushed_days is not None and pushed_days <= 90 and has_reuse_license(health) and has_adoption:
            return "tier1-mature"
    return "tier2-community"


def route_hint(candidate: dict[str, Any]) -> str:
    health = candidate.get("repo_health") or {}
    if health.get("archived") or health.get("disabled"):
        return "blocked"
    tier = source_tier_label(candidate["repo"], health, candidate.get("installs", 0))
    if tier == "tier0-official":
        return "official-adopt"
    if tier == "tier1-mature":
        return "needs-skill-md-review"
    return "needs-review"


def markdown_table_row(values: list[Any]) -> str:
    escaped = []
    for value in values:
        text = str(value).replace("|", "\\|").replace("\n", " ")
        escaped.append(text)
    return "| " + " | ".join(escaped) + " |"


def write_source_card(
    output: Path,
    query: str,
    lifecycle_task: str,
    legacy_asset: str,
    skills_candidates: list[dict[str, str]],
    github_candidates: list[dict[str, Any]],
    doko_results: list[str],
    commands: list[dict[str, Any]],
) -> None:
    lines = [
        "# Skill Upstream Source Card",
        "",
        "```text",
        "Decision: needs-review",
        "Reason: Research collected candidates; read candidate SKILL.md before adoption.",
        f"Query: {query}",
        f"Lifecycle task: {lifecycle_task}",
        f"Legacy asset: {legacy_asset or 'none'}",
        f"Generated at: {now_iso()}",
        "```",
        "",
        "## Need Decomposition",
        "",
        "| Need | Legacy Evidence | Search Query | Must Have | Nice To Have |",
        "|---|---|---|---|---|",
        markdown_table_row(
            [
                query,
                legacy_asset or "none",
                query,
                "candidate SKILL.md can satisfy the real capability",
                "official or mature maintained source",
            ]
        ),
        "",
        "## Candidate Summary",
        "",
        "| Rank | Source | Skill | Source Tier | Coverage | Health | Evidence | Suggested Route |",
        "|---|---|---|---|---|---|---|---|",
    ]

    rank = 1
    for candidate in skills_candidates:
        health = candidate.get("repo_health") or {}
        source = candidate.get("canonical_repo") or candidate["repo"]
        evidence = f"{candidate.get('installs', '')} installs"
        if candidate.get("skills_sh_url"):
            evidence += f"; {candidate['skills_sh_url']}"
        if candidate.get("canonical_repo") and candidate.get("canonical_repo") != candidate["repo"]:
            evidence += f"; canonical {candidate['canonical_repo']}"
        lines.append(
            markdown_table_row(
                [
                    rank,
                    source,
                    candidate["skill"],
                    source_tier_label(source, health, candidate.get("installs", 0)),
                    "needs-skill-md-review",
                    format_repo_health(health),
                    evidence,
                    route_hint(candidate),
                ]
            )
        )
        rank += 1

    for candidate in github_candidates:
        health = candidate.get("repo_health") or {}
        source = candidate.get("canonical_url") or candidate.get("url", "")
        lines.append(
            markdown_table_row(
                [
                    rank,
                    source,
                    "",
                    source_tier_label(candidate.get("canonical_repo") or candidate.get("full_name", ""), health),
                    "needs-skill-md-review",
                    format_repo_health(health),
                    candidate.get("description", ""),
                    "needs-review",
                ]
            )
        )
        rank += 1

    if rank == 1:
        lines.append(markdown_table_row(["-", "none", "", "unknown", "gap", "unknown", "No candidates found by enabled tools.", "kun-create?"]))

    lines.extend(
        [
            "",
            "## DOKO Results",
            "",
        ]
    )
    if doko_results:
        lines.extend(f"- {line}" for line in doko_results)
    else:
        doko_command = next((item for item in commands if item["cmd"] and item["cmd"][0] == "dokobot"), None)
        if doko_command:
            status = "timeout" if doko_command.get("timed_out") else doko_command.get("returncode")
            detail = strip_ansi((doko_command.get("stderr") or doko_command.get("stdout") or "").strip()).splitlines()
            message = detail[0] if detail else "no output"
            lines.append(f"- DOKO read ran but did not return results. status={status}; {message}")
        else:
            lines.append("- Not run. Use `--use-doko` to run DOKO local research through `dokobot read --local <search-url>`.")

    lines.extend(
        [
            "",
            "## Chain Contract",
            "",
            "Use `chain_id: standalone` when the capability is independent. If it is one step in a workflow, fill this before adoption or creation.",
            "",
            "```yaml",
            "chain_id: <workflow id or standalone>",
            "position: <this step's role>",
            "consumes:",
            "  - <upstream artifact>",
            "produces:",
            "  - <downstream artifact>",
            "handoff_status:",
            "  - <ready/needs/block status>",
            "next_skill:",
            "  - <downstream skill or none>",
            "must_not:",
            "  - <boundary this skill must not cross>",
            "proof_surface:",
            "  - <command, file, lock, or runtime proof>",
            "```",
            "",
            "Chat history may explain the decision, but it is not a proof surface.",
            "",
            "## Repo State Machine",
            "",
            "Use this block before adopting, overlaying, or creating any suite, old plugin, or multi-skill repository.",
            "",
            "```yaml",
            "repo_type: standalone_skill | composite_skill_repo | runtime_repo",
            "workflow_id: <repo workflow id or standalone>",
            "state_machine_required: true | false",
            "state_machine_doc: WORKFLOW.md | runtime_lifecycle | none",
            "artifact_gates:",
            "  - <non-empty gate>",
            "proof_surfaces:",
            "  - <checker/file/runtime proof>",
            "registry_handoff: <workflow_index entry or none>",
            "```",
            "",
            "`composite_skill_repo` requires `WORKFLOW.md` before the repo can be marked workflow-ready. `runtime_repo` may use `runtime_lifecycle`.",
            "",
            "## Invocation Policy",
            "",
            "Use this block whenever a source repo, old plugin, or suite contains more than one capability. Keep groups install-only unless a runtime bundle or explicit user request requires a facade.",
            "",
            "```yaml",
            "atomic_skill: on_demand",
            "installability: <single-skill | group-install-only | runtime-preflight-sensitive | blocked>",
            "group_callable: false",
            "facade: <blocked | runtime-exception | user-requested>",
            "```",
            "",
            "## Capability Map",
            "",
            "| Capability | Upstream Path | Source Strategy | Installability | Invocation Policy | Proof Surface |",
            "|---|---|---|---|---|---|",
            markdown_table_row(
                [
                    query,
                    legacy_asset or "<candidate skill path>",
                    "needs-review",
                    "single-skill",
                    "on-demand",
                    "read SKILL.md + quick_validate.py + audit_skill.py",
                ]
            ),
            "",
            "## Verification Checklist",
            "",
            "- [ ] Read the candidate `SKILL.md`, not only README/search result.",
            "- [ ] Check `scripts/`, `references/`, and `assets/` for runtime or security implications.",
            "- [ ] Check maintainer/source reputation with GitHub health: stars, forks, open issues, license, archived/disabled state, default branch, latest push, latest update, and canonical repo redirect.",
            "- [ ] Check license or reuse boundary when available.",
            "- [ ] Confirm commit/tag/tree hash can be locked.",
            "- [ ] Confirm install target: `.agents/skills`, `.claude/skills`, or both.",
            f"- [ ] DOKO local research was run before adoption planning for nontrivial new, modify, migration, or replacement tasks with `dokobot read --local <url>` across general web, recent {FRESHNESS_DAYS}-day web, X/Twitter, Reddit, Hacker News, YouTube, GitHub discussions/issues/PRs, and AI skill community sources.",
            "- [ ] X/Twitter, Reddit, and marketplace/community hits were treated as discovery leads only; adoption still requires repo/SKILL.md/license/maintenance review.",
            "- [ ] Old local Skill/Plugin content was treated as need evidence, not as the source of truth.",
            "- [ ] Coverage was judged against the real capability need, not only the old asset name.",
            "- [ ] Chain contract is marked `standalone` or records consumed artifact, produced artifact, handoff status, next skill, boundary, and proof surface.",
            "- [ ] Repo state machine is marked `standalone_skill`, `composite_skill_repo`, or `runtime_repo`.",
            "- [ ] Composite repos have `WORKFLOW.md` or an explicit blocker; runtime repos have `runtime_lifecycle` proof.",
            "- [ ] Multi-skill repos/suites were decomposed into atomic capabilities.",
            "- [ ] Registry groups are marked install-only and `group_callable=false`.",
            "",
            "## Recommended Next Step",
            "",
            "```text",
            "Route: needs-review",
            "Install command: <fill after SKILL.md inspection>",
            "Adoption command: <fill after source path is confirmed>",
            "Overlay needed: unknown",
            "Keep Kun gap skill: unknown",
            "Registry fields: source repo, skill path, ref/SHA, tree hash, install target",
            "Chain contract: standalone | <chain_id/position/consumes/produces/handoff_status/next_skill/proof_surface>",
            "Repo state machine: standalone_skill | composite_skill_repo + WORKFLOW.md | runtime_repo + runtime_lifecycle",
            "Invocation policy: atomic_skill=on_demand; group=install_only; group_callable=false",
            "Risks: candidate SKILL.md not inspected yet; repo health is a gate, not a substitute for reading source",
            "```",
            "",
            "## Tool Evidence",
            "",
        ]
    )

    for result in commands:
        cmd = " ".join(result["cmd"])
        status = "timeout" if result.get("timed_out") else result.get("returncode")
        lines.extend(
            [
                f"### `{cmd}`",
                "",
                f"- status: `{status}`",
                "",
                "```text",
                strip_ansi((result.get("stdout") or result.get("stderr") or "").strip())[:8000],
                "```",
                "",
            ]
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research upstream Agent Skill candidates and write a source card.")
    parser.add_argument("query", help="skill need or search query")
    parser.add_argument("--output", default="", help="source card output path")
    parser.add_argument("--research-dir", default="research/source-cards", help="directory for source cards when --output is omitted")
    parser.add_argument("--limit", type=int, default=8, help="max candidates per tool")
    parser.add_argument("--timeout", type=int, default=20, help="timeout per external command")
    parser.add_argument("--skip-skills-find", action="store_true")
    parser.add_argument("--skip-github-search", action="store_true")
    parser.add_argument(
        "--use-doko",
        action="store_true",
        help="also run multi-source DOKO local research through dokobot read --local",
    )
    parser.add_argument("--lifecycle-task", default="adopt-upstream")
    parser.add_argument("--legacy-asset", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands: list[dict[str, Any]] = []
    skills_candidates: list[dict[str, str]] = []
    github_candidates: list[dict[str, Any]] = []
    doko_results: list[str] = []

    if not args.skip_skills_find:
        result = run_command(["npx", "--yes", "skills", "find", args.query], args.timeout)
        commands.append(result)
        if result["returncode"] == 0:
            skills_candidates = parse_skills_find(result["stdout"], args.limit)

    if not args.skip_github_search:
        github_query = build_github_query(args.query)
        result = run_command(
            [
                "gh",
                "search",
                "repos",
                github_query,
                "--limit",
                str(args.limit),
                "--json",
                GITHUB_SEARCH_FIELDS,
            ],
            args.timeout,
        )
        commands.append(result)
        if result["returncode"] == 0:
            github_candidates = parse_github_search(result["stdout"], args.limit)

    if skills_candidates:
        for candidate in skills_candidates:
            health, result = fetch_repo_health(candidate["repo"], args.timeout)
            commands.append(result)
            merge_repo_health(candidate, health)

    if args.use_doko:
        for source_label, source_url in build_doko_sources(args.query):
            result = run_command(["dokobot", "read", "--local", source_url, "--screens", "3"], args.timeout)
            result["source_label"] = source_label
            commands.append(result)
            if result["returncode"] == 0:
                doko_results.extend(
                    f"[{source_label}] {line}"
                    for line in parse_doko_search(result["stdout"], args.limit)
                )

    output = Path(args.output) if args.output else Path(args.research_dir) / f"{slugify(args.query)}.md"
    write_source_card(
        output,
        args.query,
        args.lifecycle_task,
        args.legacy_asset,
        skills_candidates,
        github_candidates,
        doko_results,
        commands,
    )
    print(f"source_card: {output.resolve()}")
    print(f"skills_find_candidates: {len(skills_candidates)}")
    print(f"github_candidates: {len(github_candidates)}")
    print(f"doko_results: {len(doko_results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
