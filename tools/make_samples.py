"""生成 tests/samples/ 下的最小接口样例。

样例用[急诊科贯穿示例](../storyline/parsebench_chart/README.md#贯穿示例)的数字，
与规格文档里的 01–05 逐段对齐：900 行 → 协和 42.3 / 华山 35.8 / 瑞金 28.1 →
协和的条 [168, 196, 278, 520]。

改接口时改这里再重跑：`python tools/make_samples.py`。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from chartgen.common.geometry import Box  # noqa: E402
from chartgen.interfaces import io  # noqa: E402
from chartgen.interfaces.figure import (  # noqa: E402
    Binding, Datum, FigureSpec, PanelSpec, Sharing, Source, ViewSpec,
)
from chartgen.interfaces.record import (  # noqa: E402
    Axis, Element, Mark, Panel, Record, RenderOutput, SelfCheck,
)
from chartgen.interfaces.style import Degradation, StyleVector  # noqa: E402
from chartgen.interfaces.table import Column, DimGroup, IntentBinding, TableSchema  # noqa: E402

SCENARIO = "er_wait"
IMAGE_SIZE = (900, 600)
PLOT_RECT = Box(96, 60, 860, 520)
Y_AXIS = Axis("y", (0.0, 60.0), (520.0, 60.0), column="wait_minutes")

BARS = (
    (("协和",), 42.3, Box(168, 196, 278, 520), 372),
    (("华山",), 35.8, Box(423, 245, 533, 520), 315),
    (("瑞金",), 28.1, Box(678, 305, 788, 520), 213),
)


def table_schema() -> TableSchema:
    return TableSchema(
        scenario_id=SCENARIO,
        scenario_title="2024 上半年 A 市三家三甲医院急诊科就诊与等待时间记录",
        data_context=(
            "A 市卫健委为评估急诊分流政策的效果，"
            "汇总了三家三甲医院 2024 年 1 至 6 月的逐次就诊记录。"
        ),
        columns=(
            Column("hospital", "category", 3, group="entity",
                   values=("协和", "华山", "瑞金")),
            Column("department", "category", 4, group="entity", parent="hospital",
                   values=("内科", "外科", "儿科", "创伤")),
            Column("severity", "category", 3, group="triage", ordered="ordinal",
                   values=("轻", "中", "重")),
            Column("visit_date", "time", 182, group="calendar",
                   freq="daily", start="2024-01-01", end="2024-06-30"),
            Column("day_of_week", "category", 7, group="calendar", derived_from="visit_date",
                   ordered="ordinal",
                   values=("周一", "周二", "周三", "周四", "周五", "周六", "周日")),
            Column("month", "category", 6, group="calendar", derived_from="visit_date",
                   ordered="ordinal",
                   values=("2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06")),
            Column("wait_minutes", "measure", 900, unit="分钟", additive=True),
            Column("cost", "measure", 900, unit="元", additive=True),
            Column("satisfaction", "measure", 900, unit="分", additive=False),
        ),
        groups=(
            DimGroup("entity", ("hospital", "department")),
            DimGroup("triage", ("severity",)),
            DimGroup("calendar", ("visit_date", "day_of_week", "month")),
        ),
        dependencies=(("wait_minutes", "cost"), ("wait_minutes", "satisfaction")),
        intents=(
            IntentBinding(0, "哪家医院、哪个科室的等待时间最长",
                          ("hospital", "wait_minutes"), "AVG", "comparison"),
            IntentBinding(1, "等待时间在半年内怎么变化",
                          ("visit_date", "wait_minutes"), "AVG", "trend"),
            IntentBinding(2, "等待越久是不是满意度越低",
                          ("wait_minutes", "satisfaction"), "NONE", "relation"),
        ),
        n_rows=900,
    )


def figure_spec() -> FigureSpec:
    view = ViewSpec(
        binding=Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG"),
        data=tuple(Datum(key, {"value": v}, rows) for key, v, _, rows in BARS),
    )
    return FigureSpec(
        figure_id="f01",
        scenario_id=SCENARIO,
        panels=(PanelSpec("p0", view),),
        layout="single",
        sharing=Sharing(),
        relation=None,
        source=Source("intent", intent_index=0),
        column_units={"wait_minutes": "分钟", "cost": "元", "satisfaction": "分"},
    )


def style_vector() -> StyleVector:
    """03 §0 采样出的那一组：全不画标注、企业蓝、y 起点为零、900×600、JPEG 75。"""
    return StyleVector(
        value_labels="none",
        palette="corporate_low",
        zero_baseline=True,
        image_size=IMAGE_SIZE,
        degradation=Degradation("jpeg", 75),
    )


def render_output() -> RenderOutput:
    return RenderOutput(
        figure_id="f01",
        scenario_id=SCENARIO,
        image_path="out/er_wait/f01.png",
        image_size=IMAGE_SIZE,
        style=style_vector(),
        panels=(Panel("p0", PLOT_RECT, (Y_AXIS,), "bar"),),
        marks=tuple(
            Mark(f"m{i}", "p0", key, {"value": v}, box, "length", labeled=False)
            for i, (key, v, box, _) in enumerate(BARS)
        ),
        legend=(),
        elements=(Element(Box(0, 0, *IMAGE_SIZE), "Picture"),),
        degradations=(Degradation("jpeg", 75),),
    )


def record() -> Record:
    r = render_output()
    return Record(
        figure_id=r.figure_id, scenario_id=r.scenario_id, image_path=r.image_path,
        image_size=r.image_size, style=r.style, panels=r.panels,
        marks=tuple(
            Mark(f"m{i}", "p0", key, {"value": v}, box, "length",
                 labeled=False, rows=rows, readable=True)
            for i, (key, v, box, rows) in enumerate(BARS)
        ),
        legend=r.legend, elements=r.elements, degradations=r.degradations,
        selfcheck=SelfCheck(box_content=True, value_readback=True, style_invariant=True),
    )


BUILDERS = {
    "TableSchema": table_schema,
    "FigureSpec": figure_spec,
    "StyleVector": style_vector,
    "RenderOutput": render_output,
    "Record": record,
}


def main() -> None:
    for name, build in BUILDERS.items():
        path = io.SAMPLES[name][1]
        io.save(build(), path)
        print(f"写出 {path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
