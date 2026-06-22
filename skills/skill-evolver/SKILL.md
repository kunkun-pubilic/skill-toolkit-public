---
name: skill-evolver
description: 当真实使用、小实验或上游更新评审证明已有 Skill 需要沉淀可复用增量时使用。触发关键词：技能改进 / 演化技能 / 复盘沉淀 / improve skill / evolve skill。不用于缺陷修复、新建技能或未经验证的想法收集。
---

# 技能复用增量门

## 角色

本技能处理“用过以后发现值得复用的改进”。它不修坏技能，也不从零创建 Skill；缺陷修复交给 `skill-modify`，新能力获取交给 `skill-creator`。

核心问题只有一个：

```text
这次新增的有效做法，应当沉淀到哪里，还是不沉淀？
```

可选落位：

| 落位 | 适用情况 |
|---|---|
| upstream issue/PR | 问题属于官方/厂商上游，且对所有用户都有价值 |
| overlay patch | 上游基本正确，但 Kun/Codex/Claude 兼容层需要补充 |
| Kun-owned patch | 目标 Skill 是 Kun-owned，且增量已经被真实使用证明可复用 |
| fork | 上游方向长期不适合，需要维护分叉 |
| no-change | 只是一次性经验、项目私有上下文或证据不足 |

## Public Edition Note

公开版演化不要求 Kun 私有 registry。若没有 registry 或 upstream lock，先把目标来源标成 `standalone-local`、`public-upstream` 或 `unknown`，再决定增量是否应该进入当前 Skill、提交给上游 issue/PR、做 overlay，还是保持 no-change。完成证据至少包含改动前后 diff、目标 Skill 校验和一个真实或模拟 pressure scenario。

## 方法调用

```text
/skill-evolver(目标技能, 使用证据, 改进意图?)
```

## 输入门禁

进入本技能前必须有证据。以下输入可以进入：

- 小实验结果：`pressure scenario` 明确显示现有 Skill 需要新增可复用能力。
- 真实使用复盘：一次任务跑完，发现下次同类任务还会复用的判断、资料或脚本。
- 上游更新评审：官方更新后，overlay 需要重放、调整或删除。

以下输入不进入：

- “感觉可以加点东西”但没有用例证据。
- 技能不触发、太长、资源漂移、验证失败；这些先走 `skill-modify`。
- 用户只是要创建新 Skill；这走 `skill-creator`。
- 需要 MCP、OAuth、hooks、app/widget 或插件缓存；这走 `plugin-manager`。

## 来源判断

演进前先确认目标 Skill 来源：

1. 读 `kun-agent-registry/registry.yaml` 和 `lock.yaml`。
2. 读目标 Skill 的 official-basis reference、`skills-lock.json` 或 overlay manifest。
3. 判断来源是 `kun_owned`、`official_adopt`、`official_overlay`、`fork`、`vendor_copy` 还是未知。
4. 来源未知时停止，输出 `blocked: source-ownership-unknown`。

不同来源的演进规则：

| 来源 | 默认动作 |
|---|---|
| `official_adopt` | 不改本地副本；先判断是否应转 `official_overlay` 或给上游提 issue/PR |
| `official_overlay` | 只改 overlay manifest、Kun metadata、`agents/openai.yaml`、`official-basis` 或 registry 记录 |
| `kun_owned` | 可改 `SKILL.md`、`references/`、`scripts/`、`assets/`，但必须先写差分契约 |
| `fork` | 在 fork 仓库内改，并更新同步策略 |
| `vendor_copy` | 可改，但输出中必须声明已经不自动跟随官方 |

**编辑面铁律**：上表的"可改"都指**真理源仓库 clone 内**的修改。按 commit 键控的本地 cache 快照应视为只读，宿主/项目 skill 路径可能只是 symlink；穿过 symlink 就地写入会污染快照且改进丢不回真理源。完整回路 = clone 真理源 → 改 → 验证 → push → 推进 registry pin → 重建新 commit cache → 重指 symlink。公开 standalone 环境没有 registry 时，用 git diff、目标仓库 commit hash、`quick_validate.py` 和 `audit_skill.py` 代替。

