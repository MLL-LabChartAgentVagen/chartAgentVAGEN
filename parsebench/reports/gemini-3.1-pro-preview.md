# gemini-3.1-pro 自己写的两份报告

模型 `gemini-3.1-pro-preview`。正文与排序原样印出，没有编辑；数字在第 3 节逐条对账。「归入哪条 P」的取值域：

- `P1` = readable becomes a per-mark attainable precision instead of a boolean gate
- `P2` = the panel dimension enters the key (panel_key)
- `P3` = a whole-page markdown export, and where a title or panel name sits relative to the table
- `P4` = how often each chart family is generated, a weight vector -- not what a family looks like
- `P5` = raise the density cap, making density a controlled variable
- `P6` = three more style dimensions: value-label placement, tick format and unit position, negative values and the zero line
- `P7` = the figure title becomes a field of its own: number, title, subtitle, unit, and where the heading block sits
- `P8` = colour or highlight encodes an attribute the legend does not carry, and that attribute has to enter the key
- `P9` = two value axes in one panel and bar+line mixed marks: a value has to record which axis and which mark shape it was read from
- `new` = none of the nine covers it

## 1 · 样例 overview

它读完自己那批页面之后写的。

**结论**：5%的绝对读取容差拦截了多数无标签图表，且异构面板与混合图元严重破坏了标签关联。

### 它的排序

| # | what | why | 证据页 / case | affects | 对分数 | 对能力 | 新增的消融行 | 归入哪条 P |
|---|---|---|---|---|---|---|---|---|
| 1 | 读取精度 (value_label_inside) | Opus卡在步骤2达67次，85图未印数值。无标签时靠刻度估算极易超出5%容差而阻断。 | 05021ff2-en_p20、2024-ltra_corrected_july_2025_p27、EnergyTechnologyPerspectives2024_p53 | 2 | 使大量因未印数值而卡在容差门控的页面获得可评分机会。 | 将是否在图元内部印制数值标签转化为生成器的可配置维度。 | 可读性降级为连续精度的惩罚而非布尔门控 | P1 |
| 2 | 复合图表 (compound) | 复合与多面板分占22次。共享分类的子图若无面板隔离，必在步骤三发生同名键值碰撞。 | CleanEnergyMarketMonitorMarch2024_p13、employment_and_social_developments_in_europe_esde_2024_report_p34 | 3 | 解决跨面板同名分类的匹配碰撞，大幅提升关联成功率。 | 生成器能排版带独立标题与坐标轴的多面板结构组合图表。 | 面板维度进入寻址键 | P2 |
| 3 | 混合标记 (mixed_marks) | 混合图元命中29次并常伴随双轴。若未记录形状和归属轴，会导致读数与映射彻底错乱。 | 9f653ca1-en_p23、b263dc5d-en_p160、pwc-semiconductor-and-beyond-2026-full-report_p18 | 2,3 | 消除由于轴对齐错误或标记混淆导致的读取与关联双重失败。 | 赋予管线在同面板叠加多种标记并分配独立双Y轴的能力。 | 数值必须记录其归属的坐标轴与图元形状 | P9 |
| 4 | 颜色编码 (color_encodes_extra_attribute) | 颜色常编码额外属性出现15次，缺失此隐性维度导致无法组装完整匹配键，在第三步受阻。 | 2025-EIS_p37、b263dc5d-en_p144、b263dc5d-en_p160 | 3 | 补全缺失的隐性语义维度，恢复长键直接匹配的成功率。 | 支持利用数据直接驱动局部高亮样式，摆脱纯系列颜色限制。 | 图例未承载的颜色或高亮属性强制进入寻址键 | P8 |
| 5 | 折行标签 (wrapped_category_labels) | 折行标签出现31次，断行截断易导致提取出的键名残缺，进而无法在第三步完成标签对齐。 | FPA-guide-to-data-visualization_p5、World_Inequality_Report_2026_p99 | 1,3 | 修复因文本截断带来的标签不匹配，找回丢失的关键关联。 | 使生成引擎能够原生处理分类轴长文本的多行折叠与排版。 | 整页Markdown流导出与图表外层级标题上下文位置提取 | P3 |
| 6 | 非底线负值 (negative_values) | 负值图表达27次。零轴非底与反向延展改变了基础的视觉映射，在第二步严重干扰刻度估读。 | GWR-2024_Layout_E_RGB_Web_p33、ac8b3538-en_p153 | 2 | 大幅减少对负值分叉图表或浮动零轴图表因定位偏差的拒绝。 | 支持生成带负区间坐标域、居中零线以及图元双向延展。 | 新增数值标签位置、轴单位格式与零线位置样式维度 | P6 |

