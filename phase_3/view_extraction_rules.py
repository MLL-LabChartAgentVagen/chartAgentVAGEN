VIEW_EXTRACTION_RULES = {

    # ===== Comparison Family =====
    "bar_chart": {
        "transform": "SELECT {cat}, AGG({measure}) FROM M GROUP BY {cat} ORDER BY AGG DESC",
        "column_binding": {"cat": ["primary", "secondary"], "measure": ["measure"]},
        "agg_options": ["AVG", "SUM", "COUNT"],
        "constraint": "3 <= |GROUP BY result| <= 30",
        "visual_mapping": {"x": "{cat}", "y": "AGG({measure})"}
    },
    "grouped_bar_chart": {
        "transform": "SELECT {cat1}, {cat2}, AGG({measure}) FROM M GROUP BY {cat1}, {cat2}",
        "column_binding": {"cat1": ["primary"], "cat2": ["secondary", "orthogonal"],
                           "measure": ["measure"]},
        "constraint": "|cat1| * |cat2| in [6, 20]",
        "visual_mapping": {"x": "{cat1}", "group": "{cat2}", "y": "AGG({measure})"}
    },

    # ===== Trend Family =====
    "line_chart": {
        "transform": "SELECT {time}, {series}, AGG({measure}) FROM M GROUP BY {time}, {series}",
        "column_binding": {"time": ["temporal"], "series": ["primary", "orthogonal"],
                           "measure": ["measure"]},
        "constraint": "|time_points| >= 5; |series| in [1, 6]",
        "visual_mapping": {"x": "{time}", "series": "{series}", "y": "AGG({measure})"}
    },
    "area_chart": {
        "transform": "SELECT {time}, {stack}, SUM({measure}) FROM M GROUP BY {time}, {stack}",
        "column_binding": {"time": ["temporal"], "stack": ["primary", "orthogonal"],
                           "measure": ["measure"]},
        "constraint": "|stack| in [2, 5]",
        "visual_mapping": {"x": "{time}", "area": "{stack}", "y": "SUM({measure})"}
    },

    # ===== Distribution Family =====
    "histogram": {
        "transform": "SELECT {measure} FROM M [WHERE {filter}]",
        "column_binding": {"measure": ["measure"]},
        "constraint": "|rows| >= 100",
        "visual_mapping": {"x": "{measure}", "y": "frequency"}
    },
    "box_plot": {
        "transform": "SELECT {cat}, {measure} FROM M",
        "column_binding": {"cat": ["primary", "orthogonal"], "measure": ["measure"]},
        "constraint": ">= 15 data points per category",
        "visual_mapping": {"x": "{cat}", "y": "{measure}"}
    },
    "violin_plot": {
        "transform": "SELECT {cat}, {measure} FROM M",
        "column_binding": {"cat": ["primary", "orthogonal"], "measure": ["measure"]},
        "constraint": ">= 30 data points per category",
        "visual_mapping": {"x": "{cat}", "y": "{measure}"}
    },

    # ===== Composition Family =====
    "pie_chart": {
        "transform": "SELECT {cat}, SUM({measure}) FROM M GROUP BY {cat}",
        "column_binding": {"cat": ["primary", "secondary"], "measure": ["measure"]},
        "constraint": "3 <= |cat| <= 8",
        "visual_mapping": {"category": "{cat}", "value": "SUM({measure})"}
    },
    "donut_chart": {
        "transform": "SELECT {cat}, SUM({measure}) FROM M GROUP BY {cat}",
        "column_binding": {"cat": ["primary", "secondary"], "measure": ["measure"]},
        "constraint": "3 <= |cat| <= 8",
        "visual_mapping": {"category": "{cat}", "value": "SUM({measure})"}
    },
    "stacked_bar_chart": {
        "transform": "SELECT {cat1}, {cat2}, SUM({measure}) FROM M GROUP BY {cat1}, {cat2}",
        "column_binding": {"cat1": ["primary"], "cat2": ["secondary", "orthogonal"],
                           "measure": ["measure"]},
        "constraint": "|cat1| * |cat2| in [6, 20]",
        "visual_mapping": {"x": "{cat1}", "stack": "{cat2}", "y": "SUM({measure})"}
    },
    "treemap": {
        "transform": "SELECT {hier1}, {hier2}, SUM({measure}) FROM M GROUP BY {hier1}, {hier2}",
        "column_binding": {"hier1": ["primary"], "hier2": ["secondary"],
                           "measure": ["measure"]},
        "constraint": "|hier1| * |hier2| in [8, 50]",
        "visual_mapping": {"hierarchy": ["{hier1}", "{hier2}"], "size": "SUM({measure})"}
    },

    # ===== Relationship Family =====
    "scatter_plot": {
        "transform": "SELECT {m1}, {m2}, {color} FROM M [WHERE {filter}]",
        "column_binding": {"m1": ["measure"], "m2": ["measure"],
                           "color": ["primary", "orthogonal", None]},
        "constraint": "30 <= |rows| <= 500; m1 != m2",
        "visual_mapping": {"x": "{m1}", "y": "{m2}", "color": "{color}"}
    },
    "bubble_chart": {
        "transform": "SELECT {cat}, AGG({m1}), AGG({m2}), AGG({m3}) FROM M GROUP BY {cat}",
        "column_binding": {"cat": ["primary"], "m1": ["measure"], "m2": ["measure"],
                           "m3": ["measure"]},
        "constraint": "m1 != m2 != m3; |cat| in [5, 30]",
        "visual_mapping": {"x": "AGG({m1})", "y": "AGG({m2})", "size": "AGG({m3})", "label": "{cat}"}
    },
    "heatmap": {
        "transform": "SELECT {row_cat}, {col_cat}, AGG({measure}) FROM M GROUP BY {row_cat}, {col_cat}",
        "column_binding": {"row_cat": ["primary"], "col_cat": ["secondary", "orthogonal"],
                           "measure": ["measure"]},
        "constraint": "|row_cat| * |col_cat| in [6, 100]",
        "visual_mapping": {"row": "{row_cat}", "col": "{col_cat}", "color": "AGG({measure})"}
    },
    "radar_chart": {
        "transform": "SELECT {cat}, AVG({m1}), AVG({m2}), ..., AVG({mk}) FROM M GROUP BY {cat}",
        "column_binding": {"cat": ["primary"], "measures": ["measure"] * 4},  # >= 4 measures
        "constraint": "|cat| in [2, 8]; k >= 4 measures",
        "visual_mapping": {"entity": "{cat}", "axes": ["{m1}", ..., "{mk}"]}
    },

    # ===== Flow Family =====
    "waterfall_chart": {
        "transform": "SELECT {stage}, SUM({measure}) FROM M GROUP BY {stage} ORDER BY {stage_order}",
        "column_binding": {"stage": ["primary", "secondary"], "measure": ["measure"]},
        "constraint": "5 <= |stage| <= 15; stages must have natural ordering",
        "visual_mapping": {"x": "{stage}", "y": "SUM({measure})"}
    },
    "funnel_chart": {
        "transform": "SELECT {stage}, COUNT(*) FROM M GROUP BY {stage} ORDER BY {stage_order}",
        "column_binding": {"stage": ["primary", "secondary"], "measure": ["measure"]},
        "constraint": "3 <= |stage| <= 8; values must be monotonically decreasing",
        "visual_mapping": {"stage": "{stage}", "value": "COUNT(*)"}
    }
}