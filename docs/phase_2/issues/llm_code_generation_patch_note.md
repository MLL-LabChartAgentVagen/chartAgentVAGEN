# Patch Note: Safer Full-Code Generation with Helper Functions

## Decision

We will continue to let the LLM output a **complete Python script**, but the script must be constrained to call only a **small validated helper API** that we implement.

The LLM must **not** call the underlying simulator/SDK directly, and it must **not** construct fragile free-form formula strings, target-expression strings, or rule-heavy nested parameter dictionaries unless those values are produced through approved helper functions.

This preserves the product requirement of “full code output” while moving syntax-sensitive and contract-sensitive logic into deterministic code that we control.

---

## Why this change is necessary

The observed failures fall into two categories:

### 1. Serialization failures
Examples:
- `SyntaxError: '[' was never closed`
- `SyntaxError: unterminated string literal`
- `SyntaxError: '{' was never closed`

These are caused by asking the LLM to directly serialize complex Python source.

### 2. Semantic contract failures
Examples:
- `trend_break pattern requires 'break_point'`
- `target 'total_amount' not declared as a measure`

These are caused by asking the LLM to directly satisfy hidden SDK invariants such as:
- required pattern-specific parameters
- declaration-before-reference rules
- valid measure/category references
- acyclic dependencies
- root-vs-derived column restrictions

Prompting alone will not reliably eliminate either class of failure. The correct fix is to reduce what the LLM is allowed to author and move fragile logic behind a safe helper layer.

---

## Target architecture

Use the following execution pattern:

**LLM-generated Python script -> AST gate -> validated helper API / builder -> global validation -> compile to SDK calls -> execute**

The generated Python remains a full script, but it should function as a constrained DSL over our helper API.

---

## Mandatory implementation rule

The generated script may only use:
- approved imports
- approved helper functions
- approved expression builders
- approved predicate builders
- a builder/context object
- a final build function that performs global validation and execution

The generated script may **not**:
- call simulator/SDK methods directly
- write raw formula strings
- write raw target-expression strings
- manually encode pattern-specific `params` dictionaries for generic pattern entry points
- mutate internal simulator state outside the helper layer

---

## Required helper-layer design

Do **not** expose a thin wrapper around the raw simulator methods.

### Bad design
```python
def add_pattern(sim, pattern_type, target, col, params):
    sim.inject_pattern(pattern_type, target=target, col=col, params=params)
```

This still allows missing keys, malformed values, unknown measures, and invalid targets.

### Good design
Expose **specific validated helpers** such as:
- `declare_category(...)`
- `declare_temporal(...)`
- `declare_root_measure(...)`
- `declare_structural_measure(...)`
- `declare_orthogonal(...)`
- `declare_group_dependency(...)`
- `inject_trend_break(...)`
- `inject_outlier_entity(...)`
- `set_realism(...)`
- `finalize_and_build(...)`

Each helper must validate arguments before touching the underlying simulator.

---

## Builder/context requirement

All helper calls must write into a **builder/context object** rather than directly mutating the simulator.

Recommended usage pattern:

```python
from safe_fact_api import *

ctx = BuildContext(seed=7, rows=1200)

declare_category(ctx, ...)
declare_temporal(ctx, ...)
declare_root_measure(ctx, ...)
declare_structural_measure(ctx, ...)
inject_trend_break(ctx, ...)
set_realism(ctx, ...)

df = finalize_and_build(ctx)
```

### Why this is required
This allows us to:
- validate references globally
- validate DAG constraints globally
- reorder internal execution safely
- produce clearer repair messages
- enforce declaration-order rules at build time instead of relying on the LLM to serialize perfectly ordered code

---

## Expression and predicate helper requirement

To reduce syntax and contract errors, the LLM must not author free-form formulas or free-form target strings.

### Expression helpers
Use expression builders such as:
- `measure("total_amount")`
- `effect("severity_surcharge")`
- `const(12)`
- `add(...)`
- `sub(...)`
- `mul(...)`
- `div(...)`

Example:

```python
expr = add(
    mul(measure("wait_minutes"), const(12)),
    effect("severity_surcharge"),
)
```

The helper layer compiles this expression tree into the simulator’s formula representation only after validation.

### Predicate helpers
Use predicate builders such as:
- `eq("hospital", "Huashan")`
- `and_(...)`
- `or_(...)`
- `in_(...)`

Example:

```python
target = and_(
    eq("hospital", "Huashan"),
    eq("severity", "Severe"),
)
```

The helper layer compiles this predicate tree into the simulator’s target representation only after validation.

### Rationale
This eliminates a major source of:
- unbalanced quotes
- malformed strings
- unknown identifier references
- invalid target syntax

---

## Validation responsibilities of the helper layer

### 1. Name and declaration validation
Track all declared:
- categories
- temporals
- measures
- structural measures
- effect symbols

Reject:
- duplicate declarations
- references to undeclared names
- misuse of a category where a measure is expected
- misuse of a derived column where a root column is required

### 2. Structural measure validation
When declaring a structural measure:
- ensure the name is unique
- ensure all expression references resolve
- ensure all effect references are defined
- reject self-reference
- reject dependency cycles