### 正文

通过对100页报告的全面评估，视觉解析当前面临的最大挑战是绝对读取精度与异构组合结构。首先，数据源中高达85张图表处于完全未印制标签状态，迫使提取模型完全依靠纵坐标刻度进行估算。这就导致了opus-5模型卡在步骤2的次数高达67次。由于部分图表网格间距极大，用肉眼或像素估算精确值极易打破5%的误差容限，因此基准亟须将读取门控转为精度的连续惩罚，避免一刀切的阻断。其次，复杂的图表面板严重破坏了步骤3的键值映射。以出现22次的复合图表和同样命中22次的小多面板为例，如果底层缺乏独立的面板空间隔离，同名分类键必然会发生跨图表的交叉污染。同理，命中29次的混合标记常与双Y轴伴随出现，系统必须记录所有数值归属的物理纵轴与对应的图元标记形状，才能杜绝指代错乱。隐性的颜色特征同样是一大阻碍：额外属性颜色编码达15次，当颜色代表的显著性或高亮状态未在图例中给出时，由于遗失了这一维度，解析系统将无法组装出符合原表的完整长键。不仅如此，版面排版的物理噪声也极为严峻。命中31次的长文本标签折行极易诱发OCR截断丢失原义，而出现27次的负值序列造成的浮空零线彻底重构了图表边界映射。图表生成管线必须有能力原生绘制带有隔离轴系的独立面板簇，并将诸如内部标签有无、零线相对位置以及底层数据的高亮着色等维度彻底抽象为系统可调参数。

### 局限（它自己写的）

> 受限于100页的抽样规模，无法验证边缘版式的全量影响。未印制标签的点位仅通过视觉刻度推断，存在不可避免的主观误差。缺失图例的特殊颜色高亮均为推测属性。

## 2 · 失败 overview

它读完自己那批 case 的归因之后写的。

**结论**：寻址失败占总失败三分之二，主要源于表格结构错位与上下文丢失；数值插值读取精度不足是第二大瓶颈。

### 它的排序

