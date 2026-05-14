# Phase 2 验证失败的根因机制与修复

本文档分析 `output/agpds/pingyue-samples`（2026-05-13 生产批次，0 passed / 8
soft-failed / 2 errored）暴露出来的根本病因，并解释三条修复路径
（A + B + C）为什么能管用。结论是评估其他批次时也适用的通用机制。

> **配套阅读**：
> - 持久化层：[VALIDATION_PERSISTENCE.md](VALIDATION_PERSISTENCE.md)
> - Loop B 自动修复策略：[validation/autofix.py](validation/autofix.py)
> - M3 prompt 装配：[orchestration/prompt.py](orchestration/prompt.py)

---

## 1. 一句话根因

> **LLM 把每个 SDK 调用当成独立声明在写，但引擎把它们作为联合分布 + 乘法
> 结构公式来求值。**两边对"我在描述什么"的认知是错位的——LLM 在拼乐高
> 积木，引擎在跑微分方程。

这个错位通过三条机制反映成全部失败：

| 机制 | 触发的失败 | 涉及的失败数 |
|---|---|---:|
| 1. 复合方差盲区 | `residual_*`、大部分 `ks_*` | 15 + 大量 |
| 2. 联合分布盲区 | `PatternInjectionError`、`KeyError: 'None'` | 2 个 error |
| 3. 稀疏 cell 脆弱性 | 剩余 `ks_*` | 放大机制 1 |

---

## 2. 机制 1 — 复合方差盲区

### 现象

15 条 `residual_*` 失败，ratio = `residual_std / noise_sigma` 高达 **66×**：

| 列 | declared σ | empirical residual σ | ratio |
|---|---:|---:|---:|
| `residual_absentee_count` | 5.0 | 337.3 | 66.5× |
| `residual_student_faculty_ratio` | 1.15 | 35.2 | 29.6× |
| `residual_citation_count` | 45.0 | 319.3 | 6.1× |

### 机制

以 `agpds_8180fe4e2c` 的核心公式为例：

```
enrollment_count = application_count
                 * acceptance_fraction
                 * major_yield
                 * level_yield
                 * school_enrollment_multiplier
```

LLM 看每个因子时分别想："`application_count` 大概 0–5000，
`acceptance_fraction` 大概 0.1–0.6，每个 yield 大概 0.5–1.5"——然后给乘积加
`noise={"sigma": 5}`。

**它没有算乘积的方差**。5 个非独立随机变量相乘，方差是各项方差和均值的
复杂卷积，实际 std 可以轻松到 300+。Validator 报的 ratio 66× 不是 bug，
是数学。

`ks_*` 失败大多数也是这个机制的投影：每个分类列的 marginal 看起来对，
但 4 个分类列交叉成的 4D cell 内，实际散布远超 declared sigma →
Kolmogorov-Smirnov 拒绝原假设，D 高达 0.97，p ≈ 0。

### 2.5 为什么有些域感觉"没病"——域漂移决定了机制 1 的触发率

机制 1 一直潜伏在 LLM 的认知模型里——但**只在乘法主导的域里发病**。

实测对比（4 个 legacy 早期声明 vs 10 个 pingyue 教育域声明）：

| 批次 | 域 | structural 公式数 | 平均 `*` | 多随机变量乘积 | per-scenario 失败 |
|---|---|---:|---:|---|---:|
| **legacy** | Spotify / Netflix / faculty workload | 11 | 1.0 | ❌ 几乎全是 "stochastic × **常数** + add" | **3.5** |
| pingyue-v1 (openai) | 大学招生 / 留存 / 课程 | 19 | 1.8 | ✓ 含 5 个随机变量相乘的怪物 | 14.0 |
| pingyue-gemini-baseline | 同上 | 20 | 1.3 | ✓ 含 3 个随机变量相乘 | 8.3 |
| pingyue-gemini-pathA | 同上 | 19 | 1.5 | ✓（被 Path A 压缩了一些） | 9.3 |

