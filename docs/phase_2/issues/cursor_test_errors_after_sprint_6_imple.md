# Test errors after sprint 6 implementation
_Exported on 3/26/2026 at 20:20:17 CDT from Cursor (2.6.21)_

---

**User**

@c:\Users\dingc\.cursor\projects\c-Users-dingc-Downloads-implementation\terminals\3.txt:885-1025 After implement sprint 6, these 4 tests from sprint 2 implementation goes wrong. Help me to spot where and why such errors happen.

---

**Cursor**

我先定位这 4 个失败用例对应的 `add_temporal` / 分组层级逻辑，再对照 sprint 6 引入的改动看看是哪里把 `time` 组的 `hierarchy` 弄丢了。

我已经确认失败断言都指向同一个症状：`time` 组的 `hierarchy` 只剩根列 `visit_date`，派生列 `day_of_week` / `month` 没有被并入层级。接下来我直接读实现和测试文件，定位是哪段状态更新在 sprint 6 后变了。

我已经定位到有多份 `simulator.py`：`files/agpds` 是当前被测试的实现，`sprint_2` / `sprint_6` 则像阶段快照。现在会直接对比 `add_temporal` 和 group 相关结构，判断是回归还是规格本身在 sprint 6 改了。

我看到 `sprint_2/simulator.py` 里的 `add_temporal()` 是一次性把 `time` 组建成 `columns=[root]+derive`、`hierarchy=[root]+derive`。如果当前实现不是这样，问题基本就锁定在 sprint 6 对 group 结构的重构上了。

根因线索已经很明显了：`files/agpds/simulator.py` 和 `sprint_6/simulator.py` 的 `add_temporal()` 里有一段注释明确写着“`time` 的 `hierarchy` 只保留 root”。这和 sprint 2 测试要求的 `["visit_date", "day_of_week", "month"]` 是直接冲突的。

我还在检查这个回归是“sprint 6 才引入”，还是更早就埋下了。因为当前实现和 `sprint_6/simulator.py` 一致，所以需要再往前看一版，确认是哪个 sprint 第一次把 temporal `hierarchy` 改成 root-only。

我找到更关键的一条证据：`audit/phase_2.md` 里的 phase 2 文档示例，已经把 `time` 组写成 `columns=["visit_date","day_of_week","month"]` 但 `hierarchy=["visit_date"]`。也就是说，从后续阶段的文档视角，temporal 派生列被当成“可用列”，不是“层级链条”。

## 结论

这 4 个失败其实是同一个根因：当前实现把 `time` 组的 `hierarchy` 改成了“只保留 root”，而 sprint 2 的测试仍然要求“root + derive 列全都在 hierarchy 里”。

当前实现是这样的：

```584:592:files/agpds/simulator.py
# FIX: [self-review item 1] — §2.6 example shows "time" hierarchy as
# ["visit_date"] (root only), not ["visit_date", "day_of_week", "month"].
# Derived temporal columns are computed features, not a drill-down
# hierarchy like categorical parent→child. Hierarchy = root only.
self._groups[_TEMPORAL_GROUP_NAME] = DimensionGroup(
    name=_TEMPORAL_GROUP_NAME,
    root=name,
    columns=list(all_columns),
    hierarchy=[name],
)
```

而 sprint 2/早期实现原本是：

```534:543:sprint_3/simulator.py
# Build the column list: temporal root first, then derived children
all_columns = [name] + list(derive)

# Create the "time" dimension group with temporal root and derived children
self._groups[_TEMPORAL_GROUP_NAME] = DimensionGroup(
    name=_TEMPORAL_GROUP_NAME,
    root=name,
    columns=list(all_columns),
    hierarchy=list(all_columns),
)
```

所以失败点非常直接：

- `files/tests/test_simulator_sprint2.py` 里的断言要求 `grp.hierarchy == ["visit_date", "day_of_week", "month"]`
- 但 `files/agpds/simulator.py` 现在返回的是 `["visit_date"]`

## 它是在哪里引入的

虽然你是在做完 sprint 6 后看到它炸掉，但从代码快照看，行为变化其实在 `sprint_5` 就已经引入，`sprint_6` 只是沿用了它：

