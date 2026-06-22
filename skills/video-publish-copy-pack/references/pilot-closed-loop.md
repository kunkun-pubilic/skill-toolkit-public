# 新技能 pressure scenario 闭环

用于验证新建 Skill 是否真的改善用户可感知行为。没有真实新对话证据时，状态只能写 `pending-user-pilot`。

```text
待测技能：<技能名称和路径>
创建目标：<这个技能要稳定解决什么判断流程>
官方依据：references/official-basis.md
测试提示词：<真实用户风格的小任务>
预期行为：
- <新版技能必须自然触发>
- <新版技能必须执行的流程或脚本>
- <新版技能必须避免的相邻误触发>
当前状态：通过 / 部分通过 / 失败 / pending-user-pilot
```
