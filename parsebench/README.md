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
| [review/06_output_contract.md](review/06_output_contract.md) | **输出契约，跑模型之前只读这一份**：要出的产物（三家各写三份报告 · 程序做并排与全部数字 · agent 写 INDEX + view.html）、谁写哪一部分、每张表一行是什么与列名、哪些数字必须程序算、三家按什么对齐、模型返回什么 |
| [TODO.md](TODO.md) | **分析重做的待办 T0–T7**，附录里是上一轮两份分析的数字与口径留档 |
| [reports/view.html](reports/view.html) | **先看这一份**：自足的图示版。开头用<u>一张真实的图上的一个真实的数字</u>把「键 / 值 / 区域」和基准的四步判定讲清楚，然后两个分区——**要改什么**（第一页是一张<u>总表</u>，十条改动一屏看完；后面按三家展开：键要说全 · 读法要记下来 · 图要像真的；最后是「先做哪个」。只看这一个分区就够）与**凭什么这么说**（100 页看到什么 · 568 页失败在哪 · 五个失败逐张看 · 三个模型说的一样吗）。每条改动配着它是从哪张图上看出来的，图可以点开看整页原图；单文件约 4.6 MB |
| [reports/INDEX.md](reports/INDEX.md) | 同一份结论的纯文字版，与 view.html **由同一份文案和同一批数字生成**，不会说不同的话 |
| [`../IMPROVEMENT_PLAN.md`](../IMPROVEMENT_PLAN.md) | **这十条怎么落进流水线**：八个设计决定、七个跨阶段连锁、模块划分与六步顺序 |
| [reports/compare.md](reports/compare.md) | 程序算的全部数字，三家并列，没有结论 |
| `reports/<model>.md` · `reports/pages/` | 每家自己写的两份 overview；逐页三家并排 + 判分 + 裁决（裁决面） |
| `tools/contract/` | 契约的机读半边，与 `review/06` 同一份内容：`format.py` 全部 schema 与口径 · `vocabulary.py` 65 项组件词表 · `try_page.py` 一页一模型的验证脚本（全英文） |
| `tools/analysis/` | 抽样、prompt、三家模型的页面调用与两条控制、每家的 overview、全部一致率与判分（全英文） |
| `tools/failures/` | 运行加载、失败形态、单变量统计、case 抽样、三家的归因调用、机制折算（全英文） |
| `tools/report/` | 把上面两处的产物渲染成 `reports/`：`build.py` 出程序的那几份，`view.py` + `view_text.py` + `view_style.py` 出 agent 的图示版，`index_md.py` 出它的纯文字版，`crops.py` 从原页切图，`numbers.py` 做自报与实测的对账（全英文） |
| `tools/dataset/` | 下载、渲染、标注统计（全英文） |
| `data/raw/` · `data/pages/` | chart 分片与 568 页 PNG（不入库，可重取） |
| `data/runs/` | 解析器运行目录：逐页输出 + 官方评测报告（不入库） |
| `data/stats/` | 统计与抽样结果（入库） |
| [data/examples/](data/examples/) | 手工挑出的代表页 |
| [data/failure_cases/](data/failure_cases/) | 前沿模型失败样本，含六类归因约定 |

**代码与产物都在本目录内**，目录外只引入 `src/llmkit`（共享的模型调用层，三家模型同一个调用面）。

**分析已按三家模型重做完毕**，产物在 [reports/](reports/)。重做的理由见 [TODO.md](TODO.md)：上一轮的结论由单个模型一次跑得出，没有第二个观察者，分不出「基准的性质」与「这个模型的读法」。旧产物可从提交 `7d975c2` 取回，数字与口径留档在 [TODO.md 附录](TODO.md)。

