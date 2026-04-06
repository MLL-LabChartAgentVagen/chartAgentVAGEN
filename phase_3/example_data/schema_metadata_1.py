schema_metadata = {
    "dimension_groups": {
        "event": {"columns": ["Tournament_Name"], "hierarchy": ["Tournament_Name"]},
        "category": {"columns": ["Game_Genre"], "hierarchy": ["Game_Genre"]},
        "location": {"columns": ["Host_Region"], "hierarchy": ["Host_Region"]}
    },
    "orthogonal_groups": [
        {"group_a": "category", "group_b": "location",
         "rationale": "game genre is independent of host region"}
    ],
    "columns": [
        {"name": "Tournament_Name",       "group": "event",    "parent": None, "type": "categorical", "cardinality": 23},
        {"name": "Game_Genre",            "group": "category", "parent": None, "type": "categorical", "cardinality": 5},
        {"name": "Host_Region",           "group": "location", "parent": None, "type": "categorical", "cardinality": 5},
        {"name": "Tournament_End_Date",   "type": "temporal"},
        {"name": "Total_Prize_Pool_USD",  "type": "measure"},
        {"name": "First_Place_Prize_USD", "type": "measure"},
        {"name": "Participating_Teams",   "type": "measure"}
    ],
    "conditionals": [
        {"measure": "Total_Prize_Pool_USD", "on": "Game_Genre",
         "mapping": {"MOBA": {"mu": 4000000}, "FPS": {"mu": 1500000}, "Battle Royale": {"mu": 2000000}}}
    ],
    "correlations": [
        {"col_a": "Total_Prize_Pool_USD", "col_b": "First_Place_Prize_USD", "target_r": 0.95},
        {"col_a": "Total_Prize_Pool_USD", "col_b": "Participating_Teams", "target_r": 0.40}
    ],
    "dependencies": [
        {"target": "First_Place_Prize_USD", "formula": "Total_Prize_Pool_USD * 0.35"}
    ],
    "patterns": [
        {"type": "outlier_entity", "target": "Tournament_Name=='Riyadh Masters (Gamers8)' & Game_Genre=='MOBA'",
         "col": "Total_Prize_Pool_USD"},
        {"type": "ranking_reversal", "metrics": ["Total_Prize_Pool_USD", "Participating_Teams"]},
        {"type": "trend_break", "target": "Host_Region=='North America'",
         "col": "Total_Prize_Pool_USD", "break_point": "2023-08-01"}
    ],
    "total_rows": 24
}
