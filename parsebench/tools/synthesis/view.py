"""The merged view: one page that carries the whole argument and its evidence.

The written report is `synthesis/INDEX.md`; this is the same argument with the pages
attached. Every claim in it is one of three kinds, and each kind gets a card: a gap
the benchmark has and the spec does not (page image + the words the model wrote when
it counted it), a failure the parser produced (page image + the table it actually
wrote, marked, beside the long table that would have passed), and a chart type the
condition table has no row for.

Prose and tables come from `INDEX.md` / `INDEX.en.md` -- one source, so the written
and the illustrated report cannot say different things -- and the card galleries are
spliced in after the heading they belong to. Nothing is fetched at view time and
nothing is read from the two analyses' own directories, because the merged report is
meant to be readable on its own.
"""

from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

PARSEBENCH = Path(__file__).resolve().parents[2]
#: Both tool packages use bare module names and both define an `index` and a
#: `viewer`. Analysis goes on first so those two resolve to the page analysis, which
#: is the one this module reads; nothing here imports either module from `failures/`.
for package in ("failures", "analysis"):
    sys.path.insert(0, str(PARSEBENCH / "tools" / package))

import evidence as ev  # noqa: E402
from checks import PageResult, evidence_of  # noqa: E402
from content import AXES, BASIS_EN, CASES, FACTS, KEY_AXIS, TYPE_GAPS, UI  # noqa: E402
from data import Sources  # noqa: E402
from index import band, countable_figures, generality  # noqa: E402
from markdown import PLACEMENT_ZH, PRINTED_ZH  # noqa: E402
from vocabulary import BY_KEY  # noqa: E402

PLACEMENT_EN = {"above": "above the plot", "beside": "beside the plot",
                "below": "below the plot", "inside": "inside the plot", "none": "no heading"}
PRINTED_EN = {"all": "all", "some": "some", "none": "none"}
BAND_EN = {"高": "high", "中": "mid", "低": "low"}
GEN_EN = {"通用": "general", "常见": "common", "集中": "concentrated", "样本不足": "too few pages"}
FIG_ZH = ("面板", "系列", "类目", "图元", "数值写出")
FIG_EN = ("panels", "series", "categories", "marks", "values printed")


def t(pair, lang: str) -> str:
    return pair[0] if lang == "zh" else pair[1]


# ------------------------------------------------------------------ markdown

CELL_SPLIT = re.compile(r"(?<!\\)\|")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
STRONG = re.compile(r"\*\*(.+?)\*\*")
TICKS = re.compile(r"`([^`]+)`")
DROP = re.compile(r"[^\w一-鿿 \-]", re.UNICODE)


def slug(text: str) -> str:
    """The anchor GitHub would give this heading, so INDEX.md's own links resolve."""
    plain = TICKS.sub(r"\1", STRONG.sub(r"\1", LINK.sub(r"\1", text)))
    return DROP.sub("", plain.strip().lower()).replace(" ", "-")


def rich(text: str) -> str:
    """Escape first, then the small markdown the sources are written in."""
    out = escape(text.replace("\\|", "|"))
    out = LINK.sub(lambda m: f'<a href="{escape(m.group(2), quote=True)}">{m.group(1)}</a>', out)
    out = STRONG.sub(r"<strong>\1</strong>", out)
    return TICKS.sub(r"<code>\1</code>", out)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]]


def _table(rows: list[str]) -> str:
    head, align, body = _cells(rows[0]), _cells(rows[1]), [_cells(r) for r in rows[2:]]
    numeric = ["num" if a.endswith(":") and not a.startswith(":") else "" for a in align]
    klass = ' class="kv"' if not any(head) and len(head) == 2 else ""
    out = [f'<div class="scroll"><table{klass}><thead><tr>']
    out += [f'<th class="{numeric[i]}">{rich(c)}</th>' for i, c in enumerate(head)]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(
            f'<td class="{numeric[i] if i < len(numeric) else ""}">{rich(c)}</td>'
            for i, c in enumerate(row)) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


def _block(lines: list[str]) -> str:
    if not lines:
        return ""
    if lines[0].startswith("|"):
        return _table(lines)
    if lines[0].startswith(">"):
        return "<blockquote>" + "".join(
            f"<p>{rich(l.lstrip('> ').rstrip())}</p>" for l in lines if l.strip(" >")
        ) + "</blockquote>"
    if re.match(r"^(-|\d+\.)\s", lines[0]):
        tag = "ul" if lines[0].startswith("-") else "ol"
        items, current = [], ""
        for line in lines:
            if re.match(r"^(-|\d+\.)\s", line):
                if current:
                    items.append(current)
                current = re.sub(r"^(-|\d+\.)\s+", "", line)
            else:
                current += " " + line.strip()
        items.append(current)
        return f"<{tag}>" + "".join(f"<li>{rich(i)}</li>" for i in items) + f"</{tag}>"
    return f"<p>{rich(' '.join(l.strip() for l in lines))}</p>"


