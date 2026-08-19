# WEF_Navigating_Global_Financial_System_Fragmentation_2025_p12

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| WEF_Navigating_Global_Financial_System_Fragmentation_2025 | `untagged` | 4 | 0 |

本页顶部为 FIGURE 4：按货币划分的全球外汇储备、出口计价与日均外汇交易份额的分组柱状图（左侧%轴两组、右侧十亿美元轴一组，共用图例），下方为正文段落与 1.3 节标题。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 58% | `Global exchange reserves (%)` · `USD` | 1% | f1 | the USD bar in the 'Global exchange reserves' group of the % panel | 是 | `Global exchange reserves` · `USD` · `%` |
| 2 | 22% | `Share of export invoicing (%)` · `EUR` | 1% | f1 | the EUR bar in the 'Share of export invoicing' group of the % panel | 是 | `Share of export invoicing` · `EUR` · `%` |
| 3 | $17 | `Share of daily foreign transactions (Billions of US dollars)` · `JPY` | 1% | f1 | the JPY bar in 'Share of daily foreign transactions' on the Billions of US dollars panel | 是 | `Share of daily foreign transactions` · `JPY` · `Billions of US dollars` |
| 4 | 4% | `Share of export invoicing (%)` · `RMB` | 1% | f1 | the JPY bar in 'Share of export invoicing'; the RMB bar in the same group also prints 4% | 是 | `Share of export invoicing` · `JPY` · `%` |

**程序核对**（模型没有看到左半的标签列）：

- 模型预测的定位标签漏掉了规则实际用的标签——1 of 4 predicted key sets miss a rule label: 4%

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 2 | 5 | 2 | 15 | 全部 | 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 |

- **f1** FIGURE 4 / Share of global exchange reserves, global export invoicing and foreign transaction by currency　[图上方]　单位 `%; Billions of US dollars`
  - 来源行：Source: Share of global foreign exchange reserves: IMF's Currency Composition of Official Foreign Exchange Reserves Q2 2024. Share of export invoicing: Bloomberg Intelligence FX Strategy Dashboard. Share of foreign transactions: BIS Triennial Survey, Data Portal. Oliver Wyman analysis

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | five bars USD, EUR, GBP, JPY, RMB stand side by side within each category slot |
| `shared_legend` | 跨面板共享图例 | f1 | 有 | one legend row 'USD EUR GBP JPY RMB' below both the % panel and the Billions panel |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | 'Note: To calculate share of export invoicing...' and 'Source: Share of global foreign exchange reserves: IMF's...' below plots |
| `legend_below_plot` | 图例在绘图区下方 | f1 | 有 | legend pills sit centred beneath the plots, outside them |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | axis carries bare 0-100 ticks; scale words '%' and 'Billions of US dollars' only above the axis |
| `footnote_marker` | 标题或标签里的脚注上标 | page | **无** | superscript '13' and '14' attached to body-text sentences beside the figure section |
| `axis_title_above_axis` | 值轴标题 / 单位符号写在轴的正上方，而不是沿轴竖排 | f1 | **无** | '%' sits above the 100 tick on the left plot, 'Billions of US dollars' above 100 on the right |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | '58%', '48%', '$88', '$7' printed just above the top of each bar |
| `wrapped_category_labels` | 类目名折行，或几十个类目排成长列 | f1 | **无** | category labels are long phrases: 'Share of daily foreign transactions', 'Global exchange reserves' |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | the whole figure band including both plot areas is filled light grey, body text below is white |
| `hgrid_only` | 只有水平网格线，没有垂直网格线 | f1 | 有 | thin horizontal rules at each 10-unit tick, no vertical grid lines |

词表 65 项，本页出现 11 项，其中我们画不出来的 6 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `per_panel_unit_differs` | f1 | left panel axis headed '%', right panel axis headed 'Billions of US dollars', both ticked 0 to 100 | 两个面板刻度数字完全相同但单位不同，读值时必须先绑定面板才能确定是百分比还是十亿美元，否则 $17 会被误读为 17%。 |
| `unit_symbol_in_value_label` | f1 | labels printed as '58%', '22%' on the left and '$88', '$17' on the right | 数值标签自带单位符号，检索字符串必须包含 '%' 或 '$'，纯数字匹配会失败。 |
| `multi_category_single_axis_panel` | f1 | left plot area holds two category slots ('Global exchange reserves', 'Share of export invoicing') under one continuous % axis | 同一坐标区内含两个语义组，行键需要同时给出组名与货币名，否则 4% 无法唯一定位。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

四个值全部印在柱顶，读数不是瓶颈（步骤2容易）；难点是寻址：一个值需要面板单位（'%' 对 'Billions of US dollars'）+ 组名 + 货币名三层键。'Share of export invoicing' 组里 JPY 与 RMB 都是 4%，只给组名和数值无法区分；而 '4%' 在 'Global exchange reserves' 组也不存在，但 '$17' 与 '17' 之间的单位差异又要靠面板标题 'Billions of US dollars' 才能确定。解析器若把左右两个坐标区合成一张表，0–100 的相同刻度会把两种单位混为一体。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P2 | 一类出版方 | per_panel_unit_differs（新组件）：同一图内各面板单位不同但刻度数字相同 | 面板样式字段增加 per_panel_unit，允许每面板独立 unit_text 并在坐标区上方单独排印 | 面板单位一致 vs 面板单位不同 → 单位错配读值率 |
| P6 | 通用 | unit_symbol_in_value_label（新组件）：数值标签带 '%' 或 '$' 前后缀 | 标签格式字段（value_label_format）增加前缀/后缀符号选项 | 纯数字标签 vs 带单位符号标签 → 字符串命中率 |
| P7 | 通用 | axis_title_above_axis 与 unit_in_axis_or_title 的组合（裸 0–100 刻度 + 顶部单位词） | 标题记录拆分为 number/title/subtitle/unit + 单位放置位置字段 | 单位在轴标题旁 vs 单位置于顶端刻度上方 → 单位召回 |
| P2 | 一类出版方 | multi_category_single_axis_panel（新组件）：一个坐标区内并列两个语义类别组 | 条件行增加“每面板类别组数”，并要求行键同时输出组名与系列名 | 单组/面板 vs 双组/面板 → 重复数值（两个 4%）的唯一寻址成功率 |
