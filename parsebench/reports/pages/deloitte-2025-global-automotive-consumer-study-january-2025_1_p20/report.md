# deloitte-2025-global-automotive-consumer-study-january-2025_1_p20

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| deloitte-2025-global-automotive-consumer-study-january-2025_1 | `untagged` | 6 | 0 |

该页为《2025 Global Automotive Consumer Study》第20页，含两个并列的青色/绿色水平条形图（对自动驾驶出租车与商用车自动驾驶的担忧比例）以及一个关于车载人工智能态度的100%堆积水平条形图。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 82 | `India` · `Beneficial` | 1% | f3 | the India Beneficial segment | 是 | `Addition of artificial intelligence in vehicle systems` · `India` · `Beneficial` |
| 2 | 13 | `India` · `Neutral` | 1% | f3 | the India Neutral segment | 是 | `Addition of artificial intelligence in vehicle systems` · `India` · `Neutral` |
| 3 | 77 | `China` · `Beneficial` | 1% | f3 | the China Beneficial segment | 是 | `Addition of artificial intelligence in vehicle systems` · `China` · `Beneficial` |
| 4 | 45 | `US` · `Beneficial` | 1% | f3 | the US Beneficial segment | 是 | `Addition of artificial intelligence in vehicle systems` · `US` · `Beneficial` |
| 5 | 41 | `Germany` · `Beneficial` | 1% | f3 | the Germany Beneficial segment; note 41% also appears as the Japan bar in f1 | 是 | `Addition of artificial intelligence in vehicle systems` · `Germany` · `Beneficial` |
| 6 | 31 | `UK` · `Neutral` | 1% | f3 | the UK Neutral segment | 是 | `Addition of artificial intelligence in vehicle systems` · `UK` · `Neutral` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |
| f2 | `bar` | horizontal | 1 | 1 | 8 | 8 | 全部 | （不画值轴） |
| f3 | `stacked_bar` | horizontal | 1 | 3 | 8 | 24 | 全部 | （不画值轴） |

- **f1** Percentage of consumers concerned about fully autonomous robotaxi services operating where they live　[图上方]　（标题里没有单位）
  - 来源行：Q56. To what extent are you concerned with each of the following scenarios? Sample size: n = 939 [China]; 1,306 [Germany]; 882 [India]; 637 [Japan]; 906 [Republic of Korea]; 5,028 [Southeast Asia]; 1,314 [UK]; 937 [US]
- **f2** Percentage of consumers concerned about commercial vehicles operating in a fully autonomous mode on the highway　[图上方]　（标题里没有单位）
  - 来源行：Q56. To what extent are you concerned with each of the following scenarios? Sample size: n = 939 [China]; 1,306 [Germany]; 882 [India]; 637 [Japan]; 906 [Republic of Korea]; 5,028 [Southeast Asia]; 1,314 [UK]; 937 [US]
- **f3** Addition of artificial intelligence in vehicle systems　[图上方]　（标题里没有单位）
  - 来源行：Note: Percentages may not add up to 100 due to rounding. Q62. To what extent do you think the addition of artificial intelligence in vehicle systems (e.g., voice activated features, autonomous driving) will be beneficial? Sample size: n = 939 [China]; 1,306 [Germany]; 882 [India]; 637 [Japan]; 906 [Republic of Korea]; 5,028 [Southeast Asia]; 1,314 [UK]; 937 [US]

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `stacked_bar` | 堆叠条 | f3 | 有 | each country row is split into dark blue, green and light blue segments |
| `pct_stacked` | 百分比堆叠（归一到 100%） | f3 | **无** | all eight rows end at the same length; 5%+13%+82% = 100% for India |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | country names on the left, teal bars grow rightwards from a left baseline |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | country names on the left, green bars grow rightwards from a left baseline |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f3 | **无** | country names on the left, stacked bars run right to a common end |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a thin left baseline is drawn; no ticks or numbers along any value axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | only a thin left baseline is drawn; no ticks or numbers along any value axis |
| `no_value_axis` | 没有值轴刻度，只有基线 | f3 | **无** | no ticks under the stacked rows; percentages readable only from printed labels |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two captioned bar charts side by side plus a separately captioned stacked bar chart below |
| `source_note_lines` | source / note 行在图下方 | page | 有 | 'Q56. To what extent are you concerned...', 'Note: Percentages may not add up to 100 due to rounding.' |
| `legend_below_plot` | 图例在绘图区下方 | f3 | 有 | 'Not benefical  Neutral  Beneficial' row sits centred under the last bar |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | '63%', '52%', '36%' printed in white at the right end inside each bar |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | '74%', '67%', '47%' printed in white inside the right end of each bar |
| `value_label_inside` | 数值标签写在图元内部 | f3 | 有 | '5%', '13%', '82%' printed inside each segment of the India row |

