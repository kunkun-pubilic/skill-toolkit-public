---
name: skill-adopter
description: 当用户要新建、改造、迁移、替换、拉取、安装、锁定或更新 Agent Skill 时，先用本技能调研官方/成熟上游并生成 source card。触发关键词：拿来主义 / adopt skill / 拉取官方 skill / 安装上游 skill / 技能改造 / 新建 skill / 迁移 skill / skills-lock。没有可用上游时才交给 skill-creator。
---

# Skill Adopter

## 角色

本技能是所有 Skill 生命周期动作的默认前门。无论用户要新建、改造、迁移、替换、采用、overlay、修复还是更新 Skill，都先从真实需求出发调研官方或成熟上游；能直接用就走 `official-adopt`，基本可用但需要 Kun 约束时交给后续 `official-overlay`，没有合适上游时才交给 `skill-creator` 或 `skill-modify`。

核心目标不是重写官方 Skill，也不是把当前本地缓存当作来源，而是先找到并分析可维护的前置源，再把上游 Skill 可复现地拉下来、锁住、验证，并留下 GitHub 可审计证据。

## Public Edition Note

这个公开版可以在没有 Kun 私有 registry、DOKO 或本机缓存的环境里使用。缺少 `dokobot`、`npx skills` 或 `gh` 时，不要阻断整件事；把缺失工具写进 source card 的 evidence gap，再用可用的 GitHub、网页、手动阅读和本地文件验证继续推进。安装目标默认仍是 `.agents/skills` 或 `.claude/skills`，`skills-lock.json` 是本地可复现证据，不依赖私有组织仓库。

## 方法调用

```text
/skill-adopter(request, source?, skill_path?, target_root?, mode?)
```

## 研究优先原则

只要任务涉及 Skill 生命周期，就先研究，不直接创建或改造：

- 新建 Skill：先找官方/厂商/成熟社区是否已有同类能力；没有可用上游才进入 `kun-create`。
- 改造旧 Skill 或旧 Plugin：先把旧能力拆成真实需求，再用 DOKO local / GitHub / skills registry 找候选上游；旧本地内容只作为需求样本，不作为真理源。
- 迁移本地旧资产：先为每个旧能力生成 source card；确认替代源、覆盖度和 lock 策略后再进入 registry。
- 修复或增强已有 Skill：先确认来源类型；若是上游能力缺 Kun 边界，走 overlay，不直接改 upstream body。

“官方源”不是指本机已经安装的 Skill 名单。官方源或成熟源必须经过调研和阅读确认，至少记录 repo、skill path、license/来源边界、维护信号、覆盖度和是否需要 overlay。DOKO local 是找官方源的优先入口：用 `dokobot read --local '<url>'` 读取搜索结果页、X/Twitter、Reddit 和高质量 AI skill 社区页；不要把远端 `dokobot search` 的 API-key 限制误判为 DOKO 不可用。

DOKO local 的来源优先级：

1. 官方/厂商和可锁定 GitHub upstream：最终 adoption/overlay 的主证据。
2. X/Twitter：找最新作者、发布帖、维护者讨论和社区实际使用反馈。
3. Reddit：找踩坑、替代方案、真实用户评价和被反复提到的候选。
4. AI skill 社区/市场：如 `skills.sh`、`claudskills.com`、`claudemarketplaces.com`、`awesomeskill.ai`、`mcpmarket.com/tools/skills`、`lobehub.com/skills`，用于补候选池和热度信号。

X、Reddit、社区市场只能作为 discovery lead；不能直接证明 `official-adopt`。任何候选必须回到 repo、`SKILL.md`、license、维护信号、commit/tag/tree hash 和本地 validator 后再定路线。

近期调研门：

