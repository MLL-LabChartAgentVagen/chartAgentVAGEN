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
| [review/05_analysis_design.md](review/05_analysis_design.md) | 样例分析怎么做：两段式固定流程、抽 48 页、不做 agent、不接 OCR |
| [reports/README.md](reports/README.md) | **报告格式与组件词表**——一页样本一份报告 |
| `data/raw/` · `data/pages/` | chart 分片与 568 页 PNG（不入库，可重取） |
| `data/stats/` | 统计与抽样结果（入库） |
| [data/examples/](data/examples/) | 手工挑出的代表页 |
| [data/failure_cases/](data/failure_cases/) | 前沿模型失败样本，含六类归因约定 |
| `tools/` | 下载、渲染、统计、抽样脚本（全英文） |

**代码与产物都在本目录内**，目录外只引入 `src/llmkit`（共享的模型调用层）。

---

## 复现

```bash
python parsebench/tools/download_chart_split.py    # 1.6 MB 标注 + 568 个单页 PDF，约 150 MB
python parsebench/tools/render_pages.py --dpi 150  # PDF → PNG
python parsebench/tools/chart_split_stats.py       # 标注统计 → data/stats/
python parsebench/tools/sample_pages.py --size 48  # 分层抽样 → data/stats/analysis_sample.json
```

只拉 chart 一个维度，其余四维不下载。

---

## TODO

- [x] **基准 review 与数据落地**
  - [x] 论文与官方评测代码逐条核对，写进 `review/01`–`review/03`
  - [x] chart 分片下载（4,864 条标注 / 568 页 / 99 文档），568 页渲染为 PNG
  - [x] 标注统计固化到 `data/stats/chart_split_stats.json`
  - [x] 改进清单 `review/04`，六项 + 与 storyline 的关系
  - [x] 分析设计 `review/05`：两段式固定流程，不做 agent、不接 OCR
  - [x] llmkit 加图像通路——`Image` 类型、block 列表请求、缓存键收图摘要，附 11 项测试
  - [x] 分层抽样 `tools/sample_pages.py`：48 页 / 36 文档 / 覆盖 413 条抽查点

- [ ] **A · 48 页样例分析**
  - [ ] A1 `tools/analyze_pages.py`——定位 → 350 dpi 重渲染 → 组件分析 → 与 `chart.jsonl` 标签交叉核对，走 `llm.json(images=...)` 与 `llm.map()`
  - [ ] A2 跑完 48 页，产出 `reports/<stem>/`（格式见 [reports/README.md](reports/README.md)）
  - [ ] A3 汇总 `reports/INDEX.md`：组件频次、新组件、难点分布
  - [ ] A4 回填组件词表里的「待核实」（读 `storyline/` 规格即可，不需要模型）

- [ ] **B · 从报告与失败案例定改动**
  - [ ] B1 组件频次表里「我们无」的排序 → 直接给出改造顺序
  - [ ] B2 出现 ≥3 次的新组件并入词表，评估是否要新增 G 项
  - [ ] B3 失败六类归因（无表 / 值不准 / 标签没关联 / 量纲错 / 漏图 / 串系列）
  - [ ] B4 饼图在 5% 容差下的可读比例 → 决定饼图是否进值目标
  - [ ] B5 稠密度与失败率的相关性 → 若显著，即为 [G5](review/04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量) 的直接证据

- [ ] **C · 流水线改造**（规格写回 `storyline/`，实现进 `src/chartgen/`）
  - [ ] C1 [G1](review/04_pipeline_gap.md#g1--readable-从二值门改为按可达精度分级) `readable` 二值门 → 每 mark 的可达精度 ε；角度画法按同式重算
  - [ ] C2 [G2](review/04_pipeline_gap.md#g2--面板维进入键) 多面板图加 `panel_key`
  - [ ] C3 [G3](review/04_pipeline_gap.md#g3--加一个整页-markdown-导出) 整页 markdown 导出（长表 + 表前标题）
  - [ ] C4 [G4](review/04_pipeline_gap.md#g4--轮转图的族采样加权重向量) 族采样权重向量，默认维持均匀
  - [ ] C5 [G5](review/04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量) 抬高稠密度上限
  - [ ] C6 [G6](review/04_pipeline_gap.md#g6--风格向量补三维) 风格向量补三维：标注形态、刻度格式与单位位置、负值零线

- [ ] **D · 评测闭环**（全量 568 页只在这一组出现，[理由](review/05_analysis_design.md#3-不跑全量评测)）
  - [ ] D1 `tools/score_pages.py`——接官方 `ChartDataPointRule`，`parse_bench` 按可选依赖装
  - [ ] D2 改造前基线：568 页跑一遍 parse 并打分，与 [01 §4](review/01_benchmark.md#4-榜单) 同口径
  - [ ] D3 改造后复评；Charts 与 Visual Grounding 两维同时报告
  - [ ] D4 消融：ε 分级 vs 二值门、有无 `panel_key`、稠密度阶梯
