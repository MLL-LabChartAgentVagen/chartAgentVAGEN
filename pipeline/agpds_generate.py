"""Stage 1 CLI: generate LLM scripts and save them to disk.

Runs Phase 0 (domain) + Phase 1 (scenario) + Phase 2 Loop A (LLM → sandbox
validation). Each invocation creates a per-command batch folder under
--output-dir (default ./output/agpds/) named via --batch-name or
batch_<timestamp>_<hash>. Persists per generation, inside the batch folder:
  - scenarios/{gen_id}_scenario.json
  - scripts/{gen_id}.py             (LLM source)
  - declarations/{gen_id}.json      (replayable declarations)
  - manifest.jsonl                  (append one line per gen)

Stage 2 (pipeline/agpds_execute.py) reads these artifacts (point its
--input-dir at the batch folder) and runs Loop B deterministically without
calling the LLM.
"""
import argparse
import json
import os
import random
import sys
import traceback
from datetime import datetime
from typing import Optional

from pipeline.agpds_pipeline import AGPDSPipeline
from pipeline.agpds_runner import TeeLogger, resolve_batch_dir
from pipeline.core.llm_client import LLMClient
from pipeline.core.utils import META_CATEGORIES
from pipeline.phase_2.serialization import declarations_to_json


SCRIPTS_SUBDIR = "scripts"
DECLARATIONS_SUBDIR = "declarations"
SCENARIOS_SUBDIR = "scenarios"
MANIFEST_FILENAME = "manifest.jsonl"


