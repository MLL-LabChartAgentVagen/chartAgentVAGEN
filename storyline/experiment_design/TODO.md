# TODO · 执行清单

> 按优先级 P0 / P1 / P2 排序。每项标注：所属维度 · 预估工程量 · 是否阻断后续工作。
>
> 勾选已完成项：把 `[ ]` 改成 `[x]`。

---

## 总体节奏（8 周计划）

| 周 | 主要交付 | 关键阻断点 |
|---|---|---|
| W1 | P0 全部完成（pipeline 基础设施） | bbox 渲染层、ViewSpec 解析器 |
| W2 | Exp A (Channel Ablation) 跑完 | **不通过则重新评估 storyline** |
| W3–4 | Exp D (Killer) 跑完 + 子分析 | 主结果数字 |
| W5–6 | Exp B, C (Necessity, Pareto) | 充实贡献 |
| W7 | Exp E (Capability) + 50 题人类 baseline | 叙事支撑 |
| W8 | Exp F (OOD) + paper draft | 堵 generalization |

---

## P0 — 阻断性（不做后面没法跑）

### Pipeline 基础设施

- [ ] **bbox 渲染层** · [03 §3.3](03_动作空间.md) · 1.5 人周 · 阻断 Exp A/D/E
  - 写 matplotlib bbox collector，导出 `chart.png` + `chart_bbox.json`
  - 8 种 chart 各写一个 `render_dispatcher` 入口
