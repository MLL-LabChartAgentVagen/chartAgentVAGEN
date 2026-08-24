"""Sampling a style, and the palettes, fonts, axis ranges and number formats it picks.

Every dimension is drawn independently from `STYLE_DOMAINS`, so the sampler and the
declaration cannot drift apart: a field with no entry in that table is never given
a value, and a value outside a declared domain is never produced.

Style never changes an answer. It changes which answers can still be measured off
the image -- whether an axis starts at zero, whether it is logarithmic, whether the
value is printed next to the mark -- and that changes how many values a figure is
asked for, never what any of them is worth.
"""

from __future__ import annotations

import math
from dataclasses import replace

from ..common.rng import derive
from ..interfaces.style import STYLE_DOMAINS, Degradation, StyleVector

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
SHADOW: RGB = (120, 124, 130)

#: The colour one highlighted category is drawn in, against a palette of neighbours.
ACCENT: RGB = (196, 112, 59)

#: Panel backgrounds. A tint is why the content check reads the background off the
#: panel instead of assuming white.
PANEL_TINTS: dict[str, RGB] = {
    "white": BACKGROUND,
    "tint": (246, 247, 249),
    "grid_band": BACKGROUND,
}

#: The four margins around the plotting area, in pixels, one set per style value.
#:
#: How much white space a report leaves around a chart varies, and the margins are
#: what decide how large the plotting area is at a given image size -- so they are a
#: style dimension rather than a constant. Within one rendering they are frozen:
#: read once before anything is drawn, and never adjusted to fit content, because a
#: margin that grew to make room would move the plotting area and invalidate every
#: box already recorded against it.
#:
#: The left margin carries the value axis and its title, the top margin the figure's
#: text band, the right margin the room a second value axis needs whether or not
#: there is one, and the bottom margin the category axis, its title, the legend band
#: and the foot line.
MARGIN_SETS: dict[str, dict[str, float]] = {
    "normal": {"left": 96.0, "top": 132.0, "right": 80.0, "bottom": 120.0},
    "tight": {"left": 78.0, "top": 104.0, "right": 62.0, "bottom": 98.0},
    "wide": {"left": 118.0, "top": 156.0, "right": 100.0, "bottom": 144.0},
}

#: What each edge keeps for the axis itself -- tick labels and an axis title -- as a
#: share of that edge's whole budget. The rest of the budget is what the blocks cut
#: up. A left or right edge is all gutter by default, which is why a block moved onto
#: one has to bring its own thickness.
GUTTER_SHARES: dict[str, float] = {"left": 1.0, "right": 1.0,
                                   "top": 0.0, "bottom": 44.0 / 120.0}

#: Each block's clear space on the plot side, its thickness, and its clear space on
#: the far side -- as shares of the budget of the edge it was sized against. Summed
#: with the gutter these reproduce the margin set exactly, which is what keeps the
#: default rendering where it was.
BLOCK_SHARES: dict[str, tuple[float, float, float]] = {
    "text": (36.0 / 132.0, 82.0 / 132.0, 14.0 / 132.0),
    "legend": (0.0, 24.0 / 120.0, 8.0 / 120.0),
    "foot": (0.0, 34.0 / 120.0, 10.0 / 120.0),
}

#: Which edge each block was sized against, so a block keeps its thickness when it is
#: moved to another one.
BLOCK_HOME: dict[str, str] = {"text": "top", "legend": "bottom", "foot": "bottom"}


def gutters(margins: dict[str, float]) -> dict[str, float]:
    """The part of each margin the axis keeps, whatever the blocks do."""
    return {edge: margins[edge] * share for edge, share in GUTTER_SHARES.items()}


def block_spans(margins: dict[str, float]) -> dict[str, tuple[float, float, float]]:
    """Each block's lead, thickness and trail in pixels at this margin set."""
    return {name: tuple(s * margins[BLOCK_HOME[name]] for s in shares)
            for name, shares in BLOCK_SHARES.items()}

#: Tick density to the number of intervals aimed for.
TICK_INTERVALS: dict[str, int] = {"sparse": 4, "normal": 6, "dense": 10}

#: The tallest mark fills at most this much of the axis; the rest is headroom.
#:
#: Headroom costs readability directly. Every pixel given to empty axis is a pixel
#: not given to the marks, and whether a value can still be measured is decided by
#: how much value one pixel stands for.
MAX_AXIS_FILL = 0.90

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


def colors(style: StyleVector, n: int, highlight: int | None = None) -> tuple[RGB, ...]:
    """Take n colours, cycling if the palette is shorter.

    With `highlight_single` one of them is replaced by an accent, which is how a
    report singles out one category without saying anything different about it.
    """
    palette = PALETTES[style.palette]
    out = [palette[i % len(palette)] for i in range(n)]
    if style.highlight_single and n:
        out[(0 if highlight is None else highlight) % n] = ACCENT
    return tuple(out)


