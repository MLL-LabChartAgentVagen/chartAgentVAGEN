"""Running the stages in order, consulting the cache at each step.

    01 data --FactTable + TableSchema--> 02 figure --FigureSpec--> 03 render
       --RenderOutput--> 04 record --Record--> 05 output

Every stage has the same shape: upstream artifact, seed and configuration in,
downstream artifact out, stored under a hash of the input. A failure discards the
scenario or the figure it happened in and records why; it never stops the batch,
because the pass rate per stage is the main thing a run has to say about itself.

Two orderings matter and are not negotiable. Page composition and image degradation
both move every recorded box, so they run before the record is finished rather than
after. And the two style versions of a figure are rendered before either is checked,
because the third self-check compares them against each other.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from . import report
from .common import serde
from .common.cache import Store, content_hash
from .config import Config
from .interfaces.figure import FigureSpec
from .interfaces.record import Record, RenderOutput
from .interfaces.table import FactTable, TableSchema
from .s03_render import degrade, page
from .s03_render.render import render
from .s03_render.style import pin as pin_style
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


@dataclass(frozen=True)
class Batch:
    """One scenario's figures and the log of how they were chosen, as one artifact.

    Both together, because the log explains the figures and a cache hit that returned
    the figures without it would leave the run unable to say what it turned away.
    """

    figures: tuple[FigureSpec, ...] = ()
    log: str = "{}"


@dataclass
class ScenarioResult:
    scenario_id: str
    ok: bool
    stage: str = ""
    reason: str = ""
    records: list[Record] = field(default_factory=list)
    specs: list[FigureSpec] = field(default_factory=list)
    log: dict = field(default_factory=dict)
    dropped: list[tuple[str, str]] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        total = len(self.records) + len(self.dropped)
        return len(self.records) / total if total else 0.0


@dataclass
class Pipeline:
    config: Config
    out_dir: Path
    _sampler: object | None = field(default=None, repr=False)
    _seen: object | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.out_dir = Path(self.out_dir)
        self.store = Store(self.out_dir / "cache", self.config.get("cache.enabled", True))
        # One draw and one duplicate judge for the whole run, not one per scenario.
        # Per scenario they guarantee nothing: the draw is without replacement inside
        # a sampler, and a fresh sampler per scenario can hand the same sub-topic to
        # every one of them. The data prompt carries no scenario identifier, so a
        # repeated sub-topic is a cache hit and the second scenario comes back byte
        # for byte identical -- same title, same columns, same fact table.
        self._sampler = None
        self._seen = None

    def _drawing(self) -> tuple[object, object]:
        """The run-wide sampler and duplicate judge, built on first use.

        Built lazily because a run given a hand-written payload never draws from the
        pool, and the pool file need not exist for it.
        """
        from .s01_data.author import run_drawing

        if self._sampler is None:
            self._sampler, self._seen = run_drawing(self.config)
        return self._sampler, self._seen

    @property
    def seed(self) -> int:
        return int(self.config.get("root_seed", 0))

    # ---- the stages

    def stage_01(self, scenario_id: str, **kw) -> tuple[FactTable, TableSchema]:
        from .s01_data.author import build_scenario

        if "domain" not in kw and "sampler" not in kw:
            sampler, seen = self._drawing()
            kw = {**kw, "sampler": sampler, "is_duplicate": kw.get("is_duplicate") or seen}
        table, schema = build_scenario(scenario_id, self.seed, self.config, **kw)
        save_data(table, schema, self.out_dir,
                  max_tier=int(self.config.get("scale.max_tier", 3)))
        return table, schema

    def stage_02(self, table: FactTable, schema: TableSchema,
                 **kw) -> tuple[list[FigureSpec], dict]:
        """View selection, through the cache.

        Cached on the schema, the row count and the settings that decide what is
        chosen -- everything the stage reads. The figures are data, so a hit is the
        whole answer; rendering is not cached, because its artifact is a file beside
        the record and a record without its image is not an artifact at all.
        """
        from .s02_figure.compose import compose_with_log

        key = [schema.scenario_id, self.seed, table.n_rows,
               content_hash(schema), self.config.values.get("figure"),
               self.config.get("scale.max_tier"), self.config.get("llm.titles")]

        def build() -> Batch:
            figures, log = compose_with_log(table, schema, self.seed, self.config, **kw)
            return Batch(tuple(figures), json.dumps(log, ensure_ascii=False))

        batch = self.store.get_or_build(Batch, "s02_figure", key, build)
        return list(batch.figures), json.loads(batch.log)

    def stage_03(self, specs: Sequence[FigureSpec], schema: TableSchema,
                 out: Path) -> dict[tuple[str, int], RenderOutput]:
        """Draw every figure in every style version, compose pages, then degrade.

        Composition comes before degradation because a page is what actually gets
        degraded, and both come before the record is finished because both of them
        move every box that was recorded.
        """
        variants = int(self.config.get("render.style_variants", 1))
        drawn: dict[tuple[str, int], RenderOutput] = {}
        self.failed_to_draw: list[tuple[str, str]] = []
        for spec in specs:
            for variant in range(variants):
                # Figures composed onto one page share a style. A page whose two
                # figures were drawn in different palettes and different orientations
                # is not a page anyone publishes, and the pair is there to be a page.
                style = pin_style(
                    sample_style(self.seed, spec.scenario_id,
                                 spec.page_id or spec.figure_id, variant),
                    dict(self.config.get("render.style_overrides") or {}))
                try:
                    drawn[(spec.figure_id, variant)] = render(
                        spec, style, out / f"v{variant}", variant)
                except Exception as exc:  # noqa: BLE001 -- drop the figure, keep the batch
                    self.failed_to_draw.append((f"{spec.figure_id} v{variant}", repr(exc)))

        for variant in range(variants):
            drawn.update(self._compose_pages(specs, schema, drawn, variant, out))
        if self.config.get("render.degradation", True):
            drawn = self._degrade(drawn)
        return drawn

    def _degrade(self, drawn: dict) -> dict:
        """One degradation per image. Figures composed onto one page share an image,
        so degrading each of them would degrade the page once per figure."""
        by_image: dict[str, list] = {}
        for key, rendered in drawn.items():
            by_image.setdefault(rendered.image_path, []).append(key)
        out = dict(drawn)
        for keys in by_image.values():
            members = [drawn[k] for k in keys]
            done = degrade.apply_to_all(members, members[0].style.degradation, seed=self.seed)
            out.update(dict(zip(keys, done)))
        return out

    def _compose_pages(self, specs, schema, drawn, variant, out) -> dict:
        """Figures that share a page identifier go onto one page together."""
        pages: dict[str, list[FigureSpec]] = {}
        for spec in specs:
            if spec.page_id:
                pages.setdefault(spec.page_id, []).append(spec)
        updated = {}
        for page_id, members in pages.items():
            composed = page.compose(
                [drawn[(s.figure_id, variant)] for s in members], out / f"v{variant}",
                page_id=f"{page_id}_v{variant}",
                header=schema.scenario_title, body=schema.data_context,
                footer=f"{schema.scenario_id} - {schema.n_rows} rows",
                captions=[s.caption for s in members],
                closing=" ".join(s.text("subtitle") or s.text("title") for s in members))
            for spec, rendered in zip(members, composed):
                updated[(spec.figure_id, variant)] = rendered
        return updated

    def stage_04(self, drawn: dict, specs: Sequence[FigureSpec]
                 ) -> tuple[list[Record], list[tuple[str, str]]]:
        """Finish every record and keep the ones that pass their own checks."""
        from .s04_record.selfcheck import finish

        kept: list[Record] = []
        dropped: list[tuple[str, str]] = []
        variants = int(self.config.get("render.style_variants", 1))
        layers = {"provenance": bool(self.config.get("layers.provenance", True)),
                  "page_elements": bool(self.config.get("layers.page_elements", True)),
                  "encoding": bool(self.config.get("layers.encoding", True))}
        for spec in specs:
            second = None
            if variants > 1 and (spec.figure_id, 1) in drawn:
                second = finish(drawn[(spec.figure_id, 1)], spec, **layers)
            for variant in range(variants):
                rendered = drawn.get((spec.figure_id, variant))
                if rendered is None:
                    continue
                try:
                    record = finish(rendered, spec, **layers,
                                    variant=second if variant == 0 else None)
                except Exception as exc:  # noqa: BLE001 -- drop the figure, keep the batch
                    dropped.append((spec.figure_id, repr(exc)))
                    continue
                if record.selfcheck.passed:
                    kept.append(record)
                else:
                    dropped.append((f"{spec.figure_id} v{variant}",
                                    "; ".join(record.selfcheck.reasons) or "self-check failed"))
        return kept, dropped

    def stage_05(self, records: Sequence[Record], out: Path) -> list[Path]:
        from .s05_output.export import export, settings

        chosen = settings(lambda key: self.config.get(f"output.{key}"),
                          self.config.get("output.preset"))
        return export(records, out / "targets",
                      key_scope=chosen["key_scope"], granularity=chosen["granularity"],
                      targets=chosen["targets"], format=chosen["format"])

    # ---- one scenario end to end

    def run_scenario(self, scenario_id: str, **kw) -> ScenarioResult:
        out = self.out_dir / scenario_id
        try:
            table, schema = self.stage_01(scenario_id, **kw)
            specs, log = self.stage_02(table, schema)
        except Exception as exc:  # noqa: BLE001 -- isolate the failure to this scenario
            return ScenarioResult(scenario_id, False, "01/02", repr(exc))

        drawn = self.stage_03(specs, schema, out)
        records, dropped = self.stage_04(drawn, specs)
        dropped += getattr(self, "failed_to_draw", [])
        self.stage_05(records, out)
        for record in records:
            serde.save(record, out / "records" / f"{record.figure_id}_v{record.variant}.json")
        for spec in specs:
            serde.save(spec, out / "specs" / f"{spec.figure_id}.json")

        log["kept"] = len(records)
        log["dropped"] = len(dropped)
        log["dropped_figures"] = [{"figure": fid, "why": why} for fid, why in dropped]
        # Written out because it is the only account of what was *not* drawn: a
        # candidate the sampler threw away leaves no artifact behind, so a run that
        # kept its rejections only in memory could never be asked about them again.
        (out / "log.json").parent.mkdir(parents=True, exist_ok=True)
        (out / "log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False),
                                      encoding="utf-8")
        return ScenarioResult(scenario_id, True, records=records, specs=list(specs),
                              log=log, dropped=dropped)


def batch_stats(results: Sequence[ScenarioResult]) -> dict:
    """What a run says about its own health: how much came out, and what stopped."""
    kept = sum(len(r.records) for r in results)
    dropped = sum(len(r.dropped) for r in results)
    reasons: Counter = Counter()
    for result in results:
        for _, why in result.dropped:
            reasons[why.split(":")[0][:60]] += 1
        for kind, count in (result.log.get("rejected") or {}).items():
            reasons[f"candidate rejected: {kind}"] += count
    return {
        "scenarios": len(results),
        "scenarios_ok": sum(1 for r in results if r.ok),
        "records": kept,
        "dropped": dropped,
        "figure_pass_rate": kept / (kept + dropped) if kept + dropped else 0.0,
        "reasons": dict(reasons.most_common()),
    }
