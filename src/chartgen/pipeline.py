"""Running the stages in order, consulting the cache at each step.

    01 data ──FactTable + TableSchema──▶ 02 figure ──FigureSpec──▶ 03 render
       ──RenderOutput──▶ 04 record ──Record──▶ 05 output

Every stage has the same shape: upstream artifact, seed and configuration in,
downstream artifact out, stored under a hash of the input. A failure discards the
scenario it happened in and records why; it never stops the batch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import report
from .common import serde
from .common.cache import Store
from .config import Config
from .interfaces.figure import FigureSpec
from .interfaces.record import Record
from .interfaces.style import StyleVector
from .interfaces.table import FactTable, TableSchema
from .s03_render.render import render
from .s03_render.style import sample as sample_style


def save_data(table: FactTable, schema: TableSchema, out_dir: Path,
              *, max_tier: int = 3) -> Path:
    """Write what the data stage produced under `out_dir/<scenario_id>/`: the fact
    table, its schema, and the diagram page that makes the schema readable."""
    out = Path(out_dir) / schema.scenario_id
    out.mkdir(parents=True, exist_ok=True)
    serde.save(schema, out / "schema.json")
    serde.save_table(table, out / "facts.parquet")
    report.page(schema, out / "schema.md", max_tier=max_tier)
    return out


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

    # ---- the stages

    def stage_01(self, scenario_id: str) -> tuple[FactTable, TableSchema]:
        from .s01_data.author import build_scenario

        table, schema = build_scenario(scenario_id, self.seed, self.config)
        save_data(table, schema, self.out_dir,
                  max_tier=int(self.config.get("scale.max_tier", 3)))
        return table, schema

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

    # ---- one scenario end to end

    def run_scenario(self, scenario_id: str) -> ScenarioResult:
        try:
            table, schema = self.stage_01(scenario_id)
            specs = self.stage_02(table, schema)
        except Exception as exc:  # noqa: BLE001 -- isolate the failure to this scenario
            return ScenarioResult(scenario_id, False, "01/02", repr(exc))

        records: list[Record] = []
        for spec in specs:
            for variant in range(int(self.config.get("render.style_variants", 1))):
                style = sample_style(self.seed, scenario_id, spec.figure_id, variant)
                try:
                    records.append(self.stage_04(self.stage_03(spec, style), spec))
                except Exception as exc:  # noqa: BLE001 -- drop the figure, keep the scenario
                    print(f"dropped {spec.figure_id} style {variant}: {exc!r}")
        return ScenarioResult(scenario_id, True, records=records)
