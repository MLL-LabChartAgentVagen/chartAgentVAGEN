# ChartAgent Phase 0–2 改进建议

> 实施清单。当前 code structure 与每个文件的功能详见 [STRUCTURE.md](STRUCTURE.md)。

---

## 1. 改进事项（按严重度）

### 🔴 必须修

| # | 问题 | 文件 / 行号 | 修复方向 |
|---|---|---|---|
| 1.1 | **`DomainSampler.sample` 用全局 `random.sample`**，破坏 `(declarations, seed) → bit-for-bit reproducible` | `phase_0/domain_pool.py:399` | `__init__(seed)` 拿 `random.Random(seed)` 实例；`sample` 调实例方法 |
| 1.2 | **`generate_unique_id` 用 `random.random()`** —— `generation_id` 不可复现，artifact 路径每次跑都换 | `core/utils.py:60` | 新建 `core/ids.py::generation_id(seed, scenario_id)`，用 `hashlib.sha256` |
| 1.3 | **~9.5 kLoC legacy / 死代码** —— `pipeline/legacy/`、`pipeline/core/legacy/`、`pipeline/adapters/` 已 staged for delete；`schemas/master_table.py` 与 `core/master_table.py` 字节级相同且 Phase 0–2 无人 import | `pipeline/legacy/`、`pipeline/core/legacy/`、`pipeline/adapters/`、`pipeline/schemas/master_table.py`、`pipeline/core/master_table.py` | 一次性 `git rm` |
| 1.4 | **`sandbox.py` 864 LoC 干了三件事** —— `run_retry_loop()` (228 LoC) 调 LLM、是顶层 Loop A driver，不该在 sandbox；而 `retry_loop.py` 是它的薄包装 | `phase_2/orchestration/sandbox.py:637-864` · `retry_loop.py` 全文 | 把 228 LoC 从 sandbox 搬到 retry_loop；sandbox 缩到 ~340 LoC（仅 `execute_in_sandbox` + `format_error_feedback`） |
| 1.5 | **顶层 `README.md` 描述的是 legacy bar-chart pipeline**（chartGenerators / 操作子组合），完全没提 Phase 0–2 / FactTableSimulator | `README.md` | 重写：四 phase 概览 / 三个 CLI 入口 / 离线 build 步骤 / 引用 storyline 作为 canonical spec |

### 🟡 应该修

| # | 问题 | 文件 / 行号 | 修复方向 |
|---|---|---|---|
| 1.6 | **`target_rows` 没按 tier 区分** —— prompt + validator 仍是 100–3000 单一范围；storyline §1.2 建议 simple 200–500 / medium 500–1000 / complex 1000–3000 | `phase_1/scenario_contextualizer.py:41` (prompt) · `:241` (validator) | prompt 文本按 tier 重写；validator 接收 `complexity_tier` 选范围；one-shot example 的 `target_rows=900` 改到 complex 范围（≥1000） |
| 1.7 | **`llm_client.py` 被 fork** —— core (406) vs phase_2 (476)，差异只是 `TokenUsage` / `LLMResponse` / `_generate_with_usage` | `core/llm_client.py` · `phase_2/orchestration/llm_client.py` | 合并为单一 client + `track_tokens=False` 标志；删 phase_2 副本 |
| 1.8 | **Phase 1 envelope 里的 `category_id`** —— 反查 `META_CATEGORIES` 30-cat enum，下游无人读 | `phase_1/build_scenario_pool.py:144,150,245` | 删 `category_id` 字段 + `_category_id_for_topic` + `META_CATEGORIES` import；`core/utils.py` 全空就整个删掉 |
| 1.9 | **Phase 1 多个细节** —— `diversity_tracker` 是死状态（只写不读）；soft-failure 把 `_validation_warnings` 塞回 dict 污染 schema；`Metric.range` 没校验 | `phase_1/scenario_contextualizer.py:126,171,229` | 删 `diversity_tracker`；soft-failure 改 raise；增 `Metric.range` 校验（`low < high`） |
| 1.10 | **Phase 1 schemas 都是 loose dict**，跨模块边界没用 `@dataclass`（CLAUDE.md §24） | Phase 1 全部 | 新建 `phase_1/types.py` 定义 `Metric` / `ScenarioContext` / `ScenarioRecord` |
| 1.11 | **`code_validator.py` 名字误导** —— 是 pre-sandbox AST 检查（语法 + `def build_fact_table` + `.generate()`），不验证语义 | `phase_2/orchestration/code_validator.py` | `git mv` 改名 `code_check.py` |
| 1.12 | **`pipeline/__init__.py` 缺失** —— `import pipeline` 失败 | `pipeline/__init__.py` | 新建 3 行文件，re-export `AGPDSPipeline` |
| 1.13 | **`declare_orthogonal` 在 generation 阶段是 no-op**（合规但易误解） —— storyline §2.2 明确 "Cross-group independence is opt-in, not default"，实现的"默认独立采样"恰好满足；但 maintainer 容易误以为失效 | `phase_2/engine/skeleton.py` 顶部 | 加一段 module docstring 说明 "declare_orthogonal is consumed by L1 validator + Phase 3, no-op for generation" |
| 1.14 | **Phase 0 几个小问题** —— `SEED_TOPICS` 5 项硬编码常量是死的；`overlap_checker` 硬编码 OpenAI；`_compute_diversity` 名实不符（只算 complexity tier 熵） | `phase_0/domain_pool.py:29` · `overlap_checker.py:13` | 删 `SEED_TOPICS` + 走它的 fallback；`_compute_diversity` 改名或加注释；`overlap_checker` 加 API key 显式参数 |
| 1.15 | **`UndefinedPredictorError` 是死异常类**（0 raises） | `phase_2/exceptions.py` | 删 |
| 1.16 | **`GeminiClient` 向后兼容别名**（无活引用） | `core/llm_client.py:399` · `phase_2/orchestration/llm_client.py:399` | 删 |

