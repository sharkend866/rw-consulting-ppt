# Changelog（Claude Code 移植版）

本文件从 Claude Code 移植版开始记录；更早的 Codex 原版历史见上游仓库
<https://github.com/Pikapika260214/rw-consulting-ppt> 及本仓库 git 历史（`git log -- skills/`）。

## v1.0 — Claude Code 移植版（2026-11-05）

### rw-consulting-ppt

- 渲染后端从 Codex Image2 换成 HTML 全页设计 + `render_slide.py`（Playwright + 系统 Chrome）截图。
- SKILL.md 重写：方法论与视觉治理锁保留，Routing Lock / Backend Lock / 输出契约改为 HTML 路线。
- 新增 `gen_image.py`：豆包 Seedream 配图（OpenAI 兼容接口，默认 `watermark: false` 无水印，带 429 重试与错误体透出）。
- 复用原版 `package_image_deck.py` 打包 image-only PPTX。
- 配图水印约定写入 SKILL.md，对所有使用者强制。

### astralow-for-editable-ppt

- `editable_ppt.py` 增加 macOS 字体映射与 LibreOffice headless 渲染分支（`libreoffice-ok` 状态）。
- 新增 `verify_edit.py`：python-pptx 编辑回路验证，替代原版 Windows PowerShell 脚本。
- SKILL.md 与 references 更新渲染边界说明（LibreOffice 预览 ≠ Office 验证，WPS 人工验收）。

### 仓库

- 原版 `skills/`（Codex）移除，技能统一在 `claude-skills/`。
- README / UPGRADE / RELEASE_CHECKLIST / .gitignore / requirements.txt 全部改为 Claude Code 版。
- 验证记录：三条链路冒烟测试通过（HTML 渲染打包、图片转可编辑、豆包配图无水印）。
