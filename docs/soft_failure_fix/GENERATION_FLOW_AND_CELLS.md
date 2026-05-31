# 生成流程与 cell：从 Phase 1 context 到最终总表

> **目的**：用直观语言讲清「每次生成的总表 ↔ cell」的关系，以及一条记录如何从 Phase 1 的剧本一步步走到最终事实表。是 `AUDIT_2026-05-28.md §3`（M3 的 n<30）的背景读物。
>
> 与 `mechanisms/MECHANISM_3_DEEP_DIVE.md` 互补：那里讲 KS 失败机理，这里讲数据是怎么来的、cell 到底是什么。

---

## 1. 先建立直觉：总表是一本「流水账」

每次生成产出的总表（master table / fact table）就是**一本登记簿**：有 `target_rows` 行，每一行是**一条独立的记录/事件**（一次就诊、一天的客流、一笔订单）。列分两类：

```
┌─────────┬──────────┬───────────┬──────────┬──────────────┐
│ 日期     │ tier     │ program   │ residency│ length_of_stay│   ← 列
├─────────┼──────────┼───────────┼──────────┼──────────────┤
│ 2024-03 │ 三甲     │ 心内科     │ 本地     │ 8.2          │   ← 第 1 行 = 一条记录
│ 2024-07 │ 二甲     │ 骨科       │ 外地     │ 5.1          │   ← 第 2 行
│  ...    │  ...     │   ...     │   ...    │   ...        │
└─────────┴──────────┴───────────┴──────────┴──────────────┘
  └──── 维度列(categorical / temporal)────┘  └─ measure 列 ─┘
```

- **维度列**（categorical + temporal）：描述「这条记录属于谁、什么时候」——它们是被**先抽样**出来的标签。
- **measure 列**：描述「测到了什么值」——它们是**根据维度标签算/抽**出来的数。

---

## 2. cell 是什么？它对应一个 entity 吗？

**不对应。这是关键的概念区分。**

- 一个 **entity**（`key_entities`，如「心内科」）是**某一个维度列里的一个取值（level）**。
- 一个 **cell** 是**所有相关维度列各取一个 level 的组合**——是维度的**笛卡尔积**里的一格。