| # | what | why | 证据页 / case | affects | 对分数 | 对能力 | 新增的消融行 | 归入哪条 P |
|---|---|---|---|---|---|---|---|---|
| 1 | key_off_the_value_row | label_unlinked 占失败 66.8%，大多去向为 in_a_table_but_not_addressing。说明内容均提取，但因合并单元格等复杂结构导致键值行列层级错位。 | label_unlinked-01、label_unlinked-02、label_unlinked-04 | 3 | 可挽回大部分 label_unlinked 损失，逼近 95.4% 的全对上界。 | 能产出多级表头和合并单元格的复杂层级表格，跳出扁平结构。 | 复杂表头与多级索引生成 | new |
| 2 | value_interpolated_off_axis | value_off 占 21.9%。未印在图上时通过率跌至 70.4%（远低于印制时的 97.2%），表明模型对坐标轴插值读取精度严重不足。 | 数值是否印在图上、value_off-41、value_off-43 | 2 | 大幅减少 value_off 导致的错误，将无标签图表通过率提升至 90% 以上。 | 将可读性建模为连续可达精度取代布尔门控，支持生成任意刻度间距。 | 连续数值读取精度控制 | P1 |
| 3 | key_only_in_prose | 缺失键进入 plain_text_only 或完全丢失，常由图表标题、面板名称未进入表格引起，导致大量 label_unlinked 错误无法通过。 | label_unlinked-03、row_missing-12、row_missing-14 | 1,3 | 减少 row_missing 中上下文缺失错误，提升约 5% 整体指标。 | 标题和单位将作为独立字段，并在表格周围生成连贯 Markdown。 | 独立标题块与上下文生成 | P7 |
| 4 | scale_word_ignored | unit_mismatch 占 4.0%，多因漏乘量级或将单位字符（如 B）直接写入数值单元格，导致纯数字正则匹配失败。 | unit_mismatch-21、unit_mismatch-22、unit_mismatch-24 | 2 | 解决单位和量级错配，挽回 4.0% 的 unit_mismatch 损失。 | 能够灵活控制单位符号和量级在图表各部分中的位置及格式表达。 | 单位位置与数值格式化 | P6 |
| 5 | 图表视觉干扰项 | panel_background 使未印数值图表通过率骤降 34.8%，说明背景色块严重干扰坐标系对齐和刻度插值读取。 | 控制组（图上一个数值都不写的点）内，各组件的通过率差 | 2 | 移除或优化背景渲染可直接填补这 34.8% 的控制组通过率差距。 | 引入控制图表视觉样式维度（如背景），增强模型抗干扰能力。 | 图表视觉样式维度干扰控制 | P6 |

### 正文

本次运行评测了 4864 个抽查点，按页平均通过率为 82.8%。寻址失败（如 label_unlinked 和 row_missing）占据了绝大部分错误，若全部修正，按页平均可达 95.4% 的理论上界。第一大瓶颈在于表格结构的提取错位（key_off_the_value_row）。在占比 66.8% 的 label_unlinked 错误中，多达 627 个去向为 in_a_table_but_not_addressing。这表明解析器大多成功提取了文字，但因无法正确识别合并单元格、多级表头或行列层级，导致键和数值在结构上脱节。生成管线必须能够产出具备复杂层级的测试表，而非仅限扁平表格。第二大瓶颈是基于坐标轴的数值插值读取（value_interpolated_off_axis）。value_off 占失败的 21.9%，当图元未直接标注数值时，模型通过率仅为 70.4%（显著低于标注时的 97.2%）。此外，图表视觉元素对读取精度的干扰极大——在不写数值的控制组中，带有 panel_background 的图表通过率骤降 34.8%。管线需将可读性建模为连续精度（P1），并引入背景网格等视觉干扰维度的控制。第三，图表标题、面板名称与上下文丢失（key_only_in_prose 和 panel_name_dropped）。部分键仅存在于图表标题或说明段落中，导致 57 个走向 plain_text_only，46 个完全丢失。管线应将标题、副标题作为独立字段（P7），并增强完整页面的 Markdown 排版能力。第四是单位换算与格式解析故障（scale_word_ignored）。unit_mismatch（4.0%）中多发量级忽略或将“B”、“%”等符号直接写入数据单元格导致纯数字匹配失败。管线需将单位位置、数据标签格式作为独立维度进行控制测试（P6）。

### 局限（它自己写的）

> 本报告机制推断基于 50 个失败样本的定性抽样，罕见形态覆盖可能不全。对 value_off 中的极高误差，因无原图对照，只能推断为插值精度不足，难以确定是否叠加异常。

## 3 · 它引用的数字

逐条查这个数在程序的表里存不存在。全部 24 条里 9 条是带小数的比率或大计数（「可判别」= 是），其中 9 条找得到；其余是小整数，几百个格子里总能撞上一个，找到不算证据。「最接近的一格」是按名字相似度猜的，模型的答案里没有记它读了哪一格。找不到的**记录不改写**。

