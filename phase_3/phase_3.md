## PHASE 3: View Extraction & Question Generation

> **Core Value:** 1 Master Table → **10–30+ logically coherent tasks** (chart views + multi-hop QA). This phase is entirely deterministic. Every derived chart shares the same ground-truth arithmetic by construction.

> **Design Principle:** Questions drive everything. A view exists only if operators can query it. A multi-chart pair exists only if a bridge operator can connect them. One compatibility table replaces scoring heuristics, chart selection guides, and template systems.

---

### 3.1 View Extraction

The Master Table contains surplus information (e.g., 500 rows × 7 columns). The View Extraction Engine projects it into chart-ready DataFrames using SQL-like operators.

#### 3.1.1 Core Extraction Function

```python
def extract_view(master_table: pd.DataFrame, view_spec: ViewSpec) -> pd.DataFrame:
    """Deterministic projection from Master Table to chart-ready view."""
    df = master_table.copy()
    if view_spec.filter:    df = df.query(view_spec.filter)
    if view_spec.group_by:  df = df.groupby(view_spec.group_by).agg(view_spec.agg).reset_index()
    if view_spec.sort_by:   df = df.sort_values(view_spec.sort_by)
    if view_spec.limit:     df = df.head(view_spec.limit)
    return df[view_spec.select_columns]
```

#### 3.1.2 View Extraction Rules

Each rule specifies the SQL transformation, column role binding, structural constraints, and visual channel mapping. The engine uses Schema Metadata to enumerate all legal `(chart_type, column_binding)` pairs.

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
        "column_binding": {"cat": ["primary"], "measures": ["measure"] * 4},
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

#### 3.1.3 View Enumeration

The engine uses Schema Metadata to enumerate all feasible views. No scoring — operator compatibility (§3.2) is the only filter.

```python
def enumerate_views(master_table, schema):
    views = []
    cols_by_role = group_columns_by_role(schema)
    for chart_type, rule in VIEW_EXTRACTION_RULES.items():
        for binding in enumerate_bindings(rule["column_binding"], cols_by_role):
            if check_constraint(binding, master_table, rule):
                views.append(ViewSpec(chart_type, binding))
    return cap_per_family(views, max_per_family=3)  # prevent combinatorial explosion
```

---

### 3.2 Operator Algebra for Question Generation

A question is not a template — it is a **typed pipeline** of operators. This formalism replaces all template-based QA with one composable system.

#### 3.2.1 Types and Operators

Two types: **V** (View — a table) and **S** (Scalar — a single value). 16 operators connect them:

**Set operators** transform views (V → V):

| Operator | What it does | Example |
|----------|-------------|---------|
| Filter | Keep rows matching a condition | Keep only rows where hospital = "Xiehe" |
| Sort | Order rows by a column | Sort hospitals by cost descending |
| Limit | Keep top-k rows | Keep the top 3 hospitals |
| GroupBy | Aggregate rows by category | Group by department, compute AVG(cost) |

**Scalar operators** reduce a view to one value (V → S):

| Operator | What it does | Example |
|----------|-------------|---------|
| Max, Min, Avg, Sum, Count | Aggregate a column | What is the average cost? → 4500 |
| ArgMax, ArgMin | Entity with extreme value | Which hospital has the highest cost? → "Xiehe" |
| ValueAt | Read from a single-row view | (After Filter to one row) What is the cost? → 6200 |

**Scalar combinators** merge two scalars (S, S → S):

| Operator | What it does | Example |
|----------|-------------|---------|
| Diff | Subtract two scalars | cost_A - cost_B = 1200 |
| Ratio | Divide two scalars | cost_A / avg_cost = 1.38 |

**View combinators** merge two views (V, V → V):

| Operator | What it does | Example |
|----------|-------------|---------|
| Union | Append all rows from both views | Top-3 hospitals ∪ Bottom-2 hospitals |
| Intersect | Keep only rows present in both views | Top-3 by cost ∩ Top-3 by wait |
| Difference | Keep rows in V_a that are not in V_b | Top-3 by cost − Top-3 by wait |

**Bridge operators** connect two charts (see §3.2.3 for details):

