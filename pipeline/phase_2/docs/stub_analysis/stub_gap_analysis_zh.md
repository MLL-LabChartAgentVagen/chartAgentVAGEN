# AGPDS Phase 2 —— Stub 缺口分析

## 背景

本文档分析 AGPDS Phase 2 代码库中,在 Sprint 6 收尾后仍残留的所有
**有意 stub(intentional)** 与 **依赖 stub(dependent)**。该清单已记录于
`stage5_anatomy_summary.md` §4 / `pipeline/phase_2/docs/remaining_gaps.md`。

本文档目的是推动一个有针对性的决策:**哪些 stub 需要关闭、按什么顺序、以及
需要什么样的规范输入** —— 通过为每一项确认 (a) 代码当前的行为、(b) 规范实
际的内容、(c) 缺口在哪里、(d) 关闭它的阻塞因素、(e) 一个具体的实现方案。

### 范围

10 个 stub:6 个有意 stub(IS-1..IS-6) + 4 个依赖 stub(DS-1..DS-4)。

每个 stub 按三个分析阶段展开:

**阶段 A —— 清单确认与代码阅读**
1. 实际当前位置上的逐字代码片段(行号已与活源码核对)。
2. 规范 `phase_2.md` 中所有引用此功能的章节。
3. `pipeline/phase_2/tests/`(根 + `modular/`)中触及、跳过或引用此 stub 的
   测试。
4. 依赖 stub(必须先填充本 stub 才能完成的子项)。

**阶段 B —— 缺口分析**
5. 在管道中的角色 —— 它位于 §2.8 / §2.9 执行流的什么位置,谁消费它、它消
   费什么。
6. 缺口分析 —— 规范定义了什么、规范保持沉默的是什么、实现层面的缺口是什么。
7. 依赖链 —— 此 stub 阻塞什么(子)、什么阻塞此 stub(父项与规范决策)、必
   须与什么一起实现。

**阶段 C —— 解决方案提议**
8. 阻塞性问题 —— 仅指真正无法回答的问题(规范层面或架构层面)。
9. 提议方案 —— 函数签名、实现草图、集成点、新类型(若有)。
10. 测试标准 —— 必须验证什么。
11. 估算规模 —— trivial / small / medium / large,通过与既有类比的比较来
    论证。

### 已读源

- `pipeline/phase_2/engine/measures.py`、`engine/realism.py`、
  `engine/patterns.py`
- `pipeline/phase_2/validation/pattern_checks.py`、
  `validation/statistical.py`
- `pipeline/phase_2/sdk/columns.py`、`sdk/simulator.py`、
  `sdk/relationships.py`
- `pipeline/phase_2/orchestration/prompt.py`、
  `orchestration/sandbox.py`
- `pipeline/phase_2/pipeline.py`
- `pipeline/phase_2/docs/artifacts/phase_2.md`
- `pipeline/phase_2/tests/` 与 `tests/modular/` 下所有测试文件

---

# 有意 stub(6 个)

## [IS-1] 混合分布采样

### 代码片段
```python
# pipeline/phase_2/engine/measures.py:360-366
if family == "mixture":
    raise NotImplementedError(
        "mixture distribution sampling not yet implemented. "
        "Expected param_model schema: {'components': [{'family': str, "
        "'weight': float, 'params': {...}}, ...]}"
    )
```
(注:CLAUDE.md 中列出的是 `~L297-303`;实际位置是当前源码的 L360-366 ——
行号在实现后已发生漂移。)

### 规范引用
- §2.1.1 (L51–94):`add_measure()` 声明在 `SUPPORTED_DISTRIBUTIONS`
  (L94)中将 `"mixture"` 与 `gaussian`、`lognormal`、`gamma`、`beta`、
  `uniform`、`poisson`、`exponential` 一同列为受支持分布。
- §2.3 (L162–196):闭式测度声明 —— 定义了根据分类上下文从分布族参数中采样
  随机根 measure 的方式。Mixture 在概念上被涵盖,但没有给出每个族的参数
  schema。
- §2.5 (L302):LLM Code Generation Prompt 的允许分布列表中包含
  `"mixture"`。

### 既有测试
- (未发现)

### 依赖 stub
- DS-3:Mixture KS 检验 —— `pipeline/phase_2/validation/statistical.py:259-264`

