# Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65

![Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65](../../data/pages/Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65` | Activate_Consulting_Technology_&_Media_Outlook_2026_(10) | untagged | 9 | `parsebench/data/pages/Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一张分组柱图：3 个分段(SUPER GAMERS²/AVID GAMERS³/CASUAL GAMERS⁴)×3 个平台(MOBILE/CONSOLE/PC)，共 9 根柱。没有任何数值轴或刻度，只有一条基线，数字全部以 93%、82% 的形式印在柱顶外侧。图例不在上下方，而是贴在绘图区左侧的一列，每行由一个设备图标 + 文字 + 一条与柱色对应的横线组成。标题是整条蓝色色带：加粗的 “SHARE OF GAMERS¹ USING EACH PLATFORM FOR GAMING IN THE LAST 12 MONTHS” 后接常规体 “U.S., 2025, % GAMERS¹ BY SEGMENT”。绘图区带浅蓝六边形底纹，四处手绘风格的绿色椭圆圈住若干柱。
> 
> **定位一个值难在哪**
> 89% 在页面上出现两次：一次是 SUPER GAMERS² 的 PC 柱，一次是 AVID GAMERS³ 的 MOBILE 柱。要区分它们必须同时拿到分段名(x 轴)和平台名(左侧图例)，而平台与颜色的对应只靠图例文字下方那条细色线，没有色块，解析器很容易把两个 89% 混为一谈。
> 
> **不确定的**
> 图例三行的颜色横线是否真与柱色一一对应，只能按从上到下=从左到右推断；绿色椭圆到底圈了哪几根柱(Super Gamers 组似乎三根全圈)边界不清；页面无图号，是否属于更大编号体系无法判断。

**gpt-5.6-sol**

> **画出来要什么**：单面板三组×三平台分组柱图；左侧图标图例、全宽青色标题带、浅蓝图案背景、柱顶外置百分比、脚注与来源，以及绿色手绘圈注。无数值轴，仅有底部分类基线。
> 
> **定位一个值难在哪**：如 24%，须同时用“CASUAL GAMERS⁴”和“PC”定位；数值直接印出，难点是把远置图例的颜色对应到柱。
> 
> **不确定的**：未见图号；绿色圈线像后加批注，无法确认是否属于原始设计。轴无刻度，不能独立核验柱高。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面是一个带标注的分组柱状图。主标题和副标题横幅位于顶部。图表没有数值Y轴，只有底部类别X轴。图例（MOBILE、CONSOLE、PC）放置在图表最左侧外部，并使用对应颜色的粗实线作为引导线延伸入图表区域以指示映射。所有的数值（百分比）都直接印在各自的柱子上方。此外，图表还使用手绘风格的绿色椭圆圈对部分关键数值（如93%、82%、89%作为一个整体）进行了视觉强调标记。底部包含长段落的脚注和数据来源说明。
> 
> ### 定位一个值难在哪
> 以第一组的“93%”为例，虽然它的类别键“SUPER GAMERS²”就位于柱子正下方，但它的系列键“MOBILE”位于图表左侧较远的位置。由于缺乏网格线且图例与图表主体结构分离，解析器必须通过颜色（深蓝色）和图例旁的引导线来正确建立映射关系，非常容易在步骤3中丢失系列标签。
> 
> ### 不确定的
> 背景中淡淡的十字准星图案和渐变色块尚不确定是报告统一的页面装饰还是专属于该图表的背景设计；绿色的标记圈仅仅提供视觉强调，并没有承载额外的分类属性，因此不作为独立的数据键提取。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | grouped_bar | 9 | — | above | all |
| gpt-5.6-sol | f1 | grouped_bar | 9 | — | above | all |
| gemini-3.1-pro | f1 | grouped_bar | 9 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `annotation_callout` | ✓ | — | ✓ | opus-5: hand-drawn green ellipses drawn over the plot around the Super Gamers bars, 89% and 87%；gemini-3.1-pro: green circles drawn around specific sets of value labels |
| `footnote_marker` | ✓ | ✓ | ✓ | opus-5: `GAMERS¹`, `SUPER GAMERS²`, `AVID GAMERS³`, `CASUAL GAMERS⁴` superscripts keyed to notes 1-4；gpt-5.6-sol: Superscripts ¹, ², ³, and ⁴ appear in the heading and category labels.；gemini-3.1-pro: superscript 1, 2, 3, 4 on headings and categories |
| `grouped_bar` | ✓ | ✓ | ✓ | opus-5: three bars sit side by side inside each of SUPER GAMERS², AVID GAMERS³, CASUAL GAMERS⁴；gpt-5.6-sol: Three platform bars stand side by side within each gamer-segment category.；gemini-3.1-pro: three bars are grouped together per category |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: MOBILE / CONSOLE / PC stacked in a left-hand column level with the plot；gpt-5.6-sol: MOBILE, CONSOLE, and PC form a vertical legend left of the bars.；gemini-3.1-pro: MOBILE, CONSOLE, PC are listed on the left |
| `no_value_axis` | ✓ | ✓ | ✓ | opus-5: only a black baseline under the bars; no ticks or numbers on any vertical axis；gpt-5.6-sol: Only a bottom baseline is drawn; all nine percentages are printed above bars.；gemini-3.1-pro: no vertical axis line or tick marks drawn |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: plot area filled with a pale blue hexagon/plus pattern instead of white；gpt-5.6-sol: The plot carries a pale blue gaming image and geometric pattern instead of white.；gemini-3.1-pro: faint cross marks and blue gradient behind the chart |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Sources: Activate analysis, Activate 2025 Consumer Technology & Media Research Study (n = 4,026)`；gpt-5.6-sol: “Sources: Activate analysis, Activate 2025 Consumer Technology & Media Research Study (n = 4,026)” appears below.；gemini-3.1-pro: detailed text block at the bottom starting with 1. |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: banner ends `U.S., 2025, % GAMERS¹ BY SEGMENT`; no axis carries a unit；gpt-5.6-sol: The heading includes “% GAMERS¹ BY SEGMENT”.；gemini-3.1-pro: % GAMERS¹ is written in the blue subtitle banner |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: `93%`, `82%`, `89%` printed above the top of each bar, not inside it；gpt-5.6-sol: Every percentage is printed above its bar.；gemini-3.1-pro: percentage values sit above each bar |
| `wrapped_category_labels` | ✓ | — | — | opus-5: notes block under the plot wraps the four definitions across seven lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `icon_legend_entries` | opus-5 | 3 | each legend row shows a phone / gamepad / monitor pictogram in a box left of MOBILE, CONSOLE, PC |
| `legend_swatch_as_underline_rule` | opus-5 | 3 | series colour shown only as a coloured horizontal rule under each legend label, no colour patch |
| `handdrawn_ellipse_highlight` | opus-5 | 4 | green marker-style ovals enclose whole groups of bars and their printed labels |
| `heading_band_bold_plus_regular_runon` | opus-5 | 4 | one blue band: bold title then regular `, U.S., 2025, % GAMERS¹ BY SEGMENT` continuing the same line |
| `freehand_oval_highlight` | gpt-5.6-sol | 3 | Green freehand ovals encircle the three SUPER GAMERS² labels and the 89% and 87% mobile labels. |
| `icon_legend_entries` | gpt-5.6-sol | 3 | Phone, console, and PC pictograms appear beside the three legend labels. |
| `title_banner` | gpt-5.6-sol | 4 | The white figure heading sits inside a full-width teal banner above the plot. |
| `page_headline_above_figure` | gpt-5.6-sol | 4 | “Super Gamers play video games across all platforms, while Avid and Casual Gamers primarily use mobile” appears above. |
| `legend_with_horizontal_lines` | gemini-3.1-pro | 3 | thick horizontal colored lines extend from legend into plot |
| `hand_drawn_annotation` | gemini-3.1-pro | — | green circles appear to be hand-drawn style highlights |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 93 | MOBILE、SUPER GAMERS | MOBILE、SUPER GAMERS² | SUPER GAMERS²、MOBILE | SUPER GAMERS²、MOBILE | ✓ | ✓ | ✓ | 过 |
| 82 | CONSOLE、SUPER GAMERS | CONSOLE、SUPER GAMERS² | SUPER GAMERS²、CONSOLE | SUPER GAMERS²、CONSOLE | ✓ | ✓ | ✓ | 过 |
| 89 | PC、SUPER GAMERS | PC、SUPER GAMERS² | SUPER GAMERS²、PC | SUPER GAMERS²、PC | ✓ | ✓ | ✓ | 过 |
| 89 | MOBILE、AVID GAMERS | MOBILE、AVID GAMERS³ | AVID GAMERS³、MOBILE | AVID GAMERS³、MOBILE | ✓ | ✓ | ✓ | 过 |
| 56 | CONSOLE、AVID GAMERS | CONSOLE、AVID GAMERS³ | AVID GAMERS³、CONSOLE | AVID GAMERS³、CONSOLE | ✓ | ✓ | ✓ | 过 |
| 70 | PC、AVID GAMERS | PC、AVID GAMERS³ | AVID GAMERS³、PC | AVID GAMERS³、PC | ✓ | ✓ | ✓ | 过 |
| 87 | MOBILE、CASUAL GAMERS | MOBILE、CASUAL GAMERS⁴ | CASUAL GAMERS⁴、MOBILE | CASUAL GAMERS⁴、MOBILE | ✓ | ✓ | ✓ | 过 |
| 34 | CONSOLE、CASUAL GAMERS | CONSOLE、CASUAL GAMERS⁴ | CASUAL GAMERS⁴、CONSOLE | CASUAL GAMERS⁴、CONSOLE | ✓ | ✓ | ✓ | 过 |
| 24 | PC、CASUAL GAMERS | PC、CASUAL GAMERS⁴ | CASUAL GAMERS⁴、PC | CASUAL GAMERS⁴、PC | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
