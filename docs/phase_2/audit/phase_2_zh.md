## 阶段 2：智能体式数据模拟器（SDK 驱动）

> **核心贡献：** 用 **代码即 DGP（Code-as-DGP）** 取代脆弱的基于 JSON 的 DGP 规格定义。LLM 编写可执行的 Python 脚本来调用类型安全的 SDK。每个 measure 都通过一次调用声明为**闭式数据生成程序**，而不是通过增量式补丁逐步修补。所有列间依赖共同构成显式 DAG。一个按 DAG 顺序执行的引擎负责事件级行生成，三层验证器则确保结构、统计与模式层面的正确性，且全程无需额外的 LLM 调用。

---

### 2.1 `FactTableSimulator` SDK

该 SDK 将全部统计机制封装在一个最小化、强类型的 API 之后。LLM 在一组白名单安全操作内组装构件，同时完成：

1. **Schema 定义**：每次 `add_*()` 调用都会声明一列及其完整的生成规则。
2. **数据生成程序（Data Generation Program，DGP）**：以代码形式指定分布、依赖与模式。

#### 2.1.1 列声明（步骤 1）

**`add_category(name, values, weights, group, parent=None)`**：属于某个已命名维度组的分类列。

```python
# Root category
sim.add_category("hospital",
    values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
    weights=[0.25, 0.20, 0.20, 0.20, 0.15],
    group="entity")

# Child category: same weights for all parents (default, simplest)
sim.add_category("department",
    values=["Internal", "Surgery", "Pediatrics", "Emergency"],
    weights=[0.35, 0.25, 0.15, 0.25],
    group="entity", parent="hospital")
```

当与 `parent` 一起使用扁平列表时，同一组权重会应用于每个父值。若需更细粒度控制，可传入按父值划分的 dict，此时引擎会使用父值专属向量对 $P(\text{department} \mid \text{hospital})$ 进行采样：

```python
# Optional: per-parent conditional weights for realism
weights={"Xiehe": [0.30, 0.25, 0.15, 0.30], "Huashan": [0.35, 0.20, 0.20, 0.25], ...}
```

自动归一化；拒绝空值；验证 `parent` 是否存在于同一组中。

**`add_temporal(name, start, end, freq, derive=[])`**：带可选派生日历特征的时间列。

```python
sim.add_temporal("visit_date",
    start="2024-01-01", end="2024-06-30", freq="daily",
    derive=["day_of_week", "month"])
```

派生列（`day_of_week`、`month`、`quarter`、`is_weekend`）会被自动提取，并可作为 measure 的预测变量。

**`add_measure(name, family, param_model, scale=None)`**：**随机根 measure。** 从某个命名分布中采样。参数可随分类上下文变化，但该 measure **不**依赖任何其他 measure，因此它是 measure DAG 中的根节点。

```python
# Simple: constant parameters
sim.add_measure("temperature", family="gaussian",
    param_model={"mu": 36.5, "sigma": 0.8})

# Full: parameters vary by categorical predictors
sim.add_measure("wait_minutes", family="lognormal",
    param_model={
        "mu": {"intercept": 2.8, "effects": {
            "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
            "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                         "Tongren": 0.1, "Zhongshan": -0.1}
        }},
        "sigma": {"intercept": 0.35, "effects": {
            "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}
        }}
    })
```

**`add_measure_structural(name, formula, effects={}, noise={})`**：**结构型（派生） measure。** 通过公式基于其他 measure 和分类效应计算得出。在 measure DAG 中创建有向边。

```python
sim.add_measure_structural("cost",
    formula="wait_minutes * 12 + severity_surcharge",
    effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
    noise={"family": "gaussian", "sigma": 30})
```

公式通过名称引用先前声明的 measure 列和具名效应。每个符号都必须有显式的数值定义，不允许出现未定义项。

**两类 measure 的唯一关键区别：**

