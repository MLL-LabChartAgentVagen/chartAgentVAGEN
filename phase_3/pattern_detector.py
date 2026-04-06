import re
from typing import List

import pandas as pd

from .data_model import ViewSpec, QAPair


class PatternDetector:
    """Scan view DataFrames for patterns injected in Phase 2."""

    def detect_and_generate_qa(self, view: pd.DataFrame, view_spec: ViewSpec,
                                pattern_metadata: List[dict]) -> List[QAPair]:
        qa_pairs = []
        for pattern in pattern_metadata:
            if self._pattern_visible_in_view(pattern, view_spec):
                qa_pairs.extend(self._generate_pattern_qa(pattern, view, view_spec))
        return qa_pairs

    def _pattern_visible_in_view(self, pattern: dict,
                                  view_spec: ViewSpec) -> bool:
        """Check if the pattern's target column/entity appears in this view."""
        if pattern.get("col") and pattern["col"] not in view_spec.select_columns:
            return False
        if pattern.get("target"):
            return view_spec.filter_compatible(pattern["target"])
        return True

    def _generate_pattern_qa(self, pattern: dict, view: pd.DataFrame,
                              view_spec: ViewSpec) -> List[QAPair]:
        """Generate QA pairs specific to each pattern type."""
        ptype = pattern["type"]

        if ptype == "outlier_entity":
            entity_val = view.query(pattern["target"])[pattern["col"]].mean()
            overall_mean = view[pattern["col"]].mean()
            return [QAPair(
                question=f"Which entity shows an anomalously high "
                         f"{pattern['col']}? By how much does it deviate?",
                answer=f"{self._extract_entity(pattern['target'])}; "
                       f"deviates by {entity_val - overall_mean:.1f}",
                reasoning=f"Visual inspection shows "
                          f"{self._extract_entity(pattern['target'])} is "
                          f"clearly separated. Its value ({entity_val:.1f}) "
                          f"exceeds the group mean ({overall_mean:.1f}).",
                difficulty="hard"
            )]

        elif ptype == "trend_break":
            bp = pattern.get("break_point", pattern.get("params", {}).get("break_point"))
            mag = pattern.get("magnitude", pattern.get("params", {}).get("magnitude", 0))
            return [QAPair(
                question=f"Is there a significant change point in "
                         f"{pattern['col']}? When does it occur?",
                answer=f"Yes, around {bp} with ~{mag*100:.0f}% magnitude.",
                reasoning="The chart shows a visible discontinuity at "
                          "the identified time point.",
                difficulty="hard"
            )]

        elif ptype == "ranking_reversal":
            metrics = pattern.get("metrics",
                                  pattern.get("params", {}).get("metrics", []))
            desc = pattern.get("description",
                               pattern.get("params", {}).get("description", ""))
            m1, m2 = metrics[0], metrics[1]
            return [QAPair(
                question=f"Does the entity ranked highest on {m1} "
                         f"also rank highest on {m2}?",
                answer=f"No — ranking reversal: {desc}.",
                reasoning=f"Comparing charts reveals high {m1} does not "
                          f"imply high {m2}.",
                difficulty="very_hard"
            )]

        elif ptype == "dominance_shift":
            return [QAPair(
                question="Does the leading entity remain the same "
                         "throughout the entire time period?",
                answer="No — a dominance shift occurs mid-period.",
                reasoning="Early time points show one entity leading, "
                          "but a crossover occurs.",
                difficulty="hard"
            )]

        elif ptype == "convergence":
            return [QAPair(
                question="Are the two series converging, diverging, "
                         "or maintaining a constant gap?",
                answer="Converging — the gap narrows over time.",
                reasoning="Visual comparison shows decreasing difference.",
                difficulty="medium"
            )]

        elif ptype == "seasonal_anomaly":
            return [QAPair(
                question=f"Does {pattern['col']} follow a consistent "
                         f"seasonal pattern across all entities?",
                answer=f"Most follow typical seasonality, but "
                       f"{self._extract_entity(pattern['target'])} deviates.",
                reasoning="One entity breaks the expected cyclical pattern.",
                difficulty="hard"
            )]

        return []

    def _extract_entity(self, target_filter: str) -> str:
        """Extract entity name from filter string like \"hospital == 'Xiehe'\"."""
        match = re.search(r"== '([^']+)'", target_filter)
        return match.group(1) if match else target_filter