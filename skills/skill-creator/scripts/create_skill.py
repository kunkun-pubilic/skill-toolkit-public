#!/usr/bin/env python3
"""Create an Agent Skill skeleton from local upstream locks and contracts."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SOURCE_STRATEGIES = ("kun_owned", "wrapper_overlay", "fork", "vendor_copy", "reference_only")
INVOCATION_POLICIES = ("on_demand",)
CONTRACT_ALIASES = {
    "core": "agent-skill-core.yaml",
    "codex": "codex-skill.yaml",
    "claude": "claude-code-skill.yaml",
    "claude-code": "claude-code-skill.yaml",
    "kun": "kun-governance.yaml",
    "kun-governance": "kun-governance.yaml",
}


class Blocked(RuntimeError):
    """Raised when official contract-backed creation cannot be proven."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise Blocked(f"required file missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise Blocked(f"YAML file must contain a mapping: {path}")
    return data


def require_kebab_case(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("skill name must be kebab-case: lowercase letters, digits, and single hyphens")
    if len(name) > 64:
        raise ValueError("skill name must be <= 64 characters")


def normalize_description(description: str) -> str:
    description = " ".join(description.strip().split())
    if not description:
        raise ValueError("description is required")
    if "<" in description or ">" in description:
        raise ValueError("description cannot contain angle brackets")
    if len(description) > 500:
        raise ValueError("description must be <= 500 characters")
    return description


def split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def normalize_contract_files(raw_contracts: str) -> list[str]:
    requested = split_csv(raw_contracts)
    if not requested:
        requested = ["codex", "claude"]
    ordered = ["agent-skill-core.yaml"]
    for item in requested:
        filename = CONTRACT_ALIASES.get(item, item)
        if not filename.endswith(".yaml"):
            filename = f"{filename}.yaml"
        if filename not in ordered:
            ordered.append(filename)
    if "kun-governance.yaml" not in ordered:
        ordered.append("kun-governance.yaml")
    return ordered


def load_contracts(contracts_dir: Path, raw_contracts: str) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for filename in normalize_contract_files(raw_contracts):
        path = contracts_dir / filename
        data = read_yaml(path)
        data["_path"] = path.as_posix()
        data["_filename"] = filename
        contracts.append(data)
    return contracts


def selected_upstream_ids(contracts: list[dict[str, Any]], explicit_ids: list[str]) -> list[str]:
    ids: list[str] = []
    for contract in contracts:
        for uid in contract.get("upstream_sources", []) or []:
            if uid not in ids:
                ids.append(uid)
    for value in explicit_ids:
        for uid in split_csv(value):
            if uid not in ids:
                ids.append(uid)
    return ids


def load_upstream_state(registry_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    upstreams = read_yaml(registry_root / "upstreams.yaml")
    locks = read_yaml(registry_root / "upstream-lock.yaml")
    return upstreams, locks


def resolve_registry_root(raw_registry_root: str) -> Path:
    if raw_registry_root:
        return Path(raw_registry_root).expanduser().resolve()

    candidates = [
        repo_root().parent / "kun-agent-registry",
        Path.cwd() / "kun-agent-registry",
        Path.cwd().parent / "kun-agent-registry",
        Path.home() / ".agents" / "kun-agent-registry",
    ]
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if (resolved / "upstreams.yaml").is_file() and (resolved / "upstream-lock.yaml").is_file():
            return resolved
    checked = ", ".join(candidate.as_posix() for candidate in candidates)
    raise Blocked(
        "registry not found; provide --registry-root or install kun-agent-registry. "
        f"checked: {checked}"
    )


def verify_upstreams(registry_root: Path, upstream_ids: list[str]) -> list[dict[str, Any]]:
    upstreams, locks = load_upstream_state(registry_root)
    upstream_map = {item["id"]: item for item in upstreams.get("upstreams", [])}
    lock_map = locks.get("locks", {})
    resolved: list[dict[str, Any]] = []

    for uid in upstream_ids:
        upstream = upstream_map.get(uid)
        if not upstream:
            raise Blocked(f"upstream not registered: {uid}")
        if upstream.get("status") not in ("active", "reference_only"):
            raise Blocked(f"upstream is not active/reference_only: {uid}")
        lock = lock_map.get(uid)
        if not lock:
            raise Blocked(f"upstream lock missing: {uid}")
        snapshot = lock.get("snapshot") or upstream.get("snapshot")
        if snapshot:
            snapshot_path = registry_root / snapshot
            if not snapshot_path.is_file():
                raise Blocked(f"upstream snapshot missing for {uid}: {snapshot}")
            if lock.get("source_type") == "docs_page":
                expected = lock.get("content_sha256")
                retrieved_at = lock.get("retrieved_at")
                if not expected or not retrieved_at:
                    raise Blocked(f"docs upstream lock must include retrieved_at and content_sha256: {uid}")
                actual = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
                if actual != expected:
                    raise Blocked(f"docs upstream snapshot hash mismatch: {uid}")
        if lock.get("source_type") == "github_repo" and not lock.get("commit"):
            raise Blocked(f"github upstream lock must include commit: {uid}")
        resolved.append({"id": uid, "upstream": upstream, "lock": lock})
    return resolved


def public_standalone_upstreams(upstream_ids: list[str]) -> list[dict[str, Any]]:
    """Return explicit evidence-gap records for users without Kun's private registry."""
    return [
        {
            "id": uid,
            "upstream": {
                "url": "not-locked-in-public-standalone-mode",
                "status": "reference_only",
            },
            "lock": {
                "source_type": "public_standalone_gap",
                "note": "Generated without kun-agent-registry; verify upstream docs before claiming official adoption.",
            },
        }
        for uid in upstream_ids
    ]


def collect_applied_rules(contracts: list[dict[str, Any]]) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    for contract in contracts:
        contract_id = contract.get("id", contract.get("_filename", "unknown"))
        for rule in contract.get("applied_rules", []) or []:
            rules.append(
                {
                    "contract": str(contract_id),
                    "id": str(rule.get("id", "")),
                    "text": str(rule.get("text", "")),
                }
            )
    return rules


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def host_support_from_contracts(contracts: list[dict[str, Any]]) -> str:
    hosts = []
    for contract in contracts:
        host = contract.get("host")
        if host == "codex" and "Codex" not in hosts:
            hosts.append("Codex")
        if host == "claude_code" and "Claude Code" not in hosts:
            hosts.append("Claude Code")
    return ", ".join(hosts) if hosts else "Codex, Claude Code"


def contract_names(contracts: list[dict[str, Any]]) -> list[str]:
    return [str(contract.get("id", contract.get("_filename", "unknown"))) for contract in contracts]


def build_skill_md(args: argparse.Namespace, contracts: list[dict[str, Any]]) -> str:
    title = args.display_name or args.name
    host_support = args.host_support or host_support_from_contracts(contracts)
    plugin_needed = args.plugin_needed or "no"
    contract_list = ", ".join(contract_names(contracts))
    return f"""---
name: {args.name}
description: {args.description}
---

# {title}

## 角色

本技能用于封装一个稳定的 Agent Skill 判断流程。它基于 `references/official-basis.md` 中记录的官方来源锁定版本和本地 contracts 执行。

## 官方依据

```yaml
source_strategy: {args.source_strategy}
repo_type: {args.repo_type}
state_machine: {args.state_machine}
host_support: {host_support}
plugin_needed: {plugin_needed}
contracts: {contract_list}
proof_surface: {args.proof_surface}
invocation_policy: {args.invocation_policy}
official_basis: references/official-basis.md
```

本技能是 atomic on-demand 调用单元；不要把它包装成 suite facade、group route 或 orchestra。若多个技能需要一起安装，只在 registry 记录 install-only group。

## Chain Position

```yaml
chain_id: standalone
position: standalone
consumes: []
produces:
  - skill-owned-result
handoff_status:
  - complete
next_skill: []
must_not:
  - cross unrelated workflow boundaries
proof_surface:
  - {args.proof_surface}
```

If this Skill becomes part of a workflow chain, update `references/chain-position.md` before registry promotion. Do not rely on chat history as chain truth.
If this Skill is created inside a `composite_skill_repo`, the repository must also carry a repo-level `WORKFLOW.md` state machine before it can be marked workflow-ready.

## 方法调用

```text
/{args.name}(input, context?, output?)
```

## 运行流程

1. 确认当前请求是否命中本技能的触发条件。
2. 读取 `references/official-basis.md`，确认本技能生成时使用的官方 upstream lock、contracts 和 applied rules。
3. 检查输入材料是否足够；缺材料时只问影响结果的 1-3 个问题。
4. 执行本技能的核心判断流程。
5. 输出结果和验证证据。
6. 若涉及用户可感知行为变化，按 `references/pilot-closed-loop.md` 产出 pressure scenario；没有真实新对话证据时写 `pending-user-pilot`。

## 输出契约

```text
结果：<本技能产出的结论或文件>
证据：<命令、文件、引用或人工验收面>
官方依据：<references/official-basis.md 中的 contract/upstream 记录>
风险：<边界、缺口或需要用户确认的事项>
下一步：<完成、验证、回环或交接>
```

## 资源

- `references/official-basis.md`：生成本技能时使用的官方 upstream lock、contracts 和 applied rules。
- `references/chain-position.md`：standalone 默认链条位置；进入 workflow 前必须更新。
- `references/pilot-closed-loop.md`：新技能行为验收模板。

## 本技能的 deletion-spec

- **触发删除条件**：当该判断流程被上游官方 Skill 覆盖，或已合并进更合适的 Kun Skill。
- **禁用方式**：删除本技能目录，并同步 registry / lockfile / install adapter。
- **卸载清单**：`SKILL.md`、`agents/openai.yaml`、`references/official-basis.md`、`references/pilot-closed-loop.md`、registry/lockfile 中指向本技能的记录。
"""


def build_openai_yaml(args: argparse.Namespace) -> str:
    display_name = args.display_name or args.name
    short_description = args.short_description or "官方合同生成的 Kun Agent Skill"
    default_prompt = args.default_prompt or f"使用 ${args.name} 处理这个任务，并输出官方依据和验证证据。"
    return "\n".join(
        [
            "interface:",
            f"  display_name: {yaml_quote(display_name)}",
            f"  short_description: {yaml_quote(short_description)}",
            f"  default_prompt: {yaml_quote(default_prompt)}",
            "policy:",
            "  allow_implicit_invocation: true",
            f"  invocation_policy: {args.invocation_policy}",
            "",
        ]
    )


def build_pilot_reference() -> str:
    return """# 新技能 pressure scenario 闭环

用于验证新建 Skill 是否真的改善用户可感知行为。没有真实新对话证据时，状态只能写 `pending-user-pilot`。

```text
待测技能：<技能名称和路径>
创建目标：<这个技能要稳定解决什么判断流程>
官方依据：references/official-basis.md
测试提示词：<真实用户风格的小任务>
预期行为：
- <新版技能必须自然触发>
- <新版技能必须执行的流程或脚本>
- <新版技能必须避免的相邻误触发>
当前状态：通过 / 部分通过 / 失败 / pending-user-pilot
```
"""


def build_chain_position_reference(args: argparse.Namespace) -> str:
    return f"""# Chain Position

```yaml
chain_id: standalone
position: standalone
consumes: []
produces:
  - skill-owned-result
handoff_status:
  - complete
next_skill: []
must_not:
  - cross unrelated workflow boundaries
proof_surface:
  - {args.proof_surface}
invocation_policy: {args.invocation_policy}
```

Update this file before registry promotion if the Skill becomes one member of a workflow chain. Chat history is not chain truth.
"""


def build_official_basis(
    args: argparse.Namespace,
    contracts: list[dict[str, Any]],
    upstream_locks: list[dict[str, Any]],
    rules: list[dict[str, str]],
) -> str:
    lines = [
        "# Official Basis",
        "",
        "This file is generated by `skill-creator/scripts/create_skill.py`.",
        "",
        "## Generation Summary",
        "",
        f"- skill_name: `{args.name}`",
        f"- source_strategy: `{args.source_strategy}`",
        f"- repo_type: `{args.repo_type}`",
        f"- state_machine: `{args.state_machine}`",
        f"- host_support: `{args.host_support or host_support_from_contracts(contracts)}`",
        f"- proof_surface: `{args.proof_surface}`",
        f"- invocation_policy: `{args.invocation_policy}`",
        "",
        "## Contracts Used",
        "",
    ]
    for contract in contracts:
        lines.append(f"- `{contract.get('id')}` from `{contract.get('_path')}`")

    lines.extend(["", "## Upstream Locks", ""])
    for item in upstream_locks:
        uid = item["id"]
        lock = item["lock"]
        upstream = item["upstream"]
        bits = [f"- id: `{uid}`", f"  url: {upstream.get('url')}"]
        if lock.get("commit"):
            bits.append(f"  commit: `{lock.get('commit')}`")
        if lock.get("retrieved_at"):
            bits.append(f"  retrieved_at: `{lock.get('retrieved_at')}`")
        if lock.get("content_sha256"):
            bits.append(f"  content_sha256: `{lock.get('content_sha256')}`")
        if lock.get("source_type"):
            bits.append(f"  source_type: `{lock.get('source_type')}`")
        if lock.get("note"):
            bits.append(f"  note: {lock.get('note')}")
        if lock.get("snapshot") or upstream.get("snapshot"):
            bits.append(f"  snapshot: `{lock.get('snapshot') or upstream.get('snapshot')}`")
        lines.extend(bits)

    lines.extend(["", "## Applied Rules", ""])
    for rule in rules:
        lines.append(f"- `{rule['id']}` ({rule['contract']}): {rule['text']}")
    lines.append("")
    return "\n".join(lines)


def should_generate_openai_yaml(contracts: list[dict[str, Any]]) -> bool:
    return any(contract.get("id") == "codex-skill" for contract in contracts)


def plugin_needed_is_no(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in ("", "no", "false", "none", "0")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an official contract-backed Agent Skill skeleton.")
    parser.add_argument("name", help="kebab-case skill name")
    parser.add_argument("--target-root", default=".agents/skills", help="directory that will contain the skill folder")
    parser.add_argument("--description", required=True, help="SKILL.md trigger description")
    parser.add_argument("--display-name", default="", help="UI display name")
    parser.add_argument("--short-description", default="", help="UI short description")
    parser.add_argument("--default-prompt", default="", help="OpenAI default prompt")
    parser.add_argument("--source-strategy", choices=SOURCE_STRATEGIES, default="wrapper_overlay")
    parser.add_argument("--upstream-id", action="append", default=[], help="extra upstream id; can be repeated or comma-separated")
    parser.add_argument("--registry-root", default="", help="kun-agent-registry root; auto-discovered when omitted")
    parser.add_argument(
        "--public-standalone",
        action="store_true",
        help="continue without kun-agent-registry and record upstream locks as public evidence gaps",
    )
    parser.add_argument("--contracts", default="codex,claude", help="comma-separated contract aliases or filenames")
    parser.add_argument("--host-support", default="")
    parser.add_argument("--plugin-needed", default="no")
    parser.add_argument("--proof-surface", required=True)
    parser.add_argument("--invocation-policy", choices=INVOCATION_POLICIES, default="on_demand")
    parser.add_argument(
        "--repo-type",
        choices=("standalone_skill", "composite_skill_repo", "runtime_repo"),
        default="standalone_skill",
        help="repository context for the generated skill",
    )
    parser.add_argument(
        "--state-machine",
        default="chain-position",
        help="state machine proof: chain-position, WORKFLOW.md, or runtime_lifecycle",
    )
    parser.add_argument("--force", action="store_true", help="overwrite an existing generated skill")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        require_kebab_case(args.name)
        args.description = normalize_description(args.description)
        root = repo_root()
        contracts = load_contracts(root / "contracts", args.contracts)
        upstream_ids = selected_upstream_ids(contracts, args.upstream_id)
        registry_label = ""
        try:
            registry_root = resolve_registry_root(args.registry_root)
            upstream_locks = verify_upstreams(registry_root, upstream_ids)
            registry_label = registry_root.as_posix()
        except Blocked:
            if not args.public_standalone:
                raise
            upstream_locks = public_standalone_upstreams(upstream_ids)
            registry_label = "public-standalone-no-registry"
        rules = collect_applied_rules(contracts)
        if not plugin_needed_is_no(args.plugin_needed):
            raise Blocked(f"plugin_needed={args.plugin_needed}; route this request to plugin-manager")
        if args.repo_type == "composite_skill_repo" and args.state_machine != "WORKFLOW.md":
            raise Blocked("composite_skill_repo requires --state-machine WORKFLOW.md")
        if args.repo_type == "runtime_repo" and args.state_machine not in ("runtime_lifecycle", "WORKFLOW.md"):
            raise Blocked("runtime_repo requires --state-machine runtime_lifecycle or WORKFLOW.md")

        target_root = Path(args.target_root).resolve()
        skill_dir = target_root / args.name
        if skill_dir.exists() and not args.force:
            raise ValueError(f"target skill already exists: {skill_dir}")
        skill_dir.mkdir(parents=True, exist_ok=True)
        write(skill_dir / "SKILL.md", build_skill_md(args, contracts))
        if should_generate_openai_yaml(contracts):
            write(skill_dir / "agents" / "openai.yaml", build_openai_yaml(args))
        write(skill_dir / "references" / "official-basis.md", build_official_basis(args, contracts, upstream_locks, rules))
        write(skill_dir / "references" / "chain-position.md", build_chain_position_reference(args))
        write(skill_dir / "references" / "pilot-closed-loop.md", build_pilot_reference())
        print(f"created: {skill_dir}")
        if target_root.name == "skills" and target_root.parent.name == ".agents":
            print(f"registered_codex_project_skill: {skill_dir}")
        print("contracts: " + ", ".join(contract_names(contracts)))
        print(f"registry_root: {registry_label}")
        print("upstreams: " + ", ".join(item["id"] for item in upstream_locks))
        print("applied_rules: " + ", ".join(rule["id"] for rule in rules))
        print(f"validate: python3 {root / 'skills/skill-modify/scripts/quick_validate.py'} {skill_dir}")
        print(f"audit: python3 {root / 'skills/skill-modify/scripts/audit_skill.py'} {skill_dir}")
        return 0
    except Blocked as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
