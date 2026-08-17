# ParseBench Review · Charts 维度

`2604.08538`，LlamaIndex。代码 [run-llama/ParseBench](https://github.com/run-llama/ParseBench)（Apache 2.0），数据 [llamaindex/ParseBench](https://huggingface.co/datasets/llamaindex/ParseBench)。本文只写 Charts。

---

## 1. 任务形态

**输入是一整页 PDF，输出是这一页的完整 markdown / HTML。**

以 `2023-05-sigma-01-english_p24`（Swiss Re sigma）为例，这一页上有：页眉、Figure 16（条形图 + 一条虚线参考线）、一段正文、Figure 17（US / Germany 两个面板，各 3 条折线、49 个月度刻度）、两行 source。标注给出 10 个抽查点，横跨两张图：

```
value='102'  labels=['2011','Direct']                      → Figure 16
value='9.1%' labels=['US','2022:06','Inflation']           → Figure 17 左面板
value='2.0%' labels=['Germany','2022:12','Long-term interest rate']
```

评测时这 10 条规则在整页输出的**所有表**里搜索。因此 chart-to-table 在这个基准里不是独立任务，而是嵌在整页解析里：图表被漏掉、被写成自然语言描述、或放进结构错误的表，结果都是 0 分。

**标注是抽查点，不是整张表。** 每页 ≤10 个点（实测 mean 8.56 / median 10 / max 11），每点一个数值 + 1–4 个标签。不要求复现整张数据表。

---

## 2. 规模

| 维度 | 指标 | 页 | 文档 | 规则 |
|---|---|---:|---:|---:|
| Tables | GTRM（GriTS + TableRecordMatch） | 503 | — | 连续指标 |
| **Charts** | **ChartDataPointMatch** | **568** | **99** | **4,864** |
| Content Faithfulness | Content Faithfulness Score | 506 | 506 | 141,322 |
| Semantic Formatting | Semantic Formatting Score | 476 | 476 | 5,997 |
| Layout（Visual Grounding） | Element Pass Rate | 500 | 321 | 16,325 |

全部为确定性规则，不使用 LLM-as-a-judge。标注为前沿 VLM 自动打标 + 人工逐点核验。

---

## 3. 规则文件

`chart.jsonl`，一行一条，4,864 行全部是 `chart_data_point`。

```json
{"pdf": "docs/chart/....p101.pdf", "category": "chart", "id": "b17e5e98d6fc2763",
 "type": "chart_data_point",
 "rule": "{\"labels\": [\"IF\", \"193 UN Member States\"], \"max_diffs\": 0, \"value\": \"0.8079\"}",
 "page": null, "expected_markdown": null, "tags": []}
```

`page` 与 `expected_markdown` 在 chart 分片恒为 null（分别供 layout 与 table 规则用）。

标签两项，**按文档级施加**（568 页页内全部一致）：

| 标签 | 官方说明 | 实测含义 | 规则数 |
|---|---|---|---:|
| `need_estimate` | 数值需要视觉估读 | 一致 | 3,569（73.4%） |
| `3d_chart` | 3D chart rendering | **定位一个值需要三个键**，非透视渲染 | 703（14.5%） |

`3d_chart` 与官方说明不符，判据见 [03 §3](03_chart_characteristics.md#3-三键索引)。

---

## 4. 榜单

| 方法 | Charts | Visual Grounding |
|---|---:|---:|
| LlamaParse Agentic | **78.11%** | **80.62%** |
| Gemini 3 Flash | 64.8% | — |
| Reducto | 57.0% | 68.7% |
| Docling | 52.8% | 66.1% |
| GPT-5 Mini | 30.1% | 6.2% |
| Qwen 3 VL | 28.2% | 55.2% |
| Haiku 4.5 | 13.8% | 6.7% |
| Azure Document Intelligence | 1.6% | 73.8% |
| Google Cloud Doc AI | 1.4% | 61.3% |
| Dots OCR 1.5 | 0.9% | 55.8% |

三点：

1. **Charts 分化最剧烈**，0.9% → 78.1%。专用 OCR / 文档 parser 普遍 < 6%：它们把图表当图片跳过，输出里根本没有表（[02 §2 第一步](02_chart_metric.md#2-四步判定走一遍这条规则)直接 0 分）。
2. **两维度的强弱互补**。纯 VLM 的 Charts（13.8–64.8%）远高于其 Visual Grounding（6.2–55.2%）；版面感知流水线反过来（Azure 1.6% / 73.8%）。**没有任何方法两项都强**，唯一例外是商业多阶段流水线 LlamaParse。
3. 全局最高 84.9%。Charts 剩 22 个点，是五维中空间最大的一维。

第 2 点是本项目的直接机会：输出单位 `(键, 值, 区域)` 一次同时供给这两维，见 [04 §3](04_pipeline_gap.md#3-与-storyline-的关系)。

---

## 5. 引用

```bibtex
@misc{zhang2026parsebench,
  title={ParseBench: A Document Parsing Benchmark for AI Agents},
  author={Boyang Zhang and Sebastián G. Acosta and Preston Carlson and Sacha Bron
          and Pierre-Loïc Doulcet and Simon Suo},
  year={2026}, eprint={2604.08538}}
```
