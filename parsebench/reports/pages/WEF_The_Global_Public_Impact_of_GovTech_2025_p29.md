# WEF_The_Global_Public_Impact_of_GovTech_2025_p29

![WEF_The_Global_Public_Impact_of_GovTech_2025_p29](../../data/pages/WEF_The_Global_Public_Impact_of_GovTech_2025_p29.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `WEF_The_Global_Public_Impact_of_GovTech_2025_p29` | WEF_The_Global_Public_Impact_of_GovTech_2025 | untagged | 4 | `parsebench/data/pages/WEF_The_Global_Public_Impact_of_GovTech_2025_p29.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 
> 一幅编号图（FIGURE 5）里有两个圆环图并排：左 "2024"、右 "2034"，四个扇段共用底部一行胶囊式图例（Public sector / Education / Healthcare and life science / Transport）。年份写在圆心空洞里，不是标题栏。两环半径不同，右环明显更大，用尺寸暗示总量增长；两环之间还有两条虚线从左环上下缘张开到右环，围出一块灰色楔形，像放大镜连接线。整页图区铺浅灰底色，无坐标轴、无刻度，数值全部以 "$670"、"$1,570" 形式直接印在扇段上，细扇段（$40、$70）的标签被挤到环外。标题里同时含单位与增长率："(in \$ billions in 2024 and 2034) with an estimate growth rate of 8% per annum"。
> 
> **定位一个值难在哪**
> 
> \$40 是 2024 环的 Transport 段。它没有轴可读，只能靠印字；难点在寻址：系列名只在共享图例里，年份只在圆心文字里。同一页 "\$70" 在 2024（Healthcare）和 2034（Transport）各出现一次，若表格缺 "2024"/"2034" 这一维，两行会互相冒充。
> 
> **不确定的**
> 
> 两环半径是否严格按总量（770 vs 2,030）缩放，无法确认；灰色楔形是装饰还是表达增长区间也只能猜。图下无 Source/Note，脚注 13,14 只出现在正文里，不属于图。

**gpt-5.6-sol**

> ### 画出来要什么
> 需绘制两个大小不同的四分区圆环图，以“2024”“2034”为中心标签；切片内印数值，共用底部图例，并以两条虚线连接圆环。标题、图号与单位在图上方，绘图区为浅灰色。
> 
> ### 定位一个值难在哪
> “220”印在2034年的黄色切片内；唯一定位还需结合圆环中心的“2034”和下方图例的“Education”。但页面没有数据表，首先卡在步骤1。
> 
> ### 不确定的
> 两条虚线没有文字说明，只能判断为跨圆环引导线；“of 8% per annum”可能只是标题自动换行，而非独立副标题。

**gemini-3.1-pro**

> **画出来要什么**
> 页面包含两个代表2024和2034年的环形图。生成器需要能够绘制环形图（Donut chart），在中心留白处插入面板标签（年份），在每个扇区内部标注带货币符号的绝对数值，并且支持不同大小的环形图并置。此外，需要在两个环形图的外边缘之间绘制带透视效果的虚线连接线，以强调总量的增长。底部需要一个统一的共享水平图例。
> 
> **定位一个值难在哪**
> 以数值670为例，它印在左侧的深绿色扇区内。必须通过底部的图例将其分类对应到“Public sector”，并通过环中心的文本“2024”确定其年份维度。因为年份只是悬浮在环中间的文本，完全不具备行列对齐的表格特征，解析器很难建立起 `[2024, Public sector] -> 670` 的正确映射。
> 
> **不确定的**
> 两个环形图的相对面积大小是否精确映射了总量的比例（约870增至约2030），还是仅仅为了配合虚线锥体产生视觉放大效果而随意缩放。此外，扇区内部数值的位置排版（特别是狭窄扇区）似乎是手工微调的，未见明确的排版规则。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | donut | 8 | FIGURE 5 | above | all |
| opus-5 | f2 | unreadable | 0 | — | none | none |
| gpt-5.6-sol | f1 | donut | 8 | FIGURE 5 | above | all |
| gemini-3.1-pro | f1 | donut | 8 | FIGURE 5 | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `legend_below_plot` | ✓ | ✓ | ✓ | opus-5: Legend pill sits under both rings, above the page footer；gpt-5.6-sol: The sector legend sits below both donuts, outside the plot.；gemini-3.1-pro: the legend sits below the plot area |
| `no_value_axis` | ✓ | — | — | opus-5: No ticks or axis anywhere; values readable only from printed labels like '$670' |
| `panel_background` | ✓ | ✓ | — | opus-5: Full-bleed pale grey band fills the whole figure area behind both rings；gpt-5.6-sol: Both donut panels sit on a light grey plot background. |
| `panel_title_per_panel` | ✓ | — | — | opus-5: '2024' and '2034' set large in the centre hole of each donut |
| `shared_legend` | ✓ | ✓ | ✓ | opus-5: One legend row below both donuts: Public sector, Education, Healthcare and life science, Transport；gpt-5.6-sol: One four-item legend below both donut panels names all sector colours.；gemini-3.1-pro: one legend with four categories at the bottom for both donuts |
| `small_multiples_4` | ✓ | ✓ | ✓ | opus-5: Two donuts of identical construction, one per year, side by side；gpt-5.6-sol: Two repeated donut panels are labelled “2024” and “2034”.；gemini-3.1-pro: two identical chart types side by side for different years |
| `thin_segment_label` | ✓ | — | — | opus-5: '$40' and 2034's '$70' crowd the narrow Transport slivers and shift off the segment |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: Title reads 'IT spending in various sectors (in $ billions in 2024 and 2034)'；gpt-5.6-sol: The heading says “in $ billions in 2024 and 2034”.；gemini-3.1-pro: the title includes '(in $ billions in 2024 and 2034)' |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: '$670', '$1,570', '$220' printed on top of their ring segments；gpt-5.6-sol: “$670”, “$220”, “$170”, and “$40” are printed inside coloured slices.；gemini-3.1-pro: numbers like $670 and $220 are printed inside the colored segments |
| `value_label_outside` | ✓ | — | — | opus-5: '$40' and '$70' sit just outside the ring above the thin cyan slices |
| `wrapped_category_labels` | ✓ | — | — | opus-5: Legend entry 'Healthcare and life science' is a long multi-word category name |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `zoom_connector_between_panels` | opus-5 | — | Two dashed lines fan from the 2024 ring's top and bottom edges to the 2034 ring, enclosing grey wedge |
| `panel_size_encodes_total` | opus-5 | 2 | The 2034 donut is drawn with a visibly larger radius than the 2024 donut |
| `panel_title_in_donut_hole` | opus-5 | 3 | '2024' and '2034' are set inside the white centre hole, not above the panel |
| `figure_number_in_side_column` | opus-5 | 4 | 'FIGURE 5' sits in a left margin column, ruled off from the title text |
| `donut_center_panel_label` | gpt-5.6-sol | 3 | “2024” and “2034” are centred inside the two donut holes. |
| `inter_panel_dashed_connectors` | gpt-5.6-sol | — | Two dashed diagonal guide lines connect the 2024 donut to the 2034 donut. |
| `unequal_donut_panel_sizes` | gpt-5.6-sol | 2 | The 2034 donut is visibly larger in diameter than the 2024 donut. |
| `growth_cone_between_charts` | gemini-3.1-pro | — | dashed lines connecting the outer edges of the two donuts |
| `panel_label_in_donut_hole` | gemini-3.1-pro | 3 | 2024 and 2034 are printed inside the center holes |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 670 | Public sector、2024 | 2024、Public sector | 2024、Public sector | 2024、Public sector | ✓ | ✓ | ✓ | 过 |
| 220 | Education、2034 | 2034、Education | 2034、Education | 2034、Education | ✓ | ✓ | ✓ | 过 |
| 170 | Healthcare and life science、2034 | 2034、Healthcare and life science | 2034、Healthcare and life science | 2034、Healthcare and life science | ✓ | ✓ | ✓ | 过 |
| 40 | Transport、2024 | 2024、Transport | 2024、Transport | 2024、Transport | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `hardest_step` | 3 | 1 | 3 | 未裁决 · 无实测证据 | 这一页 4 个抽查点全过，运行没有在任何一步卡住，三家的 3 / 1 / 3 都无法证伪。 |
| `key_roles#f1` | ["panel", "series"] | ["series", "time"] | ["panel", "series"] | panel × series | opus 与 gemini 一致：两个绘图区各是一个年份（`2024` 印在面板上方）。gpt 把同一个 `2024` 记成 time——页面上没有时间轴，它是面板的名字。 |
