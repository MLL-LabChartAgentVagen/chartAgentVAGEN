import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

# Phase 0, 1, 2 AGPDS Imports
from pipeline.phase_0.domain_pool import DomainSampler
from pipeline.phase_1.scenario_contextualizer import ScenarioContextualizer
from pipeline.phase_2.pipeline import (
    run_phase2,
    run_loop_a,
    run_loop_b_from_declarations,
)
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

    def _new_generation_id(self) -> str:
        start_time = datetime.now()
        return (
            f"agpds_{start_time.strftime('%Y%m%d_%H%M%S')}_"
            f"{hashlib.md5(str(start_time).encode()).hexdigest()[:6]}"
        )

    def _sample_domain(self, category_id: int) -> Dict[str, Any]:
        from pipeline.core.utils import get_category_by_id
        category_str = get_category_by_id(category_id)
        topic_filter = None
        if category_str and " - " in category_str:
            topic_filter = category_str.split(" - ", 1)[1]

        sampled_list = self.domain_sampler.sample(n=1, topic=topic_filter)
        return sampled_list[0] if sampled_list else {
            "id": f"fallback_{category_id}",
            "tier": "General Data",
        }

    def _save_scenario(self, generation_id: str, scenario: Dict[str, Any]) -> str:
        scenario_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "agpds", "scenarios"
        )
        os.makedirs(scenario_dir, exist_ok=True)
        scenario_path = os.path.join(scenario_dir, f"{generation_id}_scenario.json")
        with open(scenario_path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, indent=2, ensure_ascii=False)
        logger.info(f"  -> Scenario saved to {scenario_path}")
        return scenario_path

    def generate_artifacts(
        self, category_id: int, constraints: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Stage 1: Phase 0 + Phase 1 + Phase 2 Loop A only.

        Produces the LLM-generated script and raw_declarations, but does NOT
        run Loop B (validation/autofix) and does NOT persist CSV/metadata.
        Intended for agpds_generate.py which writes scripts/ and declarations/
        to disk so agpds_execute.py can replay them later.
        """
        generation_id = self._new_generation_id()
        logger.info(f"[{generation_id}] Starting AGPDS Stage 1 (generate)")

        logger.info("  -> Phase 0: Sampling Domain...")
        domain_context = self._sample_domain(category_id)
        print(f"  -> Selected Subtopic: {domain_context.get('name', 'Unknown')}")

        logger.info("  -> Phase 1: Contextualizing Scenario...")
        scenario = self.contextualizer.generate(domain_context)
        self._save_scenario(generation_id, scenario)

        logger.info("  -> Phase 2 Loop A: Generating LLM script...")
        loop_a = run_loop_a(
            scenario_context=scenario,
            max_retries=5,
            api_key=self.llm.api_key,
            model=self.llm.model,
            provider=self.llm.provider,
        )
        if isinstance(loop_a, SkipResult):
            raise RuntimeError(
                f"Loop A exhausted all retries: {'; '.join(loop_a.error_log)}"
            )

        _df, metadata, raw_declarations, source_code = loop_a

        return {
            "generation_id": generation_id,
            "category_id": category_id,
            "domain_context": domain_context,
            "scenario": scenario,
            "source_code": source_code,
            "raw_declarations": raw_declarations,
            "schema_metadata": metadata,
        }

    def execute_artifact(
        self,
        generation_id: str,
        raw_declarations: Dict[str, Any],
        category_id: Optional[int] = None,
        domain_context: Optional[Dict[str, Any]] = None,
        scenario: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Stage 2: Phase 2 Loop B only — deterministic execution from declarations.

        No LLM calls. Runs generate → validate → auto-fix and returns the
        runner-style result dict (master_data_csv + schema_metadata).
        """
        logger.info(f"[{generation_id}] Starting AGPDS Stage 2 (execute)")

        result = run_loop_b_from_declarations(
            raw_declarations,
            max_retries=3,
        )
        if isinstance(result, SkipResult):
            raise RuntimeError(
                f"Loop B exhausted all retries: {'; '.join(result.error_log)}"
            )

        df, schema_metadata, val_report = result

        if val_report.all_passed:
            logger.info("  -> Validation: all checks passed.")
        else:
            failures_str = "\n".join(
                f"  - {c.name}: {c.detail}" for c in val_report.failures
            )
            logger.warning(f"  -> Validation soft-failures (continuing):\n{failures_str}")

        return {
            "generation_id": generation_id,
            "category_id": category_id,
            "domain_context": domain_context or {},
            "scenario": scenario or {},
            "master_data_csv": df.to_csv(index=False),
            "schema_metadata": schema_metadata,
        }

    def run_single(self, category_id: int, constraints: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute one full end-to-end generation pass (Stage 1 + Stage 2)."""
        stage1 = self.generate_artifacts(category_id, constraints)
        result = self.execute_artifact(
            generation_id=stage1["generation_id"],
            raw_declarations=stage1["raw_declarations"],
            category_id=stage1["category_id"],
            domain_context=stage1["domain_context"],
            scenario=stage1["scenario"],
        )
        logger.info("  -> Phases 0-2 Complete. Master Table and Schema Metadata ready for Phase 3.")
        return result
