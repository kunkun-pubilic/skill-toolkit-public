---
name: skill-creator
description: 当用户提出新能力、注册技能、创建技能、沉淀用例或 scaffold skill 时使用。先判断是否可采用官方/可信上游或 overlay，只有无可用上游时才从零创建 Kun-owned Skill。不用于修复已有技能或真实使用后的能力演进。
---

# 新能力获取门

## 角色

本技能把一个明确的能力需求变成可调用的 Skill 路径。它不是“永远从零写 Skill”的脚手架，而是新能力获取门：

```text
用户目标 -> 上游调研 -> official-adopt | official-overlay | kun-create | plugin-runtime-exception
```

默认先查官方或可信上游。官方可直接用时交给 `skill-adopter`；官方基本可用但缺 Kun/Codex/Claude 兼容时交给 `skill-overlay`；没有可用上游时才运行 `scripts/create_skill.py` 从零创建 Kun-owned Skill。命中 MCP、OAuth/app 授权、浏览器桥、hooks、app/widget 或宿主 runtime 需求时，停止普通 Skill 创建并交给 `plugin-manager`。

从零创建时，本技能读取 `contracts/` 和 `kun-agent-registry/upstreams.yaml` / `upstream-lock.yaml`；缺少官方来源锁或合同文件时必须阻断，不假装基于官方。

## Public Edition Note

这个公开版支持两种运行方式。若你有自己的 registry 和 upstream lock，按原合同执行。若没有 Kun 私有 `kun-agent-registry`，使用 standalone 模式：先由 `skill-adopter` 记录 source card；确认没有可用上游后，运行 `scripts/create_skill.py --public-standalone ...` 生成本地 Skill 骨架。公开 standalone 模式不会声称已经锁定官方来源；它会在 `references/official-basis.md` 里记录 `public_standalone_gap`，提醒后续补官方快照或本地验证证据。

## Runtime Official Source Contract

Before executing this Skill, read `references/official-basis.md` to confirm the
local official-compatibility basis and route boundary. This Skill does not
adopt an upstream Skill directly; it routes official adoption and overlay work
to `skill-adopter` and `skill-overlay`.

## 真实调用方式

用户不需要说 `contracts`、`registry_root`、`upstream lock`、`official-basis` 这些内部细节。真实使用时，用户可以只说：

```text
帮我注册一个能整理微信消息的 skill。
用 skill-creator 创建一个能处理客户聊天记录的 skill。
把这个用例沉淀成 skill，然后用它处理这份材料。
```

听到这类请求时，本技能内部默认推断：

```yaml
target_root: .agents/skills
contracts: codex,claude
source_strategy: wrapper_overlay
proof_surface: quick_validate + audit_skill
registry_root: auto-discover kun-agent-registry
first_action: upstream_research
```

只有用户的边界不清、会误碰 Plugin runtime、或找不到 `kun-agent-registry` 时才问问题或阻断。不要让用户先学习本工具的合同层；合同层是本技能内部执行和审计机制。

## 方法调用

```text
/skill-creator(name, target_root?, registry_root?, contracts?, upstream_id?, source_strategy?, proof_surface?)
```

## 新能力决策门

每次用户说“创建/注册/沉淀一个 skill”，先走这张门：

| 判断 | 动作 |
|---|---|
| 官方或厂商维护 Skill 已满足需求 | `official-adopt`，交给 `skill-adopter` 安装、锁定、验证 |
| 官方或可信上游基本满足，但缺 Kun 边界、Codex/Claude 元数据或触发描述 | `official-overlay`，先由 `skill-adopter` 锁定，再由 `skill-overlay` 叠加兼容层 |
| 没有可用上游，或上游只是参考材料 | `kun-create`，读取 contracts 后从零创建 |
| 需要 MCP、OAuth、桌面/浏览器桥、hooks、app/widget 或插件缓存语义 | `plugin-runtime-exception`，停止并交给 `plugin-manager` |
| 需求只是修已有 Skill | 交给 `skill-modify` |
| 需求来自真实使用后的复用增量 | 交给 `skill-evolver` |

`skill-creator` 自己只执行 `kun-create`。前两类必须交给 `skill-adopter` / `skill-overlay`，不能假装自己已经调研或采用了官方上游。

## Official Source Mirror Invariant

只要 route 是 `official-adopt` 或 `official-overlay`，官方/可信上游不能只停留在 provenance 或一句 reference 说明里。创建流程必须落下三个运行时可见物：

1. 按锁定 commit 记录或镜像上游 source tree：`SKILL.md`、`references/`、`scripts/`、`assets/`、templates、fixtures、schemas，以及其他会影响行为的文件。
2. 在 `references/official-basis.md` 里列出 source tree payload，说明 adopted / overlay / reference-only / rejected 的关系，并标明 rule text / executable script / runtime asset / fixture / evidence-only。
3. 在目标 `SKILL.md` 写入 `## Runtime Official Source Contract`，要求执行前先读目标技能的 official-basis reference 和 runtime-rules reference；需要精确上游行为、更新评审、license/provenance 或脚本/资产判断时，再读取完整上游源树。
4. 如果上游脚本或资产是能力的一部分，必须把可执行/可使用投影放入本地 `scripts/` / `assets/` 并记录 hash；如果还没投影，状态只能是 `blocked_until_projected`，不能宣告 adopted。

