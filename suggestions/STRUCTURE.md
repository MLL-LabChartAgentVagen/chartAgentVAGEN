# 当前 Code Structure 与重构建议

> 浏览每个模块当前在做什么 + 是否需要改动。改动方向 → [PLAN.md](PLAN.md) 对应条目。
>
> 图例：✅ 保留不动 · ✏️ 修改 · ➕ 新建 · 🗑️ 删除

---

## pipeline/ 总览

```
pipeline/
├── phase_0/         Domain pool（一次性离线，LLM 出 ~210 个细粒度子主题）
├── phase_1/         Scenario 生成（每个 domain 出一个真实场景）
├── phase_2/         Code-as-DGP（LLM 写脚本 + 引擎执行 + 三层校验）
│   ├── sdk/         LLM 调的 SDK 表面（FactTableSimulator）
│   ├── engine/      确定性数据生成引擎
│   ├── validation/  三层 validator + autofix
│   ├── orchestration/  prompt + sandbox + retry loop
│   └── metadata/    生成 schema_metadata（Phase 2 → Phase 3 契约）
├── core/            跨 phase 共享：LLM client + 工具
├── schemas/         🗑️ 死目录（仅一个字节级 dup of legacy）
├── adapters/        🗑️ 已 staged for delete
├── legacy/          🗑️ 已 staged for delete
└── agpds_*.py       4 个顶层入口（Pipeline class + 3 个 CLI）
```

---

## phase_0/ — Domain Pool

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `build_domain_pool.py` | 178 | CLI 入口：读 `taxonomy_seed.json` → 调 LLM 生成 sub-topic → 缓存到 `domain_pool.json` | ✅ 保留 |
| `domain_pool.py` | 405 | `DomainPool`（builder + 缓存） + `DomainSampler`（无放回分层抽样） | ✏️ `DomainSampler` 加 seed 参数（PLAN 1.1）；删 `SEED_TOPICS` 死常量（PLAN 1.14） |
| `overlap_checker.py` | 47 | embedding cosine 相似度 → 找重复对，被 Phase 0/1 共用 | ✏️ 加 API key 显式参数（PLAN 1.14） |
| `taxonomy_seed.json` | — | 30 个 super-topic 种子 | ✅ |
| `domain_pool.json` | — | 缓存的 ~210 个 sub-topic | ✅ |
| `tests/` | — | 现有测试 | ✅ + ➕ `test_sampler_determinism.py`（PLAN B） |

**整体评价：** 模块化清晰。唯一硬伤是 `DomainSampler` 用了全局 `random` 破坏可复现性。

---

## phase_1/ — Scenario Contextualization

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `scenario_contextualizer.py` | 383 | `ScenarioContextualizer` class（prompt + 调 LLM + 校验 + retry） + `deduplicate_scenario_records` 一族去重函数 | ✏️ tier-aware `target_rows`（PLAN 1.6）；删 `diversity_tracker` / `_validation_warnings` 泄漏（PLAN 1.9）；soft-failure 改 raise（PLAN 1.9）；删简化版 `deduplicate_scenarios`（PLAN 1.18）；**clean-code 建议：把去重抽到独立文件 §2.3** |
| `build_scenario_pool.py` | 331 | 离线 CLI：并行 + 断点续跑生成 `scenario_pool.jsonl` | ✏️ 删 `category_id` 字段 + `_category_id_for_topic`（PLAN 1.8） |
| `__init__.py` | 21 | 包公共表面 | ✏️ 移除 `deduplicate_scenarios` 导出（PLAN 1.17） |
| `types.py` | — | （不存在） | ➕ 新建：`Metric` / `ScenarioContext` / `ScenarioRecord` dataclass（PLAN 1.10） |
| `dedup.py` | — | （不存在） | ➕ 新建：把去重函数从 `scenario_contextualizer.py` 搬过来（PLAN §2.3） |
| `tests/` | — | 现有测试 | ✅ + ➕ tier-range 测试（PLAN C 验证） |

**整体评价：** 单文件 `scenario_contextualizer.py` 干两件事（生成 + 去重），适合拆。`category_id` 是 legacy 桥接，与新 storyline 无关。

---

## phase_2/ — Agentic Data Simulator

### phase_2/ 顶层

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `pipeline.py` | 277 | `run_phase2` / `run_loop_a` / `run_loop_b_from_declarations` —— Phase 2 的对外入口，桥接 Loop A / Loop B | ✅ |
| `types.py` | 496 | 跨 sdk / engine / validation 共用的 dataclass（`ColumnSpec` / `MeasureSpec` / `OrthogonalPair` / `GroupDependency` 等） | ✅ |
| `exceptions.py` | 387 | 13 种 typed exception，sandbox 失败时反馈给 LLM | ✏️ 删 `UndefinedPredictorError`（PLAN 1.15） |
| `serialization.py` | 68 | declarations 的 dump / load，支持 Stage 2 回放 | ✅ |
| `__init__.py` | 120 | 包公共表面 | ✅ |

