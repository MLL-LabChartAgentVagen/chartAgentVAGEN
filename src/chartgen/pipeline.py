"""编排：按顺序调五个阶段，每步查缓存。

    01 data ──FactTable + TableSchema──▶ 02 figure ──FigureSpec──▶ 03 render
       ──RenderOutput──▶ 04 record ──Record──▶ 05 output

每个阶段是 `阶段(上游产物, 种子, 配置) -> 下游产物`，产物按输入的内容哈希落盘。
任何阶段失败只丢弃当前场景并写一条带原因的记录，不中断批次。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .common.cache import Store
from .config import Config
from .interfaces.figure import FigureSpec
from .interfaces.record import Record
from .interfaces.style import StyleVector
from .interfaces.table import FactTable, TableSchema
from .s03_render.render import render
from .s03_render.style import sample as sample_style


@dataclass
class ScenarioResult:
    scenario_id: str
    ok: bool
    stage: str = ""
    reason: str = ""
    records: list[Record] = field(default_factory=list)


@dataclass
class Pipeline:
    config: Config
    out_dir: Path

    def __post_init__(self) -> None:
        self.out_dir = Path(self.out_dir)
        self.store = Store(self.out_dir / "cache", self.config.get("cache.enabled", True))

    @property
    def seed(self) -> int:
        return int(self.config.get("root_seed", 0))

    # ---- 各阶段。尚未落地的阶段在这里抛 NotImplementedError，串起签名。

    def stage_01(self, scenario_id: str) -> tuple[FactTable, TableSchema]:
        from .s01_data.author import build_scenario

        return build_scenario(scenario_id, self.seed, self.config)

    def stage_02(self, table: FactTable, schema: TableSchema) -> list[FigureSpec]:
        from .s02_figure.compose import compose

        return compose(table, schema, self.seed, self.config)

    def stage_03(self, spec: FigureSpec, style: StyleVector):
        return render(spec, style, self.out_dir / spec.scenario_id)

    def stage_04(self, rendered, spec: FigureSpec) -> Record:
        from .s04_record.merge import finish

        return finish(rendered, spec)

    def stage_05(self, records: list[Record]) -> Path:
        from .s05_output.export import export

        return export(records, self.out_dir / "targets")

    # ---- 一个场景走完五段

    def run_scenario(self, scenario_id: str) -> ScenarioResult:
        try:
            table, schema = self.stage_01(scenario_id)
            specs = self.stage_02(table, schema)
        except Exception as exc:  # noqa: BLE001 — 失败隔离：丢场景不中断批次
            return ScenarioResult(scenario_id, False, "01/02", repr(exc))

        records: list[Record] = []
        for spec in specs:
            for variant in range(int(self.config.get("render.style_variants", 1))):
                style = sample_style(self.seed, scenario_id, spec.figure_id, variant)
                try:
                    records.append(self.stage_04(self.stage_03(spec, style), spec))
                except Exception as exc:  # noqa: BLE001 — 丢图不丢场景
                    print(f"丢弃 {spec.figure_id} 风格 {variant}: {exc!r}")
        return ScenarioResult(scenario_id, True, records=records)