词表 65 项，本页出现 8 项，其中我们画不出来的 3 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `per_panel_category_order` | page | f1 orders India, UK, US...; f2 orders India, UK, Rep. of Korea...; each sorted by its own values | 同一组国家在两图中行序不同，表格若按图1行序照搬会把图2的数值配错国家，必须逐图重建行顺序。 |
| `shared_note_block_for_two_figures` | page | one 'Q56.' + sample-size block sits under both the teal and the green chart | 问题编号与样本量属于两张图共有，解析时不能只挂到左图，否则右图失去溯源标签。 |
| `bold_emphasis_inside_caption` | f1 | 'fully autonomous robotaxi services' is bold inside an otherwise regular caption line | 标题内部的加粗片段是区分左右两图的唯一关键词，markdown 若丢掉粗体或拆行，两图标题将难以区分。 |
| `takeaway_sentence_above_figures` | page | bold sentence 'Consumers surveyed in both India and the United Kingdom are more concerned...' precedes the charts | 该粗体结论句易被误当作图标题，从而使真正的量纲说明（'Percentage of consumers...'）降级为副标题。 |
| `unnumbered_figures` | page | no 'Figure' or 'Exhibit' number anywhere; charts identified only by caption text | 没有图号可用作定位键，数值必须靠标题措辞+国家+系列名三者共同寻址。 |

## 5 · 难在哪

卡在 **第四步 · 表外上下文**。

三张图的数值全部以白字印在条内（82%、13%、31% 等），第2步几乎无难度；第3步也不重的：f3 只需“国家 + 系列名”两个键，行列表即可承载。真正卡住的是第4步：页面没有任何图号，f1/f2/f3 的身份只存在于绘图区上方的小号说明行，而其中的区分词组（fully autonomous robotaxi services / commercial vehicles operating in a fully autonomous mode）是句内加粗片段，解析器很可能把它并入正文段落而非表格标题。后果是数字会撞车——41% 同时是 f1 的 Japan 条与 f3 的 Germany“Beneficial”段，52% 同时出现在 f1 的 UK/US 与 f3 的 Japan 附近区间，缺少图级上下文时无法判定归属。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | 新增 per_panel_category_order（同类别集合、各图自排序） | 记录字段中为每个图单独存 category order，而非页级共享类别序列 | “并列同类别但排序不同的两图”一行：检验模型是否按图重建行序而非套用首图顺序 |
| P7 | 一类出版方 | 新增 unnumbered_figures 与 bold_emphasis_inside_caption | 标题字段拆分（figure_number 允许为空、title 内部保留加粗片段标记） | “无图号、靠标题内加粗词区分的同页多图”一行：检验数值与图标题的绑定率 |
| P3 | 一类出版方 | 新增 shared_note_block_for_two_figures | 整页 markdown 导出条件行：一个 note/来源块同时归属两张表 | “一条注释服务多图”一行：检验注释是否被复制到两张表而非只挂左图 |
| P6 | 一类出版方 | 补强 value_label_inside 与 no_value_axis 组合（无刻度纯标签读数） | 样式字段：value-label placement = inside 且 value axis = none | “无值轴、仅内嵌标签”一行：验证在无刻度参照下的数值抄录准确率 |
