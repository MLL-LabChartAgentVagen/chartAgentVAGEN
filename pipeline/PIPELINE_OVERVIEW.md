# Pipeline Overview

This document explains the five pipeline files: what they do, how they work, and their entry points.

---

## 1. `chart_qa_pipeline.py`

**Purpose:** Integrated chart + QA generation for VLM evaluation. Reads metadata (e.g. `generated_metadata.json`), draws chart images (bar, scatter, pie), generates QA pairs via chart generators, and writes evaluation-ready data.

**Flow:**
1. Load metadata from JSON (list of category entries with `chart_entries`).
2. For each entry, for each requested chart type (bar/scatter/pie):
   - Draw chart image and save to `output_dir/imgs/{chart_type}/single/`.
   - Call chart QA generator (e.g. `BarChartGenerator`) to get questions/answers.
   - Build samples with `qa_id`, `question`, `answer`, `img_path`, `curriculum_level`, etc.
3. Aggregate all samples into one dict keyed by `qa_id`.
4. Save to `output_dir/evaluation_data.json` (same shape as `main.py` QA output).

**Entry point:** `main()` (when run as script).

**CLI:** `python chart_qa_pipeline.py [--input generated_metadata.json] [--output_dir ./data] [--chart-types bar scatter pie] [--num-questions 20] [--limit N] [--quiet]`

**Key class:** `ChartQAPipeline` — `run()` drives the full flow; `process_entry()` handles one metadata entry.

---

## 2. `evaluation_pipeline.py`

**Purpose:** Two-node pipeline that (A) sends a chart image + question to a VLM and (B) compares the VLM answer to ground truth.

**Flow:**
1. **Node A – `NodeA_VLMAnswerGenerator`:** Load image (base64), call `llm.generate_with_image(system, user, image_base64)`, clean and store VLM answer in state.
2. **Node B – `NodeB_AnswerEvaluator`:** Normalize VLM and ground-truth answers, compare (exact, numeric-with-tolerance, list, partial), set `is_correct`, `match_type`, `similarity_score`, `evaluation_details`.

**State:** `EvaluationState` (TypedDict) holds inputs (e.g. `qa_id`, `question`, `ground_truth_answer`, `img_path`) and outputs (`vlm_answer`, `is_correct`, `match_type`, etc.).

**Entry point:** No CLI. Used as a library. When run as script, it only prints a short usage message.

**Usage:**  
`pipeline = ChartQAEvaluationPipeline(llm)` then `result = pipeline.run_single(qa_entry)` or `results = pipeline.run_batch(qa_entries, progress_callback)`.  
Also: `metrics = pipeline.compute_metrics(results)` for accuracy/similarity/latency by level and QA type.

---

## 3. `evaluation_runner.py`

**Purpose:** CLI runner for the evaluation pipeline. Loads QA data, optionally filters it, runs `ChartQAEvaluationPipeline` on each item, and saves results + metrics.

