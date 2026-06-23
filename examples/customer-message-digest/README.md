# Customer Message Digest Demo

This demo shows how public standalone mode can turn a repeated task into a Skill without using private customer material.

## Task

Turn a customer message sample into:

- a short summary;
- risks or blockers;
- follow-up tasks;
- a suggested reply.

## Public-Safe Sample Input

```text
Customer says the weekly report is hard to read. They want a shorter summary, a clear list of blockers, and next steps before Friday. They also ask whether the new dashboard can export CSV.
```

## Create The Skill

Run from the repository root:

```bash
python3 skills/skill-creator/scripts/create_skill.py customer-message-digest \
  --public-standalone \
  --target-root .agents/skills \
  --description "Use when the user needs to turn customer messages into a summary, risks, tasks, and reply suggestions." \
  --display-name "Customer Message Digest" \
  --short-description "Digest customer messages" \
  --default-prompt "Use customer-message-digest to process this customer message sample." \
  --proof-surface "sample transcript + quick_validate + audit_skill"
```

## Validate

```bash
python3 skills/skill-modify/scripts/quick_validate.py .agents/skills/customer-message-digest
python3 skills/skill-modify/scripts/audit_skill.py .agents/skills/customer-message-digest
```

## Boundary

This demo does not include real customer conversations, private project names, credentials, or local cache paths.
