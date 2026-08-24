# TODO

换机器后从这里继续。本文件自包含——只读这一份即可。

---

## 1 · 先审：上一个 session 的实现与产物

`src/chartgen/` 的五阶段流水线，连同它生成的运行与站点，由上一个 session 写成，这次一起入库，**我还没逐条审过**。剩下要做的就是 check 这些生成的内容。

### 1.1 上一个 session 做完了什么（总结）

- **实现**：五阶段流水线从规格落成代码，149 项里 145 项完成；十条 ParseBench 缺口 P1–P10 与五条一般化都进了代码。
- **产物**：一次完整运行在 `data/generated/live`（6 个场景）；两个自建站点 `review/`（每步一页 + 全部样本 + 每种图表类型 + 多样性 + 检查页）与 `plan/reports/*.html`；三家模型的 ParseBench 分析报告在 `parsebench/reports/`。
- **自验**：1330 项测试、语句覆盖 96%、故障注入 98/144（活下来 46 处）、17 种图表类型全过自检、奖励在五种图元形状上一致性 1.0、ER 数字链五份规格文档对齐。
- **活的总结**在 `review/index.html` 与 `review/checks.html`。站点已入库，直接打开即可；要重新生成给自己看：
  ```
  python tools/build_review.py --run data/generated/live     # → review/index.html
  python tools/build_report.py data/generated/live           # → plan/reports/report.html
  ```

### 1.2 还没做（都在训练 / 评测侧，不是流水线能力）

消融表的数字（要先训模型）、其他导出（问答对 / 图表代码 / 配对样本）、官方规则在 568 页上的自评。

### 1.3 我要 check 的

- [ ] 跑一遍端到端，确认 (输入, 种子) → 输出 逐位可复现
- [ ] 打开 `review/index.html`，过一遍全部样本与检查页
- [ ] 跑测试（1330 项，语句覆盖 96%）
- [ ] 逐条核对十条缺口是否如实落地
- [ ] **再跑一批更大的样本（50+ 场景）来 check 生成质量**。当前运行只有 6 个场景，看不出多样性、图表类型覆盖、复杂组合图的比例；而 §2 三条改进的效果也得在更大的一批上才看得见。成本是每场景两次 LLM 调用（01 数据、02 文字），50 场景约 100 次，便宜。**建议做**。

---

## 2 · 当前阶段

### 2.1 图例

现有：图例位置是风格维（底 / 右 / 左、每面板、内嵌）；small multiples 能让多个面板共用一个图例。

- [ ] 图例形态扩成一个完整可配维度：位置 × 每面板 / 共享 × 有无图例标题
- [ ] 共享图例扩到 small multiples 之外——**一页 N 张图共用一个图例**，现在只有 small multiples 一种

### 2.2 类型分布按三家 VLM 汇总

ParseBench 标注不带图表类型标签，配比只能用三家模型看图数出的 pooled 计数：line 181、stacked_bar 128、bar 97、grouped_bar 90、pie 21、area 5、scatter 5，distribution 与 process 两族为 0。已折成族级预设放在 `src/chartgen/s02_figure/sampling.py`。

- [ ] 把这份配比接进生成，作对齐 ParseBench 的那一档；默认仍是 uniform（等概率轮转）

### 2.3 多生成复杂组合图

能力已在：`overlay_metric`（可加测度作条底 + 另一测度作折线叠加）、`series_marks`（折线加记号）、每个图元记 `value_axis` 与 `mark_shape`。默认批次偏简单是**预算问题**：叠放每种关系至多一张、密度档偏稀疏。

- [ ] 抬叠放预算与密度档，让「条 + 折线 + 折线上的点」这类组合图在默认批次里出得更多

---

## 3 · ParseBench 样本可视化

- [ ] 做一个 ParseBench 样本页：沿用现在的 HTML 模板（`plan/plan.html` 的样式，与 `tools/reportkit.py`），把 ParseBench 的样本页逐个列出来，每页配它的图与抽查点，清晰、well-organized、美观。数据在 `parsebench/data/`（标注 `raw/chart.jsonl`、页面图 `pages/`、100 页抽样 `stats/analysis_sample.json`）。

---

## 4 · 之后（visual provenance）

单独一批重跑，与当前阶段的改动前后可比。

- [ ] 绘图区内的**说明框 / 引线注解**：画在画区里、承载解释而非数据，进 L0（页面元素、干扰项），不进 L1
- [ ] **参考线**（水平 / 垂直虚线，含零线）：跨整个画区、常在图例占一项，进 L0，转写时不报成数据点
- [ ] 类型表缺的**图族**，扩样才进得来：地图 / 分级填色、仪表盘、雷达、桑基、甘特、人口金字塔、斜坡图（当前样本一张没抽到）