### ⚫ 死/夹带

| # | 项目 | 处置 |
|---|---|---|
| 1.17 | `phase_1/__init__.py` 重导出 `deduplicate_scenarios`（已无引用） | 从 `__all__` 删 |
| 1.18 | `phase_1/scenario_contextualizer.py:270` 的 `deduplicate_scenarios` 简化版 | 删（实际用的是 `deduplicate_scenario_records`） |
| 1.19 | `pipeline/phase_2/docs/` 74 个 .md 设计 history | `git mv` 到 `docs/phase_2_history/` |
| 1.20 | 仓库根 `chartGenerators/` / `multiChartGenerators/` / `templates/` / `metadata/` / `utils/` / `main.py` | **本次不动**，等 Phase 3 决定 |

---

## 2. Clean code / 模块化重构建议（可选）

> 这一节不是"必须修"，是 codebase 整洁度可以更进一步的地方。**如果时间不充裕可以跳过整节**，主流程不依赖。

| # | 议题 | 当前问题 | 建议 |
|---|---|---|---|
| 2.1 | **CDF builder 在 engine 与 validation 重复** | `engine/measures.py` (608 LoC) 与 `validation/statistical.py` (653 LoC) 都有 per-family（gaussian / lognormal / gamma / beta / ...）的 CDF / PDF 构造代码 | 抽到 `phase_2/engine/distributions.py` 或 `phase_2/_distributions.py`，两边都 import；engine 用来采样，validation 用来跑 KS。**遵循 CLAUDE.md §22 "extract a helper the second time a pattern repeats"** |
| 2.2 | **`engine/patterns.py` 760 LoC 模板代码重复** | 6 种 pattern handler 之间共享约 160 LoC 的"按 target_expr filter df → 取被影响 mask → 按 col 修改 → 写回 rows"模板 | 抽出 `_apply_pattern_with_filter(rows, pattern_spec, mutator_fn)` helper，每个 pattern handler 只剩 mutator_fn |
| 2.3 | **`scenario_contextualizer.py` 单文件干两件事** | 既是 `ScenarioContextualizer` class（prompt + 调 LLM + 校验），又包含 `deduplicate_scenario_records` 和 `_overlap_index_pairs`（embedding 去重） | 把去重相关函数移到新文件 `phase_1/dedup.py`。一个文件一个职责 |
| 2.4 | **`phase_2/sdk/validation.py` 693 LoC 单文件** | 包含所有声明期参数校验（columns / groups / relationships / DAG），用 `if isinstance(spec, ColumnSpec): ...` 分发 | 按主题拆：`sdk/_validate_columns.py` / `_validate_groups.py` / `_validate_relationships.py` / `_validate_dag.py`；`sdk/validation.py` 只负责对外暴露与分发 |
| 2.5 | **`agpds_*.py` 4 个顶层文件命名不直观** | `agpds_pipeline.py`（class）/ `agpds_runner.py`（端到端 CLI）/ `agpds_generate.py`（Stage 1 CLI）/ `agpds_execute.py`（Stage 2 CLI），新人看名字不易区分 | 改名 `pipeline.py` / `cli/run_all.py` / `cli/generate.py` / `cli/execute.py`，并在 `pipeline/__init__.py` 显式导出 |
| 2.6 | **`pipeline/core/` 后续会变得很薄** | Phase A–D 完工后只剩 `llm_client.py` + `ids.py`，原 `master_table.py` 和 `utils.py` 都没了 | 接受 `core/` 薄状态——它就是"跨 phase 共享的少量基础设施"，是好事不是坏事。**不要为了凑内容往里塞东西。**（CLAUDE.md §22 "never extract on the third occurrence"） |