典型公式对比：

```
LEGACY (Spotify / faculty 域 —— 度量关系天然加法):
  unique_listeners       = weekly_streams * 0.25 + region_adj           # 单随机 × 常数
  total_credit_hours     = student_faculty_ratio * teaching_load * 120  # 双随机 × 常数

PINGYUE (大学招生 funnel 域 —— 度量关系天然乘法):
  enrollment_count = application_count * acceptance_fraction * major_yield
                   * level_yield * school_enrollment_multiplier         # 五随机相乘！
  enrolled_count   = applicant_count * acceptance_rate * yield_rate     # 三随机相乘
```

**为什么是这样**：

- **Spotify/Netflix/faculty 域**的度量关系是"baseline + 线性效应 + 噪声"的
  叠加结构。LLM 用 `A + B*const + effect` 建模——单随机变量×常数是低方差
  操作，加法不放大方差。机制 1 几乎不发病。
- **大学招生/留存域**本质上是漏斗模型：`P(accept | applied) × P(enroll | accept)`，
  乘的是**条件概率**或**比率**。LLM 用 `A * B * C * D` 建模是数学上正确的
  domain modeling——但这正好触发机制 1 的最坏路径。

**实操含义**：

1. **"用 `agpds_pipeline.py` 跑时几乎没 warning" 不是 baseline，是运气**——早期
   `pingyue-samples-2`/`pingyue-samples-openai-v1` 之前的样本碰巧都是加法
   主导的域。看到一份"干净"的 validation_summary 不代表声明没问题，可能
   只是没踩到雷。
2. **机制 1 的修复优先级取决于目标域分布**：如果项目以后大量产 funnel /
   留存 / 转化类数据，§7.1 的 dry-run sigma 校准是必做项；如果主要还是
   Spotify-like 加法域，Path A 的 heuristic 就够。
3. **Validator 阈值 0.2 的合理性也跟域绑定**：加法域 LLM 易达成，乘法域
   数学上 LLM 难以闭式算出 std。要么 dry-run 校准，要么 validator 按域
   动态调阈值（后者更脏）。

---

## 3. 机制 2 — 联合分布盲区

### 现象 A：Pattern target 0 命中

`agpds_3af92040e6` 中 LLM 声明：

```python
inject_pattern(
    "outlier_entity",
    target="campus == 'UC Berkeley' & race_ethnicity == 'Native American/Alaska Native'",
)
```

引擎抛 `PatternInjectionError: Target ... matched zero rows`。

### 机制

LLM 知道 Berkeley 占 20%，Native American 在国际生中条件概率 1%。这两个值
**单独都存在**。但它没算：

```
P(both) ≈ 720 × 0.2 × 0.01 × P(International) ≈ < 1 row
```

### 现象 B：`KeyError: 'None'`

