#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Pillow 将简报 JSON 绘制为 PNG（不依赖浏览器，适合服务端/工作流）。"""

from __future__ import annotations

import argparse
import json
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data.example.json"
DEFAULT_OUT = ROOT / "output" / "briefing.png"

NAVY = (11, 58, 110)
BLUE = (26, 102, 196)
TEAL = (46, 139, 168)
INK = (28, 36, 48)
MUTED = (95, 107, 122)
LINE = (196, 214, 230)
SOFT_BLUE = (232, 241, 251)
BG = (244, 247, 251)
WHITE = (255, 255, 255)
RED = (192, 57, 43)
ORANGE = (230, 126, 34)
GREEN = (31, 138, 91)
WARN_BG = (253, 236, 236)
ACTION_BG = (255, 244, 230)
PAGE_BG = (250, 248, 242)
WEEKDAY_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def _font_candidates(bold: bool = False) -> list[tuple[str, int]]:
    """一律优先微软雅黑。"""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    win_fonts = Path(windir) / "Fonts"
    wsl_fonts = Path("/mnt/c/Windows/Fonts")

    def win_set(root: Path) -> list[tuple[str, int]]:
        if bold:
            return [
                (str(root / "msyhbd.ttc"), 0),
                (str(root / "msyh.ttc"), 0),
                (str(root / "simhei.ttf"), 0),
            ]
        return [
            (str(root / "msyh.ttc"), 0),
            (str(root / "msyhbd.ttc"), 0),
            (str(root / "simhei.ttf"), 0),
            (str(root / "msjh.ttc"), 0),
        ]

    linux = [
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
        ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 0),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
    ]
    return win_set(win_fonts) + win_set(wsl_fonts) + linux


@lru_cache(maxsize=64)
def load_font(size: int, bold: bool = False):
    last_error = None
    for path, index in _font_candidates(bold=bold):
        if not Path(path).exists():
            continue
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            try:
                return ImageFont.truetype(path, size=size)
            except Exception as exc2:  # noqa: BLE001
                last_error = exc2
                continue
    raise RuntimeError(
        "未找到微软雅黑等中文字体。WSL 请确认 /mnt/c/Windows/Fonts/msyh.ttc 可读。"
        + (f" 最后错误: {last_error}" if last_error else "")
    )


def format_cn_date(as_of_date: str) -> str:
    from datetime import datetime

    try:
        dt = datetime.strptime(as_of_date.strip()[:10], "%Y-%m-%d")
        return f"{dt.year}年{dt.month}月{dt.day}日 {WEEKDAY_CN[dt.weekday()]}"
    except Exception:
        return as_of_date


def extract_clock(generated_at: str, fallback: str = "08:00") -> str:
    text = (generated_at or "").strip()
    if len(text) >= 5 and ":" in text:
        parts = text.replace("T", " ").split()
        for p in reversed(parts):
            if ":" in p:
                return p[:5]
    return fallback


def growth_color(value: str):
    text = str(value or "").strip()
    if text.startswith("+"):
        return GREEN
    if text.startswith("-") or text.startswith("−"):
        return RED
    return NAVY


