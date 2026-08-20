"""The output contract: what the analyses return, and how three models are compared.

One file, because a contract split across four is a contract nobody re-reads. The
prose version, with the reasoning behind each field, is
`parsebench/review/06_output_contract.md`; the two say the same thing and the
field names are the join. The one thing not here is the component vocabulary --
65 keys with a criterion and an `affects` each, in `vocabulary.py`, which is a
data table rather than a contract.

Fixed before any model runs. A field only becomes comparable across models once
its domain is closed: a free-text component name cannot be summed, and two models
naming the same construction differently would read as a disagreement about the
page.

Five parts:

    1  domains     the closed vocabularies every schema field draws on
    2  page        what one page analysis returns
    3  failure     what one failure attribution returns
    4  report      which sections a report has, and who computed each number
    5  compare     how three models' answers are put side by side

Two rules from `parsebench/TODO.md` §T0 are built into the fields rather than
left to a renderer. Every observation a model proposes carries `affects` -- which
of the four judgement steps it can change, empty meaning the metric never looks
at it. Every suggestion answers two questions that are not on one scale, in two
fields: what it does to the ParseBench score, and what capability it adds to the
generation pipeline. Nothing downstream can sort them into one column.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vocabulary import KEYS

# --------------------------------------------------------------------------- #
# 1 · Domains                                                                   #
# --------------------------------------------------------------------------- #

#: What the four-step judgement of ParseBench's `ChartDataPointRule` can fail on.
#: `review/02_chart_metric.md` walks one rule through them.
STEPS = {
    1: "there is no table at all",
    2: "the value cannot be read to the tolerance",
    3: "the labels cannot be associated with the cell",
    4: "the context outside the table is not bold or a heading",
}

#: Chart types worth telling apart when counting what the benchmark contains.
#: `other` is the residue and carries `type_other`: an unnamed `other` is a hole
#: in the type mix that the family weight vector would be read off.
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

#: The seven pipeline changes a suggestion can be filed under, kept in sync with
#: `parsebench/review/04_pipeline_gap.md`. `new` is for what none of them covers;
#: it is the field that keeps the review list open rather than closed.
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


# --------------------------------------------------------------------------- #
# 2 · One page analysis                                                         #
# --------------------------------------------------------------------------- #
#
# Two fields carry most of the weight. `components[].evidence` makes every count
# checkable -- a key without the words that show it is a claim, and a frequency
# table built out of claims cannot be read. `figures[].heading` splits the caption
# into number, title, subtitle, unit and placement, because those five are
# separate generation problems and a single caption string hides all of them.

#: Which of the four steps an observation can change. Empty means the metric never
#: looks at it, which makes the observation a question about how honest the
#: generated data is rather than about the score.
_AFFECTS = {
    "type": "array",
    "items": {"type": "integer", "enum": [1, 2, 3, 4]},
    "description": "which of the four judgement steps this can change: 1 there is a "
                   "table, 2 the value is within tolerance, 3 the labels associate "
                   "with the cell, 4 the context outside the table. Empty array when "
                   "the metric never looks at it -- that is a normal answer, not a "
                   "missing one",
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

#: One vocabulary key, with the thing on the page that shows it. No `affects`
#: here: the vocabulary already fixes it for these 65 keys, before any page is seen.
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

PAGE_SCHEMA = {
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
            "description": "constructions the vocabulary has no key for. A name repeated "
                           "across enough pages earns a key of its own in the next round",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "figure_id", "evidence", "affects", "why_it_matters"],
                "properties": {
                    "name": {"type": "string",
                             "description": "a lower_snake_case key you propose, English"},
                    "figure_id": {"type": "string", "description": "the figure, or `page`"},
                    "evidence": {"type": "string",
                                 "description": "English, at most 20 words: what on the page "
                                                "shows it"},
                    "affects": _AFFECTS,
                    "why_it_matters": {"type": "string",
                                       "description": "Chinese, at most 30 words: what it "
                                                      "changes for reading a value out of "
                                                      "this page"},
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
        "hardest_step": {"type": "integer", "enum": [1, 2, 3, 4],
                         "description": "the step of the four this page blocks on"},
        "difficulty_notes": {"type": "string",
                             "description": "Chinese, at most 60 words: why that step is the "
                                            "one that blocks. Argue from this page's numbers "
                                            "-- tick spacing against the tolerance, how many "
                                            "keys a value needs -- not in general terms"},
        "unreadable": {
            "type": "array",
            "description": "entries that are not figures at all, or figures nothing can be "
                           "read off",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["figure_id", "reason"],
                "properties": {
                    "figure_id": {"type": "string"},
                    "reason": {"type": "string", "description": "Chinese, at most 20 words"},
                },
            },
        },
        "suggestions": {
            "type": "array",
            "description": "what this page says the generation pipeline should be able to "
                           "do. Two effects, never one: the score and the capability",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["what_to_add", "where_to_change", "affects", "score_effect",
                             "capability_effect", "new_ablation_row", "generality", "maps_to"],
                "properties": {
                    "what_to_add": {"type": "string",
                                    "description": "Chinese: which vocabulary key or new component"},
                    "where_to_change": {"type": "string",
                                        "description": "Chinese: which condition row, style field "
                                                       "or record field"},
                    "affects": _AFFECTS,
                    "score_effect": {"type": "string",
                                     "description": "Chinese, at most 30 words: what it does to "
                                                    "the ParseBench score, argued through the "
                                                    "step named in `affects`. Write `度量看不见它` "
                                                    "when `affects` is empty -- that is an answer, "
                                                    "not a gap"},
                    "capability_effect": {"type": "string",
                                          "description": "Chinese, at most 30 words: what the "
                                                         "generation pipeline can do afterwards "
                                                         "that it cannot do now. A change that "
                                                         "only removes an existing ability does "
                                                         "not belong here -- rewrite it as a "
                                                         "configurable dimension with the "
                                                         "current behaviour as its default"},
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


# --------------------------------------------------------------------------- #
# 3 · One failure attribution                                                   #
# --------------------------------------------------------------------------- #
#
# The division of labour is fixed and does not move: the program says *what*
# happened, the model says *why*. Whether a spot check passed comes from the run's
# own `_evaluation_report.json` and is never re-judged; which form the failure
# took is computed from the parser's output tables; the model is handed both and
# asked only for the mechanism. Mechanisms are a closed list for the same reason
# component keys are, and each names the step of the four it belongs to, so an
# attribution that cannot be mapped back onto the metric cannot be written down.

#: The forms the program computes, from the run output. Given to the model as
#: input, never asked of it. `series_swap` and `stack_confusion` were candidate
#: forms that the last round could not separate from an ordinary misread; they
#: stay out of the form list and come back as mechanisms, where they are a claim
#: about the drawing rather than a count.
FORMS = {
    "no_table": "the page produced no table at all",
    "label_unlinked": "the value is in a table, but a label will not associate with its cell",
    "row_missing": "one of the addressing labels is nowhere in the output",
    "value_off": "the addressed cell holds a different number",
    "unit_mismatch": "the addressed cell holds the same number at another scale",
    "value_absent": "the labels are all there, but that value was never written",
}

#: Where a label the metric could not associate turned out to live. Also computed
#: by the program.
LABEL_HOMES = (
    "in_a_table_but_not_addressing",
    "in_another_table_only",
    "emphasised_before_a_table",
    "emphasised_after_the_table",
    "plain_text_only",
    "absent_from_the_output",
)

#: What about the drawing produced that form, and which step of the judgement it
#: belongs to. This is the one field the model decides.
MECHANISMS = {
    "key_off_the_value_row": (3, "the key is in the table but on another row, column or header"),
    "key_only_in_another_table": (3, "the figure was split into several tables and the key stayed in one of the others"),
    "key_only_in_prose": (3, "the key was written as running text, not into any table"),
    "series_identified_by_colour": (3, "the series name is only in the legend, and the column was named after its colour"),
    "panel_name_dropped": (3, "a multi-panel figure lost the panel name, so the remaining keys address several cells"),
    "value_read_off_wrong_mark": (2, "the number belongs to a neighbouring mark or series"),
    "value_interpolated_off_axis": (2, "no number is printed and the tick spacing leaves the reading short of the tolerance"),
    "stacked_total_vs_segment": (2, "a segment was read as the cumulative total, or the total as a segment"),
    "scale_word_ignored": (2, "the scale stated in the title, axis or label was not applied"),
    "value_domain_ignored": (2, "the quantity can only take certain values (a count, a rank) and the reading is between them"),
    "non_data_mark_read_as_data": (2, "a reference line, callout or shaded band was transcribed as a series"),
    "figure_not_transcribed": (1, "the figure produced no table, only surrounding text"),
    "other": (0, "none of the above; say what it was in `mechanism_note`"),
}

FAILURE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["case_id", "mechanism", "mechanism_note", "evidence", "affects",
                 "drawn_differently", "maps_to", "confidence"],
    "properties": {
        "case_id": {"type": "string", "description": "the identifier given in the prompt"},
        "mechanism": {"type": "string", "enum": list(MECHANISMS),
                      "description": "what about the way the figure was drawn produced "
                                     "the form the program computed"},
        "mechanism_note": {"type": "string",
                           "description": "Chinese, at most 30 words. Required when the "
                                          "mechanism is `other`; empty otherwise"},
        "evidence": {"type": "string",
                     "description": "English, at most 25 words: quoted from the parser's "
                                    "output or named on the page -- the cell, the column "
                                    "header, the legend entry. Not a restatement of the "
                                    "mechanism"},
        "affects": {"type": "array", "items": {"type": "integer", "enum": [1, 2, 3, 4]},
                    "description": "the judgement step this failure belongs to, normally "
                                   "the one the mechanism names"},
        "drawn_differently": {"type": "string",
                              "description": "Chinese, at most 30 words: what a generator "
                                             "would have to record or draw for this failure "
                                             "not to be possible. A capability, not a fix "
                                             "to this one page"},
        "maps_to": {"type": "string", "enum": list(GAP_ITEMS)},
        "confidence": {"type": "string", "enum": ["certain", "likely", "guess"],
                       "description": "`certain` only when the evidence shows the mechanism "
                                      "rather than being consistent with it"},
    },
}

#: The step each mechanism belongs to, for the check that an attribution maps back
#: onto the metric. `other` maps to no step and must carry a note.
MECHANISM_STEP = {key: step for key, (step, _) in MECHANISMS.items()}

assert set(MECHANISM_STEP.values()) <= set(STEPS) | {0}


# --------------------------------------------------------------------------- #
# 4 · What a report contains, and who computed each number                      #
# --------------------------------------------------------------------------- #

PROVENANCE = ("rule_checkable", "program_measured", "model_claim")


@dataclass(frozen=True)
class Section:
    """One section of a report: the question it answers and the rows it prints."""

    id: str
    title: str
    question: str
    rows: str
    provenance: tuple[str, ...]


#: The page analysis. Three sections, each answering one question, no overlap.
#: `view.html` renders the same three, one panel each, every row carrying the page
#: it came from and the model's own evidence line.
PAGE_REPORT = (
    Section("1", "要改什么",
            "基准里出现、而 storyline 没有定义的东西，哪些保留、哪些舍弃",
            "一项一行：组件 key 或图表类型 · 三家各自的页数 · 一致性（三家 / 两家 / 一家）· "
            "affects · 文档分布 · 归入哪条 P · 双栏结论（对分数 / 对能力）",
            ("model_claim", "program_measured")),
    Section("2", "基准长什么样",
            "这批页面实际是什么样，包括我们已经画得出来的部分",
            "类型配比、标题五字段、数值印不印、难点分布、词表全表；每一格三家并列，"
            "并列不合并",
            ("model_claim", "program_measured")),
    Section("3", "能不能信",
            "这些数字是怎么来的",
            "调用口径（模型、effort、图像分辨率、一次调用）· 三家的判分（定位键预测 vs "
            "规则标签）· 交叉核对的矛盾计数 · 三家差异表",
            ("rule_checkable", "program_measured")),
)

#: The failure analysis. `passed` is never recomputed, so section 1 is entirely
#: program-measured and section 2 entirely rule-checkable.
FAILURE_REPORT = (
    Section("1", "失败长什么样",
            "896 个失败各是什么形态，失联的键在哪",
            "形态 × 个数 × 占比；失联键的去向分布；三家的归因一致率",
            ("program_measured", "model_claim")),
    Section("2", "什么样的图更容易失败",
            "哪些自变量与通过率单调相关",
            "自变量 × 分档 × 通过率 × n × 95% 区间；控制组内的组件差值",
            ("rule_checkable", "program_measured")),
    Section("3", "翻成流水线改动",
            "每条改动加了什么能力，证据是哪一行",
            "改动一行：机制 · 三家一致性 · 双栏结论（对分数 / 对能力）· 新增的消融行 · "
            "归入哪条 P",
            ("model_claim", "program_measured")),
    Section("4", "能不能信",
            "口径与没有测到的东西",
            "passed 的来源 · 分母（哪些统计只覆盖有图表描述的页）· 相关而非因果的声明 · "
            "没能分开的形态",
            ("program_measured",)),
)

#: Numbers a model must never be the source of. Each is computable without a model,
#: and each was a place the last round could have drifted had it not been.
PROGRAM_ONLY = {
    "每个组件出现在几页、几份文档": "对模型回答里的 key 计数，不问模型频次",
    "通过率与 95% 区间": "取自官方 _evaluation_report.json，不重判分",
    "失败形态的计数": "由解析器输出的表算出，模型只归因不计数",
    "规则实际用了几个标签": "chart.jsonl 的 labels 长度",
    "定位键预测的对错": "规则标签与模型预测的双向子串匹配，与基准自己的匹配方式一致",
    "页面文字量": "PDF 文字层实测",
    "三家的一致性": "对齐后按 compare.py 的判据算，不问模型",
}


# --------------------------------------------------------------------------- #
# 5 · How three models' answers are compared                                    #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Quantity:
    """One thing three answers are aligned on."""

    name: str
    unit: str            # what one comparable item is
    equal_when: str      # when two models are counted as saying the same thing
    provenance: str      # `report.PROVENANCE`; `rule_checkable` ones are also graded


QUANTITIES = (
    Quantity("图表类型判定", "(页, 图序号)",
             "两家给出同一个 type；`other` 还要求 type_other 归一化后相同",
             "model_claim"),
    Quantity("图的个数与图元数", "(页, 图序号)",
             "图数完全相同；图元数落在同一个稠密度档（≤20 / 21–60 / 61–150 / 151–400 / >400）",
             "model_claim"),
    Quantity("组件命中集合", "(页, key)",
             "同一页同一个 key 都被报出；差异表按 key 记三家 / 两家 / 一家",
             "model_claim"),
    Quantity("标题五字段", "(页, 图序号, 字段)",
             "figure_number 与 placement 完全相同；title / subtitle / unit_text 去空白与"
             "大小写后相同",
             "model_claim"),
    Quantity("数值印不印", "(页, 图序号)", "values_printed 三值相同", "model_claim"),
    Quantity("卡在哪一步", "页", "hardest_step 相同", "model_claim"),
    Quantity("抽查点落到哪张图", "(页, 抽查点序号)",
             "figure_id 相同；`not_found` 也算一个取值",
             "model_claim"),
    Quantity("定位键预测", "(页, 抽查点序号)",
             "与规则的真实标签逐条判对错，三家各自得一个分；这一项不是「谁和谁一致」，"
             "而是「谁对」",
             "rule_checkable"),
    Quantity("改进意见", "(maps_to, what_to_add 归一化后)",
             "落在同一条 P 且指向同一个组件 key；affects 不同则记为冲突",
             "model_claim"),
    Quantity("失败归因", "(case_id)",
             "mechanism 相同；affects 不同则记为冲突",
             "model_claim"),
)

#: 三家一致 / 两家 / 一家，以及冲突的定义。差异表按这四类分栏。
AGREEMENT = {
    "unanimous": "三家都报了这一项，且按 `equal_when` 相等",
    "majority": "两家相同，第三家沉默（没报，不是报了别的）",
    "single": "只有一家报了这一项",
    "conflict": "两家以上报了，但取值不同——包括 affects 不同、类型不同、步骤不同",
}

#: 结论怎么用这四类。这条规则先于任何数字。
DECISION = {
    "unanimous": "直接进改造清单",
    "majority": "进清单，标注为两家",
    "single": "单列，不进清单",
    "conflict": "单列，需要人工看页面裁决；裁决结果写进报告，不改模型的原答案",
}

#: 一致率怎么算：分母是至少一家报过的项，分子是 unanimous 的项。按页算再平均，
#: 与基准自己的按页平均口径一致。
AGREEMENT_RATE = "unanimous / (unanimous + majority + single + conflict)，按页平均"
