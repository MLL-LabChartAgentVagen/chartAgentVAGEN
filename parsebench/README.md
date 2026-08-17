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
| [review/05_analysis_design.md](review/05_analysis_design.md) | 样例分析怎么做：单 VLM，不做 agent，代码走 llmkit |
| `data/raw/` · `data/pages/` | chart 分片与 568 页 PNG（不入库，可重取） |
| `data/stats/` | 统计（入库） |
| [data/examples/](data/examples/) | 手工挑出的代表页 |
| [data/failure_cases/](data/failure_cases/) | 前沿模型失败样本，含六类归因约定 |
| `tools/` | 下载、渲染、统计脚本（全英文） |

---

## 复现

```bash
python parsebench/tools/download_chart_split.py    # 1.6 MB 标注 + 568 个单页 PDF，约 150 MB
python parsebench/tools/render_pages.py --dpi 150  # PDF → PNG
python parsebench/tools/chart_split_stats.py       # 统计写入 data/stats/
```

只拉 chart 一个维度，其余四维不下载。

---

## TODO

- [x] **基准 review 与数据落地**
  - [x] 论文与官方评测代码逐条核对，写进 `review/01`–`review/03`
  - [x] chart 分片下载（4,864 条标注 / 568 页 / 99 文档）
  - [x] 568 页渲染为 PNG
  - [x] 标注统计固化到 `data/stats/chart_split_stats.json`
  - [x] 改进清单 `review/04`，六项 + 优先级
  - [x] 分析系统设计 `review/05`，结论是单 VLM

- [ ] **A · 把 568 页跑通，拿到自己的基线**
  - [ ] A1 llmkit 加图像通路——`types.py` 加 `Image` 与 `Message.images`，`providers.py` 写 block 列表，`client.py` 透传并把图摘要收进缓存键（约 30 行，改在 llmkit 里）
  - [ ] A2 `tools/probe_pages.py`——A parse（整页 markdown）与 B profile（结构化标签）两条通路，走 `llm.map()` 并发
  - [ ] A3 `tools/score_pages.py`——接官方 `ChartDataPointRule` 打分，`parse_bench` 按可选依赖装
  - [ ] A4 产出 `data/stats/chart_profile.json` 与 `data/stats/baseline_scores.json`

- [ ] **B · 从样例与失败案例倒推改动**
  - [ ] B1 图表类型 / 面板数 / 稠密度分布 → 定 [G4](review/04_pipeline_gap.md#g4--轮转图的族采样加权重向量) 权重向量与 [G5](review/04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量) 稠密度区间
  - [ ] B2 失败六类归因（无表 / 值不准 / 标签没关联 / 量纲错 / 漏图 / 串系列）→ 校准 04 的优先级
  - [ ] B3 饼图在 5% 容差下的可读比例 → 决定饼图是否进值目标
  - [ ] B4 核实 [03 §5](../storyline/parsebench_chart/03_render.md#5-页面合成)「单页多图」的规格状态
  - [ ] B5 稠密度与失败率的相关性 → 若显著，即为 G5 的直接证据

- [ ] **C · 流水线改造**（规格写回 `storyline/`，实现进 `src/chartgen/`）
  - [ ] C1 [G1](review/04_pipeline_gap.md#g1--readable-从二值门改为按可达精度分级) `readable` 二值门 → 每 mark 的可达精度 ε；角度画法按同式重算
  - [ ] C2 [G2](review/04_pipeline_gap.md#g2--面板维进入键) 多面板图加 `panel_key`
  - [ ] C3 [G3](review/04_pipeline_gap.md#g3--加一个整页-markdown-导出) 整页 markdown 导出（长表 + 表前标题）
  - [ ] C4 [G4](review/04_pipeline_gap.md#g4--轮转图的族采样加权重向量) 族采样权重向量，默认维持均匀
  - [ ] C5 [G5](review/04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量) 抬高稠密度上限
  - [ ] C6 [G6](review/04_pipeline_gap.md#g6--风格向量补三维) 风格向量补三维：标注形态、刻度格式与单位位置、负值零线

- [ ] **D · 评测闭环**
  - [ ] D1 用 C3 的导出在 568 页上自评，与 A4 基线同口径
  - [ ] D2 训练后复评；Charts 与 Visual Grounding 两维同时报告
  - [ ] D3 消融：ε 分级 vs 二值门、有无 `panel_key`、稠密度阶梯
