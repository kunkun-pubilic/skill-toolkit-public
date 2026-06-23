# Skill Toolkit Public Pack

中文为主：[README.zh-CN.md](README.zh-CN.md)

This repository is a public, standalone Skill lifecycle toolkit for creating, adopting, overlaying, repairing, and evolving Agent Skills across Codex and Claude Code.

It comes from Kun's video about building reusable Agent Skills. The pack is not a prompt collection. It is a small workflow for turning repeated work into installable, auditable `SKILL.md` interfaces.

## What Is Inside

| Path | Purpose |
|---|---|
| `skills/skill-adopter` | Research official or mature upstream Skills before creating anything new. |
| `skills/skill-overlay` | Add a small compatibility layer on top of a pinned upstream Skill. |
| `skills/skill-creator` | Create a new Skill only when no suitable upstream exists. |
| `skills/skill-modify` | Repair trigger, structure, resource, and validation problems in existing Skills. |
| `skills/skill-evolver` | Turn proven real-use improvements into reusable Skill deltas. |
| `contracts/` | Public contracts for Agent Skill structure, Codex compatibility, Claude Code compatibility, and validation gates. |
| `WORKFLOW.md` | The lifecycle state machine for the five public Skills. |
| `skill-registry.yaml` | Public inventory and suggested install order. |

Kun's private registry is not included. When private tooling is unavailable, use public standalone mode and record missing evidence as an evidence gap.

## Quick Start

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public
```

Install into a Codex project:

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.agents/skills/"
```

Install into a Claude Code project:

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.claude/skills/"
```

Validate this public pack:

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py skills/skill-adopter/scripts/research_skill.py skills/skill-adopter/scripts/source_card_to_registry.py skills/skill-overlay/scripts/apply_overlay.py skills/skill-creator/scripts/create_skill.py skills/skill-evolver/scripts/build_patch_plan.py skills/skill-evolver/scripts/audit_incremental_update.py
for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill" && python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"; done
```

## Use It With An Agent

Paste this into Codex or Claude Code from a project that has the Skills installed:

```text
Use the Skill Toolkit in this project. Read skill-registry.yaml and WORKFLOW.md first. For Skill adoption, overlay, creation, repair, or evolution, call the smallest matching Skill from skills/skill-adopter, skills/skill-overlay, skills/skill-creator, skills/skill-modify, and skills/skill-evolver. If private registry or local tooling is missing, continue in public standalone mode and record the gap explicitly.
```

## Docs

- Chinese overview: [README.zh-CN.md](README.zh-CN.md)
- English quick start: [docs/QUICK_START.en.md](docs/QUICK_START.en.md)
- Chinese quick start: [docs/QUICK_START.zh-CN.md](docs/QUICK_START.zh-CN.md)
- Lifecycle workflow: [docs/SKILL_LIFECYCLE.zh-CN.md](docs/SKILL_LIFECYCLE.zh-CN.md)
- Public edition boundary: [docs/PUBLIC_EDITION_NOTES.en.md](docs/PUBLIC_EDITION_NOTES.en.md) / [中文](docs/PUBLIC_EDITION_NOTES.zh-CN.md)
- Public repository standard: [docs/PUBLIC_REPO_STANDARD.en.md](docs/PUBLIC_REPO_STANDARD.en.md) / [中文](docs/PUBLIC_REPO_STANDARD.zh-CN.md)
- Visual asset proposal: [docs/VISUAL_ASSET_PLAN.en.md](docs/VISUAL_ASSET_PLAN.en.md) / [中文](docs/VISUAL_ASSET_PLAN.zh-CN.md)
- Minimal demo: [examples/customer-message-digest](examples/customer-message-digest)

## Community

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing](CONTRIBUTING.md)
- [License](LICENSE)
- [Security](SECURITY.md)
- [Issue template](.github/ISSUE_TEMPLATE/skill_toolkit_issue.yml)
- [Pull request template](.github/pull_request_template.md)

License: MIT.
