# Sprint 1 Comprehension: Foundation — Data Structures, Constructor, Exception Hierarchy

---

## 1. Overview

Sprint 1 implements the three foundational modules that every subsequent sprint builds on: (1) a typed exception hierarchy of 11 classes matching the §2.7 error taxonomy, (2) three dataclass models for dimension groups and cross-group relations per §2.2 and §2.6, and (3) the `FactTableSimulator` constructor with seven typed empty registries per §2.8. These modules contain zero business logic beyond constructor validation — their purpose is to establish the type contracts, storage shapes, and error vocabulary that Sprints 2–8 will populate.

**Subtask IDs covered:** 1.1.1, 1.1.2, 2.1.1, 2.2.1, 2.2.2, 6.1.1, 6.1.2, 6.1.3, 6.1.4

**Spec sections covered:** §2.1 (SDK API surface implied by `add_*` storage targets), §2.2 (dimension groups, orthogonal declarations, group dependencies), §2.6 (metadata output format — serialization contracts), §2.7 (exception types and message formats), §2.8 (constructor signature, registry attributes)

**Relationship to prior sprints:** None — Sprint 1 is the foundation layer with zero external dependencies.

**What this sprint enables downstream:**

| Consumer Sprint | What It Imports | Purpose |
|---|---|---|
| Sprint 2 | `FactTableSimulator`, `DimensionGroup`, 5 validation exceptions | `add_category()` and `add_temporal()` validate inputs and mutate registries |
| Sprint 3 | `OrthogonalPair`, `GroupDependency`, `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError` | `declare_orthogonal()`, `add_group_dependency()`, `add_measure()`, `add_measure_structural()` |
| Sprint 4 | `CyclicDependencyError` | `topological_sort()` raises on cycles |
| Sprint 8 | `SimulatorError` (base class) | Feedback loop catches all SDK errors, extracts class name + message |

---

## 2. Architectural Map

### 2.1 Module Decomposition

```
agpds/
├── __init__.py      ← Re-exports all 15 public symbols
├── exceptions.py    ← Exception hierarchy: 1 base + 10 concrete classes
│                       No internal imports. No external deps.
├── models.py        ← Data classes: DimensionGroup, OrthogonalPair, GroupDependency
│                       No imports from exceptions.py or simulator.py.
└── simulator.py     ← FactTableSimulator class: constructor + 7 empty registries
                        Imports from: models.py (type annotations only)
```

**Decomposition rationale:** The three implementation modules are separated along a responsibility boundary that minimizes coupling and maximizes independent testability. `exceptions.py` is a leaf with zero dependencies — it can be imported in any context (sandbox, test harness, LLM feedback loop) without pulling in numpy or pandas. `models.py` is also a leaf — pure data containers that trust their callers for validation. `simulator.py` depends on `models.py` for type annotations but not on `exceptions.py` in Sprint 1 (it uses built-in `TypeError`/`ValueError`; SDK exceptions are imported starting in Sprint 2). This acyclic import structure means any module can be tested in isolation, and the heaviest dependency chains (numpy, pandas, scipy) are deferred to later sprints.

### 2.2 Dependency Web

```
Import DAG (acyclic):

  exceptions.py  ←─── (no internal imports)
                                              ╲
  models.py      ←─── (no internal imports)    ──→  __init__.py (re-exports 15 symbols)
                                              ╱
  simulator.py   ←─── models.py ─────────────╱

Specific edge:
  simulator.py line 22 → agpds.models: DimensionGroup, OrthogonalPair, GroupDependency
                          (used as type annotations for _groups, _orthogonal_pairs,
                           _group_dependencies registries)
```

Notable: `simulator.py` does **not** import from `exceptions.py` in Sprint 1. The constructor raises built-in `TypeError`/`ValueError`, not SDK exceptions. Sprint 2+ will add `exceptions.py` imports when declaration methods need to raise `EmptyValuesError`, `DuplicateColumnError`, etc.

### 2.3 Hierarchical Tree

```
Sprint 1: Foundation — Data Structures, Constructor, Exception Hierarchy
│
├── Module: __init__.py
│   └── Block: Package re-exports + __all__                       [lines 1–41]        §A
│
├── Module: exceptions.py
│   ├── Block: Module docstring + numbering convention note        [lines 1–32]        §B.0
│   │
│   ├── Class: SimulatorError(Exception)                          [lines 37–45]        §B.1
│   │
│   ├── Class: CyclicDependencyError(SimulatorError)              [lines 50–72]        §B.2
│   │   └── Method: __init__(self, cycle_path)                    [lines 64–72]
│   │       ├── Block: Store raw cycle path                       [lines 65–66]        §B.2a
│   │       └── Block: Build arrow-separated message + super()    [lines 68–72]        §B.2b
│   │
│   ├── Class: UndefinedEffectError(SimulatorError)               [lines 75–98]        §B.3
│   │   └── Method: __init__(self, effect_name, missing_value)    [lines 88–98]
│   │       ├── Block: Store fields                               [lines 89–91]        §B.3a
│   │       └── Block: Format message + super()                   [lines 93–98]        §B.3b
│   │
│   ├── Class: NonRootDependencyError(SimulatorError)             [lines 101–124]      §B.4
│   │   └── Method: __init__(self, column_name)                   [lines 114–124]
│   │       ├── Block: Store column name                          [lines 115–116]      §B.4a
│   │       └── Block: Format message + super()                   [lines 118–124]      §B.4b
│   │
│   ├── Class: InvalidParameterError(SimulatorError)              [lines 132–157]      §B.5
│   │   └── Method: __init__(self, param_name, value, reason)     [lines 148–157]
│   │       ├── Block: Store all fields                           [lines 149–152]      §B.5a
│   │       └── Block: Format message + super()                   [lines 154–157]      §B.5b
│   │
│   ├── Class: DuplicateColumnError(SimulatorError)               [lines 160–180]      §B.6
│   │   └── Method: __init__(self, column_name)                   [lines 174–180]
│   │       ├── Block: Store field                                [line 175]           §B.6a
│   │       └── Block: Format message + super()                   [lines 176–180]      §B.6b
│   │
│   ├── Class: EmptyValuesError(SimulatorError)                   [lines 183–201]      §B.7
│   │   └── Method: __init__(self, column_name)                   [lines 195–201]
│   │       ├── Block: Store field                                [line 196]           §B.7a
│   │       └── Block: Format message + super()                   [lines 197–201]      §B.7b
│   │
│   ├── Class: WeightLengthMismatchError(SimulatorError)          [lines 204–226]      §B.8
│   │   └── Method: __init__(self, column_name, n_values, n_weights)  [lines 218–226]
│   │       ├── Block: Store fields                               [lines 219–221]      §B.8a
│   │       └── Block: Format message + super()                   [lines 222–226]      §B.8b
│   │
│   ├── Class: DegenerateDistributionError(SimulatorError)        [lines 229–249]      §B.9
│   │   └── Method: __init__(self, column_name, detail)           [lines 243–249]
│   │       ├── Block: Store fields                               [lines 244–245]      §B.9a
│   │       └── Block: Format message + super()                   [lines 246–249]      §B.9b
│   │
│   ├── Class: ParentNotFoundError(SimulatorError)                [lines 252–274]      §B.10
│   │   └── Method: __init__(self, child_name, parent_name, group) [lines 266–274]
│   │       ├── Block: Store fields                               [lines 267–269]      §B.10a
│   │       └── Block: Format message + super()                   [lines 270–274]      §B.10b
│   │
│   └── Class: DuplicateGroupRootError(SimulatorError)            [lines 277–302]      §B.11
│       └── Method: __init__(self, group_name, existing_root, attempted_root) [lines 292–302]
│           ├── Block: Store fields                               [lines 295–297]      §B.11a
│           └── Block: Format message + super()                   [lines 298–302]      §B.11b
│
├── Module: models.py
│   ├── Block: Module docstring + imports + logger                [lines 1–21]         §C.0
│   │
│   ├── Class: DimensionGroup (dataclass)                         [lines 26–80]        §C.1
│   │   ├── Block: Dataclass field declarations                   [lines 45–48]        §C.1a
│   │   ├── Method: to_metadata(self)                             [lines 50–70]
│   │   │   └── Block: Defensive-copy return                      [lines 67–70]        §C.1b
│   │   └── Method: __repr__(self)                                [lines 75–80]        §C.1c
│   │
│   ├── Class: OrthogonalPair (dataclass)                         [lines 85–173]       §C.2
│   │   ├── Block: Dataclass field declarations                   [lines 105–107]      §C.2a
│   │   ├── Method: __eq__(self, other)                           [lines 109–125]
│   │   │   ├── Block: Type guard                                 [lines 118–120]      §C.2b
│   │   │   └── Block: Order-independent frozenset comparison     [lines 122–125]      §C.2c
│   │   ├── Method: __hash__(self)                                [lines 127–135]
│   │   │   └── Block: Frozenset hash                             [line 135]           §C.2d
│   │   ├── Method: to_metadata(self)                             [lines 137–149]
│   │   │   └── Block: Dict literal return                        [lines 145–149]      §C.2e
│   │   ├── Method: involves_group(self, group_name)              [lines 155–166]
│   │   │   └── Block: Membership check                           [line 166]           §C.2f
│   │   └── Method: group_pair_set(self)                          [lines 168–173]
│   │       └── Block: Frozenset construction                     [line 173]           §C.2g
│   │
│   └── Class: GroupDependency (dataclass)                        [lines 178–231]      §C.3
│       ├── Block: Dataclass field declarations                   [lines 199–201]      §C.3a
│       ├── Method: to_metadata(self)                             [lines 203–221]
│       │   └── Block: Deep-copy return                           [lines 215–221]      §C.3b
│       └── Method: __repr__(self)                                [lines 225–231]      §C.3c
│
└── Module: simulator.py
    ├── Block: Module docstring + imports + logger                [lines 1–24]         §D.0
    │
    └── Class: FactTableSimulator                                 [lines 27–151]       §D.1
        └── Method: __init__(self, target_rows, seed)             [lines 54–151]
            ├── Block: Type check target_rows                     [lines 68–87]        §D.1a
            ├── Block: Type check seed                            [lines 89–93]        §D.1b
            ├── Block: Value check target_rows > 0                [lines 95–99]        §D.1c
            ├── Block: Assign target_rows, seed + debug log       [lines 101–111]      §D.1d
            ├── Block: _columns (OrderedDict)                     [lines 115–119]      §D.1e
            ├── Block: _groups (dict → DimensionGroup)            [lines 121–124]      §D.1f
            ├── Block: _orthogonal_pairs (list → OrthogonalPair)  [lines 126–128]      §D.1g
            ├── Block: _group_dependencies (list → GroupDependency) [lines 130–133]    §D.1h
            ├── Block: _patterns (list → dict)                    [lines 135–138]      §D.1i
            ├── Block: _realism_config (Optional dict)            [lines 140–143]      §D.1j
            └── Block: _measure_dag (dict → list)                 [lines 145–151]      §D.1k
```