- 对非平凡采用/迁移/改造任务，先做 DOKO 调研，再写 adoption plan 或 registry draft。
- DOKO 调研要覆盖两类事实：稳定来源（官方文档、GitHub repo、`SKILL.md`、license、commit）和近期社区信号（近 30 天 web、X/Twitter、Reddit、Hacker News、YouTube、GitHub issues/discussions/PR）。
- 近期社区信号用于发现“现在大家真的在用什么、踩什么坑、维护者最近在讨论什么”；它不能替代官方源和本地 validator。
- 如果近期来源互相矛盾，source card 要记录冲突，并优先找 GitHub commit、issue/PR、release note 或官方文档做 tiebreaker。
- 如果某个平台登录、反爬或 DOKO 不可读，记录为 scoped evidence gap；不要把缺口解释成“没有相关讨论”。

GitHub 健康门：

- `stars` / marketplace `installs` 只表示采用热度，不等于可复用。
- `pushedAt` 是维护信号主证据；`updatedAt` 可能由 star、issue、metadata 触发，只作为辅助。
- 必须记录 `stars`、`forks`、`openIssues`、`license`、`archived/disabled`、`defaultBranch`、`pushedAt`、`updatedAt` 和 canonical repo redirect。
- 社区源只有同时满足清晰可复用 license、近 90 天有 push、且有真实采用信号，才可标 `tier1-mature`；否则保持 `tier2-community` 或 `needs-review`。
- 无 license、`NOASSERTION`、`Other` license、archived/disabled、长期无 push 的仓库不能直接 `official-adopt`，即使 `skills.sh installs` 或 stars 较高。

## 链条合同门

只要请求中的能力属于一个多步骤 workflow，source card 必须记录它在链条里的位置，而不是只记录“这个 Skill 能做什么”。

最小字段：

```yaml
repo_type: standalone_skill | composite_skill_repo | runtime_repo
workflow_id: <repo workflow id or standalone>
state_machine_required: true | false
chain_id: <workflow id or standalone>
position: <this step>
consumes: <up游 artifact>
produces: <down游 artifact>
handoff_status: <ready/needs/block 状态>
next_skill: <下游 skill or none>
proof_surface: <命令、文件、锁或运行证明>
```

如果上游官方 Skill 没有链条合同，但 Kun 的使用场景需要它，路线应标为 `official-overlay` 或 `kun-create`；不要用聊天记录、个人记忆或旧 plugin 路由代替合同。

当候选是 suite、旧插件、multi-skill repo 或同领域一组技能时，默认 `repo_type=composite_skill_repo` 且 `state_machine_required=true`。采用前必须确认 repo-level `WORKFLOW.md` 已存在或作为 overlay/creation 待办；registry 只能索引 workflow，不复制长流程。

## GitHub Suite 整理边界

当 GitHub 候选、旧插件或上游仓库包含多个技能、目录或 workflow step 时，先整理 capability map，再决定每个 atomic Skill 的路线；不要把 repo/suite 名称直接注册成可调用 facade。

最小 capability map：

```yaml
capability: <real ability>
upstream_path: <repo path or local old skill path>
source_strategy: <official-adopt | official-overlay | kun-modify | kun-create | archive | defer>
installability: <single-skill | group-install-only | runtime-preflight-sensitive | blocked>
invocation_policy: <on-demand | install-only | runtime-exception | user-requested-facade>
proof_surface: <validator/smoke/lock/manual-review>
```

整理规则：

- 每个真实能力独立 source card / registry draft；不要只给 suite 写一张总卡后直接 promote。
- registry `group` 只能代表批量安装便利，必须保持 `callable: false`。
- `orchestra`、`router`、`facade` 默认 `archive` 或 `defer`；只有 runtime bundle 或用户明确要求中央路由时才进入候选。
- workflow 顺序写在 chain metadata 里；调用仍按 atomic Skill 的 `description` 按需触发。
- source card 必须记录未迁移项的原因，例如 `runtime-preflight-sensitive`、`later-batch`、`archive` 或 `reference-only`。

## 四路线判断

1. `official-adopt`：官方或可信上游已经满足用例。
   - 读取上游 source tree：`SKILL.md`、`references/`、`scripts/`、`assets/`、templates、fixtures、schemas 和 license。
   - 安装到项目 `.agents/skills` 或指定目标；如果上游脚本/资产是能力的一部分，确认它们作为本地 `scripts/` / `assets/` 可用并被 validator 覆盖。
   - 写入 `skills-lock.json`，记录 source、skill path、ref/commit、tree hash、关键文件 hash、payload roles 和验证命令。
   - 不改上游 Skill 内容。
