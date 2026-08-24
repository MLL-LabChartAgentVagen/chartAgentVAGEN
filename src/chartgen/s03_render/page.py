"""Putting figures onto a page, and recording what else is on it.

A figure is not shipped as a bare image. It goes into a page with running text, a
header, a footer and a caption, which buys three things: page-element boxes with a
category each, a localisation task that is not trivial (a bare image has the chart
filling the whole frame), and the real layout situations -- several figures on one
page, a caption sitting apart from the figure it belongs to.

Pasting is a translate and a scale, the same mechanism image degradation uses, so
every box already recorded moves through one matrix and stays exact.

Two figures on one page each keep their own text blocks and both keep the page's
furniture. Neither record is the whole page, which is why the export merges page
elements by page identifier before writing the page-element target.
"""

from __future__ import annotations

import textwrap
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from ..common.geometry import Box, apply, compose as compose_matrix, scale, translate
from ..interfaces.record import Element, RenderOutput
from ..interfaces.style import StyleVector
from .style import BACKGROUND, TEXT_COLOR, hex_of, resolve_font

#: The page. Fixed like everything else about the layout: a page that resized
#: itself around its content would move every box pasted into it.
PAGE_SIZE = (1000, 1400)
MARGIN = 80.0

#: Where each band of the page starts, in pixels from the top.
HEADER_Y = 44.0
BODY_Y = 108.0
FIGURE_Y = 260.0
FOOTER_Y = 1330.0

#: Characters per line of running text, and the height of one line.
WRAP = 96
LINE_HEIGHT = 19.0

#: Gap between two figures placed side by side, and between a figure and its caption.
FIGURE_GAP = 24.0
CAPTION_GAP = 12.0


def _font(style: StyleVector, size: float) -> ImageFont.FreeTypeFont:
    from matplotlib import font_manager as fm

    path = fm.findfont(fm.FontProperties(family=resolve_font(style.font_family)))
    return ImageFont.truetype(path, int(size))


def fit_line(draw: ImageDraw.ImageDraw, text: str, width: float,
             font: ImageFont.FreeTypeFont) -> str:
    """The text, cut to the room a line has, with an ellipsis where it was cut.

    A page header is one line by design, and a scenario title is as long as its
    subject needs. Left as it is, a long one runs past the right margin and off the
    page, and the record then carries a box for text nobody can see.
    """
    if not text or draw.textlength(text, font=font) <= width:
        return text
    cut = len(text)
    while cut > 1 and draw.textlength(text[:cut - 1] + "\u2026", font=font) > width:
        cut -= 1
    return text[:cut - 1].rstrip() + "\u2026" if cut > 1 else "\u2026"


def text_block(draw: ImageDraw.ImageDraw, text: str, at: tuple[float, float],
               font: ImageFont.FreeTypeFont, *, colour=TEXT_COLOR,
               width: float | None = None) -> tuple[Box, str]:
    """Draw one line of page text and return the box it came out in and what was drawn.

    Both, because a line cut to fit is a different string from the one asked for, and
    what the record has to carry is the one on the page.
    """
    if width is not None:
        text = fit_line(draw, text, width, font)
    draw.text(at, text, font=font, fill=hex_of(colour))
    x0, y0, x1, y1 = draw.textbbox(at, text, font=font)
    return Box(x0, y0, x1, y1), text


def _paragraph(draw: ImageDraw.ImageDraw, text: str, top: float,
               font: ImageFont.FreeTypeFont) -> list[tuple[Box, str]]:
    return [text_block(draw, line, (MARGIN, top + i * LINE_HEIGHT), font,
                       width=PAGE_SIZE[0] - 2 * MARGIN)
            for i, line in enumerate(textwrap.wrap(text, WRAP)[:6])]


#: Room held under the figures for the closing paragraph, for a caption under each
#: figure, and clear space between the last of them and the footer.
CLOSING_ROOM = 6 * LINE_HEIGHT + 20.0
CAPTION_ROOM = CAPTION_GAP + 3 * LINE_HEIGHT
TAIL_GAP = 20.0


def _closing_top(bottoms: Sequence[float]) -> float:
    """Where the text under the figures starts.

    Under the lowest of them, rather than at a height fixed per figure count. A
    figure is scaled to the width of its slot and its height follows from its own
    aspect ratio, which is a style dimension: a page of two tall figures runs three
    hundred pixels further down than a page of two wide ones, and a fixed height put
    the closing paragraph across the picture.

    Nothing already recorded moves. The pictures are pasted and their boxes taken
    first; the paragraph records its own box at the moment it is drawn, which is
    after. That is the same order every mark on a figure follows.
    """
    return max(bottoms, default=FIGURE_Y) + CAPTION_GAP