### 在管道中的角色
位于 §2.8 step β(measure 生成)中的 `_sample_stochastic`,即
[engine/measures.py:329-378](pipeline/phase_2/engine/measures.py#L329-L378)。
上游:从 α 步骤接收每行预测变量值以及 `family="mixture"` 的 `col_meta`。下
游:输出采样得到的列,被引用此列的结构性 measure、L2 KS 校验器(DS-3 也
在此处 stub)消费,并最终被 Phase 3 视图抽取使用。当 LLM 脚本声明
`sim.add_measure(name, "mixture", param_model)` 且引擎到达该列拓扑位置时
触发。

### 缺口分析
- **规范定义:** `"mixture"` 在 `SUPPORTED_DISTRIBUTIONS` 中(§2.1.1
  L94、§2.5 L302)。§2.3 草绘了随机 measure 的通用参数模式
  `intercept + sum(effects)`。
- **规范沉默:** mixture 的参数 schema —— §2.1.1 或 §2.3 中没有
  `components: [{family, weight, params}]` schema,§2.5 或 One-Shot
  Example 中也没有任何示例,也没有规则说明 mixture 如何与 predictor
  effects 交互(组件是否共享 predictor、权重是否随 predictor 变化等)。
- **实现缺口:** sampler 抛 `NotImplementedError`。即使错误信息中建议的
  schema(`{components: [{family, weight, params}]}`)也是 *实现的猜测*,
  而非规范定义的契约。填补此 stub 需要 (a) 规范扩展定义 mixture schema、
  (b) sampler 实现、(c) 配套的 L2 CDF 构造器(DS-3)。

### 依赖链
- **阻塞:** DS-3(mixture KS 检验)。没有采样算法就没有可测的分布;没有
  定义好的组件 schema,`_expected_cdf` 就没有可构造的形状。
- **被以下阻塞:** 规范扩展定义 mixture `param_model` schema。这是 **规范
  缺口**,不仅仅是代码缺口。
- **共依赖于:** DS-3。两者必须一起实现,以确保校验器使用的 CDF 与 sampler
  一致。独立实现会出现漂移。

### 阻塞性问题
- **规范:** mixture 与 predictor effects 如何交互?有三种合理解读:
  (a) 每个组件携带自己的 `param_model`(`intercept + effects`),权重为
  常数;(b) 组件参数为常数,但 mixture 权重随 predictor 变化;(c) 两者
  都变化。(a) 与既有模式最接近;(b)/(c) 更丰富但更难校验。
- **规范:** 组件族是否限制为仅连续型,还是允许混合类型 mixture(如
  gaussian + poisson)?会影响 KS 可测性。

### 提议方案
选解读 (a)。重构 `_sample_stochastic` 中的现有分发,抽出一个可复用的
`_sample_family` 辅助函数,然后新增一个对组件循环的 `_sample_mixture`。

```python
# pipeline/phase_2/engine/measures.py — replace the NotImplementedError
# block at L360-366 with a dispatch to _sample_mixture.

def _sample_family(
    family: str,
    params: dict[str, np.ndarray],
    n_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Family-dispatch helper extracted from _sample_stochastic L387-403."""
    mu = params.get("mu", np.zeros(n_rows))
    sigma = params.get("sigma", np.ones(n_rows))
    if family == "gaussian":
        return rng.normal(mu, sigma)
    elif family == "lognormal":
        return rng.lognormal(mu, sigma)
    # ... gamma, beta, uniform, poisson, exponential
    else:
        raise ValueError(f"Unknown distribution family: '{family}'")


def _sample_mixture(
    col_name: str,
    col_meta: dict[str, Any],
    rows: dict[str, np.ndarray],
    rng: np.random.Generator,
    overrides: dict | None = None,
) -> np.ndarray:
    """Sample from a mixture distribution.

    Schema (per blocking-question decision (a)):
        param_model = {
            "components": [
                {"family": str, "weight": float, "param_model": {...}},
                ...
            ]
        }
    Each component's `param_model` follows the same intercept+effects
    shape as a non-mixture stochastic measure. Weights are auto-normalized.
    """
    components = col_meta["param_model"]["components"]
    weights = np.array([c["weight"] for c in components], dtype=float)
    weights = weights / weights.sum()

    n_rows = next(iter(rows.values())).shape[0] if rows else 0
    if n_rows == 0:
        return np.array([], dtype=np.float64)

    # Per-row component assignment
    component_idx = rng.choice(len(components), size=n_rows, p=weights)

    out = np.empty(n_rows, dtype=np.float64)
    for k, comp in enumerate(components):
        mask = component_idx == k
        if not mask.any():
            continue
        sub_meta = {"family": comp["family"], "param_model": comp["param_model"]}
        sub_params = _compute_per_row_params(
            f"{col_name}[c{k}]", sub_meta, rows, n_rows, overrides,
        )
        sub_params_masked = {p: arr[mask] for p, arr in sub_params.items()}
        out[mask] = _sample_family(comp["family"], sub_params_masked, int(mask.sum()), rng)
    return out
```

**集成点:**
- `_sample_stochastic`([engine/measures.py:329](pipeline/phase_2/engine/measures.py#L329))
  在 `family == "mixture"` 时分发到 `_sample_mixture`。
- `_compute_per_row_params`([engine/measures.py:406](pipeline/phase_2/engine/measures.py#L406))
  按组件复用(已经处理 intercept+effects)。
- `sdk/columns.py::validate_param_model` 必须学会 mixture schema(校验
  `components` 列表、每个组件的 `family`、`weight`、`param_model`)。
- `sdk/relationships.py` —— 无变更(mixture 是声明期事项,而非 pattern 期)。

**新类型:** `types.py` 中的 `MixtureComponent(TypedDict)`:

```python
class MixtureComponent(TypedDict):
    family: str
    weight: float
    param_model: dict[str, Any]
```

### 测试标准
- 权重为 `[0.6, 0.4]`、均值差异显著的 2 组件 gaussian mixture →
  经验均值 ≈ 组件均值的加权均值,误差 5% 以内。
- 每组件参数为常数的 3 组件 mixture → 样本通过 scipy mixture-CDF 的 KS
  检验。
- 组件随 predictor 变化的 mixture → 在每个 predictor 单元格内,样本与
  期望 mixture 分布一致。
- 权重归一化:`[0.3, 0.2]` 自动归一化为 `[0.6, 0.4]`。
- 校验器侧:`_validate_param_model("mixture", {})` 抛出
  `InvalidParameterError`,清楚说明 `components` 形状。

### 估算规模
**Medium (80–200 LOC)。** Sampler ~50 LOC + 校验器 schema ~30 LOC +
类型定义 ~10 LOC + 测试 ~80 LOC ≈ 170 LOC。可比类比:既有的
`_sample_stochastic` + `_compute_per_row_params` 约 150 LOC。

**Autofix 注意事项(有效规模膨胀点)。** 既有的 `ks_*` autofix 策略
(`widen_variance`)按 measure 索引单一 `sigma` 字段 —— 不能自然适用于
mixture 分布,因为每个组件都有自己的 `sigma`。联合实现 IS-1 + DS-3 还需
决定 (a) 让 mixture 退出 `widen_variance`(最简单)、(b) 仅放宽权重最大的
组件、(c) 按比例放宽所有组件。无论选择哪种,autofix 侧的改动约 20-40 LOC
加测试,使 IS-1 + DS-3 + autofix 的合计面超过 ~300 LOC 的配对估算。

---

## [IS-2] Dominance shift 校验

### 代码片段
```python
# pipeline/phase_2/validation/pattern_checks.py:189-213
def check_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Dominance shift validation (stub).

    [P1-3]

    TODO [M5-NC-4 / P1-3]: Define as rank change of entity across temporal
    split. Expected params: entity_filter, col, split_point.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "dominance_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"dominance_{pattern['col']}",
        passed=True,
        detail="dominance_shift validation not yet implemented",
    )
```

### 规范引用
- §2.1.2 (L127):`"dominance_shift"` 列于 `inject_pattern()` 的
  `PATTERN_TYPES` 中。
- §2.5 (L305):LLM prompt 中允许的 pattern 类型列表包含
  `"dominance_shift"`。
- §2.9 L3 (L672–674):伪代码草图给出
  `elif p["type"] == "dominance_shift": self._verify_dominance_change(df, p, meta)`
  但校验器主体未做规定。

### 既有测试
- (未发现)

### 依赖 stub
- (无直接;但若没有 DS-2 则无法端到端运行 —— `dominance_shift` 的 pattern
  注入会抛 `NotImplementedError`。)

### 在管道中的角色
位于 §2.9 L3 pattern 校验,在引擎生成与 pattern 注入之后由校验器调用。
上游:生成的 DataFrame 加上 `type=="dominance_shift"` 的 pattern 字典。
下游:返回一个被 `ValidationReport` 消费的 `Check`;失败本应路由到
`AUTO_FIX`,但 `dominance_*` 策略不存在。当前函数无条件返回
`passed=True`,所以无论数据如何,dominance_shift pattern 都会静默"通过"
校验。

### 缺口分析
- **规范定义:** §2.1.2 L127 在 PATTERN_TYPES 中列出
  `"dominance_shift"`;§2.5 L305 在 prompt 中列出;§2.9 L3 (L672–674)
  草绘调用面为 `elif p["type"] == "dominance_shift":
  self._verify_dominance_change(df, p, meta)`。
- **规范沉默:** `_verify_dominance_change` 的算法主体 —— 没有运算定义
  (实体在时间切分上的排名变化?份额交叉?top-k 变化?),除源码 TODO
  推测的 `entity_filter, col, split_point` 之外没有 params 契约,没有
  通过阈值,§2.6 patterns metadata 中也没有示例。
- **实现缺口:** stub 硬编码返回 `passed=True`。规范定义了调用面但没有
  算法。真实实现必须 (a) 定义 params 契约、(b) 按 `split_point` 切分
  数据、(c) 计算 dominance/rank 度量、(d) 定义通过阈值。(a)–(d) 都不在
  规范中。

### 依赖链
- **阻塞:** 直接无(它是一个叶 stub 校验器)。
- **被以下阻塞:** 规范扩展,定量定义"dominance shift" + params 契约;
  **DS-2**(dominance_shift 的 pattern 注入)以便端到端运行 —— 没有注入
  就没有可校验的信号。
- **共依赖于:** DS-2 —— 注入器与校验器必须共享同一运算定义。

### 阻塞性问题
- **规范:** "dominance shift" 的运算定义。三种合理候选:(a) 目标实体
  在时间切分上的排名反转(目标从 #1 移到 #N 或反之);(b) 均值/和的
  交叉(切分前 A > B,切分后 A < B);(c) 市场份额交叉。源码 TODO
  ("rank change of entity across temporal split")指向 (a)。
- **规范:** 通过阈值 —— 所需的最小排名变化(默认 1?可通过
  `params.rank_change` 配置?)。

### 提议方案
选解读 (a)。镜像 `check_trend_break`(也是按时间前后的 pattern)。复用
[validation/pattern_checks.py:94](pipeline/phase_2/validation/pattern_checks.py#L94)
中已有的 `_find_temporal_column`,以及
[`check_ranking_reversal`](pipeline/phase_2/validation/pattern_checks.py#L268-L316)
中的 entity-col fallback。

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L189-213.

def check_dominance_shift(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Dominance shift — target entity's rank changes across split.

    Algorithm (interpretation (a)):
      1. Resolve entity_col (param or first dim-group root).
      2. Resolve temporal_col from meta.
      3. Split data at params["split_point"].
      4. Per side, group by entity_col, compute mean of pattern["col"].
      5. Pass if |rank_after - rank_before| of params["entity_filter"]
         >= params.get("rank_change", 1).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    target_entity = params.get("entity_filter")
    split_point = params.get("split_point")
    rank_threshold = params.get("rank_change", 1)
    name = f"dominance_{col}"

    if not target_entity or not split_point:
        return Check(name=name, passed=False,
                     detail="Missing entity_filter or split_point in params.")

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(name=name, passed=False,
                     detail=f"Missing entity_col={entity_col!r} or temporal_col={temporal_col!r}.")

    sp = pd.to_datetime(split_point)
    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    before_means = df[tval < sp].groupby(entity_col)[col].mean()
    after_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if target_entity not in before_means.index or target_entity not in after_means.index:
        return Check(name=name, passed=False,
                     detail=f"Target entity {target_entity!r} missing on one side of split.")

    rank_before = before_means.rank(ascending=False)[target_entity]
    rank_after = after_means.rank(ascending=False)[target_entity]
    delta = abs(rank_after - rank_before)
    passed = bool(delta >= rank_threshold)
    return Check(
        name=name, passed=passed,
        detail=f"rank_before={int(rank_before)}, rank_after={int(rank_after)}, delta={int(delta)} (threshold={rank_threshold})",
    )


def _resolve_first_dim_root(meta: dict[str, Any]) -> Optional[str]:
    """Factor of the entity-col fallback in check_ranking_reversal."""
    dim_groups = meta.get("dimension_groups", {})
    if not dim_groups:
        return None
    first = dim_groups[next(iter(dim_groups))]
    hierarchy = first.get("hierarchy", [])
    return hierarchy[0] if hierarchy else None
```

**集成点:**
- [validation/validator.py](pipeline/phase_2/validation/validator.py)
  中的校验器分发已将 pattern 类型 `"dominance_shift"` 路由到此函数 ——
  仅函数体改变。
- 复用 `_find_temporal_column`;新增此处与 IS-3/IS-4 共用的小工具
  `_resolve_first_dim_root`。

**新类型:** 无。

### 测试标准
- 注入合成的前/后均值,使目标排名 1→3 → passed=True。
- 排名跨切分稳定 → passed=False。
- 缺失 `entity_filter` / `split_point` → passed=False,且 detail 清晰。
- 目标实体在某一侧不存在 → passed=False。
- 缺失时间列 → passed=False。

### 估算规模
**Small (20–80 LOC)。** 函数体 ≈ 45 LOC + 辅助 ≈ 8 LOC + 测试
≈ 60 LOC ≈ 110 LOC 总计(刚超 small 区间但远低于 medium)。类比:
`check_trend_break` 函数体 ~80 LOC。

---

## [IS-3] Convergence 校验

### 代码片段
```python
# pipeline/phase_2/validation/pattern_checks.py:216-239
def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence validation (stub).

    TODO [M5-NC-5 / P1-4]: Convergence validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "convergence_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"convergence_{pattern['col']}",
        passed=True,
        detail="convergence validation not yet implemented",
    )
```

### 规范引用
- §2.1.2 (L127):`"convergence"` 列于 `PATTERN_TYPES`。
- §2.5 (L305):LLM prompt 中允许的 pattern 类型列表包含
  `"convergence"`。
- §2.9 L3 (L644–677):无伪代码或算法 —— convergence 校验在 L3
  pattern 校验伪代码中**完全缺席**。

### 既有测试
- (未发现)

### 依赖 stub
- (无直接;同 IS-2 的 DS-2 链。)

### 在管道中的角色
与 IS-2 架构位置相同 —— §2.9 L3 pattern 校验,在引擎与 pattern 注入
之后调用。上游:`type=="convergence"` 的 pattern 字典。下游:供
`ValidationReport` 使用的 `Check`;`AUTO_FIX` 没有 `convergence_*` 条目。
当前无条件返回 `passed=True`。

### 缺口分析
- **规范定义:** §2.1.2 L127 在 PATTERN_TYPES 列出 `"convergence"`;
  §2.5 L305 在 prompt 中列出。
- **规范沉默:** **其余一切。** 与 `dominance_shift` 不同,§2.9 L3
  *没有* convergence 的伪代码分支 —— 它甚至未出现在校验草图中。没有
  params 契约、没有算法、没有校验标准、§2.6 中也没有示例。convergence
  在所有 stub 中规范覆盖最薄。
- **实现缺口:** stub 返回 `passed=True`。无论是注入(DS-2)还是校验
  (IS-3),都需要"convergence"的形式定义 —— 例如组内时间序列方差
  下降、组间均值对齐、排名靠拢。规范完全没有锚点。

### 依赖链
- **阻塞:** 直接无。
- **被以下阻塞:** 规范扩展正式定义 convergence(在这里比 IS-2 更关键,
  因为规范没有提供任何算法指引);**DS-2** 用于端到端运行。
- **共依赖于:** DS-2 —— 注入器与校验器必须共享同一运算定义。

### 阻塞性问题
- **规范:** 运算定义。候选:(a) `pattern["col"]` 的方差随时间整体下降;
  (b) 组均值方差随时间下降(各组变得同质);(c) 某对实体的均值单调
  靠拢。图表叙事意图(各组变得相似)指向 (b)。
- **规范:** 比较参考 —— 早半段对晚半段?滑动窗口?默认采用单一中点切分。
- **规范:** "convergence 已发生"的阈值。合理默认:
  `late_var <= early_var × (1 - 0.3)`(下降 30%)。

### 提议方案
选解读 (b)。复用 `check_dominance_shift` 的按切分时间逻辑。复用
`_find_temporal_column` 与 `_resolve_first_dim_root`。

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L216-239.

def check_convergence(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Convergence — variance of group means decreases over time.

    Algorithm (interpretation (b)):
      1. Resolve entity_col and temporal_col.
      2. Split at params["split_point"] or temporal median.
      3. Per side, compute per-entity mean of pattern["col"].
      4. Compare variance-of-means: reduction = (early_var - late_var) / early_var.
      5. Pass if reduction >= params.get("reduction", 0.3).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    threshold = params.get("reduction", 0.3)
    name = f"convergence_{col}"

    entity_col = params.get("entity_col") or _resolve_first_dim_root(meta)
    temporal_col = _find_temporal_column(meta)
    if entity_col is None or temporal_col is None:
        return Check(name=name, passed=False,
                     detail=f"Missing entity_col={entity_col!r} or temporal_col={temporal_col!r}.")

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    sp = pd.to_datetime(params["split_point"]) if params.get("split_point") else tval.quantile(0.5)
    early_means = df[tval < sp].groupby(entity_col)[col].mean()
    late_means = df[tval >= sp].groupby(entity_col)[col].mean()

    if len(early_means) < 2 or len(late_means) < 2:
        return Check(name=name, passed=False,
                     detail=f"Need >=2 entities per side, got early={len(early_means)}, late={len(late_means)}.")

    early_var = float(early_means.var())
    late_var = float(late_means.var())
    if early_var == 0:
        return Check(name=name, passed=False, detail="Early-period inter-group variance is 0.")

    reduction = (early_var - late_var) / early_var
    passed = bool(reduction >= threshold)
    return Check(
        name=name, passed=passed,
        detail=f"early_var={early_var:.4f}, late_var={late_var:.4f}, reduction={reduction:.3f} (threshold={threshold})",
    )
```

**集成点:**
- 与 IS-2 相同的分发接线;只改变函数体。
- 复用 `_find_temporal_column` 与 `_resolve_first_dim_root`。

**新类型:** 无。

### 测试标准
- 晚期组均值一致、早期分散 → passed=True。
- 各时段组均值分散程度稳定 → passed=False。
- 单一实体(只有一组)→ 优雅失败,detail 清晰。
- 缺失时间列 → 优雅失败。
- 常量列(`early_var == 0`)→ 优雅失败。

### 估算规模
**Small (20–80 LOC)。** 函数体 ≈ 40 LOC + 测试 ≈ 50 LOC ≈ 90 LOC。
类比:`check_ranking_reversal` 函数体 ~80 LOC。

---

## [IS-4] Seasonal anomaly 校验

### 代码片段
```python
# pipeline/phase_2/validation/pattern_checks.py:242-265
def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly validation (stub).

    TODO [M5-NC-5 / P1-4]: Seasonal anomaly validation not yet specified.

    [P1-4]

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" key.
        meta: Schema metadata.

    Returns:
        Check named "seasonal_{col}" with passed=True (not yet implemented).
    """
    return Check(
        name=f"seasonal_{pattern['col']}",
        passed=True,
        detail="seasonal_anomaly validation not yet implemented",
    )
```

### 规范引用
- §2.1.2 (L127):`"seasonal_anomaly"` 列于 `PATTERN_TYPES`。
- §2.5 (L305):LLM prompt 中允许的 pattern 类型列表包含
  `"seasonal_anomaly"`。
- §2.9 L3 (L644–677):无伪代码或算法 —— L3 pattern 校验伪代码中缺席。

### 既有测试
- (未发现)

### 依赖 stub
- (无直接;同 IS-2 的 DS-2 链。)

### 在管道中的角色
与 IS-2/IS-3 相同 —— §2.9 L3 pattern 校验,在引擎与 pattern 注入之后。
特别注意:此检查仅在 `add_temporal()` 被调用过的场景下才有意义,因此
对 schema metadata 中存在时间列存在隐式依赖。

### 缺口分析
- **规范定义:** §2.1.2 L127 在 PATTERN_TYPES 列出 `"seasonal_anomaly"`;
  §2.5 L305 在 prompt 中列出。
- **规范沉默:** §2.9 L3 没有 seasonal_anomaly 的伪代码。没有 params
  契约(周期?异常窗口?幅值阈值?),没有检测方法(STL 残差?去趋势
  序列上的 z-score?),没有当场景中存在多个时间列时如何解析的规则。
  规范也不要求声明 seasonal_anomaly 时必须存在时间列 —— 在无时间列的
  场景中声明会成功,但检查毫无意义。
- **实现缺口:** stub 返回 `passed=True`。实现需要 (a) 周期推断或声明、
  (b) 异常窗口契约、(c) 检测度量、(d) 通过阈值、(e) 时间列存在性的
  前置检查。(a)–(d) 需规范输入。

### 依赖链
- **阻塞:** 直接无。
- **被以下阻塞:** 规范扩展定义 seasonal_anomaly + params + 时间依赖
  契约;**DS-2** 提供注入侧;场景中存在 `add_temporal` 才能运行此
  检查。
- **共依赖于:** DS-2 —— 注入器与校验器必须共享同一运算定义。

### 阻塞性问题
- **规范:** "seasonal anomaly" 的运算定义。候选:(a) 在显式
  `anomaly_window` 内的值偏离窗外基线;(b) STL 分解后残差异常值;
  (c) 去趋势序列上的周期感知 z-score。(a) 最简单且与 `inject_pattern`
  叙事驱动的框架一致。
- **规范:** params 契约 —— `anomaly_window=[start, end]` 是必填,
  还是可推断(例如时间范围最后 10%)?
- **规范:** 通过阈值 —— 合理默认 z ≥ 1.5。

### 提议方案
选解读 (a)。镜像 `check_outlier_entity` 的窗口对基线 z-score 逻辑;
复用 `_find_temporal_column`。

```python
# pipeline/phase_2/validation/pattern_checks.py — replace stub at L242-265.

def check_seasonal_anomaly(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Seasonal anomaly — anomaly_window mean deviates from baseline.

    Algorithm (interpretation (a)):
      1. Resolve temporal_col.
      2. Get anomaly_window=[start, end] from params, or default to
         last 10% of temporal range.
      3. Compute baseline mean+std from out-of-window rows.
      4. z = |window_mean - baseline_mean| / baseline_std.
      5. Pass if z >= params.get("z_threshold", 1.5).
    """
    col = pattern["col"]
    params = pattern.get("params", {})
    z_threshold = params.get("z_threshold", 1.5)
    name = f"seasonal_{col}"

    temporal_col = _find_temporal_column(meta)
    if temporal_col is None:
        return Check(name=name, passed=False, detail="No temporal column.")

    tval = pd.to_datetime(df[temporal_col], errors="coerce")
    window = params.get("anomaly_window")
    if window:
        win_start, win_end = pd.to_datetime(window[0]), pd.to_datetime(window[1])
    else:
        tmin, tmax = tval.min(), tval.max()
        win_start, win_end = tmin + (tmax - tmin) * 0.9, tmax

    in_window = (tval >= win_start) & (tval <= win_end)
    win_vals = df.loc[in_window, col]
    base_vals = df.loc[~in_window, col]

    if len(win_vals) == 0 or len(base_vals) < 2:
        return Check(name=name, passed=False,
                     detail=f"Insufficient rows: window={len(win_vals)}, baseline={len(base_vals)}.")

    base_mean, base_std = float(base_vals.mean()), float(base_vals.std())
    if base_std == 0:
        return Check(name=name, passed=False, detail="Baseline std is 0.")

    win_mean = float(win_vals.mean())
    z = abs(win_mean - base_mean) / base_std
    passed = bool(z >= z_threshold)
    return Check(
        name=name, passed=passed,
        detail=f"win_mean={win_mean:.4f}, base_mean={base_mean:.4f}, z={z:.3f} (threshold={z_threshold})",
    )
```

**集成点:**
- 与 IS-2/IS-3 相同的分发接线;仅改变函数体。
- 复用 `_find_temporal_column`。

**新类型:** 无。

### 测试标准
- 窗口均值上升 → passed=True。
- 窗口均值与基线相当 → passed=False。
- 空窗口 → 优雅失败。
- 缺失时间列 → 优雅失败。
- 常量列 → 优雅失败。

### 估算规模
**Small (20–80 LOC)。** 函数体 ≈ 45 LOC + 测试 ≈ 50 LOC ≈ 95 LOC。
类比:`check_outlier_entity` 函数体 ~70 LOC。

---

## [IS-5] `add_measure` 的 `scale` 关键字参数

### 代码片段(SDK —— kwarg 已移除)
```python
# pipeline/phase_2/sdk/columns.py:214-250
# TODO [M?-NC-scale]: restore `scale` kwarg when a scaling implementation lands.
# Previously `scale` was accepted but silently no-op, which misled LLMs into
# tuning a knob that did nothing. Removed so Python raises a clear TypeError
# if callers still pass it.
def add_measure(
    columns: OrderedDict[str, dict[str, Any]],
    name: str,
    family: str,
    param_model: dict[str, Any],
) -> None:
    """Declare a stochastic measure column.

    [Subtask 1.4.1–1.4.3]

    Args:
        columns: Column registry (mutated in place).
        name: Measure column name.
        family: Distribution family string.
        param_model: Distribution parameters dict.
    """
    _val.validate_column_name(name, columns)
    _val.validate_family(family)
    _val.validate_param_model(name, family, param_model, columns)

    col_meta: dict[str, Any] = {
        "type": "measure",
        "measure_type": "stochastic",
        "family": family,
        "param_model": dict(param_model),
    }

    columns[name] = col_meta

    logger.debug(
        "add_measure: stochastic '%s' (family='%s') registered.",
        name, family,
    )
```

### 代码片段(orchestration —— prompt 不再记录 `scale`)
```python
# pipeline/phase_2/orchestration/prompt.py:53-54
# TODO [M?-NC-scale]: re-add `scale=None` kwarg when sdk/columns.py::add_measure implements it.
"  sim.add_measure(name, family, param_model)\n"
# (Lines L55-60 below describe param_model schema per family — unrelated to scale.)
```

### 规范引用
- §2.1.1 (L51):在签名行中列出
  `add_measure(name, family, param_model, scale=None)`。后文(
  "Stochastic root measure. Sampled from a named distribution.
  Parameters may vary by categorical context …")描述了该方法,但
  **没有解释 `scale=` 的含义**。§2.1.1 或 §2.3 任何位置都没有
  log/linear/post-transform 解释 —— 这个 kwarg 仅有签名,无语义。
- §2.5 (L287):Prompt 模板的 AVAILABLE SDK METHODS 段显示
  `sim.add_measure(name, family, param_model, scale=None)` —— 同样的
  签名行,无行为描述。实时 `prompt.py`(L53-54)不再发送 `scale` kwarg。
- **Spec/prompt/SDK 状态:** 规范保留了一行无语义的残余签名;实时 prompt
  与实时 SDK 都已移除。规范并未对 SDK 提出任何**行为**主张 —— 只是一个
  语义为空的 ghost kwarg。

### 既有测试
- `tests/modular/test_sdk_columns.py::TestAddMeasure::test_add_measure_rejects_scale_kwarg`
  —— 验证传入 `scale=` 抛 `TypeError`(刻意为之:缺失的 kwarg 在 LLM
  重试循环中产生干净的错误)。
- `tests/modular/test_sdk_columns.py::TestAddMeasure::test_add_stochastic_measure`
  —— 确认 `scale` 不被存入 column metadata。

### 依赖 stub
- (无)

### 在管道中的角色
本意是 §2.1.1 声明步骤上随机 measure 的参数,但规范只在签名中列出
该 kwarg 而从未记录其语义。当前**不在**实时 SDK 中:`add_measure`
以 `TypeError` 拒绝该 kwarg,实时
[orchestration/prompt.py](pipeline/phase_2/orchestration/prompt.py)
L53-54 也从对外 API 文档中省略了 `scale=None`。规范 §2.5 L287 在签名
行仍展示该 kwarg。净效应:**spec、prompt、SDK 已统一为 `scale` 不带
任何行为** —— 但规范保留了一行残余签名作为该参数唯一剩余的提及。这
更像"ghost kwarg",而不是三个文档中的相互竞争主张。

### 缺口分析
- **规范定义:** §2.1.1 L51 列出
  `add_measure(name, family, param_model, scale=None)`;§2.5 L287
  在 prompt 模板中记录相同。规范将 `scale` 表述为通用可选提示,
  无运算语义或示例 —— 整个规范中没有 `scale != None` 的任何使用。
- **规范沉默:** `scale` 实际做什么 —— 是按族枚举提示(例如
  `"log_scale"` 用于 lognormal `mu` 解释)、采样后变换、还是表示
  辅助。移除前的实现接受该 kwarg 但从不读取,因此该特性在任何版本
  中都从未有过行为。
- **实现缺口:** kwarg 已移除,通过清晰的 `TypeError` 让意外的 LLM
  使用快速失败(良好的防御选择)。要恢复:(a) 决定 `scale` 含义、
  (b) 在 `_compute_per_row_params` 中按定义解释 `mu`/`sigma`、
  (c) 在 §2.1.1 中加示例、(d) 重新加入 `prompt.py:53-54`。在 (a)
  解决之前,"缺失 + TypeError"是正确行为。

### 依赖链
- **阻塞:** 清单中无其他项。
- **被以下阻塞:** 规范的**新增**(而非"扩展")定义 `scale=` 的含义。
  规范今天没有任何行为主张 —— 这是一个为其增加语义的请求,而不是
  澄清既有语义。
- **共依赖于:** 三个残余提及 —— 规范 §2.1.1 L51 签名、规范 §2.5 L287
  签名、以及(若恢复)实时 `prompt.py:53-54` —— 必须一起对齐。

### 阻塞性问题
- **规范(提议而非解读):** 由于规范对 `scale=` 没有行为内容,*任何*
  含义都将是新提议而非对既有文本的阅读。两个候选提议:
  (a) 按族枚举提示(`scale="log"` → mu 在对数尺度;`scale="linear"`
  → mu 在自然尺度);(b) 应用于采样值的采样后变换。两者都未被规范
  prose 支持;两者都是新设计。
- **架构:** 鉴于 lognormal 通过族选择已经编码了对数尺度,而
  gaussian/gamma/beta 各有其自然尺度,恢复 `scale` 是否真的有用?
  恢复一个没有行为却带来混淆的参数有风险。

### 提议方案
**推荐:不要恢复该 kwarg。** 由于规范从未声明 `scale` 的作用,从规范
中删除它没有任何损失 —— 没有行为主张可以丢失。从 §2.1.1 L51 与
§2.5 L287 中剥离 `scale=None`,让 spec、prompt、SDK 一致地省略此
kwarg。当前"缺失 + TypeError"是最安全状态,与 M?-NC-scale TODO 的
"在 scaling 实现落地后恢复"一致(即:实现应驱动规范,而非反之)。

如果必须恢复,最小安全路径是按解读 (a) 作为按族提示:

```python
# sdk/columns.py::add_measure — minimal restoration sketch
def add_measure(
    columns: OrderedDict[str, dict[str, Any]],
    name: str,
    family: str,
    param_model: dict[str, Any],
    scale: Optional[str] = None,  # one of "linear", "log", or None
) -> None:
    if scale is not None and scale not in ("linear", "log"):
        raise ValueError(f"scale must be 'linear', 'log', or None; got {scale!r}.")
    # Most families ignore scale (already encode it); only lognormal /
    # exponential interpret it as a hint about whether mu is on the log
    # scale or natural scale.
    col_meta["scale"] = scale
```

但行为接线(在 `_compute_per_row_params` 与 L2 的 `_expected_cdf` 中
消费 `scale`)并不平凡 —— 而规范不给示例,所以每个族的解释无文档
依据。

**集成点(若恢复):**
- `sdk/columns.py::add_measure` —— 重新加入 kwarg + 校验。
- `engine/measures.py::_compute_per_row_params` —— 按族解释提示
  (大多忽略)。
- `validation/statistical.py::_expected_cdf` —— 与采样侧的解释一致,
  以保持 KS 检验一致。
- `orchestration/prompt.py:53-54` —— 重新加入 `scale=None` 文档。

**新类型:** 无。

### 测试标准
- **若保持缺失(推荐):** 既有
  `test_add_measure_rejects_scale_kwarg` 继续验证 TypeError;新增
  docs/spec 审计测试,断言 `prompt.py` 与规范(§2.5)记录相同的参数列表。
- **若恢复:** 往返测试 `scale="log"` + lognormal `mu` 与
  `log(samples)` 上无 scale 的 gaussian 一致;`scale="invalid"` 的
  拒绝测试。

### 估算规模
**Trivial (<20 LOC) 推荐路径** —— 从规范 L51 与 §2.5 L287 中剥离
`scale=None`(仅文档)。**Small (20–80 LOC) 作为枚举提示恢复** ——
kwarg + 校验 + 按族接线 + 测试。

---

## [IS-6] M3 多错误 + token 预算

### 代码片段(sdk/simulator.py —— 能力缺失,而非 raise-stub)
```python
# pipeline/phase_2/sdk/simulator.py:32-36
# TODO [M3-NC-3]: The sandbox currently catches one error at a time.
# Multiple simultaneous SDK validation errors (e.g. two bad effects +
# a cycle) are surfaced one per retry attempt. A future enhancement
# could collect all validation errors in a single pass and relay them
# as a batch to reduce retry iterations.
```

### 代码片段(orchestration/sandbox.py —— 引用位置,重试尝试)
```python
# pipeline/phase_2/orchestration/sandbox.py:~657
# (Sandbox attempt loop — single-error capture, no token-budget tracker.
#  No NotImplementedError; the "stub" is the absence of a multi-error
#  collector and a token-budget guard around the retry loop.)
```
(注:这是文档化的*能力缺口*,而非 `NotImplementedError` 块。上面的
TODO 是源码中唯一的标记。)

### 规范引用
- §2.7 (L485–503):Execution-Error Feedback Loop 描述了步骤 4(
  "FAILURE → SDK raises typed exception")与步骤 5(
  "Code + traceback fed back to LLM")。当前每次重试浮现一个错误;
  多错误批处理在 M3 增强中提及。
- (规范中没有 token 预算机制 —— 这是实现侧的护栏,而非规范特性。)

### 既有测试
- `tests/test_retry_feedback.py` —— 验证单错误重试反馈;无测试验证
  多错误收集(特性尚未存在)。
- (未发现 token 预算测试)

### 依赖 stub
- (无)

### 在管道中的角色
位于 Loop A(§2.7),具体在
[orchestration/sandbox.py](pipeline/phase_2/orchestration/sandbox.py)
中 `run_with_retries` 的 L689 附近(重试循环)。上游:沙盒失败(SDK
或运行时的 typed exception)。下游:异常/traceback 反馈给 LLM 并重试,
封顶 `max_retries=3`。当前每次尝试浮现一个错误;若 LLM 脚本同时存在
3 个错误(cycle + bad effect + non-root dep),需 3 次尝试才能逐一
找出。也没有 token 预算 —— 包含冗长 traceback 的脚本可能炸掉重试
上下文。

### 缺口分析
- **规范定义:** §2.7 L485-503 用 typed exception 示例记录反馈循环;
  步骤 4 说 "SDK raises typed exception"(单数);步骤 6 说
  "Retry (max_retries=3). If all fail → log and skip."
- **规范沉默:** §2.7 中没有错误批处理 —— 多错误收集是实现侧优化。
  Token 预算完全不在规范中 —— 也是操作性而非规范特性。
- **实现缺口:** 没有 `NotImplementedError` 标记 —— 这是**能力缺失**,
  而非 stub raise。两个独立子特性:
  (1) **多错误收集** —— 需要 SDK 校验器在第一个错误后继续(catch-all
  + accumulate),然后浮现一个列表。这在 `sdk/columns.py`、
  `sdk/relationships.py` 与内部校验工具中都需要重大重构,因为它们
  目前都在第一次失败就 raise。
  (2) **Token 预算** —— 在重试循环外加跟踪器,按尝试计数 prompt +
  completion tokens,在预算耗尽时提前跳过;与 `LLMClient` 接口交叉
  以获取 token 数。

### 依赖链
- **阻塞:** 清单中无(纯优化)。
- **被以下阻塞:** 架构决策(多错误模式让 LLM 困惑还是受益?);
  `LLMClient` API 暴露 token 数(目前每个 provider 不同)。
- **共依赖于:** 清单中无;两个子特性(多错误与 token 预算)独立,
  可分开发布。

### 阻塞性问题
- **架构:** 多错误反馈对 LLM 是助益还是困惑?这是经验问题 —— 较小/
  较老的模型在多错误 prompt 上常会退化;有能力的模型则受益。在将
  特性默认开启之前需要 A/B 测试。
- **架构:** token 预算是按尝试还是按场景?按场景更有用,但需要
  重试循环串接累积跟踪器。
- **操作:** 预算如何从 `LLMClient` 读取 token 数?当前 `LLMClient`
  接口因 provider 而异 —— 可能需要一个薄的 `TokenUsage` 适配器。

### 提议方案
两个独立子特性;分开发布。建议先发布 (2) token 预算 —— 影响范围更小,
不需要 SDK 重构。

**(1) 多错误收集。** 加入一个可选的 `ValidationContext`,SDK 校验器
调用它而不是裸 `raise`:

```python
# pipeline/phase_2/sdk/validation.py — new helper

class ValidationContext:
    """Context for collecting validation errors instead of raising.

    Used by sdk validators when sandbox.run_with_retries opts into
    multi-error mode. Falls back to raise-on-first when not opted in,
    preserving current behavior.
    """
    def __init__(self, accumulate: bool = False):
        self.accumulate = accumulate
        self.errors: list[Exception] = []

    def report(self, exc: Exception) -> None:
        if self.accumulate:
            self.errors.append(exc)
        else:
            raise exc

    def raise_if_any(self) -> None:
        if self.errors:
            raise MultiValidationError(self.errors)


# orchestration/sandbox.py::run_with_retries — opt-in flag
def run_with_retries(
    initial_code: str,
    ...,
    multi_error: bool = False,
) -> RetryLoopResult:
    for attempt in range(1, max_retries + 1):
        ctx = ValidationContext(accumulate=multi_error)
        result = execute_in_sandbox(current_code, ..., validation_ctx=ctx)
        if result.success:
            return ...
        # Surface ALL collected errors at once
        all_errors = ctx.errors or [result.exception]
        feedback = format_multi_error_feedback(all_errors)
        current_code = llm_generate_fn(system_prompt, feedback)
```

**(2) Token 预算。** 在重试循环中接入计数器:

```python
# orchestration/sandbox.py::run_with_retries — token-budget guard

def run_with_retries(
    initial_code: str,
    llm_generate_fn: Callable[[str, str], LLMResponse],
    ...,
    token_budget: int | None = None,
) -> RetryLoopResult:
    tokens_used = 0
    for attempt in range(1, max_retries + 1):
        ...
        if isinstance(response, LLMResponse) and response.token_usage:
            tokens_used += response.token_usage.total_tokens
        if token_budget and tokens_used >= token_budget:
            return RetryLoopResult(
                success=False,
                history=history,
                skipped_reason=f"token_budget_exceeded ({tokens_used}/{token_budget})",
            )
```

**集成点:**
- `sdk/columns.py`、`sdk/relationships.py`、`sdk/dag.py`、
  `sdk/validation.py` —— 把每个 `raise` 点改成 `ctx.report(exc)`(仅
  多错误模式;~10 个 raise 点)。
- `orchestration/sandbox.py::run_with_retries`(~L689)—— 增加
  `multi_error` 与 `token_budget` 标志。
- `orchestration/llm_client.py::LLMClient.generate_code` —— 返回携带
  `token_usage` 的结构化 `LLMResponse`(目前返回原始字符串)。
- `exceptions.py` —— 新增 `MultiValidationError(list[Exception])`。

**新类型:**
- `ValidationContext`,位于 `sdk/validation.py`。
- `MultiValidationError`,位于 `exceptions.py`。
- `LLMResponse(NamedTuple)` 与 `TokenUsage(NamedTuple)`,位于
  `orchestration/llm_client.py`。

### 测试标准
- **多错误:** 同时含 3 个 SDK 错误的脚本 → 一次重试,反馈中含 3 个
  错误(对比当前的 3 次尝试)。
- **多错误:** 含 1 个错误的脚本 → 与当前行为一致(向后兼容)。
- **Token 预算:** 命中预算时重试循环提前终止;返回带
  `token_budget_exceeded` 原因的 `SkipResult`。
- **Token 预算:** 默认 `None` → 行为不变。
- **Provider 兼容:** 不返回 token 数的 mock `LLMClient` → 预算特性
  优雅降级(计为 0)。

### 估算规模
**Large (200+ LOC)。** 仅多错误就涉及 `sdk/*.py` 中的 ~10 个 raise
点(~10 LOC × 10 = 100 LOC),加上 `ValidationContext` + 新异常
(~30 LOC),加 sandbox 接线(~30 LOC),加测试(~80 LOC)≈ 240 LOC。
Token 预算再加 ~60 LOC + LLMClient 响应重构 + 测试 ≈ 100 LOC。合计
≈ 340 LOC。两半可作为独立 PR 发布。

---

# 依赖 stub(4 个)

## [DS-1] 截断(Censoring)注入

### 代码片段
```python
# pipeline/phase_2/engine/realism.py:57-63
censoring = realism_config.get("censoring")
if censoring is not None:
    # TODO [M1-NC-7]: Censoring injection deferred.
    raise NotImplementedError(
        "Censoring injection not yet implemented. "
        "See stage3 item M1-NC-7."
    )
```

### 规范引用
- §2.1.2 (L129):`set_realism(missing_rate, dirty_rate, censoring)`
  将 censoring 声明为可选 realism-config 键。
- §2.8 (L532–534):确定性引擎执行计划将 δ(realism)展示为最后的可选
  pipeline 阶段;censoring 是与 missing 值、dirty 值并列的三个组件之一。

### 既有测试
- (未发现)

### 依赖 stub
- (无 —— DS-1 自身就是叶依赖 stub;父项是规范定义。)

### 在管道中的角色
位于 §2.8 step δ(realism,可选)—— 在 pattern 注入*之后*,在完整
DataFrame 上运行。上游:`set_realism(censoring=...)` 提供的
`realism_config` 字典。下游:写入返回给 Phase 3 的 Master DataFrame。
仅在 `censoring is not None` 时触发;否则 realism 阶段仅运行 missing
/dirty 注入。

**Prompt 侧屏蔽(重要):** 虽然
[sdk/relationships.py::set_realism](pipeline/phase_2/sdk/relationships.py#L281)
仍接受 `censoring=None`,实时 LLM prompt
[orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71)
**已不再宣告该 kwarg** —— 现在显示
`sim.set_realism(missing_rate, dirty_rate)`,并附 TODO 注释标记
`censoring=` 已延期。这与 DS-2 中 4 个延期 pattern 的"双重屏蔽"模式
完全相同:SDK 接受它(老脚本不会在 import 时崩溃),但 LLM 在常规流程
中永远不会看到。实际上,引擎的 `NotImplementedError` 分支在今天任何
prompt 驱动生成中都不可达。

### 缺口分析
- **规范定义:** §2.1.2 L129 声明
  `set_realism(missing_rate, dirty_rate, censoring)`,`censoring`
  为可选参数;§2.8 L532-534 注释列出 δ 包含 "censoring"。
- **规范沉默:** censoring schema —— 没有参数形状(在某值处右截断?
  左?区间?按列还是全局?阈值还是比率?),没有示例,没有算法。
  Missing/dirty 都有按比率的参数契约;censoring 没有。
- **实现缺口:** 任何非 None censoring 传入即抛 `NotImplementedError`。
  实现需要 (a) 定义 censoring 配置 schema(可能是
  `{col, type: right|left|interval, threshold, ...}` 列表)、
  (b) 实现把超过阈值的值用 censoring 标记(NaN?哨兵值?独立指示
  列?)替换的 DataFrame 变换、(c) 决定与 missing 值注入的交互
  (优先级)。三者都需要规范输入。

### 依赖链
- **阻塞:** 无 —— DS-1 是叶。
- **被以下阻塞:** 规范扩展定义 censoring 的参数 schema 与标记语义;
  censoring 是否产生独立指示列的决策(Phase 3 视图抽取需要知道)。
- **共依赖于:** missing 值注入顺序(被 censored 的单元是否还能被
  NaN'd)—— 但 missing 注入本身已实现,不是另一个 stub。也共依赖于
  `prompt.py:70-71` 与 One-Shot Example,它们今天都省略了
  `censoring=`,任何恢复都必须一并更新。因此恢复成本是
  **(a) 定义规范 schema + (b) 实现引擎 + (c) 在 prompt 中重新宣告 +
  (d) 更新 One-Shot Example**,而不只是 (a)+(b)。

### 阻塞性问题
- **规范:** `censoring` 配置的 schema。对既有
  `set_realism(missing_rate, dirty_rate, censoring)` 签名最自然的
  扩展是按列字典
  `{col: {"type": "right"|"left"|"interval", "threshold": ...}}`,
  但规范未定义此形状。
- **规范:** 标记语义。三选项:(a) 把被 censored 的值替换为 NaN(丢失
  censoring 信息,简单)、(b) 兄弟指示列 `<col>_censored`(保留信息
  但列数翻倍,改变 schema)、(c) 哨兵值(如 `inf` / `-inf` —— 脆弱、
  依赖族)。Phase 3 视图抽取需要知道是哪一种。
- **规范:** 与 missing 值注入的顺序 —— censoring 在前还是在后?在后
  则被 censored 的单元可能已被 NaN'd。在前则 missing 比率的分母不同。

### 提议方案
选 schema (a) 按列字典、标记 (a) NaN 替换、顺序"censoring 在 missing
之前"(让 missing 比率基于 censoring 之后的分布计算)。结构上镜像
`inject_missing_values` / `inject_dirty_values`。

```python
# pipeline/phase_2/engine/realism.py — replace NotImplementedError block at L57-63.

def inject_censoring(
    df: pd.DataFrame,
    censoring_config: dict[str, dict[str, Any]],
    rng: np.random.Generator,  # unused but kept for signature symmetry
) -> pd.DataFrame:
    """Inject censoring on declared measure columns.

    Schema:
        censoring_config = {
            "wait_minutes": {"type": "right", "threshold": 100.0},
            "cost":         {"type": "left",  "threshold": 50.0},
            "score":        {"type": "interval", "low": 0.0, "high": 10.0},
        }

    For "right": values > threshold become NaN.
    For "left":  values < threshold become NaN.
    For "interval": values outside [low, high] become NaN.
    """
    if not censoring_config:
        return df

    total_censored = 0
    for col, spec in censoring_config.items():
        if col not in df.columns:
            logger.warning(
                "inject_censoring: column '%s' not in DataFrame; skipping.", col,
            )
            continue
        c_type = spec["type"]
        if c_type == "right":
            mask = df[col] > spec["threshold"]
        elif c_type == "left":
            mask = df[col] < spec["threshold"]
        elif c_type == "interval":
            mask = (df[col] < spec["low"]) | (df[col] > spec["high"])
        else:
            raise ValueError(
                f"Unknown censoring type '{c_type}' for column '{col}'. "
                f"Expected one of: right, left, interval."
            )
        df.loc[mask, col] = np.nan
        total_censored += int(mask.sum())

    logger.debug(
        "inject_censoring: censored %d cells across %d columns.",
        total_censored, len(censoring_config),
    )
    return df


# In inject_realism, replace the NotImplementedError branch with:
censoring = realism_config.get("censoring")
if censoring:
    df = inject_censoring(df, censoring, rng)
# (Run BEFORE missing/dirty so missing-rate is on the post-censor distribution.)
```

**集成点:**
- `engine/realism.py::inject_realism`([L25-65](pipeline/phase_2/engine/realism.py#L25-L65))
  —— 替换 NotImplementedError 分支并重新排序,使 censoring 先运行。
- `sdk/relationships.py::set_realism` 已接受 `censoring` —— 升级
  参数校验以断言新 schema(按列字典,`type` ∈ {right, left, interval}
  且 `threshold` 或 `low`/`high`)。

**新类型:** `types.py` 中的可选 `CensoringSpec(TypedDict)`:

```python
class CensoringSpec(TypedDict, total=False):
    type: Literal["right", "left", "interval"]
    threshold: float
    low: float
    high: float
```

### 测试标准
- 右截断:超过阈值的值变 NaN,其余不变。
- 左截断:对称。
- 区间:仅范围外的值被 NaN'd。
- 缺失列:警告并跳过,任何位置都不注入 NaN。
- 空配置(`{}`):no-op。
- 未知 `type`:ValueError 含清晰信息。
- 顺序:missing_rate 基于 censoring 后分布计算(由行计数验证)。

### 估算规模
**Small (20–80 LOC)。** 函数体 ≈ 35 LOC + `set_realism` schema 校验
≈ 20 LOC + 可选 TypedDict ≈ 5 LOC + 测试 ≈ 50 LOC ≈ 110 LOC 总计。
类比:`inject_missing_values` ~30 LOC,`inject_dirty_values` ~60 LOC。

---

## [DS-2] 4 种 pattern 类型注入

### 代码片段
```python
# pipeline/phase_2/engine/patterns.py:61-71
elif pattern_type in (
    "ranking_reversal",
    "dominance_shift",
    "convergence",
    "seasonal_anomaly",
):
    # TODO [M1-NC-6]: Pattern injection for these types is deferred.
    raise NotImplementedError(
        f"Pattern type '{pattern_type}' injection not yet implemented. "
        f"See stage3 item M1-NC-6."
    )
```

### 规范引用
- §2.1.2 (L119–127):`inject_pattern(type, target, col, params)` 声明
  6 个 pattern 类型:`outlier_entity`、`trend_break`、
  `ranking_reversal`、`dominance_shift`、`convergence`、
  `seasonal_anomaly`。当前仅前两个有具体注入算法。
- §2.8 (L529–530):γ(pattern 注入)是确定性引擎执行的第 3 阶段 ——
  对 post-measure DataFrame 应用声明的 patterns。
- §2.9 (L644–676):L3 pattern 校验伪代码引用了 `outlier_entity`、
  `ranking_reversal`、`trend_break`、`dominance_shift`(convergence
  与 seasonal_anomaly 不在 L3 草图中)。

### 既有测试
- `tests/modular/test_validation_validator.py::test_validates_l3_layer_with_patterns`
  —— 仅在提供*已实现*的 pattern 类型(`outlier_entity`、
  `trend_break`)时执行 L3 检查。
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_amplifies_z_score_on_matching_pattern`
  —— outlier z_score 的 auto-fix 放大(仅已实现类型)。
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_amplifies_magnitude_on_matching_pattern`
  —— trend_break magnitude 的 auto-fix 放大。
- `tests/modular/test_validation_autofix.py::TestAmplifyMagnitude::test_skips_non_matching_patterns`
  —— auto-fix 仅更新匹配的 pattern 列。
- (无测试触及 4 个延期 pattern 类型的注入。)

### 依赖 stub
- IS-2:Dominance shift 校验 —— `validation/pattern_checks.py:189-213`
- IS-3:Convergence 校验 —— `validation/pattern_checks.py:216-239`
- IS-4:Seasonal anomaly 校验 —— `validation/pattern_checks.py:242-265`
  (这三个 L3 检查在 DS-2 落地之前无法端到端运行 —— 注入正是产生它们
  要校验的数据的源头。)

### 在管道中的角色
位于 §2.8 step γ(pattern 注入),在
[engine/patterns.py](pipeline/phase_2/engine/patterns.py)::`inject_patterns`
中。接收 post-measure DataFrame 与 patterns 列表,按 `pattern_type`
分发。上游:来自 `sim.inject_pattern(type, target, col, params)` 的
pattern 规格。下游:被 realism (δ) 与校验(§2.9 L3)消费的变更后
DataFrame。**当前 SDK 与 prompt 都被屏蔽到只剩 2 种类型** ——
[sdk/relationships.py:29](pipeline/phase_2/sdk/relationships.py#L29)
`VALID_PATTERN_TYPES = {"outlier_entity", "trend_break"}`,
[orchestration/prompt.py:72](pipeline/phase_2/orchestration/prompt.py#L72)
仅宣告这 2 种 —— 因此引擎中 4 个延期类型的 `NotImplementedError`
分支当前是**死的防御代码**。规范文本(§2.5 L304-305)是唯一仍列出
全部 6 种的文档。

### 缺口分析
- **规范定义:** §2.1.2 L119-127 列出全部 6 种 PATTERN_TYPES;
  §2.5 L304-305 在规范的 prompt 模板中列出全部 6 种;§2.8 step γ
  说明应用 patterns;§2.9 L3 仅对 `dominance_shift` 有部分校验草图
  (任何位置都没有注入算法)。
- **规范沉默:** 4 种类型的注入算法。`ranking_reversal` 的 L3 校验
  度量已草绘(§2.9 L655-661 中两个 metric 的秩相关),但没有任何
  关于如何*诱发*反转的内容。`dominance_shift`、`convergence`、
  `seasonal_anomaly` 规范仅说它们是合法类型名。无 params、无算法、
  无示例。
- **实现缺口:** 4 种类型在声明期(SDK 以 ValueError 拒绝)与 prompt
  级(LLM 永远看不到)都被**双重屏蔽**,因此引擎的
  `NotImplementedError` 实际上不可达。恢复需 (a) 更新
  `VALID_PATTERN_TYPES` 与 `PATTERN_REQUIRED_PARAMS`、(b) 更新
  `prompt.py:72`(以及 One-Shot 示例)、(c) 在 `engine/patterns.py`
  中实现四个独立注入算法、(d) 确保配套 L3 校验器(IS-2/3/4)同步发布。
  注意:`ranking_reversal` 校验器
  ([validation/pattern_checks.py::check_ranking_reversal](pipeline/phase_2/validation/pattern_checks.py))
  已经完整实现,但目前不可达。

### 依赖链
- **阻塞(实现后):** 端到端运行 IS-2(dominance_shift 校验)、
  IS-3(convergence 校验)、IS-4(seasonal_anomaly 校验);也消除
  LLM 选择"声明合法但无法实现"pattern 类型时的静默失败。
- **被以下阻塞:** 4 种 pattern 类型各自的规范扩展(params 契约 +
  注入算法 + 适用场景下的配套校验算法);`ranking_reversal` 有部分
  规范覆盖(校验器已定义、注入器未定义),需决定是否一并规范注入器。
- **共依赖于:** IS-2、IS-3、IS-4 —— 每个 `(注入器, 校验器)` 对必须
  共享同一运算定义。也共依赖于 `prompt.py:72` 与
  `VALID_PATTERN_TYPES` —— 它们当前屏蔽到只剩 2 种已实现类型,任何
  新注入器必须与 prompt 与 SDK 屏蔽更新一起发布。

### 阻塞性问题
- **规范:** 4 种类型各自的运算注入算法。每个必须与对应 L3 校验器
  (IS-2/IS-3/IS-4)以及既有 `check_ranking_reversal` 一致。没有这些
  定义,自由度太大。
- **路线图:** 一次发布全部 4 种,还是渐进?`ranking_reversal` 已有
  可用校验器,是最容易的首选目标;`seasonal_anomaly`(窗口尖峰)与
  `dominance_shift`(切分后偏移)在机制上类似 `trend_break`;
  `convergence` 最新颖。
- **规范:** `ranking_reversal` 的规范仅覆盖校验器 —— 注入器契约
  缺失。

### 提议方案
按类型给出草图,各自镜像 `inject_outlier_entity` / `inject_trend_break`
模式。每个函数遵循相同模板:`target_mask = df.eval(pattern["target"])`、
验证非空、退化时抛 `PatternInjectionError`、成功时记日志。

```python
# pipeline/phase_2/engine/patterns.py — replace the 4-way NotImplementedError
# branch at L61-71 with explicit dispatch.

def inject_ranking_reversal(df, pattern, columns, meta):
    """Reverse rank order between two metrics at the *entity-mean* level.

    The verifier (check_ranking_reversal) groups by entity, takes per-
    entity means of m1 and m2, and checks rank correlation < 0. To
    reliably trigger that, the injector must operate at the entity-mean
    level — a row-level pairing of high-m1 with low-m2 is a heuristic
    that may not always shift group means (especially when entities have
    similar m1 distributions). The reliable algorithm:
      1. Group target rows by entity_col.
      2. Rank entities ascending by mean(m1) → rank_m1.
      3. Compute desired mean(m2) per entity by *reversing* rank_m1
         relative to the global mean(m2) distribution.
      4. Per entity, additively shift m2 values so the entity mean lands
         at the desired position (preserving within-entity variance).
    Pairs naturally with check_ranking_reversal (Spearman corr < 0).
    """
    m1, m2 = pattern["params"]["metrics"]
    entity_col = pattern["params"].get("entity_col") or _resolve_first_dim_root(meta)
    target_mask = df.eval(pattern["target"])
    if target_mask.sum() < 2 or entity_col is None:
        raise PatternInjectionError(pattern_type="ranking_reversal", ...)
    target_df = df.loc[target_mask]
    entity_means_m1 = target_df.groupby(entity_col)[m1].mean()
    entity_means_m2 = target_df.groupby(entity_col)[m2].mean()
    # Rank reverse: entity with highest m1 gets lowest m2 mean target
    rank_m1 = entity_means_m1.rank(ascending=True)
    sorted_m2 = entity_means_m2.sort_values(ascending=False).values
    desired_m2 = pd.Series(sorted_m2, index=rank_m1.sort_values().index)
    # Apply additive per-entity shift
    for entity, desired in desired_m2.items():
        rows_e = target_mask & (df[entity_col] == entity)
        shift = desired - df.loc[rows_e, m2].mean()
        df.loc[rows_e, m2] = df.loc[rows_e, m2] + shift
    return df


def inject_dominance_shift(df, pattern, columns):
    """Shift target subset's pattern["col"] post-split_point so the
    target_entity's mean exceeds its peers'."""
    # Resolve temporal_col (mirror inject_trend_break L189-194)
    # Compute peer_max from non-target rows (post-split)
    # post_split = target_mask & (temporal >= split_point)
    # shift = peer_max + magnitude * peer_std - df.loc[post_split, col].mean()
    # df.loc[post_split, col] += shift
    return df


def inject_convergence(df, pattern, columns):
    """Pull target rows toward global_mean as time progresses; magnitude
    grows linearly with normalized time within the target window."""
    # tval = pd.to_datetime(df[temporal_col])
    # tmin, tmax = tval.min(), tval.max()
    # for each target row: factor = (t - tmin)/(tmax - tmin) * pull
    # df[col] = df[col] * (1 - factor) + global_mean * factor
    return df


def inject_seasonal_anomaly(df, pattern, columns):
    """Scale target values inside anomaly_window by (1 + magnitude).
    Mirror inject_trend_break (L160-241) but with a finite [start, end]
    window instead of a half-line break_point."""
    win_start, win_end = pattern["params"]["anomaly_window"]
    magnitude = pattern["params"]["magnitude"]
    # in_win = target_mask & (temporal in [win_start, win_end])
    # df.loc[in_win, col] *= (1 + magnitude)
    return df


# Update inject_patterns dispatch at L52-78:
elif pattern_type == "ranking_reversal":
    df = inject_ranking_reversal(df, pattern, columns)
elif pattern_type == "dominance_shift":
    df = inject_dominance_shift(df, pattern, columns)
elif pattern_type == "convergence":
    df = inject_convergence(df, pattern, columns)
elif pattern_type == "seasonal_anomaly":
    df = inject_seasonal_anomaly(df, pattern, columns)
```

**集成点:**
- `engine/patterns.py::inject_patterns`([L29-86](pipeline/phase_2/engine/patterns.py#L29-L86))
  —— 用每个新注入器的显式分发替换 4 路 NotImplementedError 分支。
- `sdk/relationships.py::VALID_PATTERN_TYPES`([L29](pipeline/phase_2/sdk/relationships.py#L29))
  —— 把 4 个名字加回。
- `sdk/relationships.py::PATTERN_REQUIRED_PARAMS`([L39](pipeline/phase_2/sdk/relationships.py#L39))
  —— 增加按类型必填参数条目:
  ```
  "ranking_reversal":  frozenset({"metrics"})            # plus optional "entity_col"
  "dominance_shift":   frozenset({"entity_filter", "split_point"})
  "convergence":       frozenset()                        # all params optional
  "seasonal_anomaly":  frozenset({"anomaly_window", "magnitude"})
  ```
- `orchestration/prompt.py:72,190+` —— 重新宣告各类型,并在 One-Shot
  示例中添加配套条目。

**新类型:** 无。

### 测试标准
- 按类型:声明使用合法 params 成功;`inject_*` 产生满足配套 L3 校验器
  的后置条件(往返)。
- 按类型:声明缺少必填参数抛 ValueError,detail 与类型相关。
- 边界:空目标子集 → `PatternInjectionError`(镜像既有 outlier 行为)。
- 边界:依赖时间的类型缺时间列 → 优雅错误(镜像
  `inject_trend_break` L195-202)。
- 往返集成:使用全部 4 种新类型的脚本端到端运行 Loop A 不崩溃;L3
  校验器返回 4 个通过的 check。

### 估算规模
**Large (200+ LOC)。** 每个注入器函数体 ≈ 50–80 LOC × 4 ≈ 250 LOC,
加 relationships.py + prompt.py 更新 ≈ 30 LOC,加测试(unit +
roundtrip)≈ 150 LOC ≈ 430 LOC 总计。可比合并的
`inject_outlier_entity` + `inject_trend_break`(~150 LOC)的 ×2,加
四个注入器与集成胶水。

---

## [DS-3] 混合分布 KS 检验

### 代码片段
```python
# pipeline/phase_2/validation/statistical.py:259-264
if family == "mixture":
    return [Check(
        name=f"ks_{col_name}",
        passed=True,
        detail="mixture distribution KS test not yet implemented",
    )]
```

### 规范引用
- §2.1.1 (L94):`"mixture"` 在 `SUPPORTED_DISTRIBUTIONS` 中。
- §2.5 (L302):LLM prompt 的允许分布列表中包含 `"mixture"`。
- §2.9 L2 (L206–314):该 stub 是 `check_stochastic_ks()` 的一部分。
  Predictor-cell 枚举(L212–221)与 `_expected_cdf()`(L130–166)的
  CDF 构造已描述,但 `_expected_cdf()` 对 `family == "mixture"`(L165)
  返回 `None` —— 未定义组件 schema。

### 既有测试
- (未发现)

### 依赖 stub
- (无 —— DS-3 是叶;父项是 IS-1。)

### 在管道中的角色
位于 §2.9 L2 统计校验,在
[validation/statistical.py](pipeline/phase_2/validation/statistical.py)::`check_stochastic_ks`
中。在引擎生成后按随机 measure 调用一次。上游:生成的 DataFrame、
`family="mixture"` 的 `col_meta`,以及 patterns 列表(pattern target
中的行被排除)。下游:供 `ValidationReport` 使用的 `Check` 列表。
`AUTO_FIX` 有一个 `ks_*` 策略(`widen_variance`),但对 mixture 不能
自然适用(没有可放宽的单一方差)。

### 缺口分析
- **规范定义:** §2.9 L2 草绘了随机 measure 的 KS 检验:
  `kstest(subset, family, args=expected_params)` 跨 predictor 单元
  (L618-621)。§2.1.1 在受支持族中列出 `mixture`。
- **规范沉默:** 如何针对 predictor 单元参数构造 mixture 的期望 CDF。
  L2 例使用 `args=expected_params` 假设有闭式 CDF;mixture 需要组件
  CDF 的加权和,但组件参数如何依赖 predictor 未定义(因为 IS-1 的
  `param_model` schema 未定义)。
- **实现缺口:** 返回硬编码 `passed=True` 的 Check。在 IS-1 的 mixture
  `param_model` schema 定义之前不能实现。具体:
  [validation/statistical.py:130-166](pipeline/phase_2/validation/statistical.py#L130-L166)
  的 `_expected_cdf` 没有显式 `mixture` 分支 —— 函数对任何无法识别
  的族在 L166 落到裸 `return None` —— 因此 mixture 最终通过 fallthrough
  返回 `None`,而非专门分支。缺口同时存在于 CDF 构造层与 kstest
  编排层。

### 依赖链
- **阻塞:** 无后续。
- **被以下阻塞:** **IS-1**(无法采样的也无法测试);规范扩展定义
  mixture `param_model` schema(与 IS-1 相同的阻塞)。
- **共依赖于:** IS-1 —— 必须共同实现以确保此处使用的 CDF 与那里使用
  的 sampler 匹配。CLAUDE.md 正式将其配对为父子。

### 阻塞性问题
- **同 IS-1** —— 必须先确定 mixture `param_model` schema。独立实现
  不可能。
- **操作:** scipy 没有原生 mixture frozen-dist;使用一个仅暴露
  `.cdf()` 的小型 `_MixtureFrozen` 适配器(对 `kstest(args=...)` 已
  足够)。

### 提议方案
基于 IS-1 的解读 (a)。扩展 `_expected_cdf` 与 predictor-cell 参数遍历
以处理 mixture。

```python
# pipeline/phase_2/validation/statistical.py — extend _expected_cdf
# (currently L130-166; mixture branch returns None).

class _MixtureFrozen:
    """scipy frozen-dist-like adapter: exposes .cdf() for kstest.

    For a mixture of K components with weights w_k and frozen scipy
    distributions D_k, mixture.cdf(x) = sum(w_k * D_k.cdf(x)).
    """
    def __init__(self, components: list[tuple[float, Any]]):
        self.components = components  # list of (weight, frozen_dist)

    def cdf(self, x: np.ndarray) -> np.ndarray:
        return sum(w * d.cdf(x) for w, d in self.components)


def _expected_cdf_mixture(params: dict[str, Any]) -> Optional[_MixtureFrozen]:
    """Build a mixture frozen-dist from per-cell mixture params.

    Schema (from IS-1): params = {"components": [{family, weight, params}, ...]}
    """
    components = params.get("components")
    if not components:
        return None
    frozen = []
    total_weight = 0.0
    for comp in components:
        sub = _expected_cdf(comp["family"], comp["params"])
        if sub is None:
            return None  # one unsupported component → skip the whole test
        frozen.append((comp["weight"], sub))
        total_weight += comp["weight"]
    if total_weight <= 0:
        return None
    # Auto-normalize
    return _MixtureFrozen([(w / total_weight, d) for w, d in frozen])


# In _expected_cdf, replace the implicit `return None` for mixture with:
elif family == "mixture":
    return _expected_cdf_mixture(params)


# In check_stochastic_ks (L259-264), drop the early-return special case
# entirely — the predictor-cell loop will now construct mixture CDFs
# via the standard path.
```

对 per-cell 参数计算,扩展 `_compute_cell_params`(L169-203)以遍历
组件列表:

```python
def _compute_cell_params(col_meta, predictor_values, columns_meta):
    """Return either a flat {param_key: theta} dict (non-mixture) or
    a {"components": [{family, weight, params}, ...]} dict (mixture)."""
    if col_meta.get("family") == "mixture":
        return {
            "components": [
                {
                    "family": comp["family"],
                    "weight": comp["weight"],
                    "params": _compute_cell_params_for_subspec(
                        comp, predictor_values, columns_meta,
                    ),
                }
                for comp in col_meta["param_model"]["components"]
            ]
        }
    # ... existing flat-params branch
```

**集成点:**
- `validation/statistical.py::_expected_cdf`([L130-166](pipeline/phase_2/validation/statistical.py#L130-L166))
  —— 加入 mixture 分支。
- `validation/statistical.py::check_stochastic_ks`([L259-264](pipeline/phase_2/validation/statistical.py#L259-L264))
  —— 去掉 mixture early-return;predictor-cell 循环现在通过标准路径
  处理。
- `validation/statistical.py::_compute_cell_params`([L169-203](pipeline/phase_2/validation/statistical.py#L169-L203))
  —— 在 `family == "mixture"` 时分支以遍历 components。

**新类型:** `_MixtureFrozen`(`validation/statistical.py` 中的私有
适配器)。

### 测试标准
- 从 IS-1 采样的 2 组件 gaussian mixture → KS 检验通过。
- 不匹配 mixture(从与声明不同的参数采样)→ KS 检验失败。
- 单组件 mixture(weight=1.0)→ 与该族非 mixture KS 检验完全一致。
- 含不受支持族(如 poisson)的组件 → 返回 None,该 predictor 单元
  以既有 "CDF not available" detail 跳过。
- 自动归一化:权重 `[0.3, 0.2]` 的组件以等价 `[0.6, 0.4]` 测试。

### 估算规模
**Small (20–80 LOC)。** `_MixtureFrozen` ≈ 15 LOC +
`_expected_cdf_mixture` ≈ 20 LOC + cell 参数遍历 ≈ 25 LOC + 测试
≈ 70 LOC ≈ 130 LOC。**不能在 IS-1 之前发布。**

---

## [DS-4] 多列 group dependency `on`

### 代码片段
```python
# pipeline/phase_2/sdk/relationships.py:123-132
# P2-4: Restrict to single-column `on` for v1
if not on:
    raise ValueError(
        f"'on' must contain at least one column, got empty list."
    )
if len(on) != 1:
    raise NotImplementedError(
        f"Multi-column 'on' is not supported in v1. "
        f"Got on={on} (length {len(on)}). Use a single column."
    )
```

### 规范引用
- §2.1.2 (L106–117):`add_group_dependency()` 签名 —— `on` 为列表
  参数;按父值键控的嵌套 `conditional_weights` 已记录。规范未明确
  限制 `on` 长度,但多列被延期(代码中 `P2-4` 标记)。
- §2.2 (L133–160):Dimension Groups 与跨组关系 —— root 级依赖图与
  条件权重;所有规范示例使用单列 `on`。

### 既有测试
- (无测试触及多列 `on`;它被 `NotImplementedError` 阻塞。)
- `tests/modular/test_sdk_dag.py` 覆盖单列 `on` 场景。

### 依赖 stub
- (无 —— DS-4 是叶;父项是嵌套 `conditional_weights` 的规范。)

### 在管道中的角色
位于 §2.1.2 / §2.2 —— SDK 声明步骤。`add_group_dependency(child_root,
on, conditional_weights)` 接受 `on` 为列表(一直如此),但用
`NotImplementedError` 强制 `len(on) == 1`。下游消费者将是引擎生成器
α 步,通过嵌套条件表计算 `P(child | a, b)`。当前多列 `on` 的脚本在
声明期就崩溃,引擎根本不会运行。

### 缺口分析
- **规范定义:** §2.1.2 L106-117 把 `on` 声明为列表参数(类型上隐含
  多列);§2.2 L150 —— "the root-level dependency graph must be a
  DAG";规范示例使用单列 `on=["severity"]` 但**没有**显式禁止多列。
- **规范沉默:** 多列 `on` 的 `conditional_weights` 结构。单列
  `on=["severity"]` 时,权重按父值键控:
  `{"Mild": {...}, "Moderate": {...}}`。多列 `on=["severity",
  "hospital"]` 时,规范没说是嵌套(`{"Mild": {"Xiehe": {...}}}`)、
  元组键(`{("Mild", "Xiehe"): {...}}`),还是平铺笛卡尔映射。无
  示例。
- **实现缺口:** 当 `len(on) != 1` 时抛 `NotImplementedError`。实现
  需要 (a) 定义多键 `conditional_weights` 结构(嵌套 dict 最自然)、
  (b) 扩展 `add_group_dependency` 中的声明校验以遍历嵌套 dict 并
  检查笛卡尔积覆盖、(c) 扩展引擎采样步以求值嵌套条件、(d) 扩展 root
  DAG 无环检查以处理多父边。

### 依赖链
- **阻塞:** 清单中无。
- **被以下阻塞:** 规范扩展澄清"嵌套 vs 元组"权重 schema、归一化
  规则、缺失组合的处理。
- **共依赖于:** 清单中无。

### 阻塞性问题
- **规范:** 多列 `on` 的 `conditional_weights` 结构。两种合理选择:
  (a) 按父值序列键控的嵌套 dict
  (`{"Mild": {"Xiehe": {"Insurance": 0.8, ...}}}`)、(b) 元组键
  扁平 dict(`{("Mild", "Xiehe"): {"Insurance": 0.8, ...}}`)。
  嵌套是 JSON 可序列化,且对单列情形是自然延伸。
- **规范:** 笛卡尔积是否必须完全覆盖,还是允许部分覆盖(带默认
  fallback)?单列情形要求完全覆盖 —— 沿用同规则最干净。
- **操作:** N 维基数膨胀 —— 对 `on=[a, b, c]`,基数 5×4×3 时,LLM
  必须声明 60 个内层权重 dict。是否需要软上限以避免 prompt 溢出?

### 提议方案
选 (a) 嵌套 dict、要求完全笛卡尔积覆盖(与既有单列规则一致)、不设
软上限(由 LLM 负责 —— 膨胀过度时浮现清晰错误)。

```python
# pipeline/phase_2/sdk/relationships.py — replace the
# NotImplementedError block at L123-132.

def add_group_dependency(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    orthogonal_pairs: list[OrthogonalPair],
    child_root: str,
    on: list[str],
    conditional_weights: dict[Any, Any],  # nesting depth = len(on)
) -> None:
    if not on:
        raise ValueError("'on' must contain at least one column.")

    # Existing: validate child_root + each parent is a group root
    if child_root not in columns:
        raise ValueError(f"Column '{child_root}' not found in registry.")
    if not _groups.is_group_root(child_root, columns, groups):
        raise NonRootDependencyError(column_name=child_root)
    for parent_col in on:
        if parent_col not in columns:
            raise ValueError(f"Column '{parent_col}' not found in registry.")
        if not _groups.is_group_root(parent_col, columns, groups):
            raise NonRootDependencyError(column_name=parent_col)

    # Existing: orthogonal-conflict check, run for each parent
    child_group = _groups.get_group_for_column(child_root, columns)
    for parent_col in on:
        parent_group = _groups.get_group_for_column(parent_col, columns)
        if child_group and parent_group:
            _check_orthogonal_conflict(child_group, parent_group, orthogonal_pairs)

    # Existing: root DAG acyclicity, run for each parent edge
    for parent_col in on:
        _dag.check_root_dag_acyclic(group_dependencies, child_root, parent_col)

    # Validate + normalize nested weights
    parent_value_sets = [columns[p]["values"] for p in on]
    child_values = columns[child_root]["values"]
    normalized_cw = _validate_and_normalize_nested_weights(
        conditional_weights, parent_value_sets, child_values, depth=len(on),
        path=[],
    )

    dep = GroupDependency(
        child_root=child_root, on=list(on),
        conditional_weights=normalized_cw,
    )
    group_dependencies.append(dep)


def _validate_and_normalize_nested_weights(
    cw: dict, parent_value_sets: list[list[Any]],
    child_values: list[Any], depth: int, path: list[Any],
) -> dict:
    """Recursively validate that cw covers the Cartesian product of
    parent_value_sets and that leaves cover child_values.
    """
    if depth == 0:
        # Leaf: cw is {child_val: weight}
        provided = set(cw.keys())
        expected = set(child_values)
        missing = expected - provided
        if missing:
            raise ValueError(
                f"conditional_weights{path} missing child values: {sorted(missing)}."
            )
        extra = provided - expected
        if extra:
            raise ValueError(
                f"conditional_weights{path} contains keys not in child values: {sorted(extra)}."
            )
        return _val.normalize_weight_dict_values(
            label=f"conditional_weights{path}", weights=cw,
        )
    # Recursive level: cw is {parent_val: <nested>}
    expected = set(parent_value_sets[0])
    provided = set(cw.keys())
    missing = expected - provided
    if missing:
        raise ValueError(
            f"conditional_weights{path} missing parent values at depth "
            f"{len(path)}: {sorted(missing)}."
        )
    return {
        k: _validate_and_normalize_nested_weights(
            v, parent_value_sets[1:], child_values,
            depth - 1, path + [k],
        )
        for k, v in cw.items()
    }
```

引擎侧(扩展现有的单父 group-dep 采样器):

```python
# pipeline/phase_2/engine/generator.py (or wherever group deps are sampled)

def _sample_group_dep(
    dep: GroupDependency, rows: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample child_root values per row given multi-parent conditional weights."""
    cw = dep.conditional_weights
    n_rows = len(next(iter(rows.values())))
    parent_arrays = [rows[p] for p in dep.on]

    out = np.empty(n_rows, dtype=object)
    for i in range(n_rows):
        node = cw
        for parent_arr in parent_arrays:
            node = node[parent_arr[i]]  # walk N levels deep
        # node is now {child_val: weight}
        child_vals = list(node.keys())
        weights = np.fromiter(node.values(), dtype=float)
        out[i] = rng.choice(child_vals, p=weights / weights.sum())
    return out
```

校验侧:扩展 `max_conditional_deviation` 以递归遍历相同嵌套结构。

**集成点:**
- `sdk/relationships.py::add_group_dependency`([L101-213](pipeline/phase_2/sdk/relationships.py#L101-L213))
  —— 替换 `len(on) != 1` 的 NotImplementedError;新增
  `_validate_and_normalize_nested_weights`。
- `sdk/dag.py::check_root_dag_acyclic` —— 已经处理单父边;按 `on` 中
  的每个父调用一次。
- `engine/generator.py` —— 把 group-dep 采样步从扁平 `cw[parent_val]`
  查找扩展为 N 层深度遍历。
- `validation/statistical.py::max_conditional_deviation`([L24-55](pipeline/phase_2/validation/statistical.py#L24-L55))
  —— 把偏差比较扩展为遍历 N 层深度嵌套 dict。

**新类型:** 无(继续用 `dict[Any, Any]`;`GroupDependency` 已接受
`on: list[str]`)。

### 测试标准
- 完整笛卡尔积覆盖的 2 父依赖 → 声明成功;引擎采样在 10% 偏差内复现
  声明的条件分布。
- 缺失组合(深度 1 的某父值缺失)→ ValueError 列出缺失键路径。
- 内层缺失(叶处某子值缺失)→ ValueError 含完整路径。
- 既有单列测试仍通过(向后兼容:depth=1 必须产生与之前相同的归一化
  输出)。
- L2 group-dep 偏差检查在多父规格上正确识别偏离观测。

### 估算规模
**Medium (80–200 LOC)。** 嵌套权重遍历 ≈ 50 LOC + 引擎采样器扩展
≈ 30 LOC + 校验偏差遍历 ≈ 30 LOC + 测试 ≈ 80 LOC ≈ 190 LOC 总计。
约为单列足迹的 2 倍;递归在三个调用点替换扁平 2 层 dict 逻辑。

---

# 阶段 A 总结

- **已确认 stub:** 全部 10 项清单条目(IS-1..IS-6, DS-1..DS-4)如述
  存在,但 IS-1 行号已从 CLAUDE.md 的 `~L297-303` 漂移到实际的
  `L360-366`。
- **完全无测试覆盖的 stub:** IS-1、IS-2、IS-3、IS-4、DS-1、DS-3、
  DS-4(10 个里 7 个)。
- **有显式"拒绝"测试的 stub:** IS-5
  (`test_add_measure_rejects_scale_kwarg`)。
- **通过"仅已实现类型"测试隐式覆盖的 stub:** DS-2(校验器/auto-fix
  测试运行,但仅在 `outlier_entity` / `trend_break` 上)。
- **规范缺席或薄弱:** IS-3(convergence)与 IS-4(seasonal_anomaly)
  出现在 `inject_pattern` PATTERN_TYPES 中,但 §2.9 中无 L3 校验
  伪代码;convergence 完全没有定义算法。
- **已识别的跨 stub 依赖链:**
  - IS-1 → DS-3(mixture KS 检验依赖 mixture 采样)
  - DS-2 → IS-2、IS-3、IS-4(pattern 校验在 pattern 注入实现前无法
    端到端运行)
- **"双重屏蔽"防御模式(横切性)。** 三个 stub 遵循同一"SDK 接受但
  prompt 不宣告"模式:**IS-5**(`scale=` 已从 `prompt.py:53-54` 的
  `add_measure` 签名中移除)、**DS-1**(`censoring=` 已从
  `prompt.py:70-71` 的 `set_realism` 签名中移除)、**DS-2**(4 个
  pattern 类型已从 `prompt.py:89` 的 PATTERN_TYPES 列表与
  `sdk/relationships.py:29` 的 `VALID_PATTERN_TYPES` 中移除)。三者
  都是为防止 LLM 把重试预算花在调整死参数上而做的防御性移除。任何
  恢复都需要更新所有三处加上 One-Shot 示例,而不仅是引擎侧 stub。

---

# 阶段 B 总结

- **规范缺口主导代码缺口,有保留。** 10 个里 6-7 个 stub 至少部分
  被规范定义缺失阻塞。两个例外:**IS-6** 纯属操作性(多错误 / token
  预算 —— 已显式标注为非规范特性),**DS-2 的 `ranking_reversal`
  注入器**可由既有校验器(已在规范 §2.9 L655-661 中)推导其契约,
  因此并非严格被规范阻塞。
  - IS-3(convergence)与 IS-4(seasonal_anomaly)规范覆盖最薄 ——
    §2.9 L3 中均无伪代码。
  - IS-5(`scale`)是规范中无行为内容的残余签名行;spec/prompt/SDK
    已统一为省略。
- **两组干净的共依赖对:** mixture 采样/校验的 `(IS-1, DS-3)` 与
  pattern 注入/校验的 `(DS-2, [IS-2, IS-3, IS-4])`。每对必须共享
  一个运算定义;只实现一侧会产生静默漂移。
- **DS-2 是与 pattern 相关最重大的 stub。** 4 个延期 pattern 类型被
  双重屏蔽(SDK 拒绝 + prompt 不宣告);恢复需要触动
  `engine/patterns.py`、`sdk/relationships.py`、`prompt.py` 加上
  IS-2/3/4 校验器。引擎中 4 类的 `NotImplementedError` 分支当前是
  死的防御代码。
- **`check_ranking_reversal` 已完整实现但不可达** —— 校验器就绪,
  但 SDK 不接受该类型,且没有注入器。一个铲到位的首步。
- **IS-6 自成一类。** 纯能力缺口,无 `NotImplementedError`,两个
  独立子特性(多错误收集 + token 预算)可分开发布。两者都是规范
  之外的操作性优化。
- **叶 stub(DS-1、DS-4):** 孤立;仅被参数 schema 的规范决策阻塞
  (censoring config、多列 conditional_weights 嵌套)。

---

# 阶段 C 总结

| Stub  | 推荐 | 规模 | 关键阻塞 |
|-------|------|------|----------|
| IS-1  | 用组件级 `param_model` schema 实现(解读 (a)) | Medium | mixture schema 的规范决策 |
| IS-2  | 实现为按切分排名变化(解读 (a)) | Small | dominance 度量的规范决策 |
| IS-3  | 实现为组均值方差下降(解读 (b)) | Small | convergence 度量的规范决策 |
| IS-4  | 实现为窗口对基线 z-score(解读 (a)) | Small | seasonal 定义的规范决策 |
| IS-5  | **不要恢复** —— 从规范中剥离残余签名 | Trivial | 无(已在正确状态) |
| IS-6  | 推后;若需要先发 token-budget 一半 | Large | 多错误反馈效率的 A/B 测试 |
| DS-1  | 实现为按列 NaN-标记 censoring | Small | schema + 标记的规范决策 |
| DS-2  | 实现 4 个注入器;`ranking_reversal` 优先 | Large | 各注入算法的规范决策 |
| DS-3  | 在 IS-1 之后实现;`_MixtureFrozen` 适配器 | Small | 先发 IS-1 |
| DS-4  | 用嵌套 dict `conditional_weights`(a)实现 | Medium | 权重嵌套的规范决策 |

**总估算规模**(若全部发布):约 1.5k LOC 实现 + 测试,以 IS-6
(~340 LOC)与 DS-2(~430 LOC)为主。IS-1+DS-3 紧密耦合(合计
~300 LOC)。

**降低风险 + 提速变现的推荐顺序:**

1. **IS-5 文档清理(trivial)。** 把残余的 `scale=None` 签名行从
   规范 §2.1.1 L51 与 §2.5 L287 中剥离,使其与已省略它的 prompt
   和 SDK 一致。无代码改动。
2. **DS-1 censoring(small)。** 叶 stub,孤立,决策仅在 schema ——
   规范一次后即可发布。
3. **`ranking_reversal` 复活(small)。** 校验器已存在;只需注入器
   + SDK 屏蔽更新 + prompt 更新。DS-2 集群中工作量最低的胜利。
4. **IS-3、IS-4、IS-2 + 余下 DS-2 注入器(medium-large)。** 在规范
   落地后,把每个校验器与其注入器配对发布。
5. **IS-1 + DS-3(medium,配对)。** 规范依赖最重;一起做。
6. **DS-4 多列 on(medium)。** 独立;在 LLM 工作流要求多父依赖时
   发布。
7. **IS-6(large)。** 优化;在重试循环开销被实测为真实瓶颈之前
   推后。

**需要的共因规范扩展**(以解锁最大比例的 stub):
- mixture `param_model` schema(解锁 IS-1 + DS-3)。
- `dominance_shift`、`convergence`、`seasonal_anomaly` 注入 + 校验
  的运算定义(解锁 IS-2/3/4 + 4 个 DS-2 子特性中的 3 个)。
- censoring 配置 schema + 标记语义(解锁 DS-1)。
- 多列 `conditional_weights` 嵌套规则(解锁 DS-4)。

Stub 缺口分析完毕。
