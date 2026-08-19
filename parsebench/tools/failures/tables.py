"""Read the tables back out of a parser's page markdown, and compare cells the way
`ChartDataPointRule` does.

The official verdict is already in the run's evaluation report, so nothing here
decides pass or fail. What it decides is *why*: to say "the label the metric wanted
is sitting in the same table, two columns away" something has to find that label,
and that means re-walking the parser's output with the metric's own notion of a
match. The reimplementation is deliberately light -- `difflib` instead of
`rapidfuzz`, no colspan expansion -- and it is checked against the official verdict
on every rule, so its error rate is a reported number rather than an assumption.

The matching rules being mirrored: `parsebench/review/02_chart_metric.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

#: Suffix multipliers `numbers_match` understands.
SUFFIX = {"k": 1e3, "m": 1e6, "b": 1e9, "g": 1e9, "t": 1e12}
CURRENCY = "$€£¥"
STRIPPED = CURRENCY + "~≈%＋"
MINUS = {"−": "-", "–": "-", "—": "-"}
SPACES = {" ": " ", " ": " ", " ": " "}

_TAG = re.compile(r"<[^>]+>")
_TABLE = re.compile(r"<table[^>]*>(.*?)</table>", re.S | re.I)
_TR = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
_TD = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
_CAPTION = re.compile(r"<caption[^>]*>(.*?)</caption>", re.S | re.I)
_ALNUM = re.compile(r"[^a-z0-9]")
_NUMERIC = re.compile(r"[-+]?[\d.,]+")


@dataclass(frozen=True)
class Table:
    """One table in the parser's output, with where it sits in the page text."""

    index: int
    rows: tuple[tuple[str, ...], ...]
    start: int
    end: int
    caption: str = ""

    def cells(self):
        """(row, column, text) for every cell."""
        for r, row in enumerate(self.rows):
            for c, cell in enumerate(row):
                yield r, c, cell


def _clean(fragment: str) -> str:
    return _TAG.sub(" ", fragment).replace("&nbsp;", " ").replace("&amp;", "&").strip()


def _html_tables(text: str, first: int) -> list[Table]:
    out = []
    for match in _TABLE.finditer(text):
        body = match.group(1)
        rows = tuple(tuple(_clean(cell) for cell in _TD.findall(tr))
                     for tr in _TR.findall(body))
        rows = tuple(row for row in rows if row)
        if not rows:
            continue
        caption = _CAPTION.search(body)
        out.append(Table(first + len(out), rows, match.start(), match.end(),
                         _clean(caption.group(1)) if caption else ""))
    return out


def _markdown_tables(text: str, first: int) -> list[Table]:
    """Pipe tables. A separator row (`|---|---|`) is dropped, not counted as data."""
    out: list[Table] = []
    rows: list[tuple[str, ...]] = []
    start = 0
    for match in re.finditer(r"^.*$", text, re.M):
        line = match.group(0).strip()
        if line.startswith("|") and line.count("|") >= 2:
            if not rows:
                start = match.start()
            cells = tuple(cell.strip() for cell in line.strip("|").split("|"))
            if not all(cell and set(cell) <= set("-: ") for cell in cells):
                rows.append(cells)
        elif rows:
            if len(rows) >= 2:
                out.append(Table(first + len(out), tuple(rows), start, match.start()))
            rows = []
    if len(rows) >= 2:
        out.append(Table(first + len(out), tuple(rows), start, len(text)))
    return out


def extract_tables(text: str) -> list[Table]:
    """Every markdown and HTML table in a page of parser output, in page order."""
    html = _html_tables(text, 0)
    return sorted(html + _markdown_tables(text, len(html)), key=lambda t: t.start)


def numbers(cell: str) -> list[float]:
    """Every reading of `cell` as a number; empty when it holds none.

    A lone comma is ambiguous, so both readings are returned -- thousands separator
    and decimal point -- exactly as the metric does.
    """
    text = cell.strip()
    for char in STRIPPED:
        text = text.replace(char, "")
    for src, dst in {**MINUS, **SPACES}.items():
        text = text.replace(src, dst)
    text = text.strip()
    multiplier = 1.0
    if len(text) > 1 and text[-1].lower() in SUFFIX:
        multiplier, text = SUFFIX[text[-1].lower()], text[:-1].strip()
    text = text.replace(" ", "")
    if not text or not _NUMERIC.fullmatch(text):
        return []
    readings = {text.replace(",", "")}
    if text.count(",") == 1:
        readings.add(text.replace(",", "."))
    out = []
    for reading in readings:
        try:
            out.append(float(reading) * multiplier)
        except ValueError:
            pass
    return out


def close(a: float, b: float, tolerance: float) -> bool:
    """`numbers_match`: the denominator is the larger of the two, not the truth."""
    scale = max(abs(a), abs(b))
    return abs(a - b) <= tolerance * scale if scale else True


def relative_error(a: float, b: float) -> float:
    scale = max(abs(a), abs(b))
    return abs(a - b) / scale if scale else 0.0


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def threshold(text: str, max_diffs: int) -> float:
    return max(0.5, 1.0 - max_diffs / max(1, len(text)))


def label_hits(label: str, cell: str, bar: float) -> bool:
    """A label matches a cell by substring after stripping punctuation, or by the
    best window of `cell` scoring at least `bar` -- `partial_ratio` in the original.
    """
    lower, target = label.lower(), cell.lower()
    stripped = _ALNUM.sub("", lower)
    if stripped and stripped in _ALNUM.sub("", target):
        return True
    if not target:
        return False
    if len(lower) >= len(target):
        return ratio(lower, target) >= bar
    best = 0.0
    for i in range(len(target) - len(lower) + 1):
        best = max(best, ratio(lower, target[i:i + len(lower)]))
        if best >= bar:
            break
    return best >= bar


@dataclass
class Emphasis:
    """A bold run, markdown heading, `<caption>` or `<strong>`, and where it sits.

    Step four of the metric only accepts a label that arrives *emphasised* and
    *before* the table, so both the styling and the offset have to be kept.
    """

    offset: int
    text: str


_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_HEADING = re.compile(r"^#{1,6}\s+(.+)$", re.M)
_MARKED = re.compile(r"<h[1-6][^>]*>(.*?)</h[1-6]>|<caption[^>]*>(.*?)</caption>"
                     r"|<strong[^>]*>(.*?)</strong>|<b[^>]*>(.*?)</b>", re.S | re.I)


def emphasised(text: str) -> list[Emphasis]:
    spans = [Emphasis(m.start(), m.group(1)) for m in _BOLD.finditer(text)]
    spans += [Emphasis(m.start(), m.group(1)) for m in _HEADING.finditer(text)]
    for match in _MARKED.finditer(text):
        body = next(group for group in match.groups() if group is not None)
        spans.append(Emphasis(match.start(), body))
    return [Emphasis(span.offset, _clean(span.text)) for span in spans]


@dataclass
class Page:
    """A parsed page of output: the markdown, its tables, and its emphasised runs."""

    stem: str
    markdown: str
    tables: list[Table] = field(default_factory=list)
    emphasis: list[Emphasis] = field(default_factory=list)

    @classmethod
    def build(cls, stem: str, markdown: str) -> "Page":
        return cls(stem, markdown, extract_tables(markdown), emphasised(markdown))
