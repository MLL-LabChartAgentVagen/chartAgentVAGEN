## PHASE 3: View Amortization & QA Instantiation

> **Core Value:** 1 LLM call → 1 Python script → 1 Master Table → **10–30+ logically coherent tasks** (chart views + multi-hop QA). This phase is entirely deterministic — no LLM calls, no randomness beyond the fixed seed. Every derived chart shares the same ground-truth arithmetic by construction.

---

### 3.1 View Extraction Engine

The Master Table contains surplus information (e.g., 500 rows × 7 columns of individual visit records). The View Extraction Engine systematically projects this into chart-ready data frames using SQL-like operators.

#### 3.1.1 Core Extraction Function

```python
def extract_view(master_table: pd.DataFrame, view_spec: ViewSpec) -> pd.DataFrame:
    """Deterministic SQL-like projection from Master Table to chart-ready view."""
    df = master_table.copy()
    if view_spec.filter:      df = df.query(view_spec.filter)       # σ: row selection
    if view_spec.group_by:    df = df.groupby(view_spec.group_by)   # γ: grouping
                                   .agg(view_spec.agg).reset_index()
    if view_spec.sort_by:     df = df.sort_values(view_spec.sort_by)
    if view_spec.limit:       df = df.head(view_spec.limit)
    return df[view_spec.select_columns]                              # π: column projection
```

#### 3.1.2 View Extraction Rules — Complete Mapping for 16 Chart Types

Each rule specifies the SQL transformation, column role binding (which Schema roles can fill each slot), structural constraints, and visual channel mapping. The engine uses Schema Metadata to enumerate all legal `(chart_type, column_binding)` pairs for a given Master Table.

```python
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
```

#### 3.1.3 Chart Selection Guide — When to Use Which Chart

Structural feasibility (§3.1.2) determines what *can* be rendered; the **Chart Selection Guide** determines what *should* be rendered. The guide encodes practitioner knowledge as a decision matrix, mapping `(analytical_intent, data_shape)` → ranked chart types. The `ViewEnumerator` (§3.1.4) uses this guide to **score and rank** feasible views by suitability.

```python
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
```

> **Design note:** The guide is consulted during view scoring (§3.1.4) but does not hard-filter chart types. A chart type that is structurally feasible but not ranked first by the guide still enters the candidate pool — this preserves diversity across the benchmark while biasing toward analytically sound choices.

#### 3.1.4 Automated View Enumeration

The engine uses Schema Metadata (column roles + orthogonal pairs) to enumerate all feasible views, then **scores** each by suitability using the Chart Selection Guide.

