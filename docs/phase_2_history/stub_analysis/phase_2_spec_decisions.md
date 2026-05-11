# AGPDS Phase 2 — Stub Spec Extension Decisions

基于 `stub_gap_analysis.md` 所有 proposed solutions 的完整决策记录。
覆盖 10 个 stub（IS-1..IS-6，DS-1..DS-4）的全部 critical blocker 解答。

---

## Measure 层（IS-1 + DS-3 配对）

### [IS-1] Mixture distribution sampling

| 维度 | 决策 |
|------|------|
| **Param model schema** | `{"components": [{"family": str, "weight": float, "param_model": {...}}, ...]}` |
| **Predictor effects 交互** | Interpretation (a)：每个 component 有独立 `param_model`（intercept + effects），weights 为常量，per-row component 赋值随机抽取 |
| **Weight 归一化** | 自动归一化（`[0.3, 0.2]` → `[0.6, 0.4]`） |
| **Autofix 策略** | Mixture opt-out `widen_variance`（不尝试扩展任一 component 的 sigma），最简路径 |
| **新增类型** | `MixtureComponent(TypedDict)` in `types.py`：`{family: str, weight: float, param_model: dict}` |

**解锁的 spec 修改：** 在 `sdk/columns.py::validate_param_model` 增加 `"mixture"` 分支，校验 `components` 列表结构及每个 component 的 `family`、`weight`、`param_model` 字段。

---

### [DS-3] Mixture KS test

| 维度 | 决策 |
|------|------|
| **CDF 构建** | `_MixtureFrozen` adapter：`cdf(x) = Σ w_k · D_k.cdf(x)`，权重自动归一化 |
| **Cell params 扩展** | 扩展 `_compute_cell_params` 走 components 列表，per-component 递归调用现有 flat-params 分支 |
| **不支持 family 处理** | 某 component family 无 CDF → 返回 `None`，跳过该 predictor cell（保持现有"CDF not available"行为） |
| **前置依赖** | **必须在 IS-1 之后实现**，不可独立推进 |

---

## Pattern validation 层（IS-2 / IS-3 / IS-4）

### [IS-2] Dominance shift validation

| 维度 | 决策 |
|------|------|
| **算法** | Interpretation (a)：目标 entity 在 `split_point` 前后的 rank 变化量 ≥ 阈值 |
| **必填 params** | `entity_filter`（目标实体值）、`split_point`（时间切分点） |
| **可选 params** | `entity_col`（未传则 fallback 到第一个 dim_group hierarchy root）、`rank_change`（默认 1） |
| **Pass 条件** | `|rank_after - rank_before| >= rank_change` |
| **Rank 方向** | 按 col 均值降序排名（值越大 rank 越小），与 `check_ranking_reversal` 保持一致 |

---

### [IS-3] Convergence validation

| 维度 | 决策 |
|------|------|
| **算法** | Interpretation (b)：各 entity 组均值的方差在后半段相比前半段减少 ≥ 阈值（组间收敛，非单 entity 收敛） |
| **切分基准** | `split_point`（可选，未传则默认时间中位数 `quantile(0.5)`） |
| **可选 params** | `entity_col`（同 IS-2 fallback）、`reduction`（默认 0.3，即 30% 方差缩减） |
| **Pass 条件** | `(early_var - late_var) / early_var >= reduction` |
| **边界处理** | `early_var == 0` → `passed=False`（detail 说明）；每侧 entity 数 < 2 → `passed=False` |

---

### [IS-4] Seasonal anomaly validation

| 维度 | 决策 |
|------|------|
| **算法** | Interpretation (a)：`anomaly_window` 内均值与 baseline（window 外所有行）的 z-score ≥ 阈值 |
| **Window 决策** | 显式传 `anomaly_window=[start, end]`；未传则默认最后 10% 时间区间（`tmin + (tmax-tmin)*0.9` 到 `tmax`） |
| **可选 params** | `z_threshold`（默认 1.5） |
| **Pass 条件** | `|win_mean - base_mean| / base_std >= z_threshold` |
| **前置条件** | temporal column 必须存在；缺失则返回 `passed=False`（不 raise），detail 说明原因 |
| **边界处理** | `base_std == 0`、`window` 为空、`baseline < 2` 行 → 均返回 `passed=False` |

