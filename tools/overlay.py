"""Draw the recorded boxes back onto the image, to look at them.

    python tools/overlay.py out/er_wait/f01.json [-o overlay.png]

The boxes come from the record, not from re-parsing the image, so the overlay is
visual evidence that drawing and recording stayed in step.
Colours: marks in magenta, plotting areas in cyan, legend entries in orange, page
elements in grey.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from chartgen.common.geometry import Box  # noqa: E402
from chartgen.common import serde  # noqa: E402
from chartgen.interfaces.record import Record, RenderOutput  # noqa: E402

MARK_COLOR = (214, 39, 120)
PANEL_COLOR = (23, 162, 184)
LEGEND_COLOR = (255, 140, 0)
ELEMENT_COLOR = (120, 120, 120)
LABEL_BG = (255, 255, 255)


def _font(size: int = 12) -> ImageFont.FreeTypeFont:
    from matplotlib import font_manager as fm

    for name in ("Noto Sans CJK JP", "Droid Sans Fallback", "DejaVu Sans"):
        try:
            return ImageFont.truetype(fm.findfont(fm.FontProperties(family=name)), size)
        except Exception:  # noqa: BLE001 -- try the next font
            continue
    return ImageFont.load_default()


def _rect(draw: ImageDraw.ImageDraw, box: Box, color, width: int = 2) -> None:
    draw.rectangle([box.x0, box.y0, box.x1, box.y1], outline=color, width=width)


def _tag(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, color, font) -> None:
    x0, y0, x1, y1 = draw.textbbox((x, y), text, font=font)
    draw.rectangle([x0 - 2, y0 - 1, x1 + 2, y1 + 1], fill=LABEL_BG)
    draw.text((x, y), text, fill=color, font=font)


def overlay(record: RenderOutput, image_path: str | Path | None = None) -> Image.Image:
    img = Image.open(image_path or record.image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = _font(12)

    for element in record.elements:
        _rect(draw, element.box, ELEMENT_COLOR, 1)
        _tag(draw, element.box.x0 + 3, element.box.y0 + 3, element.category, ELEMENT_COLOR, font)

    for panel in record.panels:
        _rect(draw, panel.box, PANEL_COLOR, 1)
        _tag(draw, panel.box.x0 + 3, panel.box.y0 + 3,
             f"{panel.panel_id} {panel.chart_type}", PANEL_COLOR, font)

    for entry in record.legend:
        _rect(draw, entry.box, LEGEND_COLOR, 2)
        _tag(draw, entry.box.x0, entry.box.y1 + 2,
             f"{entry.maps_to_category}→{','.join(entry.applies_to_panels)}", LEGEND_COLOR, font)

    for mark in record.marks:
        _rect(draw, mark.box, MARK_COLOR, 2)
        value = next(iter(mark.values.values()), "")
        text = f"{'/'.join(mark.key)} {value}"
        if getattr(mark, "readable", None) is False:
            text += " ✗"
        if mark.rows is not None:
            text += f" ({mark.rows})"
        _tag(draw, mark.box.x0, max(0.0, mark.box.y0 - 15), text, MARK_COLOR, font)
        if mark.label_box is not None:
            _rect(draw, mark.label_box, MARK_COLOR, 1)
    return img


def main() -> None:
    ap = argparse.ArgumentParser(description="draw recorded boxes back onto the image")
    ap.add_argument("record", type=Path, help="a render output or record json file")
    ap.add_argument("-i", "--image", type=Path, default=None, help="use this image instead of the one named in the record")
    ap.add_argument("-o", "--out", type=Path, default=None)
    args = ap.parse_args()

    try:
        rec: RenderOutput = serde.load(Record, args.record)
    except serde.SchemaTypeError:
        rec = serde.load(RenderOutput, args.record)

    out = args.out or args.record.with_suffix(".overlay.png")
    overlay(rec, args.image).save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
