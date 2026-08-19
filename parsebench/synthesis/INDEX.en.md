# ParseBench → Generation Pipeline · Merged Conclusions

**A self-contained document.** Everything concluded in [reports/](../reports/INDEX.md) (what the benchmark pages look like) and in [failures/](../failures/ppdoclayoutv3_lean_qwen/INDEX.md) (where one strong parser fails) is restated here; reading this one does not require opening those two. Illustrated version: **[view.en.html](view.en.html)** -- five tabs matching this document, with **each of the 39 component gaps, 10 failure pages and 2 type gaps carrying its own page image and its own raw evidence** (gaps carry the words the model wrote when it counted them; failure pages carry the table the parser actually wrote beside the long table that would have passed). 中文: **[INDEX.md](INDEX.md)** / **[view.html](view.html)**

**Evidence base**: the ParseBench chart split, 568 pages / 99 documents / 4,864 spot-check rules. 192 of those pages additionally carry a per-page chart description (`claude-opus-5`, 265 figures, a 65-item component vocabulary); all 568 pages carry the failure sample of one complete parser run (PP-DocLayoutV3 lean + `Qwen3.8-27B-FP8`, page-average 82.75%, 896 failures).

**What this document answers**: reading "what the benchmark looks like" together with "where a strong system fails", which **capabilities** the generation pipeline should gain — not which **line items**. The original lists held 39 component gaps + 10 failure-derived changes + 7 P-numbered items; the three overlap, sit at different granularities, and cannot be ordered against each other. This document maps them onto **5 capability axes + 1 methodological axis**, each with its evidence strength, cost, expected effect on ParseBench, and **whether it still holds once ParseBench is removed**.

