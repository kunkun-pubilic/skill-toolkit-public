# Skill Toolkit Public Resources

This repository is the public resource pack for Kun's Skill Toolkit video:

> A useful Agent Skill is not a saved prompt. It is a working interface for
> repeated judgment, references, mechanical actions, and verification.

The repository contains:

- a viewer-facing resource index;
- the publish-copy package used for the video;
- one sanitized sample Skill, `video-publish-copy-pack`;
- reusable templates for building platform copy from one expression spine.

It does not contain the private governance registry, private runtime locks, raw
video footage, credentials, local caches, or private project history.

## Start Here

- Chinese resource index: [docs/VIDEO_RESOURCE_INDEX.zh-CN.md](docs/VIDEO_RESOURCE_INDEX.zh-CN.md)
- Skill design notes: [docs/SKILL_DESIGN_NOTES.zh-CN.md](docs/SKILL_DESIGN_NOTES.zh-CN.md)
- Agent install prompt: [docs/AGENT_INSTALL_PROMPT.zh-CN.md](docs/AGENT_INSTALL_PROMPT.zh-CN.md)
- Sample Skill: [skills/video-publish-copy-pack/SKILL.md](skills/video-publish-copy-pack/SKILL.md)
- Example publish copy pack: [examples/publish-copy-pack.skill-toolkit-round15.md](examples/publish-copy-pack.skill-toolkit-round15.md)

## Core Idea

Prompt solves one expression. Skill solves a repeated workflow:

```text
trigger
  -> read the right references
  -> make bounded judgment
  -> run mechanical checks where possible
  -> produce a reusable artifact
```

For the video publish workflow, the reusable artifact is not "six random
captions". It is one expression spine and a set of platform-specific fields
derived from it.

## License

No open-source license has been applied yet. Treat this repository as a public
reading and reference pack until a license is added.

