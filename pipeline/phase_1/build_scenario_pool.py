#!/usr/bin/env python3
"""
Build Scenario Pool — One-Shot Offline Script

Reads pipeline/phase_0/domain_pool.json, runs ScenarioContextualizer K times
per domain in parallel, deduplicates, and writes the compiled scenarios to
pipeline/phase_1/scenario_pool.jsonl (one JSON envelope per line).

Usage:
    # From the project root (default: K=3 scenarios per domain, ~900 total):
    python pipeline/phase_1/build_scenario_pool.py

    # Force regeneration from scratch:
    python pipeline/phase_1/build_scenario_pool.py --force

    # Smaller pool (one scenario per domain, ~300 total):
    python pipeline/phase_1/build_scenario_pool.py --scenarios-per-domain 1

Requirements:
    - GEMINI_API_KEY (or OPENAI_API_KEY) set in .env or as an env var (generation)
    - OPENAI_API_KEY for embeddings (required by the dedup step)
"""

import argparse
import json
import logging
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (all relative to project root)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
POOL_PATH    = PROJECT_ROOT / "pipeline" / "phase_0" / "domain_pool.json"
OUT_PATH     = PROJECT_ROOT / "pipeline" / "phase_1" / "scenario_pool.jsonl"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("build_scenario_pool")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the AGPDS scenario pool from domain_pool.json"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing scenario_pool.jsonl and rebuild from scratch",
    )
    parser.add_argument(
        "--scenarios-per-domain",
        type=int,
        default=3,
        metavar="K",
        help="Scenarios generated per domain (default: 3)",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.4-mini-2026-03-17",
        help="LLM model to use (default: gpt-5.4-mini-2026-03-17)",
    )
    parser.add_argument(
        "--max-domains",
        type=int,
        default=None,
        help="Only process the first N domains (smoke test)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel LLM workers (default: 4)",
    )
    parser.add_argument(
        "--skip-dedup",
        action="store_true",
        help="Skip the final scenario dedup step",
    )
    parser.add_argument(
        "--dedup-scope",
        choices=["global", "category", "domain"],
        default="category",
        help=(
            "Scenario dedup comparison scope "
            "(default: category; choices: global, category, domain)"
        ),
    )
    parser.add_argument(
        "--dedup-threshold",
        type=float,
        default=0.85,
        help="Cosine-similarity threshold for dedup (default: 0.85)",
    )
    parser.add_argument(
        "--min-scenarios-per-domain",
        type=int,
        default=1,
        help=(
            "Minimum cached scenarios to preserve per domain during dedup "
            "(default: 1)"
        ),
    )
    return parser.parse_args()


