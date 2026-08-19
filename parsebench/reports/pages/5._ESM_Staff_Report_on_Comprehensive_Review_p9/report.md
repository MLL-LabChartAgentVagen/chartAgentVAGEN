# 5._ESM_Staff_Report_on_Comprehensive_Review_p9

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 5._ESM_Staff_Report_on_Comprehensive_Review | `need_estimate` | 10 | 10 |

页面上部为Figure 3双轴折线图（欧元区人口年龄中位数与老年抚养比），其余为关于气候相关风险的正文段落、要点列表与脚注。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34.1 | `1984` · `Median age of population (LHS)` | 5% | f1 | the leftmost (1984) point of the blue Median age line | 否 | `Median age of population (LHS)` · `1984` |
| 2 | 50.3 | `1984` · `Age dependency ratio (RHS)` | 5% | f1 | the leftmost (1984) point of the yellow Age dependency ratio line | 否 | `Age dependency ratio (RHS)` · `1984` |
| 3 | 48.0 | `1993` · `Age dependency ratio (RHS)` | 5% | f1 | the yellow line at its trough level near 1993, where it crosses the blue line | 否 | `Age dependency ratio (RHS)` · `1993` |
| 4 | 39.5 | `2002` · `Median age of population (LHS)` | 5% | f1 | the blue Median age line around 2002 | 否 | `Median age of population (LHS)` · `2002` |
| 5 | 49.0 | `2002` · `Age dependency ratio (RHS)` | 5% | f1 | the yellow Age dependency ratio line just before 2005 | 否 | `Age dependency ratio (RHS)` · `2005` |
| 6 | 42.5 | `2011` · `Median age of population (LHS)` | 5% | f1 | the blue Median age line between the 2011 and 2014 ticks | 否 | `Median age of population (LHS)` · `2011` · `2014` |
| 7 | 51.5 | `2011` · `Age dependency ratio (RHS)` | 5% | f1 | the yellow Age dependency ratio line between the 2008 and 2011 ticks | 否 | `Age dependency ratio (RHS)` · `2008` · `2011` |
| 8 | 56.0 | `2020` · `Age dependency ratio (RHS)` | 5% | f1 | the yellow Age dependency ratio line near the 2020 tick | 否 | `Age dependency ratio (RHS)` · `2020` |
| 9 | 45.0 | `2023` · `Median age of population (LHS)` | 5% | f1 | the final (2023) point of the blue Median age line | 否 | `Median age of population (LHS)` · `2023` |
| 10 | 57.0 | `2023` · `Age dependency ratio (RHS)` | 5% | f1 | the final (2023) point of the yellow Age dependency ratio line | 否 | `Age dependency ratio (RHS)` · `2023` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 10 predicted key sets miss a rule label: 49.0

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 2 | 14 | 80 | 无 | 46, 44, 42, 40, 38, 36, 34, 32 (left); 58%, 56%, 54%, 52%, 50%, 48%, 46%, 44% (right) |

- **f1** Figure 3. / Euro area demographic dynamics　[图上方]　（标题里没有单位）
  - 来源行：Source: Eurostat

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 32 to 46, right axis 44% to 58%, series tagged (LHS) and (RHS) |
| `axis_starts_above_zero` | 值轴起点不是零，且没有断轴标记 | f1 | **无** | lowest left tick is 32 and lowest right tick is 44%, no break glyph drawn |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Source: Eurostat' and 'Note: age dependency is measured as the ratio of population aged 0-14 and 65+...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | 'Median age of population (LHS)' and 'Age dependency ratio (RHS)' swatches sit under the x axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript 5, 6, 7 in the body text keyed to footnotes at the page foot |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | lines bend yearly but ticks read 1984, 1987, 1990 ... 2023, every third year |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each left tick; no vertical rules in the plot |

词表 65 项，本页出现 7 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `axis_side_tag_in_series_name` | f1 | legend reads 'Median age of population (LHS)' and 'Age dependency ratio (RHS)' | 读数前必须先由系列名中的(LHS)/(RHS)判断该点应对照左轴32–46还是右轴44%–58%，否则同一像素高度会被读成两个完全不同的数。 |
| `percent_sign_only_on_one_axis` | f1 | right ticks carry '%'; left ticks are bare 32...46 with no unit word anywhere | 标题与轴标题都无单位，左轴数值的量纲只能从系列名'Median age'推断。若表格只写数字会丢失量纲。 题及正无单说明。 单位仅靠刻度%区分两轴。 单侜无单位说明。 单单单。 与与均无单位行。 … |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

两条线各约40个年度点，但x轴只印了1984、1987…2023共14个刻度；42.5和51.5落在2011–2014、2008–2011之间的无标签年份上，表格无法用页面上verbatim的标签唯一指向这一个点。相反，数值本身不难：左轴每格2单位（32→46），5%容差对34.1就是±1.7，接近一整格；右轴每格2%，50.3的容差±2.5超过一格，像素读数完全够。真正卡住的是必须同时给出系列名（含(LHS)/(RHS)才能区分左右轴）与一个页面上并不存在的年份键。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 axis_starts_above_zero 的组合，并要求系列名内带(LHS)/(RHS)轴归属标记（新组件 axis_side_tag_in_series_name） | 条件行中的坐标轴配置字段：允许第二个右轴使用不同单位与不同起点（如32–46对44%–58%），并在series_name模板追加轴归属后缀 | 新增一行“双轴且系列名含轴归属标记 vs 单轴”，检验模型是否会把右轴百分比误读到左轴刻度上 |
| P1 | 一类出版方 | sparse_time_ticks：数据点密于刻度（40个年度点、每3年一个刻度） | 时间轴刻度生成规则：刻度步长与数据步长解耦，作为独立样式字段 | 新增一行“刻度=数据点 vs 刻度每3年”，量化无标签年份点的可寻址率下降 |
| P7 | 这份文档自己的习惯 | 标题块五分（“Figure 3.”独占一行、彩色粗体标题“Euro area demographic dynamics”、无副标题、无单位短语） | 图表标题记录字段：number/title/subtitle/unit分离，并记录placement=above | 新增一行“编号与标题分行 vs 合并一行”，检验导出markdown能否把标题作为表上方的标题级文本保留 |
| P6 | 一类出版方 | 单位仅出现在一侧刻度（右轴带%、左轴裸数字且全图无单位词） | 样式维度中的刻度格式与单位位置字段：允许两轴使用不同的刻度格式化器 | 新增一行“单位在标题 vs 单位仅在单侧刻度 vs 无单位”，检验数值量纲恢复率 |