### 3. Group dependency validation
When declaring group dependencies:
- child must be a valid root categorical column
- conditioning columns must be valid root columns from other groups
- conditional weights must be well-formed
- weights must normalize correctly
- dependency graph must remain acyclic

### 4. Pattern-specific validation
Pattern helpers must encode required parameters explicitly.

Example:
```python
inject_trend_break(ctx, target, col, break_point, magnitude)
```

Validation must check:
- `col` is a declared measure
- `break_point` exists and parses correctly
- `target` is a valid predicate object
- all required pattern parameters are present
- all numeric thresholds are valid

This directly prevents failures such as:
- missing `break_point`
- undeclared target measure references

### 5. Global finalization validation
`finalize_and_build(ctx)` must perform:
- minimum structural checks required by the spec
- measure dependency topological sort
- root-group dependency DAG validation
- reference resolution checks
- compilation of expressions and predicates
- deterministic ordering of underlying simulator calls

No simulator execution should happen before final validation passes.

---

## AST gate requirement before sandbox execution

Before running the generated script in sandbox, parse it with `ast.parse()` and reject scripts that violate the allowed authoring contract.

### The AST gate must reject:
- syntax errors
- forbidden imports
- forbidden function calls
- direct calls to simulator/SDK methods
- raw formula strings where expression helpers are required
- raw target strings where predicate helpers are required
- use of disallowed modules or dynamic execution primitives

### The AST gate should whitelist:
- approved helper API names
- basic Python syntax constructs needed for readable scripts
- safe imports explicitly allowed by the execution plan

This turns many failures into immediate deterministic rejections instead of ambiguous sandbox tracebacks.

---

## Prompt/spec patch

Update the code-generation spec so that it says:

### Required output form
The model must output a complete Python script.

### Allowed API
The model may only import and call the approved helper API.

### Prohibited behaviors
The model must not:
1. call simulator/SDK methods directly
2. write raw formula strings
3. write raw target-expression strings
4. use generic pattern entry points with ad hoc `params` dictionaries
5. bypass the builder/context object
6. mutate simulator internals directly

### Required final line
The final built dataframe must be assigned to:
```python
df
```

### Output restriction
Output only Python code and no prose.

---

## Recommended helper API surface

Minimum recommended public surface:

```python
BuildContext
declare_category
declare_temporal
declare_root_measure
declare_structural_measure
declare_orthogonal
declare_group_dependency
inject_trend_break
inject_outlier_entity
set_realism
finalize_and_build

measure
effect
const
add
sub
mul
div

eq
and_
or_
in_
```

This surface should be kept intentionally small.

---

## Example of the preferred generated style

### Preferred
```python
from safe_fact_api import *

ctx = BuildContext(seed=7, rows=1200)

declare_category(
    ctx,
    name="hospital",
    group="provider",
    values=["Huashan", "Ruijin", "Zhongshan"],
    weights=[0.4, 0.35, 0.25],
)

declare_root_measure(
    ctx,
    name="wait_minutes",
    family="lognormal",
    param_model={"intercept": 3.2},
)

declare_structural_measure(
    ctx,
    name="total_amount",
    expr=add(
        mul(measure("wait_minutes"), const(12)),
        effect("severity_surcharge"),
    ),
    effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
)

inject_trend_break(
    ctx,
    target=eq("hospital", "Huashan"),
    col=measure("total_amount"),
    break_point="2024-06-01",
    magnitude=0.3,
)

df = finalize_and_build(ctx)
```

### Prohibited
```python
sim.add_measure_structural(
    "total_amount",
    formula="wait_minutes * 12 + severity_surcharge",
    effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},
)

sim.inject_pattern(
    "trend_break",
    target="hospital == 'Huashan'",
    col="total_amount",
    params={"magnitude": 0.3},
)
```

---

## Repair/error feedback requirement

When validation fails, return structured machine-readable errors to the repair loop.

Preferred error style:

```json
{
  "error_type": "unknown_measure_reference",
  "location": "declare_structural_measure(name='profit_margin')",
  "detail": "measure 'revenue' is referenced but not declared"
}
```

This is far easier for an LLM to repair than raw Python tracebacks.

---

## Execution-plan update

The execution plan should be revised as follows:

1. Generate full Python script constrained to approved helper API.
2. Run AST gate.
3. If AST gate fails, return deterministic rejection with structured error.
4. Execute script in sandbox.
5. Helper layer accumulates declarations into builder/context.
6. `finalize_and_build()` performs all global validation.
7. Only after successful validation, compile into underlying simulator calls.
8. Execute simulator and assign result to `df`.
9. If validation fails, emit structured error for repair rather than relying on low-level tracebacks.

---

## Final recommendation

We should **keep full-code generation**, but only in the form of a constrained Python DSL over a validated helper API.

This is the recommended compromise because it:
- preserves the product requirement of complete code output
- sharply reduces syntax failures
- sharply reduces semantic contract failures
- makes validation deterministic
- makes repair loops significantly more reliable
- prevents the LLM from directly interacting with fragile low-level simulator APIs

In short:

**Let the LLM write the script structure.**
**Let our helper layer own correctness.**