| Operator | Signature | What it does |
|----------|-----------|-------------|
| EntityTransfer | (S, V) → V | Use an entity name from chart A to filter chart B |
| ValueTransfer | (S, V) → V | Use a numeric value from chart A as a threshold for chart B |
| TrendCompare | (V, V) → S | Compare the temporal trend direction of two views |
| RankCompare | (V, V) → S | Compare the entity rankings between two views |

#### 3.2.2 A Question = A Typed Pipeline

Every question is a chain starting with V and ending with S. Each operator's output type must match the next operator's input type.

```
Sequential:     V  →  [V→V ops]  →  [V→S op]  →  S (done)
Forked:         V ──→ [ops_a] → V_a ──┐
                                       ├── Combinator → V → [ops] → S
                V ──→ [ops_b] → V_b ──┘
Nested:         Op_outer(V, Op_inner(V) → S)  →  V → [ops] → S
Multi-chart:    V_a → [ops] → S  →  Bridge(S, V_b)  →  V  →  [ops]  →  S (done)
```

**Single-chart examples:**

| #Ops | Question | Pipeline |
|------|----------|----------|
| 1 | "Which hospital has the highest cost?" | V → **ArgMax** → S |
| 2 | "Total cost in region A?" | V → **Filter** → V → **Sum** → S |
| 3 | "Average cost of top-3?" | V → **Sort** → V → **Limit** → V → **Avg** → S |
| 5 (forked) | "Average cost of the top-3 and bottom-2 hospitals?" | V→Sort(desc)→Limit(3)→V_a ; V→Sort(asc)→Limit(2)→V_b ; **Union**(V_a,V_b)→V→**Avg**→S |
| 3 (nested) | "Which hospitals have above-average cost?" | V → **Filter**(cost > **Avg**(V))→ V → **Count** → S |

**Multi-chart examples:**

| #Ops | Question | Pipeline |
|------|----------|----------|
| 3 | "Most expensive hospital (chart A) — its wait time (chart B)?" | V_a → ArgMax → **S** → EntityTransfer(V_b) → **V** → ValueAt → S |
| 4 | "3rd-highest cost (A) — how many in B are below it?" | V_a → Sort → Limit(3) → V → Max → **S** → ValueTransfer(<, V_b) → **V** → Count → S |
| 5 | "Top-3 by cost (A) — same ranking in B?" | V_a → Sort → Limit → **V** → RankCompare(V_b → Sort → Limit) → **S** |
| 7 | "Largest dept (A) → peak month (B) → who in C beats it?" | V_a → ArgMax → **S** → EntityTransfer(V_b) → **V** → Sort → Limit(1) → Max → **S** → ValueTransfer(>, V_c) → **V** → Count → S |

The 7-op example chains **two bridges**: the first bridge (EntityTransfer) produces V, the pipeline continues with more ops until a second scalar is produced, then the second bridge (ValueTransfer) connects to a third chart. Any number of bridges can be chained as long as types match.

#### 3.2.3 Bridge Operators — Connecting Charts

Bridge operators are the mechanism for multi-chart reasoning. They take information extracted from one chart and use it to query another chart. There are four bridge operators, each serving a different purpose:

**EntityTransfer (S, V) → V** — "Look up this entity in the other chart."

The scalar S is an entity name (e.g., "Xiehe Hospital" from ArgMax on chart A). EntityTransfer filters chart B to rows matching that entity. This requires both charts to share a categorical column.

```
Example: "The hospital with the highest wait time — what is its cost?"
  Chart A (bar: hospital × wait):  V_a → ArgMax → S = "Xiehe"
  Bridge:                          EntityTransfer(S="Xiehe", V_b) → V = [row where hospital="Xiehe" in chart B]
  Chart B (bar: hospital × cost):  V → ValueAt → S = 6200
```

**ValueTransfer (S, V) → V** — "Use this number as a filter threshold on the other chart."

The scalar S is a numeric value (e.g., cost = 5000 from chart A). ValueTransfer filters chart B by a comparison operator (>, <, =) using S as the threshold. This requires both charts to have comparable numeric columns.

