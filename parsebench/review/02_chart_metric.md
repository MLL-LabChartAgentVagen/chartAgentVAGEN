# ChartDataPointMatch 的判定规则

读自官方代码 `evaluation/metrics/parse/rules_chart.py::ChartDataPointRule` 与 `test_cases/parse_rule_schemas.py`。写的是代码实际执行的判定，不是论文概述。

---

## 1. 一条规则长什么样

```json
{"value": "0.8079", "labels": ["IF", "193 UN Member States"],
 "max_diffs": 0, "normalize_numbers": true}
```

取自 `(Web_version)_E-Government_Survey_2024_1392024_p101`。这一页是 6 个面板的小倍数横向条形图，`IF` 是条的类目名，`193 UN Member States` 是**面板名**，写在面板上方的图例位置。`relative_tolerance` 缺省，取 0.01。

| 字段 | 含义 | chart 分片的分布 |
|---|---|---|
| `value` | 数值，字符串 | 整数 3,111 · 1 位小数 1,309 · 带 `%` 499 · 负值 399 |
| `labels` | 定位这个值需要的键，1–4 个 | 1→268 · 2→3,847 · 3→715 · 4→34 |
| `max_diffs` | 编辑距离上限，同时控制值与标签的阈值 | 0（含缺省）4,094 · 2→729 · 其余 41 |
| `relative_tolerance` | 相对容差 | 估读点中位 0.05；显式数值点中位 0.01 |

---

## 2. 四步判定，走一遍这条规则

假设解析器输出了这样一页：

```markdown
## Figure 2.33 Average OSI subindex values for groups of countries

**193 UN Member States**

| Subindex | Value  |
|----------|--------|
| IF       | 0.8079 |
| CP       | 0.6644 |
```

**第一步 · 只看表。** 抽出输出里所有 markdown 表与 HTML 表。**没有表直接 0 分**，正文里把数值写得再准也不算。这里抽到 1 张。

**第二步 · 找值所在的格。** 逐格比对，两条通路任一成立：

```
阈值 = max(0.5, 1.0 - max_diffs / len(value))          # max_diffs=0 → 阈值 1.0
① fuzz.ratio(value, cell)/100 ≥ 阈值                    # 退化为归一化后精确相等
② numbers_match(value, cell, relative_tolerance)
```

`numbers_match` 先归一化：去 `$€£¥`、`~≈`、`%`、千分位逗号与空格，识别后缀乘倍率（`k`=1e3 `m`=1e6 `b`/`g`=1e9 `t`=1e12），逗号有歧义时按千分位与小数点各算一遍；再判 `|a−b| / max(|a|,|b|) ≤ tolerance`。**分母是两者较大者，不是标注值。**

`0.8079` 命中 `(1, 1)`。

**第三步 · 标签是否与该格关联。** 对命中格 `(r, c)`，每个标签走四条通路，任一成立即算关联：

| 通路 | 条件 |
|---|---|
| 同行 | 第 `r` 行其他格匹配 |
| 同列 | 第 `c` 列其他格匹配 |
| 跨列表头 | `col_headers[c]` 匹配（colspan） |
| 跨行表头 | `row_headers[r]` 匹配（rowspan） |

单格匹配：`fuzz.partial_ratio ≥ max(0.5, 1 − max_diffs/len(label))`，或去掉非字母数字后 label 是 cell 的子串。

**"对表格转置不敏感"就来自这里**——接受同行或同列，行列互换判定不变，不是靠转置表再比一次。

`IF` 在同行 `(1,0)` ✓。`193 UN Member States` 四条通路全不中 ✗。

**第四步 · 表外上下文回退。** 用**表之前**的内容（`context_before`；表之后的内容不参与）再判：

- 标签在表内**任何位置都不存在**，且以 `**粗体**`、markdown 标题、`<h1>`–`<h6>`、`<strong>`/`<b>` 出现在上下文，`fuzz.ratio ≥ 0.60` → 算通过
- 标签出现在 `<caption>` 或 markdown 标题里 → 直接通过，即使它同时也是表内某个表头

`**193 UN Member States**` 是粗体且不在表内 → 通过。**这条规则最终判 1.0。**

### 同一页，改一个字符就变 0 分

把面板名写成普通文本行：

```markdown
193 UN Member States

| Subindex | Value  |
```

值对、表结构对、面板名也写出来了，但它既不是粗体也不是标题也不是 caption，第四步不认，**这条规则判 0**。

### 长表根本不会走到第四步

```markdown
| Group                | Subindex | Value  |
|----------------------|----------|--------|
| 193 UN Member States | IF       | 0.8079 |
```

两个标签都与数值同行，第三步一次通过。**键有几个都一样**，三键、四键同理。

---

## 3. 计分

单条规则**二值**，1.0 或 0.0，无部分分。

```
每页得分  = 该页规则得分之和 / 该页规则数        # evaluators/parse.py:272-274
Charts 得分 = 各页得分的平均                     # 聚合报告的 avg_ 键
```

每页 2–11 条规则（中位 10）。按页平均而非按规则平均，规则少的页权重更高。

---

## 4. 三条对输出格式的直接结论

| # | 结论 | 依据 |
|---|---|---|
| 1 | **长表是最稳形态**。宽表要靠"同列 + 表头"两条通路配合，三键时还依赖 colspan 表头被正确写出；长表只用"同行"一条 | §2 的两个对照例 |
| 2 | **只看召回，不罚精确率**。遍历所有表所有命中格，任一成立即通过；多输出的行与表不扣分。所以在 Charts 维度上，把一张图的所有点都写进表严格优于只写有把握的几个 | `run()` 的双重循环 |
| 3 | **数值必须按图上显示的刻度写**。`485k` / `485000` / `$485,000` 互相匹配，但轴标题写 "in millions" 而表里存原值会判负——`numbers_match` 只认值自带的后缀，不读表头的量纲说明 | 归一化只作用于单个 cell |

结论 2 的边界：多余内容会在 **Content Faithfulness** 维度被罚，但那是另一组 506 页、另一套规则，与 Charts 的 568 页不重叠。

---

## 5. 未启用的规则类型

代码里另有 `ChartDataArrayLabelsRule` 与 `ChartDataArrayDataRule`——整表比对、支持行列乱序与转置、给部分分。**chart 分片一条没用**，4,864 条全是 `chart_data_point`。若日后启用，评测将从抽查点转为整表召回，本节需重读。
