# 图片资产说明

本目录存放 README 和 GitHub 社交预览可用的图片资产。

## 文件

| 路径 | 用途 |
|---|---|
| `brand/logo.png` / `.svg` | 仓库 logo。 |
| `brand/banner.png` / `.svg` | README 首屏 banner。 |
| `brand/social-preview.png` / `.svg` | GitHub social preview 候选图。 |
| `brand/logo-ai-source.png` | GPT Image 2 生成的 logo 源图。 |
| `brand/banner-ai-source.png` | GPT Image 2 生成的 banner 源图。 |
| `workflow/skill-lifecycle-workflow.png` / `.svg` | README 中的 Skill 生命周期图。 |
| `workflow/skill-lifecycle-workflow.mmd` | Workflow 图的 Mermaid 源。 |
| `demo/customer-message-digest-demo.png` / `.svg` | README 中的最小 demo 图。 |

## 生成方式

Brand 资产采用两段式：

1. 用 GPT Image 2 生成 `brand/logo-ai-source.png` 和 `brand/banner-ai-source.png`。
2. 用本仓脚本裁切、叠加清晰文字，并输出 README 使用的 PNG。

```bash
node scripts/generate-readme-assets.mjs
```

脚本会生成 SVG 源文件，并用本机 Chrome headless 渲染 PNG。Workflow 图和 demo 图仍由脚本生成，保证文字清晰、可复现。

## image-cli 记录

本轮先检查并尝试使用了 `image-cli`。CLI 可用，`fal` provider 也能看到 `FAL_KEY`，但当前 adapter 的真实生成路径还有两个问题：

- 默认 `fal` provider 缺少 `baseUrl`，会在外部调用前失败。
- 用临时 endpoint 配置后，真实调用返回 401；判断是当前 CLI 固定认证头与 fal 官方接口不匹配。

所以本轮生成源图时使用 fal 官方 SDK 调用 `openai/gpt-image-2`。落盘后的图片继续用 `image-cli verify` 做本地格式和尺寸验证。

```text
image-cli doctor --agent --json       # pass
image-cli providers --agent --json    # fal configured
image-cli generate ... --provider fal # blocked by provider adapter config/auth
image-cli verify assets/brand/*.png   # pass
```

## 边界

- 本目录不包含视频资产。
- 本目录不包含真实客户材料、凭据或未公开视频素材。
- 后续修好 image-cli 的 fal adapter 后，可以把源图生成也收回到 `image-cli generate`。
- Workflow/demo 图建议继续保持脚本生成，避免图片模型生成不可读文字。
