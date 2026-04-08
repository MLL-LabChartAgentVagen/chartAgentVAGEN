# AGPDS Phase 2 — Module Interfaces

## M1 — SDK Surface

**Entry input:**
- `target_rows : int`, entering via `sdk/simulator.py` (`FactTableSimulator.__init__()`)
- `seed : int`, entering via `sdk/simulator.py` (`FactTableSimulator.__init__()`)
- *(then declaration methods: `add_category()`, `add_measure()`, `add_measure_structural()`, `add_temporal()`, `declare_orthogonal()`, `add_group_dependency()`, `inject_pattern()`, `set_realism()`)*

**Final output:**
- `df : pd.DataFrame`, exiting via `sdk/simulator.py` (`FactTableSimulator.generate()`)
- `meta : dict[str, Any]`, exiting via `sdk/simulator.py` (`FactTableSimulator.generate()`)

---

## M2 — Generation Engine

**Entry input:**
- `columns : OrderedDict[str, dict[str, Any]]`, entering via `engine/generator.py` (`run_pipeline()`)
- `groups : dict[str, DimensionGroup]`, entering via `engine/generator.py`
- `group_dependencies : list[GroupDependency]`, entering via `engine/generator.py`
- `measure_dag : dict[str, list[str]]`, entering via `engine/generator.py`
- `target_rows : int`, entering via `engine/generator.py`
- `seed : int`, entering via `engine/generator.py`
- `patterns : list[dict[str, Any]] | None`, entering via `engine/generator.py`
- `realism_config : dict[str, Any] | None`, entering via `engine/generator.py`
- `overrides : dict | None`, entering via `engine/generator.py`
- `orthogonal_pairs : list | None`, entering via `engine/generator.py`

**Final output:**
- `df : pd.DataFrame`, exiting via `engine/generator.py` (`run_pipeline()`)
- `meta : dict[str, Any]`, exiting via `engine/generator.py` (`run_pipeline()`)

---

## M3 — LLM Orchestration

**Entry input:**
- `scenario_context : dict[str, Any]`, entering via `orchestration/retry_loop.py` (`orchestrate()`)
- `llm_client : LLMClient`, entering via `orchestration/retry_loop.py`
- `max_retries : int`, entering via `orchestration/retry_loop.py`

**Final output:**
- `df : pd.DataFrame`, exiting via `orchestration/retry_loop.py` (`orchestrate()`)
- `meta : dict[str, Any]`, exiting via `orchestration/retry_loop.py`
- `raw_declarations : dict[str, Any]`, exiting via `orchestration/retry_loop.py`
- *(or `SkipResult` on exhausted retries)*

---

## M4 — Schema Metadata

**Entry input:**
- `groups : dict[str, DimensionGroup]`, entering via `metadata/builder.py` (`build_schema_metadata()`)
- `orthogonal_pairs : list[OrthogonalPair]`, entering via `metadata/builder.py`
- `target_rows : int`, entering via `metadata/builder.py`
- `measure_dag_order : list[str]`, entering via `metadata/builder.py`
- `columns : OrderedDict[str, dict[str, Any]] | None`, entering via `metadata/builder.py`
- `group_dependencies : list[GroupDependency] | None`, entering via `metadata/builder.py`
- `patterns : list[dict[str, Any]] | None`, entering via `metadata/builder.py`

**Final output:**
- `meta : dict[str, Any]`, exiting via `metadata/builder.py` (`build_schema_metadata()`)
  - Keys: `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns`, `measure_dag_order`, `patterns`, `total_rows`

---

## M5 — Validation Engine

### Validation path (`validator.py`)

**Entry input:**
- `meta : dict[str, Any]`, entering via `validation/validator.py` (`SchemaAwareValidator.__init__()`)
- `df : pd.DataFrame`, entering via `validation/validator.py` (`SchemaAwareValidator.validate()`)
- `patterns : list[dict[str, Any]] | None`, entering via `validation/validator.py` (`validate()`)

**Final output:**
- `report : ValidationReport`, exiting via `validation/validator.py` (`validate()`)

### Auto-fix loop path (`autofix.py`)

**Entry input:**
- `build_fn : Callable[[int, ParameterOverrides | None], tuple[pd.DataFrame, dict]]`, entering via `validation/autofix.py` (`generate_with_validation()`)
- `meta : dict[str, Any]`, entering via `validation/autofix.py`
- `patterns : list[dict[str, Any]]`, entering via `validation/autofix.py`
- `base_seed : int`, entering via `validation/autofix.py`
- `max_attempts : int`, entering via `validation/autofix.py`
- `auto_fix : dict[str, Any] | None`, entering via `validation/autofix.py`
- `realism_config : dict[str, Any] | None`, entering via `validation/autofix.py`

**Final output:**
- `df : pd.DataFrame`, exiting via `validation/autofix.py` (`generate_with_validation()`)
- `meta : dict[str, Any]`, exiting via `validation/autofix.py`
- `report : ValidationReport`, exiting via `validation/autofix.py`
