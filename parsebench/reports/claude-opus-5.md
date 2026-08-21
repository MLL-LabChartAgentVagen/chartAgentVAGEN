# opus-5 自己写的两份报告

模型 `claude-opus-5`。正文与排序原样印出，没有编辑；数字在第 3 节逐条对账。「归入哪条 P」的取值域：

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

**结论**：这 100 页的瓶颈是读数：85 页不印数值、67 页卡在容差，先把 readable 从布尔门改成每标记可达精度，其余都是次级。

### 它的排序

| # | what | why | 证据页 / case | affects | 对分数 | 对能力 | 新增的消融行 | 归入哪条 P |
|---|---|---|---|---|---|---|---|---|
| 1 | `readable` 布尔门（值不印 + 5% 容差）→ 每标记可达精度 | 卡在第 2 步 67 页，数值印不印 none=85 页，两个计数同向；这是唯一同时是分数瓶颈与生成约束的量。 | 05021ff2-en_p20、Snapshot-of-Global-PV-Markets_2025_p12、2024-ltra_corrected_july_2025_p29、b263dc5d-en_p95、employment_and_social_developments_in_europe_esde_2024_report_p84 | 2 | 直接动第 2 步那 67 页：读不到的格子由判错改为按可达精度计分。 | 生成时每个标记可声明可读位数，容差随刻度密度与标记大小自动放宽。 | 每标记可达精度 on/off（默认 = 现行布尔 readable） | P1 |
| 2 | 单位位置 / 值标签位置 / 零线三维（`unit_in_axis_or_title`、`no_value_axis`、`value_label_outside`、`negative_values`） | 85、18、22、27 页四项在「我们画得出」一栏全是否，是覆盖面最大的能力缺口，且后三项都挂在第 2 步。 | 9f653ca1-en_p23、GWR-2024_Layout_E_RGB_Web_p33、US_Professional_Services_Partner_Compensation_Survey_2024_p19、ac8b3538-en_p153、Feaco-Survey-2023-2024_p8 | 2 | 改动无值轴与负值页的读值路径，涉及 18 页无轴、27 页负值。 | 单位位置、标签内外、零线样式成为三个可配维度，默认保持轴内单位与柱顶标签。 | 单位位置 × 值标签位置 × 零线样式 的三维交叉行 | P6 |
| 3 | 面板维度进键（`panel_title_per_panel`、`small_multiples_4`、`per_panel_axis_range`） | 面板题 30 页、切板 22 页、各板独立值域 16 页；第 3 步的 30 页失败里，缺面板名是最常见的一种键缺。 | 2024_healthatglance_rep_en_p115、9f653ca1-en_p29、ac8b3538-en_p93、World_Inequality_Report_2026_p78、b263dc5d-en_p181、ac8b3538-en_p62 | 2,3 | 面板名入键可救第 3 步中同名行跨板串位的部分；独立值域也影响读值。 | 能生成各面板自带量程与标题的小倍数，键中带 panel_key。 | panel_key 入键 on/off × 面板共享/独立值域 | P2 |
| 4 | 双值轴与混合图元（`mixed_marks` + 同向两条值轴 + 标记形状承载系列） | 混合图元 29 页；同向两条值轴三家冲突 7 页；词表外 `marker_shape_encodes_series` 7 页。值不记轴与记号就不可核。 | 9f653ca1-en_p28、r_qt1212e_p9、wtr24_ch2_e_p14、GWR-2024_Layout_E_RGB_Web_p58、2025-EIS_p37、employment_and_social_developments_in_europe_esde_2024_report_p76 | 2,3 | 同一像素高度两读的页，值能被判为对；影响第 2、3 步。 | 一个面板可画左右双轴＋柱线混排，键里记录轴 id 与标记形状。 | 轴 id / 标记形状入键 on/off | P9 |
| 5 | 整页 markdown 导出与图外文本（`multi_figure_page`、`side_text_bullets`） | 一页多图 31 页、旁栏正文 24 页；残差里 interpretation 段与编号文本框各 2 页，落在第 1、4 步。 | 2024_healthatglance_rep_en_p115、Digital_News-Report_2022_p63、Treasury_Bulletin_2025_06_p21、US_Professional_Services_Partner_Compensation_Survey_2024_p20、natural-catastrophe-and-climate-report-2023_p72 | 1,3,4 | 决定「有没有表」和图题/面板名相对表的位置，影响第 1、4 步。 | 能输出整页多图＋并排正文的 markdown，标题块位置可配。 | 整页导出 on/off × 标题块置于表前/表后 | P3 |
| 6 | 颜色承载图例外的属性（`color_encodes_extra_attribute`、`highlighted_category`） | 15 页与 23 页，两项都标画不出；显著性、绩效组、汇总行不进键，整列会错位，直接命中第 3 步。 | ac8b3538-en_p130、ac8b3538-en_p55、b263dc5d-en_p144、b263dc5d-en_p160、2025-EIS_p39 | 3 | 让「深色=显著」「红=OECD」成为键的一段，减少第 3 步误配。 | 可生成第三变量着色，并把该属性写进单元格键。 | 属性着色入键 on/off（默认颜色仅表系列） | P8 |
| 7 | 密度上限（`dense_marks_100plus`） | 61–150 档 32 页、151–400 档 6 页、>400 档 6 页，而 100+ 标记项仍标画不出；密度是读数难度的主因之一。 | Quarterly-Sector-and-Investment-Research-Update-Q1-2025_p12、EnergyTechnologyPerspectives2024_p48、sri-sigma-natural-catastrophes-1-2025_p27、b263dc5d-en_p95、employment_and_social_developments_in_europe_esde_2024_report_p30 | 2 | 密度可控后，容差与密度的关系可分离测量，间接影响第 2 步。 | 标记数可作为受控变量拉到 400 以上，而非默认稀疏。 | 密度档 ≤20 / 21–60 / 61–150 / 151–400 / >400 逐档 | P5 |
| 8 | 族权重向量（含 `horizontal_bars` 与 compound 配比） | 横向条 20 页仍画不出；compound 我记 22 张、另两家 32 与 5 张，类型冲突 40 页——配比本身不稳，先当权重调。 | US_Professional_Services_Partner_Compensation_Survey_2024_p11、US_Professional_Services_Partner_Compensation_Survey_2024_p19、deloitte-2025-global-automotive-consumer-study-january-2025_p17、FPA-guide-to-data-visualization_p20、EnergyTechnologyPerspectives2024_p48 | — | 度量看不见它 | 族生成频率成为一个权重向量，横向条与 compound 可按目标配比抽样。 | 族权重：均匀 / 对齐本基准配比 两组 | P4 |
| 9 | 图题块成为独立字段（编号、标题、副标题、单位、位置） | 标题位置 above 129、below 7，第 4 步在我这列 0 页——分数几乎不动，但四层标题是复现版面的必需件。 | pdf_d2e0103f64cd_p29、TSLA-Q4-2024-Update_p9、sri-sigma-natural-catastrophes-1-2025_p20、investing-in-education-2025-NC0125093ENN-1_p14、Renewables2025_1_p111 | 4 | 我这列第 4 步 0 页，分数近乎不动。 | 编号/标题/副标题/单位可分层排布，标题可置于图下或图侧。 | 标题块位置 above/below/beside × 单位独立成行 on/off | P7 |
| 10 | 图与非图的边界：编号文本框、表格当图 | 卡在第 1 步三家为 3 / 16 / 11，分歧最大；残差 narrative_data_box、numbered_text_box、zebra_striped_table_rows 各 2 页，说明「算不算图」无定义。 | 2025-EIS_p64、2025-EIS_p69、investing-in-education-2025-NC0125093ENN-1_p14、2024_healthatglance_rep_en_p77、TSLA-Q4-2024-Update_p9 | 1 | 直接决定第 1 步判定，我这列仅 3 页但另两家 16、11 页。 | 可生成带编号的文本框/斑马纹表格类「图」，默认关闭。 | 非图形图对象（Box/表格）纳入 on/off | new |

