# 发布检查（Claude Code 移植版）

- [x] `claude-skills/` 两个 skill 的 SKILL.md frontmatter（name/description）与调用名一致。
- [x] 依赖声明与 README 一致：python-pptx、Pillow、playwright、certifi（requirements.txt）。
- [x] 三条链路冒烟测试通过：HTML 渲染 + PPTX 打包（editableTextBodies=0）、图片转可编辑 + LibreOffice 预览、豆包配图（watermark: false）。
- [x] 渲染/验证边界标注清楚：LibreOffice 预览 ≠ Office 验证，最终 WPS 人工验收。
- [x] 配图水印约定写入 SKILL.md 与 README。
- [x] 原版 `skills/` 已移除，README 内所有引用路径已更新为 `claude-skills/`。
- [x] UPGRADE.md 说明 Codex → Claude Code 迁移步骤与行为差异。
