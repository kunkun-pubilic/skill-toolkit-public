# Visual Asset Plan

Status: `needs-review`

This plan lists the video, workflow diagram, demo, and GIF assets planned for the public repository. Final media files are not added yet; they should be reviewed first.

## Proposed Assets

| Asset | Path | Purpose | Source | Status |
|---|---|---|---|---|
| Workflow diagram | `assets/workflow/skill-lifecycle-workflow.png` | Explain the five lifecycle Skills in README and docs | Redrawn from `WORKFLOW.md` | `needs-review` |
| Mermaid source | `assets/workflow/skill-lifecycle-workflow.mmd` | Keep an editable source for the diagram | Extracted from `WORKFLOW.md` | `needs-review` |
| Demo GIF | `assets/demo/customer-message-digest-demo.gif` | Show public standalone mode from need to validation | Re-recorded from the demo directory with no customer material | `needs-review` |
| Video cover | `assets/video/skill-toolkit-video-cover.jpg` | Link the repository to the published video | Final public video cover or approved repo cover | `needs-review` |
| Video asset notes | `assets/video/README.md` | Record source, permission, and chapter mapping | Prepared after video publish details are confirmed | `needs-review` |

## Demo Scope

The demo uses `examples/customer-message-digest`:

1. Read input, output, boundary, and validation requirements.
2. Run `skill-creator --public-standalone`.
3. Run `quick_validate.py` and `audit_skill.py`.
4. Show the generated `SKILL.md` highlights.

No real customer messages are used.
