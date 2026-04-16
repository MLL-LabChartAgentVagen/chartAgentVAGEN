# M1: SDK Surface — 模块画像

## 一句话职责

M1 是面向 LLM 的**类型安全建造者模式 API**——它接受列声明、维度组结构、度量定义和关系/模式声明，在声明时逐步验证，最终输出一个冻结的 declaration store 供下游 M2（生成）和 M4（元数据）消费。

## 实现状态：12/23（52%）

12 项 SPEC_READY 已完整实现；11 项 NEEDS_CLAR 以不同状态存在于代码中（4 项已自行实现合理方案，4 项为 stub/pass-through，3 项缺失或部分缺失）。

## 在流水线中的位置

```
Phase 1 → M3(LLM Orchestration) → 【M1: SDK Surface】→ M2(Generation Engine) + M4(Schema Metadata) → M5(Validation) → Phase 3
                                      ↑               │
                                      └── Loop A ──────┘
                                       typed exception
```

- **上游：** M3 生成的 Python 脚本在沙箱中执行，脚本中的 `add_*()` / `declare_*()` / `inject_*()` 调用触发 M1
- **下游：** 冻结的 declaration store 分发给 M2（生成 DataFrame）和 M4（构建 schema_metadata）
- **反馈：** 验证失败时抛出类型化异常回传 M3，触发 Loop A 重试

## 构建顺序中的位置

**第 2 步**（共 6 步），前置依赖：`types.py` + `exceptions.py`

```
types.py + exceptions.py ✅ → 【M1(SDK)】→ M4(Metadata) → M2(Engine) → M5(Validation) → M3(Orchestration)
```

M1 是构建顺序中第一个真正的"业务模块"。它只依赖共享数据类型（`DimensionGroup`, `OrthogonalPair`, `GroupDependency` 等）和异常层级——这些已在 types profile 中精读完毕。

---

## 已实现功能详解（SPEC_READY）

### SR-1: `FactTableSimulator` 构造器

> 如果 M1 是一家建筑事务所，构造器就是"开工会议"——你确定了这张图纸要画多少行（`target_rows`）、用什么随机种子（`seed`），然后摊开一张空白蓝图桌，准备接受后续的每一笔声明。

**规范定义（§2.1）：** 两参数构造函数 `FactTableSimulator(target_rows, seed)` 创建空的内部注册表。

**代码实现：**
- 📍 `phase_2/sdk/simulator.py:28-51`
- `__init__(self, target_rows: int, seed: int = 42)` 验证 `target_rows` 是正整数（排除 bool），`seed` 是整数
- 初始化 7 个注册表：`_columns`（OrderedDict）、`_groups`（dict of DimensionGroup）、`_orthogonal_pairs`、`_group_dependencies`、`_patterns`、`_realism_config`（None）、`_measure_dag`
- 类本身是**轻量委托壳**——所有 `add_*` 方法 (line 53-128) 都是 one-liner 转发到 `columns.py` 和 `relationships.py`

💡 **为什么这样设计？** 将验证和注册逻辑从 `simulator.py` 拆到独立模块，让 `FactTableSimulator` 只做 API facade。这样每个独立函数可以接受显式参数（无 `self`），更易测试、更符合函数式风格。

---

### SR-2: `add_category()` — 分类列声明

> 想象你在设计一个问卷调查的下拉菜单。`add_category` 就是在说："这个字段叫 hospital，可选值有 General/Teaching/Specialist，出现概率分别是 40%/35%/25%，它属于 entity 这个维度组。" 如果这个字段还有父字段（如 hospital 下面的 department），那每个医院可以有不同的部门概率分布。

**规范定义（§2.1.1）：** 分类列注册，支持自动归一化、空值拒绝、parent 验证、flat-list 广播 vs per-parent dict 条件分支。

