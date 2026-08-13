# Research Direction Planning — 2026 中至 2027 上半年投稿窗口

> **目标**:基于 chart data generation pipeline,规划一篇 best paper 候选工作。
> **核心约束**:**chart understanding 已是 solved problem**——chart QA / captioning / 多图 chart reasoning 全部禁区。Pipeline 的价值只在它的**抽象底层结构**。

---

## TL;DR

1. **Pipeline 真正的 peer 不是 ChartQA,而是 Procgen / LeanDojo / TabPFN 合成 prior** —— 一个 procedurally-generated 的、带闭式 ground-truth 因果结构的 synthetic world,可拉任意 modality view + 任意复杂度 verifiable trace + 免费 counterfactual。
2. **Best paper 上限最高**:**Closed-Loop AI Scientist**(方向 ①)—— 第一个有 oracle 的科学发现 agent 环境。
3. **Program 衔接最强**:**Latent World Programs**(方向 ②)—— 把"恢复生成程序"作为 self-sup objective,本篇 chart proof,下一篇 spatial scene graph。
4. **High-variance backup**:**Reasoning Models Don't Reason**(方向 ③)—— audit frontier reasoning model 的 CoT 是否对应真实 latent reasoning。
5. **决策**:单 paper 投 **①**;PhD program 投 **②**;**③** 可并行作为 side-project。

---

## 重新解构:Pipeline 的本质(脱离 chart)

把 "chart" 从脑子里删掉,pipeline 实际产出的是:

> **一个 procedurally-generated 的、带闭式 ground-truth 因果结构的 synthetic world,可以从中拉出任意 modality 的 view + 任意复杂度的可验证 reasoning trace,并且可以做 counterfactual。**

它的真正 peer 是:

| 已有供给 | 性质 | 与本 pipeline 的关系 |
|---------|------|---------------------|
| Procgen / MiniGrid | procedural env | 你比它结构更丰富(DAG + 因果) |
| LeanDojo / Coq Gym | verifier-graded env | 你是 numerical 版本 |
| TabPFN 合成 prior | synthetic causal DGP | 你比它复杂度高一个数量级 |
| Sakana AI Scientist 实验台 | 虚拟科研环境 | **他们没有 ground truth,你有** |

**关键 insight**:你拥有的是 **"AI 科学发现的 ground-truth 沙盒"**。2026 找不到第二个供给——真实科学没有 oracle,toy 沙盒(CLEVR / bAbI)结构太简单。**chart 只是这个沙盒的一种 view**。

---

## 方向 ① :Closed-Loop AI Scientist ★ 单 paper 首选

**Claim**:Sakana AI Scientist、Stanford ROBIN、MLE-Bench、METR RE-Bench 等所有 AI scientist 工作的共同死穴是 **open-loop**——agent 提出假说没法被严格验证(真实科学没有 oracle)。你的 pipeline 是**业内第一个**能给 ground-truth 因果结构的沙盒。构造 **inverse pipeline**:agent 拿到观测(可以是表 / 图 / 文字摘要),必须重建 Master Table 的 DGP code,通过**主动请求 view**(drill-down / orthogonal slice / counterfactual intervention)逐步缩窄假说空间,最终输出可被 SDK functional-equivalence 验证的 simulator code。

### 为什么这不是 chart 任务

- 输入:**任意 modality 的 view**(chart 只是其一,可以全文本、全表格、混合)
- 输出:**生成式因果程序**,不是答案
- 任务结构:**hypothesis → experiment → refute / refine 的科学方法本身**
- chart 在这里和 numpy print 是同级的——只是一种 observation channel

### Why now(2026 中)

- 2025 一年 AI scientist 全员爆发(Sakana / Anthropic RE-Bench / METR / OpenAI Paperbench)
- 所有这些被 "如何验证 agent 真的发现了对的东西" 卡住
- 你是**第一个具备 oracle 的 scientific environment**

### Technical novelty

- **Active probing as RL**:agent 不是被动看数据,**主动选观察哪个 view**(reward = 信息增益)
- **DGP-equivalence verification**:不是 trace-match,而是 functional equivalence —— SDK 已能跑两份 code 比 distribution
- **Counterfactual prediction as eval**:训练时不给反事实;测试时让 agent 预测 "if effects[severity][Severe] *= 2 会怎样",对比 ground-truth 重新生成的结果 —— testing causal grasp 而非 surface match
- **Differential vs Sakana**:他们做 ML research papers(无 oracle);你做 statistical mechanism discovery(有 oracle)
- **Differential vs LLM4Causal**:他们只做 graph;你做 multi-modal observation → executable program

### Experiments

- **MVP**:GPT-5.5 / Claude Opus 4.x / Llama-4 / Qwen3 在 simple/medium/complex 三档 scenario 上的 DGP recovery 准确率
- **拉满**:RL 训小 model(Qwen3-7B + GRPO,reward = SDK functional equivalence);ablation: active vs passive probing;counterfactual transfer 到 holdout scenarios
- **真实数据迁移**:同一 agent 跑 sklearn / OpenML dataset,看能否 recover 已知 statistical effect(econ / epi 数据集)

