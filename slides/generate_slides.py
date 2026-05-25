"""
Generate chartagent_slides.pptx — 26 slides, 16:9, English-only.

Clean academic style, plain researcher voice: pure white background,
one Stanford-red accent, oversized centered titles in Avenir-heavy,
soft-shadow cards replacing all bullet points. No detective metaphor,
no eyebrow breadcrumbs, no page numbers, no title-page red strip,
no pink-tinted highlight cards. Mirrors slides/chartagent_slides.html.

Two contributions:
  C1 — Synthetic data generation (atomic-grain Master Table, Code-as-DGP, SQL projection)
  C2 — Active Chart Reasoning   (budgeted protocol, bbox grounding, four investigation moves)

The SwiftEats 31 → 18 minute example runs through the deck.
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from lxml import etree


# ---------------------------------------------------------------------------
# PALETTE — academic-clean: white + one Stanford red accent
# ---------------------------------------------------------------------------
INK         = RGBColor(0x1A, 0x1A, 0x1A)
MUTED       = RGBColor(0x6B, 0x6B, 0x6B)
HAIR        = RGBColor(0xE6, 0xE6, 0xE6)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT      = RGBColor(0x8C, 0x15, 0x15)   # Stanford red
ACCENT_SOFT = RGBColor(0xFB, 0xED, 0xED)
GOOD        = RGBColor(0x2E, 0x7D, 0x4F)
GOOD_SOFT   = RGBColor(0xEA, 0xF4, 0xEC)
BAD         = RGBColor(0xB2, 0x3A, 0x3A)
BAD_SOFT    = RGBColor(0xF8, 0xEC, 0xEC)
CODE_BG     = RGBColor(0xFA, 0xFA, 0xFA)
CODE_KEY    = RGBColor(0x8C, 0x15, 0x15)   # = accent
CODE_STR    = RGBColor(0x2E, 0x7D, 0x4F)
CODE_NUM    = RGBColor(0x1A, 0x1A, 0x1A)
CODE_COM    = RGBColor(0x9A, 0x9A, 0x9A)

FONT = "Avenir Next"
MONO = "JetBrains Mono"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = 13.333, 7.5


# ---------------------------------------------------------------------------
# LOW-LEVEL HELPERS
# ---------------------------------------------------------------------------
def blank():
    return prs.slides.add_slide(prs.slide_layouts[6])


def _strip_style(shape):
    """Remove theme-derived effects so cards render identically everywhere."""
    el = shape._element
    style = el.find(qn("p:style"))
    if style is not None:
        el.remove(style)


def _set_effect(shape, soft_shadow=False):
    """Replace effectLst — empty by default, or soft outer shadow."""
    el = shape._element
    spPr = el.find(qn("p:spPr"))
    if spPr is None:
        return
    for old in spPr.findall(qn("a:effectLst")):
        spPr.remove(old)
    effectLst = etree.SubElement(spPr, qn("a:effectLst"))
    if soft_shadow:
        sh = etree.SubElement(effectLst, qn("a:outerShdw"))
        # blur 22pt, distance 6pt, downward, ~10% black
        sh.set("blurRad", str(int(22 * 12700)))
        sh.set("dist",    str(int(6  * 12700)))
        sh.set("dir",     "5400000")   # 90° (downward)
        sh.set("algn",    "ctr")
        sh.set("rotWithShape", "0")
        srgb = etree.SubElement(sh, qn("a:srgbClr"))
        srgb.set("val", "000000")
        a = etree.SubElement(srgb, qn("a:alpha"))
        a.set("val", "11000")          # 11% alpha


def shape_at(slide, x, y, w, h, fill=None, line=None, line_w=0.75,
             shape=MSO_SHAPE.RECTANGLE, soft_shadow=False):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    _strip_style(s)
    _set_effect(s, soft_shadow=soft_shadow)
    s.text_frame.word_wrap = True
    s.text_frame.margin_left = Inches(0.10)
    s.text_frame.margin_right = Inches(0.10)
    s.text_frame.margin_top = Inches(0.05)
    s.text_frame.margin_bottom = Inches(0.05)
    return s


def rect(slide, x, y, w, h, **kw):
    return shape_at(slide, x, y, w, h, shape=MSO_SHAPE.RECTANGLE, **kw)


def rounded(slide, x, y, w, h, **kw):
    return shape_at(slide, x, y, w, h, shape=MSO_SHAPE.ROUNDED_RECTANGLE, **kw)


def card(slide, x, y, w, h, fill=WHITE):
    """Soft-shadow card — no border, gentle drop shadow."""
    s = shape_at(slide, x, y, w, h, fill=fill, line=None,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, soft_shadow=True)
    # Bump radius up a touch
    return s


def oval(slide, x, y, w, h, **kw):
    return shape_at(slide, x, y, w, h, shape=MSO_SHAPE.OVAL, **kw)


def textbox(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, margin=0.04):
    """runs is either [(text, size, bold, color [, italic [, font]]), ...]
    for one paragraph, or a list of paragraphs."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(margin); tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin); tf.margin_bottom = Inches(margin)
    _strip_style(tb)
    _set_effect(tb, soft_shadow=False)

    if runs and not isinstance(runs[0], list):
        paragraphs = [runs]
    else:
        paragraphs = runs

    for pi, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(0)
        for run_def in para:
            if len(run_def) == 4:
                text, size, bold, color = run_def
                italic = False; f_override = None
            elif len(run_def) == 5:
                text, size, bold, color, italic = run_def
                f_override = None
            else:
                text, size, bold, color, italic, f_override = run_def
            r = p.add_run()
            r.text = text
            r.font.name = f_override or FONT
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
    return tb


