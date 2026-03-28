# Phase 2 — Stage 3: Model Blockers and Spec Gaps

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

Task:
Turn the current “problem list” into a “problem structure.”

Please analyze each blocker and key spec problem as follows:

## 1. Model each Critical Path Blocker
For each blocker, explain:
1. what type of problem it is:
   - missing definition
   - incomplete schema / contract
   - unresolved parameter / field definition
   - cross-module spec conflict
   - missing validation criterion
   - unclear auto-fix / orchestration semantics
2. which subtasks / modules it directly blocks
3. why it cannot currently be implemented correctly
4. what rework or deviation would happen if it were forced through
5. which downstream chains it unlocks once resolved

## 2. Model key spec gaps by theme
Group issues under themes such as:
- metadata schema
- formula DSL
- distribution families / parameter schema
- pattern triples (`params_schema + injection + validation`)
- validator ↔ metadata field contract
- L2 vs pattern injection conflict
- auto-fix mutation model
- stage ordering / orchestration
- realism / validation conflict
- soft-fail downstream policy
- typed interface completeness

## 3. Separate the issues into two categories
A. missing / undefined  
B. contradiction / contract inconsistency  

## 4. Assign priority
- P0: cannot continue correct implementation without clarification
- P1: local progress possible, but with high rework risk
- P2: does not block the main path, but affects completeness or stability

## 5. Abstract each issue from symptom to essence
Do not stop at “this is unclear.”
Instead, answer whether the missing piece is:
- an object definition
- a field-level schema
- a lifecycle / stage-ordering rule
- an input/output contract
- a testable validation criterion
- or an unfrozen boundary between modules

Constraints:
- do not move into patch drafting in depth
- do not merely restate finding titles
- do not give generic summaries
- you must explain why each issue blocks implementation
- you must distinguish missing vs contradictory
- if prior-stage outputs conflict with the source files, prefer the source files and explicitly note the correction

The output format must strictly follow this Markdown structure:

# Phase 2 Blocker and Spec Gap Model

## 1. Executive Summary
- 4–6 bullets

## 2. Critical Path Blockers Overview
| Order | Blocker | Problem Type | Core Issue | Directly Blocks | Force-Through Risk | Unlock Benefit | Priority |
|---|---|---|---|---|---|---|---|

## 3. Deep Explanation for Each Blocker
### Blocker 1: ...
- Essential problem:
- Blocking mechanism:
- Why correct implementation is not currently possible:
- Force-through risk:
- Unlock chain:
- What category of spec problem this belongs to:

### Blocker 2: ...
(repeat for all blockers)

## 4. Missing / Undefined Issues
| Theme | Specific Missing Piece | Affected Modules | Why It Blocks Implementation | Priority |
|---|---|---|---|---|

## 5. Contradictions / Contract Inconsistencies
| Theme | Contradiction | Modules / Layers Involved | Consequence | Priority |
|---|---|---|---|---|

## 6. Problem Essence Synthesis
### 6.1 Missing-definition class
- ...

### 6.2 Incomplete schema / contract class
- ...

### 6.3 Cross-module conflict class
- ...

### 6.4 Validation / auto-fix / orchestration semantic class
- ...

## 7. Final Judgment
- answer in one paragraph:
  Is the primary Phase 2 problem better characterized as “unfinished implementation volume” or “unfrozen spec / contract”?

Write the result to:
`docs/phase2/outputs/03_blockers_and_spec_gaps.md`

In chat, reply only with:
1. which files you read
2. which file you wrote
3. a stage summary of no more than 8 lines