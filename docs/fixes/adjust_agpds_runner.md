# Plan: Fix agpds_runner.py save_results() for new phase_2 output format

## Context

`agpds_pipeline.py` was already rewritten to use `run_phase2()`. Its `run_single()` now returns a plain dict with keys: `generation_id`, `category_id`, `domain_context`, `scenario`, `master_data_csv` (CSV string), `schema_metadata` (plain Python dict).

`agpds_runner.py`'s `save_results()` correctly writes the CSV and schema JSON files, but then calls `json.dump(result, f, indent=2)` to write per-generation chart JSONs — passing the **entire result dict including the raw `master_data_csv` text and full `schema_metadata` dict**. This creates bloated chart JSON files that redundantly inline data already saved as separate files.

The fix: strip the raw data blobs from the serialized chart record, keeping only path references for already-saved artifacts.

**Note**: All other runner logic (imports, CLI args, model resolution, `LLMClient` construction, `run_batch`) is compatible with the new phase_2 as-is. The core `LLMClient` has the required `.api_key`, `.model`, `.provider` attributes. `schema_metadata` is a plain dict so JSON serialization works. Only `save_results()` needs updating.

---

## Change: `save_results()` in [pipeline/agpds_runner.py](pipeline/agpds_runner.py)

**Problem** (lines 88–91): `json.dump(result, f, indent=2)` serializes the full result dict including:
- `master_data_csv`: raw multi-row CSV text (already written as `{gen_id}.csv`)
- `schema_metadata`: full nested schema dict (already written as `{gen_id}_metadata.json`)

This creates large, redundant chart JSON files that duplicate already-saved files.

**Fix**: Build a lean `chart_record` before serializing. Strip both raw blobs from it, keeping only the path references already added to `result`.

### Before (lines 86–93)
```python
# Save per-generation chart JSON (same basename as master_tables)
result["charts_path"] = os.path.join("charts", f"{gen_id}.json")
charts_path = os.path.join(charts_dir, f"{gen_id}.json")
with open(charts_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
charts_count += 1

json_results.append(result)
```

### After
```python
# Save per-generation chart JSON — strip raw blobs, keep path references
chart_record = {
    k: v for k, v in result.items()
    if k not in ("master_data_csv", "schema_metadata")
}
chart_record["charts_path"] = os.path.join("charts", f"{gen_id}.json")
result["charts_path"] = chart_record["charts_path"]
charts_path = os.path.join(charts_dir, f"{gen_id}.json")
with open(charts_path, 'w', encoding='utf-8') as f:
    json.dump(chart_record, f, indent=2)
charts_count += 1

json_results.append(chart_record)
```

The final `charts.json` bundle (line 96–98) collects `chart_record` dicts — lean manifests with path references to all artifacts. The per-generation chart JSON and bundle both contain:
```json
{
    "generation_id": "agpds_...",
    "category_id": 1,
    "domain_context": {...},
    "scenario": {...},
    "master_data_csv_path": "master_tables/agpds_....csv",
    "schema_metadata_path": "schemas/agpds_..._metadata.json",
    "charts_path": "charts/agpds_....json"
}
```

---

## Critical File

| File | Change |
|------|--------|
| [pipeline/agpds_runner.py](pipeline/agpds_runner.py) | `save_results()` lines 86–93: build lean `chart_record` before JSON serialization |

---

## Verification

```bash
# Smoke-test imports still resolve (conda env 'chart')
conda run -n chart python -c "from pipeline.agpds_runner import AGPDSRunner; print('OK')"

# After a real run, verify chart JSON does NOT contain raw CSV text:
# python -m pipeline.agpds_runner --category 1 --count 1 --provider gemini
# python -c "import json; r=json.load(open('output/agpds/charts.json')); assert 'master_data_csv' not in r[0]; print('OK')"
```
