# Claude Code 移植版

本目录是把原仓库两个 Codex Skills 移植到 Claude Code 的版本。原版 Codex `skills/` 已从本仓库移除（可在 git 历史或上游仓库取回），本目录是唯一的技能源；两个 skill 已软链到 `~/.claude/skills/` 全局可用。

## 与原版的差异

| 环节 | 原版（Codex） | 移植版（Claude Code） |
|---|---|---|
| 全页图片生成 | Codex Image2 直接生成 | 模型编写 1920×1080 HTML（内联 SVG proof object）→ `render_slide.py`（Playwright + 系统 Chrome）截图 |
| 驱动模型 | Astra low（Codex 模型） | 不绑定模型（当前会话模型即可，如 DeepSeek） |
| PPTX 渲染预览 | Windows PowerPoint COM（PowerShell） | LibreOffice headless（macOS）；最终验收用 WPS 人工确认 |
| 编辑验证 | PowerPoint COM 副本改字重开 | `verify_edit.py` python-pptx 回路验证 |
| 照片级配图 | 无 | 可选：`gen_image.py` 调 OpenAI 兼容图片 API（需用户配置 key） |
| 打包 PPTX | `package_image_deck.py` | **原样复用**（纯 Python，无平台依赖） |

方法论层（alignment-first、storyline-before-design、proof-object-first、三道批准门禁、样页 gate、视觉治理锁）**原样保留**。

## 依赖

```sh
pip install -r requirements.txt          # 根目录 requirements.txt（python-pptx、Pillow）
pip install playwright                    # 渲染用，用系统 Chrome，无需下载浏览器
brew install --cask libreoffice           # astralow 渲染预览（可选，没装则 finish 会跳过渲染）
```

## 安装

```sh
mkdir -p ~/.claude/skills
ln -sfn "$PWD/claude-skills/astralow-for-editable-ppt" ~/.claude/skills/astralow-for-editable-ppt
ln -sfn "$PWD/claude-skills/rw-consulting-ppt" ~/.claude/skills/rw-consulting-ppt
```

## 使用

- 生成图片版咨询 deck：`/rw-consulting-ppt`
- 图片转可编辑 PPT：`/astralow-for-editable-ppt`

## 照片级配图配置（可选）

`rw-consulting-ppt/scripts/gen_image.py` 默认走**豆包 Seedream（火山方舟 Ark）**，OpenAI 兼容的 `POST {base}/images/generations`：

```sh
# 只需配 Key；endpoint 和模型 ID 脚本已内置（doubao-seedream-5-0-pro）
export IMAGE_API_KEY="<火山方舟 API Key>"
```

其他 OpenAI 兼容服务（通义万相 / SiliconFlow / OpenAI 等）：

```sh
export IMAGE_API_KEY="<key>"
export IMAGE_API_BASE="<服务商 OpenAI 兼容地址>"
export IMAGE_API_MODEL="<模型名>"
```

模型 ID 可能随版本更新，以火山方舟控制台为准；size 默认 `2K`，报错可换 `1536x1024` / `1280x720`。未配置 Key 时不影响图表类页面（SVG 内联绘制）。

**水印约定**：脚本对豆包默认请求 `watermark: false`（无水印），SKILL 要求所有配图必须无水印——若服务商强制水印则裁剪水印角或换图，禁止直接使用带水印的图。需要水印时可 `--watermark true`。

## 验证状态（2026-11-05 冒烟测试）

- astralow：源图 → Deck 重建 → LibreOffice 渲染 `libreoffice-ok` → 编辑回路验证 passed ✅
- rw：样页 HTML → 3840×2160 PNG → 打包 `slides=1 pictures=1 editableTextBodies=0` ✅
- 豆包配图：Seedream 生成成功、`watermark: false` 无水印（用户已目检确认）✅
