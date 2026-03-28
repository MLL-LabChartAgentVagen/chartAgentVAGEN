# Phase 2 — Stage 4: Design Clarifications and Spec Patches

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

Task:
Convert blockers / spec gaps into:
1. directly usable clarification questions
2. an actionable spec patch backlog

Please do the following:

## 1. Generate a clarification question set
Requirements:
- group questions by blocker / theme
- each question must be concrete, answerable, and operational
- avoid vague prompts like “please improve the spec”
- questions should be directly sendable to:
  - PM / Spec Owner
  - Architect
  - Rules / Algorithm Owner
  - Implementation Owner

Question types may include:
- object-definition questions
- schema / field questions
- parameter-domain questions
- parser / DSL grammar questions
- validation-rule questions
- auto-fix semantics questions
- orchestration / stage-ordering questions
- backward-compatibility / versioning questions
- defer / remove / re-scope questions

## 2. Generate a spec patch backlog
For each blocker or theme, design the minimum necessary patch:
1. which spec section must be added or revised
2. what kind of patch content is needed:
   - formal schema
   - reference table
   - grammar
   - algorithm
   - state machine / stage order
   - validator contract
   - metadata example
   - decision note
3. what the patch completion criteria are
4. which subtasks / modules this patch unlocks

## 3. Separate two kinds of outputs
A. issues that must be decided by the spec owner / architect  
B. issues that can be left to implementation design under fixed rules  

## 4. Identify the minimum unlock patch set
That is:
- which patches, once completed, would remove the maximum amount of blocked wall
- which patches are later enhancements and should not be prioritized first

Constraints:
- do not only list questions; you must also produce the patch backlog
- do not only give patch titles; include patch type and completion criteria
- every question must align with a blocker or spec gap
- questions must be concrete
- if prior-stage outputs conflict with the source files, prefer the source files and explicitly note the correction

The output format must strictly follow this Markdown structure:

# Phase 2 Clarifications and Spec Patch Design

## 1. Executive Summary
- 4–6 bullets

## 2. Clarification Questions for Owners

### Blocker 1 / Theme 1: ...
#### Must-answer questions
1. ...
2. ...
3. ...

#### Additional recommended confirmations
1. ...
2. ...

### Blocker 2 / Theme 2: ...
(repeat as needed)

## 3. Thematic Clarification Index
### 3.1 Metadata / Schema
- ...

### 3.2 Formula DSL
- ...

### 3.3 Distribution Parameters
- ...

### 3.4 Pattern Specification
- ...

### 3.5 Validator / Auto-Fix / Orchestration
- ...

### 3.6 Typed Contract / Versioning / Downstream Policy
- ...

## 4. Spec Patch Backlog
| Patch ID | Theme | Section to Add / Revise | Patch Type | Minimum Completion Criteria | Unlocks | Priority |
|---|---|---|---|---|---|---|

## 5. What Must Be Decided by the Spec Owner / Architect
| Theme | Why Owner-Level Decision Is Required | What Implementers Cannot Decide Alone |
|---|---|---|

## 6. What Can Be Left to Implementation Design
| Theme | Why It Can Be Delegated | Constraint Boundary |
|---|---|---|

## 7. Minimum Unlock Patch Set
- list the smallest useful set of patches
- explain why this set maximizes blocker removal

## 8. Final Judgment
- answer in one paragraph:
  “What is truly missing right now is not more implementation, but which spec patches / decision patches?”

Write the result to:
`docs/phase2/outputs/04_clarifications_and_spec_patches.md`

In chat, reply only with:
1. which files you read
2. which file you wrote
3. a stage summary of no more than 8 lines