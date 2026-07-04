# KS n<30 Prevalence — At-Scale Measurement (2026-05-31)

> Measures how prevalent small (n<30) per-cell sample sizes are in the Phase 2
> KS validator, **after** Phase 1's tiered `target_rows`
> ([scenario_contextualizer.py:102-106](../../pipeline/phase_1/scenario_contextualizer.py#L102-L106))
> and Phase 2's Constraint 13 / sparse-cell handling
> ([PATH_D_KS_SPARSE_CELLS.md](subsystems/PATH_D_KS_SPARSE_CELLS.md)) are in place.
>
> Tooling (read-only): [`pipeline/phase_2/analysis/`](../../pipeline/phase_2/analysis/)
> — `sample_balanced_scenarios.py`, `run_generate_batch.py`, `ks_cell_size_audit.py`.
> Batch: `output/agpds/ks-measure-n90` (gemini, seed 42). Execute + audit run
> under the conda `chart` env (numpy 1.26.4).

## Setup

- Tier-balanced sample drawn from [scenario_pool.jsonl](../../pipeline/phase_1/scenario_pool.jsonl)
  (1,390 scenarios; pool tiers simple 21% / medium 43% / complex 36%).
- Generated 30 successes/tier (~94% generate success; 6 failed on the unrelated
  [calibration.py:102](../../pipeline/phase_2/orchestration/calibration.py#L102)
  "All rows excluded by pattern masks" crash). Executed deterministically under
  the `chart` env: **90/90 produced master tables**.
- Audit recovers every KS cell's `n` by reusing the validator's own
  `_iter_predictor_cells` (not regex over detail strings). Verified bit-exact
  against `smoke-test-batch-1` and spot-checked against at-scale `ks_*` detail
  strings (e.g. `waste_tonnage` 6 tested / 10 small-n).
- Sample: 90 scenarios (balanced 30/30/30), 148 stochastic measures, **1,102 KS cells**.

## Headline

**n<30 is NOT eliminated, but it is no longer a high-dimensionality problem.**

- **~19% of KS-eligible cells get skipped for n<30** (202 / 1,049 cells with n≥5
  and a usable CDF; 847 actually tested).
- **34% of stochastic measures (50/148)** have ≥1 cell skipped for small-n.
- **Only 1% of measures (2/148)** had *all* eligible cells skipped — the
  "silent-pass" blind spot is rare in practice.

## By complexity tier (full census, every cell n≥1)

| tier | cells | %n<30 | %n<10 | median n |
|------|------:|------:|------:|---------:|
| complex | 427 | **5.9%** | 0.2% | 128 |
| simple | 200 | 24.5% | 3.0% | 41 |
| medium | 475 | **30.7%** | 7.2% | 46 |

Complex tier is essentially clean — its higher `target_rows` (≈1,800 median)
absorbs the cross. Medium is the worst tier.

## By predictor dimensionality K, and tier × K

| bucket | cells | %n<30 | median n |
|--------|------:|------:|---------:|
| K=1 | 225 | 12.9% | 112 |
| K=2 | 812 | 21.4% | 57 |
| K=3 | 65 | 26.2% | 56 |
| **K=4** | **0** | — | — |
| complex/K=1 | 61 | 0.0% | 422 |
| complex/K=2 | 307 | 3.3% | 125 |
| complex/K=3 | 59 | 25.4% | 56 |
| medium/K=1 | 60 | 0.0% | 125 |
| **medium/K=2** | **409** | **35.2%** | 41 |
| medium/K=3 | 6 | 33.3% | 46 |
| **simple/K=1** | **104** | **27.9%** | 41 |
| simple/K=2 | 96 | 20.8% | 41 |

## Interpretation

1. **Constraint 13 worked on dimensionality.** The PATH_D-era "LLM declares a
   4D `tier × program × residency × year` cross" is gone: **zero K=4 measures**,
   and only 65 of 1,067 cells are K=3. The earlier "n=5/6 cells from K=4 crosses"
   pathology does not appear in this batch.
2. **Residual n<30 is now a row-count problem at the low tiers**, concentrated in
   two buckets: **medium/K=2** (409 cells, 35% n<30) and **simple/K=1** (104 cells,
   28%). Medium `target_rows` (~720) split across ~20-30 K=2 cells lands ~24-40/cell
   — straddling 30. Simple (~300 rows) dips below even on a single high-cardinality
   categorical.
3. **Tiering helped where it had headroom (complex), not where it didn't (simple/
   medium).** This is consistent with `n ≈ target_rows / cell_count`: only the
   complex range is large enough to keep K=2 above 30.

## Candidate follow-ups (not done here)

> **裁定 (2026-05-31): 不追究。** 见 [KS_N30_VERDICT_2026-05-31.md](./KS_N30_VERDICT_2026-05-31.md)
> —— n<30 跳过是统计上正确的,唯一真实漏洞(1% silent-pass)可接受;下列 follow-ups
> 仅作记录,不作为主手段。若日后要消灭 silent-pass,正确做法是 PIT-pooled backstop
> 而非加行数(详见裁定文档)。

- Raise the simple/medium `target_rows` floors, or make Constraint 13's
  `target_rows ≥ 30 × cell_count` actually *bind* at those tiers (currently advisory).
- Cap categorical cardinality for simple-tier scenarios (drives simple/K=1 n<30).
- Fix the [calibration.py:102](../../pipeline/phase_2/orchestration/calibration.py#L102)
  crash (all-rows-excluded → graceful skip) so generate success rate ≈ 100%.

Full machine-readable breakdown: `output/agpds/ks-measure-n90/ks_cell_size_report.json`.