### Risks

1. **DGP recovery 搜索空间爆炸,agent 退化成记忆模板** → testset 必须在 Phase 0 sub-topic level 完全 holdout
2. **"真实科学没有 oracle" 的迁移性质疑** → 必须补真实数据 case study(已知 effect recovery)
3. **Sakana / METR 跟进快** → first-mover 窗口约 6–8 个月
4. **DGP equivalence metric 设计是地狱级** → 小样本 distribution test noisy,可能影响所有结论

**Best paper 潜力**:**9/10**

---

## 方向 ② :Latent World Programs ★ Program 衔接首选

**Claim**:目前 multimodal foundation model 的 objective 都是 **判别(VQA)** / **续写(captioning)** / **对比(CLIP)**。这些 objective 训出的模型对**世界的因果结构**没有 representation。提出新 self-supervised objective:**given any observation, output the executable program that could have generated it**。Pipeline 是该 objective 的**唯一可大规模 ground-truth 供给**。

### 为什么这不是 chart 任务

- objective 是 **observation → executable program**,通用于任何"程序生成的世界"
- 长程价值:scene graph、3D 场景、molecular structure、physics simulation 都是"程序生成的"——这条 objective 通用
- chart 只是 Phase 1 的训练 substrate,paper 核心 contribution 是 objective 本身

### Why now

- 2024–2025 generative pre-training(Sora / Genie 2 / V-JEPA-2)爆发,但 generation ≠ understanding 这个 question 没人系统回答
- DeepMind 2025 Genie 2 暗示"生成即理解"是 promising 但缺 rigorous 证据
- 你能提供 ground-truth program 比对 —— **唯一严谨工具**

### Technical novelty

- **新 objective**:program-recovery as pre-training(类比 MAE 但 target 是 code 不是 pixel)
- **Functional equivalence loss**:不是 token-level match(code 有多种等价写法),而是 functional output match through executor —— program synthesis 社区标准,**几乎没人用在 multimodal pretraining**
- **Probe transfer**:pre-train 后测试在
  - (a) 标准 VLM benchmark —— generation objective 是否帮判别
  - (b) **OOD program inversion** —— 未见过的 program 模板能否 recover
  - (c) **spatial scene → scene-graph** transfer —— **直接挂钩 spatial 主线**

### Experiments

- **MVP**:Qwen2-VL-7B 加 program-recovery head,用 pipeline 输出的 (view, SDK code) pair 训
- **拉满**:对比 baseline = SFT-on-VQA-only / SFT-on-caption-only / contrastive,看 program-recovery 的边际提升;OOD test on (a) MathVista, (b) **CLEVR-Math + scene-graph-recovery**(spatial 主线 transfer)
- **Scaling law**:沿 program 长度 / DAG 深度做 scaling

### Risks

1. Objective 边际收益要 ≥ 3–5pt 才有说服力,可能不达标
2. Program 等价定义难;token-level loss 是 lazy fallback
3. Spatial transfer 实验如果失败,program 叙事破产

**Best paper 潜力**:**8/10**(但 program-strength 上限最高)

---

## 方向 ③ :Reasoning Models Don't Reason ★ High-variance Backup

**Claim**:o1 / R1 / o3 / Gemini Deep Think 全员爆发,但**没人知道它们的 long CoT 是不是真的对应到 latent reasoning**。你的 pipeline 是**唯一**能为每个问题给出"真值 operator decomposition"的供给。系统性 audit frontier reasoning model 的 CoT 是否真对应 decomposition —— **大概率会发现它们的 CoT 是 post-hoc rationalization,真实 reasoning 发生在更深的非语言 layer**。

### 为什么这不是 chart 任务

- 研究对象是 **reasoning model 本身**,不是 chart 数据
- chart 因为能给闭式 GT 才被选作 probe
- paper title 是 "Mechanistic Audit of Reasoning Models" 而不是 "Chart Reasoning"

### Why now

- 2025 一年 reasoning model 全员爆发但 mechanistic 理解为 0
- ICLR / NeurIPS 2026 零星工作 question "is CoT faithful"(Lanham, Turpin 2023–24),局限 text
- multimodal reasoning model audit 完全空白

### Technical novelty

