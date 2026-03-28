"""
ChartAgentPipelineRunner — orchestrates the multi-node generation pipeline.

Salvaged from generation_runner.py (L60–162 config, L169–359 runner class).

The runner's shape (single/batch execution, logging, save logic) is reusable.
For AGPDS integration, the wiring must change from Node A→B→C→D to
Phase 0→1→2→3 calls (see agpds_salvage_and_roadmap.md Subtask 5).
"""

import json
import os
import time
from datetime import datetime
from typing import Optional

from .utils import META_CATEGORIES, generate_unique_id


# =============================================================================
# LLM Configuration Helper
# =============================================================================

PROVIDER_CONFIGS = {
    "openai": {
        "env_model_key": "OPENAI_MODEL",
        "default_model": "gpt-5-mini-2025-08-07",
        "env_api_key": "OPENAI_API_KEY",
        "model_patterns": ["gpt", "o1"],
    },
    "gemini": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash-lite",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "gemini-native": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash-lite",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "azure": {
        "env_model_key": "AZURE_OPENAI_MODEL",
        "default_model": "gpt-4o",
        "env_api_key": "AZURE_OPENAI_API_KEY",
        "model_patterns": ["gpt"],
    },
}

DEFAULT_PROVIDER = "openai"


def infer_provider_from_model(model_name: str) -> str:
    """Infer provider from model name."""
    model_lower = model_name.lower()

    for provider, config in PROVIDER_CONFIGS.items():
        for pattern in config["model_patterns"]:
            if pattern in model_lower:
                return provider

    return DEFAULT_PROVIDER


def resolve_llm_config(args) -> tuple[str, str, str]:
    """
    Unified LLM configuration resolver. Returns (provider, model, api_key).

    Priority logic:
    1. Provider: --provider > infer from --model > default
    2. Model: --model > env var > default
    3. API Key: --api-key > env var
    """
    # Step 1: Determine provider
    if args.provider and args.provider != "auto":
        provider = args.provider
    elif args.model:
        provider = infer_provider_from_model(args.model)
    else:
        provider = DEFAULT_PROVIDER

    if provider not in PROVIDER_CONFIGS and provider != "custom":
        raise ValueError(
            f"Unsupported provider: {provider}\n"
            f"Supported options: "
            f"{', '.join(list(PROVIDER_CONFIGS.keys()) + ['custom'])}"
        )

    config = PROVIDER_CONFIGS.get(provider, {
        "env_model_key": "MODEL_NAME",
        "default_model": "unknown-model",
        "env_api_key": "API_KEY",
    })

    # Step 2: Determine model
    if args.model:
        model = args.model
    else:
        model = os.environ.get(config["env_model_key"], config["default_model"])

    # Step 3: Determine api_key
    if args.api_key:
        api_key = args.api_key
    else:
        api_key = os.environ.get(config["env_api_key"])

    return provider, model, api_key


# =============================================================================
# Pipeline Runner
# =============================================================================

