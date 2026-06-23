# Skill Toolkit 公开包

这是 Kun 在「Skill 创建与维护」主题视频里展示的 Skill Toolkit。它不是一组提示词模板，而是一套让 Agent 能持续复用、验证和维护能力的工作方法。

核心观点：

> Skill 不是把提示词存起来，而是把反复发生的判断、资料、脚本和验收方式，整理成 Agent 可以按需调用的工作接口。

这个公开包面向看完视频后想拿到同款工具的人：你可以直接复制这些 Skill 到自己的 Codex / Claude Code 项目里，让 Agent 帮你找上游 Skill、创建新 Skill、修已有 Skill、做 overlay，或者把真实使用后的有效改进沉淀回 Skill。

English entry: [README.md](README.md)

## 包里有什么

| 路径 | 用途 |
|---|---|
| `skills/skill-adopter` | 先找官方或成熟上游 Skill，能采用就采用，不能采用再创建。 |
| `skills/skill-creator` | 没有合适上游时，从一个能力需求创建新的 Agent Skill。 |
| `skills/skill-overlay` | 官方 Skill 基本可用但缺本地兼容层时，用 overlay 叠加小改动。 |
| `skills/skill-modify` | 修已有 Skill：触发不准、太臃肿、资源漂移、验证缺失等。 |
| `skills/skill-evolver` | 真实使用后，把可复用增量沉淀到上游、overlay、当前 Skill 或选择不沉淀。 |
| `contracts/` | Skill 结构、Codex / Claude Code 兼容和治理约束的生成合同。 |
| `WORKFLOW.md` | 五个 Skill 如何组成生命周期工作流。 |
| `skill-registry.yaml` | 公开包内的 Skill 清单和建议安装顺序。 |

公开版只包含这五个 lifecycle skills。私有仓里的 `plugin-manager` 不属于本期公开包；它涉及 runtime/plugin 发行语义，后续如需公开会单独设计。

## 快速开始

克隆仓库：

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public
```

安装到某个项目的 Codex Skill 目录：

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.agents/skills/"
```

安装到 Claude Code 项目目录时，把目标换成：

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/skill-adopter skills/skill-overlay skills/skill-creator skills/skill-modify skills/skill-evolver "$PROJECT/.claude/skills/"
```

建议把 `contracts/` 也保留在这个仓库里。`skill-creator` 的脚本会从仓库根目录读取它。

## 推荐使用顺序

1. `skill-adopter`：先找有没有官方或成熟上游。
2. `skill-overlay`：上游基本好用，但需要本地兼容层时使用。
3. `skill-creator`：确认没有合适上游后再从零创建。
4. `skill-modify`：已有 Skill 不好用时先修。
5. `skill-evolver`：真实使用证明有复用价值后再沉淀增量。

## 一个最小 Demo

仓库里有一个公开安全的最小示例：[examples/customer-message-digest](examples/customer-message-digest)。

它演示的是：如何把“整理客户聊天记录”这类重复工作，拆成输入、输出、边界、验证面和 `skill-creator --public-standalone` 命令。示例不包含真实客户材料。

## 视觉资料计划

视频片段、Workflow 图、Demo 和 GIF 会放进 public repo，但最终媒体资产先不直接生成。当前先看这两份方案：

- [视觉资产方案（中文）](docs/VISUAL_ASSET_PLAN.zh-CN.md)
- [Visual asset proposal](docs/VISUAL_ASSET_PLAN.en.md)

方案通过后再补实际文件，避免把不合适的视频素材、内部画面或过度复杂的演示直接放进公开仓。

## 验证

公开包内置轻量校验脚本。仓库根目录运行：

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py
python3 -m py_compile skills/skill-adopter/scripts/research_skill.py
python3 -m py_compile skills/skill-adopter/scripts/source_card_to_registry.py
python3 -m py_compile skills/skill-overlay/scripts/apply_overlay.py
python3 -m py_compile skills/skill-creator/scripts/create_skill.py
python3 -m py_compile skills/skill-evolver/scripts/build_patch_plan.py
python3 -m py_compile skills/skill-evolver/scripts/audit_incremental_update.py

for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do
  python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill"
  python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"
done
```

## 给 Agent 的一句话

把下面这句发给 Codex 或 Claude Code：

```text
请使用本项目里的 Skill Toolkit：先读 skill-registry.yaml 和 WORKFLOW.md；涉及 Skill 新建、采用、overlay、修复或演化时，按需调用 skills/skill-adopter、skills/skill-overlay、skills/skill-creator、skills/skill-modify、skills/skill-evolver。没有私有 registry 时使用 public standalone 模式，并把缺失的外部证据写成 evidence gap。
```

更多说明见：

- [快速安装与验证](docs/QUICK_START.zh-CN.md)
- [Quick Start](docs/QUICK_START.en.md)
- [生命周期工作流](docs/SKILL_LIFECYCLE.zh-CN.md)
- [给 Agent 的安装提示词](docs/INSTALL_PROMPT.zh-CN.md)
- [公开版边界说明](docs/PUBLIC_EDITION_NOTES.zh-CN.md)
- [Public edition notes](docs/PUBLIC_EDITION_NOTES.en.md)
- [公开仓库标准](docs/PUBLIC_REPO_STANDARD.zh-CN.md)
- [Public repository standard](docs/PUBLIC_REPO_STANDARD.en.md)

## 仓库基础文件

- [Code of Conduct](CODE_OF_CONDUCT.md)：公开协作的基本行为准则。
- [Contributing](CONTRIBUTING.md)：如何提 issue、提 PR、跑验证。
- [License](LICENSE)：当前公开包使用 MIT License。
- [Security](SECURITY.md)：发现密钥、私有数据或安全问题时怎么处理。
- [Issue template](.github/ISSUE_TEMPLATE/skill_toolkit_issue.yml)：提问题时按结构描述类型、路径、现状、预期和验证。
- [Pull request template](.github/pull_request_template.md)：提 PR 时说明改了什么、怎么验证、是否越过公开边界。

## 许可

当前公开包使用 [MIT License](LICENSE)。你可以复制、改造和再发布；请保留许可证和版权声明。