```
Example: "How many departments have a cost below the highest hospital's cost?"
  Chart A (bar: hospital × cost):  V_a → Max → S = 5000
  Bridge:                          ValueTransfer(S=5000, op=<, V_b) → V = [rows in chart B where cost < 5000]
  Chart B (bar: dept × cost):      V → Count → S = 2
```

**TrendCompare (V, V) → S** — "Do these two views show the same trend?"

Takes two temporal views and compares their trend directions. Both views must have a time axis (line or area charts). Returns a qualitative comparison (e.g., "both increasing", "diverging").

```
Example: "Do wait times and costs trend in the same direction over the year?"
  Chart A (line: month × wait):    V_a (temporal view of wait times)
  Chart B (line: month × cost):    V_b (temporal view of costs)
  Bridge:                          TrendCompare(V_a, V_b) → S = "both increasing"
```

**RankCompare (V, V) → S** — "Do these two views rank entities the same way?"

Takes two views with ranked categorical entities and compares their orderings. Both views must have named entities (bar, pie, etc.). Returns overlap or rank delta.

```
Example: "Do the top-3 hospitals by cost also rank in the top-3 by satisfaction?"
  Chart A (bar: hospital × cost):         V_a → Sort → Limit(3) → V (top-3 by cost)
  Chart B (bar: hospital × satisfaction):  V_b → Sort → Limit(3) → V (top-3 by satisfaction)
  Bridge:                                  RankCompare(V_a, V_b) → S = "2 of 3 overlap"
```

#### 3.2.4 Operator–Chart Compatibility

**This is the key insight that unifies view extraction and question generation.** Not every operator makes sense on every chart type. ArgMax ("which bar is tallest?") makes sense on a bar chart but not on a histogram. TrendCompare makes sense on line charts but not on pie charts.

This compatibility determines which views are useful and which multi-chart pairs are valid:
- A view is useful iff at least one non-trivial operator is compatible with its chart type.
- A multi-chart pair is useful iff at least one bridge operator is compatible with both chart types.

| Operator | Compatible Chart Types | Why |
|----------|----------------------|-----|
| ArgMax, ArgMin | bar, grouped_bar, pie, donut, stacked_bar, bubble, radar, waterfall, funnel, heatmap | Needs named entities with comparable values |
| Max, Min, Avg, Sum | bar, grouped_bar, pie, donut, stacked_bar, line, area, scatter, bubble, heatmap, radar | Needs a numeric column to aggregate |
| Count | All | Always valid — count rows |
| ValueAt | All | Read a specific cell |
| Filter | All | Row selection always valid |
| Sort | bar, grouped_bar, stacked_bar, scatter, bubble, heatmap, radar | Needs discrete rows that can be reordered |
| Limit | bar, grouped_bar, stacked_bar, scatter, bubble | Needs enough rows to truncate |
| GroupBy | scatter, bubble | Only when view has raw (ungrouped) rows |
| Diff, Ratio | N/A (S,S → S) | Operates on scalars, chart-independent |
| EntityTransfer | Any → Any with shared categorical column | Needs a named entity to look up |
| ValueTransfer | Any → Any with comparable numeric column | Needs a numeric threshold to filter by |
| TrendCompare | line, area (both sides must be temporal) | Needs temporal axis |
| RankCompare | bar, grouped_bar, pie, stacked_bar (both sides) | Needs ranked categorical entities |

---

### 3.3 Question Generation Pipeline

The abstract pipeline notation from §3.2.2 is realized by two concrete classes in `pipeline.py` — **`PipelineNode`** and **`Pipeline`** — and assembled by a composer factory that builds all four pipeline shapes.

#### 3.3.1 PipelineNode — The Operator Tree

A `PipelineNode` is a single node in a tree. It wraps one `Operator` and holds a list of child `PipelineNode` inputs:

| Inputs list | Meaning | Example |
|-------------|---------|---------|
| `[]` (empty) | Leaf — operator runs on the raw base view | `PipelineNode(Filter(...), inputs=[])` |
| `[n]` (single) | Unary/sequential — chain of one-after-another ops | `PipelineNode(Avg(...), inputs=[sort_node])` |
| `[a, b]` (two+) | Binary/fork — combinator merging two branches | `PipelineNode(Union(), inputs=[branch_a, branch_b])` |