如果上游只是启发材料，不能写成 `official-adopt` 或 `official-overlay`；应标记为 `reference_only`，并解释为什么不继承其规则。若上游存在但还没有锁定完整源树，或关键脚本/资产没有投影策略，创建结果只能是 `blocked`、`overlay-pending` 或 `blocked_until_projected`，不能宣告 adopted。

## 按需调用与 GitHub 整理边界

当候选来源是一个 GitHub repo、suite、插件目录或旧能力组时，默认按真实能力拆成 atomic Skills，而不是把整个系列注册成一个可调用入口。

- Skill 是调用单元：每个可触发能力必须有独立 `id`、`description`、source/overlay 记录、验证证据和 deletion-spec。
- `group` 只能用于安装便利，必须记录为 `callable: false`；不能把 group 当作 facade、总入口或路由技能。
- `orchestra` / `router` / `facade` 只有在用户明确要求中央路由，或该能力确实依赖 plugin runtime bundle 时才创建；否则标记 `archive`、`defer` 或 `group-install-only`。
- `description` 只写该 atomic Skill 的触发条件和负面边界，避免“系列入口”抢触发。
- workflow 链条通过 `## Chain Position`、registry chain metadata 和上下游 artifact 连接，不靠 group/facade 触发。
- GitHub 整理员处理 multi-skill repo 时，先做 capability map：`capability -> upstream path -> source_strategy -> installability -> proof_surface -> invocation_policy`。

repo 类型判断必须先落下：

```yaml
repo_type: standalone_skill | composite_skill_repo | runtime_repo
state_machine: chain-position | WORKFLOW.md | runtime_lifecycle
```

- `standalone_skill`：单技能只需 `## Chain Position` / `references/chain-position.md`。
- `composite_skill_repo`：仓库级必须有 `WORKFLOW.md`，描述一组技能的状态机、入口、artifact gates、stop states 和 proof surfaces；不能只靠每个 Skill 的 chain position 宣称 workflow-ready。
- `runtime_repo`：可用 `runtime_lifecycle` 替代领域 workflow，但仍要写清 install/check/distribution/rollback 的状态和 proof surface。

`invocation_policy` 默认值：

```yaml
atomic_skill: on_demand
group: install_only
group_callable: false
facade: blocked_unless_runtime_or_user_requested
```

## Kun-create 启动逻辑

1. 确认已经完成上游调研，且结论为 `kun-create`。没有结论时先交给 `skill-adopter` 做 source card / registry draft。
   - 如果调研结论是 `official-adopt` 或 `official-overlay`，停止 `kun-create`，转交 `skill-adopter` / `skill-overlay`，并要求其满足 Official Source Mirror Invariant。
2. 读取 `contracts/agent-skill-core.yaml`、用户指定 host contracts 和 `contracts/kun-governance.yaml`。
3. 读取 `--registry-root` 下的 `upstreams.yaml` 和 `upstream-lock.yaml`，校验合同要求的 upstream 都有 lock。
4. 若 docs upstream 的 `content_sha256` 与 snapshot 不一致，阻断。
5. 若 source strategy 是 `fork` 或 `vendor_copy`，先要求导入计划；未满足前不创建目录。
6. 若 `plugin_needed=yes`，停止创建 Skill，交给 `plugin-manager`。
7. 判断新 Skill 所在仓库是 `standalone_skill`、`composite_skill_repo` 还是 `runtime_repo`。链条成员必须有 `## Chain Position` 或 `references/chain-position.md`，并在 registry 里记录同样的 chain metadata；复合技能仓库还必须有 repo-level `WORKFLOW.md`。
8. 创建 Skill 后写入 `references/official-basis.md`，列出 upstream lock、contracts 和 applied rules。

## 输入推断

面向用户的必要输入只有两类：

- 用例：这个 skill 要稳定处理什么输入、产出什么结果。
- 边界：它不该做什么，尤其是否需要实时桌面控制、账号授权、MCP、hooks 或 app/widget runtime。

内部字段由本技能推断：

- `skill_name`：从用例提炼 kebab-case 名称。
- `description`：只写触发条件、关键词和负面边界。
- `display_name`：面向 UI 的中文短名。
- `source_strategy`：默认 `wrapper_overlay`；只有 `kun-create` 执行时才写入新 Skill。
- `host_support`：默认 Codex + Claude Code。
- `plugin_needed`：默认 no；命中 runtime bundle 需求时改为 yes 并阻断普通 Skill 创建。
- `proof_surface`：默认 `quick_validate + audit_skill`。
- `contracts`：默认 `codex,claude`。
- `repo_type`：默认 `standalone_skill`；新建或迁移一组技能时改为 `composite_skill_repo`。
- `state_machine`：默认 `chain-position`；`composite_skill_repo` 必须是 `WORKFLOW.md`，`runtime_repo` 可为 `runtime_lifecycle`。
- `registry_root`：自动发现 `kun-agent-registry`；找不到时阻断。
- `route_decision`：默认先要求 `official-adopt | official-overlay | kun-create | blocked` 之一。

