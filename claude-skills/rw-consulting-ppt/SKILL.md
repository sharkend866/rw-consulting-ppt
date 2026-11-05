---
name: rw-consulting-ppt
description: 把行业报告、会议纪要、访谈笔记、半成品 bullet 变成 proof-object-first 的图片版咨询 PPT。Use when the user wants consulting-grade slide decks from rough business inputs — alignment-first, storyline before design, one claim per page, HTML 全页设计 + 截图渲染为 PNG，再打包 image-only PPTX。
---

# RW Consulting PPT（Claude Code 移植版）

Use this skill to convert bullet points, research notes, and rough outlines into a polished consulting-style deck made from full-page images.

原版依赖 Codex 的 Image2 全页图片生成；本移植版把渲染后端换成：**模型编写完整 1920×1080 HTML 页面（内联 SVG proof object、系统字体）→ `scripts/render_slide.py`（Playwright + 系统 Chrome）截图 → `package_image_deck.py` 打包 image-only PPTX**。方法论（alignment-first、storyline-before-design、proof-object-first、样页 gate、视觉治理锁）与原版一致。

> 术语说明：本 SKILL 及 references 中的 "Image2-style full-slide prompt / image model" 一律理解为"页面构建规格 / 渲染出的全页 PNG"；凡禁止 HTML/CSS/SVG 渲染的条款已被本移植版 Routing Lock 取代。

## Routing Lock: Image-Only Consulting Slides

默认输出图片版全页 PPT。

- 每页 = 一个完整 1920×1080 HTML 页面，用 `scripts/render_slide.py` 渲染成一张 16:9 PNG。
- 若交付 PPTX，每页只有一张完整图片（`package_image_deck.py` 机械打包）。
- 不创建可编辑文本框、图表对象、表格、SmartArt 或卡片网格作为页面设计路线。
- **不**用 Python/Pillow/SVG 文件画幻灯片页面（SVG 只允许内联在 HTML 里作为 proof object）。
- **不**把裸 HTML 线框（细边框卡片、通用图标、无主导 proof object）当成品交付——HTML 必须承载咨询 exhibit 的完整视觉系统。
- 照片级配图是可选环节：用户配置图片 API 后用 `scripts/gen_image.py` 生成；未配置时禁止用占位图冒充。
- 如果用户要求可编辑 PPTX，说明本 Skill 是图片版，改用同仓库的 `astralow-for-editable-ppt` 逐页转换。

### Generation Backend Lock

本 Skill 是策略、输入生产、brief、页面契约与 QA 层，不是"代码画幻灯片"引擎。

1. 每页编写一个完整 1920×1080 HTML 页面，跑 `scripts/render_slide.py` 出 PNG。
2. 只先渲染 1-2 页代表性样页，展示给用户确认。
3. 批准后，用同一路线批量渲染剩余页面。
4. 只有 PNG 被接受后，才用 `scripts/package_image_deck.py` 打包 image-only PPTX。

Hard stop：如果 Playwright/Chrome 不可用导致无法渲染，停在 slide brief 或 HTML 页面阶段，告诉用户渲染无法继续，不得降级为 Pillow/pptx 画图或裸线框交付。

验收检查：

- 打包时 `editableTextBodies = 0`（`package_image_deck.py` 会打印校验值）。
- 每张 PNG 都是 16:9，且逐张目检过（用 Read 工具看图）。
- deck 有代表性 PNG 预览或 contact sheet。
- 输出像咨询 exhibit，而不是普通模板或"可编辑 PPT 截图感"。

## Reference Loading

按需加载 references，视觉治理类不能跳过：

