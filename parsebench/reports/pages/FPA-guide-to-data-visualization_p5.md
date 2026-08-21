# FPA-guide-to-data-visualization_p5

![FPA-guide-to-data-visualization_p5](../../data/pages/FPA-guide-to-data-visualization_p5.png)

## 1 · 三家怎么读这一页

| 页名 | 文档 | 文档级 tags | 抽查点数 | 页面图像 |
|---|---|---|---|---|
| `FPA-guide-to-data-visualization_p5` | FPA-guide-to-data-visualization | untagged | 10 | `parsebench/data/pages/FPA-guide-to-data-visualization_p5.png` |

### 每一家的报告（`report_md`，原样印出）

**opus-5**

> ## 画出来要什么
> 三个独立无编号图并列在右栏,与左栏正文共用一条横向版面带:两个饼图(3 类扇区、值标签写在扇区内、图例竖排在饼右侧,其中一条图例文字换行成五行)和一个水平条形图(5 类,值标签在条外右侧,x 轴 0%–80%,类别标签右对齐且多行换行)。标题为两到三行粗体问句,置于图上方,无图号、无单位短语。最下方一行 `Source: BPM Partners 2014 BPM Pulse Survey` 服务于整块。条形图第四条用深灰,与第三条深蓝几乎同族,只靠色差区分。
> 
> ## 定位一个值难在哪
> `21.2%` 只需一个标签 `Access to more data sources (external)`,但该标签在页面上被拆成三行,且与上一条 `Access to more data sources (internal)` 只差括号里一个词;解析器若丢掉换行或括号,就会与 43.5% 混淆。数值本身已印出,读数无风险。
> 
> ## 不确定的
> 条形图是否有竖网格线(仅见轴线);第一个饼图的图例 `Yes/No/Not sure` 与扇区对应靠颜色推断;三图是否属于同一编号图组无法判断。

**gpt-5.6-sol**

> **画出来要什么**
> 
> 右栏需重建三张无编号单面板图：两张三扇区饼图，扇区内标白色百分比、右侧设色块图例；中间是五条横向条形图，带0%—80%底轴、多行类别标签和条末数值。还需保留左栏并列正文及底部来源。
> 
> **定位一个值难在哪**
> 
> 如24.0%，数值在橙色扇区内，而“Yes”只出现在右侧图例；两者仅靠颜色关联。相比之下，70.6%紧邻“More interactive”条形，定位直接。
> 
> **不确定的**
> 
> 标题换行可能只是版式折行而非真正副标题；底部来源看似服务三图，但位置上也可能只属于最下方饼图。

**gemini-3.1-pro**

> ### 画出来要什么
> 页面采用分栏布局，左侧是大段正文，右侧并排展示了三个图表（两个饼图，一个水平条形图）。饼图需要支持图例放置在图形右侧，并能将数值直接渲染在对应的扇区内部。水平条形图需要支持将分类名称设置在y轴，由于分类文本较长，必须支持多行文本的自动换行，且需要绘制垂直网格线，数值标签需放置在条形的外部右侧。图表采用长问句作为主标题，置于上方，没有使用传统的编号前缀。页面底部需要支持单独的数据源注释行。
> 
> ### 定位一个值难在哪
> 以56.5为例，该数值对应的y轴类别标签“More chart types...”因文本过长而被分成了四行。大多数表格解析工具或OCR在识别此类排版时，极易将其错误切分为多行不相关的独立文本，甚至发生截断，使得最终提取出的键值对残缺，无法用完整的原标签名准确寻址到该数值。
> 
> ### 不确定的
> 图2中的五个条形使用了与图1和图3相似的多种颜色（橙色、红色、深蓝色等），但该图表并没有单独的图例说明。不确定这些颜色是否暗含了与前面图表分类（如“Yes”、“No”）的某种映射关系，还是仅为了视觉上的美观和区分。

### 图表分解