> **Anchor convention:** Each block is tagged with a section anchor (§A, §B.1, §C.2c, §D.1a, etc.) for cross-referencing from traces in Section 4.

---

## 3. Block-Level Reference

### 3.1 `__init__.py`

---

#### §A · `__init__.py` → [Package Re-exports + `__all__`] (lines 1–41)

**Spec anchor:** Infrastructure — enables the `from agpds import FactTableSimulator` pattern used in §2.5.

**Purpose:** Central re-export hub that surfaces all 15 public symbols from the three implementation modules so external callers can import from the package root.

**Mechanics:**

- Lines 6–18: imports all 11 exception classes from `agpds.exceptions`, ordered base-first.
- Line 19: imports three dataclasses from `agpds.models`.
- Line 20: imports `FactTableSimulator` from `agpds.simulator`.
- Lines 22–41: `__all__` mirrors the import order, controlling `from agpds import *`.

**Connects to:**

- Upstream: reads from `exceptions.py`, `models.py`, `simulator.py`.
- Downstream: every external consumer imports through this file.

**Invariant maintained:** `dir(agpds)` includes exactly the 15 names in `__all__`. No internal implementation details leak.

**Breakage scenario:** If `DuplicateGroupRootError` were omitted from lines 6–18 but left in `__all__`, `from agpds import *` would raise `NameError`. Sprint 2's `add_category` (subtask 1.2.6) would be unable to import the exception it needs.

---

### 3.2 `exceptions.py`

---

#### §B.0 · `exceptions.py` → [Module Docstring + Numbering Convention Note] (lines 1–32)

**Spec anchor:** §2.7 (error taxonomy overview) / subtasks 6.1.1–6.1.4

**Purpose:** Documents the complete error taxonomy as a quick-reference index and resolves a traceability ambiguity between sprint plan IDs and post-audit renumbered IDs.

**Mechanics:**

- Lines 1–26: module docstring enumerates all 10 concrete exception classes with their one-line purpose and §2.7 trace.
- Lines 5–8: documents that sprint plan numbering (6.1.1–6.1.4) is used throughout, noting the post-audit renumbering once here (self-review item 9).
- Line 32: `from __future__ import annotations` enables `list[str]` syntax on all supported Python versions. No other imports — zero external dependencies.

**Connects to:**

- Upstream: nothing — leaf module.
- Downstream: every class below inherits from `SimulatorError` (line 37).

**Invariant maintained:** The module is importable with zero side effects and zero external dependencies.

**Breakage scenario:** If `from __future__ import annotations` were removed on Python 3.9, `list[str]` in `CyclicDependencyError.__init__` (line 64) would raise `TypeError` at class definition time, making the entire hierarchy unimportable.

---

#### §B.1 · `exceptions.py` → `SimulatorError` (lines 37–45)

**Spec anchor:** §2.7 (feedback loop blanket catch) / subtask 6.1.1

**Purpose:** Single catch-all base class for the SDK error taxonomy, enabling `except SimulatorError` in the §2.7 feedback loop.

**Mechanics:**

- Empty class body inheriting from `Exception`. Contributes no behavior — its value is purely taxonomic.
- Inherits from `Exception` (not `ValueError`) to avoid polluting the `ValueError` catch namespace.

**Connects to:**

- Upstream: Python's built-in `Exception`.
- Downstream: all 10 concrete exception classes inherit from this.

**Invariant maintained:** `issubclass(X, SimulatorError)` is `True` for all 10 concrete classes. `issubclass(SimulatorError, ValueError)` is `False`.

**Breakage scenario:** If `SimulatorError` inherited from `ValueError`, a Sprint 5 engine doing `except ValueError: retry_sampling()` would silently swallow `CyclicDependencyError`, suppressing the cycle.

---

#### §B.2a · `exceptions.py` → `CyclicDependencyError.__init__()` → [Store raw cycle path] (lines 65–66)

**Spec anchor:** §2.7 step 4 / subtask 6.1.1

**Purpose:** Preserves the raw cycle path as a structured attribute for programmatic access by the feedback loop.

**Mechanics:**

- Line 64: constructor takes `cycle_path: list[str]`.
- Line 66: `self.cycle_path = cycle_path` — stored by reference, no copy.

**Connects to:**

- Upstream: Sprint 4's `topological_sort()` (subtask 3.1.2) constructs the cycle path during DFS.
- Downstream: feeds into §B.2b for message formatting; Sprint 8 reads `e.cycle_path`.

**Invariant maintained:** `self.cycle_path` is the caller-provided list.

**Breakage scenario:** Without `self.cycle_path`, Sprint 8 would need to regex-parse the message to extract cycle nodes.

---

#### §B.2b · `exceptions.py` → `CyclicDependencyError.__init__()` → [Build arrow-separated message + `super()`] (lines 68–72)

**Spec anchor:** §2.7 step 4 example format / subtask 6.1.1

**Purpose:** Composes the §2.7-conformant error message using Unicode arrows and registers it via `super().__init__()`.

**Mechanics:**

- Line 70: `arrow_chain = " → ".join(f"'{node}'" for node in cycle_path)` — joins single-quoted names with ` → ` (U+2192).
- Line 71: `self.message = f"Measure {arrow_chain} forms a cycle."` — e.g., `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."`
- Line 72: `super().__init__(self.message)` → sets `self.args = (message,)`.

**Connects to:**

- Upstream: reads `cycle_path` from §B.2a.
- Downstream: `str(e)` returns the formatted message.

