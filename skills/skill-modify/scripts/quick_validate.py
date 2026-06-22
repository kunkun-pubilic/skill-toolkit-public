#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 500


def load_gate_result_helper() -> object:
    for candidate in Path(__file__).resolve().parents:
        helper = candidate / "scripts" / "gate_result.py"
        if helper.is_file():
            sys.path.insert(0, str(helper.parent))
            import gate_result

            return gate_result
    return None


gate_result = load_gate_result_helper()


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    allowed_properties = {
        "name",
        "description",
        "license",
        "allowed-tools",
        "metadata",
        "compatibility",
    }

    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        allowed = ", ".join(sorted(allowed_properties))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"Name is too long ({len(name)} characters). "
                f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
            )

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > MAX_DESCRIPTION_LENGTH:
            return (
                False,
                "Description is too long "
                f"({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH} characters. "
                "Keep only trigger conditions, trigger keywords, and negative boundaries; move workflow details to the body or references/.",
            )

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            return (
                False,
                f"Compatibility must be a string, got {type(compatibility).__name__}",
            )
        if len(compatibility) > 500:
            return (
                False,
                "Compatibility is too long "
                f"({len(compatibility)} characters). Maximum is 500 characters.",
            )

    return True, "Skill is valid!"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit gate_result_v1 JSON")
    parser.add_argument("skill_directory", help="Skill directory containing SKILL.md")
    args = parser.parse_args()

    skill_dir = Path(args.skill_directory).resolve()
    valid, message = validate_skill(skill_dir)

    if args.json_output:
        if gate_result is None:
            print("SKILL_QUICK_VALIDATE: error gate_result helper missing: scripts/gate_result.py")
            return 2
        repo_root = gate_result.find_repo_root(Path(__file__))
        registry_entry = gate_result.gate_registry_entry("SKILL_QUICK_VALIDATE", repo_root)
        status = "pass" if valid else "block"
        blocks_closure, blocks_dispatch = gate_result.blocking_flags("SKILL_QUICK_VALIDATE", status, repo_root)
        check = gate_result.make_check(
            "skill-frontmatter",
            status,
            message,
            refs=[str(skill_dir / "SKILL.md")],
            fix_hint_zh=None if valid else "修复 SKILL.md frontmatter、name/description 或文件位置后重跑 quick_validate。",
            repair_route=None if valid else "skill-toolkit:skill-modify",
            suggested_command=None if valid else f"python3 {Path(__file__).as_posix()} --json {skill_dir.as_posix()}",
        )
        gate_result.emit_json(
            gate_result.build_gate_result(
                gate_id="SKILL_QUICK_VALIDATE",
                status=status,
                summary_zh="Skill 快速校验通过。" if valid else f"Skill 快速校验阻断：{message}",
                scope={"kind": "skill_directory", "path": str(skill_dir)},
                checks=[check],
                blocks_closure=blocks_closure,
                blocks_dispatch=blocks_dispatch,
                trace_refs=[str(skill_dir / "SKILL.md")],
                grading_refs=registry_entry.get("grading_refs", []),
            )
        )
    else:
        print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
