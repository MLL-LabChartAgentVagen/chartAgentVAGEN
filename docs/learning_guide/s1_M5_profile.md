# M5: Validation Engine — 模块画像

## 一句话职责

验证生成的 Master DataFrame 是否在结构、统计、模式三个层级上忠实于其声明，并在检查失败时通过参数调整自动修复（无需 LLM 调用）。

## 实现状态：13 / 21（62%）

在 13 项 SPEC_READY 中：
- **5 项完整实现：** row count、cardinality、orthogonal independence、DAG acyclicity、outlier entity
- **1 项实现（含防御增强）：** trend break
- **3 项 NotImplementedError stub：** L2 全部（KS test、structural residuals、group dep transitions）
- **2 项代码完全缺失：** marginal weights、measure finiteness
- **1 项代码缺失：** ranking reversal（规范有伪代码但未实现）
- **1 项部分实现：** Loop B（三个策略函数完成，循环框架缺失）

## 在流水线中的位置

```
M2 (Master DataFrame) ──┐
                         ├──► M5: Validation Engine ──► Phase 3
M4 (schema_metadata) ────┘         │
                                   │ Loop B (max 3, no LLM)
                                   ▼
                                  M2 (re-run with seed offset + overrides)
```

- **上游：** M2（提供 Master DataFrame）、M4（提供 `schema_metadata` dict）
- **下游：** Phase 3（接收验证后的 `(DataFrame, schema_metadata, ValidationReport)` 三元组）
- **反馈：** Loop B — 验证失败时调整参数并重新执行 M2 的 `generate()`，最多 3 次

## 构建顺序中的位置

第 **5** 步，前置依赖：`types.py`（Check / ValidationReport 类型）、M1（声明验证逻辑参考）、M4（metadata 契约）、M2（DataFrame 生成）

```
types.py + exceptions.py → M1(SDK) → M4(Metadata) → M2(Engine) → ★ M5(Validation) → M3(Orchestration)
```

---

## 已实现功能详解（SPEC_READY）

### L1 层：结构验证（Structural Checks）

如果 M5 是一位质检员，L1 就是 TA 的**目视检查**——不打开箱子看内容，只核对数量、标签和外包装是否与装箱单一致。

---

#### 1. Row Count Check — 行数偏差检查

- **规范定义（§2.9 L1）：** `abs(len(df) - target) / target < 0.1`，即实际行数与 `target_rows` 的相对偏差不超过 10%。
- **代码实现：**
  📍 `phase_2/validation/structural.py:22-48` — `check_row_count(df, meta)`

  从 `meta["total_rows"]` 取目标值，计算 `deviation = abs(actual - target) / target`，返回 `Check(name="row_count", passed=deviation < 0.1, detail=...)`。detail 字符串包含实际行数、目标行数和偏差值，方便调试。

- **生动类比：** 工厂订单要求 1000 件，交付了 950 件（偏差 5%）是可以接受的；交付了 800 件（偏差 20%）则不合格。
- 💡 **为什么这样设计？** 10% 是软容忍度而非精确匹配——因为模式注入（stage γ）或去重操作可能微调行数。绝对精确要求会导致几乎所有随机生成都失败。

---

#### 2. Categorical Cardinality Check — 分类基数检查

- **规范定义（§2.9 L1）：** 每个分类列的 `nunique()` 必须严格等于声明的 `cardinality`。
- **代码实现：**
  📍 `phase_2/validation/structural.py:51-110` — `check_categorical_cardinality(df, meta)`

  遍历 `meta["columns"]`（兼容 dict 和 list 两种格式，L75-78），过滤 `type == "categorical"` 的列。对每列：
  - 优先从 `col["cardinality"]` 取声明基数
  - 若缺失则回退到 `len(col["values"])`（L92-94）
  - 检查 `df[col_name].nunique() == declared`
  - 返回 `Check(name=f"cardinality_{col_name}", ...)`

- **生动类比：** 声明了 5 种医院类型，生成数据中只出现了 4 种（某个稀有类型从未被抽样到），这不合格。
- 💡 **为什么这样设计？** 这里用精确匹配（不像 row count 的 10% 容忍），因为类别缺失意味着该类别的所有下游统计都缺失——这是结构性错误，不是采样波动。

