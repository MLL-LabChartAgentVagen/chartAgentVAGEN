# Economic_and_Market_Report-Full_year-2024_p11

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Economic_and_Market_Report-Full_year-2024 | `untagged` | 10 | 0 |

整页只有一张图：ACEA报告第11页的「Figure 3. Top 10 global car producers」2023/2024分组柱状图，柱上方带灰底同比变化率气泡标注，下方为S&P Global Mobility来源行。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 26,704,000 | `China` · `2024` | 5% | f1 | the China 2024 cyan bar (tallest bar, just above 26.5m) | 否 | `China` · `2024` |
| 2 | 25,384,000 | `China` · `2023` | 5% | f1 | the China 2023 navy bar | 否 | `China` · `2023` |
| 3 | 11,369,000 | `EUROPEAN UNION` · `2024` | 5% | f1 | the EUROPEAN UNION 2024 cyan bar | 否 | `EUROPEAN UNION` · `2024` |
| 4 | 7,345,000 | `United States` · `2024` | 5% | f1 | the United States 2024 cyan bar | 否 | `United States` · `2024` |
| 5 | 7,734,000 | `Japan` · `2023` | 5% | f1 | the Japan 2023 navy bar | 否 | `Japan` · `2023` |
| 6 | 4,902,000 | `India` · `2024` | 5% | f1 | the India 2024 cyan bar | 否 | `India` · `2024` |
| 7 | 3,879,000 | `South Korea` · `2024` | 10% | f1 | the South Korea 2024 cyan bar (the pair is nearly equal, -1.2% box) | 否 | `South Korea` · `2024` |
| 8 | 2,710,000 | `Mexico` · `2024` | 15% | f1 | the Mexico 2024 cyan bar | 否 | `Mexico` · `2024` |
| 9 | 1,899,000 | `Brazil` · `2023` | 20% | f1 | the Brazil 2024 cyan bar | 否 | `Brazil` · `2024` |
| 10 | 931,000 | `Indonesia` · `2024` | 30% | f1 | the Indonesia 2024 cyan bar (shortest bar) | 否 | `Indonesia` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 1,899,000
- 没有估读点，模型却说数值一个都没写——no rule needs estimation, the model says no value is printed

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 2 | 10 | 20 | 无 | 0, 5,000,000, 10,000,000, 15,000,000, 20,000,000, 25,000,000, 30,000,000 |

- **f1** Figure 3. / Top 10 global car producers　[图上方]　（标题里没有单位）
  - 来源行：SOURCE: S&P GLOBAL MOBILITY

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | two bars, dark navy 2023 and cyan 2024, sit side by side in each country slot |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | grey rounded boxes '+5.2%', '-6.2%', '-18.2%' with pointer tails drawn over the plot above each pair |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'SOURCE: S&P GLOBAL MOBILITY' in small print under the plot |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | swatches '2023' and '2024' sit between the title line and the plot area |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | the only printed numbers, the percentage boxes, sit above the bar tops, not on the bars |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country names 'China', 'EUROPEAN UNION' are set vertically, turned 90 degrees under the axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each million tick; no vertical rules in the panel |

词表 65 项，本页出现 7 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `derived_change_callout_per_group` | f1 | boxed '+5.2%' … '-12.2%' above each 2023/2024 pair gives year-on-year change, not either bar's value | 图上唯一印出的数字是派生的同比百分比，10个柱组的绝对产量必须全部靠像素对刻度估读；解析表若只抓这些百分比会与真值（如26,704,000）完全不匹配。 |
| `aggregate_category_in_capitals` | f1 | 'EUROPEAN UNION' set in full capitals among title-case names like 'United States' | 全大写提示该类目是国家集合体而非单国，定位某一条柱时必须逐字照抄'EUROPEAN UNION'作为行名，否则与成员国数据混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

刻度间距为5,000,000，在图上约占90像素，即1像素≈55,000。对China的26,704,000而言5%容差约1.34M（24像素），尚可估读；但Indonesia的931,000容差仅46,550，约不到1个像素，Brazil的1,899,000容差95,000也只有约2像素，Canada/Indonesia两组柱高不足20像素，根本无法在5%内读出。图上唯一印出的数字是灰框里的百分比变化，解析器抓到的是'+5.2%'一类派生值而非产量本身，所以第2步（取值）最致命；第3步只需'China'+'2024'两个键即可定位，相对容易。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 derived_change_callout_per_group（柱组上方只印同比百分比、不印柱值） | 图表样式字段中的标签层：增加'label_content = derived_delta'选项，与 value_label_inside/outside 并列，并在记录中区分派生值与柱值 | 「印出的数字是派生量 vs 印出的数字是柱值本身」对取值命中率的影响一行 |
| P1 | 通用 | P1 的按标记精度：同一图内不同柱的可读精度差两个数量级（26.7M vs 0.93M） | 评分条件行：把 readable 从图级布尔改为按 mark 计算的 pixel_per_unit/容差比 | 「同图内最小柱与最大柱之比 > 20」时逐标记精度阈值 vs 图级阈值的对比行 |
| P7 | 通用 | P7 的标题拆分：'Figure 3.' 编号与 'Top 10 global car producers' 标题分离，且全图无任何单位短语（纵轴仅裸数字 0…30,000,000） | 记录的 heading 字段：number/title/subtitle/unit 四分，允许 unit 为空并标注 placement=above | 「无单位短语、纵轴为裸大数」时导出表格是否需要补写千分位/量级说明一行 |
| P3 | 通用 | rotated_x_ticks 与超长类目名（'EUROPEAN UNION' 竖排占约130像素高） | 布局条件行：类目轴文字旋转90度时的绘图区下留白与标签长度约束 | 「类目标签90度旋转且长度>12字符」对类目名被解析器正确抽取为表头的影响行 |
