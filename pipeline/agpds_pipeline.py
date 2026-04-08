import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

# Phase 0, 1, 2 AGPDS Imports
from pipeline.phase_0.domain_pool import DomainSampler
from pipeline.phase_1.scenario_contextualizer import ScenarioContextualizer
from pipeline.phase_2.pipeline import run_phase2
from pipeline.phase_2.exceptions import SkipResult

logger = logging.getLogger(__name__)


class AGPDSPipeline:
    """
    Main orchestrator for the Atomic-Grain Programmatic Data Synthesis (AGPDS) pipeline.

    Phases:
      0. Domain Pool: Sample a fine-grained subtopic domain from the compiled pool
      1. Scenario Contextualization: LLM generates a structured scenario
      2. Sandbox Execution: LLM generates SDK logic -> Sandbox runs it -> (DataFrame, SchemaMetadata)
      3. Schema Mapping: Deterministic adapters project the dataset to Chart metadata

    Before running for the first time, generate the domain pool:
        python scripts/build_domain_pool.py
    """

    def __init__(self, llm_client, pool_path: str = None):
        self.llm = llm_client

        # Resolve the compiled domain pool path
        if pool_path is None:
            pool_path = os.path.join(
                os.path.dirname(__file__), "phase_0", "domain_pool.json"
            )
        pool_path = os.path.abspath(pool_path)

        if not os.path.exists(pool_path):
            raise FileNotFoundError(
                f"Domain pool not found at: {pool_path}\n"
                "Run the build script first:\n"
                "  python scripts/build_domain_pool.py"
            )

        self.domain_sampler = DomainSampler(pool_path=pool_path)
        self.contextualizer = ScenarioContextualizer(llm_client)

    def run_single(self, category_id: int, constraints: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute one full end-to-end generation pass.

        Args:
            category_id: ID of the category (1-30) to generate data for
            constraints: Optional dictionary of constraints (avoid_concepts, etc.)

        Returns:
            Dictionary containing scenario, CSV, Metadata, and Charts
        """
        start_time = datetime.now()
        generation_id = f"agpds_{start_time.strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(start_time).encode()).hexdigest()[:6]}"

        logger.info(f"[{generation_id}] Starting AGPDS Phase 0-3 Generation")

        # Phase 0: Sample Domain
        logger.info("  -> Phase 0: Sampling Domain...")

        from pipeline.core.utils import get_category_by_id
        category_str = get_category_by_id(category_id)
        topic_filter = None
        if category_str and " - " in category_str:
            topic_filter = category_str.split(" - ", 1)[1]

        sampled_list = self.domain_sampler.sample(n=1, topic=topic_filter)
        domain_context = sampled_list[0] if sampled_list else {"id": f"fallback_{category_id}", "tier": "General Data"}

        print(f"  -> Selected Subtopic: {domain_context.get('name', 'Unknown')}")

        # Phase 1: Contextualize Scenario
        logger.info("  -> Phase 1: Contextualizing Scenario...")
        scenario = self.contextualizer.generate(domain_context)

        # Persist Phase 1 scenario to disk for inspection / debugging
        scenario_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "agpds", "scenarios"
        )
        os.makedirs(scenario_dir, exist_ok=True)
        scenario_path = os.path.join(scenario_dir, f"{generation_id}_scenario.json")
        with open(scenario_path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, indent=2, ensure_ascii=False)
        logger.info(f"  -> Scenario saved to {scenario_path}")

        # Phase 2: Sandbox Executor
        logger.info("  -> Phase 2: Generating and Executing Sandbox Script...")
        try:
            result = run_phase2(
                scenario_context=scenario,
                api_key=self.llm.api_key,
                model=self.llm.model,
                provider=self.llm.provider,
                max_loop_a_retries=5,
                max_loop_b_retries=3,
            )
        except Exception as e:
            logger.error(f"Phase 2 Execution Failed: {e}")
            raise RuntimeError(f"Sandbox executor failed to generate valid data: {e}")

        if isinstance(result, SkipResult):
            raise RuntimeError(
                f"Phase 2 exhausted all retries: {'; '.join(result.error_log)}"
            )

        df, schema_metadata, val_report = result

        if val_report.all_passed:
            logger.info("  -> Validation: all checks passed.")
        else:
            failures_str = "\n".join(f"  - {c.name}: {c.detail}" for c in val_report.failures)
            logger.warning(f"  -> Validation soft-failures (continuing):\n{failures_str}")

        logger.info("  -> Phases 0-2 Complete. Master Table and Schema Metadata ready for Phase 3.")

        return {
            "generation_id": generation_id,
            "category_id": category_id,
            "domain_context": domain_context,
            "scenario": scenario,
            "master_data_csv": df.to_csv(index=False),
            "schema_metadata": schema_metadata,
        }