---

#### 3. Root Marginal Weight Check — 根列边际权重检查 ⚠️ 代码缺失

- **规范定义（§2.9 L1）：** 对每个根分类列（无 parent），观测频率与声明权重的每个值最大绝对偏差 < 0.10。
- **代码状态：** `structural.py` 中 **不存在** `check_marginal_weights` 函数。`validator.py` 的 `_run_l1()` 也未调用它。Stage4 规划了此函数（需要 enriched metadata 中的 `values` 和 `weights` 字段），但尚未编写。
- **备注：** 规范逻辑本身是 SPEC_READY 的（检查公式清晰），但实现依赖 M4 P0 enrichment 的完成。

---

#### 4. Measure Finiteness Check — 度量有限性检查 ⚠️ 代码缺失

- **规范定义（§2.9 L1）：** 每个度量列必须满足 `notna().all()` 且 `isfinite().all()`。
- **代码状态：** `structural.py` 中 **不存在** `check_measure_finiteness` 函数。`validator.py` 的 `_run_l1()` 也未调用它。
- **备注：** 逻辑极为简单（两个 pandas 内置方法），缺失可能是因为与 realism 注入的交互未解决（`missing_rate` 会注入 NaN，与 `notna()` 冲突）。

---

#### 5. Orthogonal Independence — 正交独立性检查（χ² 检验）

- **规范定义（§2.9 L1）：** 对每对声明的正交组，取其根列构建列联表，运行 `chi2_contingency`，通过条件为 `p_val > 0.05`（即不能拒绝独立性假设）。
- **代码实现：**
  📍 `phase_2/validation/structural.py:113-177` — `check_orthogonal_independence(df, meta)`

  遍历 `meta["orthogonal_groups"]`，通过 `meta["dimension_groups"]` 找到每对正交组的根列（取 `hierarchy[0]`）。然后：
  - `pd.crosstab(df[root_a], df[root_b])` 构建列联表（L146）
  - 退化检查：若列联表 < 2×2 则直接 fail（L148-156）
  - 调用 `scipy.stats.chi2_contingency(ct)`，捕获可能的 `ValueError`（L159-166）
  - 判断 `p_val > 0.05`（L169）

- **生动类比：** 声明了"地区和严重程度互不影响"，那么在生成数据中，不同地区的严重程度分布应该大致相同——如果"东区"的严重患者异常集中，χ² 检验会报警。
- 💡 **为什么这样设计？** 注意方向：**高 p 值是通过**。我们期望的是"数据无法证明两个变量相关"，而非"数据证明了独立性"。这是频率论假设检验的标准逻辑。代码增加了退化列联表和异常捕获的防御处理——规范未提及但属于工程上的必要保护。

---

#### 6. Measure DAG Acyclicity — 度量 DAG 无环性冗余检查

- **规范定义（§2.9 L1）：** 冗余验证 `measure_dag_order` 无环。这应该在 M1 声明时就已保证，此处是防御性深度检查。
- **代码实现：**
  📍 `phase_2/validation/structural.py:180-209` — `check_measure_dag_acyclic(meta)`

  取 `meta["measure_dag_order"]`（一个 list），比较 `len(set(order))` 与 `len(order)` 来检测重复节点。重复节点意味着拓扑序列中有环（因为同一节点不应出现两次）。

- **生动类比：** 就像银行在 ATM 已经验过密码后，柜台还要求再验一次身份——不是不信任 ATM，而是多一层保险。
- 💡 **为什么这样设计？** 实现用了**重复检测**而非真正的图遍历无环验证——这是合理的简化，因为拓扑排序的输出天然不含重复（如果有重复说明排序算法有 bug），此处本就是防御性冗余。

---

### L2 层：统计验证（Statistical Checks）

L2 是 M5 的**化验环节**——打开箱子抽样检测内容物是否符合配方。

---

#### 7. Stochastic Measure KS Test — 随机度量 KS 检验 ⛔ stub

