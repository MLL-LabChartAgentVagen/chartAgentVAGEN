"""风格向量：采样、配色、字体、轴范围与数字格式。

七组维度各自独立按种子采样，不做联合分布。风格改不动真值——唯一的例外是轴起点，
它改变值与像素的换算，因而影响 04 判定哪些值读得出。
"""

from __future__ import annotations

import math

from ..common.rng import derive
from ..interfaces.style import Degradation, StyleVector

RGB = tuple[int, int, int]

#: 中文字形。按可用性取第一个，取不到就退回 matplotlib 自带的 DejaVu Sans。
CJK_PREFERENCE = (
    "Noto Sans CJK SC", "Noto Sans CJK JP", "Source Han Sans SC",
    "WenQuanYi Zen Hei", "Droid Sans Fallback", "DejaVu Sans",
)

#: 四套配色。每套给一串按顺序取用的颜色。
PALETTES: dict[str, tuple[RGB, ...]] = {
    # 企业报表低对比：同色系蓝，相邻两条差别不大
    "corporate_low": ((31, 78, 121), (46, 105, 156), (68, 132, 184),
                      (99, 158, 205), (139, 185, 222), (180, 210, 236)),
    "monochrome": ((40, 40, 40), (85, 85, 85), (130, 130, 130),
                   (170, 170, 170), (200, 200, 200), (225, 225, 225)),
    "gradient": ((13, 59, 102), (43, 108, 176), (72, 149, 217),
                 (126, 188, 235), (176, 216, 244), (214, 235, 250)),
    "grayscale": ((0, 0, 0), (68, 68, 68), (119, 119, 119),
                  (160, 160, 160), (198, 198, 198), (230, 230, 230)),
}

BACKGROUND: RGB = (255, 255, 255)
GRID_COLOR: RGB = (222, 226, 230)
TEXT_COLOR: RGB = (33, 37, 41)

#: 刻度密度 → 目标刻度间隔数。
TICK_INTERVALS: dict[str, int] = {"sparse": 4, "normal": 6, "dense": 10}

#: 最高的图元最多占轴的这个比例，其余留白。取 0.75 是企业报表的常见观感。
MAX_AXIS_FILL = 0.75

#: 「好看」的刻度步长尾数。
NICE_STEPS = (1.0, 2.0, 2.5, 5.0, 10.0)


def resolve_font(name: str) -> str:
    """`"auto"` 解析成本机第一个可用的中文字体。"""
    from matplotlib import font_manager as fm

    available = {f.name for f in fm.fontManager.ttflist}
    if name != "auto" and name in available:
        return name
    for candidate in CJK_PREFERENCE:
        if candidate in available:
            return candidate
    return "DejaVu Sans"


def colors(style: StyleVector, n: int) -> tuple[RGB, ...]:
    """取 n 个颜色，不够就循环。"""
    palette = PALETTES[style.palette]
    return tuple(palette[i % len(palette)] for i in range(n))


def hex_of(rgb: RGB) -> str:
    return "#%02x%02x%02x" % rgb


def nice_step(raw: float) -> float:
    """把一个粗略步长抬到最近的「好看」步长。"""
    if raw <= 0:
        return 1.0
    magnitude = 10.0 ** math.floor(math.log10(raw))
    for s in NICE_STEPS:
        if raw <= s * magnitude * (1 + 1e-12):
            return s * magnitude
    return 10.0 * magnitude


def nice_range(vmin: float, vmax: float, style: StyleVector) -> tuple[float, float, float]:
    """`(下界, 上界, 步长)`。轴起点是否为零是风格维度。

    上界由「最高的图元最多占轴的 75%」定，再抬到步长的整数倍。急诊科示例的
    42.3 因此落在 `[0, 60]`，刻度每 10 分钟——与 03 §0 记的一样。

    这是风格影响标注集大小的唯一途径：值域一变，04 判定读得出的图元就变，
    但每个图元的值不变。
    """
    intervals = TICK_INTERVALS[style.tick_density]
    if style.zero_baseline:
        vmin, vmax = min(0.0, vmin), max(0.0, vmax)
    span = max(vmax - vmin, abs(vmax) * 1e-6, 1e-9)
    step = nice_step(span / MAX_AXIS_FILL / intervals)

    if style.zero_baseline:
        lo = math.floor(vmin / step) * step
        hi = math.ceil(vmax / MAX_AXIS_FILL / step) * step if vmax > 0 else 0.0
        return (lo, max(hi, lo + step), step)

    pad = (span / MAX_AXIS_FILL - span) / 2
    lo = math.floor((vmin - pad) / step) * step
    hi = math.ceil((vmax + pad) / step) * step
    return (lo, max(hi, lo + step), step)


def format_number(value: float, style: StyleVector, unit: str | None = None) -> str:
    """数字格式是风格维度，不改变值本身。"""
    d = style.decimals
    fmt = style.number_format
    if fmt == "percent":
        return f"{value * 100:.{d}f}%"
    if fmt == "si":
        for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(value) >= limit:
                return f"{value / limit:.{d}f}{suffix}"
        return f"{value:.{d}f}"
    text = f"{value:,.{d}f}" if fmt == "thousands" else f"{value:.{d}f}"
    if fmt == "currency":
        text = f"¥{text}"
    if fmt == "paren_neg" and value < 0:
        text = f"({text.lstrip('-')})"
    if unit and fmt == "plain":
        return text
    return text


def sample(root_seed: int, scenario_id: str, figure_id: str, variant: int = 0) -> StyleVector:
    """每个维度独立按种子采样。`variant` 用来给同一份 FigureSpec 出第二份风格版本。"""
    r = derive(root_seed, scenario_id, "s03_style", figure_id, variant)
    pick = lambda xs: xs[int(r.integers(len(xs)))]
    return StyleVector(
        value_labels=pick(("all", "none", "some")),
        legend_placement=pick(("outside", "per_panel")),
        panel_gap=float(round(r.uniform(0.05, 0.18), 3)),
        repeat_shared_ticks=bool(r.integers(2)),
        panel_types=pick(("same", "mixed")),
        number_format=pick(("plain", "thousands", "currency", "percent", "si", "paren_neg")),
        decimals=int(r.integers(0, 3)),
        palette=pick(tuple(PALETTES)),
        edge_width=float(round(r.uniform(0.0, 2.0), 2)),
        shadow=bool(r.integers(2)),
        pseudo_3d=False,
        gridlines=bool(r.integers(2)),
        font_family="auto",
        font_size=float(pick((9.0, 10.0, 11.0, 12.0, 14.0))),
        bar_width=float(round(r.uniform(0.35, 0.8), 3)),
        hatch=pick((None, None, None, "//", "..", "xx")),
        donut=bool(r.integers(2)),
        zero_baseline=bool(r.integers(2)),
        tick_density=pick(("sparse", "normal", "dense")),
        label_rotation=float(pick((0.0, 0.0, 30.0, 45.0, 90.0))),
        log_scale=False,
        image_size=pick(((900, 600), (1000, 640), (800, 560), (1200, 720))),
        dpi=100,
        degradation=Degradation(pick(("none", "none", "jpeg", "noise", "blur")),
                                float(round(r.uniform(0.3, 0.9), 2))),
    )
