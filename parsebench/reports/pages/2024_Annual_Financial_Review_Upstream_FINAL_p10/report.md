# 2024_Annual_Financial_Review_Upstream_FINAL_p10

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| 2024_Annual_Financial_Review_Upstream_FINAL | `need_estimate` | 10 | 10 |

EIA 幻灯片页，展示 2015–2024 年 Henry Hub 天然气近月期货实际价格的单线折线图，右侧配有灰底文字栏。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 3.48 | `2015` | 5% | f1 | the 2015 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2015` |
| 2 | 3.35 | `2016` | 5% | f1 | the 2016 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2016` |
| 3 | 3.86 | `2017` | 5% | f1 | the 2017 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2017` |
| 4 | 3.84 | `2018` | 5% | f1 | the 2018 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2018` |
| 5 | 3.08 | `2019` | 5% | f1 | the 2019 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2019` |
| 6 | 2.58 | `2020` | 5% | f1 | the 2020 point, the local minimum of the line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2020` |
| 7 | 4.28 | `2021` | 5% | f1 | the 2021 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2021` |
| 8 | 7.01 | `2022` | 5% | f1 | the 2022 point, the peak of the line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2022` |
| 9 | 2.74 | `2023` | 5% | f1 | the 2023 point of the single line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2023` |
| 10 | 2.41 | `2024` | 5% | f1 | the 2024 point, the last point of the line | 否 | `Natural gas front-month futures price (Henry Hub)` · `2024` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `line` | vertical | 1 | 1 | 10 | 10 | 无 | $0, $1, $2, $3, $4, $5, $6, $7, $8 |

- **f1** Natural gas front-month futures price (Henry Hub)　[图上方]　单位 `real 2024 dollars per million British thermal units`
  - 来源行：Data source: Bloomberg L.P.','

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | "Data source: Bloomberg L.P." printed under the plot |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | f1 | **无** | grey column right of plot: "Lower natural gas prices reduced cash from operations..." |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | subtitle line reads "real 2024 dollars per million British thermal units" |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | horizontal rules at each dollar tick across the plot, no vertical rules |

词表 65 项，本页出现 4 项，其中我们画不出来的 2 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `source_line_without_source_word` | f1 | the note reads "Data source: Bloomberg L.P.", not "Source:" | 解析器若只搜索 "Source:" 会漏掉该行，导致图表数据来源无法与表格关联。 |
| `currency_prefixed_axis_ticks` | f1 | value axis ticks printed as "$0" ... "$8" with dollar sign on every tick | 读值时需剥离 $ 符号，且刻度间距 $1 对应 5% 容差意味着必须在半格内定位。 |

## 5 · 难在哪

卡在 **第二步 · 找到值**。

图上一个数字都没印，10 个值全靠像素读取。刻度间隔为 $1（约 40 像素），而 5% 容差在 2.41 这样的低值上仅 ±0.12，即约 5 像素；3.86 与 3.84 两点几乎等高，肉眼无法区分小数第二位。相反，标注只需「标题 + 年份」两个键，单序列无图例，寻址毫无难度。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 通用 | unit_in_axis_or_title 的变体：货币符号前缀刻度（新组件 currency_prefixed_axis_ticks） | 样式字段中的 tick_format，加入 "$%d" 这类前缀格式选项 | 刻度带货币前缀 vs 裸数字，比较解析器读值与单位识别的正确率 |
| P3 | 一类出版方 | source_note_lines 下的来源措辞变体（"Data source:" 而非 "Source:"） | 图注记录字段 source_line 的模板文本 | 来源行前缀词变化时，来源归属抽取的召回率 |
| P3 | 这份文档自己的习惯 | side_text_bullets：图右侧灰底解读文字栏 | 页面布局条件行，增加「图 + 侧栏文字共占一横带」的版式 | 有无侧栏文字时，标题与表格的对应关系是否被打乱 |
| P7 | 通用 | 标题拆分为 title 与 unit_text（副行为单位说明） | heading 记录字段：title / unit_text / placement 分离 | 单位置于副标题行 vs 置于轴标题时，数值单位还原的准确率 |