```python
class ViewEnumerator:
    def enumerate(self, schema_metadata: dict,
                  master_table: pd.DataFrame) -> List[ViewSpec]:
        """Enumerate all legal (chart_type, column_binding) pairs, scored by suitability."""
        feasible_views = []
        cols_by_role = self._group_columns_by_role(schema_metadata)

        for chart_type, rule in VIEW_EXTRACTION_RULES.items():
            for binding in self._enumerate_bindings(rule["column_binding"], cols_by_role):
                view_spec = ViewSpec(chart_type=chart_type, binding=binding, rule=rule)
                if self._check_constraint(view_spec, master_table):
                    view_spec.score = self._score_view(view_spec, schema_metadata, master_table)
                    feasible_views.append(view_spec)

        # Return sorted by suitability score (highest first)
        return sorted(feasible_views, key=lambda v: v.score, reverse=True)

    def _score_view(self, view_spec: ViewSpec, schema_metadata: dict,
                    master_table: pd.DataFrame) -> float:
        """Score a feasible view by how well it matches the Chart Selection Guide.

        Scoring dimensions:
          1. Guide match (0–3): Does the chart type appear in a matching guide entry?
             3 = first-ranked, 2 = second-ranked, 1 = third-ranked, 0 = no match.
          2. Data-shape fit (0–2): How well does the actual data satisfy the guide's
             ideal conditions (row count, cardinality, etc.)?
          3. Pattern visibility (0–2): Does this view expose injected patterns?
          4. Family diversity bonus (0–1): Bonus for underrepresented chart families.
        """
        score = 0.0

        # 1. Guide match — check which guide entries this chart type satisfies
        for intent, spec in CHART_SELECTION_GUIDE.items():
            if view_spec.chart_type in spec["ranked_charts"]:
                rank = spec["ranked_charts"].index(view_spec.chart_type)
                score += max(0, 3 - rank)  # 3 for first, 2 for second, 1 for third
                break  # Use highest-scoring match

        # 2. Data-shape fit — reward views near the ideal range
        registry_entry = CHART_TYPE_REGISTRY[view_spec.chart_type]
        row_lo, row_hi = registry_entry["row_range"]
        view_rows = self._estimate_view_rows(view_spec, master_table)
        if row_lo <= view_rows <= row_hi:
            score += 2.0
        elif view_rows >= row_lo * 0.5:
            score += 1.0

        # 3. Pattern visibility — reward views that expose injected patterns
        for pattern in schema_metadata.get("patterns", []):
            if self._pattern_visible(pattern, view_spec):
                score += 0.5  # Each visible pattern adds 0.5, up to 2.0
                if score >= 7.0:  # Cap pattern bonus
                    break

        # 4. Family diversity bonus — slight boost for rare families
        #    (applied externally during final selection, not here)

        return score

    def _group_columns_by_role(self, schema_metadata) -> Dict[str, List[str]]:
        """Group column names by their role for binding lookup."""
        groups = defaultdict(list)
        for col in schema_metadata["columns"]:
            groups[col["role"]].append(col["name"])
        return groups  # e.g., {"primary": ["hospital"], "orthogonal": ["severity"], ...}

    def _enumerate_bindings(self, required_roles: dict,
                            cols_by_role: dict) -> List[Dict]:
        """Generate all valid column-to-slot assignments via Cartesian product."""
        slot_options = {}
        for slot, accepted_roles in required_roles.items():
            candidates = []
            for role in accepted_roles:
                if role is None:
                    candidates.append(None)  # Optional slot
                else:
                    candidates.extend(cols_by_role.get(role, []))
            slot_options[slot] = candidates if candidates else [None]
        # Cartesian product of all slot options
        return [dict(zip(slot_options.keys(), combo))
                for combo in itertools.product(*slot_options.values())]

    def _check_constraint(self, view_spec: ViewSpec,
                          master_table: pd.DataFrame) -> bool:
        """Validate structural constraints (row count, cardinality, etc.)."""
        rule = view_spec.rule
        constraint = rule.get("constraint", "")

        # Check row count constraints
        if "rows" in constraint:
            view_df = extract_view(master_table, view_spec)
            row_count = len(view_df)
            if ">=" in constraint:
                min_rows = int(re.search(r'>= (\d+)', constraint).group(1))
                return row_count >= min_rows
            # ... additional constraint parsing

        # Check cardinality constraints
        if "|cat|" in constraint or "|GROUP BY" in constraint:
            cat_col = view_spec.binding.get("cat") or view_spec.binding.get("cat1")
            if cat_col:
                card = master_table[cat_col].nunique()
                # Parse range from constraint string
                # ...

        return True  # Default pass
```

**Example — Emergency Visits Master Table produces:**

```
ViewEnumerator output (14 feasible views):
  bar_chart        → hospital × AVG(wait_minutes)
  bar_chart        → hospital × AVG(cost)
  bar_chart        → department × SUM(cost)
  grouped_bar      → hospital × severity × AVG(wait_minutes)
  line_chart       → visit_date × hospital × AVG(wait_minutes)
  scatter_plot     → wait_minutes vs satisfaction, color=severity
  scatter_plot     → wait_minutes vs cost, color=hospital
  pie_chart        → department × SUM(cost)
  heatmap          → hospital × department × AVG(satisfaction)
  heatmap          → hospital × severity × AVG(wait_minutes)
  box_plot         → hospital × wait_minutes
  box_plot         → severity × satisfaction
  stacked_bar      → hospital × severity × SUM(cost)
  area_chart       → visit_date × severity × SUM(cost)
  ✗ radar_chart    → needs >= 4 measures (have 3)
  ✗ histogram      → needs >= 100 rows after filter (borderline)
```

---

### 3.2 Multi-Plot Composition (Dashboard Generation)

Single-chart understanding is a solved problem for frontier VLMs. The real evaluation frontier is **cross-chart reasoning** — requiring a model to synthesize information across 2–4 charts sharing the same underlying data.

#### 3.2.1 Composition Distribution

