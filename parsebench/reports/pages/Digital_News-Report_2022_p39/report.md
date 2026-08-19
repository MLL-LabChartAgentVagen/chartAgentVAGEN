# Digital_News-Report_2022_p39

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Digital_News-Report_2022 | `untagged` | 4 | 0 |

该页含两幅无编号图：上方为德国、挪威、英国、美国四国的跨平台新闻受众极化气泡图（四小面板），右下为四国极化程度的柱状图（34/25/15/10），左侧为正文说明。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 34 | `USA` · `Polarisation Score (%)` | 1% | f2 | the USA bar, label printed inside the bar top | 是 | `EXTENT OF CROSS-PLATFORM NEWS AUDIENCE POLARISATION – SELECTED COUNTRIES` · `USA` |
| 2 | 25 | `UK` · `Polarisation Score (%)` | 1% | f2 | the UK bar, label printed inside the bar top | 是 | `EXTENT OF CROSS-PLATFORM NEWS AUDIENCE POLARISATION – SELECTED COUNTRIES` · `UK` |
| 3 | 15 | `Norway` · `Polarisation Score (%)` | 1% | f2 | the Norway bar, label printed inside the bar top | 是 | `EXTENT OF CROSS-PLATFORM NEWS AUDIENCE POLARISATION – SELECTED COUNTRIES` · `Norway` |
| 4 | 10 | `Germany` · `Polarisation Score (%)` | 1% | f2 | the Germany bar, label printed inside the bar top | 是 | `EXTENT OF CROSS-PLATFORM NEWS AUDIENCE POLARISATION – SELECTED COUNTRIES` · `Germany` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——4 of 4 predicted key sets miss a rule label: 34, 25, 15, 10

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `scatter` | horizontal | 4 | 1 | 3 | 52 | 无 | （不画值轴） |
| f2 | `bar` | vertical | 1 | 1 | 4 | 4 | 全部 | 0%, 25%, 50%, 75%, 100% |

- **f1** CROSS-PLATFORM NEWS AUDIENCE POLARISATION – SELECTED COUNTRIES　[图上方]　（标题里没有单位）
  - 来源行：Q1F. Some people talk about ‘left’, ‘right’, and ‘centre’ to describe parties and politicians. With this in mind, where would you place yourself on the following scale? Q5A/B. Which of the following brands have you used to access news offline/online in the last week? Base: Germany = 2002, Norway = 2010, UK = 2410, USA = 2036.
