"""Projecting a binding into values: four shapes, one SELECT each."""

import pytest

from chartgen.interfaces.figure import Binding, TimeWindow
from chartgen.registry.charts import DENSITY_BANDS
from chartgen.s02_figure import project as P


def bar(**kw):
    return Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG", **kw)


class TestGroupedScalar:
    def test_one_mark_per_group_with_its_row_count(self, er_table, er_schema):
        view = P.project(er_table.df, bar(), er_schema)
        assert [d.key for d in view.data] == [
            ("Mercy General",), ("St. Luke's",), ("Riverside",)]
        assert sum(d.rows for d in view.data) == 900

    def test_the_keys_come_out_in_declared_order_not_alphabetical(self, er_table, er_schema):
        view = P.project(er_table.df, bar(), er_schema)
        assert [d.key[0] for d in view.data] != sorted(d.key[0] for d in view.data)

    def test_the_average_matches_a_direct_computation(self, er_table, er_schema):
        view = P.project(er_table.df, bar(), er_schema)
        df = er_table.df
        for d in view.data:
            expected = df.loc[df.hospital == d.key[0], "wait_minutes"].mean()
            assert d.values["value"] == pytest.approx(expected)

    def test_counting_rows_needs_no_measure(self, er_table, er_schema):
        binding = Binding("bar", dims=("hospital",), aggregate="COUNT")
        view = P.project(er_table.df, binding, er_schema)
        assert [d.values["value"] for d in view.data] == [float(d.rows) for d in view.data]

    def test_a_pie_carries_shares_that_sum_to_one(self, er_table, er_schema):
        binding = Binding("pie", dims=("department",), measures=("cost",), aggregate="SUM")
        view = P.project(er_table.df, binding, er_schema)
        assert sum(d.values["share"] for d in view.data) == pytest.approx(1.0)

    def test_a_stacked_bar_stacks_inside_its_first_grouping_column(self, er_table, er_schema):
        binding = Binding("stacked_bar", dims=("hospital", "severity"),
                          measures=("cost",), aggregate="SUM")
        view = P.project(er_table.df, binding, er_schema)
        for d in view.data:
            assert d.values["cum_end"] - d.values["cum_start"] == pytest.approx(d.values["value"])
        starts = [d.values["cum_start"] for d in view.data if d.key[0] == "Mercy General"]
        assert starts[0] == 0.0 and starts == sorted(starts)

    def test_a_waterfall_accumulates_along_one_sequence(self, er_table, er_schema):
        binding = Binding("waterfall", dims=("severity",), measures=("cost",), aggregate="SUM")
        view = P.project(er_table.df, binding, er_schema)
        assert view.data[0].values["cum_start"] == 0.0
        for before, after in zip(view.data, view.data[1:]):
            assert after.values["cum_start"] == pytest.approx(before.values["cum_end"])

    def test_a_row_filter_cuts_the_rows_it_names(self, er_table, er_schema):
        window = TimeWindow("visit_date", "2024-01-01", "2024-03-31", "Q1-Q2")
        view = P.project(er_table.df, bar(), er_schema, row_filter=window)
        assert 0 < sum(d.rows for d in view.data) < 900


class TestTimeAxis:
    def test_a_daily_column_resampled_monthly_gives_six_points(self, er_table, er_schema):
        binding = Binding("line", time="visit_date", measures=("wait_minutes",),
                          aggregate="AVG", resample="monthly")
        view = P.project(er_table.df, binding, er_schema)
        assert [d.key[0] for d in view.data] == [
            "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06"]

    def test_weekly_labels_fall_on_a_monday(self, er_table, er_schema):
        binding = Binding("line", time="visit_date", measures=("wait_minutes",),
                          aggregate="AVG", resample="weekly")
        view = P.project(er_table.df, binding, er_schema)
        import datetime
        assert all(datetime.date.fromisoformat(d.key[0]).weekday() == 0 for d in view.data)

    def test_daily_keeps_every_day_that_has_rows(self, er_table, er_schema):
        binding = Binding("line", time="visit_date", measures=("wait_minutes",),
                          aggregate="AVG", resample="daily")
        view = P.project(er_table.df, binding, er_schema)
        assert len(view.data) == er_table.df.visit_date.nunique()

    def test_a_series_column_multiplies_the_points(self, er_table, er_schema):
        binding = Binding("line", dims=("hospital",), time="visit_date",
                          measures=("wait_minutes",), aggregate="AVG", resample="monthly")
        view = P.project(er_table.df, binding, er_schema)
        assert len(view.data) == 6 * 3
        assert view.data[0].key == ("2024-01", "Mercy General")


