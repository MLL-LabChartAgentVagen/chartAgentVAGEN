"""坐标约定与框运算。全流水线只有这一套约定。

像素坐标，原点在图像左上角，框写成 `[x0, y0, x1, y1]`，随图像宽高一并记录。

变换统一写成 3×3 齐次矩阵：退化（缩放 / 仿射 / 单应）与页面合成（平移加缩放）
共用同一个机制，框的映射就是四个顶点变换后取外接框。
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
    """像素框，原点左上。构造时归一化到 x0 ≤ x1、y0 ≤ y1。"""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        vals = (self.x0, self.y0, self.x1, self.y1)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError(f"框的坐标必须有限: {vals}")
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


# ---------------------------------------------------------------- 变换

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
    """四组对应点解出单应矩阵。用于透视形变退化。"""
    if len(src) != 4 or len(dst) != 4:
        raise ValueError("单应需要四组对应点")
    a, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.extend([u, v])
    h = np.linalg.solve(np.array(a, float), np.array(b, float))
    return np.append(h, 1.0).reshape(3, 3)


def compose(*matrices: Matrix) -> Matrix:
    """从右往左依次施加：`compose(T, S)` 表示先缩放再平移。"""
    out = np.eye(3)
    for m in matrices:
        out = out @ m
    return out


def invert(m: Matrix) -> Matrix:
    return np.linalg.inv(m)


def apply_point(m: Matrix, x: float, y: float) -> Point:
    v = m @ np.array([x, y, 1.0])
    if v[2] == 0:
        raise ValueError("变换把点映到了无穷远")
    return (float(v[0] / v[2]), float(v[1] / v[2]))


def apply(m: Matrix, box: Box) -> Box:
    """框的变换：四个顶点各自变换后取外接框。

    旋转与透视之后外接框会比原图元略大，这是已知且可控的偏差。
    """
    pts = [apply_point(m, x, y) for x, y in box.corners()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return Box(min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- 轴映射

def _to_axis_space(v: float, scale_kind: Scale) -> float:
    if scale_kind == "log":
        if v <= 0:
            raise ValueError(f"对数轴上的值必须为正: {v}")
        return math.log10(v)
    return v


def value_to_pixel(value: float, value_range: Range, pixel_range: Range,
                   scale: Scale = "linear") -> float:
    """值 → 像素。`pixel_range` 按 `value_range` 的顺序给出，y 轴通常是反的。"""
    v0, v1 = (_to_axis_space(v, scale) for v in value_range)
    if v0 == v1:
        raise ValueError(f"值域跨度为零: {value_range}")
    p0, p1 = pixel_range
    return p0 + (_to_axis_space(value, scale) - v0) / (v1 - v0) * (p1 - p0)


def pixel_to_value(pixel: float, value_range: Range, pixel_range: Range,
                   scale: Scale = "linear") -> float:
    """像素 → 值。04 的自检与 05 的可验证奖励反算值时都走这里。"""
    v0, v1 = (_to_axis_space(v, scale) for v in value_range)
    p0, p1 = pixel_range
    if p0 == p1:
        raise ValueError(f"像素域跨度为零: {pixel_range}")
    t = v0 + (pixel - p0) / (p1 - p0) * (v1 - v0)
    return 10.0**t if scale == "log" else t


def value_per_pixel(value_range: Range, pixel_range: Range) -> float:
    """每像素代表多少值。chart_types.md §4 第三条判据的分母。"""
    span_v = abs(value_range[1] - value_range[0])
    span_p = abs(pixel_range[1] - pixel_range[0])
    if span_p == 0:
        raise ValueError(f"像素域跨度为零: {pixel_range}")
    return span_v / span_p


# ---------------------------------------------------------------- 冻结版面

def axes_rect(image_size: tuple[int, int], *, left: float, top: float,
              right: float, bottom: float) -> Box:
    """由图像尺寸与四边留白算出绘图区。写死，不用自动布局。"""
    w, h = image_size
    rect = (left, top, w - right, h - bottom)
    if rect[2] <= rect[0] or rect[3] <= rect[1]:
        raise ValueError(f"留白过大，绘图区为空: {image_size} {rect}")
    return Box(*rect)


def rect_to_mpl_fraction(rect: Box, image_size: tuple[int, int]) -> tuple[float, float, float, float]:
    """左上原点像素 → matplotlib 的 (left, bottom, width, height) 0–1 figure 坐标。"""
    w, h = image_size
    return (rect.x0 / w, (h - rect.y1) / h, rect.width / w, rect.height / h)


def mpl_fraction_to_rect(frac: tuple[float, float, float, float],
                         image_size: tuple[int, int]) -> Box:
    w, h = image_size
    left, bottom, fw, fh = frac
    return Box(left * w, h - (bottom + fh) * h, (left + fw) * w, h - bottom * h)