- **f2** EXTENT OF CROSS-PLATFORM NEWS AUDIENCE / POLARISATION – SELECTED COUNTRIES　[图上方]　（标题里没有单位）
  - 来源行：Q1F. Some people talk about ‘left’, ‘right’, and ‘centre’ to describe parties and politicians. With this in mind, where would you place yourself on the following scale? Q5A/B. Which of the following brands have you used to access news offline/online in the last week? Base: Germany = 2002, Norway = 2010, UK = 2410, USA = 2036.

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） | f1 | **无** | a vertical rule in each panel labelled 'Average political leaning of population' |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | the horizontal axis is a bare line with no numeric ticks, only three text labels beneath |
| `per_panel_axis_range` | 各面板各自的值域，不共享刻度 | f1 | 有 | each of the four panels draws its own baseline and its own left/centre/right labels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | four identical bubble maps for Germany, Norway, UK, USA in a 2x2 arrangement |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two separately headed figures, 'CROSS-PLATFORM NEWS AUDIENCE POLARISATION' and 'EXTENT OF CROSS-PLATFORM...', each with its own Q1F note |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | small print under the maps beginning 'Q1F. Some people talk about ‘left’, ‘right’...' with 'Base: Germany = 2002' |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | small print under the bars: 'Q1F. ... Q5A/B. ... Base: Germany = 2002, Norway = 2010, UK = 2410, USA = 2036.' |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | 'Germany', 'Norway', 'UK', 'USA' set in bold above each panel's own axis |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | body column 'NEWS AUDIENCE POLARISATION VARIES BY COUNTRY' runs left of f2 in the same horizontal band |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '34', '25', '15', '10' printed in white inside the tops of the bars |
| `inline_series_labels` | 没有图例，系列名直接标在线旁 | f1 | **无** | 'ARD News', 'ZEIT', 'Bild', 'NRK', 'Guardian', 'Fox News' printed next to individual bubbles; no legend |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | 'Very left-leaning / audience' and 'Average political leaning / of population' wrap onto two lines |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `bubble_size_encodes_magnitude` | f1 | bubble diameters vary greatly (e.g. NRK, BBC News largest) with no size legend or scale | 气泡面积承载了受众规模这一第三变量，但页面无尺寸图例，任何取值都无法定量读出，只能读位置。 |
| `semantic_axis_endpoint_labels` | f1 | axis anchored only by 'Very left-leaning audience' and 'Very right-leaning audience' at its two ends | 横轴没有数值刻度，只有两端语义标签，读数只能是相对位置描述，表格无法给出数值行。 |
| `flag_icon_beside_panel_title` | f1 | a circular national flag icon sits immediately left of each panel name 'Germany', 'Norway', 'UK', 'USA' | 面板身份部分由图标承担，若解析器丢弃图像仍可靠文字面板名定位，但需确认面板名而非图标作为键。 |
| `labelled_subset_of_marks` | f1 | only three or four bubbles per panel carry brand names; the remaining bubbles are unlabelled | 多数气泡无名称，无法为其构造可寻址行，只有被标注的少数品牌可进入表格。 |
| `color_per_category_single_series` | f2 | one series but four different bar fills: teal USA, orange UK, magenta Norway, navy Germany | 颜色只区分类别而非序列，读值仍靠x轴国家名，颜色不构成额外寻址键。 |
| `percent_ticks_bare_value_labels` | f2 | axis reads '0%, 25%, 50%, 75%, 100%' but labels on bars read bare '34', '25', '15', '10' | 条上数字没有百分号，单位只能由刻度推得，抽取表格时易被当作绝对数。 |

## 5 · 难在哪

卡在 **第一步 · 要有表**。

四个待核数值都直接印在柱内（34/25/15/10），刻度间距25%远大于5%容差，所以读数不难；寻址也只需“国家名+图标题”两个键。真正的阻塞在于是否有表：f2只有4根柱、无图号、标题是两行全大写小标题，解析器很可能把它当版面文字跳过；而f1完全没有数值轴与数值标签，只能产出品牌名与相对位置，根本无法生成数值行。此外正文只提到10%和34%，25与15若图被跳过就无处可寻。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P1 | 一类出版方 | no_value_axis 与新组件 semantic_axis_endpoint_labels（仅两端语义标签的轴） | 图表条件行中的“值轴”样式字段，允许取值为“无刻度、仅端点文字” | 新增一行：值轴无刻度且仅有语义端点标签时，每个标记的可达精度（而非布尔可读） |
| new | 一类出版方 | 新组件 bubble_size_encodes_magnitude（气泡面积编码第三变量且无尺寸图例） | 记录字段增加 size 通道，及样式字段“是否绘制尺寸图例” | 新增一行：存在无图例的尺寸通道时，数值抽取的召回率变化 |
| P7 | 一类出版方 | 无编号图的标题拆分（title 与 subtitle 换行、两图标题前缀几乎相同） | 标题记录字段：figure_number 可空，title/subtitle 分行存储，并记录标题块位置 above | 新增一行：同页两图标题前缀重叠且均无图号时，标题—表格配对的正确率 |
| P2 | 这份文档自己的习惯 | panel_title_per_panel 与新组件 flag_icon_beside_panel_title | 面板维度进入键（panel_key），并在样式字段加“面板名旁图标” | 新增一行：面板名带图标时 panel_key 是否仍能唯一寻址各面板的标记 |
| P6 | 通用 | value_label_inside 与新组件 percent_ticks_bare_value_labels | 样式维度中的“值标签位置”与“刻度格式/单位位置”组合 | 新增一行：刻度带%而标签为裸数字时，抽出数值的单位判定错误率 |