| Plot Count (k) | Target Proportion | Difficulty | Rationale |
|----------------|-------------------|------------|-----------|
| k = 1 | 30% | Easy–Medium | Baseline single-chart tasks |
| k = 2 | 40% | Medium–Hard | Most common real-world pairing |
| k = 3 | 20% | Hard | Requires multi-hop synthesis |
| k = 4 | 10% | Very Hard | Dashboard-level holistic reasoning |

#### 3.2.2 Inter-Chart Relationship Taxonomy

Not all multi-chart combinations are equal. We define 7 relationship types, categorized by whether the DGP needs special handling. Each relationship also specifies **recommended chart types** for each slot to guide the `DashboardComposer`.

| Relationship | Definition | DGP Requirement | View Extraction Strategy | Recommended Chart Types |
|-------------|------------|-----------------|--------------------------|-------------------------|
| **Drill-down** | Same metric at different aggregation granularity. | None | Chart A: `GROUP BY primary`; Chart B: `GROUP BY primary, secondary` | A: `pie_chart`, `bar_chart` (overview); B: `grouped_bar_chart`, `stacked_bar_chart` (detail) |
| **Orthogonal Slice** | Same metric split by independent dimensions. | None (uses `declare_orthogonal` pairs) | Chart A: `GROUP BY primary`; Chart B: `GROUP BY orthogonal` | Both: `bar_chart`, `line_chart` (same type preferred for visual parallelism) |
| **Comparative** | Same schema, different temporal/entity slices. | None | Chart A: `WHERE time < midpoint`; Chart B: `WHERE time >= midpoint` | Both: **same chart type** — `bar_chart`, `line_chart`, `scatter_plot` |
| **Dual-Metric** | Same entities, different measures. | None | Chart A uses `measure_1`; Chart B uses `measure_2` on same `GROUP BY` | Both: **same chart type** — `line_chart`, `bar_chart` (enables direct visual comparison) |
| **Part-Whole** | One chart shows composition, another shows totals. | None | Chart A: `pie(cat, SUM(m))`; Chart B: `bar(cat, SUM(m))` with drill-down | A: `pie_chart`, `donut_chart` (composition); B: `bar_chart`, `stacked_bar_chart` (totals/detail) |
| **Associative** | Two measures with injected correlation — visible across charts. | **Requires `add_correlation()`** | Chart A: `bar(cat, AVG(m1))`; Chart B: `bar(cat, AVG(m2))` | A/B: `bar_chart`, `line_chart` (same category axis); optionally pair with `scatter_plot` (direct correlation) |
| **Causal Chain** | Three+ variables with directional dependency. | **Requires `add_dependency()`** | Chart A: cause; Chart B: mediator; Chart C: effect | A: `bar_chart` (cause); B: `line_chart` (mediator trend); C: `bar_chart`, `scatter_plot` (effect) |

> **Key insight:** 5 of 7 relationship types require **zero** special DGP treatment — they emerge naturally from a well-designed schema with orthogonal dimensions and multiple measures. Only Associative and Causal relationships require explicit `add_correlation()` / `add_dependency()` calls in Phase 2. This is a direct benefit of the atomic-grain design.

> **Chart type selection principle for multi-chart:** For relationships that compare the *same* data across slices (Comparative, Dual-Metric), use **identical chart types** to minimize visual confounds. For relationships that show *different analytical facets* (Drill-down, Part-Whole, Causal Chain), use **complementary chart types** from different families to maximize information diversity.

#### 3.2.3 Composition Patterns

