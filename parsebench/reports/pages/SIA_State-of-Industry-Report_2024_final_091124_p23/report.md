# SIA_State-of-Industry-Report_2024_final_091124_p23

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| SIA_State-of-Industry-Report_2024_final_091124 | `need_estimate` | 10 | 10 |

本页为《2024 State of the U.S. Semiconductor Industry》第23页，主体是文字段落加一幅无编号的面积图「GLOBAL SEMICONDUCTOR SALES ($B)」，展示'01至'24E全球半导体销售额并含红色虚线预测段与框注标签。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 139 | `'01` | 5% | f1 | the '01 point at the left end of the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'01` |
| 2 | 213 | `'04` | 5% | f1 | the '04 point on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'04` |
| 3 | 298 | `'10` | 5% | f1 | the '10 point on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'10` |
| 4 | 336 | `'14` | 5% | f1 | the '14 point on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'14` |
| 5 | 469 | `'18` | 5% | f1 | the '18 peak on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'18` |
| 6 | 412 | `'19` | 5% | f1 | the '19 dip on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'19` |
| 7 | 440 | `'20` | 5% | f1 | the '20 point on the area line | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'20` |
| 8 | 574 | `'22` | 1% | f1 | the '22 point, the highest solid-line point | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'22` |
| 9 | 527 | `'23` | 1% | f1 | the '23 point where the dashed red projection starts | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'23` |
| 10 | 611 | `'24E` | 1% | f1 | the red dot at '24E ending the dashed projection | 否 | `GLOBAL SEMICONDUCTOR SALES ($B)` · `'24E` |

**程序核对**（模型没有看到左半的标签列）：

- 系列数与系列名个数不一致——f1: series=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `area` | vertical | 1 | 2 | 24 | 24 | 无 | 0, 100, 200, 300, 400, 500, 600, 700 |

- **f1** GLOBAL SEMICONDUCTOR SALES ($B)　[图上方]　单位 `($B)`

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | dark blue box reading "-8.2% '22/'23" drawn over the filled area near '23 |
| `shaded_band` | 阴影带标出某个区间（预测期 / 目标区） | f1 | **无** | pale lilac vertical band filling the '23-'24E slot marking the forecast window |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title "GLOBAL SEMICONDUCTOR SALES ($B)"; y axis shows bare 0-700 |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | the "-8.2% '22/'23" label sits inside the filled area, not outside it |
| `nonstandard_time_ticks` | 非 ISO 时间刻度（例：`2022:06` `1Q-2024` `08`） | f1 | **无** | x ticks written as "'01", "'02" ... "'23", "'24E" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at 100..700 across the plot; no vertical grid lines |
| `dashed_line_series` | 用线型（虚 / 实）区分系列 | f1 | **无** | red dashed segment from '23 to a red dot at '24E, distinct from the solid blue line |

词表 65 项，本页出现 7 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `forecast_point_marker` | f1 | single red dot at '24E terminating the dashed projection above the solid area line | 末端预测点与历史实线属不同数据性质，读值时需分辨该点（约611）不是实测面积线的延续。 |
| `area_fill_under_line` | f1 | solid blue line with light purple fill down to the zero baseline across all years | 填充区顶边即数值线，读值须对准顶边而非填充中部，否则误差可达数十$B。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，唯一印出的数字是注释框里的“-8.2% '22/'23”，10个待核值全部要从像素读。y轴刻度间隔100 $B，而5%容差在'19的412上只有约20 $B，即约刻度间距的1/5、在150 dpi下不到10像素；再加上面积填充使线顶边与填充边界难以区分，'19（412）与'20（440）相差仅28 $B，两者极易互换。相比之下行标签很简单：只需“标题+年份”两个键即可唯一定位，故读值是主要瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | dashed_line_series 与新提的 forecast_point_marker（预测段样式） | 样式字段中新增 series_style（solid/dashed）与末端 marker 开关，条件行区分历史段与预测段 | “同一序列内含虚线预测段+端点标记”对末年数值读取正确率的影响行 |
| P6 | 通用 | annotation_callout（图内深色框注百分比） | 记录字段增加 in-plot annotation 文本及其锚定年份，与数据标记区分 | “图内存在非数据文字框”时解析器误将注释当数值的比率行 |
| P7 | 通用 | unit_in_axis_or_title 与无编号标题（figure_number 为空） | 标题块字段拆分为 number/title/subtitle/unit，并允许 number 为空、unit 内嵌于标题括号 | “单位仅存在于标题括号($B)且无图号”时值-单位配对正确率行 |
| P6 | 一类出版方 | shaded_band（'23-'24E 预测窗口浅色带） | 条件行增加 forecast band 区间及其填充透明度 | “预测窗口底色带”是否导致该区间数值被跳过的对照行 |
| P6 | 一类出版方 | sparse/nonstandard 时间刻度（'01…'24E 两位年份） | 刻度格式字段增加 apostrophe two-digit year 与 E 后缀 | “非ISO年份刻度”对行标签匹配（'19 vs 2019）的命中率行 |