def _log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _save_stage1_artifacts(
    output_dir: str,
    stage1: dict,
    model: str,
    provider: str,
) -> dict:
    scripts_dir = os.path.join(output_dir, SCRIPTS_SUBDIR)
    decl_dir = os.path.join(output_dir, DECLARATIONS_SUBDIR)
    scenarios_dir = os.path.join(output_dir, SCENARIOS_SUBDIR)
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(decl_dir, exist_ok=True)
    os.makedirs(scenarios_dir, exist_ok=True)

    gen_id = stage1["generation_id"]

    script_path = os.path.join(scripts_dir, f"{gen_id}.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(stage1["source_code"] or "")

    decl_path = os.path.join(decl_dir, f"{gen_id}.json")
    with open(decl_path, "w", encoding="utf-8") as f:
        json.dump(declarations_to_json(stage1["raw_declarations"]), f, indent=2)

    scenario_path = os.path.join(scenarios_dir, f"{gen_id}_scenario.json")
    with open(scenario_path, "w", encoding="utf-8") as f:
        json.dump(stage1["scenario"], f, indent=2, ensure_ascii=False)

    manifest_entry = {
        "generation_id": gen_id,
        "category_id": stage1["category_id"],
        "subtopic": stage1["domain_context"].get("name"),
        "model": model,
        "provider": provider,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "script_path": os.path.relpath(script_path, output_dir),
        "declarations_path": os.path.relpath(decl_path, output_dir),
        "scenario_path": os.path.relpath(scenario_path, output_dir),
    }

    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    with open(manifest_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(manifest_entry) + "\n")

    return manifest_entry


def run_generation_batch(
    pipeline: AGPDSPipeline,
    category_ids,
    output_dir: str,
    model: str,
    provider: str,
) -> list:
    os.makedirs(output_dir, exist_ok=True)
    produced = []
    total = len(category_ids)

    for i, category_id in enumerate(category_ids):
        _log("=" * 50)
        _log(f"Generation {i+1}/{total}  (category {META_CATEGORIES[category_id - 1]})")
        _log("=" * 50)

        try:
            stage1 = pipeline.generate_artifacts(category_id)
            entry = _save_stage1_artifacts(output_dir, stage1, model, provider)
            produced.append(entry)
            _log(f"  -> Saved script: {entry['script_path']}")
            _log(f"  -> Saved declarations: {entry['declarations_path']}")
        except Exception as exc:
            _log(f"ERROR: Stage 1 failed for category {category_id}: {exc}")
            traceback.print_exc()
            continue

    return produced


def main() -> None:
    log_dir = os.path.join(os.getcwd(), "output", "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "pipeline_generate.log")

    sys.stdout = TeeLogger(log_file_path, sys.stdout)
    sys.stderr = TeeLogger(log_file_path, sys.stderr)

    print(f"\n{'='*60}\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stage 1: Generate LLM scripts\n{'='*60}")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    parser = argparse.ArgumentParser(description="AGPDS Stage 1: generate and save LLM scripts")
    parser.add_argument("--api-key", help="LLM API Key (OpenAI/Gemini/Azure)")
    parser.add_argument("--model", default=None, help="Model name (overrides .env)")
    parser.add_argument("--provider", default=None,
                        choices=["openai", "gemini", "gemini-native", "azure", "auto"])
    parser.add_argument("--category", type=int, choices=range(1, 31), help="Category ID (1-30)")
    parser.add_argument("--count", type=int, default=1, help="Number of scripts to generate")
    parser.add_argument("--output-dir", default="./output/agpds",
                        help="Parent directory; a per-command batch folder is created beneath it.")
    parser.add_argument(
        "--batch-name",
        default=None,
        help="Folder name for this batch under --output-dir. "
             "Default: auto-generated batch_<timestamp>_<hash>.",
    )
    parser.add_argument(
        "--scenario-source",
        choices=["live", "cached", "cached_strict"],
        default="cached_strict",
        help="Phase 1 scenario source: 'live' (LLM per record), 'cached' (read "
             "from scenario_pool.jsonl, fall back to live on miss), or "
             "'cached_strict' (error on miss). Default: cached_strict.",
    )
    parser.add_argument(
        "--scenario-pool-path",
        default=None,
        help="Override path to scenario_pool.jsonl "
             "(default: pipeline/phase_1/scenario_pool.jsonl)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Console logging level. Default INFO surfaces Phase 0/1/2 milestones "
             "and scenario cache hits; WARNING silences routine pipeline chatter.",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Pipeline seed. Drives DomainSampler, scenario pick, and category "
             "fallback when --category is not given. Default: 42.",
    )
    args = parser.parse_args()

    import logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    provider = args.provider or os.environ.get("LLM_PROVIDER") or "gemini"

    if args.api_key:
        api_key = args.api_key
    elif provider in ("openai", "azure"):
        api_key = os.environ.get("OPENAI_API_KEY")
    elif provider in ("gemini", "gemini-native"):
        api_key = os.environ.get("GEMINI_API_KEY")
    else:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: API Key must be provided via --api-key or ENV variable.", file=sys.stderr)
        sys.exit(1)

    if args.model:
        model = args.model
    elif provider in ("openai", "azure"):
        model = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    elif provider in ("gemini", "gemini-native"):
        model = os.environ.get("GEMINI_MODEL") or "gemini-3.1-pro-preview"
    else:
        model = os.environ.get("OPENAI_MODEL") or os.environ.get("GEMINI_MODEL") or "gpt-4o-mini"

    print(f"Initializing LLMClient ({provider}, {model})...")
    llm = LLMClient(api_key=api_key, model=model, provider=provider)
    pipeline = AGPDSPipeline(
        llm,
        scenario_source=args.scenario_source,
        scenario_pool_path=args.scenario_pool_path,
        seed=args.seed,
    )

    _cli_rng = random.Random(args.seed)
    category_ids = (
        [args.category] * args.count if args.category
        else [_cli_rng.randint(1, 30) for _ in range(args.count)]
    )

    batch_dir = resolve_batch_dir(args.output_dir, args.batch_name)
    produced = run_generation_batch(pipeline, category_ids, batch_dir, model, provider)
    _log(f"Stage 1 complete: {len(produced)}/{len(category_ids)} generations saved.")
    print(f"Batch folder: {os.path.abspath(batch_dir)}")
    print(f"Stage 2: python -m pipeline.agpds_execute --input-dir '{batch_dir}' --output-dir '{batch_dir}'")


if __name__ == "__main__":
    main()
