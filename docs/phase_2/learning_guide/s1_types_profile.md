# Shared Infrastructure: `types.py` + `exceptions.py` — 模块画像

## 一句话职责

为整个 Phase 2 系统提供**零业务逻辑的纯数据定义层**——所有数据结构（声明容器、校验记录、模式配置）和类型化异常（SDK 语义错误、生成时故障、终端哨兵），供 M1–M5 全部模块导入。

## 实现状态：22/22（100%）

所有项均为 SPEC_READY。无 NEEDS_CLAR 项。Stage 3 无对应审计条目——纯数据定义，规范零歧义。

## 在流水线中的位置

```
(无上游) → types.py + exceptions.py → M1, M2, M3, M4, M5, pipeline.py (全部下游)
```

这两个文件是**被动基础设施**——不参与流水线执行，但被每一步导入。

## 构建顺序中的位置

**第 0 步**（构建顺序起点），前置依赖：**无**。

```
 ► types.py + exceptions.py   ← 当前
   → M1(SDK) → M4(Metadata) → M2(Engine) → M5(Validation) → M3(Orchestration)
```

---

## 已实现功能详解（SPEC_READY）

### 一、types.py — 数据结构层

#### T1: `DimensionGroup` — 维度组容器

- **规范定义（§2.2）：** 维度组抽象——每组有一个根列、成员列列表、根优先层级链。分类组的 hierarchy 镜像 columns；时间组的 hierarchy 仅含根列（派生列是确定性变换，非钻取层级）。
- **代码实现：** 📍 [phase_2/types.py:27-80](phase_2/types.py#L27-L80) — `@dataclass`，四字段 `name`, `root`, `columns: list[str]`, `hierarchy: list[str]`。`to_metadata()` 方法返回 §2.6 格式 `{"columns": [...], "hierarchy": [...]}`，做防御性拷贝防止外部修改内部状态。
- **生动类比：** 如果列（column）是员工，`DimensionGroup` 就是一个部门：有部门名、部门负责人（root）、全体成员名单（columns）、以及汇报链（hierarchy）。时间部门比较特殊——汇报链只有负责人自己，因为"星期几"、"季度"这些派生信息是自动计算的，不算独立岗位。
- 💡 **为什么这样设计？** `columns` 和 `hierarchy` 分开存储而非统一用一个列表，是因为时间组需要区分"谁是成员"和"谁参与层级钻取"——派生时间特征（`day_of_week`, `month` 等）属于组成员但不参与层级。

#### T2: `OrthogonalPair` — 正交独立性声明

- **规范定义（§2.1.2, §2.2）：** 两组间的统计独立性声明，顺序无关。
- **代码实现：** 📍 [phase_2/types.py:87-171](phase_2/types.py#L87-L171) — `@dataclass`，三字段 `group_a`, `group_b`, `rationale`。核心设计：`__eq__` 和 `__hash__` 基于 `frozenset` 实现**顺序无关等价**——`OrthogonalPair("entity","time") == OrthogonalPair("time","entity")`。`rationale` 不参与等价判断（同一组对不同理由视为同一声明）。辅助方法：`involves_group(name)` 检查某组是否在对中，`group_pair_set()` 返回 `frozenset` 便于高效查找。
- **生动类比：** 像婚姻登记——不管谁的名字写前面，(A,B) 和 (B,A) 是同一份登记。而 `rationale` 像结婚理由，不影响登记的法律效力。
- 💡 **为什么重写 `__eq__`/`__hash__`？** 如果不这样做，将 `OrthogonalPair` 放入 `set` 或用作 `dict` 键时，(A,B) 和 (B,A) 会被视为两份不同声明，导致重复声明无法检测、M5 的 χ² 检验重复执行。

#### T3: `GroupDependency` — 跨组条件依赖声明

- **规范定义（§2.1.2, §2.2）：** 根列级别的跨组条件依赖——子根列的分布取决于父根列的取值。根级依赖图必须是 DAG。
- **代码实现：** 📍 [phase_2/types.py:178-225](phase_2/types.py#L178-L225) — `@dataclass`，三字段 `child_root: str`, `on: list[str]`, `conditional_weights: dict[str, dict[str, float]]`。`on` 存储为 `list`（当前限制单列，预留多列扩展）。`conditional_weights` 是嵌套字典：外层键=父列取值，内层=子列取值→权重。`to_metadata()` 输出 §2.6 格式，做深拷贝。
- **生动类比：** 像"支付方式取决于病情严重程度"——轻症患者自费居多，重症患者保险居多。`conditional_weights` 就是这张"如果……则……概率"条件表。
- 💡 **为什么 `on` 是 list 而不是 str？** 预留了 NEEDS_CLAR 中 "multi-column `on`" 的未来扩展空间（当前仅支持单列，多列会抛 `NotImplementedError`），避免日后改接口签名的破坏性变更。

#### T4: `Check` — 校验结果原子记录

- **规范定义（§2.9）：** 单条校验结果，携带名称、通过/失败状态、可选详情。
- **代码实现：** 📍 [phase_2/types.py:232-250](phase_2/types.py#L232-L250) — `@dataclass`，`name: str`, `passed: bool`, `detail: Optional[str] = None`。极简设计——M5 三层校验（L1/L2/L3）的每一条检查都产出一个 `Check`，`detail` 携带调试信息（如 `"χ² p=0.34"`）。
- **生动类比：** 像体检报告上的一行——检查项目（name）、正常/异常（passed）、具体数值（detail）。

#### T5: `ValidationReport` — 校验报告聚合器

- **规范定义（§2.9）：** Check 的聚合容器，供 auto-fix 回路判断是否需要重试。
- **代码实现：** 📍 [phase_2/types.py:253-306](phase_2/types.py#L253-L306) — `@dataclass`，核心字段 `checks: list[Check]`。三个接口：
  - `all_passed` 属性（📍 [types.py:269-281](phase_2/types.py#L269-L281)）：`all(c.passed for c in checks)`，空报告 vacuously true
  - `failures` 属性（📍 [types.py:283-292](phase_2/types.py#L283-L292)）：过滤出 `passed=False` 的项，返回**新列表**（防御性拷贝）
  - `add_checks()` 方法（📍 [types.py:294-306](phase_2/types.py#L294-L306)）：批量追加，供 validator 按 L1→L2→L3 逐层累加
- **生动类比：** 整份体检报告——`all_passed` 是"全部正常"大章，`failures` 是"异常项列表"，`add_checks()` 是不同科室（L1/L2/L3）逐个把检查结果贴进报告。
- 💡 **为什么 `failures` 返回新列表？** 防止调用方（auto-fix 回路）在遍历失败项并修改时意外损坏报告内部状态。

#### T6: `PatternSpec` — 叙事模式声明

- **规范定义（§2.1.2）：** 六种受支持模式之一的声明——类型、目标过滤表达式、目标列、类型专属参数。
- **代码实现：** 📍 [phase_2/types.py:313-337](phase_2/types.py#L313-L337) — `@dataclass`，四字段 `type: str`, `target: str`, `col: str`, `params: dict[str, Any]`。`to_dict()` 返回原始字典格式（兼容现有引擎代码）。
- **生动类比：** 像导演的场景指令——"类型：异常实体；在哪：severity=='Critical' 的行；对谁：cost 列；怎么做：z_score=3.0"。
- 💡 **为什么 `params` 是开放 dict？** 六种模式各有不同参数结构（`outlier_entity` 需要 `z_score`，`trend_break` 需要 `break_point` + `magnitude`），用开放字典避免为每种模式定义专属子类。四种模式的 params schema 仍在 NEEDS_CLAR 中。

#### T7: `RealismConfig` — 真实感注入配置

- **规范定义（§2.1）：** 控制生成数据的"脏度"——缺失值比例、脏数据比例、可选删截配置。
- **代码实现：** 📍 [phase_2/types.py:340-361](phase_2/types.py#L340-L361) — `@dataclass`，三字段 `missing_rate: float = 0.0`, `dirty_rate: float = 0.0`, `censoring: Optional[dict] = None`。`censoring` 为不透明字典（对应 NEEDS_CLAR stub）。`to_dict()` 返回原始字典格式。
- **生动类比：** 像摄影后期的"做旧滤镜"——`missing_rate` 是随机挖孔（NaN），`dirty_rate` 是随机换标签（分类列"张三"变"李四"），`censoring` 是删截效果（尚未实现）。

#### T8: `DeclarationStore` — 复合声明容器（M1→M2/M4 的唯一过界工件）

- **规范定义（§2.1）：** 承载 SDK 所有声明的复合容器。生命周期：accumulating（方法调用中）→ frozen（`generate()` 前冻结）→ consumed（M2/M4/M5 只读）。
- **代码实现：** 📍 [phase_2/types.py:364-409](phase_2/types.py#L364-L409) — 普通 class（非 dataclass）。
  - `__init__(target_rows, seed)`：初始化七个注册表 + `_frozen=False`
  - `freeze()`（📍 [types.py:397-401](phase_2/types.py#L397-L401)）：设置 `_frozen=True`，幂等，写 debug 日志
  - `_check_mutable()`（📍 [types.py:403-409](phase_2/types.py#L403-L409)）：冻结后调用则 raise `RuntimeError`
  - `is_frozen` 属性（📍 [types.py:392-394](phase_2/types.py#L392-L394)）：只读状态查询

  **七个注册表一览：**

  | 字段 | 类型 | 对应声明 |
  |---|---|---|
  | `columns` | `OrderedDict[str, dict]` | 列注册表（所有列的描述符） |
  | `groups` | `dict[str, DimensionGroup]` | 维度组图 |
  | `measure_dag` | `dict[str, list[str]]` | 度量 DAG（邻接表） |
  | `orthogonal_pairs` | `list[OrthogonalPair]` | 正交对列表 |
  | `group_dependencies` | `list[GroupDependency]` | 跨组依赖列表 |
  | `patterns` | `list[dict]` | 模式列表 |
  | `realism_config` | `Optional[dict]` | 真实感配置 |

- **生动类比：** 如果整个 SDK 是一个建筑设计事务所，`DeclarationStore` 就是**设计图纸存档柜**。设计阶段（Step 1 + Step 2）大家往里放图纸；一旦"封卷"（`freeze()`），就变成只读的施工依据——施工队（M2）按图施工，质检员（M5）按图验收，档案员（M4）按图编目。
- 💡 **为什么用 `_check_mutable()` 而非 `@dataclass(frozen=True)`？** 因为 `DeclarationStore` 需要**两阶段生命周期**——先可变（SDK 方法逐步填充），后冻结。Python 的 `frozen=True` dataclass 从诞生就不可变，不支持这种动态冻结。

#### T9: `SandboxResult` — 沙箱执行结果（实现细节）

- **代码实现：** 📍 [phase_2/types.py:412-430](phase_2/types.py#L412-L430) — `@dataclass`，五字段 `success`, `dataframe`, `metadata`, `exception`, `traceback_str`。被 `orchestration/sandbox.py` 导入使用，承载 M3 沙箱单次执行的结构化结果。
- **说明：** stage4 未将其规划在 `types.py` 中（属 M3 内部类型），但当前实现提升至共享层。类型注解引用 `pd.DataFrame` 但文件未导入 pandas（被 `from __future__ import annotations` 延迟求值保护，运行时不报错）。

#### T10: `RetryLoopResult` — 重试循环结果（实现细节）

- **代码实现：** 📍 [phase_2/types.py:432-449](phase_2/types.py#L432-L449) — `@dataclass`，五字段 `success`, `dataframe`, `metadata`, `attempts`, `history: list[SandboxResult]`。承载完整 §2.7 重试循环的最终结果。
- **说明：** 暗示当前 M3 的输出边界比 stage4 规划更宽——直接产出 DataFrame+metadata 而非仅产出 `DeclarationStore`。

---

### 二、exceptions.py — 异常层级

#### 异常继承树

```
Exception
  └── SimulatorError                     ← SDK 异常基类（stage4 称 SDKError）
        ├── CyclicDependencyError        ← DAG 环检测
        ├── UndefinedEffectError         ← 效果映射缺值
        ├── NonRootDependencyError       ← 非根列跨组依赖
        ├── InvalidParameterError        ← 参数域校验（A5a 前瞻）
        ├── DuplicateColumnError         ← 列名重复
        ├── EmptyValuesError             ← 空 values 列表
        ├── WeightLengthMismatchError    ← values/weights 长度不匹配
        ├── DegenerateDistributionError  ← 退化分布
        ├── ParentNotFoundError          ← 父列不存在/不同组
        ├── DuplicateGroupRootError      ← 组重复根列
        ├── PatternInjectionError        ← 生成时模式注入失败
        └── UndefinedPredictorError      ← 引用未声明列

SkipResult (dataclass, 非异常)           ← Loop A 耗尽重试的哨兵返回值
```

#### E1: `SimulatorError` — SDK 异常基类

- **规范定义（§2.7）：** 所有 SDK 语义错误的共同祖先，M3 反馈回路用 `except SimulatorError` 做通用捕获。
- **代码实现：** 📍 [phase_2/exceptions.py:39-47](phase_2/exceptions.py#L39-L47) — 空体类，继承 `Exception`。
- 💡 **为什么需要基类？** M3 的重试循环需要区分"SDK 语义错误"（可通过 LLM 重新生成脚本修复）和"系统错误"（如 `MemoryError`，不可修复应直接终止）。`except SimulatorError` 只捕获前者。

#### E2: `CyclicDependencyError` — DAG 环检测

- **规范定义（§2.7 step 4）：** DAG 检测到环时抛出，消息含精确环路径。
- **代码实现：** 📍 [phase_2/exceptions.py:52-74](phase_2/exceptions.py#L52-L74) — 接收 `cycle_path: list[str]`，存储供程序化访问。消息格式：`"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."`，使用 Unicode 箭头 `→` 连接。被 `sdk/dag.py` 抛出。

#### E3: `UndefinedEffectError` — 效果映射缺值

- **规范定义（§2.7 step 4）：** 效果表遗漏了某个分类值的定义。
- **代码实现：** 📍 [phase_2/exceptions.py:77-100](phase_2/exceptions.py#L77-L100) — 接收 `effect_name` + `missing_value`。消息格式与 §2.7 示例一致：`"'severity_surcharge' in formula has no definition for 'Severe'."`。被 `sdk/validation.py` 抛出。

#### E4: `NonRootDependencyError` — 非根列跨组依赖

- **规范定义（§2.2, §2.7）：** `add_group_dependency` 引用了非根列时抛出。
- **代码实现：** 📍 [phase_2/exceptions.py:103-126](phase_2/exceptions.py#L103-L126) — 接收 `column_name`。消息格式与 §2.7 示例一致：`"'department' is not a group root; cannot use in add_group_dependency."`。

#### E5: `InvalidParameterError` — 参数域校验

- **规范定义（§2.7 隐含，假设 A5a）：** 分布参数超出有效域（如 sigma < 0）。
- **代码实现：** 📍 [phase_2/exceptions.py:134-159](phase_2/exceptions.py#L134-L159) — 接收 `param_name`, `value`, `reason`。被 `engine/skeleton.py`、`orchestration/sandbox.py`、`validation/autofix.py` 等广泛使用。
- 💡 **为什么前瞻性添加？** 当 intercept + effects 的叠加结果产生负 sigma 时，引擎需要在运行时报告精确的参数名+值+原因，而非让 numpy 抛出难以理解的底层异常。

#### E6: `DuplicateColumnError` — 列名重复

- **规范定义（§2.7，DAG 语义推导）：** 列名作为 DAG 节点必须唯一。
- **代码实现：** 📍 [phase_2/exceptions.py:162-182](phase_2/exceptions.py#L162-L182) — 接收 `column_name`。

#### E7: `EmptyValuesError` — 空 values 列表

- **规范定义（§2.1.1）：** `add_category` "rejects empty values"。
- **代码实现：** 📍 [phase_2/exceptions.py:185-203](phase_2/exceptions.py#L185-L203) — 接收 `column_name`。

#### E8: `WeightLengthMismatchError` — values/weights 不匹配

- **规范定义（§2.1.1 隐含）：** 每个 value 必须有恰好一个 weight。
- **代码实现：** 📍 [phase_2/exceptions.py:206-228](phase_2/exceptions.py#L206-L228) — 接收 `column_name`, `n_values`, `n_weights`。

#### E9: `DegenerateDistributionError` — 退化分布

- **规范定义（§2.7）：** 明确提及 "degenerate distributions" 为可捕获语义错误。
- **代码实现：** 📍 [phase_2/exceptions.py:231-251](phase_2/exceptions.py#L231-L251) — 接收 `column_name` + `detail`（如 `"sigma=0 produces a point mass"`）。

#### E10: `ParentNotFoundError` — 父列不存在

- **规范定义（§2.1.1）：** `add_category` "validates parent exists in same group"。
- **代码实现：** 📍 [phase_2/exceptions.py:254-276](phase_2/exceptions.py#L254-L276) — 接收 `child_name`, `parent_name`, `group`。

#### E11: `DuplicateGroupRootError` — 组重复根列

- **规范定义（§2.2）：** "each group has a root column"（单数=唯一）。
- **代码实现：** 📍 [phase_2/exceptions.py:279-304](phase_2/exceptions.py#L279-L304) — 接收 `group_name`, `existing_root`, `attempted_root`。

#### E12: `PatternInjectionError` — 生成时模式注入失败

- **规范定义（§2.8 γ 阶段隐含）：** 运行时模式注入失败（如 target 匹配零行、列零方差）。
- **代码实现：** 📍 [phase_2/exceptions.py:315-336](phase_2/exceptions.py#L315-L336) — 接收 `pattern_type` + `detail`。Sprint 6 添加，填补 §2.7 仅覆盖声明时错误的空白。
- 💡 **声明时 vs 生成时错误的区分：** `inject_pattern()` 的声明时校验（type 是否合法、col 是否存在）由其他异常覆盖；`PatternInjectionError` 专门覆盖**通过了声明校验但在生成时仍然失败**的情况。

#### E13: `UndefinedPredictorError` — 引用未声明列

- **规范定义（§2.1.1）：** effects 键引用了未通过 `add_category()`/`add_temporal()` 声明的列。
- **代码实现：** 📍 [phase_2/exceptions.py:341-363](phase_2/exceptions.py#L341-L363) — 接收 `predictor_name` + 可选 `context`。被 `sdk/validation.py` 的 `validate_effects_predictors()` 抛出。

#### E14: `SkipResult` — Loop A 终端哨兵（非异常）

- **规范定义（§2.7）：** Loop A 耗尽 `max_retries` 后的优雅跳过信号。
- **代码实现：** 📍 [phase_2/exceptions.py:371-388](phase_2/exceptions.py#L371-L388) — `@dataclass`，两字段 `scenario_id: str = ""`, `error_log: list[str]`。**不继承任何异常类**——是类型化返回值，`pipeline.py` 通过 `isinstance()` 检查。
- 💡 **为什么不是异常？** 跳过一个场景是**预期的正常结果**（某些场景可能就是 LLM 无法正确生成的），不应该用异常流控制。放在 `exceptions.py` 中是因为它和异常层级紧密相关（是 "异常处理后的最终出路"）。

---

## 接口契约（已实现的）

### 对外接口一览

| 接口 | 契约（输入 → 输出 → 调用时机） | 代码入口点 |
|---|---|---|
| `DimensionGroup.to_metadata()` | `() → dict{"columns","hierarchy"}` — M4 构建 `schema_metadata` 时调用 | 📍 [types.py:59-73](phase_2/types.py#L59-L73) |
| `OrthogonalPair.to_metadata()` | `() → dict{"group_a","group_b","rationale"}` — M4 构建 `orthogonal_groups` 时调用 | 📍 [types.py:139-151](phase_2/types.py#L139-L151) |
| `GroupDependency.to_metadata()` | `() → dict{"child_root","on","conditional_weights"}` — M4 构建 `group_dependencies` 时调用 | 📍 [types.py:203-217](phase_2/types.py#L203-L217) |
| `ValidationReport.all_passed` | `→ bool` — auto-fix 回路判断是否需要重试 | 📍 [types.py:269-281](phase_2/types.py#L269-L281) |
| `ValidationReport.failures` | `→ list[Check]` — auto-fix 回路获取失败项以分派策略 | 📍 [types.py:283-292](phase_2/types.py#L283-L292) |
| `ValidationReport.add_checks()` | `list[Check] → None` — validator 按层追加结果 | 📍 [types.py:294-306](phase_2/types.py#L294-L306) |
| `DeclarationStore.freeze()` | `() → None` — M1 在 `generate()` 调用前冻结声明 | 📍 [types.py:397-401](phase_2/types.py#L397-L401) |
| `DeclarationStore._check_mutable()` | `() → None \| raise RuntimeError` — 每个变异方法的前置守卫 | 📍 [types.py:403-409](phase_2/types.py#L403-L409) |
| 全部异常类构造函数 | 结构化参数 → 存储字段 + 格式化 `self.message` → `super().__init__()` | 📍 [exceptions.py:39-388](phase_2/exceptions.py#L39-L388) |

### 导入关系图（谁导入了什么）

**types.py 被导入情况：**

| 导入方 | 导入的类型 |
|---|---|
| `sdk/simulator.py` | `DimensionGroup`, `OrthogonalPair`, `GroupDependency` |
| `sdk/columns.py` | `DimensionGroup` |
| `sdk/relationships.py` | `DimensionGroup`, `OrthogonalPair`, `GroupDependency` |
| `sdk/dag.py` | `DimensionGroup`, `GroupDependency` |
| `sdk/groups.py` | `DimensionGroup` |
| `engine/generator.py` | `DimensionGroup`, `GroupDependency`, `OrthogonalPair` |
| `engine/skeleton.py` | `GroupDependency` |
| `metadata/builder.py` | `DimensionGroup`, `OrthogonalPair`, `GroupDependency` |
| `validation/validator.py` | `Check`, `ValidationReport` |
| `validation/structural.py` | `Check` |
| `validation/statistical.py` | `Check` |
| `validation/pattern_checks.py` | `Check` |
| `validation/autofix.py` | `Check` |
| `orchestration/sandbox.py` | `SandboxResult`, `RetryLoopResult` |
| `pipeline.py` | `ValidationReport` |

**exceptions.py 被导入情况：**

| 导入方 | 导入的异常 |
|---|---|
| `sdk/columns.py` | 多个声明时异常 |
| `sdk/validation.py` | `NonRootDependencyError` 等 |
| `sdk/relationships.py` | 多个声明时异常 |
| `sdk/dag.py` | `CyclicDependencyError` |
| `engine/skeleton.py` | `InvalidParameterError` |
| `engine/patterns.py` | `PatternInjectionError` 等 |
| `orchestration/sandbox.py` | `InvalidParameterError`, `SimulatorError` |
| `orchestration/retry_loop.py` | `SkipResult` |
| `orchestration/prompt.py` | `InvalidParameterError` |
| `orchestration/code_validator.py` | `InvalidParameterError` |
| `validation/pattern_checks.py` | `PatternInjectionError` |
| `validation/autofix.py` | `InvalidParameterError` |
| `pipeline.py` | `SkipResult` |

---

## 关键约束与不变量

1. **零业务逻辑约束：** `types.py` 和 `exceptions.py` 不导入任何 `phase_2` 内部模块（`types.py` 无内部导入；`exceptions.py` 仅导入 `dataclass`）。任何业务逻辑必须放在 M1–M5 中。
2. **`DeclarationStore` 冻结不变量：** 一旦 `freeze()` 被调用，任何通过 `_check_mutable()` 守卫的写操作都会 raise `RuntimeError`。冻结是幂等的（可多次调用）。
3. **`OrthogonalPair` 等价不变量：** `(A,B) == (B,A)` 且 `hash(A,B) == hash(B,A)`。`rationale` 不参与等价判断。
4. **异常层级单根约束：** 所有 SDK 语义异常继承自 `SimulatorError`。`SkipResult` 不是异常。
5. **异常消息可机读约束：** 每个异常类都将结构化字段存储为实例属性（如 `cycle_path`, `effect_name`, `column_name`），供 M3 反馈格式化器程序化访问，而非仅靠 `str(e)` 解析。

---

## 反馈回路参与

共享基础设施本身不执行回路逻辑，但提供回路所需的**数据结构和信号类型**：

### Loop A（M3 ↔ M1 — 代码级自我修正）

- **信号类型：** 全部 `SimulatorError` 子类（E2–E13）从 M1 抛出，M3 捕获
- **终端信号：** `SkipResult`（E14）作为 Loop A 耗尽后的返回值
- **数据路径：** 异常的 `.message` 字段被 `retry_loop.py` 的 `_format_error_feedback()` 格式化为 LLM 对话消息

### Loop B（M5 → M2 — 统计自动修复）

- **判断依据：** `ValidationReport.all_passed` → `False` 触发重试
- **策略分派依据：** `ValidationReport.failures` → 逐条 `Check.name` 匹配 `AUTO_FIX` 分派表
- **数据不变量：** `DeclarationStore` 在 Loop B 期间保持 frozen，修复通过 `ParameterOverrides`（M5 内部类型）进行

---

## TODO 地图（NEEDS_CLAR）

**无。** 所有项均为 SPEC_READY。

唯一值得注意的是 `DeclarationStore` 的 "progressive wrapper" 状态（D1/D2 偏差）——`ColumnDescriptor` 迁移是架构演进目标，但不属于 NEEDS_CLAR（不阻塞任何功能）。

---

## 规范偏差登记（双边报告）

| # | 偏差 | 代码侧 | 规范侧（stage4） | 严重程度 | 影响 |
|---|---|---|---|---|---|
| D1 | `ColumnDescriptor` 未实现 | `OrderedDict[str, dict]` 📍 [types.py:384](phase_2/types.py#L384) | `list[ColumnDescriptor]` 作为首要类型 | **高** | 下游模块操作原始字典，无类型安全保证 |
| D2 | `DeclarationStore` 字段类型偏移 | `patterns: list[dict]`, `realism_config: dict`, `measure_dag: dict[str, list]` | `list[PatternSpec]`, `RealismConfig`, `set[tuple]` | **中** | 已定义的 `PatternSpec`/`RealismConfig` 类型未被自己的容器使用 |
| D3 | 基类命名 | `SimulatorError` | `SDKError` | **低** | 全代码库一致，仅命名差异 |
| D4 | 额外异常类 | E5,E7,E8,E10,E11,E12（6 个额外类） | 仅列出 E1–E4,E6,E13,E14 | **信息** | 更精细分类，合理的防御性增强 |
| D5 | M3 输出边界 | `RetryLoopResult` 含 DataFrame+metadata | M3 输出 `DeclarationStore \| SkipResult` | **中** | M3 职责边界比规划更宽 |
| D6 | `pd` 未导入 | `SandboxResult`/`RetryLoopResult` 引用 `pd.DataFrame` | N/A | **低** | `__future__.annotations` 保护，运行时不报错 |

---

## 实现细节（规范未覆盖的辅助代码）

| 方法/属性 | 位置 | 用途 |
|---|---|---|
| `DimensionGroup.__repr__()` | 📍 [types.py:75-80](phase_2/types.py#L75-L80) | 调试打印 |
| `OrthogonalPair.involves_group()` | 📍 [types.py:153-164](phase_2/types.py#L153-L164) | Sprint 3 冲突检测辅助 |
| `OrthogonalPair.group_pair_set()` | 📍 [types.py:166-171](phase_2/types.py#L166-L171) | 高效集合查找辅助 |
| `GroupDependency.__repr__()` | 📍 [types.py:219-225](phase_2/types.py#L219-L225) | 调试打印 |
| `PatternSpec.to_dict()` | 📍 [types.py:330-337](phase_2/types.py#L330-L337) | 兼容现有引擎的字典格式转换 |
| `RealismConfig.to_dict()` | 📍 [types.py:355-361](phase_2/types.py#L355-L361) | 兼容现有引擎的字典格式转换 |
| `DeclarationStore._check_mutable()` | 📍 [types.py:403-409](phase_2/types.py#L403-L409) | 冻结守卫（内部方法） |
| `DeclarationStore.is_frozen` | 📍 [types.py:392-394](phase_2/types.py#L392-L394) | 冻结状态只读查询 |
