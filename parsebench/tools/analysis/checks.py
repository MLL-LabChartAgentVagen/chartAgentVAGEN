"""What the program says about the model's answer, after the call.

Two kinds. `reconcile` settles the answer against itself: a key defined on two or
more panels cannot stand when the figure table reports one panel. `crosscheck`
settles it against the spot-check labels, which the model never saw -- it was given
the values alone, so the keys it predicts for each value are a prediction, and the
benchmark's own labels grade it.

Both report rather than repair, except for the one drop `reconcile` makes -- a key
kept there would land in the frequency table and reorder what gets built.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from rules import Rule
from vocabulary import BY_KEY

#: Keys whose definition needs more than one panel, or more than one figure.
NEEDS_PANELS = ("shared_legend", "shared_axis", "small_multiples_4", "small_multiples_5plus")
NEEDS_FIGURES = ("multi_figure_page",)


def components_of(analysis: dict) -> list[dict]:
    """The reported components, as `{key, figure_id, evidence}`, vocabulary keys only."""
    return [c for c in (analysis.get("components") or ())
            if isinstance(c, dict) and c.get("key") in BY_KEY]


def keys_of(analysis: dict) -> list[str]:
    """Just the keys, deduplicated, in the order first reported."""
    out: list[str] = []
    for component in components_of(analysis):
        if component["key"] not in out:
            out.append(component["key"])
    return out


def evidence_of(analysis: dict, key: str) -> str:
    """The first evidence given for one key on this page, empty when none."""
    return next((str(c.get("evidence", "")) for c in components_of(analysis)
                 if c["key"] == key), "")


def reconcile(analysis: dict) -> list["Finding"]:
    """Drop component keys the model's own figure table rules out.

    `shared_legend` and the other across-panel keys are defined on two or more
    panels; `multi_figure_page` on two or more figures. When the figure table says
    otherwise, the two halves of one answer disagree and the counted half wins --
    a key kept here would land in the frequency table and reorder the build.
    The drop is recorded rather than done quietly.
    """
    figures = analysis.get("figures") or []
    panels = max((int(f.get("panels", 1)) for f in figures), default=0)
    findings: list[Finding] = []

    def ruled_out(key: str) -> bool:
        return (key in NEEDS_PANELS and panels < 2) or (key in NEEDS_FIGURES and len(figures) < 2)

    dropped = [c["key"] for c in components_of(analysis) if ruled_out(c["key"])]
    if dropped:
        analysis["components"] = [c for c in (analysis.get("components") or ())
                                  if not (isinstance(c, dict) and ruled_out(c.get("key", "")))]
        findings.append(Finding("component_without_the_layout_it_needs",
                                f"{', '.join(dropped)} dropped: {len(figures)} figures, at most "
                                f"{panels} panel(s)"))

    known = {str(f.get("id")) for f in figures} | {"page", ""}
    stray = sorted({str(c.get("figure_id")) for c in components_of(analysis)} - known)
    if stray:
        findings.append(Finding("component_on_an_unknown_figure",
                                f"{', '.join(stray)} is not a figure id on this page"))

    bare = [c["key"] for c in components_of(analysis) if len(str(c.get("evidence", ""))) < 8]
    if bare:
        findings.append(Finding("component_without_evidence", ", ".join(bare)))
    return findings


@dataclass(frozen=True)
class Finding:
    """One disagreement between the model's answer and what the rules imply."""

    code: str
    detail: str


@dataclass
class PageResult:
    """A page's analysis, the rules it is scored on, and the checks between them."""

    stem: str
    document: str
    tags: str
    analysis: dict
    rules: list[Rule] = field(default_factory=list)
    attribution: list[str | None] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "stem": self.stem,
            "document": self.document,
            "tags": self.tags,
            **self.analysis,
            "rules": [
                {**asdict(r), "labels": list(r.labels), "figure": fig}
                for r, fig in zip(self.rules, self.attribution)
            ],
            "crosscheck": [asdict(f) for f in self.findings],
        }


_WORD = re.compile(r"[^0-9a-z]+")


def _normalize(text: str) -> str:
    return _WORD.sub("", str(text).lower())


