# Simulator Refactor Maintenance Notes

## 1. 文档目的

本文档记录一次已经落地的 `phase_2_new/agpds/simulator.py` 结构性重构，供后续维护、继续开发 Sprint 7+/Blocker 解锁时参考。

目标不是改变 `FactTableSimulator` 的公共使用方式，而是在不破坏 SDK 入口契约的前提下，把已经稳定的运行时实现细节从 `simulator.py` 中拆出，降低主文件的职责密度。

## 2. 重构前后的核心判断

### 重构前

- `simulator.py` 同时承载：
  - 顶层 SDK 入口
  - declaration API
  - registry ownership
  - DAG 构建与图算法
  - skeleton engine
  - pattern injection
  - realism injection
  - metadata builder
  - declaration-phase validation
- 这使得 `simulator.py` 既是 façade/orchestrator，又包含了大量具体实现。

### 重构后

- `FactTableSimulator` 继续保留为唯一公共 SDK 入口。
- `generate()` 继续保留在 `simulator.py`，但改为 orchestration shell。
- 稳定的运行时实现细节被迁出到独立模块。
- declaration-phase validation、weights、formula 相关 helper 暂时保留，等待第二轮拆分。

## 3. 本次重构的边界原则

### 保留在 `simulator.py` 的内容

- `FactTableSimulator` 类本身
- 所有 public declaration API：
  - `add_category()`
  - `add_temporal()`
  - `add_measure()`
  - `add_measure_structural()`
  - `declare_orthogonal()`
  - `add_group_dependency()`
  - `inject_pattern()`
  - `set_realism()`
  - `generate()`
- registry ownership：
  - `_columns`
  - `_groups`
  - `_orthogonal_pairs`
  - `_group_dependencies`
  - `_patterns`
  - `_realism_config`
  - `_measure_dag`
- 强依赖实例内部状态的 helper：
  - `_is_group_root()`
  - `_get_group_for_column()`
  - `_check_orthogonal_conflict()`
  - `_check_dependency_conflict()`
  - `_get_dependency_for_root()`
- 仍与 declaration API 紧耦合的声明期校验：
  - `_validate_param_model()`
  - `_validate_param_value()`
  - `_validate_effects_in_param()`
  - `_validate_structural_effects()`
  - `_normalize_weight_dict_values()`
  - `_validate_and_normalize_flat_weights()`
  - `_validate_and_normalize_dict_weights()`
  - `_extract_formula_symbols()`
  - `_parse_iso_date()`
- 编排型实现：
  - `_build_full_dag()`
  - `_post_process()`
  - `generate()`

### 迁出原则

- 纯图算法优先迁出。
- 运行时 phase 细节优先迁出。
- metadata builder 单独迁出。
- 不把 validator 逻辑回迁到 `simulator.py`。
- 不为尚未冻结的 formula / stochastic measure / full metadata contract 做过早抽象。

## 4. 新模块与职责

### `phase_2_new/agpds/dag.py`

承接纯图算法：

- `detect_cycle_in_adjacency()`
- `topological_sort()`
- `extract_measure_sub_dag()`

设计理由：

- 输入主要是 adjacency / set 这类显式参数。
- 接近纯函数，最易单测。
- 与 Sprint 7 validator / auto-fix 语义耦合最低。

### `phase_2_new/agpds/engine_skeleton.py`

承接 Phase α skeleton builder 及其子采样器：

- `build_skeleton()`
- `sample_independent_root()`
- `sample_dependent_root()`
- `sample_child_category()`
- `sample_temporal_root()`
- `derive_temporal_child()`
- `enumerate_daily_dates()`
- `enumerate_period_dates()`
- `enumerate_monthly_dates()`

设计理由：

- Sprint 5 已形成稳定子系统。
- 行为边界清晰：只负责 non-measure columns。
- 输入可以显式传入 `columns`、`group_dependencies`、`target_rows`、`rng`。

### `phase_2_new/agpds/pattern_engine.py`

承接 Phase γ pattern injection：

- `inject_patterns()`
- `inject_outlier_entity()`
- `inject_trend_break()`

设计理由：

- Sprint 6 只闭环了两类 pattern，范围清晰。
- 两个算法已锁定，不必继续占用 `simulator.py` 主体。

### `phase_2_new/agpds/realism_engine.py`

承接 Phase δ realism injection：

- `inject_realism()`
- `inject_missing_values()`
- `inject_dirty_values()`
- `perturb_string()`

设计理由：

- Sprint 6 只覆盖 `missing` 与 `dirty`。
- `censoring` 仍 blocked，因此当前边界稳定且收敛。

### `phase_2_new/agpds/metadata.py`