| Pattern | k | Relationship | Recommended Chart Types per Slot | Cross-Chart QA Example |
|---------|---|--------------|----------------------------------|------------------------|
| Same-Type Compare | 2 | Comparative | Both: `bar_chart` or `line_chart` (identical type, different time slice) | "Which hospital improved most between Q1 and Q2?" |
| Overview → Detail | 2 | Drill-down | A: `pie_chart` / `donut_chart`; B: `grouped_bar_chart` / `stacked_bar_chart` | "The department with the largest share — which hospital contributes most?" |
| Orthogonal Contrast | 2 | Orthogonal Slice | Both: `bar_chart` (same type, different dimension axis) | "Does the hospital with the highest cost also treat the most severe cases?" |
| Dual-Metric Profile | 2 | Dual-Metric | Both: `line_chart` or both: `bar_chart` (same type, different measures) | "When wait_time peaked, what happened to satisfaction?" |
| Distribution + Cause | 2 | Associative | A: `histogram` / `box_plot` / `violin_plot`; B: `scatter_plot` / `bubble_chart` | "The right-tail outliers in the histogram — where do they fall on the scatter?" |
| Cause → Mediator → Effect | 3 | Causal Chain | A: `bar_chart`; B: `line_chart`; C: `bar_chart` / `scatter_plot` | "Did increased marketing translate to conversion, or only traffic?" |
| Summary + Dual Detail | 3 | Drill-down + Dual | A: `pie_chart`; B: `line_chart`; C: `scatter_plot` | "The dominant category — is its trend improving, and how correlated are its KPIs?" |
| Full Dashboard | 4 | Mixed | One from each of 4 families (maximize family diversity) | "Across all four charts, which entity has the best overall profile?" |

#### 3.2.4 Dashboard Composition Algorithm