- 新项目、品味不明确或要对标咨询图片质量：读 `references/consulting-image-context.md`。
- 用户提供参考图/已批准样页/好坏示例或要求风格延续：读 `references/visual-style-master.md` 和 `references/example-lessons.md`。
- 写任何页面构建规格之前：读 `references/concept-image-director.md` 和 `references/message-hierarchy-rules.md`。
- 页面含公司示例、玩家分类、指标、风险、门禁或验证主张：读 `references/message-proof-mapping.md`。
- 评估任何渲染样页之前：读 `references/sample-rejection-rubric.md`。
- 多页 deck 样页批准后、批量渲染前：读 `references/deck-consistency-lock.md`。
- 打包或校验问题：读 `references/image-only-output-contract.md`。

必需 reference 无法加载时，停止并说明缺哪个。生产包中记录本次加载的 references，供后续审计。

## 视觉治理锁（核心，不可跳过）

以下规则是本 Skill 的核心部分，即使 reference 没加载也要执行。

### Style Master Lock

用户提供参考图、已批准样页、好/坏页或历史成功输出时，把它当 style master，除非用户明确说不。Style master 指整页节奏而不只是配色：action-title 字号与位置、subtitle 权重与距离、proof object 主导地位、证据带结构、底部 takeaway 处理、信息密度、字体气质、线条粗细、图标处理与视觉母题。与新需求冲突时先说明取舍。

### Deck Consistency Lock

多页 deck 把已批准样页当作 deck 级系统的基础，而不是单页参考。批量渲染前写一份 `Deck System Contract`，逐字复用到每页构建中，只锁 deck 级元素：页标系统（全有或全无、样式统一）、action-title 字号/权重/对齐/标题块宽度、subtitle 位置与权重、左上角母题、source-note 样式、bottom-synthesis 策略（全无/每页/只在指定判断页）、材质处理（纯 2D/微深度/3D）。不全局锁页内 proof object 元素。禁止每页各自发明页眉页脚系统。

### Message Hierarchy Lock

每页只有一个 governing message 和一个最高优先级结论区：

- Action title 是最高优先级结论，不得再造第二个标题式主张。
- Subtitle 解释标题为什么成立，不复述标题。
- 主 proof object 是视觉主角；大数字必须锚定 proof object，不得成为游离 KPI 块与标题竞争。
- Panel header 命名证据对象，不再说一遍结论。
- 底部 takeaway 每页最多一次，合成含义，不能成为第三个竞争模块。
- Source note / caveat 保持低权重，不得与标题或 takeaway 同权重。

### Claim-Evidence-Visual Lock

每页先映射证据与主张再进入视觉设计。公司/产品/指标示例不能只是标签，要写成说明市场动向的证据短句。已证实与待证实分开；线、箭头、环、门禁、对勾、颜色状态都是语义主张，不得暗示不成立的证明。消息是"观察到速度但信任待验证"时，观察信号与验证要求要分层呈现。

### Density Preservation Lock

独立阅读型 deck 的信息密度是风格系统的一部分：设计的任务是降低阅读摩擦、保留证据结构，不是删证据。样页批准后继承其页面节奏、中文文字密度、注释深度、证据带结构与来源边界。页面干净但太空 = 密度失败，不是视觉成功。

### Prompt Shape Lock

页面构建规格按此层级组织（不要给一堆平级字段）：

1. Action title。
2. Subtitle（如需要）。
3. 主 proof object。
4. 锚定 proof object 的证据锚点。
5. 底部 takeaway（至多一条）。
6. 低权重 source note / caveat（仅在需要时）。

### Sample Rejection Lock

样页出现以下问题就拒绝并修 brief/页面，不直接批量：

- 多个结论区；游离大数字与标题竞争；底部 takeaway 与主视觉竞争；source note 与 takeaway 竞争；
- 普通 dashboard/卡片网格/PPT 模板感；proof object 在支撑指标之前不可见；
- 独立阅读模式下的稀疏海报感；一色到底（全绿/全蓝/全灰线稿）；
- 一页塞入太多主张、caveat 和 takeaway；证据错配（视觉连线暗示不成立的证明）；
- 仅标签的玩家证据；2×2 假精度（维度不适用于所有玩家）；线框过载（框、边、连接线让每个模块一样重）。

## Alignment Gate

