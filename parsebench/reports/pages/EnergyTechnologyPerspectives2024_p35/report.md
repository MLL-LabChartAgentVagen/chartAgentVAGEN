# EnergyTechnologyPerspectives2024_p35

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| EnergyTechnologyPerspectives2024 | `3d_chart+need_estimate` | 9 | 9 |

页面上方是IEA《Energy Technology Perspectives 2024》的图1.2（左panel为堆积面积图"Investment"、右panel为折线图"Share of GDP"，共用一个底部图例），下方为"Investment in clean energy technology supply chains"一节正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 0.5 | `Investment` · `2005` · `China` | 15% | f1 | the 2005 United States band thickness in the Investment panel | 否 | `Figure 1.2` · `Investment` · `United States` · `2005` · `Trillion USD (2023, MER)` |
| 2 | 2.7 | `Investment` · `2023` · `China` | 15% | f1 | the total stack height at 2005 in the Investment panel (also close to the 2023 China band thickness) | 否 | `Figure 1.2` · `Investment` · `2005` · `Trillion USD (2023, MER)` |
| 3 | 0.6 | `Investment` · `2023` · `United States` | 15% | f1 | the 2005 European Union band thickness in the Investment panel | 否 | `Figure 1.2` · `Investment` · `European Union` · `2005` · `Trillion USD (2023, MER)` |
| 4 | 1.8 | `Investment` · `2023` · `Rest of World` | 15% | f1 | the 2023 Rest of World band (bottom grey band top edge) in the Investment panel | 否 | `Figure 1.2` · `Investment` · `Rest of World` · `2023` · `Trillion USD (2023, MER)` |
| 5 | 8 | `Share of GDP` · `2005` · `China` | 15% | f1 | the China line starting level at 2005 in the Share of GDP panel (~8%); the digit 8 is also the top tick of the Investment axis | 否 | `Figure 1.2` · `Share of GDP` · `China` · `2005` |
| 6 | 15 | `Share of GDP` · `2023` · `China` | 5% | f1 | the China line endpoint at 2023 in the Share of GDP panel, level with the 15% tick | 否 | `Figure 1.2` · `Share of GDP` · `China` · `2023` |
| 7 | 9 | `Share of GDP` · `2005` · `Japan` | 15% | f1 | the Japan line starting level at 2005 in the Share of GDP panel (~9%) | 否 | `Figure 1.2` · `Share of GDP` · `Japan` · `2005` |
| 8 | 7 | `Share of GDP` · `2023` · `Japan` | 15% | f1 | the Japan line trough around 2009-2010 in the Share of GDP panel (below the 10% grid, near 7.5%) | 否 | `Figure 1.2` · `Share of GDP` · `Japan` · `2005` · `2023` |
| 9 | 3 | `Share of GDP` · `2023` · `United States` | 15% | f1 | the flat United States line level in the Share of GDP panel (~3% across 2005-2023) | 否 | `Figure 1.2` · `Share of GDP` · `United States` · `2005` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 9 predicted key sets miss a rule label: 0.5, 2.7, 0.6, 3

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 2 | 6 | 19 | 228 | 无 | Investment: 0, 2, 4, 6, 8; Share of GDP: 0%, 5%, 10%, 15%, 20% |

- **f1** Figure 1.2 / Manufacturing sector investment by country/region, 2005-2023　[图上方]　单位 `Trillion USD (2023, MER)`
  - 来源行：Sources: IEA analysis based on Oxford Economics Limited (2024a).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_area` | 堆叠面积 | f1 | 有 | left panel "Investment" is six filled bands stacked from 0 to ~6.4 over 2005-2023 |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left axis 0-8 trillion USD, right axis 0%-20%; no reading carries across |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single legend row China ... Rest of World below both panels |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Sources: IEA analysis based on Oxford Economics Limited (2024a)." under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend sits under the two plots, above "IEA. CC BY 4.0." |
| `heterogeneous_panel_types` | 同一图号下各面板类型不同 | f1 | 有 | "Investment" panel is stacked areas, "Share of GDP" panel is six unfilled lines |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | bold "Investment" and "Share of GDP" set above each plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | bare ticks 0, 2, 4, 6, 8 scaled only by "Trillion USD (2023, MER)" axis title |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Trillion USD (2023, MER)" set vertically along the left panel's y axis |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | yearly data 2005-2023 but only "2005" and "2023" printed on each x axis |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at tick levels in both panels, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 6 series x 19 yearly points x 2 panels ≈ 228 plotted points |

词表 65 项，本页出现 12 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `key_message_line_below_figure` | f1 | bold blue two-line takeaway "Manufacturing investment has risen most rapidly in China ..." below source line | 该结论句是图的一部分文字，落在source行之下，解析时若被当作正文会丢失图的语义上下文，也可能被误当作图题。 |
| `license_line_below_figure` | f1 | right-aligned "IEA. CC BY 4.0." between legend and the source line | 这一行夹在图例与来源之间，容易被解析器当成图注或数值标签，干扰对source行与表头的定位。 |
| `unit_in_tick_labels` | f1 | right panel ticks printed as "0%, 5%, 10%, 15%, 20%"; no axis title on that panel | 右panel的单位只存在于刻度文字里，读数必须带上%号；表格若只写数字9会与左panel的trillion数混淆。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

左panel刻度间距只有0,2,4,6,8五档，1个trillion约35像素；要把United States的0.5读到5%误差即±0.025，等于不到1像素，而且堆积面积图必须用上下两条边界相减才能得到band厚度，边界线本身有1-2像素粗。右panel五档0%-20%，1%约14像素，Japan谷值7.5%的±0.4%容差也仅5像素，且19个年份只有2005与2023两个刻度，年份位置需在两端之间内插，定位误差直接变成数值误差。相比之下标签只需panel名+系列名+年份三级，表格可以承载。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 通用 | stacked_area 的逐band精度标注（配合 per_panel_axis_range） | 记录字段中为每个mark写入可达精度（band厚度=上下边界之差），而非只给boolean readable | 堆积面积band厚度 vs 顶边累计值两种取值定义下的命中率对比行 |
| P2 | 通用 | panel 维度进入主键（Investment / Share of GDP 单位不同） | 条件行中加入 panel_key，并让单位随panel变化（Trillion USD vs %） | 有/无 panel_key 时同一系列名在两panel间被混淆的比例行 |
| P7 | 一类出版方 | heading 五段拆分：figure_number="Figure 1.2"、title、旋转轴单位 "Trillion USD (2023, MER)"、panel 标题 | 样式字段 heading_placement 与 unit_position（rotated_axis_title / tick_label_percent） | 单位只在旋转轴标题 vs 只在刻度文字（%）两种设置下的数值单位标注正确率行 |
| P3 | 这份文档自己的习惯 | key_message_line_below_figure 与 license_line_below_figure 的版式 | 整页markdown导出时，图题在表上、结论句与"IEA. CC BY 4.0."在表下的相对位置 | 图下多行小字（许可行+来源行+结论句）存在时，标题与表格绑定成功率行 |
| P6 | 一类出版方 | sparse_time_ticks（19点仅两端刻度） | 刻度格式样式维度中的 time tick 密度参数 | 时间刻度密度（全部年份 / 每5年 / 仅首末）对逐年取值命中率的影响行 |