这一轮：**100 页 × 3 家**（`claude-opus-5` · `gpt-5.6-sol` · `gemini-3.1-pro-preview`）+ **两条控制**（同一家的无词表对照与自身重跑，各 100 页）+ 每家一份样例 overview 与一次失败归因，共 506 次调用。抽样分两阶段：先 20 页（种子 20260820），再从剩下的 548 页里抽 80 页（种子 20260821），两段各自均匀抽 ⇒ 合起来仍是 568 页上的均匀样本，而先抽的那 20 页答案、裁决与报告位置全部保留。

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

# 跑分析：抽样 → 三家跑页面 → 两条控制 → 程序算数 → 每家写 overview
python parsebench/tools/analysis/sample.py --size 20
for m in claude-opus-5 gpt-5.6-sol gemini-3.1-pro-preview; do
  python parsebench/tools/analysis/run.py --model $m
done
python parsebench/tools/analysis/run.py --model gemini-3.1-pro-preview --control no_vocab
python parsebench/tools/analysis/run.py --model gemini-3.1-pro-preview --control repeat
python parsebench/tools/analysis/tally.py                  # → data/stats/analysis_summary.json
for m in claude-opus-5 gpt-5.6-sol gemini-3.1-pro-preview; do
  python parsebench/tools/analysis/overview.py --model $m
done

# 跑失败分析：形态与统计全程序算，模型只做归因
python parsebench/tools/failures/stats.py                  # → data/stats/failures_<run>.json
for m in claude-opus-5 gpt-5.6-sol gemini-3.1-pro-preview; do
  python parsebench/tools/failures/attribute.py --model $m
done

# 渲染：逐页一页一份 + 每家 1 份 + compare.md（全部由程序写，没有结论）
python parsebench/tools/report/build.py

# 渲染 agent 的那一份：图示版与它的纯文字版，两者同源
python parsebench/tools/report/view.py                     # → reports/view.html
python parsebench/tools/report/index_md.py                 # → reports/INDEX.md
```

`view.html` 里的每一句话在 `tools/report/view_text.py`，每一个数字是那句话里的一个具名的洞，由 `view.py` 从 `data/stats/` 填进去——填不上就构建失败，不会留下一个过期的数字。图是用解析器自己的版面框从原页上切下来的（`tools/report/crops.py`），同一张图在页面里只内联一次。

**两处运行条件写在明处，因为不写就没人看得见。** 一是 `max_tokens`：它是上限不是目标，回答本来就装得下时调高不改变任何东西，所以每次运行用过的上限都记在答案里、印在成本表上（第一批 20 页时 `gpt-5.6-sol` 在 32,000 下截断过，这一轮三家分别用 64,000 / 64,000 / 120,000）。二是**走哪条通路**：`gpt-5.6-sol` 的直连账户跑到第 78 页时余额用尽，剩下 22 页经 OpenRouter 网关答完。网关是传输不是厂商——模型名、请求体、schema 都不变，所以那 22 页仍是同一个模型的回答；每条答案记一个 `via` 字段，成本表按次数分列 `direct` / `openrouter`。复现用 `run.py --via openrouter`（`llmkit.providers.provider_via`，`GATEWAYS` 一张表加一行就多一条通路）。

两条口径不变：`passed` 全部取自运行目录里的官方 `_evaluation_report.json`，不重判分；模型回复按 `(prompt, image, provider, model)` 缓存在 `data/cache/`，重跑为零成本。裁决写在 `data/analysis/verdicts.json`，是数据不是对文件的编辑，所以重渲染不会丢。

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
├── stats/                   ← 入库
│   ├── chart_split_stats.json    标注统计
│   ├── analysis_sample.json      抽中的 100 页（两阶段抽样，`stages` 记着每一段的种子）
│   ├── analysis_summary.json     三家的机读汇总：频次、配比、一致率、判分、两条控制
│   ├── failures_<run>.json       一次运行的失败形态、单变量通过率、控制组差值
│   └── page_text_stats.json      568 页的整页文字量（PDF 文字层实测）
├── analysis/                ← 三家的原始答案，入库
│   ├── <model>/<page>.json       一页一次调用的完整回答，附 token 与用时
│   ├── <model>/overview.json     这一家读完自己那 100 页写的报告
│   ├── <model>/failures.json     这一家的逐条归因 + 失败报告
│   └── verdicts.json             agent 对三家分歧的裁决
└── analysis_round1/         ← 第一版逐页 schema 的答案，只作对照，不参与任何统计
```