**Invariant maintained:** `str(CyclicDependencyError(["A","B","A"]))` matches the §2.7 example format. Self-cycles produce valid messages.

**Breakage scenario:** ASCII `" -> "` instead of Unicode `" → "` would fail tests asserting exact §2.7 conformance.

---

#### §B.3a · `exceptions.py` → `UndefinedEffectError.__init__()` → [Store fields] (lines 89–91)

**Spec anchor:** §2.7 step 4 / subtask 6.1.2

**Purpose:** Preserves `effect_name` and `missing_value` separately for programmatic access.

**Mechanics:**

- Line 88: constructor takes `effect_name: str`, `missing_value: str`.
- Lines 90–91: stores both as instance attributes.

**Connects to:**

- Upstream: Sprint 3's `add_measure_structural` (subtask 1.5.3).
- Downstream: §B.3b message formatting.

**Invariant maintained:** Both fields stored without transformation.

**Breakage scenario:** Without separate fields, feedback formatter must regex-parse the message.

---

#### §B.3b · `exceptions.py` → `UndefinedEffectError.__init__()` → [Format message + `super()`] (lines 93–98)

**Spec anchor:** §2.7 step 4 / subtask 6.1.2

**Purpose:** Formats `"'severity_surcharge' in formula has no definition for 'Severe'."` — matching §2.7 verbatim.

**Mechanics:**

- Lines 95–97: f-string composing effect name and missing value.
- Line 98: `super().__init__(self.message)`.

**Connects to:** Upstream: §B.3a. Downstream: `str(e)`.

**Invariant maintained:** Message matches §2.7 example exactly.

**Breakage scenario:** Omitting the trailing period would fail exact-match assertions.

---

#### §B.4a · `exceptions.py` → `NonRootDependencyError.__init__()` → [Store column name] (lines 115–116)

**Spec anchor:** §2.2 root-only constraint / §2.7 step 4 / subtask 6.1.3

**Purpose:** Preserves the offending non-root column name.

**Mechanics:** Line 116: `self.column_name = column_name`.

**Connects to:** Upstream: Sprint 3's `add_group_dependency` (subtask 1.7.1). Downstream: §B.4b.

**Invariant maintained:** `self.column_name` is the rejected column.

**Breakage scenario:** Storing `group_name` instead of `column_name` would tell the LLM which group but not which specific non-root column to fix.

---

#### §B.4b · `exceptions.py` → `NonRootDependencyError.__init__()` → [Format message + `super()`] (lines 118–124)

**Spec anchor:** §2.7 step 4 / subtask 6.1.3

**Purpose:** Formats `"'department' is not a group root; cannot use in add_group_dependency."` — naming both the column and the API method.

**Mechanics:** Lines 120–123: two-part f-string. Line 124: `super().__init__(self.message)`.

**Connects to:** Upstream: §B.4a. Downstream: `str(e)`.

**Invariant maintained:** Message names the API method (`add_group_dependency`), giving the LLM enough context.

**Breakage scenario:** Omitting the method name would leave the LLM unsure which API call to modify.

---

#### §B.5a · `exceptions.py` → `InvalidParameterError.__init__()` → [Store all fields] (lines 149–152)

**Spec anchor:** §2.7 "degenerate distributions" / subtask 6.1.4 / Assumption A5a

**Purpose:** Preserves `param_name`, `value` (float), and `reason` for targeted repair instructions.

**Mechanics:** Lines 149–152: stores all three. `value` is typed `float` for numeric comparisons.

**Connects to:** Upstream: future Sprint 3 `add_measure` (1.4.3, BLOCKED) and Sprint 5 engine (4.2.1). Downstream: §B.5b.

**Invariant maintained:** Three-field structure supports instructions like "sigma evaluated to -0.5; adjust effects."

**Breakage scenario:** Storing `value` as string would prevent numeric comparisons in downstream repair logic.

---

#### §B.5b · `exceptions.py` → `InvalidParameterError.__init__()` → [Format message + `super()`] (lines 154–157)

**Spec anchor:** §2.7 / subtask 6.1.4

**Purpose:** Formats `"Parameter 'sigma' has invalid value -0.5: must be > 0."`.

**Mechanics:** Lines 154–156: f-string with all three components. Line 157: `super().__init__()`.

**Connects to:** Upstream: §B.5a. Downstream: `str(e)`.

**Invariant maintained:** Message contains parameter name, value, and reason.

**Breakage scenario:** Omitting `value` would prevent the LLM from knowing what the intercept+effects computed to.

---

#### §B.6a–§B.11b · `exceptions.py` → Remaining Validation Errors (lines 160–302)

The six classes `DuplicateColumnError`, `EmptyValuesError`, `WeightLengthMismatchError`, `DegenerateDistributionError`, `ParentNotFoundError`, and `DuplicateGroupRootError` follow the identical two-block pattern: **store fields** → **format message + `super()`**. Each targets a specific declaration-time failure:

| Anchor | Class | Fields Stored | Invariant | Anticipated Raise Site |
|--------|-------|--------------|-----------|----------------------|
| §B.6 | `DuplicateColumnError` | `column_name` | Column names unique across all groups | Sprint 2 `add_category` (1.2.1) |
| §B.7 | `EmptyValuesError` | `column_name` | Categorical values list non-empty (§2.1.1) | Sprint 2 `add_category` (1.2.1) |
| §B.8 | `WeightLengthMismatchError` | `column_name`, `n_values`, `n_weights` | Weight vector dimensionality matches value count | Sprint 2 `add_category` (1.2.1) |
| §B.9 | `DegenerateDistributionError` | `column_name`, `detail` | Distribution params non-degenerate (§2.7) | Sprint 3 `add_measure` (1.4.3) |
| §B.10 | `ParentNotFoundError` | `child_name`, `parent_name`, `group` | Parent exists in same group (§2.1.1) | Sprint 2 `add_category` (1.2.4) |
| §B.11 | `DuplicateGroupRootError` | `group_name`, `existing_root`, `attempted_root` | Single root per group (§2.2) | Sprint 2 `add_category` (1.2.6) |

Key design decisions across all six:

- **Multi-field storage** enables programmatic access. `ParentNotFoundError` stores three fields (`child_name`, `parent_name`, `group`) because the error involves a relationship between two columns within a named group — any one field alone is insufficient.
- **DuplicateColumnError** specifies "across all groups" in its message because DAG nodes are identified by column name alone — `"status"` in group `"entity"` and `"status"` in group `"patient"` would collide.
- **DuplicateGroupRootError** stores both the existing root and the attempted root, giving the LLM two repair paths: (1) add `parent=existing_root` to the new column, or (2) move it to a different group.

---

### 3.3 `models.py`

---

#### §C.0 · `models.py` → [Module Docstring + Imports + Logger] (lines 1–21)

**Spec anchor:** §2.2, §2.6 / subtasks 2.1.1, 2.2.1, 2.2.2

**Purpose:** Establishes the module as pure data containers with serialization support; declares the design boundary that validation happens in `simulator.py`.

**Mechanics:**

- Lines 1–13: docstring states "Validation of the *values* stored in these classes happens in the SDK class (simulator.py), not here."
- Line 18: `from dataclasses import dataclass, field` — `field(default_factory=list)` prevents the shared-mutable-default bug.
- Line 19: `from typing import Any` — used in `to_metadata()` return types for the §2.6 mixed-type JSON structure.
- Line 21: `logger = logging.getLogger(__name__)` — unused in Sprint 1, present for Sprint 2+ warnings.

**Connects to:** Upstream: none. Downstream: `simulator.py` imports all three classes.

**Invariant maintained:** Module importable with only stdlib dependencies.

**Breakage scenario:** Removing `from typing import Any` would break `to_metadata() -> dict[str, Any]` annotations.

---

#### §C.1a · `models.py` → `DimensionGroup` → [Dataclass Field Declarations] (lines 45–48)

**Spec anchor:** §2.2 (dimension groups) / subtask 2.1.1

**Purpose:** Defines the four fields representing a named group's structure.

**Mechanics:**

