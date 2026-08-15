# 带位置的图表转录 — 数据生成

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription（带位置的转录）**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

所有 ground truth 在渲染时直接记下来，不靠估计，也不靠标注已有的图。

## 目录

| 路径 | 内容 |
|---|---|
| [storyline/parsebench_chart/](storyline/parsebench_chart/) | 方案规格。流水线的唯一定义处，六个阶段文档共用一份贯穿示例 |
| [IMPL_PLAN.md](IMPL_PLAN.md) | 实现计划：系统骨架、目录结构、数据接口、todo checklist |
| [slides/](slides/) | 讲稿 |

## 对齐的基准

主目标是 ParseBench 的 Charts 与 Visual Grounding 两个维度——现状是没有任何单一方法在这两项上同时强。此外覆盖 ChartREG++、ChartAB、LongChart VQA 的定位与指代任务，并要求在 ChartQA、CharXiv、ChartQAPro 上不退化。图表类型覆盖 6 族 18 型，不局限于任何单一基准收录的那几种。

## 状态

规格已定稿，实现未开始。进度见 [IMPL_PLAN.md](IMPL_PLAN.md) 的 checklist。

## 历史

本分支从 `py_parsebench` 切出，清空了与本方案无关的全部内容（VAGEN 时期的 chart generator、问答生成流水线、其他研究方向的 storyline）。这些内容仍在原分支上：

```bash
git show py_parsebench:<path>          # 看单个文件
git checkout py_parsebench -- <path>   # 取回到工作区
```

另有一份 Phase 0–2 的旧实现在 `dingc_suggest` 分支，可作参考；它对应的是已废弃的问答生成规格，不直接复用。