def hex_of(rgb: RGB) -> str:
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb)


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
    """Lower bound, upper bound and tick step for a value axis.

    The upper bound comes from letting the tallest mark fill at most `MAX_AXIS_FILL`
    of the axis, then rounding up to a whole number of steps. Whether the axis
    starts at zero and whether it is logarithmic are both style dimensions, and both
    are the way style reaches the readability rule: they change how much value one
    pixel stands for, and therefore how many marks can still be measured.
    """
    # Every value has to be positive, not just the largest. A log axis asked for
    # over data that dips below zero used to come back with a positive lower bound,
    # which is a range the negative marks cannot be drawn in: they collapse onto the
    # floor of the axis, and the value read back off them is the floor.
    if style.log_scale and vmin > 0:
        lo = max(min(vmin, vmax), vmax / 1e4)
        lo = 10.0 ** math.floor(math.log10(max(lo, vmax / 1e4)))
        hi = 10.0 ** math.ceil(math.log10(vmax))
        return (lo, max(hi, lo * 10), 0.0)

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


def ticks(lo: float, hi: float, step: float) -> list[float]:
    """Tick positions from a range and a step. A step of zero means a log axis,
    whose ticks the library places itself."""
    if step <= 0:
        return []
    out, v = [], lo
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


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
    score are both wrong, and a label is read as ground truth with no tolerance, so
    the unit decides whether those two formats apply at all. Scaling never happens:
    a label always shows the value that was recorded for that mark.

    With the unit written into the value labels, it is appended here, which is the
    one place that can guarantee it describes the number it sits beside.
    """
    d = style.decimals
    fmt = style.number_format
    key = (unit or "").strip().lower()

    if fmt == "percent":
        text = f"{value:.{d}f}%" if key in PERCENT_UNITS else f"{value:.{d}f}"
    elif fmt == "currency":
        text = (f"{CURRENCY_SYMBOLS[key]}{value:,.{d}f}" if key in CURRENCY_SYMBOLS
                else f"{value:,.{d}f}")
    elif fmt == "si":
        text = f"{value:.{d}f}"
        for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(value) >= limit:
                text = f"{value / limit:.{d}f}{suffix}"
                break
    else:
        text = f"{value:,.{d}f}" if fmt == "thousands" else f"{value:.{d}f}"
        if fmt == "paren_neg" and value < 0:
            text = f"({text.lstrip('-')})"
    if style.unit_placement == "value_labels" and unit and key not in PERCENT_UNITS:
        text = f"{text} {unit}"
    return text


def sample(root_seed: int, scenario_id: str, figure_id: str, variant: int = 0) -> StyleVector:
    """Draw every dimension independently from its declared domain.

    `variant` gives one figure a second look. That is a product in its own right --
    a paired sample -- and it is also the input to the style self-check, so one
    rendering pass serves both.
    """
    r = derive(root_seed, scenario_id, "s03_style", figure_id, variant)
    values = {}
    for name, dim in STYLE_DOMAINS.items():
        i = int(r.choice(len(dim.domain), p=dim.weights) if dim.weights
                else r.integers(len(dim.domain)))
        values[name] = dim.domain[i]
    kind = str(r.choice(("none", "none", "jpeg", "noise", "blur", "downscale"),
                        p=(0.3, 0.2, 0.2, 0.1, 0.1, 0.1)))
    return StyleVector(**values,
                       degradation=Degradation(kind, float(round(r.uniform(0.3, 0.9), 2))))


def default() -> StyleVector:
    """Every dimension at its declared default. What the fixed examples are drawn in."""
    return StyleVector(**{name: dim.default for name, dim in STYLE_DOMAINS.items()})


def pin(style: StyleVector, overrides: dict) -> StyleVector:
    """Fix some dimensions and leave the rest sampled.

    This is how a style ablation is run: pin one dimension to see what it is worth,
    or pin all of them to hold the style vector still. A name that is not a dimension
    is an error rather than a silently ignored setting -- an ablation that quietly did
    not happen is worse than one that failed.
    """
    if not overrides:
        return style
    unknown = sorted(set(overrides) - set(STYLE_DOMAINS))
    if unknown:
        raise ValueError(f"not style dimensions: {unknown}")
    # A value that came out of a configuration file arrives as a list where the
    # domain holds a tuple. They are the same setting written two ways, and refusing
    # one of them would make a dimension unpinnable from the command line.
    pinned = {name: tuple(value) if isinstance(value, list) else value
              for name, value in overrides.items()}
    for name, value in pinned.items():
        allowed = STYLE_DOMAINS[name].domain
        if value not in allowed:
            raise ValueError(f"{name}={value!r} is outside its domain {allowed}")
    return replace(style, **pinned)
