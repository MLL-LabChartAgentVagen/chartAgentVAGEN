import json
import logging
import os
import random
from typing import Optional, Dict, Any

# Phase 0, 1, 2 AGPDS Imports
from pipeline.core.ids import (
    format_scenario_id,
    generation_id,
    parse_scenario_id,
)
from pipeline.phase_0.domain_pool import DomainSampler
from pipeline.phase_1 import ScenarioContext, ScenarioContextualizer, ScenarioRecord
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
        python pipeline/phase_0/build_domain_pool.py
    """

    def __init__(
        self,
        llm_client,
        pool_path: str = None,
        scenario_source: str = "live",
        scenario_pool_path: str = None,
        seed: int = 42,
    ):
        """
        Args:
            llm_client: LLMClient used by Phase 1 (live mode) and Phase 2 Loop A.
            pool_path: Override for phase_0/domain_pool.json.
            scenario_source: "live" (default, calls LLM per record),
                             "cached" (read from scenario_pool.jsonl; fall back
                              to live on miss), or "cached_strict" (error on miss).
            scenario_pool_path: Override for phase_1/scenario_pool.jsonl.
            seed: Pipeline seed. Drives DomainSampler, cached-scenario picking,
                  generation_id derivation, and FactTableSimulator default seed.
                  Same `(seed, scenario_id)` → identical artifacts.
        """
        self.llm = llm_client
        self.seed = seed
        self._rng = random.Random(seed)
        # Per-instance monotonic counter feeding the live-mode scenario_id
        # namespace ``live:dom_NNN:<n>``. See `_resolve_by_category_id`.
        self._live_counter = 0

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
                "  python pipeline/phase_0/build_domain_pool.py"
            )

        self.domain_sampler = DomainSampler(pool_path=pool_path, seed=seed)
        self.contextualizer = ScenarioContextualizer(llm_client)

        if scenario_source not in ("live", "cached", "cached_strict"):
            raise ValueError(
                f"Invalid scenario_source: {scenario_source!r}. "
                "Expected 'live', 'cached', or 'cached_strict'."
            )
        self.scenario_source = scenario_source
        # ``_scenario_cache`` holds (k, ScenarioContext) tuples so the
        # category-id path can pick a real cached k and emit a replayable
        # scenario_id. ``_scenario_by_id`` is the direct (domain_id, k) lookup
        # for the scenario_id path.
        self._scenario_cache: Optional[
            Dict[str, list[tuple[int, ScenarioContext]]]
        ] = None
        self._scenario_by_id: Optional[Dict[tuple, ScenarioContext]] = None
        if scenario_source in ("cached", "cached_strict"):
            self._scenario_cache, self._scenario_by_id = self._load_scenario_cache(
                scenario_pool_path,
            )

    def _new_generation_id(self, scenario_id: str) -> str:
        """Derive a deterministic ``agpds_<10-hex>`` from ``(seed, scenario_id)``.

        ``scenario_id`` is one of two namespaces:
          * Cached form ``dom_NNN/k=N`` (k is 0-indexed; parseable via
            :func:`parse_scenario_id`).
          * Live form ``live:dom_NNN:<counter>`` (not parseable; used only when
            no cached entry was selected).

        ``generation_id`` treats both as opaque strings — it just hashes them.
        """
        return generation_id(self.seed, scenario_id)

    def _load_scenario_cache(
        self, path: Optional[str],
    ) -> tuple[Dict[str, list[tuple[int, ScenarioContext]]], Dict[tuple, ScenarioContext]]:
        """Load scenario_pool.jsonl into typed in-memory indices.

        Each JSONL line is parsed via :meth:`ScenarioContext.from_dict`, which
        ignores legacy envelope fields (``category_id`` from pre-Sprint-C.2
        records, ``_validation_warnings`` from pre-Sprint-C.4 records).

        Returns:
            ``(by_domain, by_id)`` where ``by_domain`` is
            ``{domain_id: [(k, ScenarioContext), ...]}`` (preserves real k so
            the category-id path can produce a replayable scenario_id) and
            ``by_id`` is ``{(domain_id, k): ScenarioContext}`` for direct
            scenario_id lookup.
        """
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__), "phase_1", "scenario_pool.jsonl"
            )
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Scenario pool not found at: {path}\n"
                "Run the build script first:\n"
                "  python pipeline/phase_1/build_scenario_pool.py"
            )
        by_domain: Dict[str, list[tuple[int, ScenarioContext]]] = {}
        by_id: Dict[tuple, ScenarioContext] = {}
        skipped = 0
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    ctx = ScenarioContext.from_dict(rec["scenario"])
                    domain_id = rec["domain_id"]
                    k = int(rec["k"])
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    skipped += 1
                    logger.warning(
                        "Skipping malformed scenario at %s:%d (%s: %s)",
                        os.path.basename(path), lineno,
                        type(exc).__name__, exc,
                    )
                    continue
                by_domain.setdefault(domain_id, []).append((k, ctx))
                by_id[(domain_id, k)] = ctx
        if skipped:
            logger.warning(
                "Scenario cache: skipped %d malformed record(s)", skipped,
            )
        logger.info(
            "Loaded scenario cache: %d domains, %d scenarios",
            len(by_domain),
            sum(len(v) for v in by_domain.values()),
        )
        return by_domain, by_id

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

    def _pick_scenario(
        self, domain_context: Dict[str, Any],
    ) -> tuple[str, ScenarioContext]:
        """Return ``(scenario_id, scenario)`` for the given domain.

        Cached mode (``cached`` / ``cached_strict``): the seeded RNG picks one
        ``(k, scenario)`` from the per-domain cache, so ``scenario_id``
        (``dom_NNN/k=N``) points at a real cached entry and the whole run is
        replayable via ``scenario_id=...``.

        Live mode (or cached fallback on miss): a fresh scenario is generated
        via LLM; ``scenario_id`` uses the ``live:dom_NNN:<counter>`` namespace
        so it is visually distinct from cached references and is *not*
        parseable as ``(domain_id, k)`` — this is the explicit signal that
        the run cannot be replayed.
        """
        domain_id = domain_context.get("id", "unknown")
        if self._scenario_cache is not None:
            bucket = self._scenario_cache.get(domain_id, [])
            if bucket:
                idx = self._rng.randrange(len(bucket))
                k, scenario = bucket[idx]
                return format_scenario_id(domain_id, k), scenario
            if self.scenario_source == "cached_strict":
                raise KeyError(
                    f"No cached scenarios for domain {domain_id!r} "
                    f"(scenario_source={self.scenario_source!r})"
                )
            logger.warning(
                "No cached scenarios for %s; falling back to live generation",
                domain_id,
            )
        scenario = self.contextualizer.generate(domain_context)
        self._live_counter += 1
        return f"live:{domain_id}:{self._live_counter}", scenario

    def _resolve_by_category_id(
        self, category_id: int,
    ) -> tuple[str, str, Dict[str, Any], ScenarioContext]:
        """Sample a domain in the category and pick a scenario.

        Returns:
            ``(scenario_id, gen_id, domain_context, scenario)``. See
            :meth:`_pick_scenario` for the cached / live scenario_id namespaces.
        """
        logger.info("  -> Phase 0: Sampling Domain...")
        domain_context = self._sample_domain(category_id)
        print(f"  -> Selected Subtopic: {domain_context.get('name', 'Unknown')}")
        logger.info(
            "  -> Phase 1: Contextualizing Scenario (source=%s)...",
            self.scenario_source,
        )
        scenario_id, scenario = self._pick_scenario(domain_context)
        gen_id = self._new_generation_id(scenario_id)
        return scenario_id, gen_id, domain_context, scenario

    def _resolve_by_scenario_id(
        self, scenario_id: str,
    ) -> tuple[str, str, Dict[str, Any], ScenarioContext]:
        """Look up an exact cached scenario by ``scenario_id`` for replay.

        Returns:
            ``(scenario_id, gen_id, domain_context, scenario)``.

        Raises:
            ValueError: scenario_source is "live" (cached lookup is impossible).
            KeyError: (domain_id, k) not present in scenario_pool.jsonl.
        """
        if self.scenario_source == "live" or self._scenario_by_id is None:
            raise ValueError(
                f"scenario_id requires scenario_source in ('cached','cached_strict'), "
                f"got {self.scenario_source!r}"
            )
        domain_id, k = parse_scenario_id(scenario_id)
        if (domain_id, k) not in self._scenario_by_id:
            raise KeyError(
                f"scenario_id {scenario_id!r} not found in scenario_pool "
                f"(have {len(self._scenario_by_id)} records)"
            )
        scenario = self._scenario_by_id[(domain_id, k)]
        domain_context = self.domain_sampler.get_by_id(domain_id)
        gen_id = self._new_generation_id(scenario_id)
        logger.info(f"  -> Phase 0+1: scenario_id={scenario_id} (skip sampling)")
        return scenario_id, gen_id, domain_context, scenario

    def generate_artifacts(
        self, *,
        category_id: Optional[int] = None,
        scenario_id: Optional[str] = None,
        constraints: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Stage 1: Phase 0 + Phase 1 + Phase 2 Loop A only.

        Pass exactly one of ``category_id`` (random sampling in that thematic
        bucket) or ``scenario_id`` (deterministic replay of a specific cached
        record). Returns LLM-generated source_code + raw_declarations; does
        NOT run Loop B and does NOT persist CSV/metadata.
        """
        if (category_id is None) == (scenario_id is None):
            raise ValueError(
                "Provide exactly one of category_id= or scenario_id= "
                "(got both or neither)"
            )

        if scenario_id is not None:
            sid, gen_id, domain_context, scenario = self._resolve_by_scenario_id(scenario_id)
        else:
            sid, gen_id, domain_context, scenario = self._resolve_by_category_id(category_id)

        logger.info(f"[{gen_id}] Starting AGPDS Stage 1 (generate)")
        logger.info("  -> Phase 2 Loop A: Generating LLM script...")
        loop_a = run_loop_a(
            scenario_context=scenario,
            scenario_id=sid,
            max_retries=5,
            api_key=self.llm.api_key,
            model=self.llm.model,
            provider=self.llm.provider,
            seed=self.seed,
        )
        if isinstance(loop_a, SkipResult):
            raise RuntimeError(
                f"Loop A exhausted all retries: {'; '.join(loop_a.error_log)}"
            )

        _df, metadata, raw_declarations, source_code = loop_a

        return {
            "generation_id": gen_id,
            "scenario_id": sid,
            "category_id": category_id,  # None in scenario_id-mode
            "domain_context": domain_context,
            # Serialize ScenarioContext → dict at the API boundary so downstream
            # callers (agpds_generate._save_stage1_artifacts, agpds_runner._save_run_result)
            # can json.dump the result without a custom encoder. Inside the Phase 1 →
            # Phase 2 wire it stays typed; outside generate_artifacts it's plain JSON.
            "scenario": scenario.to_dict(),
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

    def run_single(
        self, *,
        category_id: Optional[int] = None,
        scenario_id: Optional[str] = None,
        constraints: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Execute one full end-to-end generation pass (Stage 1 + Stage 2).

        Pass exactly one of ``category_id`` or ``scenario_id``; see
        :meth:`generate_artifacts` for the difference between the two modes.
        """
        stage1 = self.generate_artifacts(
            category_id=category_id,
            scenario_id=scenario_id,
            constraints=constraints,
        )
        result = self.execute_artifact(
            generation_id=stage1["generation_id"],
            raw_declarations=stage1["raw_declarations"],
            category_id=stage1["category_id"],
            domain_context=stage1["domain_context"],
            scenario=stage1["scenario"],
        )
        result["scenario_id"] = stage1["scenario_id"]
        logger.info("  -> Phases 0-2 Complete. Master Table and Schema Metadata ready for Phase 3.")
        return result
