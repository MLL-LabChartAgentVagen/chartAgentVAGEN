# timevalue_p9

![timevalue_p9](../../data/pages/timevalue_p9.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `timevalue_p9` | timevalue | need_estimate | 9 | `parsebench/data/pages/timevalue_p9.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一张 PowerPoint 幻灯片:大标题「Holding Period and Value」+ 装饰色块横条,页脚页码「9」,整页带浅色横条纹背景。图本身是单面板折线图,三条带点标记的线(方块/三角/叉),图例竖排在绘图区右侧(legend_beside_plot),无图号、无标题、无 source 行。左轴竖排标题「Future value of $100 investment」,刻度 0–4500、步长 500,只有横向网格线;下轴标题「Holding period (in years)」,刻度 1、5、10、20、30、40——数值间隔不等却等距排布,实为文本类目轴。单位分两处:轴标题里的「$100 investment」和图例名里的「($)」。所有数值都不打标签。
> 
> **定位一个值难在哪**
> 取 Stocks ($) 在 10 年的 240:没有数据标签,只能对着 500 一格的网格读数;5% 容差仅 ±12,而 500 单位约 68 px,12 单位不到 2 px。更糟的是 10 年处三条线几乎重叠(Bonds 约 190、Bills 约 170),标记互相压住,连归属哪条线都要靠颜色分辨。700、420、280、250 同理。
> 
> **不确定的**
> 无法确认 240 究竟是 Stocks 的 10 年点还是别的点;两个 420 分别属于 Treasury Bonds(30)与 Treasury Bills(40),只能按趋势推断。绘图区是否有独立底色、条纹是否穿过绘图区,分辨率下看不清。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 单幅三系列折线图，六个持有期类别；纵轴从0到4500、每500一格，仅有水平网格线。三条线分别使用方块、三角形和叉形点标记，图例置于绘图区右侧。页面还包括大标题、双色横条和通页浅灰横纹。
> 
> **定位一个值难在哪**
> 
> 例如“10”年、“Stocks ($)”的240没有印在图上。其5%容差仅12，而纵轴刻度间隔为500，必须在一格内精确插值到约四十分之一；系列还需由右侧图例关联。
> 
> **不确定的**
> 
> 240、250、280等均由点位反读，无法确认底层精确值；细横纹似为整页模板背景，而非绘图区填充。

**gemini-3.1-pro**

> ### 画出来要什么
> 生成器需要支持绘制带数据标记的折线图（Line chart），能自定义较粗的线条样式以及不同的标记符号（方块、三角、叉号）。图例需放置在图表区域右侧，Y轴标题支持90度旋转显示。X轴需要支持将不均匀的时间或数值跨度（1、5、10、20、30、40）强制映射为视觉上完全等距的分类刻度（Ordinal axis）。图表绘图区仅需要水平网格线（hgrid），无需垂直网格线。
> 
> ### 定位一个值难在哪
> 以定位 `240`（Stocks ($) 在第 10 年的值）为例，图表中并未直接印出具体数值，完全依赖坐标轴进行估读。Y轴的主刻度间距高达 500，而 240 的 5% 容差仅为 12。在 500 的物理间距中分辨 12 的差异远超肉眼和一般视觉模型的解析极限，导致极易出现读取误差超过容差范围。
> 
> ### 不确定的
> 由于缺乏源数据表，不确定线条标记之间的过渡是简单的线性插值还是有更复杂的拟合逻辑；也不确定X轴的等距间距是有意为之，还是由于制图工具默认将离散数值当成分类标签来处理。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | line | 18 | — | above | none |
| gpt-5.6-sol | f1 | line | 18 | — | above | none |
| gemini-3.1-pro | f1 | line | 18 | — | above | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `hgrid_only` | ✓ | ✓ | ✓ | opus-5: horizontal rules at 500, 1000 ... 4500 across the panel; no vertical gridlines；gpt-5.6-sol: Horizontal rules cross the plot at 500-unit intervals; no vertical gridlines appear.；gemini-3.1-pro: horizontal grid lines are drawn, but no vertical grid lines exist |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: legend column 'Stocks ($) / Treasury Bonds ($) / Treasury Bills ($)' sits right of the plot area；gpt-5.6-sol: A legend column to the right lists the three investment series.；gemini-3.1-pro: the legend is positioned to the right of the plotting area |
| `mixed_marks` | ✓ | — | — | opus-5: each line carries square, triangle or cross point markers drawn over the line |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: 'Future value of $100 investment' set vertically along the left axis；gpt-5.6-sol: “Future value of $100 investment” runs vertically along the left axis.；gemini-3.1-pro: the y-axis title is rotated 90 degrees along the left edge |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: axis title 'Future value of $100 investment' fixes the scale of bare ticks 0-4500；gpt-5.6-sol: The y-axis title reads “Future value of $100 investment”.；gemini-3.1-pro: the y-axis title mentions '$100 investment' |
| `unit_in_series_name` | ✓ | ✓ | ✓ | opus-5: legend entries end in '($)': 'Stocks ($)', 'Treasury Bills ($)'；gpt-5.6-sol: Legend labels read “Stocks ($)”, “Treasury Bonds ($)” and “Treasury Bills ($)”.；gemini-3.1-pro: the legend entries include the unit, e.g., 'Stocks ($)' |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `uneven_numeric_category_axis` | opus-5 | 2,3 | x ticks '1, 5, 10, 20, 30, 40' spaced equally though intervals differ |
| `slide_title_not_figure_title` | opus-5 | 3,4 | 'Holding Period and Value' is the slide heading with a decorative bar, no figure number |
| `striped_page_background` | opus-5 | — | fine horizontal stripe texture covers the whole slide behind title and plot |
| `series_specific_point_markers` | gpt-5.6-sol | 3 | Square, triangle and x markers distinguish the three lines and repeat in the legend. |
| `page_wide_ruled_background` | gpt-5.6-sol | — | Closely spaced pale horizontal rules cover the entire page behind title and chart. |
| `equidistant_non_uniform_axis` | gemini-3.1-pro | 2 | x-axis ticks 1, 5, 10, 20 are drawn with equal visual spacing despite unequal numeric gaps |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 3850 | 40、Stocks ($) | Stocks ($)、40 | 40、Stocks ($) | Stocks ($)、40 | ✓ | ✓ | ✓ | 过 |
| 1550 | 30、Stocks ($) | Stocks ($)、30 | 30、Stocks ($) | Stocks ($)、30 | ✓ | ✓ | ✓ | 过 |
| 620 | 20、Stocks ($) | Stocks ($)、20 | 20、Stocks ($) | Stocks ($)、20 | ✓ | ✓ | ✓ | 过 |
| 240 | 10、Stocks ($) | Stocks ($)、10 | 10、Stocks ($) | Stocks ($)、10 | ✓ | ✓ | ✓ | 没过 |
| 700 | 40、Treasury Bonds ($) | Treasury Bonds ($)、40 | 40、Treasury Bonds ($) | Treasury Bonds ($)、40 | ✓ | ✓ | ✓ | 过 |
| 420 | 30、Treasury Bonds ($) | Treasury Bonds ($)、30 | 30、Treasury Bonds ($) | Treasury Bonds ($)、30 | ✓ | ✓ | ✓ | 过 |
| 250 | 20、Treasury Bonds ($) | Treasury Bills ($)、30 | 20、Treasury Bonds ($) | Treasury Bonds ($)、20 | ✗ | ✓ | ✓ | 过 |
| 420 | 40、Treasury Bills ($) | Treasury Bills ($)、40 | 40、Treasury Bills ($) | Treasury Bills ($)、40 | ✓ | ✓ | ✓ | 过 |
| 280 | 30、Treasury Bills ($) | Treasury Bonds ($)、20 | 30、Treasury Bills ($) | Treasury Bills ($)、30 | ✗ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f1` | ["category", "series"] | ["category", "series"] | ["series", "time"] | category × series | x 轴是 `Holding period (in years)`，刻度 1/5/10/20/30/40 等距排开，是离散的有序类目而不是时间轴（时间轴要有可比的间隔）。gemini 记的 time 不成立。三段图例 Stocks / Treasury Bonds / Treasury Bills 是系列。 |