开始生产前必须做对齐对话。这是硬门禁：用户说"根据这份材料生成 PPT"但没给齐偏好时，第一个回复必须是对齐问题，不是产出文件。

三个独立的批准门禁，不可合并：

1. **Preference alignment**：受众/场景、交付模式、页数、信息密度、视觉风格/主题色、输出格式。
2. **Storyline / blueprint 批准**：core question、working thesis、storyline、页面列表、样页选择。
3. **Sample brief 批准**：1-2 页样页的 visual mode、proof object、visual mother concept、must-keep text、bottom-synthesis 策略、省略清单。

对齐确认前不创建：Inputs、blueprint、页面大纲、slide brief、页面构建、样页、生产包、打包计划、生成的图片。

最低必确认偏好：①交付模式（presentation / 独立阅读）②主题色/视觉基调 ③页数 ④信息密度 ⑤视觉风格 ⑥交付格式（PNG / PNG+图片型 PPTX）。

推荐对齐话术：

```markdown
请确认下面 6 个偏好，我再开始产出，不然很容易跑偏：
1. 受众 / 使用场景：
2. 交付模式：presentation / 独立阅读型报告？
3. 页数 / 图片数：
4. 信息密度：简洁 / 标准 / 密集？
5. 视觉风格 / 主题色：
6. 输出格式：PNG / PNG + 图片型 PPTX
```

批准交接必须是用户可见的对话内容，不是文件系统检查点。蓝图批准要在回复里包含完整交接块：

```markdown
需要你批准的是这套故事线 / 蓝图：

Core question:
<one sentence>

Working thesis:
<one paragraph>

Page list:
1. <page title> — <page role / proof object>
...

Recommended sample pages:
- <page number and why it tests the deck>

请回复“批准”或指出要改哪几页；批准前我不会创建 slide briefs、页面构建、样页 PNG 或 PPTX 打包计划。
```

## Delivery Mode Choice

**Mode A: Live Presentation Deck**——现场讲、面试展示、roadshow。优先级：视觉 proof object、第一眼信息、记忆钩子；文字密度低到中；must-keep：标题 + 1 subtitle + 3-6 标签/数字 + 1 takeaway；QA 重点：远距离可读性、层级、无杂乱、强 proof object。

**Mode B: Standalone Report Deck**——独立阅读、发 PDF/PPT、GitHub 展示。优先级：自包含解释、证据边界、推理链；密度中到高；页面必须自己回答 so what；QA 重点：无讲解也能读懂论证。

用户不选时问一次；仍不选则：公开/作品集用途默认独立阅读型，仅会议用途默认 presentation。

## Visual Mode Selection

- **Clear Report Exhibit**（默认，独立阅读/密集证据页）：大结论标题、解释性 subtitle、可见 proof object、结构化证据带、路线图/阶梯/矩阵/时间线、克制配色、底部 takeaway 带。
- **Hero Concept Exhibit**（开场论点/收尾判断/presentation/抽象主张）：主导 proof object（3D 堆栈、门、飞轮、桥、漏斗、能力塔）+ 侧面证据轨；不强行用于独立阅读型报告页。
- **Evidence Architecture Exhibit**（证据结构本身是 proof object 时）：路线图、价格阶梯、能力栈、矩阵、分解、风险桥、生态图、时间线；保留证据骨架、降低阅读摩擦；避免退化成等权卡片或普通表格。

## Core Principle

管理页面构建的层级是：意图、证据、边界、优先级。不过度管理精确坐标、chip 位置、图标数量等微小装饰。定义清楚：页面必须证明什么、用什么 proof object 承载、visual mother concept 是什么、哪些文字数字品牌约束不可动；排版、视觉节奏与层级在约束内自由发挥。

## Workflow

### 1. Input Production Pass

把用户已有分析转成 `Inputs for PPT Production`（扩展/压缩/改写/锐化/保留五种变换，先问用户要哪种）。必须输出完整 block 并请用户批准 core question、working thesis、storyline、页面结构后才能 blueprint。格式：