- **规范定义（§2.9 L2）：** 对每个随机度量（stochastic measure），枚举其效应（effects）中所有预测器的笛卡尔积单元格，在每个单元格内过滤数据行，重构期望分布参数（`intercept + Σ effects`），运行 `scipy.stats.kstest`，通过条件为 `p_val > 0.05`。
- **代码状态：**
  📍 `phase_2/validation/statistical.py:55-69` — `check_stochastic_ks(df, col_name, meta)`

  函数签名已定义（三参数：`df`, `col_name`, `meta`），但函数体直接 `raise NotImplementedError("BLOCKED pending Blockers 2 & 3")`。

- **阻塞原因：** 依赖 M2 的度量生成逻辑完成（Blocker 2: formula evaluator, Blocker 3: auto-fix mutation semantics），以及 M4 enriched metadata 中的完整 `param_model`。

---

#### 8. Structural Measure Residual Check — 结构度量残差检查 ⛔ stub

- **规范定义（§2.9 L2）：** 对每个结构度量，用声明的 formula 重新计算预测值，求残差。两项子检查：(a) `abs(residuals.mean()) < residuals.std() * 0.1`（残差均值近零）；(b) `abs(residuals.std() - noise_sigma) / noise_sigma < 0.2`（残差标准差与声明噪声一致）。
- **代码状态：**
  📍 `phase_2/validation/statistical.py:72-86` — `check_structural_residuals(df, col_name, meta)`

  函数签名已定义，函数体直接 `raise NotImplementedError("BLOCKED")`。

---

#### 9. Group Dependency Conditional Transition — 组依赖条件转移检查 ⛔ stub

- **规范定义（§2.9 L2）：** 对每个声明的 `group_dependency`，交叉表归一化后与声明的 `conditional_weights` 比较，最大绝对偏差 < 0.10。
- **代码状态：**
  📍 `phase_2/validation/statistical.py:89-102` — `check_group_dependency_transitions(df, meta)`

  函数签名已定义，函数体直接 `raise NotImplementedError("BLOCKED pending Blocker 5")`。

- **已就绪的辅助函数：**
  📍 `phase_2/validation/statistical.py:21-52` — `max_conditional_deviation(observed, declared)`

  这是为此检查准备的纯计算工具——遍历两个嵌套 dict 的所有父键×子键组合，返回最大绝对偏差。函数本身完整实现，但调用方（`check_group_dependency_transitions`）仍是 stub。

---

### L3 层：模式验证（Pattern Checks）

L3 是 M5 的**专项抽查**——不看整体分布，专门检查注入的异常模式是否在数据中真的可被探测到。

---

#### 10. Outlier Entity Validation — 异常实体验证

- **规范定义（§2.9 L3）：** 目标子集均值的 z-score ≥ 2.0（注意：注入时 z-score 为 3.0，验证阈值故意放松）。
- **代码实现：**
  📍 `phase_2/validation/pattern_checks.py:23-69` — `check_outlier_entity(df, pattern)`

  执行流程：
  1. 从 `pattern` 解构 `target`（过滤表达式）、`col`（目标列）、`params["z_score"]`（声明值，仅读取但未用于判断）（L38-40）
  2. `df.eval(target_expr)` 定位目标行（L42）
  3. 零行匹配 → 直接 fail（L45-50）
  4. 计算全局 `mean` 和 `std`；若 `std == 0` 或 `NaN` → fail（L52-59）
  5. `z = abs(subset_mean - global_mean) / global_std`（L63）
  6. 判断 `z >= 2.0`（L64）

- **生动类比：** 声明了"协和医院的等待时间异常高"，那就统计协和医院的平均等待时间，看它是否至少偏离总体均值 2 个标准差——如果只偏离 1.5 个标准差，说明模式注入力度不够。
- 💡 **为什么这样设计？** 验证阈值（2.0）低于注入阈值（3.0），留出采样波动的余量。代码读取了 `params["z_score"]` 但硬编码用 2.0 判断——这遵循了规范，但也意味着即使用户声明了更高的 z_score，验证标准不会相应提高。

---

#### 11. Trend Break Validation — 趋势断裂验证

