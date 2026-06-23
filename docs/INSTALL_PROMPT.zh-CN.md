# 给 Agent 的安装提示词

把下面这段复制给 Codex 或 Claude Code，让它在你的项目里使用这套 Toolkit。

```text
我想在当前项目里使用 Skill Toolkit。

请先读取这个 GitHub 仓库：
https://github.com/kun-agent-system/skill-toolkit-public

目标：
1. 把 skills/skill-adopter、skills/skill-creator、skills/skill-overlay、skills/skill-modify、skills/skill-evolver 安装到当前项目的 Skill 目录。
2. Codex 项目使用 .agents/skills；Claude Code 项目使用 .claude/skills。
3. 保留 contracts/，因为 skill-creator/scripts/create_skill.py 会读取它。
4. 安装后运行 quick_validate.py 和 audit_skill.py 验证五个 Skill。
5. 后续涉及 Skill 新建、采用、overlay、修复或演化时，直接按这五个 Skill 的用途选择最小必要 Skill。
6. 不要假设我有 Kun 的私有 registry、全局 cache 或本机工具；把我当成一个空系统用户。

安装完成后请输出：
- 安装到哪些路径；
- 跑了哪些验证命令；
- 每个 Skill 的验证结果；
- 后续我应该怎么触发这些 Skill。
```

## 创建新 Skill 的提示词

```text
请使用 Skill Toolkit 帮我创建一个新的 Agent Skill。

能力需求：
<写清楚这个 Skill 要稳定解决什么问题>

要求：
1. 先用 skill-adopter 判断是否已有官方或成熟上游。
2. 如果有可用上游，优先 adopt 或 overlay，不要从零写。
3. 如果没有上游，再用 skill-creator 创建。
4. 使用 --public-standalone，按公开版方式创建。
5. 创建后用 skill-modify 的 quick_validate.py 和 audit_skill.py 验证。
```

## 修已有 Skill 的提示词

```text
请使用 skill-modify 修这个 Skill：

目标路径：
<填 SKILL.md 所在目录>

问题现象：
<例如不触发、误触发、正文太长、资源路径漂移、验证缺失>

要求：
1. 先判断来源类型和可改边界。
2. 本轮只做最小必要修复。
3. 修完后跑 quick_validate.py 和 audit_skill.py。
4. 给我一张修复卡：问题、修法、改动路径、验证结果、下一步。
```