**代码实现：**
- 📍 `phase_2/sdk/columns.py:38-121`（主函数）
- 验证链：`validate_column_name` → 空值检查 → parent 检查 → 权重分支
- **关键分支**（line 76-88）：`isinstance(weights, dict)` 时 → per-parent 路径（要求 parent 非 None，调用 `validate_and_normalize_dict_weights`）；否则 → flat list 路径（`validate_and_normalize_flat_weights`）
- 归一化在 📍 `phase_2/sdk/validation.py:112-163`（flat）和 `validation.py:166-223`（dict）
- 额外防御：root 不允许 per-parent dict（line 77-81）、"time" 组名保留（line 91-95）、每组仅一个 root（line 98-103，抛 `DuplicateGroupRootError`）
- 注册：`col_meta = {"type": "categorical", "values": [...], "weights": normalized, "group": ..., "parent": ...}` 进入 `columns` OrderedDict + `_groups.register_categorical_column()` 更新组图

💡 **为什么这样设计？** 权重归一化在声明时完成（而非生成时），是一种"前移验证"策略——错误越早发现，LLM 在 Loop A 中就能越快修正。Per-parent dict 的完全覆盖要求（所有 parent 值必须出现）也是同一思路。

---

### SR-3: `add_temporal()` — 时序列与派生特征

> 时序列就像给你的数据表装了一个日历。你说"从 2023-01-01 到 2024-12-31，按月"，它就帮你铺好日期轴。更妙的是，你可以说 `derive=["month", "quarter"]`，它就自动从日期中提取月份和季度，作为独立列进入注册表——后续度量可以直接拿 `month` 当预测器。

**规范定义（§2.1.1）：** 时间列 + 4 种日历派生特征（`day_of_week`, `month`, `quarter`, `is_weekend`），派生列作为真实列可供度量的 effects 使用。

**代码实现：**
- 📍 `phase_2/sdk/columns.py:124-211`
- 验证：列名唯一 → ISO 日期解析（`_parse_iso_date`，line 324-345）→ `start < end` → `freq` 在有效集合 `{"D", "W-MON"..."W-SUN", "MS"}` → `derive` 项在 `TEMPORAL_DERIVE_WHITELIST` 内
- Root 列注册为 `type="temporal"`，group 固定为 `"time"`
- 每个派生特征自动命名为 `{name}_{d}`（如 `date_month`），注册为 `type="temporal_derived"`，记录 `source` 和 `derivation`
- 组注册：`_groups.register_temporal_group()` → `hierarchy=[root_col]`（仅含 root，派生列不进 hierarchy）

💡 **为什么这样设计？** 派生列与普通分类列同等对待（都在 column_registry 中），意味着度量的 `effects` 可以直接引用 `date_month` 作为预测器，不需要特殊路径。这是"一切皆列"的统一设计。

---

### SR-4: `add_measure()` — 随机根度量

> 随机根度量就像一个可调节的骰子。基础面值（`intercept`）是固定的，但根据你面前的卡片（分类列的值），可以给骰子加减偏移量（`effects`）。比如："`wait_minutes` 的均值 μ 基础是 36.5，如果 severity='Severe' 就加 12.0，如果 hospital='Teaching' 就加 3.0"——这就是 θⱼ = β₀ + Σₘ βₘ(Xₘ) 的含义。

**规范定义（§2.1.1 + §2.3）：** 随机根度量注册，支持 "simple"（常数参数）和 "full"（intercept+effects）两种 `param_model` 形式，θⱼ = β₀ + Σₘ βₘ(Xₘ)。支持 8 种分布族。

**代码实现：**
- 📍 `phase_2/sdk/columns.py:214-250`（主函数）
- 📍 `phase_2/sdk/validation.py:294-399`（param_model 验证链）
- 验证：列名唯一 → `family` 在 `SUPPORTED_FAMILIES`（8 族） → `validate_param_model`
- `validate_param_model` 分派到 `validate_param_value`：
  - **Case A**（数值标量）：常数参数，直接通过
  - **Case B**（dict with `intercept` + optional `effects`）：验证 intercept 是数值，effects 中每个键是已声明的分类列名且值集完全匹配