```python
class DashboardComposer:
    """Compose multi-chart dashboards from enumerated single views."""

    COMPOSITION_PATTERNS = {
        "same_type_compare":     {"k": 2, "rel": "comparative"},
        "overview_detail":       {"k": 2, "rel": "drill_down"},
        "orthogonal_contrast":   {"k": 2, "rel": "orthogonal_slice"},
        "dual_metric":           {"k": 2, "rel": "dual_metric"},
        "distribution_cause":    {"k": 2, "rel": "associative"},
        "cause_mediator_effect": {"k": 3, "rel": "causal_chain"},
        "summary_dual_detail":   {"k": 3, "rel": "drill_down+dual_metric"},
        "full_dashboard":        {"k": 4, "rel": "mixed"},
    }

    def compose(self, feasible_views: List[ViewSpec],
                schema_metadata: dict,
                target_k: int) -> List[Dashboard]:
        """Generate dashboard candidates for a given plot count."""
        dashboards = []
        for pattern_name, spec in self.COMPOSITION_PATTERNS.items():
            if spec["k"] != target_k:
                continue
            candidates = self._match_pattern(
                pattern_name, feasible_views, schema_metadata)
            dashboards.extend(candidates)
        return dashboards

    def _match_pattern(self, pattern: str, views: List[ViewSpec],
                       schema: dict) -> List[Dashboard]:
        """Match feasible views to a composition pattern."""
        results = []

        if pattern == "same_type_compare":
            # Find views with temporal dimension; split by time midpoint
            for v in views:
                if self._has_temporal(v):
                    midpoint = self._compute_temporal_midpoint(v)
                    v1 = v.with_filter(f"{v.binding['time']} < '{midpoint}'")
                    v2 = v.with_filter(f"{v.binding['time']} >= '{midpoint}'")
                    results.append(Dashboard(
                        views=[v1, v2], relationship="comparative"))

        elif pattern == "overview_detail":
            # Pair: aggregated overview (pie/bar) + detail (grouped_bar/stacked_bar)
            overviews = [v for v in views
                         if v.chart_type in ("pie_chart", "bar_chart")
                         and v.uses_role("primary")
                         and not v.uses_role("secondary")]
            details = [v for v in views
                       if v.chart_type in ("grouped_bar_chart", "stacked_bar_chart")
                       and v.uses_role("primary") and v.uses_role("secondary")]
            for ov in overviews:
                for det in details:
                    if ov.measure == det.measure:
                        results.append(Dashboard(
                            views=[ov, det], relationship="drill_down"))

        elif pattern == "orthogonal_contrast":
            # Pair: same metric, grouped by primary vs. grouped by orthogonal
            # ONLY use declared orthogonal pairs from schema_metadata
            ortho_pairs = schema.get("orthogonal_pairs", [])
            primary_views = [v for v in views
                             if v.uses_role("primary")
                             and not v.uses_role("orthogonal")]
            ortho_views = [v for v in views
                           if v.uses_role("orthogonal")
                           and not v.uses_role("primary")]
            for pv in primary_views:
                for ov in ortho_views:
                    if pv.measure != ov.measure:
                        continue
                    # Verify this is a declared orthogonal pair
                    pv_cat = pv.binding.get("cat") or pv.binding.get("cat1")
                    ov_cat = ov.binding.get("cat") or ov.binding.get("cat1")
                    if self._is_declared_orthogonal(pv_cat, ov_cat, ortho_pairs):
                        results.append(Dashboard(
                            views=[pv, ov], relationship="orthogonal_slice"))

        elif pattern == "dual_metric":
            # Pair: same GROUP BY key, different measures
            for i, v1 in enumerate(views):
                for v2 in views[i+1:]:
                    if (v1.chart_type == v2.chart_type
                            and v1.group_key == v2.group_key
                            and v1.measure != v2.measure):
                        results.append(Dashboard(
                            views=[v1, v2], relationship="dual_metric"))

        elif pattern == "distribution_cause":
            # Pair: distribution chart + relationship chart sharing a measure
            dist_views = [v for v in views
                          if v.chart_type in ("histogram", "box_plot", "violin_plot")]
            rel_views = [v for v in views
                         if v.chart_type in ("scatter_plot", "bubble_chart")]
            for dv in dist_views:
                for rv in rel_views:
                    if dv.measure in (rv.binding.get("m1"), rv.binding.get("m2")):
                        results.append(Dashboard(
                            views=[dv, rv], relationship="associative"))

        elif pattern == "cause_mediator_effect":
            # Triple: requires dependency chain from schema metadata
            deps = schema.get("dependencies", [])
            corrs = schema.get("correlations", [])
            if deps and corrs:
                chain = self._build_causal_chain(deps, corrs, views)
                if chain:
                    results.append(Dashboard(
                        views=chain, relationship="causal_chain"))

        elif pattern == "full_dashboard":
            # Select 4 views maximizing chart_type family diversity
            if len(views) >= 4:
                selected = self._maximize_type_diversity(views, k=4)
                results.append(Dashboard(
                    views=selected, relationship="mixed"))

        return results

    def _is_declared_orthogonal(self, col_a: str, col_b: str,
                                 ortho_pairs: list) -> bool:
        """Check if (col_a, col_b) is a declared orthogonal pair."""
        for pair in ortho_pairs:
            if set([pair["col_a"], pair["col_b"]]) == set([col_a, col_b]):
                return True
        return False

    def _build_causal_chain(self, deps, corrs, views) -> Optional[List[ViewSpec]]:
        """Find 3 views covering a cause → mediator → effect chain."""
        # Identify cause and effect from dependencies
        for dep in deps:
            target_col = dep["target"]
            # Find source columns mentioned in formula
            source_cols = self._extract_formula_columns(dep["formula"])
            # Find correlations involving source columns
            for corr in corrs:
                mediator_candidates = set([corr["col_a"], corr["col_b"]]) - source_cols
                if mediator_candidates:
                    mediator = mediator_candidates.pop()
                    cause = (source_cols & set([corr["col_a"], corr["col_b"]])).pop()
                    # Find views covering cause, mediator, and target
                    cause_view = self._find_view_for_measure(views, cause)
                    med_view = self._find_view_for_measure(views, mediator)
                    effect_view = self._find_view_for_measure(views, target_col)
                    if cause_view and med_view and effect_view:
                        return [cause_view, med_view, effect_view]
        return None

    def _maximize_type_diversity(self, views: List[ViewSpec],
                                  k: int) -> List[ViewSpec]:
        """Greedily select k views maximizing distinct chart families."""
        selected, used_families = [], set()
        # Priority: one view per family
        for v in views:
            if v.family not in used_families and len(selected) < k:
                selected.append(v)
                used_families.add(v.family)
        # Fill remaining slots
        for v in views:
            if v not in selected and len(selected) < k:
                selected.append(v)
        return selected[:k]
```

---

### 3.3 Rule-Based QA Generation

With arithmetically sound chart views derived from a shared Master Table, QA pairs are generated through two complementary mechanisms: **Template QA** for systematic coverage and **Pattern-Triggered QA** for reasoning depth.

#### 3.3.1 Intra-View QA (Single Chart)

