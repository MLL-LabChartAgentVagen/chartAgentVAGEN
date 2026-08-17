"""Measuring things back out of the rendered pixels.

Two questions, both answerable from an image and a claimed `(key, value, box)`
without any ground truth: is there anything inside the box, and does the box
geometry agree with the claimed value.

That is why there is one implementation and three callers. During generation the
claim comes from the renderer and a failure discards the figure. During training
the claim comes from the model and the same code is the reward. During evaluation
it yields a consistency metric on datasets that carry no box annotations at all.
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

#: Per-channel distance from the target colour that still counts as that colour.
COLOR_TOLERANCE = 30

#: Per-channel distance from the background before a pixel counts as ink.
INK_TOLERANCE = 12

#: Fraction of a box that must be ink before the box counts as non-empty.
MIN_CONTENT_FRACTION = 0.15

#: Absolute floor used instead of a relative tolerance when the claim is zero.
ABSOLUTE_FLOOR = 1e-6


def load_image(path: str | Path) -> np.ndarray:
    """Load as RGB uint8, shaped (H, W, 3) and indexed [y, x]."""
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
    """Fraction of the box close to this colour."""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    close = np.all(np.abs(patch.astype(np.int16) - np.array(rgb, np.int16)) <= tolerance, axis=-1)
    return float(close.mean())


def ink_fraction(img: np.ndarray, box: Box, background: RGB = (255, 255, 255),
                 tolerance: int = INK_TOLERANCE) -> float:
    """Fraction of the box that is not background. Needs no knowledge of the mark colour."""
    patch = _crop(img, box)
    if patch.size == 0:
        return 0.0
    diff = np.abs(patch.astype(np.int16) - np.array(background, np.int16))
    return float(np.any(diff > tolerance, axis=-1).mean())


def box_has_content(img: np.ndarray, box: Box, rgb: RGB | None = None,
                    min_fraction: float = MIN_CONTENT_FRACTION) -> bool:
    """Is there anything inside the box. With a colour, look for that colour; without
    one, look for anything that is not background."""
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
    """Convert a box back into a value using the panel's value and pixel ranges.

    `anchor` names the edge of the mark that carries the value: the top of a
    vertical bar, the right of a horizontal one, the centre of a point. It follows
    from the mark shape, not from the chart type.
    """
    value_range, pixel_range = axis
    return pixel_to_value(_anchor_pixel(box, anchor), value_range, pixel_range, scale)


def value_agrees(measured: float, claimed: float, tolerance: float) -> bool:
    """Relative tolerance, falling back to an absolute floor when the claim is zero."""
    limit = abs(claimed) * tolerance if claimed else ABSOLUTE_FLOOR
    return abs(measured - claimed) <= max(limit, ABSOLUTE_FLOOR)


@dataclass(frozen=True)
class Verification:
    """The outcome of both geometric checks. Computable without ground truth."""

    has_content: bool
    value_agrees: bool | None            # None when no axis was given, so it did not run
    measured_value: float | None = None
    content_fraction: float = 0.0

    @property
    def ok(self) -> bool:
        return self.has_content and self.value_agrees is not False


def verify(img: np.ndarray, *, box: Box, claimed_value: float, axis: Axis | None,
           anchor: Anchor = "top", rgb: RGB | None = None, tolerance: float = 0.01,
           scale: Literal["linear", "log"] = "linear") -> Verification:
    """Run both geometric checks on one claimed `(key, value, box)`."""
    frac = color_fraction(img, box, rgb) if rgb is not None else ink_fraction(img, box)
    has_content = frac >= MIN_CONTENT_FRACTION
    if axis is None:
        return Verification(has_content, None, None, frac)
    measured = value_from_box(box, axis, anchor, scale)
    return Verification(has_content, value_agrees(measured, claimed_value, tolerance),
                        measured, frac)
