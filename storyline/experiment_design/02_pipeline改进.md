# 02 · Pipeline 评估与改进

> **回答的两个问题：**
> 1. 当前 [data_generation pipeline](../data_generation/data_generation_pipeline.md) 有哪些隐藏污染？
> 2. 为支持 LDW 协议，需要新增哪些模块？

---

## TL;DR

**3 大隐藏风险（按严重性排序）：**
1. **Data leakage**：LLM 既生成假设又评估 agent — 闭环污染
2. **Question ambiguity**：自然语言答案没有 schema — 无法机评
3. **Difficulty collapse**：`cap_per_family` 把高难题型压没了

**2 大新增模块：**
- `DashboardIllusionInjector`（自动构造误导性 $D_0$）
- `HumanSpotCheck`（500 题样本，盲打 $k^*$ 双人一致性）

---

## 2.1 三大隐藏风险

### 2.1.a 风险 1：Data Leakage（闭环污染）

#### 直观问题

[phase_1.md](../data_generation/phase_1.md) 用 LLM 实例化 scenario。如果你**继续用同一个 LLM** 生成假设集 $H = \{h_1, \ldots, h_4\}$ 并标注哪条是真——

那么当 agent 也是同家族 LLM（例如 Claude 生数据，让另一个 Claude 做 agent）时，**评估者和数据生成者共享 prior**——in-family 优势是不公平的。

#### 比喻

就像让一个老师出题，又让他的学生考试，学生在没有任何作弊的情况下也会因为"猜中老师的思路"而占便宜。

#### 修补方案

**把假设集 $H$ 从 Phase 1 拆出来，改为从 Phase 2 schema metadata + 注入 pattern 反向规则化生成。**

每条 pattern 对应一个解释 $h_i$，参考 [phase_3.md §3.4 Pattern-Seeded QA](../data_generation/phase_3.md) 的现有表格，再加一行 "competing hypothesis label"：

| Pattern type（已存在） | 对应的解释 $h_i$（新加） |
|---|---|
| `outlier_entity` | "某个实体异常突出" |
| `trend_break` | "在某时刻发生结构变化" |
| `ranking_reversal` | "metric A 上的领先者在 metric B 上垫底" |
| `dominance_shift` | "原本领先的实体被超越" |
| `convergence` | "原本分歧的序列趋同" |
| `seasonal_anomaly` | "周期性效应被误读为长期趋势" |

加上 SwiftEats 案例需要的 4 个：

| 新加 pattern type | 对应的解释 $h_i$ |
|---|---|
| `denominator_shift` | "分母变了导致数字变化" |
| `metric_boundary_shift` | "测量边界变了导致数字变化" |
| `population_selection` | "服务对象被悄悄筛选" |
| `simpson_reversal` | "Simpson 悖论：边际趋势与分组趋势相反" |

#### 一个具体实现

```python
def generate_hypotheses(schema_metadata):
    """从 schema + patterns 反向规则化生成 H，不调用 LLM。"""
    hypotheses = []
    for pattern in schema_metadata["patterns"]:
        h = PATTERN_TO_HYPOTHESIS[pattern["type"]](pattern)
        hypotheses.append(h)
    # 用反事实 schema 生成 distractor 假设
    while len(hypotheses) < 4:
        distractor = sample_distractor(schema_metadata, hypotheses)
        hypotheses.append(distractor)
    return hypotheses  # 完全确定性，与 LLM 解耦
```

**好处：**
- 符合 CLAUDE.md "No LLM in Phase 3" 原则
- ground truth 完全确定，可逐位复现
- 切断了 in-family 污染

---

### 2.1.b 风险 2：Question Ambiguity（无 schema 答案）

#### 直观问题

[phase_3.md](../data_generation/phase_3.md) 生成的问题是自然语言 + operator chain。但**答案的标准化形式没有规定**。

reviewer 必问：
> "agent 答 'about 18 minutes' vs 'around 18.3' vs 'eighteen' 怎么打分？"

#### 修补方案

每个问题输出 `(natural-language question, structured answer schema)` 二元组。

