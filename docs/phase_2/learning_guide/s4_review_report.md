# S4 对抗性审查报告

**被审文档：** `s3_AGPDS_Phase2_Guide.md`
**审查日期：** 2026-04-05
**审查方法：** 逐断言核查——每个代码引用通过工具打开源文件验证，每个 SPEC_READY/NEEDS_CLAR 分类与 stage3 权威来源交叉比对

---

## 总结统计

| 指标 | 数值 |
|---|---|
| 代码行号引用总数（估计） | ~250 处 |
| 源码文件打开验证数 | 19 个文件 |
| SPEC_READY/NEEDS_CLAR 条目核查 | 80/80（stage3 全覆盖） |
| Cross-Module Blockers 核查 | 10/10（stage3 全覆盖） |

| 严重性 | 数量 |
|---|---|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 4 |
| LOW | 4 |
| **合计** | **9** |

| 审查类型 | 数量 |
|---|---|
| 代码引用错误 | 5 |
| 逻辑矛盾 / 状态标注偏差 | 2 |
| 重要遗漏 | 1 |
| 优先级分类编辑性偏差 | 1 |

### 整体评估

指南质量**优秀**。代码行号引用准确率约 97%（~250 处引用中仅 6 处有误，其中 1 处为真正的错误引用，5 处为范围偏差或 off-by-one）。SPEC_READY/NEEDS_CLAR 分类与 stage3 **完全一致**，未发现任何将 NEEDS_CLAR 项错误当作 SPEC_READY 深入讲解的情况。TODO 速查表覆盖了 stage3 全部 3 个 P0 项和 3 个 P1 跨模块阻塞项，并合理补充了模块级 NEEDS_CLAR 项。跨模块流追踪、Loop A/B 路径分析、规范偏差标注均经代码验证确认准确。

---

## 发现详情

### HIGH

---

#### H-1: `extract_formula_symbols()` 行号指向正则常量而非函数

- **位置：** §2.4 第 428 行 / §2.4 验证规则表第 515 行 / 附录 A 速查表第 2152 行
- **类型：** 代码引用错误
- **描述：** `extract_formula_symbols()` 的行号引用 `validation.py:49-50` 指向的是**正则常量 `IDENTIFIER_RE` 的定义**，而非函数本身。实际函数 `extract_formula_symbols()` 位于 `validation.py:554-561`（仅一行 `return set(IDENTIFIER_RE.findall(formula))`）。读者按行号跳转将找不到函数定义。
- **证据：**
  - `validation.py:49`: `# Regex pattern for extracting identifier symbols from arithmetic formulas.`
  - `validation.py:50`: `IDENTIFIER_RE: re.Pattern[str] = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")`
  - `validation.py:554`: `def extract_formula_symbols(formula: str) -> set[str]:`
  - `validation.py:561`: `    return set(IDENTIFIER_RE.findall(formula))`
- **建议修正：** 正文和验证规则表改为 `📍 [validation.py:554-561]`。附录 A 速查表已附 "(IDENTIFIER_RE)" 备注，可保留但同时补充函数行号。或采用双引用："`IDENTIFIER_RE` 📍 [validation.py:50] → `extract_formula_symbols()` 📍 [validation.py:554-561]"。

---

### MEDIUM

---

#### M-1: `validate_param_model()` 行号范围包含独立辅助函数

- **位置：** §2.2 第 412 行 / 附录 A 速查表第 2150 行
- **类型：** 代码引用错误
- **描述：** `validate_param_model()` 标注 `validation.py:294-399`，但函数本身仅占 294-327（34 行）。行 329-399 是独立定义的辅助函数 `validate_param_value()`。指南描述 "递归验证 param_model 结构" 虽然准确描述了整个验证流程（`validate_param_model` 调用 `validate_param_value`），但函数名 `validate_param_model()` 与行号范围 294-399 之间存在不匹配。
- **证据：**
  - `validation.py:294`: `def validate_param_model(`
  - `validation.py:327`: 函数最后一行（调用 `validate_param_value` 的循环）
  - `validation.py:329`: `def validate_param_value(` ← 独立函数定义
- **建议修正：** 两种方案任选：(A) 缩小范围为 `📍 [validation.py:294-327]`；(B) 保持 294-399 但改文字为 "`validate_param_model()` + `validate_param_value()` 📍 [validation.py:294-399]"。

#### M-2: code_validator.py 两个 AST Visitor 类行号范围错误且互相重叠

- **位置：** §6.6 第 1781-1782 行
- **类型：** 代码引用错误
- **描述：** 指南标注 `_GenerateCallVisitor` 为 `code_validator.py:159-169`、`_BuildFactTableVisitor` 为 `code_validator.py:171-193`。实际：`_GenerateCallVisitor` 延伸到 176 行（含 `generic_visit` 方法），`_BuildFactTableVisitor` 从 178 行开始。指南的两个范围在 171-176 之间存在虚假重叠。
- **证据：**
  - `code_validator.py:159`: `class _GenerateCallVisitor(ast.NodeVisitor):`
  - `code_validator.py:175-176`: `def generic_visit(self, node):` — 仍属于 `_GenerateCallVisitor`
  - `code_validator.py:178`: `class _BuildFactTableVisitor(ast.NodeVisitor):`