---

## 3. 重构后的目录结构

```
pipeline/
├── __init__.py                            # 新增：re-export AGPDSPipeline
│
├── phase_0/
│   ├── build_domain_pool.py
│   ├── domain_pool.py                     # DomainSampler 加 seed
│   ├── overlap_checker.py
│   ├── taxonomy_seed.json
│   ├── domain_pool.json
│   └── tests/
│
├── phase_1/
│   ├── build_scenario_pool.py             # 不再写 category_id
│   ├── scenario_contextualizer.py         # tier-aware target_rows；只剩 prompt + 调 LLM + 校验
│   ├── types.py                           # 新增：Metric / ScenarioContext / ScenarioRecord
│   ├── dedup.py                           # 新增：去重相关从 contextualizer 独立出来
│   ├── scenario_pool.jsonl
│   └── tests/
│
├── phase_2/
│   ├── pipeline.py
│   ├── types.py
│   ├── exceptions.py                      # 删 UndefinedPredictorError
│   ├── serialization.py
│   ├── sdk/                               # 不动（如果做 §2.4 则按主题拆 validation.py）
│   ├── engine/                            # 如果做 §2.1 / §2.2 则抽 distributions.py + _pattern_helper
│   ├── validation/                        # 如果做 §2.1 则共用 distributions.py
│   ├── orchestration/
│   │   ├── prompt.py
│   │   ├── code_check.py                  # 由 code_validator.py 改名
│   │   ├── sandbox.py                     # 仅 execute + format_error_feedback (~340 LoC)
│   │   └── retry_loop.py                  # Loop A driver 真正归宿（迁入后 ~400 LoC）
│   └── metadata/builder.py                # 不动
│
├── core/
│   ├── llm_client.py                      # 单一 client + track_tokens 标志，删 GeminiClient
│   └── ids.py                             # 新增：deterministic generation_id
│
├── agpds_pipeline.py                      # 不动；如果做 §2.5 则改名见目录
├── agpds_runner.py
├── agpds_generate.py
└── agpds_execute.py

# 删除：
#   pipeline/legacy/                              （~2k LoC + docs）
#   pipeline/core/legacy/                         （~6.7k LoC，含 phase_2_old/）
#   pipeline/adapters/                            （~282 LoC）
#   pipeline/schemas/                             （删完 master_table.py 后整个空了）
#   pipeline/core/master_table.py                 （字节级 dup of legacy）
#   pipeline/core/utils.py                        （删完 META_CATEGORIES + generate_unique_id 后空了）
#   pipeline/phase_2/orchestration/llm_client.py  （合并进 core/llm_client.py）
```

### 模块化与 clean code 原则（重构必须遵守）