### 正文

## 结论
这 100 页的瓶颈是读数，不是画不画得出。我这一列卡在第 2 步 67 页，第 3 步 30 页，第 1 步 3 页，第 4 步 0 页；同时「一个数值都不印」的图有 85 张。两个计数同向：绝大多数格子只能对着刻度目测，而 readable 现在是个布尔门。先把它换成每标记可达精度（P1），这是唯一同时改分数与改生成约束的一项。

## 三件最该做的
1. **单位与零线（P6）**。`unit_in_axis_or_title` 85 页、`negative_values` 27 页、`value_label_outside` 22 页、`no_value_axis` 18 页，四项在「我们画得出」一栏全是否。覆盖面最大的能力缺口就在这里，且后三项都落在第 2 步。
2. **面板进键（P2）**。面板题 30 页、切板 22 页、各板独立值域 16 页。第 3 步那 30 页失败里，缺面板名是最常见的一种键缺。
3. **轴与标记形状进键（P9）**。`mixed_marks` 29 页；「同向两条值轴」三家冲突 7 页；词表外 `marker_shape_encodes_series` 7 页。一个值不写清读的是哪条轴、哪种记号，就不可核。

## 次一级
整页导出（P3）：一页多图 31 页、旁栏正文 24 页，决定「有没有表」与标题块位置。属性着色（P8）：15 页颜色编码第三变量、23 页单独高亮某类目，两项都画不出。密度（P5）：61–150 档 32 页、151–400 档 6 页、>400 档 6 页，密度该是受控变量。

