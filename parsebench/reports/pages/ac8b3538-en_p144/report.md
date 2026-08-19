# ac8b3538-en_p144

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 10 | 10 |

本页为OECD《Employment Outlook 2024》第142页，含正文两小节与一幅双轴图（Figure 3.2），以柱状表示高排放行业就业占比、菱形标记表示排放占比（右轴），按国家升序排列。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 4.4 | `Share in employment` · `NLD` | 10% | f1 | the NLD 'Share in employment' bar, first bar on the left | 否 | `NLD` · `Share in employment` · `Share in employment, %` |
| 2 | 82 | `Share in emissions (right scale)` · `NLD` | 5% | f1 | the NLD 'Share in emissions (right scale)' diamond | 否 | `NLD` · `Share in emissions (right scale)` · `Share in total emissions, %` |
| 3 | 7.2 | `Share in employment` · `Average` | 10% | f1 | the 'Average' bar, highlighted in light green | 否 | `Average` · `Share in employment` · `Share in employment, %` |
| 4 | 80 | `Share in emissions (right scale)` · `Average` | 10% | f1 | the 'Average' diamond on the right scale | 否 | `Average` · `Share in emissions (right scale)` · `Share in total emissions, %` |
| 5 | 11.5 | `Share in employment` · `POL` | 10% | f1 | the POL 'Share in employment' bar, last bar on the right | 否 | `POL` · `Share in employment` · `Share in employment, %` |
| 6 | 79 | `Share in emissions (right scale)` · `POL` | 10% | f1 | the POL 'Share in emissions (right scale)' diamond | 否 | `POL` · `Share in emissions (right scale)` · `Share in total emissions, %` |
| 7 | 5.7 | `Share in employment` · `USA*` | 5% | f1 | the FRA (or ESP) 'Share in employment' bar, around the sixth slot | 否 | `FRA` · `Share in employment` · `Share in employment, %` |
| 8 | 83 | `Share in emissions (right scale)` · `USA*` | 5% | f1 | the ESP 'Share in emissions (right scale)' diamond | 否 | `ESP` · `Share in emissions (right scale)` · `Share in total emissions, %` |
| 9 | 5.7 | `Share in employment` · `FRA` | 5% | f1 | the ESP 'Share in employment' bar, a second bar at the same height as FRA | 否 | `ESP` · `Share in employment` · `Share in employment, %` |
| 10 | 68 | `Share in emissions (right scale)` · `FRA` | 10% | f1 | the FRA 'Share in emissions (right scale)' diamond, the lowest diamond together with SVK | 否 | `FRA` · `Share in emissions (right scale)` · `Share in total emissions, %` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——3 of 10 predicted key sets miss a rule label: 5.7, 83, 5.7

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 2 | 26 | 52 | 无 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 |

- **f1** Figure 3.2. / High-emission industries are responsible for most emissions but employ only a fraction of the workforce / Share of GHG emissions and employment in high-emission industries by country, 2019*　[图上方]　单位 `Share in employment, %`
  - 来源行：Source: OECD National Accounts and Eurostat Air Emissions Accounts.,

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `dual_axis` | 双 y 轴，同面板两个量纲 | f1 | 有 | left axis 0-20 'Share in employment, %', right axis 0-100 'Share in total emissions, %' |
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | green bars for employment plus diamond markers for emissions in the same panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: * Data refer to 2016 and to CO2 emissions for Mexico and the United States...' and 'Source: ...' |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend band with 'Share in employment' and 'Share in emissions (right scale)' between subtitle and plot |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | 'StatLink' logo with 'https://stat.link/ejxuol' under the figure |
| `unit_in_series_name` | 单位写在系列名里（例：`Operating Cash Flow ($B)`） | f1 | **无** | legend entry reads 'Share in emissions (right scale)' naming the scale it belongs to |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | 'Share in employment, %' above left axis; 'Share in total emissions, %' above right axis |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | '2019*', 'USA*', 'MEX*' carry asterisks explained in the Note line |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | both unit lines sit above the top ticks 20 and 100, not alongside the axes |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | country codes set at roughly 45 degrees under the axis |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | x ticks read 'NLD, IRL, GBR, DNK, USA*, FRA, ESP...' |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | plot area carries a light grey tint rather than white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | faint horizontal rules across the plot, no vertical rules |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the 'Average' bar is drawn in bright light green among dark green bars |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | ISL emissions diamond is filled solid dark green while other diamonds are pale |

词表 65 项，本页出现 14 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `single_series_marker_highlight` | f1 | only the ISL diamond is solid dark green; all other diamonds are light green outlines | 读取ISL排放值时须知该标记仍属同一系列，颜色差异不代表新系列，否则会误建额外行。 |
| `sorted_category_axis` | f1 | bars rise monotonically from NLD 4.4 to POL 11.5 with 'Average' inserted in order | 类别顺序由就业占比升序决定，定位某国需依代码而非位置，且平均值插在序列中间。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上无任何数值标签，26国×2系列共52个标记全靠像素对轴读数。左轴刻度间隔为2个百分点，而4.4的5%容差仅±0.22，即约刻度间距的1/9（约3像素），5.7与5.7两根几乎等高的柱更需分辨到0.1；右轴刻度间隔10而68的容差为±3.4，菱形本身高度已接近该量级。此外双轴共用一个绘图区，误把菱形读到左轴会直接偏差数倍，因此“取值”比“标签寻址”更致命——寻址只需国家代码加系列名两个键，Note中的USA*/MEX*脚注也已给出。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | dual_axis 与 mixed_marks 的组合（柱+右轴菱形标记） | 图表生成条件行中新增“双轴且第二系列为点标记”的样式组合，记录字段需为每系列标注所属轴 | 第二系列绑定右轴 vs 全部绑定左轴：比较模型读值时的轴归属错误率 |
| P6 | 一类出版方 | highlighted_category（Average柱与ISL菱形的异色高亮） | 样式字段增加 per-category 颜色覆盖，并在记录中标记该类别为聚合/参考项 | 含高亮聚合类别 vs 全同色：检验模型是否把异色标记误判为新系列 |
| P7 | 一类出版方 | 标题四段拆分（figure_number/title/subtitle/unit_text）与轴上方单位行 | P7 的标题结构字段，新增 axis_title_above_axis 的单位放置位置枚举 | 单位置于轴顶部 vs 置于副标题：检验单位能否被正确带入表头 |
| new | 通用 | sorted_category_axis（升序排列且Average插入序列中）新组件 | 条件行增加类别排序方式（原始/升序/降序）以及聚合项插入位置 | 按值排序含插入均值 vs 字母序：检验按代码而非按位置寻址的成功率 |
| P1 | 通用 | dense_marks 的中等密度档（52个无标签标记、26个旋转代码刻度） | 密度上限参数与刻度旋转样式字段 | 26类别×2系列无数值标签 vs 10类别：检验每标记可达精度随密度的衰减 |
