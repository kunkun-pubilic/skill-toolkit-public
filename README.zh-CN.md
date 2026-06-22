# Skill Toolkit 公开资料包

这是 Kun「Skill Toolkit」视频的公开资料包。

核心观点：

> Skill 不是把提示词存起来，而是把反复发生的判断、资料和机械动作，变成 Agent 可以调用、验证、维护的工作接口。

本仓库包含：

- 给观众看的资料索引；
- 本期视频的发布文案包；
- 一个已清理的 Skill 样例：`video-publish-copy-pack`；
- 用统一表达主干生成多平台文案的模板。

本仓库不包含私有治理 registry（注册表）、运行时 lock（锁文件）、原始视频素材、凭据、本机缓存、私有项目历史。

## 从这里开始

- [视频资料索引](docs/VIDEO_RESOURCE_INDEX.zh-CN.md)
- [Skill 设计笔记](docs/SKILL_DESIGN_NOTES.zh-CN.md)
- [Agent 安装提示词](docs/AGENT_INSTALL_PROMPT.zh-CN.md)
- [示例 Skill](skills/video-publish-copy-pack/SKILL.md)
- [本期发布文案样例](examples/publish-copy-pack.skill-toolkit-round15.md)

## 怎么理解 Skill

Prompt 解决这一次怎么说。Skill 解决下一次 Agent 怎么做：

```text
什么时候触发
  -> 读哪些资料
  -> 做哪些判断
  -> 哪些动作必须机械验证
  -> 输出什么可复用产物
```

本期公开的 `video-publish-copy-pack` 样例解决的是视频发布文案漂移问题：先写一条统一表达主干，再按平台字段适配，而不是给每个平台各写一套互相打架的文案。

## 许可

本仓库暂未添加开源许可证。当前请把它当作公开阅读和参考资料包；后续如果要允许复制、改造和再分发，会再补 license。

