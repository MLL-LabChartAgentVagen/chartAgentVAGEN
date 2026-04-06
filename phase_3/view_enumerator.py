from typing import List, Dict

import pandas as pd

from view_spec import ViewSpec
from chart_selection_guide import CHART_SELECTION_GUIDE
from chart_type_registry import CHART_TYPE_REGISTRY
from view_extraction_rules import VIEW_EXTRACTION_RULES
from view_extractor import ViewData, ViewExtractor
from collections import defaultdict
import itertools
import re

def extract_view(master_table: pd.DataFrame, view_spec: ViewSpec) -> pd.DataFrame:
    """Deterministic SQL-like projection from Master Table to chart-ready view."""
    df = master_table.copy()
    if view_spec.filter:      df = df.query(view_spec.filter)       # σ: row selection
    if view_spec.group_by:    df = df.groupby(view_spec.group_by).agg(view_spec.agg).reset_index()
    if view_spec.sort_by:     df = df.sort_values(view_spec.sort_by)
    if view_spec.limit:       df = df.head(view_spec.limit)
    return df[view_spec.select_columns]                              # π: column projection

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
        """Infer and group column names by their analytical role for binding lookup."""
        groups = defaultdict(list)
        
        # Determine the primary dimension group (first one defined)
        primary_group = None
        dim_groups = schema_metadata.get("dimension_groups", {})
        if dim_groups:
            primary_group = list(dim_groups.keys())[0]

        for col in schema_metadata["columns"]:
            col_name = col["name"]
            col_type = col.get("type", "")
            
            if col_type == "measure":
                groups["measure"].append(col_name)
                
            elif col_type == "temporal":
                groups["temporal"].append(col_name)
                
            elif col_type == "categorical":
                group_name = col.get("group")
                parent = col.get("parent")
                
                if group_name == primary_group:
                    if not parent:
                        groups["primary"].append(col_name)
                    else:
                        groups["secondary"].append(col_name)
                else:
                    groups["orthogonal"].append(col_name)
                    
        return groups

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
        
    def _estimate_view_rows(self, view_spec: ViewSpec, master_table: pd.DataFrame) -> int:
        """
        Estimate the number of rows a view will have without actually rendering it.
        If the view groups data (e.g., Bar Chart), the row count is the product
        of the cardinality of the grouping dimensions.
        If it's disaggregated (e.g., Scatter Plot), it's close to the original row count.
        """
        # If the chart groups data, estimate max combinations
        if view_spec.group_by:
            # Drop duplicates across the grouped columns gives the exact number of groups
            return len(master_table.drop_duplicates(subset=view_spec.group_by))
            
        # If no grouping, it uses the whole table (or filtered table)
        return len(master_table)
    import re

    def _pattern_visible(self, pattern: dict, view_spec: ViewSpec) -> bool:
        """Fast, heuristic check based on column bindings."""
        # 1. Gather all columns needed to see this pattern
        required_cols = set()
        
        # Add explicit measure columns
        if "col" in pattern:
            required_cols.add(pattern["col"])
        if "metrics" in pattern:
            required_cols.update(pattern["metrics"])
            
        # Extract columns used in pandas query strings (e.g. "Game_Genre=='MOBA'")
        if "target" in pattern:
            cols_in_query = set(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)(?===|!=|>|<)', pattern["target"]))
            required_cols.update(cols_in_query)
            
        # 2. Ask the ViewSpec if it uses these columns
        # view_spec.select_columns contains the final output columns generated for the chart
        view_cols = set(view_spec.select_columns)
        
        # If the chart groups by/plots everything needed for the pattern, it's visible!
        return required_cols.issubset(view_cols)


if __name__ == "__main__":
    from example_data.schema_metadata_1 import schema_metadata
    
    # Load the corresponding CSV
    import os
    csv_path = os.path.join("example_data", "master_data_1.csv")
    master_table = pd.read_csv(csv_path)
    
    # Enumerate
    enumerator = ViewEnumerator()
    views = enumerator.enumerate(schema_metadata, master_table)
    
    print(f"Enumerated {len(views)} feasible views:")
    chart_types = set()
    for i, v in enumerate(views[:10]): # Print top 10
        print(f"  - {v.chart_type}: {v.binding} (Score: {v.score:.2f})")
        chart_types.add(v.chart_type)
        view_data = ViewData(v, master_table)
        df = view_data.extracted_view
        df.to_csv(f"test_data/view_{i}_{v.chart_type}.csv", index=False)
    print(f"Chart types: {chart_types}")
    exit()
        

    
    