def markdown(body: str) -> str:
    out, block = [], []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---":
            out.append(_block(block))
            block = []
            continue
        if stripped.startswith("#### "):
            out.append(_block(block))
            block = []
            out.append(f"<h4>{rich(stripped[5:])}</h4>")
            continue
        if block and stripped.startswith("|") != block[0].startswith("|"):
            out.append(_block(block))
            block = []
        block.append(line)
    out.append(_block(block))
    return "".join(out)


# --------------------------------------------------------------------- cards


def _img(stem: str, lang: str) -> str:
    src = f"assets/{quote(stem)}.jpg"
    return (f'<a href="{src}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="{src}" alt="{escape(stem)}"'
            f' onerror="this.closest(\'article\').classList.add(\'no-image\')"></a>'
            f'<p class="hint">{t(UI["noimg"], lang)}</p>')


def _figure_lines(page: PageResult, lang: str) -> str:
    """The example page's figures, as the model reported them.

    A count says the key was seen; this says what was on the page when it was seen.
    Headings print split into their five fields, because five of the gaps are about
    how a heading is built and none reads without the words themselves.
    """
    names = FIG_ZH if lang == "zh" else FIG_EN
    printed = PRINTED_ZH if lang == "zh" else PRINTED_EN
    placement = PLACEMENT_ZH if lang == "zh" else PLACEMENT_EN
    heads = (("图号", "figure no."), ("标题", "title"), ("副标题", "subtitle"), ("单位", "unit"))
    keys = ("figure_number", "title", "subtitle", "unit_text")
    rows = []
    for figure in countable_figures(page):
        kind = str(figure.get("type"))
        if kind == "other" and str(figure.get("type_other", "")).strip():
            kind = f"other · {figure['type_other']}"
        facts = (f"<code>{escape(kind)}</code> · "
                 + " · ".join(f"{figure.get(k)} {n}" for k, n in
                              zip(("panels", "series", "categories", "marks"), names))
                 + f" · {names[4]}: {printed.get(figure.get('values_printed'), '?')}")
        head, lines = figure.get("heading") or {}, []
        for label, key in zip(heads, keys):
            if str(head.get(key, "")).strip():
                lines.append(f"{t(label, lang)}: {escape(str(head[key]).strip())}")
        where = placement.get(str(head.get("placement", "")), "")
        if where:
            lines.append(f"{'标题块' if lang == 'zh' else 'heading block'}: {where}")
        ticks = str(figure.get("value_axis_ticks", "")).strip()
        if ticks:
            lines.append(f"{'值轴刻度' if lang == 'zh' else 'value axis ticks'}: {escape(ticks)}")
        for label, key, cap in ((("面板", "panels"), "panel_names", 6),
                                (("系列", "series"), "series_names", 6),
                                (("类目", "categories"), "category_names", 8)):
            values = [str(n) for n in (figure.get(key) or ()) if str(n).strip()]
            if values:
                shown = " / ".join(escape(n) for n in values[:cap])
                lines.append(f"{t(label, lang)}: {shown}{' …' if len(values) > cap else ''}")
        rows.append(f'<span class="fig">{facts}' + "".join(f"<br>{n}" for n in lines) + "</span>")
    return "".join(rows)


BAND_CLASS = {"高": "hi", "中": "mid", "低": ""}
GEN_CLASS = {"通用": "yes", "常见": "mid", "集中": "", "样本不足": ""}
SUPER = str.maketrans("-0123456789", "\u207b\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")


def _power(scale: float) -> str:
    """`×10⁹` rather than `×1e+09` -- the note is read, not parsed."""
    import math
    return f"×10{str(round(math.log10(scale))).translate(SUPER)}"


