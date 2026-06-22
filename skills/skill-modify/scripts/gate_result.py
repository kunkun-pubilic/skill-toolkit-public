#!/usr/bin/env python3
"""Shared helpers for gate_result_v1 validator output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GATE_RESULT_VERSION = "gate_result_v1"
VALID_STATUSES = {"pass", "warn", "block", "error"}
HUMAN_STATUS_ZH = {
    "pass": "通过",
    "warn": "警告",
    "block": "阻断",
    "error": "执行错误",
}


def status_from_issues(errors: list[str], warnings: list[str]) -> str:
    if errors:
        return "block"
    if warnings:
        return "warn"
    return "pass"


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "scripts" / "eval_registry.json").is_file():
            return candidate
    return current


def load_eval_registry(repo_root: Path) -> dict[str, Any]:
    registry_path = repo_root / "scripts" / "eval_registry.json"
    if not registry_path.is_file():
        return {"gates": []}
    return json.loads(registry_path.read_text(encoding="utf-8"))


def gate_registry_entry(gate_id: str, repo_root: Path) -> dict[str, Any]:
    registry = load_eval_registry(repo_root)
    for entry in registry.get("gates", []):
        if entry.get("gate_id") == gate_id:
            return entry
    return {}


def make_check(
    check_id: str,
    status: str,
    message: str,
    refs: list[str] | None = None,
    fix_hint_zh: str | None = None,
    repair_route: str | None = None,
    suggested_command: str | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid gate check status: {status}")
    check: dict[str, Any] = {
        "check_id": check_id,
        "status": status,
        "message_zh": message,
    }
    if refs:
        check["refs"] = refs
    if fix_hint_zh:
        check["fix_hint_zh"] = fix_hint_zh
    if repair_route:
        check["repair_route"] = repair_route
    if suggested_command:
        check["suggested_command"] = suggested_command
    return check


def build_gate_result(
    *,
    gate_id: str,
    status: str,
    summary_zh: str,
    scope: dict[str, Any],
    checks: list[dict[str, Any]],
    trace_refs: list[str] | None = None,
    grading_refs: list[str] | None = None,
    blocks_closure: bool = False,
    blocks_dispatch: bool = False,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid gate status: {status}")
    return {
        "schema_version": GATE_RESULT_VERSION,
        "gate_id": gate_id,
        "status": status,
        "human_status_zh": HUMAN_STATUS_ZH[status],
        "summary_zh": summary_zh,
        "scope": scope,
        "checks": checks,
        "blocks_closure": blocks_closure,
        "blocks_dispatch": blocks_dispatch,
        "trace_refs": trace_refs or [],
        "grading_refs": grading_refs or [],
    }


def blocking_flags(gate_id: str, status: str, repo_root: Path) -> tuple[bool, bool]:
    entry = gate_registry_entry(gate_id, repo_root)
    closure = status in set(entry.get("blocks_closure_on", []))
    dispatch = status in set(entry.get("blocks_dispatch_on", []))
    return closure, dispatch


def emit_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