缺少用户侧用例或边界时，最多问 1-3 个问题。缺少上游调研结论、合同文件、registry 或 upstream lock 时，直接 blocked，不先 scaffold。

## 用例边界示例：微信消息 Skill

如果用户说“创建一个帮我自动看微信的 skill”，先把能力边界落清：

- 普通 Skill 可以处理用户提供的微信导出文本、聊天记录片段、截图 OCR 文本或本地工具导出的消息。
- 普通 Skill 可以提炼待办、需求、风险、客户意图、回复建议和后续跟进清单。
- 普通 Skill 不直接控制微信客户端、不实时监听、不绕过登录/加密、不读取未授权数据。
- 如果用户要求实时桌面自动化、账号授权、后台监听、浏览器/桌面桥或 MCP 工具链，标记 `plugin_needed=yes`，停止创建 Skill 并交给 `plugin-manager`。

## Kun-create 创建步骤

1. 写一张最小设计卡：目标、输入、输出、边界、验证面、删除条件。
2. 写明为什么没有走 `official-adopt` 或 `official-overlay`。
3. 根据 contracts 判断资源分层：默认生成 `SKILL.md`、`agents/openai.yaml`、`references/official-basis.md` 和 `references/pilot-closed-loop.md`；只有确定性动作才加 `scripts/`。
   - 生成物必须写明 `invocation_policy: on_demand`。
   - 若需要 registry group，只能写 install-only group，并显式 `group_callable: false`。
   - 不创建 suite facade / orchestra / router，除非用户明确要求可调用 facade 或命中 plugin runtime exception。
4. 运行 `scripts/create_skill.py` 生成目录。
5. 立刻用 `skill-modify` 的 validator 检查新目录。
6. 需要写入 registry 时，更新 `../kun-agent-registry/registry.yaml` 和 `lock.yaml`；若当前没有权限或材料不足，输出 registry 待办。

## 内部脚手架命令

以下是本技能内部可以运行的命令，不是用户必须说出来的提示词：

```bash
python3 scripts/create_skill.py <skill-name> \
  --description "<只写触发条件的 description>" \
  --display-name "<中文展示名>" \
  --source-strategy wrapper_overlay \
  --invocation-policy on_demand \
  --repo-type standalone_skill \
  --state-machine chain-position \
  --proof-surface "quick_validate + audit_skill"
```

生成后必须跑：

```bash
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/quick_validate.py .agents/skills/<skill-name>
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/audit_skill.py .agents/skills/<skill-name>
```

## 输出契约

```text
创建结果：official-adopt | official-overlay | kun-create-created | blocked | needs-interview
路径：<新 skill 目录>
上游判断：<selected upstream or none> / <adopt | overlay | create> / <reason>
官方兼容：contracts / source_strategy / host_support / plugin_needed / proof_surface
链条合同：standalone 或 chain_id / position / consumes / produces / handoff_status / next_skill / proof_surface
状态机：repo_type / state_machine / WORKFLOW.md 或 runtime_lifecycle 要求
调用策略：atomic_skill=on_demand / group=install_only / group_callable=false / facade=<blocked|runtime-exception|user-requested>
生成文件：SKILL.md / agents/openai.yaml / references/official-basis.md / references/pilot-closed-loop.md / 可选 scripts
验证：已跑命令和结果
registry：已更新 / 待更新 / 不需要
小实验：pressure scenario 状态，默认 pending-user-pilot
```

## 资源

- `scripts/create_skill.py`：生成最小官方兼容 Skill 骨架。
- `references/chain-position.md`：本技能在 skill lifecycle 链条中的位置。
- `references/official-compatibility-decision-gate.md`：本技能本地官方兼容判断门禁，单独安装时也必须携带。
- `references/official-basis.md`：生成物 `references/official-basis.md` 的格式说明。
- `references/pilot-closed-loop.md`：新技能创建后的 pressure scenario 验收模板。
- `../../contracts/*.yaml`：创建器运行所需合同。单独安装 `skill-creator` 时必须同时带上。

## 本技能的 deletion-spec

- **触发删除条件**：当官方工具能稳定完成“上游调研、采用、overlay、Kun-owned fallback、deletion-spec、OpenAI 元数据和 pressure scenario”全链路时，本技能可删除。
- **禁用方式**：删除 `skills/skill-creator/`，并同步 `skill-registry.yaml`、registry included_skills 与验证命令。
- **卸载清单**：`SKILL.md`、`agents/openai.yaml`、`scripts/create_skill.py`、`references/official-compatibility-decision-gate.md`、`references/pilot-closed-loop.md`、`skill-registry.yaml` 中的 `skill-creator` 条目、registry/lockfile 中的验证记录。
