import argparse
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Optional, List

from pipeline.core.llm_client import LLMClient
from pipeline.core.utils import META_CATEGORIES, generate_unique_id
from pipeline.agpds_pipeline import AGPDSPipeline

class AGPDSRunner:
    """
    CLI Runner for the AGPDS Pipeline.
    Manages LLM client initialization, batch execution, and IO artifact generation.
    """
    def __init__(
        self,
        llm_client: LLMClient,
        verbose: bool = True,
        scenario_source: str = "live",
        scenario_pool_path: Optional[str] = None,
    ):
        self.llm = llm_client
        self.verbose = verbose
        self.pipeline = AGPDSPipeline(
            self.llm,
            scenario_source=scenario_source,
            scenario_pool_path=scenario_pool_path,
        )

    def log(self, message: str):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_single(self, category_id: int, constraints: Optional[dict] = None) -> dict:
        self.log(f"Starting Generation. Category: {META_CATEGORIES[category_id - 1]}")
        return self.pipeline.run_single(category_id, constraints)

    def run_batch(self, category_ids: List[int], constraints_list: Optional[List[dict]] = None) -> List[dict]:
        results = []
        count = len(category_ids)
        constraints_list = constraints_list or [None] * count

        for i, (category_id, constraints) in enumerate(zip(category_ids, constraints_list)):
            self.log(f"\n{'='*50}")
            self.log(f"Generation {i+1}/{count}")
            self.log('='*50)

            try:
                result = self.run_single(category_id, constraints)
                results.append(result)
            except Exception as e:
                self.log(f"ERROR: Generation failed: {e}")
                traceback.print_exc()
                continue
                
        return results

    def save_results(self, results: List[dict], output_dir: str):
        """Save results to JSON file and master data CSVs appropriately."""
        csv_dir, schema_dir, charts_dir, scenarios_dir = _ensure_output_dirs(output_dir)

        json_results = []
        csv_count = 0
        charts_count = 0

        for result in results:
            chart_record, saved = save_single_result(result, output_dir)
            if saved.get("csv"):
                csv_count += 1
            if saved.get("chart"):
                charts_count += 1
            json_results.append(chart_record)

        bundle_path = write_charts_bundle(json_results, output_dir)

        self.log(f"Saved {len(results)} generations to {bundle_path}")
        if csv_count:
            self.log(f"Saved {csv_count} master table CSVs to {csv_dir}/")
            self.log(f"Saved {csv_count} metadata schemas to {schema_dir}/")
        if charts_count:
            self.log(f"Saved {charts_count} chart JSONs to {charts_dir}/")


def _ensure_output_dirs(output_dir: str) -> tuple:
    os.makedirs(output_dir, exist_ok=True)
    csv_dir = os.path.join(output_dir, "master_tables")
    schema_dir = os.path.join(output_dir, "schemas")
    charts_dir = os.path.join(output_dir, "charts")
    scenarios_dir = os.path.join(output_dir, "scenarios")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(schema_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)
    os.makedirs(scenarios_dir, exist_ok=True)
    return csv_dir, schema_dir, charts_dir, scenarios_dir


