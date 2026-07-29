#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Pillow 将简报 JSON 绘制为 PNG（不依赖浏览器，适合服务端/工作流）。"""

from __future__ import annotations

import argparse
import json
import math
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


def _ensure_kaiti_font() -> Path | None:
    """确保有可用楷体：优先系统楷体，否则下载开源霞鹜文楷 Bold。"""
    script_font = Path(__file__).resolve().parent / "fonts" / "LXGWWenKai-Bold.ttf"
    candidates = [
        script_font,
        Path("/mnt/c/Windows/Fonts/simkai.ttf"),
        Path("/mnt/c/Windows/Fonts/SIMKAI.TTF"),
        Path("/mnt/c/Windows/Fonts/STKAITI.TTF"),
        Path("/mnt/c/Windows/Fonts/STKaiti.ttf"),
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "simkai.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "STKAITI.TTF",
    ]
    for p in candidates:
        if p.exists() and p.stat().st_size > 100_000:
            return p

    script_font.parent.mkdir(parents=True, exist_ok=True)
    urls = [
        "https://cdn.jsdelivr.net/gh/lxgw/LxgwWenKai@v1.330/fonts/TTF/LXGWWenKai-Bold.ttf",
        "https://github.com/lxgw/LxgwWenKai/releases/download/v1.330/LXGWWenKai-Bold.ttf",
    ]
    import urllib.request

    for url in urls:
        try:
            print(f"正在下载楷体字体: {url}")
            urllib.request.urlretrieve(url, script_font)
            if script_font.exists() and script_font.stat().st_size > 1_000_000:
                print(f"楷体字体已就绪: {script_font}")
                return script_font
        except Exception as exc:  # noqa: BLE001
            print(f"下载失败: {exc}")
    return None


def _font_candidates(bold: bool = False, family: str = "yahei") -> list[tuple[str, int]]:
    """family: yahei=微软雅黑, heiti=黑体, kaiti=楷体。"""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    win_fonts = Path(windir) / "Fonts"
    wsl_fonts = Path("/mnt/c/Windows/Fonts")
    bundled = Path(__file__).resolve().parent / "fonts"

    def win_set(root: Path) -> list[tuple[str, int]]:
        if family == "kaiti":
            return [
                (str(root / "simkai.ttf"), 0),  # Windows 楷体（最像“楷体”）
                (str(root / "SIMKAI.TTF"), 0),
                (str(root / "STKAITI.TTF"), 0),  # 华文楷体
                (str(root / "STKaiti.ttf"), 0),
                (str(root / "simkai.ttc"), 0),
                (str(bundled / "LXGWWenKai-Bold.ttf"), 0),  # 开源文楷兜底
            ]
        if family == "heiti":
            return [
                (str(root / "simhei.ttf"), 0),
                (str(root / "SIMHEI.TTF"), 0),
                (str(root / "msyhbd.ttc"), 0),
                (str(root / "msyh.ttc"), 0),
            ]
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

    if family == "kaiti":
        # 先确保字体文件存在（可能触发下载）
        ensured = _ensure_kaiti_font()
        linux = [
            (str(ensured), 0) if ensured else ("", 0),
            (str(bundled / "LXGWWenKai-Bold.ttf"), 0),
            ("/usr/share/fonts/truetype/arphic/ukai.ttc", 0),
        ]
        return [c for c in win_set(win_fonts) + win_set(wsl_fonts) + linux if c[0]]
    if family == "heiti":
        linux = [
            ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
        ]
    else:
        linux = [
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
            ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 0),
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
        ]
    return win_set(win_fonts) + win_set(wsl_fonts) + linux


# 记录实际加载到的字体路径，便于排查“看起来不像楷体”
_LOADED_FONT_PATHS: dict[str, str] = {}


