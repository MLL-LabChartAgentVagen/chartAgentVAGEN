# ac8b3538-en_p25

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| ac8b3538-en | `need_estimate` | 8 | 8 |

OECD《Employment Outlook 2024》第23页正文段落之下有一幅图（Figure 1.3），以40个国家代码为横轴的柱状图叠加两组菱形标记与一行红色三角旗标，配注释、来源及StatLink链接。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 11.7 | `ESP` · `Latest (May 2024)` | 5% | f1 | the ESP bar for Latest (May 2024), the tallest bar | 否 | `ESP` · `Latest (May 2024)` |
| 2 | 17.1 | `GRC` · `Pre-crisis (December 2019)` | 8% | f1 | the GRC Pre-crisis (December 2019) diamond, highest marker in the figure | 否 | `GRC` · `Pre-crisis (December 2019)` |
| 3 | 12.3 | `COL` · `January 2022` | 8% | f1 | the CRI Pre-crisis (December 2019) diamond, the lower of the two CRI markers | 否 | `CRI` · `Pre-crisis (December 2019)` |
| 4 | 3.5 | `USA` · `Pre-crisis (December 2019)` | 20% | f1 | the MEX Pre-crisis (December 2019) diamond, sitting above the short MEX bar | 否 | `MEX` · `Pre-crisis (December 2019)` |
| 5 | 2.6 | `JPN` · `Latest (May 2024)` | 20% | f1 | the JPN bar for Latest (May 2024), the rightmost and shortest bar | 否 | `JPN` · `Latest (May 2024)` |
| 6 | 8.3 | `SWE` · `Latest (May 2024)` | 10% | f1 | the FIN bar for Latest (May 2024) | 否 | `FIN` · `Latest (May 2024)` |
| 7 | 13.1 | `GRC` · `January 2022` | 10% | f1 | the TUR Pre-crisis (December 2019) diamond, near the 13 level | 否 | `TUR` · `Pre-crisis (December 2019)` |
| 8 | 6.2 | `CAN` · `Latest (May 2024)` | 20% | f1 | the CAN bar for Latest (May 2024) (June 2024 per the note) | 否 | `CAN` · `Latest (May 2024)` |

**程序核对**（模型没有看到左半的标签列）：

- 给了 N 个值，模型回了另一个数目——8 values given, 9 answered
- 模型预测的定位标签漏掉了规则实际用的标签——4 of 8 predicted key sets miss a rule label: 12.3, 3.5, 8.3, 13.1

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `compound` | vertical | 1 | 4 | 40 | 136 | 无 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18 |

- **f1** Figure 1.3. / Unemployment rates remain at historically low levels in many countries / Unemployment rate (percentage of labour force), seasonally adjusted data　[图上方]　单位 `percentage of labour force`
  - 来源行：Source: OECD (2024), "Unemployment rate" (indicator), https://doi.org/10.1787/52570002-en (accessed on 9 July 2024).

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `mixed_marks` | 同面板混合图元（bar + line） | f1 | 有 | teal bars with green and light-green diamond markers plus red triangles in one panel |
| `color_encodes_extra_attribute` | 颜色编码的是系列以外的第三个变量（分组 / 是否显著 / 是否达标） | f1 | **无** | red triangle legend "Increased over the last 6 months" flags countries, not a quantity |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Note: The labour force population includes all those aged 15 or more..." then "Source: OECD (2024)..." |
| `legend_above_plot` | 图例在绘图区上方（标题与图之间） | f1 | 有 | legend row on a grey band between the subtitle and the plot area |
| `data_link_below_figure` | 图下方另有取数链接（StatLink / download / 二维码），与 source 行分开 | f1 | **无** | "StatLink" glyph with "https://stat.link/1z75tu" under the note lines |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | "Unemployment rate (percentage of labour force), seasonally adjusted data" heading line; axis shows bare 0-18 |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | "%" printed above the top tick "18" on the left axis |
| `rotated_x_ticks` | x 刻度标签旋转 | f1 | 有 | the country codes are set at roughly 45 degrees under the baseline |
| `abbrev_category_axis` | 类目轴用缩写码（例：`IRL` `EU-27`） | f1 | 有 | axis reads "ESP, GRC, COL, CRI, TUR, SWE ... MEX, JPN", plus "EA20", "QECD" |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the plot area carries a light grey tint behind the bars |
| `dense_marks_100plus` | 单张图 ≥100 个图元 | f1 | **无** | 40 country slots times bar plus two diamonds, about 136 drawn marks |
| `highlighted_category` | 某一个类目单独换色或标签加粗（汇总行 / 重点对象） | f1 | **无** | the EA20 bar is magenta and the QECD bar orange among otherwise teal bars |
| `vgrid_only` | 只有垂直网格线，没有水平网格线 | f1 | 有 | faint vertical rules separate country slots; no horizontal rules over the plot |

