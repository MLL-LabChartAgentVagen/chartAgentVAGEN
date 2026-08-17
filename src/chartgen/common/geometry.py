"""The coordinate convention, and the arithmetic on boxes and axes.

There is exactly one convention: pixels, origin at the top left of the image,
a box written `[x0, y0, x1, y1]`, always stored next to the image size.

Every transform is a 3x3 homogeneous matrix, so image degradation (scale, affine,
perspective) and page composition (translate and scale) share one mechanism, and
mapping a box is always the same operation: transform four corners, take the
bounding box.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np

Scale = Literal["linear", "log"]
Matrix = np.ndarray                      # (3, 3)
Point = tuple[float, float]
Range = tuple[float, float]


@dataclass(frozen=True)
class Box:
    """A pixel box, origin top left. Normalised on construction so x0 <= x1, y0 <= y1."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        vals = (self.x0, self.y0, self.x1, self.y1)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError(f"box coordinates must be finite: {vals}")
        object.__setattr__(self, "x0", float(min(self.x0, self.x1)))
        object.__setattr__(self, "x1", float(max(vals[0], vals[2])))
        object.__setattr__(self, "y0", float(min(self.y0, self.y1)))
        object.__setattr__(self, "y1", float(max(vals[1], vals[3])))

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        return self.width * self.height

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)

    def corners(self) -> tuple[Point, Point, Point, Point]:
        return ((self.x0, self.y0), (self.x1, self.y0), (self.x1, self.y1), (self.x0, self.y1))

    def contains(self, x: float, y: float) -> bool:
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1

    def clip_to(self, other: "Box") -> "Box":
        return Box(max(self.x0, other.x0), max(self.y0, other.y0),
                   min(self.x1, other.x1), min(self.y1, other.y1))


def iou(a: Box, b: Box) -> float:
    ix = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    iy = max(0.0, min(a.y1, b.y1) - max(a.y0, b.y0))
    inter = ix * iy
    union = a.area + b.area - inter
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------- transforms

def identity() -> Matrix:
    return np.eye(3)


def translate(dx: float, dy: float) -> Matrix:
    m = np.eye(3)
    m[0, 2], m[1, 2] = dx, dy
    return m


def scale(sx: float, sy: float) -> Matrix:
    m = np.eye(3)
    m[0, 0], m[1, 1] = sx, sy
    return m


def rotate(degrees: float, cx: float = 0.0, cy: float = 0.0) -> Matrix:
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    m = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return compose(translate(cx, cy), m, translate(-cx, -cy))


def homography(src: Sequence[Point], dst: Sequence[Point]) -> Matrix:
    """Solve a homography from four point correspondences."""
    if len(src) != 4 or len(dst) != 4:
        raise ValueError("a homography needs four point correspondences")
    a, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.extend([u, v])
    h = np.linalg.solve(np.array(a, float), np.array(b, float))
    return np.append(h, 1.0).reshape(3, 3)


def compose(*matrices: Matrix) -> Matrix:
    """Applied right to left: `compose(T, S)` scales first, then translates."""
    out = np.eye(3)
    for m in matrices:
        out = out @ m
    return out


def invert(m: Matrix) -> Matrix:
    return np.linalg.inv(m)


def apply_point(m: Matrix, x: float, y: float) -> Point:
    v = m @ np.array([x, y, 1.0])
    if v[2] == 0:
        raise ValueError("the transform sent the point to infinity")
    return (float(v[0] / v[2]), float(v[1] / v[2]))


def apply(m: Matrix, box: Box) -> Box:
    """Transform a box: map four corners, take the bounding box.

    After a rotation or a perspective change the bounding box is slightly larger
    than the shape it encloses. That is a known and bounded error, and the record
    notes which transform was applied.
    """
    pts = [apply_point(m, x, y) for x, y in box.corners()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return Box(min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- axis mapping

def _to_axis_space(v: float, scale_kind: Scale) -> float:
    if scale_kind == "log":
        if v <= 0:
            raise ValueError(f"a value on a log axis must be positive: {v}")
        return math.log10(v)
    return v


def value_to_pixel(value: float, value_range: Range, pixel_range: Range,
                   scale: Scale = "linear") -> float:
    """Value to pixel. `pixel_range` follows the order of `value_range`, so a y
    axis usually runs backwards."""
    v0, v1 = (_to_axis_space(v, scale) for v in value_range)
    if v0 == v1:
        raise ValueError(f"the value range has zero span: {value_range}")
    p0, p1 = pixel_range
    return p0 + (_to_axis_space(value, scale) - v0) / (v1 - v0) * (p1 - p0)


def pixel_to_value(pixel: float, value_range: Range, pixel_range: Range,
                   scale: Scale = "linear") -> float:
    """Pixel to value. Both the generation self-check and the reward check use this."""
    v0, v1 = (_to_axis_space(v, scale) for v in value_range)
    p0, p1 = pixel_range
    if p0 == p1:
        raise ValueError(f"the pixel range has zero span: {pixel_range}")
    t = v0 + (pixel - p0) / (p1 - p0) * (v1 - v0)
    return 10.0**t if scale == "log" else t


def value_per_pixel(value_range: Range, pixel_range: Range) -> float:
    """How much value one pixel stands for. The denominator of the readability rule."""
    span_v = abs(value_range[1] - value_range[0])
    span_p = abs(pixel_range[1] - pixel_range[0])
    if span_p == 0:
        raise ValueError(f"the pixel range has zero span: {pixel_range}")
    return span_v / span_p


# ---------------------------------------------------------------- frozen layout

def axes_rect(image_size: tuple[int, int], *, left: float, top: float,
              right: float, bottom: float) -> Box:
    """The plotting area, from image size and four margins.

    Fixed on purpose. Auto-layout moves the plotting area after the drawing is
    done, which silently invalidates every box already recorded.
    """
    w, h = image_size
    rect = (left, top, w - right, h - bottom)
    if rect[2] <= rect[0] or rect[3] <= rect[1]:
        raise ValueError(f"margins leave no plotting area: {image_size} {rect}")
    return Box(*rect)


def rect_to_mpl_fraction(rect: Box, image_size: tuple[int, int]) -> tuple[float, float, float, float]:
    """Top-left pixels to the plotting library's (left, bottom, width, height) fractions."""
    w, h = image_size
    return (rect.x0 / w, (h - rect.y1) / h, rect.width / w, rect.height / h)


def mpl_fraction_to_rect(frac: tuple[float, float, float, float],
                         image_size: tuple[int, int]) -> Box:
    w, h = image_size
    left, bottom, fw, fh = frac
    return Box(left * w, h - (bottom + fh) * h, (left + fw) * w, h - bottom * h)