```markdown
## Inputs for PPT Production

### Context
- Audience: / Use case: / Delivery mode: / Page count: / Language: / Theme:

### Core Question
<one question the deck must answer>

### Working Thesis
<one-sentence answer or judgment>

### Storyline
1. / 2. / 3. ...

### Page-Level Inputs
#### Page 1: <draft page title>
- Claim: / Why it matters: / Proof object: / Evidence available: / Evidence needed: / Caveats: / Takeaway:
...

### Open Questions
```

不要隐藏重大缺口；证据不足标在 `Evidence needed` 或 `Open Questions`。

### 2. Normalize The Inputs

把用户 bullet 转成 message inventory：core question、草拟答案、支撑论证、证据/示例/数字、用户假设、模型推断、未决不确定。访谈/逐字稿/杂乱笔记先合成主题、张力、证据和 1-3 条页面级主张，不要把原始笔记直接送进页面构建。

### 3. Build The Deck Blueprint

从批准的 Inputs 建 blueprint：deck 标题、一句话 storyline、受众与场景、页数、交付模式与密度目标、逐页结构、每页 governing message、每页 proof object、建议 visual mother concept、缺的证据。**每页标题必须是结论，不是主题标签**（"Workflow ROI is replacing model price" 而非 "Pricing Overview"）。

### 4. Confirm The Blueprint

请用户批准或修改（见 Alignment Gate 交接块）。批准前不创建 slide brief、页面构建、样页、打包计划。

### 5. Create Slide Briefs

每页 brief：页码、一句话 page claim、证据边界（已证实/用户假设/模型推断/未决）、claim-evidence map、proof object、visual mother concept、3-6 条 must-keep 文字数字、交付模式、独立阅读模式下的自然正文、source note/caveat、文字层级、avoid list、页面构建要点。brief 弱就先改 brief。

### 5.5 Concept Image Director Pass

构建页面前把每页 brief 升级为概念图方向：visual mode、最强 proof object、visual mother concept、证据锚点、claim-evidence 适配、视觉暗示护栏、文字层级、坏输出风险、排除项。主视觉是"卡片/对比表格/三栏/流程箭头"且该结构不是真正的 proof object 时，替换成路线图、阶梯、漏斗、栈、矩阵、时间线、分解或决策路径。样页构建前展示紧凑的 sample brief 并获批准（或用户明确说跳过）。

### 6. Write Page Build Specs（页面构建规格）

给页面构建定义内容脚本，不是僵硬的线框图。包含：16:9 全页要求、页面角色、action title + subtitle、proof object、visual mode、visual mother concept、锚定证据、至多一条底部 takeaway、低权重 source note、主题色与基调、文字预算、交付模式对应密度、明确排除项。

不得在成品页暴露内部脚手架标签（"如何阅读这一页"、"读图说明"、"研究过程"等），换成自然商业标签（证据锚点、战略含义、关键判断、商业启示、深层风险、备注）或不用标签。

### 7. Generate Samples First

先渲染 1-2 页代表性样页再批量。样页要测试：封面/开场论点页 + 一条证据最重的密集正文页；独立阅读模式至少一页测试解释性文字密度。展示样页（用 Read 工具打开 PNG）等用户确认。

### 7.5 Sample Rejection Gate

样页像普通可编辑 PPT 模板而非咨询 exhibit 时，拒绝并修 brief/HTML 再渲染。失败要精确命名（"generic card/table dashboard"、"weak proof object"、"text too small"、"one-note color"、"competing visual centers"、"multiple conclusion zones"、"detached metric"、"evidence misattribution"、"false precision chart"、"linework overload"、"editable-PPT screenshot feel"），围绕更强的 proof object 修改，而不是装饰性修补。

### 8. Batch Render And Package