---

## Pattern injection 层（DS-2 — 4 个 injector）

### [DS-2] 4 pattern type injection

**解锁时需同步更新的三个位置（缺一不可）：**
1. `sdk/relationships.py::VALID_PATTERN_TYPES` — 添加 4 个类型名
2. `sdk/relationships.py::PATTERN_REQUIRED_PARAMS` — 添加各类型必填参数集
3. `orchestration/prompt.py:72` + One-Shot Example — 重新向 LLM 广播这 4 种类型

#### ranking_reversal

| 维度 | 决策 |
|------|------|
| **必填 params** | `metrics`（两列名，list） |
| **可选 params** | `entity_col`（fallback 同 IS-2/IS-3） |
| **注入算法** | Entity-mean level shift（非 row-level pairing）：按 entity 分组计算 m1 均值并排序，反向映射期望 m2 均值，对每个 entity 用加法 shift 使其均值到达目标位置（保留 within-entity 方差） |
| **与 validator 对应** | `check_ranking_reversal`（已实现），验证 Spearman 相关系数 < 0 |

#### dominance_shift

| 维度 | 决策 |
|------|------|
| **必填 params** | `entity_filter`、`split_point` |
| **注入算法** | 计算 post-split peer_max，将目标 entity post-split 均值平移至 `peer_max + magnitude × peer_std`（additive shift） |
| **与 validator 对应** | IS-2 `check_dominance_shift`（需同步实现） |

#### convergence

| 维度 | 决策 |
|------|------|
| **必填 params** | 无（全部可选） |
| **注入算法** | 随时间线性 pull 各行向 global_mean：`val = val × (1 - factor) + global_mean × factor`，`factor = (t - tmin)/(tmax - tmin) × pull` |
| **与 validator 对应** | IS-3 `check_convergence`（需同步实现） |

#### seasonal_anomaly

| 维度 | 决策 |
|------|------|
| **必填 params** | `anomaly_window`（[start, end]）、`magnitude` |
| **注入算法** | Window 内行乘 `(1 + magnitude)`，mirror `inject_trend_break` 但使用有限 [start, end] 窗口而非半无限 break_point |
| **与 validator 对应** | IS-4 `check_seasonal_anomaly`（需同步实现） |

---

## Realism 层（DS-1）

### [DS-1] Censoring injection

| 维度 | 决策 |
|------|------|
| **Schema** | Per-column dict：`{"col_name": {"type": "right"\|"left"\|"interval", "threshold": float}}`；interval 类型用 `low`/`high` 替代 `threshold` |
| **Marker 语义** | NaN 替换（不增加 `<col>_censored` indicator 列；Phase 3 无需特殊处理） |
| **执行顺序** | Censoring **先于** missing injection 执行，missing_rate 基于 post-censor 分布计算 |
| **未知 type** | 抛 `ValueError`（含列名和非法 type 值） |
| **列不存在** | `logger.warning` 并跳过，不中断其他列 |
| **新增类型** | `CensoringSpec(TypedDict)` in `types.py`：`{type: Literal["right","left","interval"], threshold?: float, low?: float, high?: float}` |
| **解锁还需** | `set_realism` SDK 校验升级 + `prompt.py:70-71` 重新广播 `censoring=` kwarg + One-Shot Example 更新 |

---

## SDK 层（DS-4 + IS-5）

### [DS-4] Multi-column group dependency `on`

| 维度 | 决策 |
|------|------|
| **Weight 结构** | Nested dict，深度 = `len(on)`，例：`{"Mild": {"Xiehe": {"Insurance": 0.8, "Self-pay": 0.2}}}` |
| **Cartesian coverage** | 必须覆盖完整 Cartesian product（与 single-column 规则一致；无 partial coverage fallback） |
| **缺失 key 处理** | 抛 `ValueError` 并携带完整 key path（如 `conditional_weights["Mild"] missing parent values: {"Severe"}`） |
| **Cardinality 上限** | 无 soft cap（LLM 责任；过大时由 clear error 提示） |
| **Engine 侧** | N-deep nested dict walk per row：`for parent_arr in parent_arrays: node = node[parent_arr[i]]`，最终 leaf 即 `{child_val: weight}` |
| **Validation 侧** | `max_conditional_deviation` 扩展为递归走 N-deep 结构 |