```575:583:sprint_5/simulator.py
# FIX: [self-review item 1] — §2.6 example shows "time" hierarchy as
# ["visit_date"] (root only), not ["visit_date", "day_of_week", "month"].
# Derived temporal columns are computed features, not a drill-down
# hierarchy like categorical parent→child. Hierarchy = root only.
self._groups[_TEMPORAL_GROUP_NAME] = DimensionGroup(
    name=_TEMPORAL_GROUP_NAME,
    root=name,
    columns=list(all_columns),
    hierarchy=[name],
)
```

也就是说，真正的“回归提交点”不是 sprint 6 逻辑本身，而是 sprint 5 开始对 temporal hierarchy 语义的重定义。

## 它为什么会被改

改动理由已经直接写在注释里了：作者认为后续 spec / metadata 示例把 temporal derive 列视为“派生特征”，不是“层级链条”。

这个证据在 `audit/phase_2.md` 里也能对上：

```445:452:audit/phase_2.md
schema_metadata = {
    "dimension_groups": {
        "entity":  {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]},
        "patient": {"columns": ["severity"], "hierarchy": ["severity"]},
        "payment": {"columns": ["payment_method"], "hierarchy": ["payment_method"]},
        "time":    {"columns": ["visit_date", "day_of_week", "month"], "hierarchy": ["visit_date"]}
    },
```

以及前面的解释文本：

```138:146:audit/phase_2.md
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
Group "time":     visit_date → [day_of_week, month]  (derived)

**Within-group hierarchy:** Each group has a **root** column (no parent). Child columns are sampled conditionally on their parent: $P(\text{department} \mid \text{hospital})$ uses per-parent weight vectors.

**Temporal as dimension group:** Temporal columns are a special dimension group. The root is the declared temporal column; derived calendar levels are automatically extracted via `derive` and available as predictors.
```

所以现在仓库里其实存在两套互相冲突的契约：

- sprint 2 测试 / 早期实现：temporal derive 列属于 `hierarchy`
- sprint 5+ 实现 / phase 2 文档示例：temporal derive 列只属于 `columns`，不属于 `hierarchy`

## 为什么只坏这 4 个测试

因为派生列本身并没有丢，丢的只是 `group.hierarchy` 里的记录。

当前实现仍然会注册 derive 列，并给它们设置 `parent=name`：

```597:615:files/agpds/simulator.py
# Register the temporal root column with parsed date range and freq
self._columns[name] = {
    "type": "temporal",
    "group": _TEMPORAL_GROUP_NAME,
    "parent": None,
    "start": start_date,
    "end": end_date,
    "freq": freq,
    "derive": list(derive),
}

# Register each derived column as a temporal child — these are
# automatically extracted from the root at generation time (§2.2)
for token in derive:
    self._columns[token] = {
        "type": "temporal_derived",
        "group": _TEMPORAL_GROUP_NAME,
        "parent": name,
        "derivation": token,
    }
```

而后面的 DAG 也是根据 `parent` 建边，不是根据 `grp.hierarchy` 建边：

```1571:1593:files/agpds/simulator.py
# ===== Edge Type 1: parent→child (within-group hierarchy) =====

# For every column that has a parent, add a directed edge from
# parent to child. This captures the §2.2 within-group hierarchy
# (e.g., hospital→department).
for col_name, col_meta in self._columns.items():
    parent = col_meta.get("parent")
    if parent is not None and parent in adjacency:
        adjacency[parent].append(col_name)

# ===== Edge Type 3: temporal_root→derived (temporal derivations) =====

# Already captured by Edge Type 1 — temporal derived columns have
# `parent=<temporal_root>` in _columns.
```

所以你会看到：

- `day_of_week` / `month` 还在 `_columns`
- `grp.columns` 也还是对的
- 只有 `grp.hierarchy` 不再包含它们
- 因而正好只炸到这 4 个断言

## 额外的不一致点

仓库内部现在还有一处语义不一致：`DimensionGroup` 的注释仍然写着 temporal derived levels 是 children。

