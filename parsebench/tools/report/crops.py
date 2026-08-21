"""Cut one figure out of a page image, as the bytes an HTML page can carry inline.

The report shows evidence, and a whole 1040x1477 page shown at 700 pixels wide is
not evidence: the reader cannot see the tick the argument is about. The parser's
own run already holds what is needed to do better -- every block it emitted carries
a bbox in the coordinates of the image it read -- so a figure can be cut out of the
page at the size it was drawn.

The bboxes come from the parser, not from ground truth, and are used only to decide
where to cut a picture for a human to look at. Nothing counted anywhere in this
analysis depends on them.

Two things widen a crop beyond the block itself. A figure's heading and its
source/note lines are part of what the report argues about -- where the unit sits,
what the note says the colours mean -- so caption and footnote blocks that sit
directly above or below the figure are pulled in. And a margin keeps the outermost
tick labels inside the cut.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / "parsebench/data/pages"
RUNS = ROOT / "parsebench/data/runs"

#: Blocks that are the figure itself.
_FIGURE_KINDS = {"chart", "image", "figure"}
_FIGURE_LABELS = {"chart", "figure", "image", "picture"}

#: Blocks worth pulling into the crop when they sit against the figure.
_ATTACHED = {"figure_title", "caption", "vision_footnote", "footnote", "figure_note"}

#: How far above or below the figure an attached block may start, as a fraction of
#: the page height, and how much blank margin to leave around the result.
_REACH = 0.06
_MARGIN = 0.012


@dataclass(frozen=True)
class Box:
    """A rectangle in page-image pixels, origin top left."""

    x0: float
    y0: float
    x1: float
    y1: float

    def union(self, other: "Box") -> "Box":
        return Box(min(self.x0, other.x0), min(self.y0, other.y0),
                   max(self.x1, other.x1), max(self.y1, other.y1))

    def overlaps_x(self, other: "Box") -> bool:
        span = min(self.x1, other.x1) - max(self.x0, other.x0)
        return span > 0.3 * min(self.x1 - self.x0, other.x1 - other.x0)


def _blocks(stem: str, run: str) -> tuple[list[dict], float, float]:
    raw = json.loads((RUNS / run / "chart" / f"{stem}.raw.json").read_text())["raw_output"]
    return raw["blocks"], float(raw["image_width"]), float(raw["image_height"])


def figure_boxes(stem: str, run: str = "ppdoclayoutv3_lean_qwen") -> list[Box]:
    """Every figure on the page, in reading order, each widened to its heading and note.

    Reading order is the parser's `order_index`, which is what `f1, f2, ...` in a
    model's answer counts in, so the two line up without a match step.
    """
    blocks, width, height = _blocks(stem, run)
    scale_w, scale_h = 1.0 / width, 1.0 / height

    def box(block: dict) -> Box:
        x0, y0, x1, y1 = block["bbox"]
        return Box(x0 * scale_w, y0 * scale_h, x1 * scale_w, y1 * scale_h)

    ordered = sorted(blocks, key=lambda b: int(b.get("order_index", 0)))
    figures = [box(b) for b in ordered
               if b.get("kind") in _FIGURE_KINDS
               or str(b.get("label", "")).lower() in _FIGURE_LABELS]
    attached = [box(b) for b in ordered if str(b.get("label", "")).lower() in _ATTACHED]

    out = []
    for figure in figures:
        grown = figure
        for near in attached:
            if not near.overlaps_x(figure):
                continue
            above = 0 <= figure.y0 - near.y1 <= _REACH
            below = 0 <= near.y0 - figure.y1 <= _REACH
            if above or below:
                grown = grown.union(near)
        out.append(grown)
    return out


@lru_cache(maxsize=64)
def _page(stem: str) -> Image.Image:
    return Image.open(PAGES / f"{stem}.png").convert("RGB")


@lru_cache(maxsize=64)
def page_image(stem: str, width: int = 900, quality: int = 66) -> tuple[str, int, int]:
    """The whole page as `(data uri, width, height)`.

    The report inlines the *page*, never the crop. A crop is then shown by pointing a
    box at part of the same image, so a page used as evidence three times costs the
    bytes of one page -- and the reader can always open the whole thing.
    """
    image = _page(stem)
    if image.width > width:
        height = round(image.height * width / image.width)
        image = image.resize((width, height), Image.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
    uri = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
    return uri, image.width, image.height


def figure_box(stem: str, index: int = 0) -> Box:
    """Figure `index` widened by a margin; the whole page when the parser found none."""
    boxes = figure_boxes(stem)
    if not boxes:
        return Box(0.0, 0.0, 1.0, 1.0)
    box = boxes[min(index, len(boxes) - 1)]
    grown = Box(max(0.0, box.x0 - _MARGIN), max(0.0, box.y0 - _MARGIN),
                min(1.0, box.x1 + _MARGIN), min(1.0, box.y1 + _MARGIN))
    if grown.x1 - grown.x0 < 0.05 or grown.y1 - grown.y0 < 0.05:
        return Box(0.0, 0.0, 1.0, 1.0)          # a degenerate box is not a crop
    return grown


def figure_index(figure_id: str) -> int:
    """`f2` -> 1. An id that is not a figure (`page`) points at the first one."""
    digits = "".join(ch for ch in figure_id if ch.isdigit())
    return max(0, int(digits) - 1) if digits else 0


if __name__ == "__main__":                               # a size check, not a test
    import sys
    for stem in sys.argv[1:]:
        uri, width, height = page_image(stem)
        print(f"{stem:<55} {width}x{height}  {len(uri) // 1024} kB  "
              f"figures={len(figure_boxes(stem))}")
