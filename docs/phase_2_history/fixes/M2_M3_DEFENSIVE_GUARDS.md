# M2 + M3 — Defensive Guards in `inject_dominance_shift` and `inject_convergence`

## Why

Both findings flag the same underlying pattern: the implementer added
defensive code beyond the operational spec in
[stub_blocker_decisions.md §DS-2](../stub_analysis/stub_blocker_decisions.md).
The audit's initial framing was "spec-vs-code drift," but a closer read
showed the additions are **necessary correctness guards**, not
unauthorized embellishments. This fix retroactively legitimizes them
by amending the decisions doc; the source code is unchanged.

### M2 — `inject_dominance_shift` two-tier floor

**Spec (pre-fix):**
```
shift = peer_max + magnitude * peer_std - df.loc[post_split, col].mean()
```

**Code at [engine/patterns.py:369-374](../../engine/patterns.py#L369-L374):**
```python
if not np.isfinite(peer_std) or peer_std <= 0.0:
    gap = max(abs(peer_max) * 0.1, 1.0)   # degenerate peers
else:
    gap = max(magnitude * peer_std, 1e-9)  # magnitude=0 floor
shift = peer_max + gap - mean(post_split)
```

**Why the floor is required:** the paired `check_dominance_shift`
validator
([validation/pattern_checks.py L207-309](../../validation/pattern_checks.py))
checks for a rank flip across `split_point`. Two edge cases collapse
the spec formula's `gap` to zero:

1. **Zero peer variance** — peers are degenerate (e.g. one peer, or
   all peers identical). `peer_std == 0`, so spec gap = 0.
2. **Caller passed `magnitude=0`** — explicitly says "no magnitude,"
   but spec gap = 0 in this case too.

Both cases land target_mean exactly at peer_max. Pandas/NumPy stable
sort breaks ties by the index order the values were observed in,
which is unrelated to the validator's intent. The validator then
fails or passes essentially at random for these inputs. The floor
guarantees `target_mean > peer_max` strictly, giving the rank check
a deterministic positive case.

The two tiers (`max(|peer_max|*0.1, 1.0)` for degenerate peers vs.
`1e-9` for magnitude=0) reflect the different magnitudes of "what
counts as visibly dominant" — when peers have real variance but the
caller asked for a small effect, an `1e-9` floor is enough to flip
the rank without materially shifting values; when peers have no
variance at all, a 10% boost is the more natural minimum.

### M3 — `inject_convergence` `[0, 1]` clip

**Spec (pre-fix) at [stub_blocker_decisions.md:626-629](../stub_analysis/stub_blocker_decisions.md#L626-L629):**
```
factor = (t - tmin)/(tmax - tmin) * pull
df[col] = df[col] * (1 - factor) + global_mean * factor
```

**Code at [engine/patterns.py:615-617](../../engine/patterns.py#L615-L617):**
```python
factor = (norm_t.loc[valid_target_idx] * pull_strength).clip(
    lower=0.0, upper=1.0,
)
```

**Why the clip is required:** without it, `pull_strength > 1` produces
`factor > 1` near `t = tmax`, which inverts the blend `(1 - factor) < 0`
and pushes target rows to the *opposite* side of `global_mean`. The
result is **increased** inter-group variance, exactly the failure
mode the paired `check_convergence` validator is designed to detect.
Without the clip, the injector actively undermines its validator —
they would systematically disagree for `pull_strength > 1`.

Symmetrically, negative `pull_strength` clips to 0 (no-op) rather
than producing anti-convergence. The clip preserves the only sensible
semantics for the `pull_strength` parameter: "larger pull = stronger
convergence, capped at full collapse to the mean." Any caller —
human or LLM — would assume that meaning from the parameter name.

## Fix strategy

Both M2 and M3 are guards that must stay in the source. The
decisions doc was incomplete: it documented the happy-path formula
but did not specify behavior for inputs that would violate the
injector-validator agreement. The fix amends the decisions doc to
authorize the guards and explain *why* they are required (not merely
"defensive," but "needed for the paired validator to be reliable").

Source code at [engine/patterns.py:369-374](../../engine/patterns.py#L369-L374)
and
[engine/patterns.py:615-617](../../engine/patterns.py#L615-L617) is
unchanged. Tests are unchanged.

## Summary of changes

### Modified files

- **[pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md](../stub_analysis/stub_blocker_decisions.md)**
  - **§DS-2 `dominance_shift` algorithm description** — replaced the
    one-line `shift = peer_max + magnitude * peer_std - mean(...)`
    formula with the two-tier floor, plus a paragraph explaining
    why the floor is needed (zero-variance peers and `magnitude=0`
    both yield a tie that breaks the rank-flip check). Cites the
    authoritative source location.
  - **§DS-2 `convergence` algorithm description** — added
    `clip((...), 0.0, 1.0)` to the pseudocode, plus a paragraph
    explaining that without the clip the injector and the paired
    validator disagree for `pull_strength > 1`. Cites the
    authoritative source location.

- **[pipeline/phase_2/docs/POST_STUB_AUDIT_FINDINGS.md](../POST_STUB_AUDIT_FINDINGS.md)**
  - M2 entry: prepended ✅ RESOLVED marker, replaced "Fix options"
    list with "Resolution" paragraph linking here.
  - M3 entry: same treatment.

### Source code

- **No changes.** Both guards are kept verbatim in
  [engine/patterns.py](../../engine/patterns.py).

### Tests

- **No changes.** Existing tests already verify the guarded behavior
  works correctly:
  - `TestInjectDominanceShift` covers the rank-flip post-condition
    (which depends on the floor being present).
  - `TestInjectConvergence::test_round_trip_passes_validator`
    covers the injector-validator agreement (which depends on the
    clip being present for any non-trivial `pull_strength`).

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/
# 270 passed in ~1s — same as before the M2/M3 fix; no behavioral change.
```

Manual cross-check: every reference to the `dominance_shift` or
`convergence` algorithm in the decisions doc now matches the live
source. The decisions doc is again the single source of truth that
a reader can hold against the code without surprises.

## Pattern observation

This finding pair illustrates a recurring failure mode in the stub
workflow: the spec authors wrote operational definitions for the
**happy path** (clean inputs, well-behaved parameters) but did not
specify behavior on edge inputs that the implementation has to
handle anyway. The implementers — having to actually run the code
against a paired validator — discovered the gaps and patched them
inline. The decisions doc then drifted because the spec authors
never closed the loop on "what if peer_std is zero?" or "what if
pull_strength > 1?"

For future stub work: any operational definition that includes a
paired validator should be reviewed for **input domain coverage**
before the implementation begins, not after. A simple checklist
("what happens at the boundary of each parameter?") would have
caught both M2 and M3 before they shipped.