def _chips(key: str, pages: int, total: int, docs: int, total_documents: int,
           verdict: tuple[str, str], lang: str) -> str:
    """Band, which judging steps it can change, and how far it reaches beyond one publisher."""
    component = BY_KEY[key]
    name = band(pages, total)
    chips = [f'<span class="chip {BAND_CLASS[name]}">'
             f'{escape(name if lang == "zh" else BAND_EN[name])}</span>']
    if component.affects:
        chips += [f'<span class="chip yes">{t(UI["steps"], lang).format(n)}</span>'
                  for n in component.affects]
    else:
        chips.append(f'<span class="chip">{t(UI["nostep"], lang)}</span>')
    kind, _ = verdict
    label = kind if lang == "zh" else GEN_EN[kind]
    reach = min(pages, total_documents)
    number = (f"{docs} 份" if lang == "zh" else f"{docs} docs") if not reach else (
        f"{docs} / 最多 {reach} 份 = {docs / reach:.2f}" if lang == "zh"
        else f"{docs} of at most {reach} docs = {docs / reach:.2f}")
    chips.append(f'<span class="chip {GEN_CLASS[kind]}">'
                 f'{escape(label)} · {escape(number)}</span>')
    return "".join(chips)


def _absent_card(key, component, total: int, lang: str) -> str:
    """A gap the sample never showed. Absent is a finding, so it still gets a row."""
    none = ("这份抽样的 {} 页里一次也没出现——不是「不重要」，是「这批页面读不出来」。",
            "Not once in the {} sampled pages -- which is \"this sample cannot tell\", "
            "not \"unimportant\".")
    return f"""<article class="card" id="gap-{escape(key, quote=True)}">
  <header><span class="chip">{escape("未出现" if lang == "zh" else "not seen")}</span>
    <code>{escape(key)}</code>
    <h3>{rich(component.name_zh if lang == "zh" else component.name_en)}</h3>
    <span class="tally">0 / {total} {t(UI["pages"], lang)}</span>
  </header>
  <div class="split"><div class="prose" style="border-right:0">
    <p><span class="label">{t(UI["evidence"], lang)}</span>
       <span class="quote">{escape(t(none, lang).format(total))}</span></p>
    <p><span class="label">{t(UI["criterion"], lang)}</span>
       <span class="criterion">{rich(component.hint)}</span></p>
    <p><span class="label">{t(UI["why"], lang)}</span>
       {rich(component.basis if lang == "zh" else BASIS_EN[key])}</p>
  </div></div>
</article>"""


def gap_card(key: str, sources: Sources, examples: dict[str, list[PageResult]],
             counts, documents, lang: str) -> str:
    """One construct the benchmark has and the current spec cannot draw."""
    component, total = BY_KEY[key], len(sources.pages)
    pages = counts[key]
    sample = examples.get(key) or []
    if not sample:
        return _absent_card(key, component, total, lang)
    first, others = sample[0], sample[1:]
    verdict = generality(pages, documents[key], sources.documents)
    price = sources.stat_component(key)
    price_html = ""
    if price and price.get("separated"):
        price_html = (
            f'<p class="price"><span class="label">{t(UI["price"], lang)}</span>'
            f'<b>{price["delta"]:+.1%}</b> · {price["with"][1]:.1%} (n={price["with"][0]}) vs '
            f'{price["without"][1]:.1%} · {price["pages"]} {t(UI["pages"], lang)} / '
            f'{price["documents"]} {t(UI["docs"], lang)}</p>')
    proof = evidence_of(first.analysis, key) or "—"
    more = " · ".join(escape(p.stem) for p in others)
    return f"""<article class="card" id="gap-{escape(key, quote=True)}">
  <header>{_chips(key, pages, total, len(documents[key]), sources.documents, verdict, lang)}
    <code>{escape(key)}</code>
    <h3>{rich(component.name_zh if lang == "zh" else component.name_en)}</h3>
    <span class="tally"><span class="meter"><i style="width:{pages / total:.0%}"></i></span>
      {pages} / {total} {t(UI["pages"], lang)} · {pages / total:.0%}</span>
  </header>
  <div class="split">
    <div class="prose">
      <p><span class="label">{t(UI["evidence"], lang)}</span>
         <span class="quote">{escape(proof)}</span></p>
      <p><span class="label">{t(UI["criterion"], lang)}</span>
         <span class="criterion">{rich(component.hint)}</span></p>
      <p><span class="label">{t(UI["why"], lang)}</span>
         {rich(component.basis if lang == "zh" else BASIS_EN[key])}</p>
      {price_html}
      <p><span class="label">{t(UI["figures"], lang)}</span>{_figure_lines(first, lang)}</p>
      {f'<p><span class="label">{t(UI["also"], lang)}</span>{more}</p>' if others else ''}
    </div>
    <figure>{_img(first.stem, lang)}
      <figcaption>{escape(first.stem)}</figcaption></figure>
  </div>
</article>"""