def set_text_in(shape, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    if runs and not isinstance(runs[0], list):
        paragraphs = [runs]
    else:
        paragraphs = runs
    tf.text = ""
    for pi, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(0)
        for run_def in para:
            if len(run_def) == 4:
                text, size, bold, color = run_def
                italic = False; f_override = None
            elif len(run_def) == 5:
                text, size, bold, color, italic = run_def
                f_override = None
            else:
                text, size, bold, color, italic, f_override = run_def
            r = p.add_run()
            r.text = text
            r.font.name = f_override or FONT
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color


def line_seg(slide, x1, y1, x2, y2, color=MUTED, weight=1.0,
             dash=False, arrow_end=False, arrow_start=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                   Inches(x1), Inches(y1),
                                   Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(weight)
    ln = c.line._get_or_add_ln()
    if dash:
        prstDash = etree.SubElement(ln, qn("a:prstDash"))
        prstDash.set("val", "dash")
    if arrow_end:
        tail = etree.SubElement(ln, qn("a:tailEnd"))
        tail.set("type", "triangle"); tail.set("w", "med"); tail.set("len", "med")
    if arrow_start:
        head = etree.SubElement(ln, qn("a:headEnd"))
        head.set("type", "triangle"); head.set("w", "med"); head.set("len", "med")
    _strip_style(c)
    _set_effect(c, soft_shadow=False)
    return c


# ---------------------------------------------------------------------------
# CHROME — eyebrow and pageno are intentional no-ops in the clean style
# (callers retained for backward compatibility with existing slide functions).
# ---------------------------------------------------------------------------
def eyebrow(slide, text):  # noqa: ARG001
    return


def pageno(slide, n, total=26):  # noqa: ARG001
    return


def title_centered(slide, runs, y=0.85, size=36):
    """runs = [(text, color, bold?), ...] or a list of (text, color) pairs."""
    paras = []
    para = []
    for r in runs:
        if r == "\n":
            paras.append(para); para = []
            continue
        if len(r) == 2:
            text, color = r; bold = True
        else:
            text, color, bold = r
        para.append((text, size, bold, color))
    paras.append(para)
    textbox(slide, 0.55, y, SW - 1.10, 1.6, paras,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)


def subtitle_centered(slide, text, y=1.65, size=15):
    textbox(slide, 0.55, y, SW - 1.10, 0.5,
            [(text, size, False, MUTED, True)],
            align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# CARD HELPERS
# ---------------------------------------------------------------------------
def card_label(slide, x, y, w, label, color=MUTED, size=10):
    textbox(slide, x + 0.20, y + 0.18, w - 0.40, 0.28,
            [(label.upper(), size, True, color)])


def labelled_card(slide, x, y, w, h, label, body_runs,
                  label_color=ACCENT, fill=WHITE):
    """Card with small uppercase label + body text below."""
    c = card(slide, x, y, w, h, fill=fill)
    card_label(slide, x, y, w, label, color=label_color, size=11)
    textbox(slide, x + 0.20, y + 0.55, w - 0.40, h - 0.65,
            body_runs, anchor=MSO_ANCHOR.TOP)
    return c


def stat_card(slide, x, y, w, h, big, lbl, sub):
    card(slide, x, y, w, h)
    # big number occupies the top half
    textbox(slide, x, y + 0.20, w, 1.00,
            [(big, 56, True, ACCENT, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # label
    textbox(slide, x + 0.20, y + 1.35, w - 0.40, 0.32,
            [(lbl, 13, True, INK)], align=PP_ALIGN.CENTER)
    # sub fully inside the card (multi-line OK)
    textbox(slide, x + 0.25, y + 1.75, w - 0.50, h - 1.90,
            [(sub, 10.5, False, MUTED, True)], align=PP_ALIGN.CENTER)


def contrib_tag(slide, x, y, w, h, label):
    """Plain uppercase monospace label in muted gray (no red pill)."""
    textbox(slide, x, y, w, h,
            [(label.upper(), 12, True, MUTED, False, MONO)],
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)


def badge_circle(slide, cx, cy, d, label, fill=None, txt=INK, size=14):
    """Neutral pill: light gray fill, dark text. ``fill`` defaults to #f1f1f1."""
    if fill is None:
        fill = RGBColor(0xF1, 0xF1, 0xF1)
    oval(slide, cx - d/2, cy - d/2, d, d, fill=fill)
    textbox(slide, cx - d/2, cy - d/2, d, d,
            [(label, size, True, txt, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ---------------------------------------------------------------------------
# CODE BLOCK — render colored Python/JSON inside a soft card
# ---------------------------------------------------------------------------
def code_block(slide, x, y, w, h, lines, size=11.0, line_h=0.20):
    """lines: list of (segments, ) where segments=[(text, kind), ...]
    kind in {'k','s','n','c','t'}: k=keyword(accent), s=string(green),
    n=number/normal, c=comment(gray), t=text(ink)."""
    card(slide, x, y, w, h, fill=CODE_BG)
    yy = y + 0.18
    for segs in lines:
        runs = []
        for text, kind in segs:
            if kind == 'k':
                runs.append((text, size, True, CODE_KEY, False, MONO))
            elif kind == 's':
                runs.append((text, size, False, CODE_STR, False, MONO))
            elif kind == 'n':
                runs.append((text, size, False, CODE_NUM, False, MONO))
            elif kind == 'c':
                runs.append((text, size, False, CODE_COM, True, MONO))
            else:
                runs.append((text, size, False, INK, False, MONO))
        textbox(slide, x + 0.20, yy, w - 0.40, line_h + 0.05, runs)
        yy += line_h


# ===========================================================================
# SLIDE 1 — TITLE
# ===========================================================================
def slide_title():
    s = blank()

    textbox(s, 0, 2.80, SW, 1.20,
            [[("The ", 60, True, INK),
              ("Latent", 60, True, ACCENT),
              (" Data World", 60, True, INK)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    textbox(s, 0, 4.20, SW, 0.55,
            [("Evaluating VLM agents on charts as projections of a hidden table.",
              19, False, MUTED, True)],
            align=PP_ALIGN.CENTER)

    textbox(s, 0, SH - 0.85, SW, 0.35,
            [("Pingyue Zhang  ·  Northwestern University  ·  chartAgent / VAGEN",
              12, True, MUTED)],
            align=PP_ALIGN.CENTER)
    return s


# ===========================================================================
# SLIDE 2 — THE PUZZLE  (SwiftEats 31→18 setup)
# ===========================================================================
def slide_puzzle():
    s = blank()
    title_centered(s, [("A delivery dashboard reports ", INK),
                       ("31 → 18 min", ACCENT), (".", INK)],
                   y=0.85, size=36)
    subtitle_centered(s,
        "SwiftEats rolls out a new dispatcher. Average delivery time falls in one week.",
        y=1.65, size=15)

    # Three stacked shadow cards
    cw = SW - 3.20
    cx = (SW - cw) / 2
    ch = 1.20
    gap = 0.30

    cy = 2.50
    card(s, cx, cy, cw, ch)
    textbox(s, cx + 0.40, cy + 0.18, cw - 0.80, 0.30,
            [("HEADLINE METRIC", 11, True, MUTED)])
    textbox(s, cx + 0.40, cy + 0.55, cw - 0.80, 0.55,
            [("Average pickup-to-drop time: ", 19, True, INK),
             ("31", 19, True, INK, False, MONO),
             (" min (old) → ", 19, True, INK),
             ("18", 19, True, INK, False, MONO),
             (" min (new).", 19, True, INK)],
            anchor=MSO_ANCHOR.MIDDLE)

    cy += ch + gap
    card(s, cx, cy, cw, ch)
    textbox(s, cx + 0.40, cy + 0.18, cw - 0.80, 0.30,
            [("SAME WEEK, SAME DASHBOARD", 11, True, MUTED)])
    textbox(s, cx + 0.40, cy + 0.55, cw - 0.80, 0.55,
            [("Refunds, cancellations, and timeouts all ", 19, True, INK),
             ("rise", 19, True, ACCENT),
             (".", 19, True, INK)],
            anchor=MSO_ANCHOR.MIDDLE)

    cy += ch + gap
    card(s, cx, cy, cw, ch)
    textbox(s, cx, cy, cw, ch,
            [("An agent must reconcile both facts from the chart alone.",
              17, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 3 — FOUR CANDIDATE EXPLANATIONS  (h₁–h₄ hook for the investigation)
# ===========================================================================
def slide_suspects():
    s = blank()
    title_centered(s, [("Four candidate explanations for the ", INK),
                       ("31 → 18", ACCENT), (" gap.", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "Each is testable from charts derived from the same underlying table.",
        y=1.55, size=15)

    suspects = [
        ("h₁", "Genuine speedup",
         "The new dispatcher shortens routes across every order, every zone, every time of day."),
        ("h₂", "Zone selection",
         "The platform stops accepting orders in distant or low-density zones. Only easy orders remain."),
        ("h₃", "Denominator change",
         "The 18-minute figure averages only successful deliveries. Cancellations and timeouts are excluded."),
        ("h₄", "Metric boundary",
         "The 18 minutes covers pickup-to-drop only. Click-to-pickup waiting falls outside the window."),
    ]
    cy = 2.30
    ch = 2.10
    cw = (SW - 1.10 - 0.40) / 2
    gap = 0.40
    for i, (hid, name, body) in enumerate(suspects):
        x0 = 0.55 + (i % 2) * (cw + gap)
        yy = cy + (i // 2) * (ch + 0.30)
        card(s, x0, yy, cw, ch)
        badge_circle(s, x0 + 0.55, yy + 0.55, 0.50, hid, size=13)
        textbox(s, x0 + 1.20, yy + 0.32, cw - 1.40, 0.45,
                [(name, 17, True, INK)])
        textbox(s, x0 + 0.30, yy + 1.00, cw - 0.60, 1.00,
                [(body, 13, False, MUTED, True)])

    # Bottom card — plain shadow
    bx, by, bw, bh = 1.40, 6.95, SW - 2.80, 0.50
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("The Master Table fixes the truth. Each chart is one projection of it.",
              14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 4 — THE TRAP  (chart vs latent data world)
# ===========================================================================
def slide_trap():
    s = blank()
    title_centered(s, [("A chart is a ", INK), ("projection", ACCENT),
                       (" of a hidden table.", INK)],
                   y=0.85, size=36)
    subtitle_centered(s,
        "Each rendered chart is a deterministic SQL query over a Master Table M.",
        y=1.70, size=15)

    # Two-column cards
    cy = 2.45
    ch = 3.00
    gap = 0.40
    cw = (SW - 1.10 - gap) / 2

    # Visible — what the agent sees
    labelled_card(s, 0.55, cy, cw, ch, "Visible · what the agent sees",
                  [[("Two bars. One number. ", 20, True, INK)],
                   [("No information about what was filtered out.",
                     15, False, MUTED, True)]],
                  label_color=MUTED)

    # Hidden — what the Master Table holds
    rx = 0.55 + cw + gap
    labelled_card(s, rx, cy, cw, ch, "Hidden · what the Master Table holds",
                  [[("A DAG of typed columns over atomic rows.",
                     20, True, INK)]],
                  label_color=MUTED)
    cols = ["order_id", "zone_id", "algorithm", "outcome", "pickup→drop", "click→door"]
    cyy = cy + 1.30
    cxx = rx + 0.30
    cur_x = cxx
    cur_y = cyy
    chip_fill = RGBColor(0xF5, 0xF5, 0xF5)
    for tok in cols:
        chip_w = 0.18 + 0.085 * len(tok)
        if cur_x + chip_w > rx + cw - 0.30:
            cur_y += 0.42
            cur_x = cxx
        rounded(s, cur_x, cur_y, chip_w, 0.32, fill=chip_fill)
        textbox(s, cur_x, cur_y, chip_w, 0.32,
                [(tok, 10, True, INK, False, MONO)],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        cur_x += chip_w + 0.10

    # bottom conclusion card
    bx, by, bw, bh = 2.50, 5.95, SW - 5.00, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("The truth has structure. The chart shows one slice of it.",
              16, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 4 — BENCHMARK GAP
# ===========================================================================
def slide_benchmark_gap():
    s = blank()
    eyebrow(s, "§ 1 · Why this is hard")
    title_centered(s, [("Benchmarks test ", INK), ("reading", ACCENT),
                       (", not investigation.", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "Models must answer from one given chart. They cannot decide to look again.",
        y=1.55, size=15)

    cy = 2.20
    ch = 2.30
    cw = (SW - 1.10 - 0.40) / 3
    gap = 0.20
    stats = [
        ("−30",  "pts on real reasoning",
         "ChartMuseum 2025 — human 93% vs top VLM 63%."),
        ("2–3",  "charts ⇒ collapse",
         "InterChart 2025 — accuracy falls across multi-chart splits."),
        ("×",    "ungrounded answers",
         "ChartPoint 2025 — models fail to point to correct elements."),
    ]
    for i, (big, lbl, sub) in enumerate(stats):
        x0 = 0.55 + i * (cw + gap)
        stat_card(s, x0, cy, cw, ch, big, lbl, sub)

    # Existing protocol vs this work
    cy2 = 4.80
    ch2 = 2.00
    cw2 = (SW - 1.10 - 0.40) / 2
    labelled_card(s, 0.55, cy2, cw2, ch2,
                  "Existing protocol",
                  [[("[chart] → answer", 20, True, INK, False, MONO)],
                   [("single-shot, no follow-up, no grounding",
                     14, False, MUTED, True)]],
                  label_color=MUTED)
    labelled_card(s, 0.55 + cw2 + 0.40, cy2, cw2, ch2,
                  "This work",
                  [[("[D₀] ↻ request more views → answer + bbox",
                     17, True, INK, False, MONO)],
                   [("budgeted, grounded, multi-step",
                     14, False, MUTED, True)]],
                  label_color=MUTED)
    return s


# ===========================================================================
# SLIDE 5 — TWO CONTRIBUTIONS
# ===========================================================================
def slide_contributions():
    s = blank()
    title_centered(s, [("Two contributions.", INK)],
                   y=0.95, size=44)
    subtitle_centered(s,
        "A hidden Master Table to probe, and a protocol that probes it through charts.",
        y=1.95, size=15)

    cy = 2.90
    ch = 3.30
    cw = (SW - 1.10 - 0.50) / 2

    x0 = 0.55
    card(s, x0, cy, cw, ch)
    contrib_tag(s, x0 + 0.40, cy + 0.40, cw - 0.80, 0.30, "C1 · synthetic data")
    textbox(s, x0 + 0.40, cy + 0.90, cw - 0.80, 0.55,
            [("Builds the world.", 22, True, INK)])
    textbox(s, x0 + 0.40, cy + 1.70, cw - 0.80, 1.40,
            [("An LLM writes Python over a typed SDK. The output is a Master Table; deterministic SQL projection yields 10–30+ chart QA tasks per table.",
              14, False, MUTED, True)])

    x1 = x0 + cw + 0.50
    card(s, x1, cy, cw, ch)
    contrib_tag(s, x1 + 0.40, cy + 0.40, cw - 0.80, 0.30, "C2 · active chart reasoning")
    textbox(s, x1 + 0.40, cy + 0.90, cw - 0.80, 0.55,
            [("Investigates the world.", 22, True, INK)])
    textbox(s, x1 + 0.40, cy + 1.70, cw - 0.80, 1.40,
            [("A budgeted protocol with five actions and bbox grounding. Four investigation moves: Read, Reveal, Reconcile, Debunk.",
              14, False, MUTED, True)])

    # Bottom plain card
    cx, cy2, cw2, ch2 = 1.60, 6.55, SW - 3.20, 0.50
    card(s, cx, cy2, cw2, ch2)
    textbox(s, cx, cy2, cw2, ch2,
            [("C1 builds the world. ", 14, True, INK),
             ("C2 lets the agent investigate it.", 14, True, ACCENT)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 6 — PIPELINE OVERVIEW
# ===========================================================================
def slide_overview():
    s = blank()
    title_centered(s, [("Four phases. Phase 3 is ", INK),
                       ("deterministic", ACCENT), (".", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "No LLM touches the chart or the questions. The Master Table is the contract.",
        y=1.55, size=15)

    # Top row
    top_y = 2.25
    step_h = 1.40
    n = 4
    gap = 0.20
    step_w = (SW - 1.10 - (n - 1) * gap - (n - 1) * 0.20) / n   # leave room for arrows
    cur_x = 0.55
    phases = [
        ("Phase 0", "Domain Pool",       "200+ sub-topics · cached, deduped",   WHITE),
        ("Phase 1", "Scenario",          "Realistic study · entities · metrics", WHITE),
        ("Phase 2", "SDK Script",        "Code-as-DGP · execution-error loop",  WHITE),
        ("Output",     "Master Table", "Atomic rows · typed schema metadata",  WHITE),
    ]
    for i, (ph, name, sub, fill) in enumerate(phases):
        card(s, cur_x, top_y, step_w, step_h, fill=fill)
        textbox(s, cur_x + 0.10, top_y + 0.18, step_w - 0.20, 0.25,
                [(ph.upper(), 9, True, MUTED, False, MONO)],
                align=PP_ALIGN.CENTER)
        textbox(s, cur_x + 0.10, top_y + 0.48, step_w - 0.20, 0.40,
                [(name, 18, True, INK)], align=PP_ALIGN.CENTER)
        textbox(s, cur_x + 0.10, top_y + 0.90, step_w - 0.20, 0.45,
                [(sub, 10, False, MUTED, True)], align=PP_ALIGN.CENTER)
        if i < n - 1:
            ax = cur_x + step_w + gap / 2
            textbox(s, ax - 0.20, top_y + step_h / 2 - 0.20, 0.40, 0.40,
                    [("→", 22, True, MUTED)], align=PP_ALIGN.CENTER,
                    anchor=MSO_ANCHOR.MIDDLE)
        cur_x += step_w + gap + 0.20

    # Down arrow
    textbox(s, 0, top_y + step_h + 0.05, SW, 0.50,
            [("↓", 28, True, MUTED)], align=PP_ALIGN.CENTER)

    # Bottom row
    bot_y = 4.85
    bphases = [
        ("Phase 3",        "SQL Projection",      "10–30+ chart views per table",    WHITE),
        ("Runtime",        "Investigation Loop",  "request_view, point, commit, answer",  WHITE),
        ("Cases",      "Charts, QA, bbox trails", "One Master Table yields N cases", WHITE),
    ]
    nb = 3
    step_w_b = (SW - 1.10 - (nb - 1) * gap - (nb - 1) * 0.20) / nb
    cur_x = 0.55
    for i, (ph, name, sub, fill) in enumerate(bphases):
        card(s, cur_x, bot_y, step_w_b, step_h, fill=fill)
        textbox(s, cur_x + 0.10, bot_y + 0.18, step_w_b - 0.20, 0.25,
                [(ph.upper(), 9, True, MUTED, False, MONO)],
                align=PP_ALIGN.CENTER)
        textbox(s, cur_x + 0.10, bot_y + 0.48, step_w_b - 0.20, 0.40,
                [(name, 18, True, INK)], align=PP_ALIGN.CENTER)
        textbox(s, cur_x + 0.10, bot_y + 0.90, step_w_b - 0.20, 0.45,
                [(sub, 10, False, MUTED, True)], align=PP_ALIGN.CENTER)
        if i < nb - 1:
            ax = cur_x + step_w_b + gap / 2
            textbox(s, ax - 0.20, bot_y + step_h / 2 - 0.20, 0.40, 0.40,
                    [("→", 22, True, MUTED)], align=PP_ALIGN.CENTER,
                    anchor=MSO_ANCHOR.MIDDLE)
        cur_x += step_w_b + gap + 0.20
    return s


# ===========================================================================
# SLIDE 7 — SECTION TRANSITION: C1
# ===========================================================================
def slide_section_c1():
    s = blank()
    textbox(s, 0, 2.85, SW, 1.20,
            [[("C1 · Building the ", 50, True, INK),
              ("Master Table", 50, True, ACCENT),
              (".", 50, True, INK)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 0, 4.30, SW, 0.55,
            [("Phases 0 through 3, walked through on one example.",
              19, False, MUTED, True)],
            align=PP_ALIGN.CENTER)
    return s


# ===========================================================================
# SLIDE 8 — PHASE 0 (3 concrete domain examples)
# ===========================================================================
def slide_phase0():
    s = blank()
    title_centered(s, [("Phase 0 — ", INK), ("domain pool", ACCENT), (".", INK)],
                   y=0.85, size=32)
    subtitle_centered(s,
        "200+ fine-grained sub-topics, embedding-deduplicated and complexity-balanced. Generated once.",
        y=1.65, size=15)

    cy = 2.40
    ch = 3.70
    cw = (SW - 1.10 - 0.50) / 3
    gap = 0.25
    examples = [
        ("simple", [
            [("{", "n")],
            [('  "name": ',  "n"), ('"Coffee shop POS"', "s"), (",", "n")],
            [('  "topic": ', "n"), ('"Retail & Services"', "s"), (",", "n")],
            [('  "tier": ',  "n"), ('"simple"', "s"), (",", "n")],
            [('  "entities": [', "n"), ('"drink"', "s"), (', ', "n"),
             ('"hour"', "s"), ('],', "n")],
            [('  "metrics": [', "n"), ('"revenue"', "s"), ('],', "n")],
            [('  "grain": ',  "n"), ('"hourly"', "s")],
            [("}", "n")],
        ]),
        ("medium", [
            [("{", "n")],
            [('  "name": ',  "n"), ('"Urban food delivery"', "s"), (",", "n")],
            [('  "topic": ', "n"), ('"Logistics"', "s"), (",", "n")],
            [('  "tier": ',  "n"), ('"medium"', "s"), (",", "n")],
            [('  "entities": [', "n"), ('"order"', "s"), (', ', "n"),
             ('"zone"', "s"), ('],', "n")],
            [('  "metrics": [', "n"), ('"delivery_min"', "s"), ('],', "n")],
            [('  "grain": ',  "n"), ('"per order"', "s")],
            [("}", "n")],
        ]),
        ("complex", [
            [("{", "n")],
            [('  "name": ',  "n"), ('"Urban rail scheduling"', "s"), (",", "n")],
            [('  "topic": ', "n"), ('"Transportation"', "s"), (",", "n")],
            [('  "tier": ',  "n"), ('"complex"', "s"), (",", "n")],
            [('  "entities": [', "n"), ('"line"', "s"), (', ', "n"),
             ('"station"', "s"), ('],', "n")],
            [('  "metrics": [', "n"), ('"ridership"', "s"), (', ', "n"),
             ('"on_time"', "s"), ('],', "n")],
            [('  "grain": ',  "n"), ('"daily"', "s")],
            [("}", "n")],
        ]),
    ]
    for i, (label, lines) in enumerate(examples):
        x0 = 0.55 + i * (cw + gap)
        textbox(s, x0 + 0.10, cy, cw - 0.20, 0.30,
                [(label.upper(), 11, True, MUTED)])
        code_block(s, x0, cy + 0.35, cw, ch - 0.35, lines,
                   size=10, line_h=0.30)

    # Bottom callout
    bx, by, bw, bh = 1.80, 6.30, SW - 3.60, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Generated once and cached. Stratified sampling preserves complexity balance.",
              14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 9 — PHASE 1 (Shanghai Metro scenario)
# ===========================================================================
def slide_phase1():
    s = blank()
    title_centered(s, [("Phase 1 — domain to ", INK),
                       ("scenario", ACCENT), (".", INK)],
                   y=0.85, size=32)
    subtitle_centered(s,
        "Sample one domain. Instantiate entities, metrics, time grain, target rows. No chart type bound yet.",
        y=1.65, size=15)

    cy = 2.30
    ch = 3.95
    lw = (SW - 1.10) * 0.42
    rw = (SW - 1.10) * 0.55
    gap = SW - 1.10 - lw - rw

    # LEFT — input domain
    x0 = 0.55
    textbox(s, x0 + 0.10, cy, lw - 0.20, 0.30,
            [("INPUT · DOMAIN", 11, True, MUTED)])
    in_lines = [
        [("{", "n")],
        [('  "name": ', "n"), ('"Urban rail scheduling"', "s"), (",", "n")],
        [('  "tier": ', "n"), ('"complex"', "s"), (",", "n")],
        [('  "entity_hint": [', "n"), ('"line"', "s"), (", ", "n"),
         ('"station"', "s"), ("],", "n")],
        [('  "metric_hint": [', "n")],
        [('    {', "n"), ('"name"', "k"), (':', "n"), ('"ridership"', "s"), (",", "n")],
        [('     ', "n"), ('"unit"', "k"), (':', "n"), ('"10k pax"', "s"), ("},", "n")],
        [('    {', "n"), ('"name"', "k"), (':', "n"), ('"on_time_rate"', "s"), (",", "n")],
        [('     ', "n"), ('"unit"', "k"), (':', "n"), ('"%"', "s"), ("}", "n")],
        [("  ]", "n")],
        [("}", "n")],
    ]
    code_block(s, x0, cy + 0.35, lw, ch - 0.35, in_lines, size=10.5, line_h=0.28)

    # RIGHT — output scenario
    x1 = x0 + lw + gap
    textbox(s, x1 + 0.10, cy, rw - 0.20, 0.30,
            [("OUTPUT · SCENARIO  (LLM)", 11, True, MUTED)])
    out_lines = [
        [("{", "n")],
        [('  "title": ',   "n"), ('"2024 H1 Shanghai Metro Ridership Log"', "s"), (",", "n")],
        [('  "context": ', "n"), ('"Shanghai Transport Commission collected', "s")],
        [('               daily ridership and operational data..."', "s"), (",", "n")],
        [('  "entities": [', "n")],
        [('    ', "n"), ('"Line 1 (Xinzhuang–Fujin Rd)"', "s"), (",", "n")],
        [('    ', "n"), ('"Line 2 (Pudong Airport–Xujing)"', "s"), (", ...", "n")],
        [('  ],', "n")],
        [('  "metrics": [', "n")],
        [('    {', "n"), ('"name"', "k"), (':', "n"), ('"daily_ridership"', "s"),
         (', ', "n"), ('"range"', "k"), (': [5, 120]},', "n")],
        [('    {', "n"), ('"name"', "k"), (':', "n"), ('"on_time_rate"', "s"),
         (', ', "n"), ('"range"', "k"), (': [85.0, 99.9]}', "n")],
        [('  ],', "n")],
        [('  "target_rows": 900', "n")],
        [("}", "n")],
    ]
    code_block(s, x1, cy + 0.35, rw, ch - 0.35, out_lines, size=10.5, line_h=0.25)

    # Bottom callout
    bx, by, bw, bh = 1.60, 6.40, SW - 3.20, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Scenarios are ", 14, True, INK),
             ("domain-driven", 14, True, ACCENT),
             (", not visualization-driven.", 14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 10 — PHASE 2 SDK INTRO  (8 calls)
# ===========================================================================
def slide_phase2_intro():
    s = blank()
    title_centered(s, [("Phase 2 — the LLM writes ", INK),
                       ("Python", ACCENT), (", not JSON.", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "Two ordered steps. Eight call types. Every column declares its own data-generating program.",
        y=1.65, size=15)

    cy = 2.40
    ch = 3.85
    cw = (SW - 1.10 - 0.50) / 2

    # LEFT — Step 1
    x0 = 0.55
    card(s, x0, cy, cw, ch)
    textbox(s, x0 + 0.30, cy + 0.25, cw - 0.60, 0.30,
            [("STEP 1 · COLUMN DECLARATIONS", 12, True, MUTED)])
    step1 = [
        ("add_category",           "categorical · group · parent"),
        ("add_temporal",           "time grain · derived calendar"),
        ("add_measure",            "stochastic root · y ~ Dist(θ)"),
        ("add_measure_structural", "DAG-derived · closed-form"),
    ]
    for i, (call, desc) in enumerate(step1):
        yy = cy + 0.75 + i * 0.78
        textbox(s, x0 + 0.30, yy, cw - 0.60, 0.34,
                [(call, 15, True, ACCENT, False, MONO)])
        textbox(s, x0 + 0.30, yy + 0.34, cw - 0.60, 0.34,
                [(desc, 13, False, MUTED, True)])

    # RIGHT — Step 2
    x1 = x0 + cw + 0.50
    card(s, x1, cy, cw, ch)
    textbox(s, x1 + 0.30, cy + 0.25, cw - 0.60, 0.30,
            [("STEP 2 · RELATIONSHIPS AND PATTERNS", 12, True, MUTED)])
    step2 = [
        ("declare_orthogonal",    "independence across groups"),
        ("add_group_dependency",  "root-only DAG cross-group dep"),
        ("inject_pattern",        "trend · outlier · ranking reversal"),
        ("set_realism",           "noise · missingness · censoring"),
    ]
    for i, (call, desc) in enumerate(step2):
        yy = cy + 0.75 + i * 0.78
        textbox(s, x1 + 0.30, yy, cw - 0.60, 0.34,
                [(call, 15, True, ACCENT, False, MONO)])
        textbox(s, x1 + 0.30, yy + 0.34, cw - 0.60, 0.34,
                [(desc, 13, False, MUTED, True)])

    # Bottom callout
    bx, by, bw, bh = 1.60, 6.40, SW - 3.20, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Each measure is declared ", 14, True, INK),
             ("once", 14, True, ACCENT),
             (". No patching across calls.", 14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 11 — PHASE 2 EXAMPLE A: SWIFTEATS SDK CODE
# ===========================================================================
def slide_phase2_swift():
    s = blank()
    title_centered(s, [("SwiftEats — ", INK), ("zone × algorithm", ACCENT),
                       (" drives both outcomes.", INK)],
                   y=0.85, size=28)
    subtitle_centered(s,
        "Acceptance and delivery time both depend on the interaction of zone and algorithm.",
        y=1.45, size=14)

    lines = [
        [("# Step 1: columns", "c")],
        [("sim.", "n"), ("add_category", "k"),
         ('("zone_tier", values=["downtown","mid","peripheral"], group="geo")', "s")],
        [("sim.", "n"), ("add_category", "k"),
         ('("algorithm", values=["old","new"], group="system")', "s")],
        [("sim.", "n"), ("add_measure", "k"),
         ('("distance_km", family="lognormal",', "s")],
        [('                 param_model={"mu": 1.5, "sigma": 0.6})', "n")],
        [("# Step 2: zone × algorithm drives accept; both drive p→d", "c")],
        [("sim.", "n"), ("add_group_dependency", "k"),
         ('("accepted", on=["zone_tier","algorithm"],', "s")],
        [('    conditional_weights={', "n")],
        [('       ("peripheral","new"): {"yes":0.41, "no":0.59},', "s")],
        [('       ("peripheral","old"): {"yes":0.82, "no":0.18}, ', "s"),
         ("# ...", "c")],
        [('    })', "n")],
        [("sim.", "n"), ("add_measure_structural", "k"),
         ('("pickup_to_dropoff_min",', "s")],
        [('    formula="8 + 3.5*distance_km - 4*(algorithm==\'new\')",', "s")],
        [('    noise={"sigma":2.0})', "s")],
        [("# zone-selection trick: new algo silently drops the periphery", "c")],
        [("sim.", "n"), ("inject_pattern", "k"),
         ('("dominance_shift",', "s")],
        [('    target="algorithm==\'new\' & zone_tier==\'peripheral\'",', "s")],
        [('    col="accepted", params={"drop_rate":0.43})', "s")],
    ]
    code_block(s, 0.80, 1.95, SW - 1.60, 4.50, lines, size=11.0, line_h=0.245)

    bx, by, bw, bh = 1.80, 6.60, SW - 3.60, 0.50
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Every behavior the agent must discover is declared once in the script.",
              13, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 12 — PHASE 2 EXAMPLE B: HOSPITAL WAIT MINUTES
# ===========================================================================
def slide_phase2_hospital():
    s = blank()
    eyebrow(s, "§ 3 · C1 · Phase 2 · Example B · Hospital ER")
    title_centered(s, [("Hospital ER — ", INK),
                       ("severity × hospital", ACCENT),
                       (" → wait.", INK)],
                   y=0.85, size=28)

    lines = [
        [("# Step 1: nested hierarchy and conditional severity", "c")],
        [("sim.", "n"), ("add_category", "k"),
         ('("hospital", values=["Xiehe","Huashan","Ruijin","Tongren"],', "s")],
        [("                  weights=[0.30,0.25,0.25,0.20], group=", "n"),
         ('"entity"', "s"), (")", "n")],
        [("sim.", "n"), ("add_category", "k"),
         ('("department", values=["Internal","Surgery","ER","Peds"],', "s")],
        [("                  weights=[0.35,0.25,0.25,0.15], group=", "n"),
         ('"entity"', "s"), (", parent=", "n"), ('"hospital"', "s"), (")", "n")],
        [("sim.", "n"), ("add_category", "k"),
         ('("severity", values=["Mild","Moderate","Severe"],', "s")],
        [('                  weights=[0.50,0.35,0.15], group="patient")', "n")],
        [("", "n")],
        [("# wait_minutes — parameters vary by categorical context", "c")],
        [("sim.", "n"), ("add_measure", "k"),
         ('("wait_minutes", family="lognormal",', "s")],
        [("    param_model={", "n")],
        [('        "mu": {"intercept":2.8, "effects":{', "s")],
        [('            "severity": {"Mild":0.0, "Moderate":0.4, "Severe":0.9},', "s")],
        [('            "hospital": {"Xiehe":0.2, "Huashan":-0.1, "Ruijin":0.0, "Tongren":0.1}', "s")],
        [("        }},", "n")],
        [('        "sigma": {"intercept":0.35}', "s")],
        [("    })", "n")],
        [("sim.", "n"), ("declare_orthogonal", "k"),
         ('("entity", "patient",', "s")],
        [('    rationale="Severity is independent of which hospital a patient picks.")', "s")],
    ]
    code_block(s, 0.80, 1.55, SW - 1.60, 4.95, lines, size=10.5, line_h=0.25)

    bx, by, bw, bh = 1.30, 6.55, SW - 2.60, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Closed-form: ", 13, True, INK),
             ("μ = 2.8 + 0.9 (severe) + 0.2 (Xiehe) = 3.9", 13, True, ACCENT, False, MONO),
             (" — verifiable, not chained.", 13, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    pageno(s, 13)
    return s


# ===========================================================================
# SLIDE 13 — SELF-CORRECTING LOOP
# ===========================================================================
def slide_self_correct():
    s = blank()
    title_centered(s, [("Validation runs at the ", INK),
                       ("SDK level", ACCENT),
                       (", before any chart.", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "Typed exceptions feed back to the LLM. Three validator layers run after every build. Up to three retries.",
        y=1.65, size=14)

    # LEFT — try/catch story
    lx = 0.55
    lw = (SW - 1.10) * 0.58
    rx = lx + lw + 0.40
    rw = SW - 1.10 - lw - 0.40

    # Attempt 1 (bad)
    a1_y = 2.40
    a1_h = 1.85
    card(s, lx, a1_y, lw, a1_h, fill=BAD_SOFT)
    textbox(s, lx + 0.30, a1_y + 0.15, lw - 0.60, 0.30,
            [("ATTEMPT 1 · UNBOUNDED SPEEDUP", 11, True, BAD)])
    a1_lines = [
        [("sim.", "n"), ("add_measure_structural", "k"),
         ('("pickup_to_dropoff_min",', "s")],
        [('   formula="5 - 30*(algorithm==\'new\')")', "s")],
    ]
    yy = a1_y + 0.55
    for segs in a1_lines:
        runs = []
        for text, kind in segs:
            col = CODE_KEY if kind == 'k' else (CODE_STR if kind == 's' else INK)
            bold = (kind == 'k')
            runs.append((text, 11, bold, col, False, MONO))
        textbox(s, lx + 0.30, yy, lw - 0.60, 0.28, runs)
        yy += 0.27
    textbox(s, lx + 0.30, a1_y + a1_h - 0.45, lw - 0.60, 0.35,
            [("Validator L2: ", 12, True, BAD),
             ("min(p→d) = −25 < 0", 12, True, INK, False, MONO),
             (" ⇒ SDKException", 12, True, BAD)],
            anchor=MSO_ANCHOR.MIDDLE)

    # Arrow
    textbox(s, lx, a1_y + a1_h + 0.05, lw, 0.40,
            [("↓  feedback to LLM, up to 3 retries", 12, True, MUTED, True)],
            align=PP_ALIGN.CENTER)

    # Attempt 2 (good)
    a2_y = a1_y + a1_h + 0.55
    a2_h = 1.85
    card(s, lx, a2_y, lw, a2_h, fill=GOOD_SOFT)
    textbox(s, lx + 0.30, a2_y + 0.15, lw - 0.60, 0.30,
            [("ATTEMPT 2 · BOUNDED, DISTANCE-AWARE", 11, True, GOOD)])
    a2_lines = [
        [("sim.", "n"), ("add_measure_structural", "k"),
         ('("pickup_to_dropoff_min",', "s")],
        [('   formula="8 + 3.5*distance_km - 4*(algorithm==\'new\')",', "s")],
        [('   noise={"sigma":2.0})', "s")],
    ]
    yy = a2_y + 0.55
    for segs in a2_lines:
        runs = []
        for text, kind in segs:
            col = CODE_KEY if kind == 'k' else (CODE_STR if kind == 's' else INK)
            bold = (kind == 'k')
            runs.append((text, 11, bold, col, False, MONO))
        textbox(s, lx + 0.30, yy, lw - 0.60, 0.28, runs)
        yy += 0.27
    textbox(s, lx + 0.30, a2_y + a2_h - 0.45, lw - 0.60, 0.35,
            [("All three layers pass. ", 12, True, GOOD),
             ("1000 atomic rows written.", 12, False, INK)],
            anchor=MSO_ANCHOR.MIDDLE)

    # RIGHT — 3-layer validator
    val_y = 2.40
    val_h = a2_y + a2_h - val_y
    card(s, rx, val_y, rw, val_h)
    textbox(s, rx + 0.30, val_y + 0.20, rw - 0.60, 0.30,
            [("THREE VALIDATOR LAYERS", 11, True, MUTED)])
    layers = [
        ("L1", "Structural", "Schema valid. Types compatible. Every DAG acyclic."),
        ("L2", "Statistical", "Moments in range. Correlations feasible. Bounds respected."),
        ("L3", "Pattern",     "Injected trends, drop-outs, and outliers are recoverable."),
    ]
    for i, (tag, name, body) in enumerate(layers):
        yy = val_y + 0.75 + i * 1.15
        badge_circle(s, rx + 0.50, yy + 0.30, 0.50, tag, size=12)
        textbox(s, rx + 0.95, yy + 0.05, rw - 1.10, 0.30,
                [(name, 16, True, INK)])
        textbox(s, rx + 0.95, yy + 0.35, rw - 1.10, 0.60,
                [(body, 11, False, MUTED, True)])
    return s


# ===========================================================================
# SLIDE 13 — MASTER TABLE (DAG + rows)
# ===========================================================================
def slide_master_table():
    s = blank()
    title_centered(s, [("The Master Table.", INK)],
                   y=0.85, size=40)
    subtitle_centered(s,
        "M is a DAG over typed columns. Each row is one atomic event.",
        y=1.65, size=15)

    # LEFT — schema dag
    lx = 0.55
    lw = (SW - 1.10) * 0.60
    rw = (SW - 1.10) * 0.36
    rx = lx + lw + (SW - 1.10 - lw - rw)
    ly = 2.40
    lh = 3.60
    card(s, lx, ly, lw, lh)
    textbox(s, lx + 0.30, ly + 0.20, lw - 0.60, 0.30,
            [("SCHEMA DAG · SwiftEats", 11, True, MUTED)])

    # Nodes
    nodes = {
        "zone_tier":   (lx + 0.70, ly + 1.20),
        "algorithm":   (lx + 2.85, ly + 1.20),
        "accepted":    (lx + 4.95, ly + 1.20),
        "distance_km": (lx + 0.70, ly + 2.70),
        "pickup_drop": (lx + 4.45, ly + 2.70),
    }
    node_w, node_h = 1.40, 0.42
    style = {
        "zone_tier":   (ACCENT_SOFT, ACCENT,  "zone_tier"),
        "algorithm":   (WHITE,       INK,     "algorithm"),
        "accepted":    (WHITE,       INK,     "accepted"),
        "distance_km": (WHITE,       INK,     "distance_km"),
        "pickup_drop": (WHITE,       INK,     "pickup→drop"),
    }
    for name, (cx, cy) in nodes.items():
        fill, edge, lbl = style[name]
        rounded(s, cx - node_w/2, cy - node_h/2, node_w, node_h,
                fill=fill, line=edge, line_w=1.2)
        textbox(s, cx - node_w/2, cy - node_h/2, node_w, node_h,
                [(lbl, 11, True, edge, False, MONO)],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Edges
    def edge(a, b, color=INK, weight=1.4, dash=False):
        ax, ay = nodes[a]; bx, by = nodes[b]
        if abs(ay - by) < 0.05:
            x1 = ax + node_w/2 + 0.02; x2 = bx - node_w/2 - 0.02
            line_seg(s, x1, ay, x2, by, color=color, weight=weight, dash=dash, arrow_end=True)
        else:
            line_seg(s, ax + node_w/2 + 0.02, ay,
                     bx - node_w/2 - 0.02, by,
                     color=color, weight=weight, dash=dash, arrow_end=True)
    edge("zone_tier",   "algorithm",   color=ACCENT, weight=1.8)
    edge("algorithm",   "accepted",    color=INK,    weight=1.4)
    edge("distance_km", "pickup_drop", color=INK,    weight=1.4)
    edge("algorithm",   "pickup_drop", color=INK,    weight=1.2, dash=True)

    textbox(s, lx + 1.45, ly + 0.70, 1.50, 0.25,
            [("zone selection", 11, True, ACCENT, True)],
            align=PP_ALIGN.CENTER)
    textbox(s, lx + 1.80, ly + 2.30, 2.10, 0.25,
            [("distance scales time", 10, True, MUTED, True)],
            align=PP_ALIGN.CENTER)

    # RIGHT — atomic rows preview
    ry = ly
    rh = lh
    card(s, rx, ry, rw, rh)
    textbox(s, rx + 0.20, ry + 0.20, rw - 0.40, 0.30,
            [("ATOMIC ROWS · 1 ROW = 1 ORDER", 11, True, MUTED)])

    headers = ["id", "zone", "algo", "out", "p→d"]
    col_w = (rw - 0.40) / 5
    tbl_y = ry + 0.65
    # header row
    for j, hdr in enumerate(headers):
        rect(s, rx + 0.20 + j * col_w, tbl_y, col_w, 0.30, fill=INK)
        textbox(s, rx + 0.20 + j * col_w, tbl_y, col_w, 0.30,
                [(hdr, 10, True, WHITE, False, MONO)],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rows = [
        ("01", "ctr", "new", "✓", "16"),
        ("02", "per", "new", "×", "—"),
        ("03", "mid", "old", "✓", "28"),
        ("04", "ctr", "new", "✓", "14"),
        ("05", "per", "old", "✓", "38"),
        ("06", "per", "new", "×", "—"),
        ("07", "mid", "new", "✓", "19"),
    ]
    for ri, row in enumerate(rows):
        ry_i = tbl_y + 0.30 + ri * 0.28
        for j, v in enumerate(row):
            fill = WHITE if ri % 2 == 0 else CODE_BG
            rect(s, rx + 0.20 + j * col_w, ry_i, col_w, 0.28, fill=fill)
            textbox(s, rx + 0.20 + j * col_w, ry_i, col_w, 0.28,
                    [(v, 10, False, INK, False, MONO)],
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, rx + 0.20, ry + rh - 0.40, rw - 0.40, 0.30,
            [("… 1000 rows total", 10, False, MUTED, True)],
            align=PP_ALIGN.CENTER)

    # Bottom callout
    bx, by, bw, bh = 1.60, 6.30, SW - 3.20, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Aggregation lives downstream. Bar totals equal pie totals equal line totals.",
              14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 14 — TABLE AMORTIZATION (1 M → many views)
# ===========================================================================
def slide_amortize():
    s = blank()
    title_centered(s, [("Phase 3 — one table, ", INK),
                       ("many views", ACCENT), (".", INK)],
                   y=0.85, size=32)
    subtitle_centered(s,
        "Deterministic SQL projection yields 10–30+ coherent tasks per Master Table.",
        y=1.65, size=15)

    # Master Table marker — outlined neutral box, not a red pill
    mp_w = 6.40
    mp_x = SW/2 - mp_w/2
    mp_y = 2.20
    mp_h = 0.60
    rounded(s, mp_x, mp_y, mp_w, mp_h, fill=WHITE, line=INK, line_w=1.6)
    textbox(s, mp_x, mp_y, mp_w, mp_h,
            [("Master  M  ·  SwiftEats  ·  1000 atomic rows",
              14, True, INK, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 0, mp_y + mp_h + 0.05, SW, 0.45,
            [("↓", 24, True, MUTED)], align=PP_ALIGN.CENTER)

    # Three lens cards
    cy = 3.65
    ch = 2.65
    cw = (SW - 1.10 - 0.50) / 3
    gap = 0.25
    lenses = [
        ("Bar · avg time by algorithm", "Avg time by algorithm",
         "SELECT algorithm, AVG(p2d)\n  FROM M GROUP BY algorithm"),
        ("Heatmap · accept rate × zone", "Accept rate × zone",
         "SELECT zone, algo, AVG(accept)\n  FROM M GROUP BY zone, algo"),
        ("Funnel · stage × algorithm", "Stage × algorithm",
         "SELECT stage, COUNT(*)\n  FROM M GROUP BY algo, stage"),
    ]
    for i, (label, head, sql) in enumerate(lenses):
        x0 = 0.55 + i * (cw + gap)
        card(s, x0, cy, cw, ch)
        textbox(s, x0 + 0.30, cy + 0.20, cw - 0.60, 0.30,
                [(label.upper(), 11, True, MUTED)])
        textbox(s, x0 + 0.30, cy + 0.55, cw - 0.60, 0.45,
                [(head, 17, True, INK)])
        # SQL block
        rect(s, x0 + 0.30, cy + 1.20, cw - 0.60, 1.25, fill=CODE_BG)
        sql_lines = sql.split("\n")
        for j, ln in enumerate(sql_lines):
            kw_set = {"SELECT", "FROM", "GROUP", "BY", "COUNT", "AVG"}
            tokens = []
            buf = ""
            for ch_ in ln + " ":
                if ch_.isalnum() or ch_ == "_":
                    buf += ch_
                else:
                    if buf:
                        if buf.upper() in kw_set:
                            tokens.append((buf, 11, True, ACCENT, False, MONO))
                        else:
                            tokens.append((buf, 11, False, INK, False, MONO))
                        buf = ""
                    if ch_ == " ":
                        tokens.append((ch_, 11, False, INK, False, MONO))
                    elif ch_:
                        tokens.append((ch_, 11, False, INK, False, MONO))
            textbox(s, x0 + 0.40, cy + 1.30 + j * 0.32, cw - 0.80, 0.32, tokens)

    # Bottom callout
    bx, by, bw, bh = 1.60, 6.50, SW - 3.20, 0.55
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("Same M, three views. Arithmetic consistency holds by construction.",
              14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 15 — OPERATOR PIPELINE EXAMPLE
# ===========================================================================
def slide_operator():
    s = blank()
    title_centered(s, [("A question is a typed ", INK),
                       ("operator pipeline", ACCENT), (".", INK)],
                   y=0.85, size=30)
    subtitle_centered(s,
        "Difficulty equals the number of operators. No LLM is involved.",
        y=1.65, size=15)

    # Question card
    qx, qy, qw, qh = 0.95, 2.40, SW - 1.90, 2.40
    card(s, qx, qy, qw, qh)
    textbox(s, qx + 0.30, qy + 0.20, qw - 0.60, 0.30,
            [("Q · ", 11, True, MUTED),
             ('"Which zone tier has the highest delivery time under the new algorithm?"',
              11, True, MUTED, True)])
    rect(s, qx + 0.30, qy + 0.65, qw - 0.60, qh - 0.85, fill=CODE_BG)
    pipe_lines = [
        [("M  →  ", 14, False, INK, False, MONO),
         ("Filter", 14, True, ACCENT, False, MONO),
         ("(algorithm='new')", 14, False, INK, False, MONO)],
        [("   →  ", 14, False, INK, False, MONO),
         ("GroupBy", 14, True, ACCENT, False, MONO),
         ("(zone_tier, ", 14, False, INK, False, MONO),
         ("AVG", 14, True, ACCENT, False, MONO),
         ("(pickup_to_dropoff_min))", 14, False, INK, False, MONO)],
        [("   →  ", 14, False, INK, False, MONO),
         ("Sort", 14, True, ACCENT, False, MONO),
         ("(", 14, False, INK, False, MONO),
         ("desc", 14, True, ACCENT, False, MONO),
         (")", 14, False, INK, False, MONO)],
        [("   →  ", 14, False, INK, False, MONO),
         ("ArgMax", 14, True, ACCENT, False, MONO)],
        [("   →  ", 14, False, INK, False, MONO),
         ('"peripheral"', 14, False, GOOD, False, MONO),
         ("     ", 14, False, INK, False, MONO),
         ("# 5 ops = Medium difficulty", 12, False, MUTED, True, MONO)],
    ]
    for j, runs in enumerate(pipe_lines):
        textbox(s, qx + 0.50, qy + 0.80 + j * 0.28, qw - 1.00, 0.32, runs)

    # Three stat cards
    cy = 5.10
    ch = 1.80
    cw = (SW - 1.10 - 0.50) / 3
    gap = 0.25
    stats = [
        ("16", "typed operators",     "Set · Scalar · Combinator · Bridge"),
        ("6",  "chart families · 16 types", "Comparison, Trend, Distribution …"),
        ("0",  "LLM calls in Phase 3",     "deterministic, seed-reproducible"),
    ]
    for i, (big, lbl, sub) in enumerate(stats):
        x0 = 0.55 + i * (cw + gap)
        card(s, x0, cy, cw, ch)
        textbox(s, x0, cy + 0.20, cw, 0.80,
                [(big, 44, True, ACCENT, False, MONO)],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, x0 + 0.20, cy + 1.05, cw - 0.40, 0.30,
                [(lbl, 12, True, INK)], align=PP_ALIGN.CENTER)
        textbox(s, x0 + 0.20, cy + 1.35, cw - 0.40, 0.35,
                [(sub, 10, False, MUTED, True)], align=PP_ALIGN.CENTER)

    pageno(s, 16)
    return s


# ===========================================================================
# SLIDE 16 — SECTION: C2
# ===========================================================================
def slide_section_c2():
    s = blank()
    textbox(s, 0, 2.85, SW, 1.20,
            [[("C2 · ", 50, True, INK),
              ("Active", 50, True, ACCENT),
              (" Chart Reasoning.", 50, True, INK)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 0, 4.30, SW, 0.55,
            [("Four moves. Two costly actions. One bbox-grounded answer.",
              19, False, MUTED, True)],
            align=PP_ALIGN.CENTER)
    return s


# ===========================================================================
# SLIDE 17 — FOUR MOVES
# ===========================================================================
def slide_four_moves():
    s = blank()
    title_centered(s, [("Four moves: Read, Reveal, Reconcile, ", INK),
                       ("Debunk", ACCENT), (".", INK)],
                   y=0.85, size=28)
    subtitle_centered(s,
        "Each move names a specific question the agent must answer about the chart.",
        y=1.55, size=15)

    moves = [
        ("1", "Read",       "what does the metric mean?",
         "Identify the two timestamps the metric spans. Identify which orders are in the denominator."),
        ("2", "Reveal",     "what dimension is missing?",
         "Stratify by zone tier. Check whether the new algorithm stopped accepting peripheral orders."),
        ("3", "Reconcile",  "how can both charts be true?",
         "Delivery time fell and refunds rose. Find the funnel structure under which both can hold."),
        ("4", "Debunk",     "does the metric survive a fair yardstick?",
         "Widen the window to click-to-door. Include every cancelled and timed-out order. Recompute."),
    ]
    cy = 2.30
    ch = 2.30
    cw = (SW - 1.10 - 0.40) / 2
    gap = 0.40
    for i, (num, verb, tag, body) in enumerate(moves):
        x0 = 0.55 + (i % 2) * (cw + gap)
        yy = cy + (i // 2) * (ch + 0.30)
        card(s, x0, yy, cw, ch)
        badge_circle(s, x0 + 0.55, yy + 0.55, 0.55, num, size=20)
        textbox(s, x0 + 1.30, yy + 0.30, cw - 1.50, 0.45,
                [(verb, 22, True, INK)])
        textbox(s, x0 + 1.30, yy + 0.78, cw - 1.50, 0.32,
                [(tag, 14, False, MUTED, True)])
        textbox(s, x0 + 0.30, yy + 1.35, cw - 0.60, 0.90,
                [(body, 12.5, False, MUTED, True)])
    return s


# ===========================================================================
# SLIDE 18 — ACTION SPACE
# ===========================================================================
def slide_actions():
    s = blank()
    title_centered(s, [("Five actions. ", INK),
                       ("Two cost budget", ACCENT), (".", INK)],
                   y=0.85, size=32)
    subtitle_centered(s,
        "The budget forces strategy. Every answer must point to a bbox.",
        y=1.65, size=15)

    # Table card
    tx, ty, tw, th = 0.55, 2.30, SW - 1.10, 3.10
    card(s, tx, ty, tw, th)

    # Headers
    cols_x = [tx + 0.40, tx + 2.55, tx + 5.85, tx + 7.85]
    cols_w = [2.10, 3.20, 1.90, tw - (cols_x[-1] - tx) - 0.40]
    hdr = ["ACTION", "ROLE", "COST", "RETURNS"]
    for hx, hw, ht in zip(cols_x, cols_w, hdr):
        textbox(s, hx, ty + 0.25, hw, 0.30,
                [(ht, 10, True, MUTED)])
    line_seg(s, tx + 0.40, ty + 0.65, tx + tw - 0.40, ty + 0.65,
             color=HAIR, weight=0.8)

    actions = [
        ("request_view",  "Pull a new projection",     "−1 Bᵥ",  "PNG only",       True),
        ("point",         "Inspect element locally",   "−1 Bₚ",  "bbox feedback",  True),
        ("commit_belief", "Update working theory",     "free",   "confirmed",      False),
        ("answer",        "Submit answer + bbox",      "free",   "logged",         False),
        ("terminate",     "Trigger scoring",           "free",   "final report",   False),
    ]
    for i, (n, role, cost, ret, costly) in enumerate(actions):
        yy = ty + 0.80 + i * 0.42
        textbox(s, cols_x[0], yy, cols_w[0], 0.36,
                [(n, 13, True, ACCENT if costly else INK, False, MONO)],
                anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, cols_x[1], yy, cols_w[1], 0.36,
                [(role, 12, False, INK)], anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, cols_x[2], yy, cols_w[2], 0.36,
                [(cost, 12, True, ACCENT if costly else MUTED, False, MONO)],
                anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, cols_x[3], yy, cols_w[3], 0.36,
                [(ret, 12, True, INK if costly else MUTED)], anchor=MSO_ANCHOR.MIDDLE)

    # Two plain shadow cards
    py = 5.65
    ph = 1.30
    pw = (SW - 1.10 - 0.40) / 2
    labelled_card(s, 0.55, py, pw, ph, "VISUAL-ONLY RETURN",
                  [[("request_view returns PNG, never CSV.", 14, True, INK)],
                   [("The protocol cannot degenerate into SQL planning.",
                     11, False, MUTED, True)]],
                  label_color=MUTED)
    labelled_card(s, 0.55 + pw + 0.40, py, pw, ph, "BBOX GROUNDING",
                  [[("Every answer cites a bounding box, cross-chart.", 14, True, INK)],
                   [("Grounding is mandatory, not decorative.",
                     11, False, MUTED, True)]],
                  label_color=MUTED)
    return s


# ---------------------------------------------------------------------------
# HYPOTHESIS STATUS LINE — single muted monospace line, no pill widget
# ---------------------------------------------------------------------------
_HSTATUS_LABEL = {
    "pending":   ("not yet",    False),
    "off":       ("not yet",    False),
    "rising":    ("consistent", True),
    "consistent":("consistent", True),
    "partial":   ("partial",    True),
    "confirmed": ("confirmed",  True),
}


def suspect_board(slide, y, states):
    """One-line hypothesis status under the body. Replaces the suspect board.
    Active states render in accent; inactive in muted gray."""
    parts = []
    for i, (hid, _name, state) in enumerate(states):
        label, active = _HSTATUS_LABEL[state]
        color = ACCENT if active else MUTED
        if i > 0:
            parts.append(("     ", 12, True, MUTED, False, MONO))
        parts.append((hid + " · ", 12, True, INK, False, MONO))
        parts.append((label, 12, True, color, False, MONO))
    textbox(slide, 0.55, y, SW - 1.10, 0.35, parts,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def beat_header(slide, runs):
    """Plain centered beat title. ``runs`` is a list of (text, color) pairs."""
    title_centered(slide, runs, y=0.90, size=28)


def beat_question(slide, subtitle):
    """Plain italic subtitle for the beat slide."""
    subtitle_centered(slide, subtitle, y=1.55, size=15)


# ===========================================================================
# SLIDE 19 — B1 · READ
# ===========================================================================
def slide_b1_read():
    s = blank()
    beat_header(s, [("Read — what does ", INK),
                    ('"18 min"', ACCENT), (" measure?", INK)])
    beat_question(s,
        "Inspect the time window and the denominator on the headline chart.")

    # LEFT — returned view: timeline + denominator
    lx, ly, lw, lh = 0.55, 2.15, (SW - 1.10) * 0.58, 3.40
    card(s, lx, ly, lw, lh)
    textbox(s, lx + 0.30, ly + 0.20, lw - 0.60, 0.28,
            [("TIME WINDOW", 11, True, MUTED)])

    # 4-stage timeline
    tl_y = ly + 0.65
    tl_h = 0.42
    tl_l = lx + 0.30
    tl_w = lw - 0.60
    seg_w = tl_w / 4.0
    chip_gray = RGBColor(0xF5, 0xF5, 0xF5)
    rect(s, tl_l,              tl_y, seg_w, tl_h, fill=chip_gray)
    textbox(s, tl_l, tl_y, seg_w, tl_h,
            [("click → assign", 10, True, MUTED)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, tl_l + seg_w,      tl_y, seg_w, tl_h, fill=chip_gray)
    textbox(s, tl_l + seg_w, tl_y, seg_w, tl_h,
            [("prep + wait", 10, True, MUTED)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, tl_l + 2 * seg_w,  tl_y, 2 * seg_w, tl_h, fill=ACCENT)
    textbox(s, tl_l + 2 * seg_w, tl_y, 2 * seg_w, tl_h,
            [("pickup → drop  ·  the 18 min window", 11, True, WHITE)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # tick labels
    for i, lbl in enumerate(["t₀ click", "t₁ assigned", "t₂ pickup", "t₃ delivered"]):
        textbox(s, tl_l - 0.40 + i * seg_w, tl_y + tl_h + 0.04, 0.80, 0.22,
                [(lbl, 9, False, MUTED)], align=PP_ALIGN.CENTER)

    # denominator label
    textbox(s, tl_l, tl_y + 1.20, tl_w, 0.30,
            [("DENOMINATOR", 11, True, MUTED)])

    # denominator bar
    db_y = tl_y + 1.55
    db_h = 0.48
    db_l = tl_l
    db_w = tl_w
    delivered_w = db_w * 0.57
    rect(s, db_l, db_y, db_w, db_h, fill=chip_gray)
    rect(s, db_l, db_y, delivered_w, db_h, fill=INK)
    textbox(s, db_l, db_y, delivered_w, db_h,
            [("570 delivered  ·  included in 18 min", 11, True, WHITE)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, db_l + delivered_w, db_y, db_w - delivered_w, db_h,
            [("430 failed  ·  excluded", 11, True, MUTED)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, db_l, db_y + db_h + 0.04, db_w, 0.24,
            [("1000 orders requested", 10, False, MUTED, True)],
            align=PP_ALIGN.CENTER)

    # RIGHT — key finding
    rx = lx + lw + 0.40
    rw = SW - 0.55 - rx
    card(s, rx, ly, rw, lh, fill=WHITE)
    textbox(s, rx + 0.30, ly + 0.20, rw - 0.60, 0.30,
            [("AFTER READ", 11, True, MUTED)])
    textbox(s, rx + 0.30, ly + 0.60, rw - 0.60, 0.85,
            [[('Two narrow choices sit inside "18 min":', 15, True, INK)]])
    # two narrow choices
    chip_fill = RGBColor(0xF7, 0xF7, 0xF7)
    cy = ly + 1.65
    rounded(s, rx + 0.30, cy, rw - 0.60, 0.55, fill=chip_fill)
    textbox(s, rx + 0.30, cy, rw - 0.60, 0.55,
            [("pickup-to-drop only", 14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rounded(s, rx + 0.30, cy + 0.70, rw - 0.60, 0.55, fill=chip_fill)
    textbox(s, rx + 0.30, cy + 0.70, rw - 0.60, 0.55,
            [("delivered orders only", 14, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    suspect_board(s, 6.40,
        [("h₁", "", "pending"),
         ("h₂", "", "pending"),
         ("h₃", "", "rising"),
         ("h₄", "", "rising")])
    return s


# ===========================================================================
# SLIDE 20 — B2 · REVEAL
# ===========================================================================
def slide_b2_reveal():
    s = blank()
    beat_header(s, [("Reveal — where do the ", INK),
                    ("excluded orders", ACCENT), (" come from?", INK)])
    beat_question(s,
        "Stratify acceptance by zone tier and algorithm.")

    # LEFT — twin heatmaps OLD vs NEW
    lx, ly, lw, lh = 0.55, 2.15, (SW - 1.10) * 0.58, 3.40
    card(s, lx, ly, lw, lh)
    textbox(s, lx + 0.30, ly + 0.20, lw - 0.60, 0.28,
            [("ACCEPTANCE MAP · OLD VS NEW DISPATCHER",
              11, True, MUTED)])

    # 4x4 heatmaps
    grid_size = 0.30
    grid_y = ly + 0.80
    # OLD heatmap on left half
    old_pattern = [[0.55, 0.70, 0.65, 0.55],
                   [0.70, 0.90, 0.88, 0.70],
                   [0.68, 0.88, 0.90, 0.68],
                   [0.55, 0.66, 0.60, 0.55]]
    g1_x = lx + 0.70
    for r in range(4):
        for c in range(4):
            v = old_pattern[r][c]
            fill = GOOD if v >= 0.75 else GOOD_SOFT
            rect(s, g1_x + c * grid_size, grid_y + r * grid_size,
                 grid_size, grid_size, fill=fill)
    textbox(s, g1_x - 0.10, grid_y + 4 * grid_size + 0.06,
            4 * grid_size + 0.20, 0.22,
            [("OLD  ·  uniform 82%", 10, True, GOOD)],
            align=PP_ALIGN.CENTER)

    # arrow between
    textbox(s, lx + lw/2 - 0.30, grid_y + 2 * grid_size - 0.15,
            0.60, 0.30,
            [("→", 22, True, MUTED)], align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE)

    # NEW heatmap on right half: center bright, periphery gray
    g2_x = lx + lw - 4 * grid_size - 0.70
    edge_gray = RGBColor(0xE6, 0xE6, 0xE6)
    for r in range(4):
        for c in range(4):
            is_center = (r in (1, 2)) and (c in (1, 2))
            fill = GOOD if is_center else edge_gray
            rect(s, g2_x + c * grid_size, grid_y + r * grid_size,
                 grid_size, grid_size, fill=fill)
    textbox(s, g2_x - 0.10, grid_y + 4 * grid_size + 0.06,
            4 * grid_size + 0.20, 0.22,
            [("NEW  ·  periphery drops to 41%", 10, True, MUTED)],
            align=PP_ALIGN.CENTER)

    # RIGHT — key finding
    rx = lx + lw + 0.40
    rw = SW - 0.55 - rx
    card(s, rx, ly, rw, lh, fill=WHITE)
    textbox(s, rx + 0.30, ly + 0.20, rw - 0.60, 0.30,
            [("AFTER REVEAL", 11, True, MUTED)])
    textbox(s, rx + 0.30, ly + 0.60, rw - 0.60, 0.95,
            [[("Downtown is steady;", 15, True, INK)],
             [("the periphery ", 15, True, INK),
              ("collapses", 15, True, ACCENT),
              (".", 15, True, INK)]])
    # contrast — tinted comparison cards
    rounded(s, rx + 0.30, ly + 1.85, rw - 0.60, 0.55, fill=GOOD_SOFT)
    textbox(s, rx + 0.30, ly + 1.85, rw - 0.60, 0.55,
            [("Old · periphery  ", 13, True, GOOD),
             ("82%", 18, True, GOOD)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rounded(s, rx + 0.30, ly + 2.55, rw - 0.60, 0.55, fill=BAD_SOFT)
    textbox(s, rx + 0.30, ly + 2.55, rw - 0.60, 0.55,
            [("New · periphery  ", 13, True, BAD),
             ("41%", 18, True, BAD)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    suspect_board(s, 6.40,
        [("h₁", "", "pending"),
         ("h₂", "", "confirmed"),
         ("h₃", "", "rising"),
         ("h₄", "", "rising")])
    return s


# ===========================================================================
# SLIDE 21 — B3 · RECONCILE
# ===========================================================================
def slide_b3_reconcile():
    s = blank()
    beat_header(s, [("Reconcile — how can ", INK),
                    ("both", ACCENT), (" charts be true?", INK)])
    beat_question(s,
        "Inspect the funnel: requested → assigned → picked up → delivered.")

    # LEFT — twin funnels
    lx, ly, lw, lh = 0.55, 2.15, (SW - 1.10) * 0.58, 3.40
    card(s, lx, ly, lw, lh)
    textbox(s, lx + 0.30, ly + 0.20, lw - 0.60, 0.28,
            [("FUNNEL · OLD VS NEW DISPATCHER",
              11, True, MUTED)])

    # Funnel geometry
    f_top = ly + 0.75
    f_h   = 2.10
    band_h = f_h / 5.0
    max_w  = 1.20

    fail_gray = RGBColor(0xE6, 0xE6, 0xE6)

    def draw_funnel(x_left, label, counts, fail_n, success_pct, success_color):
        for i, c in enumerate(counts):
            w = max_w * (c / 1000.0)
            cx = x_left + (max_w - w) / 2.0
            y_ = f_top + i * band_h
            fill = success_color if i == 3 else INK
            rect(slide=s, x=cx, y=y_, w=w, h=band_h - 0.04, fill=fill)
            textbox(s, x_left, y_, max_w, band_h - 0.04,
                    [(f"{c}", 10, True, WHITE)],
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        fail_w = max_w * (fail_n / 1000.0)
        fcx = x_left + (max_w - fail_w) / 2.0
        fy = f_top + 4 * band_h + 0.04
        rect(s, fcx, fy, fail_w, band_h - 0.04, fill=fail_gray)
        textbox(s, x_left - 0.20, fy + band_h + 0.02, max_w + 0.40, 0.24,
                [(f"{fail_n} failed", 10, True, MUTED, True)],
                align=PP_ALIGN.CENTER)
        textbox(s, x_left - 0.10, fy + band_h + 0.34, max_w + 0.20, 0.24,
                [(label, 12, True, success_color)], align=PP_ALIGN.CENTER)
        textbox(s, x_left - 0.20, fy + band_h + 0.58, max_w + 0.40, 0.22,
                [("success ", 9, False, MUTED, True),
                 (success_pct, 11, True, success_color)],
                align=PP_ALIGN.CENTER)

    # stage labels in middle column
    stage_labels = ["requested", "assigned", "picked up", "delivered", "failed"]
    label_x = lx + lw/2 - 0.45
    for i, lbl in enumerate(stage_labels):
        y_ = (f_top + i * band_h) if i < 4 else (f_top + 4 * band_h + 0.04)
        textbox(s, label_x, y_, 1.00, band_h - 0.04,
                [(lbl, 10, True, MUTED, True)],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # OLD funnel (left of middle)
    draw_funnel(lx + 0.55, "Old · 84% success", [1000, 920, 870, 840],
                160, "84%", GOOD)
    # NEW funnel (right of middle)
    draw_funnel(lx + lw - 0.55 - max_w, "New · 57% success", [1000, 620, 590, 570],
                430, "57%", ACCENT)

    # RIGHT — key finding
    rx = lx + lw + 0.40
    rw = SW - 0.55 - rx
    card(s, rx, ly, rw, lh, fill=WHITE)
    textbox(s, rx + 0.30, ly + 0.20, rw - 0.60, 0.30,
            [("AFTER RECONCILE", 11, True, MUTED)])
    textbox(s, rx + 0.30, ly + 0.60, rw - 0.60, 0.95,
            [[("Both stories hold on", 15, True, INK)],
             [("different denominators", 15, True, ACCENT),
              (".", 15, True, INK)]])

    chip_fill = RGBColor(0xF7, 0xF7, 0xF7)
    rounded(s, rx + 0.30, ly + 1.80, rw - 0.60, 0.70, fill=chip_fill)
    textbox(s, rx + 0.30, ly + 1.80, rw - 0.60, 0.70,
            [("84%  →  57%", 22, True, ACCENT, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, rx + 0.30, ly + 2.65, rw - 0.60, 0.65,
            [("Delivered orders really are faster. They are also a different population from the orders that were requested.",
              11, False, MUTED, True)])

    suspect_board(s, 6.40,
        [("h₁", "", "rising"),
         ("h₂", "", "confirmed"),
         ("h₃", "", "confirmed"),
         ("h₄", "", "rising")])
    return s


# ===========================================================================
# SLIDE 22 — B4 · DEBUNK  + final verdict
# ===========================================================================
def slide_b4_debunk():
    s = blank()
    beat_header(s, [("Debunk — does ", INK),
                    ('"18 min"', ACCENT),
                    (" survive a ", INK),
                    ("fair yardstick", ACCENT), ("?", INK)])
    beat_question(s,
        "Widen the window to click-to-door and include every requested order.")

    # LEFT — two grouped panels: headline vs honest yardstick
    lx, ly, lw, lh = 0.55, 2.15, (SW - 1.10) * 0.58, 3.10
    card(s, lx, ly, lw, lh)
    textbox(s, lx + 0.30, ly + 0.20, lw - 0.60, 0.28,
            [("HEADLINE  VS  HONEST YARDSTICK",
              11, True, MUTED)])

    # Two panels side by side
    p_top = ly + 0.65
    p_h   = lh - 0.95
    p_w   = (lw - 0.90) / 2
    p1_x  = lx + 0.30
    p2_x  = p1_x + p_w + 0.30

    bar_gray = RGBColor(0x9B, 0x9B, 0x9B)

    # Panel 1 — pickup → drop
    rect(s, p1_x, p_top, p_w, p_h, fill=CODE_BG)
    textbox(s, p1_x + 0.15, p_top + 0.10, p_w - 0.30, 0.26,
            [("HEADLINE · pickup → drop (min)", 10, True, MUTED)])
    bx_old1 = p1_x + 0.55
    bx_new1 = p1_x + p_w - 0.55 - 0.45
    base1 = p_top + p_h - 0.45
    rect(s, bx_old1, base1 - 1.05, 0.45, 1.05, fill=bar_gray)
    textbox(s, bx_old1 - 0.20, base1 - 1.05, 0.85, 0.32,
            [("31", 18, True, MUTED, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    rect(s, bx_new1, base1 - 0.62, 0.45, 0.62, fill=GOOD)
    textbox(s, bx_new1 - 0.20, base1 - 0.62, 0.85, 0.32,
            [("18", 18, True, GOOD, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    textbox(s, bx_old1 - 0.20, base1 + 0.06, 0.85, 0.22,
            [("old", 10, False, MUTED)], align=PP_ALIGN.CENTER)
    textbox(s, bx_new1 - 0.20, base1 + 0.06, 0.85, 0.22,
            [("new", 10, False, MUTED)], align=PP_ALIGN.CENTER)
    textbox(s, p1_x + 0.15, p_top + p_h - 0.30, p_w - 0.30, 0.25,
            [("−42% (looks good)", 11, True, GOOD)],
            align=PP_ALIGN.CENTER)

    # Panel 2 — click → door on-time
    rect(s, p2_x, p_top, p_w, p_h, fill=CODE_BG)
    textbox(s, p2_x + 0.15, p_top + 0.10, p_w - 0.30, 0.26,
            [("HONEST · click → door on-time (%)", 10, True, MUTED)])
    bx_old2 = p2_x + 0.55
    bx_new2 = p2_x + p_w - 0.55 - 0.45
    base2 = p_top + p_h - 0.45
    rect(s, bx_old2, base2 - 1.15, 0.45, 1.15, fill=GOOD)
    textbox(s, bx_old2 - 0.20, base2 - 1.15, 0.85, 0.32,
            [("73%", 16, True, GOOD, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    rect(s, bx_new2, base2 - 0.78, 0.45, 0.78, fill=ACCENT)
    textbox(s, bx_new2 - 0.20, base2 - 0.78, 0.85, 0.32,
            [("49%", 16, True, ACCENT, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
    textbox(s, bx_old2 - 0.20, base2 + 0.06, 0.85, 0.22,
            [("old", 10, False, MUTED)], align=PP_ALIGN.CENTER)
    textbox(s, bx_new2 - 0.20, base2 + 0.06, 0.85, 0.22,
            [("new", 10, False, MUTED)], align=PP_ALIGN.CENTER)
    textbox(s, p2_x + 0.15, p_top + p_h - 0.30, p_w - 0.30, 0.25,
            [("−24 pt (gets worse)", 11, True, ACCENT)],
            align=PP_ALIGN.CENTER)

    # RIGHT — key finding
    rx = lx + lw + 0.40
    rw = SW - 0.55 - rx
    card(s, rx, ly, rw, lh, fill=WHITE)
    textbox(s, rx + 0.30, ly + 0.20, rw - 0.60, 0.30,
            [("AFTER DEBUNK", 11, True, MUTED)])
    textbox(s, rx + 0.30, ly + 0.60, rw - 0.60, 0.95,
            [[("On the fair yardstick,", 15, True, INK)],
             [("the headline ", 15, True, INK),
              ("reverses sign", 15, True, ACCENT),
              (".", 15, True, INK)]])
    chip_fill = RGBColor(0xF7, 0xF7, 0xF7)
    rounded(s, rx + 0.30, ly + 1.80, rw - 0.60, 0.70, fill=chip_fill)
    textbox(s, rx + 0.30, ly + 1.80, rw - 0.60, 0.70,
            [("73%  →  49%", 22, True, ACCENT, False, MONO)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Plain result strip
    vx, vy, vw, vh = 0.55, 5.45, SW - 1.10, 0.65
    card(s, vx, vy, vw, vh)
    textbox(s, vx + 0.30, vy, vw - 0.60, vh,
            [("Result. ", 15, True, INK),
             ("31 → 18", 15, True, INK, False, MONO),
             (" decomposes into ", 15, True, INK),
             ("zone selection + denominator change + metric boundary",
              15, True, ACCENT),
             (".", 15, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    suspect_board(s, 6.50,
        [("h₁", "", "rising"),
         ("h₂", "", "confirmed"),
         ("h₃", "", "confirmed"),
         ("h₄", "", "confirmed")])
    return s


# ===========================================================================
# SLIDE 21 — EXPERIMENTS
# ===========================================================================
def slide_experiments():
    s = blank()
    title_centered(s, [("Three experiments separate ", INK),
                       ("action", ACCENT), (" from perception.", INK)],
                   y=0.85, size=28)
    subtitle_centered(s, "Each isolates one axis of the protocol.", y=1.55, size=15)

    cy = 2.30
    ch = 4.00
    cw = (SW - 1.10 - 0.50) / 3
    gap = 0.25
    studies = [
        ("Exp. A · action necessity",
         "Does the action axis matter more than model scale?",
         "Cross model axis with protocol axis (passive, random, planning).",
         "Action axis explains more variance than model scale."),
        ("Exp. B · evidence pareto",
         "How does accuracy scale with view budget?",
         "Sweep Bᵥ ∈ {2, 4, 8, 16, ∞} on Recovery and Resolution splits.",
         "Frontier VLM at Bᵥ=16 stays below Oracle at Bᵥ=4."),
        ("Exp. C · channel ablation",
         "Does the agent need pixels or just SQL?",
         "request_view returns PNG only, CSV only, or both.",
         "Pixel-only and CSV-only collapse to different failure modes."),
    ]
    for i, (tag, head, body, punch) in enumerate(studies):
        x0 = 0.55 + i * (cw + gap)
        card(s, x0, cy, cw, ch)
        contrib_tag(s, x0 + 0.30, cy + 0.30, cw - 0.60, 0.30, tag)
        textbox(s, x0 + 0.30, cy + 0.85, cw - 0.60, 0.95,
                [(head, 16, True, INK)])
        textbox(s, x0 + 0.30, cy + 1.95, cw - 0.60, 0.90,
                [(body, 12, False, MUTED, True)])
        # Expected card
        rounded(s, x0 + 0.30, cy + ch - 1.30, cw - 0.60, 1.10, fill=GOOD_SOFT)
        textbox(s, x0 + 0.45, cy + ch - 1.20, cw - 0.90, 0.30,
                [("EXPECTED", 11, True, GOOD)])
        textbox(s, x0 + 0.45, cy + ch - 0.90, cw - 0.90, 0.80,
                [(punch, 12, True, INK)])

    # Bottom plain card
    bx, by, bw, bh = 1.60, 6.55, SW - 3.20, 0.50
    card(s, bx, by, bw, bh)
    textbox(s, bx, by, bw, bh,
            [("The hypothesis: the bottleneck is ", 13, True, INK),
             ("exploration strategy", 13, True, ACCENT),
             (", not perception.", 13, True, INK)],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


# ===========================================================================
# SLIDE 24 — CONCLUSION
# ===========================================================================
def slide_conclusion():
    s = blank()
    title_centered(s, [("Summary.", INK)], y=0.85, size=44)
    subtitle_centered(s,
        "From single-shot chart reading to active investigation of a hidden table.",
        y=1.85, size=15)

    bullets = [
        ("C1", "Atomic-grain Code-as-DGP",
         "An LLM writes Python over a typed SDK. One Master Table emits 10–30+ chart QA tasks through deterministic SQL projection, with cross-chart arithmetic consistent by construction."),
        ("C2", "Active Chart Reasoning protocol",
         "Five actions, two with budget cost. Bbox grounding on every answer. Four named moves: Read, Reveal, Reconcile, Debunk."),
        ("C1 + C2", "LDW-Gym",
         "One pipeline emits data and protocol together. Private test sets regenerate on demand, structurally immune to contamination."),
    ]
    cy = 2.85
    ch = 1.30
    cw = SW - 1.10
    for i, (tag, head, body) in enumerate(bullets):
        yy = cy + i * (ch + 0.25)
        card(s, 0.55, yy, cw, ch)
        tag_w = 1.30
        contrib_tag(s, 0.95, yy + 0.20, tag_w, 0.30, tag)
        textbox(s, 0.95 + tag_w + 0.20, yy + 0.18, cw - tag_w - 0.60, 0.40,
                [(head, 18, True, INK)])
        textbox(s, 0.95 + tag_w + 0.20, yy + 0.62, cw - tag_w - 0.60, 0.55,
                [(body, 12.5, False, MUTED, True)])
    return s


# ===========================================================================
# SLIDE 25 — CLOSING
# ===========================================================================
def slide_closing():
    s = blank()
    textbox(s, 0, 2.85, SW, 1.30,
            [[("Charts are projections of a", 44, True, INK)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 0, 3.85, SW, 1.30,
            [[("latent data world", 44, True, ACCENT),
              (".", 44, True, INK)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 0, 5.30, SW, 0.55,
            [("Thank you.", 19, False, MUTED, True)],
            align=PP_ALIGN.CENTER)
    return s


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
def main():
    slide_title()           # 01
    slide_puzzle()          # 02
    slide_suspects()        # 03  h₁–h₄ hook (NEW)
    slide_trap()            # 04
    slide_benchmark_gap()   # 05
    slide_contributions()   # 06
    slide_overview()        # 07
    slide_section_c1()      # 08
    slide_phase0()          # 09
    slide_phase1()          # 10
    slide_phase2_intro()    # 11
    slide_phase2_swift()    # 12
    slide_self_correct()    # 13
    slide_master_table()    # 14
    slide_amortize()        # 15
    slide_operator()        # 16
    slide_section_c2()      # 17
    slide_four_moves()      # 18
    slide_actions()         # 19
    slide_b1_read()         # 20  B1 · READ
    slide_b2_reveal()       # 21  B2 · REVEAL
    slide_b3_reconcile()    # 22  B3 · RECONCILE
    slide_b4_debunk()       # 23  B4 · DEBUNK + verdict
    slide_experiments()     # 24
    slide_conclusion()      # 25
    slide_closing()         # 26

    out = Path(__file__).resolve().parent / "chartagent_slides.pptx"
    prs.save(out)
    print(f"saved: {out}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