样页批准后：从样页写 `Deck System Contract` 并逐字复用到每页构建；先定 bottom-synthesis 策略；每页渲染一张 PNG；保存为 `slide_01.png` 等稳定文件名；出 contact sheet 并做 deck 级一致性 QA；页标、标题字号、页眉对齐、source note、bottom synthesis 漂移的页在打包前重渲染；最后用 `scripts/package_image_deck.py` 打包 image-only PPTX。

## HTML Page Conventions（本移植版新增，必读）

写页面 HTML 前遵守：

- 每个 HTML 文件 = 一页，命名 `slide_01.html`、`slide_02.html`……根元素按 1920×1080 设计，`body { margin:0; width:1920px; height:1080px; overflow:hidden }`。
- 字体用系统字体栈：`-apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`；不要依赖 WebFont（除非网络稳定）。
- proof object 用**内联 SVG**：漏斗、路线图、格局图、能力栈、风险桥、矩阵、阶梯、时间线。SVG 坐标精确、颜色受控，是页面主角而不是装饰。
- 文字必须是真实 HTML 文本（渲染后与 brief 逐字一致）；任何错字/错数字都是 brief 错误，改 brief 再改页面，不是渲染事故。
- 图表可手写 SVG；需要数据驱动图表时才引 CDN 库（ECharts/Chart.js，固定版本号）。渲染脚本等 `networkidle`，但离线时页面必须仍可读（内联 SVG 兜底）。
- 照片级配图仅通过 `scripts/gen_image.py`（用户已配置 API 时），生成后以本地路径嵌入；未配置时不使用。
- **配图水印约定（对所有用户强制）**：所有 AI 生成配图必须无水印。`gen_image.py` 对豆包默认请求 `watermark: false`；若服务商强制水印（API 报错，或渲染后目检发现水印），禁止直接使用该图——裁掉水印所在角并检查构图是否受损，或重新生成/换图；最终交付说明中标注配图处理方式。生成后目检图片四角确认无水印。
- 渲染：`<venv>/bin/python <skill>/scripts/render_slide.py slides/ --out slides_png/`（或单文件模式）；渲染后**逐张用 Read 工具目检 PNG**。
- 打包：`<venv>/bin/python <skill>/scripts/package_image_deck.py slides_png/ --out <deck-name>-image-only.pptx --title "<deck title>" --contact-sheet contact_sheet.png`，校验输出应为 `editableTextBodies=0`。

## Consulting Image Rubric（验收标准）

- **First-glance message**：几秒内看懂页面主张。
- **Visible proof object**：主视觉证明主张，不是装饰。
- **Evidence before ornament**：视觉打磨服务数据/引语/对比/机制/运营模型。
- **Few but accurate words**：文字数字有限、刻意、有优先级。
- **Mode fit / Density fit**：presentation 页可依赖讲解；独立阅读页必须自解释且保留足够证据结构；干净但空的页 = 失败。
- **Visual mode fit**：按交付模式选 Clear/Hero/Evidence 三种模式。
- **Consulting authority**：清晰主张、可见 proof object、克制的排版、克制的配色、轻分隔线、适度留白。
- **Hard visual floor**：无破损布局、无文字溢出重叠、无丑陋断行、无单字孤行、无散乱叙事。
- **Deck consistency floor / Bottom-synthesis floor / Exhibit bar**：多页系统一致；bottom synthesis 策略刻意选择；页面更接近路线图/阶梯/矩阵/能力栈/漏斗/桥/分解 exhibit，而不是普通表格卡片页。

失败时一次只修一个目标：主张 → proof object → 证据层级 → 文字准确性 → 视觉权威。

## Message Architecture

- Title：锐利的页面角度或结论。
- Subtitle：一句话解释证据为何支持标题。
- Panel headers：命名证据对象。
- Main numbers：锚定 proof object。
- Examples：让抽象 proof 具体。
- Bottom takeaway：只合成一次含义。
- Source note / caveat：低权重证据边界，只在需要时。

标题、subtitle、panel header/footer、takeaway 不得重复同一主张词。独立阅读模式可加 1-2 句自然正文和 source note，但要折叠进同一层级，不用元标签。