- [ ] **ViewSpec JSON 接口 + 解析兜底层** · [03 §3.2](03_动作空间.md) · 0.5 人周
  - 复用 [phase_3.md ViewSpec dataclass](../data_generation/phase_3.md#311-core-extraction-function)
  - 加一个温度 0 的 NL → ViewSpec 解析器
  - 单独评估解析失败率（附录数字）
- [ ] **answer_schema 字段** · [02 §2.1.b](02_pipeline改进.md) · 0.5 人周
  - Phase 3 QA 生成器每题输出 (question, answer_schema)
  - 6 种 answer 类型分别实现机评逻辑
- [ ] **$k^*$ 反向搜索算法** · [01 §1.2](01_数据与问题.md) · 0.5 人周
  - 在 Phase 3 标注阶段对每题计算 $k^*$
  - 用 operator pipeline 反向跟踪依赖列

### 数据底料

- [ ] **DashboardIllusionInjector 模块** · [02 §2.2.a](02_pipeline改进.md) · 1 人周 · 阻断 Adversarial $D_0$
  - 实现 4 种 illusion: simpson / denominator / boundary / population
  - 自动校验"naive answer ≠ ground truth"
- [ ] **带毒题 25% 配额** · [01 §1.3](01_数据与问题.md) · 0.5 人周
  - 3 类带毒题（Schema-Unanswerable / Budget-Unanswerable / $D_0$-Sufficient Trap）
  - 配套打分逻辑（hallucination rate 计数器）
- [ ] **Hypothesis 反向规则化生成** · [02 §2.1.a](02_pipeline改进.md) · 0.5 人周
  - PATTERN_TO_HYPOTHESIS 映射表
  - 切断 LLM 闭环污染

---

## P1 — 重要（少了论文 borderline）

### 实验执行

- [ ] **Exp A · Channel Ablation** · [04 §4.4 Exp A](04_实验与baseline.md) · 1 周
  - **必须先跑** — 决定论文存在性
  - B4 (CSV-only) × B5 (PNG+CSV) × LDW (PNG-only)
- [ ] **Exp D · Killer 实验** · [05](05_killer实验.md) · 1 周
  - Passive-All × LDW-Active × Oracle
  - 3 个子分析（按难度 / 按能力 / 失败模式）
- [ ] **Exp B · Action Necessity** · [04 Exp B](04_实验与baseline.md) · 1 周
  - model × protocol 二维热力图
- [ ] **Exp C · Evidence Pareto** · [04 Exp C](04_实验与baseline.md) · 1 周
  - $B_v \in \{2, 4, 8, 16, \infty\}$
- [ ] **Compute-fairness 表** · [04 §4.3](04_实验与baseline.md) · 持续
  - 每个实验主表附 token / cost / time

### 数据质量

- [ ] **HumanSpotCheck** · [02 §2.2.b](02_pipeline改进.md) · 12 人时
  - 500 题，2 标注员，Cohen's κ ≥ 0.7
  - 验证 $k^*$ 与人类直觉一致
- [ ] **$D_0$ 三档实验** · [01 §1.1](01_数据与问题.md) · 0.5 周
  - Floor / Realistic / Adversarial 三档分别跑
  - 主表用 Realistic，主推 figure 用 Adversarial

### 评估指标

- [ ] **Bbox-Grounding metric** · [04 §4.2](04_实验与baseline.md) · 0.5 人周
  - IoU ≥ 0.5 的引用比例
- [ ] **Hallucination Rate metric** · [04 §4.2](04_实验与baseline.md) · 0.5 人周
  - 在 Schema-Unanswerable 题上的自信错答比例
  - **论文最重要的单个数字**

### Baseline 实现

- [ ] **B0 Passive-VLM** · 已有协议 · 0.2 周
- [ ] **B1 Random-Request** · 已有协议 · 0.2 周
- [ ] **B2 Oracle-View-Set** · 0.3 周
- [ ] **B3 Passive-All** · **killer baseline** · 0.3 周
- [ ] **B4 CSV-Channel** · 0.3 周
- [ ] **B5 PNG+CSV** · 0.3 周
- [ ] **B6 ReAct-CoT** · 0.5 周（LangChain 集成）

---

## P2 — 锦上添花（reviewer 加分项）

- [ ] **Exp E · Capability Profile** · [04 Exp E](04_实验与baseline.md) · 0.5 周
  - 按 Read / Reveal / Reconcile / Debunk 分别评估
- [ ] **Exp F · OOD on Real Dashboards** · [04 Exp F](04_实验与baseline.md) · 1 周
  - 50 张手标真实 dashboard
  - 堵 generalization 攻击
- [ ] **B7 Human-Junior** · [04 §4.1](04_实验与baseline.md) · 12.5 人时
  - 5 个 junior 分析师 × 50 题 × 30 min
- [ ] **难度桶配额** · [02 §2.1.c](02_pipeline改进.md) · 0.3 周
  - 把 cap_per_family 改成 $k^*$ 桶 quota
  - 保证 Very Hard 桶不被压扁

### 可选扩展

- [ ] **`refine_view` action** · [03 §3.1.d](03_动作空间.md) · 0.5 周
  - 仅在 reviewer 提出后做
- [ ] **chart 类型扩展（16 全集）** · [03 §3.4](03_动作空间.md) · 1 周
  - 第二版加 radar / treemap / violin / 等
- [ ] **LDW-Gym 发布层** · [storyline §8](../storyline/research_storyline_zh.html) · 2 周
  - generate_episode(seed) 接口
  - Gym 风格 API
  - 排行榜双分割机制

---

## 进度追踪表

| 阶段 | 预估总工程量 | 已完成 | 剩余 |
|---|---|---|---|
| P0 基础设施 | 4.5 人周 | 0 | 4.5 |
| P1 实验主体 | 5.5 人周 + 12 人时 | 0 | 5.5 + 12 |
| P2 加分项 | 4 人周 + 12.5 人时 | 0 | 4 + 12.5 |
| **总计** | **14 人周 + 24.5 人时** | 0 | 14 + 24.5 |

**双人配合预计 7 周即可交付主论文实验。**

---

## 风险记账（持续更新）

| 风险 | 影响 | 缓解 |
|---|---|---|
| Exp A 跑出来 CSV 完爆 PNG | 论文存在性 | 重新评估 storyline；考虑转向 SQL-augmented agent 方向 |
| Exp D Passive-All ≈ LDW | 主结果失败 | 见 [05 §5.7](05_killer实验.md) 情况 1 |
| VLM ViewSpec 解析失败率 > 30% | agent 行为不可控 | 加重试机制；尝试 fine-tune 小模型做解析专家 |
| Human spot-check κ < 0.7 | $k^*$ 定义有争议 | 重新出指引，加 3-人仲裁；缩窄 $k^*$ 定义 |
| OOD（真实 dashboard）下 LDW 优势消失 | generalization 攻击 | 说明合成 benchmark 的 sim-to-real gap，作为 future work |

---

## 完成定义（每项任务的 done 标准）

| 任务类型 | done 条件 |
|---|---|
| 代码模块 | 单元测试通过 + 集成测试通过 + 文档写完 |
| 实验 | 主表 + 子分析 + compute-fairness 表 + 可视化 |
| 数据集 | 通过 [phase 2 三层验证](../data_generation/phase_2.md#29-three-layer-validation) + 人工抽样 50 题确认无明显错误 |
| 论文 figure | 数据 + 设计稿 + 同事 review |

---

## 下一步

回到 [README](README.md) 选择从哪个维度入手。

**强烈建议从 P0 的"bbox 渲染层 + ViewSpec 解析"开始** — 它是其他三个维度的物质基础，做完之后实验设计与 metric 都能直接跑通。
