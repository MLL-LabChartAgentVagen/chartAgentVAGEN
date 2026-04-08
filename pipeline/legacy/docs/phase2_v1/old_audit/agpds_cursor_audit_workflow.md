# AGPDS Pipeline — Cursor Agent Audit & Walkthrough Workflow

> **适用环境:** Cursor Composer (Agent Mode)
> **前置条件:** 项目根目录中存有 AGPDS 框架描述 markdowns + 你的实现代码
> **工作流逻辑:** 侦察 → 静态审计 → 规范对齐 → 代码讲解 → 综合报告
> **规则:** 每个阶段完成后，在 Cursor 中开启新 Composer 会话，粘贴下一阶段提示词

---

## 阶段总览

| 阶段 | 名称 | 目标 | 产出文件 |
|------|------|------|----------|
| Phase 0 | **侦察** | 建立代码库地图 | `audit/00_codebase_map.md` |
| Phase 1 | **静态正确性审计** | 验证代码能否产生预期输出 | `audit/01_correctness_audit.md` |
| Phase 2 | **AGPDS 规范对齐审计** | 与框架设计逐项比对 | `audit/02_spec_alignment.md` |
| Phase 3 | **代码讲解** | 深度理解每个模块的机制 | `audit/03_code_walkthrough.md` |
| Phase 4 | **综合报告** | 汇总问题 + 行动计划 | `audit/04_final_report.md` |

---

## Phase 0 — 侦察：建立代码库地图

**目标:** 在不进行任何评判的情况下，完整地摸清代码库的结构、文件职责和关键接口。

```
You are a senior ML systems architect performing a codebase reconnaissance for an
Atomic-Grain Programmatic Data Synthesis (AGPDS) pipeline. Your sole job in this
phase is to map — not judge.

<operating_rules>
1. READ ONLY: Do not modify any files. Do not execute any code.
2. EVIDENCE-BASED: Every claim must cite a file path and line number range.
3. NO JUDGMENT: Record what exists, not what should exist.
4. COMPLETENESS: Surface every .py file, config file, and markdown in the project.
</operating_rules>

<task>
Perform the following reconnaissance steps in strict sequence.

## Step 1 — File Tree
Run `find . -type f \( -name "*.py" -o -name "*.json" -o -name "*.yaml" -o -name "*.md" \) | sort`
and reproduce the full output. Group by directory.

## Step 2 — Module Role Table
For each Python file found, read the top-level docstring + class/function signatures
(first ~30 lines are sufficient). Produce a table:

| File Path | Role (1 sentence) | Key Classes/Functions | External Dependencies (imports) |
|-----------|-------------------|----------------------|---------------------------------|

## Step 3 — Data Flow Sketch
Trace the end-to-end data flow:
- What is the entry point (main script / CLI)?
- What are the intermediate data structures (dicts, dataclasses, pandas DataFrames)?
- What does each stage consume and produce?
- What is the final output format and destination?

Present the data flow as a numbered pipeline:
  [1] input → [Module A] → [artifact X] → [2] [Module B] → ... → [N] final output

## Step 4 — Framework Markdown Inventory
List every AGPDS framework markdown file in the project. For each, record:
- Filename and path
- A 1-sentence description of its content (from its title/introduction)

## Step 5 — Write Output
Write the complete output of Steps 1–4 to `audit/00_codebase_map.md`.
Include YAML front-matter:
  title: "AGPDS Codebase Reconnaissance"
  date: <today>
  generated_by: "Cursor Agent — Phase 0"

After writing, confirm: [WRITE CONFIRMED] <path> | <line count>
</task>
```

---

## Phase 1 — 静态正确性审计

**目标:** 在不运行代码的情况下，通过静态分析判断代码能否正确产生 master table 和 schema 输出。依赖 Phase 0 产出的 `audit/00_codebase_map.md`。

