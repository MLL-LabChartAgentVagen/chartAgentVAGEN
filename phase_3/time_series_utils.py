import pandas as pd
import numpy as np
import random

def reduce_time_series(df: pd.DataFrame, time_col: str, group_cols: list, agg_dict: dict) -> pd.DataFrame:
    if not time_col or time_col not in df.columns or not agg_dict:
        return df

    df = df.copy()
    try:
        df[time_col] = pd.to_datetime(df[time_col])
    except Exception:
        # Not a datetime column, fallback to standard groupby
        grp = [time_col] + group_cols
        return df.groupby(grp).agg(agg_dict).reset_index()

    # Determine granularity
    unique_years = df[time_col].dt.year.nunique()
    unique_months = df[time_col].dt.to_period('M').nunique()
    unique_weeks = df[time_col].dt.to_period('W').nunique()
    unique_days = df[time_col].dt.date.nunique()
    
    if unique_years >= 3:
        freq = 'Y'
        limit = 15
        df['agg_time'] = df[time_col].dt.to_period('Y').dt.to_timestamp()
    elif unique_months >= 3:
        freq = 'M'
        limit = 12
        df['agg_time'] = df[time_col].dt.to_period('M').dt.to_timestamp()
    elif unique_weeks >= 3:
        freq = 'W'
        limit = 15
        df['agg_time'] = df[time_col].dt.to_period('W').dt.to_timestamp()
    elif unique_days >= 3:
        freq = 'D'
        limit = 15
        df['agg_time'] = df[time_col].dt.floor('D')
    else:
        freq = 'H'
        limit = 15
        df['agg_time'] = df[time_col].dt.floor('h')

    grp = [c for c in group_cols if c] if group_cols else []
    groupby_cols = ['agg_time'] + grp
    
    agged = df.groupby(groupby_cols).agg(agg_dict).reset_index()

    unique_times = list(sorted(agged['agg_time'].unique()))
    
    if len(unique_times) > limit:
        max_start = len(unique_times) - limit
        start_idx = random.randint(0, max_start)
        selected_times = unique_times[start_idx:start_idx+limit]
    else:
        selected_times = unique_times

    filtered = agged[agged['agg_time'].isin(selected_times)].copy()
    
    if freq == 'Y':
        filtered[time_col] = filtered['agg_time'].dt.strftime('%Y')
    elif freq == 'M':
        filtered[time_col] = filtered['agg_time'].dt.strftime('%b %Y')
    elif freq == 'W':
        filtered[time_col] = filtered['agg_time'].dt.strftime('%Y-W%V')
    elif freq == 'D':
        filtered[time_col] = filtered['agg_time'].dt.strftime('%Y-%m-%d')
    else:
        filtered[time_col] = filtered['agg_time'].dt.strftime('%Y-%m-%d %H:%M')

    keep_cols = [time_col] + grp + list(agg_dict.keys())
    return filtered[keep_cols]
