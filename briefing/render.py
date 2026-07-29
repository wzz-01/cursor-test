#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将简报 JSON + HTML 模板渲染为 PNG。

用法:
  python3 briefing/render.py
  python3 briefing/render.py --data briefing/data.example.json --out briefing/output/liaoning.png
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = ROOT / "template.html"
DEFAULT_DATA = ROOT / "data.example.json"
DEFAULT_OUT = ROOT / "output" / "briefing.png"


def build_html(template: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    # 避免 </script> 提前截断
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    if "__DATA_JSON__" not in template:
        raise ValueError("模板缺少 __DATA_JSON__ 占位符")
    return template.replace("__DATA_JSON__", payload)


def render_png(html_path: Path, out_path: Path, width: int = 900) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    chrome = "google-chrome"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},2400",
        f"--screenshot={out_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    # Chrome 默认会截整个视口；若需要按内容裁切，可用 Pillow 去底边空白
    try:
        from PIL import Image

        img = Image.open(out_path)
        # 简单去白边：从底部向上找非接近背景色像素
        px = img.load()
        w, h = img.size
        bg = px[0, 0]
        bottom = h - 1
        for y in range(h - 1, -1, -1):
            row_has_content = False
            for x in range(0, w, 8):
                if px[x, y] != bg:
                    row_has_content = True
                    break
            if row_has_content:
                bottom = min(h - 1, y + 16)
                break
        img.crop((0, 0, w, bottom + 1)).save(out_path)
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="渲染经营简报 PNG")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="简报 JSON 路径")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="HTML 模板路径")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="输出 PNG 路径")
    parser.add_argument("--width", type=int, default=900, help="截图视口宽度")
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    template = args.template.read_text(encoding="utf-8")
    html = build_html(template, data)

    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "briefing.html"
        html_path.write_text(html, encoding="utf-8")
        render_png(html_path, args.out, width=args.width)

    print(f"已生成: {args.out.resolve()}")


if __name__ == "__main__":
    main()