- **建议修正：** `_GenerateCallVisitor` 改为 `📍 [code_validator.py:159-176]`，`_BuildFactTableVisitor` 改为 `📍 [code_validator.py:178-193]`。

#### M-3: L3 已实现项统计与 stage3 SPEC_READY 计数不一致

- **位置：** §5.8 本章小结第 1585 行
- **类型：** 状态标注偏差 / 逻辑矛盾
- **描述：** 小结说 "L3 **2/4 项**检查已实现"，暗示 L3 共有 4 项。但 stage3 列出的 L3 验证 SPEC_READY 项实为 **3 项**（outlier_entity、trend_break、ranking_reversal），另有 2 项 NEEDS_CLAR（dominance_shift — stage3 M5 NEEDS_CLAR #4；convergence + seasonal_anomaly — stage3 M5 NEEDS_CLAR #5）。正确表述应为 "L3 2/3 项 SPEC_READY 已实现"。指南在 L3 缺失项表（line 1446）正确区分了 "SPEC_READY" 和 "🚧 P1" 状态，但小结中的汇总数字模糊了这一区分。
- **证据：**
  - stage3 M5 SPEC_READY #10: outlier entity ✅
  - stage3 M5 SPEC_READY #11: trend break ✅
  - stage3 M5 SPEC_READY #12: ranking reversal — `means[m1].rank().corr(means[m2].rank()) < 0` ← **SPEC_READY 但代码缺失**
  - stage3 M5 NEEDS_CLAR #4: dominance_shift
  - stage3 M5 NEEDS_CLAR #5: convergence + seasonal_anomaly
- **建议修正：** 改为 "L3 2/3 项 SPEC_READY 检查已实现（outlier_entity ✅, trend_break ✅, ranking_reversal ❌ 代码缺失），另有 2 项 NEEDS_CLAR 被静默跳过"。

#### M-4: `ranking_reversal` 在 TODO 速查表中缺少独立条目

- **位置：** 附录 B TODO 速查表
- **类型：** 重要遗漏
- **描述：** `ranking_reversal` 验证在 stage3 中为 **SPEC_READY**（有完整伪代码），但代码完全缺失（`_run_l3()` 的 dispatch 不包含此类型）。指南在正文 L3 缺失项表（line 1446）正确标注了 "SPEC_READY（有伪代码）| ❌ 完全缺失"，但在附录 B TODO 速查表中**未给予独立条目**。读者查阅速查表时无法发现这一 SPEC_READY 遗漏项。P1-7 仅列出 `dominance_shift`（NEEDS_CLAR），而 ranking_reversal（SPEC_READY but unimplemented）本质上是更高优先级的实现缺口。
- **证据：** stage3 M5 SPEC_READY #12 提供完整伪代码：`means[m1].rank().corr(means[m2].rank()) < 0`。附录 B 无对应条目。
- **建议修正：** 在 P1 部分添加独立条目，例如：`"ranking_reversal 验证 | SPEC_READY 未实现 | M5 pattern_checks.py | — | §2.9 L3 有完整伪代码：负秩相关 | ❌ 完全缺失"`。与 NEEDS_CLAR 项区别标注。

---

### LOW

---

#### L-1: 优先级标签来源未标注

- **位置：** 附录 B TODO 速查表 P1 部分（P1-4 至 P1-8）
- **类型：** 逻辑一致性
- **描述：** P1-4（build_fact_table 签名）、P1-5（noise_sigma 除零）、P1-6（KS-test 枚举）、P1-7（dominance_shift）、P1-8（convergence/seasonal_anomaly）在 stage3 中仅作为**模块级 NEEDS_CLAR 项**列出，无显式优先级标签。Stage3 的 P0/P1/P2/P3 标签仅用于 Cross-Module Blockers 表（10 项）。指南将这些模块级项赋予 P1 是合理的编辑决策，但读者可能误以为这些优先级来自 stage3 权威来源。
- **证据：** stage3 Cross-Module Blockers 表仅含 3 个 P1 项（mixture param、4 pattern types、sandbox semantics）。P1-4 至 P1-8 的 P1 标签无 stage3 对应。
- **建议修正：** 在附录 B 开头添加说明："P0–P1 优先级中，P0-1 至 P0-3 和 P1-1 至 P1-3 来自 stage3 Cross-Module Blockers 表。P1-4 至 P1-8 为本指南根据影响评估赋予的编辑性优先级。"

#### L-2: `is_group_root()` 行号 off-by-one

- **位置：** §2.5 第 535 行 / 附录 A 速查表第 2160 行
- **类型：** 代码引用错误
- **严重性：** LOW
- **描述：** `is_group_root()` 标注 `groups.py:98-122`，实际函数 return 语句在第 123 行。
- **证据：** `groups.py:123` 为 `return column_name == group.root`
- **建议修正：** 改为 `groups.py:98-123`。

