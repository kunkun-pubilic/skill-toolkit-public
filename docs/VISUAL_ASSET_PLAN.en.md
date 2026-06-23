# Image Asset Plan

Status: `implemented`

This plan now covers image assets only. Video assets and GIFs are out of scope for this pass.

## Proposed Assets

| Asset | Path | Purpose | Source | Status |
|---|---|---|---|---|
| Logo | `assets/brand/logo.png` / `.svg` | Repository identity | Local script | `done` |
| Banner | `assets/brand/banner.png` / `.svg` | README first screen | Local script | `done` |
| Social preview | `assets/brand/social-preview.png` / `.svg` | Candidate GitHub social image | Local script | `done` |
| Workflow diagram | `assets/workflow/skill-lifecycle-workflow.png` / `.svg` | Explain the five lifecycle Skills in README | Local script | `done` |
| Mermaid source | `assets/workflow/skill-lifecycle-workflow.mmd` | Editable workflow source | Local script | `done` |
| Demo image | `assets/demo/customer-message-digest-demo.png` / `.svg` | Show public standalone mode | Local script | `done` |

## Demo Scope

The demo uses `examples/customer-message-digest`:

1. Read input, output, boundary, and validation requirements.
2. Run `skill-creator --public-standalone`.
3. Run `quick_validate.py` and `audit_skill.py`.
4. Show the generated `SKILL.md` highlights.

No real customer messages are used.