`analysis_round1/` 是 [T8](TODO.md) 之前那一版逐页 schema 的回答。逐页字段做细之后全部重跑了，**这一批不参与任何统计**，留着只为能看出「同一页在两版 schema 下答成什么样」。

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

- [x] **A · 分析重做**（T0–T7，逐条在 [TODO.md](TODO.md)）
  - [x] A1 上一轮存档到 `7d975c2`，数字与口径留档进 [TODO.md 附录](TODO.md)
  - [x] A2 删除 `reports/` · `failures/` · `synthesis/` 与对应的 `tools/analysis/` · `tools/failures/` · `tools/synthesis/`
  - [x] A3 llmkit 支持三家模型：`providers/` 下 Anthropic / OpenAI / Gemini 各一个文件，图像输入、结构化输出、推理强度三条通路等价，缓存键含 provider 与 model
  - [x] A4 输出契约先于跑模型：[review/06](review/06_output_contract.md) 与 `tools/contract/format.py`，定死三份报告的表与列；每个观察项带 `affects`、每条意见双栏结论；词表配两条控制
  - [x] A5 样例分析重跑：抽 100 页（20 + 80 两阶段），三家模型跑同一批，另加两条控制；程序算差异表，三家各写逐页报告与 overview，程序做并排与对账，agent 裁决冲突，只有三家一致的项进改造清单
  - [x] A6 失败样本分析重跑：输入仍是 `data/runs/` 已有的运行，模型只对抽样的 case（每形态 10 条）做归因，形态统计仍在全部失败上由程序算
  - [x] A7 agent 写 `reports/INDEX.md` 与 `reports/view.html`，每条结论标三层可信度（`chart.jsonl` 可核 · 三家一致 · 单家）

- [x] **B · 把分析结论翻成改动**（输入是 A5 / A6 的两份差异表，结论在 [reports/INDEX.md](reports/INDEX.md)）
  - [x] B1 改造顺序按两条依据出：频次与失败率，两条分开写。**第一顺位一致，都指向键**——失败侧 72% 是寻址、上界 82.75% → 95.41%；样例侧三家在颜色分组键上 30 次全错
  - [x] B2 每条改动过一遍 [T0.1](TODO.md)：消融表新增 8 行、一行没减；分数栏为空或证据不足的三条靠能力栏进清单，并在表里写明分数栏是空的
  - [x] B3 与 P1–P7 对齐：扩 P1 / P2 / P3 / P4，保持 P5 / P6 / P7，**加两条**——P8（颜色 / 高亮编码的第三属性）与 P9（同面板两条平行值轴 + 混合图元），不删