| 题型 | answer schema | 评分逻辑 |
|---|---|---|
| Scalar（数值） | `{"value": float, "unit": str, "tol": 0.05}` | 数值在 ±tol×value 内算对，单位必须匹配 |
| Ranking（排序） | `{"items": [...], "tie_break": "stable"}` | Kendall τ；完全匹配 = 1，反转 = -1 |
| Hypothesis | `{"accept": [h_ids], "reject": [h_ids]}` | micro-F1 |
| Existence（带毒题 A） | `{"answerable": false, "reason": "<列名> not in schema"}` | "insufficient" 标识 = 满分 |
| Trend | `{"direction": "increasing"/"decreasing"/"flat", "magnitude": ?}` | direction 严格匹配 + magnitude tol |
| Bbox-grounding | `{"bbox_refs": [(view_id, element_id), ...]}` | IoU ≥ 0.5 算对 |

#### SwiftEats 翻译

题："新算法下边缘区域接单率变化了多少？"

```json
{
  "question": "新算法下边缘区域的接单率与旧算法相比变化了多少？",
  "answer_schema": {
    "type": "scalar",
    "value": -41,
    "unit": "percentage_points",
    "tol": 0.10
  },
  "evidence_required": [{"view_id": "zone_heatmap", "region": "periphery"}]
}
```

#### 不这样做的代价

- "你们的评分是 LLM-as-judge，可解释性差，不可复现。"
- "scalar 题的 tolerance 是手动调的，会过拟合。"

---

### 2.1.c 风险 3：Difficulty Collapse（高难题型被压扁）

#### 直观问题

[phase_3.md §3.1.3](../data_generation/phase_3.md) 现在用 `cap_per_family(max_per_family=3)` 防视图爆炸。但这会**把高难题型一起压扁**——一个 $k^* = 4$ 的问题需要 4 张跨家族图，cap 之后可能根本生不出来。

#### 直观比喻

就像考试出题时，老师为了防止题量太大，每个章节最多出 3 题——结果高难度的"综合题"因为需要跨多个章节而消失了。

#### 修补方案

**改为 $k^*$ 分桶配额**，每个难度桶有最小 quota：

```python
DIFFICULTY_QUOTA = {
    "easy":      0.25,   # k* = 0–1
    "medium":    0.35,   # k* = 2
    "hard":      0.25,   # k* = 3
    "very_hard": 0.15,   # k* >= 4  — 高难度桶必须保留
}

def enumerate_views_with_difficulty_balance(master_table, schema):
    all_views = raw_enumerate(master_table, schema)
    # 不按 family cap，按 k* 桶 cap
    return balance_by_k_star(all_views, DIFFICULTY_QUOTA)
```

#### 不这样做的代价

- "你们的难度分布是个山型（中等题独大）——high-difficulty tail 太薄，无法证明 LDW 在难题上的优势。"
- "你们的 Pareto 实验在 $B_v = 4$ 之后没有继续提升，原因可能不是模型饱和，而是高难题根本没几道。"

---

## 2.2 两个新增模块

### 2.2.a 模块 1：`DashboardIllusionInjector`

#### 作用

给定一个 case，自动构造一个**会误导的 $D_0$**——选出投影使 Simpson reversal / 分母清洗 / 边界偏移**自然成立**。这是 Debunk 题的唯一可靠来源。

#### 直观比喻

就像新闻编辑刻意挑选一组数据来支持某个 headline——但**这是合成的，所以我们知道 ground truth**。

#### 实现思路

```python
class DashboardIllusionInjector:
    def __init__(self, schema_metadata, master_table):
        self.schema = schema_metadata
        self.M = master_table

    def construct_misleading_D0(self, pattern_id, target_illusion):
        """对给定的真实 pattern，构造让结论反向的 D0。"""
        # 1. 找到 pattern 涉及的列
        cols = self.schema["patterns"][pattern_id]["affected_cols"]
        # 2. 找一个 SQL 投影使其在边际上呈现相反趋势
        misleading_view = search_projection(self.M, cols, direction="reverse")
        # 3. 验证: D0 上的 naive 推理 != ground truth
        assert contradicts_ground_truth(misleading_view, pattern_id)
        return misleading_view

    def supported_illusions(self):
        return [
            "simpson_reversal",
            "denominator_shift",
            "metric_boundary_shift",
            "population_selection",
        ]
```

#### SwiftEats 翻译

对 SwiftEats 的 `denominator_shift` pattern：

