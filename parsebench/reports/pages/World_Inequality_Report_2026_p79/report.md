# World_Inequality_Report_2026_p79

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| World_Inequality_Report_2026 | `3d_chart+need_estimate` | 10 | 10 |

该页为《Chapter 3. Regional Wealth Inequality》第79页，上半部为 Figure 3.4 的双面板折线图（各地区净外国财富，1800–2025，分别以本地区GDP和世界GDP占比表示），下半部为两栏正文。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 25 | `Europe` · `1920` · `As % of regional GDP` | 10% | f1 | the Europe line in the right panel around 1870, read against the 20%–30% ticks | 否 | `As % of world GDP` · `Europe` |
| 2 | -25 | `North America & Oceania` · `2010` · `As % of regional GDP` | 10% | f1 | a mid-19th/early-20th century trough of one of the debtor lines in the left panel (e.g. Latin America or Sub–Saharan Africa), between the 0% and –50% ticks | 否 | `As % of regional GDP` · `Latin America` |
| 3 | 45 | `MENA` · `2010` · `As % of regional GDP` | 10% | f1 | the Europe line's plateau in the left panel around 1890, just below the 50% tick | 否 | `As % of regional GDP` · `Europe` |
| 4 | 40 | `East Asia` · `2010` · `As % of regional GDP` | 10% | f1 | the Europe line in the left panel around 1870–1880, between 0% and 50% | 否 | `As % of regional GDP` · `Europe` |
| 5 | -25 | `Sub-Saharan Africa` · `1980` · `As % of regional GDP` | 20% | f1 | repeat of the same reading: a left-panel line between 0% and –50% (e.g. South & Southeast Asia in the late 19th century) | 否 | `As % of regional GDP` · `South & Southeast Asia` |
| 6 | 8 | `Europe` · `1920` · `As % of world GDP` | 20% | f1 | the North America & Oceania line peak in 1950 in the right panel; the note states "peaking in 1950 at 8% of world GDP" | 否 | `As % of world GDP` · `North America & Oceania` · `1950` |
| 7 | -5 | `North America & Oceania` · `2010` · `As % of world GDP` | 30% | f1 | a right-panel debtor line between the 0% and –10% ticks (e.g. South & Southeast Asia in the 19th century) | 否 | `As % of world GDP` · `South & Southeast Asia` |
| 8 | 9 | `East Asia` · `2010` · `As % of world GDP` | 5% | f1 | the East Asia line in the right panel shortly before 2025, between the 0% and 10% ticks | 否 | `As % of world GDP` · `East Asia` |
| 9 | 8 | `North America & Oceania` · `1950` · `As % of world GDP` | 10% | f1 | repeat: a right-panel line just below the 10% tick (East Asia or Europe near the end of the series) | 否 | `As % of world GDP` · `East Asia` |
| 10 | -4 | `South & Southeast Asia` · `1920` · `As % of world GDP` | 30% | f1 | a right-panel line just above the –10% tick (e.g. Latin America or MENA in the 20th century) | 否 | `As % of world GDP` · `Latin America` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——10 of 10 predicted key sets miss a rule label: 25, -25, 45, 40, -25, 8

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 2 | 9 | 8 | 4000 | 无 | left panel: 50%, 0%, –50%, –100%; right panel: 30%, 20%, 10%, 0%, –10%, –20% |

- **f1** Figure 3.4. / Since the 1970s, North America & Oceania has shifted into the largest net debtor / Net foreign wealth across regions, 1800–2025　[图上方]　单位 `As % of regional GDP`
  - 来源行：Sources and series: Bauluz et al. (2025), Nievas and Piketty (2025), and wir2026.wid.world/methodology.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a thick black flat rule at 0% in both panels, legend entry "World" |
