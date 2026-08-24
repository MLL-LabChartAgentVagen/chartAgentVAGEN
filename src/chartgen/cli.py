"""Command line entry points: build the domain pool, run one stage, run everything.

    python -m chartgen.cli pool                          build the domain pool (once)
    python -m chartgen.cli data --payload FILE           data stage, no model call
    python -m chartgen.cli data --domain "ICU beds"      data stage, one model call
    python -m chartgen.cli inspect SCHEMA                diagram page for a saved schema
    python -m chartgen.cli figures --payload FILE        view selection, no model call
    python -m chartgen.cli render SPEC -o DIR            render stage from a saved spec
    python -m chartgen.cli run --scenarios 3             the whole pipeline
    python -m chartgen.cli run --payload FILE            the whole pipeline, no model call
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
               effort=config.get("llm.effort", "high"),
               cache_dir=config.get("llm.cache_dir"))


def _deduper(config: Config, key: str, path: str | None = None) -> Deduper:
    """A near-duplicate judge. The similarity function is local by default."""
    return Deduper(threshold=float(config.get(key, 0.85)), path=path)


def cmd_pool(args: argparse.Namespace) -> None:
    from .s01_data.pool import Pool, build

    config = Config.load(args.config)
    path = Path(args.out or config.get("data.pool_path", "data/domains/pool.json"))
    dedup = _deduper(config, "data.pool_dedup_cosine")
    known: tuple[str, ...] = ()
    if args.extend and path.exists():
        # Both levels of what is already there. The names go to the duplicate judge
        # and the topics into the prompt, so an extension adds to the pool instead of
        # writing a second one over it.
        old = Pool.load(path)
        known = tuple(f"{d.subject}: {d.topic}" for d in old.domains)
        for domain in old.domains:
            dedup.add(domain.name)
        print(f"extending {path}: {len(old.domains)} sub-topics already in it")
    pool = build(_llm(config), topics_per_cell=args.topics_per_cell,
                 per_topic=args.per_topic, target=args.target,
                 existing_topics=known,
                 is_duplicate=lambda name: not dedup.add(name),
                 report=print)
    if args.extend and path.exists():
        pool = Pool.load(path).merged(pool)
    written = pool.save(path)
    stats = pool.stats()
    print(f"{written}: {len(pool.topics)} topics, {len(pool.domains)} sub-topics, "
          f"{stats['tiers']}, {len(stats['cells'])} cells")


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


def cmd_figures(args: argparse.Namespace) -> None:
    """Run view selection on a hand-written answer and show what it chose and why."""
    from .s01_data.author import compose
    from .s02_figure.compose import compose_with_log

    config = Config.load(args.config).override(args.set or [])
    seed = int(config.get("root_seed", 0))
    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    table, schema = compose(payload, scenario_id=args.scenario, seed=seed, config=config)
    specs, log = compose_with_log(table, schema, seed, config)

    out = Path(args.out or config.get("output.dir", "data/generated")) / args.scenario
    for spec in specs:
        serde.save(spec, out / "specs" / f"{spec.figure_id}.json")
    print(report.figure_summary(specs, log))
    print(f"wrote {len(specs)} specs to {out}/specs")


def cmd_render(args: argparse.Namespace) -> None:
    spec = serde.load(FigureSpec, args.spec)
    style = (serde.load(StyleVector, args.style) if args.style
             else sample_style(args.seed, spec.scenario_id, spec.figure_id, args.variant))
    out = render(spec, style, args.out)
    serde.save(out, Path(args.out) / f"{spec.figure_id}.json")
    print(f"{out.image_path}: {len(out.marks)} marks")


def cmd_run(args: argparse.Namespace) -> None:
    """Run the whole pipeline. With --payload no model is called: a hand-written
    answer goes through every stage exactly as a generated one would."""
    from .pipeline import batch_stats

    config = Config.load(args.config).override(args.set or [])
    if args.scenarios:
        config.set("scale.scenarios", args.scenarios)
    pipe = Pipeline(config, Path(config.get("output.dir", "data/generated"))
                    / config.get("run_id", "dev"))

    if args.payload:
        from .s01_data.author import compose

        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        seed = int(config.get("root_seed", 0))

        def stage_01(scenario_id, **kw):
            from .pipeline import save_data

            table, schema = compose(payload, scenario_id=scenario_id, seed=seed,
                                    config=config)
            save_data(table, schema, pipe.out_dir)
            return table, schema

        pipe.stage_01 = stage_01     # type: ignore[method-assign]

    results = []
    for i in range(int(config.get("scale.scenarios", 1))):
        result = pipe.run_scenario(args.scenario if args.payload else f"s{i:03d}")
        results.append(result)
        status = "ok" if result.ok else f"failed in {result.stage}: {result.reason}"
        print(f"{result.scenario_id}  {status}  {len(result.records)} records, "
              f"{len(result.dropped)} dropped")
    stats = batch_stats(results)
    pipe.out_dir.mkdir(parents=True, exist_ok=True)
    (pipe.out_dir / "stats.json").write_text(
        json.dumps({**stats, "model": str(config.get("llm.model", "")),
                    "config": config.values}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print()
    print(report.run_summary(stats))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="chartgen")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("pool", help="build the domain pool: two levels plus dedup, once per project")
    p.add_argument("-o", "--out", type=Path, default=None)
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--topics-per-cell", type=int, default=2,
                   help="topics per (subject, register) cell; 46 cells are declared")
    p.add_argument("--per-topic", type=int, default=7)
    p.add_argument("--target", type=int, default=600,
                   help="a floor on the whole pool; the backfill tops the thin tier up")
    p.add_argument("--extend", action="store_true",
                   help="add to the pool already at --out instead of replacing it")
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

    p = sub.add_parser("figures", help="view selection only: a hand-written answer to figure specs")
    p.add_argument("--payload", type=Path, required=True)
    p.add_argument("--scenario", default="s000")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.add_argument("-o", "--out", type=Path, default=None)
    p.set_defaults(func=cmd_figures)

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
    p.add_argument("--payload", type=Path, default=None,
                   help="a hand-written answer; with this no model is called")
    p.add_argument("--scenario", default="s000")
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.set_defaults(func=cmd_run)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
