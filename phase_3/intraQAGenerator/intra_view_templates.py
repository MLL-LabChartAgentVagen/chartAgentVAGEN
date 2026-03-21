INTRA_VIEW_TEMPLATES = {
    "value_retrieval": {
        "template": "What is the {agg} {measure} for {entity}?",
        "answer_fn": lambda view, entity, measure, cat:
            view.loc[view[cat] == entity, measure].values[0] if len(view.loc[view[cat] == entity, measure].values) > 0 else "N/A",
        "difficulty": "easy",
        "applicable": ["bar_chart", "grouped_bar_chart", "heatmap", "radar_chart"]
    },
    "extremum": {
        "template": "Which {cat} has the {mode} {measure}?",
        "answer_fn": lambda view, measure, cat, mode:
            view.loc[view[measure].idxmax() if mode == "highest"
                     else view[measure].idxmin(), cat] if not view.empty else "N/A",
        "difficulty": "easy",
        "applicable": ["bar_chart", "line_chart", "scatter_plot"]
    },
    "comparison": {
        "template": "How much {mode} is {entity_a}'s {measure} compared to {entity_b}?",
        "answer_fn": lambda view, a, b, m, cat:
            abs(view.loc[view[cat] == a, m].values[0] - view.loc[view[cat] == b, m].values[0])
            if (len(view.loc[view[cat] == a, m].values) > 0 and len(view.loc[view[cat] == b, m].values) > 0) else "N/A",
        "difficulty": "medium",
        "applicable": ["bar_chart", "grouped_bar_chart"]
    },
    "trend": {
        "template": "What is the overall trend of {measure} from {start} to {end}?",
        "answer_fn": lambda view, m:
            "increasing" if view[m].iloc[-1] > view[m].iloc[0] else "decreasing" if not view.empty else "N/A",
        "difficulty": "medium",
        "applicable": ["line_chart", "area_chart"]
    },
    "proportion": {
        "template": "What percentage does {entity} contribute to the total {measure}?",
        "answer_fn": lambda view, entity, m, cat:
            (view.loc[view[cat] == entity, m].values[0] / view[m].sum() * 100)
            if (len(view.loc[view[cat] == entity, m].values) > 0 and view[m].sum() != 0) else "N/A",
        "difficulty": "medium",
        "applicable": ["pie_chart", "donut_chart", "stacked_bar_chart"]
    },
    "distribution_shape": {
        "template": "Is the distribution of {measure} left-skewed, right-skewed, or symmetric?",
        "answer_fn": lambda view, m:
            "right-skewed" if view[m].skew() > 0.5
            else ("left-skewed" if view[m].skew() < -0.5 else "approximately symmetric"),
        "difficulty": "medium",
        "applicable": ["histogram", "violin_plot"]
    },
    "correlation_direction": {
        "template": "What is the relationship between {m1} and {m2}? Positive, negative, or none?",
        "answer_fn": lambda view, m1, m2:
            "positive" if view[m1].corr(view[m2]) > 0.3
            else ("negative" if view[m1].corr(view[m2]) < -0.3 else "no clear relationship"),
        "difficulty": "hard",
        "applicable": ["scatter_plot", "bubble_chart"]
    }
}