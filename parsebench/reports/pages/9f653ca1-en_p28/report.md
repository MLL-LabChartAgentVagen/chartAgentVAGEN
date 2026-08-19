# 9f653ca1-en_p28

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 9f653ca1-en | `need_estimate` | 8 | 8 |

本页上半部为 OECD《经济展望》Figure 1.14 的两个面板（A 修剪均值通胀、B 一年后通胀预期）柱状图叠加三角标记，下半部为“Financial market conditions have improved”一节正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3.3 | `GBR` · `Latest` | 10% | f1 | the GBR 'Latest' bar in Panel A, just above the 3 gridline | 否 | `A. Trimmed mean inflation` · `GBR` · `Latest` |
| 2 | 2.8 | `USA` · `One year ago` | 10% | f1 | the USA 'Latest' bar in Panel A, between the 2 and 3 gridlines | 否 | `A. Trimmed mean inflation` · `USA` · `Latest` |
| 3 | 3.8 | `IND` · `One year ago` | 10% | f1 | the IND 'One year ago' triangle in Panel A, sitting just below the 4 gridline | 否 | `A. Trimmed mean inflation` · `IND` · `One year ago` |
| 4 | 32.0 | `TUR` · `Latest` | 5% | f1 | the TUR 'Latest' bar in Panel A, right of the vertical divider, read on the 0-50 right axis | 否 | `A. Trimmed mean inflation` · `TUR` · `Latest` · `Y-o-y % changes` |
| 5 | 46.0 | `TUR` · `One year ago` | 5% | f1 | the TUR 'One year ago' triangle in Panel A, near the top of the 0-50 right axis | 否 | `A. Trimmed mean inflation` · `TUR` · `One year ago` · `Y-o-y % changes` |
| 6 | 8.0 | `GRC` · `Latest` | 1% | f1 | the GRC 'Latest' bar in Panel B, reaching the top tick 8 | 否 | `B. Inflation expectations, one year ahead` · `GRC` · `Latest` |
| 7 | 4.5 | `USA` · `Latest` | 10% | f1 | the USA 'Latest' bar in Panel B, midway between the 4 and 5 gridlines | 否 | `B. Inflation expectations, one year ahead` · `USA` · `Latest` |
| 8 | 2.8 | `NZL` · `December 2024` | 10% | f1 | a 'December 2024' triangle in the right-hand tail of Panel B (BEL), just below the 3 gridline; neighbouring DEU/FIN triangles are within a few pixels | 否 | `B. Inflation expectations, one year ahead` · `BEL` · `December 2024` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——2 of 8 predicted key sets miss a rule label: 2.8, 2.8
- 标了 dense_marks_100plus，但没有图达到 100 个图元——dense_marks_100plus claimed, densest figure has 62 marks
- 系列数与系列名个数不一致——f1: series=2, 3 names

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `map` | vertical | 2 | 2 | 12 | 62 | 无 | Panel A left: 0, 1, 2, 3, 4, 5; Panel A right: 0, 10, 20, 30, 40, 50; Panel B: 0, 1, 2, 3, 4, 5, 6, 7, 8 |

