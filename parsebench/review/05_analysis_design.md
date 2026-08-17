# 样例分析怎么做：单 VLM，不做 agent

设计文档，尚未实现。回答三个问题：要什么数、用什么系统取、代码放哪。

---

## 1. 要回答的三个问题

| 问题 | 谁在等这个数 |
|---|---|
| bar / line / pie / compound 的实际配比，以及面板数、稠密度、是否写数值的分布 | [04 G4](04_pipeline_gap.md#g4--轮转图的族采样加权重向量) 的权重向量、[G5](04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量) 的稠密度区间 |
| 哪些页难，难在哪 | [04](04_pipeline_gap.md) 各项的优先级校准 |
| 失败落在哪一类（无表 / 值不准 / 标签没关联 / 量纲错 / 漏图 / 串系列） | [data/failure_cases/](../data/failure_cases/) 的六类归因 |

---

## 2. 结论：不需要 agentic system

**用单个 VLM，一页一次调用，不接 OCR、不接工具、不做多轮。** 四条理由：

1. **要的字段全是页面的可见属性。** 图表类型、面板数、有没有数值标签、图例位置——VLM 直接看得出来。OCR 解决的是文字转录，而我们不缺文字，缺的是结构分类。
2. **最难的那部分已经有真值。** `chart.jsonl` 给了 4,864 个 `(值, 标签)`。我们不需要模型去抽取数值再想办法验证它——**验证器是官方规则代码，不是模型**。这一步删掉了 agent 存在的主要理由。
3. **确定性。** llmkit 的磁盘缓存让 `(prompt, image, model) → 输出` 可复现；多轮工具调用的缓存键不稳定，同一份分析跑两次会得到不同的数。
4. **规模不构成理由。** 568 页 × 2 次调用，见 [§5](#5-成本)。

---

## 3. 两条通路，各一次调用

两个任务分开调用，**不合并**：合并会让 parse 的输出预算被 profile 的字段挤占，且 parse 必须复刻基准的真实任务形态才有意义。

```
                  ┌─ A · parse ────────────────────────────────────────┐
                  │  prompt 与 ParseBench 的任务一致：把这一页转成       │
 page.png ───────►│  markdown。不提示图表位置、不提示要输出表。          │
                  │  输出：整页 markdown                               │
                  └──────────────────┬─────────────────────────────────┘
                                     ▼
                  官方 ChartDataPointRule（确定性程序，非模型）
                                     ▼
                  每页通过率 + 每条规则的失败原因串
                                     │
                  ┌─ B · profile ────┴─────────────────────────────────┐
 page.png ───────►│  结构化输出：图表数与类型、面板数与共享方式、        │
                  │  是否写数值与标注位置、系列数与类目数、刻度标签      │
                  │  形态、风格特征、这页难在哪                        │
                  └────────────────────────────────────────────────────┘
                                     ▼
              A × B 交叉 → 「哪类结构上失败率高」→ 04 的优先级
```

A 的副产品：**我们自己在 Charts 维度上的基线数字**，与 [01 §4](01_benchmark.md#4-榜单) 的榜单同口径可比。

失败归因不需要模型判断——`ChartDataPointRule.run()` 返回的 `(passed, reason, score)` 里，`reason` 已经区分了 `No tables found in content`、`Value not found in any table`、`Value found but labels not associated`，正好对应前三类。

---

## 4. 代码放哪

**分析代码用 `src/llmkit/`，不另起一套模型调用层。** llmkit 是共享包，其定位就是「任何需要调模型的地方」，未来的多模型评测也走它。

### llmkit 需要一处扩展：图像通路

当前 `Message.content` 是 `str`（[types.py:13](../../src/llmkit/types.py#L13)），`build_request` 把它直接放进 `{"role", "content"}`（[providers.py:82](../../src/llmkit/providers.py#L82)）。**没有图像通路，VLM 调用现在发不出去。**

最小改动，三个文件约 30 行，**改在 llmkit 里，不在 parsebench 里包一层**：

| 文件 | 改动 |
|---|---|
| `types.py` | 加 `Image(media_type, data)` 冻结数据类；`Message` 加 `images: tuple[Image, ...] = ()`。默认空元组，现有调用点全部不动 |
| `providers.py` | `build_request` 在 `m.images` 非空时把 content 写成 block 列表（image 块在前、text 块在后） |
| `client.py` | `complete` / `json` 透传 `images`；`_cache_key` 收进每张图的摘要而非 base64 本身，缓存键才不会膨胀 |

`json()` 的 schema 重试通路、`map()` 的并发批处理、`ResponseCache` 全部照常工作，B 通路直接用 `llm.json(..., images=[page])`。

### parsebench 侧只加两个脚本

| 脚本 | 做什么 |
|---|---|
| `tools/probe_pages.py` | 跑 A、B 两条通路，结果落 `data/stats/` |
| `tools/score_pages.py` | 用官方 `ChartDataPointRule` 给 A 的输出打分，产出每页通过率与失败原因 |

`score_pages.py` 需要 `parse_bench` 包。它是 Apache 2.0，按可选依赖装（`pip install "parse-bench @ git+https://github.com/run-llama/ParseBench"`），不进 `requirements.txt` 主依赖。

---

## 5. 成本

568 页 × 2 次调用。150 dpi 的整页在服务端被缩到长边 1568 px，约 2.5k 输入 token；A 的输出约 1.5k、B 约 0.4k。合计约 **2.8M 输入 + 1.1M 输出 token**。磁盘缓存命中后重跑为零。

---

## 6. 什么时候才需要工具

一个真实的边界：长边 1568 px 的上限对稠密页面是硬约束——`2023-05-sigma-01-english_p24` 的 Fig 17 是单面板 49 个时间刻度 × 3 条折线，缩到 1568 px 后相邻刻度间距不足 10 px。裁剪放大在这里会有帮助，CharTool（`2604.02794`）用图像裁剪 + 代码计算工具在 CharXiv-R 上报告 +8.0%。

但这属于**推理系统**，不属于分析系统：

- 分析阶段要的是「稠密页面的失败率是不是显著更高」。**如果是，这本身就是结论**，直接支撑 [04 G5](04_pipeline_gap.md#g5--稠密度上限抬高把稠密度变成一个可控自变量)；给分析器加裁剪工具反而会把这个信号抹掉。
- 刷榜阶段要的是把分拉高，那时再评估裁剪工具、多轮验证这些机制。

两件事分开，不要在分析阶段就把系统做成 agent。
