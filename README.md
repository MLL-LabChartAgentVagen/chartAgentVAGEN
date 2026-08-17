# 带位置的图表转录 — 数据生成

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription（带位置的转录）**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

所有 ground truth 在渲染时直接记下来，不靠估计，也不靠标注已有的图。

## 目录

| 路径 | 内容 |
|---|---|
| [storyline/parsebench_chart/](storyline/parsebench_chart/) | 方案规格。流水线的唯一定义处，五个阶段文档共用一份贯穿示例 |
| [storyline/parsebench_chart/chart_types.md](storyline/parsebench_chart/chart_types.md) | 能画哪些图、每种图要满足什么条件才能画 |
| [IMPL_PLAN.md](IMPL_PLAN.md) | 实现计划：系统骨架、目录结构、数据接口、todo checklist |
| [parsebench/](parsebench/) | ParseBench 对齐：Charts 维度的 review、评测指标拆解、chart 分片数据与统计、待改清单 |
| [src/chartgen/](src/chartgen/) | 流水线本体 |
| [src/llmkit/](src/llmkit/) | 与本项目无关的 LLM 调用层：调用 · 结构化输出 · 缓存 · 去重 · 批量。可单独复用 |
| [tools/](tools/) | 辅助脚本：重生成接口样例、把框叠回图像 |
| [data/domains/](data/domains/) | 领域池（进版本库，整个项目只建一次） |
| `data/generated/` | 运行产物（不进版本库） |
| [slides/](slides/) | 讲稿 |

**代码一律用英文**（注释、docstring、异常文本、提示词）。中文只出现在 `storyline/`、`README.md`、`IMPL_PLAN.md` 这几份文档里。

## 流水线

五个阶段，**整条流水线只有一次 LLM 调用**：01 一次写出场景、数据生成脚本与绑到列上的分析意图，此后构造、推导、采样、拒绝、组版、渲染、记录、导出全部是规则。

```
01 数据 [LLM×1] → 02 选图 → 03 渲染 → 04 记录 → 05 输出
```

02 的三类图三种产出方式：意图图从绑定**构造**，多面板图从锚点**推导**，轮转图按族**采样加拒绝**——只有最后一路需要随机数。多样性由 `(键集合, 图元形状)` 判据管，不由数量管。

## 怎么跑

```bash
pip install -r requirements.txt
export PYTHONPATH=src          # 下面所有命令都要
```

| 想做什么 | 命令 |
|---|---|
| 跑全部测试 | `python -m pytest` |
| 跑真调模型的那个测试 | `CHARTGEN_LLM=1 python -m pytest tests/e2e -s` |
| 建领域池（**调模型，整个项目一次**） | `python -m chartgen.cli pool` |
| 只跑 01，**不调模型**（拿手写的输出走完规则那一半） | `python -m chartgen.cli data --payload tests/samples/er_scenario.json --scenario er_wait` |
| 只跑 01，**调一次模型**（临时指定领域） | `python -m chartgen.cli data --domain "ICU bed turnover" --tier medium` |
| 只跑 01，从领域池抽 | `python -m chartgen.cli data --scenario s000` |
| 重画一份已有 schema 的图 | `python -m chartgen.cli inspect data/generated/s000/schema.json` |
| 只跑 03，从一份 FigureSpec 渲染 | `python -m chartgen.cli render tests/samples/figure_spec.json -o data/generated/demo` |
| 把记录里的框叠回图像目视检查 | `python tools/overlay.py data/generated/demo/f01.json` |
| 跑整条流水线（02 起未实现，跑到 01 之后停） | `python -m chartgen.cli run --scenarios 3` |
| 重生成接口样例（改了接口之后） | `python tools/make_samples.py` |

改配置：`--config 别的.yaml` 换一份，`--set data.target_rows=1200` 覆盖单项。默认值与每一项的含义在 [configs/default.yaml](configs/default.yaml)。

**每次产出 schema 都会自动写一份 `schema.md`**，与 `schema.json`、`facts.parquet` 放在一起，不用另跑命令；上表的 `inspect` 只用于补画早先生成的 schema。`.md` 里是 Mermaid 图（层级树 + 数值列依赖 + 意图指向），VSCode 与 GitHub 直接渲染，终端同时打一棵树：

```
entity
  |- hospital (3)
    `- department (4)
triage
  `- severity (3)
measures
  |- wait_minutes [minutes] root
  |- cost [USD] <- wait_minutes
```

## 对齐的基准

主目标是 ParseBench 的 Charts 与 Visual Grounding 两个维度——现状是没有任何单一方法在这两项上同时强。此外覆盖 ChartREG++、ChartAB、LongChart VQA 的定位与指代任务，并要求在 ChartQA、CharXiv、ChartQAPro 上不退化。图表类型覆盖 6 族 13 型的常见形态，不局限于任何单一基准收录的那几种。

ParseBench 的评测指标拆解、数据统计与据此得出的待改清单在 [parsebench/](parsebench/)。

## 状态

规格已定稿。实现进行中，进度见 [IMPL_PLAN.md](IMPL_PLAN.md) 的 checklist：

- 骨架、六份数据接口、图表条件表、公共几何与像素反算、产物可读视图 — 已落地
- **01 数据** 全段已落地：领域池、四个声明方法、表达式、生成引擎、三类校验、那一次 LLM 调用与四类回喂
- 03 的 bar 边画边记 — 已落地
- 02 选图 / 03 其余类型 / 04 记录 / 05 输出 — 未开始

## 历史

本分支从 `py_parsebench` 切出，清空了与本方案无关的全部内容（VAGEN 时期的 chart generator、问答生成流水线、其他研究方向的 storyline）。这些内容仍在原分支上：

```bash
git show py_parsebench:<path>          # 看单个文件
git checkout py_parsebench -- <path>   # 取回到工作区
```

另有一份 Phase 0–2 的旧实现在 `dingc_suggest` 分支，可作参考；它对应的是已废弃的问答生成规格，不直接复用。
