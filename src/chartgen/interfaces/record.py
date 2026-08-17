"""03 → 04 的 RenderOutput 与 04 → 05 的 Record。

三层各由知道它的组件写出，拼接是按 `(figure_id, panel_id, key)` 的查表连接：

    L0 页面元素   ← 03 的页面合成器
    L1 面板 / 轴 / 图元 / 图例  ← 03 的渲染器，画每个图元时记下框、键、值
    L2 图元的原始行数          ← 02 的投影，04 按键连接进来
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..common.geometry import Box
from .style import Degradation, StyleVector

ElementCategory = Literal["Text", "Table", "Picture", "Page-Header", "Page-Footer"]
AxisRole = Literal["x", "y", "y_right"]
Channel = Literal["length", "position", "angle", "area", "color", "radius"]


@dataclass(frozen=True)
class Element:
    """L0：页面上的一个框与它的类别。纯像素事实，无数据语义。"""

    box: Box
    category: ElementCategory


@dataclass(frozen=True)
class Axis:
    """`value_range` 与 `pixel_range` 是可读性判定与值反算的全部输入。"""

    role: AxisRole
    value_range: tuple[float, float]
    pixel_range: tuple[float, float]
    scale: Literal["linear", "log"] = "linear"
    column: str | None = None      # 这条轴绑的是哪一列；compound 的两条各绑一个测度


@dataclass(frozen=True)
class Panel:
    panel_id: str
    box: Box                        # 绘图区
    axes: tuple[Axis, ...] = ()
    chart_type: str = ""


@dataclass(frozen=True)
class Mark:
    """一个可单独指认的图形：一个框、一个键、一个值字典。

    `rows`（L2）与 `readable` 由 04 补齐，渲染器写出时为 None。
    """

    mark_id: str
    panel_id: str
    key: tuple[str, ...]
    values: dict[str, float]
    box: Box
    channel: Channel
    labeled: bool = False
    label_box: Box | None = None
    rows: int | None = None
    readable: bool | None = None


@dataclass(frozen=True)
class LegendEntry:
    """`applies_to_panels` 在单面板图上恒为一个元素；共享图例时才有信息量。"""

    box: Box
    maps_to_category: str
    applies_to_panels: tuple[str, ...] = ()


@dataclass(frozen=True)
class RenderOutput:
    """03 → 04。图像加三份几何，图元还没有 rows 与 readable。"""

    figure_id: str
    scenario_id: str
    image_path: str
    image_size: tuple[int, int]
    style: StyleVector
    panels: tuple[Panel, ...] = ()
    marks: tuple[Mark, ...] = ()
    legend: tuple[LegendEntry, ...] = ()
    elements: tuple[Element, ...] = ()
    degradations: tuple[Degradation, ...] = ()


@dataclass(frozen=True)
class SelfCheck:
    """04 §6 的三项。第三项按图抽样跑，没跑到时为 None。"""

    box_content: bool | None = None
    value_readback: bool | None = None
    style_invariant: bool | None = None
    reasons: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return all(v is not False for v in
                   (self.box_content, self.value_readback, self.style_invariant))


@dataclass(frozen=True)
class Record(RenderOutput):
    """04 → 05。RenderOutput 拼上 L2 行数、逐图元的 `readable` 与自检结论。"""

    selfcheck: SelfCheck = field(default_factory=SelfCheck)

    def panel(self, panel_id: str) -> Panel:
        for p in self.panels:
            if p.panel_id == panel_id:
                return p
        raise KeyError(f"没有这个面板: {panel_id}")

    def marks_of(self, panel_id: str) -> tuple[Mark, ...]:
        return tuple(m for m in self.marks if m.panel_id == panel_id)