| Section | Question | Form of the conclusion |
|---|---|---|
| [1 Merged evidence](#1-merged-evidence) | What each analysis measured, and what the two add up to | Four crossings, one of which overturns a single-analysis verdict |
| [2 Five capability axes](#2-five-capability-axes) | Which capabilities the pipeline should gain | A1–A5 plus methodological axis M, each with a failure criterion |
| [3 Coverage and verdicts](#3-coverage-and-verdicts) | Where each of the original 56 items went | Full mapping; 4 reclassified, 3 split, 2 dropped |
| [4 Roadmap and acceptance](#4-roadmap-and-acceptance) | What to do first, and what counts as done | Ordering, ablation rows, the upgraded claim |
| [5 Method and limits](#5-method-and-limits) | How the numbers were computed, what was not measured | The correlation / causation boundary is fixed here |

---

## 1 Merged evidence

### 1.1 What each analysis measured

| | Page analysis | Failure analysis |
|---|---|---|
| Object read | The benchmark pages themselves | One parser's output on those pages |
| Denominator | 192 pages · 1,658 spot-check points · 265 figures | 568 pages · 4,864 spot-check points |
| Product | Per-page counts over a 65-item component vocabulary, type mix, the five title fields, 39 items "we cannot draw" | The form distribution of 896 failures, where the unlinked key landed, pass rate against each independent variable |
| How the criteria were fixed | `affects` (which of the four judging steps it can change) and document spread — both columns fixed from the metric definition before any page was read | Every `passed` comes from the official `_evaluation_report.json`; locally only "where in the output do this value and these keys land" is computed |
| What it can say alone | Which constructs real report pages carry, and how general each is | What shape the remaining failures have, and what each shape costs |
| What it cannot say alone | What each item is worth in points | Which constructs appear in the benchmark but never surface in the failures (either the parser was not tripped by them, or they carry no rule) |

**The two denominators are not independent**: the 192 pages are a random subset of the 568. Crossings of the form "component → pass rate" therefore raise hypotheses rather than settle them; see [§5.2](#52-correlation-is-not-causation).

### 1.2 Four crossings

The whole value of merging sits in these four rows — none of them can be written from either analysis alone.

| # | The page analysis says | The failure analysis says | Joint conclusion |
|---|---|---|---|
| 1 | `dense_marks_100plus` appears on 41 / 192 pages and affects step 2, "find the value" | ≤20 marks 85.5% → >400 marks 57.9%, 95% intervals disjoint | Density is one of the hardest continuous independent variables in this data; the current ceilings in `chart_types.md` all land in the ≤60-mark bucket |
| 2 | 79% of the 4,864 rules (3,847) use only two labels and 15% (715) need a third; the 192-page subset gives the same shape, 83% / 12% | 2 keys 83.3% → 3 keys 69.0% → 4 keys 55.9% (all 568 pages, no dependence on chart descriptions) | Key count is the independent variable; panel count is not (1 / 2 / 3+ panels: 82.0% / 80.3% / 79.4%). P2 must be restated from "a multi-panel-specific field" to "global uniqueness of the key" |
| 3 | `reference_line` (43 pages / 22 docs) and `annotation_callout` (33 pages / 23 docs) have an empty `affects` — the metric does not reference them, so both were classified "realism only, the score will not move" | Within the control group, `reference_line` -11.6% (n=297) and `annotation_callout` -11.8% (n=164), 95% intervals disjoint | **Reclassified.** `affects` covers only one kind of visibility; see [§1.3](#13-two-kinds-of-visibility) |
| 4 | The model predicted, per page, which of the four steps that page is hardest at | Actual pass rate grouped by that prediction: step 2 77% (n=1103) · step 3 90% (n=460) · step 4 100% (n=62) | The descriptive layer's difficulty prediction moves with the actual pass rate. The chart descriptions can be used as independent variables in later analyses |

### 1.3 Two kinds of visibility

Row 3 is the one place where merging overturned a single-analysis verdict, so the distinction is worth naming.

| | Definition | How the page analysis judged it | How the failure analysis measures it | Examples |
|---|---|---|---|---|
| **Visible as a target** | The construct itself carries some rule's value or label | `affects` non-empty | Points on its page fail directly | `negative_values` · `dense_marks_100plus` · `nonstandard_time_ticks` |
| **Visible as a distractor** | The construct carries no rule, but changes the shape of the table the parser writes | `affects` empty → filed under "realism only" | Only visible as a pass-rate difference inside the control group | `reference_line` · `annotation_callout` · `shaded_band` |

A reference line is never a spot-check point, so it **cannot** directly change the judging of any rule. But `pwc-semiconductor-and-beyond-2026-full-report_p17` wrote the pale orange connector band between two bars as a third data series — a distractor does not change the rules, it changes how many series the parser's output has and how the header is written, and **other rules on the same page** then fail to address.

**Direct consequence for the pipeline**: non-data ink moves from "realism item" to "score item", and what it needs is not a style switch but a new class of annotation target — see [A4](#a4--non-data-ink-and-absence).

### 1.4 Failure composition and the upper bound

Across all 568 pages and 4,864 spot-check points, 896 do not pass. The official report distinguishes only two kinds (value not found anywhere / value found but the label would not associate); the table below splits those into shapes that map onto pipeline changes.

| Form | Count | Share of failures | Side | Axis |
|---|---:|---:|---|---|
| `label_unlinked` the number is right, but the table cannot say whose number it is | 599 | 66.9% | addressing | A1 |
| `value_off` the number was read wrong | 199 | 22.2% | reading | A2 |
| `row_missing` a key was never written into the table at all | 48 | 5.4% | addressing | A1 · A5 |
| `unit_mismatch` the number was written at the wrong magnitude | 36 | 4.0% | reading | A3 |
| `value_absent` every key is there, this number is not | 14 | 1.6% | reading | A2 |
| `no_table` the page produced no table | 0 | 0.0% | — | — |

**Addressing 72% (647) · reading 28% (249).** None of the 568 pages returned a blank.

For the 599 unlinked points, searching the parser's output again for the key the rule names gives 791 placements:

| Where it is | Count | Share |
|---|---:|---:|
| In the same table, just not on this number's row / column / header | 627 | 79.3% |
| On the page, but only as ordinary body text | 57 | 7.2% |
| Nowhere in the page output | 46 | 5.8% |
| In a different table | 38 | 4.8% |
| Bold or a heading, but positioned after the table | 18 | 2.3% |
| Before the table and bold or a heading | 5 | 0.6% |

**79% of unlinked keys are in the same table.** The parser saw the key and wrote it down; it placed it at another position in a wide table. Fixing all 647 addressing failures takes the page average from **82.75% to 95.41%** — an upper bound rather than a prediction, since it assumes the table changed shape while not one reading changed.

For the 199 misread points the median relative error is 15%: ≤5% covers 13% · ≤10% covers 36% · ≤20% covers 60% · ≤50% covers 82%. **Doubling the tolerance does not recover half of them**; most of this class is not an estimation offset.

### 1.5 One-sentence conclusion

> What remains failing on this benchmark is mostly the inability to say **whose number this is**, not insufficient reading precision. The corresponding generation-side capability is: **every mark carries its complete address key, and every key component can point back to the pixels that spell it out on the page**. That is the full form of the output unit `(key, value, box)` — the pipeline currently produces `value → box` and not `key component → box`.

---

## 2 Five capability axes

All five axes follow one template: which items it absorbs · evidence · what capability to add · **the annotation quantity it newly produces** · whether it holds outside ParseBench · cost · failure criterion.

The "annotation quantity newly produced" column is the test of whether an axis belongs in a paper: an axis that only turns an existing field up or down is engineering; an axis that produces an annotation quantity no existing dataset has is a contribution of the dataset itself.

### A1 · Complete address keys, and grounding each key component

**In one line**: every mark carries a globally unique key tuple, and for each key component the pipeline also records which construct on the page spells it out and in which pixels.

Today `key` is an address **inside** a panel (`("Mercy General",)`), panel identity is an identifier carrying no value, and the correspondence between colour and series name is recorded only for multi-panel figures with a shared legend (`legend[].applies_to_panels`). Neither is enough: the panel name is often itself the third key component, and on real report pages a series name is spelled out in five different ways (legend swatch, inline label at the line end, panel title banner, axis title, unit carried inside the series name) — only the first is recorded.

**Capability to add**

1. Promote `key` to a **figure-global address**: `(figure_id, panel_key, series, category, measure)`, where `panel_key` is the sliced dimension's column name and value rather than an internal index. On multi-figure pages the visible form of `figure_id` (the figure number) enters the key as well.
2. Generalise `legend[]` in the record into **`key_carriers[]`**: one entry per key component recording which pixels on the page spell that component out — legend swatch, tick label, panel title banner, inline end-of-line label, the outer level of a two-level tick, the row a footnote superscript points at.
3. Make the export an identity mapping onto a **long table**: one value per row, with every key component written on that same row.

**Newly produced annotation quantity**: `key component → the region of its literal source`. Existing work grounds structural elements (ChartREG++'s axes / ticks / legends masks) or answers (ChartLens's answer-level attribution); no work treats "point each key component back to its literal source" as a training target. It generalises the single `legend binding` target into a whole class of targets.

| | |
|---|---|
| **Items absorbed** | Failure-derived changes 1 (long-table export) · 2 (panel name into the key) · 3 (colour → series); `P2` `P3`; 9 component gaps: `wrapped_category_labels` `footnote_marker` `color_encodes_extra_attribute` `two_level_x_ticks` `small_multiples_5plus` `inline_series_labels` `icon_category_axis` `total_row_below_axis` `stacked_and_grouped` |
| **Evidence** | 72% of all failures; 79% of unlinked keys sit in the same table; 2 keys 83.3% → 3 keys 69.0% → 4 keys 55.9%; upper bound of fixing it 82.75% → 95.41% |
| **Generality** | General. The output unit is `(key, value, box)`, so the key must be a complete address tuple — independent of any particular metric. ParseBench needing only two keys is not a reason to trim the key to two: after trimming, the mark end of the provenance chain is no longer globally unique |
| **Cost** | Low to medium. `panel_key` is one more field on the FigureSpec in 02; `key_carriers[]` is one more line written while drawing in 03 (the coordinates are already in hand when the legend, the ticks and the panel titles are drawn); the long-table export is one projection function in 05 |
| **ParseBench expectation** | The largest single item. Upper bound +12.7 percentage points |
| **Failure criterion** | After training data carries key_carriers and complete address keys, the share of addressing failures in model output does not drop |

### A2 · Readability as a continuous quantity

**In one line**: change `readable` from a boolean to **ε — the relative precision this mark can attain under its current pixel geometry** — and change density from a fixed ceiling into a controlled independent variable.

The current criterion (`chart_types.md §4`) has three branches: value printed → tolerance 0; angle or colour → not readable; length or position → readable with tolerance 1% when "1% of the value converts to ≥ 2 pixels". Three problems: **(a)** the tolerance is the constant 1%, while the benchmark's estimated points have a median tolerance of 5% and a quartile range of [5%, 10%]; **(b)** the angle channel is excluded in advance, whereas pie charts would enter the value targets at a 5% tolerance; **(c)** the density ceilings (`grouped_bar` \|P\|·\|S\| ≤ 24, `line` ≤ 6 series) all work out to the "≤60 marks" bucket, which is the bucket with the lowest failure rate.

**Capability to add**

1. Compute ε per mark: `ε = (2 pixels × value per pixel) / |value|` for length and position; for the angle channel use the same form with the lower bound of measurable angle, without excluding it in advance; keep colour excluded. A mark with a printed value gets ε = 0.01.
2. Derive the value target's tolerance from ε, replacing the constant 1%.
3. Raise the structural ceilings, or add a high-density configuration, so that mark count covers the full range from 20 to 400+.
4. One more declaration-time field: the **value lattice** (integers / one decimal / percentage points / normalised to 100). It is a prior already known in the column declarations in 01, and it snaps a reading back onto a legal value.
5. New mark shapes and drawing methods: step lines, range connector lines (dumbbell), tick markers overlaid on bars, value labels moved outside with a leader, no value axis.

**Newly produced annotation quantity**: **the attainable reading precision ε of every mark**. Existing datasets state what the value is, never how precisely that value can be read off this particular image. With ε, the chain `density → attainable precision → model performance` becomes measurable inside one dataset — and [§5.2](#52-correlation-is-not-causation) explains why correlational analysis can never supply it. ε also turns the verifiable reward in [05 §3](../../storyline/parsebench_chart/05_output.md#3-输出能自己验自己) from binary into graded.

| | |
|---|---|
| **Items absorbed** | Failure-derived changes 4 (denser figures) · 5 (attainable precision + integer prior); `P1` `P5`; the value-label-form third of `P6`; 7 component gaps: `dense_marks_100plus` `value_label_outside` `thin_segment_label` `no_value_axis` `step_line_series` `range_connector_line` `tick_marker_as_series` |
| **Evidence** | ≤20 marks 85.5% → >400 marks 57.9% (disjoint intervals); 199 reading failures, median relative error 15%, only 13% within 5%; 14 `value_absent`; measured estimation tolerance median 5% against a hard-coded 1% in the current spec |
| **Generality** | General. ChartAB reports that small-element localisation degrades sharply on dense layouts, but no work generates a density ladder **under control**; ε is the definition of that ladder's dependent variable |
| **Cost** | Medium. ε is one formula in 04; the density ceilings are numbers in `chart_types.md`; the value lattice is a declaration field in 01; new mark shapes reuse the drawing code by shape, roughly one draw plus one record each |
| **ParseBench expectation** | The attributable part of the 28% reading-side failures; on `sri-sigma-…_p10` all eight points are exactly half a gridline low, which the value lattice recovers directly |
| **Failure criterion** | Bucket model error by ε; if error is independent of ε, ε is not a valid difficulty quantity |

### A3 · Presentation semantics of a number

**In one line**: the quantity a mark denotes is not the number in the data — it is that number after a **declared presentation chain**: scale factor, unit, basis, sign convention, numeric format. That chain currently has no field anywhere.

`.4` and `0.4` differ by a factor of ten; the figure title says BILLIONS, the label says `$101B`, and the rule wants `101`; a `2011 = 100` index moves the whole value range; negative values make rectangular marks grow from the zero line in both directions. None of the four has a place in the current three specs: `unit` exists only in the measure declaration in 01 and is never drawn; tick formatting is not a style-vector dimension; the zero line has never been written about.

**Capability to add**

1. Store both **`value` (canonical)** and **`printed` (the literal drawn on the figure)** in the record, with an explicit chain between them: `scale` (×10⁶ / ×10⁹ / percentage / normalised) · `unit` · `basis` (index base period) · `sign_convention` · `format` (thousands separator / currency symbol / parenthesised negatives / K,M,B suffix).
2. Make the **unit carrier position** a sampled dimension: axis title / subtitle / figure title / series name / every tick / value label / absent. Measured: 149 of 192 pages write the unit only in the axis title or the figure title.
3. Allow a measure's range to cross zero, support rectangular marks extending from the zero line in both directions, and put the value-axis origin and the broken-axis glyph into the style vector.
4. Add a fourth self-check — **magnitude round-trip**: the value recomputed from pixels, put through the declared presentation chain, must equal the literal printed on the figure.

**Newly produced annotation quantity**: **the pairing of canonical value with printed literal, plus the location of the unit carrier**. Existing chart-to-table datasets keep one number, so magnitude errors cannot be counted separately from reading errors. The axis also yields a negative-sample class no existing work has: the same `value` printed as two different literals under two presentation chains, both of which the model must get right.

| | |
|---|---|
| **Items absorbed** | Failure-derived changes 6 (ticks and units) · 7 (negatives and the zero line); the last two thirds of `P6`; 8 component gaps: `unit_in_axis_or_title` `negative_values` `nonstandard_time_ticks` `axis_starts_above_zero` `rebased_index_values` `pct_stacked` `unit_in_series_name` `broken_axis` |
| **Evidence** | 36 `unit_mismatch`, with a full page instance for each of the two writings; negative-valued points pass at 67.4% against 81.6% overall; `negative_values` -8.8% inside the control group (n=298); `nonstandard_time_ticks` -9.4% (n=218); 78% of pages carry the unit only in the title |
| **Generality** | General, and the most damaging error class: a 15% value error and a 1000% magnitude error cost differently in any downstream use, while current metrics count them as the same failure |
| **Cost** | Low. The presentation chain is declaration fields plus formatting functions; the zero line is a drawing branch; the round-trip check reuses `common/readback.py` |
| **ParseBench expectation** | The 4% magnitude failures, plus the negative-value gap |
| **Failure criterion** | Adding presentation-chain annotation does not lower the model's magnitude error rate |

### A4 · Non-data ink and absence

**In one line**: shapes drawn on a figure that are not any data point — reference lines, callout boxes, shaded bands, highlights, error bars, `N/A` placeholders — cannot currently be drawn at all, so this dataset has never taught which shapes must not be transcribed.

This is where the reclassification in [§1.3](#13-two-kinds-of-visibility) lands. All eight current training targets are recall-oriented: every shape drawn is a datum, and a model is never penalised for reporting one extra. Real report pages mix non-data graphics into every figure, and `pwc-…_p17` is exactly the case of a connector band read as a third series.

**Capability to add**

1. A new record section written by the renderer: **`decorations[]`**, each entry carrying a box, a role label (`reference` / `annotation` / `band` / `highlight` / `connector` / `uncertainty` / `absence`), and **whether it carries a number that must not be transcribed** (a target line at y=17% has a value but is not a data point).
2. A new training target: **non-data region discrimination** — given a region, answer whether it is a datum. Plus the matching evaluation quantity: **over-report rate**, the share of a model's output entries that land on `decorations[]`. None of the current eight targets measures this.
3. Absence as a first-class state: `N/A` and empty slots replace marks, and export writes a blank rather than 0. Today every cell after projection has a value and absence never enters the candidates.
4. Error bars: an uncertainty mark has upper and lower endpoints, and the upper endpoint must not be read as the value.

**Newly produced annotation quantity**: **exact negatives**. Nobody annotates "this line is not data" on real charts — it is expensive and the criterion is subjective; a record-while-drawing generator is the only zero-cost source of exact negatives. This axis extends the error surface of grounded transcription from "how much was missed" to "how much was invented" — **the strongest single new claim in this merge**.

| | |
|---|---|
| **Items absorbed** | Failure-derived change 8 (reference lines, callouts, bands); 6 component gaps: `reference_line` `annotation_callout` `shaded_band` `highlighted_category` `error_bars` `missing_value_marker` |
| **Evidence** | Inside the control group `annotation_callout` -11.8% (n=164 · 33 pages · 23 docs) and `reference_line` -11.6% (n=297 · 43 pages · 22 docs), 95% intervals disjoint; the mechanism instance on `pwc-…_p17` |
| **Generality** | General, and more general than ParseBench: any transcription-output task needs precision as well as recall, while existing chart datasets supervise recall only |
| **Cost** | Medium. New drawing shapes in 03, a new record section in 04, a new export function in 05; the first two stages are untouched |
| **ParseBench expectation** | The distractor-visible bucket, roughly -12% for each of the two items, recorded as zero before the reclassification |
| **Failure criterion** | After adding negative targets, the pass-rate gap between pages with and without reference lines / callouts does not narrow |

### A5 · The figure is a page object

**In one line**: a figure is not an image but a page object — it has an identity (figure number + title + subtitle + unit + position), a layout, and presentation degrees of freedom; that identity is both the addressing root on multi-figure pages and, on 60% of real figures, the only carrier of the unit and the basis.

Today the FigureSpec has panels, layout, sharing, relationship and source — five fields, no title. What exists is `caption`, drawn **below** the figure, and only the three intent figures out of eight have a caption carrying information; the other five restate the axis names.

**Capability to add**

1. Add `title` to the FigureSpec: figure number + main title + optional subtitle + unit; render it **above** the plot area, with position becoming a four-valued style dimension (above / side column / below / none). The figure number is assigned per page by the page compositor.
2. Synthesise the title from the declarations by template (measure name + dimension names + aggregate + time range + unit); for intent figures, have the single LLM call in 01 emit one more line. **No additional LLM call.**
3. Separate `caption` from `title`: `title` exists on every figure and enters the L0 Text elements; `caption` is produced only for intent figures, so that training target stops being diluted by uninformative samples.
4. Fill in the layout and presentation degrees of freedom: a body-text column beside the figure, multiple figures per page, horizontal bars, legend inside the plot area, value axis on the right, axis title position, panel background colour, line style distinguishing series.
5. A whole-page markdown export: the chart part as long tables, the figure title written as a markdown heading **before** the table.

**Newly produced annotation quantity**: **figure identity links the L0 layout layer to the L1 encoding layer**. Today those two layers are connected only through "the chart is one Picture box"; with figure identity, every text block on the page can be attributed to a field of a specific figure, which is the form document-parsing benchmarks ask for.

| | |
|---|---|
| **Items absorbed** | Failure-derived changes 9 (title and figure number) · 10 (page text volume); `P7` and the whole-page export part of `P3`; 9 component gaps: `side_text_bullets` `panel_background` `horizontal_bars` `axis_title_above_axis` `axis_title_below_plot` `legend_inside_plot` `right_side_y_axis` `dashed_line_series` `data_link_below_figure` |
| **Evidence** | 254 / 265 figures have a title (96%) · 149 carry a figure number (56%) · 88 have more than one title line (33%) · 159 write the unit into the title (60%); four positions: above 231 · below 15 · none 11 · side column 8; 46 pages carry more than one figure |
| **Generality** | Highly general, **but not a scoring lever**: only 14 of 4,864 rules (0.14%) use the figure number as an addressing label, and no rule's value contains a magnitude word. The value of this axis is realism and transfer to document-parsing tasks |
| **Cost** | Low. None of the three pieces needs an additional LLM call |
| **ParseBench expectation** | Close to zero. The figure-number portion of the 48 `row_missing` cases |
| **Failure criterion** | Not tied to the ParseBench score; instead: the gap between generated pages and real report pages in the distribution of the five title fields does not narrow |

### M · Every axis ships its own ablation row

This is the methodological axis. It produces no capability, and it decides whether this work is a dataset or a paper.

Both analyses can only give correlations. The page analysis's `affects` is fixed a priori from the metric definition, and its difficulty labels are model predictions; the failure analysis's component price table controls only the largest confound inside the control group (whether values are printed on the figure), while components co-occur heavily — dense figures also tend to carry reference lines and to omit printed values. **"Untitled figures pass twenty points lower" is quite likely "untitled figures are mostly dense dashboard layouts".**

There is exactly one way to turn correlation into causation: **generate two groups of figures varying a single dimension with everything else fixed**. That is the one structural advantage a generation pipeline has over any real corpus, and it is the step that turns A1–A5 from an engineering list into publishable results.

| Axis | The ablation row it becomes | What it measures with everything else fixed |
|---|---|---|
| A1 | complete key / key trimmed to two · with key_carriers / without | share of addressing failures |
| A2 | density ladder (20 / 60 / 150 / 400 / 1000 marks) · ε buckets | reading error as a function of ε |
| A3 | several presentation chains over the same `value` · six unit carrier positions | magnitude error rate |
| A4 | with non-data ink / without · with negative targets / without | over-report rate |
| A5 | four title positions · one figure per page / several | contribution of the context fallback (weak signal on this split, see [§5.2](#52-correlation-is-not-causation)) |

None of the eight rows in the current ablation table ([05 §7](../../storyline/parsebench_chart/05_output.md#7-消融)) touches titles, a density ladder, presentation chains or non-data ink. These five rows are purely additive.

---

## 3 Coverage and verdicts

### 3.1 Where the ten failure-derived changes went

| # | Original change | Axis | Verdict |
|---:|---|---|---|
| 1 | Export one value per row with all keys written out | A1 | Keep, upgraded: the capability is `key_carriers[]`, not just the export format |
| 2 | Multi-panel figures write the panel name as a key | A1 | **Restated**: not a multi-panel-specific field but global uniqueness of the key. Panel count itself is unrelated to pass rate |
| 3 | Colour → series correspondence | A1 | Keep, generalised: a series name has five carrier forms, the legend being one |
| 4 | Be able to draw denser figures | A2 | Keep |
| 5 | Attainable precision + integer prior | A2 | Keep, upgraded: the integer prior generalises to a "value lattice" |
| 6 | Controllable tick writing and unit placement | A3 | Keep |
| 7 | Negative values and the zero line | A3 | Keep, merged with 6 into one presentation chain |
| 8 | Reference lines, callouts, shaded bands | A4 | **Promoted**: from realism item to score item, and it needs a new target class rather than a style switch |
| 9 | Figures need titles and numbers | A5 | Keep, **demoted**: close to zero in points, the value is realism and transfer |
| 10 | Set a target for page text volume | A5 | **Not an optimisation target**: the four buckets are non-monotonic (78.4 / 83.6 / 84.7 / 79.4), cause unidentified. Kept as a realism constraint: median 355 words, 94% of pages ≥100 words |

### 3.2 Verdicts on P1–P7

| P | Original statement | Verdict | Destination |
|---|---|---|---|
| P1 | `readable` from a binary gate to graded attainable precision | Keep | A2 |
| P2 | The panel dimension enters the key | **Restated** as "global uniqueness of the key" | A1 |
| P3 | Add a whole-page markdown export | **Split**: the long table is A1's export, the whole-page markdown is A5's page object | A1 · A5 |
| P4 | A weight vector for family sampling in rotation figures | Keep as a configuration item, **no axis** — it is a knob, not a capability. Uniform rotation stays the default | — |
| P5 | Raise the density ceilings | Keep | A2 |
| P6 | Add three dimensions to the style vector | **Split**: the value-label form belongs to readability, tick format and unit placement plus negatives and the zero line belong to presentation semantics. The three were already independent | A2 · A3 |
| P7 | Figure titles become first-class | Keep, **demoted** (score) and kept (realism); the figure-number-into-key part is promoted to A1 | A5 · A1 |

### 3.3 Where the 39 component gaps went

The page analysis lists 39 constructs that appear in the benchmark and are undefined in the current specs. The table below reorders them by axis. `Pg` is the page count out of 192, `List` is the page analysis's four-way classification (**score** / **realism** / **undecided** / **discard**), and `Cost` is the pass-rate difference measured inside the failure analysis's control group (blank when not separately measured).

| Axis | key | Pg | List | Cost |
|---|---|---:|---|---:|
| A1 | `wrapped_category_labels` | 58 | score | |
| A1 | `footnote_marker` | 52 | score | |
| A1 | `color_encodes_extra_attribute` | 26 | score | |
| A1 | `two_level_x_ticks` | 16 | score | |
| A1 | `small_multiples_5plus` | 12 | score | |
| A1 | `inline_series_labels` | 11 | score | |
| A1 | `icon_category_axis` | 9 | score | |
| A1 | `total_row_below_axis` | 6 | score | |
| A1 | `stacked_and_grouped` | 0 | undecided | |
| A2 | `value_label_outside` | 53 | score | |
| A2 | `no_value_axis` | 42 | score | |
| A2 | `dense_marks_100plus` | 41 | score | density ladder -27.6 |
| A2 | `thin_segment_label` | 19 | score | |
| A2 | `tick_marker_as_series` | 19 | score | |
| A2 | `range_connector_line` | 4 | score | |
| A2 | `step_line_series` | 4 | score | |
| A3 | `unit_in_axis_or_title` | 149 | realism | |
| A3 | `negative_values` | 42 | score | -8.8 |
| A3 | `nonstandard_time_ticks` | 34 | score | -9.4 |
| A3 | `axis_starts_above_zero` | 23 | score | |
| A3 | `rebased_index_values` | 19 | realism | |
| A3 | `pct_stacked` | 16 | score | |
| A3 | `unit_in_series_name` | 11 | score | |
| A3 | `broken_axis` | 2 | undecided | |
| A4 | `highlighted_category` | 45 | undecided | |
| A4 | `reference_line` | 43 | realism | **-11.6** |
| A4 | `annotation_callout` | 33 | realism | **-11.8** |
| A4 | `shaded_band` | 18 | undecided | |
| A4 | `missing_value_marker` | 11 | score | |
| A4 | `error_bars` | 2 | undecided | |
| A5 | `panel_background` | 49 | realism | |
| A5 | `side_text_bullets` | 44 | score | |
| A5 | `horizontal_bars` | 42 | undecided | |
| A5 | `axis_title_above_axis` | 41 | undecided | |
| A5 | `legend_inside_plot` | 21 | realism | |
| A5 | `data_link_below_figure` | 21 | discard | |
| A5 | `axis_title_below_plot` | 17 | discard | |
| A5 | `dashed_line_series` | 10 | realism | |
| A5 | `right_side_y_axis` | 6 | realism | -29.1 (6 pages / 4 docs, concentrated) |

**Merging resolves four of the "undecided" items**: `highlighted_category`, `shaded_band` and `error_bars` were left unjudged because their spread sat on the boundary or their page count was too low; filed under A4 they are four values of one capability and need no separate decision. `broken_axis` (2 pages) likewise joins A3's presentation chain.

**Three of the eight items the page analysis filed as "realism" carry a cost in the failure analysis**: `reference_line`, `annotation_callout`, `right_side_y_axis`. The first two have document spreads of 22 and 23, which is credible; the third comes from 4 documents only, and by the page analysis's own criterion (one publisher's habit is not a general drawing practice) it is not used as evidence on its own.

### 3.4 Whether the condition table itself needs new rows

There are only two type gaps: `map` (3 figures / 3 documents) and the three drawing methods the model named itself when reporting `other` (`dumbbell range plot` · `three-marker range plot` · `vertical dumbbell range plot`).

| Candidate | Decision | Reason |
|---|---|---|
| Range connector line (dumbbell / range plot) | **Add**, as a new mark shape | 4 pages / 2 documents is thin, but it is a new shape (two points plus a connecting segment) and falls inside A2's mark-shape extension at low marginal cost |
| Step line | **Add**, as a drawing method of `line` | Same, and a value is read differently than on a directly connected line |
| Tick marker as a series | **Add**, as a new mark shape | 19 pages / 7 documents; it has the same shape as a reference line and the opposite meaning, which makes it A4's control |
| Stacked and grouped in one figure | **Undecided** | 0 pages. The two dimensions consume P and S and the third has nowhere to go — a key-structure question (A1) rather than a drawing question |
| `map` | **Do not add** | A geographic projection is none of the six families and its marks are none of the five shapes. 3 documents; the condition table is not changed for it |

Conversely the three types present in the condition table and absent from this sample (`box` `funnel` `heatmap`) are **not removed** — they are capability held for other target benchmarks and for the type-breadth ablation; the finding only means they get no quota when weights are tuned for ParseBench.

### 3.5 Explicitly not done

| Not done | Reason |
|---|---|
| Cutting the other nine types to match ParseBench's type mix | The benchmark tests only bar / line / pie / compound. Cutting loses the 13-type coverage and the type-breadth ablation. The weight vector lives in configuration and defaults to uniform |
| Treating page text volume as an optimisation target | The four buckets are non-monotonic, the three confounds checked explain none of it, cause unidentified |
| Treating titles as a scoring lever | 0.14% of rules use the figure number, and no rule's value contains a magnitude word |
| Trimming the key to the two the benchmark needs | The generation-side output unit requires the key to be a complete address tuple; trimming sacrifices this dataset's own products for one benchmark |
| Adding a second plotting backend | Geometry may have only one source. Revisit when the style ablation shows backend differences actually affect real-benchmark performance |
| Changing the spec for `data_link_below_figure` and `axis_title_below_plot` | The metric cannot see them, and their document spread of 0.29 marks them as a single publisher's layout habit |

---

## 4 Roadmap and acceptance

### 4.1 Ordering

Ordered by evidence strength × breadth ÷ cost. The first two are the most firmly supported by this data.

| # | Axis | Evidence | Cost | ParseBench expectation | Value outside ParseBench |
|---:|---|---|---|---|---|
| 1 | **A1 complete address keys** | Strong (all 568 pages, no dependence on chart descriptions) | Low–medium | Upper bound +12.7 points | Grounding key components is a new annotation quantity |
| 2 | **A2 readability as a continuous quantity** | Strong (monotone curves with disjoint intervals) | Medium | The attributable part of the 28% reading side | ε is a new annotation quantity and the dependent variable of a controlled density ladder |
| 3 | **A3 presentation semantics** | Medium (36 magnitude failures plus the negative-value bucket) | Low | About 4% plus the negative-value gap | Magnitude errors counted separately from reading errors |
| 4 | **A4 non-data ink** | Medium (disjoint intervals inside the control group, but component co-occurrence not fully controlled) | Medium | About -12% for each of two items, recorded as zero before reclassification | Exact negatives, extending the error surface to over-reporting |
| 5 | **A5 page object** | Strong (descriptive statistics, 96% / 56% / 60%) | Low | Close to zero | Connects L0 and L1, transfers to document parsing |
| — | M ablation rows | — | Low (one extra render group per axis) | — | Turns correlation into causation; this is where publishability comes from |

**A1 and A2 can run in parallel**: one touches the record and the export, the other the condition table and the renderer. A3 and A5 both cost only at the declaration and formatting layers and can ride along. A4 is the only one requiring new drawing shapes and a new target type, and it comes after the capability is in place.

### 4.2 The claim and its failure criteria

The current claim is one sentence:

> Grounded transcription can be done by a single VLM — extracting every value while giving the region it was read from, matching dedicated parsers on chart-to-table while reaching layout-aware-pipeline-level visual grounding.

The merged evidence supports writing it as two parts, the second of which is new from this analysis:

> **(i)** On a system averaging 82.75% per page, 72% of the remaining failures are addressing failures — the model can read the number and cannot say whose number it is. The bottleneck of grounded transcription is therefore **addressing**, not reading precision.
>
> **(ii)** The supervision needed to close that gap is exactly the three classes only a record-while-drawing generator produces at zero cost: **the region of each key component's literal source**, **the attainable reading precision of each mark**, and **the shapes drawn on the figure that are not data**. Real charts can supply none of the three — each needs either per-component aligned annotation or a subjective judgement.

**Failure criteria** (if any holds, the corresponding axis does not stand):

| Axis | Failure criterion |
|---|---|
| Overall claim | Adding the region output lowers numeric precision below the table-only control |
| A1 | After key_carriers and complete address keys, the share of addressing failures does not drop |
| A2 | Model error is independent of ε |
| A3 | Presentation-chain annotation does not lower the magnitude error rate |
| A4 | The pass-rate gap between pages with and without non-data ink does not narrow |
| A5 | The gap to real pages in the distribution of the five title fields does not narrow |

### 4.3 Which spec line each axis lands on

| Axis | Spec files | What exactly |
|---|---|---|
| A1 | `02_figure.md` FigureSpec · `04_record.md` §3 record fields · `05_output.md` §2 training targets | `panel_key` field; `legend[]` → `key_carriers[]`; long-table export projection |
| A2 | `chart_types.md` §2 conditions · §3 mark shapes · §4 how values are drawn · `04_record.md` §5 | density ceilings; three new mark shapes; `readable` → ε; a value lattice in the column declarations in `01_data.md` |
| A3 | `01_data.md` measure declaration · `03_render.md` §3 style vector · `04_record.md` §6 self-checks | five presentation-chain fields; unit carrier position; bidirectional zero line; a fourth self-check |
| A4 | `03_render.md` §1 record while drawing · `04_record.md` §3 · `05_output.md` §2 | `decorations[]`; non-data region discrimination target; over-report rate |
| A5 | `02_figure.md` §5 FigureSpec · `03_render.md` §0 §5 · `05_output.md` §2 §4 | five `title` fields; four title positions; caption separated from title; whole-page markdown export |
| M | `05_output.md` §7 ablation | five new ablation rows |

**No item asks for anything existing to be deleted.** The one real constraint risk is letting the benchmark's type distribution drive generation in reverse; the first row of [§3.5](#35-explicitly-not-done) holds that at the configuration layer.

---

## 5 Method and limits

### 5.1 How the two runs were done

| | Page analysis | Failure analysis |
|---|---|---|
| Input | Full-page PNG at 150 dpi, one structured call per page, effort `high`, `max_tokens` 12000, no cropping, no OCR, no second round | The `<page>.result.json` and `_evaluation_report.json` of one run directory; no model calls, no rescoring |
| Model | `claude-opus-5` | The analysed system is PP-DocLayoutV3 lean + `Qwen3.8-27B-FP8`, 200 dpi, verify_rounds=4, median 91 seconds per page |
| What the model could not see | The spot-check points' **labels**, the vocabulary's "do we have it" column, the "which step it affects" column, the pipeline structure | — |
| Scoring | Values were given to the model and labels were not, so "which keys are needed to address this" is a prediction that rules score: 1,155 of 1,635 placed values correct (71%) | Every `passed` comes from the official report. The local re-search agrees with the official metric on "was the value found" at 99.84% (8 disagreements over 4,864 points) |
| Result | 195 cross-check contradictions (the largest class being predicted addressing labels missing a label the rule actually used, 129); 514 self-named components the vocabulary could not hold | Page average 82.75%, micro 81.58%, 296 perfect pages, 15 zero pages |

Under the same conditions (same 568 pages, same 4,864 rules, official metric) the analysed run scores above every method on the public leaderboard (highest: LlamaParse Agentic 78.11%). Whether the leaderboard rows were computed with the same evaluation code cannot be verified here, so "new SOTA" is not claimed; what can be stated is that **the failures analysed here are what remains of an already strong system**.

### 5.2 Correlation is not causation

Every row of the form "component → pass rate" in section 1 is a correlation, for three reasons:

1. **Components co-occur heavily.** Dense figures also tend to carry reference lines and to omit printed values. The control group controls only the largest confound — whether values are printed on the figure, which alone is worth 19 percentage points (all printed 94.5% · partly 92.0% · none 75.9%).
2. **"n" is not the amount of evidence.** A page holds at most ten spot-check points, so n=60 may come from six pages in two reports — one publisher's habit. `right_side_y_axis` at -29.1% is exactly that case (6 pages / 4 documents). The criterion is document spread, never point count.
3. **The rows on the other side are not levers.** `axis_starts_above_zero`, `data_link_below_figure` and `figure_number_title` mark "this is a publisher that draws figures carefully".

**The only path from correlation to causation** is to generate two groups of figures varying one dimension with everything else fixed — which is the entire content of [§2 M](#m--every-axis-ships-its-own-ablation-row), and where this merged report locates the publishable part of the work.

### 5.3 Not measured

- **One model, one pipeline.** The failure-form distribution belongs to this system, not to models in general. Every priority in section 1 derived from a distribution share (A1's 72%, A2's 28%) must be recomputed for a different pipeline.
- **The Visual Grounding dimension was not touched.** This run holds parse products only, with no element-box evaluation — and "one model strong on both" is precisely this project's claim, so half of it currently has no measurement.
- **The 192 pages are not independent of the full set.** The component price table rests on a random subset of the same pages and can only raise hypotheses.
- **The chart descriptions come from another model** (`claude-opus-5`), whose errors pass straight into every row that uses a description as an independent variable. One reverse check is row 4 of [§1.2](#12-four-crossings).
- **Two failure forms could not be separated**: "wrong series" and "read the cumulative value" produced only 10 candidates across the full set, and each wrote a number one gridline from the truth — coincidence explains that equally well. Those points are merged into reading failures. **Cause unidentified; no explanation is offered.**
- **A4's cost is not independently controlled.** The pass-rate differences for `reference_line` and `annotation_callout` hold inside the control group, but the two co-occur (the same set of publishers annotate their figures). A4's causal value can only come from the ablation row in [§2 M](#m--every-axis-ships-its-own-ablation-row).

### 5.4 Relation to the other two reports

| | This one | [reports/](../reports/INDEX.md) | [failures/](../failures/ppdoclayoutv3_lean_qwen/INDEX.md) |
|---|---|---|---|
| Reads | The conclusions of those two | The benchmark pages themselves | One parser's failure sample |
| Produces | 5 capability axes + 1 methodological axis, with ordering and failure criteria | 39 component gaps, type mix, the five title fields | The form of 896 failures, the price table, ten page-level mechanism instances |
| Independence | Every number is restated here; this document reads through without opening those two | — | — |
| Per-page evidence | None (instance pages are not duplicated here) | `pages/`, 192 per-page reports | `cases/`, 10 per-page instances |

**This directory writes no file under either of the other two.** When the source page behind a conclusion is needed, page evidence is in `reports/pages/` and failure instances are in `failures/ppdoclayoutv3_lean_qwen/cases/`.
