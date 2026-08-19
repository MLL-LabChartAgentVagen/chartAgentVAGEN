# ParseBench 对齐

**目的**：把 ParseBench 的 Charts 维度当作数据生成流水线的验收目标，据此得出**给流水线加能力**的改进清单。本目录收 ParseBench 相关的全部材料与结论，包括对流水线的改进意见；流水线本身的唯一定义处仍是 [storyline/parsebench_chart/](../storyline/parsebench_chart/)。

**当前任务形态**：chart to table。一张图必须能转成一张有 ground truth 的表，输出单位 `(键, 值)`；本项目在此之上多带一个 `区域`。

---

## 一句话结论

ParseBench 的 Charts 维度考的是：**从一张企业报告页面上，把图里没写出来的数值按 5% 容差估读出来，放进一张标签能对上的表里**。73.4% 的抽查点图上没有数值，14.5% 需要三个键才能定位。

它把 Charts 与 Visual Grounding **分开评分**，且现状没有任何方法两项都强——本项目的 `(键, 值, 区域)` 一次同时供给这两维，**ParseBench 是目前唯一能测这个主张的仪器**。

---

## 目录

| 路径 | 内容 |
|---|---|
| [review/01_benchmark.md](review/01_benchmark.md) | 任务形态、规则文件、榜单 |
| [review/02_chart_metric.md](review/02_chart_metric.md) | `ChartDataPointMatch` 逐条判定，附一条真实规则走完四步的例子 |
| [review/03_chart_characteristics.md](review/03_chart_characteristics.md) | 难度构成与视觉多样性，来自 4,864 条标注与 568 页 |
| [review/04_pipeline_gap.md](review/04_pipeline_gap.md) | **六项流水线改进** + 与 storyline 的关系 |
| [review/05_analysis_design.md](review/05_analysis_design.md) | 样例分析怎么做：一次调用、整页原图、随机抽 192 页、不做 agent、不接 OCR |
| [reports/INDEX.md](reports/INDEX.md) | **样例分析的唯一文档**，三节：**要改什么**（我们画不出来的：组件 + 类型 + 标题维度，一张排序表）· **基准长什么样**（描述，没有待办）· **能不能信**（调用方式、判分、逐页） |
| [reports/view.html](reports/view.html) | 同一份内容的图示版，三个分区与 INDEX 一一对应；每一项配一页实例**与模型写下的证据原文**。图片在 `reports/assets/`（生成时一并写出，不入库） |
| [reports/pages/](reports/pages/) | 192 份逐页报告，一页一目录 |
| [failures/](failures/README.md) | **失败样本分析**，一个解析器运行一个子目录：`INDEX.md` 四节（失败形态 · 什么图更容易失败 · 翻成流水线改动 · 能不能信）· `view.html` · `cases/` 十页实例 |
| [synthesis/](synthesis/README.md) | **两份分析的合并结论**：`INDEX.md`（中文）与 `INDEX.en.md`（英文）五节——证据合并 · **5 条能力轴 + 1 条方法轴** · 覆盖与裁决 · 路线与验收 · 口径与边界；`view.html` / `view.en.html` 是**例子优先**的图示版——39 项组件缺口、10 个失败页面、2 处类型缺口各配原页与原始证据。**自足**，不打开另外两份也能读完 |
| `data/raw/` · `data/pages/` | chart 分片与 568 页 PNG（不入库，可重取） |
| `data/runs/` | 解析器运行目录：逐页输出 + 官方评测报告（不入库） |
| `data/stats/` | 统计与抽样结果（入库） |
| [data/examples/](data/examples/) | 手工挑出的代表页 |
| [data/failure_cases/](data/failure_cases/) | 前沿模型失败样本，含六类归因约定 |
| `tools/dataset/` | 下载、渲染、标注统计（全英文） |
| `tools/analysis/` | 样例分析：词表、schema、prompt、核对、渲染、驱动（全英文） |
| `tools/failures/` | 失败样本分析：运行读取、按度量方式找格子、失败命名、与页面描述对齐、渲染（全英文） |
| `tools/synthesis/` | 合并结论：把 `synthesis/INDEX*.md` 投影成标签页视图（全英文） |

