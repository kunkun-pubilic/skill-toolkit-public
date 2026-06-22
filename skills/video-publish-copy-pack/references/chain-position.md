# Chain Position

```yaml
chain_id: video-rough-cut-chain
position: publish-copy-pack
consumes:
  - verified final video or publish-manifest.yaml
  - cover package or cover-lock.md
  - transcript/script/cut notes when available
  - Kun publish intent
produces:
  - publish-copy/publish-copy-spine.yaml
  - publish-copy/publish-copy-pack.md
  - publish-copy/copy/<platform>.md
  - publish-manifest.yaml copy_fields update when requested
handoff_status:
  - local_verified_not_published
next_skill:
  - human uploader
  - authorized platform publisher
must_not:
  - upload or publish without explicit user authorization
  - invent resource links, files, claims, or platform promises
  - let platform variants change the core message
  - produce markdown-only output with no copy-ready fields
proof_surface:
  - quick_validate + audit_skill + scripts/check-video-skills
  - generated publish-copy-spine.yaml
  - generated platform copy files
  - copied/linked evidence from publish-manifest.yaml
invocation_policy: on_demand
```

This skill sits after `video-export-verify` and `video-cover-composer`. It prepares publish copy and handoff fields only; it does not publish.
