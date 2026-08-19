# 2024_Annual_Financial_Review_Upstream_FINAL_p19

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_Annual_Financial_Review_Upstream_FINAL | `need_estimate` | 9 | 9 |

这是一页EIA幻灯片，包含一张横向堆积条形图，比较十家能源公司2024年已探明与未探明储量收购的上游支出（十亿2024美元）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 39 | `Exxon Mobil Corporation` · `proved reserve acquisition` | 5% | f1 | the Exxon Mobil Corporation light-blue (proved reserve acquisition) segment, ending just under the $40 gridline | 否 | `Exxon Mobil Corporation` · `proved reserve acquisition` · `billion 2024 dollars` |
| 2 | 46 | `Exxon Mobil Corporation` · `unproved reserve acquisition` | 5% | f1 | the Exxon Mobil Corporation dark-blue unproved segment, from ~$39 to the bar end near $85 | 否 | `Exxon Mobil Corporation` · `unproved reserve acquisition` · `billion 2024 dollars` |
| 3 | 21 | `Diamondback Energy Inc.` · `proved reserve acquisition` | 5% | f1 | the Diamondback Energy Inc. light-blue proved segment, ending just past $20 | 否 | `Diamondback Energy Inc.` · `proved reserve acquisition` · `billion 2024 dollars` |
| 4 | 16 | `Diamondback Energy Inc.` · `unproved reserve acquisition` | 5% | f1 | the Diamondback Energy Inc. dark-blue unproved segment (bar total ~37); the ConocoPhillips proved segment measures similarly | 否 | `Diamondback Energy Inc.` · `unproved reserve acquisition` · `billion 2024 dollars` |
| 5 | 13 | `ConocoPhillips` · `proved reserve acquisition` | 5% | f1 | the Expand Energy Corporation light-blue proved segment, ending between $0 and $20 | 否 | `Expand Energy Corporation` · `proved reserve acquisition` · `billion 2024 dollars` |
| 6 | 10 | `Expand Energy Corporation` · `proved reserve acquisition` | 5% | f1 | the Occidental Petroleum Corporation light-blue proved segment | 否 | `Occidental Petroleum Corporation` · `proved reserve acquisition` · `billion 2024 dollars` |
| 7 | 9 | `Occidental Petroleum Corporation` · `proved reserve acquisition` | 5% | f1 | the ConocoPhillips dark-blue unproved segment, from ~$16 to the bar end near $25 | 否 | `ConocoPhillips` · `unproved reserve acquisition` · `billion 2024 dollars` |
| 8 | 7 | `Canadian Natural Resources Limited` · `proved reserve acquisition` | 5% | f1 | the Canadian Natural Resources Limited bar, essentially all light-blue proved, ending short of $10 | 否 | `Canadian Natural Resources Limited` · `proved reserve acquisition` · `billion 2024 dollars` |
| 9 | 3 | `California Resources Corporation` · `proved reserve acquisition` | 5% | f1 | the California Resources Corporation light-blue proved segment, the shortest bar on the chart | 否 | `California Resources Corporation` · `proved reserve acquisition` · `billion 2024 dollars` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 9 predicted key sets miss a rule label: 13, 10, 9

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | horizontal | 1 | 2 | 10 | 20 | 无 | $0, $20, $40, $60, $80, $100 |

- **f1** Upstream costs incurred for select energy companies　[图上方]　单位 `billion 2024 dollars`
  - 来源行：Data source: Evaluate Energy

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each company row is one bar of a light-blue then a darker-blue segment, total is bar length |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | company names sit on the y axis; bars grow rightward to the $0-$100 axis below |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Data source: Evaluate Energy" in small print below the plot |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | "proved reserve acquisition" / "unproved reserve acquisition" set as a right-hand column level with the bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "billion 2024 dollars" printed under the bold heading; axis shows only $0...$100 |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | vertical rules at $0, $20, $40, $60, $80, $100; no horizontal rules in the plot |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `color_text_legend_no_swatch` | f1 | legend entries are just the series names typed in the light and dark blue fill colours, no key swatches | 读者必须靠文字颜色与条段颜色匹配来确定哪个段是proved、哪个是unproved，缺少色块会让系列归属易错。 |
| `currency_prefixed_axis_ticks` | f1 | value axis reads "$0, $20, $40, $60, $80, $100" with a dollar sign on every tick | 刻度自带$符号但单位（十亿2024美元）在标题行，读数时要把两处信息合起来才知道量级。 |
| `slide_sentence_headline` | page | blue two-line takeaway sentence "Ten companies accounted for nearly 90% ..." above the chart's bold heading | 图的真正标题是加粗那行，蓝色长句是结论句；解析时若误取结论句作标题，行标签的上下文就错位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，刻度间隔$20约140像素（每美元约7像素），小段的5%容差极小：3的容差是±0.15（约1像素），7是±0.35（2.5像素），9、10也只有3-4像素余量；而且unproved段必须用堆积末端减去proved末端两次读数相减，误差叠加。相比之下行标签只需“公司名+系列名”两个键，表格容易承载，所以卡点在像素读数精度。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | P1式的按段可达精度：把细堆积段（如3、7）标记为低精度目标而非布尔可读 | 记录字段中为每个mark加attainable_tolerance，条件行按段长/像素长度分档 | 新增“堆积段像素长度<30px”一行，对比整段与细段的读数命中率 |
| P6 | 一类出版方 | currency_prefixed_axis_ticks（刻度格式带$前缀）与单位位置分离 | style字段的tick_format与unit_position两项，条件行加“刻度带货币符号且单位在副标题” | 新增“刻度$前缀 + 单位仅在标题行”一行，检验单位是否被正确附加到数值 |
| P7 | 这份文档自己的习惯 | P7的标题拆分：区分蓝色结论句、加粗小标题与单位行 | heading记录字段（takeaway句/title/unit_text）及placement=above | 新增“存在结论式大标题 + 独立加粗图题”一行，测试标题字段抽取的正确率 |
| new | 这份文档自己的习惯 | color_text_legend_no_swatch（无色块、仅彩色文字的侧置图例） | legend样式字段增加swatch=false且position=beside | 新增“图例无色块”一行，考察系列名与条段颜色的绑定是否仍成立 |
