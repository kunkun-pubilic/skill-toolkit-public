# Publish Copy Spine

The spine is the single source of truth for publish copy. Platform variants must be derived from it instead of rewritten independently.

## Required Fields

```yaml
content_id: ""
status: local_verified_not_published
core_claim: ""
viewer_takeaway: ""
title_theme:
  main_angle: ""
  tension: ""
  must_include_terms: []
  must_avoid_terms: []
description_intro:
  role: "Introduce the video in Kun's voice."
  text: ""
supplement:
  role: "Add useful material not fully covered in the video."
  items: []
resource_cta:
  enabled: false
  link_label: ""
  url: ""
  promise: ""
platforms: []
chapters:
  source: ""
  items: []
tags:
  global: []
avoid_claims: []
voice_notes:
  - practical
  - direct
  - personal
  - no fake scarcity
```

## Meaning

- `core_claim`: the one sentence the viewer should remember.
- `viewer_takeaway`: what the viewer can do, understand, or decide after watching.
- `description_intro`: introduces the video, not the author bio.
- `supplement`: adds context, files, resource locations, or caveats that did not fit in the video.
- `resource_cta`: appears only when the resource exists and the promise is true.
- `avoid_claims`: things the copy must not imply.

## Decision Rule

If two platform variants cannot both be traced back to `core_claim`, rewrite the spine or mark `needs-user`. Do not silently create different positioning per platform.
