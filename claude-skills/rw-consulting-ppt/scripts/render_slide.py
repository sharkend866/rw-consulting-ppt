#!/usr/bin/env python3
"""Render consulting slide HTML pages into 16:9 PNGs with Playwright.

This is the Claude Code replacement for Codex's Image2 full-slide generation:
the model authors a complete 1920x1080 HTML page (inline SVG proof objects,
system fonts), and this script screenshots it with the installed Google
Chrome. The PNGs are then packaged with package_image_deck.py.

Usage:
    python render_slide.py <input.html> --out <output.png>
    python render_slide.py <slides_dir> --out <out_dir>     # slide_*.html -> slide_NN.png
    python render_slide.py <slides_dir> --out <out_dir> --scale 1.5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

WIDTH = 1920
HEIGHT = 1080

HIDE_SCROLLBARS = """
body { margin: 0 !important; overflow: hidden !important;
       width: 1920px; height: 1080px; }
"""


def find_chrome(pw) -> str | None:
    """Use the installed Google Chrome; do not download Chromium."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    try:
        installed = pw.chromium.executable_path
        if installed and Path(installed).exists():
            return str(installed)
    except Exception:
        pass
    return None


def render_html(html_path: Path, png_path: Path, scale: float) -> dict:
    with sync_playwright() as pw:
        chrome = find_chrome(pw)
        if chrome is None:
            raise SystemExit(
                "Google Chrome was not found. Install it or set PLAYWRIGHT_CHROME_PATH."
            )
        browser = pw.chromium.launch(headless=True, executable_path=chrome)
        page = browser.new_page(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=scale,
        )
        try:
            page.goto(html_path.as_uri(), wait_until="networkidle", timeout=60000)
            # Wait for webfonts and any deferred JS rendering (charts etc.).
            page.evaluate("document.fonts && document.fonts.ready")
            page.add_style_tag(content=HIDE_SCROLLBARS)
            page.wait_for_timeout(300)
            page.screenshot(path=str(png_path), full_page=False)
        finally:
            browser.close()

    with Image.open(png_path) as image:
        width, height = image.size
    return {"html": str(html_path), "png": str(png_path), "size_px": [width, height]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=2.0)
    args = parser.parse_args()

    if args.input.is_dir():
        html_files = sorted(args.input.glob("slide_*.html"))
        if not html_files:
            raise SystemExit(f"No slide_*.html files found in {args.input}")
        args.out.mkdir(parents=True, exist_ok=True)
        jobs = [
            (html_file, args.out / f"{html_file.stem}.png") for html_file in html_files
        ]
    elif args.input.is_file():
        jobs = [(args.input, args.out)]
        args.out.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise SystemExit(f"Input not found: {args.input}")

    results = [render_html(html_file, png_path, args.scale) for html_file, png_path in jobs]
    for result in results:
        print(
            f"rendered {result['html']} -> {result['png']} "
            f"({result['size_px'][0]}x{result['size_px'][1]})"
        )


if __name__ == "__main__":
    main()
