# 01 · 任务定义

> 现有 pipeline 的最终产出是 `{图, 问题, 答案, 推理链}`。本方案换成
> `{图, 结构化表, 溯源标注}`。这一节确定要对齐什么、输出什么、用什么评。

**本文索引**
1. [ParseBench 的五个维度与我们的选择](#1-parsebench-的五个维度与我们的选择)
2. [输出规格](#2-输出规格)
3. [mark 级 grounding 的定位](#3-mark-级-grounding-的定位)
4. [评测与消融](#4-评测与消融)

---

## 1. ParseBench 的五个维度与我们的选择

ParseBench 含约 2,000 页人工核验的企业文档（保险 / 金融 / 政府），五个维度**分开评分**：Tables、Charts、Content Faithfulness、Semantic Formatting、Visual Grounding。

我们对准其中两个：

| 维度 | 规模与任务 | 指标 | 当前最好 |
|---|---|---|---|
| **Charts** | 568 页 / 1,039 张图（bar、line、pie、compound）。转成带精确数值与标签的结构化表 | `ChartDataPointMatch`：被核验数据点在解析输出表中的命中比例。对表格转置不敏感，容忍数值格式差异 | 78.1%；**多数专用 parser 低于 6%** |
| **Visual Grounding** | 每个抽取出的元素能否指回精确的源位置 | Element Pass Rate：定位（IoA 阈值）+ 分类 + 内容归属三项同时成立 | layout-aware 流水线 70–81%；**纯 VLM 6–7%** |

**它的标注方式值得直接照抄**：不标完整 ground-truth 表（成本高且脆弱），而是每张图标注**不超过 10 个 spot-check 点**，每点带容差——图上显式画出的值要求精确匹配，需要视觉估读的值给 1% 相对容差。

**它的困难来源**（决定了 [05_render.md](05_render.md) 要做什么）：

- 有无数值标注被刻意作为策展划分轴——不画数值的图强制像素几何估读
- 共享坐标轴与共享图例的多面板版面——图例项必须绑到正确的面板
- 自定义 BI 配色、企业信息图风格、低分辨率、扫描伪影
- 数字格式归一化：货币符号、千分位、百分比
- compound chart 的双轴

---

## 2. 输出规格

每个渲染出的图（或页面）产出三样：

| 产出 | 内容 | 对应维度 |
|---|---|---|
| **结构化表** | 图上所有 mark 的 (键, 值) 全集 | Charts |
| **spot-check 标注集** | ≤10 个点，每点带容差（画了标注 → 0；没画 → 1%） | Charts，与其指标直接对接 |
| **页面元素框** | `{Text, Table, Picture, Page-Header, Page-Footer}` 的 bbox 与类别 | Visual Grounding，标签集完全对齐 |

第三项只有在渲染进页面（而非裸图像）时才存在，见 [05_render.md](05_render.md)。

---

## 3. mark 级 grounding 的定位

**ParseBench 本身不要求图表内部的 bbox。** 一根柱子的框不是它的任何一个输出——Charts 维度只要表，Visual Grounding 把整张图当作一个 `Picture` 区域。

因此 mark 级 grounding 在本方案中有两个身份，需要在写作与实验设计中严格区分：

1. **训练侧的中间监督，不是输出格式。** 机制假设：能定位 mark 的模型读值更忠实。这是可消融的机制主张，比"又一个数据集"是更强的论文。
2. **其他三个基准的直接评测目标。** ChartREG++、ChartAB、LongChart VQA 的 grounding 分数目前都很低（最好 F1 < 50%；要求同时输出 bbox 时最好模型从 85.5% 掉到 57.6%，且所有模型 mDIoU 为负），提升空间干净。

---

## 4. 评测与消融

**主目标**（要求提升）
- ParseBench：Charts + Visual Grounding
- ChartREG++：point / bbox F1
- ChartAB：grounding & dense alignment
- LongChart VQA：grounding / pointing 子集

**边界条件**（要求不退化，这是主张的可证伪处）
- CharXiv-Reasoning、ChartQAPro

**鲁棒性**（检验 [05_render.md](05_render.md) 的风格向量是否奏效）
- CHART NOISe 扰动集

**关键消融**（决定原子粒度是否成立）
- 关掉溯源第三层（L2）后重训。若 grounding 指标不变，则原子粒度缺乏实验支撑，应在论文中降级。见 [06_provenance.md](06_provenance.md)。

**数据构成**：不做纯合成。合成负责 grounding / 溯源 / 风格配对（真实图表无法提供的部分），真实图表负责风格分布。