class Drawer:
    def __init__(self, width: int = 900):
        self.width = width
        self.pad = 28
        self.y = self.pad
        self.img = Image.new("RGB", (width, 3600), PAGE_BG)
        self.draw = ImageDraw.Draw(self.img)
        self.font_title = load_font(36, bold=True)
        self.font_h2 = load_font(16, bold=True)
        self.font_body = load_font(14, bold=True)
        self.font_focus = load_font(18, bold=True)  # 聚焦语：放大两个号（约 14→18）
        self.font_small = load_font(13)
        self.font_tiny = load_font(11)
        self.font_kpi = load_font(22, bold=True)
        self.font_stat = load_font(20, bold=True)
        self.font_badge_time = load_font(22, bold=True)
        self.font_badge_label = load_font(12)
        self.font_side = load_font(14, bold=True)

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

    # Header —— 对齐「销售经营晨报」顶栏样式
    meta = data.get("meta") or {}
    brand_title = meta.get("brand_title") or "销售经营晨报"
    scope = meta.get("scope") or "省区经营管理"
    as_of_date = meta.get("as_of_date") or ""
    generated_at = meta.get("generated_at") or "08:00"
    clock = extract_clock(generated_at, meta.get("report_time") or "08:00")
    data_cutoff = meta.get("data_cutoff") or clock
    date_line = format_cn_date(as_of_date)
    sub_line = f"{scope}  |  {date_line}  |  数据截至 {data_cutoff}"

    header_top = d.y
    # 右侧「晨间速递」徽章
    badge_w, badge_h = 118, 64
    time_box = (d.width - d.pad - badge_w, header_top, d.width - d.pad, header_top + badge_h)
    d.round_rect(time_box, NAVY, radius=12)
    # 简易时钟图标（白圈）
    cx, cy = time_box[0] + 28, header_top + 22
    d.draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), outline=WHITE, width=2)
    d.draw.line((cx, cy, cx, cy - 5), fill=WHITE, width=2)
    d.draw.line((cx, cy, cx + 4, cy + 2), fill=WHITE, width=2)
    d.draw.text((time_box[0] + 42, header_top + 10), clock, font=d.font_badge_time, fill=WHITE)
    label = "晨间速递"
    lw = int(d.draw.textlength(label, font=d.font_badge_label))
    d.draw.text((time_box[0] + (badge_w - lw) // 2, header_top + 40), label, font=d.font_badge_label, fill=WHITE)

    # 左侧标题 + 副标题
    d.draw_text(x0, header_top + 2, brand_title, d.font_title, NAVY)
    d.draw_text(x0, header_top + 48, sub_line, d.font_small, MUTED, content_w - badge_w - 24)
    d.y = header_top + badge_h + 10

    # 顶栏分隔三线
    for dy, w in ((0, 1), (3, 3), (8, 1)):
        d.draw.line((x0, d.y + dy, x0 + content_w, d.y + dy), fill=NAVY, width=w)
    d.y += 18

    # 聚焦语
    focus = data.get("focus") or "聚焦预算进度、客户下单与一线执行"
    # 橙色靶心
    tx, ty = x0 + 10, d.y + 10
    d.draw.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), outline=ORANGE, width=3)
    d.draw.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=ORANGE)
    d.draw_text(x0 + 28, d.y + 2, focus, d.font_body, NAVY, content_w - 40)
    d.y += 36

    # 01 业绩追踪：整体 / 基量 两行四列
    perf = data.get("performance") or {}
    overall = perf.get("overall") or {}
    base = perf.get("base") or {}
    metrics_def = [
        ("budget", "预算额", "coin"),
        ("sales", "销额", "bars"),
        ("achieve_rate", "达成率", "donut"),
        ("growth_rate", "增长率", "arrow"),
    ]

    def draw_metric_icon(kind: str, box, accent):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if kind == "coin":
            d.draw.ellipse((cx - 8, cy - 6, cx + 8, cy + 6), outline=accent, width=2)
            d.draw.ellipse((cx - 8, cy - 10, cx + 8, cy - 2), outline=accent, width=2)
        elif kind == "bars":
            d.draw.rectangle((cx - 10, cy + 2, cx - 5, cy + 8), fill=accent)
            d.draw.rectangle((cx - 3, cy - 2, cx + 2, cy + 8), fill=accent)
            d.draw.rectangle((cx + 4, cy - 6, cx + 9, cy + 8), fill=accent)
        elif kind == "donut":
            d.draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), outline=accent, width=3)
            d.draw.pieslice((cx - 8, cy - 8, cx + 8, cy + 8), start=270, end=90, fill=accent)
            d.draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=WHITE)
        else:  # arrow
            d.draw.polygon([(cx, cy - 8), (cx + 7, cy + 2), (cx + 2, cy + 2), (cx + 2, cy + 8),
                            (cx - 2, cy + 8), (cx - 2, cy + 2), (cx - 7, cy + 2)], fill=accent)

    def draw_perf_row(row_label: str, side_color, values: dict, y: int, row_h: int):
        side_w = 36
        d.round_rect((x0 + 12, y, x0 + 12 + side_w, y + row_h - 8), side_color, radius=8)
        # 竖排文字
        chars = list(row_label)
        ch_h = 16
        start_y = y + (row_h - 8 - len(chars) * ch_h) // 2
        for i, ch in enumerate(chars):
            tw = int(d.draw.textlength(ch, font=d.font_side))
            d.draw.text((x0 + 12 + (side_w - tw) // 2, start_y + i * ch_h), ch, font=d.font_side, fill=WHITE)

        grid_x = x0 + 12 + side_w + 8
        grid_w = content_w - (grid_x - x0) - 12
        cell_w = grid_w // 4
        for i, (key, suffix, icon) in enumerate(metrics_def):
            cx1 = grid_x + i * cell_w
            cx2 = cx1 + cell_w - 6
            d.round_rect((cx1, y, cx2, y + row_h - 8), WHITE, outline=LINE, radius=8)
            label = f"{row_label}{suffix}"
            d.draw_text(cx1 + 10, y + 8, label, d.font_tiny, MUTED)
            val = values.get(key) or "—"
            color = growth_color(val) if key == "growth_rate" else NAVY
            d.draw_text(cx1 + 10, y + 28, str(val), d.font_kpi, color)
            icon_box = (cx2 - 36, y + row_h - 40, cx2 - 8, y + row_h - 14)
            draw_metric_icon(icon, icon_box, TEAL if row_label == "基量" else BLUE)

    block_top = d.y
    row_h = 88
    block_h = 34 + row_h * 2 + 18
    d.round_rect((x0, block_top, x0 + content_w, block_top + block_h), SOFT_BLUE, outline=LINE, radius=12)
    # 左上角页签
    tab = "01 业绩追踪"
    tab_w = int(d.draw.textlength(tab, font=d.font_tiny)) + 20
    d.round_rect((x0 + 14, block_top + 10, x0 + 14 + tab_w, block_top + 30), NAVY, radius=6)
    d.draw.text((x0 + 24, block_top + 12), tab, font=d.font_tiny, fill=WHITE)

    draw_perf_row("整体", NAVY, overall, block_top + 38, row_h)
    draw_perf_row("基量", TEAL, base, block_top + 38 + row_h, row_h)
    d.y = block_top + block_h + 14

    def section_start(num: str, title: str, height_guess: int = 40):
        top = d.y
        d.round_rect((x0, top, x0 + content_w, top + height_guess), WHITE, outline=LINE, radius=14)
        d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
        d.draw.text((x0 + 19, top + 20), num, font=d.font_tiny, fill=WHITE)
        d.draw.text((x0 + 52, top + 18), title, font=d.font_h2, fill=NAVY)
        return top

    # Section 02 bars（原销售组对比）
    items = data["section_01"]["items"]
    sec_h = 56 + len(items) * 42
    top = section_start("02", data["section_01"]["title"], sec_h)
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
    cities = "  ".join(data["section_02"].get("cities") or []) or "—"
    groups = "  ".join(data["section_02"].get("groups") or []) or "—"
    bottom20 = "  ".join(data["section_02"].get("bottom20_groups") or []) or "—"
    customers = data["section_02"].get("customers") or []
    left_h = 56 + 18 + d.text_height(cities, d.font_small, left_w - 28) + 10
    left_h += 18 + d.text_height(groups, d.font_small, left_w - 28) + 10
    left_h += 18 + d.text_height(bottom20, d.font_small, left_w - 28) + 16
    right_h = 56 + len(customers) * 28 + 16
    box_h = max(left_h, right_h)
    top = d.y
    d.round_rect((x0, top, x0 + left_w, top + box_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + left_w + 12, top, x0 + content_w, top + box_h), WHITE, outline=LINE, radius=14)
    d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
    d.draw.text((x0 + 19, top + 20), "03", font=d.font_tiny, fill=WHITE)
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
    d.draw.text((rx + 19, top + 20), "03", font=d.font_tiny, fill=WHITE)
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
    d.draw.text((x0 + 19, top + 20), "04", font=d.font_tiny, fill=WHITE)
    d.draw.text((x0 + 52, top + 18), p["title"], font=d.font_h2, fill=NAVY)
    stats = [
        ("年累计销额", p["sales"], f"增额 {p['delta']}"),
        ("累计进度", p["progress"], f"同期实际 {p['peer_progress']}"),
        ("同比增速", p.get("yoy") or "—", f"进度第{p['progress_rank'] if p.get('progress_rank') is not None else '—'} / 增速第{p['growth_rank'] if p.get('growth_rank') is not None else '—'}"),
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
    d.draw.text((x0 + 19, top + 20), "05", font=d.font_tiny, fill=WHITE)
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
