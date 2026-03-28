import numpy as np
from pipeline.agpds_pipeline import _build_meta_aware_script
from pipeline.phase_2.sandbox_executor import SandboxExecutor

BASE = """
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=4000, seed=seed)
    sim.add_category("g", ["A","B"], [0.5,0.5], group="grp")
    sim.add_measure("x", "gaussian", {"mu": 0, "sigma": 1})
    sim.add_measure("y", "gaussian", {"mu": 0, "sigma": 1})
    sim.add_correlation("x", "y", target_r=0.1)
    return sim.generate()
"""

ex = SandboxExecutor(timeout_seconds=30)
meta_lo = {"correlations": [{"col_a": "x", "col_b": "y", "target_r": 0.1}]}
meta_hi = {"correlations": [{"col_a": "x", "col_b": "y", "target_r": 0.8}]}

r1 = ex.execute(_build_meta_aware_script(BASE, meta_lo), seed=42)
r2 = ex.execute(_build_meta_aware_script(BASE, meta_hi), seed=42)

if not r1.success:
    print(r1.error_type, r1.error_message, r1.traceback_str)
if not r2.success:
    print(r2.error_type, r2.error_message, r2.traceback_str)
assert r1.success and r2.success
corr1 = float(r1.df["x"].corr(r1.df["y"]))
corr2 = float(r2.df["x"].corr(r2.df["y"]))

assert abs(corr1 - 0.1) < 0.2, (corr1, corr2)
assert abs(corr2 - 0.8) < 0.2, (corr1, corr2)
assert abs(corr2 - corr1) > 0.3, (corr1, corr2)

print("PASS", {"corr_lo": round(corr1, 3), "corr_hi": round(corr2, 3)})