| claim | 模型自报的值 | 它说的来源 | 程序表里有没有这个数 | 可判别 | 最接近的一格 |
|---|---|---|---|---|---|
| 抽样评估的页面总数 | 100 | 自己数的 | 找到 | 否 | 抽样 / 页数 |
| 未印制数值标签的页面数 | 85 | 数值印不印 / 稠密度档 / 标题位置 / 卡在哪一步（三家并列） | 找到 | 否 | 数值印不印 / claude-opus-5 / none |
| 阻断验证的步骤编号 | 2 | 数值印不印 / 稠密度档 / 标题位置 / 卡在哪一步（三家并列） | 找到 | 否 | 组件表 `axis_title_below_plot` / gemini-3.1-pro-preview 文档数 |
| opus-5在第二步阻断的次数 | 67 | 数值印不印 / 稠密度档 / 标题位置 / 卡在哪一步（三家并列） | 找到 | 否 | 卡在哪一步 / claude-opus-5 / 2 |
| 数值验证的误差容限 | 5 | 自己数的 | 找到 | 否 | 组件表 `data_link_below_figure` / gemini-3.1-pro-preview 文档数 |
| 标签映射步骤编号 | 3 | 数值印不印 / 稠密度档 / 标题位置 / 卡在哪一步（三家并列） | 找到 | 否 | 组件表 `abbrev_category_axis` / gemini-3.1-pro-preview 文档数 |
| 复合图表类型次数 | 22 | 类型配比（三家并列） | 找到 | 否 | 类型 / claude-opus-5 / compound |
| 小型多面板命中数 | 22 | 你自己那批答案里的组件计数 | 找到 | 否 | 卡在哪一步 / gemini-3.1-pro-preview / 3 |
| 混合图元命中数 | 29 | 你自己那批答案里的组件计数 | 找到 | 否 | 组件表 `mixed_marks` / claude-opus-5 页数 |
| 额外颜色编码次数 | 15 | 你自己那批答案里的组件计数 | 找到 | 否 | 组件表 `axis_title_above_axis` / gemini-3.1-pro-preview 文档数 |
| 标签折行组件命中数 | 31 | 你自己那批答案里的组件计数 | 找到 | 否 | 组件表 `mixed_marks` / gpt-5.6-sol 页数 |
| 负值结构命中次数 | 27 | 你自己那批答案里的组件计数 | 找到 | 否 | 组件表 `unit_in_axis_or_title` / gemini-3.1-pro-preview 文档数 |
| 平均通过率 | 82.8% | 自己数的 | 找到 | 是 | 单变量 定位需要几个键 / 2 通过率 |
| 抽查点 | 4864 | 自己数的 | 找到 | 是 | 失败运行 / points |
| 寻址失败全对上界 | 95.4% | 自己数的 | 找到 | 是 | 失败运行 / ceiling |
| label_unlinked 占失败 | 66.8% | 失败形态 | 找到 | 是 | 形态表 `label_unlinked` / 占失败 |
| 去向为 in_a_table_but_not_addressing | 627 | 失败形态 | 找到 | 是 | 形态表 `label_unlinked` / 失联键去向 in_a_table_but_not_addressing |
| 去向为 plain_text_only | 57 | 失败形态 | 找到 | 否 | 形态表 `label_unlinked` / 失联键去向 plain_text_only |
| 去向为 absent_from_the_output | 46 | 失败形态 | 找到 | 否 | 形态表 `label_unlinked` / 失联键去向 absent_from_the_output |
| value_off 占失败 | 21.9% | 失败形态 | 找到 | 是 | 形态表 `value_off` / 占失败 |
| 数值未印在图上的通过率 | 70.4% | 单变量通过率 | 找到 | 是 | 一致率表 卡在哪一步 / rate |
| 数值印在图上的通过率 | 97.2% | 单变量通过率 | 找到 | 是 | 控制组差值 `heterogeneous_panel_types` / 有它的通过率 |
| unit_mismatch 占失败 | 4.0% | 失败形态 | 找到 | 否 | 组件表 `shaded_band` / gemini-3.1-pro-preview 文档数 |
| panel_background 导致的通过率差 | 34.8% | 控制组（图上一个数值都不写的点）内，各组件的通过率差 | 找到 | 是 | 判分表 gpt-5.6-sol / missed_label_3 |