**代码与产物都在本目录内**，目录外只引入 `src/llmkit`（共享的模型调用层）。

---

## 复现

```bash
# 拿数据：parsebench/tools/dataset/
python parsebench/tools/dataset/download_chart_split.py    # 1.6 MB 标注 + 568 个单页 PDF，约 150 MB
python parsebench/tools/dataset/render_pages.py --dpi 150  # PDF → PNG
python parsebench/tools/dataset/chart_split_stats.py       # 标注统计 → data/stats/

# 做分析：parsebench/tools/analysis/
python parsebench/tools/analysis/sample_pages.py --size 192 --extend   # 随机抽样
python parsebench/tools/dataset/page_text_stats.py          # 页面文字量 → data/stats/
python parsebench/tools/analysis/analyze_pages.py          # 192 页样例分析 → reports/（INDEX.md · view.html · pages/）

# 读失败：parsebench/tools/failures/
unzip -q <运行>.zip -x "__MACOSX/*" -d parsebench/data/runs/
python parsebench/tools/failures/analyze_failures.py       # 失败样本分析 → failures/<运行名>/
python parsebench/tools/synthesis/build_view.py            # 合并结论 → synthesis/view.html · view.en.html
```

`analyze_failures.py` 不调模型、不重判分数——`passed` 全部取自运行目录里的官方 `_evaluation_report.json`，重跑零成本。

`analyze_pages.py` 一页一次调用，回复按 `(prompt, image, model)` 缓存在 `data/cache/`，重跑为零成本；`--dry-run` 只打印 prompt 不调模型，`--limit N` 先试几页。扩样用 `--size 192 --extend`，保留已抽中的页，只跑新增的。

只拉 chart 一个维度，其余四维不下载。

---

## 数据长什么样

**一个「页」= 一个单页 PDF = 一张 PNG。** 没有多页的图表；一页上可以有多张图（论文给出 1,039 张图分布在 568 页，平均 1.8 张）。

```
parsebench/data/
├── raw/                     ← 从 Hugging Face 原样下载，不入库
│   ├── chart.jsonl          1.6 MB，4,864 行，一行一个抽查点
│   ├── docs/chart/          156 MB，568 个 PDF，每个正好 1 页
│   │   ├── TSLA-Q3-2023-Update-3_p7.pdf      ← 特斯拉 Q3 财报的第 7 页
│   │   ├── TSLA-Q3-2023-Update-3_p8.pdf      ← 同一份报告的第 8 页
│   │   └── ...                                 568 页来自 99 份报告
│   ├── README.md            数据集自述：字段说明与标签词表
│   └── eval.yaml            五个维度的 split 定义
├── pages/                   ← 我们渲染的，不入库
│   └── TSLA-Q3-2023-Update-3_p7.png          176 MB，568 张，与 PDF 一一对应
└── stats/                   ← 入库
    ├── chart_split_stats.json     标注统计
    ├── analysis_sample.json       抽中的 192 页
    ├── analysis_summary.json      样例分析的机读汇总：频次向量、类型配比、难点分布
    └── page_text_stats.json       568 页的整页文字量（PDF 文字层实测）
```

**文件命名**是 `<原报告文件名>_p<该页在原报告中的页码>.pdf`。所以 `_p7` `_p8` 是同一份报告里被分别收录的两页，不是同一张图的两页。

**`chart.jsonl` 一行长这样**，靠 `pdf` 字段指回页面文件：

```json
{"pdf": "docs/chart/(Web_version)_E-Government_Survey_2024_1392024_p101.pdf",
 "type": "chart_data_point", "tags": [],
 "rule": "{\"value\": \"0.8079\", \"labels\": [\"IF\", \"193 UN Member States\"], \"max_diffs\": 0}"}
```

一页对应 2–11 行（中位 10），就是这一页上的全部抽查点。`tags` 按**文档级**施加，所以同一页内所有行的 tags 相同——`need_estimate`（数值要估读）与 `3d_chart`（定位一个值要三个键）。

