# Skill Toolkit Public Pack

[中文主入口](README.md) · [Quick Start](docs/QUICK_START.en.md) · [Public Boundary](docs/PUBLIC_EDITION_NOTES.en.md)

Skill Toolkit Public Pack turns repeated work into Agent Skills that Codex and Claude Code can call.

This repository assumes a clean user environment. You do not need Kun's private tooling or local cache. Copy the five public lifecycle Skills into your project, then ask your agent to use them when needed.

## Install

Codex:

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public

PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.agents/skills/"
```

Claude Code:

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public

PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.claude/skills/"
```

## Included Skills

| Skill | Use when |
|---|---|
| `skill-adopter` | Research and adopt official or mature upstream Skills. |
| `skill-overlay` | Add a small compatibility layer on top of a pinned upstream Skill. |
| `skill-creator` | Create a new Skill only when no suitable upstream exists. |
| `skill-modify` | Repair triggers, structure, resources, or validation gaps in existing Skills. |
| `skill-evolver` | Turn proven real-use improvements into reusable Skill deltas. |

## Workflow

![Skill lifecycle workflow](assets/workflow/skill-lifecycle-workflow.png)

## Demo

![Customer Message Digest Demo](assets/demo/customer-message-digest-demo.png)

See [examples/customer-message-digest](examples/customer-message-digest).

## Validate

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py skills/skill-adopter/scripts/research_skill.py skills/skill-adopter/scripts/source_card_to_registry.py skills/skill-overlay/scripts/apply_overlay.py skills/skill-creator/scripts/create_skill.py skills/skill-evolver/scripts/build_patch_plan.py skills/skill-evolver/scripts/audit_incremental_update.py

for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do
  python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill"
  python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"
done
```

## Public Boundary

This public pack does not include Kun's private registry, private upstream locks, local runtime cache, customer material, credentials, unpublished video assets, or `plugin-manager`.

`skill-registry.yaml` is only a repository inventory. It is not required for installation.
