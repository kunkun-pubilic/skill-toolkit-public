# 公开仓库标准

这份标准用于 Skill Toolkit Public Pack，也可以作为 Kun 后续公开资料仓的默认模板。

目标不是把仓库做得复杂，而是让第一次打开 GitHub 的读者能快速判断三件事：

1. 这个仓库解决什么问题。
2. 我怎么安装、运行和验证。
3. 哪些内容是公开版，哪些内容不在公开边界内。

## 首屏标准

README 首屏需要直接给出：

- 一句话定位：public standalone Skill lifecycle toolkit。
- 适用对象：Codex / Claude Code 用户，以及想把重复工作沉淀成 Skill 的人。
- 核心价值：创建、采用、overlay、修复、演化 Agent Skills。
- 快速开始：clone、复制到 `.agents/skills` 或 `.claude/skills`、运行验证。
- 公开边界：私有 registry、缓存、客户材料和未公开视频素材不在仓库内。

不要把首屏写成项目历史、内部复盘或视频脚注。视频来源可以保留，但读者第一眼需要看到可用价值。

## 双语标准

- 中文为主：`README.md` 承载完整中文首屏和安装路径。
- 英文为辅：`README.en.md` 承载英文入口。
- 两种语言的信息结构保持一致；英文可以更短，但不能缺少安装、验证和公开边界。

## 安装标准

公开仓默认用户是空系统：没有 Kun 的私有 registry，没有本机 cache，也不需要先理解内部治理系统。

公开仓至少给三条路径：

- Codex project：复制到 `.agents/skills`。
- Claude Code project：复制到 `.claude/skills`。
- Public standalone creation：`skill-creator --public-standalone` 示例。

每条路径必须配验证命令。只写“复制过去即可”不够。

## 示例标准

公开仓至少保留一个 public-safe demo：

- 不含真实客户材料、私有路径、未公开视频、凭据或内部缓存。
- 用一个普通读者能理解的任务，例如整理客户聊天记录。
- 展示输入、输出、非范围、验证命令和 Agent 调用方式。

## 图片资产标准

公开仓应直接包含 README 所需的图片资产：

- logo；
- banner；
- social preview 候选图；
- workflow 图；
- demo 图；
- 可维护源文件，例如 SVG 和 Mermaid。

品牌视觉（logo、banner、social preview）优先用图片模型生成源图，再由本地脚本做裁切、文字和 badge 排版。仓库里的中文标题、安装命令、workflow 和 demo 文案不要交给图片模型生成，避免乱码和不可复现。

本期不放视频资产，也不做 GIF。图片资产要有 `assets/README.md` 说明来源、生成方式和边界。

## Discoverability 标准

GitHub description 推荐：

```text
Public standalone Skill lifecycle toolkit for creating, adopting, overlaying, repairing, and evolving Agent Skills across Codex and Claude Code.
```

推荐 topics：

```text
agent-skills, skill-md, codex, claude-code, ai-agents, prompt-engineering, workflow, developer-tools, skills, skill-creator
```

## 公开边界标准

公开仓不得包含：

- 私有 registry 和 upstream lock。
- 本机 `.agents` / `.claude` cache。
- 客户材料、内部会议材料、飞书资料页或凭据。
- 未公开视频素材。
- 必须依赖 Kun 私有环境才能跑通的承诺。

公开版缺少私有能力时，写成公开版边界，不要复制内部材料补洞。

## 验收清单

- [ ] README 首屏讲清定位、对象、安装、验证和边界。
- [ ] 中文主文档和英文辅助文档都存在。
- [ ] 至少一个 public-safe demo 存在。
- [ ] README 首屏不把私有 registry 写成用户安装前提。
- [ ] logo、banner、social preview、workflow 图、demo 图都存在。
- [ ] 不包含视频资产。
- [ ] repo description 和 topics 面向搜索优化。
- [ ] 验证命令可在公开仓根目录运行。
- [ ] PR 模板包含 public boundary check。
