---
name: astralow-for-editable-ppt
description: 将整页 PNG、幻灯片截图或图片型 PPT 转成可编辑 PowerPoint。用 Python 脚本重建文本框、图形与局部裁图，LibreOffice 渲染预览，交付可编辑 PPTX。Use when the user wants to convert a slide image, screenshot, or image-only PPT page into an editable PPTX.
---

# Astralow-for-editable-ppt（Claude Code 移植版）

忠实保留源图文字、布局与视觉关系，交付可编辑 PPTX 和实际渲染预览。原版为 Codex 的 Astra low 模型优化，本版不绑定模型，由 Claude Code 会话当前模型（如 DeepSeek）执行。

## 使用

1. **先看源图**：用 Read 工具查看源 PNG，再决定重建方法。文字、数字和适合原生表达的主要结构用可编辑对象；复杂视觉可以合理保留局部裁图，说明哪些部分内部不可编辑。不要把整页图片包装成"可编辑重建"。用户要求图表数据、表格单元格或图标路径可编辑时，按该要求选择对象类型；不能从图片可靠恢复的信息应明确说明。

2. **用 Deck API 重建**：见 [工具接口](references/tools.md)。把本 Skill 的 `scripts` 绝对路径加入 `sys.path`，`from editable_ppt import Deck`。把重复的绘图、保存、渲染和报告工作交给脚本，只需读接口，不必预读脚本源码。模型独立决定文字、坐标、字体、颜色和裁图范围；接口不足时使用 `deck.slide` / `deck.presentation` 或其他合适工具。不要为满足接口而简化用户要求。

   - 字体：macOS 上用 PingFang SC / Hiragino Sans 等本机字体；原版的 Microsoft YaHei 在本机不存在，仅作名称写入不会报错但渲染时由系统替换。
   - `finish()` 返回本轮预览路径与状态；在 `finish(render=True)` 后**立即用 Read 工具查看返回的 preview 路径**，省去单独查目录。

3. **检查最终整页**：比较源图与预览 PNG，重点看错字、漏字、金额/单位/日期、重叠、文字与容器边界、裁图底色。对疑点再局部放大。修订后查看新预览；按实际问题决定是否继续修订，不设固定轮数。详情见 [质量检查](references/quality.md)。

4. **编辑验证**（可选）：用随附的 `scripts/verify_edit.py` 在副本上做改字、保存、重开验证。注意：这是 python-pptx 回路验证，**不是 Office 渲染验证**。

5. **交付**：最终回复提供 PPTX 路径、预览路径及必要限制，明确区分已验证、未验证和局部图片，避免重复过程日志。

## 渲染验证边界（重要）

- 本机渲染预览由 **LibreOffice headless** 完成（`finish` 内自动调用，状态为 `libreoffice-ok`）。它是排版预览，**不等于 Office/PowerPoint 验证**：字体度量、主题效果和换行可能与 PowerPoint / WPS 不同。
- 最终验收建议由用户在 **WPS** 中打开 PPTX 人工确认。交付物报告中标"LibreOffice 渲染预览 + 未经 Office 验证"。
- 原版 Windows PowerShell 渲染与编辑验证脚本不在本移植版范围内；Windows 用户可自行补回。

## 范围

- 基础构建工具一次处理一张源图、一页 PPT；多页按页处理，保持顺序。合并时保留原生对象，并检查最终合并文件。工具未提供通用多页合并器。
- 新建基础对象使用明确样式以避免意外主题效果；不统一删除源图需要的阴影、渐变或模板样式。
- Python 依赖见 `requirements.txt`（python-pptx、Pillow）。实际 Office 渲染与编辑验证需要 Windows 桌面 PowerPoint；macOS 用 LibreOffice 预览 + WPS 人工验收。