---

### [IS-5] `scale` kwarg — 不恢复

| 维度 | 决策 |
|------|------|
| **结论** | **不恢复**；仅文档操作，代码无需改动 |
| **操作** | 从 spec §2.1.1 L51 和 §2.5 L287 删除 `scale=None` 残留签名 |
| **理由** | spec 从未定义 `scale` 的任何语义；prompt 和 SDK 均已收敛于缺省；当前 TypeError 行为是正确的防御性选择 |

---

## 运营优化层（IS-6）

### [IS-6] Multi-error + token budget

| 功能 | 决策 |
|------|------|
| **Multi-error** | **延迟**，需 A/B test 确认对 LLM 有益后再默认开启；架构上用 opt-in `ValidationContext(accumulate=True)`，不破坏现有单错误行为 |
| **Token budget** | **优先船**，对运营有即时价值，无需 A/B 验证 |
| **Budget 粒度** | Per-scenario 累积（跨 retry 累加），非 per-attempt |
| **LLMClient 扩展** | 需返回结构化 `LLMResponse(token_usage: TokenUsage)`；无 usage 时优雅降级（计 0，不中断重试） |
| **唯一未决问题** | Multi-error A/B test 的"开启条件"——这是实验性决策，proposed solution 仅给出架构方案，何时开启取决于测试结果 |

---

## 决策间内部一致性要求

以下约束跨越多个 stub，实现时必须同步维护：

### 1. IS-1 ↔ DS-3：Schema 必须共享
`_sample_mixture`（IS-1）与 `_expected_cdf_mixture`（DS-3）必须使用完全相同的 `param_model` schema（components 结构、weight 归一化逻辑）。分开实现必然导致 sampler 与 KS CDF 漂移，产生静默错误（KS 始终 pass 或始终 fail）。

**实操建议：** 在同一 PR 中实现 IS-1 和 DS-3，共享 `_compute_per_row_params` 作为 per-component param 求解入口。

### 2. DS-2 injector ↔ IS-2/IS-3/IS-4 validator：操作定义必须对齐
每对 (injector, validator) 必须基于相同的量化定义：

| Injector（DS-2） | Validator（IS-x） | 必须对齐的量 |
|---|---|---|
| `inject_dominance_shift` | `check_dominance_shift`（IS-2） | `split_point` 语义、rank 计算方向 |
| `inject_convergence` | `check_convergence`（IS-3） | `pull` 参数强度须足以达到 30% 方差缩减阈值 |
| `inject_seasonal_anomaly` | `check_seasonal_anomaly`（IS-4） | `magnitude` 参数须足以达到 z-score 1.5 阈值；`anomaly_window` 定义一致 |

**实操建议：** 每对 (injector, validator) 在同一 PR 中实现，并用 roundtrip 集成测试验证：inject 后 validate 必须通过。

### 3. DS-2 解锁的三个位置必须同步
`VALID_PATTERN_TYPES`（SDK）、`PATTERN_REQUIRED_PARAMS`（SDK）、`prompt.py:72`（prompt）、One-Shot Example 四处必须同步更新，缺一则 LLM 看不到新类型或 SDK 会 reject。同理适用于 DS-1（`prompt.py:70-71` + One-Shot Example）。

### 4. DS-4 SDK ↔ Engine：嵌套结构必须共享
`add_group_dependency` 的 `_validate_and_normalize_nested_weights`（SDK validation）与 `_sample_group_dep`（engine sampling）必须使用相同的 N-deep dict walk 逻辑。SDK 侧归一化后写入 `GroupDependency.conditional_weights`，engine 侧直接消费同一结构。

### 5. IS-2/IS-3/IS-4 共享辅助函数
三个 validator 共同依赖：
- `_find_temporal_column(meta)` — 已存在
- `_resolve_first_dim_root(meta)` — IS-2 proposed solution 中新增，IS-3/IS-4 复用

`_resolve_first_dim_root` 应在 IS-2 实现时提取为模块级函数，IS-3/IS-4 直接 import，避免三份拷贝。

---

*本文档由 stub_gap_analysis.md Phase C 提炼，覆盖所有 10 个 stub 的 spec 决策。唯一剩余开放项：IS-6 multi-error 的 A/B 测试结论。*