- **Trace-attribution metric**:token-level CoT 与 GT operator chain 的对齐度(SBERT alignment + 中间 scalar numeric match)
- **Activation patching with controlled stimuli**:minimally different counterfactual pair $(D, D')$ 只触发一个 operator —— 给 activation patching surgical control(传统 patching 用 IOI 类人造 task)
- **Faithfulness vs Accuracy gap**:测量 accuracy 高时 CoT 是否反而 less faithful(verbalization reward hacking)

### Experiments

- **MVP**:GPT-5.5 / o3 / Claude / R1-V / DeepSeek-VL2 在不同 #ops 难度上的 (accuracy, trace faithfulness) 联合分布
- **拉满**:open-weight model 做 activation patching,定位中间 scalar 在哪一层 emerge;比较长 CoT 模型和短 CoT 模型的 reasoning layer 位置
- **Provocative finding**:if true,做 "we can predict the answer from layer-K activation BEFORE the CoT is generated" —— best paper

### Risks

1. 若发现 CoT 是 faithful,paper 退化为 confirmatory(还能发但 not best paper)
2. 需要 open-weight reasoning model(DeepSeek-R1 / Llama-Reasoning / Qwen-Reasoning);frontier API 模型做不了 mechanistic
3. Activation patching 工程量大,需要 mechanistic infra

**Best paper 潜力**:**9/10 if negative finding,5/10 if positive**

---

## 方向 ④ :Synthetic Worlds > Web Data(wildcard,不推荐单兵)

**Claim**:扩展 pipeline 生成 10M–100M 量级合成"世界"(每个有 multi-modal view + reasoning trace),作为 reasoning model 的 **pre-training 数据**,展示**纯合成世界训出的小模型在真实 reasoning benchmark 上超过 web-data 训出的大模型**。

**Exciting 处**:直接挑战 "more web data" 范式;TabPFN 在 tabular 上已证明 synthetic prior > real,multimodal reasoning 空白。

**Risk**:pre-training 实验 PhD 单兵作战 too expensive(除非 industry collab)。**不推荐**作为 main bet。

**Best paper 潜力**:7/10 但不可行

---

## 三方向横向对比

| 维度 | ① AI Scientist | ② Latent Programs | ③ Reasoning Audit |
|------|----------------|-------------------|-------------------|
| **2026 frontier hit** | AI for Science(最大) | Self-sup pretraining + WM | Reasoning model interp |
| **Pipeline 角色** | 提供 oracle env(核心) | 提供 (view, code) 对(核心) | 提供 verified GT trace(工具) |
| **chart 露出程度** | 几乎没有 | 训练用,paper 不强调 | 完全降级为 probe |
| **Spatial 主线衔接** | 弱(可后续扩展) | **强**(scene → scene graph 同 objective) | 中(可做 spatial reasoning audit) |
| **可行性 (PhD 单兵 + 1 年)** | 中等(inverse SDK 工程) | 中等(pretrain 范围可控) | **高**(主要 eval / audit) |
| **Best paper 上限** | 9/10 | 8/10 | 9/10 (if negative) |
| **失败回退** | benchmark paper | SFT-objective paper | audit / diagnostic paper |

---

## 真实推荐

| 你的目标 | 推荐 |
|---------|------|
| **最 best-paper-shaped 的单 paper** | **方向 ①** —— 单 paper 故事强度最高;2026 的 Sakana / Anthropic-RE-Bench / METR 都是友军和对照;你是第一个有 oracle 的 |
| **PhD program 化、与 spatial 主线串起来** | **方向 ②** —— objective 可无缝迁移 scene graph / molecular / physical scene;本篇 chart proof,下一篇 spatial,主线连贯 |
| **High-variance 加菜** | **方向 ③** —— 核心实验是 evaluation 不是 training,可**并行**在做 ① / ② 时跑;negative result 立刻升级 main paper |

---

## Devil's Advocate(对 ①)

**A1. DGP recovery 搜索空间太大,agent 退化成记忆模板,泛化失败。**
testset scenarios 必须在 Phase 0 sub-topic level 完全 holdout,否则审稿人会怀疑 memorization。

**A2. "AI Scientist with oracle" 的批评:真实科学没有 oracle。**
即使证明 agent 能在 oracle 环境工作,迁移到真实科学的论据仍空缺。**必须补真实数据 case study**(已知 econ / epi 数据集上 recover 已知 effect)证明 sandbox-trained capability 真实可用。

**A3. Sakana / METR 在 paper 公开后会快速跟进。**
他们有更大算力。first-mover 窗口可能只有 6–8 个月。

**A4. DGP equivalence metric 设计是地狱级。**
两份 code 等价定义比想象中难(distribution test 在 small sample 上 noisy)。metric 不稳 → 所有结论被质疑。

---

## 下一步行动

待你决定主方向后,我可以做完整 4 周 MVP design + 12 月 milestone + 风险地图。

- [ ] **决定主方向**:① / ② / 还是 ③ + ① 并行
- [ ] 如选 ①:第一步是设计 inverse SDK + DGP equivalence checker(2 周可完成 MVP)
- [ ] 如选 ②:第一步是把现有 pipeline 输出 (view, code) 对的训练数据(已有,只需 dump)
- [ ] 如选 ③:第一步是 GPT-5.5 / o3 / R1 在小 chart subset 上的 trace 收集(1 周可起手)
