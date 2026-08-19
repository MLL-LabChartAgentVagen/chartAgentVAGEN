# article_thebeatjun2025_p22

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| article_thebeatjun2025 | `untagged` | 10 | 0 |

这是Morgan Stanley「The BEAT」2025年6月刊第22页，主题为「Monetary Policy」，左侧是四大央行政策利率的阶梯折线图并叠加一个当前/1个月前/12个月前利率表格，右侧是市场对未来央行利率预期的四条折线图（带全部数值标签）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.27% | `U.S. Federal Reserve` · `3M` | 1% | f2 | the 3M point of the U.S. Federal Reserve line | 是 | `Market Expectations for Future Central Bank Rates` · `U.S. Federal Reserve` · `3M` |
| 2 | 3.54% | `U.S. Federal Reserve` · `1Y` | 1% | f2 | the 1Y point of the U.S. Federal Reserve line | 是 | `Market Expectations for Future Central Bank Rates` · `U.S. Federal Reserve` · `1Y` |
| 3 | 3.50% | `U.S. Federal Reserve` · `3Y` | 1% | f2 | the 3Y point of the U.S. Federal Reserve line | 是 | `Market Expectations for Future Central Bank Rates` · `U.S. Federal Reserve` · `3Y` |
| 4 | 4.11% | `BOE` · `3M` | 1% | f2 | the 3M point of the BOE line | 是 | `Market Expectations for Future Central Bank Rates` · `BOE` · `3M` |
| 5 | 3.98% | `BOE` · `6M` | 1% | f2 | the 6M point of the BOE line | 是 | `Market Expectations for Future Central Bank Rates` · `BOE` · `6M` |
| 6 | 3.68% | `BOE` · `1Y` | 1% | f2 | the 1Y point of the BOE line | 是 | `Market Expectations for Future Central Bank Rates` · `BOE` · `1Y` |
| 7 | 1.91% | `ECB` · `3M` | 1% | f2 | the 3M point of the ECB line | 是 | `Market Expectations for Future Central Bank Rates` · `ECB` · `3M` |
| 8 | 2.17% | `ECB` · `3Y` | 1% | f2 | the 3Y point of the ECB line | 是 | `Market Expectations for Future Central Bank Rates` · `ECB` · `3Y` |
| 9 | 0.55% | `BOJ` · `3M` | 1% | f2 | the 3M point of the BOJ dashed line | 是 | `Market Expectations for Future Central Bank Rates` · `BOJ` · `3M` |
| 10 | 0.99% | `BOJ` · `3Y` | 1% | f2 | the 3Y point of the BOJ dashed line | 是 | `Market Expectations for Future Central Bank Rates` · `BOJ` · `3Y` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 4 | 14 | 420 | 无 | 10%, 9%, 8%, 7%, 6%, 5%, 4%, 3%, 2%, 1%, 0%, (1%) |
| f2 | `line` | vertical | 1 | 4 | 5 | 20 | 全部 | 5.0%, 4.0%, 3.0%, 2.0%, 1.0%, 0.0% |

- **f1** Central Bank Policy Rates　[图上方]　（标题里没有单位）
  - 来源行：Source: Bloomberg, Factset as of 5/31/25. Data provided is for informational use only. See end of report for important additional information. Forecasts/estimates are based on current market conditions, subject to change, and may not necessarily come to pass.
- **f2** Market Expectations for Future Central Bank Rates　[图上方]　（标题里没有单位）
  - 来源行：Source: Bloomberg, Factset as of 5/31/25. Data provided is for informational use only. See end of report for important additional information. Forecasts/estimates are based on current market conditions, subject to change, and may not necessarily come to pass.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | Lowest tick reads "(1%)" and ECB/BOJ lines sit at or just below 0% |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | The rates table is drawn over the top-right of the plot area, covering the 8-10% region |
