# M2: Generation Engine — 模块画像

## 一句话职责

执行完全确定性的、DAG 排序的四阶段流水线（skeleton → measures → patterns → realism），将 M1 冻结的声明存储 + seed 转换为原子粒度的 Master DataFrame。

## 实现状态：8 / 16（50%）

8 项 SPEC_READY 中：
- **完整实现：** 4 项（skeleton 生成、预飞 DAG、单 RNG 流、返回类型）
- **框架就位但核心 stub：** 2 项（随机度量采样、结构性度量求值——被 P0 公式求值器阻塞）
- **完整实现：** 2 项（outlier_entity 和 trend_break 模式注入）

8 项 NEEDS_CLAR 中：1 项已在代码中自行解决（`_post_process`），2 项部分实现（realism missing/dirty），5 项为 stub/缺失。

## 在流水线中的位置

```
M1 (冻结的声明存储 + seed)
  │
  ├──► M2: Generation Engine ──► Master DataFrame ──► M5 (验证)
  │                                                     │
  └──► M4: Schema Metadata   ──► metadata dict    ──► M5
                                                       │
                                                  Loop B (max 3)
                                                       │
                                                       ▼
                                                  M2 (re-run, seed+attempt)
```

- **上游：** M1 — 提供冻结的声明存储（列注册表、组图、度量 DAG 边、模式列表、realism 配置）+ seed
- **下游：** M5 — 接收 Master DataFrame 进行三层校验
- **并行：** M4 — 与 M2 共读同一声明存储，可并行执行
- **反馈：** M5 → M2（Loop B）— 校验失败时以 `seed + attempt` 和参数覆盖重新执行

## 构建顺序中的位置

第 **4** 步（共 6 步）。前置依赖：types.py ✅、M1 ✅、M4 ✅

```
types.py ✅ → M1 ✅ → M4 ✅ → 【M2 ← 当前】 → M5 → M3
```

M2 在构建顺序中排在 M4 之后，因为 `generator.py` 的 return path 调用了 M4 的 `build_schema_metadata()`。理解 M4 的元数据结构有助于理解 M2 的输出契约。

---

## 已实现功能详解（SPEC_READY）

### SR1: 四阶段流水线结构 (α → β → γ → δ)

**规范定义（§2.8）：** 生成引擎实现为四阶段确定性流水线，数学表达为 `M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)`。各阶段固定顺序不可重排。

**代码实现：** 📍 `phase_2/engine/generator.py:27-133` — `run_pipeline()`

流水线编排在 `run_pipeline()` 中线性串联：

```python
# 实际执行顺序（从代码中提取）：
rng = np.random.default_rng(seed)           # L70 — 初始化
full_dag = _dag.build_full_dag(...)          # L73 — 预飞
topo_order = _dag.topological_sort(full_dag) # L76
rows = _skeleton.build_skeleton(...)         # L79 — Stage α
rows = _measures.generate_measures(...)      # L84 — Stage β (stub)
df = _postprocess.to_dataframe(...)          # L89 — τ_post ⬅ 注意位置
df = _patterns_mod.inject_patterns(df, ...)  # L94 — Stage γ
df = _realism_mod.inject_realism(df, ...)    # L99 — Stage δ
metadata = _build_meta(...)                  # L118 — M4 调用
return df, metadata                          # L133
```

**生动类比：** 如果 M2 是一条汽车装配线——Stage α 安装底盘和车身（骨架），Stage β 安装发动机和仪表盘（度量值），Stage γ 喷涂特殊标记（模式注入），Stage δ 模拟使用磨损（realism 降级）。`τ_post` 是质检包装。

**💡 为什么这样设计？** 代码中 `τ_post` 实际在 γ 之前执行（先转 DataFrame），而非规范数学表达的最外层。原因是 α/β 操作 `dict[str, np.ndarray]`（高效的列式操作），γ/δ 需要 `pd.DataFrame`（方便使用 `df.eval()` 和 `df.loc[]` 做子集操作）。这是一个务实的架构决策——功能等价但数据结构在中间切换。

---

### SR2: Stage α — Skeleton 生成

**规范定义（§2.4 步骤 1-7, §2.8）：** 按拓扑序生成所有非度量列——根分类从边际权重、子分类从条件权重、跨组依赖根从条件权重表、时间根均匀采样、时间派生确定性提取。

