"""The expression language used by measure declarations.

A generating script declares each numeric column as one expression string. An
expression has exactly four kinds of parts:

    distribution    gaussian / lognormal / gamma / beta / uniform / poisson /
                    exponential / mixture
    category effect `[column=value]` is a 0/1 indicator; `{value: number}[column]`
                    is a lookup table
    other columns   write the column name; a time column evaluates to the number
                    of days since its start, so trend breaks and seasonal terms
                    can be written as ordinary arithmetic
    arithmetic      + - * / **, `clip(x, lo, hi)`, `where(cond, a, b)`

Dependencies between numeric columns are read out of the expressions rather than
declared: `columns` reports every column an expression references, and `edges`
keeps the references that point at another numeric column.

Evaluation runs on a whole column at a time, never row by row. The same
expression with the same random stream always produces the same column.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


class DeclarationError(ValueError):
    """A declaration is not usable: bad argument, undefined symbol, bad syntax.

    The message must name the offending column, symbol or constraint: it is fed
    back to the model verbatim, and "it failed" does not help it retry.
    """


#: `[column=value]` rewritten to `_ind('column', 'value')` before parsing.
#: Values may contain spaces, as in `[hospital=Mercy General]`.
INDICATOR = re.compile(r"\[\s*([A-Za-z_]\w*)\s*=\s*([^\[\]]+?)\s*\]")

#: Name the indicator rewrite uses. Leading underscore keeps it clear of column names.
_IND = "_ind"

Vector = np.ndarray


def _draw(fn: str) -> Callable:
    return lambda rng, n, *args: getattr(rng, fn)(*args, size=n)


def _mixture(rng: np.random.Generator, n: int, p, a, b) -> Vector:
    return np.where(rng.random(n) < p, a, b)


#: Distribution name to (parameter names, sampler). Parameters may be passed
#: positionally or by name.
DISTRIBUTIONS: dict[str, tuple[tuple[str, ...], Callable]] = {
    "gaussian": (("mu", "sigma"), _draw("normal")),
    "lognormal": (("mu", "sigma"), _draw("lognormal")),
    "gamma": (("shape", "scale"), _draw("gamma")),
    "beta": (("a", "b"), _draw("beta")),
    "uniform": (("low", "high"), _draw("uniform")),
    "poisson": (("lam",), _draw("poisson")),
    "exponential": (("scale",), _draw("exponential")),
    "mixture": (("p", "a", "b"), _mixture),
}

#: Deterministic helpers. `where` expresses a piecewise term, `clip` bounds a range.
PLAIN: dict[str, Callable] = {
    "clip": np.clip, "where": np.where, "abs": np.abs, "min": np.minimum,
    "max": np.maximum, "log": np.log, "exp": np.exp, "sqrt": np.sqrt,
    "sin": np.sin, "cos": np.cos, "round": np.round,
}

CONSTANTS: dict[str, float] = {"pi": float(np.pi), "e": float(np.e)}

_BINOPS: dict[type, Callable] = {
    ast.Add: np.add, ast.Sub: np.subtract, ast.Mult: np.multiply,
    ast.Div: np.divide, ast.Pow: np.power, ast.Mod: np.mod,
}

_COMPARES: dict[type, Callable] = {
    ast.Gt: np.greater, ast.GtE: np.greater_equal, ast.Lt: np.less,
    ast.LtE: np.less_equal, ast.Eq: np.equal, ast.NotEq: np.not_equal,
}

#: Syntax nodes an expression may contain. Everything else is rejected:
#: attribute access, subscript assignment, lambdas and comprehensions are not
#: parts of an expression and would widen what a generated script can reach.
_ALLOWED = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call,
    ast.keyword, ast.Dict, ast.Subscript, ast.Compare, ast.Load, ast.USub, ast.UAdd,
    *_BINOPS, *_COMPARES,
)


def _rewrite(text: str) -> str:
    return INDICATOR.sub(lambda m: f"{_IND}({m[1]!r}, {m[2]!r})", text)


@dataclass(frozen=True)
class Expr:
    """A parsed expression together with every column name it references."""

    source: str
    tree: ast.Expression
    columns: frozenset[str]

    def eval(self, env: dict[str, Vector], rng: np.random.Generator, n: int) -> Vector:
        """Evaluate over `n` rows. `env` holds the columns computed so far."""
        try:
            value = _eval(self.tree.body, env, rng, n)
            return np.broadcast_to(np.asarray(value, dtype=float), (n,)).copy()
        except DeclarationError:
            raise
        except (TypeError, ValueError, AttributeError) as exc:
            raise DeclarationError(f"expression `{self.source}` failed: {exc}") from exc


def parse(text: str) -> Expr:
    """Parse an expression string. Syntax errors and disallowed nodes stop here."""
    rewritten = _rewrite(text)
    try:
        tree = ast.parse(rewritten, mode="eval")
    except SyntaxError as exc:
        raise DeclarationError(
            f"expression `{text}` does not parse: {exc.msg}") from exc
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise DeclarationError(
                f"expression `{text}` may not contain {type(node).__name__}; use "
                "distributions, category effects, column names and arithmetic only")
    return Expr(text, tree, frozenset(_columns(tree)))


def edges(measures: Sequence[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    """`[(column, expression)]` to dependency edges `(referenced, referencing)`."""
    names = {name for name, _ in measures}
    out: list[tuple[str, str]] = []
    for name, source in measures:
        for ref in sorted(parse(source).columns & names):
            out.append((ref, name))
    return tuple(out)


# ---------------------------------------------------------------- referenced columns

def _columns(tree: ast.Expression) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in DISTRIBUTIONS \
                and node.id not in PLAIN and node.id not in CONSTANTS and node.id != _IND:
            found.add(node.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == _IND:
            found.add(node.args[0].value)
    return found


# ---------------------------------------------------------------- evaluation

def _eval(node: ast.AST, env: dict[str, Vector], rng: np.random.Generator, n: int):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        if node.id not in env:
            raise DeclarationError(f"`{node.id}` is used but never defined")
        return env[node.id]
    if isinstance(node, ast.BinOp):
        return _BINOPS[type(node.op)](_eval(node.left, env, rng, n),
                                      _eval(node.right, env, rng, n))
    if isinstance(node, ast.UnaryOp):
        value = _eval(node.operand, env, rng, n)
        return -value if isinstance(node.op, ast.USub) else +value
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1:
            raise DeclarationError("a condition may hold only one comparison")
        return _COMPARES[type(node.ops[0])](_eval(node.left, env, rng, n),
                                            _eval(node.comparators[0], env, rng, n))
    if isinstance(node, ast.Subscript):
        return _lookup(node, env, rng, n)
    if isinstance(node, ast.Call):
        return _call(node, env, rng, n)
    raise DeclarationError(f"cannot evaluate {type(node).__name__}")


def _lookup(node: ast.Subscript, env: dict[str, Vector],
            rng: np.random.Generator, n: int) -> Vector:
    """`{value: number}[column]`. Every value of the column needs an entry."""
    if not isinstance(node.value, ast.Dict) or not isinstance(node.slice, ast.Name):
        raise DeclarationError("a lookup must be written `{value: number}[column]`")
    column = node.slice.id
    if column not in env:
        raise DeclarationError(f"`{column}` is used but never defined")
    table = {_key(k): float(_eval(v, env, rng, n)) for k, v in zip(node.value.keys,
                                                                  node.value.values)}
    values = env[column]
    missing = sorted({str(v) for v in np.unique(values)} - set(table))
    if missing:
        raise DeclarationError(
            f"the lookup on `{column}` is missing: {', '.join(missing)}")
    return np.array([table[str(v)] for v in values], dtype=float)


def _key(node: ast.AST) -> str:
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Name):
        return node.id
    raise DeclarationError("lookup keys must be strings or single words")


def _call(node: ast.Call, env: dict[str, Vector], rng: np.random.Generator, n: int):
    if not isinstance(node.func, ast.Name):
        raise DeclarationError("only distributions and arithmetic helpers are callable")
    name = node.func.id
    if name == _IND:
        column = node.args[0].value
        if column not in env:
            raise DeclarationError(f"`{column}` is used but never defined")
        return (env[column] == node.args[1].value).astype(float)

    args = [_eval(a, env, rng, n) for a in node.args]
    kwargs = {k.arg: _eval(k.value, env, rng, n) for k in node.keywords}
    if name in PLAIN:
        return PLAIN[name](*args, **kwargs)
    if name in DISTRIBUTIONS:
        params, draw = DISTRIBUTIONS[name]
        return draw(rng, n, *_bind(name, params, args, kwargs))
    raise DeclarationError(
        f"there is no function `{name}`; distributions are {sorted(DISTRIBUTIONS)}")


def _bind(name: str, params: tuple[str, ...], args: list, kwargs: dict) -> list:
    """Accept positional and keyword arguments; name whichever one is missing."""
    if len(args) > len(params):
        raise DeclarationError(
            f"`{name}` takes {len(params)} arguments, got {len(args)}")
    bound = dict(zip(params, args))
    for key, value in kwargs.items():
        if key not in params:
            raise DeclarationError(f"`{name}` has no argument `{key}`; it takes {params}")
        bound[key] = value
    if missing := [p for p in params if p not in bound]:
        raise DeclarationError(f"`{name}` is missing: {', '.join(missing)}")
    return [bound[p] for p in params]
