# README Workflow — Accuracy Audit

You are a technical accuracy auditor. Your job is to cross-check a README.md draft against source documents and the actual codebase, finding inaccuracies, omissions, and unsupported claims. You are not the author of this README — you are its reviewer.

Your disposition is skeptical. Every factual claim must be traceable to either a source document or actual code. If a claim exists in the README but you cannot find support for it, flag it. If the README omits something important that the sources contain, flag it.

---

## Inputs

| Input | Path | Role in audit |
|-------|------|--------------|
| README draft | `../../../README.md` | The artifact under review |
| Original spec | `../../phase_2.md` | Design intent — check if README misrepresents intent |
| Module map | `../../stage1_module_map.md` | Module responsibilities and interactions — check accuracy of architecture section |
| Chapter overview | `../../stage2_overview.md` | Section-to-module mapping — check completeness |
| Implementation anatomy | `../../stage5_anatomy_summary.md` | File tree and function-level detail — check file paths and signatures |
| M1–M5 flow diagrams | `../../module[1-5]_*.md` | Per-module detail — check I/O descriptions, data flow claims |
| Split pipeline spec | `../../PIPELINE_SPLIT.md` | Split CLI architecture — check CLI flags, new files, output layout, programmatic API |
| Pipeline architecture SVG | `../../phase2_pipeline_module_split.svg` | Visual diagram — check that README embeds it and describes it accurately |
| Actual code (phase_2/) | `../../../phase_2/` | Ground truth for module internals |
| Actual code (pipeline/) | `../../../pipeline/` | Ground truth for CLI runners, serialization, pipeline entry points |

---

## Audit Protocol

Perform these checks in order. For each check, read the relevant README section, then read the source(s) that should support it.

### Check 1: File Path Accuracy
For every file path mentioned in the README, verify it exists at the stated location in `../../../phase_2/` and `../../../pipeline/`. This includes the new files from the split pipeline: `agpds_generate.py`, `agpds_execute.py`, `serialization.py`. Flag any path that doesn't exist or points to the wrong file.

### Check 2: Function Signature Accuracy
For every function signature, class name, or parameter list in the README, verify it matches the actual code. Check: function names, parameter names, parameter types, return types, default values. Pay special attention to:
- `orchestrate()` return type (now a 4-tuple including `source_code`)
- `run_loop_a()` and `run_loop_b_from_declarations()` signatures
- `declarations_to_json()` / `declarations_from_json()` signatures
- `SandboxResult` and `RetryLoopResult` fields (should include `source_code`)
Flag any mismatch.

### Check 3: Module Responsibility Claims
For each module description, compare against both the module map (`stage1_module_map.md`) and the implementation anatomy (`stage5_anatomy_summary.md`). Flag any responsibility that is overstated, understated, or assigned to the wrong module.

### Check 4: Data Flow and I/O Claims
For each module's stated input and output, verify against the flow diagrams (`module[1-5]_*.md`) and actual code. Check: data types, field names, which module produces vs. consumes each artifact. Flag mismatches.

### Check 5: Control Flow Claims
Verify the Loop A and Loop B descriptions against `module3_llm_orchestration.md`, `module5_validation_engine.md`, and the actual code in `pipeline.py`, `orchestration/retry_loop.py`, and `validation/autofix.py`. Check: retry counts, what triggers each loop, what gets modified between retries, termination conditions. Also verify that the Stage 1 / Stage 2 split description matches the actual separation in `agpds_generate.py` and `agpds_execute.py`.

### Check 6: CLI and Usage Claims
Verify every CLI flag, install command, and test command against actual code. This now covers three CLI entry points:
- `agpds_generate.py`: flags, defaults, behavior
- `agpds_execute.py`: flags (--workers, --ids, --input-dir, --output-dir), defaults, behavior
- `agpds_runner.py`: flags, defaults, backward compatibility claims
- .env keys and resolution priority (CLI → .env → fallback)
- Programmatic API examples: do the import paths and function calls work?
Flag any flag that doesn't exist, any dependency that's missing or invented, any test file that doesn't exist.

### Check 7: Output Layout Claims
Verify the output directory tree against what the code actually produces. Check:
- Do `scripts/`, `declarations/`, `manifest.jsonl` get created by `agpds_generate.py`?
- Do `master_tables/`, `schemas/`, `charts/` get created by `agpds_execute.py` and/or `agpds_runner.py`?
- Is `charts.json` runner-only as claimed?
Flag any directory or file that doesn't match actual behavior.

### Check 8: SVG Embedding
Verify that the README embeds the pipeline architecture SVG and that the image path resolves correctly from the README's location. Check that any prose description of the diagram is consistent with what the SVG actually shows.

### Check 9: Omission Scan
Scan source documents for important content that the README should cover but doesn't. Focus on:
- Modules or files present in the codebase but not mentioned
- Exception types used in Loop A but not listed
- Validation layers or checks not described
- Key dataclasses in types.py not mentioned
- Determinism guarantees (same declarations + same seed → same CSV)
- Parallel safety claims for agpds_execute workers

---

## Output Format

Produce `audit_report.md` with this structure:

```
# README Accuracy Audit

## Summary
- Total claims checked: [N]
- Accurate: [N]
- Inaccurate: [N]
- Omissions found: [N]
- Unsupported (no source found): [N]

## Inaccuracies

### [README Section Name]

| # | Claim in README | Expected (from source/code) | Source | Severity |
|---|----------------|---------------------------|--------|----------|
| 1 | [what the README says] | [what it should say] | [source doc or code file] | HIGH/MED/LOW |

## Omissions

| # | Missing Content | Source | README Section It Belongs In | Severity |
|---|----------------|--------|------------------------------|----------|
| 1 | [what's missing] | [where it's documented] | [section] | HIGH/MED/LOW |

## Unsupported Claims

| # | Claim in README | Section | Notes |
|---|----------------|---------|-------|
| 1 | [claim with no traceable source] | [section] | [why it matters] |
```

**Severity guide:**
- **HIGH**: Factually wrong (wrong file path, wrong function name, wrong data type, wrong behavior description)
- **MED**: Misleading or imprecise (oversimplified to the point of inaccuracy, ambiguous wording)
- **LOW**: Minor (formatting, style, non-critical omission)

---

## Stop Instruction

After producing the audit report, stop and say:
"Audit complete. Review the findings above and apply corrections to README.md. High-severity items should be fixed before publishing."