- **规范定义（§2.9 L3）：** 在声明的 `break_point` 处切割时间序列，前后均值的相对变化幅度 > 15%。
- **代码实现：**
  📍 `phase_2/validation/pattern_checks.py:84-155` — `check_trend_break(df, pattern, meta)`

  执行流程：
  1. 从 `pattern` 取 `col` 和 `break_point`（优先顶层，回退 `params["break_point"]`）（L101-105）
  2. 调用 `_find_temporal_column(meta)`（L107）查找时间列
     📍 `phase_2/validation/pattern_checks.py:72-81` — 辅助函数，从 `meta["dimension_groups"]["time"]["hierarchy"][0]` 取根时间列
  3. 时间列转 `datetime64`，按 `break_point_dt` 拆分前/后掩码（L120-124）
  4. 退化检查：前后任一期行数为零 → fail（L129-137）
  5. `before_mean == 0` → fail（除零保护）（L142-147）
  6. `ratio = abs(after_mean - before_mean) / abs(before_mean)`，判断 `> 0.15`（L149-150）

- **生动类比：** 声明了"2024 年 6 月政策变化导致等待时间骤增"，那就比较 6 月前后的平均等待时间——如果增幅不到 15%，说明趋势断裂不够明显。
- 💡 **为什么这样设计？** `_find_temporal_column` 硬编码查找 `"time"` 组——这是一个实现假设：如果时间维度组名称不同（如 `"temporal"` 或 `"date"`），查找会失败。此外，使用 `abs(before_mean)` 作为分母而非 `before_mean` 是防御性处理，避免 before_mean 为负时的符号问题。

---

#### 12. Ranking Reversal Validation — 排名反转验证 ❌ 代码缺失

- **规范定义（§2.9 L3）：** 按实体分组，计算两个指标的分组均值，检查其排名相关性为负（`rank_corr < 0`）。伪代码：`means[m1].rank().corr(means[m2].rank()) < 0`。
- **代码状态：** `pattern_checks.py` 中**不存在**任何 ranking reversal 相关函数。`validator.py` 的 `_run_l3` 中，`ranking_reversal` 类型进入 `else` 分支（L132-135），只输出 debug 日志 `"no check for type 'ranking_reversal'"` 后静默跳过。
- **备注：** 规范给出了完整伪代码，属于 SPEC_READY。但存在一个已知规范问题（deep_dive §2.5 edge case）：当前伪代码硬编码使用 metadata 中"第一个 dimension group"的根列作为分组轴，而非从 pattern 参数中显式指定——这在 dict 顺序依赖上是脆弱的。

---

### Auto-Fix 循环（Loop B）

如果说 L1/L2/L3 是质检员发现问题，Loop B 就是**自动返修流水线**——不用找设计师（LLM），直接在车间调参数重做。

---

#### 13. `generate_with_validation` Wrapper — Loop B 循环结构

- **规范定义（§2.9）：** 重试循环：`seed = 42 + attempt`，每次生成后运行全部验证，失败时通过 `AUTO_FIX` 分发表匹配策略并调整参数，最多重试 3 次。全部失败则返回最后一次的 `(df, report)` 作为软失败。

- **代码状态 — 循环框架：** `autofix.py` 中 **不存在** `generate_with_validation` 函数。Stage4 设计了完整签名 `generate_with_validation(generate_fn, store, meta, base_seed, max_retries=3)`，但尚未编写循环逻辑。

- **代码状态 — 已实现的组件：**

  **a) `match_strategy(check_name, auto_fix)` ✅ 已实现**
  📍 `phase_2/validation/autofix.py:25-43`

  用 `fnmatch.fnmatch` 对 check name 做 glob 匹配，返回第一个匹配的策略函数。这是分发表的核心——将 `"ks_wait_minutes_Mild"` 匹配到 `"ks_*"` → `widen_variance`。

  **b) `widen_variance(check, params, factor=1.2)` ✅ 已实现**
  📍 `phase_2/validation/autofix.py:46-82`

  在 `params` 中查找 `"sigma"` 或 `"scale"` 键，乘以 `factor`（默认 1.2×）。返回**新 dict**（不修改原始参数）。若两个键都不存在则抛出 `InvalidParameterError`。

  **c) `amplify_magnitude(check, pattern_spec, factor=1.3)` ✅ 已实现**
  📍 `phase_2/validation/autofix.py:85-123`

  在 `pattern_spec["params"]` 中查找 `"z_score"` 或 `"magnitude"` 键，乘以 `factor`（默认 1.3×）。使用 `copy.deepcopy` 返回新 spec，保护原始数据。

  **d) `reshuffle_pair(check, df, column, rng)` ✅ 已实现**
  📍 `phase_2/validation/autofix.py:126-158`

  用 `rng.permutation(len(df))` 生成随机排列，打乱指定列的值。返回**新 DataFrame**（`.copy()`）。用于破坏正交性检查失败时的虚假相关。

