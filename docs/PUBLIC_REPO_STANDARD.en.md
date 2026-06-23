# Public Repository Standard

This standard is used by Skill Toolkit Public Pack and can be reused for future Kun public resource repositories.

The goal is simple: a first-time GitHub visitor should quickly understand what the repository does, how to install and verify it, and what is intentionally outside the public boundary.

## README First Screen

The first screen should include:

- Positioning: a public standalone Skill lifecycle toolkit.
- Audience: Codex / Claude Code users who want to turn repeated work into reusable Skills.
- Value: create, adopt, overlay, repair, and evolve Agent Skills.
- Quick start: clone, install into `.agents/skills` or `.claude/skills`, run validation.
- Boundary: no private registry, cache, customer material, credentials, or unpublished video assets.

## Bilingual Rule

- Chinese is primary: `README.md` carries the first screen and complete install path.
- English is secondary: `README.en.md` provides a searchable and shareable entry point.
- English can be shorter, but it must still include installation, validation, and public boundary notes.

## Install Rule

Public repositories should assume a clean user environment: no Kun private registry, no private cache, and no need to understand internal governance first.

Public repositories should provide:

- Codex project install into `.agents/skills`.
- Claude Code project install into `.claude/skills`.
- A public standalone creation path when creation scripts are included.

Every install path needs a validation command.

## Example Rule

Keep at least one public-safe demo:

- no customer material, secrets, private paths, unpublished video assets, or local cache;
- a task that a new reader can understand;
- clear input, output, boundary, validation, and agent prompt.

## Image Asset Rule

Public repositories should include the images needed by the README:

- logo;
- banner;
- social preview candidate;
- workflow diagram;
- demo image;
- maintainable sources such as SVG and Mermaid.

Video assets and GIFs are out of scope for this pass. Keep an `assets/README.md` that explains source, generation, and boundary.

## Discoverability

Recommended GitHub description:

```text
Public standalone Skill lifecycle toolkit for creating, adopting, overlaying, repairing, and evolving Agent Skills across Codex and Claude Code.
```

Recommended topics:

```text
agent-skills, skill-md, codex, claude-code, ai-agents, prompt-engineering, workflow, developer-tools, skills, skill-creator
```

## Acceptance Checklist

- [ ] README explains positioning, audience, install, validation, and boundary.
- [ ] Chinese primary docs and English support docs both exist.
- [ ] At least one public-safe demo exists.
- [ ] README first screen does not make private registry knowledge an install requirement.
- [ ] Logo, banner, social preview, workflow diagram, and demo image exist.
- [ ] No video assets are included.
- [ ] GitHub description and topics are search-friendly.
- [ ] Validation commands run from the public repository root.