代码里 cell 的定义就在 [`statistical.py:171-178`](../../pipeline/phase_2/validation/statistical.py#L171-L178)：对一个 measure 的 param_model 里引用到的所有 categorical 列，做 `itertools.product` 取笛卡尔积，每一个组合 + 落进该组合的所有行 = 一个 cell。

用 M3 讨论里的例子最直观：`tier(3) × program(8) × residency(2)`

```
entity「心内科」  ──┐
                    │  它本身只是 program 这一维度的 1 个 level,
                    │  横跨了 3×2 = 6 个不同的 cell:
                    ▼
  cell = (三甲, 心内科, 本地)   ← 一个抽屉
  cell = (三甲, 心内科, 外地)
  cell = (三乙, 心内科, 本地)
  cell = (三乙, 心内科, 外地)
  cell = (二甲, 心内科, 本地)
  cell = (二甲, 心内科, 外地)

  总 cell 数 = 3 × 8 × 2 = 48 个抽屉
```

**所以关系是：**

- 一个 entity（单维度单 level）→ 横跨**很多** cell。
- 一个 cell → 是**每个维度各取一个 level 的交集**，通常对应不止一个维度。
- 一行记录 → 恰好落进**一个** cell（它每个维度的标签确定了它在哪个抽屉）。

**为什么要分 cell？** 因为同一个 cell 里的所有行，理论上服从**同一个分布**（同样的 tier+program+residency 决定同样的均值）。KS 检验只能检「一堆同分布的样本」，所以它必须把总表按 cell 拆开，逐抽屉检验。`n_cell` 就是某个抽屉里有多少行 —— 这正是 M3 里 n<30 的那个 n：

```
n_cell ≈ target_rows / cell_count
       ≈ 1000 / 48 ≈ 每屉 20 行 < 30   → 大量抽屉被跳过
```

> 这解释了为什么 Phase 1 把 `target_rows` 按 tier 抬高（simple 200–500 / medium 500–1000 / complex 1000–3000）**修不了** n<30：`target_rows` 是总行数，n<30 是单 cell 行数，两者被 `cell_count` 隔开，而 cell_count 在 Loop A 才确定。详见 `AUDIT_2026-05-28.md §3`。

---

## 3. 从 Phase 1 的 context 到最终表：一步步走

引擎的总公式写在 [`generator.py:5`](../../pipeline/phase_2/engine/generator.py#L5)：

```
M = τ_post ∘ δ ∘ γ ∘ β ∘ α(seed)
```

把它讲成一条流水线，跟着一条记录走一遍：

### 📜 第 0 幕 · Phase 1：写剧本（还没有任何数据）

[`scenario_contextualizer.py`](../../pipeline/phase_1/scenario_contextualizer.py) 让 LLM 产出一份「语义锚」：

```json
{
  "scenario_title": "2024 某三甲医院住院记录",
  "data_context": "由 XX 医院病案室收集……",
  "key_entities": ["心内科","骨科",...],          
  "key_metrics": [{"name":"length_of_stay","unit":"天","range":[2,20]}],
  "temporal_granularity": "monthly",
  "target_rows": 1000                              
}
```

这一幕**只有文字描述**，像电影的分镜剧本，告诉下游「该拍一个什么样的数据集」。`key_entities` 将来变成维度的 level，`target_rows` 决定总表要多少行。

### 🏗️ 第 1 幕 · Phase 2 Loop A：把剧本翻译成蓝图（还没有数据）

LLM 读剧本，写出一段 **SDK 声明代码**（[`sdk/simulator.py`](../../pipeline/phase_2/sdk/simulator.py) 的接口）：

```python
sim.add_category("program", values=["心内科","骨科",...], weights=[...])
sim.add_temporal("month", start=..., end=..., freq="MS")
sim.add_measure("length_of_stay", family="gaussian",
                param_model={"mu": {"intercept": 6,
                                    "effects": {"program": {"心内科": +2, "骨科": -1}}},
                             "sigma": 2.0})
sim.inject_pattern("seasonal_anomaly", ...)
```

产出是一份 **Declarations**：列注册表 + 维度组 + DAG + 每个 measure 的 `param_model`。这仍然是**蓝图/施工图**，没有一行数据。

> ⚠️ **cell 的数量在这一幕就被决定了**——取决于 LLM 把多少个 categorical 列塞进了 `param_model.effects`（[`_collect_predictor_cols`, statistical.py:185](../../pipeline/phase_2/validation/statistical.py#L185)）。这也是为什么 Phase 1 管不了 cell 数：它在这一幕才确定。

### 🎲 第 2 幕 · Phase α：搭骨架——给每行贴标签（cell 在此诞生）

[`skeleton.py::build_skeleton`](../../pipeline/phase_2/engine/skeleton.py#L39) 按 DAG 拓扑序，为全部 `target_rows` 行填好所有**维度列**：

- 独立 categorical 根：`rng.choice(values, p=weights)` 抽 1000 个 level（[skeleton.py:133](../../pipeline/phase_2/engine/skeleton.py#L133)）——比如第 1 行抽到 `program=心内科`。
- 依赖根 / 子类：按父列条件权重抽（[`sample_dependent_root`](../../pipeline/phase_2/engine/skeleton.py#L142)）。
- 温度列：在日期池里均匀抽日期（[`sample_temporal_root`](../../pipeline/phase_2/engine/skeleton.py#L273)）。

**这一幕结束时，每行的标签组合都定了，也就等于每行被分进了某个 cell。** 心内科那行同时抽到 `tier=三甲, residency=本地`，它就落进了 `(三甲,心内科,本地)` 这个抽屉。

### 🔢 第 3 幕 · Phase β：填测量值（给每个 cell 灌入分布）

[`measures.py::generate_measures`](../../pipeline/phase_2/engine/measures.py) 为每行算 measure。对随机 measure：

```
θ_row = intercept + Σ effects(本行的预测维度取值)        # 同 cell 的行 → 同 θ
值     = 从 family(θ) 这个分布里抽一个数 + N(0,σ) 噪声
```

`_compute_cell_params`（[statistical.py:210](../../pipeline/phase_2/validation/statistical.py#L210)）算的就是这个 θ。**关键洞察：同一个 cell 里所有行共享同一组 θ，所以它们是同一个分布的 iid 抽样**——这正是 KS 后面要检的东西。心内科那行：`μ = 6 + 2(心内科) = 8`，于是从 `N(8, 2²)` 抽出 `8.2`。

### 🎭 第 4 幕 · Phase γ / δ：加戏剧性与脏污

- **γ patterns**（[`patterns.py`](../../pipeline/phase_2/engine/patterns.py)）：按 `inject_pattern` 把某些行的值人为扭曲（季节异常、趋势断裂）。这些行后续会被 KS 排除（[statistical.py:307-317](../../pipeline/phase_2/validation/statistical.py#L307-L317)），免得「故意制造的异常」被当成分布不符。
- **δ realism**：本可注入 NaN/脏字符/截断——但**当前已全局禁用**（见 `AUDIT_2026-05-28.md §6`），所以这一幕现在是空转。

### 📦 第 5 幕 · τ_post：装订成册

[`postprocess.to_dataframe`](../../pipeline/phase_2/engine/postprocess.py) 把所有列拼成最终的 DataFrame —— 这就是你看到的总表。

### 🔍 尾声 · 验证：把总表「反向拆回」cell

最后 [`check_stochastic_ks`](../../pipeline/phase_2/validation/statistical.py#L270) 拿着第 1 幕的蓝图（`param_model`），把**已经生成好的总表**重新按笛卡尔积切回 48 个抽屉（[`_iter_predictor_cells`](../../pipeline/phase_2/validation/statistical.py#L116)），逐屉对比「实际值」和「蓝图声明的分布」。**抽屉里行数 <30 的就跳过**——于是绕了一圈，又回到了 n<30。

---

## 4. 一句话串起来

Phase 1 写剧本（target_rows + 实体）→ Loop A 画蓝图（决定有几个 cell）→ α 给每行贴标签（把行分进 cell）→ β 按 cell 的 θ 灌入分布值 → γ/δ 加戏与脏污 → τ_post 装订成总表 → 验证再把总表拆回 cell 逐屉检验。

**cell 不是 entity，而是「每个维度各取一个 level」的交叉抽屉；entity 是单个维度的单个 level，横跨许多抽屉。**

---

## 5. Cross-link

- `AUDIT_2026-05-28.md §3`：M3 的 n<30 真相（被 validator 跳过，非失败）
- `mechanisms/MECHANISM_3_DEEP_DIVE.md`：M3 KS 失败完整深挖
- `FAILURE_MECHANISMS.md`：所有 mechanism 总览
