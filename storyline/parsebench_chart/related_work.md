# Related Work

截至 2026-08 的图表理解相关工作。按轴组织，每轴末尾标出与本方案的关系。

**本文**
1. [基准](#1-基准) · 2. [数据与生成方法](#2-数据与生成方法) · 3. [模型与训练](#3-模型与训练) · 4. [综述](#4-综述) · 5. [定位](#5-定位)

> **引用陷阱**：`2604.21344`（Beyond Single Plots，多图 QA）与 `2507.11939`（多语言 chart QA）的数据集**重名**，都叫 PolyChartQA，是两篇不同的工作。
> 标注为「二级来源」的数字未经原文核对，正式引用前需核实。

---

## 1. 基准

### 1.1 单图 QA — 已饱和

| 工作 | 时间 | 规模与来源 | 现状 |
|---|---|---|---|
| **PlotQA** | WACV'20 | 模板合成 | 已解决 |
| **ChartQA** | ACL Findings'22 | 网络爬取（Statista、Pew、OWID、OECD） | **饱和**。Chart-R1（7B）达 91.04% |
| **ChartBench** | 2023 | 2,100 图 / 18,900 问（2,100 数值 + 16,800 是非） | — |
| **ChartX / ChartVLM** | `2402.12185` | 每条数据四模态（图像 / CSV / Python / 文本），测试集 1,152 QA | — |
| **CharXiv** | `2406.18521` | 2,323 张 arXiv 论文图；4,000 descriptive + 1,000 reasoning | 发布时 GPT-4o 47.1%、人类 80.5%；2026 年 GPT-5.2 报告 88.7%（二级来源）——**已超人类基线** |
| **ChartQAPro** | `2504.05506` | 1,341 图 / 157 个平台 / 1,948 QA；问题更长更多样 | 仍有空间 |
| **EvoChart-QA** | 2025 | — | — |
| **ChartMind** | `2505.23242` | 复杂真实场景多模态 chart QA | — |

> 单图推理这条轴上，ChartQA 由 7B 模型达到 91%，CharXiv 推理超过人类基线。本方案不以此为主目标，只将其列为**不得退化**的边界条件。

### 1.2 多图 — 12 个月内密集出现

| 工作 | 时间 | 构造方式 | 关键数字 |
|---|---|---|---|
| **MultiChartQA** | `2410.14179` NAACL'25 | — | — |
| **InterChart** | `2508.07630` | 三层：DECAF（分解真实图）/ SPECTRA（LLM 生成共享坐标轴表 → human-in-the-loop 渲染）/ STORM（OWID 真实折线对） | 5,214 QA / 2,706 图。Gemini-1.5 Pro 逐层 65.2 → 59.1 → 34.8 |
| **PolyChartQA**（多图） | `2604.21344` | 真实复合图，来自 CS 论文，保留原始复合结构 | 534 图 / 2,297 子图 / 2,694 QA。闭源模型多图较单图掉点最多 36.98% |
| **PolyChartQA**（多语言） | `2507.11939` | 含子图级图表类型与同质性标注；问题不显式指明子图 | 与上者同名不同工作 |
| **MultiChartQA-R** | OpenReview'26 | 四级递进任务：跨图趋势对比、互补数据整合、异常与因果、策略建议。三种语言 | 每语言 695 图-代码对 / 2,160 QA |
| **ChartWalker** | `2606.23997` | 跨图 RAG，层次知识图 | — |
| **LongChart VQA** | `2608.01328` | **人工构建 latent 依赖图 → LLM 合成基础数据 → 确定性传播到关联图表 → 平行生成图与问题 → 人工验证** | 557 图 / 2,876 问；平均 6.5 图/实例（3–18）；最多 8 跳；11 种图表。人工约 30 分钟/set、共 15 天。**仅 benchmark，不发布训练数据；作者自列 scale 为 limitation** |

> **LongChart VQA 与原 Table Amortization 同构**——共享数据空间保证跨图一致，确定性传播。差异在于它是 human-in-the-loop 且规模受限。这是本方案放弃「跨图一致性」作为 contribution 的直接原因。

### 1.3 Grounding 与归属 — 本方案的主战场

| 工作 | 时间 | 内容 | 结果 |
|---|---|---|---|
| **ChartLens** | `2505.19360` ACL'25 | 细粒度视觉归属：分割 + set-of-marks 提示。附 ChartVA-Eval（合成 + 真实） | 面向答案级归属 |
| **ChartPoint** | ICCV'25 | PointCoT：让模型生成 bbox 并按位置标注重渲染图表，把推理步骤与视觉区域连起来 | 推理时机制 |
| **InfoDet** | `2505.17473` | 信息图元素检测，大规模 bbox 标注 | 检测导向 |
| **ChartAB** | `2510.26781` | chart grounding & dense alignment | 小元素定位、密集版面下显著退化 |
| **START** | `2512.07186` | 空间与文本联合学习 | — |
| **ChartREG++** | `2605.07415` | 指代表达 grounding。850 图 / 3.4K 指代 / **18 种元素类型** / 三类指代线索（数据、视觉、文本定位）/ point·bbox·mask 三种格式。提出**利用 matplotlib Artist 层级做 LLM-free mask 合成** + Mask2Former + Set-of-Mark | **最好模型 point/bbox F1 < 50%**；平均每条指代 9.7 个目标 |
| **RADAR** | `2508.16850` | 推理引导的归属框架 | — |

> 「自己渲染所以标注免费」这一思路已由 ChartREG++ 发表（mask 层面）。本方案的差异在 [第 5 节](#5-定位)。

### 1.4 文档解析 — 本方案的目标任务

| 工作 | 时间 | 内容 | 关键结果 |
|---|---|---|---|
| **OmniDocBench** | CVPR'25 | 多样 PDF 文档解析，完整标注。2026-03 更新纳入 dots.ocr、MinerU2.5、DeepSeek-OCR-2 | — |
| **MDPBench** | `2603.28130` | 真实场景多语言文档解析 | — |
| **ParseBench** | `2604.08538` | 约 2,000 页人工核验企业文档（保险 / 金融 / 政府）。五维度分开评分：Tables、**Charts**、Content Faithfulness、Semantic Formatting、**Visual Grounding** | 见下 |
| **ChartArena** | `2606.01348` | 2,400 图 = 8 个图表族（含**流程图、思维导图**）× 中英双语 × 3 场景（数字渲染 / 翻拍 / 手绘）× 6 种输出格式 | Gemini 3.1 Pro 最好；radar 对所有模型都难；手绘场景显著退化；专用 chart parser 完全不支持图式结构 |

**ParseBench 细节**（本方案的对齐目标）

- **Charts 维度**：568 页 / 1,039 图（bar、line、pie、compound）。标注方式为每图 ≤10 个 spot-check 点，先由 Gemini 3.0 Flash agent 生成再逐点人工核验；容差为显式画出的值精确匹配、需估读的值 1% 相对容差。指标 `ChartDataPointMatch` 对表格转置不敏感、容忍数值格式差异。
- **策展划分轴**：刻意同时收录「显式写出数值的图」与「完全不写数值的图」；离散 vs 连续序列；稀疏 vs 稠密；单图页 vs **共享坐标轴的多图版面**。
- **Visual Grounding 维度**：Element Pass Rate 要求三项同时成立——定位（IoA ≥ 0.50 从 GT 侧、≥ 0.20 反向）、分类（`Text / Table / Picture / Page-Header / Page-Footer`）、内容归属（token F1 ≥ 0.80，chart 类区域改用召回导向）。

| 方法 | Charts | Visual Grounding |
|---|---|---|
| LlamaParse Agentic | 78.11% | 80.62% |
| Gemini 3 Flash | 64.8% | — |
| Reducto | 57.0% | — |
| Azure Document Intelligence | 1.6% | 73.8% |
| AWS Textract | — | 70.4% |
| Google Cloud Doc AI | 1.4% | — |
| Dots OCR 1.5 | 0.9% | — |
| GPT-5 Mini | — | 6.2% |
| Haiku 4.5 | — | 6.7% |

> 全局最高 84.9%（LlamaParse Agentic），且**没有任何方法在五个维度上都强**。Charts 是分化最剧烈的维度，多数专用 parser 低于 6%。纯 VLM 与 layout-aware 流水线在 Grounding 上相差一个数量级。

### 1.5 鲁棒性与幻觉

| 工作 | 时间 | 发现 |
|---|---|---|
| **Do MLLMs Really Understand the Charts?** | `2509.04457` | 系统性数据抽取、数值推理、逻辑一致性缺陷；产出貌似合理但错误的答案 |
| **ChartHal** | `2509.17481` | 细粒度图表幻觉评估框架 |
| **Losing the Plot / CHART NOISe** | `2509.18425` | 10 类图像损坏 × 2 档强度 + 4 种遮挡策略（≤7% 面积）。**Gemini 在大幅对比度扰动下 88% → 57%**；失败形式为编造数值、误读趋势、实体混淆，且保持高置信度并给出合理解释 |
| **Navigating the Mirage** | `2603.28583` | 误导性图表 QA 的双路径 agentic 框架 |

---

## 2. 数据与生成方法

### 2.1 合成生成

| 工作 | 时间 | 规模 | 方法 |
|---|---|---|---|
| **CoSyn** | `2502.14846` | — | 代码引导的文本密集图像合成 |
| **ChartCards** | `2505.15046` | — | chart-metadata 框架，一份元数据支撑多任务 |
| **ChartGen** | `2507.19492` | 222.5K 图-代码对 | 13K 种子图 → VLM chart-to-code → LLM 代码增广。27 种图表 |
| **ECD** | `2508.06492` | — | 五步：数据/函数分离 → 子图条件生成 → 视觉多样化 → 低质过滤 → GPT-4o 生成 QA。**明确论证合成-真实风格差距限制迁移** |
| **ChartZero** | `2605.05820` | 100K | matplotlib，20 个参数化函数族；随机化曲线参数、重叠模式、线型、配色、标签、图例、网格、背景纹理；在线增广含仿射形变、色彩抖动、高斯模糊、JPEG |
| **ChartNet** | `2603.27064` MIT+IBM | **1.5M 合成 + 30K 真实** | 150K 种子图 → VLM 反推 Python → LLM 迭代增广 → 渲染 + 质量过滤（初筛 36.5%）。24 种图表 × 6 个绘图库。五重对齐：代码 / 图像 / CSV / 摘要 / 带 CoT 的 QA。含 96K 人工核验子集、**从绘图代码抽取的 geometry-aware grounding 标注（axes / ticks / gridlines / legends / patches），bbox 经 entropy 过滤**、7.6K 安全样本 |
| **LongChart VQA** | `2608.01328` | 557 图 | 见 §1.2 |

**ChartNet 的结果**：微调 256M–7B 模型后，图表重建 +42.4 点、数据抽取 +41.8 点（超过 GPT-4o 的 46.7%）、摘要 +31.4 点、QA 推理 +15.2 点；2B/7B 微调模型持续超过 20B–72B 模型。

### 2.2 真实图表侧

| 工作 | 时间 | 立场 |
|---|---|---|
| **BigCharts-R1** | `2508.09804` | 真实图表图像 + SFT + GRPO。**明确反对纯合成**：真实图表含合成无法覆盖的自然变异、渲染伪影与设计选择 |
| **CharTool / DuoChart** | `2604.02794` | 合成 + 真实**双源**；agentic RL 学习使用图像裁剪与代码计算工具。CharXiv-R **+8.0%**、ChartQAPro **+9.78%** |

> 合成-真实差距是对任何纯合成工作的既定反对意见。本方案采用双源构成：合成负责位置、来源、风格配对；真实图表负责风格分布。

---

## 3. 模型与训练

### 3.1 专用图表模型谱系

| 工作 | 时间 | 要点 |
|---|---|---|
| **ChartOCR** | 2021 | 深度混合框架做图表数据抽取 |
| **DePlot** | 2023 | plot-to-table 翻译 + 单次视觉语言推理 |
| **MatCha** | 2023 | 数学推理与图表反渲染联合预训练 |
| **UniChart** | `2305.14761` EMNLP'23 | 统一图表理解与推理的视觉语言预训练模型 |
| **ChartLlama** | 2023 | 基于 LLaVA，多样图表与下游任务 |
| **ChartAssistant / ChartAst** | 2024 | chart-to-table 预训练 + 多任务指令微调 |
| **ChartInstruct** | 2024 | 大规模图表指令微调 |
| **ChartGemma** | 2024 | **直接从图表图像**生成指令微调数据，不经中间表格 |
| **TinyChart** | 2024 | token 合并解决高分辨率图表的推理效率 |
| **AskChart** | `2412.19146` | 文本增强的通用图表理解 |
| **StrucTexTv3** | `2405.21013` | 文本密集图像感知，图表解析任务领先 |
| **Simplot** | `2405.00021` | chart-to-table，超过 DePlot 与 UniChart |
| **ChartMoE** | `2409.03277` ICLR'25 | 多样对齐专家连接器的混合 |
| **ChartReasoner** | `2506.10116` | 代码驱动的模态桥接，长链推理 |
| **ChartEditor** | `2511.15266` | 图表编辑的强化学习框架 |

### 3.2 强化学习与推理

| 工作 | 时间 | 数据与方法 | 结果 |
|---|---|---|---|
| **Chart-R1** | `2507.15509` | ChartRQA 258K（SFT 228K + RL 30K）。**代码优先**：arXiv 真实表格 → LLM 写 matplotlib → LLM 合成问题、答案与推理路径。多子图用 `plt.subplots()`，显式提示生成跨子图问题。GRPO 复合奖励（软匹配 + 编辑距离） | ChartQA **91.04%**、CharXiv-RQ 46.2% |
| **BigCharts-R1** | `2508.09804` | 真实图表 SFT + GRPO 可验证奖励 | — |
| **Chart-RVR** | `2510.10973` | GRPO 加图表代理任务奖励 + 过程一致性目标 | — |
| **Chart-RL** | `2604.03157` | 策略优化 RL 增强图表视觉推理 | — |
| **CharTool** | `2604.02794` | 见 §2.2 | CharXiv-R +8.0% |

---

## 4. 综述

| 工作 | 时间 | 要点 |
|---|---|---|
| **The State of the Art in Creating Visualization Corpora** | `2305.14525` | 图表语料构造方法综述。指出 **bbox 是最常见的标注类型**，因为多数任务都需要元素位置 |
| **Transformers Utilization in Chart Understanding** | `2410.13883` | — |
| **Multimodal Information Fusion for Chart Understanding** | `2602.10138` | 提出 **canonical / non-canonical** 图表基准的分类。指出当前 MLLM 的感知保真与认知推理缺陷导致鲁棒性不足与无根据幻觉；未来方向指向高级对齐与强化学习 |

---

## 5. 定位

本方案与最近的五项工作的区别：

| | 它做了什么 | 本方案的差异 |
|---|---|---|
| **ChartNet** `2603.27064` | 1.5M 规模；从绘图代码抽取 geometry-aware 标注 | 它 ground 的是**结构元素**（axes / ticks / gridlines / legends / patches）。其图表来自 VLM 反推种子图的代码，**底下不存在原子事实表**，一个图元只能指回聚合表的一个单元格。本方案 ground 的是「一次事件 → 图元 → 聚合行数」这条链 |
| **ChartREG++** `2605.07415` | matplotlib Artist 层级 → LLM-free mask 合成 | 它面向**指代表达 grounding** 这一独立任务。本方案把区域作为**转录输出的一部分**：输出单位是 `(键, 值, 区域)` 而非二选一 |
| **LongChart VQA** `2608.01328` | 依赖图 → 确定性传播 → 跨图一致 + 现成 bbox 标注 | 它 human-in-the-loop（30 分钟/set、15 天）、仅 benchmark、作者自列 scale 为 limitation。本方案全自动，目标是训练语料 |
| **ChartLens** `2505.19360` | 答案级视觉归属 | 归属发生在**回答之后**，是解释机制。本方案的区域与值**同时产出**，是输出格式 |
| **ParseBench** `2604.08538` | 五维度分开评分 | 它指出没有方法在五维度上都强，Charts 与 Visual Grounding 的最好成绩分属不同方法族。本方案的目标是**单模型同时强**——现状是商业多阶段流水线两项均高（78.1 / 80.6），纯 VLM 在 Grounding 上是个位数（6–7%） |

**本方案的主张与失败判据**见 [06_output.md §5](06_output.md)。