## 度量看不见但仍要做的
族权重（P4）：横向条 20 页画不出；compound 我记 22 张而另两家是 32 与 5，类型判定冲突 40 页——配比本身不稳，先当权重向量调，不必新增画法。标题块（P7）：标题位置 above 129、below 7，而第 4 步在我这列是 0 页，分数几乎不动。

## 我这一列的偏差
组件一致率 67.1%，我的键命中率 69.0%。`footnote_marker` 我报 32 页、另两家 13 与 12；`wrapped_category_labels` 我 31 页对 15 与 9。这两项更像我的读法而非基准的性质，排序时已下调。

### 局限（它自己写的）

> 仅 100 页，且是我一列的读法；组件一致率 67.1%，`footnote_marker`、`wrapped_category_labels` 明显是我的偏差。像素级细节（网格线、底色、薄段）多为目测，真实数值表不可见，归属处有猜测。

## 2 · 失败 overview

它读完自己那批 case 的归因之后写的。

**结论**：本轮失败的主体不是数读歪，而是键没被画进表：定位类占失败三分之二，全改对即到 95.4%。

### 它的排序

| # | what | why | 证据页 / case | affects | 对分数 | 对能力 | 新增的消融行 | 归入哪条 P |
|---|---|---|---|---|---|---|---|---|
| 1 | `label_unlinked` / `key_off_the_value_row`：键被画在表体之外（图例、面板名、另一张表、正文） | 599 个占失败 66.8%，失联键 627 次落在"在表里但不定位"；寻址全对的上界 95.4%，比现在高 12.6 点，这些点全是"键写在哪"。 | 失败形态表、label_unlinked-01、label_unlinked-04、label_unlinked-07、label_unlinked-10 | 3,4 | 定位类改对可把按页平均从 82.8% 推到 95.4% | 键的落位成为可配维度：写进表头、写进面板标题、只留图例、或只留正文，四种都能生成 | 键落位 × {表头内 / 面板标题 / 仅图例 / 仅正文}，默认=当前（图例+正文） | P3 |
| 2 | `value_interpolated_off_axis`：不印数值时每个标记的可达精度 | 印数 97.2% 对不印 70.4%，差 26.8 点，是所有单变量里最大的口子；抽样 50 例中 13 例是差一格的读数。 | 单变量表：数值是否印在图上、value_off-41、value_absent-34、value_absent-38 | 2 | value_off 196 加 value_absent 17 共 213 个，占失败 23.8% | 生成时为每个标记记下"按这套刻度能读到的精度"，容差随图而定而非固定布尔门 | 每标记可达精度 × {印数 / 主刻度 / 次刻度 / 无网格}，默认=不印数 | P1 |
| 3 | `panel_name_dropped`：面板名进入键（panel_key） | 1 键 94.4%、3 键 69.0%、4 键 55.9%；三键以上题面里第三个键几乎总是面板名或图号，掉了就一键指多格。 | 单变量表：定位需要几个键、label_unlinked-05、row_missing-13、unit_mismatch-27 | 3 | 3–4 键共 749 个抽查点，通过率比 1 键低 25 至 38 点 | 面板名成为键的组成部分，可生成面板名在格内、格上或仅在图题三种版式 | panel_key × {每面板标题 / 共享标题 / 无面板名}，默认=每面板标题 | P2 |
| 4 | `series_identified_by_colour`：列名写成颜色词，图例文字从未进表 | b3cd580a p49 列头直接叫 'Red dotted series'，aviva p143 列头只叫 'Label'；控制组 legend_above_plot 也是 -13.3%。 | label_unlinked-06、label_unlinked-03、控制组表：legend_above_plot | 3 | label_unlinked 抽样 10 例中 2 例，按形态折算约 120 个失败 | 图例条目文本成独立字段，可控制它等于系列名、只给颜色词、或改为线端直标 | 系列命名 × {图例给全名 / 只有颜色 / 线端直标}，默认=下方图例给全名 | new |
| 5 | `scale_word_ignored` 与复合值标签：单位位置与刻度写法 | unit_mismatch 36 个几乎全是 ×10 或 '$130B' 被展成 1.3e+11；同一张 UK Competition 表里两点分别落进 unit_mismatch 与 value_off，起因同一个。 | unit_mismatch-22、unit_mismatch-30、value_off-48、value_absent-31 | 2 | unit_mismatch 占 4.0%，加上同因的 value_off 约再多 2 个百分点 | 单位可放轴题、刻度后缀或值标签三处；值标签内容可写成计数加年份的复合文本 | 单位位置 × {轴题 / 刻度后缀 / 值标签}，值标签内容 × {纯数 / 复合}，默认=刻度后缀+纯数 | P6 |
| 6 | `figure_not_transcribed`：一页多图、信息图，图号成为定位键 | mts0625 p6 两问用 'Figure 3./Figure 4.' 定位而页上只出一张表；pdf_f270146f8ca7 p25 三问的图整个没转出。 | row_missing-14、row_missing-15、label_unlinked-08、row_missing-16 | 1,4 | row_missing 48 个占 5.4%，抽样 3/10 是整图未转出 | 图号、标题、副标题、单位各成字段，可生成一页多图且每图带号的版面 | 每页图数 × {1 / 2 / 3+}，标题块位置 × {图上 / 图下}，默认=1 图、标题在上 | P7 |
| 7 | 标签字符串保真：99% 相似仍判未命中 | semiconductor p22 三问只差 'fundrasing/fundraising' 一个字母，MTS p8 图例全称被截成 '2025'；值都在表里。 | row_missing-18、row_missing-19、row_missing-20、row_missing-11 | 3 | row_missing 抽样 10 例中 4 例，按形态折算约 19 个失败 | 可控制图上标签是否截断、缩写或带拼写噪声，默认保证键与图上文字逐字一致 | 标签书写 × {全称 / 缩写截断 / 拼写噪声}，默认=全称 | new |
| 8 | `panel_background` 等底纹与轴题位置（控制组仅有的两个区间不重叠项） | 有底纹 43.3% 对没有 78.1%，差 -34.8%；axis_title_above_axis 反向 +25.2%。方向可用，但各只有 4–5 页。 | 控制组表：panel_background、控制组表：axis_title_above_axis | 1,2 | 只在不印数的 135 个点内测得，折算到全局不足 2% | 底纹与轴题位置成可配维度，可批量产出带底纹页做定向压力测试 | 底纹 × {无 / 浅灰面板 / 带状}，轴题 × {轴上方 / 旋转在侧}，默认=无底纹 | new |
| 9 | 图元密度与整页文字量：现在还不是主因 | 61–150 图元 73.2% 对 ≤20 的 81.2%，区间重叠；页面词数 79.2%→84.7%→79.6% 不单调。提上限前先要更大的 n。 | 单变量表：图元个数、单变量表：整页文字量 | — | 度量看不见它 | 密度成为受控变量，可在同一份数据上产出稀疏与密集两版做配对比较 | 图元数 × {≤20 / 21–60 / 61–150 / >150}，同数据配对，默认=21–60 | P5 |

