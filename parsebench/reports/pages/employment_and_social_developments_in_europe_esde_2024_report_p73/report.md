# employment_and_social_developments_in_europe_esde_2024_report_p73

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| employment_and_social_developments_in_europe_esde_2024_report | `need_estimate` | 10 | 10 |

本页为报告第77页，正文讨论幼儿教育与保育（ECEC）参与率，中部嵌入 Box 3.2 内的 Chart 1——按成员国代码排列的堆叠柱状图，显示为达成2030年巴塞罗那目标所需的年度额外投资（占GDP%）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.055 | `EU` · `Additional spending needed to reach the 2030 country specific Barcelona target for children below 3` | 10% | f1 | the EU dark-blue lower segment (children below 3) | 否 | `Chart 1` · `EU` · `Additional spending  needed to reach the 2030 country specific Barcelona target for children below 3` |
| 2 | 0.030 | `EU` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` | 20% | f1 | the CZ dark-blue lower segment (children below 3) | 否 | `Chart 1` · `CZ` · `Additional spending  needed to reach the 2030 country specific Barcelona target for children below 3` |
| 3 | 0.155 | `DE` · `Additional spending needed to reach the 2030 country specific Barcelona target for children below 3` | 10% | f1 | the DE dark-blue lower segment (children below 3) | 否 | `Chart 1` · `DE` · `Additional spending  needed to reach the 2030 country specific Barcelona target for children below 3` |
| 4 | 0.145 | `EL` · `Additional spending needed to reach the 2030 country specific Barcelona target for children below 3` | 10% | f1 | the HR green segment (children from 3 to CSA), bar top ~0.15 over a near-zero blue base | 否 | `Chart 1` · `HR` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` |
| 5 | 0.135 | `EL` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` | 10% | f1 | the EL dark-blue lower segment (children below 3) | 否 | `Chart 1` · `EL` · `Additional spending  needed to reach the 2030 country specific Barcelona target for children below 3` |
| 6 | 0.165 | `PL` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` | 10% | f1 | the PL green segment (children from 3 to CSA), from ~0.04 up to the bar top ~0.205 | 否 | `Chart 1` · `PL` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` |
| 7 | 0.0950 | `RO` · `Additional spending needed to reach the 2030 country specific Barcelona target for children below 3` | 5% | f1 | the CZ green segment (children from 3 to CSA), from ~0.03 up to the bar top ~0.125 | 否 | `Chart 1` · `CZ` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` |
| 8 | 0.125 | `RO` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` | 10% | f1 | the CZ bar total, green segment top edge at ~0.125 | 否 | `Chart 1` · `CZ` · `Yearly additional investment in ECEC needed to meet the 2030 Barcelona targets (% of GDP), by Barcelona targets` |
| 9 | 0.095 | `BG` · `Additional spending needed to reach the 2030 country specific Barcelona target for children below 3` | 10% | f1 | the SK green segment (children from 3 to CSA), bar top ~0.10 over a very small blue base | 否 | `Chart 1` · `SK` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` |
| 10 | 0.125 | `CZ` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` | 10% | f1 | the RO green segment (children from 3 to CSA), from ~0.10 up to the bar top ~0.225 | 否 | `Chart 1` · `RO` · `Additional spending needed to reach the 2030 Barcelona target for children from 3 to CSA` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 0.030, 0.145, 0.0950, 0.125, 0.095, 0.125

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `stacked_bar` | vertical | 1 | 2 | 28 | 43 | 无 | 0.0%, 0.1%, 0.2%, 0.3% |

- **f1** Chart 1 / Additional investment needs in ECEC vary by Member State / Yearly additional investment in ECEC needed to meet the 2030 Barcelona targets (% of GDP), by Barcelona targets　[图上方]　单位 `(% of GDP)`
  - 来源行：Source:  DG EMPL calculations based on Eurostat data.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f1 | 有 | each country bar has a dark blue lower segment and a green upper segment, e.g. DE, EL, PL |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Source:  DG EMPL calculations based on Eurostat data." printed below the chart frame |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | two legend rows with green and blue squares sit under the category axis, inside the chart frame |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle reads "...needed to meet the 2030 Barcelona targets (% of GDP), by Barcelona targets" |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | x axis reads "EU BE BG CZ DK DE EE IE EL ES FR HR IT CY LV LT LU HU MT NL AT PL PT RO SI SK FI SE" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 0.1%, 0.2%, 0.3% across the plot; no vertical rules |

词表 65 项，本页出现 6 项，其中我们画不出来的 1 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_length_category_no_mark` | f1 | BE, ES, NL, SI, SE keep axis slots but no bar is drawn; text says "ranging from 0%" | 这些国家在轴上占位但没有任何可读的图形，取值只能判为0，表格若省略这些行会与图不一致。 |
| `boxed_feature_local_figure_numbering` | f1 | chart is titled "Chart 1" inside the tinted "Box 3.2: Future investment needs in Early Childhood Education and Care" panel | 图号在框内独立编号（Chart 1 而非 Chart 3.x），寻址时必须连同 Box 3.2 才能唯一定位该图。 |
| `cumulative_top_only_readable` | f1 | no value labels; only the blue/green boundary and bar top are visible, e.g. RO boundary ~0.10, top ~0.225 | 绿色分段的数值必须用柱顶减去蓝段得到，读数误差叠加，5%容差几乎不可达。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

纵轴只有 0.0%、0.1%、0.2%、0.3% 四个刻度，0.1% 约占 90 像素，即 1 像素≈0.001。待核值中 0.030 的 5% 容差仅 ±0.0015，约合 1.5 像素；0.055 的容差 ±0.0028 也不到 3 像素，且图上无任何数值标签。更糟的是绿色分段（0.145、0.165、0.0950、0.125）必须由柱顶减去蓝段得到，两次像素读数误差叠加后几乎不可能落在 5% 内；相比之下寻址只需“国家代码 + 图例长名”两个键，表格可承载，因此瓶颈在取值本身。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | 新组件 cumulative_top_only_readable（堆叠分段仅能由累积柱顶相减得到） | 记录字段：为堆叠柱增加 segment_value 与 cumulative_top 两种可读性标注，并按分段厚度给出可达精度 | “堆叠分段值 vs 累积柱顶值”两种读数目标下的命中率对比行 |
| P6 | 一类出版方 | 新组件 zero_length_category_no_mark（BE、ES、NL、SI、SE 无柱） | 条件行：允许类别值为 0 且不绘制任何图形，同时保留轴标签 | 含零值空槽类别 vs 全非零类别的数值/标签配对准确率行 |
| P7 | 一类出版方 | 新组件 boxed_feature_local_figure_numbering（Box 3.2 内的 “Chart 1”） | 标题字段：figure_number 与所属专栏（Box）标题分开存储，并记录框内相对位置 | 图号为文档级（Chart 3.2）与专栏级（Box 3.2 / Chart 1）时上下文匹配成功率行 |
| P3 | 一类出版方 | abbrev_category_axis 与超长图例名共同构成的寻址键组合 | 样式字段：类别用两字母代码、系列名超过 80 字符时的图例换行与表头写法 | 两字母代码类别 + 长系列名 vs 全称类别 + 短系列名的行寻址成功率行 |
