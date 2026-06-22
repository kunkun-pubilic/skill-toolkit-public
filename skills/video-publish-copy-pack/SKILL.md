---
name: video-publish-copy-pack
description: Use when a final self-media video and cover are ready to produce a unified, platform-adapted publish copy package with titles, intro, supplements, resource CTA, tags, chapters, and machine-readable copy fields. Not for editing video, generating covers, uploading, publishing, or generic markdown-only copywriting.
metadata:
  tags:
    - writing
    - video
    - generation
    - anti-slop
    - external-side-effect
    - chain
    - public-facing
---

# 视频发布文案包

## 角色

本技能用于在「视频已导出验证、封面已锁定」之后，生成 Kun 自媒体视频的发布文案包。核心不是给每个平台各写一套互相漂移的文案，而是先锁定一条统一表达主干，再按平台字段做轻量适配，最后输出人可读、机器可读、可复制粘贴的发布材料。

本技能适合处理：

- 已剪好、已验证的视频；
- 已生成或已锁定的多比例封面；
- 需要同时发布到 YouTube、B 站、小红书、视频号、抖音、X 或 Notion 记录的内容；
- 需要统一标题逻辑、简介、补充资料、资源链接 CTA、标签、章节的发布包。

本技能不做视频剪辑、封面生成、平台上传、自动发布、账号操作，也不产出只适合阅读但不好复制使用的大段 Markdown。

## 官方依据

```yaml
source_strategy: kun_owned
repo_type: composite_skill_repo
state_machine: WORKFLOW.md
host_support: codex,claude-code
plugin_needed: no
contracts: agent-skill-core, codex-skill, claude-code-skill, kun-governance
proof_surface: quick_validate + audit_skill + scripts/check-video-skills
invocation_policy: on_demand
official_basis: references/official-basis.md
```

本技能是 atomic on-demand 调用单元；不要把它包装成 suite facade、group route 或 orchestra。若多个技能需要一起安装，只在 registry 记录 install-only group。

## Runtime Official Source Contract

执行前必须先读：

- `references/official-basis.md`：生成依据、合同、旧版参考边界；
- `references/publish-copy-spine.md`：统一表达主干；
- `references/platform-adapters.md`：平台字段适配；
- `references/anti-ai-voice-gates.md`：反 AI 味和真实资源承诺门禁。

## Chain Position

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
  - platform publisher or human upload
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
```

## 方法调用

```text
/video-publish-copy-pack(input, context?, output?)
```

## 运行流程

1. **锁定发布上下文**
   - 优先读取 `publish-manifest.yaml`、`cover-lock.md`、`knowledge/publish/`、脚本、字幕、章节、剪辑 notes。
   - 明确当前状态只能是 `local_verified_not_published`，除非用户明确要求并授权发布。
   - 缺失关键信息时最多问 1-3 个问题：目标平台、主标题角度、资源/个人链接、需要补充的资料、哪些说法不要写。
2. **先写统一表达主干**
   - 产出 `publish-copy/publish-copy-spine.yaml`。
   - 主干字段必须包括：`core_claim`、`viewer_takeaway`、`title_theme`、`description_intro`、`supplement`、`resource_cta`、`avoid_claims`。
   - 简介负责介绍视频；补充负责承接视频里没讲完整的资料、文件位置、延伸说明；CTA 只在真实存在链接和资源时出现。
3. **再做平台适配**
   - 平台适配只改字段形态，不改核心观点。
   - 标题、首行、简介长度、标签、章节、CTA 位置、是否用话题标签按 `references/platform-adapters.md` 调整。
   - 大部分逻辑保持统一，小部分按平台调性微调。
4. **输出可执行发布包**
   - 输出 `publish-copy/publish-copy-pack.md` 供人审阅。
   - 输出 `publish-copy/copy/<platform>.md` 供人工复制。
   - 输出或更新机器可读字段，优先落在 `publish-copy/publish-copy-spine.yaml`，需要时同步到 `publish-manifest.yaml` 的 `copy_fields`。
5. **质量门禁**
   - 运行反 AI 味检查：不能出现模板化套话、虚假资源承诺、平台黑话堆砌、过度营销。
   - 运行一致性检查：各平台标题和简介必须回到同一 `core_claim`。
   - 明确风险：未确认链接、未确认平台、未确认章节时标 `needs-user`，不要假装完整。

## 输出契约

```yaml
status: local_verified_not_published | needs-user | blocked
inputs_read:
  - publish-manifest.yaml
  - cover-lock.md
  - transcript/script/cut notes
outputs:
  - publish-copy/publish-copy-spine.yaml
  - publish-copy/publish-copy-pack.md
  - publish-copy/copy/youtube.md
  - publish-copy/copy/bilibili.md
  - publish-copy/copy/xiaohongshu.md
  - publish-copy/copy/wechat-channels.md
  - publish-copy/copy/douyin.md
  - publish-copy/copy/x.md
quality_gates:
  unified_spine: pass | fail
  platform_adaptation: pass | fail
  human_voice: pass | fail
  real_resource_claims: pass | fail
  publish_not_performed: pass
next_step: human review or authorized publisher
```

## 对外交付门控（public-facing）

本 skill 产出真·对外成品文本（各平台 `publish-copy/copy/*.md` 发布文案）。该成品交付前必须转交 `public-expression-gate` 做去 AI 味后处理（去 AI 腔 / 表演诚实 / 反复自证 / 模板感 / 元数据与内部脚手架泄露）。默认 `stage=final`（九项全档）；草稿态中转可走 `stage=draft`（轻档只查硬伤、不改写）。`publish-copy-spine.yaml`、quality_gates 等 handoff 字段不进 gate、也不进对外正文。

## 资源

- `references/official-basis.md`：生成本技能时使用的官方 upstream lock、contracts 和 applied rules。
- `references/chain-position.md`：本技能在视频 workflow 中的位置。
- `references/publish-copy-spine.md`：统一表达主干契约。
- `references/platform-adapters.md`：平台字段适配规则。
- `references/anti-ai-voice-gates.md`：反 AI 味、真实资源承诺、统一性门禁。
- `references/pilot-closed-loop.md`：新技能行为验收模板。
- `templates/publish-copy-spine.yaml`：机器可读主干模板。
- `templates/platform-copy.md`：单平台可复制文案模板。

## 本技能的 deletion-spec

- **触发删除条件**：当视频发布包全链路被更强的 Kun publisher Skill 覆盖，且该 publisher 已能稳定复用统一表达主干、平台适配、机器可读字段和反 AI 味门禁。
- **禁用方式**：删除本技能目录，并同步 registry / lockfile / install adapter。
- **卸载清单**：`SKILL.md`、`agents/openai.yaml`、`references/official-basis.md`、`references/chain-position.md`、`references/publish-copy-spine.md`、`references/platform-adapters.md`、`references/anti-ai-voice-gates.md`、`references/pilot-closed-loop.md`、`templates/`、registry/lockfile 中指向本技能的记录。
