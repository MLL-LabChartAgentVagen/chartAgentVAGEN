"""Command line entry points: build the domain pool, run one stage, run everything.

    python -m chartgen.cli pool                          build the domain pool (once)
    python -m chartgen.cli data --payload FILE           data stage, no model call
    python -m chartgen.cli data --domain "ICU beds"      data stage, one model call
    python -m chartgen.cli inspect SCHEMA                diagram page for a saved schema
    python -m chartgen.cli render SPEC -o DIR            render stage from a saved spec
    python -m chartgen.cli run --scenarios 3             the whole pipeline
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llmkit import LLM, Deduper

from . import report
from .common import serde
from .config import Config
from .interfaces.figure import FigureSpec
from .interfaces.style import StyleVector
from .interfaces.table import TableSchema
from .pipeline import Pipeline, save_data
from .s03_render.render import render
from .s03_render.style import sample as sample_style


def _llm(config: Config) -> LLM:
    return LLM(model=str(config.get("llm.model")),
               max_tokens=int(config.get("llm.max_tokens", 8000)),
               cache_dir=config.get("llm.cache_dir"))


def _deduper(config: Config, key: str, path: str | None = None) -> Deduper:
    """A near-duplicate judge. The similarity function is local by default."""
    return Deduper(threshold=float(config.get(key, 0.85)), path=path)


def cmd_pool(args: argparse.Namespace) -> None:
    from .s01_data.pool import build

    config = Config.load(args.config)
    dedup = _deduper(config, "data.pool_dedup_cosine")
    pool = build(_llm(config), n_topics=args.topics, per_topic=args.per_topic,
                 target=args.target, is_duplicate=lambda name: not dedup.add(name))
    path = pool.save(args.out or config.get("data.pool_path", "data/domains/pool.json"))
    print(f"{path}: {len(pool.topics)} topics, {len(pool.domains)} sub-topics, "
          f"{pool.stats()['tiers']}")


def cmd_data(args: argparse.Namespace) -> None:
    """Run the data stage. With --payload no model is called: a hand-written answer
    goes through the same rules as a generated one."""
    from .s01_data.author import Rejected, build_scenario, compose

    config = Config.load(args.config).override(args.set or [])
    seed = int(config.get("root_seed", 0))
    try:
        if args.payload:
            payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
            table, schema = compose(payload, scenario_id=args.scenario, seed=seed,
                                    config=config)
        else:
            log: list[Rejected] = []
            domain = {"name": args.domain, "topic": "", "complexity_tier": args.tier,
                      "typical_entities_hint": [], "typical_metrics_hint": [],
                      "temporal_granularity_hint": "daily"} if args.domain else None
            memory = _deduper(config, "data.scenario_dedup_cosine",
                              str(config.get("data.scenario_memory")))
            table, schema = build_scenario(
                args.scenario, seed, config, domain=domain, log=log,
                is_duplicate=lambda text: not memory.add(text))
            for item in log:
                print(f"retry [{item.kind}] {item}")
    except Rejected as exc:
        print(f"the data stage rejected the answer [{exc.kind}]:\n{exc}")
        raise SystemExit(1) from exc

    max_tier = int(config.get("scale.max_tier", 3))
    out = save_data(table, schema, Path(args.out or config.get("output.dir", "data/generated")),
                    max_tier=max_tier)
    print(report.summary(table, schema, max_tier=max_tier))
    print(f"\nwrote {out}/schema.json, {out}/facts.parquet and {out}/schema.md")


def cmd_inspect(args: argparse.Namespace) -> None:
    """Draw the diagram page for a schema saved by an earlier run. The data stage
    writes one on its own; this is for schemas that predate it or live elsewhere."""
    schema = serde.load(TableSchema, args.schema)
    out = report.page(schema, args.out or args.schema.with_suffix(".md"), max_tier=args.max_tier)
    print(report.tree(schema))
    print(f"\nwrote {out}")


def cmd_render(args: argparse.Namespace) -> None:
    spec = serde.load(FigureSpec, args.spec)
    style = (serde.load(StyleVector, args.style) if args.style
             else sample_style(args.seed, spec.scenario_id, spec.figure_id, args.variant))
    out = render(spec, style, args.out)
    serde.save(out, Path(args.out) / f"{spec.figure_id}.json")
    print(f"{out.image_path}: {len(out.marks)} marks")


def cmd_run(args: argparse.Namespace) -> None:
    config = Config.load(args.config).override(args.set or [])
    if args.scenarios:
        config.set("scale.scenarios", args.scenarios)
    pipe = Pipeline(config, Path(config.get("output.dir", "data/generated"))
                    / config.get("run_id", "dev"))
    for i in range(int(config.get("scale.scenarios", 1))):
        result = pipe.run_scenario(f"s{i:03d}")
        status = "ok" if result.ok else f"failed in {result.stage}: {result.reason}"
        print(f"{result.scenario_id}  {status}  {len(result.records)} records")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="chartgen")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("pool", help="build the domain pool: two levels plus dedup, once per project")
    p.add_argument("-o", "--out", type=Path, default=None)
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--topics", type=int, default=20)
    p.add_argument("--per-topic", type=int, default=12)
    p.add_argument("--target", type=int, default=200)
    p.set_defaults(func=cmd_pool)

    p = sub.add_parser("data", help="data stage only: a domain to a fact table and its schema")
    p.add_argument("--payload", type=Path, default=None,
                   help="a hand-written answer; with this no model is called")
    p.add_argument("--domain", default=None, help="name one domain instead of drawing from the pool")
    p.add_argument("--tier", default="medium", choices=("simple", "medium", "complex"))
    p.add_argument("--scenario", default="s000")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.add_argument("-o", "--out", type=Path, default=None)
    p.set_defaults(func=cmd_data)

    p = sub.add_parser("inspect", help="draw a saved schema: hierarchy, dependencies, intents")
    p.add_argument("schema", type=Path)
    p.add_argument("-o", "--out", type=Path, default=None,
                   help="markdown file to write; defaults to schema.md beside the input")
    p.add_argument("--max-tier", type=int, default=3)
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("render", help="render stage only: a figure spec and a style to an image")
    p.add_argument("spec", type=Path)
    p.add_argument("--style", type=Path, default=None)
    p.add_argument("--variant", type=int, default=0)
    p.add_argument("--seed", type=int, default=20260816)
    p.add_argument("-o", "--out", type=Path, default=Path("data/generated/render"))
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("run", help="run the whole pipeline")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--scenarios", type=int, default=None)
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.set_defaults(func=cmd_run)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
