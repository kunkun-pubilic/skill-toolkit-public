# 快速安装与验证

English version: [QUICK_START.en.md](QUICK_START.en.md)

## 1. 克隆公开包

```bash
git clone https://github.com/kun-agent-system/skill-toolkit-public.git
cd skill-toolkit-public
```

## 2. 安装到 Codex 项目

把五个 Skill 复制到项目级 `.agents/skills`：

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"
cp -R skills/skill-adopter "$PROJECT/.agents/skills/"
cp -R skills/skill-creator "$PROJECT/.agents/skills/"
cp -R skills/skill-overlay "$PROJECT/.agents/skills/"
cp -R skills/skill-modify "$PROJECT/.agents/skills/"
cp -R skills/skill-evolver "$PROJECT/.agents/skills/"
```

公开包只安装这五个 lifecycle skills；`plugin-manager` 不属于本期 public edition。

## 3. 安装到 Claude Code 项目

把目标目录换成 `.claude/skills`：

```bash
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/skill-adopter "$PROJECT/.claude/skills/"
cp -R skills/skill-creator "$PROJECT/.claude/skills/"
cp -R skills/skill-overlay "$PROJECT/.claude/skills/"
cp -R skills/skill-modify "$PROJECT/.claude/skills/"
cp -R skills/skill-evolver "$PROJECT/.claude/skills/"
```

## 4. 验证公开包本身

在本仓库根目录运行：

```bash
python3 -m py_compile skills/skill-adopter/scripts/adopt_skill.py
python3 -m py_compile skills/skill-adopter/scripts/research_skill.py
python3 -m py_compile skills/skill-adopter/scripts/source_card_to_registry.py
python3 -m py_compile skills/skill-overlay/scripts/apply_overlay.py
python3 -m py_compile skills/skill-creator/scripts/create_skill.py
python3 -m py_compile skills/skill-evolver/scripts/build_patch_plan.py
python3 -m py_compile skills/skill-evolver/scripts/audit_incremental_update.py

for skill in skill-adopter skill-overlay skill-creator skill-modify skill-evolver; do
  python3 skills/skill-modify/scripts/quick_validate.py "skills/$skill"
  python3 skills/skill-modify/scripts/audit_skill.py "skills/$skill"
done
```

## 5. 用公开 standalone 模式创建一个新 Skill

没有私有 registry 时，使用 `--public-standalone`：

```bash
python3 skills/skill-creator/scripts/create_skill.py customer-message-digest \
  --public-standalone \
  --target-root .agents/skills \
  --description "当用户需要把客户聊天记录整理成摘要、风险、待办和回复建议时使用。" \
  --display-name "Customer Message Digest" \
  --short-description "整理客户聊天记录" \
  --default-prompt "使用 customer-message-digest 整理这份客户聊天记录。" \
  --proof-surface "sample transcript + quick_validate + audit_skill"
```

生成后再跑：

```bash
python3 skills/skill-modify/scripts/quick_validate.py .agents/skills/customer-message-digest
python3 skills/skill-modify/scripts/audit_skill.py .agents/skills/customer-message-digest
```