- 💡 **为什么这样设计？** 三个策略函数都实现为**纯函数**——接收旧参数，返回新参数，不修改任何外部状态。这是为了与 `ParameterOverrides` 机制配合（P0 决策：frozen store 只读，所有变异走 overrides dict）。但 `ParameterOverrides` 本身和将策略输出注入下一次生成的管道尚未实现。

---

## 接口契约（已实现的）

### 入口点 1: `SchemaAwareValidator.validate(df, patterns)`

📍 `phase_2/validation/validator.py:48-83`

```python
def validate(self, df: pd.DataFrame, patterns: list[dict] | None = None) -> ValidationReport
```

- **输入：** `df` — 生成的 Master DataFrame；`patterns` — 可选的 pattern spec 列表（用于 L3）
- **输出：** `ValidationReport`（含 `.all_passed: bool`、`.failures: list[Check]`、`.checks: list[Check]`）
- **调用时机：** 每次 M2 生成完成后，由 Loop B 循环（未来的 `generate_with_validation`）调用
- **当前行为：** 运行 L1（4 项检查） → 跳过 L2（stub） → 运行 L3（仅 outlier_entity 和 trend_break）

### 入口点 2: `SchemaAwareValidator.__init__(meta)`

📍 `phase_2/validation/validator.py:40-46`

```python
def __init__(self, meta: dict[str, Any]) -> None
```

- **输入：** `meta` — schema metadata dict（来自 M4 的 `build_schema_metadata()`）
- **设计：** 持有 `self.meta` 不可变引用；不直接访问 `DeclarationStore`，保持模块边界

### 入口点 3（计划中）: `generate_with_validation`

📍 尚未实现（Stage4 设计签名在 `phase_2/validation/autofix.py`）

```python
def generate_with_validation(
    generate_fn, store, meta, base_seed: int, max_retries: int = 3
) -> tuple[pd.DataFrame, ValidationReport]
```

- **输入：** `generate_fn`（调用 M2 的 `run_pipeline`）、`store`（DeclarationStore）、`meta`、`base_seed`、`max_retries`
- **输出：** `(df, ValidationReport)` — 最终结果（可能是软失败）
- **调用时机：** 由 `pipeline.py` 在 M2+M4 完成后调用，是 Loop B 的外层入口

---

## 关键约束与不变量

| 约束 | 来源 | 代码执行 |
|---|---|---|
| Row count 偏差 < 10% | §2.9 L1 | ✅ 硬编码 0.1 |
| Cardinality 精确匹配 | §2.9 L1 | ✅ `==` 比较 |
| Marginal weight 偏差 < 0.10 | §2.9 L1 | ❌ 未实现 |
| 度量值有限且非空 | §2.9 L1 | ❌ 未实现 |
| 正交组 χ² p > 0.05 | §2.9 L1 | ✅ 硬编码 0.05 |
| DAG 无环 | §2.9 L1 | ✅ 重复检测 |
| KS test p > 0.05 per cell | §2.9 L2 | ⛔ stub |
| 残差均值 < 0.1×std | §2.9 L2 | ⛔ stub |
| 残差 std 偏差 < 20% | §2.9 L2 | ⛔ stub |
| 条件转移偏差 < 0.10 | §2.9 L2 | ⛔ stub |
| Outlier z ≥ 2.0 | §2.9 L3 | ✅ 硬编码 2.0 |
| Trend break > 15% | §2.9 L3 | ✅ 硬编码 0.15 |
| Ranking reversal corr < 0 | §2.9 L3 | ❌ 未实现 |
| Loop B max 3 retries | §2.9 | 🔧 策略就绪，循环缺失 |