- `name: str` — group identifier (e.g., `"entity"`). Required.
- `root: str` — root column name (e.g., `"hospital"`). Required.
- `columns: list[str] = field(default_factory=list)` — all columns, insertion-ordered. Uses `default_factory` to avoid the shared-mutable-default bug.
- `hierarchy: list[str] = field(default_factory=list)` — root-first parent→child ordering.

**Connects to:** Upstream: constructed by Sprint 2's `add_category`/`add_temporal`. Downstream: §C.1b `to_metadata()`, Sprint 5 engine.

**Invariant maintained:** Two independent mutable lists per instance. `DimensionGroup(name="x", root="y")` produces an instance with empty-but-independent lists.

**Breakage scenario:** `columns: list[str] = []` instead of `field(default_factory=list)` would share one list object across all instances — appending to one group's columns would appear in every group.

---

#### §C.1b · `models.py` → `DimensionGroup.to_metadata()` → [Defensive-copy return] (lines 67–70)

**Spec anchor:** §2.6 (dimension_groups block) / subtask 2.1.1

**Purpose:** Serializes to `{"columns": [...], "hierarchy": [...]}` while protecting internal state with `list()` copies.

**Mechanics:** `list(self.columns)` and `list(self.hierarchy)` create shallow copies. Strings are immutable, so shallow copy is effectively full copy.

**Connects to:** Upstream: reads `self.columns`, `self.hierarchy`. Downstream: Sprint 5 metadata emitter (subtask 5.1.1).

**Invariant maintained:** Returned dict is detached — mutations do not affect internal state.

**Breakage scenario:** Returning `self.columns` directly would let Sprint 5's metadata emitter inadvertently reorder the group's column list.

---

#### §C.1c · `models.py` → `DimensionGroup.__repr__()` (lines 75–80)

**Spec anchor:** Infrastructure — additive debugging aid.

**Purpose:** Readable repr including name, root, columns. Omits hierarchy for conciseness.

**Invariant maintained:** None beyond readability. No side effects.

---

#### §C.2a · `models.py` → `OrthogonalPair` → [Dataclass Field Declarations] (lines 105–107)

**Spec anchor:** §2.2 (cross-group orthogonality) / subtask 2.2.1

**Purpose:** Three required fields: `group_a`, `group_b`, `rationale`. No defaults — all must be provided.

**Connects to:** Upstream: Sprint 3 `declare_orthogonal`. Downstream: `__eq__`, `__hash__`, `to_metadata`.

**Invariant maintained:** All three fields non-None (no defaults).

**Breakage scenario:** If `rationale` had a default of `""`, LLM code could omit it, bypassing §2.5's constraint.

---

#### §C.2b · `models.py` → `OrthogonalPair.__eq__()` → [Type guard] (lines 118–120)

**Spec anchor:** §2.2 / subtask 2.2.1

**Purpose:** Returns `NotImplemented` for non-`OrthogonalPair` comparisons, following Python's cooperative comparison protocol.

**Mechanics:** `if not isinstance(other, OrthogonalPair): return NotImplemented`. Returning `NotImplemented` (not `False`) allows Python to try the other object's `__eq__`.

**Breakage scenario:** `return False` instead of `NotImplemented` would prevent cooperative comparison from the other side.

---

#### §C.2c · `models.py` → `OrthogonalPair.__eq__()` → [Order-independent frozenset comparison] (lines 122–125)

**Spec anchor:** §2.2 / subtask 2.2.1 (done condition: `Pair("a","b","r") == Pair("b","a","r")`)

**Purpose:** Implements order-independent equality: (A, B) ≡ (B, A). Rationale excluded from equality.

**Mechanics:** `frozenset((self.group_a, self.group_b)) == frozenset((other.group_a, other.group_b))`.

**Invariant maintained:** `Pair("entity","patient","r1") == Pair("patient","entity","r2")` is `True`.

**Breakage scenario:** Tuple equality `(a,b) == (a,b)` would be order-dependent. Sprint 3's `if pair in self._orthogonal_pairs` would miss reversed-order duplicates.

---

#### §C.2d · `models.py` → `OrthogonalPair.__hash__()` → [Frozenset hash] (line 135)

**Spec anchor:** §2.2 / subtask 2.2.1

**Purpose:** Hash consistent with order-independent `__eq__`, required for set/dict usage.

**Mechanics:** `hash(frozenset((self.group_a, self.group_b)))`.

**Invariant maintained:** `hash(Pair("a","b")) == hash(Pair("b","a"))`. The `__hash__`/`__eq__` contract holds.

**Breakage scenario:** `hash((a,b))` (tuple hash) with frozenset `__eq__` would produce unequal hashes for equal objects, corrupting set operations.

---

#### §C.2e · `models.py` → `OrthogonalPair.to_metadata()` → [Dict literal return] (lines 145–149)

**Spec anchor:** §2.6 (orthogonal_groups block) / subtask 2.2.1

**Purpose:** Returns `{"group_a": ..., "group_b": ..., "rationale": ...}`. All strings — no copy needed.

**Invariant maintained:** Keys match §2.6 example exactly.

**Breakage scenario:** Key `"a"` instead of `"group_a"` → `KeyError` in Sprint 6's L1 chi-squared check.

---

#### §C.2f · `models.py` → `OrthogonalPair.involves_group()` → [Membership check] (line 166)

**Spec anchor:** Infrastructure — Sprint 3 conflict detection (subtasks 1.6.3 / 1.7.4).

**Purpose:** Tests if a group name participates in this pair.

**Mechanics:** `return group_name in (self.group_a, self.group_b)`.

---

#### §C.2g · `models.py` → `OrthogonalPair.group_pair_set()` → [Frozenset construction] (line 173)

**Spec anchor:** Infrastructure — efficient O(1) lookups.

**Purpose:** Returns `frozenset((group_a, group_b))` for set-based conflict detection.

**Breakage scenario:** Returning a tuple would make set lookups order-dependent.

---

#### §C.3a · `models.py` → `GroupDependency` → [Dataclass Field Declarations] (lines 199–201)

**Spec anchor:** §2.2 (cross-group dependency), §2.1.2 / subtask 2.2.2

**Purpose:** Three required fields: `child_root: str`, `on: list[str]`, `conditional_weights: dict[str, dict[str, float]]`.

**Mechanics:**

- `on` is a list for forward compatibility, though Sprint 3 assumption A7 restricts to single-column.
- `conditional_weights` is stored by reference (standard dataclass behavior) — this is Limitation 2 documented in the walkthrough.

**Connects to:** Upstream: Sprint 3 `add_group_dependency`. Downstream: §C.3b `to_metadata()`, Sprint 5 engine (sampling), Sprint 6 L2 validator.

**Invariant maintained:** All three fields required, non-None.

**Breakage scenario:** Default `on=[]` would let callers create a dependency without specifying what it's conditional on.

---

#### §C.3b · `models.py` → `GroupDependency.to_metadata()` → [Deep-copy return] (lines 215–221)

**Spec anchor:** §2.6 (group_dependencies block) / subtask 2.2.2

**Purpose:** Serializes with deep copies to protect internal state — critical because `conditional_weights` is a nested dict.

**Mechanics:**

- `list(self.on)` — shallow copy, sufficient for `list[str]`.
- `{k: dict(v) for k, v in self.conditional_weights.items()}` — creates new outer dict AND new inner dicts. This is the self-review item 5 fix.

**Connects to:** Upstream: reads all three fields. Downstream: Sprint 5 metadata emitter (subtask 5.1.3). Pre-emptively fixes SPEC_INCORRECT C9 by including `conditional_weights`.

**Invariant maintained:** Returned structure fully detached from `self`. Mutations to returned metadata do not affect internal state.

**Breakage scenario:** Pre-fix shallow copy `dict(self.conditional_weights)` would share inner dicts. Sprint 5's metadata emitter rounding weights for display would corrupt the engine's sampling weights.

---

#### §C.3c · `models.py` → `GroupDependency.__repr__()` (lines 225–231)

**Spec anchor:** Infrastructure — debugging aid.

**Purpose:** Concise repr showing entry count instead of full nested dict.

---

### 3.4 `simulator.py`

---

#### §D.0 · `simulator.py` → [Module Docstring + Imports + Logger] (lines 1–24)

**Spec anchor:** §2.8 / subtasks 1.1.1, 1.1.2

**Purpose:** Establishes the module, imports model classes for type annotations, sets up logging.

