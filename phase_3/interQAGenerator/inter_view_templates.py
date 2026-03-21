INTER_VIEW_TEMPLATES = {
    "ranking_consistency": {
        "template": "The {cat} with the highest {m1} in Chart A — "
                    "what is its rank for {m2} in Chart B?",
        "answer_fn": lambda views: cross_rank_lookup(views[0], views[1]),
        "required_rel": ["dual_metric", "associative"],
        "difficulty": "hard"
    },
    "conditional_lookup": {
        "template": "In Chart A, {cat} has a {measure} of {value}. "
                    "What is this {cat}'s {other_measure} shown in Chart B?",
        "answer_fn": lambda views: conditional_value_transfer(views[0], views[1]),
        "required_rel": ["any"],
        "difficulty": "hard"
    },
    "trend_divergence": {
        "template": "Do {entity_a} and {entity_b} show the same trend direction "
                    "for {measure} across both time periods?",
        "answer_fn": lambda views: compare_trend_directions(views[0], views[1]),
        "required_rel": ["comparative", "dual_metric"],
        "difficulty": "hard"
    },
    "drilldown_verification": {
        "template": "Chart A shows {cat_a} dominates overall. "
                    "In the detailed Chart B, which sub-category drives this dominance?",
        "answer_fn": lambda views: identify_dominant_subcategory(views[0], views[1]),
        "required_rel": ["drill_down"],
        "difficulty": "hard"
    },
    "orthogonal_reasoning": {
        "template": "Chart A shows {measure} by {primary_cat}. "
                    "Chart B shows the same metric by {ortho_cat}. "
                    "Is the top-performing {primary_cat} also dominant "
                    "within each {ortho_cat} group?",
        "answer_fn": lambda views, master:
            verify_orthogonal_dominance(views, master),
        "required_rel": ["orthogonal_slice"],
        "difficulty": "very_hard"
    },
    "causal_inference": {
        "template": "Chart A shows {cause} increased. Chart B shows {mediator} "
                    "also increased. But Chart C shows {effect} decreased. "
                    "What might explain this?",
        "answer_fn": lambda views, schema:
            build_causal_explanation(views, schema["dependencies"]),
        "required_rel": ["causal_chain"],
        "difficulty": "very_hard"
    },
    "holistic_synthesis": {
        "template": "Considering all {k} charts, which {cat} demonstrates "
                    "the best overall performance across all metrics?",
        "answer_fn": lambda views: compute_composite_ranking(views),
        "required_rel": ["mixed"],
        "difficulty": "very_hard"
    }
}