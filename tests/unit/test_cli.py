"""The command line, exercised without a model.

Every command has an offline path -- a hand-written answer stands in for the data
call -- and that is what a person runs first when they want to see the pipeline
work. It is also the only entry point where the stages are wired together by
argument parsing rather than by a test, so a wrong default here is invisible to
every other test in the suite.
"""

import json
from pathlib import Path

import pytest

from chartgen import cli
from chartgen.common import serde
from chartgen.interfaces.figure import FigureSpec
from chartgen.interfaces.table import TableSchema

SAMPLES = Path(__file__).resolve().parents[1] / "samples"
PAYLOAD = str(SAMPLES / "er_scenario.json")

#: What keeps an offline run to a few figures: the whole point here is the wiring,
#: and a full batch is what the end-to-end test is for.
SMALL = ["--set", "figure.k_max=3", "--set", "figure.max_derived=1",
         "--set", "figure.max_overlays=0", "--set", "figure.pages=0",
         "--set", "render.style_variants=1", "--set", "render.degradation=false"]


def data_dir(tmp_path: Path) -> Path:
    cli.main(["data", "--payload", PAYLOAD, "--scenario", "er",
              "-o", str(tmp_path), "--set", "output.dir=" + str(tmp_path)])
    return tmp_path / "er"


class TestTheDataCommand:
    def test_it_writes_a_schema_a_table_and_a_page(self, tmp_path, capsys):
        out = data_dir(tmp_path)
        assert (out / "schema.json").exists() and (out / "facts.parquet").exists()
        assert (out / "schema.md").exists()
        assert "wrote" in capsys.readouterr().out

    def test_the_schema_it_writes_reads_back(self, tmp_path):
        schema = serde.load(TableSchema, data_dir(tmp_path) / "schema.json")
        assert schema.scenario_id == "er" and schema.n_rows > 0
        assert schema.intents and schema.columns

    def test_a_rejected_answer_stops_with_a_message(self, tmp_path, capsys):
        broken = tmp_path / "broken.json"
        payload = json.loads(Path(PAYLOAD).read_text(encoding="utf-8"))
        payload["script"] = 'dim("only_one", ["a", "b"])\nemit(10)'
        broken.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SystemExit):
            cli.main(["data", "--payload", str(broken), "-o", str(tmp_path)])
        assert "rejected" in capsys.readouterr().out


class TestTheInspectCommand:
    def test_it_draws_a_page_beside_the_schema_it_was_given(self, tmp_path, capsys):
        out = data_dir(tmp_path)
        page = tmp_path / "seen.md"
        cli.main(["inspect", str(out / "schema.json"), "-o", str(page)])
        assert page.exists() and page.read_text(encoding="utf-8").strip()
        assert capsys.readouterr().out.strip()


class TestTheFiguresCommand:
    def test_it_chooses_figures_and_writes_them(self, tmp_path, capsys):
        cli.main(["figures", "--payload", PAYLOAD, "--scenario", "er",
                  "-o", str(tmp_path), *SMALL])
        specs = sorted((tmp_path / "er" / "specs").glob("*.json"))
        assert specs
        spec = serde.load(FigureSpec, specs[0])
        assert spec.panels and spec.views[0].data
        assert "wrote" in capsys.readouterr().out


class TestTheRenderCommand:
    def test_it_draws_a_saved_specification(self, tmp_path, capsys):
        cli.main(["figures", "--payload", PAYLOAD, "--scenario", "er",
                  "-o", str(tmp_path), *SMALL])
        spec = sorted((tmp_path / "er" / "specs").glob("*.json"))[0]
        cli.main(["render", str(spec), "-o", str(tmp_path / "drawn")])
        assert list((tmp_path / "drawn").glob("*.png"))
        assert "marks" in capsys.readouterr().out

    def test_a_pinned_style_is_the_one_that_gets_drawn(self, tmp_path):
        from dataclasses import replace

        from chartgen.interfaces.record import RenderOutput
        from chartgen.s03_render.style import default

        cli.main(["figures", "--payload", PAYLOAD, "--scenario", "er",
                  "-o", str(tmp_path), *SMALL])
        spec = sorted((tmp_path / "er" / "specs").glob("*.json"))[0]
        style = tmp_path / "style.json"
        serde.save(replace(default(), image_size=(700, 500)), style)
        cli.main(["render", str(spec), "--style", str(style), "-o", str(tmp_path / "pinned")])
        out = serde.load(RenderOutput, next((tmp_path / "pinned").glob("*.json")))
        assert out.image_size == (700, 500)


class TestTheRunCommand:
    def test_it_runs_every_stage_and_leaves_the_run_described(self, tmp_path, capsys):
        cli.main(["run", "--payload", PAYLOAD, "--scenario", "er",
                  "--set", f"output.dir={tmp_path}", "--set", "run_id=cli", *SMALL])
        out = tmp_path / "cli"
        assert list((out / "er" / "records").glob("*.json"))
        assert list((out / "er" / "targets").glob("*.json"))
        assert list((out / "er" / "v0").glob("*.png"))

        stats = json.loads((out / "stats.json").read_text(encoding="utf-8"))
        assert stats["scenarios"] == 1 and stats["records"] >= 1
        assert stats["figure_pass_rate"] == pytest.approx(1.0)
        log = json.loads((out / "er" / "log.json").read_text(encoding="utf-8"))
        assert log["counts"]["total"] == log["kept"] + log["dropped"] or log["kept"]
        assert "figure_pass_rate" in capsys.readouterr().out

    def test_an_overridden_setting_reaches_the_stage_that_reads_it(self, tmp_path):
        cli.main(["run", "--payload", PAYLOAD, "--scenario", "er",
                  "--set", f"output.dir={tmp_path}", "--set", "run_id=pinned",
                  "--set", "render.style_overrides={'image_size': [800, 560]}", *SMALL])
        from chartgen.interfaces.record import Record

        records = sorted((tmp_path / "pinned" / "er" / "records").glob("*.json"))
        assert records
        assert all(serde.load(Record, p).image_size == (800, 560) for p in records)