**代码实现：** 📍 `phase_2/engine/skeleton.py:31-102` — `build_skeleton()`

这是 M2 中实现最完整、零 NEEDS_CLAR 的文件。顶层调度器遍历 `topo_order`，按 `col_type` 分发：

| 列类型 | 采样器 | 代码位置 | 核心调用 |
|---|---|---|---|
| 独立根分类 | `sample_independent_root()` | 📍 `skeleton.py:109-131` | `rng.choice(values, p=weights)` |
| 跨组依赖根 | `sample_dependent_root()` | 📍 `skeleton.py:134-179` | 按父值 mask 条件 `rng.choice()` |
| 组内子分类 | `sample_child_category()` | 📍 `skeleton.py:182-230` | list → 扁平广播 / dict → 逐父值 |
| 时间根 | `sample_temporal_root()` | 📍 `skeleton.py:237-289` | 日期池 + `rng.integers()` 索引 |
| 时间派生 | `derive_temporal_child()` | 📍 `skeleton.py:343-378` | `DatetimeIndex` 属性提取，无 RNG |

**生动类比：** Stage α 就像人口普查的第一步——先给每行"居民"分配身份信息（哪个医院、什么科室、什么时间来的），这些身份信息之间有层级关系（医院→科室）和条件约束（严重程度影响入院来源的分布）。度量值（费用、住院天数）要等身份确定后才能根据身份参数生成。

**💡 为什么这样设计？** Skeleton 采用逐列生成而非逐行生成。虽然 §2.4 描述的概念模型是"per-row loop"，但代码为每一列一次性生成 `target_rows` 个值（向量化），利用 numpy 的 `rng.choice(size=target_rows)` 批量采样。这是性能优化——1000 行 × 20 列只需 ~20 次 `rng.choice` 调用，而非 20000 次逐行调用。

**关键实现细节：**
- 时间采样构建合规日期池（daily/weekly/monthly），而非直接在日期范围内随机——确保采样结果落在声明的频率网格上
- 频率代码映射 `FREQ_MAP` (📍 `skeleton.py:256`) 将 SDK 的 `"D"`/`"W-*"`/`"MS"` 转为引擎内部名称
- `sample_dependent_root()` 只取 `dep.on[0]`（📍 `skeleton.py:146`），硬编码单列依赖——与 NEEDS_CLAR "多列 on" 一致

---

### SR3: Stage β — 随机度量采样

**规范定义（§2.3, §2.8）：** 对每行，按分类上下文计算每个分布参数 `θⱼ = β₀ + Σₘ βₘ(Xₘ)`，然后从命名分布族（gaussian, lognormal, gamma, beta, uniform, poisson, exponential）中抽样。

**代码实现：** 📍 `phase_2/engine/measures.py:19-63` — `generate_measures()` + 📍 `measures.py:66-81` — `_sample_stochastic()`

**当前状态：框架就位，核心 stub。** 调度器遍历 `topo_order` 并按 `measure_type` 区分 stochastic/structural，但两个分支只打 debug 日志后 `continue`。`_sample_stochastic()` 函数定义存在但 `raise NotImplementedError`（标注 "Blockers 2 & 3"）。

参数签名已就位：`generate_measures(columns, topo_order, rows, rng, overrides=None)` — 其中 `overrides` 参数是 Loop B auto-fix 的预留载体，设计正确但无可测试的行为。

**生动类比：** 如果 skeleton 是给居民分配身份证，那么随机度量就是"根据这个居民的身份信息查保险手册，算出 TA 的费用应该服从什么分布，然后掷骰子得到具体数字"。手册（参数模型）已经写好了，但掷骰子的机器（采样器）还没装上。

---

### SR4: Stage β — 结构性度量求值

**规范定义（§2.1.1, §2.3, §2.8）：** 结构性度量通过公式引用上游度量值和分类效应，加上可选噪声。例如 `revenue = cost * 1.35 + markup_effect`。公式中的每个符号必须能解析到已生成的列或效应值。

**代码实现：** 📍 `phase_2/engine/measures.py:84-99` — `_eval_structural()`

