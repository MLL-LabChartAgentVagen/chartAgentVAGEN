# M4: Schema Metadata — 模块画像

## 一句话职责

将 M1 的声明存储（Declaration Store）投影为一份结构化的 7-key 元数据字典，作为 Phase 2 与下游（M5 校验引擎、Phase 3 视图生成）之间的机器可读契约。

## 实现状态：6 / 9（67%）

## 在流水线中的位置

```
M1 (SDK Surface) ──declaration store──► M4 (Schema Metadata) ──schema_metadata dict──► M5 (Validation Engine)
                                                                                        ──► Phase 3
```

M4 与 M2 从同一份冻结的 declaration store 读取，可并行执行。M4 必须在 M5 开始前完成。在 Loop B（M5→M2 自动修复重试）中，M4 无需重新运行——声明未变，元数据不变。

## 构建顺序中的位置

第 2 步。前置依赖：`types.py`（`DimensionGroup`, `OrthogonalPair`, `GroupDependency` 三个数据类）+ M1（提供 declaration store 数据）。

```
types.py + exceptions.py → M1(SDK) → **M4(Metadata)** → M2(Engine) → M5(Validation) → M3(Orchestration)
```

---

## 已实现功能详解（SPEC_READY）

### 1. 顶层 `schema_metadata` 7-key 结构

**规范定义（§2.6）：** `schema_metadata` 是一个包含 7 个顶层键的 dict，编码生成表的完整语义——维度分组、正交关系、组间依赖、列描述、度量 DAG 序、模式注入、目标行数。