**Mechanics:**

- Line 19: `from collections import OrderedDict` — makes insertion-order guarantee explicit.
- Line 22: `from agpds.models import DimensionGroup, OrthogonalPair, GroupDependency` — the sole cross-module import. Used for type annotations only in Sprint 1.
- Does NOT import from `exceptions.py` — Sprint 1 constructor uses built-in exceptions.

**Invariant maintained:** Single cross-module dependency: `agpds.models`.

**Breakage scenario:** Replacing `OrderedDict` with `dict` would lose the explicit ordering contract — a future contributor might substitute an unordered mapping.

---

#### §D.1a · `simulator.py` → `FactTableSimulator.__init__()` → [Type check `target_rows`] (lines 68–87)

**Spec anchor:** §2.5 one-shot example / subtask 1.1.1

**Purpose:** Rejects non-integer `target_rows` (including bools) with `TypeError`.

**Mechanics:**

- Line 84: `if not isinstance(target_rows, int) or isinstance(target_rows, bool):` — two-part guard. The bool check is necessary because `bool` is a subclass of `int` in Python: `isinstance(True, int)` returns `True`.
- Lines 85–87: `raise TypeError(f"target_rows must be an int, got {type(target_rows).__name__}.")`
- Uses built-in `TypeError` (not `SimulatorError`) because constructor arg-type checking is Python convention, not SDK semantic validation (self-review item 6).

**Connects to:** Upstream: caller input. Downstream: if passes, proceeds to §D.1b.

**Invariant maintained:** `target_rows` is a Python `int` (not `bool`, `float`, `str`, `None`).

**Breakage scenario:** Without bool rejection, `FactTableSimulator(True, 42)` sets `target_rows=True` (i.e., `1`). L1 row-count check later: `abs(500-1)/1 < 0.1` → `False` — confusing.

---

#### §D.1b · `simulator.py` → `FactTableSimulator.__init__()` → [Type check `seed`] (lines 89–93)

**Spec anchor:** §2.8 / subtask 1.1.1

**Purpose:** Same pattern as §D.1a for `seed`. Rejects non-int and bool.

**Mechanics:** Identical to §D.1a. Raises `TypeError`.

**Invariant maintained:** `seed` is a Python `int` (not `bool`). Negative seeds are allowed.

**Breakage scenario:** `FactTableSimulator(500, 42.7)` → `np.random.default_rng(42.7)` would raise `TypeError` deep in numpy, far from origin.

---

#### §D.1c · `simulator.py` → `FactTableSimulator.__init__()` → [Value check `target_rows > 0`] (lines 95–99)

**Spec anchor:** §2.4 / subtask 1.1.1

**Purpose:** Rejects zero and negative `target_rows`.

**Mechanics:**

- Line 96: `if target_rows <= 0:` — safe because §D.1a guarantees `target_rows` is `int`.
- Lines 97–99: `raise ValueError(f"target_rows must be a positive integer, got {target_rows}.")`
- Check ordering is load-bearing: type checks (§D.1a, §D.1b) BEFORE value check. If reversed, `"500" <= 0` raises confusing `TypeError` from Python's comparison operators.

**Connects to:** Upstream: receives type-validated `target_rows`. Downstream: §D.1d attribute assignment.

**Invariant maintained:** `target_rows ∈ {1, 2, 3, ...}`.

**Breakage scenario:** `FactTableSimulator(0, 42)` → engine iterates `range(0)` → zero rows → L1 row-count computes `0/0` → `ZeroDivisionError`.

---

#### §D.1d · `simulator.py` → `FactTableSimulator.__init__()` → [Assign `target_rows`, `seed` + debug log] (lines 101–111)

**Spec anchor:** §2.5 one-shot example / §2.8 / subtask 1.1.1

**Purpose:** Stores the two public attributes and logs initialization.

**Mechanics:**

- Lines 104–105: `self.target_rows: int = target_rows`, `self.seed: int = seed`. Only two public attributes.
- Lines 107–111: `logger.debug(...)` with `%d` format (lazy evaluation convention).

**Connects to:** Upstream: validated values from §D.1a–§D.1c. Downstream: `self.target_rows` read by Sprint 5 engine; `self.seed` read by `generate()` for `np.random.default_rng`.

**Invariant maintained:** `self.target_rows` is a positive int, `self.seed` is an int.

**Breakage scenario:** Using f-string in logging would format the string on every call even when DEBUG is disabled.

---

#### §D.1e · `simulator.py` → `FactTableSimulator.__init__()` → [`_columns` (OrderedDict)] (lines 115–119)

**Spec anchor:** §2.6 (column ordering), §2.4 (topological sort tie-breaking) / subtask 1.1.2

**Purpose:** Primary column registry. `OrderedDict` makes insertion-order guarantee explicit.

**Mechanics:** `self._columns: OrderedDict[str, dict[str, Any]] = OrderedDict()`. Keys: column names. Values: metadata dicts (schema varies by type).

**Connects to:** Downstream: Sprint 2 `add_category` inserts; Sprint 4 DAG construction iterates; Sprint 5 metadata emitter reads.

**Invariant maintained:** Empty `OrderedDict`.

**Breakage scenario:** Non-ordered mapping would break §2.8's "bit-for-bit reproducible" guarantee via nondeterministic tie-breaking.

---

#### §D.1f · `simulator.py` → `FactTableSimulator.__init__()` → [`_groups`] (lines 121–124)

**Spec anchor:** §2.2 / subtask 1.1.2

**Purpose:** Group registry mapping names to `DimensionGroup` instances.

**Mechanics:** `self._groups: dict[str, DimensionGroup] = {}`. Plain `dict` — group ordering doesn't affect generation.

**Invariant maintained:** Empty dict.

---

#### §D.1g · `simulator.py` → `FactTableSimulator.__init__()` → [`_orthogonal_pairs`] (lines 126–128)

**Spec anchor:** §2.2 / subtask 1.1.2

**Purpose:** List of `OrthogonalPair` declarations. List (not set) preserves declaration order for metadata.

**Invariant maintained:** Empty list.

---

#### §D.1h · `simulator.py` → `FactTableSimulator.__init__()` → [`_group_dependencies`] (lines 130–133)

**Spec anchor:** §2.2 / subtask 1.1.2

**Purpose:** List of `GroupDependency` declarations. Consumed by engine (sampling) and validator (L2).

**Invariant maintained:** Empty list.

---

#### §D.1i · `simulator.py` → `FactTableSimulator.__init__()` → [`_patterns`] (lines 135–138)

**Spec anchor:** §2.8 Phase γ / subtask 1.1.2

**Purpose:** Pattern spec list. Stored as `list[dict[str, Any]]` (not a dataclass) because four of six pattern types are under-specified (BLOCKED Blocker 4).

**Invariant maintained:** Empty list.

---

#### §D.1j · `simulator.py` → `FactTableSimulator.__init__()` → [`_realism_config`] (lines 140–143)

**Spec anchor:** §2.8 Phase δ / subtask 1.1.2

**Purpose:** `None` until `set_realism()` is called. The None/non-None toggle maps to the `δ?` optional phase.

**Invariant maintained:** `self._realism_config is None`.

**Breakage scenario:** Initialized as `{}` → truthiness check `if self._realism_config:` returns `False` (correct for empty dict) but `is not None` check returns `True` → incorrect Phase δ trigger with no keys → `KeyError`.

---

#### §D.1k · `simulator.py` → `FactTableSimulator.__init__()` → [`_measure_dag`] (lines 145–151)

**Spec anchor:** §2.3 (DAG constraint), §2.4 Step 2 / subtask 1.1.2

**Purpose:** Measure sub-DAG as an adjacency list. Keys: measure names; values: lists of downstream dependents.

**Mechanics:** `self._measure_dag: dict[str, list[str]] = {}`. Populated by Sprint 3's `add_measure` (roots with `[]`) and `add_measure_structural` (appends edges).

**Connects to:** Downstream: Sprint 3 cycle detection, Sprint 4 topological sort, Sprint 5 engine Phase β.

**Invariant maintained:** Empty dict — trivially acyclic.

**Breakage scenario:** Inverted adjacency direction (mapping to upstream deps instead of downstream) would require formula-parsed predecessors at declaration time — but the formula DSL is BLOCKED (Blocker 2).

