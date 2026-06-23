# Image Asset Plan

Status: `implemented`

This plan now covers image assets only. Video assets and GIFs are out of scope for this pass.

## Proposed Assets

| Asset | Path | Purpose | Source | Status |
|---|---|---|---|---|
| Logo | `assets/brand/logo.png` / `.svg` | Repository identity | GPT Image 2 source + local layout script | `done` |
| Banner | `assets/brand/banner.png` / `.svg` | README first screen | GPT Image 2 source + local layout script | `done` |
| Social preview | `assets/brand/social-preview.png` / `.svg` | Candidate GitHub social image | GPT Image 2 source + local layout script | `done` |
| Logo source | `assets/brand/logo-ai-source.png` | Reusable source for later crops or layouts | fal `openai/gpt-image-2` | `done` |
| Banner source | `assets/brand/banner-ai-source.png` | Reusable source for later crops or layouts | fal `openai/gpt-image-2` | `done` |
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

## Notes

- Brand visuals now use AI-generated source images instead of pure SVG placeholder art.
- The local script keeps all readable text, badges, crops, workflow, and demo layouts deterministic.
- Workflow and demo images should remain script-rendered so the text stays readable.
