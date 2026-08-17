"""Sampling a style, and the palettes, fonts, axis ranges and number formats it picks.

Each dimension is sampled independently from a seed; there is no joint
distribution to tune. Style never changes an answer, with one deliberate
exception: whether an axis starts at zero changes how values map to pixels, and
therefore which values can still be measured off the image.
"""

from __future__ import annotations

import math

from ..common.rng import derive
from ..interfaces.style import Degradation, StyleVector

RGB = tuple[int, int, int]

#: Fonts to try in order, falling back to the plotting library's own default.
CJK_PREFERENCE = (
    "Noto Sans CJK SC", "Noto Sans CJK JP", "Source Han Sans SC",
    "WenQuanYi Zen Hei", "Droid Sans Fallback", "DejaVu Sans",
)

#: Four palettes, each a sequence of colours taken in order.
PALETTES: dict[str, tuple[RGB, ...]] = {
    # Low contrast, as corporate reports tend to be: one hue, neighbours close together
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

#: Tick density to the number of intervals aimed for.
TICK_INTERVALS: dict[str, int] = {"sparse": 4, "normal": 6, "dense": 10}

#: The tallest mark fills at most this much of the axis; the rest is headroom.
MAX_AXIS_FILL = 0.75

#: Mantissas a tick step is allowed to take.
NICE_STEPS = (1.0, 2.0, 2.5, 5.0, 10.0)


def resolve_font(name: str) -> str:
    """Resolve "auto" to the first font available on this machine."""
    from matplotlib import font_manager as fm

    available = {f.name for f in fm.fontManager.ttflist}
    if name != "auto" and name in available:
        return name
    for candidate in CJK_PREFERENCE:
        if candidate in available:
            return candidate
    return "DejaVu Sans"


def colors(style: StyleVector, n: int) -> tuple[RGB, ...]:
    """Take n colours, cycling if the palette is shorter."""
    palette = PALETTES[style.palette]
    return tuple(palette[i % len(palette)] for i in range(n))


def hex_of(rgb: RGB) -> str:
    return "#%02x%02x%02x" % rgb


def nice_step(raw: float) -> float:
    """Round a rough step up to the nearest presentable one."""
    if raw <= 0:
        return 1.0
    magnitude = 10.0 ** math.floor(math.log10(raw))
    for s in NICE_STEPS:
        if raw <= s * magnitude * (1 + 1e-12):
            return s * magnitude
    return 10.0 * magnitude


def nice_range(vmin: float, vmax: float, style: StyleVector) -> tuple[float, float, float]:
    """Lower bound, upper bound and tick step for an axis.

    The upper bound comes from letting the tallest mark fill at most `MAX_AXIS_FILL`
    of the axis, then rounding up to a whole number of steps. Whether the axis
    starts at zero is a style dimension.

    This is the one way style affects how many values a figure is asked for: the
    value range changes which marks can still be measured, but never what any of
    them is worth.
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


#: Currency units and the symbol each one is written with.
CURRENCY_SYMBOLS: dict[str, str] = {
    "usd": "$", "eur": "€", "gbp": "£", "jpy": "¥", "cny": "¥",
    "rmb": "¥", "krw": "₩", "inr": "₹",
}

#: Units whose values are already shares, so a percent sign describes them.
PERCENT_UNITS = frozenset({"%", "percent", "pct", "percentage", "share", "ratio", "rate"})


def format_number(value: float, style: StyleVector, unit: str | None = None) -> str:
    """Write a number for display. The format is style; the number itself is not.

    A format that would make the label disagree with the number it labels is not
    applied. A percent sign on a duration and a currency symbol on a satisfaction
    score are both wrong, and a label is read as ground truth with no tolerance,
    so the unit decides whether those two formats apply at all. Scaling never
    happens: a label always shows the value that was recorded for that mark.
    """
    d = style.decimals
    fmt = style.number_format
    key = (unit or "").strip().lower()

    if fmt == "percent":
        return f"{value:.{d}f}%" if key in PERCENT_UNITS else f"{value:.{d}f}"
    if fmt == "currency":
        return f"{CURRENCY_SYMBOLS[key]}{value:,.{d}f}" if key in CURRENCY_SYMBOLS \
            else f"{value:,.{d}f}"
    if fmt == "si":
        for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(value) >= limit:
                return f"{value / limit:.{d}f}{suffix}"
        return f"{value:.{d}f}"
    text = f"{value:,.{d}f}" if fmt == "thousands" else f"{value:.{d}f}"
    if fmt == "paren_neg" and value < 0:
        text = f"({text.lstrip('-')})"
    return text


def sample(root_seed: int, scenario_id: str, figure_id: str, variant: int = 0) -> StyleVector:
    """Sample every dimension independently. `variant` gives one figure a second look,
    which is both a paired training sample and the input to the style self-check."""
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
