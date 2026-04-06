schema_metadata = {
    "dimension_groups": {
        "event": {"columns": ["Festival_Name"], "hierarchy": ["Festival_Name"]},
        "category": {"columns": ["Genre"], "hierarchy": ["Genre"]},
        "location": {"columns": ["Country"], "hierarchy": ["Country"]}
    },
    "orthogonal_groups": [
        {"group_a": "category", "group_b": "location",
         "rationale": "music genre is generally independent of country"}
    ],
    "columns": [
        {"name": "Festival_Name",     "group": "event",    "parent": None, "type": "categorical", "cardinality": 20},
        {"name": "Genre",             "group": "category", "parent": None, "type": "categorical", "cardinality": 8},
        {"name": "Country",           "group": "location", "parent": None, "type": "categorical", "cardinality": 10},
        {"name": "Year",              "type": "temporal"},
        {"name": "Month",             "type": "categorical"}, # Note: Although semantic time, it's ordinal/categorical here
        {"name": "Daily_Capacity",    "type": "measure"},
        {"name": "Total_Footfall",    "type": "measure"},
        {"name": "Ticket_Price_EUR",  "type": "measure"}
    ],
    "conditionals": [
        {"measure": "Daily_Capacity", "on": "Country",
         "mapping": {"United Kingdom": {"mu": 120000}, "Spain": {"mu": 60000}, "Germany": {"mu": 70000}}}
    ],
    "correlations": [
        {"col_a": "Daily_Capacity", "col_b": "Total_Footfall", "target_r": 0.85},
        {"col_a": "Total_Footfall", "col_b": "Ticket_Price_EUR", "target_r": 0.60}
    ],
    "dependencies": [
        {"target": "Total_Footfall", "formula": "Daily_Capacity * 3"} # Heuristic: most are 3-day festivals
    ],
    "patterns": [
        {"type": "outlier_entity", "target": "Festival_Name=='Glastonbury' & Country=='United Kingdom'",
         "col": "Daily_Capacity"},
        {"type": "ranking_reversal", "metrics": ["Daily_Capacity", "Ticket_Price_EUR"]},
        {"type": "clustering_effect", "target": "Genre=='EDM'", "metrics": ["Daily_Capacity", "Ticket_Price_EUR"]}
    ],
    "total_rows": 21
}