| 模型 | 图序号 | 类型 | 图元数 | 图号 | 标题位置 | 数值印不印 |
|---|---|---|---|---|---|---|
| opus-5 | f1 | pie | 3 | — | above | all |
| opus-5 | f2 | bar | 5 | — | above | all |
| opus-5 | f3 | pie | 3 | — | above | all |
| gpt-5.6-sol | f1 | pie | 3 | — | above | all |
| gpt-5.6-sol | f2 | bar | 5 | — | above | all |
| gpt-5.6-sol | f3 | pie | 3 | — | above | all |
| gemini-3.1-pro | f1 | pie | 3 | — | above | all |
| gemini-3.1-pro | f2 | bar | 5 | — | above | all |
| gemini-3.1-pro | f3 | pie | 3 | — | above | all |

### 组件命中

| key | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 证据原文 |
|---|---|---|---|---|
| `color_encodes_extra_attribute` | ✓ | — | — | opus-5: Single-series bars coloured orange, red, navy, grey, cyan with no legend explaining the colours |
| `horizontal_bars` | ✓ | ✓ | ✓ | opus-5: Categories on the left, bars grow rightwards to the 0%-80% axis；gpt-5.6-sol: Five category bars grow rightward from the 0% baseline.；gemini-3.1-pro: categories sit on the y axis and the bars grow to the right |
| `legend_beside_plot` | ✓ | ✓ | ✓ | opus-5: Three swatch entries stacked in a column right of the pie；gpt-5.6-sol: Three wrapped legend entries form a column to the right of the pie.；gemini-3.1-pro: legend is a column to the right of the pie chart |
| `multi_figure_page` | ✓ | — | ✓ | opus-5: Three separately titled question charts stacked in the right column of one page；gemini-3.1-pro: three distinct figures on the right side of the page |
| `no_value_axis` | ✓ | — | — | opus-5: Pie draws no ticks; numbers readable only from the printed slice labels |
| `side_text_bullets` | ✓ | ✓ | ✓ | opus-5: Body prose column `The trend toward greater use of visualization...` runs beside all three figures；gpt-5.6-sol: Running “Introduction: The Trend” prose occupies a column beside all three charts.；gemini-3.1-pro: a narrow column of body text runs down the left alongside the figures |
| `source_note_lines` | ✓ | ✓ | ✓ | opus-5: `Source: BPM Partners 2014 BPM Pulse Survey` in italics below the third chart；gpt-5.6-sol: “Source: BPM Partners 2014 BPM Pulse Survey” appears beneath the bottom pie.；gemini-3.1-pro: Source: BPM Partners 2014 BPM Pulse Survey at bottom |
| `value_label_inside` | ✓ | ✓ | ✓ | opus-5: `15.3%`, `11.8%`, `72.9%` printed inside the slices；gpt-5.6-sol: “15.3%”, “11.8%”, and “72.9%” are printed inside the slices.；gemini-3.1-pro: 24.0% and other percentages are printed inside the pie slices |
| `value_label_outside` | ✓ | ✓ | ✓ | opus-5: `70.6%`, `56.5%`, `7.1%` printed to the right of each bar end；gpt-5.6-sol: “70.6%”, “56.5%”, “43.5%”, “21.2%”, and “7.1%” sit beyond bar ends.；gemini-3.1-pro: 70.6% and other values are printed to the right of the bars |
| `vgrid_only` | — | — | ✓ | gemini-3.1-pro: vertical grid rules at 20%, 40%, 60%, 80%, with no horizontal lines |
| `wrapped_category_labels` | ✓ | ✓ | ✓ | opus-5: `More chart types (heat chart, fractals, tree map, bubble chart, etc.)` wraps onto four lines；gpt-5.6-sol: Several left-axis categories wrap across two to four lines.；gemini-3.1-pro: category names on the y axis wrap onto up to four lines |

### 词表外的自拟名字