```python
# 真实情况：成功率从 84% 跌到 57%
# 注入器找投影使 D0 上的 headline 显示"快了 42%"
D0_misleading_view = ViewSpec(
    chart_type="bar_chart",
    filter="status == 'delivered'",         # 只看成功订单
    group_by=["algorithm"],                  # 旧 vs 新
    agg={"pickup_to_dropoff": "AVG"},        # 只算 pickup→dropoff
    select_columns=["algorithm", "pickup_to_dropoff"]
)
# → 这就是那张"31 min 红，18 min 绿"的图
```

#### 工程量

预估 1 人周：核心是写"投影搜索 + 矛盾检测"逻辑。可以从 SwiftEats 这一个例子出发，把它机械化。

---

### 2.2.b 模块 2：`HumanSpotCheck`（最小化人工背书）

#### 作用

**不是验证答案**，而是**双人独立判定 $k^*$ 是否成立**——即"这个问题在不请求新视图时是否可解"。

只有 $k^*$ 由人工背书过，"探索是必要的"这条 claim 才不会被 reviewer 用一句"可能没你说的那么必要"戳穿。

#### 直观比喻

像数学竞赛题的"难度系数"——出题人觉得是 5 星，找两个高手做盲打，如果他们都说是 3 星，你就得调整或重出。

#### 实施细节

| 项 | 规模 / 标准 |
|---|---|
| 样本量 | 500 题 |
| 标注员 | 2 人独立判定 |
| 任务 | 给定问题 + $D_0$，判定"需要请求几张额外视图才能答出？" |
| 一致性门槛 | Cohen's κ ≥ 0.7 |
| 不一致处理 | 第三人仲裁 |
| 预算 | ≈ 12 人时（每题 1 分钟） |

#### 实施模板

发给标注员的指引：
> "请阅读以下问题和已给定的 $D_0$ 图表。你的任务**不是回答**这个问题，而是判定**至少需要请求几张新的视图**才能解出它。
> - 0: $D_0$ 已经足够
> - 1–4: 请简述你想请求的具体视图
> - "无法判定": 该问题超出当前 schema 能力"

#### 不这样做的代价

- "你们整个 benchmark 是 LLM 生 → LLM 答 → LLM 判，循环里没有人。"
- "你们的难度标注是自动的，可能与人类直觉不符——'必须 4 张视图'的题在熟练分析师眼里可能只需 2 张。"

---

## 2.3 流水线接口的增量改动

延续 [storyline §A 附录](../storyline/research_storyline_zh.html) 的"在现有流水线上的增量"思路：

| LDW 需要 | 现有提供 | 需要新增 |
|---|---|---|
| 隐藏主表 $M$ | Phase 2 输出 | — |
| 模式真值 $S$ | Phase 2 schema metadata | — |
| `request_view` 渲染 | Phase 3 SQL 投影 + 渲染器 | **bbox 导出层**（见 [03 §3.3](03_动作空间.md)） |
| 4 能力标签 | Phase 3 QA 生成器 | 加 capability tag + competing hypothesis 字段 |
| 元素级 bbox 真值 | 部分 | matplotlib bbox collector |
| 误导性 $D_0$ | 无 | **`DashboardIllusionInjector`** |
| $k^*$ 标注 | 无 | **反向搜索 + Human spot-check** |
| 答案 schema | 无 | **answer_schema 字段** |

**预估总工程量：3–4 人周。**

---

## 2.4 章节小结

| 子主题 | 一句话 | 必做改动 |
|---|---|---|
| Data leakage | 假设集从 Phase 1 LLM 改为从 patterns 反向规则化 | 加 PATTERN_TO_HYPOTHESIS 映射 |
| Question ambiguity | 每题输出 (NL question, answer schema) | Phase 3 QA 生成器加 schema 字段 |
| Difficulty collapse | family cap → $k^*$ 桶 quota | 改 enumerate_views 的 cap 策略 |
| 新模块 1 | `DashboardIllusionInjector` | 实现投影搜索逻辑 |
| 新模块 2 | `HumanSpotCheck` | 500 题，2 人，κ ≥ 0.7 |

---

## 下一步

- 数据底料 + pipeline 都过关了，agent 怎么和它交互 → [03 动作空间](03_动作空间.md)
- 怎么对比不同 baseline → [04 实验与 baseline](04_实验与baseline.md)
