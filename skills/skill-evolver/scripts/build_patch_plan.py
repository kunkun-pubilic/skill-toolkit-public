#!/usr/bin/env python3
"""
// Input: 目标 skill 目录 + 用户提出的能力 delta 文本 + 可选演化模式。
// Output: 带模式判断、影响地图与校验命令的确定性补丁计划 Markdown。
// Pos: skill-evolver/scripts - 编辑前的规划助手。
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


RESOURCE_REF_RE = re.compile(r"`((?:scripts|references|assets)/[^`]+)`")
SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)

DEFAULT_TOOLKIT_ROOT = Path(__file__).resolve().parents[3]
TOOLKIT_ROOT = Path(
    os.environ.get("KUN_SKILL_TOOLKIT_ROOT", str(DEFAULT_TOOLKIT_ROOT))
).expanduser().resolve()
SKILL_MODIFY_ROOT = TOOLKIT_ROOT / "skills" / "skill-modify"
QUICK_VALIDATE_PATH = SKILL_MODIFY_ROOT / "scripts" / "quick_validate.py"
PACKAGE_SKILL_PATH = SKILL_MODIFY_ROOT / "scripts" / "package_skill.py"


IMPACT_RULES = {
    "frontmatter.description": [
        "trigger",
        "use when",
        "when to use",
        "description",
        "triggering",
        "trigger phrase",
        "触发",
        "何时",
        "用于",
    ],
    "workflow.sections": [
        "workflow",
        "step",
        "gate",
        "flow",
        "process",
        "loop",
        "流程",
        "步骤",
        "校验",
    ],
    "references.routing": [
        "reference",
        "scenario",
        "large prompt",
        "long prompt",
        "variant",
        "prompt-heavy",
        "references/",
        "场景",
        "提示词",
    ],
    "scripts.deterministic": [
        "script",
        "audit",
        "validator",
        "check",
        "deterministic",
        "automation",
        "脚本",
        "检测",
        "验证",
    ],
    "self_evolution.harvest": [
        "conversation",
        "dialogue",
        "transcript",
        "retrospective",
        "retro",
        "harvest",
        "self-evolution",
        "self evolution",
        "prompt",
        "missed point",
        "post-call",
        "复盘",
        "对话",
        "沉淀",
        "回灌",
        "提示词",
        "未被注意",
    ],
}

MODE_KEYWORDS = {
    "conversation-harvest": [
        "conversation",
        "dialogue",
        "transcript",
        "retrospective",
        "harvest",
        "post-call",
        "prompt",
        "script opportunity",
        "复盘",
        "对话",
        "沉淀",
        "回灌",
        "提示词",
        "脚本机会",
        "未被注意",
    ],
    "new-requirement": [
        "new feature",
        "new capability",
        "extend",
        "repair",
        "fix flow",
        "新增",
        "新需求",
        "扩展",
        "加功能",
        "修复流程",
    ],
}


def read_change_text(change_text: str, change_file: str) -> str:
    if change_text and change_file:
        raise ValueError("`--change-text` 和 `--change-file` 只能二选一。")
    if not change_text and not change_file:
        raise ValueError("必须提供 `--change-text` 或 `--change-file` 之一。")
    if change_file:
        return Path(change_file).read_text(encoding="utf-8").strip()
    return change_text.strip()


def extract_sections(skill_md_text: str) -> list[str]:
    return [m.group(1).strip() for m in SECTION_RE.finditer(skill_md_text)]


def extract_resource_refs(skill_md_text: str) -> list[str]:
    seen: set[str] = set()
    refs: list[str] = []
    for match in RESOURCE_REF_RE.finditer(skill_md_text):
        ref = match.group(1).strip()
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)
    return refs


def infer_impacts(change_text: str) -> list[str]:
    lower_text = change_text.lower()
    impacts: set[str] = set()
    for impact, keywords in IMPACT_RULES.items():
        for keyword in keywords:
            if keyword in lower_text or keyword in change_text:
                impacts.add(impact)
                break
    if not impacts:
        impacts.add("workflow.sections")
    return sorted(impacts)


def infer_mode(change_text: str, explicit_mode: str) -> str:
    if explicit_mode != "auto":
        return explicit_mode

    lower_text = change_text.lower()
    scores: dict[str, int] = {}
    for mode, keywords in MODE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in lower_text or keyword in change_text:
                score += 1
        scores[mode] = score

    if scores.get("conversation-harvest", 0) > scores.get("new-requirement", 0):
        return "conversation-harvest"
    return "new-requirement"


def build_patch_tasks(mode: str, impacts: list[str]) -> list[str]:
    tasks: list[str] = []
    tasks.append("先读取现有 SKILL.md、相关 references、相关 scripts，确认应重写还是新增。")
    if "frontmatter.description" in impacts:
        tasks.append("重写 frontmatter description，保持触发精度。")
    if "workflow.sections" in impacts:
        tasks.append("先重写受影响的既有流程区块，再考虑新增区块。")
    if "references.routing" in impacts:
        tasks.append("将大体量场景提示词迁移到 references，并在 SKILL.md 增加精简路由。")
    if "scripts.deterministic" in impacts:
        tasks.append("新增或更新确定性检查脚本，并在 SKILL.md 写明入口命令。")
    if mode == "conversation-harvest" or "self_evolution.harvest" in impacts:
        tasks.append("从已完成对话中提炼可复用 prompts、漏检点与脚本机会，并给出资产分类。")
        tasks.append("将可复用提示沉淀到 references，将稳定重复步骤沉淀到 scripts；一次性内容明确忽略。")
    tasks.append("同步 SKILL.md 资源声明与实际文件。")
    tasks.append("运行验证命令并附上证据。")
    return tasks


def render_plan(
    skill_dir: Path,
    requested_delta: str,
    mode: str,
    sections: list[str],
    resource_refs: list[str],
    impacts: list[str],
    tasks: list[str],
) -> str:
    section_lines = "\n".join(f"- {name}" for name in sections) if sections else "- (none)"
    resource_lines = "\n".join(f"- `{ref}`" for ref in resource_refs) if resource_refs else "- (none)"
    impact_lines = "\n".join(f"- {item}" for item in impacts)
    task_lines = "\n".join(f"{idx}. {item}" for idx, item in enumerate(tasks, start=1))

    return (
        "# 增量补丁计划\n\n"
        f"## 目标 Skill\n\n- `{skill_dir}`\n\n"
        f"## 演化模式\n\n- `{mode}`\n\n"
        "## 请求 Delta\n\n"
        f"{requested_delta}\n\n"
        "## 现有章节地图\n\n"
        f"{section_lines}\n\n"
        "## 已声明资源地图\n\n"
        f"{resource_lines}\n\n"
        "## 影响地图\n\n"
        f"{impact_lines}\n\n"
        "## 最小补丁任务\n\n"
        f"{task_lines}\n\n"
        "## 验证命令\n\n"
        "```bash\n"
        f"python3 {QUICK_VALIDATE_PATH} {skill_dir}\n"
        f"python3 scripts/build_patch_plan.py --skill-dir {skill_dir} --change-text \"<演化描述>\" --mode {mode}\n"
        "python3 scripts/audit_incremental_update.py --before <baseline-skill-dir> "
        f"--after {skill_dir}\n"
        f"python3 {PACKAGE_SKILL_PATH} "
        f"{skill_dir} --output-dir <dist-dir>\n"
        "```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="为 skill 演化生成确定性补丁计划。")
    parser.add_argument("--skill-dir", required=True, help="目标 skill 目录路径。")
    parser.add_argument("--change-text", default="", help="能力 delta 文本。")
    parser.add_argument("--change-file", default="", help="包含能力 delta 的文本文件路径。")
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "new-requirement", "conversation-harvest"],
        help="演化模式；默认 auto，根据 delta 文本推断。",
    )
    parser.add_argument("--out", default="", help="可选：Markdown 输出路径。")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"未找到 SKILL.md: {skill_md}")

    requested_delta = read_change_text(args.change_text, args.change_file)
    if not requested_delta:
        raise SystemExit("能力 delta 为空。")

    skill_text = skill_md.read_text(encoding="utf-8")
    sections = extract_sections(skill_text)
    refs = extract_resource_refs(skill_text)
    impacts = infer_impacts(requested_delta)
    mode = infer_mode(requested_delta, args.mode)
    tasks = build_patch_tasks(mode, impacts)
    report = render_plan(skill_dir, requested_delta, mode, sections, refs, impacts, tasks)

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"已写入补丁计划: {out_path}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
