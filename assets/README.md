# 图片资产说明

本目录存放 README 和 GitHub 社交预览可用的图片资产。

## 文件

| 路径 | 用途 |
|---|---|
| `brand/logo.png` / `.svg` | 仓库 logo。 |
| `brand/banner.png` / `.svg` | README 首屏 banner。 |
| `brand/social-preview.png` / `.svg` | GitHub social preview 候选图。 |
| `workflow/skill-lifecycle-workflow.png` / `.svg` | README 中的 Skill 生命周期图。 |
| `workflow/skill-lifecycle-workflow.mmd` | Workflow 图的 Mermaid 源。 |
| `demo/customer-message-digest-demo.png` / `.svg` | README 中的最小 demo 图。 |

## 生成方式

当前图片由本仓脚本生成：

```bash
node scripts/generate-readme-assets.mjs
```

脚本会生成 SVG 源文件，并用本机 Chrome headless 渲染 PNG。

## image-cli 记录

本轮先检查并尝试使用了 `image-cli`。CLI 可用，但当前 `fal` provider 配置缺少 `baseUrl`，真实生成未发出外部调用。为了不阻塞 README 视觉改造，本轮使用本地可复现的 SVG/PNG 生成方式。

```text
image-cli doctor --agent --json     # pass
image-cli generate ... --provider fal ...  # failed before external call: missing baseUrl
```

## 边界

- 本目录不包含视频资产。
- 本目录不包含真实客户材料、凭据或未公开视频素材。
- 如果后续修好 image-cli provider，可以替换 `brand/` 里的视觉风格图，但 workflow/demo 图建议继续保持可复现。
