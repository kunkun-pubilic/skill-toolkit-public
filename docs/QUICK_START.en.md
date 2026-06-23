# Quick Start

This guide assumes a clean user environment. You do not need Kun's private tooling or local cache. Installation means copying the five public Skills into your project.

## 1. Clone

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public
```

## 2. Install Into Codex

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.agents/skills/"
```

## 3. Install Into Claude Code

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.claude/skills/"
```

## 4. Validate This Repository

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py skills/skill-adopter/scripts/research_skill.py skills/skill-adopter/scripts/source_card_to_registry.py skills/skill-overlay/scripts/apply_overlay.py skills/skill-creator/scripts/create_skill.py skills/skill-evolver/scripts/build_patch_plan.py skills/skill-evolver/scripts/audit_incremental_update.py

for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do
  python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill"
  python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"
done
```

## 5. Create A Public Standalone Skill

```bash
python3 skills/skill-creator/scripts/create_skill.py customer-message-digest \
  --public-standalone \
  --target-root .agents/skills \
  --description "Use when the user needs to turn customer messages into a summary, risks, tasks, and reply suggestions." \
  --display-name "Customer Message Digest" \
  --short-description "Digest customer messages" \
  --default-prompt "Use customer-message-digest to process this customer message sample." \
  --proof-surface "sample transcript + quick_validate + audit_skill"
```

Then validate the generated Skill:

```bash
python3 skills/skill-modify/scripts/quick_validate.py .agents/skills/customer-message-digest
python3 skills/skill-modify/scripts/audit_skill.py .agents/skills/customer-message-digest
```