---

## 4. Data Flow Traces

### Trace 1: Constructing the Simulator with the §2.5 One-Shot Example

**Entry point:** `FactTableSimulator.__init__(target_rows=500, seed=42)`

**Concrete input:** Exact values from §2.5: `sim = FactTableSimulator(target_rows=500, seed=42)`.

#### Happy Path

| Step | Block (§ anchor) | Operation | State After |
|------|-------------------|-----------|-------------|
| 1 | §D.1a — type check `target_rows` | `not isinstance(500, int)` → `False`. `isinstance(500, bool)` → `False`. Condition: `False or False` → `False`. No raise. | `target_rows=500` confirmed `int`, not `bool` |
| 2 | §D.1b — type check `seed` | `not isinstance(42, int)` → `False`. `isinstance(42, bool)` → `False`. No raise. | `seed=42` confirmed `int`, not `bool` |
| 3 | §D.1c — value check | `500 <= 0` → `False`. No raise. | `target_rows=500` confirmed positive |
| 4 | §D.1d — assign + log | `self.target_rows = 500`, `self.seed = 42`. `logger.debug(...)` | Public attributes set |
| 5 | §D.1e | `self._columns = OrderedDict()` | Empty `OrderedDict` |
| 6 | §D.1f | `self._groups = {}` | Empty dict |
| 7 | §D.1g | `self._orthogonal_pairs = []` | Empty list |
| 8 | §D.1h | `self._group_dependencies = []` | Empty list |
| 9 | §D.1i | `self._patterns = []` | Empty list |
| 10 | §D.1j | `self._realism_config = None` | `None` |
| 11 | §D.1k | `self._measure_dag = {}` | Empty dict |

**Cross-module boundary:** Steps 6–8 use type annotations referencing `DimensionGroup`, `OrthogonalPair`, `GroupDependency` imported from `models.py` (§D.0, line 22). These imports are resolved at module load time, not at `__init__` call time. At runtime, only plain Python containers (`{}`, `[]`) are created.

**Final state:**

```python
sim.target_rows          = 500
sim.seed                 = 42
sim._columns             = OrderedDict()    # empty
sim._groups              = {}               # empty
sim._orthogonal_pairs    = []               # empty
sim._group_dependencies  = []               # empty
sim._patterns            = []               # empty
sim._realism_config      = None
sim._measure_dag         = {}               # empty
```

**Return value:** `None` (Python constructor protocol). Caller receives the instance via assignment.

#### Exception Path: `FactTableSimulator(500.0, 42)`

| Step | Block | Operation | State After |
|------|-------|-----------|-------------|
| 1 | §D.1a | `not isinstance(500.0, int)` → `True`. Short-circuit: second condition not evaluated. **RAISES.** | No `self` attributes assigned. |
| 2 | §D.1a | `raise TypeError("target_rows must be an int, got float.")` | Exception propagates. |

**Atomicity verification:** All three validation blocks (§D.1a–§D.1c) execute before any assignment (§D.1d–§D.1k). A `TypeError` on line 84 leaves zero attributes on `self` — accessing `self.target_rows` would raise `AttributeError`. No partial state.

#### Exception Path: `FactTableSimulator(True, 42)` (Bool Edge Case)

| Step | Block | Operation |
|------|-------|-----------|
| 1 | §D.1a | `not isinstance(True, int)` → `False` (bool is int subclass!). Must evaluate second: `isinstance(True, bool)` → `True`. Condition: `False or True` → `True`. **RAISES.** |
| 2 | §D.1a | `raise TypeError("target_rows must be an int, got bool.")` |

This trace proves the bool guard is not redundant. Without it, step 1's condition would be `False`, no raise, and `self.target_rows` would become `True` (silently treated as `1`).

**Design insight:** The validation blocks form a narrowing pipeline: §D.1a narrows to `int ∧ ¬bool`, §D.1b does the same for `seed`, §D.1c narrows to positive. Each block's precondition is the previous block's postcondition. This pipeline pattern means checks are composable and the ordering is load-bearing.

**Fragility assessment:** The most fragile point is the type-before-value ordering. If a future contributor reorders §D.1c before §D.1a (e.g., "check value first for faster rejection"), `FactTableSimulator("500", 42)` would hit `"500" <= 0`, raising `TypeError` from Python's comparison operators with a confusing message instead of the clear constructor message.

---

### Trace 2: Constructing a CyclicDependencyError

**Entry point:** `CyclicDependencyError(["cost", "satisfaction", "cost"])`

**Concrete input:** A three-node cycle from the §2.7 step 4 example.

| Step | Block (§ anchor) | Operation | State After |
|------|-------------------|-----------|-------------|
| 1 | §B.2a — store path | `self.cycle_path = ["cost", "satisfaction", "cost"]` | List stored by reference |
| 2 | §B.2b — join | `" → ".join(["'cost'", "'satisfaction'", "'cost'"])` → `"'cost' → 'satisfaction' → 'cost'"` | `arrow_chain` computed |
| 3 | §B.2b — compose | `f"Measure {arrow_chain} forms a cycle."` | `self.message = "Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."` |
| 4 | §B.2b — super | `SimulatorError.__init__()` → `Exception.__init__()` → `self.args = (message,)` | Exception fully initialized |

**Final state:**

```python
e.cycle_path     = ["cost", "satisfaction", "cost"]
e.message        = "Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."
str(e)           = "Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."
type(e).__name__ = "CyclicDependencyError"
isinstance(e, SimulatorError) = True
isinstance(e, ValueError)     = False
```

**Edge case — self-cycle `["A", "A"]`:** Step 2 produces `"'A' → 'A'"`, step 3 produces `"Measure 'A' → 'A' forms a cycle."` — grammatically valid.

**Downstream consumption preview (Sprint 8):**

```
Sprint 3: simulator.py → add_measure_structural() → detects cycle → raise CyclicDependencyError(path)
Sprint 8: pipeline.py → except SimulatorError as e:
           type(e).__name__  →  "CyclicDependencyError"
           str(e)            →  "Measure 'cost' → ... forms a cycle."
           e.cycle_path      →  ["cost", "satisfaction", "cost"]
           → Build repair instruction → Feed back to LLM
```

**Design insight:** The store-then-format pattern shared by all 10 exceptions serves two audiences simultaneously: the human-readable `self.message` (via `str(e)`) for the LLM's natural-language consumption, and the structured attributes (`e.cycle_path`, `e.effect_name`, etc.) for programmatic repair logic. Neither audience needs to parse the other's format.

**Fragility assessment:** The `"Measure"` prefix in the message is hardcoded. If Sprint 3's root-level DAG acyclicity check (subtask 1.7.3) reuses this exception for root-dependency cycles, the message would say "Measure 'severity' → 'payment_method' → 'severity' forms a cycle" — semantically misleading since these are group roots, not measures. The walkthrough anticipates this: "If Sprint 3 needs 'Group root' phrasing, the message template can be parameterized then."

---

### Trace 3: GroupDependency Construction → `to_metadata()` — Deep-Copy Isolation

**Entry point:** `GroupDependency(child_root=..., on=..., conditional_weights=...)` then `.to_metadata()`

**Concrete input:** The §2.1.2 payment-severity dependency:

```python
original_weights = {
    "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
    "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
    "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
}
dep = GroupDependency(child_root="payment_method", on=["severity"], conditional_weights=original_weights)
meta = dep.to_metadata()
```

| Step | Block (§ anchor) | Operation | State After |
|------|-------------------|-----------|-------------|
| 1 | §C.3a — auto-`__init__` | `self.child_root = "payment_method"` (immutable string) | Stored |
| 2 | §C.3a — auto-`__init__` | `self.on = original_on` — **reference** assignment: `id(self.on) == id(original_on)` | Shared reference with caller |
| 3 | §C.3a — auto-`__init__` | `self.conditional_weights = original_weights` — **reference** assignment | Shared reference with caller (Limitation 2) |
| 4 | §C.3b — `to_metadata()` line 216 | `"child_root": self.child_root` → `"payment_method"` | String, immutable |
| 5 | §C.3b — `to_metadata()` line 217 | `"on": list(self.on)` → new list `["severity"]` | Independent copy |
| 6 | §C.3b — `to_metadata()` lines 218–220 | `{k: dict(v) for k, v in self.conditional_weights.items()}` — creates new outer dict AND new inner dict for each of 3 keys | Fully independent nested copy |