**当前状态：`raise NotImplementedError`。** 标注 "Blocker 2: formula DSL"。Stage4 设计了一个受限 AST walker 方案 `_evaluate_formula()`（仅允许 `+`/`-`/`*`/`/`/`**`、数字字面量、变量名），但该函数在代码中完全缺失。

**💡 为什么被阻塞？** 公式求值是 M2 中最具安全敏感性的组件——需要解析并执行 LLM 生成脚本中声明的公式字符串。使用 Python `eval()` 有安全风险（尽管脚本已经在沙箱中执行），使用受限 AST walker 则需要明确定义允许的操作符集合。这正是 P0 规范缺口的核心。

---

### SR5: 预飞 DAG 构建与拓扑排序

**规范定义（§2.8 伪代码, §2.4）：** `generate()` 入口处构建统一 DAG（合并四类边来源：组内层级、跨组依赖、时间派生、度量引用），计算拓扑排序，作为冗余安全检查。

**代码实现：** 📍 `phase_2/engine/generator.py:73-76`

```python
full_dag = _dag.build_full_dag(columns, groups, group_dependencies, measure_dag)
topo_order = _dag.topological_sort(full_dag)
```

M2 不自己实现 DAG 逻辑——委托给 M1 的 `dag.py`（已在 M1 画像中详细分析）。`topo_order` 驱动后续 skeleton（跳过度量列）和 measures（仅处理度量列）的遍历。

**💡 为什么重复构建？** M1 在声明阶段已验证无环，但 M2 在生成入口重新构建并排序——这是防御性编程：即使 M1 和 M2 之间的数据传递出现异常，M2 也能独立保证不在有环图上运行。成本极低（一次 O(V+E) 拓扑排序），安全收益高。

---

### SR6: 单一 RNG 流保证确定性

**规范定义（§2.8）：** `rng = np.random.default_rng(self.seed)` 传入每个阶段。相同 seed + 相同声明 = bit-for-bit 可复现。

**代码实现：** 📍 `phase_2/engine/generator.py:70`

```python
rng = np.random.default_rng(seed)
```

这个 `rng` 对象按引用传递到：
- `_skeleton.build_skeleton(..., rng)` — 📍 line 81
- `_measures.generate_measures(..., rng)` — 📍 line 85（当前 stub 不消耗）
- `_patterns_mod.inject_patterns(df, ..., rng)` — 📍 line 94
- `_realism_mod.inject_realism(df, ..., rng)` — 📍 line 99

**生动类比：** 单一 RNG 就像一卷预先掷好的骰子胶带——seed 决定了整卷的内容。skeleton 先用掉前 N 段，measures 用接下来的 M 段，以此类推。如果你在 skeleton 阶段多加了一列（多消耗了一些"骰子段"），后面所有度量的随机值都会不同——确定性是全局的，不是按列隔离的。

**💡 为什么这样设计？** 替代方案是给每列一个独立 seed（如 `seed + column_index`），这样增删列不会影响其他列的值。但 §2.8 选择了单一流——更简单、更容易推理，代价是声明变化时全局"雪崩"。对于本系统而言（每次生成都是全新的、由 LLM 脚本驱动），这个代价可以接受。

---

### SR7: Stage γ — `outlier_entity` 和 `trend_break` 模式注入

**规范定义（§2.9 L3）：** `outlier_entity` 要求目标子集的 z-score ≥ 2.0；`trend_break` 要求断点后变化幅度 > 15%。注入算法由验证逻辑反推约束。

**代码实现：**
- 调度器：📍 `phase_2/engine/patterns.py:29-82` — `inject_patterns()`
- outlier_entity：📍 `phase_2/engine/patterns.py:85-153` — `inject_outlier_entity()`
- trend_break：📍 `phase_2/engine/patterns.py:156-237` — `inject_trend_break()`

**`inject_outlier_entity` 算法：**
1. `df.eval(target_expr)` 获取目标行布尔 mask (line 110)
2. 计算全局 `mean` 和 `std` (lines 130-131)
3. 目标均值 = `global_mean + z_score × global_std` (line 142)
4. 偏移量 = `desired_mean − subset_mean` (line 144)
5. 目标子集统一加偏移 (line 146)

→ 保证注入后子集均值精确达到 z_score 倍标准差处，可通过 L3 的 z-score 校验。