#### L-3: M4 `_assert_metadata_consistency()` 行为偏差已正确标注

- **位置：** §3.3 第 783 行
- **类型：** 规范偏差（确认性发现）
- **描述：** 指南正确标注了 docstring 声称 `raises ValueError`（builder.py:209）与实际使用 `logger.warning` 不中断执行之间的偏差。此处仅确认核实，无需修改指南。
- **证据：** builder.py:209 docstring: "Raises: ValueError:"；实际实现 builder.py:215-251 全部使用 `logger.warning()` 无 `raise`。
- **建议修正：** 指南无需修改。建议在代码中修正 docstring 或改 warning 为 raise。

#### L-4: L1-4 正文未附函数名

- **位置：** §5.2 L1-4 标题区域（line 1346-1348）
- **类型：** 代码引用错误（轻微）
- **描述：** L1-4 "Measure DAG Acyclicity" 使用描述性标题和正确的行号 `structural.py:180-209`，但正文中未附函数名。附录 A 速查表（line 2203）正确使用 `check_measure_dag_acyclic()`。正文补充函数名可提高可导航性。
- **证据：** structural.py:180 定义 `def check_measure_dag_acyclic(`。
- **建议修正：** 在正文标题后补充函数名，如 "L1-4: Measure DAG Acyclicity — `check_measure_dag_acyclic()` ✅"。

---

## 核查通过的关键断言（确认正确）

以下核查项均已通过工具打开源文件逐行验证，确认指南描述准确：

1. **types.py 全部 ~30 处行号引用**精确正确（DimensionGroup、OrthogonalPair、GroupDependency、Check、ValidationReport、PatternSpec、RealismConfig、DeclarationStore、SandboxResult、RetryLoopResult）
2. **exceptions.py 全部 ~15 处行号引用**精确正确（全部 11 个异常类 + SkipResult + 基类 SimulatorError + 构造器示例）
3. **M1 SDK 模块 ~60 处引用**中 58 处正确（simulator.py、columns.py、relationships.py、groups.py、dag.py 全部函数边界、验证链、注册行为、DAG 操作）
4. **M4 builder.py 全部 ~20 处引用**精确正确（7 个键组装、5 种列类型分支、后置一致性校验 4 项检查）
5. **M2 engine 模块 ~50 处引用**全部正确（generator.py、skeleton.py、measures.py、postprocess.py、patterns.py、realism.py — 含各阶段函数、RNG 传递、DAG 排序、模式注入算法、realism 扰动）
6. **M5 validation 模块 ~55 处引用**全部正确（validator.py 编排器、structural.py 4 项 L1 检查、statistical.py 3 项 stub、pattern_checks.py 2 项 L3 检查 + 辅助函数、autofix.py 3 项策略函数 + glob 分发表）
7. **M3 orchestration 模块 ~50 处引用**全部正确（prompt.py 模板 + HC1-HC9 + 渲染器、sandbox.py 安全内置列表 + namespace 构建 + 线程执行 + 返回值验证 + 反馈格式化 + 完整重试循环含每行精确引用、code_validator.py 围栏剥离 + AST 检查、retry_loop.py stub、pipeline.py 骨架）
8. **全部 5 个模块的实现率**与 stage3 Executive Summary 精确一致
9. **stage3 全部 36 项 NEEDS_CLAR**在各章 TODO 地图中均有覆盖（含 4 项标注为"已自行解决"的 M1 项）
10. **stage3 全部 10 个 Cross-Module Blockers** 在附录 B 中均有覆盖
11. **跨模块流描述**（§7 全部 9 条传递）与代码实际行为一致
12. **Loop A / Loop B 路径追踪**（§7.6-7.7）与代码实际行为一致
13. **规范偏差标注**（DeclarationStore 未使用、orthogonal_pairs 丢失、对话累积缺失、M4 warning vs raise 等）全部经代码验证确认

---

## 推荐修正优先级

| 优先级 | 发现编号 | 修正动作 | 预计工作量 |
|---|---|---|---|
| 1 | H-1 | 修正 `extract_formula_symbols()` 行号：49-50 → 554-561 | 3 处替换 |
| 2 | M-3 | 修正 §5.8 小结 "L3 2/4" → "L3 2/3 SPEC_READY" | 1 句改写 |
| 3 | M-4 | 附录 B 添加 `ranking_reversal` 独立条目 | 1 行新增 |
| 4 | M-2 | 修正 code_validator.py 两个 Visitor 类行号 | 2 处替换 |
| 5 | M-1 | 修正或标注 `validate_param_model()` 行号范围 | 1 处修改 |
| 6 | L-1 | 附录 B 添加优先级来源说明 | 1 句新增 |
| 7 | L-2 | 修正 `is_group_root()` 行号 122→123 | 2 处替换 |
| 8 | L-4 | §5.2 L1-4 补充函数名 | 可选 |
| 9 | L-3 | 无需修改指南 | — |