### 正文

## 一句话

896 个失败的主体是"键没被画进表"，不是"数读歪了"。

## 1. 定位占三分之二（P3）

`label_unlinked` 599 个、66.8%；失联键 627 次落在"在某张表里但不定位"。抽样 10 例的机制全在第 3 步：列错位（-01、-04）、面板名与国名不同行（-05）、系列名只在图例（-03、-06）、键在另一张表（-02、-10）、图题只在正文（-07）。寻址全改对的上界 95.4%，比 82.8% 高 12.6 点——这 12.6 点买的全是"键写在哪"，与画得准不准无关。所以整页导出、以及标题/面板名相对表的位置，必须先成为可配维度。

## 2. 不印数值就掉 26.8 点（P1）

印数 97.2%（n=36）对不印 70.4%（n=135）。抽样 50 例里 13 例是 `value_interpolated_off_axis`：读数与答案只差一格（-33、-34、-37、-49、-50），有的整列被四舍到整数（-35、-41），有的被吸附到少数几个刻度（-38）。这类不该由布尔的 readable 门决定，应在生成时为每个标记记下"按这套刻度能读到的精度"。`value_off` 196 加 `value_absent` 17 共 213 个，占失败 23.8%。

## 3. 键的个数其实就是面板（P2）

1 键 94.4%、3 键 69.0%、4 键 55.9%，1 面板页 78.6%。三键以上的题面里第三个键几乎总是面板名或图号（-05、-13、-27）。panel_key 不进键，剩下的键就同时指向好几格。

