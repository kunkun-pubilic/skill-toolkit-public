# 差分契约

## 目的

用这个契约把“新增需求”或“调用后复盘收获”转换成可打补丁、可验证的差分。

## 契约模板

编辑前先完整填写：

```yaml
delta_id: "YYYYMMDD-<short-name>"
target_skill: "<absolute-or-relative-path>"
delta_source:
  mode: "new-requirement | conversation-harvest"
  evidence_inputs:
    - type: "user-request | conversation-summary | prompt-snippet | script-opportunity | validation-failure"
      note: "<本次 delta 的证据来源>"
  evidence_shape:
    root_cause_signals:
      - "<若来自真实排查：哪些事实支撑了根因判断>"
    before_after_artifacts:
      - "<改前/改后证据来源；若只有实验文档或截图，也在这里写清>"
    alternatives_tested:
      - option: "<尝试过的方案>"
        result: "<效果如何>"
        decision: "<采用 / 不采用，以及原因>"
intent:
  problem: "<缺什么或哪里坏了>"
  expected_behavior: "<更新后用户可观察到的行为>"
trigger:
  new_user_phrases:
    - "<示例触发短语 1>"
    - "<示例触发短语 2>"
  trigger_precision_notes: "<触发边界或消歧说明>"
scope:
  in_scope:
    - "<需要变更的能力或章节>"
  out_of_scope:
    - "<明确非目标>"
risk:
  fragile_points:
    - "<容易回归的步骤或行为>"
  failure_modes:
    - "<更新可能怎么失败>"
placement_hypothesis:
  rewrite_sections:
    - "<需要重写的既有区块>"
  new_sections_if_needed:
    - "<仅在重写不足时才新增的区块>"
resources:
  add_or_update:
    - "references/<file>.md"
    - "scripts/<file>.py"
  remove:
    - "<废弃文件>"
harvest:
  references_candidates:
    - observation: "<来自对话的提示词/注意点>"
      destination: "references/<file>.md"
  script_candidates:
    - routine: "<可标准化的重复步骤>"
      destination: "scripts/<file>.py"
  ignore_or_keep_ephemeral:
    - "<只适用于本次上下文、不应资产化的内容>"
upstream:
  knowledge_base_refs:
    - path: "<知识库笔记路径>"
      status: "unchanged | updated | new | removed"
      sync_action: "no-op | update-skill-ref | add-ref | remove-ref"
  route_to_kb:
    - insight: "<值得回灌的方法论级认知>"
      target_note: "<目标笔记路径>"
      reason: "<为什么应住在知识库而非 skill>"
verification:
  commands:
    - "<验证命令 1>"
    - "<验证命令 2>"
  before_after_evidence:
    baseline_source: "<改前结果来源>"
    candidate_source: "<改后结果来源>"
claim_boundary:
  done_now:
    - "<本轮已经完成并可声称完成的事项>"
  not_done_yet:
    - "<尚未正式落地/仍待人工确认的事项>"
  wording_rule: "<若只完成诊断或实验，不得写成已修复>"
success_criteria:
  user_visible:
    - "<可观察到的改进>"
  structural:
    - "<无 append-only，且无过期资源>"
```

## 评审问题

1. 预期行为是否具体且可观察？
2. 是否先判断了这是新增需求还是调用后复盘？
3. 补丁落位是否优先重写受影响区块？
4. 复盘收获是否正确区分为 `SKILL.md` / `references/` / `scripts/` / 忽略？
5. 资源增删是否写得足够明确？
6. 验证命令是否真的在检验声称改进？
7. 若差分来自真实实验，是否记录了根因信号、替代方案对比与取舍原因？
8. 是否明确区分了”已验证建议”与”已正式落地修复”？
9. 若目标技能声明了知识库依赖，依赖表是否需要更新？
10. 本次演化中是否有认知收获应回灌知识库而非留在技能？
