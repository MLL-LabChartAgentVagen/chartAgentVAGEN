"""Hold every number a model's report used against the program's own tables.

The models write the prose and the program owns the numbers, so the two have to be
joined somewhere. `numbers_cited` is that join: one entry per number the report
uses, with the table the model took it from. Here each entry is looked up in a flat
index of every number the program computed, and the result is recorded either way --
**a mismatch is reported, never corrected**, because the point of the check is to
say how much of a model's prose stands on the counts it was given.

The lookup is on value, not on wording: a claim is `找到` when the program's index
holds that number somewhere, and the cell it was found in is printed beside it, so a
number that is right by coincidence is visible as one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: How close a cited number has to be to count as the same number. Integers have to
#: match exactly; a rate is allowed the rounding a report would do.
INT_TOLERANCE = 0.0
RATE_TOLERANCE = 0.006

_NUMERIC = re.compile(r"-?\d+(?:[.,]\d+)?")


@dataclass(frozen=True)
class Entry:
    """One number the program computed, and the cell it sits in."""

    value: float
    where: str


def parse(text: str) -> tuple[float, bool] | None:
    """A cited value as a number, and whether it was written as a percentage."""
    match = _NUMERIC.search(str(text).replace(",", ""))
    if not match:
        return None
    try:
        value = float(match.group(0))
    except ValueError:
        return None
    return value, "%" in str(text)


def index(summary: dict, failures: dict | None) -> list[Entry]:
    """Every number in the program's tables, flattened, each with where it came from."""
    out: list[Entry] = []

    def add(value, where: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return
        out.append(Entry(float(value), where))

    for item in summary.get("components", ()):
        for model, pages in item["pages"].items():
            add(pages, f"组件表 `{item['key']}` / {model} 页数")
        for model, docs in item["documents"].items():
            add(docs, f"组件表 `{item['key']}` / {model} 文档数")
    for name, by_model in summary.get("mixes", {}).items():
        for model, counts in by_model.items():
            for value, count in counts.items():
                add(count, f"{name} / {model} / {value}")
    for name, stats in summary.get("agreement", {}).items():
        for field, value in stats.items():
            add(value * (100 if field == "rate" else 1), f"一致率表 {name} / {field}")
            if field == "rate":
                add(value, f"一致率表 {name} / {field}（小数）")
    for model, counts in summary.get("key_predictions", {}).get("per_model", {}).items():
        for field, value in counts.items():
            add(value, f"判分表 {model} / {field}")
        if counts.get("points"):
            add(counts["correct"] / counts["points"] * 100, f"判分表 {model} / 命中率")
    for row in summary.get("cost", ()):
        for field in ("calls", "input_tokens", "output_tokens", "seconds", "re_asked"):
            add(row.get(field), f"调用口径 {row['model']}{row['control'] and '·' + row['control']} / {field}")
    control = summary.get("vocabulary_control") or {}
    for field in ("keys_with_vocabulary", "keys_mapped_back", "shared"):
        add(control.get(field), f"词表控制 / {field}")
    for field in ("recall", "precision"):
        if control.get(field) is not None:
            add(control[field] * 100, f"词表控制 / {field}")
    add(len(summary.get("new_components", ())), "词表外残差 / 条数")
    add(len({row["name"] for row in summary.get("new_components", ())}),
        "词表外残差 / 去重后的名字数")
    add(len(summary.get("pages", ())), "抽样 / 页数")

    if failures:
        for field in ("pages", "points", "failures"):
            add(failures.get(field), f"失败运行 / {field}")
        for field in ("page_mean", "ceiling"):
            add(failures.get(field, 0) * 100, f"失败运行 / {field}")
        for row in failures.get("forms", ()):
            add(row["count"], f"形态表 `{row['form']}` / 个数")
            add(row["share"] * 100, f"形态表 `{row['form']}` / 占失败")
            for home, count in row["homes"].items():
                add(count, f"形态表 `{row['form']}` / 失联键去向 {home}")
        addressing = sum(row["share"] for row in failures.get("forms", ())
                         if row["form"] in ("label_unlinked", "row_missing"))
        add(addressing * 100, "形态表 / 寻址失败合计")
        for row in failures.get("single_variable", ()):
            add(row["rate"] * 100, f"单变量 {row['variable']} / {row['bucket']} 通过率")
            add(row["n"], f"单变量 {row['variable']} / {row['bucket']} n")
        for row in failures.get("component_deltas", ()):
            add(row["delta"] * 100, f"控制组差值 `{row['key']}` / 差")
            add(row["with"]["rate"] * 100, f"控制组差值 `{row['key']}` / 有它的通过率")
    return out


_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_.]{3,}")
_CJK = re.compile(r"[\u4e00-\u9fff]{2,}")