## Proof Object Rules

好的 proof object：重叠/近似重叠（配对指纹、匹配矩阵）、分解（公共核心+细分模块）、对比（两种运营模式/购买使命/价格架构）、集中（排序条、密点、热图、组合宇宙）、序列（客户旅程、运营流程、成熟度阶梯）、决策逻辑（2×2、决策树、路径图、标准矩阵）。当主张更适合用重叠、构成、差异、集中或排序证明时，避免流程箭头。

## High-Density Evidence Pages

竞品对比、价格架构、产品组合、用户分层、渠道结构、成本结构、能力矩阵等证据密集页：从证据结构出发选视觉形式；信息量与视觉权重分离；保留硬证据、去掉重边框/重复标签/装饰容器/冗余解释；用 callout 标注锚点、缺口、异常、拐点、决策；多对象对比给稳定识别锚（颜色、列头、图标、底线、标签系统）；重网格换成浅色带、留白、字级层级和轻分隔线；数字可能被误读时标注单位和定义。

## Default Visual System

用户没给配色时用中性高权威咨询系统：白底、炭黑文字、浅蓝灰信息层；锚色用项目品牌色或克制的分析蓝 `#1E5BFF`；点缀色只用少量暖色做点、火花或强调。避免：深蓝/石板色主导页、SaaS dashboard 卡片、stock photo、人物、渐变 blob、随机图标、模板感双栏。

## Page Build Spec Pattern

每页按此结构写构建规格（替代原版的 image prompt）：

```text
Build one complete 1920x1080 consulting exhibit page (HTML), not an editable PowerPoint layout.

Slide role: <cover / thesis / evidence / comparison / decision / roadmap / closing>
Action title: <one sharp conclusion; the only highest-priority conclusion zone>
Subtitle: <one short explanatory sentence, if needed; do not repeat the title>

Main proof object:
<the visible evidence carrier that proves the claim; inline SVG>

Visual mother concept:
<memorable composition that makes the proof object visible>

Evidence anchors attached to the proof object:
1. <item or number and where it belongs in the proof object>
...

Bottom takeaway:
<deck bottom-synthesis policy; one line only>

Low-weight source note / caveat:
<optional; small and visually quiet>

Style:
White base, charcoal text, pale blue-gray information layers, restrained analytical blue as anchor, small warm accent only if useful. High-end management consulting, crisp typography, generous margins, light rules. Avoid stock photos, decorative blobs, generic dashboards, web UI look, and normal PPT template feel.

Deck System Contract:
<repeat exactly on every page: page marker system, action-title scale and placement, subtitle placement, top-left motif, bottom-synthesis policy, source-note style, material treatment.>

Text rule:
Use only the provided key terms and numbers. Prioritize action title, proof-object labels, main numbers, and the single bottom takeaway if present. No detached KPI blocks, no multiple conclusion bands.

Output:
One complete 1920x1080 HTML page rendered to a 16:9 PNG via scripts/render_slide.py. No editable objects.
```

独立阅读模式追加密度要求（保留证据结构、1-2 句自然正文折叠进层级、轻 source note、至多一条底部 takeaway、禁用元标签）；presentation 模式追加视觉优先要求（proof object 主导、文字稀疏、无解释段落和脚注）。

## Iteration Lessons

页面接近但不满意时按此顺序诊断：proof object 是否在支撑指标之前可见？文字层是否各司其职？一侧是否视觉过重？真实指标是否把注意力拉到错误的故事？主题色是锚还是变成了布局？示例是否在增加可信度而不是把页面变成产品列表？每次迭代只改一个目标，命名问题再改。

## Anti-Slop Gate

新增或保留任何规则、示例、构建规格或视觉教训前，检查是否至少含其一：触发条件、验收测试、好坏示例、不可协商约束、停止条件。只写"更专业/更美/更高级"的句子要改写为具体可见的检查或删除。
