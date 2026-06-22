#!/usr/bin/env python3
"""
// Input: 更新前后两个 skill 目录（--before, --after）。
// Output: 增量更新审计报告（PASS/FAIL + 详细问题）。
// Pos: skill-evolver/scripts - 编辑后的质量门控。
"""

from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path


TEXT_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".txt", ".json"}
RESOURCE_DIRS = ("scripts", "references", "assets")
RESOURCE_REF_RE = re.compile(r"(?<!/)\b((?:scripts|references|assets)/[A-Za-z0-9._/-]+)")
PLACEHOLDER_PATTERNS = [r"\bTODO\b", r"\bTBD\b", r"\[TODO[^\]]*\]", r"\[TBD[^\]]*\]"]
MAX_SKILL_NAME_LENGTH = 64


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter_fields(skill_text: str) -> tuple[dict[str, str] | None, str]:
    if not skill_text.startswith("---\n"):
        return None, "SKILL.md 缺少 frontmatter 起始分隔符。"
    end_marker = "\n---\n"
    end_idx = skill_text.find(end_marker, 4)
    if end_idx == -1:
        return None, "SKILL.md 缺少 frontmatter 结束分隔符。"

    raw_frontmatter = skill_text[4:end_idx]
    fields: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        fields[key.strip()] = value
    return fields, ""


def has_trigger_phrase(description: str) -> bool:
    lower = description.lower()
    hints = ["use when", "used when", "trigger", "when ", "用于", "适用于", "当", "触发"]
    return any(h in lower or h in description for h in hints)


def extract_resource_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for match in RESOURCE_REF_RE.finditer(text):
        ref = match.group(1).rstrip("/")
        parts = ref.split("/")
        if len(parts) < 2:
            continue
        filename = parts[-1]
        if "." not in filename:
            continue
        refs.add(ref)
    return refs


def collect_resource_files(skill_dir: Path) -> set[str]:
    files: set[str] = set()
    for folder in RESOURCE_DIRS:
        base = skill_dir / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                files.add(path.relative_to(skill_dir).as_posix())
    return files


def scan_dangling_resource_refs(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir).as_posix()
        if any(part.startswith(".") for part in path.relative_to(skill_dir).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        refs = extract_resource_refs(text)
        for ref in sorted(refs):
            if not (skill_dir / ref).exists():
                errors.append(f"{rel} 引用了不存在路径: {ref}")
    return errors


def detect_append_only(before_text: str, after_text: str) -> tuple[bool, dict[str, float]]:
    before_lines = before_text.splitlines()
    after_lines = after_text.splitlines()
    matcher = difflib.SequenceMatcher(a=before_lines, b=after_lines)
    tail_start = int(len(after_lines) * 0.8)

    total_added = 0
    tail_added = 0
    touched_existing = False

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"replace", "delete"} and i2 > i1:
            touched_existing = True
        if tag in {"insert", "replace"} and j2 > j1:
            added = j2 - j1
            total_added += added
            overlap_start = max(j1, tail_start)
            overlap_end = j2
            if overlap_end > overlap_start:
                tail_added += overlap_end - overlap_start

    ratio = (tail_added / total_added) if total_added else 0.0
    append_only = total_added > 0 and ratio >= 0.85 and not touched_existing
    stats = {
        "total_added": float(total_added),
        "tail_added": float(tail_added),
        "tail_ratio": round(ratio, 4),
    }
    return append_only, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 skill 的增量更新质量。")
    parser.add_argument("--before", required=True, help="更新前的 skill 目录。")
    parser.add_argument("--after", required=True, help="更新后的 skill 目录。")
    parser.add_argument("--out", default="", help="可选：将报告写入文件。")
    args = parser.parse_args()

    before_dir = Path(args.before).resolve()
    after_dir = Path(args.after).resolve()

    major_issues: list[str] = []
    warnings: list[str] = []

    before_skill = before_dir / "SKILL.md"
    after_skill = after_dir / "SKILL.md"
    if not before_skill.exists():
        major_issues.append(f"更新前缺少 SKILL.md: {before_skill}")
    if not after_skill.exists():
        major_issues.append(f"更新后缺少 SKILL.md: {after_skill}")
    if major_issues:
        report = "\n".join(["FAIL"] + [f"- {x}" for x in major_issues])
        if args.out:
            out_path = Path(args.out).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report, encoding="utf-8")
        print(report)
        return 1

    before_text = read_text(before_skill)
    after_text = read_text(after_skill)

    fields, fm_err = extract_frontmatter_fields(after_text)
    if fm_err:
        major_issues.append(fm_err)
    else:
        assert fields is not None
        keys = set(fields.keys())
        if keys != {"name", "description"}:
            major_issues.append(
                f"frontmatter 字段应仅包含 name/description，当前为: {sorted(keys)}"
            )
        name = fields.get("name", "").strip()
        if not name:
            major_issues.append("frontmatter name 为空。")
        else:
            if not re.match(r"^[a-z0-9-]+$", name):
                major_issues.append("frontmatter name 必须为小写连字符命名（kebab-case）。")
            if name.startswith("-") or name.endswith("-") or "--" in name:
                major_issues.append("frontmatter name 不能以连字符开头/结尾或含连续连字符。")
            if len(name) > MAX_SKILL_NAME_LENGTH:
                major_issues.append(
                    f"frontmatter name 过长（{len(name)}），上限 {MAX_SKILL_NAME_LENGTH}。"
                )
        desc = fields.get("description", "").strip()
        if len(desc) < 12:
            major_issues.append("frontmatter description 过短或为空。")
        elif not has_trigger_phrase(desc):
            major_issues.append("frontmatter description 缺少明确触发表达。")
        if len(desc) > 1024:
            major_issues.append("frontmatter description 超过 1024 字符上限。")
        if "<" in desc or ">" in desc:
            major_issues.append("frontmatter description 不得包含尖括号（< 或 >）。")

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, after_text, flags=re.IGNORECASE):
            major_issues.append(f"检测到占位符残留: pattern={pattern}")

    append_only, stats = detect_append_only(before_text, after_text)
    if append_only:
        major_issues.append(
            "检测到 append-only 倾向：新增内容主要集中在末尾，且既有区块未被重写。"
        )

    declared_refs = extract_resource_refs(after_text)
    existing_resources = collect_resource_files(after_dir)
    missing_declared = sorted(ref for ref in declared_refs if not (after_dir / ref).exists())
    orphan_resources = sorted(res for res in existing_resources if res not in declared_refs)
    for ref in missing_declared:
        major_issues.append(f"声明资源不存在: {ref}")
    for res in orphan_resources:
        major_issues.append(f"存在未声明资源: {res}")

    dangling_refs = scan_dangling_resource_refs(after_dir)
    for msg in dangling_refs:
        warnings.append(msg)

    status = "PASS" if not major_issues else "FAIL"
    lines = [f"{status}: {after_dir}"]
    lines.append(
        "append-only 统计: "
        f"total_added={int(stats['total_added'])}, "
        f"tail_added={int(stats['tail_added'])}, "
        f"tail_ratio={stats['tail_ratio']}"
    )

    if major_issues:
        lines.append("\n重大问题:")
        lines.extend(f"- {item}" for item in major_issues)

    if warnings:
        lines.append("\n警告:")
        lines.extend(f"- {item}" for item in warnings)

    report = "\n".join(lines) + "\n"
    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0 if not major_issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