| | `add_measure`（随机型） | `add_measure_structural`（结构型） |
|---|---|---|
| **生成方式** | **从分布中随机采样** | **由公式 + 噪声确定性计算** |
| **可引用其他 measure 吗？** | **不能**，这是根节点 | **可以**，会创建 DAG 边 |
| **在 DAG 中的角色** | 根节点（没有传入的 measure 边） | 非根节点（依赖上游 measure） |
| **示例** | `wait_minutes ~ LogNormal(μ, σ)` | `cost = 12 × wait_minutes + surcharge + ε` |

两者都可以受到分类上下文影响。区别很简单：**如果某个值依赖于另一项 measure，它就是结构型；否则，它就是随机型。**

**支持的分布：** `"gaussian"`、`"lognormal"`、`"gamma"`、`"beta"`、`"uniform"`、`"poisson"`、`"exponential"`、`"mixture"`

#### 2.1.2 关系与模式声明（步骤 2）

**`declare_orthogonal(group_a, group_b, rationale)`**：声明两个维度组在统计上相互独立。该声明会传播到所有跨组列对。

```python
sim.declare_orthogonal("entity", "patient",
    rationale="Severity distribution is independent of hospital/department")
# Automatically implies: hospital ⊥ severity, department ⊥ severity, etc.
```

**`add_group_dependency(child_root, on, conditional_weights)`**：声明某个组的**根**列分布取决于其他组的**根**列。跨组依赖**只允许发生在组根列之间**，且根层依赖图必须是 DAG。

```python
sim.add_group_dependency("payment_method", on=["severity"],
    conditional_weights={
        "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
        "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
        "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10}
    })
```

> **仅限根节点约束：** 跨组依赖被限制在根列之间（无 `parent`）。这使依赖模型保持简洁，同时仍能覆盖真实场景（例如重症患者更偏好使用保险）。根层图必须无环。

**`inject_pattern(type, target, col, params)`**：植入由叙事驱动的统计异常。

```python
sim.inject_pattern("outlier_entity",
    target="hospital == 'Xiehe' & severity == 'Severe'",
    col="wait_minutes", params={"z_score": 3.0})
```

**模式类型：** `"outlier_entity"`、`"trend_break"`、`"ranking_reversal"`、`"dominance_shift"`、`"convergence"`、`"seasonal_anomaly"`

**`set_realism(missing_rate, dirty_rate, censoring)`**：**可选。** 模拟数据缺陷。

---

### 2.2 维度组与跨组关系

**维度组**是核心结构抽象。每个分类列恰好属于一个已命名组。组内列通过 `parent` 形成层级；组间列则通过 `declare_orthogonal()`（独立）或 `add_group_dependency()`（依赖）建立关系。

```
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
Group "time":     visit_date → [day_of_week, month]  (derived)
```

**组内层级：** 每个组都有一个**根**列（无 `parent`）。子列基于其父列进行条件采样：$P(\text{department} \mid \text{hospital})$ 使用按父值划分的权重向量。

**时间列作为维度组：** 时间列是一类特殊的维度组。根节点是声明的时间列；派生的日历层级会通过 `derive` 自动提取，并可作为预测变量使用。

**跨组正交性：** 独立性是针对**整个组**声明的，而不是单个列。如果 Group A ⊥ Group B，则所有跨组列对都会自动独立，无需逐一枚举。

**跨组依赖：** 跨组独立性是**显式声明才生效，而非默认成立**。当两个组未被声明为正交时，可通过 `add_group_dependency()` 指定它们在根层的关系。根层依赖图必须是 DAG。

**`declare_orthogonal()` 带来的能力：**

1. **生成：** 通过独立采样实现 $P(A,B) \approx P(A) \cdot P(B)$。
2. **验证（L1）：** 对根层跨组列对执行卡方检验。
3. **视图提取（Phase 3）：** “Orthogonal Contrast” 仪表板，可按两个独立维度切分同一指标。

> **设计原则：** 维度组将分类、时间与跨组语义统一到同一抽象之中。正交性传播消除了 $O(n^2)$ 的成对声明需求。根层 DAG 约束则在保持依赖模型简洁的同时，避免逻辑矛盾。

---

### 2.3 闭式 measure 声明

