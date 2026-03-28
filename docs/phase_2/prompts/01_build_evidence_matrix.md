# Phase 2 — Stage 1: Build Evidence Matrix

Please perform this stage strictly based on the following 5 authoritative documents:
- `docs/phase2/spec/phase_2.md`
- `docs/phase2/spec/1_phase2_implementation_task_hierarchy.md`
- `docs/phase2/spec/2_phase2_gap_analysis.md`
- `docs/phase2/spec/3_phase2_implementation_alignment_map.md`
- `docs/phase2/spec/4_phase2_sprint_plan.md`

Task:
Build an “evidence–role–problem-type” matrix.
This stage is for factual extraction and structured organization only.
Do not produce solutions.
Do not produce later-stage conclusions.

Please extract and organize the following:

## A. Foundation spec facts (from `phase_2.md`)
1. Core SDK API statements
2. The `generate` main flow
3. Metadata output definitions
4. Validation-related definitions
5. Auto-fix / retry / orchestration-related definitions
6. Prompt / hard-constraint-related definitions
7. Any places where examples exist but the formal contract appears missing

## B. Implementation contract facts (from `1_phase2_implementation_task_hierarchy.md`)
1. Top-level contracts, especially `generate()`
2. Key done conditions
3. Key information from the Cross-Section Dependency Map
4. Which issues are already categorized as implementation design choices rather than spec requirements
5. Which subtasks expose spec gaps at the done-condition level

## C. Gap analysis facts (from `2_phase2_gap_analysis.md`)
1. All CRITICAL findings
2. Important MODERATE findings that materially affect blocker resolution
3. Cross-reviewer conflicts / synthesis
4. Priority blockers / priority order
5. For each finding: spec location, issue, impact, recommendation

## D. Alignment map facts (from `3_phase2_implementation_alignment_map.md`)
1. Total number of subtasks
2. Counts for `SPEC_READY / NEEDS_CLARIFICATION / BLOCKED / SPEC_INCORRECT`
3. Critical Path Blockers list and order
4. Which subtasks each blocker directly blocks
5. Any readiness changes that help define boundary judgments

## E. Sprint plan facts (from `4_phase2_sprint_plan.md`)
1. Total sprint count and the scope of Sprint 1–8
2. Number of scheduled implementable subtasks
3. Counts of blocked / spec_incorrect / deferred items
4. Blocked-wall / post-Sprint-8 descriptions
5. Sprint 9+ integration order after blocker resolution

## F. Build a unified issue-theme index
Map all extracted evidence into unified themes such as:
- metadata schema
- formula DSL
- distribution family parameters
- pattern type specification
- auto-fix mutation model
- validator ↔ metadata contract
- Phase 1 → Phase 2 typed contract
- orchestrator / stage ordering
- realism / validation conflict
- soft-fail downstream policy

Constraints:
- Extract facts and structure them only
- Do not compute conclusions
- Do not generate solutions
- Do not give generic advice
- If there are conflicts, preserve both sides
- If prior chat claims conflict with the source files, prefer the source files and explicitly note the conflict

The output format must strictly follow this Markdown structure:

# Phase 2 Multi-Document Evidence Matrix

## 1. Document Role Summary
| Document | Primary Role | Questions It Can Answer | Questions It Should Not Answer |
|---|---|---|---|

## 2. Foundation Spec Key Facts (`phase_2.md`)
| Topic | Original Definition / Key Source Detail | Affected Module | Notes |
|---|---|---|---|

## 3. Implementation Contract Key Facts (`task hierarchy`)
| Topic | Contract / Done Condition / Dependency | Related Tasks | Notes |
|---|---|---|---|

## 4. Gap Analysis Key Facts
| Finding ID / Topic | Severity | Issue | Impact | Recommendation | Notes |
|---|---|---|---|---|---|

## 5. Alignment Map Key Facts
| Item | Value / Content | Meaning in Context | Notes |
|---|---|---|---|

## 6. Sprint Plan Key Facts
| Item | Value / Content | Meaning | Notes |
|---|---|---|---|

## 7. Unified Issue Theme Index
| Theme | Foundation Spec Evidence | Audit Evidence | Task / Contract Evidence | Readiness / Sprint Evidence |
|---|---|---|---|---|

## 8. Number Pool Directly Relevant to Later Completion Assessment
- list all relevant numbers
- do not calculate yet

## 9. Evidence Pool Directly Relevant to Later Blocker Resolution
- list the most critical evidence items
- for each one, label it as: missing definition / incomplete contract / conflict / missing validation / orchestration-semantic issue

## 10. Evidence Completeness Check
- Clearly established:
- Still ambiguous:
- Must be tracked carefully in the next stage:

Write the result to:
`docs/phase2/outputs/01_evidence_matrix.md`

In chat, reply only with:
1. which files you read
2. which file you wrote
3. a stage summary of no more than 8 lines