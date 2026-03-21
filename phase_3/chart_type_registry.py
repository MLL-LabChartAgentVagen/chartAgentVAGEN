
CHART_TYPE_REGISTRY = {

    # ===== Family 1: Comparison =====
    "bar_chart": {
        "family": "comparison",
        "row_range": [5, 30],
        "required_columns": {"categorical": {"min": 1, "max": 2}, "numerical": {"min": 1, "max": 5}},
        "optional_features": ["grouping", "stacking", "horizontal_orientation"],
        "data_patterns": ["ranking", "comparison", "part_of_whole"],
        "qa_capabilities": ["value_retrieval", "comparison", "extremum", "sorting"],
    },
    "grouped_bar_chart": {
        "family": "comparison",
        "row_range": [5, 20],
        "required_columns": {"categorical": {"min": 2, "max": 2}, "numerical": {"min": 1, "max": 3}},
        "data_patterns": ["cross_comparison", "groupwise_trend"],
        "qa_capabilities": ["group_comparison", "within_group_ranking", "cross_group_reasoning"],
    },

    # ===== Family 2: Trend =====
    "line_chart": {
        "family": "trend",
        "row_range": [10, 100],
        "required_columns": {"temporal_or_ordinal": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 6}},
        "optional_features": ["multi_series", "annotations"],
        "data_patterns": ["monotonic_trend", "seasonal", "inflection_point", "convergence_divergence"],
        "qa_capabilities": ["trend_identification", "turning_point", "rate_of_change", "forecasting"],
    },
    "area_chart": {
        "family": "trend",
        "row_range": [10, 100],
        "required_columns": {"temporal_or_ordinal": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 5}},
        "optional_features": ["stacking", "percentage_stacking"],
        "data_patterns": ["cumulative_trend", "composition_over_time"],
        "qa_capabilities": ["proportion_change", "cumulative_comparison", "dominance_shift"],
    },

    # ===== Family 3: Distribution =====
    "histogram": {
        "family": "distribution",
        "row_range": [100, 5000],
        "required_columns": {"numerical": {"min": 1, "max": 1}},
        "data_patterns": ["normal", "skewed", "bimodal", "uniform", "heavy_tailed"],
        "qa_capabilities": ["distribution_shape", "central_tendency", "spread", "outlier_detection"],
    },
    "box_plot": {
        "family": "distribution",
        "row_range": [50, 2000],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["different_spreads", "outlier_groups", "skewed_groups"],
        "qa_capabilities": ["median_comparison", "iqr_comparison", "outlier_identification", "spread_comparison"],
    },
    "violin_plot": {
        "family": "distribution",
        "row_range": [100, 3000],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["bimodal_within_group", "asymmetric_distribution"],
        "qa_capabilities": ["distribution_shape_comparison", "modality_identification"],
    },

    # ===== Family 4: Composition =====
    "pie_chart": {
        "family": "composition",
        "row_range": [3, 8],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["dominant_category", "even_split", "long_tail"],
        "qa_capabilities": ["proportion", "comparison", "majority_minority"],
    },
    "donut_chart": {
        "family": "composition",
        "row_range": [3, 8],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["dominant_category", "even_split"],
        "qa_capabilities": ["proportion", "comparison", "aggregation"],
    },
    "stacked_bar_chart": {
        "family": "composition",
        "row_range": [5, 20],
        "required_columns": {"categorical": {"min": 2, "max": 2}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["composition_shift", "growing_shrinking_segments"],
        "qa_capabilities": ["segment_comparison", "total_comparison", "proportion_trend"],
    },
    "treemap": {
        "family": "composition",
        "row_range": [8, 50],
        "required_columns": {"categorical": {"min": 1, "max": 3}, "numerical": {"min": 1, "max": 2}},
        "data_patterns": ["hierarchical_composition", "power_law_distribution"],
        "qa_capabilities": ["relative_size", "hierarchical_comparison", "dominance"],
    },

    # ===== Family 5: Relationship =====
    "scatter_plot": {
        "family": "relationship",
        "row_range": [30, 500],
        "required_columns": {"numerical": {"min": 2, "max": 2}, "categorical": {"min": 0, "max": 1}},
        "data_patterns": ["positive_correlation", "negative_correlation", "clusters", "nonlinear"],
        "qa_capabilities": ["correlation_direction", "outlier_detection", "cluster_identification"],
    },
    "bubble_chart": {
        "family": "relationship",
        "row_range": [15, 100],
        "required_columns": {"numerical": {"min": 3, "max": 3}, "categorical": {"min": 0, "max": 1}},
        "data_patterns": ["multi_dimensional_clusters", "size_correlation"],
        "qa_capabilities": ["three_way_comparison", "outlier_detection", "cluster_reasoning"],
    },
    "heatmap": {
        "family": "relationship",
        "row_range": [5, 30],
        "required_columns": {"row_categorical": {"min": 1}, "col_categorical": {"min": 1}, "numerical": {"min": 1}},
        "data_patterns": ["diagonal_dominance", "block_structure", "gradient"],
        "qa_capabilities": ["cell_value_retrieval", "row_col_comparison", "pattern_identification"],
    },
    "radar_chart": {
        "family": "relationship",
        "row_range": [2, 8],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 4, "max": 10}},
        "data_patterns": ["balanced_profile", "specialized_profile", "dominant_entity"],
        "qa_capabilities": ["dimension_comparison", "profile_similarity", "strength_weakness"],
    },

    # ===== Family 6: Flow/Sequential =====
    "waterfall_chart": {
        "family": "flow",
        "row_range": [5, 15],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["incremental_buildup", "positive_negative_mix"],
        "qa_capabilities": ["cumulative_effect", "largest_contributor", "net_change"],
    },
    "funnel_chart": {
        "family": "flow",
        "row_range": [3, 8],
        "required_columns": {"categorical": {"min": 1, "max": 1}, "numerical": {"min": 1, "max": 1}},
        "data_patterns": ["monotonic_decrease", "bottleneck_stage"],
        "qa_capabilities": ["conversion_rate", "drop_off_identification", "stage_comparison"],
    },
}