def write_charts_bundle(records: List[dict], output_dir: str) -> str:
    """Write the per-batch charts.json index. Returns the absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    bundle_path = os.path.join(output_dir, "charts.json")
    with open(bundle_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    return bundle_path


def resolve_batch_dir(output_dir: str, batch_name: Optional[str]) -> str:
    """Compute the per-command batch folder under output_dir."""
    name = batch_name or generate_unique_id("batch")
    batch_dir = os.path.join(output_dir, name)
    os.makedirs(batch_dir, exist_ok=True)
    return batch_dir


def save_single_result(result: dict, output_dir: str) -> tuple:
    """Persist one generation result (CSV + schema + chart JSON + scenario).
    Returns (chart_record, {"csv": bool, "schema": bool, "chart": bool,
    "scenario": bool})."""
    csv_dir, schema_dir, charts_dir, scenarios_dir = _ensure_output_dirs(output_dir)
    gen_id = result.get("generation_id", "unknown")
    saved = {"csv": False, "schema": False, "chart": False, "scenario": False}

    csv_content = result.get("master_data_csv")
    if csv_content:
        csv_path = os.path.join(csv_dir, f"{gen_id}.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        result["master_data_csv_path"] = os.path.join("master_tables", f"{gen_id}.csv")
        saved["csv"] = True

    schema_content = result.get("schema_metadata")
    if schema_content:
        schema_path = os.path.join(schema_dir, f"{gen_id}_metadata.json")
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(schema_content, f, indent=2)
        result["schema_metadata_path"] = os.path.join("schemas", f"{gen_id}_metadata.json")
        saved["schema"] = True

    scenario_content = result.get("scenario")
    if scenario_content:
        scenario_path = os.path.join(scenarios_dir, f"{gen_id}_scenario.json")
        with open(scenario_path, 'w', encoding='utf-8') as f:
            json.dump(scenario_content, f, indent=2, ensure_ascii=False)
        result["scenario_path"] = os.path.join("scenarios", f"{gen_id}_scenario.json")
        saved["scenario"] = True

    chart_record = {
        k: v for k, v in result.items()
        if k not in ("master_data_csv", "schema_metadata")
    }
    chart_record["charts_path"] = os.path.join("charts", f"{gen_id}.json")
    result["charts_path"] = chart_record["charts_path"]
    charts_path = os.path.join(charts_dir, f"{gen_id}.json")
    with open(charts_path, 'w', encoding='utf-8') as f:
        json.dump(chart_record, f, indent=2)
    saved["chart"] = True

    return chart_record, saved


class TeeLogger:
    def __init__(self, filename, stream):
        self.stream = stream
        self.log_file = open(filename, 'a', encoding='utf-8')

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        self.log_file.write(data)
        self.log_file.flush()

    def flush(self):
        self.stream.flush()
        self.log_file.flush()

    def isatty(self):
        return hasattr(self.stream, 'isatty') and self.stream.isatty()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def main():
    log_dir = os.path.join(os.getcwd(), "output", "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "pipeline_run.log")

    sys.stdout = TeeLogger(log_file_path, sys.stdout)
    sys.stderr = TeeLogger(log_file_path, sys.stderr)

    print(f"\n{'='*60}\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting new pipeline run\n{'='*60}")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    parser = argparse.ArgumentParser(description="AGPDS Pipeline Execution")
    parser.add_argument("--api-key", help="LLM API Key (OpenAI/Gemini/Azure)")
    parser.add_argument("--model", default=None, help="Model name (overrides .env OPENAI_MODEL/GEMINI_MODEL)")
    parser.add_argument("--provider", default=None, choices=["openai", "gemini", "gemini-native", "azure", "auto"],
                        help="Provider (overrides .env LLM_PROVIDER)")
    parser.add_argument("--category", type=int, choices=range(1, 31), help="Specific Category ID (1-30)")
    parser.add_argument("--count", type=int, default=1, help="Number of generations to run")
    parser.add_argument("--output-dir", default="./output/agpds", help="Parent directory for batch folders")
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
    args = parser.parse_args()

    import logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Resolve provider: CLI flag > .env LLM_PROVIDER > "gemini"
    provider = args.provider or os.environ.get("LLM_PROVIDER") or "gemini"

    if args.api_key:
        api_key = args.api_key
    elif provider in ("openai", "azure"):
        api_key = os.environ.get("OPENAI_API_KEY")
    elif provider in ("gemini", "gemini-native"):
        api_key = os.environ.get("GEMINI_API_KEY")
    else:  # auto / custom fallback
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: API Key must be provided via --api-key or ENV variable.", file=sys.stderr)
        sys.exit(1)

    # Resolve model: CLI flag > provider-specific .env var > hardcoded fallback
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
    
    runner = AGPDSRunner(
        llm_client=llm,
        scenario_source=args.scenario_source,
        scenario_pool_path=args.scenario_pool_path,
    )

    import random
    category_ids = [args.category] * args.count if args.category else [random.randint(1, 30) for _ in range(args.count)]
    
    results = runner.run_batch(category_ids)
    if results:
        batch_dir = resolve_batch_dir(args.output_dir, args.batch_name)
        runner.save_results(results, batch_dir)
        print(f"Batch folder: {os.path.abspath(batch_dir)}")

if __name__ == "__main__":
    main()