每个 measure 都只会被声明一次，并且声明内容就是完整的数据生成程序。

#### 随机根 measure

从参数受分类上下文影响的分布中随机采样。具体示例如下：

$$\text{wait\_minutes} \mid \text{severity}, \text{hospital} \;\sim\; \text{LogNormal}(\mu,\; \sigma)$$

其中每个参数都由**截距 + 效应求和**构成：

$$\mu = \underbrace{2.8}_{\text{intercept}} + \underbrace{0.9}_{\text{severity=Severe}} + \underbrace{0.2}_{\text{hospital=Xiehe}} = 3.9, \quad \sigma = 0.35 + 0.10 = 0.45$$

一般形式为：$Y \mid X_1, \ldots, X_k \sim \mathcal{D}(\theta_1, \theta_2, \ldots)$，其中 $\theta_j = \beta_0 + \sum_m \beta_m(X_m)$。

#### 结构型（派生） measure

基于其他 measure、分类效应与噪声进行确定性计算。具体示例如下：

$$\text{cost} = \underbrace{12 \times \text{wait\_minutes}}_{\text{formula on measures}} + \underbrace{\text{surcharge}(\text{severity})}_{\text{categorical effect}} + \underbrace{\epsilon}_{\text{noise} \sim \mathcal{N}(0, 30^2)}$$

#### measure 间关系如何生效

measure 之间的关系通过两种机制表达，无需单独的相关性 API：

1. **结构依赖：** 结构型 measure 在其公式中直接引用另一项 measure（例如 `cost = f(wait_minutes)`），从而在 measure DAG 中创建一条有向边。这会自然地产生相关性。
2. **共享预测变量：** 两个随机型 measure 如果依赖相同的分类预测变量（例如都随 `severity` 变化），就会因共享条件变量而在边际上相关，尽管在给定这些预测变量时它们条件独立。

#### Measure DAG 约束

所有 measure 依赖必须构成**有向无环图（DAG）**。结构型 measure 只能引用在其之前声明的 measure。引擎通过拓扑排序确定生成顺序。

> **为何采用闭式声明？** 在此前的设计中，一个 measure 的最终 DGP 需要通过串联 `add_measure()` → `add_conditional()` → `add_dependency()` → `add_correlation()` 得到。声明的分布与实际生成的分布可能会在连续覆盖后发生偏离。闭式声明确保每个 measure 的统计语义自包含、可验证，并与验证逻辑保持一致。

---

### 2.4 按 DAG 排序的事件级行生成

> 本节描述**核心生成机制**，即主表（Master Table）的每一行是如何生成的。

**`target_rows`** 继承自 Phase 1 的场景上下文，它会根据领域复杂度层级、时间跨度和实体数量确定该值（见 §1.2）：

| 复杂度层级 | 典型 `target_rows` | 理由 |
|----------------|----------------------|-----------|
| 简单 | 200–500 | 实体较少，`metric` 仅 1–2 个，时间跨度较短 |
| 中等 | 500–1000 | 存在多种实体类型，`metric` 为 2–3 个 |
| 复杂 | 1000–3000 | 存在嵌套层级，且有 3 个以上相互依赖的 `metric` |

引擎**不会**将完整的分类笛卡尔积实例化。每一行都作为一个**独立的原子事件**生成。

#### 完整生成 DAG

所有列，包括分类列、时间列和 measure 列，共同构成一个 DAG。引擎按拓扑顺序生成各列：

```
Topological Generation Order:

Layer 0 — Independent roots:
  hospital, severity, visit_date

Layer 1 — Dependent non-measure columns:
  payment_method       ← P(payment | severity)          [cross-group root dep]
  department           ← P(dept | hospital)              [within-group hierarchy]
  day_of_week, month   ← derived from visit_date         [temporal derivation]

Layer 2 — Stochastic root measures:
  wait_minutes         ← severity, hospital
                         ~ LogNormal(μ(severity, hospital), σ(severity))

Layer 3 — Structural measures:
  cost                 ← wait_minutes, severity
                         = wait_minutes × 12 + surcharge(severity) + ε
  satisfaction         ← wait_minutes, severity
                         = 9 − 0.04 × wait_minutes + adj(severity) + ε
```

