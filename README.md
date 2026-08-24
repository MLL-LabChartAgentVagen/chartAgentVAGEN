# 带位置的图表转录 — 数据生成

程序化生成图表数据，产出的每个数值都带着它被画在哪里的坐标。目标能力是 **grounded transcription（带位置的转录）**：把图表转成结构化表的同时，给出每个值读取自哪块像素区域。

所有 ground truth 在渲染时直接记下来，不靠估计，也不靠标注已有的图。

## 目录

| 路径 | 内容 |
|---|---|
| [storyline/parsebench_chart/](storyline/parsebench_chart/) | 方案规格。流水线的唯一定义处，五个阶段文档共用一份贯穿示例 |
| [storyline/parsebench_chart/chart_types.md](storyline/parsebench_chart/chart_types.md) | 能画哪些图、每种图要满足什么条件才能画 |
| [plan/](plan/) | 实现计划，两份，都按流水线的顺序排：[PLAN.md](plan/PLAN.md) 给 coding agent（一步一节，缺口就地嵌进它落的那一步，每节末尾是该步的施工清单）· [plan.html](plan/plan.html) 给人看的图解版（总览 ＋ 每步一页） |
| [parsebench/](parsebench/) | ParseBench 对齐：Charts 维度的 review、评测指标拆解、chart 分片数据与统计、待改清单 |
| [src/chartgen/](src/chartgen/) | 流水线本体 |
| [src/llmkit/](src/llmkit/) | 与本项目无关的 LLM 调用层：调用 · 结构化输出 · 缓存 · 去重 · 批量。Anthropic / OpenAI / Gemini 三家同一个调用面，写模型名就换家。可单独复用 |
| [plan/reports/report.html](plan/reports/report.html) | **一页纸的总览**：一次真实运行（六个场景，两次模型调用各写数据与图上的字）的产出，按阶段分节，16 个完整例子，图片内嵌，可单独发出去。英文版 [report_en.html](plan/reports/report_en.html) 是同一份代码换一种语言写出来的，内容与数字完全一致 |
| [review/](review/) | **长版，也是总入口**：[review/index.html](review/index.html) 一页站点地图，往下是每一步一页（各十几个完整例子）、[全部样本](review/gallery.html)（这次画的 96 张图一张不落）、每种图表类型一页（17 页）、[一页多图](review/pages.html)（同页两图、多面板、同画区叠画，也是唯一把整页当成一页看的地方）、[多样性](review/diversity.html)（同一张图换六套样式重画，答案必须一致），最后是 [checks.html](review/checks.html) 讲代码怎么被验的——测试、覆盖率、故障注入、产物核对。共 28 页。页面本身不进版本库（图片内嵌，二十兆），`python tools/build_review.py` 跑一次就有 |
| [tools/](tools/) | 辅助脚本：接口样例 · 框叠回图像 · 两套报告 · 每种图表类型的例子 · 故障注入 |
| [data/domains/](data/domains/) | 领域池（进版本库，整个项目只建一次） |
| `data/generated/` | 运行产物（不进版本库） |
| [slides/](slides/) | 讲稿 |

**代码一律用英文**（注释、docstring、异常文本、提示词）。中文只出现在 `storyline/`、`README.md`、`plan/` 这几份文档里。

## 流水线

五个阶段，**整条流水线只有两次 LLM 调用**：01 写数据，02 写字。01 一次写出场景散文、数据生成脚本与绑到列上的分析意图；02 在图选定之后，一次给这一批图写标题、副标题、单位与每列的散文名。两次调用都不产出任何数值、键或框，此后构造、推导、采样、拒绝、组版、渲染、记录、导出全部是规则。

```
01 数据 [LLM×1] → 02 选图 [LLM×1] → 03 渲染 → 04 记录 → 05 输出
```

02 的三类图三种产出方式：意图图从绑定**构造**，多面板图与组合图从锚点**推导**，轮转图按族**采样加拒绝**——只有最后一路需要随机数。多样性由 `(键集合, 图元形状)` 判据管，不由数量管。

图表类型表是「投影形态 × 图元形状」的乘积，6 族 17 型 6 种图元形状；每一格要么填一个类型，要么写明为什么空着。

## 怎么跑

```bash
pip install -r requirements.txt
export PYTHONPATH=src          # 下面所有命令都要
```

