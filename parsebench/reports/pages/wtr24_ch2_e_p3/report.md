# wtr24_ch2_e_p3

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| wtr24_ch2_e | `need_estimate` | 10 | 10 |

世界贸易报告2024第32页：两栏正文加页底一幅带蓝色标题横幅的双轴复合图（柱+折线）Figure B.1，下附Source与Note小字。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 2.7 | `1996` · `Speed of income convergence` | 10% | f1 | the 1996 Speed of income convergence bar | 否 | `Figure B.1:` · `Speed of income convergence` · `1996` |
| 2 | 100 | `1996` · `Trade participation` | 1% | f1 | the 1996 Trade participation line point (index base year) | 否 | `Figure B.1:` · `Trade participation` · `1996` · `Trade participation (100=1996)` |
| 3 | 0.0 | `1998` · `Speed of income convergence` | 1% | f1 | the 1998 Speed of income convergence slot, where no bar is drawn | 否 | `Figure B.1:` · `Speed of income convergence` · `1998` |
| 4 | 4.6 | `2008` · `Speed of income convergence` | 10% | f1 | the 2008 Speed of income convergence bar (its top, read against the left axis between 4 and 5) | 否 | `Figure B.1:` · `Speed of income convergence` · `2008` |
| 5 | 155 | `2008` · `Trade participation` | 5% | f1 | the 2007 Trade participation line point, the series maximum | 否 | `Figure B.1:` · `Trade participation` · `2007` |
| 6 | 7.7 | `2009` · `Speed of income convergence` | 5% | f1 | the 2009 Speed of income convergence bar total, top of the light blue portion | 否 | `Figure B.1:` · `Speed of income convergence` · `2009` |
| 7 | 128 | `2009` · `Trade participation` | 5% | f1 | the 2014 Trade participation line point on the post-2012 decline | 否 | `Figure B.1:` · `Trade participation` · `2014` |
| 8 | 138 | `2010` · `Trade participation` | 10% | f1 | the 2012 Trade participation line point just after the 2011 local peak | 否 | `Figure B.1:` · `Trade participation` · `2012` |
| 9 | -0.2 | `2021` · `Speed of income convergence` | 30% | f1 | the 2021 Speed of income convergence bar, drawn below the zero line | 否 | `Figure B.1:` · `Speed of income convergence` · `2021` |
| 10 | 125 | `2021` · `Trade participation` | 5% | f1 | the 2009 Trade participation line point at the crisis trough | 否 | `Figure B.1:` · `Trade participation` · `2009` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 10 predicted key sets miss a rule label: 155, 128, 138, 125

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 26 | 53 | 无 | left: -1, 0, 1, 2, 3, 4, 5, 6, 7, 8; right: 40, 60, 80, 100, 120, 140, 160 |

- **f1** Figure B.1: / Positive correlation between low- and middle-income economies' convergence speed and trade participation, 1996-2021　[图上方]　单位 `Speed of income convergence (percentage points)`
  - 来源行：Source: Authors' calculations, based on World Bank data on nominal GDP and real GDP per capita and WTO data on trade in goods and commercial services.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | 2009 bar dark blue to ~3.8 then light blue continuing to ~7.7; 2020 bar likewise two-tone |
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 'Speed of income convergence (percentage points)', right axis 'Trade participation (100=1996)' |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | blue bars per year with a green line crossing the same plot area |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | left axis lowest tick '-1'; the 2021 bar hangs just below the zero line |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | Note: 'The light blue fill indicates a contribution of negative growth in high-income economies.' |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Authors' calculations...' and 'Note: The figure displays the evolution over time...' below the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Speed of income convergence' and 'Trade participation' swatches centred under the plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | '(percentage points)' in left axis title; bare numbers -1..8 on the axis itself |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | both axis titles set vertically along the left and right axes |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | body text 'global poverty rate¹' and '(Cerdeiro and Komaromi, 2021).²' |
| `rebased_index_values` | 数值是指数，基期写在标题里（例：`2011 = 100`） | f1 | **无** | right axis title 'Trade participation (100=1996)' |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | year labels 1996...2021 tilted about 45 degrees under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each left-axis tick, no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | 2009 and 2020 bar portions drawn in pale blue against the dark blue of all other years |

词表 65 项，本页出现 14 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `banner_title_block` | f1 | figure number and title set in white on a solid blue band spanning the plot width | 标题在色块横幅内而非普通文字行，解析器可能丢掉标题或把它并入表格外，取值时无法定位图号。 |
| `legend_omits_extra_color` | f1 | pale blue bar fill has no legend entry; only the Note explains it | 7.7与2.2这类含浅蓝段的柱子无法从图例得到名称，行标签只能引用Note文字。 |
| `zero_valued_bar_absent` | f1 | no bar drawn at 1998 between the 1997 and 1999 bars | 0.0这一年在图上没有可测标记，只能靠空槽推断，表格里必须显式写出该年为0。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签（values_printed=none），全部要靠像素对轴读数。左轴刻度间距1个百分点约占30px，2.7的5%容差仅±0.135，即约4px；-0.2与0.0的5%容差是±0.01和0，物理上不可达。右轴刻度每20个指数点（40,60,...,160）约占48px，128的容差±6.4只有约15px，而折线26个点、无标记点，2012与2011峰值相差仅约4px，极易错点。相比之下行标签只需‘系列名+年份’两个键，标题也是清晰横幅，所以卡点在读数精度。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 为浅蓝色段建立 color_encodes_extra_attribute 与 stacked_bar 的组合条件行（同一系列内部分年份才有第二段） | 图形生成条件表的 series/segment 定义字段：允许某一系列仅在部分类别上出现附加着色段，且该段不进图例 | ‘部分类别才有的无图例着色分段’在有/无时的取值准确率对比 |
| P1 | 通用 | negative_values 与近零值（-0.2、0.0）的容差处理，改为按标记可达精度评分 | readable 门控改为 per-mark 精度：以像素/刻度比推导每个标记的可达绝对容差，替代统一5% | ‘\|值\|<1的标记’在绝对容差与相对容差两种评分下的得分差 |
| P7 | 一类出版方 | dual_axis + rebased_index_values（右轴 100=1996）的轴标题与单位字段 | 记录字段拆出 unit_left/unit_right 与 rotated_axis_title 位置，标题块用色块横幅表示 | 双轴且两轴单位不同的图，导出表是否携带各轴单位对读数正确率的影响 |
| P3 | 一类出版方 | 零值类别不绘制标记（1998空槽）的显式记录 | 数据记录层允许 value=0 且不绘柱，并要求导出表仍保留该类别行 | 含零值空槽类别的图在表格中缺行 vs 保留行的检索命中率 |