1. **一文件一职责。** `sandbox.py` 不能既是 executor 又是 retry-loop driver；`scenario_contextualizer.py` 不能既写 prompt 又做 dedup。
2. **跨 phase 共享逻辑住 `core/` 或显式共享模块。** `check_overlap` 留在 `phase_0/overlap_checker.py` 给 Phase 1 复用是好的；LLM client 必须只有一个。
3. **跨模块边界传 `@dataclass`，不传 loose dict。** `ScenarioContext` / `SchemaMetadata` / `Check` / `ValidationReport` 全部 typed。
4. **每一层有清晰的 input/output 契约。** Loop A 输出 `Declarations`；Loop B 接受 `Declarations` 输出 `(DataFrame, schema_metadata, ValidationReport)`。
5. **不写"以防万一"的 abstraction**（CLAUDE.md §22）。
6. **不重复实现同一件事。** 当前 `master_table.py × 2`、`llm_client.py × 2`、`run_retry_loop` 同时在 sandbox.py 和 retry_loop.py —— 全部违反。

---

## 4. 改动清单（实施时跟着做）

> 自上而下，每完成一个 Phase 跑该 Phase 末尾验证，再进入下一个。每个 Phase 一次 commit。
>
> Phase A–E 是必做项；**Phase F 是可选 clean code 优化，对应 §2 那一节**。

### Phase A — 清理（极低风险）

**目标：** 删 ~10 kLoC legacy + 重复 + 死代码。**不改任何活逻辑。**

- [ ] `git rm -r pipeline/legacy/` `pipeline/core/legacy/` `pipeline/adapters/`
- [ ] `git rm pipeline/schemas/master_table.py` `pipeline/core/master_table.py` `pipeline/schemas/__init__.py`，然后 `rmdir pipeline/schemas`
- [ ] `phase_2/exceptions.py` — 删 `UndefinedPredictorError`
- [ ] `core/llm_client.py:399` 与 `phase_2/orchestration/llm_client.py:399` — 删 `class GeminiClient`
- [ ] `phase_0/domain_pool.py:29` — 删 `SEED_TOPICS` 与 `_build` 里走它的 fallback
- [ ] `phase_1/scenario_contextualizer.py:270` — 删 `deduplicate_scenarios` 简化版
- [ ] `phase_1/__init__.py` — 从 `__all__` 删 `deduplicate_scenarios`

**验证：**
```bash
pytest pipeline/phase_{0,1,2}/tests/                                      # 全绿
grep -RIn "from pipeline.legacy\|from pipeline.core.legacy\|from pipeline.adapters\|pipeline.schemas.master_table\|pipeline.core.master_table" pipeline/ --include="*.py"   # 空
grep -RIn "GeminiClient\|UndefinedPredictorError\|SEED_TOPICS\|deduplicate_scenarios" pipeline/ --include="*.py"   # 空
```

**Commit:** `chore(audit-A): drop legacy trees, byte-duplicate master_table, dead exceptions/aliases`

---

### Phase B — 确定性（低风险）

**目标：** `(declarations, seed) → bit-for-bit reproducible` 在所有非测试代码里成立。

- [ ] `phase_0/domain_pool.py` — `DomainSampler.__init__(self, pool_path, seed: int = 0)`；内部 `self._rng = random.Random(seed)`；所有 `random.sample(...)` → `self._rng.sample(...)`
- [ ] 新建 `core/ids.py`：
  ```python
  import hashlib
  def generation_id(seed: int, scenario_id: str, prefix: str = "agpds") -> str:
      h = hashlib.sha256(f"{seed}:{scenario_id}".encode()).hexdigest()[:10]
      return f"{prefix}_{h}"
  ```
- [ ] `agpds_pipeline.py::_new_generation_id` 改调 `core.ids.generation_id`
- [ ] `AGPDSPipeline.__init__(seed: int = 42)`，把 seed 透传到 `DomainSampler(seed=)`、`FactTableSimulator(seed=)`、autofix 的 `base + attempt`
- [ ] `core/utils.py` — 至少删 `generate_unique_id` 与 `import random`；如果 Phase C 已删 `category_id`，整个文件 `git rm`
- [ ] 新增 `phase_0/tests/test_sampler_determinism.py`：两次 `DomainSampler(POOL, seed=42).sample(n=10)` 结果一致
- [ ] 新增 `tests/test_pipeline_determinism.py` smoke：两次 `AGPDSPipeline(seed=42).run_single(scenario_id="dom_001/k=0")` 的 `generation_id` 一致

> ⚠️ **本步会改 artifact 路径命名。** 若有正在用的 batch output 依赖具体 `generation_id`，先沟通。

