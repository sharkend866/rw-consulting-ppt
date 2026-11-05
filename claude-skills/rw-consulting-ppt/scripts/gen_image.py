#!/usr/bin/env python3
"""Generate a photo-grade image through an OpenAI-compatible images API.

Optional step for RW Consulting PPT: used only when a page needs a real
photograph/illustration (not an SVG diagram). The user must have configured
an image-generation service.

Configuration:
    --provider doubao (default): Volcano Engine Ark, the official Doubao
        Seedream endpoint. Base URL and model are filled in automatically;
        only the API key is required (IMAGE_API_KEY or --api-key).
    --provider openai-compatible: any other OpenAI-compatible service.
        Requires IMAGE_API_BASE / IMAGE_API_MODEL (or --base-url / --model).

Watermark policy:
    Doubao/Ark watermarks images by default. This script requests
    watermark: false by default for doubao (override with --watermark true).
    If the provider rejects the request or the image still carries a
    watermark, do not use it: crop the watermark corner or regenerate.

Environment variables:
    IMAGE_API_KEY    the API key (all providers)
    IMAGE_API_BASE   override base URL (doubao default: Ark Beijing)
    IMAGE_API_MODEL  override model (doubao default: doubao-seedream-5-0-pro)

The script calls POST {base}/images/generations with the OpenAI schema and
saves the returned image (b64_json or url) as a local PNG.

Usage:
    python gen_image.py "prompt text" --out assets/hero.png [--size 2048x1152]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import urllib.request
from pathlib import Path

try:
    import certifi
except ImportError:
    certifi = None

DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_MODEL = "doubao-seedream-5-0-flash-260915"
DOUBAO_SIZE = "2K"
# Local key file, chmod 600, read when IMAGE_API_KEY is not set.
LOCAL_KEY_FILE = Path.home() / ".config" / "rw-consulting-ppt" / "ark-api-key"


def _ssl_context() -> ssl.SSLContext:
    # macOS framework Pythons often lack the system CA bundle; certifi fixes
    # CERTIFICATE_VERIFY_FAILED without disabling verification.
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def _post_json(url: str, payload: bytes, api_key: str, timeout: int = 300) -> bytes:
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=_ssl_context()) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc


def generate(
    prompt: str,
    size: str,
    base_url: str,
    api_key: str,
    model: str,
    watermark: bool | None,
) -> bytes:
    url = base_url.rstrip("/") + "/images/generations"
    payload_dict: dict = {"model": model, "prompt": prompt, "n": 1, "size": size}
    # Doubao/Ark watermarks images by default. Always request watermark-free
    # output unless the caller explicitly opts in; other OpenAI-compatible
    # providers may not know this field, so only send it when set.
    if watermark is not None:
        payload_dict["watermark"] = watermark
    payload = json.dumps(payload_dict).encode("utf-8")

    # Ark can rate-limit (429) on bursty calls; retry a few times with backoff.
    last_error: RuntimeError | None = None
    for attempt in range(1, 4):
        try:
            raw = _post_json(url, payload, api_key)
            data = json.loads(raw.decode("utf-8"))
            first = data.get("data", [{}])[0]
            if "b64_json" in first:
                return base64.b64decode(first["b64_json"])
            if "url" in first:
                with urllib.request.urlopen(
                    first["url"], timeout=300, context=_ssl_context()
                ) as image_response:
                    return image_response.read()
            raise RuntimeError(f"No image payload in response: {str(data)[:300]}")
        except RuntimeError as exc:
            last_error = exc
            message = str(exc)
            # Retry only transient rate limits; account-level pauses
            # (SetLimitExceeded) and other errors fail fast.
            if "429" not in message or "SetLimitExceeded" in message:
                break
            import time
            time.sleep(8 * attempt)
    assert last_error is not None
    raise last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--size", default=None)
    parser.add_argument(
        "--provider",
        default="doubao",
        choices=["doubao", "openai-compatible"],
        help="doubao: Volcano Ark (default); openai-compatible: any other service",
    )
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--watermark",
        default=None,
        choices=["true", "false"],
        help="override watermark request; doubao defaults to false (watermark-free)",
    )
    args = parser.parse_args()

    watermark: bool | None = (
        None if args.watermark is None else args.watermark == "true"
    )
    if args.provider == "doubao" and args.watermark is None:
        watermark = False

    api_key = args.api_key or os.environ.get("IMAGE_API_KEY")
    if not api_key and LOCAL_KEY_FILE.exists():
        api_key = LOCAL_KEY_FILE.read_text(encoding="utf-8").strip()
    base_url = args.base_url or os.environ.get("IMAGE_API_BASE")
    model = args.model or os.environ.get("IMAGE_API_MODEL")
    size = args.size
    if args.provider == "doubao":
        base_url = base_url or DOUBAO_BASE_URL
        model = model or DOUBAO_MODEL
        size = size or DOUBAO_SIZE
    else:
        size = size or "2048x1152"

    missing = [name for name, value in (
        ("api-key", api_key), ("base-url", base_url), ("model", model),
    ) if not value]
    if missing:
        raise SystemExit(
            "Missing image API configuration: " + ", ".join(missing)
            + ". Set IMAGE_API_KEY (and, for openai-compatible providers,"
            " IMAGE_API_BASE / IMAGE_API_MODEL) or pass --api-key / --base-url / --model."
        )

    image_bytes = generate(args.prompt, args.size, base_url, api_key, model, watermark)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(image_bytes)
    print(f"saved {args.out} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    main()
