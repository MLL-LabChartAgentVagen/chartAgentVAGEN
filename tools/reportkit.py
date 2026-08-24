"""The pieces both generated sites are built out of: page shell, tables, images.

Two things are written from the artifacts of a run -- the one-page report beside the
plan, and the review site with a page per stage and a page per chart type. They share
a stylesheet, an image encoder and a dozen small builders, so those live here rather
than in one of them.

The stylesheet is lifted out of `plan/plan.html` at build time: the pages are meant
to look like the plan they are evidence for, and copying it would let the two drift.
"""

from __future__ import annotations

import base64
import html
import io
from pathlib import Path
from typing import Any, Sequence

from chartgen.interfaces.record import Record

ROOT = Path(__file__).resolve().parents[1]

#: Embedded images: JPEG at this width and quality. Small enough that forty of them
#: fit in one file, large enough to read a tick label off.
IMAGE_WIDTH = 900
IMAGE_QUALITY = 80

#: Contact-sheet images. Small enough that a hundred of them fit in one file: the
#: point of a wall is what the batch looks like, and a page carries the full-size
#: version of anything worth reading a number off.
THUMB_WIDTH = 300

#: Box colours drawn back onto an image: a value target, a localisation target only,
#: and the page furniture around them.
VALUE_BOX = (196, 60, 40)
PLACE_BOX = (130, 130, 140)
PAGE_BOX = (46, 106, 85)


# ---------------------------------------------------------------- text

def esc(value: Any) -> str:
    return html.escape(str(value))


