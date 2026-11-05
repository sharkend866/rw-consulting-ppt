# 从 Codex 原版迁移到 Claude Code 版

本仓库是 Codex 原版（Pikapika260214/rw-consulting-ppt）的 Claude Code 移植版，原版 `skills/` 目录已移除，替代品在 `claude-skills/`。

## 迁移步骤

1. 卸载已安装的 Codex skills：从 `~/.codex/skills/` 移除 `rw-consulting-ppt` 与 `astralow-for-editable-ppt`（先备份到其他位置再删）。
2. 安装 Claude Code 版：

```bash
mkdir -p ~/.claude/skills
ln -sfn "$PWD/claude-skills/rw-consulting-ppt" ~/.claude/skills/rw-consulting-ppt
ln -sfn "$PWD/claude-skills/astralow-for-editable-ppt" ~/.claude/skills/astralow-for-editable-ppt
```

3. 安装依赖：`pip install -r requirements.txt`；渲染预览需要 LibreOffice（可选）。
4. 调用方式从 `$skill-name` 变为 `/skill-name`（`/rw-consulting-ppt`、`/astralow-for-editable-ppt`）。当前会话未识别时新开对话。

## 行为差异（需知）

- 页面渲染改为 HTML + 截图路线，不再依赖 Image2；配图需配置豆包 API Key（可选）。
- 渲染预览为 LibreOffice headless，**不是 Office 验证**；最终验收用 WPS/PowerPoint 人工确认。
- 原版 Windows PowerShell 渲染/编辑验证脚本已由 `verify_edit.py`（python-pptx 回路验证）替代。
- 原版 Git 历史仍可回溯：`git log -- skills/` 或上游仓库。
