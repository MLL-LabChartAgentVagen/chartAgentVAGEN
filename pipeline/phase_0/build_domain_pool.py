#!/usr/bin/env python3
"""
Build Domain Pool — One-Shot Offline Script

Reads 30 seed topics from metadata/taxonomy_seed.json, calls the LLM to
generate ~7 subtopics per topic (~210 total), deduplicates, and saves the
compiled pool to metadata/domain_pool.json.

Usage:
    # From the project root:
    python scripts/build_domain_pool.py

    # Force regeneration, even if domain_pool.json already exists:
    python scripts/build_domain_pool.py --force

Requirements:
    - GEMINI_API_KEY (or OPENAI_API_KEY) set in .env or as an env var
    - pip install google-genai python-dotenv (or openai)
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (all relative to project root)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_PATH    = PROJECT_ROOT / "pipeline" / "phase_0" / "taxonomy_seed.json"
POOL_PATH    = PROJECT_ROOT / "pipeline" / "phase_0" / "domain_pool.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("build_domain_pool")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the AGPDS domain pool from taxonomy_seed.json"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate domain_pool.json even if it already exists",
    )
    parser.add_argument(
        "--subtopics-per-topic",
        type=int,
        default=10,
        metavar="N",
        help="Number of subtopics to generate per seed topic (default: 10)",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-pro",
        help="LLM model to use (default: gemini-2.5-pro)",
    )
    return parser.parse_args()


def load_api_key() -> str:
    """Load API key from .env file or environment variables."""
    # Try loading .env
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            log.info("Loaded .env from %s", env_file)
        except ImportError:
            # Manual parse of simple KEY=VALUE .env
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())

    for var in ("GEMINI_API_KEY", "OPENAI_API_KEY"):
        key = os.environ.get(var)
        if key:
            log.info("Using API key from %s", var)
            return key

    log.error(
        "No API key found. Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
    )
    sys.exit(1)


def main() -> None:
    args = parse_args()

    # -----------------------------------------------------------------------
    # Validate input
    # -----------------------------------------------------------------------
    if not SEED_PATH.exists():
        log.error("Seed file not found: %s", SEED_PATH)
        sys.exit(1)

    with open(SEED_PATH) as f:
        seed_data = json.load(f)
    n_seeds = len(seed_data.get("domains", []))
    log.info("Seed file has %d topics", n_seeds)

    # Early exit if pool already exists and --force not given
    if POOL_PATH.exists() and not args.force:
        with open(POOL_PATH) as f:
            existing = json.load(f)
        n_existing = len(existing.get("domains", []))
        log.info(
            "domain_pool.json already exists with %d domains. "
            "Skip (use --force to regenerate).",
            n_existing,
        )
        return

    # -----------------------------------------------------------------------
    # Set up LLM + DomainPool
    # -----------------------------------------------------------------------
    api_key = load_api_key()

    # Add project pipeline to path
    sys.path.insert(0, str(PROJECT_ROOT))

    from pipeline.core.llm_client import LLMClient
    from pipeline.phase_0.domain_pool import DomainPool

    llm = LLMClient(api_key=api_key, model=args.model)
    pool_builder = DomainPool(
        llm_client=llm,
        pool_path=str(POOL_PATH),
        seed_path=str(SEED_PATH),
    )

    # -----------------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------------
    target = n_seeds * args.subtopics_per_topic
    log.info(
        "Building pool: %d topics × %d subtopics = ~%d domains …",
        n_seeds,
        args.subtopics_per_topic,
        target,
    )

    pool = pool_builder.load_or_build(
        subtopics_per_topic=args.subtopics_per_topic,
        force=args.force,
    )

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Domain Pool Build Complete")
    print("=" * 60)
    print(f"  Output file   : {POOL_PATH}")
    print(f"  Total domains : {pool['total_domains']}")
    print(f"  Diversity     : {pool.get('diversity_score', 'N/A')}")
    print(f"  Complexity    : {pool.get('complexity_distribution', {})}")
    print("=" * 60 + "\n")
    print("Next step: run agpds_pipeline.py — it will read domain_pool.json automatically.")


if __name__ == "__main__":
    main()
