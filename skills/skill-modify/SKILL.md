---
name: skill-modify
description: 当已有 Skill 出现触发不准、正文臃肿、流程失效、资源漂移、验证缺失，或官方/可信上游 Skill 需要通过 overlay 修兼容层时使用。触发关键词：修技能 / 改技能 / 技能不触发 / fix skill / overlay repair。不用于新建技能或真实使用后的能力演进。
---

# 技能修复器

## 方法调用签名

```
/skill-modify(目标技能, 问题现象, 改动范围?)
```

同一流程 × 不同目标技能 → 修复不同技能。问题现象决定先看触发、正文、资源、脚本还是小实验路径；改动范围用于控制本轮只修最小必要问题。

修复前先做收敛判断。默认先删减和归位，再补内容；先用 `references/skill-layering-audit.md` 区分固定层、动态层和按需资源层。若本轮涉及官方来源、迁移、发布或宿主兼容，先读取本技能自带的 `references/official-compatibility-decision-gate.md`。

## Public Edition Note

公开版修技能时，优先修改当前仓库或项目里的真实 Skill 目录，不要假设存在 Kun 私有 registry、全局 cache 或 symlink 投影。若这些治理面不存在，输出里写成 `standalone-local`，并用 `quick_validate.py`、`audit_skill.py`、git diff 和一次 pressure scenario 作为完成证据。

## 和演进的边界

修改和演进可以连续发生，但不能混成一步。

```text
先修改：修掉已经影响使用的缺陷。
再评估：用小实验判断修复是否真的改善。
后演进：只有评估发现“新增可复用能力”时，才交给 skill-evolver。
```

判断口径：

- 技能不触发、误触发、太长、边界乱、资源漂移、机器字段看不懂 → 本技能先修。
- 修完后只是恢复正常 → 到小实验评估后停止。
- 修完后发现需要沉淀新场景、新判断标准、新脚本机会 → 交给 `skill-evolver`。
- 用户一开始同时要求“修一下并加能力” → 先用本技能修缺陷，再把新增能力作为评估后的下一步。

## 这是判断流程的封装

skill-modify 本身就是“胖技能”的典型：正文是一个判断流程（锁定目标 → 诊断缺陷 → 判断轻重 → 同步清理 → 验证和小实验），不是命令清单。

修复的目标是“用户可感知的行为改进”，不是“文档体量增加”。`SKILL.md` 是资源定义的唯一真源。价值判断由模型主导，Python 脚本只承担兜底的确定性检查与转换。

常见根因：模型会把技能当普通长提示词写，把脚本、参考资料、资产都压进 `SKILL.md`。修复时先做资源分流和归属判断，再决定是否改正文。

## 核心判定

每次修技能先做四个判定：

1. 来源类型：`kun_owned` / `official_adopt` / `official_overlay` / `fork` / `vendor_copy` / `reference_only`。
2. 分层：固定动作进 `scripts/` 或 schema；动态判断留在 `SKILL.md`；长例子和规则进 `references/`。
3. 缺陷：优先修触发失配、大而全、抽象口号、资源漂移、验证缺失。
4. Plugin 例外：只有 MCP、OAuth/app 授权、浏览器桥、hooks、app/widget 或宿主 runtime 才进入 Plugin 路径。
5. 链条合同：若目标 Skill 属于多步骤 workflow，缺失或过期的 Chain Position 本身就是缺陷；修复时必须补齐 consumed artifact、produced artifact、handoff status、next Skill、hard boundary 和 proof surface。
6. 仓库状态机：若目标位于复合技能仓库，缺少 repo-level `WORKFLOW.md` 本身就是重大缺陷；不能只修单个 Skill 后宣称整个 repo workflow-ready。

## 官方上游修改边界

修官方或可信上游 Skill 时，先看 registry、lock、目标 Skill 的 official-basis reference、`skills-lock.json`，确认它是 raw adopt、overlay、fork 还是 Kun-owned。不同来源的可改面不同：