## 决策流程

1. 写差分契约：用 `references/delta-contract.md` 记录来源、证据、目标行为、非目标行为、验证面和删除条件。
2. 判断是否值得沉淀：
   - 是否会在未来同类任务复用？
   - 是否有真实输入/输出或小实验证据？
   - 是否能机械验证，或至少有明确 pressure scenario？
   - 是否属于上游公共问题，而不是 Kun 私有偏好？
3. 判断落位：
   - 公共上游问题优先 upstream issue/PR。
   - 宿主兼容、触发描述、Kun governance 优先 overlay。
   - Kun-owned 流程缺口才直接 patch 目标 Skill。
   - 长期方向分叉才 fork。
   - 证据不足则 no-change。
4. 执行最小改动：
   - 先重写既有区块，再考虑新增区块。
   - 大段场景提示词进 `references/`。
   - 确定性检查或转换进 `scripts/`。
   - 不创建共享资源池，不恢复 plugin-era facade/orchestra。
5. 验证：
   - 编辑前运行 `scripts/build_patch_plan.py`。
   - 编辑后运行 `scripts/audit_incremental_update.py`。
   - 目标 Skill 再跑 `skill-modify` 的 `quick_validate.py` 和 `audit_skill.py`。
   - 没有真实新对话证据时，结论只能写 `pending-user-pilot`。
6. 若演进改变了输入 artifact、输出 artifact、handoff status、下游 Skill、边界或 proof surface，必须同步更新 Chain Position 和 registry chain metadata；不能只改正文叙述。

## 输出契约

```text
演进结果：upstream-issue | overlay-patch | kun-owned-patch | fork-change | no-change | blocked
目标 Skill：<id/path/source>
证据：<真实使用 / 小实验 / 上游更新评审>
来源判断：<kun_owned | official_adopt | official_overlay | fork | vendor_copy | unknown>
差分：<新增 / 重写 / 删除 / 外移 / 不沉淀>
落位理由：<为什么在这里，而不是上游/overlay/目标正文>
改动路径：<files changed or planned>
链条影响：standalone/no-change 或 <chain_id/position/changed fields>
验证：<commands and pass/fail>
复用状态：reusable | project-local | one-off | pending-user-pilot
下一步：停止 | 交给 skill-modify | 交给 skill-overlay | 提 upstream issue/PR | 更新 registry
```

## 资源

- `references/delta-contract.md`：可验证能力差分契约。
- `references/evolution-principles.md`：演进时不可违背的最小化、证据和触发规则。
- `references/convergence-evolution-decision-questions.md`：判断是否值得沉淀的问题库。
- `references/patch-placement-matrix.md`：决定落到 `SKILL.md`、`references/`、`scripts/`、overlay 还是不落位。
- `references/scenario-prompts.md`：真实任务复盘或大体量场景提示词的资产化模板。
- `references/task-process-improvement-proposal.md`：把任务过程记录转成改进候选的模板。
- `references/verification-gates.md`：演进完成前验证门。
- `references/pilot-closed-loop.md`：演进后的 pressure scenario 验收模板。
- `scripts/build_patch_plan.py`：编辑前生成补丁计划。
- `scripts/audit_incremental_update.py`：编辑后审计增量质量。

## 本技能的 deletion-spec

- **触发删除条件**：当 `skill-modify` 或官方工具能稳定处理“真实使用证据 → 落位判断 → upstream/overlay/Kun-owned patch → 验证”的完整闭环时，本技能可合并或删除。
- **禁用方式**：从 `kun-skill-toolkit/skills/` 删除本目录，并同步 `kun-agent-registry` 的 skill index / lock 记录。
- **卸载清单**：`SKILL.md`、`agents/openai.yaml`、`references/delta-contract.md`、`references/evolution-principles.md`、`references/convergence-evolution-decision-questions.md`、`references/patch-placement-matrix.md`、`references/scenario-prompts.md`、`references/task-process-improvement-proposal.md`、`references/verification-gates.md`、`references/pilot-closed-loop.md`、`scripts/build_patch_plan.py`、`scripts/audit_incremental_update.py`。
