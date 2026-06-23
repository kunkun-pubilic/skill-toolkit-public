# Skill 生命周期工作流

这套 Toolkit 的核心不是“写一个很长的提示词”，而是把 Skill 的生命周期拆成五个可验证阶段。

```text
需求出现
  -> skill-adopter：先找官方或成熟上游
  -> skill-overlay：上游可用但需要本地兼容层
  -> skill-creator：没有上游才从零创建
  -> skill-modify：已有 Skill 不好用时修复
  -> skill-evolver：真实使用后沉淀可复用增量
```

## 1. Adopt：先找上游

使用 `skills/skill-adopter`。

适用情况：

- 你想要一个新能力，但不知道是否已有官方 Skill。
- 你要迁移旧提示词或旧插件，想先找可维护来源。
- 你要采用 GitHub 上的某个 Skill，并留下来源证据。

输出应该包含 source card、候选上游、拒绝原因、采用路线和验证命令。

## 2. Overlay：保留上游，再加小兼容层

使用 `skills/skill-overlay`。

适用情况：

- 上游 Skill 基本可用。
- 但缺 Codex / Claude Code 元数据、触发描述、运行边界或本地验证约束。
- 你希望未来还能跟随上游更新，而不是直接改坏上游副本。

输出应该包含 overlay manifest、生成后的 Skill、`skills-lock.json` 和校验结果。

## 3. Create：没有上游才创建

使用 `skills/skill-creator`。

适用情况：

- 上游调研后没有合适候选。
- 这个能力有稳定、可复用的判断流程。
- 它不需要 MCP、OAuth、浏览器桥、hooks 或 hosted app 这类 runtime 集成。

公开版默认用 `--public-standalone`，不要求用户先接入 Kun 的私有 registry。

## 4. Modify：修不好用的 Skill

使用 `skills/skill-modify`。

适用情况：

- Skill 不触发或误触发。
- `SKILL.md` 太臃肿，把脚本、例子、长规则都塞在正文里。
- 资源路径漂移，声明的 references/scripts/assets 不存在。
- 没有 quick_validate / audit / pressure scenario。

修复优先级是：先改触发和结构，再补资源，最后验证。不要把一次修复顺手扩成新能力演化。

## 5. Evolve：真实使用后再沉淀

使用 `skills/skill-evolver`。

适用情况：

- 一次真实任务跑完，发现一个下次还会复用的判断。
- 小实验证明某个流程应该固化进 Skill。
- 上游更新后，overlay 需要重放、调整或删除。

它的关键问题只有一个：这个增量应该进上游、进 overlay、进当前 Skill，还是不沉淀。

## 完成证据

不要只说“改好了”。每次 Skill 生命周期动作至少留下：

- 改动路径；
- 来源说明；
- `quick_validate.py` 结果；
- `audit_skill.py` 结果；
- 一个 pressure scenario 或真实使用证据；
- 如果推到 GitHub，再补对应 commit 或 PR 链接。
