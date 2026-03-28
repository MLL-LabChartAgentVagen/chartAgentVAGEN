import pandas as pd
from typing import List, Any, Union, Callable

class RelationalOperator:
    """Base class for relational operators"""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

class Filter(RelationalOperator):
    """Filter rows based on a condition."""
    def __init__(self, column: str, condition: Callable[[Any], bool]):
        self.column = column
        self.condition = condition

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns:
            # If column missing, skip or error? For now, skip to be safe
            return df
        return df[df[self.column].apply(self.condition)].copy()

class Project(RelationalOperator):
    """Select specific columns."""
    def __init__(self, columns: List[str]):
        self.columns = columns

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Only select columns that exist
        valid_cols = [c for c in self.columns if c in df.columns]
        if not valid_cols:
            return df # Return all if none found? Or empty?
        return df[valid_cols].copy()

class GroupBy(RelationalOperator):
    """Group by columns and apply aggregation."""
    def __init__(self, by: List[str], agg: dict):
        """
        by: list of columns to group by
        agg: dict mapping column names to aggregation functions (str or callable)
             e.g., {'Revenue': 'sum'}
        """
        self.by = by
        self.agg = agg

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        valid_by = [c for c in self.by if c in df.columns]
        if not valid_by:
            return df
            
        return df.groupby(valid_by, as_index=False).agg(self.agg)

class Aggregate(RelationalOperator):
    """Aggregate a column using a function (Sum, Avg, Count, etc.)."""
    def __init__(self, column: str, func: str):
        """
        column: column to aggregate
        func: aggregation function name ('sum', 'mean', 'count', 'min', 'max')
        """
        self.column = column
        self.func = func

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns:
            return df
        value = df[self.column].agg(self.func)
        return pd.DataFrame({self.column: [value]})

class Sort(RelationalOperator):
    """Sort by a column."""
    def __init__(self, column: str, ascending: bool = True):
        self.column = column
        self.ascending = ascending

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns:
            return df
        return df.sort_values(by=self.column, ascending=self.ascending)

class Limit(RelationalOperator):
    """Limit number of rows."""
    def __init__(self, n: int):
        self.n = n

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.head(self.n).copy()

class Chain:
    """Chain multiple operators."""
    def __init__(self, operators: List[RelationalOperator]):
        self.operators = operators

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        res = df
        for op in self.operators:
            res = op.apply(res)
        return res