**`inject_trend_break` 算法：**
1. `df.eval(target_expr)` 获取目标行 mask (line 202)
2. 在列注册表中查找唯一时间列 (lines 186-189)
3. 构建断点后 mask: `target & (temporal ≥ break_point)` (line 223)
4. 后断点行的目标列 `× (1 + magnitude)` (line 227-229)

→ `magnitude` 直接对应 L3 的 "幅度 > 15% 相对变化" 检查。

**生动类比：** 模式注入像在一幅已完成的画上"做旧"——outlier 是在某个角落加一抹不协调的亮色（异常值），trend_break 是在画面中间画一条横线，线上面和线下面的色调明显不同（趋势断裂）。

**💡 为什么这样设计？** 注入在 DataFrame 全部生成后才执行（而非生成时嵌入），因为模式需要全局统计信息（全局均值/标准差）和跨行时间信息（断点前后分割），这些在逐行生成时不可用。

**注意事项：**
- 两个注入器都有"列不存在"的优雅降级（warn + skip）——当度量未生成时（当前 stub 状态）不会崩溃
- `inject_patterns()` 接收 `rng` 但当前两种类型都不消耗它——注入操作是确定性的（纯数学位移/缩放）
- 代码未返回 `pattern_mask`（stage4 设计有但未实现），这意味着 realism 阶段无法知道哪些单元格被模式修改过

---

### SR8: 返回类型 `Tuple[pd.DataFrame, dict]`

**规范定义（§2.8 伪代码）：** `return self._post_process(rows), self._build_schema_metadata()`

**代码实现：** 📍 `phase_2/engine/generator.py:133`

```python
return df, metadata
```

- `df`: `pd.DataFrame`，由 `to_dataframe()` 转换（📍 `postprocess.py:19-82`）
- `metadata`: `dict`，由 M4 的 `build_schema_metadata()` 构建（📍 `generator.py:118-126`）
- 签名注解：📍 `generator.py:37` — `tuple[pd.DataFrame, dict[str, Any]]`

**💡 为什么 metadata 在 M2 中构建？** §2.8 的伪代码将 `_build_schema_metadata()` 放在 `generate()` 的 return 语句中，但 Stage1 将 M4 定义为独立模块。代码的解决方案是折中——M4 是独立函数（`phase_2.metadata.builder.build_schema_metadata`），但由 M2 的 `run_pipeline()` 在 return path 上调用。这保持了模块边界清晰（M4 的代码在自己的文件中），同时满足了 §2.8 的 return 契约。

---

## 接口契约（已实现的）

### 入口点：`run_pipeline()`

📍 `phase_2/engine/generator.py:27-37`

```python
def run_pipeline(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    measure_dag: dict[str, list[str]],
    target_rows: int,
    seed: int,
    patterns: list[dict[str, Any]] | None = None,
    realism_config: dict[str, Any] | None = None,
    overrides: dict | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
```

- **输入：** 解包的声明存储各部分 + seed + 可选的 patterns/realism/overrides
- **输出：** `(Master DataFrame, schema_metadata dict)`
- **调用时机：** M1 的 `FactTableSimulator.generate()` 调用此函数；Loop B 的 auto-fix 以 `seed + attempt` 重复调用

### 内部阶段接口：`build_skeleton()`

📍 `phase_2/engine/skeleton.py:31-37`

```python
def build_skeleton(
    columns: dict[str, dict[str, Any]],
    target_rows: int,
    group_dependencies: list[GroupDependency],
    topo_order: list[str],
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
```

- **输入：** 列注册表 + 行数 + 组依赖 + 拓扑序 + RNG
- **输出：** 列名 → numpy 数组字典（仅非度量列）
- **调用时机：** `run_pipeline()` 的 Stage α

### 内部阶段接口：`inject_patterns()`

📍 `phase_2/engine/patterns.py:29-34`

```python
def inject_patterns(
    df: pd.DataFrame,
    patterns: list[dict[str, Any]],
    columns: dict[str, dict[str, Any]],
    rng: np.random.Generator,
) -> pd.DataFrame:
```

- **输入：** 完整 DataFrame + 模式规范列表 + 列注册表 + RNG
- **输出：** 注入模式后的 DataFrame（in-place 修改并返回）
- **调用时机：** `run_pipeline()` 的 Stage γ（仅当 `patterns` 非空时）

### 内部阶段接口：`inject_realism()`

