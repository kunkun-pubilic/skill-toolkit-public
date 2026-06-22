# 修复完成前验证模板

本文件由收敛扫描拆出，承载 `SKILL.md` 中不应默认注入的检查清单或命令模板。`SKILL.md` 保留流程和门禁；执行到对应步骤时再读取本文件。

### 5) 声称完成前先验证

```bash
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/quick_validate.py <target-skill-dir>
test ! -f <target-skill-dir>/scripts/audit_skill.py || python3 <target-skill-dir>/scripts/audit_skill.py <target-skill-dir>
python3 <kun-skill-toolkit>/skills/skill-modify/scripts/package_skill.py <target-skill-dir> --output-dir <dist-dir>
```

任一失败要修复后重跑。对于本次删除的每个文件名：

```bash
rg -n "<removed-file-or-path>" <target-skill-dir> || grep -RIn "<removed-file-or-path>" <target-skill-dir>
```

应无残留命中。

随后读 `references/pilot-closed-loop.md`。只要本轮修改会改变触发、流程或输出行为，就产出至少 1 个 pressure scenario，或生成可复制的新对话验证提示词。没有真实新对话证据时，结论只能写成 `pending-user-pilot`，不得写“行为已验证”。真实新对话测试交给 TASK-007。
