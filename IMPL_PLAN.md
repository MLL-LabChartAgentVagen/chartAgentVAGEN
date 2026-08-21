# 实现计划

规格见 [storyline/parsebench_chart/](storyline/parsebench_chart/)。本文只讲怎么实现，不重复规格内容，也不写代码细节。

1. [范围](#1-范围) · 2. [系统骨架](#2-系统骨架) · 3. [目录结构](#3-目录结构) · 4. [数据接口](#4-数据接口) · 5. [模块划分的决定](#5-模块划分的决定) · 6. [运行方式](#6-运行方式) · 7. [风险与对策](#7-风险与对策) · 8. [Todo checklist](#8-todo-checklist)

---

## 1. 范围

**做**：从领域池到训练目标文件的完整数据生成流水线，以及它的自检。

**不做**：模型训练、评测脚本、真实图表的抓取与清洗。这三项消费本流水线的产物，不在本仓库。

**规模目标**：13 种图表类型端到端可复现、单机能跑通。规模化只是重复调用，不是新设计。

---

## 2. 系统骨架

五个阶段，一条单向的数据流。每个阶段只认它上游那一份数据接口。**整条流水线只有一次 LLM 调用**，在 01；02–05 全部由程序执行。

```
配置 + 根种子
     │
     ▼
┌──────────┐ FactTable   ┌──────────┐            ┌──────────┐          ┌──────────┐          ┌──────────┐
│ 01 data  │+TableSchema │02 figure │ FigureSpec │03 render │RenderOut │04 record │  Record  │05 output │
│ 数据 LLM×1│────────────▶│  选图     │───────────▶│  渲染     │─────────▶│ 标注记录  │─────────▶│ 训练目标  │
└────┬─────┘             └────┬─────┘            └──────────┘          └──────────┘          └──────────┘
     │ 逐族判非空               │ 逐条判候选
     └──────────┬──────────────┘
                ▼
     registry/conditions.py    ViewSpec + TableSchema → 能不能画
     纯函数，01 与 02 共用，只读声明

──────────────────── 共享层 ────────────────────
  interfaces/  五份数据接口，唯一定义处
  registry/    图表条件表 + 条件判定 + 可读性判据
  common/      种子 · 几何 · 像素反算 · 读写与版本 · 缓存
```

| 阶段 | 输入 → 输出 | LLM |
|---|---|---|
| 01 data | 领域池 → FactTable + TableSchema（含场景与意图绑定） | **1 次**：写场景、生成脚本与意图绑定。解析、判族、执行、结构检查全是程序 |
| 02 figure | FactTable + TableSchema → FigureSpec | 0 |
| 03 render | FigureSpec + StyleVector → RenderOutput | 0 |
| 04 record | RenderOutput → Record | 0 |
| 05 output | Record → 训练目标文件 | 0 |

每个阶段是一个函数：`阶段(上游产物, 种子, 配置) -> 下游产物`。同样的输入必得同样的输出，产物按输入的内容哈希落盘。任何阶段可以单独重跑，也可以拿样例文件单独开发。

**没有候选清单这个中间产物。** 01 只判每个族非空还是空；02 的三类图分别用构造、推导、采样产出具体 ViewSpec。两处调同一个 `registry/conditions.py`。

---

## 3. 目录结构

```
.
├── configs/                     模型 · 根种子 · 规模 · 层级开关 · K_max · 采样上限 T
├── storyline/parsebench_chart/  规格，唯一定义处
│
├── src/llmkit/                  ── 与 chartgen 无关的 LLM 调用层，可单独复用
│   ├── types.py                 Message · Usage · Response · 三类异常
│   ├── providers/               Provider 接口 + 三家实现（换家只加一个文件）
│   │   ├── __init__.py          协议 · effort 词表 · schema 严格性检查 · 按模型名选家
│   │   ├── anthropic.py         Anthropic
│   │   ├── openai.py            OpenAI（Responses API）
│   │   └── gemini.py            Gemini（google-genai）
│   ├── client.py                LLM：complete · json（结构化输出 + 回喂重试）· map（批量评测）
│   ├── parse.py                 从散文 / 围栏里挖 JSON + schema 校验
│   ├── cache.py                 按请求内容哈希缓存回复
│   └── embed.py                 Deduper：领域池与场景去重共用一个判据
│
├── src/chartgen/
│   ├── interfaces/            ── 五份数据接口，先定死，其他一切依赖它
│   │   ├── table.py             TableSchema（场景、维度组、列清单、依赖图、意图绑定）+ FactTable
│   │   ├── figure.py            Binding、ViewSpec、FigureSpec
│   │   ├── style.py             StyleVector
│   │   └── record.py            Element、Panel、Axis、Mark、LegendEntry、RenderOutput、Record
│   │
│   ├── registry/              ── 图表类型的唯一定义处，01 与 02 共用
│   │   ├── charts.py            6 族 13 型：结构 / 语义 / 数据条件、族、投影形态、图元形状、通道
│   │   ├── conditions.py        check(Binding, TableSchema) · family_nonempty(family, TableSchema)
│   │   └── channels.py          画法 → "值能否读出"的三条规则
│   │
│   ├── common/                ── 跨阶段复用
│   │   ├── rng.py               由根种子派生各阶段子种子
│   │   ├── geometry.py          坐标约定、框运算、缩放 / 仿射 / 单应
│   │   ├── readback.py          框内颜色占比、框 + 轴 → 反算值。自检与可验证奖励共用
│   │   ├── serde.py             接口对象的统一读写与版本检查（原 interfaces/io.py）
│   │   └── cache.py             内容哈希缓存与产物落盘
│   │
│   ├── s01_data/
│   │   ├── pool.py              领域池两级构建与分档无放回采样
│   │   ├── expr.py              表达式解析、自由变量提取、整列求值
│   │   ├── declare.py           dim / time / measure / emit 四个声明方法 + 隔离执行 + 建表结构
│   │   ├── engine.py            依赖图拓扑执行 + 后处理
│   │   ├── validate.py          逐族判可画 + 意图绑定校验 + 结构检查（三者都产出回喂文本）
│   │   └── author.py            那一次 LLM 调用：提示词、输出契约、规则那一半、四类回喂
│   │
│   ├── s02_figure/
│   │   ├── project.py           四种投影形态；逐行形态含确定性抽样
│   │   ├── admit.py             准入检查：数据条件三项 + (键集合, 图元形状) 冗余判据
│   │   ├── panel.py             五种关系：锚点 → 第二个面板；面板数与共享关系
│   │   └── compose.py           构造意图图 · 推多面板 · 按族采样轮转图 → FigureSpec
│   │
│   ├── s03_render/
│   │   ├── style.py             风格向量采样
│   │   ├── draw/                ── 边画边记，按图元形状分文件
│   │   │   ├── canvas.py          画布、面板、轴、图例的公共记录
│   │   │   ├── rect.py            bar 族 / histogram / waterfall / funnel
│   │   │   ├── point.py           line / area / scatter
│   │   │   ├── sector.py          pie（中空与否是风格参数）
│   │   │   ├── cell.py            heatmap
│   │   │   └── boxlike.py         box
│   │   ├── degrade.py           图像退化与框的同步变换
│   │   └── page.py              页面合成与页面元素层
│   │
│   ├── s04_record/
│   │   ├── merge.py             三层拼接
│   │   ├── readable.py          逐图元判定值能否读出
│   │   └── selfcheck.py         三项自检，前两项调 common/readback.py
│   │
│   ├── s05_output/
│   │   ├── export.py            记录 → 八类训练目标 + 文件布局
│   │   └── verify.py            模型输出的可验证奖励，调同一个 common/readback.py
│   │
│   ├── report.py                产物的可读视图：schema 的三张 Mermaid 图 + 终端摘要
│   ├── pipeline.py              编排：按顺序调各阶段，每步查缓存，产物落盘
│   └── cli.py                   建池 / 单阶段运行 / 画图 / 批量生成
│
├── data/domains/                领域池，进版本库
├── data/generated/              运行产物，不进版本库
├── tools/
│   ├── make_samples.py          重生成 tests/samples/ 的接口样例
│   └── overlay.py               把记录里的框叠回图像，人工目视检查
└── tests/{samples,unit,e2e}/
```

---

## 4. 数据接口

**这一步在写任何阶段代码之前完成。** 六份接口定死之后，五个阶段可以并行开发：每个人只需要上游的样例文件。改接口要同时改样例文件并升 `schema_version`，让旧产物在读取时报错而不是静默错算。

| 接口 | 从 → 到 | 字段 |
|---|---|---|
| **FactTable** | 01 → 02 | 行级事件表，落盘为 parquet |
| **TableSchema** | 01 → 02 | 场景标题与数据背景、维度组与层级链、列清单（类型 / 所属组 / 父列 / 基数 / ordered；数值列另含单位与可加性）、依赖图、**意图绑定**（句子 + 目标列 + 聚合 + 族）、总行数 |
| **ViewSpec** | 02 内部 | 图表类型、列绑定、聚合、行过滤、求值结果、每组行数、逐行形态的抽样索引 |
| **FigureSpec** | 02 → 03 | 面板列表、版面、共享关系（含共享图例时的系列列）、多面板的关系类型、来源 |
| **StyleVector** | 03 内部 | 七组风格维度；随记录一起存，供消融按维度分组 |
| **RenderOutput** | 03 → 04 | 图像路径与尺寸、L0 元素、L1 面板 / 轴 / 图元 / 图例、施加过的退化变换 |
| **Record** | 04 → 05 | RenderOutput 拼上 L2 行数与逐图元的 `readable` |

**场景散文与意图绑定是 TableSchema 的字段**，与列声明在 01 的同一次调用里产出，不占单独的跨阶段产物。

三条约定：**键是有序字符串元组**（`("Mercy General", "Surgery")`，三层记录靠 `(figure_id, panel_id, key)` 对齐）；**框只有一种写法**（像素、原点左上、`[x0,y0,x1,y1]`，与图像宽高一起存）；**每个接口对象带 `schema_version`**。

以[急诊科示例](storyline/parsebench_chart/README.md#贯穿示例)为例：

```
TableSchema   hospital(3)→department(4)、severity(3,ordinal)、visit_date(182天)
              wait_minutes minutes 可加 · cost USD 可加 · satisfaction points 不可加
              意图绑定 ①比较 hospital×AVG(wait) ②趋势 visit_date×AVG(wait) ③关系 wait×satisfaction
FactTable     900 行，一行一次就诊
FigureSpec    bar，x=hospital，y=AVG(wait_minutes)
              Mercy General 42.3 (372 行) · St. Luke's 35.8 (315 行) · Riverside 28.1 (213 行)
StyleVector   不写数值标注 · 企业蓝 · y 轴起点为零 · 900×600 · JPEG 75
RenderOutput  绘图区 [96,60,860,520]，y 值域 [0,60] ↔ 像素域 [520,60]；Mercy General的条 [168,196,278,520]
Record        上面这些 + rows=372 + readable=true
```

---

## 5. 模块划分的决定

**LLM 调用层独立成包。** `src/llmkit/` 不认识 chartgen，只做「调模型、要 JSON、缓存、去重、批量」五件事。01 用它，横向评测多个模型也用它。换一家模型只加一个 provider 文件——写模型名就换家（`LLM("gemini-3.1-pro-preview")`），三家的图像输入、结构化输出、推理强度落在同一个调用面上，缓存键含 provider 与 model，互不覆盖。

**LLM 只在"定义"时出现，不在"选择"时出现。** 01 定义场景、列、单位、可加性、有序性与意图绑定；此后构造、推导、采样、拒绝、组版全部是规则，每次运行可复现。

**场景与脚本在同一次调用里写。** 脚本是场景的形式化写法。分两次调用会在中间放一层有损的 JSON（层级、有序性、单位、可加性在自然语言里都不显式），而且下游没有回到上游的反馈通路。

**三类图三种产出方式，只有一种需要随机数。** 意图图从绑定构造，多面板图从锚点推导，只有轮转图采样加拒绝。因此 `compose.py` 里只有一处读随机数。

**不枚举候选清单。** 枚举要把几百到几千条候选全算出来、每条投影一遍才知道通不通过，而一个场景只出十来张图。改成：01 只判族非空，02 逐条构造或采样、逐条投影、逐条判进出。`registry/conditions.py` 的 `check()` 两处共用。

**多样性由 `(键集合, 图元形状)` 判据管，不由数量管。** 数量上限 K_max 只是渲染与存储的预算。拿数量当多样性的代理挡不住"八张图全是 `bar(hospital × …)`"。

**投影按形态分支，不按图表类型分支。** `project.py` 只有四条路径：分组标量、分组五数、分箱计数、逐行不分组。形态写在 `registry/charts.py` 的类型条目里。

**行过滤只在 `panel.py` 里出现。** 它只服务「时间对照」一种关系，是配对时从锚点现场切出来的，不是 ViewSpec 的一个采样维度。

**按图元形状分文件，不按图表类型分文件。** 13 种类型只有 5 种图元形状。`draw/rect.py` 同时服务 bar、grouped_bar、stacked_bar、histogram、waterfall、funnel——差别只在值字典里填哪几个键。

**视觉变体归风格向量，不进类型表。** 四类条件、图元形状、值字典逐项相同的两个"类型"（实心饼与中空饼）在 `registry/charts.py` 里只占一行。**但共享图例要求各面板共用系列列，这条是 FigureSpec 的硬约束，风格改不动。**

**画和记不分开。** 画每个图元的那一行同时写记录——只有那一刻框、键、值三者同时在手。

**像素反算只有一个实现。** `common/readback.py` 提供「框内某颜色的占比」与「框 + 轴 → 值」。04 的自检拿渲染器的记录当输入，05 的可验证奖励拿模型输出当输入。

**图表条件表是唯一定义处。** 新增一个图表类型只改 `registry/charts.py` 加一个绘制分支，不改 01、02、04、05 的任何代码。

**自检在生产路径上，不在测试里。** 每张图都跑，失败就丢图并记原因——边画边记的错误只会在真实数据上暴露。

---

## 6. 运行方式

**种子**：一个根种子，按 `(scenario_id, 阶段名, 序号)` 派生子种子。任何阶段不读全局随机状态。

**缓存**：每个阶段的产物按输入的内容哈希落盘，命中直接返回。改 03 不会触发 01–02 重跑，这同时就是断点续跑。

**产物布局**：`data/generated/<run_id>/<scenario_id>/` 下按阶段分文件，图像与记录同名不同后缀。单阶段运行少一层 `run_id`。

**产物自带可读视图**：写 schema 的同时写一份 `schema.md`（层级树、数值列依赖、意图指向三张 Mermaid 图，加可画族与最密叉积的行/格）。不用另跑命令才能看懂一次运行产出了什么。

**失败处理**：任何阶段失败只丢弃当前场景并写一条带原因的记录，不中断批次。跑完输出各阶段通过率——这是流水线健康度的主要观测量。

**CLI**：单阶段运行（拿样例文件当输入）、指定场景重跑、批量生成、补画已有 schema。

---

## 7. 风险与对策

| 风险 | 表现 | 对策 |
|---|---|---|
| 坐标漂移 | 自动布局、dpi、`bbox_inches` 改变实际绘图区，框整体偏移且不报错 | 冻结这三项；"框里有没有东西"这项自检逐图元拦截 |
| 轴映射错误 | 对数轴、负值、堆叠基线上反算出的值与记录的值不符 | "量出来的值对不对"这项自检；对数轴放到 Tier 1 之后再开 |
| 声明期与执行后基数不一致 | 按声明判非空的族在实际数据上一张也画不出 | 01 的结构检查强制实际基数与声明一致，不一致就重掷或反馈 |
| 单次调用负担过重 | 场景 + 脚本 + 意图三段一起写，某一段质量下降 | 三段各有独立校验：去重查场景、结构检查查脚本、绑定校验查意图；哪段不过就带具体原因回喂哪段 |
| 脚本失败率 | LLM 写的生成程序反复触发同一类异常 | 统计异常类型分布；高频类型进提示词的约束段，不靠加大重试次数 |
| 采样抽不中 | 某个族反复抽到不合法或冗余的候选 | 每族至多 T 次，超了就跳过并记日志；各族出图率是观测量 |
| 值目标稀疏 | 饼图、热力图的值几乎全部读不出 | 预期结果不是缺陷。这些图仍贡献定位目标；值目标产出率按图表类型分别统计 |
| 风格泄漏进真值 | 某个风格参数意外改了求值结果 | "换风格答案变不变"这项自检按图抽样跑，输入就是风格配对样本 |
| 接口漂移 | 上下游对同一个字段的理解不一致 | 接口先定死；每份接口带版本号与样例文件；改接口必须同时改样例 |

---

## 8. Todo checklist

A 是所有人的前置。A 完成后 B–F 之间只靠样例文件耦合，可以并行推进；其中 D + E 风险最高，建议 A 之后先用 `tests/samples/` 里手写的 FigureSpec 把 D1 + E3 打通一遍。

### A. 骨架与数据接口

- [x] A1 仓库骨架：各子包与空 `__init__`；`configs/` 默认配置（模型、根种子、规模、层级开关、K_max、采样上限 T）；`tests/` 三个子目录与 pytest 配置；`pipeline.py` / `cli.py` 空壳串起五个阶段的签名
- [x] A2 六份数据接口
  - [x] A2.1 dataclass 定义，全部带类型标注与 `schema_version`
  - [x] A2.2 `common/serde.py` 统一读写与版本检查
  - [x] A2.3 每份接口一个最小样例进 `tests/samples/`
  - [x] A2.4 序列化往返测试：读进来再写出去逐位相同
- [x] A3 图表条件表
  - [x] A3.1 `registry/charts.py`：13 型的条件、族、投影形态、图元形状、通道
  - [x] A3.2 `registry/conditions.py`：`check(ViewSpec, TableSchema)` 与 `family_nonempty(family, TableSchema)`
  - [x] A3.3 `registry/channels.py`：画法 → 可读性的三条规则
  - [x] A3.4 静态检查：`conditions.py` 只读 TableSchema，碰不到数据
  - [x] A3.5 自检：每型声明的图元形状与它的值字典键一致
- [x] A4 公共模块：`rng` 种子派生 · `geometry` 坐标与变换 · `readback` 颜色占比与反算值 · `cache` 内容哈希；LLM 调用、JSON 解析、重试与去重独立成 `src/llmkit/`
- [x] A5 产物可读视图 `report.py`：schema 的三张 Mermaid 图与终端摘要，随每次产出自动落盘；`cli inspect` 补画早先的 schema

### B. 01 数据

- [x] B1 领域池：topic → sub-topic 两级生成、embedding 去重（0.80）、三档均衡补齐到 200+、落盘带统计；分档无放回采样（80% 后重置）与同种子可复现测试
- [x] B2 四个声明方法：`dim` / `time` / `measure` / `emit` 与参数校验；`unit` / `additive` / `ordered` 写进 TableSchema；带语义的异常；隔离执行与异常捕获
- [x] B3 表达式：分布族求值 · 类别效应两种写法 · 自由变量提取与依赖边推断 · 算术裁剪条件分段
- [x] B4 生成引擎
  - [x] B4.1 全列依赖图与拓扑排序，环检测
  - [x] B4.2 非数值列：根维度、条件下钻（权重 0 表示严格层级）、时间与随频率决定的日历派生
  - [x] B4.3 数值列：按拓扑序整列向量求值；后处理裁剪与小数位
  - [x] B4.4 结构检查四项，其中基数必须与声明一致
  - [x] B4.5 「声明 + 种子」逐位可复现测试
- [x] B5 覆盖度检查：调 `conditions.family_nonempty` 逐族判；五条缺口的回喂文案（缺可加测度、缺 stage 维度、基数全部越界、二维叉积每格行数过稀、非空族数过低）
- [x] B6 那一次 LLM 调用
  - [x] B6.1 提示词：声明方法说明 + 一个完整的输入-输出样例
  - [x] B6.2 同一次调用输出三段：场景散文、脚本、带绑定的意图
  - [x] B6.3 场景去重（比对 `scenario_title`），命中就换子领域重来；判据默认是 `llmkit.embed.lexical`（字符 n-gram，不需要服务），换语义 embedding 只是换一个函数
  - [x] B6.4 意图绑定校验：列存在、聚合对该测度合法、族在六个里
  - [x] B6.5 四类回喂（执行失败 / 覆盖度不足 / 结构检查不过 / 绑定不合法），上限三次
  - [x] B6.6 异常与缺口类型分布统计
  - [x] B6.7 手写脚本样例进 `tests/samples/`，供 C 阶段脱离 LLM 开发

### C. 02 选图

- [ ] C1 投影 `project.py`
  - [ ] C1.1 分组标量：选行 → 分组聚合 → 取列，一并返回每组行数
  - [ ] C1.2 分组五数（box）与离群点图元
  - [ ] C1.3 分箱计数（histogram）：先定箱边再计数
  - [ ] C1.4 逐行（scatter）：不分组；超过点数上限时按种子确定性抽样，抽样索引进 ViewSpec
  - [ ] C1.5 时间轴重采样（daily / weekly / monthly）
- [ ] C2 准入检查 `admit.py`
  - [ ] C2.1 数据条件三项，按形态决定查哪几项
  - [ ] C2.2 `(键集合, 图元形状)` 冗余判据；多面板图豁免
  - [ ] C2.3 拒绝原因分类统计
- [ ] C3 关系 `panel.py`
  - [ ] C3.1 五种关系的构造规则：锚点 → 第二个面板
  - [ ] C3.2 面板数 2–4；「同指标不同切面」的 N 面板 small multiples
  - [ ] C3.3 关系 → 版面与共享关系的映射
  - [ ] C3.4 共享图例的硬约束：各面板系列列必须相同，否则降级为每面板一个图例
  - [ ] C3.5 时间对照：从锚点现场切前后两半各跑一次投影
- [ ] C4 组装 `compose.py`
  - [ ] C4.1 意图图：从绑定构造 ViewSpec，族内按确定顺序取第一条；取不到记录原因
  - [ ] C4.2 多面板图：以意图图为锚点，每种关系最多一张
  - [ ] C4.3 轮转图：按族轮转，先补批次里没有的族；每族至多 T 次采样；到 K_max 或一整轮不收为止
  - [ ] C4.4 组装 FigureSpec，带上每组行数、关系与来源
  - [ ] C4.5 每场景实际出图数与各族出图率进日志
- [ ] C5 静态检查：全程无 LLM；随机数只在 `compose.py` 的轮转图一路出现
- [ ] C6 多面板产出率统计：共享图例的图占比，`图例绑定` 目标非空的比例

### D. 03 渲染

- [x] D1 边画边记的最小实现
  - [x] D1.1 `draw/canvas.py`：画布、面板框、轴的值域与像素域、图例
  - [x] D1.2 `draw/rect.py`：bar 的绘制与图元记录
  - [x] D1.3 冻结图像尺寸、dpi、绘图区矩形，确认记录与实际一致
  - [x] D1.4 `tools/overlay.py` 把框叠回图像，目视确认
- [ ] D2 其余图元形状（Tier 1）：`rect.py` 扩到 grouped_bar / stacked_bar / histogram / waterfall / funnel；`point.py` line / area / scatter；`sector.py` pie；compound 双轴各记一份值域像素域
- [ ] D3 多面板绘制
  - [ ] D3.1 逐面板绘制，每面板各记一份框与轴的值域像素域
  - [ ] D3.2 2–4 面板的并排与网格排布；共享 x / y 轴
  - [ ] D3.3 共享图例：系列列相同才画一个外置图例，并记 `applies_to_panels`
  - [ ] D3.4 同类型 / 混类型两种面板配置
- [ ] D4 风格向量：七个维度独立采样 · 数值标注三态与标注框 · 随记录落盘 · 同一 FigureSpec 渲两份风格版本的入口（供 E3.3 与风格配对样本共用）
  - [x] D4.1 数字格式受单位约束：百分号只给份额单位，货币符号取自单位，标注文本永远是记录下来的那个数
  - [ ] D4.2 刻度与数值标注共用同一个格式函数（现在刻度走绘图库默认，两者可能不一致）
- [ ] D5 图像退化：恒等类（JPEG / 噪声 / 模糊）· 缩放 / 仿射 / 单应及其框变换 · 退化前后框一致性测试
- [ ] D6 页面合成：版面排布与图表贴入 · L0 元素框与五类标签 · 平移缩放施加到 L1 的框

### E. 04 标注记录

- [ ] E1 拼接：L0 / L1 / L2 按 `(figure_id, panel_id, key)` 连接；缺层降级（L2 关掉、L0 平凡）
- [ ] E2 值能否读出：调 `registry/channels.py` 的三条规则；长度 / 位置类的逐图元像素换算；`readable` 写进记录
- [ ] E3 三项自检
  - [ ] E3.1 框里有没有东西：调 `common/readback.py` 查颜色占比
  - [ ] E3.2 量出来的值对不对：调 `common/readback.py` 反算值与记录值比对
  - [ ] E3.3 换风格答案变不变：拿 D4 的两份风格版本比对键 → 值
  - [ ] E3.4 失败时丢图并记原因
- [ ] E4 13 型全部通过自检

### F. 05 输出

- [ ] F1 八类训练目标：A 组（带位置的表、抽查标注集）· B 组（图元定位、图元读值、下钻）· C 组（页面元素框、图例绑定）· caption（意图图用意图与场景，其余用视图描述）
- [ ] F2 可验证奖励
  - [ ] F2.1 `verify.py`：模型输出的 `(键, 值, 区域)` → 两项几何判定，调 `common/readback.py`
  - [ ] F2.2 与 E3.1 / E3.2 共用同一实现的静态检查
  - [ ] F2.3 无标注一致性指标的批量计算入口
- [ ] F3 输出格式与静态检查：导出程序只 import `interfaces/record.py` 与 `common/`，不 import 任何阶段模块
- [ ] F4 批量与统计：失败隔离 · 各阶段通过率与丢弃原因 · 值目标产出率按图表类型 · 端到端逐位可复现测试进 `tests/e2e/`
- [ ] F5 数据构成：真实图表的接入格式 · 按标注支持度限制其参与的目标类型 · 混合比例作为配置项

### G. 扩展与消融

- [ ] G1 Tier 2：`draw/cell.py` heatmap；`draw/boxlike.py` box
- [ ] G2 消融开关：L2 单独关闭 · 风格向量固定 · 全部写数值标注 · 去掉区域输出 · 去掉可验证奖励 · 只用 Tier 1 · 只用意图图
- [ ] G3 其他导出（不在当前主线）：问答对 · 图表代码 · 风格配对 / 版面配对 / 多图一致性样本
- [ ] G4 文档同步：规格与实现逐条对齐；README 补 CLI 与产物说明

### H. ParseBench 对齐

十条改动（`P1`–`P10`）由 [`parsebench/reports/INDEX.md`](parsebench/reports/INDEX.md) 定稿，**落地方式在 [`IMPROVEMENT_PLAN.md`](IMPROVEMENT_PLAN.md)**（逐条的文件、字段、验收、目录结构）。这里只留 checklist。

三条前提：

1. **十条里七条落在还没写的文件上**（`s02` / `s04` / `s05` / `s03` 的其余图元）。写的时候带上，不要写完再改。
2. **接口只动三个文件**（`record.py` · `figure.py` · `style.py`），一次抬 `serde.SCHEMA_VERSION` 2 → 3，同步重生成 `tests/samples/`。
3. **三条按读码收缩过**：P1 不加字段（ε 从 `Panel.axes` 现算，收缩成 `channels.py` 两个函数各加一个 `tolerance` 参数）· P2 不加字段（面板名就是面板的小标题，并入 P7；对外的键长短是 `05` 的导出参数）· P3 只剩两件（一页多图 `03 §5` 规格已有，标题块位置属于 P7）。

**次序**：**H10 → H1**（P1 现算 ε 要先知道对着哪条轴；两条都在 `s04/selfcheck.py`、`s05/verify.py` 动笔之前）→ **H7 → H2 / H9**（面板名取自标题块）→ **H11 → H5 → H4**（类型名单定死，权重才不会一写就过期）→ **H6**（在 H1 之后）→ **H3**（导出侧，最后）。

#### H10 · P9 图元记读法
- [ ] `record.Mark` 加 `axis_id`（指向 `Panel.axes` 里的一条）与 `mark_shape`
- [ ] `charts.ChartType` 的 `mark` / `channel` 改成元组（`compound` 同时画矩形与点）
- [ ] `compound` 的 `family=None` 改成 `"relation"`——**一个词**，它就能被轮转抽到；`Family` 六个取值不动，01 的 LLM 契约不受影响
- [ ] `common/readback.py` 按 `axis_id` 取轴
- [ ] 先澄清规格：`chart_types.md` 说 compound「同面板两条纵轴」，`02 §3.2` 说「图⑤ 两个面板」。一个 `Panel` 是一个绘图区 ⇒ **一个 panel、两条 value axes**
- **验收**：双轴图上 `verify()` 的「值对不对」能判对错

#### H1 · P1 容差变成参数（不动接口）
- [ ] `channels.readable(..., tolerance)` 与 `channels.tolerance(labeled, base)` 各加一个参数。**ε 从 `Panel.axes` 现算，不新增字段**
- [ ] 三个调用点各传各的：抽查标注集用基准口径（0 / 1%）· 回读自检与 RL 奖励用 ε
- [ ] 三种图内变化写进 `channels.py`：对数轴逐图元 · 堆叠中间段 ×2 · `value_labels="some"` 时印了的 ε ＝ 0
- [ ] 阈值取「容差」与「半个记录精度」的较大者（`_decimals` 在评分、比率这类接近 0 的列上会超过百分比容差）

#### H7 · P7 标题块（吃掉 P2 的一半）
- [ ] `interfaces/figure.py` 加 `TitleBlock(number, main, subtitle, unit, placement, scope)`，`scope ∈ {figure, panel}`；`FigureSpec` 与 `PanelSpec` 各挂一个可选 `title`
- [ ] `interfaces/record.py` 的 `Element` 加 `text`，`ElementCategory` 加 `"Heading"`——**画出来的字是真值**
- [ ] `main`/`subtitle`/`unit` 由 `binding`/`column_units`/`relation` 拼；只有 `number` 是新信息
- [ ] **标题块占固定高度**，有没有标题都留着（不变式 6）⇒ 绘图区不随标题变
- [ ] **一次重算 ER 数字链**：`[96,60,860,520]`、`[168,196,278,520]` 在五份文档里链住

#### H2 + H9 · P2 / P8 对外的键拼多长（不改记录结构）
- [ ] `Binding` 加 `colour_group`（哪一列分色）
- [ ] `s05_output/export.py` 加 `key_scope`：拼不拼面板名、附不附颜色分组。**`Mark.key` 结构、`project` 建键、`merge` 连接、冗余判据全不动**
- [ ] `key_scope` **随产物落盘**（不变式 11 要求键能回落到图元）
- [ ] 面板名取自 `TitleBlock.main`；没有标题块就不许把面板维算进键
- [ ] **分色列归 `FigureSpec`、色值归 `StyleVector`**，否则换风格改 key、自检③失效

#### H11 · P10 类型表加三行
- [ ] 区间条 / 哑铃归 `distribution`，**复用 `grouped_fivenum`**、`value_keys=("min","max")`，不新造 `RANGE` 聚合；`rect.py` 加不从零起算的分支
- [ ] windsock 归 `trend`，区间画成**带状图元**（`lo`/`hi` 塞进 `point` 会落在框外）
- [ ] 表格型图 `family=None`（唯一例外），`Channel` 加 `"printed"`；采样权重单独设低配比、可读率统计里单列；写明它没有值轴 ⇒ `verify()` 的「值对不对」恒为 `None`
- [ ] 加行前过门槛：四类条件 ＋ 图元形状 ＋ 值字典全同才算风格变体、不占一行

#### H5 · P5 密度档
- [ ] `charts.py` 加 `DENSITY_BANDS`（≤20 / 21–60 / 61–150 / 151–400 / >400），`card`/`points`/`n_marks` 随档取值。**留在 `charts.py`**——它们是声明期的界
- [ ] 档位给**行数下界**，不够就降档记日志；不要放宽 `min_rows_per_cell`
- [ ] **先改 `rect.py::_write_label`**：每个标签一次全图重绘，>400 图元跑不动 ⇒ 一次 `draw()` 后批量量取
- [ ] `chart_types.md §4` 给出每档预期可读率（高密度档大批图元掉出值目标是设计后果）

#### H4 · P4 采样权重
- [ ] 新文件 `s02_figure/sampling.py`，三个预设（`uniform` 默认 · `parsebench` · 自定义）
- [ ] 权重作用在**抽取顺序**上，不是配额（配额会把空族预算浪费掉，默认档产出的图变少）
- [ ] `uniform` ＝ 现有「先补批次里还没有的族」那条规则本身，逐位等价
- [ ] 权重**按名键入**、随产物落盘；**不回流到 01**

#### H6 · P6 风格向量
- [ ] 七组维度各自扩取值域，**只加取值不加字段**
- [ ] **每加一个取值同时加绘制分支** ＋ 一条自检（`sample()` 逐维独立采样，没分支落实的维度会在记录里写下没发生的事）
- [ ] **面板底色之前先修 `readback.ink_fraction`**：按白底判会**静默失效**（自检恒过、偏移的框照样写盘）⇒ 改成按「与面板底色不同的像素」算
- [ ] 横条 / 竖条是风格维度；`rect.py` 要同时处理两个方向

#### H3 · P3 导出侧（一页多图 `03 §5` 规格已有，只是 `page.py` 没实现）
- [ ] `s05_output/export.py` 加**整页 markdown** 导出：一页每张图各成一张长表，图号与标题写成表**前面**的小标题
- [ ] 页面元素框目标**按 `page_id` 合并去重**（一页两图各导一份会互相漏标对方的标题块）
- [ ] `s02_figure/admit.py` 的冗余判据给**同一页且标题块不同**的多张图开豁免；`02 §3.2` 的条文从按面板数改成按来源
- [ ] 逐 value key 的回读自检**只对有几何锚点的键做**（`value` · `cum_*` · 五数里落在框边的），否则 histogram 的 `bin_lo`/`bin_hi` 会把 `bar_width` 钉死

#### 验收
- [ ] H8 用官方 `ChartDataPointRule` 在 568 页上自评，改造前后各一次
- [ ] 消融数字标注它在哪一套权重预设与哪一档密度下取得（H4 / H5 会让基线漂移）
- [ ] 风格消融改成**分组消融**；混合比例拆出来单测