**验证：**
```bash
pytest pipeline/                                                          # 全绿
grep -RIn 'random\.\(random\|sample\|choice\|uniform\|randint\)' pipeline/ --include="*.py" | grep -v 'tests/'   # 空
```

**Commit:** `fix(audit-B): seed DomainSampler, deterministic generation_id, drop global random`

---

### Phase C — Phase 1 收紧（中风险）

#### C.1 tier-aware `target_rows`

- [ ] `phase_1/scenario_contextualizer.py:41` — prompt 第 6 条改为：
  ```
  6. "target_rows": Row count for the fact table, derived from complexity tier:
     simple → 200-500, medium → 500-1000, complex → 1000-3000.
     Adjust within range based on temporal span and entity count.
  ```
- [ ] `phase_1/scenario_contextualizer.py:241` — `validate_output` 增加 `complexity_tier: str` 参数：
  ```python
  TIER_TARGET_ROWS = {
      "simple":  (200, 500),
      "medium":  (500, 1000),
      "complex": (1000, 3000),
  }
  low, high = TIER_TARGET_ROWS[complexity_tier]
  if not (low <= target_rows <= high):
      errors.append(f"target_rows out of tier range '{complexity_tier}': {target_rows} (expected {low}-{high})")
  ```
- [ ] `generate(domain_sample)` 把 `domain_sample["complexity_tier"]` 传给 `validate_output`
- [ ] one-shot example 把 `target_rows=900` 改到 complex 范围（≥1000）

#### C.2 删 `category_id` 桥接

- [ ] `phase_1/build_scenario_pool.py` — 删 `_category_id_for_topic`、删 `from pipeline.core.utils import META_CATEGORIES`、envelope 删 `"category_id"` 字段
- [ ] `grep -RIn 'category_id' pipeline/ --include="*.py" | grep -v tests/` 确认无活引用

#### C.3 类型化 schema

- [ ] 新建 `phase_1/types.py`：
  ```python
  from dataclasses import dataclass

  @dataclass(frozen=True)
  class Metric:
      name: str
      unit: str
      range: tuple[float, float]   # 必须 low < high

  @dataclass(frozen=True)
  class ScenarioContext:
      scenario_title: str
      data_context: str
      temporal_granularity: str    # ∈ VALID_GRANULARITIES
      key_entities: tuple[str, ...]
      key_metrics: tuple[Metric, ...]
      target_rows: int

  @dataclass(frozen=True)
  class ScenarioRecord:
      generation_id: str
      domain_id: str
      k: int
      scenario: ScenarioContext
  ```
- [ ] `scenario_contextualizer.py::generate` 把 LLM dict 解析为 `ScenarioContext` 后返回
- [ ] `build_scenario_pool.py` 写 jsonl 时序列化 `ScenarioRecord`
- [ ] Phase 2 reader 改为消费 `ScenarioContext`

#### C.4 其他清理

- [ ] `validate_output` 增加 `Metric.range` 校验（`low < high` 且都是数字）
- [ ] 删 `diversity_tracker` 字段、`_update_tracker` 方法、`__init__` 对应参数
- [ ] soft-failure 改为 `raise ValueError`，**不**把 `_validation_warnings` 塞回 dict

#### C.5 抽出 dedup 模块

- [ ] 新建 `phase_1/dedup.py`，把 `deduplicate_scenario_records` + `_record_groups` + `_overlap_index_pairs` 从 `scenario_contextualizer.py` 搬过来
- [ ] `phase_1/__init__.py` 重新组织 `__all__`

**验证：**
```bash
pytest pipeline/phase_1/                                                            # 全绿
grep -RIn 'category_id\|_validation_warnings\|diversity_tracker' pipeline/ --include="*.py" | grep -v tests/   # 空
```

**Commit:** `refactor(audit-C): tier-aware target_rows; type Phase 1 schemas; drop legacy category_id bridge`

---

### Phase D — 编排整合（中风险）

#### D.1 合并 `llm_client.py` fork

- [ ] 把 `TokenUsage`、`LLMResponse`、`_extract_token_usage`、`_generate_with_usage` 从 `phase_2/orchestration/llm_client.py` 搬到 `core/llm_client.py`
- [ ] `LLMClient.__init__` 增加 `track_tokens: bool = False`；True 时 `generate*` 返回 `LLMResponse(value, usage)`，False 时返回裸值（**默认行为不变**）
- [ ] 全仓库替换 import：
  ```bash
  grep -RIln 'from pipeline.phase_2.orchestration.llm_client import' pipeline/ --include="*.py" \
    | xargs sed -i 's|from pipeline.phase_2.orchestration.llm_client|from pipeline.core.llm_client|g'
  ```
