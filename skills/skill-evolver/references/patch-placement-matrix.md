# 补丁落位矩阵

## 目的

按行为影响选择落位，不按“改哪里方便”选择落位。

## 决策矩阵

| 差分类型 | 主落位 | 次落位 | 说明 |
| --- | --- | --- | --- |
| 触发失配 | `SKILL.md` 文件头元数据 `description` | 无 | 触发规则必须在元数据可见。 |
| 流程僵化或缺口 | `SKILL.md` 既有流程章节 | `references/evolution-principles.md` | 先改旧逻辑，再考虑新增标题。 |
| 管理者角色/决策边界升级 | `SKILL.md` 核心理念 / 工作流 | `references/evolution-principles.md` | 角色定位与核心判断必须直接写在主技能。 |
| 大体量场景提示词 | `references/scenario-prompts.md` | `SKILL.md` 中的路由短句 | `SKILL.md` 保持精简导航。 |
| 调用后复盘得到的提示词 / 漏检点 | `references/*.md` | `SKILL.md` 中的路由短句 | 先抽象成可复用规则，再沉淀到参考资料。 |
| 实证排查得到的决策规则 / 低侵入优先边界 | `SKILL.md` 核心理念 / 工作流 | `references/scenario-prompts.md` | 若改变了以后如何比较方案、何时保守落地，必须写入主技能；具体采证提示再放参考资料。 |
| 需要确定性检查 | `scripts/*.py` | `SKILL.md` 中脚本入口 | 脚本调用必须显式写出。 |
| 调用后复盘得到的标准化重复步骤 | `scripts/*.py` | `SKILL.md` 中脚本入口 | 仅当步骤稳定、重复、可验证时才脚本化。 |
| 变体专属深度细节 | `references/*.md` | `SKILL.md` 中路由句 | 避免默认加载无关变体。 |
| 资源漂移 | `SKILL.md` 资源声明 | 删除过期文件 | 真源声明必须与文件系统一致。 |
| `contract-first` / 合并门禁语义 | shared core / 共享剧本 | `SKILL.md` 中升级指令 | 若影响多个技能、多个宿主、多个仓库，优先升到共享层。 |
| 确定性门禁 vs AI 建议 边界 | 共享剧本 / `SKILL.md` | `references/*.md` | 能机械验证的约束优先升共享规则；单技能只保留调用边界。 |
| anti-cheat amendment / retry 规则 | shared core / 共享剧本 | `SKILL.md` | 若规则改变“失败后允许做什么”，默认视为系统级行为。 |
| GitHub capability probe / `hard-vs-soft` 门禁语义 | 共享剧本 + planning 技能 | `references/*.md` | 若影响多个仓库的 合并门禁设计，优先放共享 GitHub 剧本与 `req-project-spec`。 |
| bootstrap sequencing / stacked PR policy | 共享剧本 + planning 技能 | `SKILL.md` + `references/*.md` | 先定义何时必须 bootstrap，再定义何时允许 stacked PR。 |
| UTF-8-safe boundary / PR body hash sync discipline | 共享剧本 + 技能参考资料 | `scripts/*.py` + `references/*.md` | 规则先上共享层，再在具体脚本或模板中落实。 |
| CI runner portability / 验证器 tool baseline | 共享剧本 + planning 技能 + execution 技能 | `references/*.md` + `scripts/*.sh` | 若验证器进入 required checks，必须把“runner 上能不能跑”升级成显式规则。 |
| shell-safe PR body generation | 共享 GitHub 剧本 + planning templates | `references/*.md` | 含反引号或表格的 PR body 优先文件模板生成，不靠 inline heredoc。 |
| 知识库引用漂移（笔记已更新但技能未同步） | `SKILL.md` 知识库依赖表 | `references/` 中引用旧内容的段落 | 先更新依赖表，再检查参考资料中是否硬编码了旧内容。 |
| 方法论级认知回灌 | 知识库（Obsidian）笔记 | `SKILL.md` 知识库依赖表 | 认知先写入知识库，技能只保留引用。 |

## 落位规则

1. 先重写受影响的既有区块。
2. 先检查现有 `references/`、`scripts/` 能否承载；只有不足时才新增文件。
3. 仅在无安全承载区块时才新增章节。
4. 提示词密集的场景细节不得直接堆在 `SKILL.md`。
5. 纯指导文本可解决时，不新增脚本。
6. 复盘收获必须先抽象、再落位，禁止直接存档原始对话。
7. 若收获来自真实实验，优先沉淀“根因 → 比较 → 推荐 → 边界”；临时文件路径只作为当次证据，不升格为长期技能资产。
8. 所有资源路径必须显式且有效。
9. 若同一规则将改变跨技能的 合并/验证 行为，先考虑升级到 共享核心/剧本，再决定是否在单个技能做薄适配。