def table(header: Sequence[Any], rows: Sequence[Sequence[Any]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return (f'<div class="scroll"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def band(title: str, note_text: str = "", anchor: str = "") -> str:
    at = f' id="{anchor}"' if anchor else ""
    return (f'<div class="band"{at}><h2>{esc(title)}</h2>'
            + (f"<span>{esc(note_text)}</span>" if note_text else "") + "</div>")


def card(title: str, body: str, ident: str = "", size: str = "") -> str:
    return (f'<div class="card"><header><h3>{esc(title)}</h3>'
            + (f'<span class="id">{esc(ident)}</span>' if ident else "")
            + (f'<span class="size">{esc(size)}</span>' if size else "")
            + f'</header><div class="body">{body}</div></div>')


def note(text: str) -> str:
    return f'<p class="note">{text}</p>'


def code(text: str) -> str:
    return f'<pre class="tree">{esc(text)}</pre>'


def tags(names: Sequence[str], lit: Sequence[str] = ()) -> str:
    """Names as chips. The ones not in `lit` are greyed, which is how a table shows
    what was available beside what was used."""
    keep = set(lit) if lit else set(names)
    return " ".join(f'<span class="tag{"" if n in keep else " g"}">{esc(n)}</span>'
                    for n in names)


def bar(fraction: float) -> str:
    """A share, as a number and a bar. Reading twenty of these as bare decimals is
    what the bar is for."""
    return (f'<span class="bar"><i class="d" style="width:{fraction * 100:.0f}%"></i></span>'
            f'<span class="n">{fraction:.0%}</span>')


def num(value: Any) -> str:
    return f'<span class="n">{esc(value)}</span>'


# ---------------------------------------------------------------- images

def embed(path: Path, boxes: Record | None = None, width: int = IMAGE_WIDTH) -> str:
    """One image as a data URI, optionally with the recorded boxes drawn back onto it.

    Drawing the boxes back is how a person checks the thing the self-checks check:
    the red ones carry a value target, the grey ones only a position, the green ones
    are page furniture.
    """
    from PIL import Image, ImageDraw

    if not Path(path).exists():
        return ""
    img = Image.open(path).convert("RGB")
    if boxes is not None:
        draw = ImageDraw.Draw(img)
        for element in boxes.elements:
            draw.rectangle(list(element.box.as_tuple()), outline=PAGE_BOX, width=1)
        for mark in boxes.marks:
            draw.rectangle(list(mark.box.as_tuple()),
                           outline=VALUE_BOX if mark.readable else PLACE_BOX, width=2)
    if img.width > width:
        img = img.resize((width, int(img.height * width / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=IMAGE_QUALITY, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


#: Which language the shared pieces write in. A builder sets it before calling them:
#: the review site is English, and the one-page report is built in both.
LANG = "zh"


def tr(zh: str, en: str) -> str:
    """One string in two languages, kept side by side so they cannot drift apart."""
    return en if LANG == "en" else zh


#: The one drawing this page does not author: it is lifted whole out of the plan, which
#: is written in Chinese. Its labels are translated on the way through rather than the
#: figure being redrawn, so the two versions of the page cannot show different diagrams.
FLOW_EN = {
    "\u2460\u5199\u573a\u666f\u3001\u751f\u6210\u811a\u672c\u4e0e\u610f\u56fe\uff1b":
        "(1) writes the scenario, the generating script and the intents; ",
    "\u2461\u5728\u56fe\u5df2\u7ecf\u9009\u5b9a\u4e4b\u540e\uff0c\u7ed9\u8fd9\u4e00"
    "\u6279\u56fe\u5199\u6807\u9898\u4e0e\u5217\u7684\u6563\u6587\u540d\u3002\u9009"
    "\u56fe\u3001\u6295\u5f71\u3001\u7ec4\u7248\u3001\u6e32\u67d3\u3001\u8bb0\u5f55"
    "\u3001\u5bfc\u51fa\u5168\u90e8\u662f\u7a0b\u5e8f\u3002":
        "(2) after the figures are chosen, writes their titles and readable column names. "
        "Choosing, projecting, composing, rendering, recording and exporting are all "
        "program.",
    "\u4e24\u6b21\u8c03\u7528\u90fd\u4e0d\u4ea7\u51fa\u4efb\u4f55\u6570\u503c\u3002":
        "Neither call produces a single number.",
    "\u6bcf\u4e2a\u9636\u6bb5\u662f\u4e00\u4e2a\u51fd\u6570":
        "Every stage is a function",
    "\u9636\u6bb5(\u4e0a\u6e38\u4ea7\u7269, \u79cd\u5b50, \u914d\u7f6e) -":
        "stage(upstream artifact, seed, config) -",
    "\u4e0b\u6e38\u4ea7\u7269": "downstream artifact",
    "\u3002\n    \u540c\u6837\u7684\u8f93\u5165\u5fc5\u5f97\u540c\u6837\u7684\u8f93"
    "\u51fa\uff0c\u4ea7\u7269\u6309\u5185\u5bb9\u54c8\u5e0c\u843d\u76d8\uff0c\u4efb"
    "\u4f55\u9636\u6bb5\u53ef\u4ee5\u5355\u72ec\u91cd\u8dd1\uff0c\n    \u4e5f\u53ef"
    "\u4ee5\u62ff ":
        ". The same input always gives the same output, artifacts are written under a "
        "content hash, any stage can be rerun on its own, and a stage can be developed "
        "against the sample files in ",
    "\u7684\u6837\u4f8b\u6587\u4ef6\u5355\u72ec\u5f00\u53d1\u3002":
        " on its own.",
    "\u9886\u57df\u6c60 \u2192 \u4e8b\u5b9e\u8868": "domain pool \u2192 fact table",
    "\u9009\u56fe \uff0b \u5199\u6807\u9898": "choose figures + write the words",
    "\u8fb9\u753b\u8fb9\u8bb0": "recorded while drawing",
    "\u4e09\u5c42\u62fc\u63a5 \uff0b \u81ea\u68c0":
        "three layers joined + self-checks",
    "\u8bad\u7ec3\u76ee\u6807": "training targets",
    "\u8c03\u7528\u2460\u3000\u5199\u6570\u636e": "call (1)\u2003writes the data",
    "\u8c03\u7528\u2461\u3000\u56fe\u9009\u5b9a\u540e\u5199\u5b57":
        "call (2)\u2003writes the words, after the figures are chosen",
    "\u4e5d\u7c7b\u6587\u4ef6": "nine kinds of file",
    "\u8d2f\u7a7f\u793a\u4f8b": "the running example",
    "\u884c\u5c31\u8bca\u8bb0\u5f55": " visit records",
    "\u6807\u9898\u300c\u5404\u9662\u5e73\u5747\u5019\u8bca\u65f6\u957f\u300d":
        'title "Average wait by hospital"',
    "\u7ed8\u56fe\u533a [96,60,860,520]": "plotting area [96,60,860,520]",
    "\u503c\u57df [0,60] \u2194 \u50cf\u7d20 [520,60]":
        "value range [0,60] \u2194 pixels [520,60]",
    "\u7684\u6761 [168,196,278,520]": " bar [168,196,278,520]",
    "\u4e09\u9879\u81ea\u68c0\u901a\u8fc7": "all three self-checks passed",
    "\u5e26\u4f4d\u7f6e\u7684\u8868 \u00b7 \u62bd\u67e5\u96c6":
        "grounded table \u00b7 spot checks",
    "\u5b9a\u4f4d \u00b7 \u8bfb\u503c \u00b7 \u4e0b\u94bb":
        "locate \u00b7 read \u00b7 drill down",
    "\u9875\u9762\u5143\u7d20 \u00b7 \u56fe\u4f8b\u7ed1\u5b9a":
        "page elements \u00b7 legend binding",
    "\u8f93\u51fa\u5355\u4f4d \uff1d (": "output unit = (",
    "\uff0cx\uff1dhospital": ", x=hospital",
    "\uff1dAVG(wait)": "=AVG(wait)",
    "\uff1d372": "=372",
    "\uff1dtrue": "=true",
    "\uff1a": ": ",
    # The figure's own accessible name, which a screen reader reads out.
    "\u4e94\u4e2a\u9636\u6bb5\u7684\u6570\u636e\u6d41":
        "the data flow across the five stages",
}


def flow_diagram() -> str:
    """The plan's own data-flow drawing, taken out of it rather than redrawn.

    Both site builders show this figure, so it lives here rather than in
    either of them.
    """
    text = (ROOT / "plan" / "plan.html").read_text(encoding="utf-8")
    marker = 'aria-label="五个阶段的数据流"'
    start = text.rindex("<figure", 0, text.index(marker))
    figure = text[start:text.index("</figure>", start) + len("</figure>")]
    if LANG != "en":
        return figure
    # Longest first, in one pass, so a short label cannot cut into a longer one.
    for zh in sorted(FLOW_EN, key=len, reverse=True):
        figure = figure.replace(zh, FLOW_EN[zh])
    return figure


def image(path: Path, boxes: Record | None = None, width: int = IMAGE_WIDTH) -> str:
    src = embed(path, boxes, width)
    return (f'<img src="{src}" alt="figure" style="width:100%;display:block">'
            if src else "")


def figure_pair(record: Record, caption: str = "", *,
                left: str = "", right: str = "") -> str:
    """The page as drawn, beside the same page with every recorded box on it."""
    left = left or tr("画出来的页面", "The page as drawn")
    right = right or tr("记下来的框", "The boxes as recorded")
    drawn = image(Path(record.image_path))
    if not drawn:
        return ""
    marked = image(Path(record.image_path), record)
    return (f'<div class="diff"><div class="next"><h4>{esc(left)}</h4>{drawn}</div>'
            f'<div class="now"><h4>{esc(right)}</h4>{marked}</div></div>'
            + (f"<p>{caption}</p>" if caption else ""))


def wall(items: Sequence[tuple[str, str, str]]) -> str:
    """A contact sheet: many small images, each under a name and a line of facts.

    What a single worked example cannot show is what the whole batch came out as --
    whether the figures differ from each other, and whether any one of them is
    visibly broken. `meta` is written by the caller and goes in as HTML.
    """
    cells = [f'<figure><img src="{src}" alt="{esc(title)}" loading="lazy">'
             f"<figcaption><b>{esc(title)}</b>{meta}</figcaption></figure>"
             for src, title, meta in items if src]
    return f'<div class="wall">{"".join(cells)}</div>' if cells else ""


def box_legend() -> str:
    return ('<p class="legend">'
            f'<span><b style="background:rgb{VALUE_BOX}"></b>'
            f'{tr("带值目标的图元", "mark with a value target")}</span>'
            f'<span><b style="background:rgb{PLACE_BOX}"></b>'
            f'{tr("只有定位目标", "localization target only")}</span>'
            f'<span><b style="background:rgb{PAGE_BOX}"></b>'
            f'{tr("页面元素", "page element")}</span></p>')


# ---------------------------------------------------------------- the page shell

#: Classes the generated pages add on top of the plan's stylesheet.
EXTRA_CSS = """
.n{font-variant-numeric:tabular-nums;white-space:nowrap}
.tag.g{background:var(--raised);color:var(--muted)}
.bar{display:inline-flex;width:96px;vertical-align:middle;margin:0 8px 0 0}
.bar i{background:var(--have)}
figure.draw img,.diff img,.body img{border:1px solid var(--line);border-radius:6px}
pre.tree{white-space:pre-wrap;word-break:break-word}
td pre.tree{margin:0;font-size:12px}
.card .body>.scroll:last-child{margin-bottom:0}
nav.tabs a{display:block;padding:11px 14px 10px;font:inherit;font-size:13.5px;
  color:var(--muted);text-decoration:none;border-bottom:2px solid transparent}
nav.tabs a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--ink)}
nav.tabs a span{display:block;font-size:11.5px;color:var(--muted)}
.gridcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.gridcards a{display:block;text-decoration:none;color:inherit;background:var(--surface);
  border:1px solid var(--line);border-radius:10px;overflow:hidden;box-shadow:var(--shadow)}
.gridcards a b{display:block;padding:9px 12px 2px;font-size:14px}
.gridcards a span{display:block;padding:0 12px 10px;font-size:12px;color:var(--muted)}
.wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(236px,1fr));
  gap:12px;margin:14px 0}
.wall figure{margin:0;background:var(--surface);border:1px solid var(--line);
  border-radius:8px;overflow:hidden;box-shadow:var(--shadow)}
.wall img{width:100%;display:block;border:0;border-radius:0}
.wall figcaption{padding:7px 10px 9px;font-size:11.5px;color:var(--muted);line-height:1.55}
.wall figcaption b{display:block;color:var(--ink);font-size:12px;font-weight:600;
  margin-bottom:2px;word-break:break-all}
.ok{color:var(--have);font-weight:600}
.bad{color:var(--gap);font-weight:600}
"""


def css() -> str:
    """The plan's own stylesheet, plus what these pages add."""
    text = (ROOT / "plan" / "plan.html").read_text(encoding="utf-8")
    return text[text.index("<style>") + 7:text.index("</style>")] + EXTRA_CSS


def masthead(title: str, lead: str, facts: Sequence[tuple[Any, str]]) -> str:
    chips = "".join(f'<div class="fact"><b>{esc(n)}</b><span>{esc(t)}</span></div>'
                    for n, t in facts)
    return (f'<header class="masthead"><div class="inner"><div><h1>{esc(title)}</h1>'
            f'<p>{lead}</p></div><div class="facts">{chips}</div></div></header>')


def site_nav(current: str, links: Sequence[tuple[str, str, str]]) -> str:
    """The bar across the top of every review page: file, name, one-line hint."""
    out = ['<nav class="tabs">']
    for href, name, hint in links:
        here = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{href}"{here}>{esc(name)}<span>{esc(hint)}</span></a>')
    return "".join(out) + "</nav>"


def document(title: str, head: str, body: str) -> str:
    """One self-contained page. No external request is ever made from these files."""
    return (f'<!doctype html>\n<html lang="{"en" if LANG == "en" else "zh-CN"}">'
            f'<head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f"<title>{esc(title)}</title>\n<style>{css()}</style></head>\n<body>\n"
            f"{head}\n<main>{body}</main>\n</body></html>\n")

def page_document(records: Sequence[Record]) -> str:
    """One page written out as a document, which is the shape a benchmark asks for.

    Built here rather than read off disk, because the run this page describes was
    exported under its own settings and the point is that the settings are a
    parameter: the same records, asked for another way.
    """
    from chartgen.s05_output.export import (
        PRESETS, as_markdown, build as build_one, with_whole_page,
    )

    # Keyed by scenario as well as by page: a page identifier is unique inside the
    # scenario that wrote it, and every scenario is exported into its own directory.
    pages: dict[tuple[str, str], list[Record]] = {}
    for record in records:
        if record.page_id:
            pages.setdefault((record.scenario_id, record.page_id), []).append(record)
    pair = next((v for v in pages.values() if len({r.figure_id for r in v}) > 1), None)
    if pair is None:
        return ""
    preset = PRESETS["parsebench"]
    units = with_whole_page([build_one(r, key_scope=preset["key_scope"]) for r in pair])
    text = as_markdown(pair[0].page_id, units)
    limit = text.find("\n", 2600)
    shown = text if limit < 0 else text[:limit] + "\n…"
    out = [band(tr("同一页写成一份文档", "One page written as one document"),
                f"output.preset = parsebench · {pair[0].page_id}")]
    out.append(table(
        [tr("参数", "Setting"), tr("这个预设要什么", "What this preset asks for"),
         tr("为什么", "Why")], [
        ["<code>granularity</code>", "<code>page</code>",
         tr("一页就是一张图像、一次回答",
           "One page is one image and one answer")],
        ["<code>format</code>", "<code>markdown</code>",
         tr("回答里的每一张表都会被搜",
           "Every table in the answer is searched")],
        ["<code>key_scope</code>", "<code>full</code>",
         tr("一个抽查点可能要三个键才定位得到",
           "A spot check can need three key segments to locate")],
        ["<code>targets</code>", "<code>grounded_table</code>",
         tr("这一维只看那一张长表",
           "This dimension looks only at the long table")],
    ]))
    out.append(card("", code(shown), f"{pair[0].page_id}.md"))
    out.append(note(tr(
        "三件事各有理由。<b>二级标题是分开两张图的唯一凭据</b>——"
        "并排的两张图类别名一模一样，一张没有标题的表会和旁边那张撞在一起。"
        "<b>标题写的是画在图上的图号与图题，不是文件标识</b>——"
        "<code>f08_v0</code> 是一个文件名，页面上一个字都没写它，"
        "一个看着图的人产不出这个字符串。"
        "<b>键的每一段单独占一列</b>——折进一个格子的键读起来是一个名字，"
        "而一个由面板、类目、颜色分组三段指认的图元是三个名字。",
        "Three decisions, each for its own reason. <b>The second-level heading is the only "
        "thing separating the two figures</b> -- side by side they use the same category "
        "names, and an untitled table runs into the one beside it. "
        "<b>The heading carries the figure number and title drawn on the image, not a file "
        "identifier</b> -- <code>f08_v0</code> names a file, appears nowhere on the page, "
        "and no one looking at the image could produce that string. "
        "<b>Every key segment takes its own column</b> -- a key folded into one cell reads "
        "as one name, and a mark addressed by panel, category and colour group is three "
        "names.")))
    out.append(note(tr(
        "<b>预设改的只是取哪个投影、写成什么样，记录里有什么一个字不动。</b>"
        "这是同一条流水线能服务不止一把尺子而不被任何一把塑形的原因；"
        "单独写明的项盖过预设，于是「取这个预设、改其中一项」不用把整组抄一遍。",
        "<b>A preset changes which projection is taken and how it is written; it changes "
        "nothing in the record.</b> That is what lets one pipeline serve more than one "
        "benchmark without being shaped by any of them. Anything named explicitly beside a "
        "preset wins, so \"this preset with one thing changed\" needs no copy of the whole "
        "set.")))
    return "".join(out)
