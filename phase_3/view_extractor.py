from view_spec import ViewSpec
import pandas as pd

class ViewExtractor:
    def __init__(self, view_spec: ViewSpec):
        self.view_spec = view_spec

    def extract_view(self, master_table: pd.DataFrame) -> pd.DataFrame:
        """Deterministic SQL-like projection from Master Table to chart-ready view."""
        view_spec = self.view_spec
        df = master_table.copy()
        if view_spec.filter:      df = df.query(view_spec.filter)       # σ: row selection
        if view_spec.chart_type in ["line_chart", "area_chart"] and view_spec.binding.get("time"):
            time_col = view_spec.binding.get("time")
            group_cols = [c for c in view_spec.group_by if c and c != time_col]
            from time_series_utils import reduce_time_series
            df = reduce_time_series(df, time_col, group_cols, view_spec.agg)
        elif view_spec.group_by and view_spec.chart_type not in ["box_plot", "violin_plot"]:
            df = df.groupby(view_spec.group_by).agg(view_spec.agg).reset_index()
        if view_spec.sort_by:     df = df.sort_values(view_spec.sort_by)
        if view_spec.limit:       df = df.head(view_spec.limit)
        
        # Ensure dynamic columns mapped correctly, sometimes measures is a list string
        columns = view_spec.select_columns
        if isinstance(columns, str):
            columns = [columns]
        elif isinstance(columns, list):
            flat_cols = []
            for col in columns:
                if isinstance(col, list):
                    flat_cols.extend(col)
                elif pd.isna(col) or col is None:
                    continue
                else:
                    flat_cols.append(col)
            columns = flat_cols
            
        columns = [c for c in columns if c in df.columns]

        return df[columns]

class ViewData:
    def __init__(self, view_spec: ViewSpec, master_table: pd.DataFrame):
        self.view_spec = view_spec
        self.master_table = master_table
        self.view_extractor = ViewExtractor(view_spec)
        self.extracted_view = self.view_extractor.extract_view(master_table)
        
        
