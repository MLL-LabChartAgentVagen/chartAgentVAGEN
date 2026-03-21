import pandas as pd
import copy
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

CHART_FAMILIES = {
    "bar_chart": "Comparison", "grouped_bar_chart": "Comparison",
    "line_chart": "Trend", "area_chart": "Trend",
    "histogram": "Distribution", "box_plot": "Distribution", "violin_plot": "Distribution",
    "pie_chart": "Composition", "donut_chart": "Composition", "stacked_bar_chart": "Composition", "treemap": "Composition",
    "scatter_plot": "Relationship", "bubble_chart": "Relationship", "heatmap": "Relationship", "radar_chart": "Relationship",
    "waterfall_chart": "Flow", "funnel_chart": "Flow"
}

@dataclass
class ViewSpec:
    """Specification for projecting data into a chart-ready view."""
    
    chart_type: str
    binding: Dict[str, str]
    rule: Dict[str, Any]
    score: float = 0.0
    filter: Optional[str] = None
    
    _schema_metadata: Optional[Dict[str, Any]] = None
    extracted_view: Optional[pd.DataFrame] = None
    
    @property
    def family(self) -> str:
        """Returns the chart family (e.g. Comparison, Trend)."""
        return CHART_FAMILIES.get(self.chart_type, "Unknown")

    @property
    def measure(self) -> str:
        """Convenience property to get the primary measure column."""
        return self.binding.get("measure") or self.binding.get("m1") or ""

    @property
    def group_by(self) -> List[str]:
        """Extract 'GROUP BY' columns from binding keys dynamically."""
        group_slots = ["cat", "cat1", "cat2", "time", "series", "stack", "hier1", "hier2", "row_cat", "col_cat", "stage", "entity"]
        cols = [self.binding[slot] for slot in group_slots if self.binding.get(slot)]
        return list(dict.fromkeys(cols)) # Preserve order and keep unique
        
    @property
    def group_key(self) -> Tuple[str, ...]:
        """A hashable representation of the grouping columns, for composing patterns."""
        return tuple(sorted(self.group_by))

    @property
    def agg(self) -> Dict[str, str]:
        """Dictionary mapping a measure column to its aggregation function."""
        # Simple heuristic from rule transform string
        transform = self.rule.get("transform", "")
        agg_fun = "mean"
        if "SUM(" in transform.upper():
            agg_fun = "sum"
        elif "COUNT(" in transform.upper():
            agg_fun = "count"
        
        agg_dict = {}
        for slot in ["measure", "measures", "m1", "m2", "m3"]:
            binding = self.binding.get(slot)
            if binding:
                if isinstance(binding, list):
                    for b in binding:
                        agg_dict[b] = agg_fun
                else:
                    agg_dict[binding] = agg_fun
        return agg_dict

    @property
    def sort_by(self) -> List[str]:
        """Returns sorting columns if strictly required by rule transform."""
        if "ORDER BY AGG DESC" in self.rule.get("transform", "") and self.measure:
            return [self.measure] 
        return []

    @property
    def limit(self) -> Optional[int]:
        return None

    @property
    def select_columns(self) -> List[str]:
        """Return the final columns required for the generated view."""
        cols = self.group_by.copy()
        for slot in ["measure", "measures", "m1", "m2", "m3", "color"]:
            if self.binding.get(slot):
                val = self.binding[slot]
                if isinstance(val, list):
                    cols.extend(val)
                else:
                    cols.append(val)
        return list(dict.fromkeys(cols))

    def extract_view(self, master_table: pd.DataFrame) -> pd.DataFrame:
        """Deterministic SQL-like projection from Master Table to chart-ready view."""
        df = master_table.copy()
        if self.filter:      df = df.query(self.filter)       # σ: row selection
        if self.group_by:    df = df.groupby(self.group_by).agg(self.agg).reset_index()
        if self.sort_by:     df = df.sort_values(self.sort_by)
        if self.limit:       df = df.head(self.limit)
        self.extracted_view = df[self.select_columns]
        return self.extracted_view

    def uses_role(self, role: str) -> bool:
        """Check whether the assigned columns fulfill a specific schema role."""
        if self._schema_metadata and "columns" in self._schema_metadata:
            col_roles = {c["name"]: c["role"] for c in self._schema_metadata["columns"]}
            return any(col_roles.get(col) == role for col in self.binding.values() if col)

        # Fallback to checking the rule's allowed roles logic
        col_binding_rules = self.rule.get("column_binding", {})
        for slot, col in self.binding.items():
            if col and role in col_binding_rules.get(slot, []):
                return True
        return False

    def with_filter(self, filter_condition: str) -> 'ViewSpec':
        """Create a duplicate ViewSpec with an added compound filter."""
        new_spec = copy.deepcopy(self)
        if new_spec.filter:
            new_spec.filter = f"({new_spec.filter}) and ({filter_condition})"
        else:
            new_spec.filter = filter_condition
        return new_spec

    def filter_compatible(self, target_condition: str) -> bool:
        """Ensure condition doesn't logically clash with an existing filter."""
        # Sophisticated parsing required for robust usage; naive truth for implementation skeleton
        return True
