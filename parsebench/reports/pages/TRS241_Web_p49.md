# TRS241_Web_p49

![TRS241_Web_p49](../../data/pages/TRS241_Web_p49.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `TRS241_Web_p49` | TRS241_Web | need_estimate | 10 | `parsebench/data/pages/TRS241_Web_p49.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> **画出来要什么**
> 一幅黑白散点图：整幅带外框、刻度向内的坐标框；左侧竖排轴标题 `1981 per capita GDP at market prices (US $)`（刻度 2000…18000），底部 `1981 per capita energy use (GJ)`（100…400）。17 个国家点，每点上方直接写两字母代码（`CH`、`SE`、`US`…），无图例色彩；图内另有两个方框：一个是缩写对照表 `AR: ARGENTINA … YU: YUGOSLAVIA`，一个是来源框 `Sources: IAEA Energy and Economic Data Bank / 1983 World Bank Atlas`。右侧还要画三段带双箭头的竖向括弧＋两条横向分界线，标 `Industrial market economies` / `middle income economies` / `low income economies`。标题以 `FIG.2.2.` 斜体置于图下。
> 
> **定位一个值难在哪**
> 取 `CH` 的横坐标 140 GJ：图上不印任何数字，x 轴每 100 GJ 一格、无网格线，5% 容差只有 ±7 GJ，约 9 像素；而点被 `CH` 标签遮住，且要先由图内对照表把 `CH` 还原成 SWITZERLAND 才能与表格行名对上。
> 
> **不确定的**
> 右下角 2600 究竟属 `AR` 还是 `YU`（两点重叠）；300 与 310 分别属 `US` 还是 `CA` 也无法判定；分界横线对应的 GDP 阈值没有标数。

**gpt-5.6-sol**

> ### 画出来要什么
> 单面板散点图，双数量轴分别表示人均能源使用与人均GDP；17个点以国家代码直接标注。图内还需绘制国家代码对照框、来源框，以及带箭头和分界线的收入经济体分类；图题置于图下。
> 
> ### 定位一个值难在哪
> 例如“CN”的GDP值300只能从纵轴估读。纵轴首个标示刻度是2000，刻度间隔也为2000，而300的5%仅15，远低于图像可辨精度。
> 
> ### 不确定的
> 所有数据值均未印在点旁；140、300等只能按点位和国家代码推定。右侧分类线没有数值刻度，其确切阈值不可见。

**gemini-3.1-pro**

> ### 画出来要什么
> 需要生成一个双数值轴的散点图，散点不仅包含位置信息，其旁边还需要直接印有分类的缩写标签（如"CH"、"US"）。图表内部放置了一个类似图例的文本框，用于将缩写映射为国家全称。最具挑战性的是，绘图区右侧外边缘需要绘制带有箭头的垂直标尺带（bracket），用来标注“Industrial market economies”、“middle income economies”和“low income economies”这三个不同的数值跨度范围，这超出了传统图表坐标轴和辅助线的范畴。
> 
> ### 定位一个值难在哪
> 以瑞士（CH）的纵坐标值 `17500` 为例，图中既没有水平和垂直网格线，也没有数据点到坐标轴的引导线。Y轴的刻度间距极大（每档2000），要在一个两档之间的广阔空白区域中纯靠肉眼平行映射到Y轴并估算出 17500，且保证误差在5%以内，实际上是不可能的。
> 
> ### 不确定的
> 左下角靠近原点的低收入国家聚类区（如IN、CN、PH）标签和数据点高度重叠。仅凭视觉很难确切对应哪个黑点属于哪个国家，这导致读取这些数据点的坐标值时包含极大的猜测成分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | scatter | 17 | FIG.2.2. | below | none |
| gpt-5.6-sol | f1 | scatter | 17 | FIG.2.2. | below | none |
| gemini-3.1-pro | f1 | scatter | 17 | FIG.2.2. | below | none |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `abbrev_category_axis` | ✓ | — | — | opus-5: countries appear only as codes "AR", "BR", "CA", "YU" beside the points |
| `annotation_callout` | ✓ | ✓ | ✓ | opus-5: boxed note inside plot: "Sources: IAEA Energy and Economic Data Bank 1983 World Bank Atlas"；gpt-5.6-sol: Arrows and labels identify “industrial market economies”, “middle income economies”, and “low income economies”.；gemini-3.1-pro: arrows and text on the right define income economy brackets |
| `axis_title_below_plot` | ✓ | ✓ | — | opus-5: "1981 per capita energy use (GJ)" centred under the bottom tick row；gpt-5.6-sol: “1981 per capita energy use (GJ)” is centered beneath the plot. |
| `inline_series_labels` | ✓ | — | ✓ | opus-5: each dot carries its code above it: "CH", "SE", "US", "JP"；gemini-3.1-pro: country codes like CH and US are printed directly next to their data points |
| `legend_inside_plot` | ✓ | ✓ | ✓ | opus-5: bordered key box drawn over the plot: "AR: ARGENTINA ... YU: YUGOSLAVIA"；gpt-5.6-sol: A boxed AR-to-YU country-code key overlays the lower middle of the plot.；gemini-3.1-pro: a box mapping country abbreviations to full names sits inside the plot area |
| `reference_line` | ✓ | ✓ | — | opus-5: two horizontal rules on the right at about 5000 and 1000 dividing the income bands；gpt-5.6-sol: Two partial horizontal rules divide the right-side income-economy classifications. |
| `rotated_axis_title` | ✓ | ✓ | ✓ | opus-5: "1981 per capita GDP at market prices (US $)" set vertically along the left axis；gpt-5.6-sol: “1981 per capita GDP at market prices (US $)” runs vertically along the left axis.；gemini-3.1-pro: the left y-axis title runs vertically along the axis |
| `unit_in_axis_or_title` | ✓ | ✓ | ✓ | opus-5: units live only in axis titles: "(US $)" and "(GJ)"; ticks are bare numbers；gpt-5.6-sol: Axes read “1981 per capita GDP at market prices (US $)” and “1981 per capita energy use (GJ)”.；gemini-3.1-pro: US $ and GJ are integrated into the respective axis titles |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `income_band_brackets` | opus-5 | 3,4 | double-headed vertical arrows at right spanning y ranges, labelled "Industrial market economies", "middle income economies", "low income economies" |
| `abbreviation_key_box` | opus-5 | 3 | in-plot box maps point codes to full names: "CH: SWITZERLAND", "DE: GERMANY, FEDERAL REPUBLIC OF" |
| `source_box_inside_plot` | opus-5 | 4 | source line boxed inside the plot area rather than printed under the figure |
| `full_frame_plot_box` | opus-5 | — | plot enclosed on all four sides by a rule with ticks drawn inward |
| `abbreviated_scatter_labels_with_lookup` | gpt-5.6-sol | 3 | Points use “CH”, “SE”, and other codes; a boxed country-name lookup sits inside. |
| `source_box_inside_plot` | gpt-5.6-sol | 4 | A boxed “Sources: IAEA Energy and Economic Data Bank” note overlays the upper plot. |
| `caption_heading_below_plot` | gpt-5.6-sol | 4 | “FIG.2.2. Relation of GDP to energy consumption” is printed below the x-axis. |
| `value_range_bracket` | gemini-3.1-pro | 4 | vertical lines with arrows mark specific numeric bands on the right outside edge |
| `abbreviation_mapping_legend` | gemini-3.1-pro | 3 | the legend maps codes to names textually rather than decoding mark colours or shapes |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 17500 | CH、SWITZERLAND、1981 per capita GDP at market prices (US $)、Industrial market economies | CH、1981 per capita GDP at market prices (US $) | CH、1981 per capita GDP at market prices (US $) | CH、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 140 | CH、SWITZERLAND、1981 per capita energy use (GJ)、Industrial market economies | CH、1981 per capita energy use (GJ) | CH、1981 per capita energy use (GJ) | CH、1981 per capita energy use (GJ) | ✗ | ✗ | ✗ | 过 |
| 15000 | SE、SWEDEN、1981 per capita GDP at market prices (US $)、Industrial market economies | SE、1981 per capita GDP at market prices (US $) | SE、1981 per capita GDP at market prices (US $) | SE、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 12800 | US、UNITED STATES OF AMERICA、1981 per capita GDP at market prices (US $)、Industrial market economies | US、1981 per capita GDP at market prices (US $) | US、1981 per capita GDP at market prices (US $) | US、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 310 | US、UNITED STATES OF AMERICA、1981 per capita energy use (GJ)、Industrial market economies | US、1981 per capita energy use (GJ) | US、1981 per capita energy use (GJ) | US、1981 per capita energy use (GJ) | ✗ | ✗ | ✗ | 过 |
| 11500 | CA、CANADA、1981 per capita GDP at market prices (US $)、Industrial market economies | CA、1981 per capita GDP at market prices (US $) | CA、1981 per capita GDP at market prices (US $) | CA、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 10200 | JP、JAPAN、1981 per capita GDP at market prices (US $)、Industrial market economies | JP、1981 per capita GDP at market prices (US $) | JP、1981 per capita GDP at market prices (US $) | JP、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 2600 | AR、ARGENTINA、1981 per capita GDP at market prices (US $)、middle income economies | AR、1981 per capita GDP at market prices (US $) | AR、1981 per capita GDP at market prices (US $) | AR、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 过 |
| 300 | CN、CHINA、1981 per capita GDP at market prices (US $)、low income economies | CA、1981 per capita energy use (GJ) | CN、1981 per capita GDP at market prices (US $) | IN、1981 per capita GDP at market prices (US $) | ✗ | ✗ | ✗ | 没过 |
| 240 | SE、SWEDEN、1981 per capita energy use (GJ)、Industrial market economies | SE、1981 per capita energy use (GJ) | SE、1981 per capita energy use (GJ) | SE、1981 per capita energy use (GJ) | ✗ | ✗ | ✗ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f1` | ["category", "colour_group", "series"] | ["category", "series"] | ["category"] | category × series | opus 与 gpt 都记了「哪一个量」这一段（1981 年的人均能耗 / 人均 GDP），这张图两个量分别画在两根轴上，不说是哪一个就指不到一个图元；gemini 只记国家代码。opus 另记的 colour_group（收入组）在页面上有印出来的名字，但指认一个点用国家代码就够，按 <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 它不是定位所必需的一段。 |