| `negative_values` | 负值 / 零线居中的分叉条 | f1 | **无** | left ticks go to –50%, –100%; right ticks to –10%, –20%; most lines run below the 0% rule |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | left panel 50% to –100%, right panel 30% to –20%; different scales |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one nine-entry legend under both panels governing them jointly |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | two panels of the same line chart split by denominator, side by side |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Interpretation. Between 1800 and 1914..." and "Sources and series: Bauluz et al. (2025)..." under the figure |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend rows "East Asia ... World" and "Europe ... Sub–Saharan Africa" sit below the two plots |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | "As % of regional GDP" over the left plot, "As % of world GDP" over the right plot |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | panel titles "As % of regional GDP" / "As % of world GDP" carry the scale |
| `rotated_axis_title` | 轴标题竖排 | f1 | 有 | "Net foreign assets, MER" set vertically along the left panel's y axis |
| `sparse_time_ticks` | 刻度比数据点稀，读某点要自己内插 | f1 | 有 | annual lines but x ticks only every 30 years: 1800, 1830, 1860, 1890, 1920, 1950, 1980, 2010 |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 9 annual series over 1800–2025 in each of 2 panels, thousands of plotted points |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the "World" series drawn in black and thicker than the coloured regional lines |

词表 65 项，本页出现 13 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `aggregate_series_doubles_as_zero_line` | f1 | the black "World" series lies flat on 0% in both panels, indistinguishable from the zero rule | 读值时无法区分“零基准线”和“World 系列”，World 在任一年份的值只能靠图例推断为约 0，不能从像素单独定位。 |
| `interpretation_note_with_inline_numbers` | f1 | "Interpretation." block states 71% of GDP, 12%, 4%, 8% of world GDP, –18% below the plot | 若干关键数值只写在注释散文里而非图上，解析表格若丢掉这段文字，这些值就完全无处可取。 |
| `axis_title_governing_both_panels` | f1 | "Net foreign assets, MER" printed only left of panel 1 but applies to both panels | 右面板的纵轴含义需借用左侧竖排标题，表格若按面板拆行会丢失该量纲说明。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

最卡的是取值本身。左面板刻度只有 50%、0%、–50%、–100% 四档，约 35 像素对应 50 个百分点，要把 45 与 40 区分开需要约 3 像素精度；右面板对 8 这个值 5% 容差只有 ±0.4 个百分点，远低于线宽。更糟的是 9 条年度曲线在 –25% 到 0% 区间大量交叉重叠（1890–1950 段几乎黏在一起），像素上无法把某一年某一系列单独摘出；而 x 轴每 30 年一个刻度，指定年份还要在刻度间插值。相比之下标签只需“面板名+系列名(+年份)”三层，表格是可以承载的。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | panel_title_per_panel 与 per_panel_axis_range 组合（同一图内两套不同纵轴范围的面板标题） | 条件行中的 panel 维度：为每个面板单独生成 axis_range 与面板标题字段 | “双面板不同量纲（%本地区GDP vs %世界GDP）时，是否把面板名写入 key”对读值正确率的影响 |
| P6 | 一类出版方 | aggregate_series_doubles_as_zero_line（聚合系列与零参考线重合） | style 字段中 reference_line 的绘制规则：允许某一图例系列本身就是零线并加粗描黑 | “零线兼作 World 系列”与“独立零线”两种设定下，模型是否错把参考线当数据系列 |
| P5 | 通用 | dense_marks_100plus + sparse_time_ticks（226 年年度数据、刻度每 30 年） | 密度上限参数与时间轴刻度间隔参数，作为可控变量而非固定值 | 刻度间隔（每年/每10年/每30年）× 系列数（3/9）下的取值误差曲线 |
| P7 | 通用 | 标题四段拆分：figure_number「Figure 3.4.」、title、subtitle「Net foreign wealth across regions, 1800–2025」、面板级 unit | 记录的 heading 字段结构，以及 markdown 导出时标题/副标题相对表格的位置 | “副标题与面板名以粗体/标题形式置于表上”与“合并进表内单元格”两种导出的上下文命中率 |
| P3 | 这份文档自己的习惯 | interpretation_note_with_inline_numbers（注释散文中含 71%、12%、4%、8%、–18% 等数值） | 图下 note 行的生成模板：允许把若干真实数值写进解释性文字 | “数值仅在 note 文本中”时，整页 markdown 导出是否保留 note 段落对命中率的影响 |