**代码实现：** 📍 [phase_2/metadata/builder.py:23-111](phase_2/metadata/builder.py#L23-L111) — `build_schema_metadata()`

函数接收 6 个已拆解的参数（`groups`, `orthogonal_pairs`, `target_rows`, `measure_dag_order`, `columns`, `group_dependencies`, `patterns`），按固定顺序组装 7 个键，最后调用 `_assert_metadata_consistency()` 做后置校验。三个可选参数（`columns`, `group_dependencies`, `patterns`）缺省时填空容器。

**生动类比：** 如果 M1 是一位建筑师画好了蓝图（declaration store），M4 就是那个把蓝图拍照、标注、装订成册交给验收团队的人。它不建造任何东西，只是把"系统应该长什么样"翻译成一份标准化的说明书。

**💡 为什么这样设计？** M4 作为独立模块而非 M2 内部方法，是为了保持模块边界清晰——M5 只消费元数据 dict，不直接访问 DeclarationStore，避免校验引擎与 SDK 内部实现耦合。

### 2. `dimension_groups` 结构

**规范定义（§2.6）：** `{group_name: {columns: [...], hierarchy: [...]}}` — 每个维度组的列清单和根优先的层次链。temporal 组的 `hierarchy` 仅含根时间列，`columns` 包含衍生列。

**代码实现：** 📍 [builder.py:59-63](phase_2/metadata/builder.py#L59-L63) 遍历 `groups` dict，对每个 `DimensionGroup` 调用 `to_metadata()`。
📍 [types.py:59-73](phase_2/types.py#L59-L73) — `DimensionGroup.to_metadata()` 返回 `{"columns": list(...), "hierarchy": list(...)}`，做防御性 list 拷贝。

temporal 组的特殊处理（hierarchy 只含 root）由 `DimensionGroup` 对象在构建时决定，`to_metadata()` 忠实反映内部状态，不做额外逻辑。

**类比：** 像公司的组织架构图——`columns` 是"这个部门有哪些人"，`hierarchy` 是"谁向谁汇报"的链条。temporal 组比较特殊：衍生列（`day_of_week`, `month`）是从根时间列自动计算出来的，不算"汇报链"的层级。

### 3. `orthogonal_groups` — 1:1 映射

**规范定义（§2.6）：** `[{group_a, group_b, rationale}, ...]` — 声明两个组统计独立的列表，直接从 `declare_orthogonal()` 透传。

**代码实现：** 📍 [builder.py:66-68](phase_2/metadata/builder.py#L66-L68) — 列表推导调用 `OrthogonalPair.to_metadata()`。
📍 [types.py:139-151](phase_2/types.py#L139-L151) — 返回 `{"group_a": ..., "group_b": ..., "rationale": ...}`。纯透传，零转换。

`OrthogonalPair` 本身实现了顺序无关的 `__eq__`/`__hash__`（📍 [types.py:111-137](phase_2/types.py#L111-L137)，使用 `frozenset`），但 `to_metadata()` 保留原始声明顺序（`group_a` 始终是第一个声明的组）。

### 4. `columns` 类型区分描述符

**规范定义（§2.6）：** 按列类型（categorical / temporal / measure）携带不同字段的描述符集合。§2.6 示例仅包含稀疏字段（如 categorical 只有 `cardinality`），但 P0 enrichment 决策要求包含 M5 校验所需的全部字段。

**代码实现：** 📍 [builder.py:78-83](phase_2/metadata/builder.py#L78-L83)（入口）→ 📍 [builder.py:114-175](phase_2/metadata/builder.py#L114-L175) — `_build_columns_metadata()`

按 `col_meta["type"]` 四路分支：

| 类型 | 包含字段 | 代码行 |
|---|---|---|
| `categorical` | `values`, `weights`, `cardinality`(=len(values)), `group`, `parent` | [L138-143](phase_2/metadata/builder.py#L138-L143) |
| `temporal` | `start`, `end`, `freq`, `derive`, `group` | [L145-150](phase_2/metadata/builder.py#L145-L150) |
| `temporal_derived` | `derivation`, `source`, `group` | [L152-155](phase_2/metadata/builder.py#L152-L155) |
| `measure` (stochastic) | `measure_type`, `family`, `param_model`（深拷贝） | [L157-165](phase_2/metadata/builder.py#L157-L165) |
| `measure` (structural) | `measure_type`, `formula`, `effects`(dict-of-dict 拷贝), `noise`(dict 拷贝) | [L166-171](phase_2/metadata/builder.py#L166-L171) |

stochastic measure 的 `param_model` 深拷贝委托给 📍 [builder.py:178-191](phase_2/metadata/builder.py#L178-L191) `_deep_copy_param_model()`，处理嵌套 effects dict。

**💡 为什么这样设计？** 防御性拷贝（defensive copy）贯穿全函数——每个 list 用 `list()` 拷贝，每个 dict 用 `dict()` 或手动遍历拷贝。这是为了确保返回的 metadata dict 与 declaration store 完全解耦，任何一方的后续修改不会意外影响另一方。

**规范偏差（两边都报告）：**
1. §2.6 规范的 `columns` 是**列表**（每个元素含 `name` 字段），代码实现为 **dict**（列名作 key，描述符不含 `name`）。
2. §2.6 structural measure 含 `depends_on` 字段，代码用 `formula`/`effects`/`noise` 替代但未保留 `depends_on`。
3. 代码新增了 `temporal_derived` 类型（§2.6 未定义），作为衍生时间列的独立类型。

### 5. `measure_dag_order` — 拓扑排序列表

**规范定义（§2.6）：** M1 计算的 measure DAG 拓扑序的直接透传，flat list。

**代码实现：** 📍 [builder.py:85](phase_2/metadata/builder.py#L85) — `metadata["measure_dag_order"] = list(measure_dag_order)`。一次 `list()` 拷贝，防御性设计。拓扑排序本身由 M1 的 DAG 模块计算，M4 不参与排序逻辑。

### 6. `total_rows` — 标量透传

**规范定义（§2.6）：** 构造函数的 `target_rows` 参数，声明的目标行数（非实际生成行数）。

**代码实现：** 📍 [builder.py:102](phase_2/metadata/builder.py#L102) — `metadata["total_rows"] = target_rows`。直接赋值，零转换。

---

## 接口契约（已实现的）

### 唯一公共接口：`build_schema_metadata()`

**契约描述：**
- **输入：** `groups`(dict[str, DimensionGroup]), `orthogonal_pairs`(list[OrthogonalPair]), `target_rows`(int), `measure_dag_order`(list[str]), 以及可选的 `columns`(OrderedDict), `group_dependencies`(list[GroupDependency]), `patterns`(list[dict])
- **输出：** `dict[str, Any]` — 含 7 个顶层键的元数据字典
- **调用时机：** 在 M1 声明完成后、M5 校验开始前。由 `FactTableSimulator.generate()` 在返回路径上调用（stage4 设计）。在 Loop B 重试中不重新运行。
- **副作用：** 调用 `_assert_metadata_consistency()` 做后置校验（仅 warning 级日志），无异常抛出。

**代码入口点：** 📍 [builder.py:23](phase_2/metadata/builder.py#L23) — `def build_schema_metadata(groups, orthogonal_pairs, target_rows, measure_dag_order, columns=None, group_dependencies=None, patterns=None) -> dict[str, Any]`

### 类型依赖（来自 types.py）

| 类型 | 位置 | M4 使用方式 |
|---|---|---|
| `DimensionGroup` | [types.py:28-81](phase_2/types.py#L28-L81) | 调用 `.to_metadata()` 序列化为 `{columns, hierarchy}` |
| `OrthogonalPair` | [types.py:88-171](phase_2/types.py#L88-L171) | 调用 `.to_metadata()` 序列化为 `{group_a, group_b, rationale}` |
| `GroupDependency` | [types.py:179-225](phase_2/types.py#L179-L225) | 调用 `.to_metadata()` 序列化为 `{child_root, on, conditional_weights}` |

---

## 关键约束与不变量

1. **元数据不可变性：** 返回的 dict 中所有集合类型（list, dict）均为防御性拷贝，与源数据解耦。
2. **声明完备性前提：** M4 假设 M1 的所有声明已完成且通过内部校验。不做重复校验（如 DAG 无环性）。
3. **幂等性：** 同一份 declaration store 输入，多次调用产出相同结果。
4. **无 DataFrame 依赖：** M4 不需要也不接收 M2 生成的 DataFrame，可与 M2 并行。
5. **内部一致性约束（隐式）：**
   - `dimension_groups` 中的每个列名必须在 `columns` 中存在
   - `measure_dag_order` 中的每个名称必须在 `columns` 中存在且为 measure 类型
   - 每个 pattern 的 `col` 必须指向 measure 列
   - 每个 `orthogonal_groups` 的组名必须在 `dimension_groups` 中存在

---

## 反馈回路参与

M4 本身不直接参与任何反馈回路。但间接相关：

- **Loop B（M5→M2）：** M5 使用 M4 产出的 `schema_metadata` 作为"期望值契约"来校验 M2 的输出。当校验失败触发 Loop B 重试时，M2 用新 seed 重新生成 DataFrame，但 M4 不重新运行——因为声明未变，元数据不变。
- **隐含假设：** Loop B 的 auto-fix 策略仅调整生成参数，不修改声明。如果 auto-fix 修改了声明，M4 需要重新运行，但当前设计不支持这一路径。

---

## TODO 地图（NEEDS_CLAR）

### 🚧 TODO: P0 — Lossy Projection / 元数据 Enrichment

- **阻塞原因：** §2.6 示例是 lossy projection，省略了 M5 L1/L2/L3 校验所需的 `values`/`weights`、完整 `param_model`、`formula`/`effects`/`noise`、`conditional_weights`、完整 pattern `params`。
- **在代码中的当前状态：** **已实现。** `_build_columns_metadata()` 包含全部 enriched 字段；`GroupDependency.to_metadata()` 包含 `conditional_weights`；patterns 包含完整 `params`。docstring 明确标注 "Enriched beyond §2.6 example"。
- **影响的下游模块：** M5 全部三层校验（L1 需 `values`/`weights`，L2 需 `param_model`/`formula`/`noise`/`conditional_weights`，L3 需 pattern `params`）。
- **stage3 建议：** 将 §2.6 示例视为示意性而非穷举，enrichment 所有 M5 引用的字段。**已采纳。**

### 🚧 TODO: P1 — M4 是否需要 DataFrame 输入

- **阻塞原因：** stage1 列出 "Declaration store + generated DataFrame" 作为 M4 输入，但 §2.6 无字段需要行数据。
- **在代码中的当前状态：** **已解决。** 函数签名无 DataFrame 参数。
- **影响的下游模块：** 影响 M2∥M4 并行调度能力（已解除）。
- **stage3 建议：** M4 不需要 DataFrame，从 declaration store 构建，允许与 M2 并行。**已采纳。**

### 🚧 TODO: P2 — Metadata 内部一致性校验

- **阻塞原因：** 未规定 `schema_metadata` 自检逻辑。
- **在代码中的当前状态：** **已实现，但行为偏差。** `_assert_metadata_consistency()` 📍 [builder.py:194-251](phase_2/metadata/builder.py#L194-L251) 执行 4 项交叉引用检查（维度组列存在性、DAG 序列存在性、pattern col 为 measure、正交组引用有效组名）。但 docstring 声明 `raises ValueError`，实际使用 `logger.warning` — 不一致时仅记录日志，不中断执行。
- **影响的下游模块：** M5（可能接收内部不一致的元数据）。
- **stage3 建议：** 实现 `_assert_metadata_consistency()` 验证交叉引用。**已部分采纳**——校验逻辑已实现，但未按设计抛出异常。

---

## 实现细节（规范未覆盖的辅助代码）

| 函数 | 位置 | 用途 |
|---|---|---|
| `_build_columns_metadata()` | [builder.py:114-175](phase_2/metadata/builder.py#L114-L175) | 从 column registry 按类型分支构建描述符 dict，是 Key 4 的核心实现 |
| `_deep_copy_param_model()` | [builder.py:178-191](phase_2/metadata/builder.py#L178-L191) | 对 stochastic measure 的 `param_model` 做递归深拷贝，处理嵌套 `effects` dict |
| `_assert_metadata_consistency()` | [builder.py:194-251](phase_2/metadata/builder.py#L194-L251) | 后置校验：4 项交叉引用检查（已在 TODO 地图中分析） |

---

## 规范偏差汇总

| # | 偏差描述 | 规范侧 | 代码侧 |
|---|---|---|---|
| 1 | 函数签名 | stage4: `build_schema_metadata(store: DeclarationStore) → dict` | 实际接收 6 个拆解参数，非单一 store 对象 |
| 2 | `columns` 数据结构 | §2.6: 列表 (list of descriptors with `name` field) | dict (name → descriptor, 无 `name` 字段) |
| 3 | structural measure `depends_on` | §2.6: 包含 `depends_on` 字段 | 缺失，用 `formula`/`effects`/`noise` 替代 |
| 4 | `temporal_derived` 类型 | §2.6: 未定义此类型 | 新增为衍生时间列的独立类型 |
| 5 | 一致性校验行为 | stage4: `raises ValueError` | 实际 `logger.warning`，不抛异常 |
