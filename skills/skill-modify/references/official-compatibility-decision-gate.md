# Official Compatibility Decision Gate

Use this local gate before modifying, migrating, publishing, or importing any skill asset. This file is duplicated inside `skill-modify` so the skill can be installed and used on its own without a central router skill.

## Goal

Decide whether the asset should stay Kun-owned, wrap an official upstream, fork an upstream, vendor-copy a source, or remain reference-only.

Default policy:

- Skill is the atomic unit.
- GitHub repo is the durable source package.
- Plugin is exceptional and only used for runtime bundles: MCP, OAuth/app authorization, browser bridges, hooks, apps, or host-specific runtime integration.
- Active host targets are Codex and Claude Code.

## Decision Flow

1. Identify the asset name, purpose, proof surface, and runtime needs.
2. Check whether a primary-source upstream exists for the domain, host behavior, or lifecycle tool.
3. Choose source strategy:
   - `kun_owned`: no suitable upstream; Kun owns behavior and lifecycle.
   - `wrapper_overlay`: keep upstream clean; add Kun-specific routing, gates, or style.
   - `fork`: upstream is useful but long-lived behavior changes are required.
   - `vendor_copy`: absorb content when tracking upstream is not useful.
   - `reference_only`: study patterns but do not import.
4. Check host compatibility:
   - Codex: `.agents/skills`, `agents/openai.yaml`, plugin only for distribution/runtime.
   - Claude Code: `.claude/skills`, plugin skills, frontmatter extensions.
5. Apply Plugin exception test: MCP, OAuth/app authorization, browser bridge, hooks, app/widget runtime, or marketplace/cache semantics.
6. Record upstream, source strategy, host support, plugin need, proof surface, and registry/manifest update.

## Output Block

```text
Official compatibility:
- upstream: <none | url>
- source_strategy: <kun_owned | wrapper_overlay | fork | vendor_copy | reference_only>
- host_support: <Codex | Claude Code>
- plugin_needed: <no | yes, reason>
- proof_surface: <commands/files/browser/runtime>
- registry_update: <needed | not-needed>
```

## Import Rules

- Pin upstream by tag, commit SHA, or reviewed docs snapshot before importing. This is a current verified revision, not a permanent freeze.
- Do not bulk-import vendor skills into resident context.
- Treat community directories as discovery only until the primary source is verified.
- Keep Kun-specific policy in overlays or registry metadata rather than editing upstream content directly.
