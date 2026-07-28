#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Pillow 将简报 JSON 绘制为 PNG（不依赖浏览器，适合服务端/工作流）。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data.example.json"
DEFAULT_OUT = ROOT / "output" / "briefing.png"

NAVY = (11, 58, 110)
BLUE = (26, 102, 196)
INK = (28, 36, 48)
MUTED = (95, 107, 122)
LINE = (217, 226, 236)
BG = (244, 247, 251)
WHITE = (255, 255, 255)
RED = (192, 57, 43)
ORANGE = (199, 119, 0)
WARN_BG = (253, 236, 236)
ACTION_BG = (255, 244, 230)
PAGE_BG = (238, 243, 248)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


class Drawer:
    def __init__(self, width: int = 860):
        self.width = width
        self.pad = 28
        self.y = self.pad
        self.img = Image.new("RGB", (width, 3200), PAGE_BG)
        self.draw = ImageDraw.Draw(self.img)
        self.font_title = load_font(34)
        self.font_h2 = load_font(16)
        self.font_body = load_font(13)
        self.font_small = load_font(12)
        self.font_tiny = load_font(11)
        self.font_kpi = load_font(26)
        self.font_stat = load_font(20)

    def text_height(self, text: str, font, max_width: int) -> int:
        lines = self.wrap(text, font, max_width)
        bbox = font.getbbox("字")
        line_h = bbox[3] - bbox[1] + 4
        return len(lines) * line_h

    def wrap(self, text: str, font, max_width: int) -> list[str]:
        if not text:
            return [""]
        lines: list[str] = []
        current = ""
        for ch in text:
            trial = current + ch
            if self.draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines

    def draw_text(self, x: int, y: int, text: str, font, fill, max_width: int | None = None) -> int:
        if max_width is None:
            self.draw.text((x, y), text, font=font, fill=fill)
            bbox = font.getbbox(text or " ")
            return bbox[3] - bbox[1]
        lines = self.wrap(text, font, max_width)
        bbox = font.getbbox("字")
        line_h = bbox[3] - bbox[1] + 4
        for i, line in enumerate(lines):
            self.draw.text((x, y + i * line_h), line, font=font, fill=fill)
        return len(lines) * line_h

    def round_rect(self, box, fill, outline=None, radius=14, width=1):
        self.draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def finish(self, out: Path):
        cropped = self.img.crop((0, 0, self.width, min(self.y + self.pad, self.img.height)))
        out.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(out, format="PNG")