```
You are a senior ML data engineering auditor. You have read-only access to the
codebase and the file `audit/00_codebase_map.md` from a prior reconnaissance phase.
Your job is static correctness verification — find bugs and logic errors by reading
the code, not by running it.

<operating_rules>
1. CITE LINE NUMBERS: Every finding must reference file:line_start-line_end.
2. CLASSIFY FINDINGS: Use CRITICAL / WARNING / NOTE severity labels.
3. NO SPECULATION: If you cannot determine correctness without execution, mark
   it [NEEDS RUNTIME VERIFICATION] and move on.
4. EXTRACT BEFORE ANALYZE: Quote the relevant code snippet before commenting on it.
</operating_rules>

<context>
This pipeline implements the AGPDS framework (Atomic-Grain Programmatic Data
Synthesis), Phases 0–2. The expected outputs are:
  - A master CSV/DataFrame table (structured tabular data)
  - A schema_metadata dict or JSON (column definitions, data types, constraints)

These two artifacts must together be sufficient to drive Phase 3 (chart generation)
without additional inputs.
</context>

<task>
Perform the following audits in strict sequence.

## Audit 1 — Output Contract Verification
For the module responsible for producing the master table and schema:
  a. Identify exactly where in the code the output is written/returned.
     → Cite file:line for each output write operation.
  b. Verify the output format matches the expected schema:
     - Master table: correct column names, data types, no missing values in
       required columns, correct row structure
     - Schema metadata: all required keys present, types correctly annotated
  c. For each output field, verdict: CORRECT / INCORRECT / AMBIGUOUS

## Audit 2 — Logic Correctness Check
For each major processing function in the pipeline, check:
  a. Are there off-by-one errors, incorrect indexing, or wrong variable references?
  b. Are conditional branches (if/else, try/except) correctly structured?
  c. Is there any dead code that appears to be intended logic?
  d. Are LLM API calls structured correctly (correct message format, temperature,
     model name, response parsing)?

## Audit 3 — Data Integrity Check
  a. Are there any places where data could silently be dropped or overwritten?
  b. Is there defensive handling for LLM API failures (retry logic, fallback values)?
  c. Are random seeds set where reproducibility is expected?

## Audit 4 — Dependency & Import Check
  a. Are all imported modules used?
  b. Are there any circular imports or import-time side effects?
  c. Are external library calls using the correct API signatures?
     (Check especially: LangGraph, LangChain, pandas, any LLM SDK)

## Summary Table
| Audit ID | File:Lines | Severity | Description | Recommended Fix |
|----------|------------|----------|-------------|-----------------|

## Write Output
Write the full audit to `audit/01_correctness_audit.md`.
YAML front-matter: title, date, severity_counts (CRITICAL/WARNING/NOTE counts).
Confirm: [WRITE CONFIRMED] <path> | <line count>
</task>
```

---

## Phase 2 — AGPDS 规范对齐审计

**目标:** 以 AGPDS 框架 markdowns 为权威参考，逐条检查实现是否忠实于设计方案。依赖 Phase 0 和 Phase 1 的输出文件。

```
You are a senior ML research architect acting as a specification compliance auditor.
You have access to the AGPDS framework design documents (markdowns identified in
`audit/00_codebase_map.md`) and the correctness audit in `audit/01_correctness_audit.md`.

<operating_rules>
1. SPEC IS LAW: The framework markdowns are the ground truth. Your implementation
   is the subject under review. Never invert this relationship.
2. CITE BOTH SIDES: Every divergence must cite (a) the spec file+section and
   (b) the implementation file+line.
3. DISTINGUISH INTENTIONAL vs ACCIDENTAL: If a divergence could be a deliberate
   simplification, flag it as [POSSIBLY INTENTIONAL] rather than a hard error.
4. EXTRACT BEFORE COMPARE: Quote the spec requirement verbatim before comparing.
</operating_rules>

<task>
Perform the following compliance checks in strict sequence.

## Check 1 — Framework Design Extraction
Read every AGPDS markdown file. Extract and list:
  - The officially named pipeline stages (e.g., Phase 0, Phase 1, Phase 2...)
  - The "atomic grain" concept definition (what constitutes one atomic unit?)
  - The required input/output contract for each stage
  - Any explicitly stated design constraints or anti-patterns

Present as a numbered list with citations: [Source: filename.md § Section Name]

## Check 2 — Stage-by-Stage Compliance Matrix
For each framework-defined stage, assess the implementation:

| Stage | Spec Requirement | Implementation | Status | Gap Description |
|-------|-----------------|----------------|--------|-----------------|

Status options: ✅ COMPLIANT / ⚠️ PARTIAL / ❌ MISSING / 🔍 UNVERIFIABLE

## Check 3 — Atomic Grain Integrity
The core AGPDS principle is "atomic grain" — each synthesis unit should be
maximally decomposed. Verify:
  a. Does the implementation decompose data at the grain level specified in the spec?
  b. Are there any places where multiple grains are conflated into one operation?
  c. Does the programmatic synthesis step match the spec's described approach?

## Check 4 — Naming & Structural Conventions
  a. Do module names, class names, and variable names follow the framework's
     terminology? List any deviations.
  b. Is the directory/file structure consistent with any structure implied by the spec?

## Check 5 — Phase 3 Readiness Gate
Based on the spec's Phase 3 requirements:
  a. List every input field Phase 3 requires (cite the spec source).
  b. For each, check if Phases 0–2 produce it.
  c. Final verdict: READY FOR PHASE 3 / BLOCKED — with a list of blockers if blocked.

## Write Output
Write to `audit/02_spec_alignment.md`.
YAML front-matter: title, date, compliance_summary (counts of ✅/⚠️/❌/🔍),
phase3_readiness_verdict.
Confirm: [WRITE CONFIRMED] <path> | <line count>
</task>
```