def _slots(count: int, width: float) -> list[tuple[float, float, float, float]]:
    """Where each figure goes: left edge, top edge, and the width and height it has.

    Two figures share a row, which is the layout that puts the same category names
    in both and leaves only their own titles to tell their rows apart. Beyond two
    they wrap into rows of two, and each row gets an equal share of the band between
    the figures' top and the room held for the closing text.
    """
    band = FOOTER_Y - FIGURE_Y - CLOSING_ROOM - TAIL_GAP
    if count <= 1:
        return [(MARGIN, FIGURE_Y, width, band - CAPTION_ROOM)]
    each = (width - FIGURE_GAP) / 2
    rows = 1 if count <= 2 else -(-count // 2)
    per_row = band / rows
    return [(MARGIN + (i % 2) * (each + FIGURE_GAP),
             FIGURE_Y + (i // 2) * per_row, each, per_row - CAPTION_ROOM)
            for i in range(count)]


def compose(rendered: Sequence[RenderOutput], out_dir: str | Path, *, page_id: str,
            header: str = "", body: str = "", footer: str = "",
            captions: Sequence[str] = (), closing: str = "") -> list[RenderOutput]:
    """Paste these figures onto one page and return their records in page coordinates."""
    if not rendered:
        return []
    style = rendered[0].style
    page = Image.new("RGB", PAGE_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(page)
    width = PAGE_SIZE[0] - 2 * MARGIN

    furniture: list[Element] = []
    if header:
        box, drawn = text_block(draw, header, (MARGIN, HEADER_Y), _font(style, 15),
                                width=width)
        furniture.append(Element(box, "Page-Header", drawn))
    for box, drawn in _paragraph(draw, body, BODY_Y, _font(style, 13)):
        furniture.append(Element(box, "Text", drawn))
    if footer:
        box, drawn = text_block(draw, footer, (MARGIN, FOOTER_Y), _font(style, 12),
                                width=width)
        furniture.append(Element(box, "Page-Footer", drawn))

    out: list[RenderOutput] = []
    bottoms: list[float] = []
    for figure, (x, y, target, room) in zip(rendered, _slots(len(rendered), width)):
        # Both directions. Scaled by width alone, a tall figure runs past the slot and
        # onto whatever the page holds below it.
        factor = min(target / figure.image_size[0], room / figure.image_size[1])
        picture = Image.open(figure.image_path).convert("RGB")
        picture = picture.resize((int(figure.image_size[0] * factor),
                                  int(figure.image_size[1] * factor)), Image.LANCZOS)
        page.paste(picture, (int(x), int(y)))
        matrix = compose_matrix(translate(x, y), scale(factor, factor))
        pasted = Box(x, y, x + picture.width, y + picture.height)

        # The panel an element belongs to is carried through: it is the only field
        # the export joins a panel title on, and a panel title is where a key segment
        # at panel scope comes from.
        elements = [Element(apply(matrix, e.box), e.category, e.text, e.panel_id)
                    for e in figure.elements if e.category != "Picture"]
        elements.append(Element(pasted, "Picture", ""))
        caption = captions[len(out)] if len(out) < len(captions) else ""
        if caption:
            font = _font(style, 12)
            wrap = max(20, int(picture.width / 6.2))
            for i, line in enumerate(textwrap.wrap(caption, wrap)[:3]):
                box, drawn = text_block(
                    draw, line,
                    (x, y + picture.height + CAPTION_GAP + i * LINE_HEIGHT), font,
                    width=picture.width)
                elements.append(Element(box, "Text", drawn))
        bottoms.append(y + picture.height + (CAPTION_ROOM if caption else 0.0))
        out.append((figure, matrix, elements))  # type: ignore[arg-type]

    if closing:
        top = _closing_top(bottoms)
        for box, drawn in _paragraph(draw, closing, top, _font(style, 13)):
            furniture.append(Element(box, "Text", drawn))

    path = Path(out_dir) / f"{page_id}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    page.save(path)

    return [_in_page_space(figure, matrix, elements + furniture, path, page_id)
            for figure, matrix, elements in out]


def _in_page_space(figure: RenderOutput, matrix, elements: Sequence[Element],
                   path: Path, page_id: str) -> RenderOutput:
    move = lambda box: apply(matrix, box)
    return replace(
        figure,
        image_path=str(path),
        image_size=PAGE_SIZE,
        page_id=page_id,
        panels=tuple(replace(p, box=move(p.box), axes=tuple(
            replace(a, pixel_range=_move_range(matrix, a)) for a in p.axes))
            for p in figure.panels),
        marks=tuple(replace(m, box=move(m.box),
                            label_box=move(m.label_box) if m.label_box else None)
                    for m in figure.marks),
        legend=tuple(replace(e, box=move(e.box)) for e in figure.legend),
        elements=tuple(elements),
    )


def _move_range(matrix, axis) -> tuple[float, float]:
    """An axis's pixel range after the paste. A translate and a scale act on each
    coordinate on its own, so the range maps exactly."""
    from ..common.geometry import apply_point

    horizontal = axis.role in ("x",)
    pts = [apply_point(matrix, v, 0.0) if horizontal else apply_point(matrix, 0.0, v)
           for v in axis.pixel_range]
    i = 0 if horizontal else 1
    return (float(pts[0][i]), float(pts[1][i]))