@lru_cache(maxsize=64)
def load_font(size: int, bold: bool = False, family: str = "yahei"):
    last_error = None
    for path, index in _font_candidates(bold=bold, family=family):
        if not path or not Path(path).exists():
            continue
        try:
            font = ImageFont.truetype(path, size=size, index=index)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            try:
                font = ImageFont.truetype(path, size=size)
            except Exception as exc2:  # noqa: BLE001
                last_error = exc2
                continue
        key = f"{family}:{size}:{bold}"
        _LOADED_FONT_PATHS[key] = path
        if family == "kaiti":
            print(f"[font] 楷体已加载: {path} @ {size}px")
        return font
    raise RuntimeError(
        "未找到楷体/雅黑字体。请确认存在 Windows 楷体 simkai.ttf，或允许脚本下载霞鹜文楷。"
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
    def __init__(self, width: int = 793, target_height: int = 1983):
        self.width = width
        self.target_height = target_height
        self.pad = 18
        self.y = self.pad
        self.img = Image.new("RGB", (width, 4200), PAGE_BG)
        self.draw = ImageDraw.Draw(self.img)
        # 手机竖版：字号略收，保证 793 宽可读
        self.font_title = load_font(36, bold=True, family="kaiti")  # 销售经营晨报
        self.font_h2 = load_font(15, bold=True, family="yahei")
        self.font_body = load_font(13, bold=True, family="yahei")
        self.font_focus = load_font(24, bold=True, family="kaiti")  # 聚焦语
        self.font_small = load_font(12, family="yahei")
        self.font_tiny = load_font(10, family="yahei")
        self.font_kpi = load_font(18, bold=True, family="yahei")
        self.font_kpi_lg = load_font(24, bold=True, family="yahei")  # 业绩追踪数字
        self.font_stat = load_font(17, bold=True, family="yahei")
        self.font_badge_time = load_font(24, bold=True, family="kaiti")  # 08:00
        self.font_badge_label = load_font(14, bold=True, family="kaiti")  # 晨间速递
        self.font_side = load_font(13, bold=True, family="yahei")

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

    def draw_text(self, x: int, y: int, text: str, font, fill, max_width: int | None = None, stroke: int = 0) -> int:
        kwargs = {}
        if stroke > 0:
            kwargs = {"stroke_width": stroke, "stroke_fill": fill}
        if max_width is None:
            self.draw.text((x, y), text, font=font, fill=fill, **kwargs)
            bbox = font.getbbox(text or " ")
            return bbox[3] - bbox[1]
        lines = self.wrap(text, font, max_width)
        bbox = font.getbbox("字")
        line_h = bbox[3] - bbox[1] + 4
        for i, line in enumerate(lines):
            self.draw.text((x, y + i * line_h), line, font=font, fill=fill, **kwargs)
        return len(lines) * line_h

    def round_rect(self, box, fill, outline=None, radius=14, width=1):
        self.draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def finish(self, out: Path):
        """裁剪内容后输出固定手机尺寸 793×1983。
        - 过长：等比缩小顶对齐
        - 略短（≥目标 75%）：轻微纵向拉满，避免大块留白
        - 过短：顶对齐 + 底部补色
        """
        h = min(max(self.y + self.pad, 1), self.img.height)
        cropped = self.img.crop((0, 0, self.width, h))
        tw, th = self.width, self.target_height
        if cropped.width != tw:
            nh = max(1, int(round(cropped.height * tw / float(cropped.width))))
            cropped = cropped.resize((tw, nh), Image.Resampling.LANCZOS)

        if cropped.height > th:
            scale = th / float(cropped.height)
            nw = max(1, int(round(cropped.width * scale)))
            resized = cropped.resize((nw, th), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (tw, th), PAGE_BG)
            canvas.paste(resized, ((tw - nw) // 2, 0))
        elif cropped.height >= int(th * 0.75):
            canvas = cropped.resize((tw, th), Image.Resampling.LANCZOS)
        else:
            canvas = Image.new("RGB", (tw, th), PAGE_BG)
            canvas.paste(cropped, (0, 0))

        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, format="PNG")
        print(f"[size] 输出 {tw}x{th}（内容原高 {h}）")



def render(data: dict, out: Path) -> None:
    """按手机竖版模板（一张图看全）渲染：业绩/拜访/推广/预警。"""
    d = Drawer()
    x0 = d.pad
    content_w = d.width - 2 * d.pad

    def empty(v):
        if v is None or v == "" or v == "—" or v == "-" or v == "None":
            return ""
        return str(v)

    def to_pct(v):
        if v is None or v == "" or v == "—":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        text = str(v).replace("%", "").replace(" ", "").replace("−", "-")
        try:
            return float(text)
        except Exception:
            return None

    def fmt_pct(v):
        p = to_pct(v)
        return "" if p is None else f"{p:.1f}%"

    def fmt_growth(v):
        p = to_pct(v)
        if p is None:
            return ""
        return f"+{p:.1f}%" if p > 0 else f"{p:.1f}%"

    # ---------- Header ----------
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
    badge_w, badge_h = 118, 66
    time_box = (d.width - d.pad - badge_w, header_top, d.width - d.pad, header_top + badge_h)
    d.round_rect(time_box, NAVY, radius=10)
    cx, cy = time_box[0] + 24, header_top + 22
    d.draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), outline=WHITE, width=2)
    d.draw.line((cx, cy, cx, cy - 5), fill=WHITE, width=2)
    d.draw.line((cx, cy, cx + 4, cy + 2), fill=WHITE, width=2)
    d.draw.text((time_box[0] + 38, header_top + 8), clock, font=d.font_badge_time, fill=WHITE)
    label = "晨间速递"
    lw = int(d.draw.textlength(label, font=d.font_badge_label))
    d.draw.text((time_box[0] + (badge_w - lw) // 2, header_top + 40), label, font=d.font_badge_label, fill=WHITE)
    d.draw_text(x0, header_top + 2, brand_title, d.font_title, NAVY, stroke=1)
    d.draw_text(x0, header_top + 44, sub_line, d.font_tiny, MUTED, content_w - badge_w - 12)
    d.y = header_top + badge_h + 8

    for dy, w in ((0, 1), (3, 2)):
        d.draw.line((x0, d.y + dy, x0 + content_w, d.y + dy), fill=NAVY, width=w)
    d.y += 14

    # ---------- Focus ----------
    focus = data.get("focus") or "聚焦预算进度、客户下单与一线执行"
    text_w = int(d.draw.textlength(focus, font=d.font_focus))
    icon_box = 26
    icon_gap = 10
    group_w = icon_box + icon_gap + text_w
    start_x = x0 + max(0, (content_w - group_w) // 2)
    ty = d.y + 14

    def draw_target_arrow(cx: int, cy: int, r: int = 10):
        d.draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ORANGE, width=2)
        d.draw.ellipse((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), outline=ORANGE, width=2)
        d.draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=ORANGE)
        ax, ay = cx + r + 4, cy - r - 3
        bx, by = cx + 1, cy - 1
        ang = math.atan2(by - ay, bx - ax)
        d.draw.line((ax, ay, bx, by), fill=ORANGE, width=2)
        ah = 6
        p1 = (bx, by)
        p2 = (bx - ah * math.cos(ang) + 3.5 * math.sin(ang), by - ah * math.sin(ang) - 3.5 * math.cos(ang))
        p3 = (bx - ah * math.cos(ang) - 3.5 * math.sin(ang), by - ah * math.sin(ang) + 3.5 * math.cos(ang))
        d.draw.polygon([p1, p2, p3], fill=ORANGE)
        back = 5
        d.draw.line((ax, ay, ax + back * math.cos(ang + 2.45), ay + back * math.sin(ang + 2.45)), fill=ORANGE, width=2)
        d.draw.line((ax, ay, ax + back * math.cos(ang - 2.45), ay + back * math.sin(ang - 2.45)), fill=ORANGE, width=2)

    draw_target_arrow(start_x + icon_box // 2, ty, 10)
    bbox = d.font_focus.getbbox(focus)
    text_h = bbox[3] - bbox[1]
    d.draw.text((start_x + icon_box + icon_gap, ty - text_h // 2 - 1), focus, font=d.font_focus, fill=NAVY, stroke_width=1, stroke_fill=NAVY)
    d.y += 48

    def section_badge(num: str, title: str, accent=NAVY):
        top = d.y
        d.round_rect((x0 + 2, top, x0 + 28, top + 22), accent, radius=6)
        nw = int(d.draw.textlength(num, font=d.font_tiny))
        d.draw.text((x0 + 2 + (26 - nw) // 2, top + 4), num, font=d.font_tiny, fill=WHITE)
        d.draw.text((x0 + 34, top + 2), title, font=d.font_h2, fill=accent)
        d.y = top + 26

    def draw_simple_icon(kind: str, box, accent):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if kind == "coin":
            for dy in (-5, 0, 5):
                d.draw.ellipse((cx - 7, cy + dy - 2, cx + 7, cy + dy + 2), outline=accent, width=2)
        elif kind == "bars":
            for i, h in enumerate((4, 7, 10, 12)):
                bx = cx - 10 + i * 5
                d.draw.rectangle((bx, cy + 6 - h, bx + 3, cy + 6), fill=accent)
        elif kind == "donut":
            d.draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=accent, width=2)
            d.draw.pieslice((cx - 7, cy - 7, cx + 7, cy + 7), start=270, end=100, fill=accent)
            d.draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=WHITE)
        elif kind == "progress":
            d.round_rect((cx - 12, cy - 3, cx + 12, cy + 3), (220, 230, 238), radius=3)
            d.round_rect((cx - 12, cy - 3, cx + 1, cy + 3), accent, radius=3)
        elif kind == "arrow":
            d.draw.polygon([(cx, cy - 7), (cx + 6, cy + 1), (cx + 2, cy + 1), (cx + 2, cy + 7), (cx - 2, cy + 7), (cx - 2, cy + 1), (cx - 6, cy + 1)], fill=accent)
        elif kind == "people":
            d.draw.ellipse((cx - 8, cy - 7, cx - 2, cy - 1), outline=accent, width=1)
            d.draw.ellipse((cx + 2, cy - 7, cx + 8, cy - 1), outline=accent, width=1)
            d.draw.arc((cx - 10, cy - 1, cx, cy + 8), 200, 340, fill=accent, width=1)
            d.draw.arc((cx, cy - 1, cx + 10, cy + 8), 200, 340, fill=accent, width=1)
        elif kind == "briefcase":
            d.draw.rectangle((cx - 8, cy - 3, cx + 8, cy + 6), outline=accent, width=1)
            d.draw.rectangle((cx - 3, cy - 6, cx + 3, cy - 3), outline=accent, width=1)
        elif kind == "target":
            d.draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=accent, width=2)
            d.draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=accent)
        elif kind == "store":
            d.draw.polygon([(cx - 8, cy), (cx, cy - 7), (cx + 8, cy)], outline=accent)
            d.draw.rectangle((cx - 6, cy, cx + 6, cy + 7), outline=accent, width=1)
        elif kind == "pins":
            d.draw.ellipse((cx - 3, cy - 6, cx + 3, cy), outline=accent, width=1)
            d.draw.line((cx, cy, cx, cy + 6), fill=accent, width=1)
            d.draw.ellipse((cx + 3, cy - 3, cx + 8, cy + 2), outline=accent, width=1)
        elif kind == "check":
            d.draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=accent, width=2)
            d.draw.line((cx - 3, cy, cx - 1, cy + 3), fill=accent, width=2)
            d.draw.line((cx - 1, cy + 3, cx + 4, cy - 3), fill=accent, width=2)
        elif kind == "megaphone":
            d.draw.polygon([(cx - 6, cy - 2), (cx + 6, cy - 6), (cx + 6, cy + 6), (cx - 6, cy + 2)], fill=accent)
        elif kind == "star":
            d.draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=accent, width=2)
            d.draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=accent)
        elif kind == "money":
            d.draw.ellipse((cx - 7, cy - 5, cx + 7, cy + 5), outline=accent, width=2)
        elif kind == "flag":
            d.draw.line((cx - 4, cy - 7, cx - 4, cy + 7), fill=accent, width=2)
            d.draw.polygon([(cx - 3, cy - 7), (cx + 7, cy - 3), (cx - 3, cy + 1)], fill=accent)
        elif kind == "pair":
            d.draw.ellipse((cx - 7, cy - 6, cx - 1, cy), outline=accent, width=1)
            d.draw.ellipse((cx + 1, cy - 6, cx + 7, cy), outline=accent, width=1)
        else:
            d.draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=accent, width=2)

    # ---------- 01 业绩追踪 ----------
    section_badge("01", "业绩追踪")
    perf = data.get("performance") or {}
    overall = perf.get("overall") or {}
    base = perf.get("base") or {}
    metrics_def = [
        ("budget", "预算额", "coin"),
        ("sales", "销额", "bars"),
        ("achieve_rate", "达成率", "donut"),
        ("order_progress", "订单进度", "progress"),
        ("growth_rate", "增长率", "arrow"),
    ]
    title_h = 0
    row_h = 98
    side_w = 28
    pad = 8
    block_h = row_h * 2 + pad
    block_top = d.y
    d.round_rect((x0, block_top, x0 + content_w, block_top + block_h), WHITE, outline=LINE, radius=10)

    def draw_perf_row(row_label: str, side_color, values: dict, y: int):
        d.round_rect((x0 + pad, y + 3, x0 + pad + side_w, y + row_h - 3), side_color, radius=6)
        chars = list(row_label)
        ch_h = 14
        start_y = y + (row_h - len(chars) * ch_h) // 2
        for i, ch in enumerate(chars):
            tw = int(d.draw.textlength(ch, font=d.font_side))
            d.draw.text((x0 + pad + (side_w - tw) // 2, start_y + i * ch_h), ch, font=d.font_side, fill=WHITE)
        grid_x = x0 + pad + side_w + 4
        grid_w = content_w - (grid_x - x0) - pad
        n = len(metrics_def)
        cell_w = grid_w // n
        row_accent = TEAL if row_label == "基量" else NAVY
        d.draw.rectangle((grid_x, y + 3, grid_x + cell_w * n, y + row_h - 3), outline=LINE, width=1)
        for i, (key, suffix, icon) in enumerate(metrics_def):
            cx1 = grid_x + i * cell_w
            cx2 = cx1 + cell_w
            if i > 0:
                d.draw.line((cx1, y + 3, cx1, y + row_h - 3), fill=LINE, width=1)
            label_t = suffix if key in ("order_progress", "growth_rate") else f"{row_label}{suffix}"
            val = empty(values.get(key))
            if key == "growth_rate":
                num_color = growth_color(val) if val else row_accent
                icon_color = GREEN if val.startswith("+") else (RED if val.startswith("-") else row_accent)
            else:
                num_color = row_accent
                icon_color = TEAL if row_label == "基量" else BLUE
            mid = (cx1 + cx2) // 2
            lw = int(d.draw.textlength(label_t, font=d.font_tiny))
            d.draw.text((mid - lw // 2, y + 10), label_t, font=d.font_tiny, fill=MUTED)
            if val:
                vw = int(d.draw.textlength(val, font=d.font_kpi))
                d.draw.text((mid - vw // 2, y + 30), val, font=d.font_kpi, fill=num_color)
            draw_simple_icon(icon, (mid - 12, y + row_h - 30, mid + 12, y + row_h - 10), icon_color)

    draw_perf_row("整体", NAVY, overall, block_top)
    draw_perf_row("基量", TEAL, base, block_top + row_h)
    d.y = block_top + block_h + 12

    # 分区/销售组表（归属 01）
    s1 = data.get("section_groups") or data.get("section_01") or {}
    rows = s1.get("rows") or []
    if not rows and s1.get("items"):
        rows = [{"name": it.get("name"), "achieve_rate": it.get("rate"), "growth_rate": None, "base_achieve_rate": None, "order_amount_5d": ""} for it in s1["items"]]
    warn_below = float(s1.get("warn_below") or 90)
    title_02 = s1.get("title") or "分区 / 销售组业绩进度"
    header_h = 26
    row_h_tbl = 32
    title_h2 = 24
    table_h = title_h2 + header_h + max(1, len(rows)) * row_h_tbl + 8
    top = d.y
    d.round_rect((x0, top, x0 + content_w, top + table_h), WHITE, outline=LINE, radius=10)
    d.round_rect((x0 + 10, top + 8, x0 + 20, top + 18), NAVY, radius=2)
    d.draw.text((x0 + 26, top + 5), title_02, font=d.font_h2, fill=NAVY)

    cols = [
        ("name", "经销组", 0.22),
        ("achieve_rate", "达成率", 0.20),
        ("growth_rate", "增长率", 0.14),
        ("base_achieve_rate", "大单品达成率", 0.22),
        ("order_amount_5d", "近5日下单额", 0.22),
    ]
    usable = content_w - 20
    col_ws = [int(usable * c[2]) for c in cols]
    col_ws[-1] = usable - sum(col_ws[:-1])
    table_x = x0 + 10
    head_y = top + title_h2
    grid_bot = head_y + header_h + max(1, len(rows)) * row_h_tbl
    TABLE_BODY = (205, 220, 236)
    TABLE_ZEBRA = (190, 208, 228)
    d.draw.rectangle((table_x, head_y, table_x + usable, grid_bot), fill=TABLE_BODY)
    d.draw.rectangle((table_x, head_y, table_x + usable, head_y + header_h), fill=NAVY)
    cx = table_x
    for (_, label_c, _), cw in zip(cols, col_ws):
        tw = int(d.draw.textlength(label_c, font=d.font_tiny))
        d.draw.text((cx + (cw - tw) // 2, head_y + 7), label_c, font=d.font_tiny, fill=WHITE)
        cx += cw

    def draw_rate_cell(cx, ry, cw, rh, value, bar_color, text_color):
        txt = fmt_pct(value)
        pct = to_pct(value)
        if txt:
            tw = int(d.draw.textlength(txt, font=d.font_tiny))
            d.draw.text((cx + (cw - tw) // 2, ry + 3), txt, font=d.font_tiny, fill=text_color)
        bar_x1, bar_x2 = cx + 8, cx + cw - 8
        bar_y1, bar_y2 = ry + rh - 10, ry + rh - 5
        d.round_rect((bar_x1, bar_y1, bar_x2, bar_y2), (230, 236, 244), radius=2)
        if pct is not None:
            fill_w = int((bar_x2 - bar_x1) * max(0.0, min(pct / 100.0, 1.0)))
            if fill_w > 0:
                d.round_rect((bar_x1, bar_y1, bar_x1 + fill_w, bar_y2), bar_color, radius=2)

    for idx, row in enumerate(rows):
        ry = head_y + header_h + idx * row_h_tbl
        if idx % 2 == 1:
            d.draw.rectangle((table_x, ry, table_x + usable, ry + row_h_tbl), fill=TABLE_ZEBRA)
        achieve = to_pct(row.get("achieve_rate"))
        warn = achieve is not None and achieve < warn_below
        text_color = RED if warn else INK
        bar_overall = RED if warn else BLUE
        bar_base = RED if warn else TEAL
        cx = table_x
        d.draw.text((cx + 6, ry + 9), str(row.get("name") or ""), font=d.font_tiny, fill=text_color)
        cx += col_ws[0]
        draw_rate_cell(cx, ry, col_ws[1], row_h_tbl, row.get("achieve_rate"), bar_overall, text_color)
        cx += col_ws[1]
        gtxt = fmt_growth(row.get("growth_rate"))
        gcolor = RED if warn else (growth_color(gtxt) if gtxt else text_color)
        if gtxt:
            tw = int(d.draw.textlength(gtxt, font=d.font_tiny))
            d.draw.text((cx + (col_ws[2] - tw) // 2, ry + 9), gtxt, font=d.font_tiny, fill=gcolor)
        cx += col_ws[2]
        draw_rate_cell(cx, ry, col_ws[3], row_h_tbl, row.get("base_achieve_rate"), bar_base, text_color)
        cx += col_ws[3]
        amt = empty(row.get("order_amount_5d"))
        if amt:
            tw = int(d.draw.textlength(amt, font=d.font_tiny))
            d.draw.text((cx + (col_ws[4] - tw) // 2, ry + 9), amt, font=d.font_tiny, fill=text_color)

    d.draw.line((table_x, head_y + header_h, table_x + usable, head_y + header_h), fill=WHITE, width=1)
    for idx in range(len(rows)):
        ry = head_y + header_h + (idx + 1) * row_h_tbl
        d.draw.line((table_x, ry, table_x + usable, ry), fill=WHITE, width=1)
    vx = table_x
    for cw in col_ws[:-1]:
        vx += cw
        d.draw.line((vx, head_y, vx, grid_bot), fill=WHITE, width=1)
    d.y = top + table_h + 12

    # 预算订单进度后10客户
    b10 = data.get("section_bottom10") or {}
    b_rows = b10.get("rows") or []
    b_title = b10.get("title") or "预算订单进度后10客户"
    show_n = min(len(b_rows), 6) if b_rows else 0
    b_row_h = 28
    b_head = 24
    b_title_h = 22
    b_h = b_title_h + b_head + (show_n if show_n else 1) * b_row_h + 8
    top = d.y
    d.round_rect((x0, top, x0 + content_w, top + b_h), WHITE, outline=LINE, radius=10)
    d.round_rect((x0 + 10, top + 7, x0 + 20, top + 17), ORANGE, radius=2)
    d.draw.text((x0 + 26, top + 4), b_title, font=d.font_h2, fill=NAVY)
    bx = x0 + 10
    bw = content_w - 20
    bcols = [0.34, 0.14, 0.14, 0.14, 0.24]
    bws = [int(bw * x) for x in bcols]
    bws[-1] = bw - sum(bws[:-1])
    hy = top + b_title_h
    d.draw.rectangle((bx, hy, bx + bw, hy + b_head), fill=(90, 110, 140))
    labels = ["客户", "预算", "实际", "预估", "订单进度"]
    cx = bx
    for lab, cw in zip(labels, bws):
        tw = int(d.draw.textlength(lab, font=d.font_tiny))
        d.draw.text((cx + (cw - tw) // 2, hy + 5), lab, font=d.font_tiny, fill=WHITE)
        cx += cw
    if not b_rows:
        d.draw.text((bx + 8, hy + b_head + 8), "暂无数据", font=d.font_tiny, fill=MUTED)
    else:
        for i in range(show_n):
            row = b_rows[i]
            ry = hy + b_head + i * b_row_h
            if i % 2:
                d.draw.rectangle((bx, ry, bx + bw, ry + b_row_h), fill=BG)
            vals = [empty(row.get("name")), empty(row.get("budget")), empty(row.get("actual")), empty(row.get("forecast"))]
            cx = bx
            for vi, (val, cw) in enumerate(zip(vals, bws[:-1])):
                if val:
                    d.draw.text((cx + 4, ry + 7), val[:10], font=d.font_tiny, fill=INK)
                cx += cw
            # progress
            pct = to_pct(row.get("order_progress"))
            track = (cx + 4, ry + 10, cx + bws[-1] - 36, ry + 18)
            d.round_rect(track, (230, 236, 244), radius=3)
            if pct is not None:
                fw = int((track[2] - track[0]) * max(0.0, min(pct / 100.0, 1.0)))
                if fw > 0:
                    d.round_rect((track[0], track[1], track[0] + fw, track[3]), ORANGE, radius=3)
                pt = f"{pct:.0f}%"
                d.draw.text((cx + bws[-1] - 32, ry + 7), pt, font=d.font_tiny, fill=RED)
    d.y = top + b_h + 12

    # ---------- 02 拜访执行 ----------
    section_badge("02", "拜访执行", BLUE)
    visit = data.get("section_visit") or {}
    v_metrics = visit.get("metrics") or []
    while len(v_metrics) < 6:
        v_metrics.append({"label": "", "value": "", "icon": "target"})
    card_h = 70
    gap = 6
    cols_n = 3
    card_w = (content_w - gap * (cols_n - 1)) // cols_n
    top = d.y
    for i, m in enumerate(v_metrics[:6]):
        r, c = divmod(i, cols_n)
        sx = x0 + c * (card_w + gap)
        sy = top + r * (card_h + gap)
        d.round_rect((sx, sy, sx + card_w, sy + card_h), WHITE, outline=LINE, radius=8)
        d.draw_text(sx + 8, sy + 8, empty(m.get("label")) or " ", d.font_tiny, MUTED, card_w - 16)
        val = empty(m.get("value"))
        if val:
            d.draw_text(sx + 8, sy + 26, val, d.font_stat, NAVY)
        draw_simple_icon(m.get("icon") or "target", (sx + card_w - 28, sy + card_h - 26, sx + card_w - 8, sy + card_h - 8), BLUE)
    d.y = top + 2 * (card_h + gap) + 6
    alert = empty(visit.get("alert"))
    if alert:
        d.round_rect((x0, d.y, x0 + content_w, d.y + 26), (255, 232, 230), outline=(240, 180, 170), radius=6)
        d.draw.polygon([(x0 + 14, d.y + 6), (x0 + 22, d.y + 20), (x0 + 6, d.y + 20)], fill=RED)
        d.draw.text((x0 + 28, d.y + 6), alert, font=d.font_small, fill=RED)
        d.y += 32
    else:
        d.y += 4

    # ---------- 03 推广执行 ----------
    section_badge("03", "推广执行", ORANGE)
    promo = data.get("section_promo") or {}
    p_metrics = promo.get("metrics") or []
    while len(p_metrics) < 6:
        p_metrics.append({"label": "", "value": "", "icon": "megaphone"})
    top = d.y
    for i, m in enumerate(p_metrics[:6]):
        r, c = divmod(i, cols_n)
        sx = x0 + c * (card_w + gap)
        sy = top + r * (card_h + gap)
        d.round_rect((sx, sy, sx + card_w, sy + card_h), WHITE, outline=LINE, radius=8)
        d.draw_text(sx + 8, sy + 8, empty(m.get("label")) or " ", d.font_tiny, MUTED, card_w - 16)
        val = empty(m.get("value"))
        if val:
            d.draw_text(sx + 8, sy + 26, val, d.font_stat, ORANGE)
        draw_simple_icon(m.get("icon") or "megaphone", (sx + card_w - 28, sy + card_h - 26, sx + card_w - 8, sy + card_h - 8), ORANGE)
    d.y = top + 2 * (card_h + gap) + 8

    # 图表区：近7日趋势 + 结构
    chart_h = 120
    left_w = int(content_w * 0.55)
    right_w = content_w - left_w - 8
    top = d.y
    d.round_rect((x0, top, x0 + left_w, top + chart_h), WHITE, outline=LINE, radius=8)
    d.round_rect((x0 + left_w + 8, top, x0 + content_w, top + chart_h), WHITE, outline=LINE, radius=8)
    d.draw.text((x0 + 8, top + 6), "近7日推广门店数趋势", font=d.font_tiny, fill=MUTED)
    d.draw.text((x0 + left_w + 16, top + 6), "推广门店结构(累计)", font=d.font_tiny, fill=MUTED)

    trend = promo.get("trend_7d") or []
    plot = (x0 + 12, top + 28, x0 + left_w - 12, top + chart_h - 12)
    d.draw.rectangle(plot, outline=LINE, width=1)
    if len(trend) >= 2:
        nums = [float(x) for x in trend]
        mn, mx = min(nums), max(nums)
        span = max(mx - mn, 1.0)
        pts = []
        for i, v in enumerate(nums):
            px = plot[0] + int((plot[2] - plot[0]) * i / (len(nums) - 1))
            py = plot[3] - int((plot[3] - plot[1]) * (v - mn) / span)
            pts.append((px, py))
        d.draw.line(pts, fill=ORANGE, width=2)
        for px, py in pts:
            d.draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=ORANGE)
    else:
        d.draw.text((plot[0] + 8, plot[1] + 20), "暂无数据", font=d.font_tiny, fill=MUTED)

    structure = promo.get("structure") or []
    sx0 = x0 + left_w + 16
    if structure:
        vals_f = []
        for s in structure:
            try:
                vals_f.append(float(str(s.get("value") or 0).replace("%", "")))
            except Exception:
                vals_f.append(0.0)
        max_v = max(vals_f) if vals_f else 1.0
        max_v = max_v or 1.0
        yy = top + 28
        for s in structure[:4]:
            lab = empty(s.get("label"))
            val = s.get("value")
            d.draw.text((sx0, yy), lab[:8], font=d.font_tiny, fill=INK)
            bar_x1 = sx0 + 56
            bar_x2 = x0 + content_w - 14
            d.round_rect((bar_x1, yy + 2, bar_x2, yy + 10), (235, 238, 242), radius=3)
            try:
                vv = float(str(val).replace("%", "")) if val not in (None, "") else 0
            except Exception:
                vv = 0
            fw = int((bar_x2 - bar_x1) * max(0.0, min(vv / max_v, 1.0)))
            if fw > 0:
                d.round_rect((bar_x1, yy + 2, bar_x1 + fw, yy + 10), TEAL, radius=3)
            yy += 16
    else:
        d.draw.text((sx0, top + 48), "暂无数据", font=d.font_tiny, fill=MUTED)
    d.y = top + chart_h + 12

    # ---------- 04 经营预警 ----------
    section_badge("04", "经营预警", RED)
    warn = data.get("section_warn") or {}
    blocks = warn.get("blocks") or []
    # 兼容旧数据：从 section_02 / section_04 拼装
    if not blocks:
        s2 = data.get("section_02") or {}
        s4 = data.get("section_04") or {}
        blocks = [
            {
                "key": "A",
                "title": s2.get("title") or "连续三月同比下滑",
                "tone": "red",
                "lines": [
                    "城市：" + ("、".join(s2.get("cities") or []) or "—"),
                    "销售组：" + ("、".join(s2.get("groups") or []) or "—"),
                ],
            },
            {
                "key": "B",
                "title": "近5日未下单销售组",
                "tone": "orange",
                "lines": s4.get("no_order_groups_5d") or ["无"],
            },
            {
                "key": "C",
                "title": "下滑客户",
                "tone": "red",
                "lines": (s2.get("customers") or [])[:8],
            },
        ]

    for blk in blocks[:3]:
        tone = blk.get("tone") or "red"
        bg = WARN_BG if tone == "red" else ACTION_BG
        outline = (243, 198, 194) if tone == "red" else (240, 210, 160)
        accent = RED if tone == "red" else ORANGE
        lines = blk.get("lines") or []
        # 限制行数避免超高
        lines = lines[:6]
        box_h = 28 + max(1, len(lines)) * 16 + 6
        top = d.y
        d.round_rect((x0, top, x0 + content_w, top + box_h), bg, outline=outline, radius=8)
        key = str(blk.get("key") or "")
        d.round_rect((x0 + 8, top + 6, x0 + 28, top + 24), accent, radius=5)
        kw = int(d.draw.textlength(key, font=d.font_tiny))
        d.draw.text((x0 + 8 + (20 - kw) // 2, top + 8), key, font=d.font_tiny, fill=WHITE)
        d.draw.text((x0 + 34, top + 7), empty(blk.get("title")), font=d.font_h2, fill=accent)
        yy = top + 28
        for line in lines:
            d.draw_text(x0 + 12, yy, f"· {line}", d.font_tiny, INK, content_w - 24)
            yy += 16
        d.y = top + box_h + 8

    # ---------- Footer ----------
    d.y += 4
    left_footer = "数据源：CRM | SFA | 终端巡检系统 | 市场活动平台"
    right_footer = "制作部门：数据组"
    d.draw.text((x0, d.y), left_footer, font=d.font_tiny, fill=MUTED)
    rw = int(d.draw.textlength(right_footer, font=d.font_tiny))
    d.draw.text((x0 + content_w - rw, d.y), right_footer, font=d.font_tiny, fill=MUTED)
    d.y += 20
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