**页面内容不只有图表。** 每个 PDF 是原报告完整的一页：正文、页眉页脚、图号与标题、note 行、source 行，加上 1–3 张图。评测时模型输出这一页的完整 markdown，抽查点在其中的所有表里搜索。

---

## 样例分析：192 页读出了什么

全表在 [reports/INDEX.md](reports/INDEX.md)（三节），配图版在 [reports/view.html](reports/view.html)——**每一项都配一页实例与模型写下的证据原文**，逐页在 [reports/pages/](reports/pages/)。192 页 / 70 份文档 / 1,658 条抽查点 / 265 张图，词表 65 项。

### 四份清单：保留什么、待定什么、舍弃什么

**频次单独看会骗人。** `unit_in_axis_or_title` 出现在 **149 / 192 页（78%）**，排缺口表第一行——而 ParseBench 的度量根本看不见它：

| 检验（4,864 条规则全量） | 结果 |
|---|---|
| 规则的**值**里出现量纲词（`billion` `million` …） | **0 条** |
| 规则的**标签**里出现单位符号 | 461 / 10,243（4.5%），全是 `Anticipated Reserve Margin (%)` 这种**系列名自带**的 |
| 规则的标签里出现图号 | **14 条（0.14%）** |
| 每条规则要几个标签 | **2 个占 79%**（3,847 / 4,864），3 个 15% |

所以每个组件带一个声明字段 **`affects`**——它能改变[四步判定](review/02_chart_metric.md)的哪一步，空就是度量看不见它。和「我们有没有」一样，看任何一页之前就按度量定义定死。**65 项里 42 项能改变某一步，23 项不能。**

两个已测判据依次问，39 项缺口**各归其一，没有重叠也没有遗漏**：

| 清单 | 项数 | 判据 | 里面有什么 |
|---|---|---|---|
| **保留 · 能提分** | 23 | `affects` 非空且出现过 | `wrapped_category_labels` 58 页 · `value_label_outside` 53 · `footnote_marker` 52 · `no_value_axis` 42 · `negative_values` 42 · `dense_marks_100plus` 41 |
| **保留 · 只提升真实性与视觉多样性** | 11 | 不满足第一条 · 通用度 通用/常见 | `unit_in_axis_or_title` 149 页 · `panel_background` 49 · `reference_line` 43 · `horizontal_bars` 42 · `annotation_callout` 33 · **标题维度整体在这一档** |
| **舍弃** | 5 | 前两条都不满足 | `highlighted_category`（20 / 45 份文档 = 0.44）· `data_link_below_figure`（OECD StatLink）· `axis_title_below_plot` · `error_bars` · `stacked_and_grouped`（一次没出现） |

**前两份之间没有汇率**，硬排成一列就得凭空发明一个换算率。第二份不会让分数动一格，做它们的理由是我们要的是一份通用的 chart 数据集，不是一个刷 ParseBench 的工具。**分界不是硬的**——通用度印的是比值本身（0.70 以上通用、0.45 以上常见），落在 0.43–0.47 的项换一份抽样就可能换一份清单。

### 标题：五个字段，不是四个组件

图题不是组件，是 **图号 / 主标题 / 副标题 / 单位 / 位置** 五个字段，每张图都记。词表里原本有四个 key 在重复记录同一件事，而且是**按页**记不是**按图**记（一页同时报「图号标题在上方」和「副标题分行」就把一个标题数了两次）——已删除，词表 69 → 65。

