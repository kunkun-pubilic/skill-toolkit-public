# Pull Request

## Summary

-

## What changed

-

## Validation

- [ ] `python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py skills/skill-adopter/scripts/research_skill.py skills/skill-adopter/scripts/source_card_to_registry.py skills/skill-overlay/scripts/apply_overlay.py skills/skill-creator/scripts/create_skill.py skills/skill-evolver/scripts/build_patch_plan.py skills/skill-evolver/scripts/audit_incremental_update.py`
- [ ] `for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill" && python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"; done`
- [ ] Documentation updated when install steps, public boundaries, or behavior changed.

## Public boundary

- [ ] No secrets, tokens, private registry data, customer material, unpublished production assets, or private runtime cache paths are included.
- [ ] Any missing private context is described as an evidence gap instead of being copied into the public repo.

## Related issue

Refs #