| QA Type | Description | Applicable Charts | Difficulty |
|---------|-------------|-------------------|------------|
| **Value Retrieval** | Read a specific data point. | All | Easy |
| **Extremum** | Identify max/min entity or value. | Bar, Line, Scatter | Easy |
| **Comparison** | Compare two entities or time points. | Bar, Grouped Bar, Line | Medium |
| **Trend** | Describe overall direction or inflection. | Line, Area | Medium |
| **Distribution** | Characterize shape (skew, modality, spread). | Histogram, Box, Violin | Medium |
| **Proportion** | Calculate or compare part-to-whole ratios. | Pie, Donut, Stacked Bar, Treemap | Medium |
| **Correlation** | Assess direction/strength of variable relationship. | Scatter, Bubble, Heatmap | Hard |
| **Anomaly Detection** | Identify outliers or unexpected values. | All (if pattern present) | Hard |

**Template QA Generation:**

```python
INTRA_VIEW_TEMPLATES = {
    "value_retrieval": {
        "template": "What is the {agg} {measure} for {entity}?",
        "answer_fn": lambda view, entity, measure, cat:
            view.loc[view[cat] == entity, measure].values[0],
        "difficulty": "easy",
        "applicable": ["bar_chart", "grouped_bar_chart", "heatmap", "radar_chart"]
    },
    "extremum": {
        "template": "Which {cat} has the {highest/lowest} {measure}?",
        "answer_fn": lambda view, measure, cat, mode:
            view.loc[view[measure].idxmax() if mode == "highest"
                     else view[measure].idxmin(), cat],
        "difficulty": "easy",
        "applicable": ["bar_chart", "line_chart", "scatter_plot"]
    },
    "comparison": {
        "template": "How much {more/less} is {entity_a}'s {measure} compared to {entity_b}?",
        "answer_fn": lambda view, a, b, m, cat:
            abs(view.loc[view[cat] == a, m].values[0]
                - view.loc[view[cat] == b, m].values[0]),
        "difficulty": "medium",
        "applicable": ["bar_chart", "grouped_bar_chart"]
    },
    "trend": {
        "template": "What is the overall trend of {measure} from {start} to {end}?",
        "answer_fn": lambda view, m:
            "increasing" if view[m].iloc[-1] > view[m].iloc[0] else "decreasing",
        "difficulty": "medium",
        "applicable": ["line_chart", "area_chart"]
    },
    "proportion": {
        "template": "What percentage does {entity} contribute to the total {measure}?",
        "answer_fn": lambda view, entity, m, cat:
            view.loc[view[cat] == entity, m].values[0] / view[m].sum() * 100,
        "difficulty": "medium",
        "applicable": ["pie_chart", "donut_chart", "stacked_bar_chart"]
    },
    "distribution_shape": {
        "template": "Is the distribution of {measure} left-skewed, right-skewed, or symmetric?",
        "answer_fn": lambda view, m:
            "right-skewed" if view[m].skew() > 0.5
            else ("left-skewed" if view[m].skew() < -0.5 else "approximately symmetric"),
        "difficulty": "medium",
        "applicable": ["histogram", "violin_plot"]
    },
    "correlation_direction": {
        "template": "What is the relationship between {m1} and {m2}? Positive, negative, or none?",
        "answer_fn": lambda view, m1, m2:
            "positive" if view[m1].corr(view[m2]) > 0.3
            else ("negative" if view[m1].corr(view[m2]) < -0.3 else "no clear relationship"),
        "difficulty": "hard",
        "applicable": ["scatter_plot", "bubble_chart"]
    }
}
```

#### 3.3.2 Inter-View QA (Cross-Chart, Multi-Plot Only)

These questions are the **unique strength** of Table Amortization — only possible because all charts derive from the same Master Table with guaranteed arithmetic consistency.

| QA Type | Description | Required Relationship | Difficulty |
|---------|-------------|----------------------|------------|
| **Ranking Consistency** | Does entity ranking stay the same across metrics? | Dual-Metric, Associative | Hard |
| **Conditional Lookup** | Use one chart to identify an entity, look it up in another. | Any k >= 2 | Hard |
| **Trend Divergence** | Do two entities/metrics trend in the same direction? | Comparative, Dual-Metric | Hard |
| **Drill-down Verification** | Does a detail chart confirm the overview's pattern? | Drill-down | Hard |
| **Orthogonal Reasoning** | Does a pattern hold when sliced by an orthogonal dimension? | Orthogonal Slice | Very Hard |
| **Causal Inference** | Does the cause metric explain the effect? | Causal Chain (k=3) | Very Hard |
| **Holistic Synthesis** | Across all charts, which entity has the best overall profile? | Full Dashboard (k=4) | Very Hard |