| 想做什么 | 命令 |
|---|---|
| 跑全部测试 | `python -m pytest` |
| 跑真调模型的那个测试 | `CHARTGEN_LLM=1 python -m pytest tests/e2e -s` |
| 建领域池（**调模型，整个项目一次**：14 个领域 × 6 种语域 = 46 个单元） | `python -m chartgen.cli pool` |
| 往已有的池子里加，不是覆盖它 | `python -m chartgen.cli pool --extend` |
| 只跑 01，**不调模型**（拿手写的输出走完规则那一半） | `python -m chartgen.cli data --payload tests/samples/er_scenario.json --scenario er_wait` |
| 只跑 01，**调一次模型**（临时指定领域） | `python -m chartgen.cli data --domain "ICU bed turnover" --tier medium` |
| 只跑 01，从领域池抽 | `python -m chartgen.cli data --scenario s000` |
| 重画一份已有 schema 的图 | `python -m chartgen.cli inspect data/generated/s000/schema.json` |
| 只跑 02，**不调模型**（看它选了哪些图、拒了什么） | `python -m chartgen.cli figures --payload tests/samples/er_scenario.json --scenario er_wait` |
| 只跑 03，从一份 FigureSpec 渲染 | `python -m chartgen.cli render tests/samples/figure_spec.json -o data/generated/demo` |
| 把记录里的框叠回图像目视检查 | `python tools/overlay.py data/generated/demo/f01.json` |
| **跑整条流水线，不调模型** | `python -m chartgen.cli run --payload tests/samples/er_scenario.json --scenario er_wait` |
| 跑整条流水线，从领域池抽场景 | `python -m chartgen.cli run --scenarios 3` |
| 多图页那一档（一页放几张图，关系拆到页上） | `python -m chartgen.cli run --set figure.pages=3 --set figure.k_max=22` |
| 重建 [plan/reports/report.html](plan/reports/report.html)（读一次跑完的产物，出一页 HTML） | `python tools/build_report.py data/generated/live` |
| 同一份报告的英文版 | `python tools/build_report.py data/generated/live --lang en -o plan/reports/report_en.html` |
| 重建 [review/](review/)（总入口 ＋ 每步一页 ＋ 全部样本 ＋ 17 种类型 ＋ 多样性 ＋ 检查页） | `python tools/build_review.py` |
| 故障注入：把代码改错，看测试会不会失败 | `python tools/mutation.py --limit 5` |
| 语句覆盖率 | `pytest --cov=src/chartgen --cov=src/llmkit` |
| 重生成接口样例（改了接口之后） | `python tools/make_samples.py` |

改配置：`--config 别的.yaml` 换一份，`--set data.target_rows=1200` 覆盖单项。默认值与每一项的含义在 [configs/default.yaml](configs/default.yaml)。

想按某一把尺子的形态导出，用一个预设：`--set output.preset=parsebench` 把导出粒度、形态、键的范围与目标打包成一组——一页一份 markdown，表前标题写画在图上的图号与图题，键的每一段单独占一列。预设改的只是取哪个投影、写成什么样，记录里有什么一个字不动；单独写明的项盖过预设，例如 `--set output.preset=parsebench --set output.format=both` 同时写 markdown 与结构化载荷。

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

主目标是 ParseBench 的 Charts 与 Visual Grounding 两个维度——现状是没有任何单一方法在这两项上同时强。此外覆盖 ChartREG++、ChartAB、LongChart VQA 的定位与指代任务，并要求在 ChartQA、CharXiv、ChartQAPro 上不退化。图表类型覆盖 6 族 17 型的常见形态，不局限于任何单一基准收录的那几种。

ParseBench 的评测指标拆解、数据统计与据此得出的待改清单在 [parsebench/](parsebench/)。

## 状态

五个阶段全部落地，端到端可跑、逐位可复现。进度见 [plan/PLAN.md](plan/PLAN.md) 各节末尾的 checklist。跑出来的东西按三层读：先 [plan/reports/report.html](plan/reports/report.html)（一页总览），再 [review/index.html](review/index.html)（总入口，往下是每一步、全部样本、17 种类型、多样性），最后 [review/checks.html](review/checks.html)（代码怎么被验的）。

一次六场景的真实运行（每个场景两次 `gemini-flash-latest` 调用，其余全部是程序）：192 份标注记录、8 378 个图元。**丢掉值目标有两个原因，分开算**：6 024 个图元的键在页面上没有出处（几乎全是散点，它用行号寻址），剩下 2 354 个里 1 407 个带值目标（60%），1 189 个的值印在图上。17 种图表类型里画出 16 种——漏斗是唯一没画出来的，它要求值只降不升，而声明得出阶段列不等于那几段的值真的一路下降。三项自检 192/192 通过。产物核对：2 175 个页面元素无一落在图外，两两比过的 10 118 对文字无一互相压盖。

代码这一侧：测试 1 330 项、语句覆盖 96%、故障注入 98/144 被测试抓住，覆盖 50 个模块（活下来的 46 处逐条列在 [review/checks.html](review/checks.html)，是接下来要补的测试清单）。

ParseBench 对齐的十条改进 P1–P10（[parsebench/reports/INDEX.md](parsebench/reports/INDEX.md)）已全部落地，其中五条按 [plan/PLAN.md](plan/PLAN.md) 的一般化形式实现——键的每一段记来源、图外文本一等对象、风格取值域表、类型表按乘积、导出粒度是参数。

## 历史

本分支从 `py_parsebench` 切出，清空了与本方案无关的全部内容（VAGEN 时期的 chart generator、问答生成流水线、其他研究方向的 storyline）。这些内容仍在原分支上：

```bash
git show py_parsebench:<path>          # 看单个文件
git checkout py_parsebench -- <path>   # 取回到工作区
```

另有一份 Phase 0–2 的旧实现在 `dingc_suggest` 分支，可作参考；它对应的是已废弃的问答生成规格，不直接复用。
