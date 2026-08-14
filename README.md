# Grounded Transcription — Chart Data Generation

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

对齐的基准是 ParseBench 的 Charts 与 Visual Grounding 两个维度——现状是没有任何单一方法在这两项上同时强。

## 目录

| 路径 | 内容 |
|---|---|
| [storyline/parsebench_chart/](storyline/parsebench_chart/) | 方案规格。流水线的唯一定义处 |
| [IMPL_PLAN.md](IMPL_PLAN.md) | 实现计划：文件结构、代码结构、todo checklist |
| [slides/](slides/) | 讲稿 |

## 状态

规格已定稿，实现未开始。实现进度见 [IMPL_PLAN.md](IMPL_PLAN.md) 的 checklist。

## 历史

本分支从 `py_parsebench` 切出并清空了与本方案无关的全部内容（VAGEN 时期的 chart generator、QA 生成流水线、其他研究方向的 storyline）。这些内容仍在原分支上，取回方式：

```bash
git show py_parsebench:<path>          # 单个文件
git checkout py_parsebench -- <path>   # 取回到工作区
```

另有一份 Phase 0–2 的旧实现在 `dingc_suggest` 分支，可作参考；它对应的是已废弃的 QA-generation 规格，不直接复用。