#### 行生成算法

对 `target_rows` 中的每一行：

```
Step 1: Generate all non-measure columns (topological order)
  1. hospital_i       ~ Cat([0.25, 0.20, ...])                 // independent root
  2. severity_i       ~ Cat([0.50, 0.35, 0.15])                // independent root
  3. visit_date_i     ~ Uniform(2024-01-01, 2024-06-30)        // independent root
  4. payment_method_i ~ Cat(weights[severity_i])                // root dep ← severity
  5. department_i     ~ Cat(weights | hospital_i)                // child ← hospital
  6. day_of_week_i    = DOW(visit_date_i)                       // temporal derived
  7. month_i          = MONTH(visit_date_i)                     // temporal derived

Step 2: Generate measures (topological order of measure DAG)
  8. wait_minutes_i   ~ LogNormal(μ(severity_i, hospital_i),
                                   σ(severity_i))              // stochastic root
  9. cost_i           = wait_minutes_i × 12
                        + surcharge(severity_i) + ε₁           // structural
 10. satisfaction_i   = 9 − 0.04 × wait_minutes_i
                        + adj(severity_i) + ε₂                 // structural

Step 3: Post-generation adjustments (applied to full DataFrame)
 11. Pattern injection (outliers, trend breaks, etc.)
 12. Realism injection (optional)
```

> **为什么采用事件级生成？** 将行作为原子事件生成（而不是实例化一个笛卡尔积数据立方体再重复采样），能够产生更真实的单元占用分布，也符合“每一行代表一个不可再分事件”这一硬性约束。

---

### 2.5 LLM 代码生成提示词

````text
SYSTEM:
You are an expert Data Scientist Agent. Build an Atomic-Grain Fact Table
using the `FactTableSimulator` Python SDK.

INPUT:
1. Scenario Context: real-world setting with entities, metrics, temporal grain,
   and target_rows (from Phase 1).
2. SDK Reference: you may ONLY use the methods listed below.

AVAILABLE SDK METHODS (declare columns FIRST, then relationships):
  # --- Step 1: Column declarations ---
  sim.add_category(name, values, weights, group, parent=None)
      # weights: list (root/global) or dict-of-lists (per-parent conditional)
  sim.add_temporal(name, start, end, freq, derive=[])
  sim.add_measure(name, family, param_model, scale=None)
      # Stochastic ROOT measure: param_model uses {intercept, effects}
      # Does NOT depend on any other measure
  sim.add_measure_structural(name, formula, effects={}, noise={})
      # Structural DERIVED measure: formula references other measures
      # Creates edges in the measure DAG

  # --- Step 2: Relationships & patterns ---
  sim.declare_orthogonal(group_a, group_b, rationale)
  sim.add_group_dependency(child_root, on, conditional_weights)
      # Cross-group dependency between ROOT columns only; must be DAG
  sim.inject_pattern(type, target, col, params)
  sim.set_realism(missing_rate, dirty_rate, censoring=None)    # optional

SUPPORTED DISTRIBUTIONS: "gaussian", "lognormal", "gamma", "beta", "uniform",
                         "poisson", "exponential", "mixture"

PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",
               "dominance_shift", "convergence", "seasonal_anomaly"

HARD CONSTRAINTS — the script MUST satisfy ALL:
1. ATOMIC_GRAIN: each row = one indivisible event.
2. At least 2 dimension groups, each with ≥1 categorical column, plus ≥2 measures.
3. All column declarations (Step 1) BEFORE any relationship declarations (Step 2).
4. At least 1 declare_orthogonal() between genuinely independent groups.
5. At least 1 add_measure_structural() creating inter-measure dependency,
   and at least 2 inject_pattern() calls.
6. Output must be pure, valid Python returning sim.generate().
7. All measure dependencies must be acyclic (DAG). No circular or
   self-referential dependency is allowed.
8. Cross-group dependencies only between group ROOT columns; root DAG must be acyclic.
9. Every symbolic effect in param_model or formula must have an explicit
   numeric definition. No undefined symbols.