- **f1** Figure 1.14. / Underlying inflation and short-term inflation expectations have risen in some economies　[图上方]　单位 `Y-o-y % changes`
  - 来源行：Source: Banco de Mexico; Bank of Canada; Bank of Japan; Bank of Korea; Bureau of Economic Analysis; European Central Bank; Eurostat; Federal Reserve Bank of Atlanta; Korean Statistical Information Service; Ministry of Statistics and Program Implementation; Office of National Statistics; Reserve Bank of Australia; Statistics of Japan; Turkish Statistical Institute; University of Michigan; YouGov/Citigroup; and OECD calculations.ationale_other_placeholder":""Continuing:_marks_note""}

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | Panel A has 'Y-o-y % changes' 0-5 on the left and 'Y-o-y % changes' 0-50 on the right for TUR |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | orange triangle markers ('One year ago', 'December 2024') overlaid on the green 'Latest' bars in both panels |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | Panel A tops at 5, Panel B tops at 8; Panel A also carries a 0-50 right scale |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | no shared legend: each panel repeats its own 'Latest' key inside its plot area |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: In Panel A, the latest data are for October 2025...' and 'Source: Banco de Mexico; ...' below the plots |
| `legend_inside_plot` | 图例画在绘图区内部 | f1 | **无** | both legend boxes are drawn over the plot area near the top of each panel |
| `per_panel_legend` | 每个面板各有一个图例 | f1 | 有 | Panel A legend 'Latest / One year ago'; Panel B its own legend 'Latest / December 2024' |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'A. Trimmed mean inflation' and 'B. Inflation expectations, one year ahead' set above each panel |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'StatLink' icon with 'https://stat.link/0bjrsm' under the source block |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Y-o-y % changes' over Panel A axes and '%' over Panel B axis; bars carry bare numbers |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | 'Y-o-y % changes' sits above the top tick '5'/'50'; '%' sits above '8' in Panel B |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | all country codes are set vertically, rotated 90 degrees under the baseline |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | category axis reads GBR, USA, ESP, JPN, CAN, DEU, EA, KOR, ITA, IND, FRA, TUR; GRC, AUS, PRT, NLD, NZL... |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules at each unit tick across both panels, no vertical rules |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | not reached: 12+19 categories x 2 series gives about 62 drawn marks |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the 'EA' bar is blue while all other bars are green, in both Panel A and Panel B |

词表 65 项，本页出现 16 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `split_scale_outlier_category` | f1 | a solid vertical rule separates TUR from FRA in Panel A; TUR bar and triangle are read on the 0-50 right axis | 读 TUR 的两个值必须换用右侧 0-50 刻度，若按左轴 0-5 读会错十倍。 |
| `duplicated_axis_title_both_sides` | f1 | 'Y-o-y % changes' printed twice in Panel A, once above the left axis and once above the right axis | 两轴单位文字相同但量级不同，单位文字无法用于区分左右轴，必须靠分隔线定位。 |
| `series_name_differs_per_panel` | f1 | comparison series is 'One year ago' in Panel A but 'December 2024' in Panel B | 同一图号内三角标记的行名随面板变化，表格行必须带面板名才能唯一定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

没有任何数字印在图上，全部要靠像素对刻度。Panel B 一个单位约33像素，2.8 的5%容差只有0.14即约4.6像素，而三角标记本身宽约10像素、19个类别柱宽仅约20像素，DEU/BEL/FIN 三个约2.2-3.0的三角彼此仅差几像素，取值极易越界。Panel A 的 TUR 更要先辨认竖直分隔线并改用右侧 0,10,...,50 刻度，46.0 的容差±2.3约等于一个刻度的四分之一。类别数在两面板不同（A 为12个含TUR，B 为19个），categories 字段只填了 Panel A 的数目。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新增 split_scale_outlier_category（面板内竖线分隔+右轴单独刻度的离群类别） | 条件行增加“panel 内第二值轴仅服务于末尾若干类别”的样式字段，并在记录中为该类别标注 axis=right | 有/无“离群类别走右轴”这一行，对比模型是否会把 TUR 按左轴读成 3.2 |
| P2 | 一类出版方 | per_panel_legend 与 series_name_differs_per_panel（同图号内比较系列改名） | 图例配置改为按面板独立生成，series 名称允许随 panel 变化 | 共享图例 vs 每面板独立且系列改名，两种条件下行名命中率对比 |
| P4 | 通用 | mixed_marks（三角标记系列叠加在柱上）作为显式家族权重 | 图表家族权重向量中加入“bar + point-marker overlay”组合的抽样比例 | marker-overlay 家族占比 0% vs 15% 时，标记系列值的读取误差 |
| P7 | 一类出版方 | axis_title_above_axis 与重复的双侧轴单位文字 | 样式字段 unit_position 增加“置于顶端刻度上方”并允许左右各写一次 | 单位在轴顶 vs 轴旁旋转标题，两种位置下单位识别正确率 |
| P3 | 通用 | panel_title_per_panel 与图号/标题分离的整页导出 | 整页 markdown 导出时把 'Figure 1.14.' 标题设为标题级、'A./B.' 面板名设为表格上方粗体行 | 面板名在表内一列 vs 表外粗体行，对上下文命中的影响 |
