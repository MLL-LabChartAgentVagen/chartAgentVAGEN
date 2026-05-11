# AGPDS Phase 2 学习指南

> 本指南以**构建顺序**（从零搭建）展开主线，以**执行顺序**（数据流动）展开辅线，帮助读者深入理解 AGPDS Phase 2 五个模块的已实现代码。每个知识点绑定代码位置，NEEDS_CLAR 项简要标注但不深入分析。

---

# 第一部分：共享基础设施 + M1 SDK 接口层

这一部分覆盖系统最底层的两个组件——零依赖的数据定义层（types.py + exceptions.py）和第一个业务模块 M1 SDK Surface。按构建顺序，它们分别是第 0 步和第 1 步，是整个系统的地基。

---

## 第 0 章：系统全景与阅读指南

### AGPDS Phase 2 是什么

AGPDS（Agent-Generated Parametric Data Synthesis，代理生成参数化数据合成）Phase 2 的核心任务是：接受一个场景描述（scenario context），由 LLM 生成一段合法的 Python 脚本来声明一张合成事实表（fact table）的完整结构——维度分组、度量依赖、统计模式、真实感噪声——然后由确定性引擎根据这些声明生成 DataFrame，再由校验引擎验证生成结果是否忠实于声明。

整个系统由 **5 个模块** + **共享基础设施** 构成：

| 模块 | 职责一句话 | 实现率 |
|---|---|---|
| **types.py + exceptions.py** | 零业务逻辑的纯数据定义 + 类型化异常层级 | 100% (22/22) |
| **M1 — SDK Surface** | 面向 LLM 的类型安全建造者模式 API | 52% (12/23) |
| **M4 — Schema Metadata** | 将声明存储投影为 7-key 元数据字典 | 67% (6/9) |
| **M2 — Generation Engine** | 确定性四阶段流水线，声明→DataFrame | 50% (8/16) |
| **M5 — Validation Engine** | 三层校验 + 参数调整自动修复 | 62% (13/21) |
| **M3 — LLM Orchestration** | 提示 LLM、沙箱执行、异常反馈重试 | 45% (5/11) |

### 两种阅读顺序

**构建顺序（本指南主线）**——每一步只依赖已理解的部分，从零搭建：

```
types.py + exceptions.py → M1(SDK) → M4(Metadata) → M2(Engine) → M5(Validation) → M3(Orchestration)
```

**流水线执行顺序**——系统运行时的数据流动方向：

```
Phase 1 → M3 → M1 → M2 ∥ M4 → M5 → Phase 3
```

注意 M3 是流水线的**入口**却是构建顺序的**终点**——因为理解 M3 需要先理解它调用的所有下游模块。

### 约定说明

- 📍 `文件路径:行号` — 代码精确位置（行号已验证）
- ✅ 已实现 / ⚠️ TODO 或 stub / ❌ 缺失
- 💡 — 关键设计决策
- 🔄 — 反馈回路相关
- 🚧 — NEEDS_CLAR 项（TODO 地图条目）

---

## 第 1 章：地基——types.py + exceptions.py

> 如果这两个文件是一个人，TA 的工作是：**档案管理员**——设计好所有表格的模板（数据类）和所有报警单的格式（异常类），自己从不填写内容，但每个科室都必须用 TA 的模板。

这是构建顺序的**第 0 步**——零前置依赖，被 M1–M5 全部模块导入。100% SPEC_READY，无任何 NEEDS_CLAR 项。

### 1.1 数据容器三剑客

Phase 2 的声明系统围绕三种核心数据结构展开。它们定义了"维度分组是什么"、"正交独立性是什么"、"跨组条件依赖是什么"——所有上层 API 都是围绕创建和操作这三种对象来设计的。

#### `DimensionGroup` — 维度组容器

