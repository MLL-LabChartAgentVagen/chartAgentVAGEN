# Stub 缺口分析 —— 对抗式审阅

## 总体结论

该分析整体准确、范围合理 —— 10 个 stub 中有 9 个的行号和代码片段与当前源码一致,IS-1↔DS-3 与 DS-2↔IS-2/3/4 之间的依赖关系也判断正确。但有两个值得注意的非琐碎问题:(1) **IS-5 编造了规范语义**(声称是 "log/linear scaling 提示"),而 `phase_2.md` §2.1.1 中并无此说法;并将该状况描述为 "三方漂移",但实际上规范对 `scale` 几乎没有任何内容;(2) **DS-1 漏掉了一处横切性发现** —— `censoring=` 关键字参数已从**实时 prompt** ([prompt.py:70](pipeline/phase_2/orchestration/prompt.py#L70)) 中移除,因此 censoring 现在与 DS-2 中那 4 个延期的 pattern 完全相同地被 "双重屏蔽",但分析却仅作为单一 stub 来处理。此外还有少量行号 / 文件引用上的小错。**整体:** 2 个 stub 有重大问题、3 个有小问题、5 个干净。

---

## 逐 stub 评审

### [IS-1] 混合分布采样

**结论:** 有小问题

#### 发现的问题
1. **代码位置准确性** —— 已核实:stub 位于 [engine/measures.py:360-366](pipeline/phase_2/engine/measures.py#L360-L366),分析中关于 "与 CLAUDE.md 行号漂移" 的说法正确。
2. **方案 —— sub_meta 构造** —— 在 `_sample_mixture` 草图中,`sub_meta = {"family": comp["family"], "param_model": comp["param_model"]}` 这一行悄悄丢掉了 `_compute_per_row_params` 可能依赖的 `"measure_type": "stochastic"` 键。未必是 bug(取决于 `_compute_per_row_params` 如何读取参数),但实施时值得提醒。
   - **证据:** [engine/measures.py:376-378](pipeline/phase_2/engine/measures.py#L376-L378) 表明 `_compute_per_row_params(col_name, col_meta, rows, n_rows, overrides)` 是用**完整的** col_meta 字典调用的;分析师构造的子 spec 字典键更少。
   - **影响:** 实现时必须验证 `_compute_per_row_params` 不依赖 col_meta 中的 `measure_type` 或 `name`,或将 sub_meta 构造得与之匹配。
3. **架构层面 —— 与 auto-fix 的交互** —— 该方案未讨论 `widen_variance`(现有的 `ks_*` 自动修复策略)在混合分布上应如何工作。混合分布没有单一的 `sigma` 可以放大 —— 每个分量都有自己的 sigma。分析仅在 DS-3 中隐晦地提到一句("`AUTO_FIX` 有 `ks_*` 策略,但对 mixture 不自然适用"),却未在 IS-1 实施计划中考虑这一点。
   - **证据:** [validation/autofix.py](pipeline/phase_2/validation/autofix.py) —— `widen_variance` 索引单一 `sigma`;混合分布需要按分量处理或选择性退出。
   - **影响:** 一旦把 autofix 路径也算进来,联合实现 IS-1 + DS-3 + autofix 混合支持的工作面要比 "Medium (80–200 LOC)" 估计的更大。

---

### [IS-2] Dominance shift 校验

**结论:** 干净

未发现问题。代码位置 [pattern_checks.py:189-213](pipeline/phase_2/validation/pattern_checks.py#L189-L213) 已核实;规范引用(§2.1.2 L127、§2.5 L305、§2.9 L672-674)均逐字核实。"按时间切分点的实体排名变化" 这一解读与代码内 TODO 以及现有 `check_trend_break` 类比最一致。建议规模(~110 LOC)与现有 `check_trend_break` 类比一致。

---

### [IS-3] Convergence 校验

**结论:** 干净

代码位置 [pattern_checks.py:216-239](pipeline/phase_2/validation/pattern_checks.py#L216-L239) 已核实。 "在所有 stub 中规范覆盖最薄" 的说法与 `phase_2.md` §2.9 实际内容相符 —— `convergence` 只出现在 `PATTERN_TYPES` (L127) 和 prompt 列表 (L305) 中,任何位置都没有 L3 校验草图。建议规模和类比对象 (`check_ranking_reversal`) 合理。

---

### [IS-4] Seasonal anomaly 校验

**结论:** 干净

代码位置 [pattern_checks.py:242-265](pipeline/phase_2/validation/pattern_checks.py#L242-L265) 已核实。规范覆盖判断正确 —— 只有类型名称的列举,没有 L3 算法。窗口对照基线的 z-score 解读合理;类比对象 (`check_outlier_entity`) 适当。

---

### [IS-5] `add_measure` 的 `scale` 关键字参数

**结论:** 有重大问题

#### 发现的问题
1. **虚假规范缺口 —— 编造的语义** —— "Spec references" 段落声称:
   > §2.1.1 (L51–70):规定 `add_measure(name, family, param_model, scale=None)` 签名;`scale` 被记录为 log/linear 缩放的提示。

   "被记录为 log/linear 缩放的提示" 这一说法**根本不在规范中**。§2.1.1 L51 在签名行中给出 `scale=None`,后跟散文 "Stochastic root measure. Sampled from a named distribution. Parameters may vary by categorical context, but the measure does **not** depend on any other measure" —— 在规范任何地方都没有进一步说明 `scale=` 的含义。
   - **证据:** 直接 grep —— `scale` 只在 [phase_2.md:51](pipeline/phase_2/docs/artifacts/phase_2.md#L51)(签名行)和 [phase_2.md:287](pipeline/phase_2/docs/artifacts/phase_2.md#L287)(prompt 模板的签名)出现。任何位置都没有解释 `scale` 的散文。
   - **影响:** "Blocking question" 中的 `(a) per-family enum hint specifying parameter interpretation (scale="log" → mu is log-scale; scale="linear" → mu is on natural scale)` 是一个**虚构的**解读,而不是对规范的阅读。Phase B 中 "spec / prompt / SDK 三方漂移" 的描述夸大了规范内容 —— 规范并未对 `scale` 提出任何**主张**,只是在签名中列出该 kwarg 而无任何语义。这更接近于规范中的 "幽灵 kwarg",而不是相互冲突的主张。

2. **代码位置行号 —— prompt.py 不准确** —— 分析师写作 `pipeline/phase_2/orchestration/prompt.py:50-54` 并仅引用 `sim.add_measure(name, family, param_model)` 一行。实际文件:
   - L50-52:关于 `add_temporal` 的 `freq` 与 `derive` 的注释(与 `scale` 无关)。
   - L53:`# TODO [M?-NC-scale]: re-add scale=None kwarg ...`
   - L54:`"  sim.add_measure(name, family, param_model)\n"`
   - **证据:** [orchestration/prompt.py:50-54](pipeline/phase_2/orchestration/prompt.py#L50-L54) —— 只有 L53-54 与 scale 相关。
   - **影响:** 引用区间偏差 3 行;实际相关的 TODO+签名位于 L53-54,而非 L50-54。改起来很容易,但作为分析文档中的权威指针有误导性。

3. **建议正确性(附带保留)** —— "不要恢复该 kwarg" 在规范无内容的状态下是正确的判断。但建议把 "修正 spec/prompt 漂移" 与 "从 spec 中删除 `scale`" 混为一谈。鉴于规范从未对 `scale` 做出任何行为主张,从规范中删掉它当然是不错的第一步 —— 但分析应明确说明:由于规范从未声明 `scale` 的作用,删除它没有任何损失。

---

### [IS-6] M3 多错误 + token 预算

**结论:** 干净

#### 发现的问题
1. **代码位置 —— sandbox.py 引用** —— 分析师写作 `phase_2/orchestration/sandbox.py:~657`,括号说明 "Sandbox attempt loop"。已核实:[sandbox.py:649-680](pipeline/phase_2/orchestration/sandbox.py#L649-L680) 包含描述算法的 `run_retry_loop` docstring,实际重试循环体则位于该函数其余部分。鉴于这是 "能力缺失" 而非 stub raise,使用 `~` 记法是合适的。无需更正。

"两个独立子特性"(多错误收集 + token 预算)的描述正确;LOC 估计(合计约 340)与所列接触面一致。

---

### [DS-1] Censoring 注入

**结论:** 有重大问题

#### 发现的问题
1. **遗漏的依赖 —— prompt 侧屏蔽** —— 分析将 DS-1 视为 "engine 抛 NotImplementedError、SDK 接受 kwarg" —— 但**实时 LLM prompt 也已被更新以省略 `censoring=`**。位于 [orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71) 的 prompt 是:
   ```python
   # TODO [M1-NC-7]: censoring kwarg deferred — re-add when engine/realism.py supports it.
   "  sim.set_realism(missing_rate, dirty_rate)    # optional\n"
   ```
   这与分析师正确识别出的 DS-2 模式("4 个延期 pattern 既被 SDK 屏蔽又被 prompt 省略")是**完全相同的 "双重屏蔽" 模式** —— 但 DS-1 条目并未提及。
   - **证据:** [orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71);对照同一分析师在 DS-2 中正确指出的类似行为(`prompt.py:72`)。
   - **影响:** DS-1 的依赖链低估了恢复成本:让 censoring 重回不只是 (a) 定义 schema + (b) 实现 engine —— 还需要 (c) 在 prompt 中重新宣告该 kwarg + (d) 更新 One-Shot 示例。分析师所引用的 stage5 文档甚至提到 "scale was removed in same advertising-a-nonfeature class as `censoring=`" —— 即仓库内部对该模式有所认知,但 DS-1 分析本身并未浮现这一点。

2. **规范引用准确性** —— "§2.1.2 (L129)" 已核实 —— `set_realism(missing_rate, dirty_rate, censoring)` 位于 [phase_2.md:129](pipeline/phase_2/docs/artifacts/phase_2.md#L129)。✓

3. **架构层面 —— 建议的 marker 语义** —— 建议的 `(a) per-column dict, marker (a) NaN replacement` 方案合理,但会丢失 censoring 信息,影响下游 Phase 3 的视图抽取。分析在 "Blocking questions" 中确实标记了这一点,但随后在 "Proposed solution" 中悄悄选了 NaN 替换而未重新权衡。一个独立的 `<col>_censored` 指示列(分析师自己列出的选项 b)对 Phase 3 而言是更安全的默认。
   - **影响:** Phase 3 的视图抽取可能需要区分 "缺失" 与 "截断",仅用 NaN 标记会抹掉这一信号 —— 关于 Phase 3 的影响应进入依赖链,而不仅停留在 blocking-questions 列表中。

---

### [DS-2] 4 种 pattern 类型注入

**结论:** 有小问题

#### 发现的问题
1. **`inject_ranking_reversal` 算法 —— 与校验器不匹配的风险** —— 提议草图:
   ```python
   sorted_by_m1 = df.loc[target_idx, m1].sort_values().index
   m2_descending = sorted(df.loc[target_idx, m2], reverse=True)
   df.loc[sorted_by_m1, m2] = m2_descending
   ```
   把 m1 高的**行**与 m2 低的值配对。但校验器(`check_ranking_reversal`,镜像自规范 §2.9 L655-661)按实体分组、取分组均值,然后检查均值的秩相关。
   - **证据:** [phase_2.md:655-661](pipeline/phase_2/docs/artifacts/phase_2.md#L655-L661) —— 校验器是 `means[m1].rank().corr(means[m2].rank()) < 0`,在实体级均值上计算。
   - **影响:** 行级反相关并不必然产生分组均值的秩反转。如果各实体的 m1 分布相似,逐行的反转在分组均值层面可能会相互抵消。注入器应当在实体均值粒度上工作(例如:对 m1 高的实体把 m2 缩小,对 m1 低的实体把 m2 放大)才能可靠触发校验器。这条警示应放在方案的注意事项中。

2. **代码位置已核实** —— [engine/patterns.py:61-71](pipeline/phase_2/engine/patterns.py#L61-L71) 已确认。elif 元组中列出的 pattern 类型与分析师的引用一致。✓

3. **`VALID_PATTERN_TYPES` 位置已核实** —— [sdk/relationships.py:29-31](pipeline/phase_2/sdk/relationships.py#L29-L31) 是 `frozenset({"outlier_entity", "trend_break"})`,验证了 "双重屏蔽" 主张。✓

4. **规范 L656-661 引用(差一)** —— 分析师在引用 ranking_reversal 校验器时写作 "§2.9 L656-661";实际范围是 L655-661(`elif` 行在 L655,而不是 L656)。极小问题。

---

### [DS-3] 混合分布 KS 检验

**结论:** 有小问题

#### 发现的问题
1. **`_expected_cdf` 行号引用不准确** —— 分析师写道:
   > `_expected_cdf(family="mixture", params)` at `validation/statistical.py:165` returns `None`

   查看实际 [statistical.py:130-166](pipeline/phase_2/validation/statistical.py#L130-L166):`_expected_cdf` 对 gaussian、lognormal、exponential、gamma、beta、uniform 显式分支(L143-162),并在 L163-165 为 poisson 分支返回 None。**没有显式的 `mixture` 分支**。该函数对任何无法识别的 family(包括 mixture)在 L166 通过 fallthrough 返回 None。所以 "对 mixture 返回 None" 在技术上正确(经由 fallthrough),但所引用的行(L165)是 poisson 分支 —— 引用错误。
   - **证据:** [validation/statistical.py:163-166](pipeline/phase_2/validation/statistical.py#L163-L166)。
   - **影响:** 仅是表面问题,但日后照行号查找的实现者会落到 poisson 处理而非真正的 fallthrough 位置。

2. **建议的 `_MixtureFrozen` 适配器 —— scipy 兼容警告** —— `scipy.stats.kstest` 接受可调用的 `cdf` 实参,因此只暴露 `.cdf()` 的对象**只要**以 `kstest(sample, dist.cdf)` 方式调用即可使用(现有代码在 [statistical.py:296](pipeline/phase_2/validation/statistical.py#L296) 正是这样做的)。建议草图与该调用约定兼容。

---

### [DS-4] 多列 group dependency `on`

**结论:** 干净

代码位置 [sdk/relationships.py:123-132](pipeline/phase_2/sdk/relationships.py#L123-L132) 已核实。规范覆盖判断正确 —— §2.1.2 L106-117 将 `on` 声明为列表(隐含多列),但未给出嵌套权重 schema。提议的 "嵌套字典 + 完整笛卡尔覆盖" schema 是对现有单列规则(镜像自 [relationships.py:166-200](pipeline/phase_2/sdk/relationships.py#L166-L200))的自然扩展。

基数膨胀(5×4×3 → 60 个内层字典)的担忧是真实的,但被正确地识别为 LLM 侧问题,而非代码侧问题。

---

## 横切性发现

1. **"双重屏蔽" 模式被低估。** 分析正确识别了 DS-2(4 个 pattern)的 "SDK 屏蔽 + prompt 省略" 模式。同样的模式适用于 **DS-1 (censoring)** 与 **IS-5 (`scale`)** —— 这三者现在都被防御性地从实时 prompt 中移除。只有 DS-2 条目把 prompt 侧屏蔽作为依赖链中一等事实呈现。DS-1 的 prompt 移除在其分析中不可见;IS-5 的 prompt 移除虽被承认,但被框定为 "三方漂移" 的一部分,而不是同一防御性模式的体现。
   - **建议:** 增加一条跨 stub 注记,说明该项目对未实现的 LLM-facing 参数有一致的 "absent + TypeError + prompt-omitted" 模式,且 IS-5、DS-1、DS-2 三者都遵循之。

2. **"10 个里 8 个被规范阻塞" 的说法有所夸大。** Phase B 概要称 "Spec gaps dominate over code gaps. 8 of 10 stubs are blocked at least partially by missing spec definitions." 然而:
   - **IS-6**(多错误 / token 预算)被明确标注为操作性事项,而非 spec 特性 —— 它**并非**被规范阻塞。
   - **DS-2 的 `ranking_reversal` 注入器** 的契约可由现有校验器(已在规范 §2.9 L655-661 中)推导 —— 严格说不被规范阻塞。

   因此更诚实的计数是 10 个里有 6-7 个被规范阻塞。问题不致命,但该说法夸大了对规范扩展的明显依赖。

3. **IS-1 中的规范行号漂移。** 分析师指出了一处漂移(CLAUDE.md 中 `~L297-303` → 实际 L360-366)。他们没有检查同样的漂移是否出现在别处 —— 例如 stage5 anatomy summary 自身日期为 2026-04-22,可能存在其它过时行号引用。值得用一句话说明这更可能是系统性问题,而非 IS-1 特有。

4. **`set_realism(censoring=)` 的 SDK 侧暴露。** [relationships.py:281](pipeline/phase_2/sdk/relationships.py#L281) 证实 `set_realism` 仍接受 `censoring=None`。分析师的说法 "sdk/relationships.py::set_realism already accepts censoring" 正确。但由于 prompt 不再记录它(横切发现 #1),在常规 LLM 驱动流程中该 kwarg 实际上不可达。DS-1 依赖链应注明这种不对称。

5. **测试覆盖 "(none found)" 的说法对部分 stub 未独立核实。** 抽查 IS-5:[test_sdk_columns.py:130-157](pipeline/phase_2/tests/modular/test_sdk_columns.py#L130-L157) 同时存在 `test_add_stochastic_measure`(L130)与 `test_add_measure_rejects_scale_kwarg`(L145)。对其它 stub,"(none found)" 的说法听上去合理但审阅者未做穷尽核实;若要把分析作为测试覆盖断言的依据,值得后续扫描。

---

## 建议

按严重程度排序,在把 `stub_gap_analysis.md` 用于实施前应做的修复:

1. **(高)重写 IS-5 spec 段。** 把 "documented as a hint for log/linear scaling" 替换为字面规范内容 —— "L51 在签名中列出 `scale=None`;§2.1.1 或其它任何位置都没有相关散文语义"。重写 blocking question,承认解读 (a) 不是对规范的*阅读*,而是*为其增加语义的提议*。"三方漂移" 的说法应改为 "spec/prompt/SDK 已统一为省略,但规范仍残留一行有名无实的签名"。

2. **(高)在 DS-1 中加上 prompt 侧屏蔽。** DS-1 条目应明确指出 `prompt.py:70-71` 不再向 LLM 宣告 `censoring=`,并将其加入 "Role in pipeline" 与 "Dependency chain — Co-dependent with"。恢复成本应从 "实现 engine + 定义 schema" 增长为 "实现 engine + 定义 schema + 在 prompt 中重新宣告 + 更新 One-Shot 示例"。

3. **(中)细化 DS-2 中的 `inject_ranking_reversal` 方案。** 当前草图按行级别操作;校验器按实体均值级别操作。要么 (a) 修订算法以缩放分组级均值,要么 (b) 明确指出行级反转是启发式做法,可能并不总能触发校验器,基于实体级别的更直接方法更可靠。

4. **(中)添加关于 "双重屏蔽" 防御模式的横切说明。** 一段 3 行的横切段落,把 IS-5、DS-1、DS-2 命名为同一 SDK + prompt 移除模式的实例,可避免对它们分析方式上的不一致。

5. **(低)修正行号引用。**
   - IS-5:`prompt.py:50-54` → `prompt.py:53-54`。
   - DS-3:`validation/statistical.py:165` → `:166`(fallthrough,而不是 mixture 分支)。
   - DS-2:规范 `§2.9 L656-661` → `L655-661`(`elif` 行差一)。

6. **(低)在 Phase B 概要中弱化 "10 个里 8 个被规范阻塞" 的措辞。** 承认 IS-6(纯操作性)与 DS-2 的 `ranking_reversal` 注入器(可从校验器推导)是例外;诚实计数更接近 10 个里 6-7 个。

7. **(低)IS-1 增加关于 autofix 的实施警示。** 注明 `widen_variance`(`ks_*` autofix 策略)对混合分布并不自然适用 —— 实现 IS-1 + DS-3 还需要决定 autofix 的退出或按分量处理方式,这会扩大有效工作面。

只要修复 1-3 落地,stub gap 分析在根本上就是可靠的、可用于实施的。修复 4-7 属于打磨。