---

## Phase 3 — 代码讲解

**目标:** 以教学为目的，深度讲解代码的工作机制。重点解释"为什么这样设计"，而非仅仅描述"做了什么"。适合作者自己留存的理解文档。

```
You are a senior ML educator and systems architect. Your audience is the author
of this code — an undergraduate researcher who wants to deeply understand their
own implementation, not just what it does but WHY it does it that way.

Your tone: precise but accessible. Use analogies when they illuminate. Avoid
jargon without definition. Think of this as writing a "guided tour" of the code
for the author to refer back to months later.

<operating_rules>
1. EXPLAIN INTENT: For every non-trivial design choice, explain the reasoning
   behind it, even if that reasoning is implicit in the code.
2. CITE LINE NUMBERS: All code references must include file:line.
3. CONNECT TO AGPDS: Where relevant, connect code behavior to the AGPDS
   framework concept it implements. Flag disconnections with [NOTE: spec divergence].
4. HIGHLIGHT SUBTLETIES: Explicitly call out any code that could confuse a
   reader or that has non-obvious behavior.
</operating_rules>

<context>
Read `audit/00_codebase_map.md`, `audit/01_correctness_audit.md`, and
`audit/02_spec_alignment.md` before starting. These provide the full picture
of what the code does and where it diverges from spec.
</context>

<task>
Produce a module-by-module walkthrough. For each Python module in the pipeline:

## Module Walkthrough Template

### [Module Name] (`file/path.py`)

**Purpose in the Pipeline**
1–2 sentences on this module's role in the end-to-end flow.

**Key Design Decisions**
For each significant class or function (cite file:line):
  - What does it do (inputs → transformation → outputs)?
  - Why is it structured this way? (What problem does this design solve?)
  - What assumptions does it make about its inputs?
  - What could go wrong if those assumptions are violated?

**Data Structures Explained**
For each non-trivial data structure (dict schema, DataFrame shape, dataclass):
  - What does each field/column represent?
  - Where does it come from, and where does it go?

**AGPDS Connection**
Which AGPDS concept or framework stage does this module implement?
Quote the relevant spec language and explain how the code fulfills (or partially
fulfills) it.

**Gotchas & Subtleties**
List 1–3 things about this module that are easy to misunderstand or get wrong.

---

After all modules, add a section:

## End-to-End Data Journey
Walk through ONE complete execution from entry point to final output file,
tracing exactly what happens to the data at each transformation step.
Use concrete example values where helpful (you may invent representative ones).

## Write Output
Write to `audit/03_code_walkthrough.md`.
YAML front-matter: title, date, modules_covered (list), total_sections.
Confirm: [WRITE CONFIRMED] <path> | <line count>
</task>
```

---

## Phase 4 — 综合报告

**目标:** 将前三个阶段的发现汇总为一份可直接行动的最终报告，包括问题清单、优先级排序和执行计划。