## 4. 形态切分掩盖了同一个原因（P6）

`unit_mismatch` 与一部分 `value_off` 是同一件事：'$130B' 被展成 1.3e+11（-22、-23、-24），或整轴按 ×10 读（-26、-30）。UK Competition p31 同一张表，Berry ratio 判 unit_mismatch、Labour share 判 value_off，起因都是轴上标注的量级没被应用。`value_absent` 里还有 '28 countries, 80%'、'2 (2011, 2017)' 这种复合值标签——值标签的内容形态也要能配。

## 5. 剩下的

row_missing 48 个（5.4%）里，抽样 3/10 是整图没出表（一页多图、信息图），3/10 是标签差一个字母（'fundrasing'）；前者要图号成为字段，后者是生成端逐字一致的问题，跟画法无关。

控制组里只有 `panel_background`（-34.8%，n=30）与 `axis_title_above_axis`（+25.2%）区间不重叠，但各只有 4–5 页，方向可用、幅度别信。图元密度 73.2% 对 81.2% 区间重叠，页面词数 79.2%→84.7% 不单调——现在没有证据支持提密度上限，只支持把密度变成受控变量。

### 局限（它自己写的）

> 每形态抽 10 例、共 50 例，形态内机制比例的区间很宽；控制组各组件仅 3–10 页、n≈30；密度与面板数只在 20 页子样本上看过；部分机制（面板拆分、堆叠总量）是我据表面版式的推断，未见原图。

## 3 · 它引用的数字

逐条查这个数在程序的表里存不存在。全部 68 条里 24 条是带小数的比率或大计数（「可判别」= 是），其中 16 条找得到；其余是小整数，几百个格子里总能撞上一个，找到不算证据。「最接近的一格」是按名字相似度猜的，模型的答案里没有记它读了哪一格。找不到的**记录不改写**。

