import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

function write(path, content) {
  ensureDir(dirname(path));
  writeFileSync(path, content);
}

function svgFrame({ width, height, body, bg = "#fbfbf7" }) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <rect width="${width}" height="${height}" fill="${bg}"/>
  ${body}
</svg>
`;
}

function render(svgPath, pngPath, width, height) {
  const htmlPath = `${pngPath}.html`;
  write(
    htmlPath,
    `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;width:${width}px;height:${height}px;overflow:hidden;background:white;}img{display:block;width:${width}px;height:${height}px;}</style></head><body><img src="${pathToFileURL(svgPath).href}"></body></html>`,
  );
  execFileSync(chrome, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    `--window-size=${width},${height}`,
    `--screenshot=${pngPath}`,
    pathToFileURL(htmlPath).href,
  ], { stdio: "ignore" });
}

function pngDataUri(relativePath) {
  const imagePath = resolve(root, relativePath);
  if (!existsSync(imagePath)) return "";
  return `data:image/png;base64,${readFileSync(imagePath).toString("base64")}`;
}

const colors = {
  ink: "#161616",
  muted: "#5f6368",
  line: "#d9ded8",
  cyan: "#2b8cbe",
  green: "#2f9e44",
  yellow: "#f2b705",
  red: "#d9480f",
  blue: "#235789",
  white: "#ffffff",
};

const aiLogo = pngDataUri("assets/brand/logo-ai-source.png");
const aiBanner = pngDataUri("assets/brand/banner-ai-source.png");

const fallbackLogoBody = `
  <rect x="64" y="64" width="384" height="384" rx="88" fill="#ffffff" stroke="${colors.ink}" stroke-width="18"/>
  <path d="M154 166h104c46 0 82 36 82 82s-36 82-82 82H154" fill="none" stroke="${colors.cyan}" stroke-width="34" stroke-linecap="round"/>
  <path d="M358 346H254c-46 0-82-36-82-82s36-82 82-82h104" fill="none" stroke="${colors.green}" stroke-width="34" stroke-linecap="round"/>
  <circle cx="256" cy="256" r="36" fill="${colors.yellow}" stroke="${colors.ink}" stroke-width="12"/>
  <circle cx="154" cy="166" r="18" fill="${colors.ink}"/>
  <circle cx="358" cy="346" r="18" fill="${colors.ink}"/>
  `;

const logo = svgFrame({
  width: 512,
  height: 512,
  body: aiLogo
    ? `<image href="${aiLogo}" x="0" y="0" width="512" height="512" preserveAspectRatio="xMidYMid meet"/>`
    : fallbackLogoBody,
});

const banner = svgFrame({
  width: 1600,
  height: 520,
  body: `
  ${aiBanner ? `<image href="${aiBanner}" x="0" y="-186" width="1600" height="894" preserveAspectRatio="xMidYMid slice"/>` : ""}
  <rect width="1600" height="520" fill="${aiBanner ? "rgba(255,255,255,0.14)" : "#fbfbf7"}"/>
  <linearGradient id="bannerWash" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.10"/>
    <stop offset="46%" stop-color="#ffffff" stop-opacity="0.35"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0.94"/>
  </linearGradient>
  <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#161616" flood-opacity="0.14"/>
  </filter>
  <clipPath id="bannerLogoClip"><rect x="104" y="114" width="190" height="190" rx="34"/></clipPath>
  <rect width="1600" height="520" fill="url(#bannerWash)"/>
  <rect x="52" y="50" width="1496" height="420" rx="34" fill="none" stroke="rgba(22,22,22,0.10)" stroke-width="2"/>
  <rect x="92" y="102" width="214" height="214" rx="38" fill="#ffffff" filter="url(#softShadow)"/>
  <image href="${aiLogo || ""}" x="104" y="114" width="190" height="190" preserveAspectRatio="xMidYMid meet" clip-path="url(#bannerLogoClip)"/>
  <text x="812" y="174" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Noto Sans CJK SC', sans-serif" font-size="62" font-weight="850" fill="${colors.ink}">Skill Toolkit 公开包</text>
  <text x="812" y="236" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="29" fill="${colors.muted}">把重复工作整理成 Codex / Claude Code 可调用的 Agent Skill</text>
  <g font-family="Inter, -apple-system, BlinkMacSystemFont, sans-serif" font-size="24" font-weight="700">
    <rect x="812" y="296" width="172" height="52" rx="16" fill="#e7f5ff"/><text x="840" y="330" fill="${colors.blue}">5 Skills</text>
    <rect x="1008" y="296" width="170" height="52" rx="16" fill="#ebfbee"/><text x="1036" y="330" fill="${colors.green}">Codex</text>
    <rect x="1202" y="296" width="236" height="52" rx="16" fill="#fff3bf"/><text x="1230" y="330" fill="#8a5a00">Claude Code</text>
  </g>
  `,
});

const social = svgFrame({
  width: 1280,
  height: 640,
  body: `
  ${aiBanner ? `<image href="${aiBanner}" x="0" y="-38" width="1280" height="716" preserveAspectRatio="xMidYMid slice"/>` : ""}
  <rect width="1280" height="640" fill="rgba(255,255,255,0.20)"/>
  <linearGradient id="socialWash" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
    <stop offset="58%" stop-color="#ffffff" stop-opacity="0.54"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0.96"/>
  </linearGradient>
  <filter id="socialShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#161616" flood-opacity="0.14"/>
  </filter>
  <clipPath id="socialLogoClip"><rect x="102" y="114" width="158" height="158" rx="28"/></clipPath>
  <rect width="1280" height="640" fill="url(#socialWash)"/>
  <rect x="44" y="44" width="1192" height="552" rx="44" fill="none" stroke="rgba(22,22,22,0.10)" stroke-width="3"/>
  <rect x="90" y="102" width="182" height="182" rx="32" fill="#ffffff" filter="url(#socialShadow)"/>
  <image href="${aiLogo || ""}" x="102" y="114" width="158" height="158" preserveAspectRatio="xMidYMid meet" clip-path="url(#socialLogoClip)"/>
  <text x="326" y="158" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="54" font-weight="840" fill="${colors.ink}">Skill Toolkit Public Pack</text>
  <text x="326" y="222" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="30" fill="${colors.muted}">创建、采用、叠加、修复和演化 Agent Skills</text>
  <g transform="translate(326 300)">
    ${["Adopt", "Overlay", "Create", "Modify", "Evolve"].map((label, i) => `<rect x="${i * 176}" y="0" width="150" height="74" rx="20" fill="${["#e7f5ff", "#ebfbee", "#fff3bf", "#fff0f6", "#f1f3f5"][i]}" stroke="${colors.line}"/><text x="${i * 176 + 24}" y="48" font-family="Inter, sans-serif" font-size="26" font-weight="800" fill="${colors.ink}">${label}</text>`).join("")}
  </g>
  <text x="326" y="520" font-family="Inter, -apple-system, BlinkMacSystemFont, sans-serif" font-size="25" fill="${colors.muted}">kun-agent-system/skill-toolkit-public</text>
  `,
});

const workflow = svgFrame({
  width: 1400,
  height: 760,
  body: `
  <text x="70" y="80" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="42" font-weight="800" fill="${colors.ink}">Skill 生命周期工作流</text>
  <text x="70" y="126" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="23" fill="${colors.muted}">先找上游，能采用就采用；没有合适上游再创建，真实使用后再沉淀。</text>
  ${[
    ["Need", "重复需求出现", "#f1f3f5"],
    ["Adopt", "先找官方或成熟上游", "#e7f5ff"],
    ["Overlay", "保留上游，加小兼容层", "#ebfbee"],
    ["Create", "没有上游才创建", "#fff3bf"],
    ["Modify", "已有 Skill 不好用就修", "#fff0f6"],
    ["Evolve", "真实使用后沉淀增量", "#f1f3f5"],
  ].map(([title, subtitle, fill], i) => {
    const x = 70 + (i % 3) * 430;
    const y = 190 + Math.floor(i / 3) * 230;
    return `<rect x="${x}" y="${y}" width="350" height="148" rx="24" fill="${fill}" stroke="${colors.line}" stroke-width="3"/>
      <text x="${x + 28}" y="${y + 56}" font-family="Inter, sans-serif" font-size="32" font-weight="800" fill="${colors.ink}">${title}</text>
      <text x="${x + 28}" y="${y + 98}" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="22" fill="${colors.muted}">${subtitle}</text>`;
  }).join("")}
  <g stroke="${colors.ink}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.78">
    <path d="M420 264H500"/><path d="M493 252l14 12-14 12"/>
    <path d="M850 264H930"/><path d="M923 252l14 12-14 12"/>
    <path d="M1240 338v74H250v8"/><path d="M238 413l12 14 12-14"/>
    <path d="M420 494H500"/><path d="M493 482l14 12-14 12"/>
    <path d="M850 494H930"/><path d="M923 482l14 12-14 12"/>
  </g>
  <rect x="70" y="660" width="1260" height="46" rx="16" fill="#ffffff" stroke="${colors.line}"/>
  <text x="96" y="691" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="22" fill="${colors.ink}">完成标准：能安装、能验证、边界清楚，命令跑得通。</text>
  `,
});

const demo = svgFrame({
  width: 1400,
  height: 780,
  body: `
  <text x="70" y="82" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="42" font-weight="800" fill="${colors.ink}">Demo：从一个需求到可验证 Skill</text>
  <text x="70" y="126" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="23" fill="${colors.muted}">示例不含真实客户材料，只展示 public standalone mode 的最小路径。</text>
  ${[
    ["1", "输入需求", "整理客户消息：摘要、风险、待办、回复建议"],
    ["2", "创建 Skill", "运行 skill-creator --public-standalone"],
    ["3", "安装到项目", "复制到 .agents/skills 或 .claude/skills"],
    ["4", "验证", "quick_validate.py + audit_skill.py"],
  ].map(([n, title, text], i) => {
    const x = 86 + i * 318;
    return `<rect x="${x}" y="208" width="276" height="260" rx="26" fill="#ffffff" stroke="${colors.line}" stroke-width="3"/>
      <circle cx="${x + 50}" cy="260" r="30" fill="${[colors.cyan, colors.green, colors.yellow, colors.red][i]}"/>
      <text x="${x + 41}" y="271" font-family="Inter, sans-serif" font-size="28" font-weight="800" fill="#ffffff">${n}</text>
      <text x="${x + 28}" y="330" font-family="Inter, -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif" font-size="30" font-weight="800" fill="${colors.ink}">${title}</text>
      <foreignObject x="${x + 28}" y="354" width="220" height="86"><div xmlns="http://www.w3.org/1999/xhtml" style="font:22px -apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;color:${colors.muted};line-height:1.35">${text}</div></foreignObject>`;
  }).join("")}
  <rect x="126" y="548" width="1148" height="116" rx="24" fill="#f8f9fa" stroke="${colors.line}"/>
  <text x="166" y="588" font-family="SFMono-Regular, Menlo, Consolas, monospace" font-size="22" fill="${colors.ink}">python3 skills/skill-modify/scripts/quick_validate.py</text>
  <text x="166" y="624" font-family="SFMono-Regular, Menlo, Consolas, monospace" font-size="22" fill="${colors.ink}">  .agents/skills/customer-message-digest</text>
  <text x="166" y="660" font-family="SFMono-Regular, Menlo, Consolas, monospace" font-size="24" fill="${colors.green}">PASS: Skill is valid</text>
  `,
});

const assets = [
  ["assets/brand/logo", 512, 512, logo],
  ["assets/brand/banner", 1600, 520, banner],
  ["assets/brand/social-preview", 1280, 640, social],
  ["assets/workflow/skill-lifecycle-workflow", 1400, 760, workflow],
  ["assets/demo/customer-message-digest-demo", 1400, 780, demo],
];

for (const [base, width, height, svg] of assets) {
  const svgPath = resolve(root, `${base}.svg`);
  const pngPath = resolve(root, `${base}.png`);
  write(svgPath, svg);
  render(svgPath, pngPath, width, height);
}

write(
  resolve(root, "assets/workflow/skill-lifecycle-workflow.mmd"),
  `flowchart LR
  A["Need: repeatable capability"] --> B["skill-adopter: find upstream"]
  B --> C{"Route"}
  C --> D["Adopt"]
  C --> E["Overlay"]
  C --> F["Create"]
  F --> G["Validate"]
  D --> G
  E --> G
  G --> H["skill-modify: repair"]
  H --> I["skill-evolver: reuse proven delta"]
`,
);

console.log(JSON.stringify({ ok: true, assets: assets.map(([base]) => [`${base}.svg`, `${base}.png`]).flat() }, null, 2));
