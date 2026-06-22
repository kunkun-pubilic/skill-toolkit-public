# Official Basis

This public sample is extracted from a real self-media publishing workflow and
sanitized for sharing.

## Generation Summary

- skill_name: `video-publish-copy-pack`
- source_strategy: `public_sample_from_kun_workflow`
- host_support: `codex, claude-code`
- invocation_policy: `on_demand`
- proof_surface: `human review + generated spine + platform copy files`

## Public References

This sample follows the general Agent Skill pattern:

- a required `SKILL.md` entrypoint;
- short discovery frontmatter;
- long rules moved into `references/`;
- reusable output shapes moved into `templates/`;
- one atomic task boundary instead of a broad facade.

Useful public references:

- Agent Skills specification: <https://github.com/agentskills/agentskills>
- OpenAI skills examples: <https://github.com/openai/skills>
- Anthropic skills examples: <https://github.com/anthropics/skills>

## Local Domain Basis

This Skill exists because platform publishing copy often drifts when every
platform is written independently. The locked workflow is:

```text
unified expression spine
  -> title theme
  -> intro body
  -> supplement/resources
  -> profile/resource CTA
  -> platform field adaptation
  -> copy pack + manifest fields
```

The practical rule is simple: write the spine first, adapt second. If a platform
variant no longer traces back to the same core claim, rewrite the spine or mark
the package as not ready.
