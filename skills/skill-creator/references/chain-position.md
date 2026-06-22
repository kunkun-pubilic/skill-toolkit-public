# Chain Position: skill-creator

```yaml
chain_id: skill-lifecycle
position: kun-create
consumes:
  - source card with route=kun-create
  - contracts/agent-skill-core.yaml
  - host contracts
  - kun-agent-registry upstream locks
produces:
  - new Kun-owned Skill scaffold
  - references/official-basis.md
  - references/pilot-closed-loop.md
  - optional agents/openai.yaml
handoff_status:
  - kun-create-created
  - blocked
  - needs-interview
next_skill:
  - skill-modify when the scaffold needs repair
  - skill-evolver after real use proves reusable deltas
must_not:
  - skip upstream research
  - create Plugin runtime bundles
  - claim official adoption without a locked source
  - promote a workflow Skill without explicit chain metadata
proof_surface:
  - scripts/create_skill.py output
  - quick_validate.py
  - audit_skill.py
```

Generated Skills default to `chain_id: standalone`. If a generated Skill belongs to a workflow, replace that default before registry promotion.