265 张图实测：**图号 149 张（56%）** · 副标题（标题不止一行）88 张（33%）· **单位写在标题里 159 张（60%）**。位置：图上方 231 · 图下方 15 · 无标题 11 · **与图并排的侧栏 8**（`2023-05-sigma-01-english_p23`，图号、标题、副标题三行排在左栏）。[P7](review/04_pipeline_gap.md#p7--图标题成为一等公民) 的消融行因此是四值——但它属于上面的第二份清单，**做完分数基本不动**。

### 类型缺口

`other` 22 张（8%）· `map` 3。这一轮起 `other` 必须命名，22 张分开之后：**表格 13 张**（`data_table_as_figure` 我们已经有）· **不是图 6 张**（占位、正文块，本该进 `unreadable`）· **真正的新画法只有 3 张，而且是同一种**——区间 / 哑铃图（`dumbbell range plot` · `three-marker range plot` · `vertical dumbbell range plot`）。**原来的 8% 类型空洞主要是表格与非图，不是异类图表。**

**类型配比**（[P4](review/04_pipeline_gap.md#p4--轮转图的族采样加权重向量) 的权重向量要的表）：`line` 57 · `compound` 52 · `stacked_bar` 45 · `bar` 37 · `grouped_bar` 34 · 其余 40。**`box`、`funnel`、`heatmap` 零出现**——不是白做，只说明按 ParseBench 调权重时不该给它们配额。**55% 的图一个数值都不写**（无 144 · 全部 98 · 部分 23）。

### 难点与判分

**难点**：第二步（读值）116 页、第三步（标签关联）60 页、第四步 11 页、第一步 5 页。

**规则实际要几个键 vs 模型预测要几个**——这是这一轮唯一被真正打分的东西：值给了模型、标签没给，所以模型说的「要哪些键才能定位」是预测，规则来判分。**1,635 个落位的值里对了 1,155 个（71%）**。规则里 79% 只用两个标签（行头 + 列头，markdown 表刚好装得下），而模型倾向于预测三个——差距逐条可查，每页 `report.md` 第 2 节把两者并排放在同一行。

**图不会单独出现。** 568 页整页文字量实测（PDF 文字层）：中位 **359 词**，94% 的页 ≥100 词，只有 6 页少于 50 词（[03 §4](review/03_chart_characteristics.md#4-版面形态)）。

**两个方法层面的测量**：`unreadable` 非空 4 / 192（2%）；交叉核对 192 页出 **195 条矛盾**，其中 129 条是上面那个判分，12 条是「规则需要的键比图能提供的多」，正对着 [P2](review/04_pipeline_gap.md#p2--面板维进入键)。

---

## TODO

- [x] **基准 review 与数据落地**
  - [x] 论文与官方评测代码逐条核对，写进 `review/01`–`review/03`
  - [x] chart 分片下载（4,864 条标注 / 568 页 / 99 文档），568 页渲染为 PNG
  - [x] 标注统计固化到 `data/stats/chart_split_stats.json`
  - [x] 改进清单 `review/04`，六项 + 与 storyline 的关系
  - [x] 分析设计 `review/05`：整页一次调用，不裁剪、不做 agent、不接 OCR
  - [x] llmkit 加图像通路——`Image` 类型、block 列表请求、缓存键收图摘要，附 11 项测试
  - [x] 随机抽样 `tools/analysis/sample_pages.py`：48 → 96 → 192，`--extend` 每次保留已抽中的页

- [ ] **A · 192 页样例分析**
  - [x] A1 `tools/analysis/`——整页一次结构化调用，`llm.map(..., schema=)` 并发。十一个文件各司其职：`vocabulary` 词表与类型的「我们有没有」 · `schema` 输出契约 · `prompt` 送什么 · `rules` 规则与归图 · `checks` 核对 · `markdown`/`report`/`index`/`viewer` 渲染 · `sample_pages` 抽样 · `analyze_pages` 驱动
  - [x] A2 抽样 48 → 96 → 192（`--extend` 每次保留已抽中的页），跑完 192 页 / 70 文档 / 1,658 抽查点
  - [x] A3 汇总 [`reports/INDEX.md`](reports/INDEX.md) 三节 + 机读的 `data/stats/analysis_summary.json`
  - [x] A7 页面文字量 `tools/dataset/page_text_stats.py`：568 页从 PDF 文字层实测，中位 359 词
  - [x] A4 回填组件词表：8 项「待核实」全部定案，另改正 `log_axis`（`03 §3` 风格向量的「轴」维已含对数轴）；词表移到 `tools/analysis/vocabulary.py`，README 的表由它生成
  - [x] A5 图示版 `reports/view.html`：三个分区，与 INDEX.md 一一对应，每一项配一页实例**与模型写下的证据原文**；同一份数据，同一次跑出
  - [ ] A6 *（等 03 能出整页后）* [反向差集](review/05_analysis_design.md#9-反向差集同一套词表也跑我们自己的页面)——同一 prompt、同一词表跑我们自己的页面，两个 `analysis_summary.json` 的频次向量相减，逐项过消费者表

- [ ] **B · 把分析结论翻成改动**（输入是 [INDEX §1](reports/INDEX.md) 与 [view.html](reports/view.html)）
  - [x] B1 改造顺序 = [INDEX §1](reports/INDEX.md)：组件缺口按频次分档，类型缺口并列在 §1.2；[§2](reports/INDEX.md) 再按**文档分布**把它们分成通用 / 常见 / 集中三档，「先做这几项」是由这三个已测条件算出来的，不是挑出来的
  - [x] B2 词表 **29 → 65 项**，长出来又剪掉一次。29 → 56：加方向维，把 289 个自拟名字按词干归并，26 个概念达到 ≥3 页（不归并只有 8 个），同时修准 4 条易误判的判据。56 → 69，并入的 13 项来自自拟名字与两处人工核对：`legend_above_plot` 22 页 · `color_encodes_extra_attribute`（`color_encodes_group_not_series` 与 `significance_by_fill_shade` 是同一个机制，合成一个 key）· `step_line_series` · `tick_marker_as_series` · `legend_beside_plot`（左右合一）· `data_link_below_figure`（StatLink 与 download 合一）· `range_connector_line` · `panel_title_per_panel` · `side_text_bullets` · `axis_title_above_axis` · **`axis_starts_above_zero`**（把 `broken_axis` 的误判源单列出来）· **`title_block_beside_plot`** 与 **`rebased_index_values`**（`2023-05-sigma-01-english_p23` 人工核出来的：标题块排在左栏与图并排，标题里写着 `2011 = 100`）。**69 → 65**：图题那四个 key 删掉，见 B2c
  - [x] B2c 词表 **69 → 65 项**，并加了一个声明字段。删掉的四项（`figure_number_title` `subtitle_above_plot` `caption_below_figure` `title_block_beside_plot`）都在重复记录 `heading` 那五个字段已经记的事，而且是按页记不是按图记——一页同时报前两项就把一个标题数了两次。新增 **`affects`**：这个组件能改变四步判定的哪一步，空就是**度量看不见它**。65 项里 42 项能改变某一步、23 项不能。**改造清单因此劈成 A（能提分）/ B（只关真实性）两半**，因为两者之间没有汇率，硬排成一列就得凭空发明一个。依据：4,864 条规则里值出现量纲词的 0 条、标签出现图号的 14 条（0.14%）
  - [x] B2b 这一轮同时改了**方法**，不只是词表：① 每个组件必须带 `evidence`（页面上的原话或画了什么），实例因此可核；② 标题拆成图号 / 主标题 / 副标题 / 单位 / 位置五项；③ `other` 类型必须命名；④ **抽查点的数值送进 prompt、标签不送**，模型逐个说值落在哪个图元、要哪些键定位，程序拿真实标签判分；⑤ 每条意见带通用度。设计见 [review/05 §5](review/05_analysis_design.md)
  - [ ] B6 失败数据带出的**三条新项**，P1–P7 都装不下，逐项定去留（[failures/ ... INDEX §3](failures/ppdoclayoutv3_lean_qwen/INDEX.md) 第 3 / 5 / 8 行）
    - **图例绑定**：色块 → 系列名成为一条监督信号。`pwc-semiconductor-and-beyond-2026-full-report_p17` 数值全对、列名写成 `Gray` / `Orange`，十个点全 0；控制组内 `shared_legend` −10.1 · `legend_beside_plot` −24.7。我们绘制时就知道每个图元的颜色与系列名，导出这一对是加法
    - **测度取值域进入读数先验**：`sri-sigma-natural-catastrophes-1-2025_p10` 的纵轴是年份**个数**（只能取整数），解析器写下 4.5。P1 的 ε 只描述精度，描述不了取值域
    - **图内非数据元素**：与 B3 第二项是同一件事，但现在有价了——`annotation_callout` −11.8 · `reference_line` −11.6（控制组内，区间不重叠），且 pwc 那一页把装饰连接带当成了第三个数据系列
  - [ ] B3 **五项 P1–P7 装不下的**，逐项定：扩哪一条 P，还是加新项
    - **图周围的文字位置**——单位在轴标题 / 副标题 / 图题（149 页，**通用**）· 轴标题在轴正上方（41 页）· 图旁另有文字栏（44 页）· 轴标题在图下方（17 页），加上标题那五个字段（见 §1.4）。[P3](review/04_pipeline_gap.md#p3--加一个整页-markdown-导出) 只管导出不管渲染，[P6](review/04_pipeline_gap.md#p6--风格向量补三维) 的「单位位置」只覆盖其中一条。**这是最大的一块，而且几乎整块落在「只提升真实性」那份清单里**——文本从哪来这一半已经单列为 [P7](review/04_pipeline_gap.md#p7--图标题成为一等公民)，这里只剩「渲染在哪」
    - **图内非数据元素**——`reference_line` 41 页 · `annotation_callout` 31 页 · `shaded_band` 18 页。它们不是任何族的图元，`chart_types.md` 无此形状
    - **页面文字量目标**——[03 §5](../storyline/parsebench_chart/03_render.md#5-页面合成) 要求嵌进含正文的版面，但没给量。实测中位 359 词 / 页，94% 的页 ≥100 词
    - **颜色承载语义**——`highlighted_category` 49 页（某一个类目单独换色标出汇总行或重点对象）与新加的 `color_encodes_extra_attribute` 27 页（颜色编码的是分组、是否显著、是否达标这类第三个变量）。`03 §3` 的配色按系列上色，颜色不承载数据列
    - **画不出来的整族**——`map` 2 张 · `gauge` 1 张，以及 `other` 里真正是新画法的 5 张（`fan chart` + 三张区间 / 哑铃图 + `cagr connector column`）。[P4](review/04_pipeline_gap.md#p4--轮转图的族采样加权重向量) 只能在已有的 13 型之间分配配额，管不到这一类。列在 [INDEX §1.2](reports/INDEX.md)。**量都很小，倾向只记录不加族**；唯一值得考虑的是区间 / 哑铃图，`range_connector_line` 已经先作为组件进了词表
  - [x] B3b **「待定」7 项的人工裁决**（程序不替人决定这一档，见 [INDEX §1.1](reports/INDEX.md)）
    - **保留** `highlighted_category`（45 页，分布 0.44）——`horizontal_bars` 0.45 保留而它 0.44 舍弃，差 0.01 分到两边。某一个类目单独换色标出汇总行或重点对象是通用作图习惯
    - **保留** `error_bars`（2 页）——条上的 T 形误差棒是通用画法，2 页说明的是**这个分片里少**，不是**真实世界里少**；它也是 `box` 五数之外唯一的离散度画法。归入「提升真实性与视觉多样性」
    - **保留** `horizontal_bars` `axis_title_above_axis` `shaded_band`（都压在 0.45–0.46 上）
    - **暂不处理** `broken_axis`（2 页）与 `stacked_and_grouped`（0 页）——证据不足，等扩样
  - [x] B3c **区间 / 哑铃图不加族**。`other` 22 张里真正是新画法的只有 3 张，全是区间图；为 3 / 265 加一整族不划算。`range_connector_line` 作为**组件**留在「能提分」清单（它确实卡第 2、3 步），但**不进条件表当第 14 种类型**
  - [x] B4 失败六类归因，改为在整个运行上做，不再等人工样本：`ppdoclayoutv3_lean_qwen`（PP-DocLayoutV3 lean + Qwen3.8-27B，按页平均 **82.75%**，高于 [01 §4](review/01_benchmark.md#4-榜单) 榜单任一行）的 896 个失败逐条归类 → [failures/ppdoclayoutv3_lean_qwen/INDEX.md](failures/ppdoclayoutv3_lean_qwen/INDEX.md)。**72% 是寻址失败**（值读对了但键对不上），其中 79% 的失联键就在同一张表里；`无表` 一例没有；「串系列 / 累计值」两类**没能与普通读数误差分开**，10 个候选并入读数失败
  - [x] B5 稠密度与失败率：≤20 图元 85.5% → >400 图元 57.9%，95% 区间不重叠——[P5](review/04_pipeline_gap.md#p5--稠密度上限抬高把稠密度变成一个可控自变量) 的直接证据，而 `chart_types.md` 现在的上限全落在最容易那一档。另有两条同样单调：定位键数 2 键 83.3% → 4 键 55.9%（全量 568 页，不依赖图表描述）· 数值印在图上 94.5% vs 一个不写 75.9%

- [ ] **C · 流水线改造**（规格写回 `storyline/`，实现进 `src/chartgen/`，对应 [IMPL_PLAN 的 H 组](../IMPL_PLAN.md#h-parsebench-对齐)）

  **次序**由 B1 的频次给出：**C3 与 C6 先做**——三个高档缺口都落在「图周围的文字」，而这是 C3 与 C6 的地盘（先按 B3 第一项把范围定清）。再 C1 → C5 → C2 → C4。

  **B4 / B5 的失败数据同意 C3 打头，并把 C5 往前提**：72% 的失败是寻址（C3 的地盘），稠密度是三条单调曲线里落差最大的一条（C5）。两条排序依据不同——频次说的是「基准里有多少这种图」，失败率说的是「这种图要付多少代价」——两者第一顺位一致，[failures/](failures/README.md) §3 逐条给了价。

  - [ ] C1 [P1](review/04_pipeline_gap.md#p1--readable-从二值门改为按可达精度分级) `readable` 二值门 → 每 mark 的可达精度 ε；角度画法按同式重算。**验收**：饼图在 5% 容差下的去留由 ε 算出（基准里饼族仅 4 张 / 3 页，频次定不了）
  - [ ] C2 [P2](review/04_pipeline_gap.md#p2--面板维进入键) 多面板图加 `panel_key`
  - [ ] C3 [P3](review/04_pipeline_gap.md#p3--加一个整页-markdown-导出) 整页 markdown 导出（长表 + 表前标题）；**图号 + 标题渲染到图上方**是否并进这一条，等 B3 定
  - [ ] C4 [P4](review/04_pipeline_gap.md#p4--轮转图的族采样加权重向量) 族采样权重向量，默认维持均匀；对齐 ParseBench 的那份配比按 [INDEX §3](reports/INDEX.md) 填
  - [ ] C5 [P5](review/04_pipeline_gap.md#p5--稠密度上限抬高把稠密度变成一个可控自变量) 抬高稠密度上限，目标档位参考实测的 448–1300 图元；页面合成同时补上文字量目标（B3 第三项）
  - [ ] C6 [P6](review/04_pipeline_gap.md#p6--风格向量补三维) 风格向量补三维：标注形态、刻度格式与单位位置、负值零线
  - [ ] C7 [P7](review/04_pipeline_gap.md#p7--图标题成为一等公民) 图标题成为一等公民：FigureSpec 加 `title`（图号 / 主标题 / 副标题 / 单位 / **位置**四值）、轮转图与多面板图按模板合成标题、图号由页面合成器编、caption 退回只服务意图图。**这一项属于 B 半——做完 ParseBench 的分数基本不动**（只有 14 条规则拿图号当定位标签），理由是 94% 的真实图有标题而我们八张图里五张连标题来源都没有

- [ ] **D · 评测闭环**（全量 568 页只在这一组出现，[理由](review/05_analysis_design.md#4-组件分析与全量评测是两件事)）
  - [ ] D1 `tools/eval/score_pages.py`——接官方 `ChartDataPointRule`，`parse_bench` 按可选依赖装
  - [ ] D2 改造前基线：568 页跑一遍 parse 并打分，与 [01 §4](review/01_benchmark.md#4-榜单) 同口径
  - [ ] D3 改造后复评；Charts 与 Visual Grounding 两维同时报告
  - [ ] D4 消融：ε 分级 vs 二值门、有无 `panel_key`、稠密度阶梯
