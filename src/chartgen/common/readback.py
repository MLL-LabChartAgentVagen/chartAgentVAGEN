"""从像素反算：框内颜色占比，以及「框 + 轴 → 值」。

**一份实现，三处使用**——04 的自检拿渲染器的记录当输入，05 的可验证奖励拿模型
输出当输入，评测期算无标注一致性指标。三处的差别只在谁写的那条 `(键, 值, 区域)`。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from .geometry import Box, Range, pixel_to_value

Anchor = Literal["top", "bottom", "left", "right", "center_x", "center_y"]
Axis = tuple[Range, Range]                 # (value_range, pixel_range)
RGB = tuple[int, int, int]

#: 与目标颜色的每通道最大差，超过就不算这个颜色。
COLOR_TOLERANCE = 30

#: 与背景色的每通道差超过这个值才算「有墨」。
INK_TOLERANCE = 12

#: 框内有多少比例的像素不是背景，才算「框里有东西」。
MIN_CONTENT_FRACTION = 0.15

#: 声称的值为零时改用绝对下限判定。
ABSOLUTE_FLOOR = 1e-6


def load_image(path: str | Path) -> np.ndarray:
    """读成 RGB uint8。形状 (H, W, 3)，索引是 [y, x]。"""
    from PIL import Image

    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def _crop(img: np.ndarray, box: Box) -> np.ndarray:
    h, w = img.shape[:2]
    x0, y0 = int(np.floor(max(box.x0, 0))), int(np.floor(max(box.y0, 0)))
    x1, y1 = int(np.ceil(min(box.x1, w))), int(np.ceil(min(box.y1, h)))
    if x1 <= x0 or y1 <= y0:
        return img[:0, :0]
    return img[y0:y1, x0:x1]


def color_fraction(img: np.ndarray, box: Box, rgb: RGB,
                   tolerance: int = COLOR_TOLERANCE) -> float:
    """框内有多少比例的像素接近这个颜色。"""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    close = np.all(np.abs(patch.astype(np.int16) - np.array(rgb, np.int16)) <= tolerance, axis=-1)
    return float(close.mean())


def ink_fraction(img: np.ndarray, box: Box, background: RGB = (255, 255, 255),
                 tolerance: int = INK_TOLERANCE) -> float:
    """框内有多少比例的像素不是背景色。不需要知道图元是什么颜色。"""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    diff = np.abs(patch.astype(np.int16) - np.array(background, np.int16))
    return float(np.any(diff > tolerance, axis=-1).mean())


def box_has_content(img: np.ndarray, box: Box, rgb: RGB | None = None,
                    min_fraction: float = MIN_CONTENT_FRACTION) -> bool:
    """自检①：框里有没有东西。给了颜色就查那个颜色的占比，否则查有没有墨。"""
    frac = color_fraction(img, box, rgb) if rgb is not None else ink_fraction(img, box)
    return frac >= min_fraction


def _anchor_pixel(box: Box, anchor: Anchor) -> float:
    return {
        "top": box.y0,
        "bottom": box.y1,
        "left": box.x0,
        "right": box.x1,
        "center_x": (box.x0 + box.x1) / 2,
        "center_y": (box.y0 + box.y1) / 2,
    }[anchor]


def value_from_box(box: Box, axis: Axis, anchor: Anchor,
                   scale: Literal["linear", "log"] = "linear") -> float:
    """自检②：用框的像素位置与该面板的值域、像素域反算出值。

    `anchor` 说的是这个图元的哪条边编码了值：竖条取 `top`、横条取 `right`、
    点取 `center_y`。它由图元形状决定，不由图表类型决定。
    """
    value_range, pixel_range = axis
    return pixel_to_value(_anchor_pixel(box, anchor), value_range, pixel_range, scale)


def value_agrees(measured: float, claimed: float, tolerance: float) -> bool:
    """相对容差；声称的值为零时退到绝对下限。"""
    limit = abs(claimed) * tolerance if claimed else ABSOLUTE_FLOOR
    return abs(measured - claimed) <= max(limit, ABSOLUTE_FLOOR)


@dataclass(frozen=True)
class Verification:
    """两项几何判定的结果。不需要 ground truth 就能算。"""

    has_content: bool
    value_agrees: bool | None            # 没给轴时为 None，这一项没跑
    measured_value: float | None = None
    content_fraction: float = 0.0

    @property
    def ok(self) -> bool:
        return self.has_content and self.value_agrees is not False


def verify(img: np.ndarray, *, box: Box, claimed_value: float, axis: Axis | None,
           anchor: Anchor = "top", rgb: RGB | None = None, tolerance: float = 0.01,
           scale: Literal["linear", "log"] = "linear") -> Verification:
    """一条 `(键, 值, 区域)` 的两项几何判定。"""
    frac = color_fraction(img, box, rgb) if rgb is not None else ink_fraction(img, box)
    has_content = frac >= MIN_CONTENT_FRACTION
    if axis is None:
        return Verification(has_content, None, None, frac)
    measured = value_from_box(box, axis, anchor, scale)
    return Verification(has_content, value_agrees(measured, claimed_value, tolerance),
                        measured, frac)