### phase_2/sdk/ — LLM 调的 SDK 表面

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `simulator.py` | 198 | `FactTableSimulator` 主 class —— 9 个对外方法 + `generate()` | ✅ |
| `columns.py` | 345 | `add_category` / `add_temporal` / `add_measure` / `add_measure_structural` 四个声明器实现 | ✅ |
| `groups.py` | 142 | dimension group 注册 + 单 root 强制 | ✅ |
| `relationships.py` | 487 | `declare_orthogonal` / `add_group_dependency` / `inject_pattern` / `set_realism` 实现 | ✅ |
| `dag.py` | 451 | measure DAG 构建 + 环检测 + 拓扑排序 | ✅ |
| `validation.py` | 693 | 所有声明期参数校验（columns / groups / relationships / DAG）的总入口 | ✅；**clean-code 建议：按主题拆分 §2.4** |
| `__init__.py` | 9 | re-export `FactTableSimulator` | ✅ |

**整体评价：** 与 storyline §2.1 完全对齐。`validation.py` 单文件 693 LoC 略显笨重，可选拆分。

### phase_2/engine/ — 确定性引擎

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `generator.py` | 133 | `α → β → γ → δ → τ` 顶层编排，单一 seeded `rng` | ✅ |
| `skeleton.py` | 424 | α 阶段：非 measure 列按 column DAG 拓扑顺序生成（roots / 子类 / temporal + derived） | ✏️ 顶部加 declare_orthogonal no-op 注释（PLAN 1.13） |
| `measures.py` | 608 | β 阶段：8 种分布族采样 + structural formula 评估 + mixture handler | ✅；**clean-code 建议：与 validation/statistical.py 共享 distributions §2.1** |
| `patterns.py` | 760 | γ 阶段：6 种 pattern injection（outlier_entity / trend_break / ...） | ✅；**clean-code 建议：抽 _apply_pattern_with_filter helper §2.2** |
| `realism.py` | 259 | δ 阶段（可选）：missing / dirty / censoring 注入 | ✅ |
| `postprocess.py` | 82 | τ 阶段：类型转换 + 列序 + 重置索引 | ✅ |
| `__init__.py` | 6 | re-export | ✅ |

**整体评价：** 管线 + 各阶段语义都正确。两个文件 (`measures.py` / `patterns.py`) 偏大，主要因为每个 family / pattern 类型一个 handler；可选 clean-code 改进通过共享 helper 减重。

### phase_2/validation/ — 三层 validator + autofix

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `validator.py` | 224 | `SchemaAwareValidator` —— 顶层 dispatch L1/L2/L3 | ✅ |
| `structural.py` | 315 | L1：row count / cardinality / marginal weights / orthogonal chi-square / DAG 无环 / measure 有限 | ✅ |
| `statistical.py` | 653 | L2：stochastic measure 按 (predictor cells) KS / structural 残差 mean+std / group dependency 转移 | ✅；**clean-code 建议：与 engine/measures.py 共享 distributions §2.1** |
| `pattern_checks.py` | 585 | L3：6 种 pattern 各一个 checker | ✅ |
| `autofix.py` | 359 | AUTO_FIX 策略 + name-prefix dispatch（`ks_*` / `outlier_*` / `trend_*` / `orthogonal_*`） | ✅ |
| `__init__.py` | 6 | re-export | ✅ |

**整体评价：** 与 storyline §2.9 完全对齐。`statistical.py` 偏大主要因为 per-family CDF 重新实现；与 engine 共享后可减重。

### phase_2/orchestration/ — Loop A 编排

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `prompt.py` | 309 | system + user prompt 构造，含 one-shot example | ✅ |
| `llm_client.py` | 476 | **🗑️ fork** of `pipeline/core/llm_client.py`，多了 `TokenUsage` / `LLMResponse` / `_generate_with_usage` | 🗑️ 合并进 `core/llm_client.py` 加 `track_tokens` 标志（PLAN 1.7） |
| `code_validator.py` | 309 | pre-sandbox AST 检查（语法 + `def build_fact_table` + `.generate()`） | ✏️ 改名 `code_check.py`（PLAN 1.11） |
| `sandbox.py` | 864 | 三件事混在一起：(a) `execute_in_sandbox` 224 LoC、(b) `format_error_feedback` 117 LoC、(c) `run_retry_loop` 228 LoC（**该归 retry_loop 管**） | ✏️ 把 `run_retry_loop` 迁到 `retry_loop.py`，sandbox 缩到 ~340 LoC（PLAN 1.4） |
| `retry_loop.py` | 175 | 现在只是 `sandbox.run_retry_loop` 的薄包装 + scenario context 序列化 + 生成函数包装 | ✏️ 接收 `run_retry_loop` 后扩到 ~400 LoC，成为 Loop A 真正归宿（PLAN 1.4） |
| `__init__.py` | 6 | re-export | ✅ |

**整体评价：** **是 Phase 2 整洁度最差的子目录。** sandbox 越权 + llm_client fork + code_validator 命名误导。Phase D 是重点。

### phase_2/metadata/ — schema metadata builder

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `builder.py` | 251 | 把 SDK 收集到的 declarations 渲染成 `schema_metadata` dict（与 storyline §2.6 七个键对齐 + `measure_dag_order` + `time` group） | ✅ |
| `__init__.py` | 6 | re-export | ✅ |

