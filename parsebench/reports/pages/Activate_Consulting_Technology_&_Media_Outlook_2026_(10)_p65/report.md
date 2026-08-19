# Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p65

![page](page.png)

## 1 · 样本

| 来源文档 | 标签组 | 抽查点 | 其中估读 |
|---|---|---|---|
| Activate_Consulting_Technology_&_Media_Outlook_2026_(10) | `untagged` | 9 | 0 |

该页为Activate Consulting关于美国游戏玩家分群的一张分组柱状图，展示Super/Avid/Casual三类玩家使用Mobile、Console、PC三种平台的比例，所有数值直接标注在柱顶，无数值轴。

## 2 · 抽查点与模型的定位

左半是基准的规则，右半是模型只看图给出的定位。**值给了模型，标签没有**——所以「需要哪些键」是预测，最后一列由程序判分。

| # | 值 | 规则用的标签 | 容差 | 落在 | 是哪个图元 | 印在图上 | 模型预测的键 |
|---|---|---|---|---|---|---|---|
| 1 | 93 | `MOBILE` · `SUPER GAMERS` | 1% | f1 | the SUPER GAMERS² MOBILE bar (leftmost, dark navy) | 是 | `SUPER GAMERS²` · `MOBILE` |
| 2 | 82 | `CONSOLE` · `SUPER GAMERS` | 1% | f1 | the SUPER GAMERS² CONSOLE bar (middle, mid-blue) | 是 | `SUPER GAMERS²` · `CONSOLE` |
| 3 | 89 | `PC` · `SUPER GAMERS` | 1% | f1 | the SUPER GAMERS² PC bar (right, teal) | 是 | `SUPER GAMERS²` · `PC` |
| 4 | 89 | `MOBILE` · `AVID GAMERS` | 1% | f1 | the AVID GAMERS³ MOBILE bar (dark navy) | 是 | `AVID GAMERS³` · `MOBILE` |
| 5 | 56 | `CONSOLE` · `AVID GAMERS` | 1% | f1 | the AVID GAMERS³ CONSOLE bar (mid-blue) | 是 | `AVID GAMERS³` · `CONSOLE` |
| 6 | 70 | `PC` · `AVID GAMERS` | 1% | f1 | the AVID GAMERS³ PC bar (teal) | 是 | `AVID GAMERS³` · `PC` |
| 7 | 87 | `MOBILE` · `CASUAL GAMERS` | 1% | f1 | the CASUAL GAMERS⁴ MOBILE bar (dark navy) | 是 | `CASUAL GAMERS⁴` · `MOBILE` |
| 8 | 34 | `CONSOLE` · `CASUAL GAMERS` | 1% | f1 | the CASUAL GAMERS⁴ CONSOLE bar (mid-blue) | 是 | `CASUAL GAMERS⁴` · `CONSOLE` |
| 9 | 24 | `PC` · `CASUAL GAMERS` | 1% | f1 | the CASUAL GAMERS⁴ PC bar (teal) | 是 | `CASUAL GAMERS⁴` · `PC` |

**程序核对**（模型没有看到左半的标签列）：

- 无矛盾

## 3 · 图表分解

| 图 | 类型 | 方向 | 面板 | 系列 | 类目 | 图元 | 数值写出 | 值轴刻度 |
|---|---|---|---|---|---|---|---|---|
| f1 | `grouped_bar` | vertical | 1 | 3 | 3 | 9 | 全部 | （不画值轴） |

- **f1** SHARE OF GAMERS¹ USING EACH PLATFORM FOR GAMING IN THE LAST 12 MONTHS / U.S., 2025　[图上方]　单位 `% GAMERS¹ BY SEGMENT`
  - 来源行：Sources: Activate analysis, Activate 2025 Consumer Technology & Media Research Study (n = 4,026)

## 4 · 组件清单

