# US_Professional_Services_Partner_Compensation_Survey_2024_p7

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| US_Professional_Services_Partner_Compensation_Survey_2024 | `untagged` | 5 | 0 |

该页为 Heidrick & Struggles 报告第7页，左侧为两段说明文字，右侧是两组「个人营收目标（%）」的水平条形图小多图（按公司规模、按在职年限各四栏）。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 46 | `$1.00m–$3.00m` · `Less than $1.00bn` | 1% | f1 | the `$1.00m–$3.00m` bar in the `Less than $1.00bn` panel | 是 | `Personal revenue targets, by firm size` · `Less than $1.00bn` · `$1.00m–$3.00m` |
| 2 | 13 | `$1.00m–$3.00m` · `$1.01bn–$5.00bn` | 1% | f1 | the `$1.00m–$3.00m` bar in the `$1.01bn–$5.00bn` panel; `13` also appears for `$10.01m–$15.00m` and `$15.01m–$20.00m` in that same panel | 是 | `Personal revenue targets, by firm size` · `$1.01bn–$5.00bn` · `$1.00m–$3.00m` |
| 3 | 27 | `$1.00m–$3.00m` · `Less than 3 years` | 1% | f2 | the `$1.00m–$3.00m` bar in the `Less than 3 years` panel | 是 | `Personal revenue targets, by tenure at firm` · `Less than 3 years` · `$1.00m–$3.00m` |
| 4 | 21 | `$6.01m–$10.00m` · `3–5 years` | 1% | f1 | the `$6.01m–$10.00m` bar in the `More than $20.00bn` panel; the same number also appears in f2 at `3–5 years` / `$6.01m–$10.00m` | 是 | `Personal revenue targets, by firm size` · `More than $20.00bn` · `$6.01m–$10.00m` |
| 5 | 29 | `More than $30.00m` · `More than 10 years` | 1% | f2 | the `More than $30.00m` bar in the `More than 10 years` panel | 是 | `Personal revenue targets, by tenure at firm` · `More than 10 years` · `More than $30.00m` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 5 predicted key sets miss a rule label: 21

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `bar` | horizontal | 4 | 1 | 10 | 32 | 全部 | （不画值轴） |
| f2 | `bar` | horizontal | 4 | 1 | 10 | 38 | 全部 | （不画值轴） |

- **f1** Personal revenue targets (%) / Personal revenue targets, by firm size　[图上方]　单位 `(%)`
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=155
- **f2** Personal revenue targets, by tenure at firm　[图上方]　（标题里没有单位）
  - 来源行：Source: Heidrick & Struggles US professional services partner compensation survey, 2024, n=155

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `horizontal_bars` | 横向条形（类目在 y 轴） | f1 | **无** | row labels `Less than $1.00m` ... `Prefer not to answer` on the left, bars grow rightward |
| `horizontal_bars` | 横向条形（类目在 y 轴） | f2 | **无** | same ten row labels at left, bars extend to the right in each of four columns |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | no ticks or scale anywhere; only the printed numbers beside each bar |
| `no_value_axis` | 没有值轴刻度，只有基线 | f2 | **无** | no ticks or numeric axis drawn; each bar carries its own printed number |
| `shared_axis` | 跨面板共享坐标轴 | f1 | 有 | the ten revenue-target row labels are printed once at left and serve all four columns |
| `shared_axis` | 跨面板共享坐标轴 | f2 | 有 | one left-hand column of row labels governs the four tenure panels |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f1 | 有 | four side-by-side columns: `Less than $1.00bn`, `$1.01bn–$5.00bn`, `$5.01bn–$20.00bn`, `More than $20.00bn` |
| `small_multiples_4` | 同一张图按一维切成多面板（2–4 个） | f2 | 有 | four columns `Less than 3 years`, `3–5 years`, `6–10 years`, `More than 10 years` |
| `multi_figure_page` | 一页多张独立图，各自有图号 | page | 有 | two captioned charts, `...by firm size` and `...by tenure at firm`, each with own Note and Source |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | `Note: Numbers may not sum to 100%, because of rounding.` above the `Source: Heidrick & Struggles...` line |
| `source_note_lines` | source / note 行在图下方 | f2 | 有 | same two small-print lines `Note: Numbers may not sum to 100%...` and `Source: Heidrick & Struggles...` |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f1 | 有 | each column headed in bold above it, e.g. `$5.01bn–$20.00bn`, some wrapping to two lines |
| `panel_title_per_panel` | 每个面板上方各有一个面板标题 / 色块标题条 | f2 | 有 | bold column heads `Less than 3 years`, `More than 10 years` set above each panel |
| `side_text_bullets` | 图旁另有一栏正文 / 提要文字，与图并排占同一横带 | page | **无** | left column prose `By firm size, we saw a correlation...` and `We also saw a positive correlation...` level with the charts |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | title reads `Personal revenue targets (%)` while the marks carry bare numbers `46`, `13` |
| `value_label_inside` | 数值标签写在图元内部 | f1 | 有 | `46`, `22`, `16`, `26`, `28` printed inside the long bars in white/dark type |
| `value_label_inside` | 数值标签写在图元内部 | f2 | 有 | `27`, `22`, `21`, `24`, `29` printed within the bars themselves |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | `5`, `3`, `2` sit to the right of very short bars, outside the mark |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f2 | **无** | `5`, `3`, `2` printed just right of the short bars |