2. `official-overlay`：上游基本满足，但缺 Kun 边界或宿主兼容层。
   - 先按 `official-adopt` 拉取和锁定。
   - 只记录需要叠加的 Kun 差异，不把 Kun 改动混进 upstream source。
   - 若 upstream scripts/assets 需要运行，交给 overlay 生成本地投影；若无法投影，标记 `blocked_until_projected`。
   - 交给后续 `skill-overlay` 处理。
3. `kun-modify`：目标是修复或改造 Kun-owned / fork / vendor_copy Skill。
   - 先用 source card 说明为什么不能采用或 overlay 上游。
   - 再交给 `skill-modify` 执行最小修复。
4. `kun-create`：没有可用上游。
   - 不伪装成官方采用。
   - 交给 `skill-creator` 从零创建。

## 执行流程

1. 先把用户需求或旧 Skill/Plugin 拆成 1-5 个真实能力问题；不要直接拿旧技能名当答案。
2. 先做上游调研：优先官方或厂商维护仓库，其次高维护成熟社区仓库；只看 README 不够，必须读取候选 `SKILL.md`，并通过 GitHub 健康门记录 repo 可维护性。
3. 调研阶段先运行 `scripts/research_skill.py`，生成 `research/source-cards/<query>.md`。对非平凡的新建、改造、迁移任务，必须优先补一轮多源 DOKO local：`dokobot read --local '<url>'` 读取 general web、recent 30-day web、X/Twitter、Reddit、Hacker News、YouTube、GitHub issues/discussions/PR 和 AI skill community 来源；只有 CLI 不存在、本地浏览器不可用、目标站点登录/反爬导致不可读，或用户明确不走 DOKO 时，才记录为 scoped evidence gap。
4. 用 `scripts/source_card_to_registry.py` 把候选转成 registry draft；状态保持 `candidate_needs_skill_md_review`，不要冒充已采用。
5. 读取 source card、registry draft 和候选 `SKILL.md` 后，输出采用判断：`official-adopt | official-overlay | kun-modify | kun-create | blocked`。
6. 若能力属于 workflow 链条，确认 source card 已写明 `repo_type`、`workflow_id`、`state_machine_required`、`chain_id`、输入 artifact、输出 artifact、交接状态、下游技能和 proof surface；缺失时先补卡再推进。
   - `composite_skill_repo` 必须有 repo-level `WORKFLOW.md` 或明确待补，不能只给单个 Skill 写 chain position。
   - `runtime_repo` 可以用 `runtime_lifecycle`，但必须记录 install/check/distribution/rollback 的 proof surface。
   - `standalone_skill` 可保持 `chain_id: standalone`。
7. 若进入 `official-adopt`，运行 `scripts/adopt_skill.py`。
8. 安装后立即跑目标仓库的 `quick_validate.py` 和 `audit_skill.py`；若目标仓库没有 validator，使用当前 `kun-skill-toolkit/skills/skill-modify/scripts/` 下的 validator。
9. 若采用后发现需要 Kun 规则，停止直接改 upstream body，记录 overlay 待办并交给 `skill-overlay`。
10. 若没有合适上游，source card 必须说明已查过的候选和拒绝原因，再交给 `skill-creator` 或 `skill-modify`。

## 内部脚本

调研候选：

```bash
python3 scripts/research_skill.py "<skill need or query>" \
  --research-dir research/source-cards
```

调研脚本会调用可用工具：

- `npx skills find <query>`：发现 skills.sh / Skills CLI 候选。
- `gh search repos "<query> agent skills SKILL.md"`：补充 GitHub 仓库候选，并采集 stars、forks、open issues、license、archived/disabled、default branch、latest push、latest update 等健康信号；对 `skills.sh` 候选还会反查 GitHub repo health。
- `dokobot read --local <url>`：用本机浏览器做多源 DOKO local 阅读，使用 `--use-doko` 时启用；脚本会覆盖 general web、recent 30-day web、X/Twitter、Reddit、Hacker News、YouTube、GitHub issues/discussions/PR 和 AI skill community focused query，这是 official source discovery 的优先入口。