| 来源 | 可直接改 | 禁止 |
|---|---|---|
| `kun_owned` | `SKILL.md`、本地 `references/`、`scripts/`、`assets/`、`agents/openai.yaml` | 无理由大改或不验证 |
| `official_adopt` | 安装记录、registry 记录、lock、禁用/作用域配置 | 直接改上游正文或资源 |
| `official_overlay` | overlay manifest、Kun 补充说明、`agents/openai.yaml`、official-basis reference、触发描述兼容层 | 把 Kun 改动混进 upstream copy |
| `fork` | fork 仓库内受控修改 | 不记录 fork 原因、同步策略和删除条件 |
| `vendor_copy` | Kun 接管后的副本 | 继续声称可自动跟随官方 |

如果用户说“把别人的 Skill 拿来改一下”，默认不是直接编辑副本，而是：

```text
读上游锁定信息 -> 判断是否 raw adopt 或 overlay -> raw adopt 先转 overlay -> 修改 overlay manifest / Kun metadata -> 验证 -> 更新 registry lock
```

官方/可信上游 Skill 的修复还必须检查运行时官方源树，而不只是 Markdown：

1. 目标 Skill 的 upstream source tree 是否覆盖被采用上游的关键 `SKILL.md`、`references/`、`scripts/`、`assets/`、模板、schema 和 fixtures，而不只是摘要、链接或一句 provenance。
2. 目标 Skill 的 official-basis reference 是否列出所有 source-tree mirrors，并区分 adopted / overlay / reference-only / rejected，以及每类 payload 的角色：rule text / executable script / runtime asset / fixture / evidence-only。
3. `SKILL.md` 是否有 `## Runtime Official Source Contract`，且要求执行前读取 `official-basis.md` 和 `runtime-rules.md`；若需要精确上游行为、审计或更新评审，再读取 `references/upstream/` 下的完整上游源树。
4. 上游 `scripts/` 或 `assets/` 若是能力的一部分，不能只放在 `references/upstream/` 当证据。可执行或可使用投影必须进入本 Skill 的本地 `scripts/` / `assets/`，或在 `runtime-rules.md` 里明确标为 `evidence_only` / `blocked_until_projected`。
5. registry / lock / overlay manifest 的 commit pin、tree hash、关键文件 hash 是否和本地镜像及运行投影一致。

缺任一项时，按 `official_source_tree_gap` 修复：补源树镜像、补 runtime read contract、补脚本/资产投影说明、补 registry/lock 证据，再跑 `quick_validate.py` 和 `audit_skill.py`。不能用“官方源已写在 official-basis 里”代替完整上游源树，也不能在没有 runtime read requirement 时声称完成 official-overlay。

只有当 registry 明确标为 `kun_owned`、`fork` 或 `vendor_copy` 时，才允许直接改技能正文。无法判断来源时输出 `blocked: source-ownership-unknown`，不要猜。

## 适用范围

修复已有技能的提示词质量缺陷：

- 触发失配（描述字段写"我能做什么"而非"何时触发我"）
- 大而全（单技能多职责，应拆成多个小技能）
- 限制护栏代替判断流程（用"要认真"代替具体的判断步骤）
- 结构噪音（README / CHANGELOG 等无关文档）
- 资源漂移（声明的资源不存在 / 存在的资源未声明）
- 渐进披露不足（细节没有外挂到参考资料）
- 可拆分性受损（普通结构约束、提示词模式、评分标准、示例或脚本被抽到插件根部共享目录）
- 关键词触发不足（描述字段关键词稀薄，模型语义推断不可靠）

不用于新增能力沉淀（那是 `skill-evolver`）或从零创建（那是 `skill-creator`）。如果新增能力和修复同时出现，先修复，再根据小实验评估决定是否演进。

## 定位技能源文件

修改前先找到 SKILL.md 实际位置：