词表 65 项，本页出现 11 项，其中我们画不出来的 5 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `zero_value_printed_without_bar` | f1 | `0` printed at the baseline in eight slots (e.g. $20.01m–$25.00m under `Less than $1.00bn`) with no bar drawn | 零值只有文字没有图形，解析器可能漏掉该行/列的单元格，导致表格缺格或错位对齐。 |
| `panel_color_coded_bars` | f1 | each column uses its own fill: navy, cyan, teal, grey; no legend explains the colours | 颜色区分的是面板而非系列，读值时必须靠列标题而不能靠图例来定位。 |
| `per_panel_baseline_rule` | f2 | a faint vertical rule at the left of each of the four bar columns acts as the only baseline | 该竖线是每个面板的零点起线，是判断条长归属哪一列的唯一视觉参照。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

数值本身全部印在条上（46、13、27、21、29），读数不需要靠刻度，所以第2步不是瓶颈。真正卡住的是寻址：一个值要三把钥匙——图小标题（by firm size / by tenure at firm）、列面板名（如 $1.01bn–$5.00bn）、行名（$1.00m–$3.00m）。而 `13` 在同一面板内出现三次、`21` 在两张图各出现一次、`7`/`5`/`2` 更是遍布全页，若解析器把四栏压成一张无列头的表，或把两张图合并，任何搜索都无法唯一定位。此外八个 `0` 只有文字无条形，容易导致列错位。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 通用 | 把面板维度写入键（panel_key），并在导出表中为每一列保留列头文字 | 记录字段：新增 panel_key，条件行中把 small_multiples_4 与 shared_axis 组合成一类 | 有列头面板名 vs 无列头（四栏压平）时，重复值（如同一面板内三个 13）的唯一寻址成功率 |
| P7 | 一类出版方 | 标题拆成 number/title/subtitle/unit 四段，允许总标题带 (%) 而子图标题不带单位 | 样式字段：heading 块（title=`Personal revenue targets (%)`，subtitle=`Personal revenue targets, by firm size`） | 单位只出现在总标题、子标题不带单位时，数值百分比语义的恢复率 |
| P6 | 通用 | value_label_inside 与 value_label_outside 在同一图内按条长混用 | 样式维度：标签位置改为按条长阈值切换，而非全图统一 | 标签位置混用（短条外置、长条内置）对标签-条对应关系判定的影响 |
| new | 一类出版方 | 新组件 zero_value_printed_without_bar（零值只印 `0` 不画条） | 条件行：允许生成零值槽位，仅输出文字标签 | 含零值文字槽 vs 全部非零时，表格行列对齐错位率 |
| P3 | 这份文档自己的习惯 | 整页 markdown 导出，明确两张同页无编号图各自的粗体小标题与其表格的相对位置 | 页面级导出规则：multi_figure_page + 无 figure_number 的场景 | 同页两图共用同一 Source 文案时，标题作为粗体行置于表上 vs 缺失，对上下文归属的判定率 |