- 只有 gaussian/lognormal 有严格的必需键验证（`mu`, `sigma`），其他族的 param keys 不做白名单检查
- 注册为 `{"type": "measure", "measure_type": "stochastic", "family": ..., "param_model": ...}`
- **不产生 DAG 边**——随机根度量是 DAG 的叶节点（无入边）

💡 **为什么这样设计？** 只验证 gaussian/lognormal 的参数键名，是因为规范只给出了这两个族的具体示例。对其余族保持开放，避免过度约束——但代价是拼写错误（如 `mu` 写成 `mean`）不会在声明时被捕获。

---

### SR-5: `add_measure_structural()` — 结构度量与 DAG 边提取

> 结构度量就像 Excel 中引用其他单元格的公式。你写 `formula="wait_minutes * 2.5 + severity_surcharge"`，SDK 就知道：(1) `wait_minutes` 是上游度量——建立 DAG 边；(2) `severity_surcharge` 是一个效果名——去 `effects` 字典里查它对 severity 各值的数值定义；(3) 最终值 = 公式结果 + 可选噪声。

**规范定义（§2.1.1）：** 结构度量注册，公式符号必须全部解析，自动提取 DAG 边。

**代码实现：**
- 📍 `phase_2/sdk/columns.py:253-321`
- 公式符号提取：`extract_formula_symbols()` 📍 `validation.py:554-561` 用正则 `[a-zA-Z_][a-zA-Z0-9_]*`
- 符号解析（line 285-292）：在 effects 键中 → 跳过；在 columns 中且 type="measure" → 加入 `measure_deps`；其他 → **静默跳过**
- Effects 验证：`validate_structural_effects()` 📍 `validation.py:467-547` — 每个 effect name 必须在公式中出现，内层 dict 键必须匹配某分类列值集
- DAG 环检测：`check_measure_dag_acyclic()` 📍 `dag.py:379-410` — 构建临时邻接表 + 环检测
- 注册后更新 `measure_dag`：`measure_dag[dep].append(name)` 建立 upstream → downstream 边

💡 **为什么这样设计？** 公式中未匹配的符号被静默跳过而不报错——这是为了容忍 Python 关键字（如 `max`、`min`）和数值常量可能被正则匹配为标识符。实际的 "every symbol must resolve" 约束推迟到运行时公式求值器。这是声明时宽松 + 运行时严格的策略。

---

### SR-6: `declare_orthogonal()` — 组级独立性声明

> 正交声明就像公司里两个部门签了一份"互不干涉条约"：entity 组（医院/部门）和 patient 组（严重度/支付方式）的行为完全独立。声明了这个之后，(1) 生成时用 P(A) × P(B) 独立采样，(2) 验证时 M5 会用 χ² 检验确认独立性，(3) Phase 3 用它设计"正交对比"仪表盘。

**规范定义（§2.1.2）：** 组级独立性断言，传播到所有跨组列对。

**代码实现：**
- 📍 `phase_2/sdk/relationships.py:39-92`
- 验证：两组存在 → 不同名 → 无依赖冲突（`_check_dependency_conflict`，line 322-343）→ 无重复声明
- `OrthogonalPair` 数据类（📍 `types.py:87-171`）使用 `frozenset` 实现**顺序无关等价性**：`OrthogonalPair("A","B") == OrthogonalPair("B","A")`
- 追加到 `orthogonal_pairs` 列表

💡 **为什么这样设计？** 冲突检测是双向的：`declare_orthogonal` 检查是否已有依赖，`add_group_dependency` 也检查是否已声明正交。这种"互斥锁"设计确保两种矛盾声明无论先后顺序都会被拒绝。

---

### SR-7: `add_group_dependency()` — 跨组条件依赖（单列 `on`）