def render(data: dict, out: Path) -> None:
    d = Drawer()
    x0 = d.pad
    content_w = d.width - 2 * d.pad

    # Header
    d.draw_text(x0, d.y, data["meta"]["title"], d.font_title, NAVY)
    time_box = (d.width - d.pad - 100, d.y, d.width - d.pad, d.y + 52)
    d.round_rect(time_box, NAVY, radius=10)
    clock = (data["meta"].get("generated_at") or "08:00")[-5:]
    d.draw.text((time_box[0] + 24, d.y + 6), "晨报时点", font=d.font_tiny, fill=(220, 230, 245))
    d.draw.text((time_box[0] + 18, d.y + 22), clock, font=d.font_h2, fill=WHITE)
    d.y += 42
    meta = f"{data['meta']['subtitle']} · {data['meta']['region']}  |  数据截至 {data['meta']['as_of_date']} · {data['meta']['owner']}"
    h = d.draw_text(x0, d.y, meta, d.font_small, MUTED, content_w - 110)
    d.y += h + 14

    # Headline
    hl_h = d.text_height(data["headline"], d.font_body, content_w - 120) + 28
    d.round_rect((x0, d.y, x0 + content_w, d.y + hl_h), NAVY, radius=12)
    d.round_rect((x0 + 14, d.y + 12, x0 + 86, d.y + 32), (40, 90, 150), radius=10)
    d.draw.text((x0 + 22, d.y + 14), "核心结论", font=d.font_tiny, fill=WHITE)
    d.draw_text(x0 + 96, d.y + 12, data["headline"], d.font_body, WHITE, content_w - 120)
    d.y += hl_h + 14

    # KPIs
    gap = 12
    card_w = (content_w - 3 * gap) // 4
    card_h = 118
    for i, kpi in enumerate(data["kpis"][:4]):
        cx = x0 + i * (card_w + gap)
        tone = kpi.get("tone")
        accent = RED if tone == "danger" else ORANGE if tone == "warn" else BLUE
        d.round_rect((cx, d.y, cx + card_w, d.y + card_h), WHITE, outline=LINE, radius=14)
        d.draw.rectangle((cx, d.y + 10, cx + 4, d.y + card_h - 10), fill=accent)
        d.draw_text(cx + 14, d.y + 12, kpi["label"], d.font_tiny, MUTED)
        d.draw_text(cx + 14, d.y + 34, kpi["value"], d.font_kpi, NAVY)
        d.draw_text(cx + 14, d.y + 68, kpi.get("sub", ""), d.font_tiny, MUTED, card_w - 24)
        badge = kpi.get("badge", "")
        bw = int(d.draw.textlength(badge, font=d.font_tiny)) + 16
        badge_bg = (253, 232, 230) if tone == "danger" else (255, 241, 219) if tone == "warn" else (232, 241, 251)
        badge_fg = accent
        d.round_rect((cx + 14, d.y + 88, cx + 14 + bw, d.y + 106), badge_bg, radius=10)
        d.draw.text((cx + 22, d.y + 90), badge, font=d.font_tiny, fill=badge_fg)
    d.y += card_h + 14

    def section_start(num: str, title: str, height_guess: int = 40):
        top = d.y
        d.round_rect((x0, top, x0 + content_w, top + height_guess), WHITE, outline=LINE, radius=14)
        d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
        d.draw.text((x0 + 19, top + 20), num, font=d.font_tiny, fill=WHITE)
        d.draw.text((x0 + 52, top + 18), title, font=d.font_h2, fill=NAVY)
        return top

    # Section 01 bars
    items = data["section_01"]["items"]
    sec_h = 56 + len(items) * 42
    top = section_start("01", data["section_01"]["title"], sec_h)
    # redraw with exact height already set via estimate; draw content
    yy = top + 52
    for item in items:
        rate = item.get("rate")
        name = item["name"]
        note = item.get("note") or ""
        d.draw_text(x0 + 18, yy, name, d.font_small, INK)
        track = (x0 + 150, yy + 4, x0 + content_w - 80, yy + 16)
        d.round_rect(track, (237, 242, 247), radius=8)
        width_ratio = 0.35 if rate is None else max(0.08, min(1.0, rate / 100))
        fill_w = int((track[2] - track[0]) * width_ratio)
        color = RED if (rate is not None and rate < 60) else ORANGE if (rate is None or rate < 80) else BLUE
        d.round_rect((track[0], track[1], track[0] + fill_w, track[3]), color, radius=8)
        rate_text = "—" if rate is None else f"{rate:.1f}%"
        d.draw_text(x0 + content_w - 70, yy, rate_text, d.font_small, NAVY)
        d.draw_text(x0 + 150, yy + 18, note, d.font_tiny, MUTED)
        yy += 42
    d.y = top + sec_h + 12

    # Section 02 two columns
    left_w = int(content_w * 0.52)
    right_w = content_w - left_w - 12
    cities = "  ".join(data["section_02"]["cities"])
    groups = "  ".join(data["section_02"]["groups"])
    bottom20 = "  ".join(data["section_02"]["bottom20_groups"])
    customers = data["section_02"]["customers"]
    left_h = 56 + 18 + d.text_height(cities, d.font_small, left_w - 28) + 10
    left_h += 18 + d.text_height(groups, d.font_small, left_w - 28) + 10
    left_h += 18 + d.text_height(bottom20, d.font_small, left_w - 28) + 16
    right_h = 56 + len(customers) * 28 + 16
    box_h = max(left_h, right_h)
    top = d.y
    d.round_rect((x0, top, x0 + left_w, top + box_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + left_w + 12, top, x0 + content_w, top + box_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
    d.draw.text((x0 + 19, top + 20), "02", font=d.font_tiny, fill=WHITE)
    d.draw.text((x0 + 52, top + 18), data["section_02"]["title"], font=d.font_h2, fill=NAVY)
    yy = top + 52
    d.draw_text(x0 + 16, yy, "下滑城市", d.font_tiny, MUTED)
    yy += 18
    yy += d.draw_text(x0 + 16, yy, cities, d.font_small, RED, left_w - 28) + 8
    d.draw_text(x0 + 16, yy, "下滑销售组", d.font_tiny, MUTED)
    yy += 18
    yy += d.draw_text(x0 + 16, yy, groups, d.font_small, RED, left_w - 28) + 8
    d.draw_text(x0 + 16, yy, "近三月达成率全国后20%销售组", d.font_tiny, MUTED)
    yy += 18
    d.draw_text(x0 + 16, yy, bottom20, d.font_small, BLUE, left_w - 28)

    rx = x0 + left_w + 12
    d.round_rect((rx + 14, top + 14, rx + 42, top + 42), NAVY, radius=8)
    d.draw.text((rx + 19, top + 20), "02", font=d.font_tiny, fill=WHITE)
    d.draw.text((rx + 52, top + 18), "下滑客户", font=d.font_h2, fill=NAVY)
    yy = top + 52
    for c in customers:
        d.round_rect((rx + 12, yy, rx + right_w - 12, yy + 24), BG, radius=8)
        d.draw_text(rx + 18, yy + 5, c, d.font_tiny, INK, right_w - 40)
        yy += 28
    d.y = top + box_h + 12

    # Section 03
    p = data["section_03"]
    sec_h = 140
    top = d.y
    d.round_rect((x0, top, x0 + content_w, top + sec_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
    d.draw.text((x0 + 19, top + 20), "03", font=d.font_tiny, fill=WHITE)
    d.draw.text((x0 + 52, top + 18), p["title"], font=d.font_h2, fill=NAVY)
    stats = [
        ("年累计销额", p["sales"], f"增额 {p['delta']}"),
        ("累计进度", p["progress"], f"同期实际 {p['peer_progress']}"),
        ("同比增速", p["yoy"], f"进度第{p['progress_rank']} / 增速第{p['growth_rank']}"),
    ]
    sw = (content_w - 48 - 20) // 3
    for i, (k, v, s) in enumerate(stats):
        sx = x0 + 16 + i * (sw + 10)
        sy = top + 54
        d.round_rect((sx, sy, sx + sw, sy + 70), BG, radius=12)
        d.draw_text(sx + 12, sy + 10, k, d.font_tiny, MUTED)
        d.draw_text(sx + 12, sy + 28, v, d.font_stat, NAVY)
        d.draw_text(sx + 12, sy + 52, s, d.font_tiny, MUTED)
    d.y = top + sec_h + 12

    # Section 04
    o = data["section_04"]
    custs = o.get("yesterday_customers") or []
    sec_h = 150 + len(custs) * 48
    top = d.y
    d.round_rect((x0, top, x0 + content_w, top + sec_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
    d.draw.text((x0 + 19, top + 20), "04", font=d.font_tiny, fill=WHITE)
    d.draw.text((x0 + 52, top + 18), o["title"], font=d.font_h2, fill=NAVY)
    no_group = "无" if not o.get("no_order_groups_5d") else "、".join(o["no_order_groups_5d"])
    no_cust = "无" if not o.get("no_order_customers_month") else "有"
    stats = [
        ("昨日下单额", o["order_amount"], f"下单量 {o['order_qty']}"),
        ("占全月预算", o["budget_share"], f"预算分母 {o['budget_base']}"),
        ("连续5日未下单组", no_group, f"当月未下单客户：{no_cust}"),
    ]
    for i, (k, v, s) in enumerate(stats):
        sx = x0 + 16 + i * (sw + 10)
        sy = top + 54
        d.round_rect((sx, sy, sx + sw, sy + 70), BG, radius=12)
        d.draw_text(sx + 12, sy + 8, k, d.font_tiny, MUTED)
        vh = d.draw_text(sx + 12, sy + 26, str(v), d.font_stat if len(str(v)) < 8 else d.font_h2, NAVY, sw - 20)
        d.draw_text(sx + 12, sy + 26 + max(vh, 22), s, d.font_tiny, MUTED, sw - 20)
    yy = top + 136
    d.draw_text(x0 + 16, yy, "昨日下单客户", d.font_tiny, MUTED)
    yy += 20
    for c in custs:
        d.round_rect((x0 + 16, yy, x0 + content_w - 16, yy + 40), BG, radius=10)
        line1 = f"{c['code']} {c['name']}"
        line2 = f"{c['group']} · 下单额 {c['amount']} · 下单量 {c['qty']}"
        d.draw_text(x0 + 24, yy + 6, line1, d.font_small, NAVY, content_w - 56)
        d.draw_text(x0 + 24, yy + 22, line2, d.font_tiny, MUTED, content_w - 56)
        yy += 48
    d.y = top + sec_h + 12

    # Warnings / Actions
    box_h = 40 + max(len(data["warnings"]), len(data["actions"])) * 36 + 10
    half = (content_w - 12) // 2
    top = d.y
    d.round_rect((x0, top, x0 + half, top + box_h), WARN_BG, outline=(243, 198, 194), radius=14)
    d.round_rect((x0 + half + 12, top, x0 + content_w, top + box_h), ACTION_BG, outline=(240, 210, 160), radius=14)
    d.draw_text(x0 + 16, top + 14, "经营预警", d.font_h2, RED)
    d.draw_text(x0 + half + 28, top + 14, "今日关键动作", d.font_h2, ORANGE)
    yy = top + 44
    for i, w in enumerate(data["warnings"], 1):
        d.draw_text(x0 + 16, yy, f"{i}. {w}", d.font_small, INK, half - 32)
        yy += 36
    yy = top + 44
    for i, w in enumerate(data["actions"], 1):
        d.draw_text(x0 + half + 28, yy, f"{i}. {w}", d.font_small, INK, half - 40)
        yy += 36
    d.y = top + box_h + 14

    footer = f"{data['footer']['sources']}  |  {data['footer']['note']}  ·  {data['meta']['owner']}"
    h = d.draw_text(x0, d.y, footer, d.font_tiny, MUTED, content_w)
    d.y += h + 8
    d.finish(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pillow 渲染经营简报 PNG")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    render(data, args.out)
    print(f"已生成: {args.out.resolve()}")


if __name__ == "__main__":
    main()
