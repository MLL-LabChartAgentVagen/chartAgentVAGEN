# Economic_and_Market_Report-Full_year-2024_p16

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Economic_and_Market_Report-Full_year-2024 | `need_estimate` | 10 | 10 |

ACEA 报告第16页「COMMERCIAL VEHICLES / REGISTRATIONS / Global」正文加一幅堆积柱状图 Figure 4，按七个地区拆分 Vans/Trucks/Buses 新车销量。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4,000,000 | `North America` · `Vans` | 5% | f1 | the North America Vans segment (bar bottom segment, top edge at the 4,000,000 gridline) | 否 | `North America` · `Vans` · `Figure 4.` |
| 2 | 3,000,000 | `Greater China` · `Vans` | 5% | f1 | the Greater China Vans segment, topping just under the 3,000,000 gridline | 否 | `Greater China` · `Vans` · `Figure 4.` |
| 3 | 1,000,000 | `Greater China` · `Trucks` | 5% | f1 | the Greater China Trucks segment (~2.97M to ~4.03M, i.e. about 1,000,000 tall) | 否 | `Greater China` · `Trucks` · `Figure 4.` |
| 4 | 2,500,000 | `Europe` · `Vans` | 5% | f1 | the Europe Vans segment, top edge just under halfway between 2,000,000 and 3,000,000 | 否 | `Europe` · `Vans` · `Figure 4.` |
| 5 | 1,500,000 | `South Asia` · `Vans` | 5% | f1 | the South Asia Vans segment, top edge halfway between 1,000,000 and 2,000,000 | 否 | `South Asia` · `Vans` · `Figure 4.` |
| 6 | 1,100,000 | `South America` · `Vans` | 5% | f1 | the South America Vans segment, top edge slightly above the 1,000,000 gridline | 否 | `South America` · `Vans` · `Figure 4.` |
| 7 | 4000000 | `Vans` · `North America` | 10% | f1 | the North America Vans segment again, unformatted spelling of the same quantity | 否 | `North America` · `Vans` · `Figure 4.` |
| 8 | 1000000 | `Trucks` · `Greater China` | 10% | f1 | the Greater China Trucks segment again, unformatted spelling | 否 | `Greater China` · `Trucks` · `Figure 4.` |
| 9 | 120997 | `Buses` · `Greater China` | 20% | f1 | the Greater China Buses segment; the number itself appears only in the prose ('120,997 units') | 否 | `Greater China` · `Buses` · `Figure 4.` |
| 10 | 96949 | `Buses` · `South Asia` | 20% | f1 | the South Asia Buses segment; number given only in the prose ('96,949 units') | 否 | `South Asia` · `Buses` · `Figure 4.` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 3 | 7 | 21 | 无 | 0, 1,000,000, 2,000,000, 3,000,000, 4,000,000, 5,000,000 |

- **f1** Figure 4. / Global new commercial vehicles and bus sales¹⁰　[图上方]　（标题里没有单位）
  - 来源行：SOURCE: S&P GLOBAL MOBILITY

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each region bar carries Vans, Trucks and Buses segments stacked to the bar total |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'SOURCE: S&P GLOBAL MOBILITY' printed in small type under the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Vans  Trucks  Buses' swatch row sits between the caption and the plot area |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | caption reads 'Global new commercial vehicles and bus sales¹⁰' with footnote 10 at page foot |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text 'Greater China⁹' with '⁹ Includes Mainland China, and Taiwan' at page foot |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | 'North America', 'Greater China', 'Middle East/Africa' set vertically, turned 90 degrees |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis slots are region codes/groupings 'Japan/Korea', 'Middle East/Africa' |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | Buses segments (e.g. 120,997) are hairline slivers at the bar tops, unlabelled |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each million tick, no vertical rules in the panel |

词表 65 项，本页出现 8 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `full_number_thousands_separator_ticks` | f1 | value axis prints '5,000,000 ... 1,000,000, 0' in full digits rather than a scaled unit | 刻度以完整千分位数字书写，读数需与文中「4 million units」这类缩写单位换算，表格里也要保留 4,000,000 这种写法才能匹配。 |
| `unit_absent_on_count_axis` | f1 | no '%', 'units' or scale phrase anywhere on figure; only 'sales' in the caption | 图上没有任何单位短语，读者只能从正文「units」推断计数单位，解析出的表格若无标题就无法确定量纲。 |
| `segment_value_only_in_body_text` | page | '120,997 units', '96,949 units', '60,625', '55,322' appear only in the prose above the figure | 最细的 Buses 分段数值只存在于正文，表格化时必须把正文数字与图上分段对应，否则该值无处可查。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度间距为 1,000,000，全图高度仅约 300 px，1 px 约等于 17,000 辆；而被考核的 Buses 值 120,997 与 96,949 只占约 7 px 与 6 px，5% 容差分别是 ±6,050 与 ±4,847，即不到半个像素，纯靠像素读数根本不可能达到。Vans 段（4,000,000、2,500,000、1,500,000）虽然刚好落在或贴近网格线，尚可读到 5% 内，但整幅图无任何数值标签，Trucks 段还需用上下沿相减，误差叠加。相比之下寻址只需「地区 + 系列」两个键，标题也是加粗彩色的独立行，反而不是瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | thin_segment_label（细分段无标签）与新提的 segment_value_only_in_body_text | 条件行中增加「最小分段占轴长 <2% 且无数值标签」的样式行，并在记录字段里区分 readable_precision（每个 mark 可达精度） | 堆积图中最小分段占比 <2%：对该分段单独统计 5% 命中率，与占比 >10% 的分段对照 |
| P6 | 一类出版方 | unit_absent_on_count_axis 与 full_number_thousands_separator_ticks | 样式字段 tick_format（完整千分位数字 vs 缩写 4M）与 unit_position（无单位／标题内／轴内） | 轴刻度为 5,000,000 式完整数字且全图无单位词时，数值匹配率对比缩写刻度版本 |
| P7 | 通用 | 标题拆分：figure_number 'Figure 4.'、title、上标脚注 ¹⁰ 与缺失的 unit_text | 记录字段把标题拆成 number/title/subtitle/unit 四项，并记录 placement=above 及脚注标记 | 标题带上标脚注且不含单位短语时，导出表格能否携带上下文（标题作为粗体行） |
| P6 | 一类出版方 | rotated_x_ticks（90° 垂直类别标签） | 样式条件行的 x 轴标签角度维度，加入 90° 竖排选项 | 类别标签竖排 90° 时行名解析正确率 vs 水平标签 |