def _caption(caption: str, lang: str) -> str:
    """`evidence.build` writes its caption in Chinese; the numbers carry to English."""
    if lang == "zh":
        return caption
    n = [int(x) for x in re.findall(r"\d+", caption)]
    if len(n) >= 4:
        return f"Parser table {n[0]} of {n[1]}, rows {n[2]}–{n[3]}"
    return f"Parser table {n[0]}, rows {n[1]}–{n[2]}"


def _note(rule, diagnosis, lang: str) -> str:
    """Why this point failed, said the same way in both languages.

    Re-derived rather than taken from `evidence.note`, so the two pages cannot end
    up asserting different things about the same cell.
    """
    #: `Diagnosis.homes` is keyed lowercase; print the rule's own spelling back.
    spelling = {label.lower(): label for label in rule.labels}
    lost = [spelling.get(name.lower(), name) for name in (diagnosis.homes or ())]
    lower = {n.lower() for n in lost}
    found = [label for label in rule.labels if label.lower() not in lower]
    code = lambda names: "、".join(f"`{n}`" for n in names) if lang == "zh" \
        else ", ".join(f"`{n}`" for n in names)
    if diagnosis.kind == "label_unlinked":
        parts = ["值落在标出来的那一格" if lang == "zh" else "the value sits in the marked cell"]
        if found:
            parts.append(code(found) + (" 在同一行" if lang == "zh" else " are on that row"))
        if lost:
            parts.append(code(lost) + (" 不在这一行、这一列，也不在表头" if lang == "zh"
                                       else " are on neither its row, its column, nor the header"))
        return "；".join(parts) if lang == "zh" else "; ".join(parts)
    if diagnosis.kind == "row_missing":
        absent = code(diagnosis.absent_labels)
        return (f"这个值不在任何表里；{absent} 一个字都没进表" if lang == "zh"
                else f"the value is in no table; {absent} never reached one at all")
    shown = f"{diagnosis.model_value:g}" if diagnosis.model_value is not None else "—"
    if diagnosis.kind == "unit_mismatch":
        power = _power(diagnosis.scale) if diagnosis.scale else ""
        return (f"键指向的格子写着 {shown}，标注值是 `{rule.value}`——度量把它读成差 {power}"
                if lang == "zh" else
                f"the addressed cell reads {shown} against a labelled `{rule.value}` -- "
                f"the metric reads them {power} apart")
    if diagnosis.kind == "value_off" and diagnosis.error is not None:
        return (f"键指向的格子写着 {shown}，标注值是 `{rule.value}`，相对差 "
                f"{diagnosis.error:.0%}，该点容差 {rule.tolerance:g}" if lang == "zh" else
                f"the addressed cell reads {shown} against a labelled `{rule.value}`, a relative "
                f"gap of {diagnosis.error:.0%} on a point whose tolerance is {rule.tolerance:g}")
    return ("定位键都在表里，但没有任何格子放着这个数" if lang == "zh"
            else "every key is in the table and no cell holds this number")


def _bad_headers(item: ev.Evidence) -> set[int]:
    """Header cells over a column of numbers that name none of the keys.

    Where the label should have been: the value's column is a data column and its
    header is supposed to say which series it is. `Gray` / `Orange` light up.
    """
    if len(item.rows) < 2:
        return set()
    head, numeric = item.rows[0], set()
    for column in range(len(head)):
        values = [row[column].text for row in item.rows[1:] if column < len(row)]
        hits = sum(1 for text in values if _numeric(text))
        if values and hits >= max(2, len(values) // 2):
            numeric.add(column)
    return {c for c in numeric if c < len(head) and head[c].kind not in ("key", "hit")}


def _numeric(text: str) -> bool:
    body = text.strip().replace(",", "").replace("%", "").replace("$", "")
    body = body.lstrip("-−–").rstrip("xX")
    return bool(body) and body.replace(".", "", 1).replace(" ", "").isdigit()


def _excerpt(item: ev.Evidence, mark: set[int], lang: str) -> str:
    rows = '<tr><td colspan="99" class="head">⋮</td></tr>' if item.elided_above else ""
    for index, line in enumerate(item.rows):
        cells = ""
        for column, cell in enumerate(line):
            kind = cell.kind
            if index == 0 and column in mark and cell.text.strip():
                kind = "wrong"
            cells += f'<td class="{kind}">{escape(ev.tidy(cell.text))}</td>'
        if item.elided_right:
            cells += '<td class="head">…</td>'
        rows += f"<tr>{cells}</tr>"
    return (f'<p class="grid-cap">{escape(_caption(item.caption, lang))}</p>'
            f'<div class="scroll"><table class="excerpt"><tbody>{rows}</tbody></table></div>')


def _expected(want: ev.Expected, lang: str) -> str:
    if not want.rows:
        return ""
    header = want.header if lang == "zh" else \
        [f"key {i + 1}" for i in range(len(want.header) - 1)] + ["value"]
    head = "".join(f'<td class="head">{escape(name)}</td>' for name in header)
    body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>"
                   for row in want.rows)
    more = (f'<tr><td colspan="{len(header)}" class="head">'
            + (f"⋮ 还有 {want.more} 行" if lang == "zh" else f"⋮ {want.more} more rows")
            + "</td></tr>") if want.more else ""
    return (f'<div class="scroll"><table class="excerpt good"><tbody>'
            f"<tr>{head}</tr>{body}{more}</tbody></table></div>")