> 组依赖就像说"支付方式的分布取决于你去的是哪家医院"。你给出一张条件概率表：General 医院 → Insurance 45% / Self-pay 45% / Government 10%；Teaching 医院 → 不同的分布……SDK 在声明时就验证这张表的完整性和合法性。

**规范定义（§2.1.2）：** 根列条件分布，root-only 约束 + DAG 验证 + 权重归一化。

**代码实现：**
- 📍 `phase_2/sdk/relationships.py:95-196`
- 验证链：child_root 和 on 列均为 root（`is_group_root()`）→ 正交冲突检查 → 根 DAG 无环（`check_root_dag_acyclic()`，📍 `dag.py:413-451`）→ conditional_weights 覆盖所有 parent 值 + 每行覆盖所有 child 值 → 每行归一化
- **仅使用 `on[0]`**（line 132, 139, 143）—— 单列条件的完整实现
- 注册为 `GroupDependency`（📍 `types.py:178-225`）追加到 `group_dependencies`

---

### SR-8: `inject_pattern()` — 模式注入（`outlier_entity` & `trend_break`）

> 模式注入就像在完美的模拟数据中"种下"故意的异常信号。`outlier_entity` 说"让 General Hospital 的 wait_minutes z-score ≥ 2.0"；`trend_break` 说"在 2024-06 之后让 revenue 跳升 30%"。这些是给 Phase 3 QA 仪表盘设计的"预埋答案"。

**规范定义（§2.1.2 + §2.9 L3）：** 两种完全规范的模式类型注册，参数 schema 清晰。

**代码实现：**
- 📍 `phase_2/sdk/relationships.py:199-257`
- 验证：type 在 `VALID_PATTERN_TYPES`（全部 6 种接受）→ col 存在且为 measure → 对 `outlier_entity` 要求 `z_score`、对 `trend_break` 要求 `break_point` + `magnitude`（`PATTERN_REQUIRED_PARAMS`，line 33-36）
- 存储为 `{"type", "target", "col", "params"}` dict 追加到 `patterns`

---

### SR-9: 声明时验证规则集

> M1 的验证器就像建筑审批的四关检查：(1) 图纸名称不能重复；(2) 你引用的父结构必须真实存在；(3) 跨区域依赖只能在"一楼大厅"（root 列）之间建立；(4) 依赖关系不能画成环。每一关失败都会生成一张带详细描述的"整改通知单"（类型化异常），通过 Loop A 交给 LLM 修正。

**规范定义（§2.1.1, §2.1.2）：** 四类声明时验证器 + 对应类型化异常。

**代码实现：** 📍 `phase_2/sdk/validation.py` 全文 + `dag.py` 环检测部分

| 规范规则 | 验证函数 | 位置 | 异常 |
|---|---|---|---|
| DAG 无环 | `detect_cycle_in_adjacency()` + `check_measure_dag_acyclic()` + `check_root_dag_acyclic()` | `dag.py:33-102`, `dag.py:379-451` | `CyclicDependencyError` |
| Parent 存在+同组 | `validate_parent()` | `validation.py:78-105` | `ParentNotFoundError` |
| Root-only 约束 | `validate_root_only()` | `validation.py:568-585` | `NonRootDependencyError` |
| 公式符号解析 | `extract_formula_symbols()` + `validate_structural_effects()` | `validation.py:554-561`, `validation.py:467-547` | `UndefinedEffectError` |
| 列名唯一（扩展） | `validate_column_name()` | `validation.py:57-71` | `DuplicateColumnError` |
| 空值拒绝（扩展） | 内联在 `add_category()` | `columns.py:67-68` | `EmptyValuesError` |
| 权重长度匹配（扩展） | `validate_and_normalize_flat_weights()` | `validation.py:137-142` | `WeightLengthMismatchError` |
| 分布族白名单（扩展） | `validate_family()` | `validation.py:274-287` | `ValueError` |
| 效果预测器存在（扩展） | `validate_effects_in_param()` | `validation.py:402-460` | `UndefinedEffectError` |

