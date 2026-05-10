import json
from pipeline.phase_2.sdk.simulator import FactTableSimulator
from pipeline.phase_2.orchestration.sandbox import execute_in_sandbox

def main():
    print("=== Demo 1: Direct SDK Usage ===")
    sim = FactTableSimulator(target_rows=5, seed=42)
    sim.add_category("gender", ["Male", "Female"], [0.5, 0.5], "demographics")
    sim.add_measure("age", "gaussian", {"mu": 35, "sigma": 10})
    
    df, meta = sim.generate()
    print("1. Generated DataFrame (Shape:", df.shape, "):")
    print(df.to_string())
    print("\n2. Generated Metadata:")
    print(json.dumps(meta, indent=2))
    
    print("\n=== Demo 2: Sandbox Environment Usage ===")
    
    sandbox_code = """
def build_fact_table(seed=99):
    sim = FactTableSimulator(target_rows=3, seed=seed)
    sim.add_category("status", ["Active", "Inactive"], [0.8, 0.2], "accounts")
    return sim.generate()
"""
    result = execute_in_sandbox(sandbox_code)
    print("3. Sandbox Success:", result.success)
    if result.success:
        print("Sandbox Generated Shape:", result.dataframe.shape)
        print("Sandbox Output:\n", result.dataframe.to_string())
    else:
        print("Sandbox failed:", result.exception)

if __name__ == "__main__":
    main()
