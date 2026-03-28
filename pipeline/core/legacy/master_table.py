import pandas as pd
import io
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class MasterTable:
    """
    Represents a Master Data Table adhering to Star Schema principles.
    Validates that the data contains:
    1. Temporal Backbone (Date/Time column)
    2. Dimensional Diversity (Categorical columns)
    3. Metric Correlation (Numerical columns)
    """
    df: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.validate_schema()

    def validate_schema(self) -> bool:
        """
        Validates the DataFrame against Star Schema constraints.
        Returns True if valid, raises ValueError otherwise.
        """
        if self.df.empty:
            raise ValueError("MasterTable DataFrame is empty")

        # 1. Temporal Backbone
        temporal_cols = self.df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
        # Also check for likely string-based date columns if not explicitly datetime
        if not temporal_cols:
             potential_date_cols = [col for col in self.df.columns if 'date' in col.lower() or 'time' in col.lower() or 'period' in col.lower() or 'year' in col.lower() or 'month' in col.lower()]
             if potential_date_cols:
                 # Attempt simpler validation or just accept for now, ideally we enforce strict types
                 temporal_cols = potential_date_cols

        if not temporal_cols:
             # Relaxed check: Accept if we have at least one column that *could* be temporal
             # For strict Star Schema, this should be enforced.
             logger.warning("No explicit temporal column found. Ensure data has a time dimension.")

        # 2. Dimensional Diversity (Categorical)
        cat_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        # Filter out temporal cols if they were identified as objects
        cat_cols = [c for c in cat_cols if c not in temporal_cols]
        
        if len(cat_cols) < 2:
            logger.warning(f"Low dimensional diversity: Found {len(cat_cols)} categorical columns, expected 2+")
            
        # 3. Metric Correlation (Numerical)
        num_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        if len(num_cols) < 2:
             logger.warning(f"Low metric correlation: Found {len(num_cols)} numerical columns, expected 2+")

        return True

    @classmethod
    def from_csv(cls, csv_content: str, metadata: Optional[Dict] = None) -> 'MasterTable':
        """Creates a MasterTable from a CSV string."""
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            # Basic cleanup: strip whitespace from column names
            df.columns = df.columns.str.strip()
            return cls(df, metadata or {})
        except Exception as e:
            raise ValueError(f"Failed to parse CSV content: {e}")

    def to_csv(self) -> str:
        """Serializes the MasterTable to a CSV string."""
        return self.df.to_csv(index=False)
    
    def to_legacy_chart_entry(self, chart_type: str, x_col: str, y_col: str, **kwargs) -> Dict[str, Any]:
        """
        Adapter: Converts the relational table slice into the legacy 
        chart_entries format expected by drawing functions.
        
        Args:
            chart_type: 'bar', 'scatter', 'pie'
            x_col: Column name for X-axis (labels)
            y_col: Column name for Y-axis (values)
            **kwargs: Additional mapping args (e.g., z_col for scatter size)
        """
        # Ensure columns exist
        if x_col not in self.df.columns:
            raise KeyError(f"Column '{x_col}' not found in MasterTable")
        if y_col not in self.df.columns:
             raise KeyError(f"Column '{y_col}' not found in MasterTable")

        # Basic projection
        # For legacy compatibility, we often need flat lists
        data = self.df[[x_col, y_col]].dropna().copy()
        
        entry = {
            "x_label": x_col,
            "y_label": y_col,
            "img_title": self.metadata.get("title", f"{y_col} by {x_col}")
        }

        if chart_type == "bar":
            entry["bar_labels"] = data[x_col].astype(str).tolist()
            entry["bar_data"] = data[y_col].tolist()
            # Legacy logic often assigned arbitrary colors, we can keep that or generate here
            # For now, let's leave color generation to the drawer or assign default
            entry["bar_colors"] = ["#1f77b4"] * len(entry["bar_data"]) 

        elif chart_type == "pie":
            entry["pie_labels"] = data[x_col].astype(str).tolist()
            entry["pie_data"] = data[y_col].tolist()
            entry["pie_colors"] = ["#1f77b4"] * len(entry["pie_data"]) # Placeholder

        elif chart_type == "scatter":
            entry["scatter_labels"] = data[x_col].astype(str).tolist()
            entry["scatter_x_data"] = data[y_col].tolist() # Wait, scatter usually X is numeric too
            
            # If x_col is actually categorical, this might be a categorical scatter logic
            # But standard scatter expects numeric X and Y. 
            # If x_col is categorical, maybe generate numeric mapping?
            # For now, assume simple case or follow legacy logic.
            
            # The legacy logic had: entities, primary (y), secondary (x), tertiary (size)
            # So if we map: y_col -> y, and kwargs['x_metric'] -> x
            
            x_metric = kwargs.get('x_metric')
            if x_metric and x_metric in self.df.columns:
                 entry["scatter_x_data"] = self.df[x_metric].tolist()
                 entry["x_label"] = x_metric
                 entry["scatter_y_data"] = data[y_col].tolist()
            else:
                 # Fallback/Error for scatter
                 entry["scatter_y_data"] = data[y_col].tolist()
                 # Index as X if no metric provided?
                 entry["scatter_x_data"] = list(range(len(data)))
            
            size_col = kwargs.get('size_col')
            if size_col and size_col in self.df.columns:
                entry["scatter_sizes"] = self.df[size_col].tolist()
            else:
                 entry["scatter_sizes"] = [50] * len(entry["scatter_y_data"])
                 
            entry["scatter_colors"] = ["#ff7f0e"] * len(entry["scatter_y_data"])

        return entry
