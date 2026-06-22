#!/usr/bin/env python3
"""
技能目录轻量审计器（Lightweight auditor for a skill folder）。

检查项（Checks）:
- SKILL.md 存在且 frontmatter 合法
- frontmatter 仅包含 name/description
- description 含有明确触发表达
- 无占位符泄漏（TODO/TBD/template 标记）
- SKILL.md 资源声明完整（声明存在）
- 资源目录无孤儿文件（存在但未在 SKILL.md 声明）
- 全目录无悬空路径引用（scripts/references/assets 路径指向不存在文件）
- 可选结构卫生检查（额外噪音文档）
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


MAJOR_DOC_NOISE = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}

PLACEHOLDER_PATTERNS = [
    r"\[TODO[^\]]*\]",
    r"\[TBD[^\]]*\]",
    r"\bTODO:\b",
    r"\bTBD:\b",
    r"Replace with",
    r"请替换为",
]

TRIGGER_HINTS_EN = [
    "use when",
    "use this skill",
    "used when",
    "when ",
    "trigger",
    "used for",
    "especially",
]

TRIGGER_HINTS_ZH = [
    "使用时",
    "用于",
    "适用于",
    "当",
    "触发",
]

RESOURCE_DIRS = ("scripts", "references", "assets")
IGNORED_REF_SCAN_DIRS = {"examples"}
# 仅匹配相对路径形式，避免将绝对路径中的 ".../scripts/xxx" 误判为本 skill 资源。
RESOURCE_REF_RE = re.compile(r"(?<!/)\b((?:scripts|references|assets)/[A-Za-z0-9._/-]+)")
TEXT_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".py", ".json", ".txt"}
SCRIPT_SUFFIXES = {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".ts", ".tsx"}
DOC_SUFFIXES = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json"}
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 500
OFFICIAL_BASIS_REF = "/".join(("references", "official-basis.md"))
RUNTIME_RULES_REF = "/".join(("references", "runtime-rules.md"))
UPSTREAM_SOURCE_DIR = "/".join(("references", "upstream"))


def official_basis_text(skill_dir: Path) -> str:
    official_basis = skill_dir / OFFICIAL_BASIS_REF
    if not official_basis.exists():
        return ""
    try:
        return official_basis.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def is_official_overlay(skill_dir: Path, raw_text: str) -> bool:
    official_basis = skill_dir / OFFICIAL_BASIS_REF
    basis_text = official_basis_text(skill_dir)
    combined = f"{raw_text}\n{basis_text}".lower()
    if official_basis.exists() and ("official-overlay" in combined or "official_overlay" in combined):
        return True

    self_declared_overlay_patterns = [
        "it is an official-overlay",
        "this skill is an official-overlay",
        "this skill was generated through `official-overlay`",
        "route decision: `official_overlay`",
        "route decision: `official-overlay`",
    ]
    return any(pattern in combined for pattern in self_declared_overlay_patterns)


def is_official_adopt(skill_dir: Path, raw_text: str) -> bool:
    basis_text = official_basis_text(skill_dir)
    combined = f"{raw_text}\n{basis_text}".lower()
    official_basis = skill_dir / OFFICIAL_BASIS_REF
    if official_basis.exists() and ("official-adopt" in combined or "official_adopt" in combined):
        return True

    self_declared_adopt_patterns = [
        "it is an official-adopt",
        "this skill is an official-adopt",
        "this skill was generated through `official-adopt`",
        "route decision: `official_adopt`",
        "route decision: `official-adopt`",
    ]
    return any(pattern in combined for pattern in self_declared_adopt_patterns)


def official_source_route(skill_dir: Path, raw_text: str) -> str:
    if is_official_overlay(skill_dir, raw_text):
        return "official-overlay"
    if is_official_adopt(skill_dir, raw_text):
        return "official-adopt"
    return ""


def official_basis_is_runtime_required(raw_text: str) -> bool:
    if OFFICIAL_BASIS_REF not in raw_text:
        return False
    read_patterns = [
        rf"\b[Rr]ead\s+`?{re.escape(OFFICIAL_BASIS_REF)}`?",
        rf"读取\s*`?{re.escape(OFFICIAL_BASIS_REF)}`?",
        rf"先读\s*`?{re.escape(OFFICIAL_BASIS_REF)}`?",
        rf"先读取\s*`?{re.escape(OFFICIAL_BASIS_REF)}`?",
    ]
    return any(re.search(pattern, raw_text) for pattern in read_patterns)


def runtime_rules_are_runtime_required(raw_text: str) -> bool:
    if RUNTIME_RULES_REF not in raw_text:
        return False
    read_patterns = [
        rf"\b[Rr]ead\b[\s\S]{{0,200}}`?{re.escape(RUNTIME_RULES_REF)}`?",
        rf"读取\s*`?{re.escape(RUNTIME_RULES_REF)}`?",
        rf"先读\s*`?{re.escape(RUNTIME_RULES_REF)}`?",
        rf"先读取\s*`?{re.escape(RUNTIME_RULES_REF)}`?",
    ]
    return any(re.search(pattern, raw_text) for pattern in read_patterns)


def runtime_rules_define_progressive_contract(skill_dir: Path) -> bool:
    runtime_rules = skill_dir / RUNTIME_RULES_REF
    if not runtime_rules.exists():
        return False
    try:
        text = runtime_rules.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    lowered = text.lower()
    required_markers = [
        "ordinary",
        "maintenance",
        "audit",
        "references/upstream",
        "source map",
        "full-read",
    ]
    if not all(marker in lowered for marker in required_markers):
        return False

    escalation_markers = [
        "ambiguity",
        "uncertainty",
        "exact upstream",
        "upstream update",
        "license",
        "provenance",
        "user requests source",
        "conflict",
    ]
    return any(marker in lowered for marker in escalation_markers)


def runtime_rules_define_payload_contract(skill_dir: Path, payload_refs: set[str]) -> bool:
    runtime_rules = skill_dir / RUNTIME_RULES_REF
    if not runtime_rules.exists():
        return False
    try:
        text = runtime_rules.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    lowered = text.lower()
    if not ("source tree" in lowered or "payload" in lowered):
        return False

    has_script = any(Path(ref).suffix.lower() in SCRIPT_SUFFIXES or "/scripts/" in ref for ref in payload_refs)
    has_asset = any(
        "/assets/" in ref or Path(ref).suffix.lower() not in DOC_SUFFIXES | SCRIPT_SUFFIXES
        for ref in payload_refs
    )
    if has_script and "script" not in lowered:
        return False
    if has_asset and not any(marker in lowered for marker in ("asset", "binary", "media", "template", "fixture")):
        return False
    return any(marker in lowered for marker in ("evidence_only", "blocked_until_projected", "operational", "projection"))


def collect_upstream_payload_files(skill_dir: Path) -> set[str]:
    upstream_dir = skill_dir / UPSTREAM_SOURCE_DIR
    if not upstream_dir.exists():
        return set()

    refs: set[str] = set()
    for path in iter_skill_files(upstream_dir):
        refs.add(path.relative_to(skill_dir).as_posix())
    return refs


def collect_upstream_text_files(skill_dir: Path) -> set[str]:
    return {ref for ref in collect_upstream_payload_files(skill_dir) if Path(ref).suffix.lower() in TEXT_SUFFIXES}


def resource_is_runtime_required(raw_text: str, ref: str) -> bool:
    if ref not in raw_text:
        return False
    if ref.startswith(f"{UPSTREAM_SOURCE_DIR}/"):
        upstream_dir_patterns = [
            rf"\b[Rr]ead\b[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/?`?",
            rf"\b[Rr]ead\b[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/\*\.md`?",
            rf"读取[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/?`?",
            rf"读取[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/\*\.md`?",
            rf"先读[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/?`?",
            rf"先读取[\s\S]{{0,400}}`?{re.escape(UPSTREAM_SOURCE_DIR)}/?`?",
        ]
        if any(re.search(pattern, raw_text) for pattern in upstream_dir_patterns):
            return True
    read_patterns = [
        rf"\b[Rr]ead\b[\s\S]{{0,800}}`?{re.escape(ref)}`?",
        rf"读取[\s\S]{{0,800}}`?{re.escape(ref)}`?",
        rf"先读[\s\S]{{0,800}}`?{re.escape(ref)}`?",
        rf"先读取[\s\S]{{0,800}}`?{re.escape(ref)}`?",
    ]
    return any(re.search(pattern, raw_text) for pattern in read_patterns)


def load_frontmatter(skill_md: Path):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text, "文件开头缺少 YAML frontmatter 分隔符（Missing YAML frontmatter delimiter at file start）."

    marker = "\n---\n"
    idx = text.find(marker, 4)
    if idx == -1:
        return None, text, "YAML frontmatter 结束分隔符不合法（Invalid YAML frontmatter closing delimiter）."

    raw = text[4:idx]
    body = text[idx + len(marker) :]

    if yaml is None:
        return None, text, "缺少 PyYAML，无法解析 frontmatter（PyYAML is not available; cannot parse frontmatter）."

    try:
        data = yaml.safe_load(raw)
    except Exception as exc:  # pragma: no cover
        return None, text, f"frontmatter YAML 非法（Invalid frontmatter YAML）: {exc}"

    if not isinstance(data, dict):
        return None, text, "frontmatter 必须是 YAML 映射（Frontmatter must be a YAML mapping）."

    return data, body, None


def has_trigger_language(description: str) -> bool:
    desc_en = description.lower()
    if any(h in desc_en for h in TRIGGER_HINTS_EN):
        return True

    if any(h in description for h in TRIGGER_HINTS_ZH):
        return True

    return False


def iter_skill_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if "__pycache__" in rel.parts:
            continue
        if path.suffix.lower() == ".pyc":
            continue
        yield path


def extract_resource_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for match in RESOURCE_REF_RE.finditer(text):
        ref = match.group(1).rstrip("/`'\".,;:)]}")
        if not ref:
            continue
        parts = ref.split("/")
        if len(parts) < 2:
            continue
        filename = parts[-1]
        # 目录级引用用于说明，不纳入“文件存在性”审计。
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
        for path in iter_skill_files(base):
            files.add(path.relative_to(skill_dir).as_posix())
    return files


def scan_text_refs(skill_dir: Path) -> dict[str, list[str]]:
    ref_to_files: dict[str, list[str]] = defaultdict(list)
    for path in iter_skill_files(skill_dir):
        rel = path.relative_to(skill_dir)
        if rel.parts and rel.parts[0] in IGNORED_REF_SCAN_DIRS:
            continue
        if len(rel.parts) >= 2 and rel.parts[0] == "references" and rel.parts[1] == "upstream":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        refs = extract_resource_refs(text)
        rel_file = rel.as_posix()
        for ref in refs:
            ref_to_files[ref].append(rel_file)
    return ref_to_files


def enclosing_skill_repo(skill_dir: Path) -> Path | None:
    """Return repo root when the audited path is <repo>/skills/<skill>."""
    if skill_dir.parent.name == "skills":
        return skill_dir.parent.parent
    return None


def repo_skill_count(repo_root: Path) -> int:
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return 0
    return sum(1 for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="审计一个 skill 目录（Audit a skill folder）")
    parser.add_argument(
        "skill_dir",
        type=Path,
        help="目标 skill 目录路径（Path to target skill directory）",
    )
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    majors: list[str] = []
    warns: list[str] = []

    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"FAIL: 找不到 skill 目录（skill directory not found）: {skill_dir}")
        return 1

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("FAIL: 缺少 SKILL.md（missing SKILL.md）")
        return 1

    repo_root = enclosing_skill_repo(skill_dir)
    if repo_root and repo_skill_count(repo_root) > 1 and not (repo_root / "WORKFLOW.md").is_file():
        majors.append(
            "复合技能仓库缺少 repo-level WORKFLOW.md 状态机 "
            "(composite skill repo is missing repo-level WORKFLOW.md state machine)."
        )

    frontmatter, body, fm_err = load_frontmatter(skill_md)
    raw_text = skill_md.read_text(encoding="utf-8")

    if fm_err:
        majors.append(fm_err)
    else:
        keys = set(frontmatter.keys())
        required = {"name", "description"}
        if keys != required:
            majors.append(
                "frontmatter 只能包含 name 与 description "
                f"（Frontmatter must contain only name and description; found: {sorted(keys)}）."
            )

        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")

        if not isinstance(name, str) or not name.strip():
            majors.append("frontmatter 的 name 缺失或为空（Frontmatter name is missing or empty）.")
        else:
            clean_name = name.strip()
            if not re.match(r"^[a-z0-9-]+$", clean_name):
                majors.append(
                    "frontmatter 的 name 必须是 kebab-case "
                    "（Frontmatter name must be kebab-case: lowercase letters, digits, hyphens）."
                )
            if clean_name.startswith("-") or clean_name.endswith("-") or "--" in clean_name:
                majors.append(
                    "frontmatter 的 name 不能以连字符开头/结尾且不能出现连续连字符 "
                    "（Frontmatter name cannot start/end with hyphen or contain consecutive hyphens）."
                )
            if len(clean_name) > MAX_SKILL_NAME_LENGTH:
                majors.append(
                    "frontmatter 的 name 过长 "
                    f"（Frontmatter name exceeds {MAX_SKILL_NAME_LENGTH} characters）."
                )
        if not isinstance(description, str) or len(description.strip()) < 24:
            majors.append(
                "frontmatter 的 description 缺失或过短（Frontmatter description is missing or too short）."
            )
        elif not has_trigger_language(description):
            majors.append(
                "frontmatter 的 description 必须包含明确触发表达 "
                "（Frontmatter description must include explicit trigger phrasing, "
                "for example: 'Use when ...' or '用于...'）."
            )
        if isinstance(description, str):
            clean_description = description.strip()
            if len(clean_description) > MAX_DESCRIPTION_LENGTH:
                majors.append(
                    "frontmatter 的 description 超长，疑似把流程/历史/能力清单塞进路由字段 "
                    f"（Frontmatter description exceeds {MAX_DESCRIPTION_LENGTH} characters）."
                )
            if "<" in clean_description or ">" in clean_description:
                majors.append(
                    "frontmatter 的 description 不应包含尖括号 "
                    "（Frontmatter description should not contain < or >）."
                )

    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, raw_text, flags=re.IGNORECASE):
            majors.append(f"检测到占位符标记（Placeholder marker detected）: pattern '{pat}'")

    skill_declared_refs = extract_resource_refs(raw_text)
    existing_resources = collect_resource_files(skill_dir)

    official_route = official_source_route(skill_dir, raw_text)
    if official_route:
        for rel in (OFFICIAL_BASIS_REF, RUNTIME_RULES_REF):
            path = skill_dir / rel
            if path.exists() and path.suffix.lower() in TEXT_SUFFIXES:
                try:
                    skill_declared_refs |= extract_resource_refs(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    pass

        official_basis = skill_dir / OFFICIAL_BASIS_REF
        if not official_basis.exists():
            majors.append(
                f"{official_route} 技能缺少运行时官方底座 "
                f"（{official_route} skill is missing {OFFICIAL_BASIS_REF}）."
            )
        elif not official_basis_is_runtime_required(raw_text):
            majors.append(
                f"{official_route} 技能必须在 SKILL.md 的执行流程中要求读取 "
                f"`{OFFICIAL_BASIS_REF}`，不能只在 Resources 中列出 "
                f"({official_route} must require reading official-basis.md at runtime, "
                "not only list it as a resource)."
            )
        upstream_payload_refs = collect_upstream_payload_files(skill_dir)
        upstream_text_refs = sorted(collect_upstream_text_files(skill_dir))
        if upstream_text_refs:
            full_runtime_read = all(resource_is_runtime_required(raw_text, ref) for ref in upstream_text_refs)
            if not full_runtime_read:
                runtime_rules = skill_dir / RUNTIME_RULES_REF
                if not runtime_rules.exists():
                    majors.append(
                        f"{official_route} 技能包含完整上游源，但既未要求运行时全读 upstream，"
                        f"也缺少 `{RUNTIME_RULES_REF}` 渐进披露合同 "
                        f"({official_route} includes full upstream source files, but neither "
                        "requires full runtime upstream reads nor provides runtime-rules.md)."
                    )
                elif not runtime_rules_are_runtime_required(raw_text):
                    majors.append(
                        f"{official_route} 技能使用渐进披露时，SKILL.md 必须要求普通运行读取 "
                        f"`{RUNTIME_RULES_REF}` "
                        f"(progressive {official_route} runtime must require reading runtime-rules.md)."
                    )
                elif not runtime_rules_define_progressive_contract(skill_dir):
                    majors.append(
                        f"`{RUNTIME_RULES_REF}` 必须声明 ordinary runtime、maintenance/audit full-read、"
                        "references/upstream source map 与升级触发器 "
                        "(runtime-rules.md must define ordinary runtime, maintenance/audit "
                        "full-read, references/upstream source map, and escalation triggers)."
                    )
        upstream_non_doc_payload = {
            ref
            for ref in upstream_payload_refs
            if Path(ref).suffix.lower() not in DOC_SUFFIXES or "/scripts/" in ref or "/assets/" in ref
        }
        if upstream_non_doc_payload and not runtime_rules_define_payload_contract(skill_dir, upstream_payload_refs):
            majors.append(
                f"`{RUNTIME_RULES_REF}` 必须声明 upstream source tree 中 scripts/assets/templates/fixtures "
                "的角色，并说明它们是 operational projection、evidence_only 还是 blocked_until_projected "
                "(runtime-rules.md must classify upstream scripts/assets/templates/fixtures as "
                "operational projection, evidence_only, or blocked_until_projected)."
            )

    missing_declared = sorted(ref for ref in skill_declared_refs if not (skill_dir / ref).exists())
    for ref in missing_declared:
        majors.append(f"SKILL.md 声明了不存在的资源（Missing declared resource）: {ref}")

    orphan_resources = sorted(res for res in existing_resources if res not in skill_declared_refs)
    for res in orphan_resources:
        majors.append(f"存在未在 SKILL.md 声明的资源（Orphan resource）: {res}")

    ref_hits = scan_text_refs(skill_dir)
    for ref, files in sorted(ref_hits.items()):
        if (skill_dir / ref).exists():
            continue
        sample = ", ".join(sorted(files)[:3])
        extra_count = max(0, len(files) - 3)
        extra_suffix = f" ... +{extra_count}" if extra_count else ""
        majors.append(
            "检测到悬空路径引用（Dangling resource reference）: "
            f"{ref} <- {sample}{extra_suffix}"
        )

    line_count = raw_text.count("\n") + 1
    if line_count > 500:
        warns.append(
            f"SKILL.md 偏长（{line_count} 行），建议将细节拆到 references/ "
            "(SKILL.md is long; consider splitting details into references/)."
        )

    for bad in sorted(MAJOR_DOC_NOISE):
        if (skill_dir / bad).exists():
            warns.append(f"发现非必要文档（Non-essential document present）: {bad}")

    if not (skill_dir / "agents" / "openai.yaml").exists():
        warns.append("缺少 agents/openai.yaml（agents/openai.yaml is missing）.")

    status = "PASS" if not majors else "FAIL"
    print(f"{status}: {skill_dir}")

    if majors:
        print("\n重大问题（Major issues）:")
        for item in majors:
            print(f"- {item}")

    if warns:
        print("\n警告（Warnings）:")
        for item in warns:
            print(f"- {item}")

    return 0 if not majors else 1


if __name__ == "__main__":
    sys.exit(main())
