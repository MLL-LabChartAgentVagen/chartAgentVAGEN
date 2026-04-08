# Chart Master Data Schema Analysis

## Part 1 — Field Definitions

| Field Name | Data Type | Purpose (Charting context) | Consuming Chart Types |
| :--- | :--- | :--- | :--- |
| `entities` | `List[String]` | Defines the categorical keys (independent variable) that distinct graphical marks represent. | **Bar Chart** (X-axis categories), **Pie Chart** (Slice labels), **Radar Chart** (Axis points) |
| `primary_values` | `List[Number]` | Supplies the core quantitative metric that drives the main visual magnitude. | **Bar Chart** (Height), **Line Chart** (Y-position), **Donut Chart** (Arc length) |
| `secondary_values` | `List[Number]` | Provides a second quantitative dimension for coordinate-based or multi-series plots. | **Scatter Plot** (Y-axis position), **Bubble Chart** (Y-axis position), **Clustered Bar Chart** (Second bar series) |
| `tertiary_values` | `List[Number]` | Encodes a third dimension via visual channels beyond position, such as area or saturation. | **Bubble Chart** (Circle radius), **Heatmap** (Color density), **Weighted Scatter** (Point size) |
| `unit_primary` | `String` | Dictates number formatting logic for axis ticks and data labels (e.g., currency symbols, precision). | **Bar Chart** (Y-axis ticks), **Metric Card** (KPI display), **Tooltip** (Value suffix) |
| `unit_secondary` | `String` | Controls formatting for the secondary axis or dimension in multi-variate views. | **Dual-Axis Line Chart** (Second Y-axis), **Scatter Plot** (Y-axis ticks) |
| `entity_type_singular`| `String` | Grammatical primitive used to construct natural language tooltips or dynamic titles. | **Interactive Tooltip** ("This _country_ generated..."), **Drill-down Menu** |
| `entity_type_plural` | `String` | Serves as the default title for the categorical axis or legend header. | **Bar Chart** (X-axis title), **Table** (Column Header) |
| `metric_name_primary` | `String` | Identifies the semantic variable for the primary quantitative axis title or legend. | **Line Chart** (Y-axis title), **Pie Chart** (Legend title), **Bar Chart** (Series label) |
| `metric_name_secondary`| `String` | Identifies the second variable in multivariate plots to distinguish it from the primary metric. | **Scatter Plot** (Y-axis title), **Mixed-Measure Line Chart** (Right Y-axis title) |
| `statistical_properties`| `Object` | Container for pre-calculated analytics to drive annotations, reference lines, or color-coding rules. | **Annotated Line Chart** (Trend line), **Box Plot** (Outlier highlighting), **Executive Dashboard** (Summary captions) |

---

## Part 2 — Necessity Audit

### TIER 1: REQUIRED (Blocking)
*   `primary_values`: The fundamental signal. No rendering is possible without this vector (e.g., a **Line Chart** has no path to draw, a **Pie Chart** has no geometry).
*   `entities`: required to anchor the values to a domain. Without this, a **Bar Chart** has no X-axis labels and a **Scatter Plot** lacks point identifiers for interactivity.

### TIER 2: CONDITIONAL (Topology Dependent)
*   `secondary_values`: **REQUIRED** for **Scatter Plots** (determines Y-coordinate while `primary` determines X) and **Range Area Charts** (High vs Low). **OPTIONAL** for simple Bar/Line charts.
*   `tertiary_values`: **REQUIRED** for **Bubble Charts** (determines Z-axis/size). **OPTIONAL** for standard 2D plots (acts as metadata).
*   `metric_name_primary`: **REQUIRED** for **Legend** generation and multi-series disambiguation. **OPTIONAL** only if the chart is a sparkline with no text chrome.
*   `unit_primary`: **CONDITIONAL**. Required if the data values are raw (e.g., `0.5`) but need to be rendered as specific formats (e.g., `50%`).

### TIER 3: OPTIONAL (Enhancement)
*   `entity_type_singular` / `entity_type_plural`: Purely for semantic richness in tooltips/titles. The chart renders standard strings without them.
*   `statistical_properties`: This is metadata "sugar". A renderer can calculate outliers or correlations on the fly from the raw data; explicitly passing them is an optimization or narrative convenience, not a rendering requirement.
*   `data_year` (within statistical_properties): Contextual only.

---

## Verdict

The **`statistical_properties`** object and **`entity_type_*`** fields can be safely removed for a minimal viable schema. The rendering engine should accept raw vectors (`entities`, `values`) and calculate distributions or trends at runtime if visualization of those properties (like trend lines) is requested.