承接元数据构建：

- `build_schema_metadata()`

设计理由：

- 当前稳定输出只有：
  - `dimension_groups`
  - `orthogonal_groups`
  - `measure_dag_order`
  - `total_rows`
- builder 单独成模块后，后续 metadata contract 变化不会继续污染 `simulator.py`。

## 5. `simulator.py` 内的重构方式

本次不是“移除入口”，而是“薄壳化”。

### 具体做法

- `simulator.py` 新增内部模块导入：
  - `agpds.dag as _dag`
  - `agpds.engine_skeleton as _engine`
  - `agpds.pattern_engine as _pattern`
  - `agpds.realism_engine as _realism`
  - `agpds.metadata as _meta`
- 原先的私有方法名保留不变，但函数体改为委派：
  - `_topological_sort()` -> `_dag.topological_sort()`
  - `_extract_measure_sub_dag()` -> `_dag.extract_measure_sub_dag()`
  - `_detect_cycle_in_adjacency()` -> `_dag.detect_cycle_in_adjacency()`
  - `_build_skeleton()` -> `_engine.build_skeleton()`
  - `_sample_*()` / `_derive_temporal_child()` / `_enumerate_*()` -> `_engine.*`
  - `_inject_patterns()` / `_inject_outlier_entity()` / `_inject_trend_break()` -> `_pattern.*`
  - `_inject_realism()` / `_inject_missing_values()` / `_inject_dirty_values()` / `_perturb_string()` -> `_realism.*`
  - `_build_schema_metadata()` -> `_meta.build_schema_metadata()`

### 保留为本地实现而不迁出的内容

- `_build_full_dag()`
- `_post_process()`

原因：

- 它们不是纯工具函数。
- 两者都直接消费多个 registry，并承担 façade 层的本地编排职责。

## 6. 对外兼容性约束

本次重构明确遵守以下兼容性约束：

- `FactTableSimulator` 对外导入路径不变。
- `agpds/__init__.py` 的 `__all__` 不变。
- `generate()` 方法名与对外语义不变。
- 既有异常类型不变。
- `validator.py` 继续独立，不回流到 `simulator.py`。

## 7. 已验证的事项

本次重构完成后，已做过以下验证：

- `FactTableSimulator` 可正常导入与实例化。
- declaration API + `generate()` 基本链路可运行。
- 生成后的 `df` 与 `meta` 可通过至少一条 validator 路径（如 `check_row_count()`）。
- 新模块本身可单独导入。
- `dag.py` 的纯图函数可独立工作。
- `realism_engine.py` 的 `perturb_string()` 可独立工作。
- `ReadLints` 未发现本次改动引入的 linter 问题。

## 8. 重构后文件职责快照

### `simulator.py`

当前职责应理解为：

- SDK entrypoint
- façade
- declaration state owner
- generate orchestrator shell
- declaration-phase validation host

### 不应再继续往 `simulator.py` 塞入的内容

- 新的 pattern 注入算法实现细节
- 新的 realism 注入实现细节
- 通用 DAG 算法
- 独立 metadata builder 逻辑
- validator / auto-fix 的执行细节

## 9. 明确延期到第二轮拆分的内容

以下内容本次故意不拆：

- declaration validation
- weights normalization / validation
- formula symbol utilities
- `_parse_iso_date()`

推荐的第二轮目标模块：

- `phase_2_new/agpds/declaration_validation.py`
- `phase_2_new/agpds/weights.py`
- `phase_2_new/agpds/formula.py`

延期原因：

- 这些逻辑与 public declaration API 强耦合。
- Sprint 7 之后再拆，风险更低。
- formula DSL 仍未冻结，过早抽离只会形成半成品模块。

## 10. 后续维护规则

后续如果继续改 Phase 2，请遵守以下规则：

1. 新的运行时 phase 细节优先加到独立模块，不要直接堆回 `simulator.py`。
2. `simulator.py` 新增代码应优先属于：
   - public API
   - registry-bound helper
   - orchestration shell
   - declaration-phase validation
3. `validator.py` 的扩张保持在 validator 侧，不要把 L1/L2/L3 或 auto-fix 重新塞回 simulator。
4. 如果 Blocker 2 解锁，再统一推进 `formula.py`，不要提前做半套 parser/evaluator 抽象。
5. 如果 metadata contract 变化，优先修改 `metadata.py`，避免扩大 `simulator.py` 体积。

## 11. 一句话维护结论

这次重构的本质不是“换入口”，而是“保住 `FactTableSimulator` 作为稳定 façade，同时把已经稳定的运行时实现细节拆成可单测、可替换、可独立演进的内部模块”。
