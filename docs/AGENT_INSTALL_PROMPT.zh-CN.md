# Agent 安装 / 使用提示词

把下面这段发给你的 Agent，让它阅读本仓库并使用公开样例 Skill。

```text
你要阅读这个 GitHub 仓库：
https://github.com/kun-agent-system/skill-toolkit-public

目标：
理解 Agent Skill 不是高级 prompt，而是一种可维护的工作接口。重点阅读：

1. README.zh-CN.md
2. docs/VIDEO_RESOURCE_INDEX.zh-CN.md
3. docs/SKILL_DESIGN_NOTES.zh-CN.md
4. skills/video-publish-copy-pack/SKILL.md
5. skills/video-publish-copy-pack/references/publish-copy-spine.md
6. skills/video-publish-copy-pack/references/platform-adapters.md
7. skills/video-publish-copy-pack/templates/publish-copy-spine.yaml

任务：
基于 `video-publish-copy-pack` 的结构，帮我判断我自己的某个重复工作流是否适合做成 Skill。

输出：
- 这个工作流是否值得做成 Skill；
- 触发边界；
- 需要放进 references 的资料；
- 需要放进 scripts / tools / checker 的机械动作；
- 第一个最小可用 SKILL.md 草稿。

约束：
不要上传、发布、付费、删除或操作任何外部账号。
不要编造资源链接。
能机械验证的地方，优先建议机械验证。
```

