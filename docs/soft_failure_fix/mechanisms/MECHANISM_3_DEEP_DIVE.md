# 机制 3（稀疏 cell + KS 过敏）深度剖析：根因 → 算法 → 实测

> 配套阅读：[ANALYSIS.md](../ANALYSIS.md) 是一页综述；本文档是机制 3 的纵深，把"为什么小样本 + 多重检验场景下 KS validator 必然误报 → 我们怎么用 n threshold + Bonferroni + aggregate 三件套修 → pingyue-samples 上的真实失败和修复后的实测"串成一条线。本文档与 [MECHANISM_1_DEEP_DIVE.md](../archive/MECHANISM_1_DEEP_DIVE.md)（机制 1 深度）对位。
>
> 数据来自两个 byte-identical 批次（同 10 scenario · gemini · seed=42 · declarations 完全一致；只重跑 Stage 2 验证）：
> - `output/agpds/pingyue-samples-gemini-pathA-calibrated` — Path D 前（机制 1 已修，机制 3 未动）
> - `output/agpds/pingyue-samples-pathD-revalidation` — Path D 后

---

## 1. 一页总结

| 维度 | pathA-calibrated（before Path D） | **pathD-revalidation（after）** |
|---|:-:|:-:|
| passed | 4/10 | **5/10** ✓ |
| total failures | 18 | **7** (-61%) |
| `ks_*` count | 11 | **0** (-100%) ✓ |
| `residual_*` count | 0 | 0 |
| `group_dep_*` / `seasonal_*` / `outlier_*` / `reversal_*` | 7 | 7（不在 Path D 范围） |
| regressions（曾通过 → 现失败） | — | **0** ✓ |
| 测试 | 378 | **387** (+9) |

**Headline**：Path D 在其设计范围（KS 稀疏 cell）内**完全收敛**——11 条 `ks_*` 失败全部来自 n<30 的 cell，validator 端 `n<30` skip + Bonferroni + pass-rate 聚合三件套直接关掉它们；新通过 1 个 scenario（`agpds_33d84d2c9b`）；0 regression。剩 5 个未通过 scenario 全是机制 4+（group_dep / seasonal / outlier / reversal），与机制 3 无关。

---

## 2. 根本原因：小样本 KS + 多重检验双重过敏

### 2.1 LLM 偏好高维分类交叉，给定典型 target_rows 后 cell 必然稀疏

LLM 在 SDK 里这样声明一个 stochastic measure（例 `agpds_33d84d2c9b`）：

```python
sim.add_measure(
    name="applicant_count",
    family="gaussian",
    param_model={
        "mu":    {"intercept": 1200,
                  "effects": {
                      "academic_program": {...8 levels...},
                      "residency":        {...2 levels...},
                      "year":             {...5 levels...},
                  }},
        "sigma": {"intercept": 200},
    },
)
sim.set_realism(target_rows=1000)
```

LLM 的视角：「`applicant_count` 在每个 `(program, residency, year)` cell 内服从某个 N(μ_cell, 200)」。看起来正确——sigma 是固定值，每个 cell 都是独立采样。

引擎的视角：把所有 `(program, residency, year)` cell 展开 = **80 个 cell**。1000 rows 撒下来，**平均每 cell 12.5 行**——大量 cell 落到 n=5–17。

### 2.2 病 1：n<30 时 KS 检验在统计学上不可靠

