# Image-Only Output Contract（Claude Code 移植版）

Use this reference when implementing or validating an RW Consulting PPT output.

本移植版与原版唯一的不同：全页 PNG 不再由 Codex Image2 生成，而是由模型编写完整 1920×1080 HTML 页面（内联 SVG proof object、系统字体），经 `scripts/render_slide.py`（Playwright + 系统 Chrome）截图为 16:9 PNG，再由 `scripts/package_image_deck.py` 机械打包成 image-only PPTX。其余方法论与原版一致。

## Core Contract

- Treat any approved reference image as the style master for full-page rhythm: color tone, texture, information density, typography mood, proof-object dominance, evidence-band structure, and bottom-takeaway treatment.
- The page is authored as one complete 1920×1080 HTML page and rendered to PNG by `scripts/render_slide.py`. The HTML is the production route, not a stand-in.
- Generate each slide as one complete 16:9 PNG.
- For multi-page decks, render all slides against one deck-level style contract: identical page-marker system, action-title scale and placement, subtitle relationship, bottom-synthesis policy, source-note treatment, and material treatment.
- Do not assemble the page as bare HTML wireframes with thin borders and generic cards; the HTML must carry a consulting exhibit: dominant proof object, consulting typography, evidence bands, restrained color.
- Do not crop a reference image into assets and re-layout those assets with code unless the user asks for strict reproduction.
- Do not use Python/Pillow canvas drawing or python-pptx shapes as the slide-design route. Packaging PNGs into PPTX is allowed because packaging does not alter slide design.
- 照片级配图（非图表）是可选项：通过 `scripts/gen_image.py` 调用用户配置的图片 API 生成，再嵌入页面；未配置时禁止用占位图冒充。
- If text fidelity is risky, reduce text, render a sample, or ask before changing artifact type.

## Alignment Lock

Before creating production artifacts, confirm the user's output preferences.

Do not create `Inputs for PPT Production`, a deck blueprint, slide briefs, HTML page builds, production-pack Markdown, sample PNGs, images, or a packaging plan until the user has confirmed:

- audience / use case;
- delivery mode: live presentation or standalone report;
- page count / image count;
- detail level;
- theme color / visual style;
- delivery format: PNG only or PNG plus image-only PPTX.

If any item is missing, ask for alignment first. Defaults may be used only when the user explicitly says to use defaults.

Preference alignment is not enough to start rendering. After preferences are confirmed, require user approval for:

- `Inputs for PPT Production`: core question, working thesis, storyline, and page-level structure;
- deck blueprint: page list, governing message, proof object, visual mode, and sample page choice;
- sample page brief: visual mother concept, must-keep text, and what will be left out to avoid clutter.

Do not build HTML pages, render sample PNGs, or create PPTX packaging plans before these approvals unless the user explicitly says to skip the approval gate.

## Backend Lock

RW Consulting PPT does the strategy, inputs, slide briefs, HTML page builds, and QA. The HTML page is the slide design; `render_slide.py` only screenshots it.

Required route:

1. Run the Concept Image Director pass before building the page.
2. Show and confirm the sample page brief before rendering.
3. Build and render 1-2 representative sample pages.
4. Reject weak samples that look like generic editable PPT templates, generic cards, plain tables without a governing proof object, overloaded pages with competing visual centers, detached large metrics, or source notes competing with takeaways.
5. Wait for user approval after acceptable samples exist.
6. Before batch rendering, write a deck style contract from the approved sample and user feedback, including the bottom-synthesis policy, then repeat that contract in every page build.
7. Render the remaining slides through the same HTML + render_slide.py route.
8. Build a contact sheet and inspect deck-level consistency before packaging.
9. Regenerate affected slides if title scale, page marker, header motif, bottom synthesis, evidence-chip style, source-note treatment, or material treatment drifts.
10. Package accepted PNGs into an image-only PPTX if requested.

If rendering is unavailable (Chrome/Playwright missing), stop after briefs and tell the user. Do not substitute Python/Pillow canvas drawings or python-pptx shapes for the page design.

## Allowed

- Full-page 1920×1080 HTML authored as a consulting exhibit, rendered to 16:9 PNG via render_slide.py.
- Inline SVG proof objects, data-driven charts (inline or via CDN), system fonts.
- Optional photo-grade images through scripts/gen_image.py when the user has configured an image API.
- PPTX packaging with one image per slide (package_image_deck.py).
- Contact sheets and preview images.
- Dimension checks and slide-object validation.
- Mechanical compression, renaming, and copying.

## Not Allowed

- Editable PPT text boxes as the slide-design route (packaging-only).
- Native PowerPoint charts, tables, SmartArt, shapes, or grouped objects as the slide-design route.
- Python/Pillow/canvas-drawn slide pages as the final design route.
- Bare HTML wireframes that look like editable PPT or web dashboards: thin boxes, card grids, generic icons, no governing proof object.
- A clean editable-style deck that is simply rasterized afterward.
- Using code-rendered wireframes as a temporary stand-in for a consulting exhibit.

## Sample Gate

Render only 1-2 representative samples first.

Use samples to test:

- visual system;
- title readability;
- dense text handling;
- proof-object strength;
- theme color balance;
- message hierarchy: one action title, one main proof object, one optional bottom takeaway, and low-weight source notes.

Wait for user approval before batch rendering.

## Packaging Acceptance Test

For a packaged PPTX:

- slide count equals source PNG count;
- each slide has exactly one picture object;
- each slide has zero editable text objects;
- each picture fills the full 16:9 slide area;
- source PNGs are retained alongside the PPTX;
- a contact sheet or representative preview is available;
- deck-level contact-sheet review confirms page-marker consistency, action-title scale consistency, header alignment consistency, bottom-synthesis consistency, and source-note consistency.

## Text Density And Accuracy

- Match the approved density target; do not simplify a dense consulting exhibit into a sparse poster unless the user asks.
- Provide exact action title and 3-6 must-keep text/number items attached to the proof object.
- Inspect rendered pages for title errors, wrong numbers, or illegible labels. HTML rendering makes text exact: any wrong number is a brief mistake, not a rendering accident — fix the brief, then the page.
