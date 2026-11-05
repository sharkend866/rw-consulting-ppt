#!/usr/bin/env python3
"""Check all runtime dependencies for the Claude Code skills in this repo.

Usage:
    python check_env.py

Checks and reports:
  1. Python >= 3.10                 (required)
  2. pip packages                   (required: install with requirements.txt)
  3. Google Chrome                  (required for slide rendering)
  4. LibreOffice                    (optional: render preview in image-to-editable-ppt)
  5. Image API key                  (optional: photo-grade images via gen_image.py)
  6. Skills in ~/.claude/skills/    (required to invoke /rw-consulting-ppt etc.)

Exit code: 0 = all required dependencies present, 1 = something required is missing.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import sys
from pathlib import Path

REQUIRED_PIP = {
    "pptx": "python-pptx",
    "PIL": "Pillow",
    "playwright": "playwright",
    "certifi": "certifi",
}

CHROME_PATHS = {
    "Darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ],
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "Linux": [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ],
}

SOFFICE_PATHS = {
    "Darwin": [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ],
    "Windows": [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
    ],
    "Linux": [
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
    ],
}

KEY_FILE = Path.home() / ".config" / "rw-consulting-ppt" / "ark-api-key"
SKILLS = ["rw-consulting-ppt", "image-to-editable-ppt"]

REQUIRED = "required"
OPTIONAL = "optional"


def check_python() -> tuple[str, str, str]:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        return REQUIRED, "ok", f"Python {version}"
    return REQUIRED, "fail", f"Python {version}（需要 3.10+）"


def check_pip() -> list[tuple[str, str, str]]:
    rows = []
    for module, package in REQUIRED_PIP.items():
        if importlib.util.find_spec(module) is not None:
            rows.append((REQUIRED, "ok", package))
        else:
            rows.append((REQUIRED, "fail", f"{package} 未安装"))
    return rows


def find_executable(paths: list[str]) -> str | None:
    for path in paths:
        if Path(path).exists():
            return path
    for name in ("chrome", "google-chrome", "chromium", "soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    return None


def check_chrome() -> tuple[str, str, str]:
    found = find_executable(CHROME_PATHS.get(platform.system(), []))
    if found:
        return REQUIRED, "ok", f"Google Chrome（{found}）"
    return REQUIRED, "fail", "Google Chrome 未找到（渲染截图必需）"


def check_soffice() -> tuple[str, str, str]:
    found = find_executable(SOFFICE_PATHS.get(platform.system(), []))
    if found:
        return OPTIONAL, "ok", f"LibreOffice（{found}）"
    hint = "brew install --cask libreoffice" if platform.system() == "Darwin" else "https://www.libreoffice.org/download/"
    return OPTIONAL, "warn", f"LibreOffice 未安装（{hint}）"


def check_image_key() -> tuple[str, str, str]:
    if os.environ.get("IMAGE_API_KEY"):
        return OPTIONAL, "ok", "IMAGE_API_KEY 环境变量已设置"
    if KEY_FILE.exists():
        return OPTIONAL, "ok", f"{KEY_FILE}"
    return OPTIONAL, "warn", (
        "未配置豆包配图 key（如需照片级配图："
        "echo 'ark-你的key' > ~/.config/rw-consulting-ppt/ark-api-key && chmod 600 该文件）"
    )


def check_skills() -> list[tuple[str, str, str]]:
    skills_dir = Path.home() / ".claude" / "skills"
    rows = []
    for name in SKILLS:
        path = skills_dir / name
        if path.exists():
            rows.append((REQUIRED, "ok", f"~/.claude/skills/{name}"))
        else:
            rows.append(
                (REQUIRED, "fail",
                 f"~/.claude/skills/{name} 未安装（ln -sfn \"$PWD/claude-skills/{name}\" ~/.claude/skills/{name}）")
            )
    return rows


def main() -> None:
    print("=== 依赖检查 ===")
    rows = [check_python(), *check_pip(), check_chrome(), check_soffice(), check_image_key(), *check_skills()]

    has_fail = False
    for kind, status, message in rows:
        icon = {"ok": "✅", "warn": "⚠️", "fail": "❌"}[status]
        tag = "" if kind == REQUIRED else "（可选）"
        print(f"{icon} {message}{tag}")
        if status == "fail":
            has_fail = True

    print()
    if has_fail:
        print("存在缺失的必需依赖。修复提示：")
        print("  - pip 包：pip install -r requirements.txt")
        print("  - Chrome：安装 Google Chrome 后重跑本脚本")
        print("  - 技能：按上方命令软链到 ~/.claude/skills/")
        sys.exit(1)
    print("所有必需依赖就绪；⚠️ 项为可选功能，按需安装。")
    sys.exit(0)


if __name__ == "__main__":
    main()
