# 前沿模型失败案例

放前沿模型在 ParseBench chart 页面上的失败样本。目的只有一个：**从失败形态倒推我们的数据生成流水线缺哪类样本**，结论写回 [../../review/04_pipeline_gap.md](../../review/04_pipeline_gap.md)。

## 放法

一个案例一个子目录，目录名 `<模型>__<页面stem>`：

```
failure_cases/
  gemini3flash__She-figures_p115/
    page.png          必需
    output.md         必需，模型输出的整页 markdown / HTML 原文
    rules.json        必需，该页的抽查规则
    verdict.json      可选，逐条规则的通过与否及失败原因
    notes.md          可选，人工判断
```

`output.md` 必须是**原样输出**，不要截取图表部分。[02_chart_metric.md §2](../../review/02_chart_metric.md#2-四步判定走一遍这条规则) 的判定依赖表格前面的上下文与整页里的所有表，截取会改变判定结果。

## 需要区分的失败形态

分析时先归到下面某一类，不同类指向不同的流水线改动：

| 形态 | 指向 |
|---|---|
| 输出里根本没有表，图表被写成自然语言描述或被跳过 | 输出格式，不是图表理解能力 |
| 有表，但值不在容差内 | 估读精度。对照该点的 `need_estimate` 与 `relative_tolerance` |
| 值对，但标签没关联上（表结构错，或第三个键丢了） | 表结构。对照 [04_pipeline_gap.md P2](../../review/04_pipeline_gap.md#p2--面板维进入键) |
| 值对标签对，但量纲错（写了底层原值而非图上刻度） | 见 [02_chart_metric.md §4 结论 3](../../review/02_chart_metric.md#4-三条对输出格式的直接结论) |
| 同页多图时只转了其中一张 | 版面，对照 [04_pipeline_gap.md 待核实](../../review/04_pipeline_gap.md#4-待核实) |
| 系列张冠李戴（值取自相邻系列） | 图例绑定 |

前四类需要逐条跑一遍官方判定才能区分，不能靠看输出判断。判定代码在 `run-llama/ParseBench` 的 `evaluation/metrics/parse/rules_chart.py`。