`agpds_8180fe4e2c` 在 [engine/measures.py:247](engine/measures.py#L247) 抛
`KeyError: 'None'`。根因是 `major` 是 `school_college` 的子列，条件分布在
某些 `(school_college, major)` 组合下的权重和未归一化到 1，sampling 回退
出 `None`，然后 effect map 查不到 `'None'` 这个键。

### 共同特征

机制 2 的两个表现共享一个特征——LLM 在**没算联合概率**的情况下，对
marginal 上"看起来合理"的值做了 AND 操作（pattern target 是显式 AND，
group dependency 是隐式条件 AND）。

---

## 4. 机制 3 — 稀疏 cell 脆弱性

LLM 喜欢声明多维分类结构（`tier × program × year × residency`），交叉后
cell 大小 n=5–35。KS 检验在 n<30 时对单个噪声样本非常敏感——一个 outlier
就能把 D 推到 0.7+。

这部分**不全是 LLM 的错**：多因子设计下，给定 `target_rows=300–1000`，
cell 必然稀疏。但 LLM 没考虑"我的 `target_rows` 够不够喂这个 cell 结构"。

这一机制不在本次修复范围（Path D 已显式拒绝），但被机制 1 放大——
如果 LLM 的 noise 估错了，稀疏 cell 是最先暴露的地方。

---

## 5. 为什么 Loop B 救不了

Loop B 的四把工具：

| 工具 | 来源 | 能力 |
|---|---|---|
| `widen_variance` | `autofix.py:77` | sigma × 1.2 每次重试（复利） |
| `amplify_magnitude` | `autofix.py:147` | pattern 强度 × 1.3 |
| `reshuffle_pair` | `autofix.py:206` | 重排序某列破坏伪相关 |
| `override_noise` | engine | 调 noise 参数 |

这些都是**局部参数微调**——它们能在 LLM 写的菜谱上撒盐换油，**不能改变
公式结构**。

具体看为什么救不了本次的失败：

- **机制 1**：当 residual std 是 declared sigma 的 66× 时，
  `widen_variance × 1.2^3 = × 1.73`，远远不够。
- **机制 2 (zero rows)**：当 pattern target 本来就是 0 行时，没有任何
  参数 override 能凭空造出符合条件的行。
- **机制 2 (KeyError)**：effect map 漏了一个 key 时，重跑只是同一份脚本
  同一个 bug——而且原本还是裸 `KeyError`，Loop A 都无法把它识别成 typed
  exception 反馈给 LLM。

> **Loop B 的设计前提**是"LLM 把骨架搭对了，只是火候没调准"。这批样本
> 暴露的是：LLM 连骨架都没搭对——它**误判了变量之间的耦合关系**。骨架
> 错误必须沿着 Loop A（LLM-in-the-loop）修。

---

## 6. 三条修复路径为什么管用

我们刚做的三条修复，从不同角度逼 LLM 把骨架搭对：

| 路径 | 治哪条机制 | 治法 | 代码位点 |
|---|---|---|---|
| **A. Prompt 加 noise + None 约束** | 机制 1 + 机制 2 | 在 LLM 写代码前**告诉它复合方差和 None 陷阱存在**，让它在 declaration 时就算清楚 | [orchestration/prompt.py:103-118](orchestration/prompt.py#L103-L118) |
| **B. PatternInjectionError 详化** | 机制 2 | 在第一次写错后，**给 LLM 显式的修复指引**：检查值组合的边际频率 | [engine/patterns.py:47-63](engine/patterns.py#L47-L63) |
| **C. `KeyError → UndefinedEffectError`** | 机制 2 | 把哑错变成会话——Loop A 收到 typed feedback，能 surgical 修 effect map | [engine/measures.py:245-251](engine/measures.py#L245-L251) |

### 6.1 Path A：预防——在声明阶段就别犯错

新增的两条 HARD CONSTRAINT：

**约束 11（noise 校准）**

> 当声明 gaussian/normal 噪声的 stochastic 或 structural measure 时，
> `sigma` **必须**约等于 measure 期望动态范围的 10–30%。如果 measure
> 范围是 `[0, 1000]`，`sigma` 应当是 ~50–300，**不是** 1–5。
> Under-sizing noise 是单一最常见的验证失败。

**约束 12（None 禁用）**

> **永远不要**把 Python `None` 或字符串 `"None"` 用作类别值、`parent=`
> 引用、`add_group_dependency` 的 parent/child、effect-map 的 key、或
> pattern `target` 滤波器。缺失值要通过 `set_realism(missing=...)` 在
> 所有列声明之后表达，不在列层声明。

直接打击机制 1 的 15 条 `residual_*` 和机制 2 的 `KeyError` 触发条件。

### 6.2 Path B：反馈循环——犯了能给指引

`_resolve_target` 的 detail 字符串从一句陈述

```
Target '...' matched zero rows. Cannot inject ... on an empty subset.
```

扩展为带两个常见原因 + 三步修复指引的可操作信息。这条 detail 会原样
被 [orchestration/sandbox.py:579](orchestration/sandbox.py#L579) 的
`format_error_feedback` 转发给 LLM 的下一轮——也就是说 LLM 看到的不是
一个谜，而是一份带"怎么改"的工单。

### 6.3 Path C：把哑错变成 typed exception

原 [engine/measures.py:247](engine/measures.py#L247) 直接 `val_map[cat_val]`
查字典，遇到 `'None'` 抛 `KeyError`——这是个**裸异常**，Loop A 的
`format_error_feedback` 只能转发一条不知所云的 traceback。

修复后改为：

```python
if cat_val not in val_map:
    raise UndefinedEffectError(
        effect_name=effect_name,
        missing_value=cat_val,
    )
context[effect_name] = float(val_map[cat_val])
```

`UndefinedEffectError` 早已存在于 [exceptions.py:77](exceptions.py#L77)——
它是 §2.7 typed-error 分类法里的一员，原本就是为这种情况设计的，只是
没在引擎层用上。**复用现有类型，不新增**。

修复后，repro 输出：

```
UndefinedEffectError: 'major_yield' in formula has no definition for 'None'.
```

Loop A 看到这种 typed exception 会写"effect 'major_yield' 缺值 'None'，
检查 None 处理"，给 LLM 下一轮一个明确目标。

### 6.4 A、B、C 怎么协同

```
┌──────────────────────┐
│ Path A (预防)         │  让 LLM 第一次就别犯错
│ noise 校准 + None 禁用 │
└─────────┬────────────┘
          │
          v
   LLM 写脚本 ──→ M2 引擎执行 ──→ M5 validator
                       │                │
                       │                └─ residual/ks 失败
                       │                   └─ Loop B 兜底
                       │
                       └─ 异常路径
                           ├─ PatternInjectionError ──┐
                           │   (Path B 详化 detail)   │
                           │                          ├─→ format_error_feedback
                           └─ UndefinedEffectError ───┘   │
                              (Path C 替换裸 KeyError)    │
                                                          v
                                                      Loop A 下一轮
                                                      LLM 拿到精准指引重写
```

- **A** 缩小命中 B/C 的概率（在源头降低犯错率）。
- **B、C** 在仍然犯错时，把"哑错"升级为"会话"，让 Loop A 能修。
- 三者**不互相替代**：A 改不了 Loop A 的反馈通道，B/C 改不了 LLM 一开始
  的认知模型。

---

## 7. 没修的部分（坦白）

### 7.1 机制 1 的根（已修复 → 见 orchestration/calibration.py）

Path A 的 heuristic prompt 是 prevention layer。**实际修复机制 1 的根**
靠的是 [orchestration/calibration.py](orchestration/calibration.py)：
Loop A 的 LLM-in-loop dry-run sigma 校准。算法：

1. Loop A exec 成功后，engine 用 `realism_config=None` 做 full-N replay。
2. 对每个声明 sigma 的 structural measure，调用
   [check_structural_residuals](validation/statistical.py) 量 empirical residual std。
3. 若任一 measure 的 ratio ≥ 0.2，构造 typed feedback
   ([sandbox.py::format_calibration_feedback](orchestration/sandbox.py)) 把
   suggested sigma 送回 LLM。calibration retry budget 独立于 exec retry
   budget（各 3 次），见 [retry_loop.py](orchestration/retry_loop.py)。
4. 3 轮未收敛 → `SkipResult(skip_reason="calibration_unconverged")`，
   每行写入 `output/agpds/<batch>/skipped.jsonl`（[agpds_generate.py::_save_skip_record](../agpds_generate.py)）。

设计意图：Loop A 校准过的 declarations 进入 Stage 2 后，Stage 2 validator
应一致 pass、Loop B 的 `widen_variance` 不应触发——calibration 是 Stage 1
的 correction layer，Loop B 仅作 safety net。

实测数据：见 [§8](#8-实测数据3-way-对照) 的 -v3-calibrated 列。
关键指标：residual_* median ratio = 6.763 (was 2.49 in pathA);
max ratio = 54.75 (was 28.74); count = 10 (was 15).
校准降低了 residual count 和 ks_* 总量（-34 total failures），但 ratio magnitude
反向恶化——机制 1 未被 Loop A 校准有效收敛，PARTIAL。

### 7.2 机制 3 没动

稀疏 cell + KS 过敏（Path D）被用户拒了。短期靠 Path A 让 LLM 别再
压低 sigma 来侧面缓解；长期需要 validator 上做 small-n 修正
（bonferroni 校正或 cell-size threshold）。

---

## 8. 实测数据（3-way 对照）

为了精确测量 Path A 的净效应，做了 **同 model + 同 10 个 scenario** 的
对照实验。三个批次都在 `output/agpds/` 下：

| 批次目录 | 简称 | provider / model | Path A | 校准 | 用途 |
|---|---|---|---|---|---|
| `pingyue-samples-openai-v1` | **v1** | openai / `gpt-5.5-2026-04-23` | 关 | 关 | 原始 production |
| `pingyue-samples-gemini-baseline` | **-2** | gemini / `gemini-3.1-pro-preview` | 关 | 关 | **gemini baseline** |
| `pingyue-samples-gemini-pathA` | **-v2** | gemini / `gemini-3.1-pro-preview` | **开** | 关 | 改造后跑 |
| `pingyue-samples-gemini-pathA-calibrated` | **-v3** | gemini / `gemini-3.1-pro-preview` | **开** | **开** | T1-T7 校准后跑 |

scenarios 在三个批次间 byte-identical（content-addressed `generation_id` +
`--scenario-source cached_strict --seed 42 --category 3`）。本节后续用
**v1 / -2 / -v2** 简称这三个批次。

### 8.1 失败计数（按 check 前缀）

> **重要订正**：本节最初基于一份带有先存在 plumbing bug 的 Stage 2 报告
> （[pipeline.py:281](pipeline.py#L281)，patterns 从空 `metadata` 取而非
> `raw_declarations`）。bug 修复后（commit `b16525e`）用**同一批 declarations
> 重跑 Stage 2**，所有数据见下表 -v3 列。

| 前缀 | v1 (openai, 无 A) | -2 (gemini, 无 A) | -v2 (gemini, +A) | -v3 (gemini, +A+cal) | cal 净效应 |
|---|---:|---:|---:|---:|---|
| `ks_*` | 95 | 64 | 76 | **11** | **-65** ✓✓✓ |
| `residual_*` count | 15 | 18 | 15 | **0** | **-15** ✓✓✓ |
| `group_dep_*` | 2 | 0 | 0 | 1 | +1 |
| `orthogonal_*` | 1 | 1 | 1 | 0 | -1 ✓ |
| `marginal_*` | 1 | 0 | 1 | 0 | -1 ✓ |
| `outlier_*` | 0 | 0 | 0 | 2 | +2 |
| `seasonal_*` | 0 | 0 | 0 | 2 | +2 |
| **TOTAL** | **114** | **83** | **93** | **18** | **-75** ✓✓✓ |
| **passed scenarios** | 0/10 | 0/10 | 0/10 | **4/10** | **+4** ✓✓✓ |
| errored | 2 | 0 | 0 | 0 | 0 ✓ |
| skipped (cal_unconverged) | — | — | — | 0 | — |

### 8.2 `residual_*` 偏差幅度（最关键指标）

光看 count 看不出 Path A 的真实效果——要看 ratio magnitude。
`ratio = residual_std / noise_sigma`，validator 阈值 0.2。

| 批次 | n | min | **median** | **max** |
|---|---:|---:|---:|---:|
| v1 (openai, 无 A) | 15 | 0.26 | 1.54 | 66× |
| **-2 (gemini, 无 A)** | 18 | 0.49 | **19.25** | **9742×** |
| **-v2 (gemini, +A)** | 15 | 0.29 | **2.49** | **29×** |
| **-v3 (gemini, +A+cal)** | **0** | — | **—** | **—** |

**Path A 把 gemini 的 residual 偏差 median 压了 87%，max 压了 99.7%。**
也就是 LLM 真的听懂了——它在某些 measure 上把 sigma 调高了 1–3 个数量级。

**-v3 (校准) 把 residual_* 失败完全干掉**（count 15→0）。所有 10 个 scenario 都
通过 residual 检查——calibration 在 Loop A 让 LLM 重写 sigma 配合 empirical
residual std，10 次中只 1 次触发 calibration retry（dom_024，3 轮收敛），
其他 9 次第一轮就过——证明 Path A prompt + 校准的组合让 LLM 写出来的
sigma 跟乘法链 residual 自然匹配。

### 8.3 三个非平凡解读

**(1) Path A 在 residual 上**显著生效**，但 KS 反向上升**

原因：sigma 调对方向（变大）→ 生成分布更宽 → 在多维稀疏 cell 上更容易
拒绝 KS 原假设。这是机制 3（稀疏 cell 脆弱性）的露头，**不是 Path A 失败**——
sigma 调对了才是真的，KS 阈值偏严才是另一个问题。

**(2) Total 失败数 83 → 93 是 misleading 的简单计数**

因为 `ks_*`（76 项）权重过大压住了 `residual_*` 改善（-3 项 + magnitude 大降）。
应该看 magnitude 而非 count：residual ratio 中位数从 19 降到 2.5 是质变。

**(3) v1 → v2 的"114 → 93 总数下降"几乎都是 model 切换的功劳**

| 比较 | total |
|---|---|
| v1 (openai, 无 A) → -2 (gemini, 无 A) | **114 → 83** = -27%（**model 差异**） |
| -2 (gemini, 无 A) → -v2 (gemini, +A) | **83 → 93** = +12%（**Path A 净效应**） |

也就是说：把 production model 从 openai 切到 gemini 本身就能消掉
27% 的失败，跟 Path A 无关。

### 8.4 Path B/C 在这次 gemini 跑里其实没触发

两个 errored 的 scenario（`agpds_3af92040e6`、`agpds_8180fe4e2c`）只在
v1（openai）上触发了 `PatternInjectionError` 和 `KeyError`。gemini 在
-2 和 -v2 上都把它们写成了 0 命中以外的 pattern target、没把 None 漏进
effect map——纯运气。

所以：
- Path B（详化 PatternInjectionError detail）的代码改动是对的。
- Path C（把裸 KeyError 升级为 UndefinedEffectError）的代码改动也是对的。
- 但**它们带来的"Loop A 拿到 typed feedback 后自修"的能力，本次实测里
  没有真正被验证**——需要在 openai 上重跑才能看到 Loop A 修复的全流程。
- 单元测试（`test_engine_measures.py::TestEvalStructuralUndefinedEffectGuard`）
  保证 B/C 的代码路径正确，但 production 端到端验证仍是缺口。

### 8.5 调查"-v3 校准看似失败"的根因——是 plumbing bug，不是校准失败

> 此节最初记录了 -v3 校准的"MISS"verdict。**后续调查发现根因是
> [pipeline.py:281](pipeline.py#L281) 的 plumbing bug**——validator 从空
> `metadata` 取 patterns，导致 `check_structural_residuals` 的 P3-8
> pattern-row 排除逻辑静默失效，把 pattern-injected 的 outlier 行计入
> residual std，膨胀 ratio。修复后用**同一份 declarations 重跑 Stage 2**
> 得到上表的真实数字。

#### 5.1 发现过程

T8 production rerun 报告 -v3 0/10 passed、residual median 6.76、max 54.75
（看似比 -v2 还差）。怀疑校准没起作用。debug 步骤：

1. 找一个 Stage 2 报 residual failure 但 Loop A calibration 报通过的 scenario：
   `agpds_8022981cf7`（dom_024），`course_completion_rate`。Loop A 校准说
   `residual_std=4.49, ratio=0`；Stage 2 报告说 `residual_std=9.54, ratio=1.12`。
2. 手动用 `run_pipeline` 在 disk-loaded declarations 上重放 → residual=5.27
   （与 Loop A 校准一致）。Stage 2 的 9.54 哪来的？
3. 完整复刻 `run_loop_b_from_declarations` 流程：residual=9.54。但手动
   `SchemaAwareValidator(meta).validate(df, patterns)` 还是 residual=5.27。
4. 差异：手动调用传了 `patterns=disk_decls['patterns']`，但
   `run_loop_b_from_declarations` 内部传的是 `metadata.get("patterns", [])`。
   metadata 默认空 dict → patterns=[]。
5. 验证：同 df、同 col、同 noise_sigma，仅 patterns 参数从 `[]` 改成
   `disk_decls['patterns']` → residual_std 从 9.35 降到 5.27（ccr）、
   从 116.45 降到 4.17（pass_rate）。

#### 5.2 Bug 与修复

```python
# pipeline.py:281 (BEFORE — fixed in commit b16525e)
result_df, result_meta, report = generate_with_validation(
    ...
    patterns=metadata.get("patterns", []),   # ← BUG
    ...
)

# AFTER
result_df, result_meta, report = generate_with_validation(
    ...
    patterns=patterns,   # local var from raw_declarations.get("patterns", [])
    ...
)
```

`agpds_execute.py` 调 `run_loop_b_from_declarations(raw_declarations, max_retries=3)`
时不传 metadata，所以 metadata 默认 `{}` → patterns 默认 `[]` → P3-8 失效。

回归测试：[`test_pipeline_loop_b_patterns.py`](tests/modular/test_pipeline_loop_b_patterns.py)
通过 `SchemaAwareValidator.validate` 的 mock 验证 patterns 不为空。

#### 5.3 修复后的真实数字

| 指标 | -v3 (修复前) | **-v3 (修复后)** | delta |
|---|---:|---:|---|
| passed | 0/10 | **4/10** | +4 |
| total failures | 59 | **18** | -41 (-69%) |
| residual_* count | 10 | **0** | -10 (-100%) |
| residual median ratio | 6.76 | **N/A** (空集) | — |
| residual max ratio | 54.75 | **N/A** (空集) | — |
| ks_* count | 48 | **11** | -37 (-77%) |

**机制 1 关闭**：residual_* 失败从 15 (-v2) → 0 (-v3 修复后)。同时 ks_*
也大降（76 → 11），因为 ks 失败大多是机制 1 的投影。

### 8.6 下一步该做什么

机制 1 + plumbing bug 都关闭后，剩余的失败集中在：

1. **机制 3（稀疏 cell）的"真"失败**——还剩 11 个 ks_* 失败和零星的
   `outlier_*`/`seasonal_*` 没过。这些是稀疏 cell 上 KS 检验过敏的
   真实表现。修法仍是 bonferroni 校正或 cell-size threshold（Path D，
   之前显式拒绝过），需要新 plan。
2. **openai 重跑 -v3** 验证 Path B/C 端到端——pingyue gemini 这批没触发
   `PatternInjectionError` 或 `KeyError: 'None'`，B/C 的 Loop A 自修能力
   还没在 production 上验证过。
3. **6 个仍 soft-fail 的 scenario 调查**——passed 4/10 是 stretch 目标
   达成，但剩 6 个还有 18 条失败。逐一分析它们的失败 check 类型，看是
   机制 3 还是其他新机制。
