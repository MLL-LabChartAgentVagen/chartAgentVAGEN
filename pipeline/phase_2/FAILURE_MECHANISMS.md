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

### 7.1 机制 1 的根没动

Path A 加的是 heuristic——"sigma 应为 range 的 10–30%"——不是数学推导。
如果 LLM 设计了 5 个因子的乘法链，10–30% 仍然偏小。

**根治需要**：在 Loop A 加一个 "先 dry-run 生成 ~100 行预估方差" 的
self-check 步骤——让 LLM 在提交脚本前，用一小段 Python 自查一下乘积
的实际 std，并自动调 sigma。

这是下一个 plan 的事，本次 plan 显式 out-of-scope。

### 7.2 机制 3 没动

稀疏 cell + KS 过敏（Path D）被用户拒了。短期靠 Path A 让 LLM 别再
压低 sigma 来侧面缓解；长期需要 validator 上做 small-n 修正
（bonferroni 校正或 cell-size threshold）。

---

## 8. 实测数据（3-way 对照）

为了精确测量 Path A 的净效应，做了 **同 model + 同 10 个 scenario** 的
对照实验。三个批次都在 `output/agpds/` 下：

| 批次目录 | 简称 | provider / model | Path A | 用途 |
|---|---|---|---|---|
| `pingyue-samples-openai-v1` | **v1** | openai / `gpt-5.5-2026-04-23` | 关 | 原始 production |
| `pingyue-samples-gemini-baseline` | **-2** | gemini / `gemini-3.1-pro-preview` | 关 | **gemini baseline** |
| `pingyue-samples-gemini-pathA` | **-v2** | gemini / `gemini-3.1-pro-preview` | **开** | 改造后跑 |

scenarios 在三个批次间 byte-identical（content-addressed `generation_id` +
`--scenario-source cached_strict --seed 42 --category 3`）。本节后续用
**v1 / -2 / -v2** 简称这三个批次。

### 8.1 失败计数（按 check 前缀）

| 前缀 | v1 (openai, 无 A) | -2 (gemini, 无 A) | -v2 (gemini, +A) | Path A 净效应 |
|---|---:|---:|---:|---|
| `ks_*` | 95 | 64 | 76 | **+12** ⚠ |
| `residual_*` count | 15 | 18 | 15 | -3 ✓ |
| `group_dep_*` | 2 | 0 | 0 | = |
| `orthogonal_*` | 1 | 1 | 1 | = |
| `marginal_*` | 1 | 0 | 1 | +1 |
| **TOTAL** | **114** | **83** | **93** | +10 |
| errored | 2 | 0 | 0 | — |

### 8.2 `residual_*` 偏差幅度（最关键指标）

光看 count 看不出 Path A 的真实效果——要看 ratio magnitude。
`ratio = (residual_std - declared_sigma) / declared_sigma`，validator
阈值 0.2。

| 批次 | n | min | **median** | **max** |
|---|---:|---:|---:|---:|
| v1 (openai, 无 A) | 15 | 0.26 | 1.54 | 66× |
| **-2 (gemini, 无 A)** | 18 | 0.49 | **19.25** | **9742×** |
| **-v2 (gemini, +A)** | 15 | 0.29 | **2.49** | **29×** |

**Path A 把 gemini 的 residual 偏差 median 压了 87%，max 压了 99.7%。**
也就是 LLM 真的听懂了——它在某些 measure 上把 sigma 调高了 1–3 个数量级。

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

### 8.5 下一步该做什么

按收益排序：

1. **§7.1 dry-run sigma 校准**——Path A 把 residual median 压到 2.5×，
   但 validator 阈值 0.2 还要再降一个量级。heuristic prompt 已到极限；
   必须让 LLM 写完后跑 ~100 行 self-check 自调 sigma。
2. **openai 重跑 v3** 验证 Path B/C 端到端——故意触发 zero-row pattern
   或缺 effect key 的 scenario，看 Loop A 能否拿 typed feedback 修。
3. **机制 3 修复**——bonferroni 校正或 cell-size threshold，让 KS 检验
   不在 n<30 的稀疏 cell 上轻易报警。Path A 把 sigma 调对反而暴露了这个
   问题更严重。
