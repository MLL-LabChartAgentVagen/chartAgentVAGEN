"""The whole pipeline, offline, on the worked scenarios.

No model is called: the data stage is handed the same hand-written answer its one
call would have produced, and everything after it is program. So this runs in the
suite, and what it asserts is the property the whole design rests on -- that
`(input, seed) -> output` holds all the way to the training targets.
"""

import json
from pathlib import Path

import pytest

from chartgen.common import serde
from chartgen.config import Config
from chartgen.pipeline import Pipeline, batch_stats, save_data
from chartgen.registry.charts import CHARTS
from chartgen.s01_data.author import compose as compose_data

SAMPLES = Path(__file__).resolve().parents[1] / "samples"
SEED = 20260816

SCENARIOS = (("er_wait", "er_scenario.json"),
             ("checkout", "funnel_scenario.json"),
             ("logistics", "logistics_scenario.json"))


def run(out_dir: Path, scenario_id: str, payload_name: str, **overrides):
    payload = json.loads((SAMPLES / payload_name).read_text(encoding="utf-8"))
    config = Config.load().set("root_seed", SEED)
    for key, value in overrides.items():
        config.set(key, value)
    pipe = Pipeline(config, out_dir)

    def stage_01(sid, **kw):
        table, schema = compose_data(payload, scenario_id=sid, seed=SEED, config=config)
        save_data(table, schema, pipe.out_dir)
        return table, schema

    pipe.stage_01 = stage_01                    # type: ignore[method-assign]
    return pipe.run_scenario(scenario_id)


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    out = tmp_path_factory.mktemp("e2e")
    return [run(out / sid, sid, name) for sid, name in SCENARIOS]


class TestItRunsThrough:
    def test_every_scenario_finishes(self, results):
        assert all(r.ok for r in results)

    def test_every_scenario_yields_figures(self, results):
        assert all(len(r.records) >= 10 for r in results)

    def test_nothing_is_kept_that_failed_its_own_checks(self, results):
        for result in results:
            for record in result.records:
                assert record.selfcheck.passed, (record.figure_id, record.selfcheck.reasons)

    def test_both_style_versions_of_a_figure_agree(self, results):
        """The third self-check has an input only because two style versions of every
        figure are a product in their own right."""
        checked = [r for result in results for r in result.records
                   if r.selfcheck.style_invariant is not None]
        assert checked and all(r.selfcheck.style_invariant for r in checked)

    def test_the_run_reports_its_own_health(self, results):
        stats = batch_stats(results)
        assert stats["scenarios_ok"] == len(results)
        assert stats["figure_pass_rate"] > 0.9
        assert stats["reasons"], "a run that turned nothing away has no admission rules"


class TestWhatCameOut:
    def test_the_three_ways_into_a_batch_are_all_used(self, results):
        kinds = {s.source.kind for r in results for s in r.specs}
        assert {"intent", "panel", "overlay", "rotation"} <= kinds

    def test_the_batch_spans_most_of_the_type_table(self, results):
        drawn = {t for r in results for rec in r.records
                 for p in rec.panels for t in p.chart_types}
        assert len(drawn) >= len(CHARTS) - 4, sorted(set(CHARTS) - drawn)

    def test_a_figure_appears_both_alone_and_inside_a_derived_one(self, results):
        """The same view drawn twice at different pixels with the same keys and
        values is the layout pairing, and the anchor rule is what guarantees it."""
        for result in results:
            derived = [s for s in result.specs if s.source.anchor_figure_id]
            assert derived
            for spec in derived:
                anchor = next(s for s in result.specs
                              if s.figure_id == spec.source.anchor_figure_id)
                assert len(anchor.panels) == 1

    def test_a_shared_legend_covers_more_than_one_panel(self, results):
        entries = [e for r in results for rec in r.records for e in rec.legend
                   if len(e.applies_to_panels) > 1]
        assert entries, "no figure produced a legend entry governing several panels"

    def test_every_key_segment_says_where_it_was_read_from(self, results):
        for result in results:
            for record in result.records:
                for mark in record.marks:
                    assert len(mark.key) == len(mark.key_src)

    def test_the_batch_shows_several_different_key_sources(self, results):
        sources = {s for r in results for rec in r.records for m in rec.marks
                   for s in m.key_src}
        assert len(sources) >= 5, sources

    def test_two_figures_are_composed_onto_one_page(self, results):
        for result in results:
            pages = {rec.page_id for rec in result.records if rec.page_id}
            assert pages
            for page in pages:
                on_it = {rec.figure_id for rec in result.records if rec.page_id == page}
                assert len(on_it) >= 2


class TestArtifacts:
    def test_the_records_land_on_disk_and_read_back(self, results, tmp_path_factory):
        from chartgen.interfaces.record import Record

        for result in results:
            saved = list((Path(result.records[0].image_path).parents[1] /
                          "records").glob("*.json"))
            assert saved
            assert serde.load(Record, saved[0]).figure_id

    def test_the_training_targets_are_written(self, results):
        for result in results:
            targets = Path(result.records[0].image_path).parents[1] / "targets"
            written = list(targets.glob("*.json"))
            assert len(written) == len(result.records)
            payload = json.loads(written[0].read_text(encoding="utf-8"))
            assert payload["key_scope"] and payload["figures"]

    def test_the_schema_page_is_written_beside_the_schema(self, results):
        for result in results:
            folder = Path(result.records[0].image_path).parents[1]
            assert (folder / "schema.md").exists() and (folder / "schema.json").exists()


