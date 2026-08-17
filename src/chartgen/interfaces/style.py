"""03 内部的风格向量。

七组维度各自独立按种子采样，不做联合分布；随记录一起存，供消融按维度分组。
真值由 FigureSpec 决定，与风格无关——除了轴起点这一项会改变值与像素的换算，
因而影响 04 判定哪些值读得出（影响标注集大小，不影响标注内容）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ValueLabels = Literal["all", "none", "some"]
LegendPlacement = Literal["outside", "per_panel"]
PanelTypes = Literal["same", "mixed"]
NumberFormat = Literal["plain", "thousands", "currency", "percent", "si", "paren_neg"]
Palette = Literal["corporate_low", "monochrome", "gradient", "grayscale"]
DegradationKind = Literal["none", "jpeg", "noise", "blur", "downscale", "rotate", "perspective"]


@dataclass(frozen=True)
class Degradation:
    """一次图像退化。只允许几何变换写得出解析式的那几种。"""

    kind: DegradationKind = "none"
    amount: float = 0.0     # jpeg 质量 / 噪声 sigma / 模糊半径 / 缩放比 / 旋转角 / 形变强度


@dataclass(frozen=True)
class StyleVector:
    """七组风格维度。字段名的前缀就是消融时的分组依据。"""

    # 1 数值标注
    value_labels: ValueLabels = "none"

    # 2 版面细节
    legend_placement: LegendPlacement = "outside"
    panel_gap: float = 0.08
    repeat_shared_ticks: bool = False

    # 3 多面板类型
    panel_types: PanelTypes = "same"

    # 4 数字格式
    number_format: NumberFormat = "plain"
    decimals: int = 1

    # 5 配色
    palette: Palette = "corporate_low"

    # 6 图形细节
    edge_width: float = 0.8
    shadow: bool = False
    pseudo_3d: bool = False
    gridlines: bool = True
    font_family: str = "auto"          # "auto" 由 s03_render.style 解析成本机可用的中文字体
    font_size: float = 11.0
    bar_width: float = 0.432           # 三分类占满 764 像素绘图区时恰好 110 像素宽
    hatch: str | None = None
    donut: bool = False

    # 7 轴
    zero_baseline: bool = True
    tick_density: Literal["sparse", "normal", "dense"] = "normal"
    label_rotation: float = 0.0
    log_scale: bool = False

    # 画布（冻结项：写死后自动布局不得改动）
    image_size: tuple[int, int] = (900, 600)
    dpi: int = 100

    degradation: Degradation = Degradation()