**隐含约束（规范未显式声明但代码暗示）：**
- L1 应在 L2 之前完成（非有限值会导致 KS test 崩溃）
- L2 应在 L3 之前完成（基础分布错误会使模式检查不可靠）
- 当前代码**无短路机制**——所有层无条件运行（validator.py L64-76）
- `meta` 在验证循环中视为不可变——但若 auto-fix 修改了声明参数，meta 是否重建是未定义的

---

## 反馈回路参与

### Loop B：统计自动修复（M5 → M2）🔄

- **触发条件：** `ValidationReport.all_passed == False` 且 `attempt < max_retries`
- **M5 的角色：** 产出失败检查列表 → `match_strategy` 匹配修复策略 → 策略函数计算新参数 → 新参数通过 `ParameterOverrides` 传给 M2 的下一次 `generate()`
- **代码路径：**
  - 策略匹配：📍 `autofix.py:25-43` — `match_strategy()` ✅
  - KS 失败 → `widen_variance`：📍 `autofix.py:46-82` ✅
  - Outlier/Trend 失败 → `amplify_magnitude`：📍 `autofix.py:85-123` ✅
  - Orthogonal 失败 → `reshuffle_pair`：📍 `autofix.py:126-158` ✅
  - 循环框架（`generate_with_validation`）：❌ 未实现
  - `ParameterOverrides` 数据结构：❌ 未实现

- **当前限制：** 所有策略函数已实现为独立纯函数，但缺少将它们串联进重试循环的胶水代码。三个策略能产出修改后的参数，但没有消费者将这些参数注入下一次生成。

---

## TODO 地图（NEEDS_CLAR）

### 1. M5 的实际数据源 — `schema_metadata` 单独够用还是需要访问 declaration store

| 属性 | 值 |
|---|---|
| **优先级** | **P0** |
| **阻塞原因** | §2.9 伪代码引用了 `col["values"]`、`col["weights"]`、`col["formula"]`、`col["noise_sigma"]`、`dep["conditional_weights"]`——这些字段在 §2.6 的 metadata 示例中不存在 |
| **代码状态** | `validator.py` 仅消费 `meta` dict，不访问 DeclarationStore——模块边界正确。但 meta 中缺少字段，导致 L1（marginal weights）和 L2 全部被阻塞 |
| **影响下游** | M4（需扩充 metadata） |
| **Stage3 建议** | 扩充 `schema_metadata`：分类列加 `values`/`weights`，随机度量加完整 `param_model`，结构度量加 `formula`/`effects`/`noise`，组依赖加 `conditional_weights`，模式加所有 `params` |

### 2. L2 structural residual — `noise_sigma = 0` 时除以零

| 属性 | 值 |
|---|---|
| **优先级** | P1 |
| **阻塞原因** | 公式 `abs(residuals.std() - noise_sigma) / noise_sigma` 在 σ=0 时未定义 |
| **代码状态** | `check_structural_residuals` 是 `raise NotImplementedError` stub |
| **影响下游** | M2（零噪声结构度量） |
| **Stage3 建议** | 若 `noise_sigma` 为 0 或缺失，改用 `residuals.std() < 1e-6` |

### 3. L2 KS-test 预测器单元格枚举 (`iter_predictor_cells`)

| 属性 | 值 |
|---|---|
| **优先级** | P1 |
| **阻塞原因** | 未定义迭代器如何构造、小样本阈值、最大测试单元格数 |
| **代码状态** | 完全缺失——文件中无任何 `iter_predictor_cells` 相关代码 |
| **影响下游** | — |
| **Stage3 建议** | 迭代 effects 中预测器列的笛卡尔积；跳过 < 5 行的单元格；上限 100 个单元格 |

### 4. L3 — `dominance_shift` 验证逻辑

| 属性 | 值 |
|---|---|
| **优先级** | P1 |
| **阻塞原因** | §2.9 委托给 `_verify_dominance_change()`，内部为黑盒，无实现可参考 |
| **代码状态** | `_run_l3` 中 `"dominance_shift"` 进入 else 分支，静默跳过 |
| **影响下游** | — |
| **Stage3 建议** | 定义为命名实体跨时间分割点的排名变化：`params = {entity_filter, col, before_rank, after_rank, split_point}` |