📍 `phase_2/engine/realism.py:25-30`

```python
def inject_realism(
    df: pd.DataFrame,
    realism_config: dict[str, Any],
    columns: dict[str, dict[str, Any]],
    rng: np.random.Generator,
) -> pd.DataFrame:
```

- **输入：** DataFrame + realism 配置 + 列注册表 + RNG
- **输出：** 注入缺失/脏值后的 DataFrame
- **调用时机：** `run_pipeline()` 的 Stage δ（仅当 `realism_config is not None` 时）

---

## 关键约束与不变量

1. **确定性不变量：** 相同 `(seed, declarations)` → 相同输出。由单一 `rng` 的顺序消耗保证。📍 `generator.py:70`
2. **阶段顺序不变量：** α → β → γ → δ 不可重排。非度量列必须在度量之前（度量参数依赖分类上下文），度量必须在模式之前（模式修改度量值），模式必须在 realism 之前（realism 降级不应在模式注入前破坏数据）。
3. **DAG 顺序不变量：** 列生成严格按拓扑序——列永远不会在其依赖之前生成。📍 `skeleton.py:55` / `measures.py:43`
4. **无 LLM 调用不变量：** M2 是纯计算。LLM 的贡献在 M1 的脚本执行阶段已结束。
5. **行数不变量：** skeleton 精确生成 `target_rows` 行。后续阶段修改值但不增减行。
6. **声明存储只读不变量：** M2 不修改声明存储——Loop B 的参数调整通过 `overrides` 叠加层实现，不突变原始声明。

---

## 反馈回路参与

### Loop B：统计自动修复（M5 → M2）

- **触发条件：** M5 的 L1/L2/L3 校验失败
- **M2 的角色：** 被动执行方——以新 seed (`seed + attempt`) 和参数覆盖 (`overrides`) 重新执行整个 `run_pipeline()`
- **代码路径：** `run_pipeline()` 的 `overrides` 参数 → 📍 `generator.py:36` 接收 → 📍 `generator.py:85` 传递给 `generate_measures()` → 📍 `measures.py:24` 接收（当前 stub 不使用）
- **最大重试：** 3 次（由 M5 的 `generate_with_validation()` 控制，M2 不感知重试计数）
- **🚧 当前状态：** 框架完备（参数签名已预留 `overrides`），但因 Stage β stub，auto-fix 的效果无法体现

---

## TODO 地图（NEEDS_CLAR）

### NC1: 公式求值机制 — **P0** 🔴

- **阻塞原因：** `_eval_structural` 必须对公式字符串求值，但规范未指定使用 `eval()`、受限解析器还是 AST 求值器
- **代码状态：** `raise NotImplementedError` — 📍 `measures.py:96-98`
- **影响下游：** M1（`add_measure_structural` 的符号解析依赖同一语义）、M5（L2 残差检查需要公式求值结果）
- **Stage3 建议：** 使用受限 AST 表达式求值器，仅允许 `+`/`-`/`*`/`/`/`**`、数字字面量和变量名

### NC2: `_post_process(rows)` 行为 — **P2** 🟡

- **阻塞原因：** 规范提及 `τ_post` 但未定义具体操作
- **代码状态：** **已实现** — 📍 `postprocess.py:19-82`（dict→DataFrame + RangeIndex + dtype 转换）
- **影响下游：** M5（DataFrame 的 dtype 影响校验行为）
- **Stage3 建议：** 与代码实现一致——DataFrame 转换 + RangeIndex + datetime64 cast，无值裁剪

### NC3: 模式组合——目标重叠时优先级 — **P3** 🟢

- **阻塞原因：** 两个模式命中同一行同一列，无定义优先级或组合规则
- **代码状态：** 隐式按声明顺序——📍 `patterns.py:48` `for pattern in patterns:` 循环顺序突变
- **影响下游：** M5 L3 校验结果取决于最后一个模式的效果
- **Stage3 建议：** 按声明顺序应用，文档记录顺序突变语义

### NC4: 模式注入破坏结构性公式一致性 — **P2** 🟡

- **阻塞原因：** 对结构性度量注入异常值会覆盖公式推导值，导致 M5 L2 残差检查失败
- **代码状态：** 无保护代码——patterns.py 不检查目标列类型，不返回 pattern_mask
- **影响下游：** M5 L2
- **Stage3 建议：** L2 残差检查应排除匹配任何模式 `target` 过滤器的行

