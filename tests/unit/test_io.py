"""接口读写：一份编解码器，版本检查在这一层。"""

import json

import pandas as pd
import pytest

from chartgen.common.geometry import Box
from chartgen.interfaces import io
from chartgen.interfaces.figure import Binding, Datum, FigureSpec, PanelSpec, Sharing, Source, ViewSpec
from chartgen.interfaces.record import Axis, Mark, Panel, Record, RenderOutput, SelfCheck
from chartgen.interfaces.style import StyleVector
from chartgen.interfaces.table import Column, FactTable, IntentBinding, TableSchema


@pytest.fixture
def schema() -> TableSchema:
    return TableSchema(
        scenario_id="er_wait",
        scenario_title="2024 上半年 A 市三家三甲医院急诊科就诊与等待时间记录",
        data_context="A 市卫健委为评估急诊分流政策的效果……",
        columns=(
            Column("hospital", "category", 3, group="entity", values=("协和", "华山", "瑞金")),
            Column("wait_minutes", "measure", 900, unit="分钟", additive=True),
        ),
        dependencies=(("wait_minutes", "cost"),),
        intents=(IntentBinding(0, "哪家医院等待最久", ("hospital", "wait_minutes"), "AVG", "comparison"),),
        n_rows=900,
    )


@pytest.fixture
def figure() -> FigureSpec:
    view = ViewSpec(
        binding=Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG"),
        data=(
            Datum(("协和",), {"value": 42.3}, 372),
            Datum(("华山",), {"value": 35.8}, 315),
            Datum(("瑞金",), {"value": 28.1}, 213),
        ),
    )
    return FigureSpec(
        figure_id="f01", scenario_id="er_wait",
        panels=(PanelSpec("p0", view),),
        sharing=Sharing(), source=Source("intent", intent_index=0),
    )


class TestRoundTrip:
    def test_table_schema_round_trips_to_the_same_object(self, schema, tmp_path):
        io.save(schema, tmp_path / "schema.json")
        assert io.load(TableSchema, tmp_path / "schema.json") == schema

    def test_figure_spec_round_trips(self, figure, tmp_path):
        io.save(figure, tmp_path / "figure.json")
        assert io.load(FigureSpec, tmp_path / "figure.json") == figure

    def test_second_write_is_byte_identical(self, figure, tmp_path):
        io.save(figure, tmp_path / "a.json")
        io.save(io.load(FigureSpec, tmp_path / "a.json"), tmp_path / "b.json")
        assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()

    def test_tuples_stay_tuples_not_lists(self, figure, tmp_path):
        io.save(figure, tmp_path / "f.json")
        back = io.load(FigureSpec, tmp_path / "f.json")
        assert isinstance(back.panels[0].view.data[0].key, tuple)
        assert isinstance(back.panels[0].view.binding.dims, tuple)

    def test_box_round_trips_as_four_numbers(self, tmp_path):
        mark = Mark("m0", "p0", ("协和",), {"value": 42.3}, Box(168, 196, 278, 520), "length")
        io.save(mark, tmp_path / "m.json")
        raw = json.loads((tmp_path / "m.json").read_text())
        assert raw["data"]["box"] == [168.0, 196.0, 278.0, 520.0]
        assert io.load(Mark, tmp_path / "m.json") == mark

    def test_optional_fields_survive_as_none(self, tmp_path):
        mark = Mark("m0", "p0", ("协和",), {"value": 1.0}, Box(0, 0, 1, 1), "length")
        assert io.load_dict(Mark, io.to_dict(mark)).readable is None

    def test_record_inherits_render_output_fields(self, tmp_path):
        rec = Record(
            figure_id="f01", scenario_id="s", image_path="a.png", image_size=(900, 600),
            style=StyleVector(),
            panels=(Panel("p0", Box(96, 60, 860, 520),
                          (Axis("y", (0.0, 60.0), (520.0, 60.0), column="wait_minutes"),), "bar"),),
            marks=(Mark("m0", "p0", ("协和",), {"value": 42.3}, Box(168, 196, 278, 520),
                        "length", rows=372, readable=True),),
            selfcheck=SelfCheck(True, True, None),
        )
        io.save(rec, tmp_path / "r.json")
        assert io.load(Record, tmp_path / "r.json") == rec

    def test_style_vector_round_trips_with_nested_degradation(self, tmp_path):
        s = StyleVector(value_labels="all", palette="grayscale")
        assert io.load_dict(StyleVector, io.to_dict(s)) == s


class TestVersionCheck:
    def test_envelope_carries_type_and_version(self, schema, tmp_path):
        io.save(schema, tmp_path / "s.json")
        raw = json.loads((tmp_path / "s.json").read_text())
        assert raw["type"] == "TableSchema"
        assert raw["schema_version"] == io.SCHEMA_VERSION

    def test_old_version_raises_instead_of_silently_misreading(self, schema, tmp_path):
        p = tmp_path / "s.json"
        io.save(schema, p)
        raw = json.loads(p.read_text())
        raw["schema_version"] = io.SCHEMA_VERSION - 1
        p.write_text(json.dumps(raw))
        with pytest.raises(io.SchemaVersionError):
            io.load(TableSchema, p)

    def test_wrong_type_raises(self, schema, figure, tmp_path):
        io.save(schema, tmp_path / "s.json")
        with pytest.raises(io.SchemaTypeError):
            io.load(FigureSpec, tmp_path / "s.json")


class TestFactTable:
    def test_fact_table_round_trips_through_parquet(self, tmp_path):
        df = pd.DataFrame({"hospital": ["协和", "华山"], "wait_minutes": [42.3, 35.8]})
        io.save_table(FactTable("er_wait", df), tmp_path / "facts.parquet")
        back = io.load_table(tmp_path / "facts.parquet")
        assert back.scenario_id == "er_wait"
        pd.testing.assert_frame_equal(back.df, df)


class TestSamples:
    """每份接口一个最小样例，改接口必须同时改样例。"""

    def test_every_sample_file_loads(self):
        assert io.SAMPLES, "tests/samples/ 里没有样例文件"
        for name, (cls, path) in io.SAMPLES.items():
            assert io.load(cls, path) is not None, name

    def test_samples_on_disk_match_their_builder(self):
        """样例与接口不许漂移：改了接口就必须重跑 tools/make_samples.py。"""
        import tools.make_samples as mk

        for name, build in mk.BUILDERS.items():
            cls, path = io.SAMPLES[name]
            assert io.load(cls, path) == build(), f"{name} 样例已过期，重跑 tools/make_samples.py"

    def test_running_example_numbers_are_the_ones_in_the_spec(self):
        """急诊科示例的数字在 01–05 各文档里是串起来的，样例必须对得上。"""
        schema = io.sample("TableSchema")
        figure = io.sample("FigureSpec")
        record = io.sample("Record")
        assert schema.n_rows == 900
        assert [d.values["value"] for d in figure.panels[0].view.data] == [42.3, 35.8, 28.1]
        assert record.marks[0].box.as_tuple() == (168.0, 196.0, 278.0, 520.0)
        assert record.marks[0].rows == 372
