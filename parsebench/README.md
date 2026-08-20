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
| [review/04_pipeline_gap.md](review/04_pipeline_gap.md) | **七项流水线改进** P1–P7 + 与 storyline 的关系 |
| [review/05_analysis_design.md](review/05_analysis_design.md) | 样例分析怎么做：一次调用、整页原图、随机抽样、不做 agent、不接 OCR |
| [review/06_output_contract.md](review/06_output_contract.md) | **输出契约，跑模型之前只读这一份**：要出的产物（模型的 JSON · 程序渲染的逐页报告与汇总表 · agent 写的 INDEX + view.html）、谁写哪一部分、每张表一行是什么与列名、哪些数字必须程序算、三家按什么对齐、模型返回什么 |
| [TODO.md](TODO.md) | **分析重做的待办 T0–T7**，附录里是上一轮两份分析的数字与口径留档 |
| `tools/contract/` | 契约的机读半边，与 `review/06` 同一份内容：`format.py` 全部 schema 与口径 · `vocabulary.py` 65 项组件词表 · `try_page.py` 一页一模型的验证脚本（全英文） |
| `tools/dataset/` | 下载、渲染、标注统计（全英文） |
| `data/raw/` · `data/pages/` | chart 分片与 568 页 PNG（不入库，可重取） |
| `data/runs/` | 解析器运行目录：逐页输出 + 官方评测报告（不入库） |
| `data/stats/` | 统计与抽样结果（入库） |
| [data/examples/](data/examples/) | 手工挑出的代表页 |
| [data/failure_cases/](data/failure_cases/) | 前沿模型失败样本，含六类归因约定 |

**代码与产物都在本目录内**，目录外只引入 `src/llmkit`（共享的模型调用层，三家模型同一个调用面）。

**样例分析与失败样本分析的产物目录（`reports/` · `failures/` · `synthesis/`）已删除**，重做中。删除的理由与留档见 [TODO.md](TODO.md)：上一轮的结论由单个模型一次跑得出，没有第二个观察者，分不出「基准的性质」与「这个模型的读法」。旧产物可从提交 `7d975c2` 取回。

---

## 复现

```bash
# 拿数据：parsebench/tools/dataset/
python parsebench/tools/dataset/download_chart_split.py    # 1.6 MB 标注 + 568 个单页 PDF，约 150 MB
python parsebench/tools/dataset/render_pages.py --dpi 150  # PDF → PNG
python parsebench/tools/dataset/chart_split_stats.py       # 标注统计 → data/stats/
python parsebench/tools/dataset/page_text_stats.py         # 页面文字量 → data/stats/

# 看契约：跑分析之前先读这一份
python parsebench/tools/contract/vocabulary.py             # 65 项组件词表与它们的 affects
python parsebench/tools/contract/try_page.py --model gemini-3.1-pro-preview   # 一页一模型，验证契约填得满
```

样例分析与失败样本分析的驱动脚本随产物一并删除，按 [TODO T5 / T6](TODO.md) 重写。重写时不变的两条口径：`passed` 全部取自运行目录里的官方 `_evaluation_report.json`，不重判分；模型回复按 `(prompt, image, provider, model)` 缓存在 `data/cache/`，重跑为零成本。

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

## TODO

- [x] **基准 review 与数据落地**
  - [x] 论文与官方评测代码逐条核对，写进 `review/01`–`review/03`
  - [x] chart 分片下载（4,864 条标注 / 568 页 / 99 文档），568 页渲染为 PNG
  - [x] 标注统计固化到 `data/stats/chart_split_stats.json`
  - [x] 改进清单 `review/04`，七项 P1–P7 + 与 storyline 的关系
  - [x] 分析设计 `review/05`：整页一次调用，不裁剪、不做 agent、不接 OCR
  - [x] llmkit 加图像通路——`Image` 类型、block 列表请求、缓存键收图摘要，附 11 项测试
  - [x] 随机抽样：48 → 96 → 192，`--extend` 每次保留已抽中的页（脚本随产物删除，重做按 20 页重抽）

- [ ] **A · 分析重做**（T0–T7，逐条在 [TODO.md](TODO.md)）
  - [x] A1 上一轮存档到 `7d975c2`，数字与口径留档进 [TODO.md 附录](TODO.md)
  - [ ] A2 删除 `reports/` · `failures/` · `synthesis/` 与对应的 `tools/analysis/` · `tools/failures/` · `tools/synthesis/`
  - [x] A3 llmkit 支持三家模型：`providers/` 下 Anthropic / OpenAI / Gemini 各一个文件，图像输入、结构化输出、推理强度三条通路等价，缓存键含 provider 与 model
  - [x] A4 输出契约先于跑模型：[review/06](review/06_output_contract.md) 与 `tools/contract/format.py`，定死三份报告的表与列；每个观察项带 `affects`、每条意见双栏结论；词表配两条控制
  - [ ] A5 样例分析重跑：抽 20 页，三家模型跑同一批，另加一次无词表对照；程序算差异表，程序渲染逐页报告与汇总表，agent 裁决冲突，只有三家一致的项进改造清单
  - [ ] A6 失败样本分析重跑：输入仍是 `data/runs/` 已有的运行，模型只做归因，形态统计仍由程序算
  - [ ] A7 agent 写 `reports/INDEX.md` 与 `reports/view.html`，每条结论标三层可信度（`chart.jsonl` 可核 · 三家一致 · 单家）