```python
INTER_VIEW_TEMPLATES = {
    "ranking_consistency": {
        "template": "The {cat} with the highest {m1} in Chart A — "
                    "what is its rank for {m2} in Chart B?",
        "answer_fn": lambda views: cross_rank_lookup(views[0], views[1]),
        "required_rel": ["dual_metric", "associative"],
        "difficulty": "hard"
    },
    "conditional_lookup": {
        "template": "In Chart A, {cat} has a {measure} of {value}. "
                    "What is this {cat}'s {other_measure} shown in Chart B?",
        "answer_fn": lambda views: conditional_value_transfer(views[0], views[1]),
        "required_rel": ["any"],
        "difficulty": "hard"
    },
    "trend_divergence": {
        "template": "Do {entity_a} and {entity_b} show the same trend direction "
                    "for {measure} across both time periods?",
        "answer_fn": lambda views: compare_trend_directions(views[0], views[1]),
        "required_rel": ["comparative", "dual_metric"],
        "difficulty": "hard"
    },
    "drilldown_verification": {
        "template": "Chart A shows {cat_a} dominates overall. "
                    "In the detailed Chart B, which sub-category drives this dominance?",
        "answer_fn": lambda views: identify_dominant_subcategory(views[0], views[1]),
        "required_rel": ["drill_down"],
        "difficulty": "hard"
    },
    "orthogonal_reasoning": {
        "template": "Chart A shows {measure} by {primary_cat}. "
                    "Chart B shows the same metric by {ortho_cat}. "
                    "Is the top-performing {primary_cat} also dominant "
                    "within each {ortho_cat} group?",
        "answer_fn": lambda views, master:
            verify_orthogonal_dominance(views, master),
        "required_rel": ["orthogonal_slice"],
        "difficulty": "very_hard"
    },
    "causal_inference": {
        "template": "Chart A shows {cause} increased. Chart B shows {mediator} "
                    "also increased. But Chart C shows {effect} decreased. "
                    "What might explain this?",
        "answer_fn": lambda views, schema:
            build_causal_explanation(views, schema["dependencies"]),
        "required_rel": ["causal_chain"],
        "difficulty": "very_hard"
    },
    "holistic_synthesis": {
        "template": "Considering all {k} charts, which {cat} demonstrates "
                    "the best overall performance across all metrics?",
        "answer_fn": lambda views: compute_composite_ranking(views),
        "required_rel": ["mixed"],
        "difficulty": "very_hard"
    }
}
```

#### 3.3.3 Pattern-Triggered QA

The `PatternDetector` scans each extracted view for the statistical patterns injected during Phase 2. When a pattern is detected, it triggers a specialized hard question that tests genuine visual reasoning.