```27:35:files/agpds/models.py
class DimensionGroup:
    """A named dimension group containing a hierarchy of categorical columns.

    [Subtask 2.1.1]

    Represents the §2.2 dimension group abstraction. Each group has exactly
    one root column (no parent) and zero or more child columns forming a
    hierarchy. Temporal groups use the temporal column as root with derived
    calendar levels as children.
```

这和当前 `hierarchy=[name]` 的实现并不完全一致，也解释了为什么旧测试还会坚持原语义。

## 你现在该怎么判断

你需要先决定哪份契约才是“最终正确”：

- 如果以 sprint 2 contract 为准：`add_temporal()` 应该改回 `hierarchy=list(all_columns)`。
- 如果以后续 `phase_2.md` / sprint 5+ 语义为准：这 4 个 sprint 2 测试需要更新，`DimensionGroup` 的说明也应该一起改，避免继续自相矛盾。

如果你愿意，我下一步可以直接帮你列出“最小修复方案”两套版本：一套改实现，一套改测试。

---

**User**

给我找一下@audit/phase_2.md 中把 temporal derive 列视为“派生特征”，不是“层级链条”的相关的部分。并讨论两种方案的优缺点

---

**Cursor**

我先把 `audit/phase_2.md` 里明确表达 temporal derive 语义的几处原文摘出来，再基于这些证据比较“算进 hierarchy”和“不算进 hierarchy”两种方案的取舍。

## 文档中相关部分

`audit/phase_2.md` 里把 temporal derive 列更像写成“从 root 计算出来的特征”，而不是常规的组内层级，证据主要有这几处。

第一处，结构总览里单独用了 `derived` 标记，而不是像分类层级那样用链式层级表达：

```138:146:audit/phase_2.md
Group "entity":   hospital ← department ← ward
Group "patient":  severity ← acuity_level
Group "payment":  payment_method
Group "time":     visit_date → [day_of_week, month]  (derived)

**Within-group hierarchy:** Each group has a **root** column (no parent). Child columns are sampled conditionally on their parent: $P(\text{department} \mid \text{hospital})$ uses per-parent weight vectors.

**Temporal as dimension group:** Temporal columns are a special dimension group. The root is the declared temporal column; derived calendar levels are automatically extracted via `derive` and available as predictors.
```

第二处，生成层次里把它们单独归类为 `temporal derivation`，和真正的 within-group hierarchy 分开：

```220:226:audit/phase_2.md
Layer 0 — Independent roots:
  hospital, severity, visit_date

Layer 1 — Dependent non-measure columns:
  payment_method       ← P(payment | severity)          [cross-group root dep]
  department           ← P(dept | hospital)              [within-group hierarchy]
  day_of_week, month   ← derived from visit_date         [temporal derivation]
```

第三处，执行步骤也明确写成函数变换，不是条件采样：

```244:251:audit/phase_2.md
Step 1: Generate all non-measure columns (topological order)
  1. hospital_i       ~ Cat([0.25, 0.20, ...])                 // independent root
  2. severity_i       ~ Cat([0.50, 0.35, 0.15])                // independent root
  3. visit_date_i     ~ Uniform(2024-01-01, 2024-06-30)        // independent root
  4. payment_method_i ~ Cat(weights[severity_i])                // root dep ← severity
  5. department_i     ~ Cat(weights | hospital_i)                // child ← hospital
  6. day_of_week_i    = DOW(visit_date_i)                       // temporal derived
  7. month_i          = MONTH(visit_date_i)                     // temporal derived
```

第四处，metadata 示例最直接：`columns` 里包含 derive 列，但 `hierarchy` 只保留 root：

```446:451:audit/phase_2.md
schema_metadata = {
    "dimension_groups": {
        "entity":  {"columns": ["hospital", "department"], "hierarchy": ["hospital", "department"]},
        "patient": {"columns": ["severity"], "hierarchy": ["severity"]},
        "payment": {"columns": ["payment_method"], "hierarchy": ["payment_method"]},
        "time":    {"columns": ["visit_date", "day_of_week", "month"], "hierarchy": ["visit_date"]}
```

第五处，下游使用语义也把 `hierarchy` 和 temporal derive 区分开了：