def case_card(note, sources: Sources, lang: str) -> str:
    """One page the parser failed on: what it wrote, and what would have passed."""
    from data import failure_evidence
    found = failure_evidence(sources, note.stem, note.kind)
    if not found:
        return ""
    focus, diagnosis, item, want, passed, total = found
    mark = _bad_headers(item) if diagnosis.kind == "label_unlinked" else set()
    keys = " · ".join(f"<code>{escape(label)}</code>" for label in focus.rule.labels)
    axis = next(a for a in AXES if a.id == note.axis)
    return f"""<article class="ev" id="case-{escape(note.stem, quote=True)}">
  <figure>{_img(note.stem, lang)}</figure>
  <div class="body">
    <p class="axis-tag"><b>{axis.id.upper()}</b> {escape(t((axis.zh, axis.en), lang))}</p>
    <h4>{rich(t((note.mech_zh, note.mech_en), lang))}</h4>
    <p class="meta"><code>{escape(note.stem)}</code> ·
      {t(UI["page_score"], lang).format(a=passed, b=total)}</p>
    <p class="says"><span class="label">{t(UI["says"], lang)}</span>
      {rich(t((note.says_zh, note.says_en), lang))}</p>
  </div>
  <div class="vs">
    <div class="bad">
      <p class="side-h">{t(UI["wrote"], lang)}</p>
      <p class="rule-line">{t(UI["rule_line"], lang).format(
          v=f"<b>{escape(focus.rule.value)}</b>", k=keys, t=f"{focus.rule.tolerance:g}")}</p>
      {_excerpt(item, mark, lang)}
      <p class="why"><b>{rich(_note(focus.rule, diagnosis, lang))}</b></p>
    </div>
    <div class="good">
      <p class="side-h">{t(UI["pass"], lang)}</p>
      {_expected(want, lang)}
      <p class="why">{rich(t(UI["long_note"], lang))}</p>
    </div>
  </div>
  <p class="tail">{t(UI["verdict"], lang)}: {escape(focus.explanation[:200])}</p>
</article>"""


def type_card(name: str, sources: Sources, lang: str) -> str:
    """One chart type the condition table has no row for."""
    entry = next((e for e in TYPE_GAPS if e[0] == name), None)
    if entry is None:
        return ""
    sample = None
    for page in sorted(sources.pages, key=lambda p: (len(countable_figures(p)), p.stem)):
        match = next((f for f in countable_figures(page)
                      if str(f.get("type")) == name), None)
        if match:
            sample = (page, match)
            break
    if not sample:
        return ""
    page, figure = sample
    count = sum(1 for p in sources.pages for f in countable_figures(p)
                if str(f.get("type")) == name)
    named = str(figure.get("type_other", "")).strip()
    head = figure.get("heading") or {}
    title = " ".join(str(head.get(k, "")).strip() for k in ("figure_number", "title")
                     if str(head.get(k, "")).strip())
    return f"""<article class="card">
  <header><span class="chip hi">{'类型缺口' if lang == 'zh' else 'type gap'}</span>
    <code>{escape(name)}{f" · {escape(named)}" if named else ""}</code>
    <span class="tally">{count} {'张' if lang == 'zh' else 'figures'} ·
      {escape(t((entry[3], entry[4]), lang))}</span>
  </header>
  <div class="split">
    <div class="prose">
      <p><span class="label">{'这一页上是什么' if lang == 'zh' else 'What is on this page'}</span>
         <span class="quote">{escape(title) or "—"}</span></p>
      <p><span class="label">{t(UI["why"], lang)}</span>{rich(t((entry[1], entry[2]), lang))}</p>
      <p><span class="label">{t(UI["figures"], lang)}</span>{_figure_lines(page, lang)}</p>
    </div>
    <figure>{_img(page.stem, lang)}
      <figcaption>{escape(page.stem)}</figcaption></figure>
  </div>
</article>"""
