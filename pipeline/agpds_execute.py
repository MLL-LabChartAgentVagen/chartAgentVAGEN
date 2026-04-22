"""Stage 2 CLI: execute saved LLM scripts in parallel, no LLM calls.

Reads each declarations file produced by `pipeline.agpds_generate` and runs
Phase 2 Loop B (deterministic generation + validation + auto-fix) to produce
the final CSV / schema / chart JSON under --output-dir.

Parallelism: uses ProcessPoolExecutor(max_workers=--workers).
"""
import argparse
import glob
import json
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from typing import Optional

from pipeline.agpds_runner import TeeLogger, save_single_result
from pipeline.phase_2.exceptions import SkipResult
from pipeline.phase_2.pipeline import run_loop_b_from_declarations
from pipeline.phase_2.serialization import declarations_from_json


DECLARATIONS_SUBDIR = "declarations"
MANIFEST_FILENAME = "manifest.jsonl"


def _log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _load_manifest(input_dir: str) -> dict:
    """Return {gen_id: manifest_entry} for any manifest.jsonl present."""
    path = os.path.join(input_dir, MANIFEST_FILENAME)
    if not os.path.exists(path):
        return {}
    entries = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            gid = rec.get("generation_id")
            if gid:
                entries[gid] = rec
    return entries


def _discover(input_dir: str, ids_filter: Optional[set]) -> list:
    decl_dir = os.path.join(input_dir, DECLARATIONS_SUBDIR)
    if not os.path.isdir(decl_dir):
        raise FileNotFoundError(
            f"Declarations directory not found: {decl_dir}\n"
            "Run `python -m pipeline.agpds_generate` first."
        )

    paths = sorted(glob.glob(os.path.join(decl_dir, "*.json")))
    work = []
    for p in paths:
        gen_id = os.path.splitext(os.path.basename(p))[0]
        if ids_filter and gen_id not in ids_filter:
            continue
        work.append((gen_id, p))
    return work


def _execute_one(gen_id: str, declarations_path: str, output_dir: str,
                 manifest_entry: Optional[dict]) -> dict:
    """Worker: load declarations, run Loop B, save CSV/metadata/chart."""
    try:
        with open(declarations_path, "r", encoding="utf-8") as f:
            raw_declarations = declarations_from_json(json.load(f))

        result = run_loop_b_from_declarations(raw_declarations, max_retries=3)

        if isinstance(result, SkipResult):
            return {
                "generation_id": gen_id,
                "status": "failed",
                "error": "; ".join(result.error_log or ["Loop B exhausted"]),
            }

        df, schema_metadata, val_report = result

        payload = {
            "generation_id": gen_id,
            "category_id": (manifest_entry or {}).get("category_id"),
            "domain_context": {"name": (manifest_entry or {}).get("subtopic")},
            "scenario": {},
            "master_data_csv": df.to_csv(index=False),
            "schema_metadata": schema_metadata,
        }

        save_single_result(payload, output_dir)

        return {
            "generation_id": gen_id,
            "status": "ok",
            "rows": len(df),
            "validation_passed": val_report.all_passed,
        }
    except Exception as exc:
        return {
            "generation_id": gen_id,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def main() -> None:
    log_dir = os.path.join(os.getcwd(), "output", "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "pipeline_execute.log")

    sys.stdout = TeeLogger(log_file_path, sys.stdout)
    sys.stderr = TeeLogger(log_file_path, sys.stderr)

    print(f"\n{'='*60}\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stage 2: Execute saved scripts\n{'='*60}")

    parser = argparse.ArgumentParser(description="AGPDS Stage 2: execute saved scripts")
    parser.add_argument("--input-dir", default="./output/agpds",
                        help="Directory that holds declarations/ (and optional manifest.jsonl)")
    parser.add_argument("--output-dir", default="./output/agpds",
                        help="Directory for CSV/schema/chart outputs")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument("--ids", default=None,
                        help="Comma-separated generation IDs to execute (default: all)")
    args = parser.parse_args()

    ids_filter = None
    if args.ids:
        ids_filter = {s.strip() for s in args.ids.split(",") if s.strip()}

    work = _discover(args.input_dir, ids_filter)
    if not work:
        _log("No declarations to execute.")
        return

    manifest = _load_manifest(args.input_dir)
    _log(f"Found {len(work)} declaration file(s). Dispatching with workers={args.workers}.")

    results = []
    if args.workers <= 1:
        for gen_id, path in work:
            _log(f"  -> executing {gen_id}")
            results.append(_execute_one(gen_id, path, args.output_dir, manifest.get(gen_id)))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(_execute_one, gen_id, path, args.output_dir, manifest.get(gen_id)): gen_id
                for gen_id, path in work
            }
            for fut in as_completed(futures):
                gen_id = futures[fut]
                try:
                    results.append(fut.result())
                except Exception as exc:
                    results.append({
                        "generation_id": gen_id,
                        "status": "error",
                        "error": f"worker crashed: {exc}",
                    })
                _log(f"  -> done {gen_id}")

    ok = sum(1 for r in results if r.get("status") == "ok")
    failed = len(results) - ok
    _log(f"Stage 2 complete: {ok} succeeded, {failed} failed.")

    for r in results:
        if r.get("status") != "ok":
            _log(f"  ! {r['generation_id']}: {r.get('error')}")


if __name__ == "__main__":
    main()
