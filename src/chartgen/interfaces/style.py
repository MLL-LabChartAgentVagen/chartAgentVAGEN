"""The style vector: everything about how a figure looks, and nothing about what it says.

Each dimension is sampled independently from a seed and stored with the record, so
an ablation can group results by any single dimension. Style cannot change an
answer, with one deliberate exception: whether an axis starts at zero changes how
values map to pixels, and therefore which values can still be measured off the
image. That changes how many values are asked for, never what they are.
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
    """One image degradation. Only degradations whose geometry has a closed form
    are allowed, so recorded boxes can be mapped through the same transform."""

    kind: DegradationKind = "none"
    amount: float = 0.0     # jpeg quality, noise sigma, blur radius, scale, angle, strength


@dataclass(frozen=True)
class StyleVector:
    """Seven groups of visual dimensions. The field prefixes are the ablation groups."""

    # 1 value labels
    value_labels: ValueLabels = "none"

    # 2 layout detail
    legend_placement: LegendPlacement = "outside"
    panel_gap: float = 0.08
    repeat_shared_ticks: bool = False

    # 3 panel types
    panel_types: PanelTypes = "same"

    # 4 number format
    number_format: NumberFormat = "plain"
    decimals: int = 1

    # 5 palette
    palette: Palette = "corporate_low"

    # 6 shape detail
    edge_width: float = 0.8
    shadow: bool = False
    pseudo_3d: bool = False
    gridlines: bool = True
    font_family: str = "auto"          # "auto" resolves to a font available on this machine
    font_size: float = 11.0
    bar_width: float = 0.432           # three bars across a 764 pixel plot area are 110 wide
    hatch: str | None = None
    donut: bool = False

    # 7 axes
    zero_baseline: bool = True
    tick_density: Literal["sparse", "normal", "dense"] = "normal"
    label_rotation: float = 0.0
    log_scale: bool = False

    # canvas: frozen, because auto-layout must never move a recorded box
    image_size: tuple[int, int] = (900, 600)
    dpi: int = 100

    degradation: Degradation = Degradation()
