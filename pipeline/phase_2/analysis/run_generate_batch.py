"""Resilient driver: generate the tier-balanced batch one scenario at a time.

Reads the tier sidecar (generation_id -> {scenario_id, complexity_tier, ...}),
runs ``agpds_generate --scenario-id`` per scenario, and treats any failure
(LLM error, calibration crash, skip) as a skip and continues. Stops generating
for a tier once it reaches ``--target-per-tier`` successes, to cap LLM cost.

A success is detected by the appearance of ``declarations/{gen_id}.json``.
Progress is logged to stdout and appended to ``{batch}/generate_progress.log``.

Assumes the environment already has provider API keys loaded (e.g. via a prior
``set -a; source .env; set +a``). Read-only w.r.t. source; writes only into the
batch output dir.

Usage:
    python -m pipeline.phase_2.analysis.run_generate_batch \\
        --batch-dir output/agpds/ks-measure-n90 \\
        --tier-map output/agpds/ks-measure-n90/tier_map.json \\
        --seed 42 --provider gemini --target-per-tier 30 --timeout 300
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-dir", required=True, type=Path)
    ap.add_argument("--tier-map", required=True, type=Path)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--provider", default="gemini")
    ap.add_argument("--target-per-tier", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args(argv)

    tier_map: dict[str, dict] = json.loads(args.tier_map.read_text())
    # Order: interleave tiers so an early failure run is still balanced.
    entries = list(tier_map.items())  # [(gid, info), ...]
    decl_dir = args.batch_dir / "declarations"
    log_path = args.batch_dir / "generate_progress.log"

    success: dict[str, int] = defaultdict(int)
    attempted: dict[str, int] = defaultdict(int)

    def log(msg: str) -> None:
        print(msg, flush=True)
        with log_path.open("a") as f:
            f.write(msg + "\n")

    total = len(entries)
    log(f"=== batch generate: {total} candidate scenarios, "
        f"target {args.target_per_tier}/tier ===")

    for idx, (gid, info) in enumerate(entries, 1):
        tier = info["complexity_tier"]
        sid = info["scenario_id"]
        if success[tier] >= args.target_per_tier:
            continue
        if (decl_dir / f"{gid}.json").exists():
            success[tier] += 1
            log(f"[{idx}/{total}] {sid} ({tier}) ALREADY-DONE "
                f"-> {tier} {success[tier]}/{args.target_per_tier}")
            continue

        attempted[tier] += 1
        cmd = [
            sys.executable, "-m", "pipeline.agpds_generate",
            "--scenario-id", sid, "--scenario-source", "cached_strict",
            "--batch-name", args.batch_dir.name,
            "--output-dir", str(args.batch_dir.parent),
            "--seed", str(args.seed), "--provider", args.provider,
            "--log-level", "WARNING",
        ]
        outcome = "FAIL"
        try:
            subprocess.run(cmd, timeout=args.timeout, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            outcome = "TIMEOUT"
        if (decl_dir / f"{gid}.json").exists():
            success[tier] += 1
            outcome = "OK"
        log(f"[{idx}/{total}] {sid} ({tier}) {outcome} "
            f"-> {tier} {success[tier]}/{args.target_per_tier} "
            f"(attempted {attempted[tier]})")

        if all(success[t] >= args.target_per_tier
               for t in ("simple", "medium", "complex")):
            log("All tiers reached target. Stopping.")
            break

    log(f"=== DONE: success {dict(success)} attempted {dict(attempted)} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