**Flow:**
1. Parse CLI (data path, output path, provider/model, filters: level, qa_type, chart_type, count).
2. Resolve LLM config (provider, model, API key) from args and env (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`).
3. Build `LLMClient` from `generation_pipeline.LLMClient` (must support `generate_with_image`).
4. Instantiate `ChartQAEvaluationRunner(llm, verbose, log_file)`.
5. `runner.run(data_path, output_path, level, qa_type, chart_type, count)`:
   - Load JSON (list or dict keyed by `qa_id`).
   - Filter by level/qa_type/chart_type/count.
   - Run `ChartQAEvaluationPipeline.run_batch()` with progress callback.
   - Compute metrics; write JSON to `output_path`; optionally print summary.

**Entry point:** `main()` → `sys.exit(main())`.

**CLI:** `python evaluation_runner.py [--data ./data/evaluation_data.json] [--output ./results/evaluation_results.json] [--provider gemini-native] [--model MODEL] [--level 1] [--qa-type simple_min] [--chart-type bar] [--count 10] [--log-dir ./logs] [--quiet] [--no-summary]`

**Key class:** `ChartQAEvaluationRunner` — wraps pipeline + data load/filter/save and logging.

---

## 4. `generation_pipeline.py`

**Purpose:** LLM-driven synthetic data pipeline: from a category ID (1–30) to topic, fabricated data, chart schemas (bar/scatter/pie), and captions. No image drawing; only metadata/schema generation.

**Flow (four nodes in sequence):**
1. **Node A – Topic Agent:** Given `category_id` and optional constraints, produce `semantic_concept` and `topic_description` (e.g. “streaming subscriptions” under Media & Entertainment).
2. **Node B – Data Fabricator:** From topic, generate `MasterDataRecord` (entities, primary/secondary/tertiary values, units, statistical properties).
3. **Node C – Schema Mapper:** Map master data to chart-specific schemas (`CHART_SCHEMAS`): bar, scatter, pie (required keys, constraints).
4. **Node D – RL Captioner:** Generate ground-truth captions per chart type.

**State:** `PipelineState` (TypedDict): category_id, category_name, semantic_concept, topic_description, master_data, chart_entries, captions, generation_id, timestamp.

**Entry point:** When run as script, only prints architecture info (no full run). Used as a library.

**Usage:**  
`pipeline = ChartAgentPipeline(llm)` then `state = pipeline.run(category_id, constraints)` or `states = pipeline.run_batch(category_ids, constraints_list)`.

**Key class:** `ChartAgentPipeline` — owns the four nodes and `run` / `run_batch`.

---

## 5. `generation_runner.py`

**Purpose:** CLI runner for the generation pipeline. Parses category/count, builds LLM client, runs `ChartAgentPipeline` (via `ChartAgentPipelineRunner`), and saves results to JSON.

**Flow:**
1. Parse CLI (e.g. `--category 1`, `--categories 1,4,10`, `--count 5`, `--provider`, `--model`, `--output`, `--list-categories`).
2. Resolve provider/model/API key; create `LLMClient` from `generation_pipeline`.
3. `ChartAgentPipelineRunner(llm, verbose)` wraps `ChartAgentPipeline`.
4. `runner.run_batch(category_ids)` → for each ID, `run_single()` runs Node A → B → C → D.
5. `runner.save_results(results, output_path)` writes JSON (list of pipeline outputs).

**Entry point:** `main()`.

**CLI:** `python generation_runner.py [--category 1] [--count 5]` or `[--categories 1,4,10]` or `--list-categories`, plus `[--provider gemini] [--model MODEL] [--output generated_metadata.json] [--quiet]`

**Key class:** `ChartAgentPipelineRunner` — wraps `ChartAgentPipeline`, adds logging and `run_single`/`run_batch`/`save_results`.

---

## Summary Table

| File                     | Role                | Entry point | Output / Effect |
|--------------------------|---------------------|------------|------------------|
| `chart_qa_pipeline.py`   | Charts + QA from metadata JSON | `main()` | Chart images + `evaluation_data.json` |
| `evaluation_pipeline.py` | VLM answer + compare to GT     | Library only (script prints usage) | In-memory `EvaluationState` / metrics |
| `evaluation_runner.py`   | Run evaluation from CLI        | `main()` | `evaluation_results.json` + logs |
| `generation_pipeline.py` | Topic → data → schemas → captions | Library only (script prints info) | In-memory `PipelineState` |
| `generation_runner.py`   | Run generation from CLI        | `main()` | `generated_metadata.json` (or custom path) |

**Typical order:**  
1) `generation_runner.py` → produces metadata (e.g. `generated_metadata.json`).  
2) `chart_qa_pipeline.py` → produces chart images + `evaluation_data.json`.  
3) `evaluation_runner.py` → runs VLM on `evaluation_data.json` and writes `evaluation_results.json`.