| 名字 | 哪家报的 | affects | 证据原文 |
|---|---|---|---|
| `legend_entry_multiline_wrap` | opus-5 | 3 | `Third-party solution that may access my performance management data` set over five lines in the side legend |
| `question_text_as_title` | opus-5 | 3,4 | Every title is a survey question ending in `?`, e.g. `(select all that apply)` |
| `shared_source_line_for_multiple_figures` | opus-5 | 4 | One `Source:` line under the last chart appears to cover all three figures |
| `unit_in_tick_labels` | gpt-5.6-sol | 2 | Bottom ticks read “0%”, “20%”, “40%”, “60%”, and “80%”. |
| `unnumbered_multi_figure_page` | gpt-5.6-sol | 1,3,4 | Three separately titled charts appear in the right column, none carrying a figure number. |
| `per_category_bar_colors` | gpt-5.6-sol | — | The five single-series bars use five different fills without a legend. |
| `arbitrary_bar_colors` | gemini-3.1-pro | — | each bar has a different color but no legend explains them |

## 2 · 抽查点

值送进了 prompt，标签没有，所以「三家各自预测的键」是预测，右边由 `chart.jsonl` 判分。最后一列是这个点在 `ppdoclayoutv3_lean_qwen` 那次运行里的官方判定。

| 值 | 规则的真实标签 | opus-5 预测的键 | gpt-5.6-sol 预测的键 | gemini-3.1-pro 预测的键 | opus-5 对错 | gpt-5.6-sol 对错 | gemini-3.1-pro 对错 | 失败运行里过没过 |
|---|---|---|---|---|---|---|---|---|
| 24.0 | Yes | Do you require data visualization capabilities beyond standard charts and graphs?、Yes | Yes | Yes | ✓ | ✓ | ✓ | 过 |
| 40.9 | No | Do you require data visualization capabilities beyond standard charts and graphs?、No | No | No | ✓ | ✓ | ✓ | 过 |
| 70.6 | More interactive | More interactive | More interactive | More interactive | ✓ | ✓ | ✓ | 过 |
| 56.5 | More chart types (heat chart, fractals, tree map, bubble chart, etc.) | More chart types (heat chart, fractals, tree map, bubble chart, etc.) | More chart types (heat chart, fractals, tree map, bubble chart, etc.) | More chart types (heat chart, fractals, tree map, bubble chart, etc.) | ✓ | ✓ | ✓ | 过 |
| 43.5 | Access to more data sources (internal) | Access to more data sources (internal) | Access to more data sources (internal) | Access to more data sources (internal) | ✓ | ✓ | ✓ | 过 |
| 21.2 | Access to more data sources (external) | Access to more data sources (external) | Access to more data sources (external) | Access to more data sources (external) | ✓ | ✓ | ✓ | 过 |
| 7.1 | Not sure | Not sure | Not sure | Not sure | ✓ | ✓ | ✓ | 过 |
| 15.3 | Included in performance management solution | Where would you prefer to get these data visualization capabilities from?、Included in performance management solution | Included in performance management solution | Included in performance management solution | ✓ | ✓ | ✓ | 过 |
| 11.8 | Doesn't matter | Where would you prefer to get these data visualization capabilities from?、Doesn't matter | Doesn’t matter | Doesn't matter | ✓ | ✓ | ✓ | 过 |
| 72.9 | Third-party solution that may access my performance management data | Where would you prefer to get these data visualization capabilities from?、Third-party solution that may access my performance management data | Third-party solution that may access my performance management data | Third-party solution that may access my performance management data | ✓ | ✓ | ✓ | 过 |

## 3 · 分歧与裁决

| 量 | opus-5 | gpt-5.6-sol | gemini-3.1-pro | 人工裁决 | 理由 |
|---|---|---|---|---|---|
| `key_roles#f1` | ["series"] | ["category"] | ["series"] | series | <strong>colour_group 的判据</strong>：只由颜色承载、既不是系列也不是类目的<strong>第三个变量</strong>。单独给某一个类目换色（`highlighted_category`）不算；图例里列出的项是 series。 三段选项来自图例，按判据记 series；opus 与 gemini 都这样记，gpt 记成 category。 |
| `key_roles#f3` | ["series"] | ["category"] | ["series"] | series | 同 f1，同一页的另一张。 |