class ChartAgentPipelineRunner:
    """
    Complete pipeline runner that integrates all nodes.

    Provides:
    - run_single(): Execute one pipeline pass with timing and logging
    - run_batch(): Execute multiple passes with diversity control
    - save_results(): Persist outputs as JSON + CSV artifacts

    For AGPDS: rewire the node calls in run_single() from
    Node A→B→C→D to Phase 0→1→2→3.
    """

    def __init__(
        self, llm_client, verbose: bool = True,
        config: Optional[dict] = None
    ):
        self.llm = llm_client
        self.verbose = verbose
        self.config = config or {}

        # NOTE: For AGPDS, replace this import with the new pipeline class.
        # Keeping the lazy import pattern so this module is importable
        # even without generation_pipeline.py present.
        self._pipeline = None

    def _ensure_pipeline(self):
        """Lazy-initialize the pipeline (defers import)."""
        if self._pipeline is None:
            try:
                from generation_pipeline import ChartAgentPipeline
                self._pipeline = ChartAgentPipeline(
                    self.llm, config=self.config
                )
            except ImportError:
                raise ImportError(
                    "ChartAgentPipeline not found. For AGPDS integration, "
                    "replace this import with the new Phase 0→1→2→3 pipeline."
                )

    @property
    def pipeline(self):
        self._ensure_pipeline()
        return self._pipeline

    def log(self, message: str):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_single(
        self, category_id: int,
        constraints: Optional[dict] = None
    ) -> dict:
        """
        Run the complete pipeline once with specified category.

        Args:
            category_id: Category ID (1-30) from META_CATEGORIES
            constraints: Optional constraints for topic generation

        Returns:
            Complete pipeline output with all chart types and captions
        """
        generation_id = generate_unique_id("gen")
        pipeline_start = time.time()
        self.log(f"Starting generation {generation_id}")

        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}. Must be between 1 and 30."
            )

        category_name = META_CATEGORIES[category_id - 1]
        self.log(f"Category: {category_name}")

        state = self.pipeline.create_initial_state()

        # Node A: Topic Generation
        self.log("  → Node A: Generating topic concept...")
        node_start = time.time()
        state = self.pipeline.node_a(
            state, category_id, category_name, constraints
        )
        node_time = time.time() - node_start
        self.log(f"  ✓ Node A completed in {node_time:.1f}s")
        self.log(f"    Concept: {state['semantic_concept']}")

        # Node B: Data Fabrication
        self.log("  → Node B: Fabricating master data...")
        node_start = time.time()
        state = self.pipeline.node_b(state)
        node_time = time.time() - node_start
        master_data = state.get("master_data", {})
        self.log(f"  ✓ Node B completed in {node_time:.1f}s")
        if isinstance(master_data, dict):
            self.log(
                f"    Entities: {len(master_data.get('entities', []))}"
            )
        elif hasattr(master_data, 'df'):
            self.log(
                f"    Rows: {len(master_data.df)}, "
                f"Columns: {len(master_data.df.columns)}"
            )

        # Node C: Schema Mapping + Caption Generation
        self.log("  → Node C: Mapping to chart schemas...")
        node_start = time.time()
        state = self.pipeline.node_c(state)
        node_time = time.time() - node_start
        self.log(f"  ✓ Node C completed in {node_time:.1f}s")
        self.log(
            f"    Schemas: {list(state.get('chart_entries', {}).keys())}"
        )

        total_time = time.time() - pipeline_start
        self.log(f"  ✓ Pipeline completed in {total_time:.1f}s total")

        # Serialize MasterTable if present
        master_data_output = state.get("master_data")
        master_data_csv = None
        if hasattr(master_data_output, "to_csv"):
            master_data_csv = master_data_output.to_csv()
            master_data_output = {
                "format": "csv",
                "content": master_data_csv,
                "metadata": getattr(master_data_output, "metadata", {})
            }

        return {
            "generation_id": generation_id,
            "category_id": state.get("category_id"),
            "category_name": state.get("category_name"),
            "semantic_concept": state.get("semantic_concept"),
            "topic_description": state.get("topic_description"),
            "master_data": master_data_output,
            "master_data_csv": master_data_csv,
            "chart_entries": state.get("chart_entries"),
            "captions": state.get("captions")
        }

    def run_batch(
        self,
        category_ids: list[int],
        constraints_list: Optional[list[dict]] = None
    ) -> list[dict]:
        """
        Run pipeline multiple times with automatic topic diversity control.

        Args:
            category_ids: List of category IDs (1-30), one per generation
            constraints_list: Optional list of constraints (one per gen)

        Returns:
            List of pipeline outputs
        """
        results = []
        count = len(category_ids)
        constraints_list = constraints_list or [None] * count

        for i, (category_id, constraints) in enumerate(
            zip(category_ids, constraints_list)
        ):
            self.log(f"\n{'='*50}")
            self.log(f"Generation {i+1}/{count}")
            self.log('='*50)

            try:
                result = self.run_single(category_id, constraints)
                results.append(result)
            except Exception as e:
                self.log(f"ERROR: Generation failed: {e}")
                import traceback
                traceback.print_exc()
                continue

        return results

    def save_results(self, results: list[dict], output_path: str):
        """
        Save results to JSON file and master data CSVs.

        Creates a ``master_tables/`` directory next to the output JSON.
        Each generation's master data is written as an individual CSV file
        named ``{generation_id}.csv``.
        """
        output_dir = os.path.dirname(os.path.abspath(output_path))
        csv_dir = os.path.join(output_dir, "master_tables")
        os.makedirs(csv_dir, exist_ok=True)

        csv_count = 0
        for result in results:
            csv_content = result.pop("master_data_csv", None)
            gen_id = result.get("generation_id", "unknown")
            if csv_content:
                csv_path = os.path.join(csv_dir, f"{gen_id}.csv")
                with open(csv_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                result["master_data_csv_path"] = os.path.join(
                    "master_tables", f"{gen_id}.csv"
                )
                csv_count += 1

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        self.log(f"Saved {len(results)} generations to {output_path}")
        if csv_count:
            self.log(f"Saved {csv_count} master table CSVs to {csv_dir}/")