| 类型 | 路径 | 示例 |
|---|---|---|
| **Registry-indexed GitHub skill** | `<repo>/skills/<name>/SKILL.md` | `kun-skill-toolkit/skills/skill-modify/SKILL.md` |
| **Project skill** | `.agents/skills/<name>/SKILL.md` 或 `.claude/skills/<name>/SKILL.md` | `.agents/skills/client-intake/SKILL.md` |
| **Global installed skill** | host skill path symlink 到 locked cache | global host skill directory |
| **Legacy local skill** | `skills-original-repo/<name>/SKILL.md` | 只作为迁移来源，不作为新真理源 |

判断方法：优先看当前仓库；再看 `kun-agent-registry/registry.yaml`、`lock.yaml` 和安装目录的 `skills-lock.json`；最后看旧本地运行时路径。Plugin 后处理只在命中 Plugin runtime 例外时执行，并必须写清用户授权和 proof surface。

## 真理源回写环（铁律）

上面的来源表只回答"能改什么"，这里回答"在哪改"：**唯一合法编辑面是真理源仓库的 clone**。按 commit 键控的本地 cache 快照应视为只读；宿主/项目 skill 路径可能只是指向它的 symlink。直接编辑投影或缓存（包括穿过 symlink 的写入）= 污染快照 + 改进永远丢不回真理源。

完整回路，缺一步不算修完：

```text
clone 真理源 -> 修改 -> 本地验证（仓库 check + fixtures）-> push
  -> 推进 kun-agent-registry pin -> 重建新 commit 的 cache 目录
  -> 重指宿主/项目 symlink -> 终验穿透 symlink 读到新内容
```

在完整治理环境里，可以用 governance cache integrity checker 把每个 cache 快照与真实 commit 内容逐文件 diff，任何就地修改都会以 `drift` 暴露。公开 standalone 环境没有这个检查器时，用 git diff、目标仓库 commit hash、`quick_validate.py` 和 `audit_skill.py` 代替。

## 输出契约

执行修复任务时始终返回用户可读的“修复卡”，不要把机器字段当成主输出：

1. 问题：哪里不好用，为什么影响用户。
2. 修法：本轮最小改什么，哪些明确不动。
3. 改后文本：把关键技能正文片段拿给用户看。
4. 工程化审计：组件、组件关系、状态载体、失败回环和验证面是否补齐；未补齐时为什么只做局部修复。
5. 资源状态：哪些资源已使用、哪些过时、哪些缺失，以及怎么处理。
6. 验证证据：跑了什么命令，结果是什么。
7. 行为门禁：pressure scenario 是什么；结果是通过、部分通过、失败，还是 `pending-user-pilot`。
8. 链条合同：standalone，或 `chain_id / position / consumes / produces / handoff_status / next_skill / proof_surface` 的修复结果。
9. 仓库状态机：standalone、`WORKFLOW.md` 已存在/已补、或 runtime_lifecycle；缺失时写 blocker。
10. 下一步：停止、继续修改、交给 `skill-evolver`、合并、删除，或等待用户确认。

小实验评估卡固定使用这几项：

```text
测试场景：
预期变化：
实际结果：
评估结论：通过 / 部分通过 / 失败 / pending-user-pilot
下一步建议：停止 / 继续修改 / 进入演进 / 合并 / 删除
```

## 最小修复回路

### 1) 锁定修复目标

一句话明确目标技能路径与用户意图。成功标准定义为"用户可感知的行为改进"。

### 2) 执行精简诊断

先读 `references/skill-layering-audit.md`。若需要更细规则，再按需读 `references/repair-checklist.md`、`references/prompt-patterns.md`、`references/convergence-repair-heuristics.md`。

默认只输出：

- 触发问题
- 分层问题
- 资源问题
- 官方兼容 / Plugin 例外判断
- 验证缺口
- 最小修法

### 3) 应用最小且高影响改动

按以下优先级：

1. **必须先修**：文件头元数据非法、触发描述损坏、占位符泄漏、严重违反三原则。
2. **本轮应该修**：流程过于僵化、关键约束缺失、输出契约过弱、脚本越权主导判断。
3. **本轮应该修**：长内容未拆参考资料、确定性动作未下沉脚本、资产未进入资产。
4. **本轮应该修**：普通资源被错误移出技能目录，导致子技能后期不能独立分发。
5. **可后续修**：结构简化、去重、资源减负。