```python
class PatternDetector:
    """Scan view DataFrames for patterns injected in Phase 2."""

    def detect_and_generate_qa(self, view: pd.DataFrame, view_spec: ViewSpec,
                                pattern_metadata: List[dict]) -> List[QAPair]:
        qa_pairs = []
        for pattern in pattern_metadata:
            if self._pattern_visible_in_view(pattern, view_spec):
                qa_pairs.extend(self._generate_pattern_qa(pattern, view, view_spec))
        return qa_pairs

    def _pattern_visible_in_view(self, pattern: dict,
                                  view_spec: ViewSpec) -> bool:
        """Check if the pattern's target column/entity appears in this view."""
        if pattern.get("col") and pattern["col"] not in view_spec.select_columns:
            return False
        if pattern.get("target"):
            return view_spec.filter_compatible(pattern["target"])
        return True

    def _generate_pattern_qa(self, pattern: dict, view: pd.DataFrame,
                              view_spec: ViewSpec) -> List[QAPair]:
        """Generate QA pairs specific to each pattern type."""
        ptype = pattern["type"]

        if ptype == "outlier_entity":
            entity_val = view.query(pattern["target"])[pattern["col"]].mean()
            overall_mean = view[pattern["col"]].mean()
            return [QAPair(
                question=f"Which entity shows an anomalously high "
                         f"{pattern['col']}? By how much does it deviate?",
                answer=f"{self._extract_entity(pattern['target'])}; "
                       f"deviates by {entity_val - overall_mean:.1f}",
                reasoning=f"Visual inspection shows "
                          f"{self._extract_entity(pattern['target'])} is "
                          f"clearly separated. Its value ({entity_val:.1f}) "
                          f"exceeds the group mean ({overall_mean:.1f}).",
                difficulty="hard"
            )]

        elif ptype == "trend_break":
            bp = pattern.get("break_point", pattern.get("params", {}).get("break_point"))
            mag = pattern.get("magnitude", pattern.get("params", {}).get("magnitude", 0))
            return [QAPair(
                question=f"Is there a significant change point in "
                         f"{pattern['col']}? When does it occur?",
                answer=f"Yes, around {bp} with ~{mag*100:.0f}% magnitude.",
                reasoning="The chart shows a visible discontinuity at "
                          "the identified time point.",
                difficulty="hard"
            )]

        elif ptype == "ranking_reversal":
            metrics = pattern.get("metrics",
                                  pattern.get("params", {}).get("metrics", []))
            desc = pattern.get("description",
                               pattern.get("params", {}).get("description", ""))
            m1, m2 = metrics[0], metrics[1]
            return [QAPair(
                question=f"Does the entity ranked highest on {m1} "
                         f"also rank highest on {m2}?",
                answer=f"No — ranking reversal: {desc}.",
                reasoning=f"Comparing charts reveals high {m1} does not "
                          f"imply high {m2}.",
                difficulty="very_hard"
            )]

        elif ptype == "dominance_shift":
            return [QAPair(
                question="Does the leading entity remain the same "
                         "throughout the entire time period?",
                answer="No — a dominance shift occurs mid-period.",
                reasoning="Early time points show one entity leading, "
                          "but a crossover occurs.",
                difficulty="hard"
            )]

        elif ptype == "convergence":
            return [QAPair(
                question="Are the two series converging, diverging, "
                         "or maintaining a constant gap?",
                answer="Converging — the gap narrows over time.",
                reasoning="Visual comparison shows decreasing difference.",
                difficulty="medium"
            )]

        elif ptype == "seasonal_anomaly":
            return [QAPair(
                question=f"Does {pattern['col']} follow a consistent "
                         f"seasonal pattern across all entities?",
                answer=f"Most follow typical seasonality, but "
                       f"{self._extract_entity(pattern['target'])} deviates.",
                reasoning="One entity breaks the expected cyclical pattern.",
                difficulty="hard"
            )]

        return []

    def _extract_entity(self, target_filter: str) -> str:
        """Extract entity name from filter string like \"hospital == 'Xiehe'\"."""
        match = re.search(r"== '([^']+)'", target_filter)
        return match.group(1) if match else target_filter
```

---

### 3.4 Difficulty Classification

Each QA pair is assigned a difficulty level based on the reasoning steps required:

| Difficulty | Definition | Reasoning Steps | Example |
|------------|-----------|-----------------|---------|
| **Easy** | Single-step lookup from one chart. | 1 | "What is hospital A's wait time?" |
| **Medium** | Aggregation, comparison, or derivation within one chart. | 2 | "How much more does A cost than B?" |
| **Hard** | Multi-step reasoning, cross-chart lookup, or pattern detection. | 3–4 | "The hospital with longest wait — what's its satisfaction rank?" |
| **Very Hard** | 3–4 chart synthesis, causal reasoning, or holistic judgment. | 5+ | "Across all charts, which hospital has the best composite profile?" |

**Target difficulty distribution per Master Table:**

| Difficulty | Proportion |
|------------|-----------|
| Easy | 25% |
| Medium | 35% |
| Hard | 25% |
| Very Hard | 15% |

---

### 3.5 End-to-End Summary

```
Input: Master Table (N rows × C columns) + Schema Metadata

Step 1: ViewEnumerator.enumerate()
        → All feasible (chart_type, column_binding) pairs

Step 2: DashboardComposer.compose()
        → Single views (k=1) + multi-chart dashboards (k=2,3,4)

Step 3: For each view/dashboard:
        a) extract_view() → chart-ready DataFrame
        b) Render chart image (matplotlib/plotly)
        c) Generate Intra-View QA via templates
        d) Generate Inter-View QA via cross-chart templates (k >= 2)
        e) PatternDetector → Pattern-Triggered QA

Step 4: Difficulty assignment + proportion balancing

Output per Master Table: 10–30+ {chart_image(s), question, answer,
                                  reasoning_chain, difficulty}
```