### NC5: Realism 注入语义 — **P2** 🟡

- **阻塞原因：** 哪些列缺失？单元格能否同时缺失和脏？"脏"具体含义？
- **代码状态：** 部分实现 —
  - missing：📍 `realism.py:67-99` — 对所有列均匀注入 NaN ✅
  - dirty：📍 `realism.py:102-163` — 仅对分类列进行字符级扰动 ✅
  - censoring：📍 `realism.py:59-63` — `raise NotImplementedError` ❌
  - 优先级：missing 先于 dirty 执行（line 51-55）✅
- **影响下游：** M5 L1（缺失影响基数检查）、L3（NaN 可能破坏模式信号）
- **Stage3 建议：** 与已实现行为一致——missing 全列均匀，dirty 仅分类列，missing 优先，censoring stub

### NC6: 结构性度量 `noise={}` 默认行为 — **P2** 🟡

- **阻塞原因：** 是零噪声（确定性）还是错误？影响 M5 L2 除零
- **代码状态：** 不可达——度量生成整体 stub，`noise` 参数从未被读取
- **影响下游：** M5 L2（`noise_sigma = 0` 时残差检查公式除零）
- **Stage3 建议：** `noise={}` 意为零噪声，跳过噪声抽样，L2 改用 `residuals.std() < 1e-6`

### NC7: Realism 与模式信号交互 — **P2** 🟡

- **阻塞原因：** Stage δ 可向模式目标单元格注入 NaN，破坏模式信号致 L3 失败
- **代码状态：** 无保护——`inject_realism()` 不接收 `pattern_mask` 参数（📍 `realism.py:25-30`），`inject_patterns()` 不返回 mask（📍 `patterns.py:29`），`generator.py` 不传递掩码
- **影响下游：** M5 L3
- **Stage3 建议：** realism 跳过被模式修改的单元格（需 pattern_mask），或先校验后注入 realism
- **🔄 Loop B 关联：** 如果 realism 破坏了模式信号导致 L3 失败，auto-fix 的 `amplify_magnitude` 策略无法修复（因为问题在 realism 阶段而非模式阶段）

### NC8: `_build_schema_metadata()` 归属 — **P2** 🟡

- **阻塞原因：** §2.8 在 M2 的 `generate()` 内构建 metadata，但 Stage1 定义 M4 为独立模块
- **代码状态：** **已解决** — M4 是独立函数 `phase_2.metadata.builder.build_schema_metadata()`，由 M2 在 return path 调用（📍 `generator.py:102-126`）
- **影响下游：** M4、M5
- **Stage3 建议：** 与代码一致——M4 standalone 函数，M2 调用，保持边界清晰

---

## 实现细节（规范未覆盖的辅助代码）

| 函数/常量 | 位置 | 说明 |
|---|---|---|
| `enumerate_daily_dates()` | 📍 `skeleton.py:292-298` | 生成 `[start, end]` 范围内每日日期列表 |
| `enumerate_period_dates()` | 📍 `skeleton.py:301-315` | 生成指定 weekday 的周期日期（weekly 频率） |
| `enumerate_monthly_dates()` | 📍 `skeleton.py:318-340` | 生成每月 1 日的日期列表 |
| `_get_dependency_for_root()` | 📍 `skeleton.py:385-397` | 通过 `child_root` 名称查找 `GroupDependency` |
| `FREQ_MAP` | 📍 `skeleton.py:256` | SDK 频率码 → 引擎名映射 `{"D":"daily","MS":"monthly"}` |
| `perturb_string()` | 📍 `realism.py:166-204` | 字符级扰动：swap / delete / insert 三选一 |
| `inject_missing_values()` | 📍 `realism.py:67-99` | 全列均匀 NaN 注入（独立概率 mask） |
| `inject_dirty_values()` | 📍 `realism.py:102-163` | 仅分类列，逐单元格调用 `perturb_string()` |
| 延迟导入（γ/δ） | 📍 `generator.py:93,98` | 避免循环导入的 `from ... import` 在函数体内 |
| measure_order 提取 | 📍 `generator.py:106-113` | 从 full_dag 中提取度量子 DAG 排序供 metadata 使用 |