小范围补丁足够时不要大改重写。

### 4) 同步清理（必须执行）

先改 SKILL.md，再按 SKILL.md 做同步清理：

- 从 SKILL.md 移除的脚本 / 引用 / 资产，必须删除对应文件
- 同步删除所有残留调用与说明（`agents/openai.yaml`、`references/*.md`、`scripts/*.py` 中的失效路径）
- 禁止保留孤儿文件（文件存在但未在 SKILL.md 声明）
- 禁止保留悬空引用（SKILL.md 或其他文件引用不存在路径）
- 不把普通资源移动到插件根部共享目录作为清理手段；若发现历史共享资源不是运行时配置，报告 `needs-skill-localization`
- 修复后用搜索确认没有新增对插件根部共享资源池的依赖：`_shared`、`shared/`、`common/`、根部 `references/`。

## 修复完成前验证模板

详细检查清单和命令模板已下沉到 `references/convergence-verification-template.md`。执行到本段相关步骤时按需读取。

### 6) 以讨论钩子收尾

仅当仍有不确定项且会影响实现选择时才提问。改完不再提宽泛的头脑风暴问题。

**完成条件**：`quick_validate.py` + `audit_skill.py` 均通过，触发对照证据至少 1 组，改前/改后差异能说明预期行为改善，且 pressure scenario 结论明确；没有真实新对话证据时只能收口为 `pending-user-pilot`。

## 修复启发式规则

详细规则、模板和示例已下沉到 `references/convergence-repair-heuristics.md`。执行到本段相关步骤时按需读取；默认注入只保留流程、门禁和交接要求。

## 资源

- `references/repair-checklist.md`：诊断与重写决策标准
- `references/skill-layering-audit.md`：判断 `SKILL.md` / `scripts/` / `references/` / `assets/` 分工是否正确
- `references/official-compatibility-decision-gate.md`：官方上游、宿主兼容、source strategy 与 Plugin 例外判断
- `references/prompt-patterns.md`："差 → 优"提示词模式重写模板
- `references/convergence-verification-template.md`：修复完成前验证命令模板
- `references/convergence-repair-heuristics.md`：收敛修复启发式规则
- `scripts/audit_skill.py`：改动后的轻量本地审计
- `scripts/quick_validate.py`：SKILL.md frontmatter 与基础结构快速校验
- `scripts/gate_result.py`：JSON gate 输出 helper，供校验脚本按需使用
- `scripts/package_skill.py`：将单个 skill 打包为可分发归档
- `references/pilot-closed-loop.md`：修复后的最小小实验和新对话验证提示词
- 官方最佳实践（按需查）：
  - [Claude 智能体技能最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
  - [OpenAI Codex 技能文档](https://developers.openai.com/codex/skills/)

## 本技能的 deletion-spec

- **触发删除条件**：当 Claude Code / Codex 都能原生提供可解释的技能 lint、资源对齐、触发回归与插件市场索引同步检查时，本技能可降级为规则文档
- **禁用方式**：从 `kun-skill-toolkit/skills/` 删除本目录，并同步 `kun-agent-registry` 的 skill index
- **卸载清单**：
  - `references/repair-checklist.md`
  - `references/prompt-patterns.md`
  - `references/convergence-verification-template.md`
  - `references/convergence-repair-heuristics.md`
  - `references/official-compatibility-decision-gate.md`
  - `scripts/audit_skill.py`
  - `scripts/quick_validate.py`
  - `scripts/gate_result.py`
  - `scripts/package_skill.py`
  - `agents/openai.yaml`
  - `kun-agent-registry` 中引用 `skill-modify` 的 skill index / lock 记录
  - `skills/skill-creator/`、`skills/skill-evolver/` 中引用本技能 validator 的说明