def keys_agree(predicted: list[str], actual: tuple[str, ...]) -> bool:
    """Do the predicted addressing keys cover the labels the benchmark uses?

    Substring either way, because a prediction of `1992` for a label of `1992` and
    a prediction of `Weather-related losses` for `Weather-related` are both right;
    the benchmark itself matches labels by containment.
    """
    got = [_normalize(k) for k in predicted if len(_normalize(k)) >= 2]
    return all(any(want in have or have in want for have in got)
               for want in (_normalize(l) for l in actual) if len(want) >= 2)


def crosscheck(analysis: dict, rules: list[Rule], tags: str,
               attribution: list[str | None]) -> list[Finding]:
    """Compare the model's answer against what the rules and tags already imply.

    The labels are free evidence: the model was given each value but not the labels
    that address it, so `spot_checks[].addressing_keys` is a prediction and the rule
    grades it. A `need_estimate` tag says the values are not printed, which the
    model was not told either.
    """
    figures: list[dict] = analysis.get("figures") or []
    findings: list[Finding] = []

    if not figures:
        findings.append(Finding("no_figures", "the model found no figure on this page"))

    checks = analysis.get("spot_checks") or []
    if rules and len(checks) != len(rules):
        findings.append(Finding("spot_check_count_mismatch",
                                f"{len(rules)} values given, {len(checks)} answered"))
    placed = [(r, c) for r, c in zip(rules, checks)]
    unplaced = sum(str(c.get("figure_id")) == "not_found" for _, c in placed)
    if unplaced:
        findings.append(Finding("values_not_placed",
                                f"{unplaced} of {len(placed)} values could not be put on a mark"))
    wrong = [r.value for r, c in placed
             if str(c.get("figure_id")) != "not_found"
             and not keys_agree(list(c.get("addressing_keys") or ()), r.labels)]
    if wrong:
        findings.append(Finding(
            "addressing_keys_wrong",
            f"{len(wrong)} of {len(placed)} predicted key sets miss a rule label: "
            f"{', '.join(wrong[:6])}"))

    if rules:
        needed = max(r.arity for r in rules)
        # A figure addresses a value by panel (when it has several), by series (when
        # it has several) and by category -- at most three keys.
        available = max((int(f.get("panels", 1) > 1) + int(f.get("series", 1) > 1) + 1
                         for f in figures), default=0)
        if needed > available:
            findings.append(Finding(
                "keys_missing",
                f"rules need {needed} keys, the richest figure offers {available}"))

    unattributed = sum(a is None for a in attribution)
    if unattributed:
        findings.append(Finding(
            "unattributed_rules",
            f"{unattributed} of {len(attribution)} rules match no figure's printed names"))

    printed = {f.get("values_printed") for f in figures}
    if "need_estimate" in tags and printed == {"all"}:
        findings.append(Finding(
            "estimate_tag_but_values_printed",
            "the page is tagged need_estimate, the model says every value is printed"))
    if "need_estimate" in tags and placed and all(c.get("printed_on_figure") for _, c in placed):
        findings.append(Finding(
            "estimate_tag_but_every_value_printed",
            "the page is tagged need_estimate, every spot-check value is claimed printed"))
    if tags == "untagged" and printed == {"none"}:
        findings.append(Finding(
            "no_estimate_tag_but_values_absent",
            "no rule needs estimation, the model says no value is printed"))

    densest = max((int(f.get("marks", 0)) for f in figures), default=0)
    flagged = "dense_marks_100plus" in keys_of(analysis)
    if densest >= 100 and not flagged:
        findings.append(Finding("dense_not_flagged", f"densest figure has {densest} marks"))
    if flagged and densest < 100:
        findings.append(Finding("dense_flagged_without_marks",
                                f"dense_marks_100plus claimed, densest figure has {densest} marks"))

    for figure in figures:
        for count_key, names_key in (("panels", "panel_names"), ("series", "series_names")):
            count, names = int(figure.get(count_key, 0)), figure.get(names_key) or []
            if count > 1 and len(names) != count:
                findings.append(Finding(
                    f"{names_key}_count_mismatch",
                    f"{figure.get('id')}: {count_key}={count}, {len(names)} names"))
        if figure.get("type") == "other" and not str(figure.get("type_other", "")).strip():
            findings.append(Finding("other_type_unnamed",
                                    f"{figure.get('id')} is `other` with no name"))
    return findings