| claim | 模型自报的值 | 它说的来源 | 程序表里有没有这个数 | 可判别 | 最接近的一格 |
|---|---|---|---|---|---|
| 本批页数 | 100 | 题面给定 | 找到 | 否 | 抽样 / 页数 |
| 我这列卡在第 2 步的页数 | 67 | 卡在哪一步（三家并列） | 找到 | 否 | 卡在哪一步 / claude-opus-5 / 2 |
| 我这列卡在第 3 步的页数 | 30 | 卡在哪一步（三家并列） | 找到 | 否 | 组件表 `rotated_axis_title` / claude-opus-5 页数 |
| 我这列卡在第 1 步的页数 | 3 | 卡在哪一步（三家并列） | 找到 | 否 | 组件表 `shared_axis` / claude-opus-5 页数 |
| 我这列卡在第 4 步的页数 | 0 | 卡在哪一步（三家并列） | 找到 | 否 | 组件表 `thin_segment_label` / gemini-3.1-pro-preview 页数 |
| 数值一个都不印的图数（none） | 85 | 数值印不印（三家并列） | 找到 | 否 | 数值印不印 / claude-opus-5 / none |
| `unit_in_axis_or_title` 页数 | 85 | 组件计数表 | 找到 | 否 | 组件表 `unit_in_axis_or_title` / claude-opus-5 页数 |
| `negative_values` 页数 | 27 | 组件计数表 | 找到 | 否 | 组件表 `negative_values` / claude-opus-5 页数 |
| `value_label_outside` 页数 | 22 | 组件计数表 | 找到 | 否 | 组件表 `value_label_outside` / claude-opus-5 页数 |
| `no_value_axis` 页数 | 18 | 组件计数表 | 找到 | 否 | 组件表 `no_value_axis` / claude-opus-5 页数 |
| `panel_title_per_panel` 页数 | 30 | 组件计数表 | 找到 | 否 | 组件表 `panel_title_per_panel` / claude-opus-5 页数 |
| `small_multiples_4` 页数 | 22 | 组件计数表 | 找到 | 否 | 组件表 `small_multiples_4` / claude-opus-5 页数 |
| `per_panel_axis_range` 页数 | 16 | 组件计数表 | 找到 | 否 | 组件表 `per_panel_axis_range` / claude-opus-5 页数 |
| `mixed_marks` 页数 | 29 | 组件计数表 | 找到 | 否 | 组件表 `mixed_marks` / claude-opus-5 页数 |
| 「同向两条值轴」三家冲突页数 | 7 | 三家一致率表 | 找到 | 否 | 一致率表 同向两条值轴 / conflict |
| 残差 `marker_shape_encodes_series` 出现页数 | 7 | 词表外残差表 | 找到 | 否 | 组件表 `unit_in_series_name` / claude-opus-5 页数 |
| `horizontal_bars` 页数 | 20 | 组件计数表 | 找到 | 否 | 组件表 `horizontal_bars` / claude-opus-5 页数 |
| compound 图数（我 / gpt / gemini） | 22 / 32 / 5 | 类型配比表 | 找到 | 否 | 类型 / claude-opus-5 / compound |
| 图表类型判定冲突页数 | 40 | 三家一致率表 | 找到 | 否 | 一致率表 图表类型判定 / conflict |
| 标题位置 above 的图数 | 129 | 标题位置表 | 找到 | 否 | 标题位置 / claude-opus-5 / above |
| 标题位置 below 的图数 | 7 | 标题位置表 | 找到 | 否 | 标题位置 / claude-opus-5 / below |
| 组件命中集合按页平均一致率 | 67.1% | 三家一致率表 | 找到 | 是 | 一致率表 组件命中集合 / rate |
| 我的定位键命中率 | 69.0% | 预测定位键 vs 规则真实标签 | **没找到** | 否 | — |
| `footnote_marker` 页数（我 / gpt / gemini） | 32 / 13 / 12 | 组件计数表 | 找到 | 否 | 组件表 `footnote_marker` / claude-opus-5 页数 |
| `wrapped_category_labels` 页数（我 / gpt / gemini） | 31 / 15 / 9 | 组件计数表 | 找到 | 否 | 组件表 `wrapped_category_labels` / claude-opus-5 页数 |
| 密度 61–150 档页数 | 32 | 稠密度档表 | 找到 | 否 | 组件表 `rotated_x_ticks` / claude-opus-5 页数 |
| 密度 151–400 档页数 | 6 | 稠密度档表 | 找到 | 否 | 组件表 `heterogeneous_panel_types` / claude-opus-5 页数 |
| 密度 >400 档页数 | 6 | 稠密度档表 | 找到 | 否 | 组件表 `heterogeneous_panel_types` / claude-opus-5 页数 |
| `multi_figure_page` 页数 | 31 | 组件计数表 | 找到 | 否 | 组件表 `multi_figure_page` / claude-opus-5 页数 |
| `side_text_bullets` 页数 | 24 | 组件计数表 | 找到 | 否 | 组件表 `side_text_bullets` / claude-opus-5 页数 |
| `color_encodes_extra_attribute` 页数 | 15 | 组件计数表 | 找到 | 否 | 组件表 `color_encodes_extra_attribute` / claude-opus-5 页数 |
| `highlighted_category` 页数 | 23 | 组件计数表 | 找到 | 否 | 组件表 `highlighted_category` / claude-opus-5 页数 |
| 本轮失败总数 | 896 | 运行摘要 | 找到 | 是 | 失败运行 / failures |
| 按页平均通过率 | 82.8% | 运行摘要 | 找到 | 是 | 单变量 定位需要几个键 / 2 通过率 |
| 寻址全改对的上界 | 95.4% | 运行摘要 | 找到 | 是 | 一致率表 标题 / rate |
| 上界与现状之差 | 12.6 | 自己数的 | **没找到** | 是 | — |
| label_unlinked 个数 | 599 | 失败形态表 | 找到 | 是 | 形态表 `label_unlinked` / 个数 |
| label_unlinked 占失败 | 66.8% | 失败形态表 | 找到 | 是 | 形态表 `label_unlinked` / 占失败 |
| 失联键落在"在表里但不定位"的次数 | 627 | 失败形态表 | 找到 | 是 | 形态表 `label_unlinked` / 失联键去向 in_a_table_but_not_addressing |
| value_off 个数 | 196 | 失败形态表 | 找到 | 否 | 形态表 `value_off` / 个数 |
| value_absent 个数 | 17 | 失败形态表 | 找到 | 否 | 形态表 `value_absent` / 个数 |
| value_off 与 value_absent 之和 | 213 | 自己数的 | **没找到** | 是 | — |
| 这两类占失败比例 | 23.8% | 自己数的 | **没找到** | 是 | — |
| unit_mismatch 个数 | 36 | 失败形态表 | 找到 | 否 | 形态表 `unit_mismatch` / 个数 |
| unit_mismatch 占失败 | 4.0% | 失败形态表 | 找到 | 否 | 组件表 `per_panel_legend` / claude-opus-5 文档数 |
| row_missing 个数 | 48 | 失败形态表 | 找到 | 否 | 形态表 `row_missing` / 个数 |
| row_missing 占失败 | 5.4% | 失败形态表 | **没找到** | 是 | — |
| 图上印数值时的通过率 | 97.2% | 单变量表：数值是否印在图上 | 找到 | 是 | 控制组差值 `heterogeneous_panel_types` / 有它的通过率 |
| 印数值组样本量 | 36 | 单变量表：数值是否印在图上 | 找到 | 否 | 单变量 数值是否印在图上 / some n |
| 不印数值时的通过率 | 70.4% | 单变量表：数值是否印在图上 | 找到 | 是 | 一致率表 卡在哪一步 / rate |
| 不印数值组样本量 | 135 | 单变量表：数值是否印在图上 | **没找到** | 否 | — |
| 印数与不印数之差 | 26.8 | 自己数的 | **没找到** | 是 | — |
| 本次归因样本例数 | 50 | 提示中的案例 | 找到 | 否 | 组件表 `hgrid_only` / gpt-5.6-sol 页数 |
| 样本中判为读数差一格的例数 | 13 | 自己数的 | 找到 | 否 | 组件表 `rotated_axis_title` / claude-opus-5 文档数 |
| 1 个键的通过率 | 94.4% | 单变量表：定位需要几个键 | 找到 | 是 | 单变量 定位需要几个键 / 1 通过率 |
| 3 个键的通过率 | 69.0% | 单变量表：定位需要几个键 | **没找到** | 否 | — |
| 4 个键的通过率 | 55.9% | 单变量表：定位需要几个键 | 找到 | 是 | 单变量 定位需要几个键 / 4 通过率 |
| '$130B' 被解析成的数 | 1.3e+11 | unit_mismatch-22 | **没找到** | 是 | — |
| row_missing 抽样中整图未转出的比例 | 3/10 | 自己数的 | 找到 | 否 | 组件表 `shared_axis` / claude-opus-5 页数 |
| row_missing 抽样中拼写差一字母的比例 | 3/10 | 自己数的 | 找到 | 否 | 组件表 `shared_axis` / claude-opus-5 页数 |
| panel_background 有无之差 | -34.8% | 控制组表 | **没找到** | 是 | — |
| axis_title_above_axis 有无之差 | 25.2% | 控制组表 | **没找到** | 是 | — |
| 底纹组样本量 | 30 | 控制组表 | 找到 | 否 | 组件表 `rotated_axis_title` / claude-opus-5 页数 |
| 61–150 图元通过率 | 73.2% | 单变量表：图元个数 | 找到 | 是 | 控制组差值 `legend_above_plot` / 有它的通过率 |
| ≤20 图元通过率 | 81.2% | 单变量表：图元个数 | 找到 | 是 | 控制组差值 `legend_beside_plot` / 有它的通过率 |
| ≤240 词页面通过率 | 79.2% | 单变量表：整页文字量 | 找到 | 是 | 单变量 整页文字量 / ≤240 词 通过率 |
| 361–500 词页面通过率 | 84.7% | 单变量表：整页文字量 | 找到 | 是 | 单变量 整页文字量 / 361–500 词 通过率 |
| 1 面板页面的通过率 | 78.6% | 单变量表：面板数 | 找到 | 是 | 控制组差值 `small_multiples_4` / 有它的通过率 |
