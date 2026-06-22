---
name: skill-overlay
description: 当上游官方或可信 Agent Skill 基本可用但需要 Kun/Codex/Claude 兼容层时使用。触发关键词：official-overlay / overlay skill / 给官方 skill 加兼容层 / 上游 skill 二次封装。不用于从零创建 skill。
---

# Skill Overlay

## Role

Use this skill after `skill-adopter` has proven that an upstream Skill can be fetched and pinned, but raw adoption does not meet Kun runtime policy.

The goal is to keep the upstream update path intact while applying a small replayable compatibility layer. Do not silently edit a copied upstream Skill by hand.

## Public Edition Note

In this public edition, an overlay can target any pinned public Git repository or local upstream Skill directory. If a private registry is unavailable, keep the overlay manifest, generated `references/official-basis.md`, and local `skills-lock.json` as the proof surface. Do not claim organization-level registry promotion unless the user has actually added one.

## Method

```text
/skill-overlay(manifest, target_root?, lock_file?)
```

## Flow

1. Read `references/official-basis.md`, then read the overlay manifest and confirm the pinned upstream source, ref, and skill path.
2. Run `scripts/apply_overlay.py`.
3. Verify the generated Skill with `quick_validate.py` and `audit_skill.py`.
4. If validation passes, record the generated `skills-lock.json` evidence in the registry.
5. If validation fails, classify the failure as `overlay_manifest_gap`, `upstream_policy_gap`, or `validator_policy_gap`; do not mark the Skill adopted.
6. If the Skill participates in a workflow chain, confirm the overlay adds or preserves an explicit Chain Position: consumed artifacts, produced artifacts, handoff status, next Skill, hard boundaries, and proof surface.
7. If the overlay target is a composite skill repository, confirm repo-level `WORKFLOW.md` exists or add it as part of the overlay contract before marking the repo workflow-ready.

## Overlay Boundary

Allowed default overlay changes:

- normalize `SKILL.md` frontmatter to Kun-compatible `name` and `description`;
- preserve original vendor frontmatter in a generated upstream frontmatter reference;
- move upstream root `README.md` into a generated upstream README reference;
- create a generated official-basis reference;
- create `agents/openai.yaml`;
- insert a short Kun overlay note that makes the official-basis reference a runtime read requirement, not only provenance metadata.
- when the overlay includes `references/upstream/` source-tree mirrors, keep those files as the maintenance/adoption/audit proof source.
- preserve or explicitly project important upstream `scripts/`, `assets/`, templates, schemas, and fixtures when they are part of the upstream capability.
- copy executable/runtime payloads into local `scripts/` or `assets/` only when the overlay intends to use them; otherwise mark them as evidence-only source-tree payloads.
- for ordinary runtime, use progressive disclosure: read the generated official-basis reference plus generated runtime-rules reference; read scoped upstream files only when the runtime rules say the task crosses an uncertainty, exact upstream behavior, update, license/provenance, or user-requested source boundary.

Not allowed by default:

- rewriting the upstream rule content;
- deleting upstream scripts, references, or assets without evidence;
- changing behavior to satisfy Kun taste rather than runtime compatibility;
- pretending an overlayed Skill is still raw upstream.
- hiding workflow handoff rules in prose only. Chain member Skills need explicit artifacts, statuses, next Skill, boundaries, and proof surface.
- claiming `official-overlay` when `SKILL.md` does not require reading the generated official-basis reference at runtime.
- keeping full upstream source mirrors under `references/upstream/` without either a full-runtime read requirement or a progressive runtime contract that points ordinary runtime to the generated runtime-rules reference and maintenance/adoption/audit to full upstream reads.
- treating the generated runtime-rules reference as a summary replacement for upstream. It is only an executable ordinary-runtime extraction with source mapping and full-read escalation triggers.
- treating scripts or assets hidden under `references/upstream/` as operational runtime dependencies. Evidence mirrors are read/inspected; operational code and media must be projected into local `scripts/` / `assets/` with lock/hash evidence.
- claiming a composite repository is workflow-ready by adding only single-skill chain metadata. Repo-level `WORKFLOW.md` is required for composite skill repos.

## Commands

Durable manifests live in `kun-agent-registry/overlay-catalog/`. This skill does not keep demo overlay manifests as local source truth.

Apply an overlay manifest:

```bash
python3 scripts/apply_overlay.py <kun-agent-registry>/overlay-catalog/<skill-id>.overlay.yaml \
  --target-root .agents/skills \
  --lock-file skills-lock.json \
  --force
```

Manifest format is documented in `references/overlay-manifest-format.md`.

## Output Contract

```text
route: official-overlay
source: <repo/url/ref/skill_path>
installed: <target skill dir>
overlay: <manifest path and applied operations>
lock: <skills-lock.json tree/file hashes>
source_tree_payload: <docs/scripts/assets/templates/fixtures inventory and role>
operational_projection: <local scripts/assets copied or blocked/evidence-only>
chain: standalone | <chain_id/position/consumes/produces/handoff_status/next_skill/proof_surface>
state_machine: standalone | WORKFLOW.md | runtime_lifecycle
validation: <quick_validate/audit result>
next: adopted | registry-update | blocked
```

## Resources

- `scripts/apply_overlay.py`: replay an official-overlay manifest.
- `references/overlay-manifest-format.md`: manifest schema and promotion rules.

## Deletion Spec

- Trigger: official tools support pinned upstream Skill install plus replayable host-specific overlays and lock evidence.
- Disable: delete `skills/skill-overlay/` and remove it from `skill-registry.yaml`.
- Cleanup: migrate existing overlay manifests and lock records to the official replacement first.