This representation unifies all four pipeline shapes from §3.2.2 into a single recursive tree structure. Building a sequential chain simply produces a linked list of nodes; building a forked pipeline produces a tree with branching.

**Core methods:**

| Method | What it does |
|--------|-------------|
| `execute(view)` | Recursively executes the tree bottom-up. Leaf nodes call `operator.execute(view)`. Unary inner nodes pass their child's result. Binary nodes pass all child results as positional args. |
| `render_question(**ctx)` | Recursively composes NL fragments inside-out — children render first, then the parent fragment is appended. |
| `display(indent)` | Pretty-prints the tree for debugging with indentation showing depth. |
| `type_check()` | Recursively verifies every child→parent connection is type-compatible (`V→V`, `V→S`, etc.). |
| `depth` / `op_count` | Recursive properties — max tree depth and total operator count. |
| `to_dict()` | Serializes the tree to a JSON-safe dict (no DataFrames). |

**Execution walkthrough — sequential:** *"What is the average cost of the top-3 hospitals in the East?"*

```
Tree:          Avg("cost")                    ← root, V→S
                 └── Limit(3)                 ← V→V
                       └── Sort("cost", desc) ← V→V
                             └── Filter(...)  ← leaf, V→V

execute(view):
  1. Avg  → recurses → Limit → recurses → Sort → recurses → Filter
  2. Filter.execute(view)        → OperatorResult(V, east_rows_df)
  3. Sort.execute(east_rows_df)  → OperatorResult(V, sorted_df)
  4. Limit.execute(sorted_df)    → OperatorResult(V, top_3_df)
  5. Avg.execute(top_3_df)       → OperatorResult(S, 5200.0)
```

Every node receives a **DataFrame** from its child, transforms it, and passes it up. The base view is touched once at the leaf.

**Execution walkthrough — forked:** *"Average cost of the top-3 and bottom-2 hospitals?"*

```
Tree:          Avg("cost")                  ← root, V→S
                 └── Union()                ← binary, (V,V)→V
                       ├── Limit(3)         ← branch a
                       │     └── Sort(desc) ← leaf a
                       └── Limit(2)         ← branch b
                             └── Sort(asc)  ← leaf b

execute(view):
  1. Union.execute calls both branches independently
  2. Branch a: Sort(desc)(view) → Limit(3) → top-3 rows
  3. Branch b: Sort(asc)(view) → Limit(2) → bottom-2 rows
  4. Union merges both into a single DataFrame
  5. Avg reduces to a scalar
```

**Execution walkthrough — nested:** *"How many hospitals have above-average cost?"*

```
Tree:          Count("cost")                          ← root, V→S
                 └── Filter("cost", ">", threshold)   ← V→V (parameterized)
                       └── Avg("cost")                ← leaf, V→S (inner sub-pipeline)

execute(view):
  1. Count → recurses → Filter → recurses → Avg
  2. Avg.execute(view)             → OperatorResult(S, 4500.0)  ← scalar, not DataFrame!
  3. Filter receives child_results[0].value = 4500.0
     Filter uses 4500.0 as threshold, filters base view to rows where cost > 4500
                                   → OperatorResult(V, above_avg_df)
  4. Count.execute(above_avg_df)   → OperatorResult(S, 2)
```

**Why the tree looks "upside-down."** In §3.2.2 we wrote pipelines left-to-right in logical order — the way a human would describe the steps:

```
Original notation:   V → Filter → Sort → Limit → Avg → S
                     ↑ first step               last step ↑
```

The `PipelineNode` tree reverses this visualization. Because execution is recursive, the **root** node is the *last* operator to run (it waits for its children), and the **leaf** is the *first* (it touches the raw view). So the same pipeline renders top-down as:

```
Tree (root = last op):   Avg           ← executes last, returns S
                           └── Limit   ← executes third
                                 └── Sort    ← executes second
                                       └── Filter  ← executes first (leaf)
```

This is an artefact of the recursive data structure, not a change in semantics. The logical order of operations is unchanged — Filter still runs before Sort, Sort before Limit, Limit before Avg. The tree simply shows **containment** (who calls whom) rather than **temporal sequence**.