**整体评价：** 与 storyline 对齐，干净。

### phase_2/docs/ — 设计 history

74 个 .md：design 决策、deep_dive、stub 分析、Claude 对话存档。**和当前活代码无关。** 处置：`git mv` 到 `docs/phase_2_history/`（PLAN 1.19）。

### phase_2/tests/ — 测试

`tests/modular/` 下约 18 个 module-level 单测，覆盖 sdk / engine / validation 主要路径。**保留不动。**

---

## core/ — 跨 phase 共享基础设施

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `llm_client.py` | 406 | 多 provider LLM client（OpenAI / Gemini-native / Azure / Custom），带 `generate / generate_json / generate_code` | ✏️ 接收 token tracking 合并；删 `GeminiClient` 别名（PLAN 1.7 / 1.16） |
| `utils.py` | 92 | `META_CATEGORIES` 30-cat enum + `generate_unique_id`（不可复现） | 🗑️ Phase B 删 `generate_unique_id`；Phase C 删 `META_CATEGORIES` → 全空就整个 `git rm`（PLAN 1.2 / 1.8） |
| `master_table.py` | 146 | 🗑️ legacy bar-chart drawing adapter，与 `pipeline/core/legacy/master_table.py` 字节级相同；Phase 0–2 无人 import | 🗑️ `git rm`（PLAN 1.3） |
| `ids.py` | — | （不存在） | ➕ 新建：`generation_id(seed, scenario_id)` 用 `hashlib.sha256`（PLAN 1.2） |
| `__init__.py` | 44 | re-export | ✅（Phase B/C 后简化） |
| `tests/` | — | `test_core_imports.py` | ✅ |

**整体评价：** 完工后 `core/` 只剩 `llm_client.py` + `ids.py`，是好事——是"少量真正跨 phase 共享的基础设施"。**别为了凑内容塞东西。**

---

## schemas/ — 死目录

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `master_table.py` | 146 | 🗑️ 与 `core/master_table.py` 字节级相同的 legacy adapter | 🗑️ `git rm`（PLAN 1.3） |
| `__init__.py` | 3 | 仅 import 上面那个 | 🗑️ `git rm` 后整个目录 `rmdir` |

---

## adapters/ — 已 staged for delete

`pipeline/adapters/basic_operators.py` (282 LoC) + `__init__.py`：RelationalOperator stub（Filter / Project / GroupBy / Aggregate / Sort / Limit / Chain）。是 Phase 3 SQL projection 的前身，但当前空 stub 没人用。处置：🗑️ `git rm`（PLAN 1.3）。

---

## legacy/ + core/legacy/ — 已 staged for delete

约 9 kLoC 的 pre-storyline 代码：旧 `generation_pipeline.py` (2,157 LoC) + 旧 `chart_qa_pipeline.py` + 旧 `phase_2_old/` (FactTableSimulator v1) + 各种 v1 模块。**Phase 0–2 零依赖。** 处置：🗑️ `git rm -r`（PLAN 1.3）。

---

## 顶层 agpds_*.py + 其他

| 文件 | 行 | 功能 | 处置 |
|---|---:|---|---|
| `agpds_pipeline.py` | 251 | `AGPDSPipeline` class —— 跨 phase 编排（Stage 1 = generate_artifacts，Stage 2 = execute_artifact） | ✅；可选改名（PLAN §2.5） |
| `agpds_runner.py` | 290 | 端到端 CLI：`run_single` 一次跑完 0→1→2 | ✅ |
| `agpds_generate.py` | 224 | Stage 1 CLI：只跑到 declarations，便于离线回放 | ✅ |
| `agpds_execute.py` | 208 | Stage 2 CLI：从 declarations 跑确定性 Loop B，可 `ProcessPoolExecutor` 并行 | ✅ |
| `evaluation_pipeline.py` / `evaluation_runner.py` | 1,793 | Phase 4 评估流程 | ✅ 本次不动（Phase 3+） |
| `pipeline/__init__.py` | — | （不存在） | ➕ 新建：re-export `AGPDSPipeline`（PLAN 1.12） |

**整体评价：** Stage 1 / Stage 2 拆分非常漂亮 —— LLM 调用与确定性回放分离，回放可并行。**核心架构保留。**

---

## 重构后预期形态（一句话总结）

- **删 ~10 kLoC dead code**（legacy / 双胞胎 / 死异常）→ 仓库瘦身、目录树清晰。
- **`DomainSampler` + `generation_id` 双确定性修复** → CLAUDE.md §25 合规、artifact 路径稳定。
- **Phase 1 类型化 + tier-aware target_rows** → 跨模块边界都是 `@dataclass`、与 storyline §1.2 对齐。
- **`sandbox.py` 拆开 + `llm_client.py` 合并** → 一文件一职责。
- **可选 Phase F**：CDF 共享、pattern helper、sdk/validation 拆分 → 进一步消除重复。
- **不动**：Stage 1/2 拆分、Loop A/B 拆分、三层 validator + autofix、SDK 与 engine 的边界、`metadata/builder.py`、所有 modular 测试。