词表 65 项，本页出现 13 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `flag_marker_constant_height` | f1 | red triangles all sit at about y=17 on the value axis, marking a yes/no condition | 这些三角形不是数值点，若按轴读数会得到虚假的17左右；表格必须把它们记为布尔标记而非度量。 |
| `sorted_descending_categories` | f1 | bars fall monotonically from ESP (~11.7) to JPN (~2.6) across all 40 codes | 排序本身提供了排序约束，可用来校验读数顺序，但也使相邻国家柱高差小于刻度分辨率。 |
| `legend_period_overridden_by_note` | f1 | legend says "Latest (May 2024)" but note lists Q1 2024, February, March, April, June 2024 per country | 同一系列的时间键因国家而异，定位某一柱的"最新期"需要同时读注释，不能只靠图例标签。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上没有任何数值标签，纵轴刻度为0,2,4,...,18，每2个百分点约占24像素，即1个百分点约12像素。对2.6这类小值，5%容差只有±0.13个百分点，约1.6像素，落在柱顶抗锯齿与柱边框宽度之内；对3.5的菱形标记，标记本身直径就有5-6像素，且MEX、CZE、JPN三国柱高差不到0.3个百分点，几乎无法区分。CRI/TUR处两个菱形（约12.3与13.4）相距仅十余像素并部分重叠，系列归属与数值都难以确定。相比之下标签层面只需"国家代码+图例名"两个键，负担明显更轻。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | 新组件 flag_marker_constant_height（固定高度的旗标系列） | 图形规格中的系列定义字段：允许某一系列声明为boolean flag并指定绘制高度，记录层不写数值 | 有/无"非数值旗标系列"时，模型是否把旗标误读为约17的数值点 |
| P7 | 通用 | unit_in_axis_or_title 与 axis_title_above_axis 组合：标题行承载单位、轴上只有"%"符号 | 标题块样式字段：figure_number/title/subtitle/unit 四段拆分，并把单位符号放在最高刻度之上 | 单位仅出现在副标题行 vs 出现在轴标签时，导出表格的表头是否保留单位 |
| P5 | 一类出版方 | dense_marks_100plus：40个类别×3系列的排序柱+标记混合图 | 密度上限条件行：类别数上限从约20提升到40以上，并允许每类别3个marks | 类别数20 vs 40（每格约12像素宽）时逐mark读数精度的衰减曲线 |
| P1 | 通用 | mixed_marks（柱上叠加两组点标记）对应的可达精度评估 | readable判定：由布尔门改为按mark类型（柱顶 vs 重叠菱形）给出容差 | 柱顶读数 vs 重叠标记读数在5%容差下的通过率对比 |
| P3 | 这份文档自己的习惯 | legend_period_overridden_by_note（注释按类别改写系列时间键） | 记录层的note字段与系列键：允许per-category的期别覆盖 | 注释中含按国家不同的"latest month"时，表格行键是否需要额外一列时间 |