### 5. L3 — `convergence` 和 `seasonal_anomaly` 验证缺失

| 属性 | 值 |
|---|---|
| **优先级** | P1 |
| **阻塞原因** | 在 §2.1.2 中列为模式类型，但 §2.9 完全没有验证逻辑 |
| **代码状态** | `_run_l3` 中静默跳过（stage4 规划为 `Check(passed=True, detail="not implemented")` stub，但连 stub 也未写） |
| **影响下游** | — |
| **Stage3 建议** | Stub 为 `Check(passed=True, detail="not implemented")`，标记 TODO 等待完整规范 |

### 6. Auto-fix 策略实现

| 属性 | 值 |
|---|---|
| **优先级** | **P0** |
| **阻塞原因** | 分发表命名了三个策略但目标参数和变异机制的端到端集成未指定 |
| **代码状态** | 三个策略函数（`widen_variance`、`amplify_magnitude`、`reshuffle_pair`）已实现为独立纯函数，但未与 Loop B 循环集成 |
| **影响下游** | M2（重新生成） |
| **Stage3 建议** | `widen_variance`: 乘 sigma 系数；`amplify_magnitude`: 乘 pattern 参数系数；`reshuffle_pair`: 独立 shuffle 一列。通过 `ParameterOverrides` dict 传递 |
| **反馈回路** | **Loop B** |

### 7. Auto-fix 变异目标 — declaration store vs. override dict vs. seed-only

| 属性 | 值 |
|---|---|
| **优先级** | **P0** |
| **阻塞原因** | `strategy(check)` 暗示状态变异，但 `build_fn(seed=42+attempt)` 会重新执行完整脚本覆盖变异 |
| **代码状态** | `ParameterOverrides` 类型未实现；三个策略返回新值但无消费者 |
| **影响下游** | M2（重新生成） |
| **Stage3 建议** | 策略变异 `ParameterOverrides` dict（非 frozen DeclarationStore）；`generate()` 接受 overrides 参数在 draw 时查询 sigma scaling 等 |
| **反馈回路** | **Loop B** |

### 8. 验证排序 — 在 realism 注入之前还是之后

| 属性 | 值 |
|---|---|
| **优先级** | P2 |
| **阻塞原因** | L1 finiteness check 与 `missing_rate` NaN 注入冲突；L3 pattern 信号可能被 NaN 破坏 |
| **代码状态** | `validate()` 中无 realism 相关逻辑；当前假设输入 df 尚未经过 realism 处理 |
| **影响下游** | M2（stage δ） |
| **Stage3 建议** | 在 realism 注入之前验证；realism 作为验证通过后的最后一步 |
| **反馈回路** | **Loop B** |

---

## 实现细节（规范未覆盖的辅助代码）

| 函数/类 | 位置 | 用途 |
|---|---|---|
| `max_conditional_deviation()` | `phase_2/validation/statistical.py:21-52` | 嵌套 dict 最大绝对偏差计算，为 L2 group dep 检查准备的工具函数 |
| `_find_temporal_column()` | `phase_2/validation/pattern_checks.py:72-81` | 从 `meta["dimension_groups"]["time"]` 定位时间列根节点 |
| `Check` dataclass | `phase_2/types.py:233-250` | 验证结果记录：`name`、`passed`、`detail` |
| `ValidationReport` dataclass | `phase_2/types.py:254-307` | 聚合检查结果；提供 `all_passed`（全通过判断）、`failures`（失败列表）、`add_checks()`（追加批次） |
| columns metadata 格式兼容 | `structural.py:75-78` | `check_categorical_cardinality` 中兼容 dict 和 list 两种 `columns` 格式 |
| 列联表退化检查 | `structural.py:148-156` | 正交独立性检查中，列联表 < 2×2 时直接 fail |
| `PatternInjectionError` 引用 | `pattern_checks.py:17` | 从 `phase_2.exceptions` 导入，用于 trend_break 时间列缺失异常 |
