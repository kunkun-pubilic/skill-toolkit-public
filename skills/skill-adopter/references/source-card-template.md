# Source Card Template

Use this format after upstream research and before adoption.

```text
Decision: official-adopt | official-overlay | kun-modify | kun-create | blocked | needs-review
Reason: <one sentence>
Query: <user request or search query>
Lifecycle task: new-skill | modify-skill | migrate-old-skill | migrate-old-plugin | adopt-upstream | update-upstream
Legacy asset: <path or none>
Generated at: <UTC timestamp>
```

## Chain Contract

Use `chain_id: standalone` when the capability is independent. If it is one step in a workflow, fill this before adoption or creation.

```yaml
chain_id: <workflow id or standalone>
position: <this step's role>
consumes:
  - <upstream artifact>
produces:
  - <downstream artifact>
handoff_status:
  - <ready/needs/block status>
next_skill:
  - <downstream skill or none>
must_not:
  - <boundary this skill must not cross>
proof_surface:
  - <command, file, lock, or runtime proof>
```

Chat history may explain the decision, but it is not a proof surface.

## Repo State Machine

Use this block before adopting, overlaying, or creating any suite, old plugin, or multi-skill repository.

```yaml
repo_type: standalone_skill | composite_skill_repo | runtime_repo
workflow_id: <repo workflow id or standalone>
state_machine_required: true | false
state_machine_doc: WORKFLOW.md | runtime_lifecycle | none
artifact_gates:
  - <non-empty gate>
proof_surfaces:
  - <checker/file/runtime proof>
registry_handoff: <workflow_index entry or none>
```

`composite_skill_repo` requires `WORKFLOW.md` before the repo can be marked workflow-ready. `runtime_repo` may use `runtime_lifecycle`, but must still expose install/check/distribution/rollback proof. `standalone_skill` may use `chain-position`.

## Invocation Policy

Use this block whenever a source repo, old plugin, or suite contains more than one capability. Keep groups install-only unless a runtime bundle or explicit user request requires a facade.

```yaml
atomic_skill: on_demand
installability: <single-skill | group-install-only | runtime-preflight-sensitive | blocked>
group_callable: false
facade: <blocked | runtime-exception | user-requested>
```

## Capability Map

| Capability | Upstream Path | Source Strategy | Installability | Invocation Policy | Proof Surface |
|---|---|---|---|---|---|
| <real ability> | <repo path or old skill path> | official-adopt/official-overlay/kun-modify/kun-create/archive/defer | single-skill/group-install-only/runtime-preflight-sensitive/blocked | on-demand/install-only/runtime-exception/user-requested-facade | validator/smoke/lock/manual-review |

## Need Decomposition

| Need | Legacy Evidence | Search Query | Must Have | Nice To Have |
|---|---|---|---|---|
| <real capability, not old skill name> | <old skill/plugin path, user request, or transcript> | <DOKO/GitHub query> | <hard requirement> | <optional fit> |

## Candidate Summary

| Rank | Source | Skill | Source Tier | Coverage | Health | Evidence | Suggested Route |
|---|---|---|---|---|---|---|---|
| 1 | <repo/url> | <skill> | tier0-official/tier1-mature/tier2-community/unknown | exact/partial/adjacent/gap | <stars/forks/issues/license/archived/latest push/latest update/canonical repo> | <marketplace installs, docs, community lead, SKILL.md path> | official-adopt/official-overlay/kun-modify/kun-create/needs-review |

`Health` is a gate, not a replacement for reading source. A community repo is not `tier1-mature` unless it has a clear reuse license, recent maintenance, and real adoption signals. `updatedAt` alone is weak because stars, issue comments, or metadata can change it; prefer `pushedAt` for code maintenance.

## Freshness Gate

For nontrivial adoption, migration, modification, or replacement tasks, run DOKO local research before adoption planning. Cover stable upstream evidence and recent community signal:

- stable upstream: official docs, GitHub repo, candidate `SKILL.md`, license, commit/tag/release evidence.
- recent signal: last 30 days web, X/Twitter, Reddit, Hacker News, YouTube, GitHub issues/discussions/PRs, and AI skill community/marketplace pages.
- source conflict: record the disagreement and look for a tiebreaker from commit history, issue/PR discussion, release notes, or official docs.
- evidence gap: if login, anti-bot, unavailable local browser, or unreadable page blocks DOKO, record the scoped gap instead of treating it as absence of discussion.

## Source Tier Guide

- `tier0-official`: platform or vendor maintained source, such as OpenAI, Anthropic, Vercel, Microsoft, Google, or the direct product owner.
- `tier1-mature`: high-maintenance upstream with clear reuse license, recent pushed code, broad adoption, and cross-host support.
- `tier2-community`: useful lead only; do not adopt until `SKILL.md`, license, maintenance, and compatibility are reviewed.
- `unknown`: insufficient evidence.

## Verification Checklist

- `SKILL.md` was read, not only README/search result.
- `scripts/`, `references/`, and `assets/` were checked for runtime or security implications.
- Maintainer/source reputation was checked with GitHub health: stars, forks, open issues, license, archived/disabled state, default branch, latest push, latest update, and canonical repo redirect.
- License or reuse boundary was checked when available.
- Commit/tag/tree hash can be locked.
- Install target is clear: `.agents/skills`, `.claude/skills`, or both.
- DOKO local research was run before adoption planning for nontrivial new, modify, migration, or replacement tasks with `dokobot read --local <url>` across general web, recent 30-day web, X/Twitter, Reddit, Hacker News, YouTube, GitHub issues/discussions/PRs, and focused AI skill community sources; remote `dokobot search` API-key failure is not proof that DOKO local is unavailable.
- X/Twitter, Reddit, and marketplace/community hits were treated as discovery leads only; adoption still requires repo/SKILL.md/license/maintenance review.
- Old local Skill/Plugin content was treated as need evidence, not as the source of truth.
- Coverage was judged against the real capability need, not only the old asset name.
- Chain contract is marked `standalone` or records consumed artifact, produced artifact, handoff status, next skill, boundary, and proof surface.
- Repo state machine is marked `standalone_skill`, `composite_skill_repo`, or `runtime_repo`.
- Composite repos have `WORKFLOW.md` or an explicit blocker; runtime repos have `runtime_lifecycle` proof.
- Multi-skill repos/suites were decomposed into atomic capabilities.
- Registry groups are marked install-only and `group_callable=false`.

## Recommendation

```text
Route:
Install command:
Adoption command:
Overlay needed:
Keep Kun gap skill:
Registry fields:
Chain contract:
Repo state machine:
Invocation policy:
Risks:
```