- [ ] Phase 2 构造 LLMClient 处加 `track_tokens=True`
- [ ] `git rm pipeline/phase_2/orchestration/llm_client.py`

#### D.2 把 `run_retry_loop` 从 sandbox 迁到 retry_loop

- [ ] 把 `phase_2/orchestration/sandbox.py:637-864` 的 `run_retry_loop` + 仅它用的 helper 剪到 `retry_loop.py`
- [ ] `retry_loop.py::orchestrate` 改调本地 `run_retry_loop`，删 `from .sandbox import run_retry_loop`
- [ ] sandbox.py 仅留 `execute_in_sandbox` + `format_error_feedback` + `_TrackingSimulator` + 模块常量
- [ ] 检查体积：`wc -l sandbox.py` ≈ 340，`wc -l retry_loop.py` ≈ 400

#### D.3 改名 `code_validator.py` → `code_check.py`

- [ ] `git mv pipeline/phase_2/orchestration/code_validator.py pipeline/phase_2/orchestration/code_check.py`
- [ ] `grep -RIln 'code_validator' pipeline/ --include="*.py" | xargs sed -i 's/code_validator/code_check/g'`

#### D.4 声明 package 表面

- [ ] 新建 `pipeline/__init__.py`：
  ```python
  """ChartAgent pipeline (Phase 0–2 implementation)."""
  from pipeline.agpds_pipeline import AGPDSPipeline
  __all__ = ["AGPDSPipeline"]
  ```

#### D.5 给 `declare_orthogonal` 加 docstring

- [ ] `phase_2/engine/skeleton.py` 顶部 module docstring 增加：
  ```
  Note on declare_orthogonal:
      Cross-group orthogonality is consumed by the L1 chi-squared validator
      and Phase 3 view enumeration; it is a no-op for generation. The skeleton
      defaults to independent sampling for any cross-group pair not explicitly
      linked by add_group_dependency. This matches storyline §2.2:
      "Cross-group independence is opt-in, not default."
  ```

**验证：**
```bash
pytest pipeline/phase_2/tests/                                                # 全绿
python -c "from pipeline import AGPDSPipeline"                                # 成功
grep -RIn 'phase_2.orchestration.llm_client\|code_validator' pipeline/ --include="*.py"   # 空
```

**Commit:** `refactor(audit-D): collapse llm_client fork, move retry-loop out of sandbox, declare pipeline surface`

---

### Phase E — 文档（低风险）

- [ ] 完全重写 `README.md`：四 phase 概览 / 三个 CLI 入口（runner / generate / execute）/ 离线 build 步骤（`python pipeline/phase_0/build_domain_pool.py` 然后 `python pipeline/phase_1/build_scenario_pool.py`）/ `pipeline/` 目录树 / 引用 `storyline/data_generation/` 作为 canonical spec / 删除所有 legacy bar-chart 描述
- [ ] `mkdir -p docs/phase_2_history && git mv pipeline/phase_2/docs/* docs/phase_2_history/`（若 `module_interfaces.md` 是活的接口文档，留在 `pipeline/phase_2/INTERFACES.md`），然后 `rmdir pipeline/phase_2/docs`

**验证：**
```bash
pytest pipeline/                                                  # 全绿
ls docs/phase_2_history/ | wc -l                                  # ≈ 73-74
```

**Commit:** `docs(audit-E): rewrite top-level README; archive phase_2/docs`

---

### Phase F — Clean code 优化（可选，对应 §2）

> 只在 A–E 全做完且时间允许时考虑。每条独立，可单独 commit，无依赖关系。

- [ ] **F.1 抽 distributions 共享模块**（对应 §2.1）
  - 新建 `phase_2/engine/distributions.py`，集中 8 个分布族的 sample / pdf / cdf 构造函数
  - `engine/measures.py` import 它做采样
  - `validation/statistical.py` import 它做 KS 测试
  - 验证：原有 `pipeline/phase_2/tests/modular/test_engine_*` 与 `test_validation_statistical*` 全绿

