import json
import logging
import os
import textwrap
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

from pipeline.core.master_table import MasterTable

# Phase 0, 1, 2 AGPDS Imports
from pipeline.phase_0.domain_pool import DomainSampler
from pipeline.phase_1.scenario_contextualizer import ScenarioContextualizer
from pipeline.phase_2.sandbox_executor import SandboxExecutor, run_with_retries, PHASE2_SYSTEM_PROMPT
from pipeline.phase_2.validators import generate_with_validation

logger = logging.getLogger(__name__)


def _build_meta_aware_script(base_script: str, meta_overrides: dict) -> str:
    """Wrap a generated script so FactTableSimulator consumes meta overrides.

    This keeps schema stable (same base script) while making auto-fix effective:
    retries can alter generation by overriding declaration-time parameters.
    """
    payload = repr(meta_overrides or {})  # Use Python literal (None/True/False), not JSON (null/true/false), for exec().
    wrapper = textwrap.dedent(
        f"""\
        _META_OVERRIDES = {payload}
        __name__ = "__sandbox__"
        _BaseFactTableSimulator = FactTableSimulator

        class _MetaAwareFactTableSimulator(_BaseFactTableSimulator):
            def __init__(self, *args, **kwargs):
                _BaseFactTableSimulator.__init__(self, *args, **kwargs)
                self._meta_overrides = _META_OVERRIDES if isinstance(_META_OVERRIDES, dict) else {{}}

            def add_measure(self, name, dist, params, scale=None):
                cols = self._meta_overrides.get("columns", [])
                for c in cols:
                    if c.get("name") == name:
                        declared = c.get("declared_params")
                        if isinstance(declared, dict):
                            params = dict(declared)
                        break
                return _BaseFactTableSimulator.add_measure(self, name, dist, params, scale=scale)

            def add_correlation(self, col_a, col_b, target_r):
                for corr in self._meta_overrides.get("correlations", []):
                    a = corr.get("col_a")
                    b = corr.get("col_b")
                    if (a == col_a and b == col_b) or (a == col_b and b == col_a):
                        if "target_r" in corr:
                            target_r = corr.get("target_r", target_r)
                        break
                return _BaseFactTableSimulator.add_correlation(self, col_a, col_b, target_r)

            def inject_pattern(self, pattern_type, target, col, params):
                params = dict(params) if isinstance(params, dict) else {{}}
                for p in self._meta_overrides.get("patterns", []):
                    if p.get("type") != pattern_type:
                        continue
                    if p.get("target") != target:
                        continue
                    if p.get("col") != col:
                        continue
                    for k, v in p.items():
                        if k in ("type", "target", "col"):
                            continue
                        if v is not None:
                            params[k] = v
                    break
                return _BaseFactTableSimulator.inject_pattern(self, pattern_type, target, col, params)

        FactTableSimulator = _MetaAwareFactTableSimulator
        """
    )
    return f"{wrapper}\n{base_script}"


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
        
        # print(f"  -> Selected Topic: {domain_context.get('topic', topic_filter or 'Unknown')}")
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
        phase2_user_prompt = json.dumps(scenario, indent=2)
        try:
            # First successful script/materialization gives the baseline meta
            # used by generate_with_validation as external, mutable target.
            initial_result = run_with_retries(
                self.llm, phase2_user_prompt, max_retries=5, seed=42
            )
            if not initial_result.success:
                raise RuntimeError(f"Sandbox failed: {initial_result.error_message}")
            schema_metadata = initial_result.schema_metadata
            if schema_metadata is None:
                raise RuntimeError("Sandbox returned empty schema_metadata")

            initial_df = initial_result.df
            if initial_df is None:
                raise RuntimeError("Sandbox returned empty DataFrame")
            base_script = initial_result.script
            if not base_script:
                raise RuntimeError("Sandbox returned empty script")

            first_attempt_used = {"done": False}
            executor = SandboxExecutor(timeout_seconds=30)

            def _build_with_seed(seed: int, meta: dict):
                # Reuse the first successful materialization for attempt 0;
                # later retries replay the same successful script with a new seed.
                # This keeps df/meta schema aligned and avoids script drift.
                if not first_attempt_used["done"] and seed == 42:
                    first_attempt_used["done"] = True
                    return initial_df
                script_for_retry = _build_meta_aware_script(base_script, meta)
                replay_result = executor.execute(script_for_retry, seed=seed)
                if not replay_result.success or replay_result.df is None:
                    raise RuntimeError(
                        f"Sandbox retry failed: {replay_result.error_message}"
                    )
                return replay_result.df

            logger.info("  -> Phase 2: Running Three-Layer Validation + Auto-Fix...")
            df, val_report, schema_metadata = generate_with_validation(
                build_fn=_build_with_seed,
                meta=schema_metadata,
                max_retries=3,
                base_seed=42,
            )
        except Exception as e:
            logger.error(f"Phase 2 Execution Failed: {e}")
            raise RuntimeError(f"Sandbox executor failed to generate valid data: {e}")

        if val_report.all_passed:
            logger.info("  -> Validation: all checks passed.")
        else:
            logger.warning(
                f"  -> Validation soft-failures (continuing):\n{val_report.summary()}"
            )
            
        # Wrap the DataFrame + Schema Metadata for downstream Phase 3
        mt = MasterTable(df, metadata=schema_metadata)
        
        logger.info("  -> Phases 0-2 Complete. Master Table and Schema Metadata ready for Phase 3.")
        
        return {
            "generation_id": generation_id,
            "category_id": category_id,
            "domain_context": domain_context,
            "scenario": scenario,
            "master_data_csv": df.to_csv(index=False),
            "schema_metadata": schema_metadata,
        }
