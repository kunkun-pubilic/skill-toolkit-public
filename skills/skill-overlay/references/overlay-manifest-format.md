# Overlay Manifest Format

An overlay manifest describes how to turn a pinned upstream Skill into a Kun-compatible project Skill without forking the upstream repository.

Durable manifests should be stored in `kun-agent-registry/overlay-catalog/`. Toolkit-local examples are only for smoke tests and authoring references.

## Minimal Example

```yaml
version: 1
route: official-overlay
source:
  url: https://github.com/vercel-labs/agent-skills.git
  ref: 4ec6f84b61cd3c931046c3e6e398f3ae7de372f7
  skill_path: skills/react-best-practices
target:
  skill_id: vercel-react-best-practices
  target_root: .agents/skills
overlay:
  normalize_frontmatter: true
  description: Short Kun-compatible trigger description under 500 characters.
  runtime_source_contract:
    ordinary_runtime: digest-plus-scoped-upstream
    runtime_rules: <target skill references dir>/runtime-rules.md
    maintenance_runtime: full-upstream-mirror
    full_read_triggers:
      - ambiguity
      - exact_upstream_behavior
      - upstream_update_review
      - license_or_provenance
      - user_requests_source
  move_files:
    - from: README.md
      to: <target skill references dir>/upstream-readme.md
  skill_markdown_replacements:
    - from: README.md
      to: <target skill references dir>/upstream-readme.md
  append_skill_markdown: |
    ## Overlay Resource Index

    - `<target skill references dir>/upstream-readme.md` for upstream reference context.

    ## Runtime Official Source Contract

    For ordinary runtime, read `<target skill references dir>/official-basis.md`
    and `<target skill references dir>/runtime-rules.md`.
    For maintenance, adoption, audit, upstream update review, license/provenance
    checks, exact upstream behavior, or unresolved ambiguity, read the scoped
    files under `<target skill references dir>/upstream/` before deciding.
    Treat upstream rules as inherited defaults; apply overlay rules only where
    this Skill explicitly narrows them.
  inject_skill_note: true
  official_basis: true
  openai_yaml:
    display_name: Vercel React Best Practices
    short_description: Vercel-maintained React and Next.js guidance with Kun compatibility metadata.
    default_prompt: Use $vercel-react-best-practices when writing, reviewing, or optimizing React/Next.js code.
```

## Required Fields

- `version`: currently `1`.
- `route`: must be `official-overlay`.
- `source.url`: Git URL or local path containing the upstream Skill.
- `source.ref`: commit, tag, or branch. Prefer commit SHA for reviewed adoption.
- `source.skill_path`: path to the upstream skill directory.
- `target.skill_id`: installed Skill directory and frontmatter name.

## Overlay Source Tree

Some Kun overlays are larger than a short frontmatter/resource compatibility note. In that case the manifest can keep the official upstream pin while replaying a reviewed Kun overlay Skill tree:

```yaml
source:
  url: https://github.com/official/upstream-skills.git
  ref: <reviewed-upstream-commit>
  skill_path: skills/upstream-suite
overlay_source:
  url: ../kun-paper-skills
  ref: <reviewed-kun-overlay-commit>
  skill_path: skills/paper-storyline-planner
overlay:
  replace_with_overlay_source_tree: true
  normalize_frontmatter: false
  preserve_overlay_source_skill_markdown: true
  inject_skill_note: false
  official_basis: false
```

Use this only when the Kun delta is already reviewed as a complete Skill tree. The generated lock records both upstream hashes and `overlay_source` hashes. For local scaffolds, keep registry status blocked or pending until the overlay source has a remote commit pin.

## Default Operations

- `normalize_frontmatter`: keep only `name` and `description` in `SKILL.md` frontmatter.
- `description`: optional replacement description for upstream Skills whose frontmatter route text is too long for Kun validation.
- `replace_with_overlay_source_tree`: replace the copied upstream Skill with the reviewed `overlay_source.skill_path` tree while preserving the upstream pin in the lock.
- `preserve_overlay_source_skill_markdown`: when replacing from `overlay_source`, keep the overlay Skill's `SKILL.md` bytes instead of re-dumping frontmatter.
- `move_files`: move root docs that Kun audit treats as noise into the target Skill references directory.
- `skill_markdown_replacements`: literal replacements applied to the generated `SKILL.md` body before writing.
- `append_skill_markdown`: markdown appended to the generated `SKILL.md`; use it for resource indexes and explicit script/reference declarations.
- If `append_skill_markdown` declares `references/upstream/*.md`, it must also declare whether ordinary runtime uses full upstream reads or progressive disclosure through the generated runtime-rules reference.
- `runtime_source_contract`: optional explicit source-read policy. Use `ordinary_runtime: digest-plus-scoped-upstream` with `runtime_rules` pointing to the generated runtime-rules reference for large upstream mirrors; use `ordinary_runtime: full-upstream-mirror` only when the upstream mirror is small enough to read every time.
- `inject_skill_note`: add a short provenance note to `SKILL.md`.
- `official_basis`: write generated official-basis and upstream-frontmatter reference files.
- `openai_yaml`: write `agents/openai.yaml`.

## Script And Asset Payload Policy

An upstream Skill is a source tree, not a Markdown page. Adoption review must
classify every important upstream payload:

- `rule_text`: `SKILL.md`, `README.md`, `references/*.md`, schemas, and docs
  that the model reads.
- `executable_script`: upstream scripts or CLIs that implement deterministic
  behavior.
- `runtime_asset`: images, templates, prompt packs, schemas, fixtures, examples,
  or media used by the Skill at runtime.
- `evidence_only`: upstream files kept only for audit, provenance, license, or
  update review.
- `blocked_until_projected`: upstream files needed for behavior but not yet
  safely projected into local `scripts/` or `assets/`.

Do not execute scripts directly from `references/upstream/`. If an upstream
script is part of the adopted behavior, copy or generate a reviewed local
projection under `scripts/`, record its upstream path/hash in the lock or
official-basis, and validate it with the target repo checker. Runtime assets
follow the same rule: usable assets live under `assets/`; evidence-only upstream
assets may stay under `references/upstream/`.

If a manifest uses `replace_with_overlay_source_tree`, the upstream source pin
is still not enough. Any upstream script or asset that materially controls
behavior must be mirrored, projected, or explicitly marked
`blocked_until_projected`.

## Promotion Rule

A generated Skill may be promoted from `overlay_needed` to `adopted` only after:

- the manifest pins a reviewed upstream ref;
- the generated `skills-lock.json` records source and installed tree SHA-256 values, including scripts and assets;
- `official-basis.md` or `runtime-rules.md` records the role of important upstream scripts/assets;
- the generated Skill passes `quick_validate.py`;
- the generated Skill passes `audit_skill.py`, or the registry explicitly records a validator policy exception.