class TestReproducible:
    def test_the_same_seed_gives_the_same_records(self, tmp_path):
        first = run(tmp_path / "a", "er_wait", "er_scenario.json")
        second = run(tmp_path / "b", "er_wait", "er_scenario.json")
        strip = lambda rs: [(r.figure_id, [m.key for m in r.marks],
                             [round(v, 9) for m in r.marks for v in m.values.values()],
                             [m.box.as_tuple() for m in r.marks]) for r in rs]
        assert strip(first.records) == strip(second.records)

    def test_the_same_seed_gives_byte_identical_images(self, tmp_path):
        first = run(tmp_path / "a", "er_wait", "er_scenario.json")
        second = run(tmp_path / "b", "er_wait", "er_scenario.json")
        for a, b in zip(first.records, second.records):
            assert Path(a.image_path).read_bytes() == Path(b.image_path).read_bytes()

    def test_a_different_seed_moves_the_sampled_figures_only(self, tmp_path):
        base = run(tmp_path / "a", "er_wait", "er_scenario.json")
        other = run(tmp_path / "b", "er_wait", "er_scenario.json", root_seed=99)
        built = lambda r: [s.chart_types for s in r.specs if s.source.kind == "intent"]
        assert built(base) == built(other)


class TestAblationSwitches:
    def test_the_provenance_layer_can_be_switched_off(self, tmp_path):
        result = run(tmp_path, "er_wait", "er_scenario.json", **{"layers.provenance": False})
        assert all(m.rows is None for r in result.records for m in r.marks)

    def test_a_wider_key_scope_lands_in_the_artifact(self, tmp_path):
        result = run(tmp_path, "er_wait", "er_scenario.json", **{"output.key_scope": "panel"})
        targets = Path(result.records[0].image_path).parents[1] / "targets"
        payload = json.loads(next(targets.glob("*.json")).read_text(encoding="utf-8"))
        assert payload["key_scope"] == "panel"

    def test_a_page_sized_export_writes_one_payload_per_page(self, tmp_path):
        result = run(tmp_path, "er_wait", "er_scenario.json",
                     **{"output.granularity": "page"})
        targets = Path(result.records[0].image_path).parents[1] / "targets"
        assert list(targets.glob("*.json")) and not list(targets.glob("*.md"))

    def test_the_format_is_what_decides_whether_a_document_is_written(self, tmp_path):
        """Granularity says what goes in one file and the format says what that file
        is. A page as a document and a page as a payload are one record projected
        twice, so neither setting implies the other."""
        result = run(tmp_path, "er_wait", "er_scenario.json",
                     **{"output.granularity": "page", "output.format": "both"})
        targets = Path(result.records[0].image_path).parents[1] / "targets"
        assert list(targets.glob("*.md")) and list(targets.glob("*.json"))

    def test_the_parsebench_preset_writes_one_markdown_page_and_nothing_else(
            self, tmp_path):
        result = run(tmp_path, "er_wait", "er_scenario.json",
                     **{"output.preset": "parsebench"})
        targets = Path(result.records[0].image_path).parents[1] / "targets"
        assert list(targets.glob("*.md")) and not list(targets.glob("*.json"))
        text = next(targets.glob("*.md")).read_text(encoding="utf-8")
        assert "| key 1 |" in text and text.lstrip().startswith("#")

    def test_another_family_weight_preset_changes_the_sampled_figures(self, tmp_path):
        base = run(tmp_path / "a", "er_wait", "er_scenario.json")
        other = run(tmp_path / "b", "er_wait", "er_scenario.json",
                    **{"figure.family_weights": "parsebench"})
        sampled = lambda r: [s.chart_types for s in r.specs if s.source.kind == "rotation"]
        assert sampled(base) != sampled(other)
        assert other.log["family_weights"]["preset"] == "parsebench"

    def test_a_denser_band_is_recorded_with_the_batch(self, tmp_path):
        result = run(tmp_path, "er_wait", "er_scenario.json",
                     **{"figure.density_band": "normal"})
        assert result.log["density_band"] == "normal"


class TestTheArtifactCache:
    """Changing a later stage must not re-run the earlier ones, and an interrupted
    batch has to resume where it stopped. Both are the same mechanism: a stage's
    output stored under a hash of everything that stage reads."""

    def _selection(self, out: Path, **overrides):
        payload = json.loads((SAMPLES / "er_scenario.json").read_text(encoding="utf-8"))
        config = Config.load().set("root_seed", SEED)
        for key, value in overrides.items():
            config.set(key, value)
        pipe = Pipeline(config, out)
        table, schema = compose_data(payload, scenario_id="er_wait", seed=SEED,
                                     config=config)
        return pipe, pipe.stage_02(table, schema), table, schema

    def test_a_second_run_returns_the_stored_answer(self, tmp_path):
        pipe, (first, log), table, schema = self._selection(tmp_path)
        again, log_again = Pipeline(Config.load().set("root_seed", SEED),
                                    tmp_path).stage_02(table, schema)
        assert [f.figure_id for f in again] == [f.figure_id for f in first]
        assert log_again == log
        assert list((tmp_path / "cache").rglob("*.json"))

    def test_a_setting_that_changes_the_answer_changes_the_key(self, tmp_path):
        _, (first, _), table, schema = self._selection(tmp_path)
        _, (other, _), _, _ = self._selection(tmp_path, **{"figure.k_max": 6})
        assert len(other) < len(first)

    def test_the_cache_can_be_switched_off(self, tmp_path):
        self._selection(tmp_path, **{"cache.enabled": False})
        assert not list((tmp_path / "cache").rglob("*.json"))