class TestGroupedFivenum:
    def test_five_numbers_come_out_in_order(self, er_table, er_schema):
        binding = Binding("box", dims=("department",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM")
        view = P.project(er_table.df, binding, er_schema)
        groups = [d for d in view.data if len(d.key) == 1]
        assert len(groups) == 4
        for d in groups:
            v = d.values
            assert v["min"] <= v["q1"] <= v["median"] <= v["q3"] <= v["max"]

    def test_outliers_are_their_own_marks_hung_off_their_group(self, er_table, er_schema):
        binding = Binding("box", dims=("department",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM")
        view = P.project(er_table.df, binding, er_schema)
        extra = [d for d in view.data if len(d.key) == 2]
        assert extra, "the wait time distribution is skewed enough to have outliers"
        assert all(d.rows >= 1 and set(d.values) == {"value"} for d in extra)
        assert P.group_keys(view) == {(name,) for name in
                                      er_table.df.department.astype(str).unique()}

    def test_outliers_that_share_a_value_are_one_mark_counting_its_rows(self, er_table,
                                                                        er_schema):
        """Rows with the same value are drawn on top of each other. Recorded one per
        row, several keys would carry the same box and a question about that box
        would have several right answers."""
        binding = Binding("box", dims=("department",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM")
        view = P.project(er_table.df, binding, er_schema)
        extra = [d for d in view.data if len(d.key) == 2]
        by_group: dict[tuple, list[float]] = {}
        for d in extra:
            by_group.setdefault(d.key[:-1], []).append(d.values["value"])
        for group, values in by_group.items():
            assert len(values) == len(set(values)), group
        assert sum(d.rows for d in extra) > len(extra), "some values repeat"

    def test_a_range_bar_reuses_the_same_path_without_outliers(self, er_table, er_schema):
        binding = Binding("range_bar", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM")
        view = P.project(er_table.df, binding, er_schema)
        assert len(view.data) == 3
        assert all(len(d.key) == 1 for d in view.data)

    def test_the_whiskers_stop_at_one_and_a_half_interquartile_ranges(self, er_table, er_schema):
        binding = Binding("box", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="FIVE_NUM")
        view = P.project(er_table.df, binding, er_schema)
        group = next(d for d in view.data if d.key == ("Mercy General",))
        raw = er_table.df.loc[er_table.df.hospital == "Mercy General", "wait_minutes"]
        assert group.values["max"] <= raw.max()
        assert group.values["max"] <= group.values["q3"] + 1.5 * (
            group.values["q3"] - group.values["q1"]) + 1e-9


class TestBinnedCount:
    def test_bins_tile_the_range_and_the_counts_add_up(self, er_table, er_schema):
        binding = Binding("histogram", measures=("wait_minutes",), aggregate="BIN_COUNT")
        view = P.project(er_table.df, binding, er_schema)
        assert 5 <= len(view.data) <= 30
        assert sum(d.values["count"] for d in view.data) == 900
        for a, b in zip(view.data, view.data[1:]):
            assert a.values["bin_hi"] == pytest.approx(b.values["bin_lo"])

    def test_provenance_is_the_count_itself(self, er_table, er_schema):
        binding = Binding("histogram", measures=("cost",), aggregate="BIN_COUNT")
        view = P.project(er_table.df, binding, er_schema)
        assert all(d.rows == int(d.values["count"]) for d in view.data)

    def test_a_constant_column_has_no_bins_to_draw(self, er_table, er_schema):
        df = er_table.df.assign(wait_minutes=1.0)
        binding = Binding("histogram", measures=("wait_minutes",), aggregate="BIN_COUNT")
        with pytest.raises(P.ProjectionError):
            P.project(df, binding, er_schema)


class TestPerRow:
    def test_nine_hundred_rows_are_thinned_to_the_point_cap(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        view = P.project(er_table.df, binding, er_schema, seed=7)
        assert len(view.data) == 500
        assert len(view.sample_index) == 500
        assert all(d.rows == 1 for d in view.data)

    def test_which_rows_survived_is_stored_and_reproducible(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        a = P.project(er_table.df, binding, er_schema, seed=7)
        b = P.project(er_table.df, binding, er_schema, seed=7)
        c = P.project(er_table.df, binding, er_schema, seed=8)
        assert a.sample_index == b.sample_index
        assert a.sample_index != c.sample_index

    def test_the_values_are_the_two_measures_of_that_row(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        view = P.project(er_table.df, binding, er_schema, seed=7)
        for d in view.data[:20]:
            row = er_table.df.iloc[int(d.key[-1].removeprefix("row_"))]
            assert d.values["x"] == pytest.approx(row.wait_minutes)
            assert d.values["y"] == pytest.approx(row.satisfaction)

    def test_a_series_column_leads_the_key(self, er_table, er_schema):
        binding = Binding("scatter", dims=("severity",),
                          measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        view = P.project(er_table.df, binding, er_schema, seed=7)
        assert all(len(d.key) == 2 for d in view.data)
        assert {d.key[0] for d in view.data} <= {"Minor", "Moderate", "Severe"}


class TestDensity:
    def test_a_denser_band_lets_more_points_through(self, er_table, er_schema):
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"), aggregate="NONE")
        sparse = P.project(er_table.df, binding, er_schema, seed=7, density=DENSITY_BANDS[0])
        extreme = P.project(er_table.df, binding, er_schema, seed=7, density=DENSITY_BANDS[4])
        assert len(sparse.data) == 500 and len(extreme.data) == 900


class TestDeterminism:
    def test_the_same_input_projects_to_the_same_values(self, er_table, er_schema):
        a = P.project(er_table.df, bar(), er_schema)
        b = P.project(er_table.df, bar(), er_schema)
        assert a == b

    def test_shuffling_the_rows_does_not_move_the_keys(self, er_table, er_schema):
        shuffled = er_table.df.sample(frac=1.0, random_state=3)
        a = P.project(er_table.df, bar(), er_schema)
        b = P.project(shuffled, bar(), er_schema)
        assert [d.key for d in a.data] == [d.key for d in b.data]
        assert [round(d.values["value"], 9) for d in a.data] == [
            round(d.values["value"], 9) for d in b.data]
