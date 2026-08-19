# WEF_The_Global_Public_Impact_of_GovTech_2025_p29

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| WEF_The_Global_Public_Impact_of_GovTech_2025 | `untagged` | 4 | 0 |

这是报告附录页，上半为A2国家案例链接与A3方法论说明文字，下半为Figure 5——两个并列环形图（2024与2034）展示四个部门IT支出（十亿美元），带虚线放大连接与共享图例。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 670 | `Public sector` · `2024` | 1% | f1 | the 2024 donut's Public sector segment, labelled $670 | 是 | `2024` · `Public sector` |
| 2 | 220 | `Education` · `2034` | 1% | f1 | the 2034 donut's Education segment, labelled $220 | 是 | `2034` · `Education` |
| 3 | 170 | `Healthcare and life science` · `2034` | 1% | f1 | the 2034 donut's Healthcare and life science segment, labelled $170 | 是 | `2034` · `Healthcare and life science` |
| 4 | 40 | `Transport` · `2024` | 1% | f1 | the 2024 donut's Transport segment, labelled $40 | 是 | `2024` · `Transport` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `donut` | na | 2 | 4 | 4 | 8 | 全部 | （不画值轴） |

- **f1** FIGURE 5 / IT spending in various sectors (in $ billions in 2024 and 2034) with an estimate growth rate of 8% per annum　[图上方]　单位 `in $ billions in 2024 and 2034`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | donuts have no axis; only printed labels $670, $90, $70, $40, $1,570, $220, $170, $70 |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend below governs both the 2024 and 2034 donuts |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two donut panels of identical construction, labelled 2024 and 2034 |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | pill-shaped legend row 'Public sector Education Healthcare and life science Transport' under both donuts |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | '2024' and '2034' set large inside each donut hole |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | two-column methodology text 'a. Determination of sector focus' 'b. Projecting IT spending' beside body prose above figure |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads 'IT spending in various sectors (in $ billions in 2024 and 2034)' |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | '(see Figure 5).13,14' superscript footnote digits in the methodology text |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | $670, $90, $70, $40 printed on the coloured ring segments themselves |
| `thin_segment_label` | 窄分段里的数值标签互相挤压或外移 | f1 | **无** | '$40' and '$70' labels sit on very narrow cyan/orange arcs, pushed to the ring edge |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | whole figure band sits on a light grey-blue tinted background across the page width |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `panel_zoom_connector` | f1 | dashed lines and grey wedge join the smaller 2024 donut to the larger 2034 donut | 虚线放大连接暗示两个面板尺寸不同且成比例，读者须知面积/直径本身编码总量，不能把两图当同尺度环图直接比较。 |
| `panel_size_encodes_total` | f1 | 2034 donut drawn markedly larger than 2024 donut, same four sectors | 面板半径承载总额信息，取值时必须先绑定面板（2024/2034），否则同为'$70'的两个扇段无法区分。 |
| `duplicate_value_across_panels` | f1 | '$70' appears in both donuts: Healthcare 2024 and Transport 2034 | 同一数字在两面板重复出现，表格行必须同时含年份与部门标签才能唯一定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在环上（$670、$220、$170、$40），无需按像素读取，第2步不构成障碍；难点在标签寻址：图中唯一的部门名只出现在底部共享图例，颜色是唯一连接扇段与部门的通道，而年份只写在环心（2024/2034）。要唯一定位'$70'必须同时给出年份与部门两个键，而'$70'在两个环里各出现一次；解析器若把两环并成一列或丢掉颜色—图例映射，就无法把220与170分别绑到Education与Healthcare and life science。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | 新增 panel_size_encodes_total / panel_zoom_connector 类构造 | 图形生成条件行中的 donut 面板设置字段：允许各面板半径按总量缩放并绘制虚线放大连接 | 环形图多面板：等径 vs 半径编码总量（含虚线连接）两种条件下的取值正确率对比 |
| P3 | 通用 | legend_below_plot 与颜色→类别映射的记录字段 | 记录（record）中把扇段的 series 标签强制写入表格行，而非仅靠图例颜色 | 仅图例携带类别名 vs 扇段旁直接内联标注两种条件下的标签寻址成功率 |
| P7 | 通用 | 标题五段拆分（FIGURE 5 / 标题 / 单位短语 'in $ billions'） | P7 的标题字段：单位嵌在标题括号内而非独立副标题的样式选项 | 单位在标题括号内 vs 独立单位行时，导出表格是否保留 $ billions 尺度 |
| P6 | 一类出版方 | thin_segment_label（窄扇段标签外移/贴边） | 样式字段：饼/环图 value-label 放置策略（inside / edge / leader line） | 最小扇段占比 <5% 时标签放置策略对数值可读性的影响行 |