**Sequential vs. nested — same recursion, different composition.** The `execute()` code path is identical in both cases — it always recurses into children, collects results, and passes them to the parent operator. The difference is entirely in how operators are **composed into the tree**:

| | Sequential | Nested |
|---|---|---|
| **Tree shape** | Linear linked list | Branch at the nesting point |
| **What flows between nodes** | DataFrame → DataFrame → … → Scalar | DataFrame → **Scalar** → DataFrame → Scalar |
| **Base view touched by** | Leaf only | Leaf (inner scalar) **and** outer op (re-accesses view) |
| **Key idea** | Each op transforms the previous result | Inner op produces a **reference value**; outer op uses it as a dynamic parameter |

Whether a pipeline is sequential or nested is not a property of the runtime — it is a **composition problem determined by operator output types**. In a sequential pipeline, every intermediate operator outputs **V** (a DataFrame), so the chain flows V→V→V→…→S in a straight line. A nested pipeline arises when an intermediate operator outputs **S** (a scalar) and that scalar must be consumed by a downstream operator that still expects to produce a view. The inner operator's S-typed output cannot feed directly into a V→V set operator, so it is instead absorbed as a *parameter* — a filter threshold, a comparison target, a ratio denominator — by an outer operator that re-accesses the base view. The tree branches at exactly this point: one child computes the reference scalar, and the parent uses it to parameterize its own view transformation. The composer decides between sequential and nested composition by inspecting whether the sampled operator sequence requires an intermediate scalar to flow back into a view-producing context.

#### 3.3.2 Pipeline — Wrapper with Metadata

`Pipeline` is a thin dataclass wrapper around the root `PipelineNode`. It adds metadata and delegates all behavior to the root:

```python
@dataclass
class Pipeline:
    root: PipelineNode              # root of the operator tree
    view_specs: List[ViewSpec]      # which view(s) this pipeline was built for
    pipeline_type: str              # "sequential" | "forked" | "nested" | "multi_chart"
    relationship: Optional[str]     # inter-chart relationship (multi-chart only)
```

All core methods (`execute`, `render_question`, `display`, `type_check`) are one-line delegates to `self.root`. Pipeline also provides:

- **`op_count` / `depth`** — delegates to root's recursive properties (these determine difficulty per §3.6).
- **`to_dict()` / `to_json()`** — serializes the full pipeline including metadata and the operator tree.

The `pipeline_type` field classifies the tree's shape for logging, display, and downstream analysis.

#### 3.3.3 Pipeline Composer

TBD

---

### 3.4 Unified Generation Algorithm

View enumeration, multi-chart composition, and QA generation are fused into **one loop** with operator compatibility as the single filter.

#### 3.4.1 Inter-Chart Relationships
Two views can be paired only if they have a semantic relationship. `candidate_pairs()` yields all `(va, vb)` from enumerated views, plus **split pairs**: for each temporal view, split by time midpoint → `(v_early, v_late)` to produce Comparative pairs.

| Relationship | Predicate | Example |
|---|---|---|
| **Drill-down** | Same measure, `va.group_keys ⊂ vb.group_keys` | bar(hospital × cost) → grouped_bar(hospital × dept × cost) |
| **Orthogonal Slice** | Same measure, group keys declared orthogonal | bar(hospital × cost) vs bar(severity × cost) |
| **Comparative** | Same chart type & measure, different time filter | bar(hospital × cost, Q1) vs bar(hospital × cost, Q2) |
| **Dual-Metric** | Same group key, different measures | bar(hospital × cost) vs bar(hospital × wait) |
| **Part-Whole** | Composition chart + totals chart, same data | pie(dept × cost) → bar(dept × cost) |
| **Associative** | Measures linked by `add_correlation()` in schema | bar(hospital × cost) vs bar(hospital × satisfaction) |
| **Causal Chain** | `va.measure → vb.measure` in dependency DAG | bar(marketing) → line(traffic) → bar(conversion) |

#### 3.4.2 Bridge Selection

A pair is kept **if and only if** the relationship allows a bridge AND both chart types support it. This single check fuses what used to be separate "composition" and "QA feasibility" stages.