| key | 组件 | 在哪 | 我们 | 证据（模型写的） |
|---|---|---|---|---|
| `grouped_bar` | 分组条 | f1 | 有 | three bars side by side in each of SUPER GAMERS², AVID GAMERS³, CASUAL GAMERS⁴ slots |
| `annotation_callout` | 绘图区内的说明框 / 引线注解 | f1 | **无** | green hand-drawn ovals circling Super Gamers' three bars, the 89% and the 87% bars |
| `no_value_axis` | 没有值轴刻度，只有基线 | f1 | **无** | only a black baseline under the bars; no ticks or numbers on any vertical axis |
| `source_note_lines` | source / note 行在图下方 | f1 | 有 | numbered notes 1.-4. plus "Sources: Activate analysis, Activate 2025 Consumer Technology & Media Research Study (n = 4,026)" |
| `legend_beside_plot` | 图例在绘图区左侧或右侧，排成一列 | f1 | 有 | MOBILE / CONSOLE / PC icon-and-name column at the left edge, level with the bars |
| `unit_in_axis_or_title` | 单位写在轴标题 / 副标题 / 图题里，值轴上只有裸数字 | f1 | **无** | banner ends "% GAMERS¹ BY SEGMENT"; bars themselves carry no axis unit |
| `footnote_marker` | 标题或标签里的脚注上标 | f1 | **无** | "SHARE OF GAMERS¹", "SUPER GAMERS²", "AVID GAMERS³", "CASUAL GAMERS⁴" carry superscript digits |
| `value_label_outside` | 数值标签在图元外 / 带引线 / 带边框 | f1 | **无** | 93%, 82%, 89%, 56%, 70%, 34%, 24% printed above each bar top |
| `panel_background` | 绘图区带底色，不是白底 | f1 | **无** | plot area sits on a pale blue hexagon-patterned tint rather than white |
| `icon_category_axis` | 类目轴用图标代替文字 | f1 | **无** | pictograms of phone, gamepad and desktop precede MOBILE, CONSOLE, PC in the side legend |

词表 65 项，本页出现 10 项，其中我们画不出来的 7 项。

### 新组件

| 名字 | 在哪 | 证据 | 为什么要紧 |
|---|---|---|---|
| `heading_in_filled_banner` | f1 | heading set in white type on a solid blue full-width band above the plot | 标题与单位在色带中，解析器可能把它当作页面横幅而非图表标题，导致数值失去上下文键。 |
| `mixed_weight_heading_line` | f1 | banner is bold up to "LAST 12 MONTHS," then lighter "U.S., 2025, % GAMERS¹ BY SEGMENT" | 、隷区分只靠字重。单/单位靠字重区分。/在能相同一行。副单/单位。区仴单位同在一行，需按字重切分标题、副标题与单位。 |
| `handdrawn_highlight_oval` | f1 | three green marker-style ellipses drawn over bar tops and their value labels | 手绘椭圆覆盖数值标签，可能遮挡或干扰OCR识别93%与89%等数字。 |
| `series_legend_as_stacked_rows` | f1 | MOBILE, CONSOLE, PC listed as three stacked rows separated by horizontal rules at left | 该竖排图例暗示柱内从左到右的系列顺序，读值时必须靠位置而非颜色标注来定系列。 |

## 5 · 难在哪

卡在 **第三步 · 标签关联**。

九个数值全部印在柱顶，读数不成问题（步骤2无风险，也没有刻度轴可参照）；真正的障碍是寻址：每个值都需要“分群×平台”两个键，而平台名只出现在左侧竖排图例（MOBILE/CONSOLE/PC）里，柱子本身无标签，89%在SUPER GAMERS²-PC与AVID GAMERS³-MOBILE两处重复出现，若表格丢掉平台维度或列顺序，89%就无法唯一定位。此外三个分群标签都带上标数字（SUPER GAMERS²），逐字匹配容易失配。

## 6 · 对 data pipeline 的意见

| 归入 | 通用度 | 加什么 | 改哪里 | 新增哪一行消融 |
|---|---|---|---|---|
| P6 | 一类出版方 | legend_beside_plot 与 icon_category_axis 组合：系列名以带图标的竖排列于绘图区左侧 | 样式条件行中新增 legend_position=beside_left 且 legend_item_icon=true | 图例位于侧栏（含图标）vs 常规下方图例时，系列键被正确写入表头列名的比例 |
| P7 | 一类出版方 | 新组件 heading_in_filled_banner（标题+单位置于满宽实色色带内） | 标题记录字段：新增 heading_style=banner 及 heading placement=above 的渲染分支 | 色带式标题 vs 普通文本标题时，图题/单位被导出为粗体或标题行的比例 |
| P3 | 一类出版方 | footnote_marker：类别名与标题内嵌上标数字（SUPER GAMERS²） | 类别名与标题字段允许附带上标标记，并在注释区生成对应编号注释 | 类别名带上标 vs 不带上标时，寻址键逐字匹配成功率 |
| P6 | 这份文档自己的习惯 | 新组件 handdrawn_highlight_oval（手绘绿色椭圆圈注覆盖柱顶与数值标签） | 标注层样式：新增 highlight_shape=hand_drawn_ellipse，可覆盖多个柱及其数值标签 | 数值标签被圈注图形叠压 vs 未叠压时，标签数字被正确读出的比例 |
| P1 | 一类出版方 | no_value_axis 与 value_label_outside 同时出现（仅基线，无刻度） | 轴条件行：value_axis=none 且 value_label=outside 的组合 | 无数值轴仅靠外置标签 vs 有刻度轴时，数值召回率对比 |
