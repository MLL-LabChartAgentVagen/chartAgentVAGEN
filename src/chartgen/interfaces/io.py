"""六份接口的统一读写与版本检查。

一个按类型标注驱动的编解码器，接口 dataclass 因此不用各写一遍 `to_dict`。
落盘时套一层信封 `{schema_version, type, data}`：版本与类型只在这一处检查，
旧产物在读取时报错，不会静默错算。
"""

from __future__ import annotations

import dataclasses
import json
import types
import typing
from pathlib import Path
from typing import Any, Literal, TypeVar, Union, get_args, get_origin, get_type_hints

import pandas as pd

from ..common.geometry import Box
from .figure import FigureSpec
from .record import Record, RenderOutput
from .style import StyleVector
from .table import FactTable, TableSchema

SCHEMA_VERSION = 1

T = TypeVar("T")


class SchemaVersionError(RuntimeError):
    """产物的 schema_version 与当前代码不符。"""


class SchemaTypeError(RuntimeError):
    """产物的类型与请求的类型不符。"""


# ---------------------------------------------------------------- 编码

def to_dict(obj: Any) -> Any:
    if isinstance(obj, Box):
        return list(obj.as_tuple())
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_dict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, dict):
        return {str(k): to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_dict(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    raise TypeError(f"不知道怎么编码 {type(obj)!r}")


# ---------------------------------------------------------------- 解码

def _unwrap_optional(tp: Any) -> tuple[Any, bool]:
    """`X | None` → `(X, True)`。"""
    if get_origin(tp) in (Union, types.UnionType):
        args = [a for a in get_args(tp) if a is not type(None)]
        return (args[0] if len(args) == 1 else Union[tuple(args)], len(args) < len(get_args(tp)))
    return (tp, False)


def _from_dict(tp: Any, raw: Any) -> Any:
    tp, optional = _unwrap_optional(tp)
    if raw is None:
        if not optional:
            raise ValueError(f"{tp} 不接受 None")
        return None

    if tp is Box:
        return Box(*raw)
    if get_origin(tp) is Literal:
        if raw not in get_args(tp):
            raise ValueError(f"{raw!r} 不在 {get_args(tp)} 里")
        return raw

    origin = get_origin(tp)
    if origin in (tuple,):
        args = get_args(tp)
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_from_dict(args[0], v) for v in raw)
        return tuple(_from_dict(a, v) for a, v in zip(args, raw))
    if origin in (list,):
        return [_from_dict(get_args(tp)[0], v) for v in raw]
    if origin in (dict,):
        kt, vt = get_args(tp)
        return {_from_dict(kt, k): _from_dict(vt, v) for k, v in raw.items()}

    if dataclasses.is_dataclass(tp):
        hints = get_type_hints(tp)
        kwargs = {f.name: _from_dict(hints[f.name], raw[f.name])
                  for f in dataclasses.fields(tp) if f.name in raw}
        return tp(**kwargs)

    if tp in (int, float, str, bool):
        return tp(raw)
    if tp is Any:
        return raw
    raise TypeError(f"不知道怎么解码 {tp!r}")


def from_dict(cls: type[T], raw: dict) -> T:
    return typing.cast(T, _from_dict(cls, raw))


#: 别名，读起来对称
load_dict = from_dict


# ---------------------------------------------------------------- 落盘

def _envelope(obj: Any) -> dict:
    return {"schema_version": SCHEMA_VERSION, "type": type(obj).__name__, "data": to_dict(obj)}


def dumps(obj: Any) -> str:
    return json.dumps(_envelope(obj), ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def save(obj: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(obj), encoding="utf-8")
    return path


def loads(cls: type[T], text: str) -> T:
    raw = json.loads(text)
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise SchemaVersionError(
            f"产物是 schema_version={raw.get('schema_version')}，当前是 {SCHEMA_VERSION}；"
            "改接口必须同时改样例并重跑上游"
        )
    if raw.get("type") != cls.__name__:
        raise SchemaTypeError(f"产物类型是 {raw.get('type')}，请求的是 {cls.__name__}")
    return from_dict(cls, raw["data"])


def load(cls: type[T], path: str | Path) -> T:
    return loads(cls, Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 事实表

def save_table(table: FactTable, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = table.df.copy()
    df.attrs = {}
    df.to_parquet(path, index=False)
    (path.with_suffix(".meta.json")).write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "scenario_id": table.scenario_id},
                   ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_table(path: str | Path) -> FactTable:
    path = Path(path)
    meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    if meta.get("schema_version") != SCHEMA_VERSION:
        raise SchemaVersionError(f"事实表是 schema_version={meta.get('schema_version')}")
    return FactTable(meta["scenario_id"], pd.read_parquet(path))


# ---------------------------------------------------------------- 样例

_SAMPLE_DIR = Path(__file__).resolve().parents[3] / "tests" / "samples"

#: 每份接口一个最小样例。改接口要同时改这里的文件并升 SCHEMA_VERSION。
SAMPLES: dict[str, tuple[type, Path]] = {
    "TableSchema": (TableSchema, _SAMPLE_DIR / "table_schema.json"),
    "FigureSpec": (FigureSpec, _SAMPLE_DIR / "figure_spec.json"),
    "StyleVector": (StyleVector, _SAMPLE_DIR / "style_vector.json"),
    "RenderOutput": (RenderOutput, _SAMPLE_DIR / "render_output.json"),
    "Record": (Record, _SAMPLE_DIR / "record.json"),
}


def sample(name: str) -> Any:
    cls, path = SAMPLES[name]
    return load(cls, path)