SOFT GUIDELINES — include when naturally fitting the domain:
- Temporal dimension with derive (if data has a time component).
- Within-group hierarchy via parent with per-parent conditional weights.
- 3+ measures (enables richer chart coverage).
- add_group_dependency() when groups are not genuinely independent.
- set_realism() for data imperfections (missing values, dirty entries).

=== ONE-SHOT EXAMPLE ===
[SCENARIO]
Title: 2024 Shanghai Emergency Records
target_rows: 500
Entities: [Xiehe, Huashan, Ruijin, Tongren, Zhongshan]
Metrics: wait_minutes (min), cost (CNY), satisfaction (1-10)
Temporal: daily, 2024-01 to 2024-06

[AGENT CODE]
```python
from chartagent.synth import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=500, seed=seed)

    # ========== Step 1: Declare all columns ==========

    # Dimension group "entity": hospital → department
    sim.add_category("hospital",
        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
        weights=[0.25, 0.20, 0.20, 0.20, 0.15],
        group="entity")

    sim.add_category("department",
        values=["Internal", "Surgery", "Pediatrics", "Emergency"],
        weights=[0.35, 0.25, 0.15, 0.25],
        group="entity", parent="hospital")

    # Dimension group "patient": severity
    sim.add_category("severity",
        values=["Mild", "Moderate", "Severe"],
        weights=[0.50, 0.35, 0.15],
        group="patient")

    # Dimension group "payment": payment_method
    sim.add_category("payment_method",
        values=["Insurance", "Self-pay", "Government"],
        weights=[0.60, 0.30, 0.10],
        group="payment")

    # Temporal dimension with derived calendar levels
    sim.add_temporal("visit_date",
        start="2024-01-01", end="2024-06-30", freq="daily",
        derive=["day_of_week", "month"])

    # Stochastic root measure: wait_minutes varies by severity and hospital
    sim.add_measure("wait_minutes",
        family="lognormal",
        param_model={
            "mu": {
                "intercept": 2.8,
                "effects": {
                    "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},
                    "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,
                                 "Tongren": 0.1, "Zhongshan": -0.1}
                }
            },
            "sigma": {
                "intercept": 0.35,
                "effects": {
                    "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}
                }
            }
        })

    # Structural measure: cost ← wait_minutes, severity
    sim.add_measure_structural("cost",
        formula="wait_minutes * 12 + severity_surcharge",
        effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
        noise={"family": "gaussian", "sigma": 30})

    # Structural measure: satisfaction ← wait_minutes, severity
    sim.add_measure_structural("satisfaction",
        formula="9 - 0.04 * wait_minutes + severity_adj",
        effects={"severity_adj": {"Mild": 0.5, "Moderate": 0.0, "Severe": -1.5}},
        noise={"family": "gaussian", "sigma": 0.6})

    # ========== Step 2: Relationships & patterns ==========

    # Group-level orthogonal declaration
    sim.declare_orthogonal("entity", "patient",
        rationale="Severity distribution is independent of hospital/department")

    # Cross-group dependency: payment root depends on patient root
    sim.add_group_dependency("payment_method", on=["severity"],
        conditional_weights={
            "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
            "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
            "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10}
        })

    # Pattern injection
    sim.inject_pattern("outlier_entity",
        target="hospital == 'Xiehe' & severity == 'Severe'",
        col="wait_minutes", params={"z_score": 3.0})

    sim.inject_pattern("trend_break",
        target="hospital == 'Huashan'",
        col="wait_minutes",
        params={"break_point": "2024-03-15", "magnitude": 0.4})

    return sim.generate()
```

=== YOUR TASK ===
[SCENARIO]
{scenario_context}

[AGENT CODE]
````

---

### 2.6 Schema 元数据输出

该 SDK 会同时返回主 DataFrame（Master DataFrame）和结构化的 **Schema Metadata**。它是 Phase 2 与 Phase 3 之间的契约：

