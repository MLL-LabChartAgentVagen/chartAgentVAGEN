# Adjustment of markdown files for phase 2
_Exported on 3/25/2026 at 14:07:04 CDT from Cursor (2.6.21)_

---

**User**

@audit/4_phase2_sprint_plan.md and  @audit/3_phase2_implementation_alignment_map.md  are for phase 2 implementation and are designed without knowing I have exisiting modules of @pipeline/core/llm_client.py @pipeline/core/master_table.py and @pipeline/core/utils.py . With the context of these three modules, how should the content of these two markdown files adjust?

---

**Cursor**

Let me read all the relevant files first.

Good question. I carefully compared these five files. Below is a systematic analysis of how the two planning documents should be adjusted given the existing three modules: `llm_client.py`, `master_table.py`, and `utils.py`.

---

## 1. Impact of `llm_client.py` on the documents

### Core existing capabilities

`LLMClient` already provides:
- Multi-provider support (OpenAI / Gemini / Azure / custom)
- `generate(system, user, ...)` — directly accepts system/user prompts
- **`generate_code(system, user, ...)` — automatically strips ```` ```python ``` ```` fences**
- `generate_json(system, user, ...)` — JSON parsing + fence cleanup
- `ParameterAdapter` automatically adapts parameter differences across providers

### Adjustments to the Alignment Map (Module 10)

| Subtask | Current Status | Adjustment Recommendation |
|--------|---------|---------|
| **10.1.1** — System prompt construction | SPEC_READY | Reduce implementation scope. There is no need to build LLM invocation infrastructure from scratch. You only need to write `system` and `user` string templates for `LLMClient.generate_code()`. Note: the existing client already supports system/user separation |
| **10.2.1** — Extract Python code block | NEEDS_CLAR. | **Can be upgraded to SPEC_READY**. `LLMClient.generate_code()` lines 371-392 already implement fence stripping logic (`re.sub` matching both ```` ```python ```` and ```` ``` ````), which is exactly the "defensive robustness measure" described in the alignment map. This subtask becomes: simply call `generate_code()` directly |
| **10.2.2** — Validate code contains `generate()` | NEEDS_CLAR. | No change. You still need to perform an AST/string check on the result returned by `generate_code()` |
| **10.1.2** — Scenario context injection | BLOCKED (D1) | No change, but add a note that `META_CATEGORIES` in `utils.py` can be used as domain context inside the prompt |

### Adjustments to the Alignment Map (Module 7)

| Subtask | Adjustment Recommendation |
|--------|---------|
| **7.1.2** — Format error feedback for LLM | Implementation is simplified: just construct a new `user` prompt string (including the original code + traceback + fix instructions), then call `LLMClient.generate_code()` again. No new HTTP invocation logic is needed |
| **7.1.3** — Retry loop with max_retries=3 | It only needs to be implemented as a loop wrapper around `LLMClient.generate_code()`. Provider switching and parameter adaptation are already handled by `ParameterAdapter` |

### Adjustments to the Sprint Plan (Sprint 8)

The **workload of Sprint 8 should be reduced significantly**:

- The original Sprint 8 plan had 6 subtasks, and the LLM infrastructure work (client construction, multi-provider adaptation, code extraction) accounted for the majority
- Now both LLM invocation and code extraction are already covered by `LLMClient`, so Sprint 8 effectively only has:
  1. **Write prompt templates** (`10.1.1`) — pure string work
  2. **Code validation logic** (`10.2.2`) — verify the returned code contains `build_fact_table` and `generate()`
  3. **Sandbox execution** (`7.1.1`) — `SandboxExecutor` already exists
  4. **Error feedback formatting** (`7.1.2`) — construct the feedback prompt
  5. **Retry loop** (`7.1.3`) — simple loop
- `10.2.1` (fence stripping) can be marked directly as **completed/already covered**

The Sprint 8 description should be updated to:

> **Deliverable:** ~~The prompt template renders correctly with scenario context. The error feedback loop catches SDK exceptions and retries LLM code generation up to 3 times. Code extraction from LLM responses works.~~ → Use the existing `LLMClient.generate_code()` to integrate prompt templates and build the retry loop. Code fence extraction is already implemented by `LLMClient`.

---

## 3. Impact of `utils.py` on the documents

### Core existing capabilities

- `META_CATEGORIES` — a standardized list of 30 domain categories
- `generate_unique_id()` — unique ID generation with timestamp + random hash
- `validate_category()` / `get_category_by_id()` — category validation and lookup

### Adjustments to the Alignment Map

**Module 10 (Prompt & Integration):**

- **10.1.1** (System prompt construction): add a note that `META_CATEGORIES` can be used in the prompt to enumerate available domains
- **10.1.2** (Scenario context injection, BLOCKED on D1): add a note that although the complete Phase 1 → Phase 2 contract is not yet defined, the category system in `utils.py` is already the shared foundation across the Phase 0 → Phase 1 → Phase 2 chain. The `ScenarioContext` typed schema (which D1 needs to define) should reference `META_CATEGORIES` rather than introducing a new category system

**General infrastructure note:**

Both documents should add the following sentence at the beginning or in a "Prerequisites" section:

> **Existing infrastructure:** `pipeline/core/utils.py` provides 30 domain categories (`META_CATEGORIES`) and unique ID generation (`generate_unique_id()`). These utilities are already used in Phase 0 and Phase 1, and the Phase 2 pipeline orchestration should reuse them directly instead of redefining them.

### Adjustments to the Sprint Plan

The description of **Blocker 6** (Phase 1 → Phase 2 Interface Contract) should be supplemented with:

> When defining the `ScenarioContext` typed schema, its domain/category fields should reference the `META_CATEGORIES` taxonomy in `pipeline/core/utils.py`. `generate_unique_id()` can be used as the tracking identifier for pipeline runs.

---

## 4. Summary: structural changes that need to be made

### New prerequisite section to add to the Alignment Map

Before "Module 1", it is recommended to add a new section:

> ### Pre-existing Infrastructure (`pipeline/core/`)
> 
> The following modules are already implemented, and Phase 2 modules should reuse them rather than rebuild them:
> 
> | Module | File | Capabilities Already Provided | Affected Subtasks |
> |------|------|-----------|------------|
> | `LLMClient` | `pipeline/core/llm_client.py` | Multi-provider LLM invocation, code fence stripping, JSON parsing | 10.1.1, 10.2.1, 7.1.2, 7.1.3 |
> | `utils` | `pipeline/core/utils.py` | META_CATEGORIES, unique ID generation, category validation | 10.1.1, 10.1.2, 11.1.1 |

### Numbers that should be adjusted in the Sprint Plan

| Change | Explanation |
|------|------|
| Sprint 8 subtask count | Reduce from 6 to **5** (`10.2.1` is covered by `generate_code()`), or keep it at 6 but mark `10.2.1` as "already implemented by `LLMClient`, only integration validation needed" |
| Sprint 8 workload | Significantly reduced. Originally it needed client construction + code extraction + retries; now it only needs prompt templates + validation + retry loop |
| Parallelization opportunities | Sprint 8 is now more parallelizable. Since the LLM infrastructure is already ready, it could even start earlier (only depending on Sprint 1 exception types) |
| Critical Path diagram | The "parallel" path for Sprint 8 becomes shorter/lighter and can be annotated as "partially complete" |

---

In summary, the three existing modules mainly affect **Sprint 8** (LLM integration is greatly simplified). At the same time, the alignment map should add "already implemented" notes for several subtasks to avoid rebuilding what already exists.

---