```python
def get_valid_bridges(relationship, chart_type_a, chart_type_b):
    """Return bridge operators valid for this relationship AND both chart types."""
    valid = []
    for bridge in RELATIONSHIP_BRIDGES[relationship]:
        if (chart_type_a in bridge.compatible_source_charts
                and chart_type_b in bridge.compatible_target_charts):
            valid.append(bridge)
    return valid  # empty → this pair is infeasible, skip it
```

| Relationship | Valid Bridges |
|---|---|
| Drill-down | EntityTransfer, ValueTransfer |
| Orthogonal Slice | EntityTransfer, RankCompare |
| Comparative | ValueTransfer, TrendCompare |
| Dual-Metric | EntityTransfer, RankCompare, ValueTransfer |
| Part-Whole | EntityTransfer, ValueTransfer |
| Associative | RankCompare, EntityTransfer |
| Causal Chain | EntityTransfer, ValueTransfer |

#### 3.4.3 The Algorithm

```python
def generate_tasks(master_table, schema):
    """One loop: enumerate → check operator compatibility → sample questions."""

    # Step 1: Enumerate all feasible views
    all_views = enumerate_views(master_table, schema)

    # Step 2: Single-chart QA — check operator compatibility, sample pipelines
    single_tasks = []
    for view in all_views:
        compatible_ops = get_compatible_ops(view.chart_type)
        if len(compatible_ops) >= 2:
            single_tasks.extend(
                sample_pipelines(view, compatible_ops, target_ops=[1, 2, 3]))

    # Step 3: Multi-chart QA — check relationship + bridge validity
    multi_tasks = []
    for (va, vb) in candidate_pairs(all_views, schema):
        rel = detect_relationship(va, vb, schema)
        if rel is None:
            continue
        valid_bridges = get_valid_bridges(rel, va.chart_type, vb.chart_type)
        if not valid_bridges:
            continue  # relationship exists but no bridge fits → skip
        multi_tasks.extend(
            sample_cross_pipelines(va, vb, valid_bridges, target_ops=[3, 4, 5, 6]))

    # Step 4: k=3,4 — extend valid pairs by chaining additional views
    for pair in multi_tasks:
        for vc in all_views:
            if vc not in pair.views:
                rel_c = detect_relationship(pair.views[-1], vc, schema)
                if rel_c and get_valid_bridges(rel_c, pair.views[-1].chart_type, vc.chart_type):
                    multi_tasks.append(extend_pair(pair, vc, rel_c))

    return single_tasks + multi_tasks
```

#### 3.4.4 Pipeline Sampling

```python
def sample_question(views, relationship, target_ops):
    """Build a typed pipeline left-to-right."""
    pipe = views[0]                # start: type = V
    cur_type = "V"
    ops_left = target_ops
    view_idx = 1

    while ops_left > 0:
        if cur_type == "V":
            # Option A: apply a Set op (V → V), keep going
            # Option B: apply a Scalar op (V → S)
            # Option C: apply a bridge like RankCompare/TrendCompare (V,V) → S
            op = sample_op(cur_type, ops_left, views[view_idx - 1].chart_type,
                           can_bridge=(view_idx < len(views)))
        elif cur_type == "S":
            if view_idx < len(views) and ops_left > 1:
                # Bridge to next view: EntityTransfer/ValueTransfer (S,V) → V
                op = sample_bridge(cur_type, relationship)
                op.set_side_input(preprocess(views[view_idx]))
                view_idx += 1
            else:
                break  # pipeline complete

        pipe = op(pipe)
        cur_type = op.output_type
        ops_left -= 1

    return pipe  # final type must be S


def sample_op(cur_type, budget, chart_type, can_bridge):
    """Pick a random operator compatible with current type AND chart type."""
    candidates = [op for op in ALL_OPS
                  if op.input_type == cur_type
                  and chart_type in OPERATOR_CHART_COMPAT[op.name]  # the compatibility check
                  and (not op.is_bridge or can_bridge)]
    if budget == 1:
        candidates = [op for op in candidates if op.output_type == "S"]
    return random.choice(candidates)
```

---

### 3.5 Pattern-Seeded QA