```python
schema_metadata = {
    "dimension_groups": {
        "entity":  {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]},
        "patient": {"columns": ["severity"], "hierarchy": ["severity"]},
        "payment": {"columns": ["payment_method"], "hierarchy": ["payment_method"]},
        "time":    {"columns": ["visit_date", "day_of_week", "month"], "hierarchy": ["visit_date"]}
    },
    "orthogonal_groups": [
        {"group_a": "entity", "group_b": "patient",
         "rationale": "severity is independent of hospital/department"}
    ],
    "group_dependencies": [
        {"child_root": "payment_method", "on": ["severity"]}
    ],
    "columns": [
        {"name": "hospital",       "group": "entity",  "parent": null,       "type": "categorical", "cardinality": 5},
        {"name": "department",     "group": "entity",  "parent": "hospital", "type": "categorical", "cardinality": 4},
        {"name": "severity",       "group": "patient", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "payment_method", "group": "payment", "parent": null,       "type": "categorical", "cardinality": 3},
        {"name": "visit_date",     "group": "time",    "type": "temporal",  "derived": ["day_of_week", "month"]},
        {"name": "wait_minutes",   "type": "measure",  "measure_type": "stochastic", "family": "lognormal"},
        {"name": "cost",           "type": "measure",  "measure_type": "structural", "depends_on": ["wait_minutes"]},
        {"name": "satisfaction",   "type": "measure",  "measure_type": "structural", "depends_on": ["wait_minutes"]}
    ],
    "measure_dag_order": ["wait_minutes", "cost", "satisfaction"],
    "patterns": [
        {"type": "outlier_entity", "target": "hospital=='Xiehe' & severity=='Severe'",
         "col": "wait_minutes"},
        {"type": "trend_break", "target": "hospital=='Huashan'",
         "col": "wait_minutes", "break_point": "2024-03-15"}
    ],
    "total_rows": 500
}
```

> 视图提取利用维度组和正交声明来枚举合法的图表映射；QA 生成利用模式和 measure DAG 来构造高难度问题；依赖图则支持因果推理类 QA。

---

### 2.7 执行错误反馈循环

LLM 脚本中的任何数学或结构错误，都会触发 SDK 抛出带有信息的 `Exception`，从而实现**原生代码级自纠正**：

```
1. LLM outputs Python script.
2. Sandbox executes build_fact_table().
3. SUCCESS → proceed to Deterministic Engine (§2.8) + Validation (§2.9).
4. FAILURE → SDK raises typed exception, e.g.:
   "CyclicDependencyError: Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."
   "UndefinedEffectError: 'severity_surcharge' in formula has no definition for 'Severe'."
   "NonRootDependencyError: 'department' is not a group root; cannot use in add_group_dependency."
5. Code + traceback fed back to LLM: "Adjust parameters to resolve the error."
6. Retry (max_retries=3). If all fail → log and skip.
```

> 与只能捕捉*语法*错误的 JSON 配置校验不同，代码执行能够捕捉*语义*上不可能成立的情况，例如循环依赖、不完整的效应表、非根节点的跨组依赖和退化分布。LLM 会收到精确的约束违例信息，以进行定向修复。

---

### 2.8 确定性引擎执行

`FactTableSimulator.generate()` 运行的是一条**完全确定、按 DAG 顺序执行的管线**，会把声明转换为主 DataFrame。给定相同的 `seed`，输出可做到逐位复现。**无需 LLM 调用。**

```python
class FactTableSimulator:
    def generate(self) -> Tuple[pd.DataFrame, dict]:
        rng = np.random.default_rng(self.seed)

        # Pre-flight: build and validate full generation DAG
        full_dag = self._build_full_dag()      # all columns in one DAG
        topo_order = topological_sort(full_dag)

        # α — Non-measure columns: sample roots, drill down, derive temporal
        #     All in topological order of the full DAG
        rows = self._build_skeleton(topo_order, rng)

        # β — Measures: generate in topological order of measure sub-DAG
        for col in topo_order:
            if self._is_stochastic(col):
                rows[col] = self._sample_stochastic(col, rows, rng)
            elif self._is_structural(col):
                rows[col] = self._eval_structural(col, rows, rng)

        # γ — Pattern Injection: outlier scaling, trend breaks, etc.
        rows = self._inject_patterns(rows, rng)

        # δ — Realism (optional): missing data, dirty values, censoring
        if self._has_realism:
            rows = self._inject_realism(rows, rng)

        return self._post_process(rows), self._build_schema_metadata()
```