💡 **为什么这样设计？** 代码实现了 9 种验证（超出规范命名的 4 种），因为 M1 是 LLM 代码质量的**第一道防线**。Loop A 的 3 次重试预算很紧张——每次只能看到一个异常，所以每种可能的声明错误都需要精准的类型化异常和描述性消息，让 LLM 在一次重试中就能定位问题。

---

### SR-10: 维度组抽象

> 维度组就像公司的组织架构图。每个组有一个"组长"（root 列，如 hospital），下面可以有"组员"（child 列，如 department），他们的行为取决于组长。组与组之间要么独立（正交），要么有条件依赖。时间组是个特殊角色——它的"组员"（month、quarter 等）不是层级关系，而是从日期直接计算出来的。

**规范定义（§2.2）：** `{columns, hierarchy}` per group，root-first 层次，temporal 作为特殊组处理。

**代码实现：**
- 📍 数据类：`types.py:27-80`（`DimensionGroup` with `name`, `root`, `columns`, `hierarchy`）
- 📍 注册逻辑：`groups.py:20-55`（`register_categorical_column`）——按需创建组，设置 root，追加到 columns/hierarchy
- 📍 时序特殊处理：`groups.py:57-81`（`register_temporal_group`）——`columns` 含 root+派生，`hierarchy` **仅含 root**
- 📍 查询辅助：`groups.py:84-95`（`get_roots`）、`groups.py:98-122`（`is_group_root`）

---

### SR-11: Measure DAG 拓扑排序

> 拓扑排序就像决定做菜的顺序：你不能在煮面条之前加酱料——如果 `cost = f(wait_minutes)`，那 `wait_minutes` 必须先生成。Kahn 算法从零入度的"原料"（根度量）开始，每完成一道菜就释放下游依赖。当出现环路时（`cost → satisfaction → cost`），算法检测到并报告精确的环路径。

**规范定义（§2.3）：** `measure_dag_order` 为度量边集的拓扑排序。

**代码实现：**
- 📍 `dag.py:105-155`（`topological_sort`）——Kahn 算法 + **min-heap 字典序 tie-breaking** 保证确定性
- 📍 `dag.py:158-190`（`extract_measure_sub_dag`）——从完整 DAG 过滤出度量子图
- 📍 `dag.py:197-293`（`build_full_dag`）——从 5 种边源组装统一 DAG：
  1. 组内层级（parent → child）
  2. 跨组根依赖（on → child_root）
  3. 时序派生（root → derived）
  4. 度量预测器引用（效果预测器 → 度量）
  5. 度量间公式引用（upstream measure → downstream measure）
- 组装完成后做**防御性环检测**（line 283-285）

💡 **为什么这样设计？** `build_full_dag` 合并了声明阶段的增量边和生成阶段需要的完整依赖图。5 种边源中第 4 种（度量预测器引用）是规范未显式列出的——代码补充了"分类列作为度量效果预测器"所隐含的生成顺序依赖，确保预测器列在度量列之前被生成。

---

### SR-12: `set_realism()` — 数据仿真噪声配置

> Realism 就像给一幅完美的照片加上滤镜：`missing_rate=0.02` 随机删除 2% 的数据（变成 NaN），`dirty_rate=0.01` 随机篡改 1% 的分类值。这让模拟数据更接近真实世界——毕竟真实数据总有缺失和脏值。

**规范定义（§2.1.2）：** 接受并存储 `missing_rate`, `dirty_rate`, `censoring` 参数。

**代码实现：**
- 📍 `relationships.py:260-299`（函数）——验证 missing_rate/dirty_rate ∈ [0,1]，返回 config dict
- 📍 `simulator.py:120-128`（委托）——`self._realism_config = _rels_api.set_realism([], ...)`

---

## 接口契约（已实现的）

### 入口契约：LLM 脚本 → M1