```710:712:audit/phase_2.md
- **Aggregation charts** (bar, pie, line) apply `GROUP BY` on hierarchy roots.
- **Drill-down charts** (grouped/stacked bar, treemap) exploit within-group hierarchy with per-parent conditionals.
```

这几段合起来，基本可以认定文档倾向于：

- `day_of_week` / `month` 属于 `time` 组
- 但它们是从 `visit_date` 派生出来的特征
- 不是 `hierarchy` 语义里的“drill-down chain”

## 两种方案的优缺点

### 方案 A：temporal derive 列也放进 `hierarchy`

也就是像 sprint 2 测试那样，让 `hierarchy = ["visit_date", "day_of_week", "month"]`。

优点：

- 和早期 sprint 2 contract 一致，现有这 4 个测试会直接恢复通过。
- 实现更统一：所有 group 都遵循“`columns` 和 `hierarchy` 基本同步”的直觉。
- 对不了解 temporal 特殊语义的人更容易理解，少一个例外规则。

缺点：

- 语义上不够精确，`month` 不是通过 `P(month | visit_date)` 采样出来的层级子节点，而是确定性函数。
- 会把“条件层级”和“派生特征”混成一个概念，后续做 metadata 消费、可视化解释、文档说明时更容易混乱。
- 如果下游把 `hierarchy` 理解成 drill-down 路径，`visit_date -> day_of_week -> month` 这种顺序本身也不自然，甚至不总是可逆或严格层级化。

### 方案 B：temporal derive 列只在 `columns`，不进 `hierarchy`

也就是文档当前表达的方式：`columns=["visit_date","day_of_week","month"]`，`hierarchy=["visit_date"]`。

优点：

- 语义更干净：`hierarchy` 专门表示真正的组内层级/条件结构，temporal derive 表示 deterministic feature extraction。
- 和 `audit/phase_2.md` 的整体叙述一致，包括生成流程、metadata 示例、图表语义。
- 更利于以后扩展更多 temporal features，比如 `is_weekend`、`quarter`，它们明显更像特征而不是 drill-down 层级。

缺点：

- 会和 sprint 2 的旧测试、旧实现预期冲突，需要统一更新 contract。
- `DimensionGroup` 的抽象会变得稍微“不纯”：有的组 `columns != hierarchy`，需要调用方理解这个特例。
- 如果某些下游逻辑偷懒假设“组内所有列都在 `hierarchy` 里”，就需要额外修正。

## 我的判断

如果你现在是以 `audit/phase_2.md` 作为后续阶段的主规范，那么更合理的是 **方案 B**。因为文档已经多次明确把 temporal derive 描述为“derived / available as predictors / temporal derivation”，而不是 within-group hierarchy。

但如果你的目标是“严格保持 sprint 2 原合同不动”，那就只能回到 **方案 A**，否则 sprint 2 的断言必然继续冲突。

最关键的不是哪种绝对更好，而是要统一这三处定义：

- `add_temporal()` 的实现
- sprint 2 的测试合同
- `DimensionGroup` / metadata 文档语义

---

## Resolution

**Adopted: Plan B** — temporal derive columns belong to `columns` but NOT to `hierarchy`. The `time` group's `hierarchy` contains only the temporal root.

Changes applied:
- `phase_2_new/agpds/models.py`: `DimensionGroup` docstring updated to distinguish categorical hierarchy from temporal derive semantics.
- `phase_2_new/agpds/simulator.py`: `add_temporal()` and `_build_full_dag()` comments clarified that `parent` on temporal derived columns is a DAG dependency, not a `hierarchy` membership.
- `phase_2_new/agpds/validator.py`: `hierarchy[0]` usage annotated with temporal root-only constraint.
- `phase_2_new/tests/test_simulator_sprint2.py`: `test_row31` and `test_row50` assertions updated to `hierarchy == ["visit_date"]`.
- `sprint_2/test_simulator_sprint2.py` and `sprint_2/sprint_2_walkthrough.md`: aligned with superseded notice.
- Task hierarchy and sprint plan documents: "Derive temporal children" renamed to "Derive temporal features"; output description clarified.

如果你愿意，我可以下一步继续帮你把这三处整理成一份“推荐统一口径清单”。

