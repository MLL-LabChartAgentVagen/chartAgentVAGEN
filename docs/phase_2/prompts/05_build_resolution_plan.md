# Phase 2 — Stage 5: Build Resolution Plan

Please perform this stage strictly based on the following files.

Authoritative spec files:
- `docs/phase2/spec/phase_2.md`
- `docs/phase2/spec/1_phase2_implementation_task_hierarchy.md`
- `docs/phase2/spec/2_phase2_gap_analysis.md`
- `docs/phase2/spec/3_phase2_implementation_alignment_map.md`
- `docs/phase2/spec/4_phase2_sprint_plan.md`

Required input files:
- `docs/phase2/outputs/01_evidence_matrix.md`
- `docs/phase2/outputs/02_delivery_state.md`
- `docs/phase2/outputs/03_blockers_and_spec_gaps.md`
- `docs/phase2/outputs/04_clarifications_and_spec_patches.md`

Task:
Produce a genuinely actionable resolution path.

Please do the following:

## 1. Define the unlock path
In order, explain:
1. what must be clarified first
2. what patch must be completed first
3. which modules can continue in parallel
4. which modules must wait for patches
5. which unresolved items would create the highest rework if deferred

## 2. Define the shortest path to stable delivery
Answer:
- starting from “Sprint 1–8 completed,” what minimum steps remain before stable delivery
- which blockers are the highest-leverage unlock points
- which issue-order dependencies cannot be reversed

## 3. Provide a responsibility split
Assign responsibilities across:
- Spec Owner
- Architect
- Validation / Rules Owner
- Implementation Owner
- PM / Prioritization Owner

## 4. Provide an execution strategy
Distinguish between:
- work that can continue immediately
- work that must pause pending upstream clarification
- work that can proceed under stubs / assumptions but must not be claimed as done
- work that should be deferred / removed / re-scoped

## 5. Provide the final readiness conclusion
Explicitly answer:
- what still stands between the project and stable delivery
- what the biggest remaining uncertainty is
- what the single most valuable next step is

Constraints:
- do not merely repeat earlier analysis
- you must provide order and ownership
- you must distinguish continue / pause / assumption-driven / defer
- if prior-stage outputs conflict with the source files, prefer the source files and explicitly note the correction

The output format must strictly follow this Markdown structure:

# Phase 2 Resolution Path and Execution Order

## 1. Executive Summary
- 4–6 bullets

## 2. Recommended Unlock Path (In Order)
| Order | Action First | Goal | Risk If Not Done | What It Unlocks |
|---|---|---|---|---|

## 3. Shortest Path to Stable Delivery
- explain in 1–2 paragraphs what still remains between “Sprint 1–8 complete” and “stable delivery”

## 4. Responsibility Split
| Role | Required Actions | Priority | Notes |
|---|---|---|---|

## 5. What Can Continue vs What Must Pause
### Can continue now
- ...

### Can proceed only under assumptions
- ...

### Must pause pending patch / decision
- ...

### Should be deferred / removed / re-scoped
- ...

## 6. Highest-Risk Wrong Execution Patterns
- list 3–5 patterns
- explain why each one causes rework or false completion

## 7. Final Readiness Judgment
- answer in one paragraph:
  “What still separates the project from stable delivery, and what is the most important next step?”

Write the result to:
`docs/phase2/outputs/05_resolution_plan.md`

In chat, reply only with:
1. which files you read
2. which file you wrote
3. a stage summary of no more than 8 lines