- [ ] **C · 流水线改造**（规格写回 `storyline/`，实现进 `src/chartgen/`，对应 [IMPL_PLAN 的 H 组](../IMPL_PLAN.md#h-parsebench-对齐)）

  **次序**由 B1 的两条依据给出，重跑后的读法是：**C2 + C8 + C9 一次改完**——它们是同一处代码，都在「一个值的地址不够长」上。两条依据的第一顺位一致，都指向键：896 个失败里约七成是寻址，全部改对的上界是按页平均 82.75% → 95.41%；而键的分量不止面板一维，颜色编码的分组名是一维（三家模型在它上面全错，是本轮唯一可核的缺口），两条平行值轴时「对着哪条轴读的」也是一维。再 C3 → C1 → C4 → C6 → C5 → C7。

  **这里与三家模型自己的排序不一致**：三家的失败报告都把 C3（整页导出）排第一，理由是它覆盖的失败最多；这里排第二，因为 C3 改的是「记录怎么导出」，C2 / C8 / C9 改的是「记录里有什么」。先做 C3，导出的表里仍然缺面板名、缺颜色分组、缺轴的身份，补完还要再导一次；反过来则不用。三家的排序与这里的排序并列在 [view.html](reports/view.html) 的「三家自己怎么排」一页。

  **与上一轮的差别**：上一轮把 C3 / C6（图周围的文字）排在最前，依据是频次；重跑之后频次轴的头名仍然是「图周围的文字」，但那批组件的 `affects` 大多是空的，按 T0.1 属于能力栏。失败率轴给出的头名是键，两条依据在「键」上重合，所以键先做。

  - [ ] C1 [P1](review/04_pipeline_gap.md#p1--readable-从二值门改为按可达精度分级) `readable` 二值门 → 每 mark 的可达精度 ε。**ε 不是新记一层**：值轴的「一像素等于多少数值单位」在绘制时的坐标变换里已经有，`labeled` 布尔也已经有，两者相除即得；角度画法按同式重算。**它的主要消费者是自检而非判分**——`common/readback.py` 与 RL 奖励都要拿模型给的值和像素回读值比较，这个比较必须有一个阈值，二值门给不出阈值，全局放宽容差只是随手挑一个阈值。**验收**：饼图在 5% 容差下的去留由 ε 算出（基准里饼族仅 4 张 / 3 页，频次定不了）
  - [ ] C2 [P2](review/04_pipeline_gap.md#p2--面板维进入键) 多面板图加 `panel_key`
  - [ ] C3 [P3](review/04_pipeline_gap.md#p3--加一个整页-markdown-导出) **页面成为一个对象**：一页多张图（各带图号）+ **标题块作为独立于绘图区的一块**来合成与记录（位置、归属、共不共用）+ 整页 markdown 导出（长表 + 表前标题）。**B3 已定**：图号与图题写成表**前**的 markdown 标题并进这一条（本轮抽到一条直接拿 `Figure 3.` 当定位键的规则）；把图号 + 标题**渲染到图上方**归 C7。一页多图各自成表，带图号的表格也算一张图。**正文 / 页眉 / 页脚与「裁到哪」都不进这一条**：把图从整页里裁出来是下游预处理那一步的事，不是生成端的维度——每个部件（绘图区、标题块、图例、来源行）的框绘制时已经记着，下游按框自己切即可，同一次渲染切得出任意一档。**验收**：并排两张共用类目名的图，导出后不撞车（本轮 `FPA-guide-to-data-visualization_p20` 是干净实例）
  - [ ] C4 [P4](review/04_pipeline_gap.md#p4--轮转图的族采样加权重向量) 族采样从写死的等概率改成**一个可插拔的分布**：一个 flag 选预设（`uniform` 默认 · `parsebench` 实测配比 · 自定义权重文件），预设本身只是一个返回权重向量的小函数。**不是「照 ParseBench 的配比生成」**——那会把流水线绑死在一把尺子上；换尺子只换预设，流水线不动。**验收**：三档预设各生成一批，类型覆盖率与读数正确率可分开比
  - [ ] C5 [P5](review/04_pipeline_gap.md#p5--稠密度上限抬高把稠密度变成一个可控自变量) 抬高稠密度上限；页面合成同时补上文字量目标（实测中位 359 词 / 页）。**扩到 100 页后这一条的证据变硬了**：按图元个数分档的正确率 ≤20 91.9%（n=247）→ 61–150 75.5%（n=233）→ >400 69.8%（n=43），首尾两档的 95% 区间不重叠，「越密越差」在两端复核出来了；唯一不顺的是 151–400 这一档 87.0%（n=46）比两边都高，**原因未定**，区间宽到能盖住相邻两档。20 页时说的「151–400 几乎没见到」不再成立：三家各数出 6 / 7 / 8 张图落在这一档。**验收**：这五档都能生成，且各档的读数正确率与反读自检通过率可分开测
  - [ ] C6 [P6](review/04_pipeline_gap.md#p6--风格向量补三维) 风格向量按**实测清单**逐项补，不再只补三维：65 项组件词表的 `ours` 列是看任何一页之前照 `storyline/` 定的，与本轮实测一交得出 37 项「100 页上出现过、我们画不出来」，其中 7 项已在 C2 / C3 / C5 / C8 / C9 / C10 下单算，其余归这一条；头部是单位位置、负值零线、值轴标题写在轴正上方、脚注上标、单类目高亮、非 ISO 时间刻度、标注形态、说明框、面板底色、**横向条（条件表无「方向」维）**。**验收**：这些维度逐项可配且默认保持现行行为；风格成对样本因此覆盖得到第三条自检
  - [ ] C7 [P7](review/04_pipeline_gap.md#p7--图标题成为一等公民) 图标题成为一等公民：FigureSpec 加 `title`（图号 / 主标题 / 副标题 / 单位 / **位置**四值）、轮转图与多面板图按模板合成标题、图号由页面合成器编、caption 退回只服务意图图。**这一项属于 B 半——做完 ParseBench 的分数基本不动**（只有 14 条规则拿图号当定位标签，本轮 100 页抽到其中一条），理由是重跑实测三家各数出 141 / 139 / 136 张图，其中 129 / 126 / 123 张标题在图的上方、83 / 83 / 81 张带图号，而我们八张图里五张连标题来源都没有
  - [ ] C8 **P8（重跑新增）** 颜色 / 高亮编码的第三属性：它同时是风格向量的一维与 `key` 的一维。**验收**：含颜色分组的页面上，导出的表里分组名独立成列，且第 3 步命中率有 / 无这一列可对照
  - [ ] C10 **P10（重跑新增）** 类型表里根本没有的图族，扩样后是**三族**：区间条 / 浮动条 / 哑铃图（三家合计提到 11 次；一根条两端各一个值，记录结构要能装下「一个图形两个值」）、表格型图（14 次，带图号的表当作一张图）、**扇形预测带 / windsock**（2 次，一条实测线接一段向外张开的不确定区间；面积族画的是堆叠带，画不出以中线为轴张开的这种）。**验收**：这三族能生成，类型覆盖率表里各占一行，区间条那族另加一行「一个图形两个值」的记录结构开 / 关。**这一条明确没列全**：一族图不在这 100 页里出现就进不了清单。地图 / 分级填色图、仪表盘、雷达图、桑基图、甘特与时间条、人口金字塔、斜坡图这 100 页一张都没抽到。**其中地图不是「没证据」**：上一轮单模型在 192 页上报过 3 张 / 3 页——口径不同（单个观察者、另一份 prompt），只能当第三层证据，但足以说明基准里确实有地图。其余六族两边都没有证据
  - [ ] C9 **P9（重跑新增）** 同面板两条平行值轴与混合图元：每个 mark 记下它对着哪条值轴、什么图元形状读出来的；`compound` 从「多面板的一种关系」升为一个族。**验收**：双轴图上 `common/readback.py` 的回读自检有定义且能判对错——现在同一个像素高度对应两个值，自检在这类图上无法判；三家里至少两家认为画了两条平行值轴的图，本轮 100 页上有 9 张（三家各自数出 9 / 9 / 8 张）

- [ ] **D · 评测闭环**（全量 568 页只在这一组出现，[理由](review/05_analysis_design.md#4-组件分析与全量评测是两件事)）
  - [ ] D1 `tools/eval/score_pages.py`——接官方 `ChartDataPointRule`，`parse_bench` 按可选依赖装
  - [ ] D2 改造前基线：568 页跑一遍 parse 并打分，与 [01 §4](review/01_benchmark.md#4-榜单) 同口径
  - [ ] D3 改造后复评；Charts 与 Visual Grounding 两维同时报告
  - [ ] D4 消融：ε 分级 vs 二值门、有无 `panel_key`、稠密度阶梯
