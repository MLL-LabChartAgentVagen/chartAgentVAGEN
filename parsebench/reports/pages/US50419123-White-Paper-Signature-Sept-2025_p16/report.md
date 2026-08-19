# US50419123-White-Paper-Signature-Sept-2025_p16

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US50419123-White-Paper-Signature-Sept-2025 | `need_estimate` | 10 | 10 |

该页仅含一张图（FIGURE 4），为按成熟度分组的水平分组条形图，展示制造业受访者在数据与集成方面的首要优先事项占比，条上无数值标签，下方另附来源行与指向附录补充数据的链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 28 | `Breaking down organizational silos` · `Very limited` | 5% | f1 | the 'Very limited' bar of 'Breaking down organizational silos' (the 'Preconfigured' bar of the same group is nearly identical length) | 否 | `Breaking down organizational silos` · `Very limited` |
| 2 | 39 | `Accessing partner/channel and ecosystem data` · `Orchestrated` | 5% | f1 | the 'Orchestrated' bar of 'Accessing partner/channel and ecosystem data' | 否 | `Accessing partner/channel and ecosystem data` · `Orchestrated` |
| 3 | 35 | `Integrating offline data/CRM` · `Early stages` | 5% | f1 | the 'Preconfigured' bar of 'Upskilling/reskilling teams' | 否 | `Upskilling/reskilling teams` · `Preconfigured` |
| 4 | 40 | `Addressing cybersecurity concerns` · `Preconfigured` | 5% | f1 | the 'Preconfigured' bar of 'Addressing cybersecurity concerns' | 否 | `Addressing cybersecurity concerns` · `Preconfigured` |
| 5 | 42 | `Offering digitally centric products and services` · `End to end` | 5% | f1 | the 'End to end' bar of 'Offering digitally centric products and services' | 否 | `Offering digitally centric products and services` · `End to end` |
| 6 | 50 | `Upskilling/reskilling teams` · `Very limited` | 5% | f1 | the 'Very limited' bar of 'Upskilling/reskilling teams', the longest light-blue bar | 否 | `Upskilling/reskilling teams` · `Very limited` |
| 7 | 47 | `Using data to create or adopt new business models` · `Orchestrated` | 5% | f1 | the 'Preconfigured' bar of 'Using real-time data and feedback to help drive more business' | 否 | `Using real-time data and feedback to help drive more business` · `Preconfigured` |
| 8 | 54 | `Using real-time data and feedback to help drive more business` · `End to end` | 5% | f1 | the 'End to end' bar of 'Using real-time data and feedback to help drive more business', the longest bar in the figure | 否 | `Using real-time data and feedback to help drive more business` · `End to end` |
| 9 | 52 | `Using real-time data and feedback to help drive more business` · `Orchestrated` | 5% | f1 | the 'Orchestrated' bar of 'Using real-time data and feedback to help drive more business' | 否 | `Using real-time data and feedback to help drive more business` · `Orchestrated` |
| 10 | 21 | `Integrating offline data/CRM` · `Orchestrated` | 5% | f1 | the 'Orchestrated' bar of 'Integrating offline data/CRM', the shortest bar in the figure | 否 | `Integrating offline data/CRM` · `Orchestrated` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 10 predicted key sets miss a rule label: 35, 47

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | horizontal | 1 | 5 | 8 | 40 | 无 | 10%, 20%, 30%, 40%, 50%, 60% |

- **f1** FIGURE 4 / First-Party Data/Integration Priorities by Maturity Level / What are your top priorities around data and integration to drive better manufacturing outcomes?　[图上方]　单位 `(% of respondents)`
  - 来源行：n = 1,514; Source: IDC's Manufacturing Customer Experience Survey, September 2022

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | five bars stacked side by side within each category slot, one per maturity level |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | category names sit at left, bars grow rightward to the 10%-60% axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'n = 1,514; Source: IDC's Manufacturing Customer Experience Survey, September 2022' small print below plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | 'Very limited  Early stages  Preconfigured  End to end  Orchestrated' row between subtitle and plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'For an accessible version of the data in this figure, see Figure 4 Supplemental Data in Appendix 2.' |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | '(% of respondents)' printed under the question line, above the plot |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'Accessing partner/channel and / ecosystem data' and four others wrap onto two lines |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | only vertical rules at 10%, 20% ... 60%; no horizontal grid lines in the panel |

词表 65 项，本页出现 8 项，其中我们画不出来的 4 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `dotted_leader_category_labels` | f1 | each left-hand category label ends in a dotted leader running to the plot's zero baseline | 点线引导使标签与其对应的条形组在视觉上绑定，解析时需把引导线后的空白与标签文本分离，否则行名会带上一串点号而无法与数值配对。 |
| `unlabeled_axis_origin` | f1 | bars start at a heavy black rule at left; first printed tick is '10%', no '0%' label | 零点没有刻度文字，读数必须由10%网格线反推基线位置，任何基线定位偏差都会系统性地整体偏移全部40个条形的读数。 |
| `category_group_whitespace_separator` | f1 | wide blank gaps separate the eight five-bar groups, with no divider rule or label band | 分组仅靠空白区分，靠像素判断某条属于上一组还是下一组时容易错位，从而把数值配到错误的类别行。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上40个条形全部没有数值标签，唯一刻度是每10%一条竖网格线（约99像素/10%），而5%容差在21这个值上只有±1.05个百分点，约等于10像素；再加上零点刻度没有文字，基线只能靠10%线外推，一点基线误差就让所有读数整体偏移。更麻烦的是同组内数值密集：'Breaking down organizational silos'的Very limited与Preconfigured几乎等长（都约28），Early stages约27，像素级差别小于容差窗口，即使读对数字也可能挂到错误的系列上。相比之下寻址只需类别+成熟度两个键，表格容易承载（虽然长类别名换行需拼接）。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | vgrid_only 与 unlabeled_axis_origin（新键）的组合：水平分组条形、仅竖网格、零刻度不标注 | 样式字段中的网格/刻度配置行：允许 value_axis_ticks 省略首个（零）刻度标签，同时强制绘制加粗基线 | 新增一行'零刻度无标签 + 仅竖网格'条件，对比标注零点时的每条读数误差分布 |
| P1 | 通用 | per-mark 可读性：无数值标签的分组条形按条形长度给出可达精度，而非整图一个布尔可读标志 | 记录字段中每个 mark 增加 attainable_precision（由像素/刻度间距推出） | 新增一行'条形长度 <25% 与 >45% 两档下的命中率对比'，检验短条（如21）是否为主要失分源 |
| P3 | 这份文档自己的习惯 | wrapped_category_labels 与新键 dotted_leader_category_labels | 类别轴标签样式行：允许两行换行并在标签尾部加点线引导至绘图区 | 新增一行'类别名换行+点线引导'，衡量行名拼接错误导致的寻址失败率 |
| P7 | 通用 | 标题块五段拆分（FIGURE 4 / 标题 / 问句副标题 / (% of respondents) / 位于绘图区上方） | 图表记录的 heading 字段拆成 number、title、subtitle、unit、placement 五项 | 新增一行'单位只出现在副标题而非轴标题'，检验导出表格是否仍能带上百分比单位 |
| P3 | 一类出版方 | data_link_below_figure（'see Figure 4 Supplemental Data in Appendix 2.'） | 图注区域字段：在 source 行之外增加独立的数据链接行 | 新增一行'图下同时存在来源行与数据链接行'，检验解析器是否把链接文本误当作来源或类别名 |
