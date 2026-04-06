from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from view_spec import ViewSpec


@dataclass
class Dashboard:
    """A multi-chart composition produced by DashboardComposer.

    Attributes:
        views:        2–4 ViewSpec objects that form the dashboard.
        relationship: Semantic relationship label (e.g. "comparative",
                      "drill_down", "dual_metric").
        pattern:      Composition pattern key (e.g. "overview_detail").
        title:        Human-readable title; auto-derived if not supplied.
        layout:       Grid layout hint ("2x1", "1x3", "2x2").
        qa_pairs:     Cross-view QA dicts appended by IntraQAGenerator /
                      PatternDetector after construction.
    """

    views: List["ViewSpec"]
    relationship: str
    pattern: str = ""
    title: Optional[str] = None
    layout: Optional[str] = None
    qa_pairs: List[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Auto-derive title
        if self.title is None:
            rel_label = self.relationship.replace("_", " ").title()
            type_labels = " + ".join(v.chart_type for v in self.views)
            self.title = f"{rel_label} — {type_labels}"

        # Auto-derive layout
        if self.layout is None:
            n = len(self.views)
            self.layout = "2x1" if n == 2 else "1x3" if n == 3 else "2x2"

    # ── Computed properties ──────────────────────────────────────────────────

    @property
    def score(self) -> float:
        """Mean suitability score of member views."""
        if not self.views:
            return 0.0
        return sum(v.score for v in self.views) / len(self.views)

    @property
    def chart_families(self) -> List[str]:
        """Chart family of each member view (e.g. ["Comparison", "Trend"])."""
        return [v.family for v in self.views]

    @property
    def family_diversity(self) -> int:
        """Number of distinct chart families represented."""
        return len(set(self.chart_families))

    @property
    def view_count(self) -> int:
        return len(self.views)

    @property
    def measures(self) -> List[str]:
        """Unique primary measures across all views, insertion-ordered."""
        seen: set = set()
        result: List[str] = []
        for v in self.views:
            if v.measure and v.measure not in seen:
                result.append(v.measure)
                seen.add(v.measure)
        return result

    # ── Mutators ─────────────────────────────────────────────────────────────

    def add_qa(self, qa: dict) -> None:
        """Append a QA dict (keys: question, answer, difficulty, template)."""
        self.qa_pairs.append(qa)

    # ── Serialisation ────────────────────────────────────────────────────────

    def to_dict(self) -> Dict:
        """Return a JSON-safe representation of the dashboard."""
        return {
            "pattern": self.pattern,
            "relationship": self.relationship,
            "title": self.title,
            "layout": self.layout,
            "score": round(self.score, 3),
            "family_diversity": self.family_diversity,
            "measures": self.measures,
            "views": [
                {
                    "chart_type": v.chart_type,
                    "binding": v.binding,
                    "family": v.family,
                    "score": round(v.score, 3),
                }
                for v in self.views
            ],
            "qa_pairs": self.qa_pairs,
        }

    def summary(self) -> str:
        """One-line human-readable description."""
        types = " + ".join(v.chart_type for v in self.views)
        return f"[{self.pattern}] {types} — {self.relationship}"

    def __repr__(self) -> str:
        return (
            f"Dashboard(pattern={self.pattern!r}, "
            f"views={[v.chart_type for v in self.views]}, "
            f"score={self.score:.2f})"
        )