- [ ] **F.2 抽 pattern handler 模板**（对应 §2.2）
  - `phase_2/engine/patterns.py` 顶部新增 `_apply_pattern_with_filter(rows, pattern_spec, mutator_fn)` helper
  - 6 种 pattern handler 改为只提供 `mutator_fn`
  - 验证：`test_engine_patterns*` 全绿

- [ ] **F.3 拆分 `phase_2/sdk/validation.py`**（对应 §2.4，**风险中等，需要重测全部 sdk modular 测试**）
  - 新建 `sdk/_validate_columns.py` / `_validate_groups.py` / `_validate_relationships.py` / `_validate_dag.py`
  - `sdk/validation.py` 只负责对外暴露与分发
  - 验证：`test_sdk_*` 全绿

- [ ] **F.4 顶层 CLI 命名**（对应 §2.5，**侵入性大，可选中的可选**）
  - `git mv agpds_runner.py pipeline/cli/run_all.py`、`agpds_generate.py → cli/generate.py`、`agpds_execute.py → cli/execute.py`
  - `agpds_pipeline.py` 改名 `pipeline/orchestrator.py`，class 改名 `Pipeline`
  - 更新 README + `pipeline/__init__.py` 导出
  - **风险：所有外部脚本调用都要改**——只在确定没人依赖旧名字时做

**Commit（每条独立）:** `refactor(audit-F.x): <主题>`

---

## 5. 完工后的最终验证（一次跑完）

```bash
# 1. 所有测试
pytest pipeline/

# 2. 确定性 smoke
python -c "
from pipeline import AGPDSPipeline
import pandas as pd
a = AGPDSPipeline(...).run_single(seed=42, scenario_id='dom_001/k=0')
b = AGPDSPipeline(...).run_single(seed=42, scenario_id='dom_001/k=0')
assert a.generation_id == b.generation_id, 'generation_id 不可复现'
assert pd.read_csv(a.master_table_path).equals(pd.read_csv(b.master_table_path)), 'master_table 不可复现'
print('确定性 OK')
"

# 3. 没有 legacy import / 死符号
grep -RIn 'from pipeline.legacy\|from pipeline.core.legacy\|from pipeline.adapters\|pipeline.schemas.master_table\|pipeline.core.master_table\|GeminiClient\|UndefinedPredictorError\|category_id' pipeline/ --include="*.py"

# 4. 没有全局 random（非测试代码）
grep -RIn 'random\.\(random\|sample\|choice\|uniform\|randint\)' pipeline/ --include="*.py" | grep -v 'tests/'

# 5. storyline ↔ code SDK 表面一致
python -c "
from pipeline.phase_2.sdk.simulator import FactTableSimulator
methods = {m for m in dir(FactTableSimulator) if not m.startswith('_')}
required = ['add_category','add_temporal','add_measure','add_measure_structural',
            'declare_orthogonal','add_group_dependency','inject_pattern','set_realism','generate']
for m in required:
    assert m in methods, f'{m} 不在 FactTableSimulator 里'
print('SDK 表面 OK')
"
```

---

## 6. 风险 / 待拍板 / 不动的范围

**实施前确认：**
- Phase B 改 `generation_id` 算法 → artifact 路径换名。若有正在用的 batch output 依赖具体字符串，先沟通。
- Phase F.4（CLI 改名）侵入性大，需确认无外部脚本依赖旧名。
- 仓库根 `chartGenerators/` / `multiChartGenerators/` / `templates/` / `metadata/` 等本次不动，等 Phase 3 启动再决定。
- `overlap_checker.py` 多 provider embeddings 支持作为 future work（已知限制，不阻塞）。

**保留不动：**
- Stage 1 / Stage 2 拆分（`agpds_generate.py` + `agpds_execute.py`）—— 优秀设计。
- `phase_2/pipeline.py` 的 Loop A / Loop B 切分。
- 三层 validator + autofix 架构。
- `phase_2/sdk/` 与 `phase_2/engine/` 的拆分（除非做 F.3）。
- `metadata/builder.py`（与 storyline §2.6 完全对齐）。
- 所有 `phase_2/tests/modular/` 测试。
- `pipeline/phase_2/docs/` 内容（仅迁位置，不改内容）。