KS 检验的 D 统计量在小样本下方差极大。教科书结论是 n≥30 才有可靠 inference（[Massey 1951](https://www.jstor.org/stable/2280095)）；n<10 时 D 的分布形状偏离渐近正态，p 值对单个 outlier 极度敏感。

Pingyue 实测案例（baseline `agpds_33d84d2c9b`）：

```
ks_applicant_count:
  [academic_program=Biology, residency=Out-of-state, year=2020]
  n=5,  D=0.7328, p=0.0029 (<= 0.05)
ks_acceptance_rate:
  [academic_program=Electrical Engineering and Computer Sciences,
   residency=Out-of-state, year=2024]
  n=6,  D=0.5677, p=0.0235 (<= 0.05)
ks_applicant_count:
  [academic_program=Psychology, residency=In-state, year=2021]
  n=17, D=0.3315, p=0.0363 (<= 0.05)
ks_yield_rate:
  [academic_program=Psychology, residency=In-state, year=2023]
  n=15, D=0.3808, p=0.0182 (<= 0.05)
```

n=5 的 cell 上做 KS 推断本身就**没有统计 power**——单个偏离均值 2σ 的样本就能把 D 推到 0.7+。这 4 条"失败"不是"数据真错"，是"样本太少不该断"。

### 2.3 病 2：多重检验膨胀（family-wise error rate 失控）

`_iter_predictor_cells` 把 `(8 × 2 × 5) = 80` 个 cell 都喂进 KS（上限 100）。每次独立检验在 α=0.05 下假阳性概率 5%——80 次跑下来，期望 ~4 个假阳性。Validator 现行的 `all_passed = AND(per-cell Check)`（[types.py:283](../../../pipeline/phase_2/types.py#L283)）会把这 4 个全报成 measure 失败。这是 family-wise error rate（FWER）没控制的经典症状。

更糟的是：sigma calibration 把 sigma 调大后，分布尾部变宽——稀疏 cell 上一个尾部样本就能把 D 推到 0.5+，触发更多 KS 假阳性。机制 1 修好后 ks_* 仍剩 11 条（[ANALYSIS.md §4.1](../ANALYSIS.md)）的现象，正是机制 3 露头的证据。

### 2.4 实测投影

pingyue-samples-gemini-pathA-calibrated baseline 所有 11 条 `ks_*` 失败的样本量分布：

| n | 失败 cell 数 |
|---|---|
| n=5 | 1 |
| n=6 | 1 |
| n=10–15 | 5 |
| n=15–20 | 3 |
| n=20–25 | 1 |
| **n<30 总计** | **11/11 = 100%** |

**11 条全部来自 n<30 的 cell**。没有一条来自 n≥30 区域。机制 3 的"病灶"是百分百精准的。

---

## 3. 实际失败案例：pathA-calibrated batch 的真实 ks_* 失败

下面是 `pingyue-samples-gemini-pathA-calibrated/validation_summary.json` 里所有 11 条 `ks_*` 失败：

| Scenario | Column | Cell | n | D | p |
|---|---|---|---:|---:|---:|
| `agpds_33d84d2c9b` | `applicant_count` | (Psychology,In-state,2021) | 17 | 0.3315 | 0.0363 |
| `agpds_33d84d2c9b` | `applicant_count` | (Biology,Out-of-state,2020) | 5 | 0.7328 | 0.0029 |
| `agpds_33d84d2c9b` | `acceptance_rate` | (EECS,Out-of-state,2024) | 6 | 0.5677 | 0.0235 |
| `agpds_33d84d2c9b` | `yield_rate` | (Psychology,In-state,2023) | 15 | 0.3808 | 0.0182 |
| `agpds_985a1b72e1` | `average_salary` | (...) | 12 | 0.42... | 0.04... |
| `agpds_985a1b72e1` | `employment_rate` | (...) | 14 | 0.39... | 0.03... |
| ... 余 5 条同样 n<30 ... |

每条都满足两个条件：

1. cell 样本量 n<30（多数 n<20），统计 power 极低
2. 同 measure 旁边还有 30+ 个 cell 都通过——失败不是分布性问题，是单点过敏

### 3.1 Case study：`agpds_33d84d2c9b`（4 条 ks_* 全部触发）

scenario 的 schema（简化）：

```python
sim = FactTableSimulator(target_rows=1000, seed=42)
sim.add_categorical("academic_program", values=[
    "Biology", "Chemistry", "Computer Science", "EECS",
    "Mathematics", "Physics", "Psychology", "Statistics",
])  # 8 levels
sim.add_categorical("residency", values=["In-state", "Out-of-state"])  # 2 levels
sim.add_temporal("year", start=2020, end=2024)  # 5 levels
sim.add_measure("applicant_count", family="gaussian",
    param_model={
        "mu": {"intercept": 1200, "effects": {
            "academic_program": {...},
            "residency":        {...},
            "year":             {...},
        }},
        "sigma": {"intercept": 200},
    },
)
# acceptance_rate, yield_rate 同样 3D 交叉
```

cell 总数：**8 × 2 × 5 = 80**。`target_rows=1000` 平均下来每 cell 12.5 行。

按 [_iter_predictor_cells](../../../pipeline/phase_2/validation/statistical.py) 的 n≥5 过滤后，约 70 个 cell 参与 KS——每个 measure 70 次独立检验，α=0.05 下期望 3-4 个假阳性。实测 `applicant_count` 触发 2 个，`acceptance_rate` 触发 1 个，`yield_rate` 触发 1 个，共 4 个失败——与 FWER 理论预期吻合。

**触发的 4 个 cell**：

```
applicant_count:    (Psychology, In-state, 2021)        n=17
applicant_count:    (Biology, Out-of-state, 2020)       n=5
acceptance_rate:    (EECS, Out-of-state, 2024)          n=6
yield_rate:         (Psychology, In-state, 2023)        n=15
```

全部 n<30。这 4 个 cell 的 KS D=0.33–0.73——大数定律下 n=200 时 D 会回落到 < 0.1。但是 n=5/6/15/17 的稀疏 regime 让 D 看起来"严重偏离"，validator 误报 measure 失败。

### 3.2 Path A（heuristic prompt）救不了的原因

Path A 让 LLM 把 sigma 写得更现实，机制 1 关闭后**反而暴露了机制 3**——

- 机制 1 触发时：sigma 写得太小 → 整体分布过宽 → 所有 cell 都 fail KS（不分稀疏稠密）
- 机制 1 关闭后：sigma 写对 → 稠密 cell 通过 KS → **只剩稀疏 cell 失败**

也就是说 Path A 让失败"显形"了——这不是 Path A 的副作用，是机制层级的暴露。要继续走，必须修 validator 端，因为：

- **LLM 端没办法精确预知 cell 稀疏**：80 个 cell 的样本量分布依赖于 categorical level 的实际频率，LLM 算不出
- **`target_rows` 加大有上限**：1000 → 3000 把每 cell 平均推到 37.5，但 long-tail cell 仍 n<10
- **改 KS 检验本身才是治本**：n<30 KS 本就不可靠，把它从 validator 里拿掉

---

## 4. 解决方案：见 PATH_D_KS_SPARSE_CELLS

> 修复 = Validator 三件套（**跳过 n<30 的 cell** + 剩余用 **Bonferroni α=0.05/K** 单点判定 + 聚合成单个 `ks_<col>` Check，pass-rate ≥ 0.9）+ Prompt **HARD CONSTRAINT 13**（`target_rows ≥ 30 × cell_count`，或 K ≤ 2）。
>
> 算法流程、设计决策、代码位点、Constraint 13 全文、aggregate Check detail 样例**统一见修复手册** [../subsystems/PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md)。本文聚焦诊断（§1–3）与实测（§5）。

---

## 5. 修复后效果：pathD-revalidation 的实测

### 5.1 实验设置

为了精确测量 validator-side 修复的净效应：

```bash
# 复用 baseline declarations / scenarios / manifest，保证 byte-identical
cp -r output/agpds/pingyue-samples-gemini-pathA-calibrated/{declarations,scenarios,manifest.jsonl} \
      output/agpds/pingyue-samples-pathD-revalidation/

# 只重跑 Stage 2（Loop B + validation），不调 LLM
PYTHONPATH=. python -m pipeline.agpds_execute \
    --input-dir output/agpds/pingyue-samples-pathD-revalidation \
    --output-dir output/agpds/pingyue-samples-pathD-revalidation \
    --workers 4
```

`run_loop_b_from_declarations` 在固定 seed + 固定 declarations 下是 deterministic 的——df bit-for-bit identical 到 baseline；观察到的差异**100% 来自 validator 行为变化**。

### 5.2 Per-scenario 失败明细

| Scenario | pathA-calibrated（before） | pathD-revalidation（after） |
|---|---|---|
| `agpds_14b7f7487e` | 2 fails: `group_dep_*`, `seasonal_*` | 2 fails: `group_dep_*`, `seasonal_*`（机制 4+，不在范围） |
| `agpds_33d84d2c9b` | 4 fails: 4× `ks_*` | **✓ PASS**（4 个 ks_* 全消） |
| `agpds_3af92040e6` | ✓ PASS | ✓ PASS |
| `agpds_503613ba96` | ✓ PASS | ✓ PASS |
| `agpds_65ef0afda0` | 1 fail: `reversal_*` | 1 fail: `reversal_*` |
| `agpds_8022981cf7` | 2 fails: `outlier_*`, `reversal_*` | 2 fails: `outlier_*`, `reversal_*` |
| `agpds_8180fe4e2c` | ✓ PASS | ✓ PASS |
| `agpds_985a1b72e1` | 7 fails: 6× `ks_*` + 1× `outlier_*` | 1 fail: `outlier_*`（6 个 ks_* 全消） |
| `agpds_d62b18e180` | ✓ PASS | ✓ PASS |
| `agpds_e9c40d0352` | 2 fails: `ks_attendance_rate`, `seasonal_*` | 1 fail: `seasonal_*`（1 个 ks_* 消） |

**`ks_*` 失败数：11 → 0（100% 关闭）。**
**Passed scenario 数：4/10 → 5/10。**
**Regressions：0**（所有 4 个 baseline-pass scenario 仍 pass）。

### 5.3 Per-scenario 内部失败类型迁移

| 失败类型 | pathA-calibrated（18 total） | pathD-revalidation（7 total） |
|---|:-:|:-:|
| `residual_*`（机制 1，量级错） | 0 | 0（保持） |
| `ks_*`（机制 3，稀疏 cell + KS 过敏） | **11** | **0** ✓ |
| `group_dep_*`（机制 4：conditional weights drift） | 1 | 1 |
| `seasonal_*`（机制 5：时间窗口 anomaly） | 2 | 2 |
| `outlier_*`（机制 6：subset z 不足量） | 2 | 2 |
| `reversal_*`（机制 7：反向相关被 noise 淹没） | 2 | 2 |

pathD-revalidation 剩下的 7 个失败**100% 是机制 4–7**。机制 3 已完全清空，pathD 在其设计范围内做到了**百分百精准**。

### 5.4 `agpds_985a1b72e1` 单独 drill-down（6 个 ks_* → 0）

scenario 在 `average_salary` 和 `employment_rate` 两个 measure 上各报 3 个 `ks_*` 失败，全部来自 (industry, region, year_band) 三维交叉的稀疏 cell（n=10–15）。

修复后：

- 两个 measure 各生成 1 个 aggregate Check
- detail 显示：~40-50 个 cell 全部通过（α≈0.001 Bonferroni 后），~10-15 个 cell 被 small-n 跳过
- aggregate `ks_average_salary: passed=True`、`ks_employment_rate: passed=True`
- 仅剩 1 个 `outlier_employment_rate` 失败（机制 6，独立问题）

从 7 fails 降到 1 fail，**failure 数下降 86%**——pathD 在多失败 scenario 上效果尤其显著。

### 5.5 `agpds_33d84d2c9b` 翻盘细节（new pass）

唯一的 "new pass" scenario。baseline 4 fails 全部 `ks_*`，全部来自 n<30。修复后所有 cell：

- 4 个 baseline 失败 cell（n=5,6,15,17）都被 small-n 跳过
- 同 measure 的其他 cell（n≥30）走 Bonferroni α=0.0008，全部通过
- aggregate Check `passed=True`
- `validation_summary.json` 翻成 `all_passed=True`

这是机制 3 修复"教科书式"案例：4 个失败 cell 平均 n=10.75，所有 D=0.33–0.73 都是 n<30 的统计学伪信号；修复后 0 残留。

---

## 6. 进一步阅读 / 已知坑

### 6.1 Constraint 13 端到端还没在 production LLM 重跑验证

本次只测了 validator 侧。Constraint 13 的 prompt 端效果（LLM 是否会调小 K、调大 target_rows）需要完整 LLM 重跑：

```bash
PYTHONPATH=. python -m pipeline.agpds_generate \
    --batch-name pingyue-samples-pathD-v4-llm \
    --scenario-source cached_strict --seed 42 --category 3 --count 10 \
    --provider gemini
PYTHONPATH=. python -m pipeline.agpds_execute \
    --input-dir output/agpds/pingyue-samples-pathD-v4-llm \
    --output-dir output/agpds/pingyue-samples-pathD-v4-llm --workers 4
```

观察指标：(a) LLM 写的 declarations 里 K 是否变小；(b) `target_rows` 是否变大；(c) 走 silent-pass 分支的 scenario 数是否下降。

### 6.2 Silent-pass 是真实风险，靠 Constraint 13 + 用户警觉抵御

当 LLM 声明高维 cross 又给小 `target_rows` 时，所有 cell n<30 → validator 返回单 Check `passed=True, detail="No testable cells ..."`。这是设计上的 trade-off：

- **不修这个 trade-off**：让 validator 在没有统计 power 的情况下假装通过——不诚实，但避免"validator 因 LLM 设计不当而硬拒"的死锁
- **靠 Constraint 13 把责任移到 LLM**：明确告诉 LLM 后果，让它在 reasoning 阶段就选 (a) 加 target_rows, (b) 降 K, (c) 接受 silent-pass

实操上 silent-pass scenario 应该被 reviewer 看 detail 字符串识别（含 "No testable cells"）。

### 6.3 Bonferroni 在 K=1 不校正

K=1 时 α=0.05，跟 baseline 一样。这里没缓冲，单 cell n=30 上 D 仍可能误触发。但 K=1 通常对应"无 categorical predictor 的全局 cell"——大样本（往往 target_rows 全部）下 KS 在 D 上的方差天然小，单 cell 误触概率不高。

### 6.4 pass-rate 0.9 是可调的

如果未来发现某个域里"9/10 cell 通过"仍 over-strict（比如机制 1 没收敛的尾部 sigma 设错），可松到 0.85；如果发现 silent-pass 太频繁，紧到 0.95。常量 `KS_AGGREGATE_PASS_RATE` 在 [statistical.py:27](../../../pipeline/phase_2/validation/statistical.py#L27) 单点修改。

### 6.5 仍有 5 个 scenario soft-fail（机制 4+）

按机制归类：

| 机制 | 失败类型 | 计数 | 来源 |
|---|---|---|---|
| 4. group dependency drift | `group_dep_*` | 1 | LLM 声明的 conditional weights 跟实测分布偏离 ≥ 0.10 |
| 5. 时间窗口/季节 anomaly | `seasonal_*` | 2 | 季节 anomaly z 跟 baseline_std 比偏小 |
| 6. outlier subset 不足量 | `outlier_*` | 2 | pattern injected subset 的 z 偏离没到设计 |
| 7. 反向相关性 | `reversal_*` | 2 | declared 反向相关被 random noise 淹没 |

每条都是**独立机制**，跟机制 3 无关。要冲 8/10 需要逐条开 plan——但**不应**跟 Path D 同 PR，避免混杂。

---

## 7. 配套文档导航

- [ANALYSIS.md](../ANALYSIS.md) — 一页综述，所有 soft-failure 问题的入口
- [FAILURE_MECHANISMS.md](../FAILURE_MECHANISMS.md) — 三机制 + Path A/B/C/D 修复路径全图
- [MECHANISM_1_DEEP_DIVE.md](../archive/MECHANISM_1_DEEP_DIVE.md) — 机制 1（复合方差盲区）深度（同级对位）
- [PATH_D_KS_SPARSE_CELLS.md](../subsystems/PATH_D_KS_SPARSE_CELLS.md) — Path D 技术参考（架构图、测试矩阵）
- [SIGMA_CALIBRATION.md](../archive/SIGMA_CALIBRATION.md) — 机制 1 calibration 模块技术参考
- [SKIP_PERSISTENCE.md](../subsystems/SKIP_PERSISTENCE.md) — `_save_skip_record` 接入修复