**管线组成：**

$$M = \tau_{\text{post}} \circ \delta^{?} \circ \gamma \circ \beta \circ \alpha(\text{seed})$$

> 每一步都是 `(declarations, seed)` 的确定性函数。LLM 的贡献在写出 SDK 脚本时就结束了，从 `generate()` 开始的部分全部是纯计算。$\delta$ 上的上标 $?$ 表示 realism 注入是可选的。

---

### 2.9 三层验证

在引擎生成主表（§2.8）之后，确定性验证器会在三个层面检查正确性。**无需 LLM 调用**，失败项会通过调整参数并重新执行来自动修复。

#### L1：结构验证

```python
class SchemaAwareValidator:
    def _L1_structural(self, df, meta):
        checks = []

        # Row count within 10% of target
        target = meta["total_rows"]
        checks.append(Check("row_count",
            passed=abs(len(df) - target) / target < 0.1))

        # Categorical cardinality matches declaration
        for col in meta["columns"]:
            if col["type"] == "categorical":
                actual = df[col["name"]].nunique()
                checks.append(Check(f"cardinality_{col['name']}",
                    passed=actual == col["cardinality"]))

        # Categorical root marginal weights match declaration
        for col in meta["columns"]:
            if col["type"] == "categorical" and col.get("parent") is None:
                observed = df[col["name"]].value_counts(normalize=True)
                max_dev = max(abs(observed[v] - w)
                    for v, w in zip(col["values"], col["weights"]))
                checks.append(Check(f"marginal_{col['name']}",
                    passed=max_dev < 0.10))

        # Measure columns: finite and non-null
        for col in meta["columns"]:
            if col["type"] == "measure":
                checks.append(Check(f"finite_{col['name']}",
                    passed=df[col["name"]].notna().all()
                           and np.isfinite(df[col["name"]]).all()))

        # Orthogonal group independence (chi-squared on root pairs)
        for pair in meta["orthogonal_groups"]:
            ga = meta["dimension_groups"][pair["group_a"]]
            gb = meta["dimension_groups"][pair["group_b"]]
            root_a, root_b = ga["hierarchy"][0], gb["hierarchy"][0]
            ct = pd.crosstab(df[root_a], df[root_b])
            _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
            checks.append(Check(f"orthogonal_{root_a}_{root_b}",
                passed=p_val > 0.05,
                detail=f"χ² p={p_val:.4f} (>0.05 = independent)"))

        # Measure DAG acyclicity (pre-validated, but double-check)
        checks.append(Check("measure_dag_acyclic",
            passed=is_acyclic(meta.get("measure_dag_order", []))))

        return checks
```

#### L2：统计验证

验证逻辑与 **measure 的声明类型保持一致**。随机型 measure 会在声明的预测变量层级上，对其条件分布进行检验；结构型 measure 则会对其公式残差进行检验。

```python
    def _L2_statistical(self, df, meta):
        checks = []

        # Stochastic measures: conditional distribution test
        for col in meta["columns"]:
            if col.get("measure_type") == "stochastic":
                spec = self._get_measure_spec(col["name"])
                for group_filter, expected_params in spec.iter_predictor_cells():
                    subset = df.query(group_filter) if group_filter else df
                    _, p_val = scipy.stats.kstest(
                        subset[col["name"]], col["family"], args=expected_params)
                    checks.append(Check(f"ks_{col['name']}_{group_filter or 'marginal'}",
                        passed=p_val > 0.05))

        # Structural measures: residual check
        for col in meta["columns"]:
            if col.get("measure_type") == "structural":
                predicted = eval_formula(col["formula"], df)
                residuals = df[col["name"]] - predicted
                checks.append(Check(f"structural_{col['name']}_residual_mean",
                    passed=abs(residuals.mean()) < residuals.std() * 0.1))
                checks.append(Check(f"structural_{col['name']}_residual_std",
                    passed=abs(residuals.std() - col["noise_sigma"]) / col["noise_sigma"] < 0.2))

        # Group dependency: conditional transition vs declared weights
        for dep in meta.get("group_dependencies", []):
            observed = pd.crosstab(df[dep["on"][0]], df[dep["child_root"]], normalize="index")
            max_dev = self._max_conditional_deviation(observed, dep["conditional_weights"])
            checks.append(Check(f"group_dep_{dep['child_root']}",
                passed=max_dev < 0.10,
                detail=f"max deviation from declared transition: {max_dev:.3f}"))

        return checks
```

