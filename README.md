# 带位置的图表转录 — 数据生成

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription（带位置的转录）**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

所有 ground truth 在渲染时直接记下来，不靠估计，也不靠标注已有的图。

## 目录

| 路径 | 内容 |
|---|---|
| [storyline/parsebench_chart/](storyline/parsebench_chart/) | 方案规格。流水线的唯一定义处，五个阶段文档共用一份贯穿示例 |
| [storyline/parsebench_chart/chart_types.md](storyline/parsebench_chart/chart_types.md) | 能画哪些图、每种图要满足什么条件才能画 |
| [IMPL_PLAN.md](IMPL_PLAN.md) | 实现计划：系统骨架、目录结构、数据接口、todo checklist |
| [src/llmkit/](src/llmkit/) | 与本项目无关的 LLM 调用层：调用 · 结构化输出 · 缓存 · 去重 · 批量。可单独复用 |
| [slides/](slides/) | 讲稿 |

## 流水线

五个阶段，**整条流水线只有一次 LLM 调用**：01 一次写出场景、数据生成脚本与绑到列上的分析意图，此后构造、推导、采样、拒绝、组版、渲染、记录、导出全部是规则。

```
01 数据 [LLM×1] → 02 选图 → 03 渲染 → 04 记录 → 05 输出
```

02 的三类图三种产出方式：意图图从绑定**构造**，多面板图从锚点**推导**，轮转图按族**采样加拒绝**——只有最后一路需要随机数。多样性由 `(键集合, 图元形状)` 判据管，不由数量管。

## 对齐的基准

主目标是 ParseBench 的 Charts 与 Visual Grounding 两个维度——现状是没有任何单一方法在这两项上同时强。此外覆盖 ChartREG++、ChartAB、LongChart VQA 的定位与指代任务，并要求在 ChartQA、CharXiv、ChartQAPro 上不退化。图表类型覆盖 6 族 13 型的常见形态，不局限于任何单一基准收录的那几种。

## 状态

规格已定稿。实现进行中，进度见 [IMPL_PLAN.md](IMPL_PLAN.md) 的 checklist：
骨架与六份数据接口、图表条件表、公共几何与像素反算、03 的 bar 边画边记已落地。

```bash
pip install -r requirements.txt
python -m pytest                                   # 单元测试
python tools/make_samples.py                       # 重生成 tests/samples/ 的接口样例

PYTHONPATH=src python -m chartgen.cli render \
    tests/samples/figure_spec.json --style tests/samples/style_vector.json -o out/demo
python tools/overlay.py out/demo/f01.json          # 把记录里的框叠回图像目视检查
```

## 历史

本分支从 `py_parsebench` 切出，清空了与本方案无关的全部内容（VAGEN 时期的 chart generator、问答生成流水线、其他研究方向的 storyline）。这些内容仍在原分支上：

```bash
git show py_parsebench:<path>          # 看单个文件
git checkout py_parsebench -- <path>   # 取回到工作区
```

另有一份 Phase 0–2 的旧实现在 `dingc_suggest` 分支，可作参考；它对应的是已废弃的问答生成规格，不直接复用。
