# Adoption Lock Format

`skill-adopter` writes a project-local `skills-lock.json`. The lock file is the proof that an adopted Skill came from a specific source and can be compared before future updates.

## Top-Level Shape

```json
{
  "version": 1,
  "updated_at": "2026-06-04T00:00:00Z",
  "skills": {
    "skill-id": {
      "id": "skill-id",
      "name": "skill-id",
      "description": "trigger description from SKILL.md",
      "source": {},
      "install": {},
      "hashes": {},
      "payload_roles": {},
      "files": [],
      "validation": {}
    }
  }
}
```

## Required Evidence

- `source.url`: original Git URL or local path.
- `source.skill_path`: path inside the source repo.
- `source.commit`: exact Git commit when source is a Git repo.
- `hashes.installed_tree_sha256`: deterministic hash of installed files.
- `payload_roles`: count of installed source-tree payload roles such as `rule_text`, `executable_script`, `runtime_asset`, and `fixture_or_template`.
- `files[]`: relative file path, byte size, and SHA-256 for each installed file.
- `validation.suggested_commands`: validator commands to run after install.

## Trust Boundary

The lock proves reproducibility and change detection. It does not prove that the upstream is trustworthy. Trust comes from source research, official/vendor ownership, review of the full source tree including scripts/assets, and validation output.
