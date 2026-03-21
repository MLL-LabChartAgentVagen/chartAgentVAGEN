CHART_SELECTION_GUIDE = {
    # Each entry: (analytical_intent, data_shape_predicate) → ranked chart types
    # The ranker matches the Master Table's schema to these predicates
    # and boosts matching chart types during view scoring.

    # --- Comparison ---
    "compare_magnitudes": {
        "description": "Compare a single metric across categorical entities",
        "data_shape": {"categorical": 1, "numerical": 1},
        "ranked_charts": ["bar_chart", "pie_chart"],
        "rationale": "Bar is the default for magnitude comparison; pie only when "
                     "part-of-whole is the primary question and |cat| ≤ 8"
    },
    "cross_group_comparison": {
        "description": "Compare a metric across two categorical dimensions",
        "data_shape": {"categorical": 2, "numerical": 1},
        "ranked_charts": ["grouped_bar_chart", "stacked_bar_chart", "heatmap"],
        "rationale": "Grouped bar for side-by-side comparison; stacked bar when "
                     "composition is also relevant; heatmap for dense matrices"
    },

    # --- Trend ---
    "show_trend": {
        "description": "Show how a metric evolves over an ordered dimension",
        "data_shape": {"temporal": 1, "numerical": "1+"},
        "ranked_charts": ["line_chart", "area_chart"],
        "rationale": "Line for precise trend reading; area when cumulative volume "
                     "or composition change over time is the emphasis"
    },

    # --- Distribution ---
    "understand_distribution": {
        "description": "Assess the shape of a single continuous variable",
        "data_shape": {"numerical": 1, "min_rows": 100},
        "ranked_charts": ["histogram", "violin_plot", "box_plot"],
        "rationale": "Histogram for shape; violin when comparing across groups; "
                     "box when summary stats suffice"
    },
    "compare_distributions": {
        "description": "Compare distribution of a measure across categorical groups",
        "data_shape": {"categorical": 1, "numerical": 1, "min_rows_per_group": 15},
        "ranked_charts": ["box_plot", "violin_plot"],
        "rationale": "Box for quick median/IQR compare; violin when modality matters"
    },

    # --- Composition ---
    "show_part_of_whole": {
        "description": "Show proportional contribution of categories to a total",
        "data_shape": {"categorical": 1, "numerical": 1, "max_cats": 8},
        "ranked_charts": ["pie_chart", "donut_chart", "treemap"],
        "rationale": "Pie/donut for ≤8 categories; treemap when hierarchical or >8"
    },
    "show_composition_over_categories": {
        "description": "Show how sub-groups contribute to totals across a primary dimension",
        "data_shape": {"categorical": 2, "numerical": 1},
        "ranked_charts": ["stacked_bar_chart", "treemap"],
        "rationale": "Stacked bar when both total and segments matter; treemap for hierarchy"
    },
    "show_hierarchical_composition": {
        "description": "Show nested composition with 2-3 levels of categorical hierarchy",
        "data_shape": {"categorical": "2+", "numerical": 1, "has_hierarchy": True},
        "ranked_charts": ["treemap", "stacked_bar_chart"],
        "rationale": "Treemap excels at multi-level hierarchies; stacked bar for 2-level"
    },

    # --- Relationship ---
    "assess_correlation": {
        "description": "Assess relationship between two continuous variables",
        "data_shape": {"numerical": 2, "min_rows": 30},
        "ranked_charts": ["scatter_plot", "bubble_chart"],
        "rationale": "Scatter for 2D; bubble when a third dimension adds value"
    },
    "multi_dimensional_profile": {
        "description": "Compare entities across 4+ metrics simultaneously",
        "data_shape": {"categorical": 1, "numerical": "4+"},
        "ranked_charts": ["radar_chart"],
        "rationale": "Radar is uniquely suited for multi-axis profiling (4–8 axes)"
    },
    "matrix_interaction": {
        "description": "Reveal interaction intensity between two categorical dimensions",
        "data_shape": {"categorical": 2, "numerical": 1},
        "ranked_charts": ["heatmap"],
        "rationale": "Heatmap is the canonical choice for row × column intensity patterns"
    },

    # --- Flow ---
    "show_incremental_changes": {
        "description": "Show step-by-step increases and decreases to a running total",
        "data_shape": {"ordered_stages": True, "numerical": 1, "has_pos_neg": True},
        "ranked_charts": ["waterfall_chart"],
        "rationale": "Waterfall is the only chart type designed for incremental buildup"
    },
    "show_conversion_pipeline": {
        "description": "Show monotonically decreasing stages with drop-off rates",
        "data_shape": {"ordered_stages": True, "numerical": 1, "monotonic_decrease": True},
        "ranked_charts": ["funnel_chart"],
        "rationale": "Funnel is purpose-built for conversion/pipeline visualization"
    }
}