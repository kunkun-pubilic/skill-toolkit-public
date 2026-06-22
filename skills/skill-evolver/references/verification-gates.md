# 验证门控

## 目的

定义“声称增量更新完成”之前必须通过的检查。

## 门控集合

1. 差分完整性：
   - 差分契约字段填写完整。
   - 已明确 `delta_source.mode`，并记录请求或复盘证据来源。
2. 落位正确性：
   - 受影响区块已按需重写。
   - 新收获已正确分流到 `SKILL.md` / `references/` / `scripts/` / 忽略。
3. 反追加门：
   - 当逻辑应整合时，不得出现 append-only 模式。
4. 资源完整性：
   - 声明的资源文件必须存在。
   - 存在的资源文件必须被声明。
   - 不得存在悬空资源路径引用。
5. 占位符卫生：
   - 最终产物不得含 TODO/TBD/template 残留。
6. 触发完整性：
   - 文件头元数据 `description` 只写何时触发、触发关键词和负面边界。
   - 不把流程摘要、输出契约、验证门或能力清单写进 `description`。
7. 资产化质量：
   - 复盘收获只有在可复用、可复现、可解释时才允许进入技能资产。
   - 一次性上下文、客户专属噪音、临时调试命令不得误升格。
8. 对照证据：
   - 至少保留一组“改前 vs 改后”结果，防止主观误判。
9. 实证型复盘完整性：
   - 若差分来自真实排查或方案实验，必须保留根因证据与至少一组替代方案比较证据。
10. 声明边界卫生：
   - 若本轮只完成诊断、实验或候选方案排序，不得声称“已修复/已正式交付”；必须明确写成待正式落地或待回写。
11. 升层判断：
   - 若本轮变化会改变跨技能、跨宿主或跨仓库的 合并语义，必须说明为什么它应留在技能层，或为什么应升级到 共享核心/剧本。
12. 确定性优先：
   - 若变化涉及 `contract-first`、`skip != pass`、`uncertain != pass`、AI 建议 边界，必须显式说明哪些部分能机械验证，哪些只能 advisory。
13. 上游一致性：
    - 若目标技能声明了知识库依赖，每条引用路径指向的笔记必须存在。
    - 若笔记更新时间晚于技能最后修改，必须在输出中说明是否需要同步。
    - 若差分 contract 的 `route_to_kb` 非空，必须在输出契约中列出回灌建议。

## 命令清单

运行 `skill-modify` 的基础校验：

```bash
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/quick_validate.py <target-skill-dir>
```

运行本技能的增量审计：

```bash
python3 scripts/audit_incremental_update.py --before <baseline-skill-dir> --after <updated-skill-dir>
```

若这次属于调用后复盘沉淀，建议在编辑前输出规划结果，确认资产分类：

```bash
python3 scripts/build_patch_plan.py --skill-dir <target-skill-dir> --change-text "<演化描述>" --mode conversation-harvest
```

可选：交付前打包可用性检查：

```bash
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/package_skill.py <target-skill-dir> --output-dir <dist-dir>
```

可选：对已删除项做残留搜索：

```bash
rg -n "<removed-file-or-path>" <target-skill-dir>
```

## 完成声明规则

满足以下条件前，不得声称完成：

1. 上述命令已执行。
2. 结果已写入证据。
3. 已提供至少一组改前/改后对照证据。
4. 若属于调用后复盘沉淀，已给出“观察 → 落位”的资产化说明。
5. 若没有真实新对话证据，状态写为 `pending-user-pilot`，并给出可交给 TASK-007 的 pressure scenario。
6. 剩余阻塞项已明确列出。


## 试运行后新增核对项

- 若本轮变化涉及 GitHub 合并门禁，先确认当前结论是 `hard`、`hard-possible` 还是 `soft`，不要混写。
- 若脚本比较 changed files、evidence paths、plan binding，至少补一组 UTF-8 / 非 ASCII 路径场景。
- 若流程使用 stacked PR，验证证据中要写清 parent PR、base branch，以及 checks 是否真的对 feature branch 生效。
- 若 PR body 包含 `plan_path`，验证时要检查 body 与仓内活跃 plan 是否同步，而不是只看字段存在。
