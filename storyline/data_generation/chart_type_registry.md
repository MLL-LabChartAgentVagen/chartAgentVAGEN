## Chart Type Registry

The meta-configuration layer for the entire system. Each chart type is modeled as a structured spec guiding all downstream phases. We define **6 families, 16 chart types**.

> **Note:** Horizontal bar is not a separate chart type. It is a rendering variant of `bar_chart` (`orientation: "horizontal"`), sharing identical data structure. Orientation is a rendering decision (e.g., auto-switch when labels are long), not a data generation concern.

```python
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
```

**The Registry serves three roles:**

| Direction | Role | Description |
|-----------|------|-------------|
| **Upward (→ LLM)** | Schema constraint | Tells the LLM what column structures are needed |
| **Downward (→ Rule Engine)** | QA capabilities | Tells the QA generator what question types each chart supports |
| **Lateral (→ Coverage)** | Data volume control | Each chart type has a `row_range` for view extraction validation |

---

## Chart Reference Guide

Quick-reference for chart selection. Each entry includes a description, typical scenarios, and a minimal illustrative dataset.

### Family 1 — Comparison

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **bar_chart** | Rectangular bars comparing categorical values — the most fundamental comparison tool. | Comparing revenue across departments; ranking products by sales; survey response counts | `region`: [North, South, East, West] · `revenue`: [420, 310, 530, 280] |
| **grouped_bar_chart** | Side-by-side grouped bars comparing multiple sub-groups across categories. | Product sales by region × quarter; test scores by school × subject; A/B results by segment | `region`: [East, West] · `product`: [A, B, C] · `sales`: grouped values |

### Family 2 — Trend

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **line_chart** | Connected data points over time showing trends, cycles, and inflections. | Monthly revenue over 2 years; daily active users; multi-region infection rates | `month`: [Jan–Jun] · `revenue`: [120, 135, 128, 150, 162, 175] |
| **area_chart** | Filled line chart emphasizing cumulative volume or composition change over time. | Market share by source over time; stacked energy mix by year; traffic by device type | `month`: [Jan–Apr] · `mobile`: [40, 45, 48, 55] · `desktop`: [60, 58, 55, 50] |

### Family 3 — Distribution

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **histogram** | Bins a continuous variable into frequency counts, revealing distribution shape. | Exam score distributions; salary spread; wait-time analysis | `score` values (n=200): bins [50–60, 60–70, …] · `count`: [8, 22, 45, 60, 38, 20, 7] |
| **box_plot** | Five-number summary (min, Q1, median, Q3, max) per group with outlier display. | Salary by job title; wait times across hospitals; defect rates by production line | `dept`: [Eng, Sales, Ops] · `salary` distributions per group |
| **violin_plot** | Density-enhanced box plot showing full distribution shape (bimodal, asymmetric). | Response times across server clusters; income by education level; tempo by music genre | `genre`: [Pop, Jazz, Classical] · `tempo` distributions with density curves |

### Family 4 — Composition

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **pie_chart** | Sector areas showing part-to-whole proportions (best for 3–8 categories). | Market share among competitors; budget breakdown; revenue by product line | `segment`: [A, B, C, D] · `share`: [38, 27, 21, 14] |
| **donut_chart** | Hollow-center pie variant, often used with a central KPI. | Dashboard widgets with total in center; device usage share; portfolio allocation | `asset`: [Stocks, Bonds, Cash] · `pct`: [60, 30, 10] · center label: "$2.4M" |
| **stacked_bar_chart** | Stacked bars showing sub-group contributions to totals across categories. | Revenue by product × quarter; headcount by dept × office; energy output by source × country | `quarter`: [Q1–Q4] · `product`: [A, B, C] stacked per quarter |
| **treemap** | Nested rectangles showing hierarchical composition by area. | Disk usage by folder/type; sales by region → product; stock market cap by sector | `sector`: [Tech, Finance, Health] · `company` sub-tiles · `market_cap` encodes area |

### Family 5 — Relationship

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **scatter_plot** | 2D points showing correlation, clusters, and outliers between two variables. | Ad spend vs. revenue; height vs. weight; price vs. demand | `ad_spend`: [10, 20, 35, 50, 80] · `revenue`: [22, 41, 68, 95, 160] |
| **bubble_chart** | Scatter plot with bubble size encoding a third numerical dimension. | Countries by GDP × life expectancy (bubble = population); products by price × rating (bubble = sales) | `country`: [US, DE, IN] · `gdp`: [21, 4, 3] · `life_exp`: [79, 81, 70] · `pop`: [330M, 83M, 1.4B] |
| **heatmap** | Color-coded matrix revealing row–column interaction patterns. | Correlation matrix; traffic by day × hour; student scores by subject × semester | rows: [Mon–Fri] · cols: [9am–5pm] · `visitors` heatmap values |
| **radar_chart** | Polar chart comparing entities across 4+ normalized dimensions. | Product model profiles; athlete evaluation; supplier scorecard | `entity`: [Model A, Model B] · axes: [Speed, Cost, Durability, Design, Support] |

### Family 6 — Flow / Sequential

| Chart | Description | Typical Scenarios | Example Data |
|-------|-------------|-------------------|--------------|
| **waterfall_chart** | Incremental positive/negative changes from a start to an end value. | Revenue bridge (start → gains/losses → end); P&L breakdown; population change | `step`: [Start, Sales, Returns, Costs, End] · `delta`: [500, +120, −40, −80, 500] |
| **funnel_chart** | Monotonically decreasing stages showing conversion/drop-off rates. | Sales pipeline (leads → closed); e-commerce checkout; recruitment stages | `stage`: [Visits, Views, Cart, Purchase] · `count`: [10000, 4200, 1800, 620] |
