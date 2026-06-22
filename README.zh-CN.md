# Skill Toolkit 公开包

这是 Kun 在「Skill 创建与维护」主题视频里展示的 Skill Toolkit。它不是一组提示词模板，而是一套让 Agent 能持续复用、验证和维护能力的工作方法。

核心观点：

> Skill 不是把提示词存起来，而是把反复发生的判断、资料、脚本和验收方式，整理成 Agent 可以按需调用的工作接口。

这个公开包面向看完视频后想拿到同款工具的人：你可以直接复制这些 Skill 到自己的 Codex / Claude Code 项目里，让 Agent 帮你找上游 Skill、创建新 Skill、修已有 Skill、做 overlay，或者把真实使用后的有效改进沉淀回 Skill。

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

## 快速开始

克隆仓库：

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public
```

安装到某个项目的 Codex Skill 目录：

```bash
mkdir -p /path/to/your/project/.agents/skills
cp -R skills/skill-adopter /path/to/your/project/.agents/skills/
cp -R skills/skill-creator /path/to/your/project/.agents/skills/
cp -R skills/skill-overlay /path/to/your/project/.agents/skills/
cp -R skills/skill-modify /path/to/your/project/.agents/skills/
cp -R skills/skill-evolver /path/to/your/project/.agents/skills/
```

安装到 Claude Code 项目目录时，把目标换成：

```bash
/path/to/your/project/.claude/skills
```

建议把 `contracts/` 也保留在这个仓库里。`skill-creator` 的脚本会从仓库根目录读取它。

## 推荐使用顺序

1. `skill-adopter`：先找有没有官方或成熟上游。
2. `skill-overlay`：上游基本好用，但需要本地兼容层时使用。
3. `skill-creator`：确认没有合适上游后再从零创建。
4. `skill-modify`：已有 Skill 不好用时先修。
5. `skill-evolver`：真实使用证明有复用价值后再沉淀增量。

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
- [生命周期工作流](docs/SKILL_LIFECYCLE.zh-CN.md)
- [给 Agent 的安装提示词](docs/INSTALL_PROMPT.zh-CN.md)
- [公开版边界说明](docs/PUBLIC_EDITION_NOTES.zh-CN.md)

## 许可

当前仓库暂未添加开源许可证。你可以公开阅读、学习和在自己的本地项目中参考使用；如果要复制、改造后再发布，请先确认适合的许可证和署名方式。