📍 [types.py:27-80](phase_2/types.py#L27-L80) — `@dataclass`

想象你在设计一家公司的组织架构。`DimensionGroup` 就是一个**部门**：

- `name` — 部门名（如 `"entity"`、`"patient"`、`"time"`）
- `root` — 部门负责人（根列，如 `hospital`），每个部门恰好一个
- `columns` — 全体成员名单（所有列名）
- `hierarchy` — 汇报链（根优先的层级顺序）

```python
# 📍 types.py:54-57
name: str
root: str
columns: list[str] = field(default_factory=list)
hierarchy: list[str] = field(default_factory=list)
```

关键区别：**分类组**的 `hierarchy` 镜像 `columns`（每个成员都参与层级钻取）；**时间组**的 `hierarchy` 仅含 root（`day_of_week`、`month` 等派生列是确定性变换，不是钻取层级）。

💡 **为什么 `columns` 和 `hierarchy` 分开存储？** 正是因为时间组需要区分"谁是成员"和"谁参与层级钻取"。如果合并成一个列表，就无法表达"派生时间列属于组但不参与层级"的语义。

`to_metadata()` 📍 [types.py:59-73](phase_2/types.py#L59-L73) 输出 `{"columns": [...], "hierarchy": [...]}`，做**防御性拷贝**（`list(self.columns)`），防止外部调用方修改内部状态。防御性拷贝是整个项目的通用模式。

#### `OrthogonalPair` — 正交独立性声明

📍 [types.py:87-171](phase_2/types.py#L87-L171) — `@dataclass`

正交声明像一份**互不干涉条约**——声明两个维度组（如 `entity` 和 `patient`）在统计上完全独立。三个字段：

```python
# 📍 types.py:107-109
group_a: str
group_b: str
rationale: str
```

核心设计点在于 `__eq__` 和 `__hash__` 的实现 📍 [types.py:111-137](phase_2/types.py#L111-L137)：

```python
# 📍 types.py:125-127 — 顺序无关等价
self_pair = frozenset((self.group_a, self.group_b))
other_pair = frozenset((other.group_a, other.group_b))
return self_pair == other_pair
```

`OrthogonalPair("entity", "time")` 和 `OrthogonalPair("time", "entity")` 是**同一份声明**。`rationale` 不参与等价判断——同一组对不管理由如何不同，都是同一份条约。

💡 **为什么重写这两个方法？** 如果不这样做，把 `OrthogonalPair` 放进 `set` 或用作 `dict` 键时，(A,B) 和 (B,A) 会被视为两份不同声明，导致重复声明无法检测、M5 的 χ² 检验重复执行。

辅助方法：`involves_group(name)` 📍 [types.py:153-164](phase_2/types.py#L153-L164) 检查某组是否在对中；`group_pair_set()` 📍 [types.py:166-171](phase_2/types.py#L166-L171) 返回 `frozenset` 便于集合查找。

#### `GroupDependency` — 跨组条件依赖声明

📍 [types.py:178-225](phase_2/types.py#L178-L225) — `@dataclass`

条件依赖像一张"**如果……则……概率**"条件表——比如"支付方式的分布取决于病情严重程度"：

```python
# 📍 types.py:199-201
child_root: str                                    # "payment_method"
on: list[str]                                      # ["severity"]
conditional_weights: dict[str, dict[str, float]]   # {"Mild": {"Insurance": 0.45, ...}, ...}
```

💡 **为什么 `on` 是 `list` 而不是 `str`？** 预留了未来多列联合条件的扩展空间。当前代码仅使用 `on[0]`（单列条件），多列会导致下游行为未定义（🚧 NEEDS_CLAR P2）。

`to_metadata()` 📍 [types.py:203-217](phase_2/types.py#L203-L217) 输出 `{"child_root", "on", "conditional_weights"}`，嵌套 dict 做深拷贝 `{k: dict(v) for k, v in ...}`。

### 1.2 校验结构

#### `Check` — 校验结果原子记录

📍 [types.py:232-250](phase_2/types.py#L232-L250) — `@dataclass`

像体检报告上的**一行**——检查项目（`name`）、正常/异常（`passed`）、具体数值（`detail`）：

```python
name: str                      # "row_count", "cardinality_hospital", "ks_wait_minutes_Mild"
passed: bool
detail: Optional[str] = None   # "χ² p=0.34", "deviation=0.05"
```

M5 三层校验（L1 结构 / L2 统计 / L3 模式）的每条检查都产出一个 `Check`。

#### `ValidationReport` — 校验报告聚合器

📍 [types.py:253-306](phase_2/types.py#L253-L306) — `@dataclass`

整份体检报告——内含三个接口：

| 接口 | 位置 | 行为 | 类比 |
|---|---|---|---|
| `all_passed` 属性 | 📍 [types.py:270-280](phase_2/types.py#L270-L280) | `all(c.passed for c in checks)`，空报告 vacuously true | "全部正常"大章 |
| `failures` 属性 | 📍 [types.py:283-292](phase_2/types.py#L283-L292) | 过滤出 `passed=False` 的项，返回**新列表** | "异常项列表" |
| `add_checks()` | 📍 [types.py:294-306](phase_2/types.py#L294-L306) | `self.checks.extend(new_checks)` | 不同科室逐个贴结果 |

💡 **为什么 `failures` 返回新列表？** 防止调用方（auto-fix 回路）在遍历失败项并修改时意外损坏报告内部状态。这又是防御性拷贝模式。

### 1.3 声明配置类

#### `PatternSpec` — 叙事模式声明

📍 [types.py:313-337](phase_2/types.py#L313-L337) — `@dataclass`

像导演的场景指令——"类型：异常实体；在哪：`severity=='Critical'` 的行；对谁：`cost` 列；怎么做：`z_score=3.0`"：

```python
type: str                      # "outlier_entity", "trend_break", ...
target: str                    # DataFrame query 表达式
col: str                       # 目标度量列
params: dict[str, Any]         # 类型专属参数
```

💡 **为什么 `params` 是开放 dict？** 六种模式各有不同参数结构，用开放字典避免为每种模式定义专属子类。代价是拼写错误不会在声明时被捕获。

#### `RealismConfig` — 真实感注入配置

📍 [types.py:340-361](phase_2/types.py#L340-L361) — `@dataclass`

像摄影后期的"做旧滤镜"——`missing_rate` 是随机挖孔（NaN），`dirty_rate` 是随机换标签：

```python
missing_rate: float = 0.0      # 缺失率
dirty_rate: float = 0.0        # 脏数据率
censoring: Optional[dict] = None  # 🚧 P2 — 语义未阐述，当前为不透明 dict
```

### 1.4 核心容器——`DeclarationStore`

📍 [types.py:364-409](phase_2/types.py#L364-L409) — 普通 class（非 dataclass）

如果整个 SDK 是一个建筑设计事务所，`DeclarationStore` 就是**设计图纸存档柜**。设计阶段大家往里放图纸；一旦"封卷"（`freeze()`），就变成只读的施工依据。

**两阶段生命周期：**
1. **Accumulating（可变）**：SDK 方法逐步填充七个注册表
2. **Frozen（冻结）**：`freeze()` 📍 [types.py:397-401](phase_2/types.py#L397-L401) 设置 `_frozen=True`，幂等

**七个注册表：**

| 字段 | 类型 | 位置 |
|---|---|---|
| `columns` | `OrderedDict[str, dict]` | 📍 [types.py:384](phase_2/types.py#L384) |
| `groups` | `dict[str, DimensionGroup]` | 📍 [types.py:385](phase_2/types.py#L385) |
| `orthogonal_pairs` | `list[OrthogonalPair]` | 📍 [types.py:386](phase_2/types.py#L386) |
| `group_dependencies` | `list[GroupDependency]` | 📍 [types.py:387](phase_2/types.py#L387) |
| `patterns` | `list[dict]` | 📍 [types.py:388](phase_2/types.py#L388) |
| `realism_config` | `Optional[dict]` | 📍 [types.py:389](phase_2/types.py#L389) |
| `measure_dag` | `dict[str, list[str]]` | 📍 [types.py:390](phase_2/types.py#L390) |

冻结守卫 `_check_mutable()` 📍 [types.py:403-409](phase_2/types.py#L403-L409) 在冻结后调用则 raise `RuntimeError`。

💡 **为什么用 `_check_mutable()` 而非 `@dataclass(frozen=True)`？** 因为 Python 的 `frozen=True` 从诞生就不可变，不支持"先可变后冻结"的动态生命周期。

**重要规范偏差：** `FactTableSimulator` 📍 [simulator.py:28-51](phase_2/sdk/simulator.py#L28-L51) 内部使用 7 个独立字段而非 `DeclarationStore` 实例。`DeclarationStore` 虽然已定义，但实际上是**未被使用的 progressive wrapper**。这意味着冻结保护并未在运行路径中生效。

### 1.5 M3 内部类型（提升至共享层）

两个 M3 内部使用的数据类也定义在 types.py 中：

- `SandboxResult` 📍 [types.py:412-430](phase_2/types.py#L412-L430) — 沙箱单次执行结果：`success`, `dataframe`, `metadata`, `exception`, `traceback_str`
- `RetryLoopResult` 📍 [types.py:432-449](phase_2/types.py#L432-L449) — 完整重试循环结果：`success`, `dataframe`, `metadata`, `attempts`, `history`

它们暗示 M3 的输出边界比规范更宽——直接产出 DataFrame+metadata 而非仅 `DeclarationStore`。

### 1.6 异常层级

📍 [exceptions.py](phase_2/exceptions.py) 全文

异常层级是 Loop A（M3 ↔ M1 代码级自我修正）的核心基础设施——LLM 生成的脚本执行失败时，类型化异常携带精确错误信息反馈给 LLM 修正。

**继承树：**

```
Exception
  └── SimulatorError                     ← SDK 异常基类  📍 exceptions.py:39-47
        ├── CyclicDependencyError        ← DAG 环检测    📍 exceptions.py:52-74
        ├── UndefinedEffectError         ← 效果映射缺值  📍 exceptions.py:77-100
        ├── NonRootDependencyError       ← 非根列跨组依赖 📍 exceptions.py:103-126
        ├── InvalidParameterError        ← 参数域校验    📍 exceptions.py:134-159
        ├── DuplicateColumnError         ← 列名重复      📍 exceptions.py:162-182
        ├── EmptyValuesError             ← 空 values     📍 exceptions.py:185-203
        ├── WeightLengthMismatchError    ← 长度不匹配    📍 exceptions.py:206-228
        ├── DegenerateDistributionError  ← 退化分布      📍 exceptions.py:231-251
        ├── ParentNotFoundError          ← 父列不存在    📍 exceptions.py:254-276
        ├── DuplicateGroupRootError      ← 组重复根列    📍 exceptions.py:279-304
        ├── PatternInjectionError        ← 生成时注入失败 📍 exceptions.py:315-336
        └── UndefinedPredictorError      ← 引用未声明列  📍 exceptions.py:341-363

SkipResult (dataclass, 非异常)           ← Loop A 终端哨兵 📍 exceptions.py:371-388
```

每个异常类的设计模式都一样：

1. **构造函数接收结构化参数**（如 `cycle_path: list[str]`），存储为实例属性
2. **格式化 `.message`** 为 LLM 可直接理解的描述性字符串
3. **调用 `super().__init__(self.message)`**

以 `CyclicDependencyError` 📍 [exceptions.py:66-74](phase_2/exceptions.py#L66-L74) 为例：

```python
def __init__(self, cycle_path: list[str]) -> None:
    self.cycle_path = cycle_path
    arrow_chain = " → ".join(f"'{node}'" for node in cycle_path)
    self.message = f"Measure {arrow_chain} forms a cycle."
    super().__init__(self.message)
```

输出类似 `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."` —— LLM 读到这个消息就知道要删掉 `cost → satisfaction` 或 `satisfaction → cost` 其中一条边。

💡 **为什么异常消息要如此结构化？** Loop A 只有 3 次重试预算。LLM 每次只能看到一个异常，所以错误消息必须足够精准，让 LLM 在一次重试中就能定位并修正问题。

**`SkipResult`** 📍 [exceptions.py:371-388](phase_2/exceptions.py#L371-L388) 比较特殊——**不继承任何异常类**，是 `@dataclass`，含 `scenario_id` 和 `error_log`。它代表"Loop A 耗尽重试后的优雅跳过"，是**预期的正常结果**而非错误。`pipeline.py` 通过 `isinstance()` 检查而非 `except` 子句来识别它。放在 `exceptions.py` 是因为它和异常层级紧密相关——是异常处理后的最终出路。

### 1.7 本章小结

types.py + exceptions.py 是整个 Phase 2 的**无源之水**——不导入任何 `phase_2` 内部模块，但被所有模块导入。它们建立了三个关键约束：

1. **声明结构标准化**：所有声明通过 `DimensionGroup` / `OrthogonalPair` / `GroupDependency` 三种类型表达
2. **冻结语义**：`DeclarationStore` 的 accumulating→frozen 两阶段生命周期（虽然 simulator 尚未使用）
3. **异常可机读**：每个异常携带结构化字段，供 M3 反馈格式化器程序化访问，驱动 Loop A 自我修正

**规范偏差提示：**
- `DeclarationStore` 定义了但未被 `FactTableSimulator` 使用（D1/D2 偏差）
- 基类命名 `SimulatorError` 而非规范的 `SDKError`（D3 偏差）
- 代码有 11 个异常类，规范仅命名 7 个（D4 偏差——合理的防御性增强）

---

## 第 2 章：建筑师事务所——M1 SDK Surface

> 如果 M1 是一个人，TA 的工作是：**LLM 的建筑审批官**——接受 LLM 提交的每一笔声明（列、组、依赖、模式），逐条审查是否合法，合法就盖章归档到注册表，不合法就开具整改通知单（类型化异常）。TA 不建造任何东西，但保证所有蓝图在交给施工队（M2）之前都是正确的。

M1 是构建顺序中**第一个真正的业务模块**，实现率 52%（12/23 项 SPEC_READY）。

```
types.py + exceptions.py ✅ → 【M1(SDK) ← 当前】 → M4 → M2 → M5 → M3
```

### 2.1 `FactTableSimulator` — 轻量委托壳

📍 [simulator.py:28-51](phase_2/sdk/simulator.py#L28-L51)

`FactTableSimulator` 是 LLM 脚本中唯一使用的类。但它自己几乎不做任何事——所有 `add_*` 方法都是 one-liner 委托：

```python
# 📍 simulator.py:32-51 — 构造器
def __init__(self, target_rows: int, seed: int = 42) -> None:
    # 类型校验（排除 bool，因为 isinstance(True, int) 为 True）
    # 正整数校验
    self.target_rows = target_rows
    self.seed = seed
    # 初始化 7 个注册表（与 DeclarationStore 相同的结构）
    self._columns: OrderedDict[str, dict] = OrderedDict()
    self._groups: dict[str, DimensionGroup] = {}
    self._orthogonal_pairs: list[OrthogonalPair] = []
    self._group_dependencies: list[GroupDependency] = []
    self._patterns: list[dict] = []
    self._realism_config: Optional[dict] = None
    self._measure_dag: dict[str, list[str]] = {}
```

所有 `add_*` 方法的模式一致——一行转发：

```python
# 📍 simulator.py:53-61
def add_category(self, name, values, weights, group, parent=None):
    _columns_api.add_category(self._columns, self._groups, name, values, weights, group, parent)
```

💡 **为什么这样设计？** 将验证和注册逻辑从 `simulator.py` 拆到独立模块（`columns.py`、`relationships.py`），让每个函数接受显式参数（无 `self`），更易测试、更符合函数式风格。`FactTableSimulator` 只做 API 门面（facade pattern）。

### 2.2 Step 1：列声明四方法

LLM 脚本的前半段调用这四个方法来声明列。

#### `add_category()` — 分类列声明

📍 [columns.py:38-121](phase_2/sdk/columns.py#L38-L121)

想象你在设计问卷调查的下拉菜单。`add_category` 就是在说："这个字段叫 `hospital`，可选值有 General/Teaching/Specialist，出现概率分别是 40%/35%/25%，它属于 `entity` 这个维度组。"

**验证链（声明时逐步检查）：**

1. `validate_column_name()` — 列名全局唯一 📍 [validation.py:57-71](phase_2/sdk/validation.py#L57-L71)
2. 空值检查 — `values` 不能为空列表 📍 [columns.py:67-68](phase_2/sdk/columns.py#L67-L68)
3. `validate_parent()` — parent 存在且同组 📍 [validation.py:78-105](phase_2/sdk/validation.py#L78-L105)
4. 权重分支 📍 [columns.py:76-88](phase_2/sdk/columns.py#L76-L88)：
   - **flat list**（根列）→ `validate_and_normalize_flat_weights()` 📍 [validation.py:112-163](phase_2/sdk/validation.py#L112-L163)
   - **per-parent dict**（子列）→ `validate_and_normalize_dict_weights()` 📍 [validation.py:166-223](phase_2/sdk/validation.py#L166-L223)
5. `"time"` 组名保留检查 📍 [columns.py:91-95](phase_2/sdk/columns.py#L91-L95)
6. 组内单根检查 📍 [columns.py:98-103](phase_2/sdk/columns.py#L98-L103) → 违反则抛 `DuplicateGroupRootError`

注册产物 📍 [columns.py:106-113](phase_2/sdk/columns.py#L106-L113)：

```python
col_meta = {
    "type": "categorical",
    "values": list(values),
    "weights": normalized_weights,  # 已归一化到 sum=1.0
    "group": group,
    "parent": parent,
}
columns[name] = col_meta
```

同时更新组注册表：`register_categorical_column()` 📍 [groups.py:20-55](phase_2/sdk/groups.py#L20-L55)——按需创建组、设置 root、追加到 columns/hierarchy。

💡 **为什么权重归一化在声明时完成？** 这是"前移验证"策略——错误越早发现，LLM 在 Loop A 中就能越快修正。比起在生成时才发现权重不合法，声明时报错可以节省整个 M2 的计算开销。

#### `add_temporal()` — 时序列与派生特征

📍 [columns.py:124-211](phase_2/sdk/columns.py#L124-L211)

时序列就像给数据表装了一个**日历**。你说"从 2023-01-01 到 2024-12-31，按月"，它就帮你铺好日期轴。更妙的是，你可以说 `derive=["month", "quarter"]`，它就自动从日期中提取月份和季度，作为独立列进入注册表。

**验证链：**
1. 列名唯一
2. ISO-8601 日期解析：`_parse_iso_date()` 📍 [columns.py:324-345](phase_2/sdk/columns.py#L324-L345)
3. `start < end`
4. `freq` 在有效集合 `{"D", "W-MON"..."W-SUN", "MS"}` 内 📍 [columns.py:170-175](phase_2/sdk/columns.py#L170-L175)
5. `derive` 项在 `TEMPORAL_DERIVE_WHITELIST` 📍 [validation.py:42-44](phase_2/sdk/validation.py#L42-L44) 内（4 种：`day_of_week`, `month`, `quarter`, `is_weekend`）

**注册行为：**
- 根列注册为 `type="temporal"`，group 固定为 `"time"` 📍 [columns.py:178-187](phase_2/sdk/columns.py#L178-L187)
- 每个派生特征自动命名为 `{name}_{d}`（如 `date_month`），注册为 `type="temporal_derived"` 📍 [columns.py:191-201](phase_2/sdk/columns.py#L191-L201)
- 组注册：`register_temporal_group()` 📍 [groups.py:57-81](phase_2/sdk/groups.py#L57-L81) —— `columns` 含 root+派生，`hierarchy` **仅含 root**

💡 **"一切皆列"的统一设计。** 派生列与普通分类列同等对待——都在 column_registry 中，度量的 `effects` 可以直接引用 `date_month` 作为预测器，不需要特殊路径。

#### `add_measure()` — 随机根度量

📍 [columns.py:214-250](phase_2/sdk/columns.py#L214-L250)

随机根度量就像一个**可调节的骰子**。基础面值（`intercept`）是固定的，但根据分类上下文可以加减偏移量（`effects`）。数学表达：

```
θⱼ = β₀ + Σₘ βₘ(Xₘ)
```

比如："`wait_minutes` 的均值 μ 基础是 36.5，如果 `severity='Severe'` 就 +12.0，如果 `hospital='Teaching'` 就 +3.0"。

**验证链：**
1. 列名唯一
2. `family` 在 `SUPPORTED_FAMILIES`（8 族）📍 [validation.py:30-33](phase_2/sdk/validation.py#L30-L33)：gaussian, lognormal, gamma, beta, uniform, poisson, exponential, mixture
3. `validate_param_model()` 📍 [validation.py:294-399](phase_2/sdk/validation.py#L294-L399)——递归验证 param_model 结构

`validate_param_model` 的两条路径：
- **Case A** — 数值标量：常数参数，直接通过
- **Case B** — dict with `intercept` + optional `effects`：验证 intercept 是数值，effects 中每个键是已声明的分类列名且值集完全匹配

注册为 `{"type": "measure", "measure_type": "stochastic", "family": ..., "param_model": ...}`。随机根度量是 DAG 的叶节点——**不产生 DAG 边**。

💡 **为什么只验证 gaussian/lognormal 的参数键名？** 📍 [validation.py:36-39](phase_2/sdk/validation.py#L36-L39) 规范只给出了这两个族的具体示例。对其余 6 族保持开放，避免过度约束——但代价是拼写错误（如把 `mu` 写成 `mean`）不会在声明时被捕获。

#### `add_measure_structural()` — 结构度量与 DAG 边

📍 [columns.py:253-321](phase_2/sdk/columns.py#L253-L321)

结构度量就像 Excel 中**引用其他单元格的公式**。你写 `formula="wait_minutes * 2.5 + severity_surcharge"`，SDK 就知道：(1) `wait_minutes` 是上游度量——建立 DAG 边；(2) `severity_surcharge` 是一个效果名——去 `effects` 字典里查定义。

**公式符号提取：** `extract_formula_symbols()` 📍 [validation.py:49-50](phase_2/sdk/validation.py#L49-L50) 用正则 `[a-zA-Z_][a-zA-Z0-9_]*` 提取所有标识符。

**符号分类** 📍 [columns.py:285-292](phase_2/sdk/columns.py#L285-L292)：

| 符号在 | 处理方式 |
|---|---|
| effects 键中 | 跳过（效果名，由 effects 验证器处理） |
| columns 中且 type="measure" | 加入 `measure_deps`（建立 DAG 边） |
| 其他 | **静默跳过**（可能是 Python 关键字如 `max`） |

**Effects 验证：** `validate_structural_effects()` 📍 [validation.py:467-547](phase_2/sdk/validation.py#L467-L547)——每个 effect name 必须在公式中出现，内层 dict 键集必须完全匹配某分类列的值集。

**DAG 环检测：** `check_measure_dag_acyclic()` 📍 [dag.py:379-410](phase_2/sdk/dag.py#L379-L410)——每次新增度量后构建临时邻接表并检测环。

注册后更新 `measure_dag` 📍 [columns.py:313-316](phase_2/sdk/columns.py#L313-L316)：

```python
measure_dag.setdefault(name, [])
for dep in measure_deps:
    measure_dag.setdefault(dep, [])
    measure_dag[dep].append(name)   # upstream → downstream 边
```

💡 **声明时宽松 + 运行时严格。** 公式中未匹配的符号被静默跳过而不报错——容忍 Python 关键字和数值常量。实际的 "every symbol must resolve" 约束推迟到运行时公式求值器（🚧 P0 — 尚未实现）。

### 2.3 Step 2：关系声明四方法

LLM 脚本的后半段调用这四个方法来声明跨组关系和模式。

#### `declare_orthogonal()` — 组级独立性声明

📍 [relationships.py:39-92](phase_2/sdk/relationships.py#L39-L92)

正交声明就是两个部门签了一份"互不干涉条约"。声明了 `entity` ⊥ `patient` 之后：(1) M2 生成时用 P(A) × P(B) 独立采样，(2) M5 用 χ² 检验确认独立性，(3) Phase 3 用它设计"正交对比"仪表盘。

**验证链：** 两组存在 → 不同名 → 无依赖冲突（`_check_dependency_conflict` 📍 [relationships.py:322-343](phase_2/sdk/relationships.py#L322-L343)）→ 无重复声明

💡 **双向互斥锁设计。** `declare_orthogonal` 检查是否已有依赖，`add_group_dependency` 也检查是否已声明正交（`_check_orthogonal_conflict` 📍 [relationships.py:306-319](phase_2/sdk/relationships.py#L306-L319)）。两种矛盾声明无论先后顺序都会被拒绝。

#### `add_group_dependency()` — 跨组条件依赖

📍 [relationships.py:95-196](phase_2/sdk/relationships.py#L95-L196)

组依赖就像说"支付方式的分布取决于去的是哪家医院"。你给出一张条件概率表：General 医院 → Insurance 45% / Self-pay 45%；Teaching 医院 → 不同的分布……

**验证链：**
1. `child_root` 和 `on` 列均为组根（`is_group_root()` 📍 [groups.py:98-122](phase_2/sdk/groups.py#L98-L122)）→ 违反则抛 `NonRootDependencyError`
2. 正交冲突检查 → 不能同时声明正交和依赖
3. 根 DAG 无环（`check_root_dag_acyclic()` 📍 [dag.py:413-451](phase_2/sdk/dag.py#L413-L451)）
4. `conditional_weights` 覆盖所有 parent 值 + 每行覆盖所有 child 值 → 每行归一化

注意代码**仅使用 `on[0]`**（📍 relationships.py line 132, 139, 143）——单列条件的完整实现。多列 `on` 是 🚧 NEEDS_CLAR P2。

#### `inject_pattern()` — 模式注入声明

📍 [relationships.py:199-257](phase_2/sdk/relationships.py#L199-L257)

模式注入就像在完美的模拟数据中"种下"故意的异常信号——给 Phase 3 QA 仪表盘设计的"预埋答案"。

支持 6 种模式类型 📍 [relationships.py:27-30](phase_2/sdk/relationships.py#L27-L30)，但仅 2 种有完整参数 schema 📍 [relationships.py:33-36](phase_2/sdk/relationships.py#L33-L36)：

| 类型 | 必需参数 | 状态 |
|---|---|---|
| `outlier_entity` | `z_score` | ✅ 完整 |
| `trend_break` | `break_point`, `magnitude` | ✅ 完整 |
| `ranking_reversal` | — | 🚧 P1 无参数校验 |
| `dominance_shift` | — | 🚧 P1 无参数校验 |
| `convergence` | — | 🚧 P1 无参数校验 |
| `seasonal_anomaly` | — | 🚧 P1 无参数校验 |

验证：type 在白名单 → col 存在且为 measure → 对已知类型检查必需参数。

#### `set_realism()` — 数据仿真噪声配置

📍 [relationships.py:260-299](phase_2/sdk/relationships.py#L260-L299)

验证 `missing_rate`/`dirty_rate` ∈ [0, 1]，返回 config dict。委托入口 📍 [simulator.py:120-128](phase_2/sdk/simulator.py#L120-L128)。

### 2.4 声明时验证规则集

M1 的验证器是 LLM 代码质量的**第一道防线**。代码实现了 **9 种验证**（超出规范命名的 4 种）：

| 验证规则 | 验证函数 | 位置 | 触发异常 |
|---|---|---|---|
| DAG 无环 | `detect_cycle_in_adjacency()` + `check_*_acyclic()` | 📍 [dag.py:33-102](phase_2/sdk/dag.py#L33-L102), [dag.py:379-451](phase_2/sdk/dag.py#L379-L451) | `CyclicDependencyError` |
| Parent 存在+同组 | `validate_parent()` | 📍 [validation.py:78-105](phase_2/sdk/validation.py#L78-L105) | `ParentNotFoundError` |
| Root-only 约束 | `validate_root_only()` | 📍 [validation.py:568-585](phase_2/sdk/validation.py#L568-L585) | `NonRootDependencyError` |
| 公式符号解析 | `extract_formula_symbols()` + `validate_structural_effects()` | 📍 [validation.py:49-50](phase_2/sdk/validation.py#L49-L50), [validation.py:467-547](phase_2/sdk/validation.py#L467-L547) | `UndefinedEffectError` |
| 列名唯一 | `validate_column_name()` | 📍 [validation.py:57-71](phase_2/sdk/validation.py#L57-L71) | `DuplicateColumnError` |
| 空值拒绝 | 内联 | 📍 [columns.py:67-68](phase_2/sdk/columns.py#L67-L68) | `EmptyValuesError` |
| 权重长度匹配 | `validate_and_normalize_flat_weights()` | 📍 [validation.py:137-142](phase_2/sdk/validation.py#L137-L142) | `WeightLengthMismatchError` |
| 分布族白名单 | `validate_family()` | 📍 [validation.py:274-287](phase_2/sdk/validation.py#L274-L287) | `ValueError` |
| Effects 预测器存在 | `validate_effects_in_param()` | 📍 [validation.py:402-460](phase_2/sdk/validation.py#L402-L460) | `UndefinedEffectError` |

💡 **为什么要 9 种而不是规范的 4 种？** Loop A 只有 3 次重试。每次只能看到一个异常，所以每种可能的声明错误都需要精准的类型化异常和描述性消息，让 LLM 一次就能定位问题。

### 2.5 维度组抽象与 Measure DAG

#### 组注册逻辑

📍 [groups.py](phase_2/sdk/groups.py) — 两个注册函数 + 两个查询辅助

| 函数 | 位置 | 职责 |
|---|---|---|
| `register_categorical_column()` | 📍 [groups.py:20-55](phase_2/sdk/groups.py#L20-L55) | 按需创建组，设置 root，追加到 columns/hierarchy |
| `register_temporal_group()` | 📍 [groups.py:57-81](phase_2/sdk/groups.py#L57-L81) | `columns` = root+派生，`hierarchy` = 仅 root |
| `get_roots()` | 📍 [groups.py:84-95](phase_2/sdk/groups.py#L84-L95) | 返回所有组的根列列表 |
| `is_group_root()` | 📍 [groups.py:98-122](phase_2/sdk/groups.py#L98-L122) | 判断列是否为其组的 root |

#### Measure DAG 拓扑排序

📍 [dag.py:105-155](phase_2/sdk/dag.py#L105-L155) — `topological_sort()`

拓扑排序就像决定做菜的顺序：你不能在煮面条之前加酱料——如果 `cost = f(wait_minutes)`，那 `wait_minutes` 必须先生成。

实现使用 **Kahn 算法 + min-heap 字典序 tie-breaking**：

```python
# 📍 dag.py:134-135 — 零入度节点入堆
heap: list[str] = [n for n, deg in in_degree.items() if deg == 0]
heapq.heapify(heap)
```

字典序 tie-breaking 保证**确定性**——同一输入永远产出同一顺序，不依赖 dict 迭代顺序。

相关辅助函数：
- `build_full_dag()` 📍 [dag.py:197-293](phase_2/sdk/dag.py#L197-L293)——从 **5 种边源**组装统一 DAG：组内层级、跨组根依赖、时序派生、度量预测器引用、度量间公式引用。组装完成后做防御性环检测。
- `extract_measure_sub_dag()` 📍 [dag.py:158-190](phase_2/sdk/dag.py#L158-L190)——从完整 DAG 过滤出度量子图。

💡 **第 4 种边源（度量预测器引用）是规范未显式列出的。** 代码补充了"分类列作为度量效果预测器"所隐含的生成顺序依赖，确保预测器列在度量列之前被生成。

### 2.6 `generate()` — 从声明到生成的桥梁

📍 [simulator.py:130-141](phase_2/sdk/simulator.py#L130-L141)

```python
def generate(self) -> tuple[pd.DataFrame, dict[str, Any]]:
    df, schema_metadata = _generator_api.run_pipeline(
        columns=self._columns,
        groups=self._groups,
        group_dependencies=self._group_dependencies,
        measure_dag=self._measure_dag,
        target_rows=self.target_rows,
        seed=self.seed,
        patterns=self._patterns,
        realism_config=self._realism_config,
    )
    return df, schema_metadata
```

注意两个规范偏差：
1. **未调用 `DeclarationStore.freeze()`** —— 冻结是隐式约定而非强制保护
2. **未传递 `orthogonal_pairs`** —— `run_pipeline()` 签名中没有此参数，但 M4 在内部被调用时需要它（导致 metadata 中 `orthogonal_groups` 始终为空列表 `[]`）

还有一个**死代码**：`_build_schema_metadata()` 📍 [simulator.py:143-152](phase_2/sdk/simulator.py#L143-L152) 正确传递了 `orthogonal_pairs`，但 `generate()` 从未调用它——M4 实际由 M2 内部调用。

### 2.7 🔄 反馈回路参与——Loop A

M1 是 Loop A 的**异常源**——当 LLM 脚本中的 `add_*()` 调用触发验证失败时：

```
LLM 脚本 → sim.add_category(...) → M1 验证失败
    → raise CyclicDependencyError(["cost", "satisfaction", "cost"])
    → 异常沿调用栈冒泡回 M3 沙箱
    → M3 捕获并格式化为 traceback
    → M3 将 "code + traceback" 追加到 LLM 对话
    → LLM 重新生成脚本 → 再次进入 M1
    → 最多 3 次重试
```

所有 9 种异常类型（§1.6）都有结构化的 `.message` 属性，设计为 LLM 可直接理解并修正。

M1 **不参与 Loop B**——auto-fix 策略调整参数后直接重新调用 `generate()`，不重新执行声明。

### 2.8 🚧 TODO 地图

| 项目 | 优先级 | 阻塞原因 | 代码状态 | 影响模块 |
|---|---|---|---|---|
| 公式求值机制 | **P0** | M2 的 `_eval_structural` 求值器未定义 | M1 部分已实现（符号提取+DAG 边） | M2, M5 |
| `mixture` param_model schema | P1 | 参数结构未定义 | Stub：accepted 但不验证 | M2, M5 |
| 4 种欠规范 pattern 类型 | P1 | 无参数 schema | Stub：类型名被接受 | M2, M5 |
| `scale` 参数 | P2 | 语义未定义 | Dead param：存储但无消费 | M1 内部 |
| 多列 `on` | P2 | 联合条件未展示 | 静默降级：只用 `on[0]` | M2 |
| `censoring` 参数 | P2 | 语义未阐述 | Pass-through：存储为 opaque dict | M2 |
| Step 1/2 顺序强制 | P2 | SDK 无 `_phase` 状态机 | 部分实现（target_rows 验证有）| — |
| 负分布参数 | P3 | 加性效应可能产生无效参数 | 缺失：M1 不检查 | M2 |

已自行解决的 NEEDS_CLAR（4 项）：正交+依赖矛盾（双向检测 ✅）、Per-parent 缺失父值（要求完全覆盖 ✅）、列名唯一性（`DuplicateColumnError` ✅）、Effects 引用未声明列（声明时验证 ✅）。

### 2.9 本章小结

M1 建立了三个关键保证：

1. **类型安全的声明 API**：所有声明通过验证链逐步检查，不合法立即抛出精准异常
2. **DAG 无环不变量**：度量 DAG 和根依赖 DAG 在每次声明后增量检测
3. **权重归一化不变量**：所有 weights 在声明时归一化到 sum=1.0

**M1 的输出契约**：成功时——冻结的 7 个注册表传递给 M2（生成 DataFrame）和 M4（构建 schema_metadata）；失败时——类型化异常传递给 M3 触发 Loop A。

**规范偏差提示：**
- `DeclarationStore` 未被使用，注册表作为 8 个独立参数传递（非单一 store 对象）
- `generate()` 未调用 `freeze()` 也未传递 `orthogonal_pairs`
- `_build_schema_metadata()` 是死代码

---

# 第二部分：M4 Schema 元数据 + M2 生成引擎

这一部分覆盖构建顺序中的第 2、3 步——M4 将声明存储投影为机器可读的元数据字典，M2 根据声明执行确定性生成流水线。M4 先于 M2 讲解，因为 M2 的 return path 调用了 M4，理解元数据结构有助于理解 M2 的输出契约。

---

## 第 3 章：档案员——M4 Schema Metadata

> 如果 M4 是一个人，TA 的工作是：**技术文档编写员**——把建筑师（M1）画好的蓝图拍照、标注、装订成册，交给验收团队（M5）和下游客户（Phase 3）。TA 不建造任何东西，只是把"系统应该长什么样"翻译成一份标准化的说明书。

M4 是构建顺序中**第 2 步**，前置依赖：types.py（`DimensionGroup`、`OrthogonalPair`、`GroupDependency`）+ M1（提供声明数据）。实现率 67%（6/9 项 SPEC_READY）。

```
types.py + exceptions.py ✅ → M1(SDK) ✅ → 【M4(Metadata) ← 当前】 → M2 → M5 → M3
```

### 3.1 唯一公共接口：`build_schema_metadata()`

📍 [builder.py:23-111](phase_2/metadata/builder.py#L23-L111)

整个 M4 就是一个函数——接收 6 个参数（3 个可选），输出一个包含 7 个顶层键的 dict：

```python
def build_schema_metadata(
    groups: dict[str, DimensionGroup],          # 必需
    orthogonal_pairs: list[OrthogonalPair],     # 必需
    target_rows: int,                            # 必需
    measure_dag_order: list[str],                # 必需
    columns: OrderedDict[str, dict] | None = None,       # 可选
    group_dependencies: list[GroupDependency] | None = None,  # 可选
    patterns: list[dict] | None = None,          # 可选
) -> dict[str, Any]:
```

**规范偏差：** stage4 设计为 `build_schema_metadata(store: DeclarationStore) → dict`（接收单一 store 对象），实际接收 6 个拆解参数。这与 M1 不使用 `DeclarationStore` 的偏差一脉相承。

### 3.2 七个键的组装

函数按固定顺序组装 7 个键，最后调用 `_assert_metadata_consistency()` 做后置校验：

#### Key 1: `dimension_groups` — 维度组结构

📍 [builder.py:60-63](phase_2/metadata/builder.py#L60-L63)

```python
for group_name, group in groups.items():
    dimension_groups[group_name] = group.to_metadata()
# 产出：{"entity": {"columns": [...], "hierarchy": [...]}, "time": {...}, ...}
```

遍历 `groups` dict，对每个 `DimensionGroup` 调用 `to_metadata()`（已在第 1 章详解）。temporal 组的 `hierarchy` 仅含 root，`columns` 包含衍生列——忠实反映 M1 组注册时的内部状态。

#### Key 2: `orthogonal_groups` — 正交对列表

📍 [builder.py:66-68](phase_2/metadata/builder.py#L66-L68)

```python
metadata["orthogonal_groups"] = [
    pair.to_metadata() for pair in orthogonal_pairs
]
# 产出：[{"group_a": "entity", "group_b": "patient", "rationale": "..."}, ...]
```

纯透传，零转换。`OrthogonalPair.to_metadata()` 保留原始声明顺序。

**重大问题：** 由于 `run_pipeline()` 调用 M4 时传入 `orthogonal_pairs=[]`（📍 [generator.py:120](phase_2/engine/generator.py#L120)），这个键在运行时**始终为空列表**。M5 的 `check_orthogonal_independence()` 遍历此列表时跳过所有 χ² 检验。详见第 7 章跨模块流分析。

#### Key 3: `group_dependencies` — 跨组依赖

📍 [builder.py:71-76](phase_2/metadata/builder.py#L71-L76)

```python
metadata["group_dependencies"] = [
    dep.to_metadata() for dep in group_dependencies
]
# 产出：[{"child_root": "payment_method", "on": ["severity"],
#          "conditional_weights": {"Mild": {"Insurance": 0.45, ...}, ...}}, ...]
```

`GroupDependency.to_metadata()` 做深拷贝。包含 `conditional_weights`——这是 enrichment 决策的一部分（§2.6 示例中省略了此字段，M5 的 L2 条件转移检查需要它）。

#### Key 4: `columns` — 类型区分描述符（最复杂的键）

📍 [builder.py:78-82](phase_2/metadata/builder.py#L78-L82)（入口）→ 📍 [builder.py:114-175](phase_2/metadata/builder.py#L114-L175)（`_build_columns_metadata()`）

按 `col_type` 五路分支构建不同字段的描述符：

| 类型 | 包含字段 | 代码行 |
|---|---|---|
| `categorical` | `values`, `weights`, `cardinality`(=len(values)), `group`, `parent` | 📍 [builder.py:138-143](phase_2/metadata/builder.py#L138-L143) |
| `temporal` | `start`, `end`, `freq`, `derive`, `group` | 📍 [builder.py:145-150](phase_2/metadata/builder.py#L145-L150) |
| `temporal_derived` | `derivation`, `source`, `group` | 📍 [builder.py:152-155](phase_2/metadata/builder.py#L152-L155) |
| `measure` (stochastic) | `measure_type`, `family`, `param_model`（深拷贝） | 📍 [builder.py:161-165](phase_2/metadata/builder.py#L161-L165) |
| `measure` (structural) | `measure_type`, `formula`, `effects`(dict-of-dict 拷贝), `noise`(dict 拷贝) | 📍 [builder.py:166-171](phase_2/metadata/builder.py#L166-L171) |

stochastic measure 的 `param_model` 深拷贝由 📍 [builder.py:178-191](phase_2/metadata/builder.py#L178-L191) `_deep_copy_param_model()` 处理——递归遍历，遇到嵌套 `effects` dict 则逐层拷贝。

**规范偏差：**
1. §2.6 的 `columns` 是**列表**（每个元素含 `name` 字段），代码实现为 **dict**（列名作 key，描述符不含 `name`）
2. §2.6 structural measure 含 `depends_on` 字段，代码用 `formula`/`effects`/`noise` 替代但未保留 `depends_on`
3. 代码新增了 `temporal_derived` 类型（§2.6 未定义），作为衍生时间列的独立类型

💡 **防御性拷贝贯穿全函数。** 每个 `list` 用 `list()` 拷贝，每个 `dict` 用 `dict()` 或手动遍历拷贝。这是为了确保返回的 metadata dict 与 declaration store **完全解耦**——任何一方的后续修改不会意外影响另一方。对于 Loop B 而言这很关键：auto-fix 可能修改 overrides，但不能意外突变 metadata。

#### Key 5: `measure_dag_order` — 拓扑排序列表

📍 [builder.py:85](phase_2/metadata/builder.py#L85)

```python
metadata["measure_dag_order"] = list(measure_dag_order)
```

一次 `list()` 拷贝，防御性设计。拓扑排序本身由 M1 的 DAG 模块计算，M4 不参与排序逻辑——纯透传。

#### Key 6: `patterns` — 模式规范列表

📍 [builder.py:88-99](phase_2/metadata/builder.py#L88-L99)

```python
metadata["patterns"] = [
    {"type": p["type"], "target": p["target"], "col": p["col"],
     "params": dict(p.get("params", {}))}
    for p in patterns
]
```

包含完整 `params`——这是 enrichment 决策的一部分（M5 L3 模式验证需要 `z_score`、`break_point`、`magnitude` 等参数）。

#### Key 7: `total_rows` — 标量透传

📍 [builder.py:102](phase_2/metadata/builder.py#L102)

```python
metadata["total_rows"] = target_rows
```

直接赋值，零转换。这是声明的目标行数（非实际生成行数）。

### 3.3 后置一致性校验

📍 [builder.py:194-251](phase_2/metadata/builder.py#L194-L251) — `_assert_metadata_consistency()`

组装完成后执行 4 项交叉引用检查：

1. 📍 [builder.py:215-222](phase_2/metadata/builder.py#L215-L222) — `dimension_groups` 中的每个列名必须在 `columns` 中存在
2. 📍 [builder.py:225-231](phase_2/metadata/builder.py#L225-L231) — `measure_dag_order` 中的每个名称必须在 `columns` 中存在
3. 📍 [builder.py:234-241](phase_2/metadata/builder.py#L234-L241) — 每个 pattern 的 `col` 必须指向 measure 列
4. 📍 [builder.py:244-251](phase_2/metadata/builder.py#L244-L251) — 每个 `orthogonal_groups` 的组名必须在 `dimension_groups` 中存在

**行为偏差：** docstring 声明 `raises ValueError`（📍 [builder.py:209](phase_2/metadata/builder.py#L209)），但实际使用 `logger.warning`——不一致时**仅记录日志，不中断执行**。这意味着 M5 可能接收到内部不一致的元数据。

### 3.4 关键约束

1. **元数据不可变性：** 返回的 dict 中所有集合类型均为防御性拷贝，与源数据解耦
2. **声明完备性前提：** M4 假设 M1 的所有声明已完成且通过内部校验，不做重复校验
3. **幂等性：** 同一份 declaration store 输入，多次调用产出相同结果
4. **无 DataFrame 依赖：** M4 不需要也不接收 M2 生成的 DataFrame，可与 M2 并行（设计上支持，代码上串行——M4 在 M2 的 return path 上被调用）

### 3.5 反馈回路参与

M4 本身**不直接参与**任何反馈回路。但间接相关：

🔄 **Loop B（M5→M2）：** M5 使用 M4 产出的 `schema_metadata` 作为"期望值契约"来校验 M2 的输出。当校验失败触发 Loop B 重试时，M2 用新 seed 重新生成 DataFrame，但 **M4 不重新运行**——因为声明未变，元数据不变。

隐含假设：Loop B 的 auto-fix 策略仅调整生成参数，不修改声明。如果 auto-fix 修改了声明，M4 需要重新运行，但当前设计不支持这一路径。

### 3.6 🚧 TODO 地图

| 项目 | 优先级 | 代码状态 | 说明 |
|---|---|---|---|
| Metadata Enrichment | **P0** | **已解决 ✅** | `_build_columns_metadata()` 包含全部 enriched 字段，超越 §2.6 示例 |
| M4 是否需要 DataFrame | P1 | **已解决 ✅** | 函数签名无 DataFrame 参数，允许与 M2 并行 |
| 内部一致性校验行为 | P2 | **部分 ⚠️** | 校验逻辑已实现，但 warning 而非 raise——docstring 与行为不一致 |

### 3.7 本章小结

M4 是整个 Phase 2 中最简洁的模块——一个函数、7 个键、防御性拷贝。它建立了一个关键的**解耦层**：M5 只消费 metadata dict，不直接访问 M1 的 `DeclarationStore` 或内部注册表，避免校验引擎与 SDK 实现耦合。

已解决的规范阻塞项（P0 enrichment）意味着 M4 的输出已包含 M5 所需的**全部字段**——问题在 M5 侧：部分校验函数尚未编写或为 stub。

---

## 第 4 章：装配线——M2 Generation Engine

> 如果 M2 是一个人，TA 的工作是：**工厂流水线操作员**——拿到建筑师（M1）的蓝图和档案员（M4）的说明书后，按固定工序一步步把原材料（随机种子）加工成产品（DataFrame）。TA 不做任何创意性决策，只严格执行蓝图——相同蓝图 + 相同种子 = bit-for-bit 相同的产品。

M2 是构建顺序中**第 3 步**（实际是第 4 步，因为 M4 是第 2 步但代码中 M4 在 M2 内部调用），前置依赖：types.py、M1、M4。实现率 50%（8/16 项 SPEC_READY）。

```
types.py ✅ → M1 ✅ → M4 ✅ → 【M2(Engine) ← 当前】 → M5 → M3
```

### 4.1 四阶段流水线架构

📍 [generator.py:27-133](phase_2/engine/generator.py#L27-L133) — `run_pipeline()`

规范数学表达：`M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)`。代码中各阶段按固定顺序线性串联：

```python
# 📍 generator.py — 实际执行顺序
rng = np.random.default_rng(seed)           # L70 — 初始化 RNG
full_dag = _dag.build_full_dag(...)          # L73 — 预飞 DAG
topo_order = _dag.topological_sort(full_dag) # L76 — 拓扑排序
rows = _skeleton.build_skeleton(...)         # L79 — Stage α：骨架
rows = _measures.generate_measures(...)      # L84 — Stage β：度量（stub）
df = _postprocess.to_dataframe(...)          # L89 — τ_post：dict→DataFrame
df = _patterns_mod.inject_patterns(df, ...)  # L94 — Stage γ：模式注入
df = _realism_mod.inject_realism(df, ...)    # L99 — Stage δ：真实感注入
metadata = _build_meta(...)                  # L118 — M4 调用
return df, metadata                          # L133 — 返回
```

如果把 M2 比作一条汽车装配线：

| 阶段 | 类比 | 操作数据形态 | 状态 |
|---|---|---|---|
| **α Skeleton** | 安装底盘和车身 | `dict[str, np.ndarray]` | ✅ 完整 |
| **β Measures** | 安装发动机和仪表盘 | `dict[str, np.ndarray]` | ⛔ stub |
| **τ_post** | 质检包装 | dict → `pd.DataFrame` | ✅ 完整 |
| **γ Patterns** | 喷涂特殊标记 | `pd.DataFrame` (in-place) | ✅ 2/6 类型 |
| **δ Realism** | 模拟使用磨损 | `pd.DataFrame` (in-place) | ⚠️ 部分 |

💡 **为什么 τ_post 在 γ 之前而非规范数学表达的最外层？** α/β 操作 `dict[str, np.ndarray]`（高效的列式批量操作），γ/δ 需要 `pd.DataFrame`（方便使用 `df.eval()` 和 `df.loc[]` 做子集操作）。这是一个务实的架构决策——功能等价但数据结构在中间切换。

### 4.2 单一 RNG 流——确定性保证

📍 [generator.py:70](phase_2/engine/generator.py#L70)

```python
rng = np.random.default_rng(seed)
```

这个 `rng` 对象按引用传递到每个阶段：

- `build_skeleton(..., rng)` — 📍 [generator.py:80](phase_2/engine/generator.py#L80)（大量 `rng.choice` / `rng.integers`）
- `generate_measures(..., rng)` — 📍 [generator.py:85](phase_2/engine/generator.py#L85)（当前 stub 不消耗）
- `inject_patterns(df, ..., rng)` — 📍 [generator.py:94](phase_2/engine/generator.py#L94)（当前两种注入均确定性，不消耗）
- `inject_realism(df, ..., rng)` — 📍 [generator.py:99](phase_2/engine/generator.py#L99)（`rng.random()` 用于 missing/dirty mask）

单一 RNG 就像一卷预先掷好的骰子胶带——seed 决定了整卷内容。skeleton 先用掉前 N 段，measures 用接下来的 M 段，以此类推。如果你在 skeleton 阶段多加了一列（多消耗了一些"骰子段"），**后面所有度量的随机值都会不同**——确定性是全局的，不是按列隔离的。

💡 **为什么不给每列一个独立 seed？** 替代方案是 `seed + column_index`，这样增删列不影响其他列。但 §2.8 选择了单一流——更简单、更容易推理。对于本系统（每次生成都是全新的、由 LLM 脚本驱动），这个代价可以接受。

### 4.3 预飞 DAG 构建

📍 [generator.py:73-76](phase_2/engine/generator.py#L73-L76)

```python
full_dag = _dag.build_full_dag(columns, groups, group_dependencies, measure_dag)
topo_order = _dag.topological_sort(full_dag)
```

M2 不自己实现 DAG 逻辑——委托给 M1 的 `dag.py`（已在第 2 章详解）。`topo_order` 驱动后续 skeleton（跳过度量列）和 measures（仅处理度量列）的遍历。

💡 **为什么 M2 重复构建 DAG？** M1 在声明阶段已验证无环。但 M2 在生成入口重新构建并排序——防御性编程：即使 M1→M2 数据传递出现异常，M2 也能独立保证不在有环图上运行。成本极低（一次 O(V+E) 拓扑排序），安全收益高。

### 4.4 Stage α — Skeleton 生成（最完整的组件）

📍 [skeleton.py:31-102](phase_2/engine/skeleton.py#L31-L102) — `build_skeleton()`

Skeleton 是 M2 中实现最完整、**零 NEEDS_CLAR** 的文件。顶层调度器遍历 `topo_order`，按 `col_type` 五路分发：

#### 独立根分类 — `sample_independent_root()`

📍 [skeleton.py:109-131](phase_2/engine/skeleton.py#L109-L131)

最简单的情况——从边际权重直接采样：

```python
# 📍 skeleton.py:125
result = rng.choice(values_arr, size=target_rows, p=weights_arr)
```

一次 `rng.choice` 调用生成 `target_rows` 个值。向量化——不是逐行调用。

#### 跨组依赖根 — `sample_dependent_root()`

📍 [skeleton.py:134-179](phase_2/engine/skeleton.py#L134-L179)

条件采样——遍历父列的每个取值，用 mask 筛选对应行，再按条件权重采样：

```python
# 📍 skeleton.py:146-173 — 核心循环
parent_col_name = dep.on[0]            # 只用 on[0]——单列条件
parent_values = rows[parent_col_name]  # 已生成的父列值

for parent_val, child_weight_map in dep.conditional_weights.items():
    mask = parent_values == parent_val          # 匹配父值的行
    weights_for_parent = np.array(...)          # 该父值下的子值权重
    sampled = rng.choice(child_arr, size=n_matching, p=weights_for_parent)
    result[mask] = sampled                      # 填入对应位置
```

注意 `dep.on[0]` 📍 [skeleton.py:146](phase_2/engine/skeleton.py#L146)——硬编码单列依赖，与 M1 NEEDS_CLAR "多列 on" 一致。

#### 组内子分类 — `sample_child_category()`

📍 [skeleton.py:182-230](phase_2/engine/skeleton.py#L182-L230)

两条路径：
- **flat list 权重** → 全行统一采样（📍 [skeleton.py:198-200](phase_2/engine/skeleton.py#L198-L200)），行为等同于独立根
- **per-parent dict 权重** → 按父列值分组条件采样（📍 [skeleton.py:208-224](phase_2/engine/skeleton.py#L208-L224)），与依赖根类似但 parent 在组内

#### 时间根 — `sample_temporal_root()`

📍 [skeleton.py:237-289](phase_2/engine/skeleton.py#L237-L289)

不像分类列从 values 直接采样——时间列需要先构建**合规日期池**，再从池中均匀随机索引：

```python
# 📍 skeleton.py:256-278 — 频率映射 + 日期池构建
FREQ_MAP = {"D": "daily", "MS": "monthly"}

# 根据频率选择不同的日期枚举函数：
# daily  → enumerate_daily_dates()   📍 skeleton.py:292-298
# weekly → enumerate_period_dates()  📍 skeleton.py:301-315
# monthly → enumerate_monthly_dates() 📍 skeleton.py:318-340

dates_as_dt64 = np.array(eligible_dates, dtype="datetime64[D]")
indices = rng.integers(0, len(dates_as_dt64), size=target_rows)  # L281
result = dates_as_dt64[indices]                                   # L282
```

💡 **为什么构建日期池而非在日期范围内直接随机？** 确保采样结果**落在声明的频率网格上**。如果声明了月度频率（`"MS"`），池中只有每月 1 日——不会采样出 1 月 15 日。

三个日期枚举辅助函数：
- `enumerate_daily_dates()` 📍 [skeleton.py:292-298](phase_2/engine/skeleton.py#L292-L298) — `[start, end]` 范围内每日
- `enumerate_period_dates()` 📍 [skeleton.py:301-315](phase_2/engine/skeleton.py#L301-L315) — 指定 weekday 的周期日期
- `enumerate_monthly_dates()` 📍 [skeleton.py:318-340](phase_2/engine/skeleton.py#L318-L340) — 每月 1 日

#### 时间派生 — `derive_temporal_child()`

📍 [skeleton.py:343-378](phase_2/engine/skeleton.py#L343-L378)

纯确定性提取，**无 RNG 消耗**：

```python
# 📍 skeleton.py:357-367
dt_index = pd.DatetimeIndex(temporal_root)

if derivation == "day_of_week":
    result = dt_index.dayofweek.to_numpy(dtype=np.int64)
elif derivation == "month":
    result = dt_index.month.to_numpy(dtype=np.int64)
elif derivation == "quarter":
    result = dt_index.quarter.to_numpy(dtype=np.int64)
elif derivation == "is_weekend":
    result = (dt_index.dayofweek.to_numpy(dtype=np.int64) >= 5).astype(bool)
```

💡 **Skeleton 的性能设计。** 虽然 §2.4 的概念模型描述了 per-row loop，但代码为每一列一次性生成 `target_rows` 个值（向量化）。1000 行 × 20 列只需 ~20 次 `rng.choice` 调用，而非 20000 次逐行调用。

### 4.5 Stage β — 度量生成（stub 状态）

📍 [measures.py:19-63](phase_2/engine/measures.py#L19-L63) — `generate_measures()`

**当前状态：框架就位，核心 stub。** 调度器遍历 `topo_order` 并按 `measure_type` 区分 stochastic/structural，但两个分支都只打 debug 日志后 `continue`，返回 rows dict **不做任何修改**。

```python
# 📍 measures.py:43-61 — 调度循环
for col_name in topo_order:
    if col_meta.get("type") != "measure":
        continue
    if measure_type == "stochastic":
        logger.debug("... skipping stochastic '%s' (BLOCKED).", col_name)
    elif measure_type == "structural":
        logger.debug("... skipping structural '%s' (BLOCKED).", col_name)
return rows  # 原样返回
```

两个内部函数均 `raise NotImplementedError`：

- `_sample_stochastic()` 📍 [measures.py:66-81](phase_2/engine/measures.py#L66-L81) — 标注 "Blockers 2 & 3"
- `_eval_structural()` 📍 [measures.py:84-99](phase_2/engine/measures.py#L84-L99) — 标注 "Blocker 2: formula DSL"

参数签名已就位：`overrides` 参数（📍 [measures.py:24](phase_2/engine/measures.py#L24)）是 Loop B auto-fix 的预留载体——M5 调整参数后通过此 dict 注入，但当前无可测试的行为。

如果 skeleton 是给居民分配身份证，那么度量就是"根据身份查保险手册，算出费用应该服从什么分布，然后掷骰子得到具体数字"。手册（参数模型）已经写好了，但掷骰子的机器（采样器）还没装上。

**🚧 P0 阻塞：** 公式求值器是 Stage β 的核心瓶颈。stage3 建议使用受限 AST 表达式求值器，仅允许 `+`/`-`/`*`/`/`/`**`、数字字面量和变量名。无函数调用，无属性访问。

### 4.6 τ_post — DataFrame 组装

📍 [postprocess.py:19-82](phase_2/engine/postprocess.py#L19-L82) — `to_dataframe()`

将 `dict[str, np.ndarray]` 转换为 `pd.DataFrame`，同时做 dtype 转换：

```python
# 📍 postprocess.py:49-53
ordered_cols = [col for col in topo_order if col in rows]  # 按拓扑序排列
data = {col: rows[col] for col in ordered_cols}
df = pd.DataFrame(data, index=range(target_rows))           # RangeIndex
```

Dtype 策略（📍 [postprocess.py:56-74](phase_2/engine/postprocess.py#L56-L74)）：

| 列类型 | dtype |
|---|---|
| categorical | `object`（Python str） |
| temporal | `datetime64[ns]` |
| temporal_derived（day_of_week/month/quarter） | `int64` |
| temporal_derived（is_weekend） | `bool` |
| measure | `float64`（未来实现时） |

### 4.7 Stage γ — 模式注入

📍 [patterns.py:29-82](phase_2/engine/patterns.py#L29-L82) — `inject_patterns()`

调度器遍历 `patterns` 列表，按 `pattern_type` 分发：

```python
# 📍 patterns.py:48-74
for pattern in patterns:
    pattern_type = pattern["type"]
    if pattern_type == "outlier_entity":
        df = inject_outlier_entity(df, pattern)
    elif pattern_type == "trend_break":
        df = inject_trend_break(df, pattern, columns)
    elif pattern_type in ("ranking_reversal", "dominance_shift", ...):
        raise NotImplementedError(...)   # 🚧 4/6 类型 stub
```

模式注入就是在完美的模拟数据中"种下"故意的异常信号——给 Phase 3 QA 仪表盘设计的"预埋答案"。

#### `inject_outlier_entity()` — 异常实体注入

📍 [patterns.py:85-153](phase_2/engine/patterns.py#L85-L153)

算法（5 步）：

1. `df.eval(target_expr)` 获取目标行布尔 mask 📍 [patterns.py:110](phase_2/engine/patterns.py#L110)
2. 零行匹配 → 抛 `PatternInjectionError` 📍 [patterns.py:113-120](phase_2/engine/patterns.py#L113-L120)
3. 计算全局 `mean` 和 `std` 📍 [patterns.py:130-131](phase_2/engine/patterns.py#L130-L131)
4. 目标均值 = `global_mean + z_score × global_std` 📍 [patterns.py:142](phase_2/engine/patterns.py#L142)
5. 偏移量 = `desired_mean − subset_mean`，目标子集统一加偏移 📍 [patterns.py:144-146](phase_2/engine/patterns.py#L144-L146)

这保证注入后子集均值**精确达到** z_score 倍标准差处，可通过 M5 L3 的 z-score ≥ 2.0 校验（注入时 z_score 默认 3.0，验证阈值故意放松到 2.0，留出采样波动余量）。

防御：列不存在时优雅降级（warn + skip）📍 [patterns.py:122-128](phase_2/engine/patterns.py#L122-L128)——当度量未生成时（当前 stub 状态）不会崩溃。

#### `inject_trend_break()` — 趋势断裂注入

📍 [patterns.py:156-237](phase_2/engine/patterns.py#L156-L237)

算法（5 步）：

1. `df.eval(target_expr)` 获取目标行 mask 📍 [patterns.py:202](phase_2/engine/patterns.py#L202)
2. 在列注册表中查找唯一时间列 📍 [patterns.py:186-189](phase_2/engine/patterns.py#L186-L189)
3. 构建断点后 mask：`target & (temporal ≥ break_point)` 📍 [patterns.py:223](phase_2/engine/patterns.py#L223)
4. 后断点行的目标列 `× (1 + magnitude)` 📍 [patterns.py:227-229](phase_2/engine/patterns.py#L227-L229)
5. `magnitude` 直接对应 M5 L3 的 "幅度 > 15% 相对变化" 检查

💡 **为什么注入在 DataFrame 全部生成后才执行？** 模式需要全局统计信息（全局均值/标准差）和跨行时间信息（断点前后分割），这些在逐行生成时不可用。

**注意事项：**
- 两个注入器都接收 `rng` 但当前都不消耗它——注入操作是确定性的（纯数学位移/缩放）
- 代码**未返回 `pattern_mask`**（stage4 设计有但未实现），意味着 realism 阶段无法知道哪些单元格被模式修改过——🚧 P2 问题，可能导致 realism NaN 注入破坏模式信号

### 4.8 Stage δ — 真实感注入

📍 [realism.py:25-64](phase_2/engine/realism.py#L25-L64) — `inject_realism()`

执行优先级：**missing 先于 dirty**——避免浪费工作扰动即将被 NaN 覆盖的单元格。

```python
# 📍 realism.py:51-62
if missing_rate > 0.0:
    df = inject_missing_values(df, missing_rate, rng)      # 先注入缺失
if dirty_rate > 0.0:
    df = inject_dirty_values(df, columns, dirty_rate, rng)  # 再注入脏值
if censoring is not None:
    raise NotImplementedError(...)  # 🚧 censoring stub
```

#### `inject_missing_values()` — 全列均匀 NaN 注入

📍 [realism.py:67-99](phase_2/engine/realism.py#L67-L99)

```python
# 📍 realism.py:91-92
mask = rng.random(size=df.shape) < missing_rate
df = df.mask(mask)
```

每个单元格独立概率 `missing_rate` 成为 NaN。不区分列类型——分类列、时间列、度量列均匀注入。

#### `inject_dirty_values()` — 仅分类列字符级扰动

📍 [realism.py:102-163](phase_2/engine/realism.py#L102-L163)

只对 `type == "categorical"` 的列操作。对每个非 NaN 单元格以 `dirty_rate` 概率调用 `perturb_string()`。

`perturb_string()` 📍 [realism.py:166-204](phase_2/engine/realism.py#L166-L204) 三选一扰动：

| 扰动类型 | 操作 | 条件 |
|---|---|---|
| 0 — swap | 交换两个相邻字符 | len ≥ 2 |
| 1 — delete | 删除一个字符 | len ≥ 2 |
| 2 — insert | 在随机位置插入随机小写字母 | 总是可执行 |

💡 这里的"脏"是**单字符拼写错误**级别的——把 `"General"` 变成 `"Gneeral"`（swap）或 `"Gneral"`（delete）。不是替换成完全不同的值。

### 4.9 M4 调用——metadata 在 return path 上构建

📍 [generator.py:102-126](phase_2/engine/generator.py#L102-L126)

```python
# 📍 generator.py:106-113 — 从 full_dag 提取度量子 DAG 排序
measure_names = {col_name for col_name, col_meta in columns.items()
                 if col_meta.get("type") == "measure"}
if measure_names:
    _, measure_order = _dag.extract_measure_sub_dag(full_dag, measure_names)
else:
    measure_order = []

# 📍 generator.py:118-126 — 调用 M4
metadata = _build_meta(
    groups=groups,
    orthogonal_pairs=[],            # ← 硬编码空列表！
    target_rows=target_rows,
    measure_dag_order=list(measure_order),
    columns=columns,
    group_dependencies=group_dependencies,
    patterns=patterns,
)
```

**`orthogonal_pairs=[]` 的影响链：** `run_pipeline()` 签名中没有 `orthogonal_pairs` 参数（它不影响行生成逻辑），但 M4 需要它来填充 `schema_metadata["orthogonal_groups"]`。结果：`orthogonal_groups` 始终为空 → M5 的 χ² 检验被跳过 → Phase 3 无法得知哪些组被声明为正交。修复复杂度低——`run_pipeline()` 加一个参数即可。

### 4.10 关键约束与不变量

1. **确定性不变量：** 相同 `(seed, declarations)` → 相同输出。由单一 `rng` 的顺序消耗保证 📍 [generator.py:70](phase_2/engine/generator.py#L70)
2. **阶段顺序不变量：** α → β → τ_post → γ → δ 不可重排
   - 非度量列必须在度量之前（度量参数依赖分类上下文）
   - 度量必须在模式之前（模式修改度量值）
   - 模式必须在 realism 之前（realism 降级不应在模式注入前破坏数据）
3. **DAG 顺序不变量：** 列生成严格按拓扑序——列永远不会在其依赖之前生成 📍 [skeleton.py:55](phase_2/engine/skeleton.py#L55) / 📍 [measures.py:43](phase_2/engine/measures.py#L43)
4. **无 LLM 调用不变量：** M2 是纯计算。LLM 的贡献在 M1 的脚本执行阶段已结束
5. **行数不变量：** skeleton 精确生成 `target_rows` 行。后续阶段修改值但不增减行
6. **声明只读不变量：** M2 不修改声明存储——Loop B 的参数调整通过 `overrides` 叠加层实现

### 4.11 🔄 反馈回路参与——Loop B

M2 在 Loop B 中是**被动执行方**——验证失败时以新 seed 和参数覆盖重新执行整个流水线：

```
M5 validate() → 失败
    → match_strategy(check.name) → 策略函数调整参数
    → run_pipeline(seed=base_seed+attempt, overrides=overrides)
        └→ generate_measures(overrides=...)  ← 签名就绪，stub 不消耗
    → M5 再次 validate()
    → 重复最多 3 次
```

M2 不感知重试计数——由 M5 的 `generate_with_validation()` 控制（尚未实现）。

**当前限制：** 因 Stage β stub，auto-fix 的效果无法体现。即使传入 `overrides`，度量生成不执行，DataFrame 中无度量列，L2/L3 大部分检查不可触发。

### 4.12 🚧 TODO 地图

| 项目 | 优先级 | 代码状态 | 影响 |
|---|---|---|---|
| 公式求值机制 | **P0** | `_eval_structural()` NotImplementedError 📍 [measures.py:96-98](phase_2/engine/measures.py#L96-L98) | 解锁全部度量生成 + L2 校验 |
| 随机度量采样 | **P0** | `_sample_stochastic()` NotImplementedError 📍 [measures.py:78-81](phase_2/engine/measures.py#L78-L81) | 同上 |
| `τ_post` 行为 | P2 | **已实现 ✅** — dict→DataFrame + dtype 转换 | — |
| 模式组合优先级 | P3 | 隐式按声明顺序循环 📍 [patterns.py:48](phase_2/engine/patterns.py#L48) | 重叠模式按最后一个生效 |
| 模式注入破坏公式一致性 | P2 | 无保护——不检查目标列类型，不返回 pattern_mask | M5 L2 残差检查 |
| Realism 注入语义 | P2 | missing ✅ dirty ✅ censoring ❌ 📍 [realism.py:59-62](phase_2/engine/realism.py#L59-L62) | M5 L1/L3 |
| 结构度量 noise={} | P2 | 不可达——度量生成整体 stub | M5 L2 除零 |
| Realism 与模式交互 | P2 | 无保护——realism 不接收 pattern_mask | 🔄 Loop B 相关 |

### 4.13 本章小结

M2 建立了一个**确定性、阶段固定、DAG 排序**的生成流水线。当前可运行的端到端路径是：

```
seed → rng → full_dag + topo_order → skeleton(仅非度量列) → DataFrame → patterns(2/6) → realism(部分) → metadata
```

**关键缺口：** Stage β 整体 stub，导致 DataFrame 中无度量列。这意味着：
- L2 统计验证全部不可触发（没有度量数据可校验分布）
- L3 模式验证中 outlier_entity 和 trend_break 在当前会被优雅降级（列不存在→warn+skip）
- Loop B 端到端路径事实上不可触发

解除 P0-2（公式求值器）将同时解锁 `_sample_stochastic` 和 `_eval_structural`，是整个系统突破 50% 实现率的关键瓶颈。

---

# 第三部分：M5 校验引擎 + M3 LLM 编排

这一部分覆盖构建顺序中的第 4、5 步——M5 验证生成结果是否忠实于声明，M3 编排 LLM 生成合法脚本并驱动完整重试循环。M5 先于 M3 讲解，因为 M3 需要理解 M5 的 Loop B 才能完整理解整个嵌套重试架构。

---

## 第 5 章：质检站——M5 Validation Engine

> 如果 M5 是一个人，TA 的工作是：**三级质检员**——先目视检查外包装（L1 结构验证），再抽样化验内容物（L2 统计验证），最后做专项抽查（L3 模式验证）。检查不过关的产品不扔掉，而是交给自动返修流水线（Loop B）调参数重做。

M5 是构建顺序中**第 4 步**，前置依赖：types.py（Check/ValidationReport）、M1（声明验证逻辑参考）、M4（metadata 契约）、M2（DataFrame 生成）。实现率 62%（13/21 项 SPEC_READY）。

```
types.py ✅ → M1 ✅ → M4 ✅ → M2 ✅ → 【M5(Validation) ← 当前】 → M3
```

### 5.1 编排入口：`SchemaAwareValidator`

📍 [validator.py:24-146](phase_2/validation/validator.py#L24-L146)

M5 的核心是一个编排类，持有 metadata 的不可变引用，提供单一 `validate()` 方法：

```python
# 📍 validator.py:40-46 — 构造
class SchemaAwareValidator:
    def __init__(self, meta: dict[str, Any]) -> None:
        self.meta = meta      # 不可变引用，不直接访问 DeclarationStore
```

```python
# 📍 validator.py:48-83 — 验证主入口
def validate(self, df: pd.DataFrame, patterns: list[dict] | None = None) -> ValidationReport:
    report = ValidationReport()

    # L1: 结构验证
    l1_checks = self._run_l1(df)              # 📍 L65
    report.add_checks(l1_checks)

    # L2: 统计验证 — 被跳过（全是 stub）
    # （📍 L68-70 注释说明）

    # L3: 模式验证
    if patterns:
        l3_checks = self._run_l3(df, patterns)  # 📍 L74
        report.add_checks(l3_checks)

    return report
```

💡 **M5 不直接访问 `DeclarationStore`。** 它只消费 M4 产出的 `schema_metadata` dict——这保持了模块边界清晰，M5 不与 SDK 内部实现耦合。

**当前行为：** 运行 L1（4 项检查）→ 跳过 L2（stub）→ 运行 L3（仅 outlier_entity 和 trend_break）。无短路机制——所有层无条件运行。

### 5.2 L1 层：结构验证——"目视检查"

L1 不看数据内容，只核对数量、标签和外包装是否与装箱单（metadata）一致。

📍 [validator.py:85-105](phase_2/validation/validator.py#L85-L105) — `_run_l1()` 编排 4 项检查：

#### L1-1: Row Count — 行数偏差检查 ✅

📍 [structural.py:22-48](phase_2/validation/structural.py#L22-L48)

```python
target = meta["total_rows"]
actual = len(df)
deviation = abs(actual - target) / target
passed = deviation < 0.1    # 10% 容忍度
```

工厂订单要求 1000 件，交付 950 件（偏差 5%）可以接受；交付 800 件（偏差 20%）则不合格。

💡 **为什么是 10% 而非精确匹配？** 模式注入（Stage γ）或去重操作可能微调行数。绝对精确要求会导致几乎所有随机生成都失败。

#### L1-2: Categorical Cardinality — 分类基数检查 ✅

📍 [structural.py:51-110](phase_2/validation/structural.py#L51-L110)

```python
# 📍 structural.py:75-78 — 兼容 dict 和 list 两种 columns 格式
if isinstance(columns_meta, dict):
    items = [{"name": name, **info} for name, info in columns_meta.items()]
else:
    items = columns_meta

# 📍 structural.py:90-94 — 优先取 cardinality，回退到 len(values)
declared = col.get("cardinality")
if declared is None:
    declared = len(col.get("values", []))

# 📍 structural.py:101-102 — 精确匹配
actual = df[col_name].nunique()
passed = actual == declared
```

声明了 5 种医院类型，生成数据中只出现了 4 种（某个稀有类型从未被抽样到）——不合格。这里用**精确匹配**（不像 row count 的 10% 容忍），因为类别缺失意味着该类别的所有下游统计都缺失——是结构性错误，不是采样波动。

#### L1-3: Orthogonal Independence — 正交 χ² 检验 ✅

📍 [structural.py:113-177](phase_2/validation/structural.py#L113-L177)

```python
# 📍 structural.py:143-144 — 取正交对的根列
root_a = dimension_groups[group_a_name]["hierarchy"][0]
root_b = dimension_groups[group_b_name]["hierarchy"][0]

# 📍 structural.py:146 — 构建列联表
ct = pd.crosstab(df[root_a], df[root_b])

# 📍 structural.py:148-157 — 退化检查：< 2×2 直接 fail
if ct.shape[0] < 2 or ct.shape[1] < 2:
    return Check(passed=False, detail="Degenerate contingency table...")

# 📍 structural.py:160 — χ² 检验
_, p_val, _, _ = scipy.stats.chi2_contingency(ct)

# 📍 structural.py:169 — 高 p 值 = 通过
passed = p_val > 0.05
```

注意方向：**高 p 值是通过**。我们期望的是"数据无法证明两个变量相关"，而非"数据证明了独立性"。这是频率论假设检验的标准逻辑。

**实际运行状态：** 由于 `orthogonal_pairs=[]` 数据丢失（§4.9），`orthogonal_groups` 始终为空 → 此检查**被跳过**。修复 `run_pipeline()` 传参后即可恢复工作。

#### L1-4: Measure DAG Acyclicity — DAG 无环冗余检查 ✅

📍 [structural.py:180-209](phase_2/validation/structural.py#L180-L209)

```python
# 📍 structural.py:194-196
dag_order = meta.get("measure_dag_order", [])
unique_count = len(set(dag_order))
passed = unique_count == len(dag_order)  # 重复节点 = 有环
```

用**重复检测**而非真正的图遍历——合理简化，因为拓扑排序的输出天然不含重复。像银行在 ATM 已验过密码后，柜台还要求再验一次——不是不信任 ATM，而是多一层保险。

#### L1 缺失项

| 检查 | 规范要求 | 代码状态 |
|---|---|---|
| Root Marginal Weight | 观测频率与声明权重最大偏差 < 0.10 | ❌ 函数未编写 |
| Measure Finiteness | 每个度量列 `notna().all()` 且 `isfinite().all()` | ❌ 函数未编写 |

Marginal Weight 逻辑清晰但依赖 enriched metadata 中的 `values`/`weights`（M4 P0 已提供）。Measure Finiteness 极简但与 realism 的 `missing_rate` NaN 注入冲突（先验证还是先注入 realism？——🚧 P2）。

### 5.3 L2 层：统计验证——"化验环节" ⛔ 全部 stub

L2 打开箱子抽样检测内容物是否符合配方。三项检查**全部 `raise NotImplementedError`**：

| 检查 | 位置 | 规范要求 | stub 标注 |
|---|---|---|---|
| Stochastic KS Test | 📍 [statistical.py:55-69](phase_2/validation/statistical.py#L55-L69) | 枚举预测器笛卡尔积单元格，每个单元格内 `kstest(data, cdf)` p > 0.05 | "BLOCKED pending Blockers 2 & 3" |
| Structural Residuals | 📍 [statistical.py:72-86](phase_2/validation/statistical.py#L72-L86) | 用公式重算预测值，残差均值近零 + std 与 noise_sigma 一致 | "BLOCKED" |
| Group Dep Transitions | 📍 [statistical.py:89-102](phase_2/validation/statistical.py#L89-L102) | 交叉表归一化后与 `conditional_weights` 最大偏差 < 0.10 | "BLOCKED pending Blocker 5" |

**已就绪的辅助函数：** `max_conditional_deviation()` 📍 [statistical.py:21-52](phase_2/validation/statistical.py#L21-L52) 是为 group dependency 检查准备的纯计算工具——遍历两个嵌套 dict 的所有父键×子键组合，返回最大绝对偏差。函数本身完整实现，但调用方仍是 stub。

**`validator.py` 中 L2 被注释跳过**（📍 [validator.py:68-70](phase_2/validation/validator.py#L68-L70)）——如果调用 stub 函数会抛异常中断验证。

### 5.4 L3 层：模式验证——"专项抽查"

L3 不看整体分布，专门检查注入的异常模式是否在数据中可被探测到。

📍 [validator.py:107-145](phase_2/validation/validator.py#L107-L145) — `_run_l3()` 遍历 patterns，按 type 分发：

```python
# 📍 validator.py:127-136
if pattern_type == "outlier_entity":
    checks.append(_l3.check_outlier_entity(df, pattern))
elif pattern_type == "trend_break":
    checks.append(_l3.check_trend_break(df, pattern, self.meta))
else:
    logger.debug("no check for type '%s'.", pattern_type)  # 静默跳过
```

异常安全：📍 [validator.py:137-143](phase_2/validation/validator.py#L137-L143) `except Exception` 捕获 L3 检查中的任何异常，转换为 `Check(passed=False)`——不让单个模式验证崩溃阻断整个报告。

#### L3-1: Outlier Entity — 异常实体 z-score 检查 ✅

📍 [pattern_checks.py:23-69](phase_2/validation/pattern_checks.py#L23-L69)

```python
# 📍 pattern_checks.py:52-53
global_mean = float(df[col].mean())
global_std = float(df[col].std())

# 📍 pattern_checks.py:62-64
subset_mean = float(df.loc[target_idx, col].mean())
z = abs(subset_mean - global_mean) / global_std
passed = z >= 2.0    # 验证阈值 2.0 < 注入阈值 3.0
```

注入时 z_score 默认 3.0，验证阈值故意放松到 2.0——留出采样波动余量。代码读取了 `params["z_score"]`（📍 [pattern_checks.py:40](phase_2/validation/pattern_checks.py#L40)）但**硬编码用 2.0 判断**——即使用户声明了更高的 z_score，验证标准不会相应提高。

防御：零行匹配 → fail（📍 [pattern_checks.py:45-50](phase_2/validation/pattern_checks.py#L45-L50)）；`std == 0` 或 `NaN` → fail（📍 [pattern_checks.py:55-60](phase_2/validation/pattern_checks.py#L55-L60)）。

#### L3-2: Trend Break — 趋势断裂幅度检查 ✅

📍 [pattern_checks.py:84-155](phase_2/validation/pattern_checks.py#L84-L155)

```python
# 📍 pattern_checks.py:107-108 — 查找时间列
temporal_col = _find_temporal_column(meta)  # 📍 pattern_checks.py:72-81
# 硬编码查找 "time" 组 → dimension_groups["time"]["hierarchy"][0]

# 📍 pattern_checks.py:120-124 — 按断点拆分
temporal_values = pd.to_datetime(df[temporal_col], errors="coerce")
before_mask = temporal_values < break_point_dt
after_mask = temporal_values >= break_point_dt

# 📍 pattern_checks.py:149-150
ratio = abs(after_mean - before_mean) / abs(before_mean)
passed = ratio > 0.15    # 15% 相对变化阈值
```

防御：前后任一期行数为零 → fail（📍 [pattern_checks.py:129-137](phase_2/validation/pattern_checks.py#L129-L137)）；`before_mean == 0` → fail（除零保护，📍 [pattern_checks.py:142-147](phase_2/validation/pattern_checks.py#L142-L147)）。

`_find_temporal_column()` 📍 [pattern_checks.py:72-81](phase_2/validation/pattern_checks.py#L72-L81) 硬编码查找 `"time"` 组——如果时间组名称不同会查找失败。

#### L3 缺失项

| 检查 | 规范状态 | 代码状态 |
|---|---|---|
| Ranking Reversal | SPEC_READY（有伪代码） | ❌ 完全缺失，`_run_l3` 静默跳过 |
| Dominance Shift | 🚧 P1 | ❌ 静默跳过 |
| Convergence | 🚧 P1 | ❌ 静默跳过 |
| Seasonal Anomaly | 🚧 P1 | ❌ 静默跳过 |

### 5.5 🔄 Auto-Fix 循环（Loop B）——"自动返修流水线"

如果 L1/L2/L3 是质检员发现问题，Loop B 是**直接在车间调参数重做**——不用找设计师（LLM），无需 Loop A 参与。

#### 分发表：`match_strategy()`

📍 [autofix.py:25-43](phase_2/validation/autofix.py#L25-L43)

```python
def match_strategy(check_name: str, auto_fix: dict[str, Any]) -> Optional[Any]:
    for glob_pattern, strategy_fn in auto_fix.items():
        if fnmatch.fnmatch(check_name, glob_pattern):
            return strategy_fn
    return None
```

用 `fnmatch.fnmatch` 对 check name 做 glob 匹配——`"ks_wait_minutes_Mild"` 匹配 `"ks_*"` → 调用 `widen_variance`。按声明顺序匹配第一个。

**设计中的分发映射（stage4 规划，未编码为默认实例）：**

| Glob Pattern | 策略函数 | 目标 |
|---|---|---|
| `ks_*` | `widen_variance` | L2 KS 检验失败 |
| `orthogonal_*` | `reshuffle_pair` | L1 正交失败 |
| `outlier_*` | `amplify_magnitude` | L3 outlier 失败 |
| `trend_*` | `amplify_magnitude` | L3 trend 失败 |

#### 策略 A：`widen_variance()` — 放大方差

📍 [autofix.py:46-82](phase_2/validation/autofix.py#L46-L82)

```python
# 📍 autofix.py:63-76
if "sigma" in params:   target_key = "sigma"
elif "scale" in params:  target_key = "scale"
else: raise InvalidParameterError(...)

new_params = dict(params)                    # 新 dict，不修改原始
new_params[target_key] = old_value * factor  # 默认 ×1.2
return new_params
```

KS 检验失败 → σ 太小 → 放大方差，让生成分布更宽松以通过拟合检验。

#### 策略 B：`amplify_magnitude()` — 放大模式幅度

📍 [autofix.py:85-123](phase_2/validation/autofix.py#L85-L123)

```python
# 📍 autofix.py:104-117
if "z_score" in inner_params:      target_key = "z_score"
elif "magnitude" in inner_params:  target_key = "magnitude"
else: raise InvalidParameterError(...)

new_spec = copy.deepcopy(pattern_spec)           # 深拷贝保护原始
new_spec["params"][target_key] *= factor          # 默认 ×1.3
return new_spec
```

L3 outlier/trend 失败 → 注入信号不足 → 放大 z_score 或 magnitude。

#### 策略 C：`reshuffle_pair()` — 打乱列破坏虚假相关

📍 [autofix.py:126-158](phase_2/validation/autofix.py#L126-L158)

```python
# 📍 autofix.py:148-152
new_df = df.copy()
perm = rng.permutation(len(new_df))
shuffled = new_df[column].take(perm).copy()
shuffled.index = new_df.index
new_df[column] = shuffled
return new_df
```

χ² 失败 → 正交组的根列出现虚假相关 → 直接打乱一列的值。这是唯一直接操作 DataFrame 的策略（其他两个修改参数→重新生成）。

💡 **三个策略都是纯函数**——接收旧参数/数据，返回新参数/数据，不修改外部状态。这是为了与 `ParameterOverrides` 机制配合（frozen store 只读，所有变异走 overrides dict）。

#### Loop B 已就绪 vs 缺失组件

| 组件 | 状态 |
|---|---|
| `validate()` 返回 `ValidationReport` | ✅（L1 部分 + L3 部分） |
| `report.all_passed` / `report.failures` | ✅ |
| `match_strategy()` glob 匹配 | ✅ |
| 三个策略函数 | ✅ 纯函数就绪 |
| `run_pipeline(overrides=...)` 签名 | ✅ |
| **`generate_with_validation()` 循环框架** | **❌ 未实现** |
| **`AUTO_FIX` 默认分发表实例化** | **❌ 未编码** |
| **`ParameterOverrides` 数据结构** | **❌ 未定义** |
| **策略输出 → overrides 格式适配** | **❌ 未编码** |
| **seed 偏移逻辑 `seed + attempt`** | **❌ 未编码** |

所有策略函数已实现为独立纯函数，但缺少将它们串联进重试循环的**胶水代码**。三个策略能产出修改后的参数，但没有消费者将这些参数注入下一次 `run_pipeline()` 调用。

### 5.6 关键约束矩阵

| 约束 | 来源 | 阈值 | 代码状态 |
|---|---|---|---|
| Row count 偏差 | §2.9 L1 | < 10% | ✅ 硬编码 0.1 |
| Cardinality 精确匹配 | §2.9 L1 | `==` | ✅ |
| Marginal weight 偏差 | §2.9 L1 | < 0.10 | ❌ 未实现 |
| 度量有限且非空 | §2.9 L1 | `notna` + `isfinite` | ❌ 未实现 |
| 正交 χ² | §2.9 L1 | p > 0.05 | ✅（但 orthogonal_pairs 为空→跳过） |
| DAG 无环 | §2.9 L1 | 无重复 | ✅ |
| KS test per cell | §2.9 L2 | p > 0.05 | ⛔ stub |
| 残差均值 | §2.9 L2 | < 0.1×std | ⛔ stub |
| 残差 std 偏差 | §2.9 L2 | < 20% | ⛔ stub |
| 条件转移偏差 | §2.9 L2 | < 0.10 | ⛔ stub |
| Outlier z-score | §2.9 L3 | ≥ 2.0 | ✅ 硬编码 2.0 |
| Trend break ratio | §2.9 L3 | > 15% | ✅ 硬编码 0.15 |
| Ranking reversal | §2.9 L3 | corr < 0 | ❌ 未实现 |
| Loop B max retries | §2.9 | 3 | ⚠️ 策略就绪，循环缺失 |

### 5.7 🚧 TODO 地图

| 项目 | 优先级 | 核心阻塞 | 影响 |
|---|---|---|---|
| M5 数据源——meta 够用还是需要 store | **P0** | §2.6 示例缺字段 | **已解决** ✅（M4 enrichment 已提供） |
| Auto-fix 策略集成 | **P0** | 循环框架 + ParameterOverrides 未定义 | Loop B 端到端 |
| Auto-fix 变异目标 | **P0** | store 只读 vs override dict | **已确认**——走 overrides 叠加层 |
| L2 noise_sigma=0 除零 | P1 | 公式 `residuals.std()/noise_sigma` | 改用 `residuals.std() < 1e-6` |
| KS-test 单元格枚举 | P1 | 迭代器未定义 | 枚举 effects 笛卡尔积 |
| dominance_shift 验证 | P1 | 内部黑盒 | 定义为排名变化 |
| convergence/seasonal_anomaly | P1 | §2.9 无验证逻辑 | Stub 为 passed=True |
| 验证在 realism 之前还是之后 | P2 | NaN 与 finiteness 冲突 | 先验证后注入 realism |

### 5.8 本章小结

M5 建立了一个**三层验证 + 策略驱动自动修复**的架构。已完成的核心组件：

- **编排器** `SchemaAwareValidator` 正确隔离了 M5 与 M1——只消费 metadata dict
- **L1** 4/6 项检查已实现，覆盖行数、基数、正交性、DAG 无环
- **L3** 2/4 项检查已实现，覆盖 outlier entity 和 trend break
- **Auto-fix** 3 个纯函数策略就绪，glob 分发表就绪

**关键缺口：** L2 全部 stub + Loop B 循环框架缺失。当 Stage β 解除阻塞后，L2 的三项 stub 需要实现，`generate_with_validation()` 循环需要编写来串联策略函数 → overrides → `run_pipeline()` 重试。

---

## 第 6 章：总调度——M3 LLM Orchestration

> 如果 M3 是一个人，TA 的工作是：**翻译官兼谈判代表**——把人类描述的场景需求翻译成 LLM 能理解的 prompt，拿到 LLM 写的脚本后在沙箱中试运行，如果脚本出错就把错误信息格式化后交给 LLM "再谈一次"，最多谈 3 轮。

M3 是构建顺序中**最后一步**——流水线入口但构建顺序终点，因为理解它需要先理解它调用的所有下游模块。实现率 45%（5/11 项 SPEC_READY）。

```
types.py ✅ → M1 ✅ → M4 ✅ → M2 ✅ → M5 ✅ → 【M3(Orchestration) ← 当前】
```

### 6.1 System Prompt Template

📍 [prompt.py:35-200](phase_2/orchestration/prompt.py#L35-L200) — `SYSTEM_PROMPT_TEMPLATE: Final[str]`

这是 LLM 行为的**唯一约束机制**——一份完整的系统提示模板，包含五个区域：

| 区域 | 内容 | 大致行号 |
|---|---|---|
| 角色前言 | "You are an expert Data Scientist Agent..." | 📍 prompt.py:37-43 |
| SDK 白名单 | Step 1 四方法 + Step 2 四方法，含内联签名注释 | 📍 prompt.py:45-63 |
| 分布/模式白名单 | 8 种 families, 6 种 patterns | 📍 prompt.py:64-68 |
| HC1-HC9 硬约束 | 九条二值通过/失败规则 | 📍 prompt.py:70-82 |
| 软指引 + One-shot 示例 | 上海急诊 `build_fact_table(seed=42)` | 📍 prompt.py:84-199 |

#### HC1-HC9：九条硬约束

| HC | 约束 | 保护的属性 |
|---|---|---|
| HC1 | 每行 = 一个不可分割事件 | 语义粒度 |
| HC2 | ≥2 维度组 + ≥2 度量 | 结构最小丰富度 |
| HC3 | Step 1（列声明）全部在 Step 2（关系）之前 | SDK 内部阶段排序 |
| HC4 | ≥1 `declare_orthogonal()` | 正交声明存在性 |
| HC5 | ≥1 `add_measure_structural()` + ≥2 `inject_pattern()` | 结构度量 + 模式注入 |
| HC6 | 纯合法 Python，返回 `sim.generate()` | 输出格式 |
| HC7 | 度量依赖必须无环（DAG） | 度量 DAG |
| HC8 | 跨组依赖仅根列 + 根 DAG 无环 | 根级 DAG |
| HC9 | 每个符号效果必须有数值定义 | 符号完备性 |

HC7/HC8/HC9 在 M1 中有运行时验证对应（`CyclicDependencyError`/`NonRootDependencyError`/`UndefinedEffectError`）——prompt 中的声明是预防性提示，M1 的验证是最终防线。

#### 渲染函数

📍 [prompt.py:207-262](phase_2/orchestration/prompt.py#L207-L262) — `render_system_prompt(scenario_context: str) -> str`

```python
# 📍 prompt.py:252-253
rendered = SYSTEM_PROMPT_TEMPLATE.replace("{scenario_context}", scenario_context)
```

💡 **为什么用 `str.replace()` 而非 `str.format()` 或 Jinja2？** §2.5 的 one-shot 示例中到处是 Python 字典字面量 `{"Mild": 0.0, "Moderate": 0.4, ...}`——花括号会被 `str.format()` 当作模板变量。`str.replace()` 只替换唯一的 `{scenario_context}` 占位符，零歧义。

**规范偏差：** stage4 描述了 `PromptTemplate` 类和 `assemble_prompt(scenario_context: dict) → list[dict]`（接收 dict，返回消息数组）。实际更简单：接收 `str`，返回 `str`。消息格式化需调用方完成。

### 6.2 沙箱执行模型

M3 的核心安全机制——LLM 脚本在受限环境中执行。

#### `_SAFE_BUILTINS` — 白名单

📍 [sandbox.py:55-110](phase_2/orchestration/sandbox.py#L55-L110)

约 50 个安全的 Python 内置对象（构造器、类型转换、集合操作、常用异常类），**刻意排除**：`__import__`、`eval`、`exec`、`open`、`compile`。

#### `_build_sandbox_namespace()` — 构建执行环境

📍 [sandbox.py:117-175](phase_2/orchestration/sandbox.py#L117-L175)

1. 以 `_SAFE_BUILTINS` 为基础构建 `namespace`
2. 预注入 `FactTableSimulator` 类 📍 [sandbox.py:139-140](phase_2/orchestration/sandbox.py#L139-L140)
3. 安装 `_restricted_import()` 📍 [sandbox.py:144-161](phase_2/orchestration/sandbox.py#L144-L161)——仅允许 `chartagent.synth`、`phase_2.sdk.simulator` 等 SDK 路径

#### `_SandboxThread` — 守护线程执行

📍 [sandbox.py:180-223](phase_2/orchestration/sandbox.py#L180-L223)

```python
# 📍 sandbox.py:200-223 — run() 方法
def run(self) -> None:
    try:
        compiled = compile(self.source_code, "<llm_script>", "exec")
        exec(compiled, self.namespace)                    # 执行脚本
        build_fn = self.namespace.get("build_fact_table")  # 取出函数
        self.result = build_fn()                           # 调用
    except Exception as exc:
        self.exception = exc                               # 通杀捕获
        self.traceback_str = tb_module.format_exc()
```

使用守护线程（daemon=True）而非 `signal.alarm`，允许超时保护在非主线程环境中工作。

#### `execute_in_sandbox()` — 完整执行+验证

📍 [sandbox.py:225-430](phase_2/orchestration/sandbox.py#L225-L430)

1. 输入验证（空代码、非法 timeout）
2. 构建或使用提供的 namespace
3. 启动 `_SandboxThread` + `join(timeout=30s)`
4. 超时检测——线程仍活着 → `TimeoutError`
5. 返回值验证 📍 sandbox.py:350-430——检查 `build_fact_table()` 返回值为 `(DataFrame, dict)` 二元组：None、非 tuple、长度非 2、元素类型不匹配，每种情况格式化为结构化错误
6. 包装为 `SandboxResult`

### 6.3 反馈格式化

📍 [sandbox.py:445-529](phase_2/orchestration/sandbox.py#L445-L529) — `format_error_feedback()`

组装**四段式反馈**：

```
=== ORIGINAL CODE ===
{失败的脚本全文}

=== ERROR ===
Exception: CyclicDependencyError: Measure 'cost' → 'satisfaction' → 'cost' forms a cycle.

=== TRACEBACK ===
{完整 traceback}

=== INSTRUCTION ===
The script above raised an error during sandbox execution.
Adjust parameters to resolve the error.
Return only the corrected Python script.
```

`_FIX_INSTRUCTION` 📍 [sandbox.py:438-442](phase_2/orchestration/sandbox.py#L438-L442) 匹配 §2.7 step 5 措辞。清晰的节标题让 LLM 能无歧义地解析每个组件。

### 6.4 🔄 Retry Protocol——Loop A 核心

📍 [sandbox.py:536-704](phase_2/orchestration/sandbox.py#L536-L704) — `run_retry_loop()`

```python
# 📍 sandbox.py:623-704 — 核心循环（简化伪代码）
current_code = initial_code
history: list[SandboxResult] = []

for attempt in range(1, max_retries + 1):    # L629
    sandbox_ns = ns_factory()                 # L637 — 全新 namespace
    result = execute_in_sandbox(current_code, timeout, sandbox_ns)  # L638
    history.append(result)                    # L643

    if result.success:                        # L647 — 成功，提前退出
        return RetryLoopResult(success=True, dataframe, metadata, attempts)

    if attempt < max_retries:                 # L663 — 非最后一次
        feedback = format_error_feedback(     # L665
            current_code, result.exception, result.traceback_str)
        current_code = llm_generate_fn(       # L682
            system_prompt, feedback)

return RetryLoopResult(success=False, ...)    # L700 — 预算耗尽
```

关键参数：
- `DEFAULT_MAX_RETRIES = 3` 📍 [sandbox.py:48](phase_2/orchestration/sandbox.py#L48)
- `DEFAULT_TIMEOUT_SECONDS = 30` 📍 [sandbox.py:47](phase_2/orchestration/sandbox.py#L47)

💡 **为什么最后一次失败不调 LLM？** `if attempt < max_retries`（📍 [sandbox.py:663](phase_2/orchestration/sandbox.py#L663)）保护——最后一次 sandbox 失败后没有下一次迭代来使用新代码，调 LLM 只浪费 token。

**每次迭代全新 namespace**（📍 [sandbox.py:637](phase_2/orchestration/sandbox.py#L637)）——前次失败的部分 SDK 状态不污染下次尝试。

### 6.5 对话累积——重大规范偏差

这是 M3 中最重要的规范偏差：

| 维度 | §2.7 规范 | 实际代码 |
|---|---|---|
| 对话模型 | Append-only `list[dict]`，消息逐次增长 | 无状态，每次 LLM 调用只看当前失败 |
| LLM 可见历史 | 所有先前失败尝试 + traceback | 仅最近一次 |
| 最大消息数 | 8 条（1 system + 3×2 user/assistant + 1 final） | 始终 2 条（system + feedback） |
| 多轮学习能力 | LLM 可避免重复先前错误 | LLM 可能重蹈覆辙 |

**影响：** 在 attempt 3 时，LLM 看不到 attempt 1 和 attempt 2 的失败代码和 traceback，可能在 attempt 3 重犯 attempt 1 的错误。

`retry_loop.py` 的 `orchestrate()` 📍 [retry_loop.py:20-50](phase_2/orchestration/retry_loop.py#L20-L50) 描述了完整对话管理，但该函数是**纯 stub**——仅 log warning 并返回 `SkipResult`。

### 6.6 代码验证辅助

📍 [code_validator.py](phase_2/orchestration/code_validator.py) — 两个公共函数

#### `extract_clean_code()` — markdown 围栏剥离

📍 [code_validator.py:76-152](phase_2/orchestration/code_validator.py#L76-L152)

三级优先策略提取净 Python 代码：完整围栏块（` ```python...``` `）→ 首尾围栏 → 裸代码。使用正则 `_FENCED_BLOCK_RE`/`_LEADING_FENCE_RE`/`_TRAILING_FENCE_RE` 📍 [code_validator.py:62-73](phase_2/orchestration/code_validator.py#L62-L73)。

#### `validate_generated_code()` — AST 三重检查

📍 [code_validator.py:195-309](phase_2/orchestration/code_validator.py#L195-L309)

1. **语法检查**——`ast.parse()` 成功？
2. **函数定义**——`_BuildFactTableVisitor` 📍 [code_validator.py:171-193](phase_2/orchestration/code_validator.py#L171-L193) 检测 `def build_fact_table(...)`
3. **generate 调用**——`_GenerateCallVisitor` 📍 [code_validator.py:159-169](phase_2/orchestration/code_validator.py#L159-L169) 检测 `.generate()` 方法调用

返回 `CodeValidationResult`（frozen dataclass）📍 [code_validator.py:36-53](phase_2/orchestration/code_validator.py#L36-L53)：`is_valid`, `has_build_fact_table`, `has_generate_call`, `errors`。

### 6.7 关键约束

1. **Prompt 不可变性：** `SYSTEM_PROMPT_TEMPLATE` 是 `Final[str]`，运行时不可修改
2. **每次执行全新 namespace：** 前次失败的 SDK 状态不污染下次尝试
3. **受限 builtins：** 屏蔽 `__import__`/`eval`/`exec`/`open`，LLM 脚本只能使用预注入的 `FactTableSimulator`
4. **超时保护：** 守护线程 + `join(timeout=30s)` 防止无限循环脚本挂起 pipeline
5. **重试预算固定：** `max_retries=3`，不根据错误类型动态调整
6. **返回值验证：** `build_fact_table()` 必须返回 `(DataFrame, dict)` 二元组

### 6.8 🚧 TODO 地图

| 项目 | 优先级 | 代码状态 | 说明 |
|---|---|---|---|
| Sandbox 执行语义 | P1 | **大部分已解决 ✅** | `exec()` in-process + 守护线程 + timeout + 全新 namespace |
| 非 SDK 异常处理 | P1 | **已解决 ✅** | `except Exception` 通杀捕获 + 统一格式化 traceback |
| `build_fact_table` 签名强制 | P1 | 部分——函数名检查有，`seed` 参数不检查 | AST 级 + namespace 级 |
| 多错误同时发生 | P2 | 未处理——接受 one-at-a-time | Python 每次只抛一个异常 |
| 上下文窗口耗尽策略 | P2 | 未实现——但因不累积对话，问题被"绕过" | 未来实现累积对话后需处理 |
| Loop A 终端 ↔ 上层 orchestrator | P2 | Stub——`orchestrate()` 仅返回 `SkipResult` | `SkipResult` vs `RetryLoopResult` 未统一 |

### 6.9 本章小结

M3 是系统的**最外层壳**——连接人类意图（场景描述）和机器执行（SDK 脚本）的桥梁。已完成的核心组件：

- **Prompt 工程**：完整的 §2.5 模板 + HC1-HC9 硬约束 + one-shot 示例 + `str.replace()` 渲染
- **安全沙箱**：受限 builtins + 预注入 SDK + import 门控 + 超时保护
- **重试协议**：`run_retry_loop()` 完整实现 §2.7 六步循环
- **错误反馈**：四段式格式化，LLM 可直接解析
- **代码验证**：围栏剥离 + AST 三重检查

**关键缺口：** 对话累积未实现（LLM 看不到先前失败历史）+ `orchestrate()` 高层入口是 stub + `SkipResult` / `RetryLoopResult` 两种返回类型未统一。

---

# 第四部分：跨模块数据流 + 速查表

这一部分切换到**流水线执行顺序**视角，横向追踪数据如何从 Phase 1 流经 M3→M1→M2∥M4→M5 到达 Phase 3，重点讲两条反馈回路的嵌套关系和管道断裂点。最后附上两份速查表。

---

## 第 7 章：当系统跑起来——跨模块数据流

> 前六章是"如果你从零搭建这个系统"的视角。本章换一个问题："当系统跑起来，一条场景描述是怎么变成一张验证过的 DataFrame 的？"

### 7.1 正向流水线——9 条传递

下图是端到端的数据流。每条传递标注发送方接口→接收方接口、数据类型和实现状态。

```
Phase 1 ─①─► M3 ─②─► M1 ─③─► M3        (Loop A 异常反馈)
                             ├─④─► M2 ─┬─⑥─► M5 ─⑨─► Phase 3
                             │          │       ▲
                             └─⑤─► M4 ─┘─⑦─► M5
                                              │
                                              ⑧ Loop B → M2
```

| # | 传递 | 数据类型 | 机制 | 状态 |
|---|---|---|---|---|
| ① | Phase 1 → M3 | `str`（场景描述） | `render_system_prompt()` 📍 [prompt.py:207](phase_2/orchestration/prompt.py#L207) | ✅ |
| ② | M3 → M1 | `str`（Python 源码）→ SDK 方法调用 | `exec()` 间接调用 📍 [sandbox.py:206](phase_2/orchestration/sandbox.py#L206) | ✅ |
| ③ | M1 → M3 | `SimulatorError` 子类 | 异常冒泡 📍 [sandbox.py:219](phase_2/orchestration/sandbox.py#L219) | ✅ |
| ④ | M1 → M2 | 8 个解包参数（共享对象引用） | `generate()` → `run_pipeline()` 📍 [simulator.py:131](phase_2/sdk/simulator.py#L131) → 📍 [generator.py:27](phase_2/engine/generator.py#L27) | ✅ |
| ⑤ | M1 → M4 | 7 个参数（M2 内部调用） | `run_pipeline()` return path 📍 [generator.py:118](phase_2/engine/generator.py#L118) → 📍 [builder.py:23](phase_2/metadata/builder.py#L23) | ⚠️ `orthogonal_pairs=[]` |
| ⑥ | M2 → M5 | `pd.DataFrame` | **管道缺失** — 无自动传递 | ⚠️ |
| ⑦ | M4 → M5 | `dict`（7-key metadata） | **管道缺失** — 无自动传递 | ⚠️ |
| ⑧ | M5 → M2 | 调整后参数 (overrides) | **循环框架缺失** — 策略就绪无消费者 | ⚠️ |
| ⑨ | M5 → Phase 3 | `(DataFrame, metadata, ValidationReport)` | **管道缺失** | ⚠️ |

### 7.2 关键发现：M4 由 M2 内部调用

规范设计中 M1 将声明存储同时分发给 M2 和 M4，两者可并行。但代码实现中：

- M4 的 `build_schema_metadata()` 被 M2 的 `run_pipeline()` 在 **return path 上调用** 📍 [generator.py:102-126](phase_2/engine/generator.py#L102-L126)
- M1 的 `_build_schema_metadata()` 📍 [simulator.py:143-152](phase_2/sdk/simulator.py#L143-L152) 正确传递了 `orthogonal_pairs`，但 `generate()` **从未调用它**——是死代码

结果：M4 事实上在 M2 内部**串行执行**。虽然设计允许并行（M4 不需要 DataFrame），但当前代码路径不支持。

### 7.3 `orthogonal_pairs` 数据丢失

这是正向流水线中**影响最大的管道断裂**。

`run_pipeline()` 的签名 📍 [generator.py:27-37](phase_2/engine/generator.py#L27-L37) 不包含 `orthogonal_pairs` 参数（正交对不影响行生成逻辑），但 M4 在 M2 内部被调用时需要它。代码硬编码 `orthogonal_pairs=[]` 📍 [generator.py:120](phase_2/engine/generator.py#L120)。

**影响链：**

```
run_pipeline() 不接收 orthogonal_pairs
    → build_schema_metadata(orthogonal_pairs=[])
        → schema_metadata["orthogonal_groups"] == []
            → M5 check_orthogonal_independence() 遍历为空 → 跳过全部 χ² 检验
            → Phase 3 无法得知哪些组被声明为正交
```

**修复：** `run_pipeline()` 加一个参数，`generate()` 传递 `self._orthogonal_pairs`。修复复杂度低。

### 7.4 M2→M5 管道断裂

`run_pipeline()` 返回 `(df, metadata)` 📍 [generator.py:133](phase_2/engine/generator.py#L133)，透传回 `generate()` → `_SandboxThread.result` → `SandboxResult` → `RetryLoopResult`。但**到此为止**——没有代码将 DataFrame + metadata 自动传给 `SchemaAwareValidator`。

```
run_pipeline() → (df, metadata)           📍 generator.py:133
  → generate() 透传                        📍 simulator.py:141
  → _SandboxThread.result                  📍 sandbox.py:217
  → SandboxResult                          📍 sandbox.py:426-430
  → RetryLoopResult                        📍 sandbox.py:651-657
  ⛔ 到此为止。无代码传给 SchemaAwareValidator。
```

`generate_with_validation()` 应承担此桥接角色（stage4 设计签名在 `autofix.py`），但**尚未实现**。

`pipeline.py` 📍 [pipeline.py:85-139](phase_2/pipeline.py#L85-L139) 的 `_run_loop_b()` 包含一个骨架循环，但 auto-fix 集成处标注 `# TODO` 后直接 `break`——无法实际重试。

### 7.5 M2 内部数据形态切换

虽非模块间传递，但理解 M2→M5 输出的关键：

```
Stage α   dict[str, np.ndarray]    (列式 numpy 数组，高效批量采样)
Stage β   dict[str, np.ndarray]    (同上，当前 stub 不修改)
  ── τ_post 切换点 ──
Stage γ   pd.DataFrame             (需要 df.eval() 做子集操作)
Stage δ   pd.DataFrame             (in-place NaN/dirty 注入)
```

τ_post 📍 [postprocess.py:19-82](phase_2/engine/postprocess.py#L19-L82) 在 β 和 γ 之间将 `dict[str, ndarray]` 转为 `pd.DataFrame`。规范数学表达 `M = τ_post ∘ δ ∘ γ ∘ β ∘ α(seed)` 中 τ_post 在最外层，但代码将它提前——功能等价，数据结构在中间切换。

### 7.6 🔄 Loop A 完整路径追踪

Loop A 是**外层循环**——M1 声明时验证失败时触发，LLM 重新生成脚本修正错误。

```
LLM 脚本 ─exec()─► sim.add_category(...)
                      └─ M1 验证失败 → raise SimulatorError 子类
                                ↓
        _SandboxThread.run() except Exception    📍 sandbox.py:219
        self.exception = exc; self.traceback_str = format_exc()
                                ↓
        execute_in_sandbox() → SandboxResult(success=False)  📍 sandbox.py:344
                                ↓
        run_retry_loop() 检测 result.success == False   📍 sandbox.py:647
                                ↓
        format_error_feedback(code, exc, tb)              📍 sandbox.py:665
        → 四段式反馈: CODE + ERROR + TRACEBACK + INSTRUCTION
                                ↓
        current_code = llm_generate_fn(system_prompt, feedback)  📍 sandbox.py:682
                                ↓
        下一迭代：sandbox_ns = ns_factory()    ← 全新 namespace  📍 sandbox.py:637
```

**9 种可抛出的 SDK 异常**（全部继承 `SimulatorError`，见第 1 章 §1.6），每种携带精确的结构化字段和 LLM 可理解的错误消息。

**已实现 vs 缺失：**

| 组件 | 状态 |
|---|---|
| M1 异常抛出（全部 9 种） | ✅ |
| 沙箱捕获 + SandboxResult 包装 | ✅ |
| 四段式反馈格式化 | ✅ |
| LLM 调用 callable 接口 | ✅ |
| Namespace 状态重置 | ✅ |
| 重试循环框架 | ✅ |
| **对话累积（append-only 多轮）** | **⚠️ 未实现**——每次只传最近一次失败 |
| **`orchestrate()` 高层入口** | **⚠️ stub** |
| **`SkipResult` vs `RetryLoopResult` 统一** | **⚠️ 两种返回类型共存** |

### 7.7 🔄 Loop B 完整路径追踪

Loop B 是**内层循环**——生成的 DataFrame 通过 M5 验证失败时，通过参数调整 + 新 seed 重新执行 M2。**无 LLM 参与。**

```
M5 validate(df, patterns) → ValidationReport
    ↓ report.all_passed == False
match_strategy(check.name, AUTO_FIX)   ← ✅ 已实现  📍 autofix.py:25
    ↓ 返回策略函数
strategy_fn(check, params/pattern/df)  ← ✅ 三个策略  📍 autofix.py:46-158
    ↓ 返回新参数
ParameterOverrides 聚合                ← ❌ 未实现
    ↓
run_pipeline(seed=base_seed+attempt,   ← ✅ 签名就绪  📍 generator.py:36
             overrides=overrides)
    └→ generate_measures(overrides=...)← ✅ 签名就绪  📍 measures.py:24
    ↓
M5 再次 validate()                     ← ✅ 可调用
    ↓
重复最多 3 次
```

**关键缺失环节：** `generate_with_validation()` 循环框架、`AUTO_FIX` 默认分发表实例化、`ParameterOverrides` 数据结构、seed 偏移逻辑、策略输出→overrides 格式适配。

### 7.8 嵌套关系

```
┌─── Loop A (外层, max 3, 含 LLM 调用) ──────────────────────────────────┐
│                                                                          │
│  M3 渲染 prompt → LLM 生成脚本 → sandbox exec → M1 声明时验证           │
│    成功 ↓                                   失败 → 异常 → 反馈 → LLM    │
│                                                                          │
│  M1.generate() → M2 run_pipeline() → (df, metadata)                     │
│                                                                          │
│  ┌─── Loop B (内层, max 3, 无 LLM) ──────────────────────────┐         │
│  │                                                              │         │
│  │  M5 validate(df, patterns) → ValidationReport               │         │
│  │    全通过 → 返回 (df, metadata, report)                      │         │
│  │    失败 → match_strategy → 策略调参                          │         │
│  │         → run_pipeline(seed+attempt, overrides) → M5 再验证  │         │
│  │                                                              │         │
│  └──────────────────────────────────────────────────────────────┘         │
│                                                                          │
│  Loop B 产出 (df, metadata, report) → Phase 3                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**关键约束：**

1. Loop B **仅在 Loop A 成功后**执行。M1 验证失败走 Loop A 异常路径，不进入 M2/M5。
2. Loop B **不修改声明**（store 只读）。M4 metadata 不需要在 Loop B 中重建——声明未变，元数据不变。
3. **当前实际行为：** 由于 Loop B 循环框架未实现且度量生成为 stub，`generate()` 总是"成功"返回仅含 skeleton 列的 DataFrame。整个 Loop B 路径事实上不可触发。

### 7.9 NEEDS_CLAR 跨模块阻塞图

三个 P0 阻塞项在 M2 的 `measures.py` 交汇：

```
P0-1 (Metadata Enrichment)         P0-2 (Formula Evaluator)          P0-3 (Auto-fix Semantics)
  │                                   │                                  │
  ├─ builder.py ✅ 已解决             ├─ columns.py ✅ 符号提取          ├─ autofix.py ✅ 策略函数
  │                                   ├─ measures.py ❌ _eval_structural ├─ autofix.py ❌ 循环框架
  ├─ structural.py ❌ marginal/finite ├─ measures.py ❌ _sample_stoch.   ├─ measures.py ❌ overrides消费
  ├─ statistical.py ❌ 全部 stub      ├─ statistical.py ❌ residuals     │
  └─ validator.py ⚠️ 缺 L2 调用       └─ (需共享 formula evaluator)      └─ (需 ParameterOverrides)
                                            │
                  ┌────────────────────────┘
                  ▼
          P0-2 和 P0-3 在 measures.py 交汇：
          _sample_stochastic() 和 _eval_structural() 同时需要：
          (a) 公式/分布求值能力 ← P0-2
          (b) overrides 叠加逻辑 ← P0-3
```

**解除优先级：**

1. **P0-1 已解除**（M4 enrichment 已实现）→ 只需补齐 M5 函数
2. **P0-2 优先**——实现公式求值器，解锁 Stage β 全部度量生成
3. **P0-3 其次**——需 P0-2 完成后才有可测试的 Loop B 端到端路径
4. **P1-1/P1-2 可并行**——独立于 P0 阻塞链

### 7.10 数据生命周期总结

| 数据对象 | 创建 | 消费 | 可变性 | 代码位置 | 状态 |
|---|---|---|---|---|---|
| `scenario_context` (str) | Phase 1 | M3 | Read-only | 📍 prompt.py:207 接收 | ✅ |
| `system_prompt` (str) | M3 | M3 retry loop | Frozen | 📍 prompt.py:252 渲染 | ✅ |
| LLM 脚本 (str) | M3 (LLM) | M1 (via exec) | Per-attempt | 📍 sandbox.py:206 exec | ✅ |
| `FactTableSimulator` | M1 | M1 | Accumulating→frozen | 📍 simulator.py:32 | ✅ |
| `columns` (OrderedDict) | M1 | M2, M4 | Frozen | 📍 simulator.py:132 | ✅ |
| `groups` (dict) | M1 | M2, M4 | Frozen | 📍 simulator.py:133 | ✅ |
| `group_dependencies` (list) | M1 | M2, M4 | Frozen | 📍 simulator.py:134 | ✅ |
| `measure_dag` (dict) | M1 | M2 | Frozen | 📍 simulator.py:135 | ✅ |
| `orthogonal_pairs` (list) | M1 | M4 | Frozen | **丢失**——generator.py:120 硬编码 `[]` | ⚠️ |
| `patterns` (list) | M1 | M2 γ, M4, M5 L3 | Frozen | 📍 simulator.py:138 | ✅ |
| `realism_config` (dict) | M1 | M2 δ | Frozen | 📍 simulator.py:139 | ⚠️ 部分 |
| `topo_order` (list) | M2 pre-flight | M2 α/β/meta | Computed once | 📍 generator.py:76 | ✅ |
| `rng` (Generator) | M2 | M2 α/β/γ/δ | Progressive | 📍 generator.py:70 | ✅ |
| `rows` (dict→ndarray) | M2 α | M2 β, τ_post | In-place per stage | 📍 skeleton.py:31 | ✅/⛔ |
| `df` (DataFrame) | M2 τ_post | M2 γ/δ, M5, Phase 3 | In-place by γ/δ | 📍 postprocess.py:19 | ✅ |
| `schema_metadata` (dict) | M4 via M2 | M5, Phase 3 | Defensively copied | 📍 builder.py:23 | ✅ (⚠️ orth空) |
| `ValidationReport` | M5 | Loop B, Phase 3 | Additive | 📍 validator.py:62 | ✅ |
| `Check` | M5 L1/L3 | report, Loop B | Immutable | structural.py / pattern_checks.py | ✅ 部分 |
| `overrides` (dict) | Loop B 策略 | M2 re-run | Per-retry | 📍 autofix.py → generator.py:36 | ⚠️ 签名就绪 |
| `SandboxResult` | M3 | M3 retry loop | Per-attempt | 📍 sandbox.py:344 | ✅ |
| `RetryLoopResult` | M3 | Pipeline | Final | 📍 sandbox.py:651 | ✅ |
| `SkipResult` | M3 | Pipeline | Terminal sentinel | 📍 exceptions.py:371 | ⚠️ 未统一 |
| typed Exception | M1 | M3 feedback | Per-attempt | 📍 exceptions.py:52-336 | ✅ |

### 7.11 管道断裂点汇总

| # | 断裂点 | 影响 | 修复复杂度 |
|---|---|---|---|
| 1 | `orthogonal_pairs=[]` 硬编码 📍 generator.py:120 | metadata 丢失正交信息 → M5 χ² 跳过 | **低**——`run_pipeline()` 加参数 |
| 2 | M2→M5 无自动管道 | 生成后不自动验证 | **中**——实现 `generate_with_validation()` |
| 3 | Loop B 循环框架缺失 | 验证失败无法自动修复 | **中**——循环+分发表+overrides |
| 4 | 对话累积缺失 | LLM 可能重复先前错误 | **低**——`run_retry_loop` 维护 messages list |
| 5 | Stage β 度量生成 stub | 无度量列 → L2/L3 不可测 | **高**——P0-2 公式求值器 |
| 6 | `SkipResult` vs `RetryLoopResult` | 两种终端失败表示共存 | **低**——统一返回类型 |

### 7.12 已实现的完整路径

尽管存在多个断裂点，以下端到端路径**当前可运行**：

```
scenario_context (str)
  → render_system_prompt()           ✅
  → run_retry_loop(initial_code, llm_fn, prompt)  ✅
    → execute_in_sandbox(code)       ✅
      → exec() → FactTableSimulator.add_*() → M1 验证  ✅
      → sim.generate() → run_pipeline()  ✅
        → build_skeleton()           ✅  (仅非度量列)
        → generate_measures()        ⛔  (stub, 原样返回)
        → to_dataframe()             ✅
        → inject_patterns()          ✅  (2/6 类型, 列不存在时 warn+skip)
        → inject_realism()           ⚠️  (missing ✅ dirty ✅ censoring ❌)
        → build_schema_metadata()    ✅  (orthogonal 为空)
      → SandboxResult(success=True, df, metadata)  ✅
    → RetryLoopResult(success=True)  ✅
```

产出一个**仅含 skeleton 列**（分类+时间+派生）的 DataFrame + enriched metadata dict。Loop A 异常反馈路径也完整可用。

---

## 附录 A：代码速查表

> 模块 → 核心类/函数 → 文件位置 → 对应章节号 → 实现状态

### 共享基础设施（第 1 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `DimensionGroup` | phase_2/types.py | 27-80 | ✅ |
| `OrthogonalPair` | phase_2/types.py | 87-171 | ✅ |
| `GroupDependency` | phase_2/types.py | 178-225 | ✅ |
| `Check` | phase_2/types.py | 232-250 | ✅ |
| `ValidationReport` | phase_2/types.py | 253-306 | ✅ |
| `PatternSpec` | phase_2/types.py | 313-337 | ✅ |
| `RealismConfig` | phase_2/types.py | 340-361 | ✅ |
| `DeclarationStore` | phase_2/types.py | 364-409 | ✅ (未被 simulator 使用) |
| `SandboxResult` | phase_2/types.py | 412-430 | ✅ |
| `RetryLoopResult` | phase_2/types.py | 432-449 | ✅ |
| `SimulatorError` | phase_2/exceptions.py | 39-47 | ✅ |
| `CyclicDependencyError` | phase_2/exceptions.py | 52-74 | ✅ |
| `UndefinedEffectError` | phase_2/exceptions.py | 77-100 | ✅ |
| `NonRootDependencyError` | phase_2/exceptions.py | 103-126 | ✅ |
| `InvalidParameterError` | phase_2/exceptions.py | 134-159 | ✅ |
| `DuplicateColumnError` | phase_2/exceptions.py | 162-182 | ✅ |
| `EmptyValuesError` | phase_2/exceptions.py | 185-203 | ✅ |
| `WeightLengthMismatchError` | phase_2/exceptions.py | 206-228 | ✅ |
| `DegenerateDistributionError` | phase_2/exceptions.py | 231-251 | ✅ |
| `ParentNotFoundError` | phase_2/exceptions.py | 254-276 | ✅ |
| `DuplicateGroupRootError` | phase_2/exceptions.py | 279-304 | ✅ |
| `PatternInjectionError` | phase_2/exceptions.py | 315-336 | ✅ |
| `UndefinedPredictorError` | phase_2/exceptions.py | 341-363 | ✅ |
| `SkipResult` | phase_2/exceptions.py | 371-388 | ✅ |

### M1 SDK Surface（第 2 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `FactTableSimulator.__init__` | phase_2/sdk/simulator.py | 32-51 | ✅ |
| `FactTableSimulator.generate` | phase_2/sdk/simulator.py | 130-141 | ✅ |
| `add_category()` | phase_2/sdk/columns.py | 38-121 | ✅ |
| `add_temporal()` | phase_2/sdk/columns.py | 124-211 | ✅ |
| `add_measure()` | phase_2/sdk/columns.py | 214-250 | ✅ |
| `add_measure_structural()` | phase_2/sdk/columns.py | 253-321 | ✅ |
| `declare_orthogonal()` | phase_2/sdk/relationships.py | 39-92 | ✅ |
| `add_group_dependency()` | phase_2/sdk/relationships.py | 95-196 | ✅ |
| `inject_pattern()` | phase_2/sdk/relationships.py | 199-257 | ✅ |
| `set_realism()` | phase_2/sdk/relationships.py | 260-299 | ✅ |
| `validate_column_name()` | phase_2/sdk/validation.py | 57-71 | ✅ |
| `validate_parent()` | phase_2/sdk/validation.py | 78-105 | ✅ |
| `validate_and_normalize_flat_weights()` | phase_2/sdk/validation.py | 112-163 | ✅ |
| `validate_and_normalize_dict_weights()` | phase_2/sdk/validation.py | 166-223 | ✅ |
| `validate_family()` | phase_2/sdk/validation.py | 274-287 | ✅ |
| `validate_param_model()` | phase_2/sdk/validation.py | 294-399 | ✅ |
| `validate_structural_effects()` | phase_2/sdk/validation.py | 467-547 | ✅ |
| `extract_formula_symbols()` | phase_2/sdk/validation.py | 49-50 (IDENTIFIER_RE) | ✅ |
| `detect_cycle_in_adjacency()` | phase_2/sdk/dag.py | 33-102 | ✅ |
| `topological_sort()` | phase_2/sdk/dag.py | 105-155 | ✅ |
| `build_full_dag()` | phase_2/sdk/dag.py | 197-293 | ✅ |
| `check_measure_dag_acyclic()` | phase_2/sdk/dag.py | 379-410 | ✅ |
| `check_root_dag_acyclic()` | phase_2/sdk/dag.py | 413-451 | ✅ |
| `register_categorical_column()` | phase_2/sdk/groups.py | 20-55 | ✅ |
| `register_temporal_group()` | phase_2/sdk/groups.py | 57-81 | ✅ |
| `is_group_root()` | phase_2/sdk/groups.py | 98-122 | ✅ |

### M4 Schema Metadata（第 3 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `build_schema_metadata()` | phase_2/metadata/builder.py | 23-111 | ✅ |
| `_build_columns_metadata()` | phase_2/metadata/builder.py | 114-175 | ✅ |
| `_deep_copy_param_model()` | phase_2/metadata/builder.py | 178-191 | ✅ |
| `_assert_metadata_consistency()` | phase_2/metadata/builder.py | 194-251 | ⚠️ warning 而非 raise |

### M2 Generation Engine（第 4 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `run_pipeline()` | phase_2/engine/generator.py | 27-133 | ✅ (β stub) |
| `build_skeleton()` | phase_2/engine/skeleton.py | 31-102 | ✅ |
| `sample_independent_root()` | phase_2/engine/skeleton.py | 109-131 | ✅ |
| `sample_dependent_root()` | phase_2/engine/skeleton.py | 134-179 | ✅ |
| `sample_child_category()` | phase_2/engine/skeleton.py | 182-230 | ✅ |
| `sample_temporal_root()` | phase_2/engine/skeleton.py | 237-289 | ✅ |
| `derive_temporal_child()` | phase_2/engine/skeleton.py | 343-378 | ✅ |
| `generate_measures()` | phase_2/engine/measures.py | 19-63 | ⛔ stub |
| `_sample_stochastic()` | phase_2/engine/measures.py | 66-81 | ⛔ NotImplementedError |
| `_eval_structural()` | phase_2/engine/measures.py | 84-99 | ⛔ NotImplementedError |
| `to_dataframe()` | phase_2/engine/postprocess.py | 19-82 | ✅ |
| `inject_patterns()` | phase_2/engine/patterns.py | 29-82 | ✅ 2/6 类型 |
| `inject_outlier_entity()` | phase_2/engine/patterns.py | 85-153 | ✅ |
| `inject_trend_break()` | phase_2/engine/patterns.py | 156-237 | ✅ |
| `inject_realism()` | phase_2/engine/realism.py | 25-64 | ⚠️ censoring stub |
| `inject_missing_values()` | phase_2/engine/realism.py | 67-99 | ✅ |
| `inject_dirty_values()` | phase_2/engine/realism.py | 102-163 | ✅ |
| `perturb_string()` | phase_2/engine/realism.py | 166-204 | ✅ |

### M5 Validation Engine（第 5 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `SchemaAwareValidator.__init__` | phase_2/validation/validator.py | 40-46 | ✅ |
| `SchemaAwareValidator.validate` | phase_2/validation/validator.py | 48-83 | ✅ (L2 跳过) |
| `check_row_count()` | phase_2/validation/structural.py | 22-48 | ✅ |
| `check_categorical_cardinality()` | phase_2/validation/structural.py | 51-110 | ✅ |
| `check_orthogonal_independence()` | phase_2/validation/structural.py | 113-177 | ✅ (orth 为空→跳过) |
| `check_measure_dag_acyclic()` | phase_2/validation/structural.py | 180-209 | ✅ |
| `check_marginal_weights()` | — | — | ❌ 未编写 |
| `check_measure_finiteness()` | — | — | ❌ 未编写 |
| `check_stochastic_ks()` | phase_2/validation/statistical.py | 55-69 | ⛔ stub |
| `check_structural_residuals()` | phase_2/validation/statistical.py | 72-86 | ⛔ stub |
| `check_group_dependency_transitions()` | phase_2/validation/statistical.py | 89-102 | ⛔ stub |
| `max_conditional_deviation()` | phase_2/validation/statistical.py | 21-52 | ✅ 辅助函数 |
| `check_outlier_entity()` | phase_2/validation/pattern_checks.py | 23-69 | ✅ |
| `check_trend_break()` | phase_2/validation/pattern_checks.py | 84-155 | ✅ |
| `_find_temporal_column()` | phase_2/validation/pattern_checks.py | 72-81 | ✅ |
| `check_ranking_reversal()` | — | — | ❌ 未编写 |
| `match_strategy()` | phase_2/validation/autofix.py | 25-43 | ✅ |
| `widen_variance()` | phase_2/validation/autofix.py | 46-82 | ✅ |
| `amplify_magnitude()` | phase_2/validation/autofix.py | 85-123 | ✅ |
| `reshuffle_pair()` | phase_2/validation/autofix.py | 126-158 | ✅ |
| `generate_with_validation()` | — | — | ❌ 未编写 |

### M3 LLM Orchestration（第 6 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `SYSTEM_PROMPT_TEMPLATE` | phase_2/orchestration/prompt.py | 35-200 | ✅ |
| `render_system_prompt()` | phase_2/orchestration/prompt.py | 207-262 | ✅ |
| `_SAFE_BUILTINS` | phase_2/orchestration/sandbox.py | 55-110 | ✅ |
| `_build_sandbox_namespace()` | phase_2/orchestration/sandbox.py | 117-175 | ✅ |
| `_SandboxThread` | phase_2/orchestration/sandbox.py | 180-223 | ✅ |
| `execute_in_sandbox()` | phase_2/orchestration/sandbox.py | 225-430 | ✅ |
| `format_error_feedback()` | phase_2/orchestration/sandbox.py | 445-529 | ✅ |
| `run_retry_loop()` | phase_2/orchestration/sandbox.py | 536-704 | ✅ (对话累积缺失) |
| `extract_clean_code()` | phase_2/orchestration/code_validator.py | 76-152 | ✅ |
| `validate_generated_code()` | phase_2/orchestration/code_validator.py | 195-309 | ✅ |
| `CodeValidationResult` | phase_2/orchestration/code_validator.py | 36-53 | ✅ |
| `orchestrate()` | phase_2/orchestration/retry_loop.py | 20-50 | ⚠️ stub |

### Pipeline（第 7 章）

| 类/函数 | 文件 | 行号 | 状态 |
|---|---|---|---|
| `run_phase2()` | phase_2/pipeline.py | 22-56 | ⚠️ 骨架 |
| `_run_loop_a()` | phase_2/pipeline.py | 59-82 | ⚠️ 委托 stub |
| `_run_loop_b()` | phase_2/pipeline.py | 85-139 | ⚠️ auto-fix TODO |

---

## 附录 B：TODO 速查表

> 阻塞项 → 优先级 → 源头模块 → 影响模块 → stage3 建议方案

### P0 阻塞项

| # | 阻塞项 | 源头 | 影响 | Stage3 建议 | 当前状态 |
|---|---|---|---|---|---|
| P0-1 | Metadata Enrichment | M4 builder.py | M5 全部 | 将 §2.6 示例视为示意性，enrichment 所有 M5 字段 | **已解决 ✅** |
| P0-2 | Formula Evaluation | M2 measures.py | M2 β, M5 L2 | 受限 AST walker：仅 `+`/`-`/`*`/`/`/`**` + 数字 + 变量名 | ❌ NotImplementedError |
| P0-3 | Auto-fix Mutation | M5 autofix.py | M2 重试 | 策略变异 `ParameterOverrides` dict（非 frozen store） | ❌ 循环缺失 |

### P1 阻塞项

| # | 阻塞项 | 源头 | 影响 | Stage3 建议 | 当前状态 |
|---|---|---|---|---|---|
| P1-1 | `mixture` param schema | M1 validation.py | M2, M5 | `{"components": [{family, weight, params}]}` | ⚠️ accepted 但不验证 |
| P1-2 | 4 种 pattern 类型 | M1 relationships.py | M2, M5 | 实现 ranking_reversal + dominance_shift；stub 另两个 | ⚠️ 类型名被接受 |
| P1-3 | Sandbox 语义 | M3 sandbox.py | M3 | `exec()` scope + timeout + 全新 namespace | **大部分已解决 ✅** |
| P1-4 | `build_fact_table` 签名 | M3 sandbox/code_validator | M3, M5 | AST 解析验证函数名和签名 | ⚠️ 函数名有，`seed` 参数不检查 |
| P1-5 | L2 noise_sigma=0 除零 | M5 statistical.py | M2 | `residuals.std() < 1e-6` 替代公式 | ⛔ stub |
| P1-6 | KS-test 单元格枚举 | M5 statistical.py | — | 迭代 effects 笛卡尔积，跳过 < 5 行，上限 100 | ⛔ stub |
| P1-7 | dominance_shift 验证 | M5 pattern_checks.py | — | 排名变化检测 | ❌ 缺失 |
| P1-8 | convergence/seasonal_anomaly | M5 pattern_checks.py | — | Stub 为 `Check(passed=True)` | ❌ 缺失 |

### P2 阻塞项

| # | 阻塞项 | 源头 | 影响 | Stage3 建议 | 当前状态 |
|---|---|---|---|---|---|
| P2-1 | `scale` 参数 | M1 columns.py | M1 内部 | No-op until 规范明确 | ⚠️ dead param |
| P2-2 | 多列 `on` | M1 relationships.py | M2 | 限制单列 or tuple keys | ⚠️ 只用 `on[0]` |
| P2-3 | `censoring` | M1/M2 realism.py | M2 | 接受存储，stub 下游 | ⛔ NotImplementedError |
| P2-4 | Step 1/2 顺序强制 | M1 simulator.py | — | 加 `_phase` flag | ⚠️ 部分 |
| P2-5 | 模式组合优先级 | M2 patterns.py | M5 L3 | 按声明顺序，文档记录 | ⚠️ 隐式顺序 |
| P2-6 | 模式破坏公式一致性 | M2 patterns.py | M5 L2 | L2 排除模式行 | ❌ 无保护 |
| P2-7 | Realism 与模式交互 | M2 realism.py | M5 L3 | realism 跳过 pattern_mask 行 | ❌ 无 pattern_mask |
| P2-8 | Metadata 校验行为 | M4 builder.py | M5 | docstring 说 raise，实际 warning | ⚠️ 偏差 |
| P2-9 | 验证排序 | M5/M2 | M5 L1/L3 | 先验证后注入 realism | ⚠️ 未定义 |
| P2-10 | 多错误同时发生 | M3 sandbox.py | M3 | 接受 one-at-a-time | ⚠️ 未处理 |
| P2-11 | 上下文窗口耗尽 | M3 sandbox.py | M3 | 3 次保留完整历史 + token 检查 | ⚠️ 被无状态绕过 |
| P2-12 | Loop A 终端返回类型 | M3/pipeline | Pipeline | 统一 `SkipResult` / `RetryLoopResult` | ⚠️ 两类型共存 |

### P3 阻塞项

| # | 阻塞项 | 源头 | 影响 | Stage3 建议 | 当前状态 |
|---|---|---|---|---|---|
| P3-1 | Per-parent 缺失父值 | M1 columns.py | M2 | raise ValueError 要求完全覆盖 | **已解决 ✅** |
| P3-2 | 负分布参数 | M1/M2 | M2 | 生成时 clamp 到有效范围 | ❌ 缺失 |
| P3-3 | 模式组合目标重叠 | M2 patterns.py | M5 L3 | 按声明顺序，文档记录顺序突变 | ⚠️ 隐式 |
