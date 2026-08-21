# GWR-2024_Layout_E_RGB_Web_p58

![GWR-2024_Layout_E_RGB_Web_p58](../../data/pages/GWR-2024_Layout_E_RGB_Web_p58.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `GWR-2024_Layout_E_RGB_Web_p58` | GWR-2024_Layout_E_RGB_Web | 3d_chart+need_estimate | 10 | `parsebench/data/pages/GWR-2024_Layout_E_RGB_Web_p58.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一个编号图 Figure 5.3，四个小面板（Low-income / Lower-middle-income / Upper-middle-income / High-income countries），每板各自画：左值轴 0–60「Female wage workers (%)」（竖排标题）、右值轴 −4 到 30、每 2 一格的「Gender wage gap (%)」（红字，与红菱形同色）、底部类别轴 D1–D10 加轴标题「Deciles of the hourly wage distribution」。每板 10 根蓝柱 + 10 个红菱形 + 10 个黄三角，共约 120 个标记，全图无任何数字标签。四板共用一条下置图例，外加 Notes 与 Source 两段小字，整块图坐在浅蓝底色上。
> 
> **定位一个值难在哪**
> 
> 取 22：它是 Low-income countries、D1 的红菱形，读的是**右轴**而非左轴。同一像素高度在左轴读作 45、在右轴读作约 22，必须先判断标记归属哪条轴；右轴刻度间距 2，而 5% 容差只有 ±1.1，菱形与同处的黄三角几乎重叠。一行表还要同时带面板名、D1、legend 名三个标签才唯一。
> 
> **不确定的**
> 
> 右轴数值全靠像素换算（0 与左轴 0 不对齐，左 0 对右 −4），所以 22/24/19/18/11 都是估读；28 无法唯一定位（Lower-middle D3 柱约 28.5 与 Low-income D8/D9 柱约 28 都符合）；56 在高收入 D1 与 D2 上几乎相同。

**gpt-5.6-sol**

> **画出来要什么**
> 需绘制四宫格复合图：每格10根蓝色柱，并叠加红色菱形、黄色三角形两组点；左右双百分比轴、统一图例、分面标题及浅蓝背景。
> 
> **定位一个值难在哪**
> 例如“High-income countries—D5—Mean gender wage gap by decile”的11，要先选分面、D5、菱形系列，再按右轴每2个百分点插值；5%容差仅0.55。
> 
> **不确定的**
> 所有数值均未印在标记上；同一整数可能由多个邻近标记读出，因此部分抽查值的具体归属只能依位置推定。

**gemini-3.1-pro**

> **画出来要什么** 生成器需要支持2x2的小型多重图（small multiples），并在每个子面板内绘制双Y轴（左侧为柱状图，右侧为散点标记，无连接线）。需要支持为左右Y轴分别设置不同的量程、刻度和标题，支持绘图区背景色填充，以及在图表底部统一放置全局图例和长文本注释。 **定位一个值难在哪** 以“Upper-middle-income countries”面板中“D2”类别的“Mean gender wage gap by decile”为例（值为19）。该值没有任何数字标签，必须依靠肉眼将其水平对齐到右侧Y轴。由于缺乏网格线辅助，且图表内部存在三种不同的标记重合（柱子、菱形、三角形），在右侧纵轴间隔为2的密集刻度下，将其精确读取到5%容差范围内非常困难。 **不确定的** 图形中散点（菱形和三角形）在多处有重合甚至完全遮挡，右侧Y轴的精确读数在没有水平网格线的情况下存在一定程度的估算成分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | compound | 120 | Figure 5.3. | above | none |
| gpt-5.6-sol | f1 | compound | 120 | Figure 5.3. | above | none |
| gemini-3.1-pro | f1 | other · mixed marks | 120 | Figure 5.3. | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | ✓ | — | opus-5: Category ticks read 'D1 D2 D3 ... D10' with a separate title naming deciles；gpt-5.6-sol: Each category axis uses decile codes “D1” through “D10”. |
| `axis_title_below_plot` | — | — | ✓ | gemini-3.1-pro: 'Deciles of the hourly wage distribution' sits below x-axis |
| `dense_marks_100plus` | ✓ | ✓ | ✓ | opus-5: 4 panels x 10 deciles x 3 series = 120 drawn marks；gpt-5.6-sol: Four panels × ten deciles × three marks produces 120 marks.；gemini-3.1-pro: 4 panels * 10 categories * 3 series = 120 marks |
| `dual_axis` | ✓ | ✓ | ✓ | opus-5: Left axis 'Female wage workers (%)' 0-60; right axis 'Gender wage gap (%)' -4 to 30 in each panel；gpt-5.6-sol: Every panel has left 0–60 and right -4–30 value axes.；gemini-3.1-pro: left axis for share of women, right axis for wage gaps |
| `hgrid_only` | — | ✓ | — | gpt-5.6-sol: Faint horizontal rules cross the panels; no vertical grid is drawn. |
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: Legend row sits below the bottom two panels, above the Notes block；gpt-5.6-sol: The three-item legend is centered below all four plots.；gemini-3.1-pro: legend sits at the bottom of the multi-panel figure |
| `mixed_marks` | ✓ | ✓ | ✓ | opus-5: Blue bars with red diamond and yellow triangle markers overlaid at each decile slot；gpt-5.6-sol: Blue bars are overlaid with red diamond and yellow triangle point series.；gemini-3.1-pro: bars for share of women, point markers for wage gaps |
| `negative_values` | ✓ | ✓ | ✓ | opus-5: Right axis ticks read '2, 0, -2, -4'; the D10 triangle in Lower-middle panel sits below zero；gpt-5.6-sol: The right axes extend to -4; Lower-middle-income D10 markers fall below zero.；gemini-3.1-pro: right axis starts at -4 with zero above it |
| `panel_background` | ✓ | ✓ | ✓ | opus-5: The whole figure band, plot areas included, sits on a pale blue fill across the page width；gpt-5.6-sol: All four plot areas sit on a pale blue tint.；gemini-3.1-pro: all four plot areas have a light blue tint |
| `panel_title_per_panel` | ✓ | ✓ | ✓ | opus-5: 'Low-income countries', 'Lower-middle-income countries', 'Upper-middle-income countries', 'High-income countries' above each panel；gpt-5.6-sol: Panels are titled “Low-income countries” through “High-income countries” above each plot.；gemini-3.1-pro: titles like 'Low-income countries' above each panel |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Female wage workers (%)' and 'Gender wage gap (%)' set vertically along left and right axes；gpt-5.6-sol: Both value-axis titles run vertically beside every panel.；gemini-3.1-pro: y-axis titles are printed vertically alongside the axes |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: One legend row under all four panels: 'Share of women by decile', 'Mean gender wage gap by decile'；gpt-5.6-sol: One three-item legend governs all four panels.；gemini-3.1-pro: one legend row below all four panels |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: Four identical charts, one per country income group, in a 2x2 grid；gpt-5.6-sol: Four repeated decile panels form a two-by-two layout.；gemini-3.1-pro: four panels arranged in a 2x2 grid |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: 'Notes: Each of the four charts shows two vertical axes...' and 'Source: ILO estimates based on national survey data from 82 countries.'；gpt-5.6-sol: “Notes:” and “Source:” lines appear beneath the legend.；gemini-3.1-pro: Notes and Source text printed below the legend |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: Title ends '(percentage)'; axis titles carry '(%)' while ticks are bare numbers 0,10,...,60；gpt-5.6-sol: “Female wage workers (%)”, “Gender wage gap (%)”, and “(percentage)” state units.；gemini-3.1-pro: (percentage) in heading, (%) in axis titles |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `axis_colour_matched_to_series` | opus-5 | 2,3 | Right axis ticks and title 'Gender wage gap (%)' printed in red, matching the red diamond series |
| `asymmetric_tick_density_dual_axis` | opus-5 | 2 | Left axis has 7 ticks (0..60 by 10); right axis has 18 ticks (-4..30 by 2) |
| `category_axis_title_below_ticks` | opus-5 | 3 | 'Deciles of the hourly wage distribution' printed under the D1-D10 tick row in every panel |
| `marker_shape_encodes_series` | gpt-5.6-sol | 3 | Diamonds identify mean gaps while triangles identify median gaps in the legend and plots. |
| `point_markers_without_lines` | gemini-3.1-pro | 2 | wage gap series are drawn as disconnected floating shapes |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 45 | D1、Share of women by decile、Low-income countries | Low-income countries、D1、Share of women by decile | Low-income countries、D1、Share of women by decile | Low-income countries、D1、Share of women by decile | ✓ | ✓ | ✓ | 没过 |
| 22 | D1、Mean gender wage gap by decile、Low-income countries | Low-income countries、D1、Mean gender wage gap by decile | Low-income countries、D4、Mean gender wage gap by decile | Low-income countries、D3、Mean gender wage gap by decile | ✓ | ✗ | ✗ | 没过 |
| 44 | D1、Share of women by decile、Lower-middle-income countries | Lower-middle-income countries、D1、Share of women by decile | Lower-middle-income countries、D1、Share of women by decile | Lower-middle-income countries、D1、Share of women by decile | ✓ | ✓ | ✓ | 没过 |
| 24 | D1、Mean gender wage gap by decile、Lower-middle-income countries | Lower-middle-income countries、D1、Mean gender wage gap by decile | Lower-middle-income countries、D1、Mean gender wage gap by decile | Lower-middle-income countries、D1、Mean gender wage gap by decile | ✓ | ✓ | ✓ | 没过 |
| 54 | D2、Share of women by decile、Upper-middle-income countries | Upper-middle-income countries、D2、Share of women by decile | Upper-middle-income countries、D2、Share of women by decile | Upper-middle-income countries、D2、Share of women by decile | ✓ | ✓ | ✓ | 过 |
| 19 | D2、Median gender wage gap by decile、Upper-middle-income countries | Upper-middle-income countries、D2、Mean gender wage gap by decile | Upper-middle-income countries、D2、Mean gender wage gap by decile | Upper-middle-income countries、D2、Mean gender wage gap by decile | ✗ | ✗ | ✗ | 过 |
| 56 | D1、Share of women by decile、High-income countries | High-income countries、D1、Share of women by decile | High-income countries、D1、Share of women by decile | High-income countries、D1、Share of women by decile | ✓ | ✓ | ✓ | 过 |
| 18 | D10、Mean gender wage gap by decile、High-income countries | High-income countries、D10、Mean gender wage gap by decile | High-income countries、D10、Mean gender wage gap by decile | Upper-middle-income countries、D5、Mean gender wage gap by decile | ✓ | ✓ | ✗ | 没过 |
| 11 | D5、Median gender wage gap by decile、High-income countries | High-income countries、D5、Mean gender wage gap by decile | High-income countries、D5、Mean gender wage gap by decile | Lower-middle-income countries、D5、Mean gender wage gap by decile | ✗ | ✗ | ✗ | 过 |
| 28 | D10、Share of women by decile、Lower-middle-income countries | Lower-middle-income countries、D3、Share of women by decile | Lower-middle-income countries、D3、Share of women by decile | Lower-middle-income countries、D3、Share of women by decile | ✗ | ✗ | ✗ | 没过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `type#f1` | "compound" | "compound" | "other · mixed marks" | compound | 三家图元数都是 120、都报 mixed_marks；gemini 写成 other · mixed bar and scatter，说的是同一件事。 |