| 契约 | 入口点 | 调用时机 |
|---|---|---|
| LLM 脚本实例化 `FactTableSimulator(target_rows, seed)` | 📍 `simulator.py:32` | 脚本开头 |
| Step 1: 列声明 `add_category/add_temporal/add_measure/add_measure_structural` | 📍 `simulator.py:53-89` → `columns.py` | 脚本中部 |
| Step 2: 关系声明 `declare_orthogonal/add_group_dependency/inject_pattern/set_realism` | 📍 `simulator.py:91-128` → `relationships.py` | 脚本中部 |
| 生成触发 `sim.generate()` | 📍 `simulator.py:130-141` | 脚本末尾 |

**输入 →** 合法的 Python 方法调用序列
**输出 →** 成功：冻结的内部注册表传递给 M2/M4 | 失败：类型化异常传递给 M3

### 出口契约：M1 → 下游

| 消费者 | 输出内容 | 代码路径 |
|---|---|---|
| **M2（Generation Engine）** | `self._columns`, `self._groups`, `self._group_dependencies`, `self._measure_dag`, `self._patterns`, `self._realism_config`, `target_rows`, `seed` | 📍 `simulator.py:131-140` → `_generator_api.run_pipeline(...)` |
| **M4（Schema Metadata）** | 同上（排除 patterns/realism） | 📍 `simulator.py:143-152` → `_metadata_api.build_schema_metadata(...)` |
| **M3（Loop A 反馈）** | `SimulatorError` 子类（含 `message` 属性） | 异常冒泡回 M3 沙箱 |

### 异常契约（M1 → M3）

| 异常类型 | 触发场景 | 消息示例 |
|---|---|---|
| `CyclicDependencyError` | 度量 DAG 或根 DAG 有环 | `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."` |
| `UndefinedEffectError` | 效果引用未定义的分类值 | `"'severity_surcharge' in formula has no definition for 'Severe'."` |
| `NonRootDependencyError` | 跨组依赖引用非根列 | `"'department' is not a group root; cannot use in add_group_dependency."` |
| `DuplicateColumnError` | 列名重复 | `"Column 'hospital' is already declared."` |
| `EmptyValuesError` | values 列表为空 | `"Column 'status' has an empty values list."` |
| `ParentNotFoundError` | parent 不存在或不同组 | `"Parent 'hospital' not found in group 'patient'."` |
| `WeightLengthMismatchError` | values/weights 长度不匹配 | `"Column 'hospital' has 3 values but 4 weights."` |
| `DuplicateGroupRootError` | 组内第二个 root | `"Group 'entity' already has root column 'hospital'."` |
| `InvalidParameterError` | param_model 结构错误 | `"Parameter 'mu': required param key(s) ['mu'] missing..."` |

---

## 关键约束与不变量

1. **列名全局唯一**：跨所有组、跨所有类型，column_registry 中不允许重名
2. **每组单根**：每个 DimensionGroup 恰好一个 root 列（`parent=None`）
3. **DAG 无环**：度量 DAG 和根依赖 DAG 在每次声明后增量检测，保证全程无环
4. **权重归一化**：所有 weights（flat 或 per-parent dict）在声明时归一化到 sum=1.0
5. **Root-only 跨组约束**：`add_group_dependency` 的 `child_root` 和 `on` 列必须都是组根
6. **效果值集完全匹配**：param_model 或 structural effects 中引用的分类列，其 effect dict 的键集必须与该列的 values 集合完全一致（不多不少）
7. **声明存储不可变性**：声明完成后（`generate()` 调用时），注册表语义上冻结（注：`DeclarationStore.freeze()` 已定义但 `simulator.py` 未显式调用——冻结是隐式的）

---

## 反馈回路参与

### Loop A：代码级自我修正（M3 ↔ M1）

**触发条件：** M1 的任何声明时验证失败

**M1 的角色：** 异常源——抛出类型化 `SimulatorError` 子类，携带精确的错误定位信息