def load_api_key() -> str:
    """Load API key from .env file or environment variables."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            log.info("Loaded .env from %s", env_file)
        except ImportError:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())

    key = os.environ.get("OPENAI_API_KEY")
    if key:
        log.info("Using API key from OPENAI_API_KEY")
        return key

    log.error("No API key found. Set OPENAI_API_KEY in your .env file.")
    sys.exit(1)


def _category_id_for_topic(topic: str, categories: list[str]) -> int:
    """Reverse-lookup category_id (1..30) from a META_CATEGORIES entry that
    ends with ' - <topic>'. Returns -1 if not found."""
    for i, c in enumerate(categories, start=1):
        if c.endswith(f" - {topic}"):
            return i
    return -1


def main() -> None:
    args = parse_args()

    # -----------------------------------------------------------------------
    # Validate input
    # -----------------------------------------------------------------------
    if not POOL_PATH.exists():
        log.error(
            "Domain pool not found: %s\n"
            "Run `python pipeline/phase_0/build_domain_pool.py` first.",
            POOL_PATH,
        )
        sys.exit(1)

    with open(POOL_PATH) as f:
        pool = json.load(f)
    domains: list[dict] = pool["domains"]
    if args.max_domains is not None:
        domains = domains[: args.max_domains]
        log.info("Limiting to first %d domains (smoke test)", len(domains))
    log.info("Domain pool has %d domains", len(domains))

    # -----------------------------------------------------------------------
    # Resume support — skip (domain_id, k) pairs already persisted
    # -----------------------------------------------------------------------
    if args.force and OUT_PATH.exists():
        OUT_PATH.unlink()
        log.info("--force: removed existing %s", OUT_PATH)

    existing: set[tuple[str, int]] = set()
    if OUT_PATH.exists():
        with open(OUT_PATH) as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                existing.add((rec["domain_id"], rec.get("k", 0)))
        log.info("Resuming: %d scenarios already persisted", len(existing))

    # -----------------------------------------------------------------------
    # Plan the work
    # -----------------------------------------------------------------------
    targets: list[tuple[dict, int]] = [
        (d, k)
        for d in domains
        for k in range(args.scenarios_per_domain)
        if (d["id"], k) not in existing
    ]
    if not targets:
        log.info("Nothing to do — all (domain, k) pairs already persisted.")
    else:
        log.info(
            "Generating %d scenarios (%d domains × K=%d, %d already done)",
            len(targets),
            len(domains),
            args.scenarios_per_domain,
            len(existing),
        )

    # -----------------------------------------------------------------------
    # Set up LLM + Contextualizer
    # -----------------------------------------------------------------------
    if targets:
        api_key = load_api_key()
        sys.path.insert(0, str(PROJECT_ROOT))

        from pipeline.core.llm_client import LLMClient
        from pipeline.core.utils import META_CATEGORIES
        from pipeline.phase_1 import ScenarioContextualizer

        # Use thread-local clients: Gemini's httpx async client is not safe to
        # share across threads (raises "client has been closed").
        _local = threading.local()

        def _get_ctx() -> ScenarioContextualizer:
            if not hasattr(_local, "ctx"):
                _local.ctx = ScenarioContextualizer(
                    LLMClient(api_key=api_key, model=args.model)
                )
            return _local.ctx

        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        write_lock = threading.Lock()

        def gen_one(domain: dict, k: int) -> dict:
            scenario = _get_ctx().generate(domain)
            category_id = _category_id_for_topic(
                domain.get("topic", ""), META_CATEGORIES
            )
            return {
                "domain_id": domain["id"],
                "k": k,
                "category_id": category_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "scenario": scenario,
            }

        # Append-mode streaming: every finished record hits disk immediately
        # so a crash leaves the file resumable.
        done = 0
        with open(OUT_PATH, "a", encoding="utf-8") as out_f, \
                ThreadPoolExecutor(max_workers=args.workers) as pool_exec:
            futures = {
                pool_exec.submit(gen_one, d, k): (d["id"], k)
                for d, k in targets
            }
            for fut in as_completed(futures):
                domain_id, k = futures[fut]
                try:
                    rec = fut.result()
                except Exception as exc:  # noqa: BLE001
                    log.warning("Failed %s/k=%d: %s", domain_id, k, exc)
                    continue
                with write_lock:
                    out_f.write(
                        json.dumps(rec, ensure_ascii=False) + "\n"
                    )
                    out_f.flush()
                done += 1
                if done % 25 == 0:
                    log.info("  progress: %d/%d", done, len(targets))

        log.info("Generated %d/%d scenarios", done, len(targets))

    # -----------------------------------------------------------------------
    # Dedup (optional, in place)
    # -----------------------------------------------------------------------
    if not args.skip_dedup and OUT_PATH.exists():
        sys.path.insert(0, str(PROJECT_ROOT))
        from pipeline.phase_1 import deduplicate_scenario_records

        with open(OUT_PATH) as f:
            records = [json.loads(ln) for ln in f if ln.strip()]

        survivors = deduplicate_scenario_records(
            records,
            threshold=args.dedup_threshold,
            scope=args.dedup_scope,
            min_per_domain=args.min_scenarios_per_domain,
        )
        removed = len(records) - len(survivors)
        covered_domains = {r["domain_id"] for r in survivors}

        # Rewrite only if dedup removed anything, to avoid gratuitous churn
        if removed:
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                for r in survivors:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        log.info(
            "Dedup (%s): kept %d, removed %d, domains covered %d",
            args.dedup_scope,
            len(survivors),
            removed,
            len(covered_domains),
        )

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    final_count = 0
    if OUT_PATH.exists():
        with open(OUT_PATH) as f:
            final_count = sum(1 for ln in f if ln.strip())

    print("\n" + "=" * 60)
    print("  Scenario Pool Build Complete")
    print("=" * 60)
    print(f"  Output file        : {OUT_PATH}")
    print(f"  Total scenarios    : {final_count}")
    print(f"  Scenarios/domain   : {args.scenarios_per_domain}")
    print(f"  Dedup threshold    : {args.dedup_threshold if not args.skip_dedup else 'skipped'}")
    print(f"  Dedup scope        : {args.dedup_scope if not args.skip_dedup else 'skipped'}")
    print(f"  Min/domain kept    : {args.min_scenarios_per_domain if not args.skip_dedup else 'skipped'}")
    print("=" * 60 + "\n")
    print("Next step: construct AGPDSPipeline with scenario_source='cached'.")


if __name__ == "__main__":
    main()
