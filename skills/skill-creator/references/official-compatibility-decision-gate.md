# Official Compatibility Decision Gate

Use this local gate before creating, modifying, migrating, publishing, or importing any skill asset. This file is duplicated inside `skill-creator` so the skill can be installed and used on its own without a central router skill.

## Goal

Decide whether the asset should stay Kun-owned, wrap an official upstream, fork an upstream, vendor-copy a source, or remain reference-only.

Default policy:

- Skill is the atomic unit.
- GitHub repo is the durable source package.
- GitHub repo, suite, and registry group are not callable facades by default.
- Plugin is exceptional and only used for runtime bundles: MCP, OAuth/app authorization, browser bridges, hooks, apps, or host-specific runtime integration.
- Active host targets are Codex and Claude Code.

## Official Upstream Map

| Upstream | Role | Use |
|---|---|---|
| `https://github.com/agentskills/agentskills` | Agent Skills open specification | Base format and progressive disclosure contract. |
| `https://developers.openai.com/codex/skills` | Codex skill behavior | Codex paths, description budget, plugins as distribution, `agents/openai.yaml`. |
| `https://github.com/openai/skills` | OpenAI Codex official catalog | Codex examples and curated/system skill patterns. |
| `https://code.claude.com/docs/en/skills` | Claude Code skill behavior | Claude paths, frontmatter extensions, live reload, plugin skills, `skillOverrides`. |
| `https://github.com/anthropics/skills` | Anthropic official skills | Skill authoring patterns and production document skill examples. |
| `https://github.com/vercel-labs/skills` | `npx skills` lifecycle tool | Install, use, list, find, update, remove, init, multi-agent path mapping. |
| `https://github.com/microsoft/skills` | Large governed skill estate | Acceptance criteria, scenarios, SDK/language skill packaging, MCP references. |
| `https://github.com/MicrosoftDocs/Agent-Skills` | Docs-to-skills pipeline | Microsoft Learn-derived skill generation and multi-agent compatibility. |
| `https://github.com/google/skills` | Google vendor skills | Google Cloud and Gemini skill reference. |
| `https://github.com/elastic/agent-skills` | Elastic vendor skills | Platform skill packaging, release/version/security posture. |
| `https://github.com/elastic/elastic-docs-skills` | Docs authoring skill system | SemVer, CI validation, freshness/source fields. |
| `https://github.com/greensock/gsap-skills` | Compact library skill pack | Focused framework/API skill structure and `llms.txt` index. |

## Decision Flow

1. Identify the asset:
   - name
   - purpose
   - target users
   - expected proof surface
   - runtime needs

2. Check upstream:
   - Is there an official upstream for the domain, host behavior, or lifecycle tool?
   - Is it primary-source and maintained by the vendor/platform?
   - Does its license and host assumption allow reuse?

3. Choose source strategy:
   - `kun_owned`: no suitable upstream; Kun owns behavior and lifecycle.
   - `wrapper_overlay`: keep upstream clean; add Kun-specific routing, gates, or style.
   - `fork`: upstream is useful but long-lived behavior changes are required.
   - `vendor_copy`: absorb content when tracking upstream is not useful.
   - `reference_only`: study patterns but do not import.

4. Check host compatibility:
   - Codex: `.agents/skills`, `agents/openai.yaml`, plugin only for distribution/runtime.
   - Claude Code: `.claude/skills`, plugin skills, frontmatter extensions.

5. Apply Plugin exception test:
   - Needs MCP server config?
   - Needs OAuth/app authorization?
   - Needs browser/desktop bridge?
   - Needs hooks or hosted app/widget runtime?
   - Needs marketplace/cache install semantics?

If all answers are no, keep it as a Skill repo/package.

6. Record outcome:
   - registry entry or project-local manifest
   - invocation policy: `atomic_skill=on_demand`, `group=install_only`, `group_callable=false`
   - compatibility matrix row when this is a shared asset
   - lockfile pin/ref when importing upstream content
   - verification commands
   - deletion-spec

## Output Block

```text
Official compatibility:
- upstream: <none | url>
- source_strategy: <kun_owned | wrapper_overlay | fork | vendor_copy | reference_only>
- host_support: <Codex | Claude Code>
- plugin_needed: <no | yes, reason>
- proof_surface: <commands/files/browser/runtime>
- invocation_policy: <on-demand | install-only | runtime-exception | user-requested-facade>
- registry_update: <needed | not-needed>
```

## Import Rules

- Pin upstream by tag, commit SHA, or reviewed docs snapshot before importing. This is a current verified revision, not a permanent freeze.
- Do not bulk-import vendor skills into resident context.
- Do not promote a repo, suite, or group to a callable route unless the runtime bundle or user request explicitly requires that facade.
- For multi-skill sources, create one reviewed source/overlay record per atomic skill and keep groups as install-only metadata.
- Treat community directories as discovery only until the primary source is verified.
- Keep Kun-specific policy in overlays or registry metadata rather than editing upstream content directly.
