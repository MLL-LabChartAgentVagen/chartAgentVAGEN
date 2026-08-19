"""The contract of the one call: what the model must return, in what shape.

Three vocabularies live here because they are all part of that contract -- the
chart types worth telling apart, the four ways a page can fail to score, and the
seven pipeline changes a suggestion is filed under.

Two fields carry most of the weight. `components[].evidence` makes every count
checkable: a key without the words that show it is a claim, and a frequency table
built out of claims cannot be read. `figures[].heading` splits the caption into
number, title, subtitle, unit and placement, because those five are separate
generation problems and a single caption string hides all of them.
"""

from __future__ import annotations

from vocabulary import KEYS

#: What the four-step judgement of ParseBench's ChartDataPointRule can fail on.
STEPS = {
    1: "there is no table at all",
    2: "the value cannot be read to the tolerance",
    3: "the labels cannot be associated with the cell",
    4: "the context outside the table is not bold or a heading",
}

#: Chart types worth telling apart when counting what the benchmark contains.
#: `other` is the residue and carries `type_other`: an unnamed 8% of the figures
#: is a hole in the type mix that P4's weight vector is read off.
CHART_TYPES = (
    "bar", "grouped_bar", "stacked_bar", "line", "area", "pie", "donut", "scatter",
    "heatmap", "box", "histogram", "waterfall", "funnel", "compound", "map",
    "radar", "treemap", "gauge", "other",
)

#: How widely a construction is used, as the model reads it off this one page.
#: The program computes the same thing independently, from how many distinct
#: documents a component appears in, so the two can be compared.
GENERALITY = {
    "general": "most published charts of this kind do it, whoever drew them",
    "common": "a whole class of publisher does it, not all of them",
    "house_style": "this document's own convention",
}

#: The seven pipeline changes a suggestion can be filed under. Kept in sync with
#: `parsebench/review/04_pipeline_gap.md`.
GAP_ITEMS = {
    "P1": "readable becomes a per-mark attainable precision instead of a boolean gate",
    "P2": "the panel dimension enters the key (panel_key)",
    "P3": "a whole-page markdown export, and where a title or panel name sits "
          "relative to the table",
    "P4": "how often each chart family is generated, a weight vector -- not what a family looks like",
    "P5": "raise the density cap, making density a controlled variable",
    "P6": "three more style dimensions: value-label placement, tick format and unit "
          "position, negative values and the zero line",
    "P7": "the figure title becomes a field of its own: number, title, subtitle, unit, "
          "and where the heading block sits",
    "new": "none of the seven covers it",
}

#: The caption, split into the five things a generator would have to produce.
_HEADING = {
    "type": "object",
    "additionalProperties": False,
    "required": ["figure_number", "title", "subtitle", "unit_text", "placement"],
    "properties": {
        "figure_number": {"type": "string",
                          "description": "`Figure 15`, `Exhibit 3`, `Chart 2.1` as printed; "
                                         "empty string when the figure is unnumbered"},
        "title": {"type": "string",
                  "description": "the main title line, verbatim, without the number"},
        "subtitle": {"type": "string",
                     "description": "further heading lines under the title, verbatim; "
                                    "empty when the heading is one line"},
        "unit_text": {"type": "string",
                      "description": "the phrase that fixes the scale of the numbers, "
                                     "wherever it sits -- `USD billion (2022 prices)`, "
                                     "`% of GDP`, `2011 = 100`; empty when there is none"},
        "placement": {"type": "string",
                      "enum": ["above", "beside", "below", "inside", "none"],
                      "description": "where the heading block sits relative to the plot "
                                     "area. `beside` means a side column level with the "
                                     "plot, not stacked over it"},
    },
}

_FIGURE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "heading", "type", "type_other", "orientation", "panels",
                 "panel_names", "series", "series_names", "categories", "category_names",
                 "marks", "values_printed", "value_axis_ticks", "source_line"],
    "properties": {
        "id": {"type": "string", "description": "f1, f2, ... in reading order"},
        "heading": _HEADING,
        "type": {"type": "string", "enum": list(CHART_TYPES)},
        "type_other": {"type": "string",
                       "description": "when type is `other`, name the form in two or three "
                                      "English words (`dumbbell`, `bullet chart`, "
                                      "`population pyramid`); empty otherwise"},
        "orientation": {"type": "string", "enum": ["vertical", "horizontal", "na"]},
        "panels": {"type": "integer", "description": "1 for a single-panel figure"},
        "panel_names": {"type": "array", "items": {"type": "string"},
                        "description": "one per panel, verbatim; empty when panels is 1"},
        "series": {"type": "integer",
                   "description": "distinct legend entries, 1 when there is no legend"},
        "series_names": {"type": "array", "items": {"type": "string"}},
        "categories": {"type": "integer",
                       "description": "distinct slots on the category or time axis, per panel"},
        "category_names": {"type": "array", "items": {"type": "string"},
                           "description": "up to 12 of them, verbatim, in axis order"},
        "marks": {"type": "integer",
                  "description": "individually drawn marks in the whole figure across all "
                                 "panels: bars, stacked segments, points, slices, cells"},
        "values_printed": {"type": "string", "enum": ["all", "some", "none"],
                           "description": "whether the numbers are written on the figure"},
        "value_axis_ticks": {"type": "string",
                             "description": "the value-axis tick labels as printed, comma "
                                            "separated (`0, 25, 50, 75, 100`); empty string "
                                            "when the figure draws no value axis"},
        "source_line": {"type": "string",
                        "description": "the `Source:` line under the figure, verbatim; "
                                       "empty when there is none"},
    },
}