| `step_line_series` | 阶梯线（水平段 + 垂直跳变），不是直连折线 | f1 | **无** | All four policy-rate lines move in horizontal treads and vertical risers |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | Two titled charts side by side: "Central Bank Policy Rates" and "Market Expectations for Future Central Bank Rates" |
| `source_note_lines` | source / note 行在图下方 | page | 有 | "Source: Bloomberg, Factset as of 5/31/25. Data provided is for informational use only..." under both plots |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | Series names drawn over the plot area, e.g. "BOE" above the grey line near '06 |
| `data_table_as_figure` | 一块带表头的表格当作图收录 | f1 | 有 | Table with headers "Current, 1-Mo. Ago, 12-Mo. Ago" and rows "U.S. Federal Reserve, BOE, BOJ, ECB" |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | Each point labelled beside the marker, e.g. "4.27%" above, "3.54%" below the line |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f2 | 有 | Category axis labelled "3M", "6M", "1Y", "2Y", "3Y" |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | Ticks written as bare two-digit years with apostrophe: "'98", "'00", "'24" |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | Monthly step data but ticks only every two years: '98, '00, '02 ... '24 |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | "BOE", "U.S. Federal Reserve", "ECB", "BOJ" written in colour next to the lines, no legend |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f2 | **无** | "U.S. Federal Reserve", "BOE", "ECB", "BOJ" printed beside each line's left endpoint |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | Four monthly step series spanning '98 to '24, several hundred plotted points |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | BOJ drawn as a blue dashed line while BOE, Fed and ECB are solid |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f2 | **无** | BOJ series drawn dashed blue; other three series solid |

词表 65 项，本页出现 14 项，其中我们画不出来的 9 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `table_overlaid_on_plot` | f1 | Current/1-Mo. Ago/12-Mo. Ago table with banded rows sits inside the chart's upper-right plot area | 表格与折线共享同一图形区，解析时同一图既产生表格行（4行×3列），又产生需从像素读取的折线值，取值必须先判定数字来自表格还是曲线。 |
| `percent_ticks_on_all_labels` | page | Every value tick and label already carries "%": "10%", "0.0%", "4.27%" | 单位直接写在刻度和数值标签里，没有独立单位行，检索时数值字符串必须带百分号才能匹配。 |
| `zebra_striped_table_rows` | f1 | Alternating shaded rows: "U.S. Federal Reserve" and "BOJ" rows tinted grey, BOE/ECB white | 行底色仅作阅读辅助，不编码数值，避免把底色误读为附加变量。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

被评分的10个值全部印在f2上，读数不是障碍（每点都有两位小数标签）；难点在寻址：f2无图例，四个系列名（U.S. Federal Reserve、BOE、ECB、BOJ）只以彩色文字贴在各线左端，解析器若不把颜色/位置还原成系列名，20个点就只剩"3M…3Y"五个列名，4.27%与4.11%都落在3M列而无法区分。另外同名标签（U.S. Federal Reserve、BOE、ECB、BOJ）也出现在f1叠加表格的行名里，且f1表格里有4.50%、4.25%这类同量级数值，一行若缺少图标题"Market Expectations for Future Central Bank Rates"就会与"Central Bank Policy Rates"的表格混淆，因此一个值需要图标题+系列名+期限三重键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P3 | 一类出版方 | inline_series_labels（端点内联系列名，无图例） | 样式条件行：legend_mode 增加 "inline_endpoint" 取值，渲染时把系列名以系列色写在首点或末点旁 | 图例位置消融：legend_below / legend_inside / inline_endpoint 三档下，系列名能否进入表格行头的成功率 |
| new | 这份文档自己的习惯 | 新组件 table_overlaid_on_plot（数据表压在折线图形区内） | 图形记录字段：新增 overlay_table 块（表头、行名、单元格），与折线 series 共存于同一 figure | 同一图内"表格值 vs 曲线值"来源歧义行：有/无叠加表时数值归属判定错误率 |
| P4 | 一类出版方 | step_line_series（阶梯折线） | 折线族样式字段 line_interpolation 增加 "step" 档，并在时间轴上启用月度密点 | 插值方式消融：linear vs step 时，稀疏刻度（每两年一格）下取点年份定位误差 |
| P6 | 通用 | unit_in_axis_or_title 的替代形态：刻度与数值标签自带 %（percent_ticks_on_all_labels） | 刻度格式字段 tick_format：区分 "bare number + unit line" 与 "每个标签带 % 后缀" | 单位位置消融：单位在轴标题 / 单位随每个刻度与数值标签时，检索字符串带不带 % 的命中率 |
| P6 | 一类出版方 | negative_values 与 (1%) 括号负值刻度 | 数值轴条件行：负号呈现方式增加 "parenthesis" 取值，最低刻度可低于 0 | 负值书写消融：-1% 与 (1%) 两种写法下零线以下值的解析正确率 |
