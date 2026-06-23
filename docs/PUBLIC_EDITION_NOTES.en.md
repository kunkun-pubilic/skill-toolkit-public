# Public Edition Notes

This repository is the public edition of Skill Toolkit. It is not a full mirror of Kun's private governance system.

The public edition assumes a clean user environment. Users can copy the five public Skills into a Codex or Claude Code project without Kun's private tooling.

## Included

- Five lifecycle Skills:
  - `skill-adopter`
  - `skill-overlay`
  - `skill-creator`
  - `skill-modify`
  - `skill-evolver`
- Local scripts for adoption, overlay, creation, validation, audit, and evolution.
- `contracts/` for public Skill structure and host compatibility.
- `WORKFLOW.md` and `skill-registry.yaml`.

## Not Included

- Kun's private `kun-agent-registry`.
- Private upstream locks.
- Local `.agents` / `.claude` cache.
- Customer material, credentials, private meeting notes, or unpublished video assets.
- `plugin-manager`, because runtime/plugin distribution has a different public boundary.

## Standalone Mode

For normal public users:

- continue in public standalone mode;
- use `skill-creator --public-standalone` for local creation;
- do not pretend that Kun's private registry is installed;
- connect your own registry or lockfile later if you have one.

The public edition keeps the lifecycle method and the reusable Skills. It does not publish Kun's private registry, local cache, or customer/project history.