**Deep-copy isolation diagram:**

```
self.conditional_weights:               result["conditional_weights"]:
┌─────────────────────┐                 ┌─────────────────────┐
│ outer dict (id=A)   │                 │ outer dict (id=D)   │  ← NEW
│  "Mild" → (id=B)    │                 │  "Mild" → (id=E)    │  ← NEW inner
│  "Moderate" → (id=C)│                 │  "Moderate" → (id=F)│  ← NEW inner
│  "Severe" → (id=G)  │                 │  "Severe" → (id=H)  │  ← NEW inner
└─────────────────────┘                 └─────────────────────┘
All ids different. Values (0.45, etc.) are immutable floats.
```

**Isolation proof — mutation through metadata does NOT corrupt internal state:**

```python
meta["conditional_weights"]["Mild"]["Insurance"] = 0.99
meta["on"].append("hospital")

dep.conditional_weights["Mild"]["Insurance"]  →  0.45  ✓  (id=E ≠ id=B)
dep.on                                        →  ["severity"]  ✓
```

**Contrast with pre-fix shallow copy:** Before self-review item 5, `dict(self.conditional_weights)` created a new outer dict but shared inner dicts (`id=B == id=E`). Mutation through metadata would have corrupted the engine's sampling weights.

**Final state of `meta`:**

```python
{
    "child_root": "payment_method",
    "on": ["severity"],
    "conditional_weights": {
        "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},
        "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},
        "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10},
    },
}
```

**Design insight:** `GroupDependency` serves two consumers with different access patterns: the Sprint 5 engine reads the live object (`dep.conditional_weights`) for sampling, while the Sprint 6 validator reads the serialized metadata (`meta["conditional_weights"]`). The deep copy at the serialization boundary decouples these consumers. This is an instance of the Interface Segregation Principle — the `to_metadata()` method is the boundary between the "live object" interface and the "serialized contract" interface.

**Fragility assessment:** The construction-time aliasing (Limitation 2) is the most fragile point. If Sprint 3's `add_group_dependency` does not copy the caller's dict before constructing the `GroupDependency`, and the LLM's script mutates the dict after the call (unlikely but possible), the internal state would be corrupted without any error signal. The walkthrough recommends Sprint 3 pass a defensive copy into the constructor.

---

## 5. Invariant Summary Table

| Block (§) | Invariant | Enforced By | Violated By | Downstream Impact |
|-----------|-----------|-------------|-------------|-------------------|
| §A | `__all__` contains exactly 15 symbols matching the import list | `__init__.py` lines 6–41 | Adding a class to `__all__` without importing it | `NameError` on `from agpds import *` |
| §B.0 | Module importable with zero external dependencies | No imports beyond `__future__` | Adding `import numpy` | Breaks sandbox importability (Sprint 8) |
| §B.1 | All 10 exceptions are `SimulatorError` subclasses; `SimulatorError` is not a `ValueError` subclass | Inheritance declaration | Changing base to `ValueError` | Sprint 5 engine's `except ValueError` would swallow SDK errors |
| §B.2b | `str(CyclicDependencyError(path))` matches §2.7 arrow format | Join on `" → "` (U+2192) | Using ASCII `" -> "` | Fails exact §2.7 conformance tests |
| §B.3b | `str(UndefinedEffectError(name, val))` matches §2.7 format | f-string template | Omitting trailing period | Fails exact §2.7 conformance tests |
| §B.4b | Message names the API method `add_group_dependency` | f-string template | Omitting method name | LLM cannot determine which call to fix |
| §C.1a | Each `DimensionGroup` gets independent `columns` and `hierarchy` lists | `field(default_factory=list)` | Using `= []` default | Shared-mutable-default bug: all groups share one list |
| §C.1b | `to_metadata()` returns detached copy | `list()` copy | Returning `self.columns` directly | Metadata mutations corrupt group's column ordering |
| §C.2c | `Pair("a","b") == Pair("b","a")` | `frozenset` comparison | Tuple comparison | Sprint 3 misses reversed-order duplicate declarations |
| §C.2d | `hash(Pair("a","b")) == hash(Pair("b","a"))` | `hash(frozenset(...))` | `hash(tuple(...))` | Set/dict operations produce duplicate entries for equal pairs |
| §C.3b | `to_metadata()` returns deep copy of nested `conditional_weights` | Dict comprehension with `dict(v)` | Shallow copy `dict(self.conditional_weights)` | Metadata mutations corrupt engine's sampling weights |
| §D.1a | `target_rows` is `int`, not `bool` | `isinstance` double-check | Removing bool guard | `True` silently becomes `target_rows=1` |
| §D.1b | `seed` is `int`, not `bool` | `isinstance` double-check | Removing bool guard | `True` becomes `seed=1`, changing RNG stream |
| §D.1c | `target_rows ≥ 1` | `<= 0` guard | Removing guard | `range(0)` → zero rows → `ZeroDivisionError` in L1 |
| §D.1a–c | Validation runs before any assignment | Code ordering: lines 68–99 before 104–151 | Reordering checks after assignments | Partial state on exception: some registries exist, others don't |
| §D.1e | `_columns` preserves insertion order | `OrderedDict` type | Plain `dict` (works in CPython 3.7+ but contract is implicit) | Nondeterministic tie-breaking in topological sort |
| §D.1j | `_realism_config` is `None` until `set_realism()` | Initialized as `None` | Initialized as `{}` | `is not None` check triggers Phase δ with empty config → `KeyError` |
| §D.1k | `_measure_dag` points downstream (key → dependents) | Convention | Inverted direction (key → dependencies) | Formula DSL needed at declaration time (BLOCKED) |

---

## 6. Cross-Sprint Interface Contract

| Exported Symbol | Module | Consumers | Contract (Preconditions → Postconditions) |
|---|---|---|---|
| `FactTableSimulator` | `simulator.py` | Sprint 2 (`add_category`, `add_temporal`), Sprint 3 (`add_measure`, `declare_orthogonal`, `add_group_dependency`), Sprint 4 (DAG construction), Sprint 5 (engine) | Pre: `target_rows` is positive int, `seed` is int. Post: instance has 2 public attrs + 7 empty registries. All registries are fresh mutable containers (no aliasing between instances). |
| `DimensionGroup` | `models.py` | Sprint 2 (create/populate groups), Sprint 5 (metadata via `to_metadata()`), Sprint 5 engine (hierarchy traversal) | Pre: `name` and `root` are non-empty strings. Post: `to_metadata()` returns `{"columns": [...], "hierarchy": [...]}` with detached lists. `columns` and `hierarchy` are independent mutable lists per instance. |
| `OrthogonalPair` | `models.py` | Sprint 3 (`declare_orthogonal`), Sprint 5 (metadata), Sprint 6 (L1 chi-squared) | Pre: `group_a`, `group_b`, `rationale` are strings. Post: `Pair(a,b) == Pair(b,a)` and `hash(Pair(a,b)) == hash(Pair(b,a))`. `to_metadata()` returns `{"group_a": ..., "group_b": ..., "rationale": ...}`. `involves_group(g)` and `group_pair_set()` available for Sprint 3 conflict detection. |
| `GroupDependency` | `models.py` | Sprint 3 (`add_group_dependency`), Sprint 5 (engine sampling + metadata), Sprint 6 (L2 conditional deviation) | Pre: `child_root` is string, `on` is non-empty list of strings, `conditional_weights` is nested dict. Post: `to_metadata()` returns deep copy including `conditional_weights`. **Caveat (Limitation 2):** constructor stores `conditional_weights` by reference — caller should copy if mutation is possible. |
| `SimulatorError` | `exceptions.py` | Sprint 8 (feedback loop blanket catch) | Pre: none. Post: `except SimulatorError as e` catches all SDK exceptions. `type(e).__name__` returns the specific class name. `str(e)` returns the §2.7-formatted message. |
| `CyclicDependencyError` | `exceptions.py` | Sprint 3 (1.5.5), Sprint 4 (3.1.2) | Pre: `cycle_path` is `list[str]` with first == last element. Post: `e.cycle_path` is the raw list. `str(e)` is `"Measure 'X' → 'Y' → 'X' forms a cycle."` |
| `UndefinedEffectError` | `exceptions.py` | Sprint 3 (1.5.3) | Pre: `effect_name` and `missing_value` are strings. Post: `e.effect_name`, `e.missing_value` stored. `str(e)` matches §2.7. |
| `NonRootDependencyError` | `exceptions.py` | Sprint 3 (1.7.1) | Pre: `column_name` is string. Post: `e.column_name` stored. `str(e)` matches §2.7. |
| `InvalidParameterError` | `exceptions.py` | Sprint 3 (1.4.3), Sprint 5 (4.2.1) | Pre: `param_name` str, `value` float, `reason` str. Post: all three stored. `str(e)` includes all three. |
| `DuplicateColumnError` | `exceptions.py` | Sprint 2 (1.2.1, 1.3.1) | Pre: `column_name` is string. Post: `e.column_name` stored. Message includes "across all groups." |
| `EmptyValuesError` | `exceptions.py` | Sprint 2 (1.2.1) | Pre: `column_name` is string. Post: `e.column_name` stored. |
| `WeightLengthMismatchError` | `exceptions.py` | Sprint 2 (1.2.1) | Pre: `column_name` str, `n_values` int, `n_weights` int. Post: all three stored. Message includes both counts. |
| `DegenerateDistributionError` | `exceptions.py` | Sprint 3 (1.4.3) | Pre: `column_name` str, `detail` str. Post: both stored. |
| `ParentNotFoundError` | `exceptions.py` | Sprint 2 (1.2.4) | Pre: `child_name`, `parent_name`, `group` all strings. Post: all three stored. |
| `DuplicateGroupRootError` | `exceptions.py` | Sprint 2 (1.2.6) | Pre: `group_name`, `existing_root`, `attempted_root` all strings. Post: all three stored. Message names both roots. |