def _tokens(text: str) -> set[str]:
    """The words a claim and a cell name can be tied by: identifiers, and Chinese
    bigrams. Both halves are written half in English and half in Chinese -- a claim
    reading `卡在哪一步的三家一致率` and a cell reading `一致率表 卡在哪一步 / rate`
    share nothing at all unless the Chinese is compared too."""
    out = {t.lower() for t in _TOKEN.findall(str(text))}
    for run in _CJK.findall(str(text)):
        out |= {run[i:i + 2] for i in range(len(run) - 1)}
    return out


def relatedness(claim: str, where: str) -> float:
    """How much this cell's name has in common with what the claim counts.

    An identifier counts double -- a vocabulary key or a model name is specific,
    where a Chinese bigram like `页数` is in half the cells. Zero means nothing is
    shared, and the number is then reported as existing somewhere rather than as
    the claimed cell.
    """
    shared = _tokens(claim) & _tokens(where)
    return sum(2.0 if token.isascii() else 1.0 for token in shared)


def look_up(value: float, percent: bool, entries: list[Entry],
            claim: str = "", model: str = "") -> tuple[Entry | None, bool]:
    """The program's cell holding this number, and whether it is the claimed cell.

    The second half of the answer is the cell whose name has the most in common with
    the claim, which is a guess at where the number came from and is printed as one.
    It cannot be more than a guess: nothing in the answer says which cell was read,
    and with a few hundred small integers in the tables `7` is somewhere whatever it
    was supposed to count. Whether a value match means anything is `decisive`, not
    this.

    A rate written as `0.72` and one written as `72%` are the same claim, so a
    fraction below one is tried at both scales.
    """
    candidates = [value] + ([value * 100] if not percent and abs(value) <= 1 else [])
    best: Entry | None = None
    tied: Entry | None = None
    tied_score = 0.0
    for candidate in candidates:
        tolerance = RATE_TOLERANCE * max(1.0, abs(candidate)) \
            if candidate != int(candidate) else INT_TOLERANCE
        for entry in entries:
            if abs(entry.value - candidate) > tolerance + 1e-9:
                continue
            if best is None or len(entry.where) < len(best.where):
                best = entry
            #: Between two cells that both name the claim, the model's own column.
            score = relatedness(claim, entry.where) + (
                0.5 if model and model.lower() in entry.where.lower() else 0.0)
            if score > 0 and score > tied_score:
                tied, tied_score = entry, score
    return (tied, True) if tied else (best, False)


#: Above this an integer is specific enough that finding it is worth something.
#: Below it, `7` is in the tables whatever it was supposed to count.
DECISIVE_INTEGER = 200


def decisive(value: float) -> bool:
    """Would finding this number in the tables mean anything?

    A rate carrying a decimal, or a large count, appears in one cell or in none. A
    small integer appears in dozens, so its being found is not evidence that the
    report was written against the tables, and the check says so rather than
    counting it.
    """
    return value != int(value) or abs(value) >= DECISIVE_INTEGER


def reconcile(cited: list[dict], entries: list[Entry], model: str = "") -> list[dict]:
    """One row per cited number: does the program hold it, and does that mean anything.

    `找到` says the number is in the program's tables. It is evidence only when the
    number is `decisive` -- a rate or a large count. The cell named beside it is the
    one whose name has the most in common with the claim, which is a guess: nothing
    in a model's answer records which cell it read. A number the program never
    computed is recorded and **not corrected**.
    """
    rows = []
    for item in cited:
        parsed = parse(item.get("value", ""))
        found, tied = look_up(*parsed, entries, str(item.get("claim", "")), model) \
            if parsed else (None, False)
        rows.append({"claim": item.get("claim", ""), "value": item.get("value", ""),
                     "source": item.get("source", ""),
                     "status": "找到" if found else "没找到",
                     "found": bool(found), "tied": tied,
                     "decisive": bool(parsed) and decisive(parsed[0]),
                     "where": found.where if found else ""})
    return rows