#### L3：模式验证

```python
    def _L3_pattern(self, df, meta):
        checks = []
        for p in meta["patterns"]:
            if p["type"] == "outlier_entity":
                z = abs(df.query(p["target"])[p["col"]].mean()
                        - df[p["col"]].mean()) / df[p["col"]].std()
                checks.append(Check(f"outlier_{p['col']}", passed=z >= 2.0))

            elif p["type"] == "ranking_reversal":
                m1, m2 = p["metrics"]
                root = meta["dimension_groups"][
                    list(meta["dimension_groups"].keys())[0]]["hierarchy"][0]
                means = df.groupby(root)[[m1, m2]].mean()
                checks.append(Check(f"reversal_{m1}_{m2}",
                    passed=means[m1].rank().corr(means[m2].rank()) < 0))

            elif p["type"] == "trend_break":
                bp = pd.to_datetime(p["break_point"])
                tc = [c["name"] for c in meta["columns"]
                      if c["type"] == "temporal"][0]
                before = df[df[tc] < bp][p["col"]].mean()
                after = df[df[tc] >= bp][p["col"]].mean()
                checks.append(Check(f"trend_{p['col']}",
                    passed=abs(after - before) / before > 0.15))

            elif p["type"] == "dominance_shift":
                checks.append(Check("dominance",
                    passed=self._verify_dominance_change(df, p, meta)))

        return checks
```

#### 自动修复循环（不重新调用 LLM）

```python
AUTO_FIX = {
    "ks_*":         lambda c: widen_variance(c, factor=1.2),
    "outlier_*":    lambda c: amplify_magnitude(c, factor=1.3),
    "trend_*":      lambda c: amplify_magnitude(c, factor=1.3),
    "orthogonal_*": lambda c: reshuffle_pair(c),
}

def generate_with_validation(build_fn, meta, max_retries=3):
    for attempt in range(max_retries):
        df = build_fn(seed=42 + attempt)
        report = SchemaAwareValidator().validate(df, meta)
        if report.all_passed:
            return df, report
        for check in report.failures:
            strategy = match_strategy(check.name, AUTO_FIX)
            if strategy:
                strategy(check)
    return df, report  # soft failure after max retries
```

> 三层验证的运行时间仅为毫秒级。验证与声明层级相对齐：随机型 measure 对照其条件分布进行检验，结构型 measure 同时对残差均值和方差进行检验，分类根列则对照声明的边际权重进行检验。

---

### 2.10 设计优势

采用原子粒度事实表、维度组和闭式 measure 后，下游可获得最大的灵活性：

- **分布图**（histogram、box、violin）可直接使用原始行。
- **聚合图**（bar、pie、line）可在层级根节点上执行 `GROUP BY`。
- **下钻图**（grouped/stacked bar、treemap）可利用带按父值条件的组内层级。
- **关系图**（scatter、bubble）可利用行级结构依赖。
- **多视图仪表板**可沿正交组对同一张主表进行切分。
- **因果推理 QA** 可利用显式的 measure DAG。

$$\text{View}_{\text{chart}} = \sigma_{\text{filter}} \circ \gamma_{\text{agg}} \circ \pi_{\text{cols}}(M)$$

其中 $\sigma$ = 行选择，$\gamma$ = group-by 聚合，$\pi$ = 列投影。