---

## 7. Comprehension Checkpoints

**Q1. Validation ordering.** Why does `simulator.py` validate `target_rows` and `seed` types (§D.1a, §D.1b) *before* the `target_rows > 0` value check (§D.1c)? Trace what would happen with input `FactTableSimulator("500", 42)` if the value check ran first.

> *Expected answer:* If §D.1c ran first, `"500" <= 0` would call `str.__le__(int)`, which returns `NotImplemented`, then Python tries `int.__ge__(str)`, which also returns `NotImplemented`, resulting in `TypeError: '<=' not supported between instances of 'str' and 'int'` — a confusing stdlib error. The type check first produces the clear `"target_rows must be an int, got str."` message. This is why §D.1a–§D.1c form a narrowing pipeline: each block's precondition is the previous block's postcondition.

**Q2. Bool subclass edge case.** Explain why `isinstance(target_rows, bool)` is checked separately in §D.1a after `isinstance(target_rows, int)` already passed. What specific downstream failure does this prevent?

> *Expected answer:* `bool` is a subclass of `int` in Python, so `isinstance(True, int)` is `True`. Without the bool guard, `FactTableSimulator(True, 42)` would set `target_rows = True`, which is `1`. The L1 row-count check (subtask 8.2.1) would compute `abs(N - 1) / 1` for an N-row DataFrame, almost certainly failing. The guard converts this into a clear `TypeError` at construction.

**Q3. `__eq__` / `__hash__` consistency.** If `OrthogonalPair.__hash__()` (§C.2d) used `hash((self.group_a, self.group_b))` (tuple hash) while `__eq__` (§C.2c) kept using frozenset comparison, what specific data structure operation would produce incorrect results? Give a concrete example.

> *Expected answer:* `Pair("entity","patient")` and `Pair("patient","entity")` would be equal (`__eq__` uses frozenset) but have different hashes (tuple hash is order-dependent). Adding both to a `set` could result in two entries for the "same" pair, because Python uses hash to find the bucket — different hashes mean different buckets, so `__eq__` is never called. Sprint 3's conflict detection scanning a set of orthogonal pairs would fail to detect the duplicate.

**Q4. Deep copy vs shallow copy.** In `GroupDependency.to_metadata()` (§C.3b), what is the precise difference between the pre-fix `dict(self.conditional_weights)` and the post-fix `{k: dict(v) for k, v in self.conditional_weights.items()}`? Construct a mutation scenario that succeeds (corrupts internal state) with the shallow copy but fails (is isolated) with the deep copy.

> *Expected answer:* `dict(self.conditional_weights)` creates a new outer dict but the values (inner dicts like `{"Insurance": 0.45, ...}`) are still the same objects. `meta["conditional_weights"]["Mild"]["Insurance"] = 0.99` mutates the shared inner dict, corrupting `dep.conditional_weights["Mild"]["Insurance"]`. The dict comprehension creates new inner dicts (`dict(v)`), so the mutation only affects the metadata copy. Sprint 5's engine, reading `dep.conditional_weights` for sampling, would see `0.99` with the shallow copy but `0.45` with the deep copy.

**Q5. Atomicity of constructor validation.** If `FactTableSimulator(500.0, 42)` raises `TypeError` at §D.1a, what is the state of the partially-constructed `self` object? Specifically: can any code path access `self._columns` or `self.target_rows` after this exception?

> *Expected answer:* No. The three validation blocks (§D.1a–§D.1c) execute before any attribute assignment (§D.1d–§D.1k). A `TypeError` at §D.1a means `self.target_rows`, `self._columns`, etc. were never assigned. Accessing any of them raises `AttributeError`. The operation is atomic — there is no partial state. The caller's `except TypeError` discards the object.

**Q6. `SimulatorError` hierarchy design.** Sprint 8's sandbox executor needs to catch all SDK errors but NOT catch numpy/pandas errors that might indicate bugs in the engine. Explain how the current inheritance design (§B.1) enables this, and what would break if `SimulatorError` inherited from `ValueError` instead of `Exception`.

> *Expected answer:* `except SimulatorError as e` catches `CyclicDependencyError`, `UndefinedEffectError`, etc. but lets `numpy.linalg.LinAlgError`, `pandas.errors.MergeError`, etc. propagate. If `SimulatorError` inherited from `ValueError`, then `except ValueError` blocks (common in numerical code for catching array shape mismatches etc.) would also catch `CyclicDependencyError`, silently swallowing SDK errors instead of surfacing them to the feedback loop.

**Q7. Construction-time aliasing.** `GroupDependency` stores `conditional_weights` by reference (§C.3a, Limitation 2). Trace what happens if Sprint 3's `add_group_dependency` does NOT copy the caller's dict, and the LLM-generated script modifies the dict after the call. Which downstream consumer (Sprint 5 engine or Sprint 6 validator) would see corrupted data, and which would not? Why?

> *Expected answer:* Both the engine and the dataclass instance's `conditional_weights` point to the same object as the caller's dict (reference aliasing from §C.3a). If the caller mutates the dict, the engine (reading `dep.conditional_weights` directly) sees corrupted data. However, the validator (reading `meta["conditional_weights"]` from a previously-called `to_metadata()`) sees clean data — because `to_metadata()` (§C.3b) deep-copies at serialization time. If `to_metadata()` hasn't been called yet, both consumers see corrupted data. The fix is for Sprint 3 to copy the dict before constructing the `GroupDependency`.

**Q8. Spec message conformance.** The spec's §2.7 uses the message `"Measure 'cost' → 'satisfaction' → 'cost' forms a cycle."` as an example. Sprint 3's root-level DAG acyclicity check (subtask 1.7.3) also needs to raise `CyclicDependencyError` — but for group *roots* (e.g., `["severity", "payment_method", "severity"]`), not measures. Would the current message format (§B.2b, which hardcodes `"Measure"`) be misleading? What modification would you make, and which blocks would need to change?

> *Expected answer:* Yes, `"Measure 'severity' → 'payment_method' → 'severity' forms a cycle."` is misleading because these are group roots, not measures. The fix: add an optional `context` parameter to `CyclicDependencyError.__init__()` (default `"Measure"`) and change §B.2b's f-string to `f"{context} {arrow_chain} forms a cycle."`. Sprint 3 would pass `context="Group root"`. Only §B.2a (add parameter) and §B.2b (use parameter in f-string) need modification. All existing callers would work unchanged via the default.
