# EnergyTechnologyPerspectives2024_p50

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| EnergyTechnologyPerspectives2024 | `need_estimate` | 10 | 10 |

本页为IEA《Energy Technology Perspectives 2024》第48页，主体是图1.12（上下两个未命名面板的分组柱状图，含100%“Local demand”参考线）加注释与一段正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 185 | `Solar PV modules` · `China` | 5% | f1 | China bar in 'Solar PV modules', upper panel | 否 | `Solar PV modules` · `China` |
| 2 | 12 | `Solar PV modules` · `United States` | 20% | f1 | United States bar in 'Solar PV modules', upper panel | 否 | `Solar PV modules` · `United States` |
| 3 | 114 | `Wind nacelles` · `European Union` | 5% | f1 | China bar in 'ICE cars', upper panel | 否 | `ICE cars` · `China` |
| 4 | 67 | `Battery cells` · `United States` | 5% | f1 | European Union bar in 'Heat pumps', upper panel (US 'Battery cells' bar sits at a similar height) | 否 | `Heat pumps` · `European Union` |
| 5 | 136 | `Heat pumps` · `China` | 5% | f1 | China bar in 'Heat pumps', upper panel | 否 | `Heat pumps` · `China` |
| 6 | 102 | `Electrolysers` · `United States` | 5% | f1 | China bar in 'Aluminium', lower panel | 否 | `Aluminium` · `China` |
| 7 | 108 | `Alumina` · `European Union` | 5% | f1 | China bar in 'Fertilisers', lower panel (China 'Steel' bar is nearly identical) | 否 | `Fertilisers` · `China` |
| 8 | 55 | `Aluminium` · `United States` | 5% | f1 | United States bar in 'Aluminium', lower panel | 否 | `Aluminium` · `United States` |
| 9 | 112 | `Steel` · `China` | 5% | f1 | China bar in 'Wind nacelles', upper panel | 否 | `Wind nacelles` · `China` |
| 10 | 79 | `Fertilisers` · `European Union` | 5% | f1 | European Union bar in 'Ammonia', lower panel | 否 | `Ammonia` · `European Union` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——6 of 10 predicted key sets miss a rule label: 114, 67, 102, 108, 112, 79
- 面板数与面板名个数不一致——f1: panels=2, 0 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 2 | 4 | 7 | 41 | 无 | upper panel: 0%, 50%, 100%, 150%, 200%; lower panel: 0%, 50%, 100%, 150% |

- **f1** Figure 1.12 / Production of selected clean energy technologies and materials relative to / domestic demand by country/region, 2023　[图上方]　（标题里没有单位）

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars (red, blue, green) side by side in every category slot such as 'Wind nacelles' |
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a green horizontal rule drawn at 100% across both panels, legend entry 'Local demand' |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | upper axis tops at 200%, lower axis tops at 150% |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | single legend 'China / European Union / United States / Local demand' below both panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two stacked panels of the same grouped-bar chart, technologies above, materials below |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Notes: Battery cells are for both electric vehicles and stationary storage. Steel includes crude steel...' |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend row sits under the lower panel's category axis, outside the plot |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'Solar PV modules' set on two lines in its axis cell |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at 50%/100%/150%/200%, no vertical grid inside the plots |

词表 65 项，本页出现 9 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `boxed_category_axis_cells` | f1 | category names sit in a bordered row of cells with vertical dividers between 'Battery cells' and 'Electric cars' | 类目轴被画成表格式方格，取值时须按方格边界而非刻度线分组，容易把相邻类目的柱子归错列。 |
| `unnamed_panels_distinguished_by_categories` | f1 | two panels carry no titles; only the category sets (technologies vs Alumina…Fertilisers) tell them apart | 无面板名意味着表格行只能用类目+系列定位，读者必须靠类目集合推断所属面板与其0–200%/0–150%量程。 |
| `takeaway_caption_below_figure` | f1 | bold blue line under notes: 'China is a net exporter of key clean energy technologies, while the European Union...' | 结论句在图下方且加粗，读数时的语义上下文（谁净出口/净进口）不在标题内，需另行抓取。 |
| `license_credit_line_below_plot` | f1 | right-aligned 'IEA. CC BY 4.0.' between the legend and the notes line | 该行既非来源也非数据链接，解析时易被误当作Source行而污染表格上下文。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上一个数字都没印，全部要靠像素对刻度。上面板刻度间隔50个百分点约占63像素，即1像素≈0.8个百分点：读185时5%容差有±9.3点余量，问题不大；但读12时5%容差只有±0.6点，不到1像素，实际不可能落在容差内；同理55与Aluminium的美国柱（约53）差约4%，已在容差边缘。再加上China 'Steel'（约108）与China 'Fertilisers'（约108）、EU 'Heat pumps'（约66.7）与US 'Battery cells'（约68）几乎等高，同一读数可以对应两个不同标记，取值本身而非标签成为最大瓶颈。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_axis_range 与新组件 unnamed_panels_distinguished_by_categories | 条件行中的面板设置：允许两面板量程不同（0–200% / 0–150%）且不写面板标题，记录字段增加 panel_key 由类目集合推断 | “面板无标题+各面板独立量程”对比“面板有标题+共用量程”，看 panel_key 缺失时行定位错误率 |
| P1 | 通用 | P1 精度分级：把每个标记的可达精度按柱高与刻度像素密度打分 | 评分侧 readable 门限，改为按 value/tick-spacing 计算每柱容差（如12%柱容差0.6点<1像素判为不可读） | “小值柱（<20%）计入评分”对比“仅评>20%的柱”，量化低幅值标记对总分的拖累 |
| P6 | 一类出版方 | reference_line 作为独立图例项（'Local demand' 以线形色块与柱形色块并列） | 样式字段：图例中混入线形样例的参考线系列，位置为 legend_below_plot | “参考线带图例项”对比“无图例参考线”，检验解析是否把参考线误建成第4个柱系列 |
| P3 | 这份文档自己的习惯 | takeaway_caption_below_figure 与 license_credit_line_below_plot | 整页导出模板：标题块在表上、结论句与授权行在表下的相对位置 | “图下加粗结论句参与上下文匹配”对比“仅用标题匹配”，看上下文命中率变化 |