Patterns injected in Phase 2 pre-fix certain operators in the pipeline. The remaining operators are randomly sampled. No special `PatternDetector` class is needed — patterns simply constrain which operators appear in the pipeline. The compatibility table ensures the fixed operators are valid for the view's chart type.

| Pattern | Fixed Operators | Example Question |
|---------|----------------|-----------------|
| outlier | Filter(target) + Ratio | "How much does the outlier entity deviate from the group mean?" |
| trend_break | Filter(time > breakpoint) + ValueAt | "Is there a change point? When does it occur?" |
| ranking_reversal | RankCompare | "Does the entity ranked highest on metric A also rank highest on B?" |
| dominance_shift | Filter(early) + ArgMax vs Filter(late) + ArgMax | "Does the leading entity remain the same throughout?" |
| convergence | TrendCompare | "Are the two series converging or diverging?" |

---

### 3.6 Difficulty = #Ops

Difficulty is determined by a single, objective metric: the number of operators in the pipeline. No manual labeling, no heuristic scoring.

| #Ops | Difficulty | Typical Shape |
|------|-----------|---------------|
| 1–2 | Easy | Single-chart: direct lookup |
| 3–4 | Medium | Single-chart chain or 2-chart with 1 bridge |
| 5–6 | Hard | Multi-chart with ops on both sides of the bridge |
| 7+ | Very Hard | 3+ charts with chained bridges |

---

### 3.7 Walkthrough Example

**Setup:** Master Table with 500 rows, 7 columns. Three hospitals, three departments, 12 months of visits.

```
Columns: hospital(P), dept(S), severity(O), visit_date(T), wait_min(M), cost(M), satisfaction(M)
P = primary, S = secondary, O = orthogonal, T = temporal, M = measure
```

**Step 1 — Enumerate views:** Match column roles to chart type rules.

```
V1: bar_chart(hospital × AVG(wait))         — rule: (cat:P/S, measure:M), |cat|∈[3,30] ✓
V2: bar_chart(hospital × AVG(cost))         — same rule, different measure ✓
V3: line_chart(date × hospital × AVG(wait)) — rule: (time:T, series:P/O, measure:M) ✓
V4: pie_chart(dept × SUM(cost))             — rule: (cat:P/S, measure:M), |cat|∈[3,8] ✓
```

**Step 2 — Single-chart QA:** V1 is a bar_chart → compatible ops: ArgMax, Sort, Limit, Filter, Max, Min, Avg, Sum, Count, ValueAt.

```
1-op:  V1 → ArgMax → S                      "Which hospital has the highest wait time?"
3-op:  V1 → Sort → Limit(2) → V → Avg → S  "Average wait of the top-2 hospitals?"
```

**Step 3 — Multi-chart QA:** Check each pair for relationship + bridge validity.

```
Pair (V1, V2):  same group_key(hospital), different measure(wait vs cost)  →  Dual-Metric
  Valid bridges for Dual-Metric: [EntityTransfer, RankCompare, ValueTransfer]
  bar_chart supports EntityTransfer? ✓ (has named entities)
  bar_chart supports RankCompare?    ✓ (has ranked entities)
  → valid_bridges not empty → KEEP this pair

  Sample pipeline (3-op):
  V1 → ArgMax → S="Xiehe" → EntityTransfer(S, V2) → V=[Xiehe's cost row] → ValueAt → S=6200
  "The hospital with the longest wait — what is its average cost?"

Pair (V1, V3):  same measure(wait), {hospital} ⊂ {date, hospital}  →  Drill-down
  Valid bridges: [EntityTransfer, ValueTransfer]
  bar → EntityTransfer → line? bar has entities ✓, line has series ✓  → KEEP

Pair (V2, V3):  different measure, no shared group_key pattern  →  None  →  SKIP
```

---

### 3.8 End-to-End Summary

```
Input:  Master Table + Schema Metadata

Step 1: Enumerate feasible views (column-role matching)
Step 2: For each view/pair/group:
        a) Check operator–chart compatibility (single-chart)
        b) Check relationship + bridge compatibility (multi-chart)
        c) Sample operator pipelines → {question, answer, chain}
Step 3: Render charts + package QA

Output: 10–30+ {chart_image(s), question, answer, operator_chain, difficulty}
```

