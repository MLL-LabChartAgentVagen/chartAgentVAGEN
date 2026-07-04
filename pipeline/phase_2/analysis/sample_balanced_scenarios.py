"""Sample a tier-balanced set of scenario_ids from the Phase 1 pool.

Picks ``--per-tier`` scenario_ids from each complexity tier (deterministically,
seeded), prints the ``dom_NNN/k=N`` ids (one per line, for the generate driver),
and writes a sidecar JSON mapping ``generation_id(seed, scenario_id) -> {scenario_id,
domain_id, k, complexity_tier, target_rows}`` so the audit can join tiers without
re-deriving them.

This is read-only w.r.t. pipeline state; it only writes the sidecar at ``--out``.

Usage:
    python -m pipeline.phase_2.analysis.sample_balanced_scenarios \\
        --per-tier 35 --seed 42 \\
        --out output/agpds/ks-measure-n90/tier_map.json \\
        --ids-out output/agpds/ks-measure-n90/scenario_ids.txt
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from pipeline.core.ids import generation_id, format_scenario_id


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool-path", type=Path,
                    default=Path("pipeline/phase_1/scenario_pool.jsonl"))
    ap.add_argument("--per-tier", type=int, default=35,
                    help="Scenario_ids to sample per tier (over-sample past target).")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, required=True,
                    help="Sidecar JSON: generation_id -> tier metadata.")
    ap.add_argument("--ids-out", type=Path, default=None,
                    help="Optional newline-delimited scenario_id list for the driver.")
    args = ap.parse_args(argv)

    by_tier: dict[str, list[dict]] = defaultdict(list)
    with args.pool_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            by_tier[rec["complexity_tier"]].append(rec)

    rng = random.Random(args.seed)
    chosen: list[dict] = []
    for tier in ("simple", "medium", "complex"):
        pool = by_tier.get(tier, [])
        k = min(args.per_tier, len(pool))
        chosen.extend(rng.sample(pool, k))
        print(f"{tier}: pool={len(pool)} sampled={k}")

    sidecar: dict[str, dict] = {}
    ids: list[str] = []
    for rec in chosen:
        sid = format_scenario_id(rec["domain_id"], rec["k"])
        gid = generation_id(args.seed, sid)
        sidecar[gid] = {
            "scenario_id": sid,
            "domain_id": rec["domain_id"],
            "k": rec["k"],
            "complexity_tier": rec["complexity_tier"],
            "target_rows": rec["scenario"].get("target_rows"),
        }
        ids.append(sid)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(sidecar, indent=2))
    print(f"Wrote tier sidecar ({len(sidecar)} entries) -> {args.out}")

    if args.ids_out:
        args.ids_out.parent.mkdir(parents=True, exist_ok=True)
        args.ids_out.write_text("\n".join(ids) + "\n")
        print(f"Wrote {len(ids)} scenario_ids -> {args.ids_out}")
    else:
        for sid in ids:
            print(sid)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