- [ ] **B · 把分析结论翻成改动**（输入是 A5 / A6 的两份差异表）
  - [ ] B1 改造顺序按两条依据出：频次（基准里有多少这种图）与失败率（这种图要付多少代价），两条分开写，不合成一列
  - [ ] B2 每条改动过一遍 [T0.1](TODO.md)：它给流水线加了什么能力、消融表因此多哪一行；只被「基准要求」支撑而不加能力的条目不进清单
  - [ ] B3 与 P1–P7 对齐：扩哪一条、加哪一条新的、删哪一条

- [ ] **C · 流水线改造**（规格写回 `storyline/`，实现进 `src/chartgen/`，对应 [IMPL_PLAN 的 H 组](../IMPL_PLAN.md#h-parsebench-对齐)）

  **次序**由 B1 的两条依据给出，上一轮的读法是：**C3 与 C6 先做**——高频缺口都落在「图周围的文字」，而这是 C3 与 C6 的地盘。再 C1 → C5 → C2 → C4。这个次序等 A5 / A6 重做后复核。

  **上一轮的失败数据同意 C3 打头，并把 C5 往前提**：72% 的失败是寻址（C3 的地盘），稠密度是三条单调曲线里落差最大的一条（C5）。两条排序依据不同——频次说的是「基准里有多少这种图」，失败率说的是「这种图要付多少代价」——两者第一顺位一致。这两条依据本身要等重做后的差异表复核，数字见 [TODO.md 附录](TODO.md)。

  - [ ] C1 [P1](review/04_pipeline_gap.md#p1--readable-从二值门改为按可达精度分级) `readable` 二值门 → 每 mark 的可达精度 ε；角度画法按同式重算。**验收**：饼图在 5% 容差下的去留由 ε 算出（基准里饼族仅 4 张 / 3 页，频次定不了）
  - [ ] C2 [P2](review/04_pipeline_gap.md#p2--面板维进入键) 多面板图加 `panel_key`
  - [ ] C3 [P3](review/04_pipeline_gap.md#p3--加一个整页-markdown-导出) 整页 markdown 导出（长表 + 表前标题）；**图号 + 标题渲染到图上方**是否并进这一条，等 B3 定
  - [ ] C4 [P4](review/04_pipeline_gap.md#p4--轮转图的族采样加权重向量) 族采样权重向量，默认维持均匀；对齐 ParseBench 的那份配比等重做后的类型配比表填
  - [ ] C5 [P5](review/04_pipeline_gap.md#p5--稠密度上限抬高把稠密度变成一个可控自变量) 抬高稠密度上限，目标档位参考实测的 448–1300 图元；页面合成同时补上文字量目标（实测中位 359 词 / 页）
  - [ ] C6 [P6](review/04_pipeline_gap.md#p6--风格向量补三维) 风格向量补三维：标注形态、刻度格式与单位位置、负值零线
  - [ ] C7 [P7](review/04_pipeline_gap.md#p7--图标题成为一等公民) 图标题成为一等公民：FigureSpec 加 `title`（图号 / 主标题 / 副标题 / 单位 / **位置**四值）、轮转图与多面板图按模板合成标题、图号由页面合成器编、caption 退回只服务意图图。**这一项属于 B 半——做完 ParseBench 的分数基本不动**（只有 14 条规则拿图号当定位标签），理由是 94% 的真实图有标题而我们八张图里五张连标题来源都没有

- [ ] **D · 评测闭环**（全量 568 页只在这一组出现，[理由](review/05_analysis_design.md#4-组件分析与全量评测是两件事)）
  - [ ] D1 `tools/eval/score_pages.py`——接官方 `ChartDataPointRule`，`parse_bench` 按可选依赖装
  - [ ] D2 改造前基线：568 页跑一遍 parse 并打分，与 [01 §4](review/01_benchmark.md#4-榜单) 同口径
  - [ ] D3 改造后复评；Charts 与 Visual Grounding 两维同时报告
  - [ ] D4 消融：ε 分级 vs 二值门、有无 `panel_key`、稠密度阶梯