#: One vocabulary key, with the thing on the page that shows it.
_COMPONENT = {
    "type": "object",
    "additionalProperties": False,
    "required": ["key", "figure_id", "evidence"],
    "properties": {
        "key": {"type": "string", "enum": list(KEYS)},
        "figure_id": {"type": "string",
                      "description": "the figure it appears on, or `page` when it is a "
                                     "property of the page rather than of one figure"},
        "evidence": {"type": "string",
                     "description": "English, at most 20 words: the words on the page that "
                                    "show it, quoted, or what is drawn and where. `the "
                                    "y axis reads 0, 25, ... 200 with no unit` is evidence; "
                                    "`the unit is in the title` is a restatement of the key"},
    },
}

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["page_note", "figures", "components", "new_components", "spot_checks",
                 "hardest_step", "difficulty_notes", "unreadable", "suggestions"],
    "properties": {
        "page_note": {"type": "string",
                      "description": "one sentence in Chinese: what is on this page"},
        "figures": {"type": "array", "items": _FIGURE},
        "components": {"type": "array", "items": _COMPONENT,
                       "description": "every vocabulary key present anywhere on the page, "
                                      "each with the evidence for it"},
        "new_components": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "figure_id", "evidence", "why_it_matters"],
                "properties": {
                    "name": {"type": "string",
                             "description": "a lower_snake_case key you propose, English"},
                    "figure_id": {"type": "string", "description": "the figure, or `page`"},
                    "evidence": {"type": "string",
                                 "description": "English, at most 20 words: what on the page "
                                                "shows it"},
                    "why_it_matters": {"type": "string",
                                       "description": "Chinese: what it changes for reading "
                                                      "a value out of this page"},
                },
            },
        },
        "spot_checks": {
            "type": "array",
            "description": "one entry per value listed in the prompt, in the order given",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["value", "figure_id", "mark", "printed_on_figure",
                             "addressing_keys"],
                "properties": {
                    "value": {"type": "string", "description": "the value, copied back"},
                    "figure_id": {"type": "string",
                                  "description": "the figure carrying it, or `not_found`"},
                    "mark": {"type": "string",
                             "description": "English: which mark it is, e.g. `the 1992 "
                                            "Weather-related segment`, or why it cannot "
                                            "be placed"},
                    "printed_on_figure": {"type": "boolean",
                                          "description": "whether that number is written on "
                                                         "the figure, rather than read off "
                                                         "the mark against the axis"},
                    "addressing_keys": {
                        "type": "array", "items": {"type": "string"},
                        "description": "the labels a table row would need to address this "
                                       "one value and no other, verbatim from the page"},
                },
            },
        },
        "hardest_step": {"type": "integer", "enum": [1, 2, 3, 4]},
        "difficulty_notes": {"type": "string",
                             "description": "Chinese: why that step is the one that blocks. "
                                            "Argue from this page's numbers -- tick spacing "
                                            "against the tolerance, how many keys a value "
                                            "needs -- not in general terms"},
        "unreadable": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["figure_id", "reason"],
                "properties": {
                    "figure_id": {"type": "string"},
                    "reason": {"type": "string", "description": "Chinese"},
                },
            },
        },
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["what_to_add", "where_to_change", "new_ablation_row",
                             "generality", "maps_to"],
                "properties": {
                    "what_to_add": {"type": "string",
                                    "description": "Chinese: which vocabulary key or new component"},
                    "where_to_change": {"type": "string",
                                        "description": "Chinese: which condition row, style field "
                                                       "or record field"},
                    "new_ablation_row": {"type": "string",
                                         "description": "Chinese: the row this adds to the ablation "
                                                        "table; without one the change only chases "
                                                        "the benchmark"},
                    "generality": {"type": "string", "enum": list(GENERALITY),
                                   "description": "how widely charts outside this document "
                                                  "use the construction"},
                    "maps_to": {"type": "string", "enum": list(GAP_ITEMS)},
                },
            },
        },
    },
}