**代码路径：**
1. M3 沙箱执行 LLM 脚本 → 脚本中的 `add_*()` 调用触发 M1
2. M1 验证失败 → 抛出如 `CyclicDependencyError(["cost", "satisfaction", "cost"])`
3. 异常沿调用栈冒泡回 M3 沙箱 → M3 捕获并格式化为 traceback
4. M3 将 "code + traceback" 追加到 LLM 对话 → 重新提示 → 新脚本 → 重新进入 M1
5. 最多 3 次重试（`max_retries=3`）

**已实现路径：** 所有 9 种异常类型（见上表）都有结构化的 `message` 属性，设计为 LLM 可直接理解并修正。

**NEEDS_CLAR 路径：** `_phase` 状态机未实现 → Step 1/2 顺序违反不会被捕获为异常。

### Loop B：M1 不直接参与

Loop B（M5 → M2）跳过 M1——auto-fix 策略调整参数后直接调用 `generate(seed=42+attempt)`，不重新执行声明。

---

## TODO 地图（NEEDS_CLAR）

### P0 相关

| # | 项目 | 优先级 | 阻塞原因 | 代码状态 | 影响模块 | stage3 建议 |
|---|---|---|---|---|---|---|
| — | Formula evaluation mechanism | **P0** | M1 做符号解析，但下游 M2 的 `_eval_structural` 求值器未定义 | M1 部分已实现（符号提取+DAG 边），M2 部分阻塞 | M2 | 限制性表达式求值器：仅允许 `+`, `-`, `*`, `/`, `**` |

### P1

| # | 项目 | 优先级 | 阻塞原因 | 代码状态 | 影响模块 | stage3 建议 |
|---|---|---|---|---|---|---|
| 1 | `mixture` param_model schema | **P1** | 参数结构未定义，无法实现采样 | **Stub**：accepted by `validate_family()` 但 param_model 不验证 | M2, M5 | 定义 `{"components": [{"family": ..., "weight": ..., "params": {...}}]}` |
| 6 | 4 种欠规范 pattern 类型 | **P1** | ranking_reversal/dominance_shift/convergence/seasonal_anomaly 无参数 schema | **Stub**：类型名被接受，无参数验证 | M2, M5 | 实现 ranking_reversal + dominance_shift；stub convergence + seasonal_anomaly |

### P2

| # | 项目 | 优先级 | 阻塞原因 | 代码状态 | 影响模块 | stage3 建议 |
|---|---|---|---|---|---|---|
| 2 | `scale` 参数 | **P2** | 从未定义语义 | **Dead param**：存储但无消费 | M1 内部 | 接受存储，no-op until 规范明确 |
| 4 | 正交+依赖矛盾 | **P2** | 逻辑矛盾声明无优先级 | **已实现**：双向冲突检测，raise ValueError | M2, M5 | ✅ 代码已按建议实现 |
| 5 | 多列 `on` | **P2** | 联合条件结构未展示 | **静默降级**：只用 `on[0]`，无 NotImplementedError | M2 | 限制单列 or 使用 tuple keys |
| 7 | `censoring` 参数 | **P2** | 语义未阐述 | **Pass-through**：存储为 opaque dict | M2 | 接受存储，stub 下游 |
| 8 | 列名唯一性 | **P2** | 隐含但无规则 | **已实现**：`DuplicateColumnError` | — | ✅ 代码已按建议实现 |
| 9 | Effects 引用未声明列 | **P2** | 验证时机模糊 | **已实现**：声明时验证，raise `UndefinedEffectError` | — | ✅ 代码已按建议实现 |
| 11 | Step 1/2 顺序强制 | **P2** | SDK 无状态机 | **target_rows 验证已实现**；`_phase` 状态机**缺失** | — | 加 `_phase` flag，首个 Step 2 调用时转换 |

### P3

