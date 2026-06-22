# Contributing

Thanks for improving Skill Toolkit Public Pack. This repository is a public standalone extraction, so contributions should help people understand, install, validate, or adapt the five lifecycle Skills without depending on Kun's private registry.

## What to contribute

- README, docs, diagrams, screenshots, and examples that make the toolkit easier to understand.
- Fixes to public Skill instructions, references, or scripts.
- Validation improvements for `skills/` and `contracts/`.
- Small examples showing how to create, adopt, overlay, repair, or evolve an Agent Skill.

## Public boundary

Do not include:

- API keys, tokens, private keys, or account credentials.
- Private organization registry data or local runtime lock files.
- Raw footage, unpublished production materials, Feishu/Lark workspace exports, or customer project material.
- Private cache paths or machine-specific setup details unless they are clearly anonymized.

If a useful change depends on private context, describe the public behavior and record the missing private evidence as an evidence gap.

## Issue flow

Before opening an issue:

1. Check existing issues and docs.
2. State the expected behavior and the current behavior.
3. Include the affected path, command, or Skill name.
4. Add a small reproduction case when possible.

Good issue titles are concrete, for example:

- `skill-modify quick_validate misses missing agents/openai.yaml`
- `README quick start should include Claude Code install path`
- `Add lifecycle diagram for adopter -> overlay -> creator -> modify -> evolver`

## Pull request flow

1. Keep the change focused.
2. Update docs when behavior, install steps, or public boundaries change.
3. Run the validation commands below.
4. In the PR description, include what changed, how you verified it, and any known evidence gaps.

## Validation

From the repository root, compile the bundled Python scripts:

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py
python3 -m py_compile skills/skill-adopter/scripts/research_skill.py
python3 -m py_compile skills/skill-adopter/scripts/source_card_to_registry.py
python3 -m py_compile skills/skill-overlay/scripts/apply_overlay.py
python3 -m py_compile skills/skill-creator/scripts/create_skill.py
python3 -m py_compile skills/skill-evolver/scripts/build_patch_plan.py
python3 -m py_compile skills/skill-evolver/scripts/audit_incremental_update.py
```

Then validate each Skill package:

```bash
for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do
  python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill"
  python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"
done
```

If a command cannot run in your environment, explain why and include the exact error output.

## Documentation style

- Prefer practical examples over abstract claims.
- Keep private Kun-internal workflow details out of public docs.
- Use clear links between README, docs, examples, and visual assets.
- When adding generated images or screenshots, commit the final asset file and reference it from the README or docs.
