# 公开版边界说明

这个仓库是 Skill Toolkit 的 public edition，不是 Kun 内部治理系统的完整公开镜像。

## 包含

- 五个 Skill 生命周期入口：
  - `skill-adopter`
  - `skill-creator`
  - `skill-overlay`
  - `skill-modify`
  - `skill-evolver`
- 本地可运行脚本：
  - adopt / overlay / create / validate / audit / evolve 相关脚本
- `contracts/`：
  - Agent Skill 基础结构；
  - Codex 兼容；
  - Claude Code 兼容；
  - Kun 风格的验证和 deletion-spec 约束。
- `WORKFLOW.md` 和 `skill-registry.yaml`：
  - 说明这些 Skill 的关系和安装顺序。

## 不包含

- Kun 私有 `kun-agent-registry`；
- 私有 upstream lock；
- 本机 `.agents` / `.claude` cache；
- 未公开视频素材；
- 飞书资料页；
- 私有项目历史、客户材料和凭据。

## 没有私有 registry 时怎么做

使用 standalone 模式：

- `skill-adopter` 仍然先找官方或成熟上游；
- 缺少 `dokobot`、`gh` 或 `npx skills` 时，把它写成 evidence gap；
- `skill-creator` 使用 `--public-standalone` 创建 Skill；
- 创建结果不能声称已经完成官方锁定，只能说使用了 public standalone evidence；
- 后续可以补上你自己的 registry、upstream snapshot 或 lockfile。

## 为什么不直接公开整个私有仓

私有仓里包含面向 Kun 自己工作流的 registry、缓存、历史决策和本地运行时约束。观众真正需要的是可复用的生命周期方法和 Skill 文件，而不是整套私有治理面。

因此公开版做了三件事：

1. 保留核心 Skill 和脚本。
2. 去掉视频发布样例、私有 registry 和本地缓存。
3. 给没有 Kun 环境的用户补 standalone 使用方式。
