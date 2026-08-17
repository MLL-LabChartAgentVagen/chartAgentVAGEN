"""画法 → 「值能否读出」的三条规则。

判据在 [chart_types.md §4](../../../storyline/parsebench_chart/chart_types.md) 定义一次，
04 的 `readable` 与 05 的容差都只调这里：

    图上写出了数值            → readable，容差 0
    没写，画法是角度 / 颜色    → 不 readable
    没写，画法是长度 / 位置    → 1% 的值折算成像素 ≥ 2 时 readable，容差 1%
"""

from __future__ import annotations

from ..common.geometry import Range, value_per_pixel

#: 量像素能反算出值的画法。
MEASURABLE = frozenset({"length", "position"})

#: 量不出 1% 相对精度的画法：角度分辨率不够，色标量化且感知非线性。
UNMEASURABLE = frozenset({"angle", "color"})

#: 1% 的值至少要折算成这么多像素才算读得出。
MIN_PIXELS_PER_PERCENT = 2.0

#: 没写标注时的相对容差。
RELATIVE_TOLERANCE = 0.01

Axis = tuple[Range, Range]     # (value_range, pixel_range)


def pixels_per_percent(value: float, axis: Axis) -> float:
    """该值的 1% 折算成多少像素。第三条规则的左边。"""
    value_range, pixel_range = axis
    return abs(value) * RELATIVE_TOLERANCE / value_per_pixel(value_range, pixel_range)


def readable(channel: str, *, labeled: bool, value: float, axis: Axis | None) -> bool:
    if labeled:
        return True
    if channel in UNMEASURABLE:
        return False
    if channel not in MEASURABLE:
        raise ValueError(f"没有这种画法: {channel}")
    if axis is None:
        return False
    return pixels_per_percent(value, axis) >= MIN_PIXELS_PER_PERCENT


def tolerance(labeled: bool) -> float:
    """写了标注要求精确匹配，没写则 1% 相对容差。"""
    return 0.0 if labeled else RELATIVE_TOLERANCE
