# semiconductor_sector_study_p22

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| semiconductor_sector_study | `need_estimate` | 7 | 7 |

这一页是报告第4章"Investment"的开头，正文介绍英国半导体公司融资总额，并附有唯一一张图 Figure 4.1 – Latest Fundraisings（按年份堆叠的融资额柱状图）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | `2007` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 20% | f1 | the 2013 bar total, a short stack just above 0M | 否 | `Figure 4.1 – Latest Fundraisings` · `2013` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` |
| 2 | 0 | `2016` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 10% | f1 | one of the hairline bars in the 2010, 2016 or 2018 slot, indistinguishable at this scale | 否 | `Figure 4.1 – Latest Fundraisings` · `2016` |
| 3 | 23 | `2017` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 10% | f1 | the 2017 bar total, topping just above the 20M gridline | 否 | `Figure 4.1 – Latest Fundraisings` · `2017` |
| 4 | 189 | `2020` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 5% | f1 | the 2020 bar total, topping between 180M and 200M | 否 | `Figure 4.1 – Latest Fundraisings` · `2020` |
| 5 | 22 | `2021` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 10% | f1 | the 2021 bar total, topping just above 20M | 否 | `Figure 4.1 – Latest Fundraisings` · `2021` |
| 6 | 84 | `2022` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 5% | f1 | the 2022 bar total, topping just above 80M | 否 | `Figure 4.1 – Latest Fundraisings` · `2022` |
| 7 | 218 | `2023` · `Fundraisings - Amount received by the company in its latest fundraising (GBP)` | 5% | f1 | the 2023 bar total, topping just under 220M | 否 | `Figure 4.1 – Latest Fundraisings` · `2023` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——7 of 7 predicted key sets miss a rule label: 2, 0, 23, 189, 22, 84
- 规则需要的键比模型报出的图能提供的多——rules need 2 keys, the richest figure offers 1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 1 | 11 | 45 | 无 | 0M, 20M, 40M, 60M, 80M, 100M, 120M, 140M, 160M, 180M, 200M, 220M |

- **f1** Figure 4.1 / Latest Fundraisings　[图上方]　单位 `Fundraisings - Amount received by the company in its latest fundraising (GBP)`
  - 来源行：Source: Beauhurst (all latest fundraisings, 2007 - 2023)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each teal bar is cut by thin white rules, e.g. the 2023 bar shows ~10 segments |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source: Beauhurst (all latest fundraisings, 2007 - 2023)" printed under the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | ticks read "220M", "200M"; only the rotated axis title supplies "(GBP)" |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Fundraisings - Amount received by the company in its latest fundraising (GBP)" set vertically along the y axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text reads "fundraisings\u02e3\u2071\u2071" with a superscript roman-numeral marker above the figure |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each 20M tick across the panel, no vertical rules |

词表 65 项，本页出现 6 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `anonymous_stack_segments` | f1 | bars are divided into many segments but no legend, colour key or segment label appears anywhere | 每个分段代表一家公司却无任何标签，读者只能读出年度总高度，无法为任一分段取值。 |
| `gapped_year_categories` | f1 | x ticks jump 2007, 2010, 2013, 2016, then 2017, 2018, 2019 with equal slot widths | 轴上年份不等距跳跃，柱间距离不代表时间距离，定位某年必须靠刻度文字而非位置推算。 |
| `near_zero_bar` | f1 | the 2010, 2016 and 2018 slots show only a hairline of teal on the 0M baseline | 这些柱在20M刻度间距下高度不足1像素，数值只能判为接近0，无法满足5%容差。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度每格20M、约60像素，5%容差在小值上完全不可达："2"要求±0.1M（约0.3像素），"0"所在的2010/2016/2018柱只有一条发丝般的填色，根本分不清是0还是1M；"23"要求±1.15M也只有3像素余量。同时图上没有任何数值标签，堆叠分段又无图例，所以年度总高度必须从像素反推——取值本身而非表头结构是主要障碍。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| new | 一类出版方 | 新组件 anonymous_stack_segments（无图例、无标签的堆叠分段） | 条件行中的 stacked_bar 样式字段增加"segment_labeled=false / legend=none"选项，记录字段只保留柱总计 | "堆叠柱有图例 vs 分段完全匿名"一行，比较模型是否只输出总计而不臆造分段名 |
| P6 | 一类出版方 | 新组件 gapped_year_categories（时间轴跳过无数据年份且等距排布） | 类别轴生成器的时间刻度字段，允许非连续年份序列 | "连续年度刻度 vs 缺年等距刻度"一行，检验按刻度文字而非位置对齐取值 |
| P7 | 通用 | 组件 rotated_axis_title 与 unit_in_axis_or_title 的组合（长句式旋转轴标题内含 (GBP)，刻度带 M 后缀） | 标题/单位样式字段：单位位置=旋转轴标题，刻度后缀=M | "单位在标题 vs 单位在旋转轴标题且刻度带缩写后缀"一行，检验导出表格是否补回 GBP 百万量纲 |
| P1 | 通用 | 新组件 near_zero_bar（亚像素高度的柱） | readable 判定改为按单个 mark 给出可达精度，小于一定像素高度的柱标为不可读 | "全图统一可读 vs 按 mark 标注可达精度"一行，使近零柱不再计入取值评分 |