| # | 项目 | 优先级 | 阻塞原因 | 代码状态 | 影响模块 | stage3 建议 |
|---|---|---|---|---|---|---|
| 3 | Per-parent 缺失父值 | **P3** | 回退 vs 报错无共识 | **已实现**：raise ValueError 要求完全覆盖 | M2 | ✅ 代码已按建议实现 |
| 10 | 负分布参数 | **P3** | 加性效应可能产生无效参数 | **缺失**：M1 不检查，M2 也无 clamping | M2 | 生成时 clamp 到有效范围 |

**总结：** 11 项 NEEDS_CLAR 中，4 项（#3, #4, #8, #9）代码已自行实现合理方案，4 项（#1, #2, #6, #7）为 stub/pass-through，2 项（#5 多列 on, #10 负参数）为静默降级或缺失，1 项（#11 `_phase`）部分实现。

---

## 实现细节（规范未覆盖的辅助代码）

### DAG 构建辅助 (`dag.py`)

| 函数 | 位置 | 用途 |
|---|---|---|
| `collect_stochastic_predictor_cols()` | `dag.py:300-334` | 从 param_model 的 effects 中提取预测器列名，用于 full-DAG Edge Type 4 |
| `collect_structural_predictor_cols()` | `dag.py:337-372` | 通过值集匹配将 structural effects 名映射到分类列 |
| `extract_measure_sub_dag()` | `dag.py:158-190` | 从完整 DAG 过滤度量子图 + 拓扑排序（供 M2 和 M4 使用） |

### 验证辅助 (`validation.py`)

| 函数 | 位置 | 用途 |
|---|---|---|
| `validate_and_normalize_dict_weights()` | `validation.py:166-223` | Per-parent 权重 dict 验证 + 按行归一化 |
| `normalize_weight_dict_values()` | `validation.py:226-267` | `{value: weight}` dict 归一化（用于 group dependency 权重行） |
| `validate_param_model()` / `validate_param_value()` | `validation.py:294-399` | param_model 递归验证：标量 vs intercept+effects 两种形式 |
| `validate_effects_in_param()` | `validation.py:402-460` | 随机度量 param_model 内 effects 验证 |
| `SUPPORTED_FAMILIES` / `VALIDATED_PARAM_KEYS` / `TEMPORAL_DERIVE_WHITELIST` | `validation.py:30-47` | 白名单常量 |

### 组查询辅助 (`groups.py`)

| 函数 | 位置 | 用途 |
|---|---|---|
| `is_group_root()` | `groups.py:98-122` | 判断列是否为其所属组的 root |
| `get_group_for_column()` | `groups.py:125-142` | 从列注册表查找列所属组名 |

### 日期解析 (`columns.py`)

| 函数 | 位置 | 用途 |
|---|---|---|
| `_parse_iso_date()` | `columns.py:324-345` | ISO-8601 字符串 → `datetime.date` 对象 |

### 冲突检测 (`relationships.py`)

| 函数 | 位置 | 用途 |
|---|---|---|
| `_check_orthogonal_conflict()` | `relationships.py:306-319` | 检查组对是否已声明正交（供 `add_group_dependency` 使用） |
| `_check_dependency_conflict()` | `relationships.py:322-343` | 检查组对是否已有依赖（供 `declare_orthogonal` 使用） |

### 数据类型（`types.py`，已在 types profile 中精读）

| 类型 | 位置 | M1 中的角色 |
|---|---|---|
| `DimensionGroup` | `types.py:27-80` | `_groups` 注册表的值类型 |
| `OrthogonalPair` | `types.py:87-171` | `_orthogonal_pairs` 列表元素 |
| `GroupDependency` | `types.py:178-225` | `_group_dependencies` 列表元素 |
| `DeclarationStore` | `types.py:364-409` | 设计中的统一存储容器（`simulator.py` 尚未使用，仍用直接字段） |

### 异常层级（`exceptions.py`，已在 types profile 中精读）

`SimulatorError` 基类 + 11 个子类，覆盖所有声明时验证失败场景。`PatternInjectionError` 和 `UndefinedPredictorError` 是后续 sprint 添加的扩展。