```
You are a senior ML project lead producing a final audit report. You have access
to all prior audit files in the `audit/` directory. Synthesize their findings
into a single actionable document.

<operating_rules>
1. NO NEW ANALYSIS: Do not introduce findings not present in the prior audit files.
   Synthesize and prioritize — do not re-audit.
2. ACTION-ORIENTED: Every problem must have a concrete, implementable action.
3. PRIORITIZE RUTHLESSLY: Use P0/P1/P2/P3. P0 = blocks Phase 3. P1 = correctness
   risk. P2 = spec divergence. P3 = style/naming.
4. CITE SOURCES: Reference the source audit file for every issue row.
</operating_rules>

<task>

## Section 1 — Executive Summary (≤200 words)
Answer these three questions:
  1. Is the implementation functionally correct? (Yes / Mostly / No — with evidence)
  2. Is it aligned with the AGPDS specification? (Fully / Partially / Significantly Divergent)
  3. Is it ready to proceed to Phase 3? (Ready / Ready with caveats / Blocked)

## Section 2 — Master Issue Registry
Consolidate ALL issues from Phase 1 and Phase 2 audits into one table.
Deduplicate and cross-reference. Schema:

| Issue ID | Source Audit | File:Lines | Priority | Category | Description | Recommended Action |
|----------|-------------|------------|----------|----------|-------------|-------------------|

Categories: CORRECTNESS_BUG / SPEC_DIVERGENCE / MISSING_FEATURE / CODE_QUALITY

## Section 3 — Sprint Plan
Group P0 and P1 issues into a logical implementation sequence.
For each item in the sprint:
  - Issue IDs addressed
  - Concrete implementation step (be specific: "Rename X to Y", "Add retry
    loop at file:line", "Rewrite function F to match spec §3.2")
  - Why this ordering? (1-sentence sequencing rationale)

## Section 4 — What the Code Gets Right
List 3–5 things the implementation does well, with evidence. This is important
for calibration — the author should know what to preserve during refactoring.

## Section 5 — Open Questions
List any unresolved ambiguities that require the author to consult the framework
designer (e.g., Dr. Tong Sun) or run the code to verify. Format:
  - [Q-001] Ambiguity description → What information would resolve this?

## Write Output
Write to `audit/04_final_report.md`.
YAML front-matter:
  title: "AGPDS Implementation Audit — Final Report"
  date: <today>
  verdict:
    functional_correctness: <Yes|Mostly|No>
    spec_alignment: <Fully|Partially|Significantly Divergent>
    phase3_ready: <Ready|Ready with caveats|Blocked>
  issue_counts:
    P0: <n>
    P1: <n>
    P2: <n>
    P3: <n>

Confirm: [WRITE CONFIRMED] audit/04_final_report.md | <line count>
</task>
```

---

## 使用指南

### 执行顺序
```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
```
每个阶段在 **独立的 Cursor Composer 会话**中运行。不要在同一会话中连续执行多个阶段——上下文污染会降低质量。

### 如何粘贴提示词
1. 打开 Cursor → `Cmd+I` 开启 Composer
2. 确认 Agent Mode 已开启（右下角切换）
3. 粘贴对应阶段的提示词
4. 如果框架 markdown 文件尚未在代码库中，在提示词末尾补充：`The AGPDS framework documents are located at: <path>`

### 阶段间依赖检查
运行下一阶段前，确认上一阶段的输出文件已写入：
```bash
ls -la audit/
# 期望看到: 00_codebase_map.md, 01_correctness_audit.md, ...
```

### 提示词定制建议
- **Phase 1:** 如果你知道具体的 LLM SDK（如 `openai`, `anthropic`），在 `<context>` 块中补充 `LLM SDK: openai v1.x`，帮助 agent 核查 API 调用格式
- **Phase 2:** 在提示词开头补充框架 markdown 的文件路径，例如：`Framework markdowns: ./docs/agpds_design.md, ./docs/agpds_roadmap.md`
- **Phase 3:** 如果想要中文讲解输出，在提示词末尾加：`Write the walkthrough document in Chinese (Simplified).`

---

*Workflow version: 1.0 | Designed for Cursor Agent Mode | AGPDS Project*
