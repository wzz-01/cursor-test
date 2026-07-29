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
        """裁剪内容后输出固定手机尺寸 793×1983（不足底部补色，过长等比缩小顶对齐）。"""
        h = min(max(self.y + self.pad, 1), self.img.height)
        cropped = self.img.crop((0, 0, self.width, h))
        tw, th = self.width, self.target_height
        canvas = Image.new("RGB", (tw, th), PAGE_BG)
        if cropped.height > th:
            scale = th / float(cropped.height)
            nw = max(1, int(round(cropped.width * scale)))
            nh = th
            resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
            canvas.paste(resized, ((tw - nw) // 2, 0))
        else:
            # 宽对齐到目标宽，高度按比例；再贴到画布顶部，底部留白
            if cropped.width != tw:
                nh = max(1, int(round(cropped.height * tw / float(cropped.width))))
                resized = cropped.resize((tw, nh), Image.Resampling.LANCZOS)
            else:
                resized = cropped
            if resized.height > th:
                scale = th / float(resized.height)
                resized = resized.resize((max(1, int(round(resized.width * scale))), th), Image.Resampling.LANCZOS)
                canvas.paste(resized, ((tw - resized.width) // 2, 0))
            else:
                canvas.paste(resized, (0, 0))
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, format="PNG")
        print(f"[size] 输出 {tw}x{th}（内容原高 {cropped.height}）")


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
    # 右侧「晨间速递」徽章（楷体加大后加宽加高）
    badge_w, badge_h = 120, 70
    time_box = (d.width - d.pad - badge_w, header_top, d.width - d.pad, header_top + badge_h)
    d.round_rect(time_box, NAVY, radius=10)
    # 简易时钟图标（白圈）
    cx, cy = time_box[0] + 26, header_top + 22
    d.draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), outline=WHITE, width=2)
    d.draw.line((cx, cy, cx, cy - 5), fill=WHITE, width=2)
    d.draw.line((cx, cy, cx + 4, cy + 3), fill=WHITE, width=2)
    d.draw.text((time_box[0] + 40, header_top + 10), clock, font=d.font_badge_time, fill=WHITE, stroke_width=1, stroke_fill=WHITE)
    label = "晨间速递"
    lw = int(d.draw.textlength(label, font=d.font_badge_label))
    d.draw.text((time_box[0] + (badge_w - lw) // 2, header_top + 42), label, font=d.font_badge_label, fill=WHITE, stroke_width=1, stroke_fill=WHITE)

    # 左侧标题（楷体加粗）+ 副标题（雅黑）
    d.draw_text(x0, header_top + 2, brand_title, d.font_title, NAVY, stroke=1)
    d.draw_text(x0, header_top + 48, sub_line, d.font_small, MUTED, content_w - badge_w - 16)
    d.y = header_top + badge_h + 10

    # 顶栏分隔三线
    for dy, w in ((0, 1), (3, 3), (8, 1)):
        d.draw.line((x0, d.y + dy, x0 + content_w, d.y + dy), fill=NAVY, width=w)
    d.y += 18

    # 聚焦语：楷体加粗加大、整行居中；两侧为「靶子+箭」图标（与截图一致）
    focus = data.get("focus") or "聚焦预算进度、客户下单与一线执行"
    focus_font = d.font_focus
    text_w = int(d.draw.textlength(focus, font=focus_font))
    icon_gap = 14
    icon_box = 28  # 含箭头伸出的占位
    group_w = icon_box * 2 + icon_gap * 2 + text_w
    start_x = x0 + max(0, (content_w - group_w) // 2)
    ty = d.y + 18

    def draw_target_arrow(cx: int, cy: int, r: int = 11):
        """橘黄靶子 + 从右上射入靶心的箭（与截图一致）"""
        # 三层同心靶环
        d.draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ORANGE, width=2)
        d.draw.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), outline=ORANGE, width=2)
        d.draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=ORANGE)

        # 箭杆：右上 → 靶心
        ax, ay = cx + r + 5, cy - r - 4
        bx, by = cx + 1, cy - 1
        ang = math.atan2(by - ay, bx - ax)
        d.draw.line((ax, ay, bx, by), fill=ORANGE, width=2)

        # 箭头
        ah = 7
        p1 = (bx, by)
        p2 = (
            bx - ah * math.cos(ang) + 4.2 * math.sin(ang),
            by - ah * math.sin(ang) - 4.2 * math.cos(ang),
        )
        p3 = (
            bx - ah * math.cos(ang) - 4.2 * math.sin(ang),
            by - ah * math.sin(ang) + 4.2 * math.cos(ang),
        )
        d.draw.polygon([p1, p2, p3], fill=ORANGE)

        # 尾羽
        back = 6
        d.draw.line(
            (ax, ay, ax + back * math.cos(ang + 2.45), ay + back * math.sin(ang + 2.45)),
            fill=ORANGE,
            width=2,
        )
        d.draw.line(
            (ax, ay, ax + back * math.cos(ang - 2.45), ay + back * math.sin(ang - 2.45)),
            fill=ORANGE,
            width=2,
        )

    draw_target_arrow(start_x + icon_box // 2, ty, 11)
    text_x = start_x + icon_box + icon_gap
    bbox = focus_font.getbbox(focus)
    text_h = bbox[3] - bbox[1]
    d.draw.text((text_x, ty - text_h // 2 - 1), focus, font=focus_font, fill=NAVY, stroke_width=1, stroke_fill=NAVY)
    draw_target_arrow(text_x + text_w + icon_gap + icon_box // 2, ty, 11)
    d.y += 62

    # 01 业绩追踪：整体 / 基量 两行五列（严格按模板排版）
    perf = data.get("performance") or {}
    overall = perf.get("overall") or {}
    base = perf.get("base") or {}
    # 五列：预算额、销额、达成率、订单进度、增长率；无数据则留空
    metrics_def = [
        ("budget", "预算额", "coin"),
        ("sales", "销额", "bars"),
        ("achieve_rate", "达成率", "donut"),
        ("order_progress", "订单进度", "progress"),
        ("growth_rate", "增长率", "arrow"),
    ]

    def fmt_empty(v):
        if v is None or v == "" or v == "—" or v == "-":
            return ""
        return str(v)

    def draw_metric_icon(kind: str, box, accent):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if kind == "coin":
            for dy in (-6, -1, 4):
                d.draw.ellipse((cx - 8, cy + dy - 3, cx + 8, cy + dy + 3), outline=accent, width=2)
        elif kind == "bars":
            for i, h in enumerate((4, 7, 10, 13)):
                bx = cx - 11 + i * 6
                d.draw.rectangle((bx, cy + 8 - h, bx + 4, cy + 8), fill=accent)
        elif kind == "donut":
            d.draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), outline=accent, width=3)
            d.draw.pieslice((cx - 9, cy - 9, cx + 9, cy + 9), start=270, end=110, fill=accent)
            d.draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=WHITE)
        elif kind == "progress":
            d.round_rect((cx - 14, cy - 4, cx + 14, cy + 4), (220, 230, 238), radius=4)
            d.round_rect((cx - 14, cy - 4, cx + 2, cy + 4), accent, radius=4)
        else:
            d.draw.polygon(
                [
                    (cx, cy - 9),
                    (cx + 7, cy + 1),
                    (cx + 2, cy + 1),
                    (cx + 2, cy + 9),
                    (cx - 2, cy + 9),
                    (cx - 2, cy + 1),
                    (cx - 7, cy + 1),
                ],
                fill=accent,
            )

    title_h = 40
    row_h = 100
    side_w = 34
    pad = 10
    block_h = title_h + row_h * 2 + pad
    block_top = d.y
    d.round_rect((x0, block_top, x0 + content_w, block_top + block_h), WHITE, outline=LINE, radius=12)

    # 标题：01 方块 + 业绩追踪 + 底部分隔线
    d.round_rect((x0 + 14, block_top + 10, x0 + 42, block_top + 38), NAVY, radius=8)
    d.draw.text((x0 + 19, block_top + 16), "01", font=d.font_tiny, fill=WHITE)
    d.draw.text((x0 + 52, block_top + 14), "业绩追踪", font=d.font_h2, fill=NAVY)
    d.draw.line((x0 + 14, block_top + title_h - 2, x0 + content_w - 14, block_top + title_h - 2), fill=NAVY, width=1)

    def draw_perf_row(row_label: str, side_color, values: dict, y: int):
        d.round_rect((x0 + pad, y + 4, x0 + pad + side_w, y + row_h - 4), side_color, radius=8)
        chars = list(row_label)
        ch_h = 18
        start_y = y + (row_h - len(chars) * ch_h) // 2
        for i, ch in enumerate(chars):
            tw = int(d.draw.textlength(ch, font=d.font_side))
            d.draw.text((x0 + pad + (side_w - tw) // 2, start_y + i * ch_h), ch, font=d.font_side, fill=WHITE)

        grid_x = x0 + pad + side_w + 6
        grid_w = content_w - (grid_x - x0) - pad
        n = len(metrics_def)
        cell_w = grid_w // n
        row_accent = TEAL if row_label == "基量" else NAVY

        d.draw.rectangle((grid_x, y + 4, grid_x + cell_w * n, y + row_h - 4), outline=LINE, width=1)

        for i, (key, suffix, icon) in enumerate(metrics_def):
            cx1 = grid_x + i * cell_w
            cx2 = cx1 + cell_w
            if i > 0:
                d.draw.line((cx1, y + 4, cx1, y + row_h - 4), fill=LINE, width=1)

            if key in ("order_progress", "growth_rate"):
                label = suffix  # 订单进度 / 增长率（截图不加整体/基量前缀）
            else:
                label = f"{row_label}{suffix}"

            val = fmt_empty(values.get(key))
            if key == "growth_rate":
                num_color = growth_color(val) if val else row_accent
                if val.startswith("+"):
                    icon_color = GREEN
                elif val.startswith("-"):
                    icon_color = RED
                else:
                    icon_color = row_accent
            else:
                num_color = row_accent
                icon_color = TEAL if row_label == "基量" else BLUE

            mid = (cx1 + cx2) // 2
            lw = int(d.draw.textlength(label, font=d.font_tiny))
            d.draw.text((mid - lw // 2, y + 14), label, font=d.font_tiny, fill=MUTED)
            if val:
                vw = int(d.draw.textlength(val, font=d.font_kpi_lg))
                d.draw.text((mid - vw // 2, y + 38), val, font=d.font_kpi_lg, fill=num_color)
            draw_metric_icon(icon, (mid - 16, y + row_h - 36, mid + 16, y + row_h - 12), icon_color)

    draw_perf_row("整体", NAVY, overall, block_top + title_h)
    draw_perf_row("基量", TEAL, base, block_top + title_h + row_h)
    d.y = block_top + block_h + 14

    def section_start(num: str, title: str, height_guess: int = 40):
        top = d.y
        d.round_rect((x0, top, x0 + content_w, top + height_guess), WHITE, outline=LINE, radius=14)
        d.round_rect((x0 + 14, top + 14, x0 + 42, top + 42), NAVY, radius=8)
        d.draw.text((x0 + 19, top + 20), num, font=d.font_tiny, fill=WHITE)
        d.draw.text((x0 + 52, top + 18), title, font=d.font_h2, fill=NAVY)
        return top

    # Section 02：分区/销售组业绩进度表
    s1 = data.get("section_01") or {}
    rows = s1.get("rows") or []
    # 兼容旧版 items
    if not rows and s1.get("items"):
        rows = [
            {
                "name": it.get("name"),
                "achieve_rate": it.get("rate"),
                "growth_rate": None,
                "base_achieve_rate": None,
                "order_amount_5d": "—",
            }
            for it in s1["items"]
        ]
    warn_below = float(s1.get("warn_below") or 90)
    title_02 = s1.get("title") or "分区 / 销售组业绩进度"

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
        return "—" if p is None else f"{p:.1f}%"

    def fmt_growth(v):
        p = to_pct(v)
        if p is None:
            return "—"
        if p > 0:
            return f"+{p:.1f}%"
        return f"{p:.1f}%"

    header_h = 36
    row_h_tbl = 42
    title_h = 40
    table_h = title_h + header_h + max(1, len(rows)) * row_h_tbl + 16
    top = d.y
    d.round_rect((x0, top, x0 + content_w, top + table_h), WHITE, outline=LINE, radius=12)
    # 标题：小图标 + 标题（不写序号 02）
    d.round_rect((x0 + 14, top + 12, x0 + 26, top + 24), NAVY, radius=3)
    d.draw.text((x0 + 34, top + 10), title_02, font=d.font_h2, fill=NAVY)

    # 列宽
    cols = [
        ("name", "经销组", 0.22),
        ("achieve_rate", "达成率", 0.20),
        ("growth_rate", "增长率", 0.14),
        ("base_achieve_rate", "大单品达成率", 0.22),
        ("order_amount_5d", "近5日下单额", 0.22),
    ]
    usable = content_w - 28
    col_ws = [int(usable * c[2]) for c in cols]
    col_ws[-1] = usable - sum(col_ws[:-1])
    table_x = x0 + 14
    head_y = top + title_h
    grid_bot = head_y + header_h + max(1, len(rows)) * row_h_tbl

    # 表体先铺浅蓝底，白线才看得见
    TABLE_BODY = (198, 214, 232)
    TABLE_ZEBRA = (184, 204, 226)
    d.draw.rectangle((table_x, head_y, table_x + usable, grid_bot), fill=TABLE_BODY)
    d.draw.rectangle((table_x, head_y, table_x + usable, head_y + header_h), fill=NAVY)

    cx = table_x
    for (key, label, _), cw in zip(cols, col_ws):
        tw = int(d.draw.textlength(label, font=d.font_small))
        d.draw.text((cx + (cw - tw) // 2, head_y + 10), label, font=d.font_small, fill=WHITE)
        cx += cw

    def draw_rate_cell(cx, ry, cw, rh, value, bar_color, text_color):
        txt = fmt_pct(value)
        pct = to_pct(value)
        tw = int(d.draw.textlength(txt, font=d.font_small))
        d.draw.text((cx + (cw - tw) // 2, ry + 6), txt, font=d.font_small, fill=text_color)
        bar_x1 = cx + 10
        bar_x2 = cx + cw - 10
        bar_y1 = ry + rh - 13
        bar_y2 = ry + rh - 7
        d.round_rect((bar_x1, bar_y1, bar_x2, bar_y2), (230, 236, 244), radius=3)
        if pct is not None:
            fill_w = int((bar_x2 - bar_x1) * max(0.0, min(pct / 100.0, 1.0)))
            if fill_w > 0:
                d.round_rect((bar_x1, bar_y1, bar_x1 + fill_w, bar_y2), bar_color, radius=3)

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
        d.draw.text((cx + 10, ry + 12), str(row.get("name") or "—"), font=d.font_small, fill=text_color)
        cx += col_ws[0]
        draw_rate_cell(cx, ry, col_ws[1], row_h_tbl, row.get("achieve_rate"), bar_overall, text_color)
        cx += col_ws[1]
        gtxt = fmt_growth(row.get("growth_rate"))
        gcolor = RED if warn else growth_color(gtxt)
        tw = int(d.draw.textlength(gtxt, font=d.font_small))
        d.draw.text((cx + (col_ws[2] - tw) // 2, ry + 12), gtxt, font=d.font_small, fill=gcolor)
        cx += col_ws[2]
        draw_rate_cell(cx, ry, col_ws[3], row_h_tbl, row.get("base_achieve_rate"), bar_base, text_color)
        cx += col_ws[3]
        amt = str(row.get("order_amount_5d") or "—")
        tw = int(d.draw.textlength(amt, font=d.font_small))
        d.draw.text((cx + (col_ws[4] - tw) // 2, ry + 12), amt, font=d.font_small, fill=text_color)

    # 细白线网格（铺在浅蓝底上可见）
    d.draw.line((table_x, head_y + header_h, table_x + usable, head_y + header_h), fill=WHITE, width=2)
    for idx in range(len(rows)):
        ry = head_y + header_h + (idx + 1) * row_h_tbl
        d.draw.line((table_x, ry, table_x + usable, ry), fill=WHITE, width=2)
    vx = table_x
    for cw in col_ws[:-1]:
        vx += cw
        d.draw.line((vx, head_y, vx, grid_bot), fill=WHITE, width=2)
    # 外边框白线
    d.draw.rectangle((table_x, head_y, table_x + usable, grid_bot), outline=WHITE, width=2)

    d.y = top + table_h + 14

    # Section 03 two columns
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

    # 底部：左数据源 / 右制作部门（统一固定文案，无【】）
    left_footer = "数据源：CRM | SFA | 终端巡检系统 | 市场活动平台"
    right_footer = "制作部门：数据组"
    d.draw.text((x0, d.y), left_footer, font=d.font_tiny, fill=MUTED)
    rw = int(d.draw.textlength(right_footer, font=d.font_tiny))
    d.draw.text((x0 + content_w - rw, d.y), right_footer, font=d.font_tiny, fill=MUTED)
    d.y += 22
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
