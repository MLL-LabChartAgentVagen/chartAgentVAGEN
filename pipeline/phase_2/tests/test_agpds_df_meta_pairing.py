import io
import pandas as pd
import pipeline.agpds_pipeline as ag
from pipeline.agpds_pipeline import AGPDSPipeline
from pipeline.phase_2.sandbox_executor import SandboxExecutor
# 固定脚本：同一schema，只变seed
STABLE_SCRIPT = """
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=120, seed=seed)
    sim.add_category("region", ["N","S","E"], [0.4,0.3,0.3], group="geo")
    sim.add_category("platform", ["web","app"], [0.5,0.5], group="channel")
    sim.add_measure("arpu", "gaussian", {"mu": 20, "sigma": 3})
    sim.add_measure("engagement_score", "gaussian", {"mu": 70, "sigma": 8})
    sim.declare_orthogonal("geo", "channel", rationale="independent")
    sim.add_correlation("arpu", "engagement_score", target_r=0.4)
    return sim.generate()
"""
def fake_run_with_retries(llm_client, scenario_context, system_prompt=None, max_retries=3, seed=42, timeout_seconds=30):
    ex = SandboxExecutor(timeout_seconds=timeout_seconds)
    res = ex.execute(STABLE_SCRIPT, seed=seed)
    # run_with_retries 的返回需要带 script，供 agpds_pipeline 后续 replay
    res.script = STABLE_SCRIPT
    return res
# monkeypatch agpds_pipeline 内部引用
ag.run_with_retries = fake_run_with_retries
# 构建 pipeline，并替换 phase0/phase1 依赖为本地stub
pipe = AGPDSPipeline(llm_client=object())
pipe.domain_sampler.sample = lambda n=1, topic=None: [{"id":"stub","name":"stub-subtopic","topic":"stub-topic"}]
pipe.contextualizer.generate = lambda domain: {
    "title": "stub",
    "data_context": "stub",
    "key_entities": ["region","platform"],
    "key_metrics": ["arpu","engagement_score"],
    "temporal_granularity": "none",
    "target_rows": 120
}
out = pipe.run_single(category_id=1)
df = pd.read_csv(io.StringIO(out["master_data_csv"]))
meta = out["schema_metadata"]
declared_cols = [c.get("name") for c in meta.get("columns", []) if c.get("name")]
missing = [c for c in declared_cols if c not in df.columns]
print("rows(df)=", len(df), " meta.total_rows=", meta.get("total_rows"))
print("missing_declared_cols=", missing)
assert len(df) == meta.get("total_rows"), "row_count mismatch: df vs meta.total_rows"
assert not missing, f"schema columns missing in df: {missing}"
print("PASS: df/meta 配对一致（无错配）")