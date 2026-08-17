"""命令行：单阶段运行（拿样例文件当输入）、指定场景重跑、批量生成。

    python -m chartgen.cli render tests/samples/figure_spec.json -o out/demo
    python -m chartgen.cli run --scenarios 3
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import Config
from .interfaces import io
from .interfaces.figure import FigureSpec
from .interfaces.style import StyleVector
from .pipeline import Pipeline
from .s03_render.render import render
from .s03_render.style import sample as sample_style


def cmd_render(args: argparse.Namespace) -> None:
    spec = io.load(FigureSpec, args.spec)
    style = (io.load(StyleVector, args.style) if args.style
             else sample_style(args.seed, spec.scenario_id, spec.figure_id, args.variant))
    out = render(spec, style, args.out)
    io.save(out, Path(args.out) / f"{spec.figure_id}.json")
    print(f"{out.image_path}  图元 {len(out.marks)} 个")


def cmd_run(args: argparse.Namespace) -> None:
    config = Config.load(args.config).override(args.set or [])
    if args.scenarios:
        config.set("scale.scenarios", args.scenarios)
    pipe = Pipeline(config, Path(config.get("output.dir", "out")) / config.get("run_id", "dev"))
    for i in range(int(config.get("scale.scenarios", 1))):
        result = pipe.run_scenario(f"s{i:03d}")
        status = "通过" if result.ok else f"失败于 {result.stage}: {result.reason}"
        print(f"{result.scenario_id}  {status}  记录 {len(result.records)} 份")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="chartgen")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("render", help="只跑 03：FigureSpec + 风格 → 图像与几何")
    p.add_argument("spec", type=Path)
    p.add_argument("--style", type=Path, default=None)
    p.add_argument("--variant", type=int, default=0)
    p.add_argument("--seed", type=int, default=20260816)
    p.add_argument("-o", "--out", type=Path, default=Path("out/render"))
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("run", help="跑整条流水线")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--scenarios", type=int, default=None)
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.set_defaults(func=cmd_run)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