对旧 Skill/Plugin 改造，调研不应只用一个宽泛查询。推荐按下面方式拆查询：

```text
<旧技能名> agent skill SKILL.md
<真实能力英文名> agent skill official
<真实能力英文名> Claude Code skill
<真实能力英文名> Codex skill
<真实能力英文名> GitHub agent skill
```

调研脚本只输出 source card，不直接安装；采用前必须读取候选 `SKILL.md`。DOKO 发现的 URL 也必须进入 source card，而不是停留在聊天记录里。

生成 registry 草案：

```bash
python3 scripts/source_card_to_registry.py \
  research/source-cards/<query>.md \
  --rank 1 \
  --draft-dir registry-drafts
```

如果已经确认上游 skill path 和 ref：

```bash
python3 scripts/source_card_to_registry.py \
  research/source-cards/<query>.md \
  --rank 1 \
  --skill-path <path/to/skill> \
  --ref <tag-or-commit-sha>
```

registry draft 是 handoff，不等于采用完成；只有读过 `SKILL.md` 并安装验证后，才把状态升级为 adopted。

采用已确认上游：

```bash
python3 scripts/adopt_skill.py \
  --source <git-url-or-local-repo> \
  --skill-path <path/to/skill> \
  --target-root .agents/skills \
  --lock-file skills-lock.json
```

脚本做四件事：

- 校验 source 里的 `SKILL.md` 存在。
- 复制该 skill 目录到目标 skill root。
- 计算安装目录的 deterministic tree SHA-256 和每个文件的 SHA-256。
- 更新 `skills-lock.json`。

锁文件格式见 `references/adoption-lock-format.md`。

## 输出契约

```text
需求：<新建/改造/迁移/修复/更新，以及旧资产路径或用户请求>
调研：<source card path；DOKO/GitHub/skills registry 覆盖情况>
候选：<repo/url/path/ref，覆盖度和来源等级>
路线：official-adopt | official-overlay | kun-modify | kun-create | blocked
上游：<repo/url/path/ref>
安装路径：<target skill dir>
锁定：<commit/ref/tree_sha256/skills-lock.json>
payload：<rule_text/executable_script/runtime_asset/fixture/evidence_only/blocked_until_projected>
验证：<quick_validate/audit 结果>
链条合同：<standalone 或 chain_id/position/consumes/produces/handoff_status/next_skill/proof_surface>
状态机：<repo_type/workflow_id/state_machine_required/WORKFLOW.md 或 runtime_lifecycle>
调用策略：<on-demand atomic skill / install-only group / runtime exception / user-requested facade>
下一步：完成 | 交给 skill-overlay | 交给 skill-modify | 交给 skill-creator | needs-user
```

## 资源

- `scripts/research_skill.py`：调研官方/可信上游候选并生成 source card。
- `scripts/source_card_to_registry.py`：把 source card 候选转成 registry draft。
- `scripts/adopt_skill.py`：从 Git 或本地 repo 采用并锁定指定 Skill。
- `references/source-card-template.md`：source card 字段和人工判断清单。
- `references/adoption-lock-format.md`：`skills-lock.json` 的字段说明和质量边界。

## 本技能的 deletion-spec

- **触发删除条件**：当 `npx skills`、GitHub skill tooling 或官方 Codex/Claude 工具已经能稳定完成“调研候选、拉取、锁定、安装、验证、跨宿主 registry 记录”全链路时，本技能可删除或降级为 thin wrapper。
- **禁用方式**：删除 `skills/skill-adopter/`，并同步 `skill-registry.yaml` 中的 `skill-adopter` 条目和 `install_order`。
- **卸载清单**：`SKILL.md`、`scripts/adopt_skill.py`、`references/adoption-lock-format.md`、`agents/openai.yaml`、`skill-registry.yaml` 中的默认前门配置。
