import argparse
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Optional, List

from pipeline.core.llm_client import LLMClient
from pipeline.core.utils import META_CATEGORIES
from pipeline.agpds_pipeline import AGPDSPipeline

class AGPDSRunner:
    """
    CLI Runner for the AGPDS Pipeline.
    Manages LLM client initialization, batch execution, and IO artifact generation.
    """
    def __init__(self, llm_client: LLMClient, verbose: bool = True):
        self.llm = llm_client
        self.verbose = verbose
        self.pipeline = AGPDSPipeline(self.llm)

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
        os.makedirs(output_dir, exist_ok=True)
        
        csv_dir = os.path.join(output_dir, "master_tables")
        schema_dir = os.path.join(output_dir, "schemas")
        charts_dir = os.path.join(output_dir, "charts")
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(schema_dir, exist_ok=True)
        os.makedirs(charts_dir, exist_ok=True)

        json_results = []
        csv_count = 0
        charts_count = 0

        for result in results:
            gen_id = result.get("generation_id", "unknown")
            
            # Save CSV
            csv_content = result.get("master_data_csv")
            if csv_content:
                csv_path = os.path.join(csv_dir, f"{gen_id}.csv")
                with open(csv_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                result["master_data_csv_path"] = os.path.join("master_tables", f"{gen_id}.csv")
                csv_count += 1
                
            # Save Schema Metadata
            schema_content = result.get("schema_metadata")
            if schema_content:
                schema_path = os.path.join(schema_dir, f"{gen_id}_metadata.json")
                with open(schema_path, 'w', encoding='utf-8') as f:
                    json.dump(schema_content, f, indent=2)
                result["schema_metadata_path"] = os.path.join("schemas", f"{gen_id}_metadata.json")

            # Save per-generation chart JSON (same basename as master_tables)
            result["charts_path"] = os.path.join("charts", f"{gen_id}.json")
            charts_path = os.path.join(charts_dir, f"{gen_id}.json")
            with open(charts_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            charts_count += 1

            json_results.append(result)

        # Save main charts bundle (all generations combined)
        output_path = os.path.join(output_dir, "charts.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2)

        self.log(f"Saved {len(results)} generations to {output_path}")
        if csv_count:
            self.log(f"Saved {csv_count} master table CSVs to {csv_dir}/")
            self.log(f"Saved {csv_count} metadata schemas to {schema_dir}/")
        if charts_count:
            self.log(f"Saved {charts_count} chart JSONs to {charts_dir}/")


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
    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Model name")
    parser.add_argument("--provider", default="gemini", choices=["openai", "gemini", "gemini-native", "azure", "auto"])
    parser.add_argument("--category", type=int, choices=range(1, 31), help="Specific Category ID (1-30)")
    parser.add_argument("--count", type=int, default=1, help="Number of generations to run")
    parser.add_argument("--output-dir", default="./output/agpds", help="Output directory path")
    args = parser.parse_args()

    if args.api_key:
        api_key = args.api_key
    elif args.provider in ("openai", "azure"):
        api_key = os.environ.get("OPENAI_API_KEY")
    elif args.provider in ("gemini", "gemini-native"):
        api_key = os.environ.get("GEMINI_API_KEY")
    else:  # auto / custom fallback
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: API Key must be provided via --api-key or ENV variable.", file=sys.stderr)
        sys.exit(1)

    # Resolve model: CLI flag > provider-specific ENV var > argument default
    model = args.model
    if not args.model or args.model == parser.get_default("model"):
        if args.provider in ("openai", "azure"):
            model = os.environ.get("OPENAI_MODEL") or args.model
        elif args.provider in ("gemini", "gemini-native"):
            model = os.environ.get("GEMINI_MODEL") or args.model

    print(f"Initializing LLMClient ({args.provider}, {model})...")
    llm = LLMClient(api_key=api_key, model=model, provider=args.provider)
    
    runner = AGPDSRunner(llm_client=llm)

    import random
    category_ids = [args.category] * args.count if args.category else [random.randint(1, 30) for _ in range(args.count)]
    
    results = runner.run_batch(category_ids)
    if results:
        runner.save_results(results, args.output_dir)

if __name__ == "__main__":
    main()
