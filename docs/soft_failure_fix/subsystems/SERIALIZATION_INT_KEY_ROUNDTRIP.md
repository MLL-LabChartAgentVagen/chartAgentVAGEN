# Serialization: int-keyed dict 往返归一（2026-05-31）

> **TL;DR**：整数取值的分类列被用作 group-dependency parent（或 within-group 子分类 parent）时，`declarations` 经 JSON 往返后会**整列变 None**——`json.dumps` 把 dict 键强制成字符串，而分类列 `values` 保持 int，二者不再匹配。已在反序列化层归一修复。**与 M1/noise 无关。**

## 症状

Stage 2 replay（`agpds_execute` / `residual_source_dump --declarations`）对某些 scenario 直接崩：

```
'obs_bias' in formula has no definition for 'None'
```

ks-measure-n90 批次里 **2/90** 命中（`agpds_e3dd9db51a`、`agpds_e64a0fe4fc`），都因为用了整数 `year`（`[2023, 2024]`）作 group-dependency parent。

## 根因：JSON 键 stringify + 采样层精确比较

1. 生成脚本用整数：`add_category("year", values=[2023,2024])` + `add_group_dependency(..., conditional_weights={2023:{...}})`。生成时 int == int → 匹配 → 成功 → 声明保存。
2. `json.dumps({2023: ...})` → `{"2023": ...}`（**JSON 的 object 键永远是字符串**），而 `year` 值在 JSON 数组里仍是 int。
3. 回读后 [`skeleton.sample_dependent_root`](../../../pipeline/phase_2/engine/skeleton.py#L168) 的 `mask = parent_values == parent_val`（无类型强制）：`int 2023 == "2023"` 恒 False → 每行 fall through → 依赖列 `np.empty(..., dtype=object)` 整列 **None**。
4. 下游 effect（按值集匹配到该列）查 `None` 键 → 崩；若该列没被结构 effect 消费，则**静默产出全-None 列**（更隐蔽的坏数据）。

这是 **Stage1/Stage2 不一致**：Stage 1（内存、无往返）int 键正常，往返后才坏。`sample_child_category`（[skeleton.py:247](../../../pipeline/phase_2/engine/skeleton.py#L247)）同形（within-group 子分类 dict weights）同理。

## 修复（反序列化层，单点）

[`serialization.py`](../../../pipeline/phase_2/serialization.py) 新增 `_coerce_keys_by_columns`，在 `declarations_from_json` 里把键归一回对应 parent 列的声明取值 dtype（`{str(v): v for v in column.values}`）：

- group_dependencies `conditional_weights`：按 `on` 各层 + `child_root` 逐层归一。
- within-group 子分类 `weights`（dict 形）：按 parent 列归一。
- 非破坏性（构造副本，不 mutate 传入 dict）；str-keyed 正常情形为 no-op。

**未改 `skeleton.py`**：往返一致性归反序列化层（单一职责）；不在采样层加 `str()` 强制。

## 测试

[`tests/modular/test_serialization.py`](../../../pipeline/phase_2/tests/modular/test_serialization.py)（此前**无任何**往返测试）：
- `test_int_parent_group_dep_roundtrip`：往返后 on-disk 键确为 str、from_json 后回 int、依赖列无 None。
- `test_string_parent_group_dep_roundtrip_noop`：防过度归一。
- `test_int_parent_child_weights_roundtrip`：覆盖子分类路径。

## 验证

- 新测试 3 passed；全 phase_2 套件 442 passed / 2 skipped（M1 baseline）无新失败。
- 端到端：`agpds_e3dd9db51a`（gas_fraction σ=1.5→residual 1.50）、`agpds_e64a0fe4fc`（lifecycle_carbon σ=150→148.9）replay 不再崩。

## 关联

- 发现于 M1 residual 调查的 `--declarations` 复核环节：[`residual_source_dump.py`](../../../pipeline/phase_2/analysis/residual_source_dump.py)、[mechanisms/M1_RESIDUAL_RECONCILIATION.md](../mechanisms/M1_RESIDUAL_RECONCILIATION.md) §6 旁注。
