# 01 · 数据

把一个抽象的领域变成一张行级事件表，同时算出这张表能画出哪些图。

**这是整条流水线唯一调用 LLM 的地方，一个场景一次。** 这次调用同时产出三样东西：场景散文、数据生成脚本、绑到列上的分析意图。三样都在同一次调用里写出，所以意图指向的列一定存在——不需要先写自然语言、再由第二个调用反推绑定。

**子阶段**

| 子阶段 | 谁做 | 产出 |
|---|---|---|
| [领域池构建](#1-领域池)（整个项目只跑一次） | LLM ×2 → 规则去重 | 200+ 子领域的缓存文件 |
| [分档无放回采样](#1-领域池) | 规则 | 一条子领域 |
| [写场景 + 脚本 + 意图绑定](#2-一次调用产出三样东西) | **LLM ×1** | **整条流水线唯一一次调用** |
| 场景去重 | 规则 | embedding 余弦；命中就换一条子领域重来 |
| [解析声明](#4-表达式)、建依赖图、校验绑定 | 规则 | 依赖图 |
| [覆盖度检查](#5-覆盖度检查) | 规则 | 每个族非空还是空。**不需要数据** |
| [执行脚本](#6-生成引擎) + 结构检查 | 规则 | 900 行事实表；不过就[回喂](#7-错误反馈)，上限三次 |
| [产出表结构说明](#8-表结构说明) | 规则 | 给 [02](02_figure.md) 的数据接口 |

参考：[3 四个声明方法](#3-四个声明方法) · [7 错误反馈](#7-错误反馈)

先看 [§0 示例](#0-示例)，只看那一节就能明白这个阶段在干什么。

---

## 0. 示例

### 第一步 · **[规则]** 从领域池里抽一条

```json
{"name": "急诊科运营分析", "topic": "Healthcare", "complexity_tier": "medium",
 "typical_entities_hint": ["hospital", "department", "triage level"],
 "typical_metrics_hint": [{"name": "wait_time", "unit": "minutes"}],
 "temporal_granularity_hint": "daily"}
```

### 第二步 · **[LLM ×1]** 写场景、脚本与意图

一次调用，输出三段。第一段是场景散文，只用于 [05](05_output.md) 的 caption：

```json
{"scenario_title": "Emergency department visits and wait times at three metro hospitals, Jan–Jun 2024",
 "data_context": "The county health department compiled per-visit records from three hospitals for January through June 2024 to assess a new triage diversion policy."}
```

第二段是脚本：

```python
dim("hospital", ["Mercy General", "St. Luke's", "Riverside"], weights=[0.40, 0.35, 0.25])
dim("department", ["Internal Medicine", "Surgery", "Pediatrics", "Trauma"], parent="hospital",
    weights={"Mercy General": [0.35, 0.25, 0.15, 0.25],
             "St. Luke's": [0.40, 0.20, 0.20, 0.20],
             "Riverside": [0.30, 0.30, 0.15, 0.25]})
dim("severity", ["Minor", "Moderate", "Severe"], weights=[0.50, 0.35, 0.15], ordered="ordinal")

time("visit_date", start="2024-01-01", end="2024-06-30", freq="daily")

measure("wait_minutes",
        "lognormal(mu = 2.8 + 0.4*[severity=Moderate] + 0.9*[severity=Severe] + 0.2*[hospital=Mercy General],"
        "          sigma = 0.35)",
        unit="minutes", additive=True)
measure("cost",
        "wait_minutes * 12 + {Minor: 80, Moderate: 260, Severe: 700}[severity] + gaussian(0, 30)",
        unit="USD", additive=True)
measure("satisfaction",
        "clip(5.2 - wait_minutes / 32 + gaussian(0, 0.3), 1, 5)",
        unit="points", additive=False)

emit(900)
```

第三段是分析意图。每条意图带着它指向的列一起写出——**这份数据被收集来回答什么问题，以及这个问题落在哪几列上**：

```
① Which hospital and department waits longest   hospital × AVG(wait_minutes)    比较
② How wait time moved over the half year  visit_date × AVG(wait_minutes)  趋势
③ Do longer waits go with lower satisfaction wait_minutes × satisfaction     关系
```

绑定里带聚合方式，因为规则分不出这一层：`wait_minutes` 可加，`SUM` 与 `AVG` 都合法，但"三家医院的总等待分钟数"不是意图①问的东西。定义列的人顺手说清楚，比让下游猜便宜。

**LLM 的工作到此结束。它没有写出任何一个数据值，只写了"数据该怎么产生"和"这份数据要回答什么"。**

**去重** — **[规则]** 对 `data_context` 做 embedding 检查，与已有场景余弦 ≥ 0.85 就丢弃，换一条子领域重来。

### 第三步 · **[规则]** 解析声明，还不执行

从表达式里读出依赖：`cost` 引用了 `wait_minutes`，`satisfaction` 也引用了它，所以 `wait_minutes → cost`、`wait_minutes → satisfaction`，`wait_minutes` 是根。无环，通过。

意图绑定同时校验：三条意图指向的五个列名都在声明里，`AVG` 对 `wait_minutes` 合法，视图类三个取值都在六个族里。

### 第四步 · **[规则]** 检查这套 schema 的覆盖度

**这一步不需要数据。** 基数从声明直接读：`dim` 的取值列表长度、`time` 的起止与频率。

**逐族判断非空即可，不需要把候选一条条列出来。**

```
比较  hospital 3 · department 4 · severity 3 · day_of_week 7 · month 6 落在基数区间   非空
趋势  182 天可重采样为 weekly 26 / monthly 6，点数达标                              非空
构成  可加测度 wait_minutes, cost                                                    非空
关系  两个以上数值列；二维叉积最大 7×6 = 42 格，900 行摊下去期望每格 21 行            非空
分布  有数值列，原始行数 900 ≥ 100                                                   非空
流程  没有 ordered="stage" 的维度                                                     空

6 族中 5 族非空
```

阈值是至少 3 个族，通过。流程族缺一个 `ordered="stage"` 的维度，本场景没有天然的流转阶段，不强行补。

### 第五步 · **[规则]** 执行脚本，生成 900 行

| visit_date | day_of_week | hospital | department | severity | wait_minutes | cost | satisfaction |
|---|---|---|---|---|---|---|---|
| 2024-01-03 | Wed | Mercy General | Surgery | Moderate | 38.4 | 721 | 4.0 |
| 2024-01-03 | Wed | Riverside | Internal Medicine | Minor | 19.7 | 316 | 4.6 |
| 2024-02-11 | Sun | Mercy General | Trauma | Severe | 92.1 | 1805 | 2.3 |
| … | | | | | | | 共 900 行 |

结构检查：行数 900 ✓ · 三个类别列的实际取值数与声明一致 ✓ · 三个数值列有限非常数 ✓ · 无环 ✓。

### 第六步 · **[规则]** 产出表结构说明

```
场景    "Emergency department visits and wait times at three metro hospitals, Jan–Jun 2024" + 数据背景一段
维度组  entity = hospital(3) → department(4)      triage = severity(3, ordinal)
时间列  visit_date, daily, 182 天;  派生 day_of_week / month / quarter / is_weekend
数值列  wait_minutes  minutes  可加   根
        cost          USD      可加   ← wait_minutes
        satisfaction  points   不可加 ← wait_minutes
意图绑定  ①比较 hospital×AVG(wait_minutes)  ②趋势 visit_date×AVG(wait_minutes)  ③关系 wait×satisfaction
总行数  900
```

### 出错时

第三到第五步任何一项不通过，**[规则]** 组装一段说明原因的反馈文本，**[LLM]** 拿着它改脚本重来，最多三次。例如覆盖度只剩 2 个族时，反馈是"没有可加测度，画不出以 SUM 表达构成的图（pie、stacked_bar、area 的可加要求），请加一个计数或金额类的测度"。

---

## 1. 领域池

一次性构建、之后反复复用的 200+ 细粒度子领域池。两级：Topic → Sub-topic。

**怎么建**

```
1  [LLM]  生成 topic          一次产出 N 个互不重叠的行业级大类，把已有的 topic 传入避免重复
2  [LLM]  逐 topic 生成 sub-topic  每个 topic 下产出若干具体分析情境，附实体 / 指标 / 时间粒度提示
3  [规则] 去重                对名称做 embedding 检查，余弦 ≥ 0.80 的成对标出，删掉或重生成
4  [规则] 补齐                统计复杂度三档与 topic 覆盖，缺哪档补哪档，直到 200+ 且三档均衡
```

这四步只跑一次，产物是一个缓存文件。第 3 步的检查器只有一个实现，topic、sub-topic、场景三处共用。

**怎么采** — **[规则]**：按复杂度分档，档内无放回随机抽。某档抽掉 80% 后重置。抽样由随机种子决定，同一个种子给出同一串子领域。

**领域条目**

```json
{
  "id": "dom_001",
  "name": "ICU 床位周转分析",
  "topic": "Healthcare",
  "complexity_tier": "complex",
  "typical_entities_hint": ["hospital", "ICU unit", "patient class"],
  "typical_metrics_hint": [{"name": "occupancy_rate", "unit": "%"},
                           {"name": "length_of_stay", "unit": "天"}],
  "temporal_granularity_hint": "daily"
}
```

池文件另存版本号、生成时间、复杂度分布与 topic 覆盖统计。

| 复杂度 | 含义 | 目标行数 |
|---|---|---|
| simple | 单一实体类型，1–2 个指标，直接的时间序列 | 200–500 |
| medium | 多个相关指标，2 个以上实体类型 | 500–1000 |
| complex | 嵌套层级，3 个以上相互依赖的指标 | 1000–3000 |

子领域给的提示是软约束：具体场景需要时可以改写或替换，但不能越出该子领域的范围与复杂度档位。

---

## 2. 一次调用产出三样东西

**为什么必须在同一次调用里出**：脚本就是场景的形式化写法。分成两次调用意味着第一次写自然语言、第二次把自然语言反解成列——层级关系、有序性、单位、可加性在自然语言里都不显式，反解要靠猜；意图指向的列在写意图时还不存在，绑定也要靠猜。写在一起之后，这两处猜测都不存在。

| 段 | 内容 | 谁消费 |
|---|---|---|
| **场景** | `scenario_title` 含时间段、机构、分析焦点；`data_context` 说清谁收集、为何收集、何时收集 | [05](05_output.md) 的 caption；场景去重 |
| **脚本** | 四个声明方法的调用序列，见 [§4](#3-四个声明方法) | 本阶段的引擎 |
| **意图** | 2–4 条，每条 = 一句话 + 目标列 + 聚合 + 视图类 | [02](02_figure.md#11-意图图--构造) 构造意图图；[05](05_output.md) 的 caption |

提示词里带一个完整的输入-输出样例来固定格式。严格 JSON 外壳，脚本段是字符串。

### 分析意图有什么用

一条分析意图就是一句话：**这份数据被收集来回答什么问题**。它在后面有两个具体用途。

**用途一：指定该画哪张图。** 这张表能画出的合法视图有几百个，光 `bar` 配上五个类别列与六种聚合就是 30 个。意图直接把目标写死：「`hospital × AVG(wait_minutes)`，视图类 比较」，[02](02_figure.md#11-意图图--构造) 拿它构造 ViewSpec，不需要搜。

真实报表里的图是为了回答问题才画的，不是为了覆盖图表类型才画的。意图把这件事带进了生成流程。

### 意图把图表类型确定到什么程度

视图类与图表族一一对应，所以**一条意图确定了它那张意图图的族**。族内的具体类型由规则接着定：

| 谁定 | 定了什么 | 例 |
|---|---|---|
| 意图（LLM） | 目标列、聚合、族 | `hospital × AVG(wait_minutes)`，比较族 |
| 条件表（规则） | 族内哪些类型的结构与语义条件成立 | 比较族有 bar 与 grouped_bar；grouped_bar 要两个类别角色，这里只有一个，淘汰 |
| 确定性顺序（规则） | 成立的有多条时取哪条 | 只剩 `bar`，无需取舍 |

LLM 写不出 `bar` 这个词；它写的是"这份数据被收集来比较各家医院的等待时间"。族由这句话推出来，类型由列声明推出来，取舍由顺序推出来。

**由此产生的限制**：8 张图里 3 张意图图的族反映模型偏好，另外 5 张（2 张多面板 + 3 张补充）的类型由规则轮转。因此「图表类型分布由轮转保证」只对后 5 张成立。意图图会稳定偏向比较 / 趋势 / 关系——真实报表本来就这样偏，这是意图图的设计意图；类型覆盖面由轮转图那一路负责，见 [02 §5](02_figure.md#5-挑图与组版)。

**用途二：caption 的内容来源。** caption 是[训练目标](05_output.md#2-训练目标)之一。没有意图，caption 只能从 ViewSpec 生成——那种句子模型看着图就能写出来，拿它当目标学不到东西。

```
有意图   "Average emergency-department wait time at three metro hospitals, shown to assess the triage diversion policy introduced in early 2024"
没意图   "Average wait time by hospital"      —— 复述坐标轴名，图上读得出来
```

第一句里的"评估分流政策的效果""三甲医院"**图上一个字都没有**。这是 caption 作为训练目标的全部价值。

**它管的范围**：意图只管意图图。[02](02_figure.md) 还会按关系推出多面板图、按图表族采样出轮转图；那些图没有对应意图，caption 由视图本身的描述生成。

### 视图类的六个取值

与 [chart_types.md](chart_types.md) 的族一一对应。

| 视图类 | 什么样的问题 |
|---|---|
| 比较 | 谁最高、谁最低、排序 |
| 趋势 | 随时间怎么变、什么时候拐弯 |
| 构成 | 谁占多大比例、构成怎么变 |
| 关系 | 两个指标是不是一起动 |
| 分布 | 散得开不开、有没有离群 |
| 流程 | 一步步流转下来在哪一步掉得最多 |

**本阶段不出现具体图表类型词汇。** 意图写到视图类为止，是 `bar` 还是 `grouped_bar` 由 [02](02_figure.md) 按数据条件决定。数据源于业务需求，图表是数据的投影，选择权在下游。

---

## 3. 四个声明方法

列声明在前，行产出在后。整段脚本没有循环，没有条件语句，只有这四个调用。

| 方法 | 作用 |
|---|---|
| `dim(name, values, weights, parent, ordered, group)` | 类别列。`parent` 表达层级，`weights` 可以是一个向量，也可以是按父值给出的条件分布；`ordered` 取 `None` / `"ordinal"`（有大小顺序，如 Minor / Moderate / Severe）/ `"stage"`（流程里依次经过的阶段，如Triage → Exam → Admission）；`group` 给这条层级链命名，同一条链上的列写同一个 `group`，不写就取链的根列名。子列在某个父值下权重为 0 就表示不出现在那个父值下——**严格层级（一个处理中心只属于一个大区）这样写**，而每家医院都有外科则各父值下都给正权重；每个声明值至少要在一个父值下出现 |
| `time(name, start, end, freq)` | 时间列。星期、月、季度、是否周末四个日历字段自动派生，但只派生比轴步长粗的那几个：日频四个都派生，周频派生月与季度，月频只派生季度——比步长细的字段描述的是点落在哪一天，与数据无关；与时间列一一对应的字段是同一列换个名字 |
| `measure(name, expr, unit, additive)` | 数值列。`expr` 是一个表达式字符串 |
| `emit(n)` | 产出 n 行 |

`unit`、`additive`、`ordered` 不影响数值生成，只服务下游：`unit` 决定 [03](03_render.md) 的轴标签与数字格式；`additive` 与 `ordered` 决定能画哪些图。计数、金额、时长可加；比率、百分比、温度、评分不可加。流程类图表要求 `ordered="stage"`——有大小顺序不等于是流程阶段，把严重程度画成漏斗图没有意义。

**硬约束**

1. 每行是一件不可再分的事，不铺类别叉积
2. ≥2 个维度组、≥2 个数值列
3. 依赖关系必须无环
4. 表达式里每个符号都有显式数值定义
5. 每个数值列只声明一次，不靠后续调用打补丁
6. 每个数值列必须给出 `unit` 与 `additive`
7. 所有数字、实体、时间窗须落在合理的真实世界范围内

---

## 4. 表达式

| 成分 | 写法 | 例 |
|---|---|---|
| 分布 | `gaussian` `lognormal` `gamma` `beta` `uniform` `poisson` `exponential` `mixture` | `lognormal(mu=2.8, sigma=0.35)` |
| 类别效应 | `[列=取值]` 作为 0/1 指示，或 `{取值: 数}[列]` 作为查表 | `0.9*[severity=Severe]`、`{Minor:80, Moderate:260}[severity]` |
| 其他数值列 | 直接写列名 | `wait_minutes * 12` |
| 算术与裁剪 | `+ - * /`、`clip`、条件分段 | `clip(..., 1, 5)` |

**依赖从表达式里读出来，不用声明。** 解析取出自由变量，凡是引用了另一个数值列就连一条边。

**统计模式也是表达式的一部分**，不是单独的注入接口。离群值是一个乘性条件项，趋势断点是一个关于时间的分段项，季节性是一个关于月份的正弦项。

---

## 5. 覆盖度检查

**[规则]**。声明解析完、一行数据都还没生成时，**这套 schema 能画出哪些族的图已经完全确定**。[chart_types.md §1](chart_types.md) 的四类条件里，结构条件与语义条件只看列声明。

本步调 `registry/feasible.py`：`列声明 → 每个族非空还是空`。**只判断非空，不列举候选**——每个族里有没有任何一个 (类型, 列绑定, 聚合) 能通过条件表，这是对基数与声明字段的算术判断，不需要把组合展开。

这一步必须在 01 内部，因为能改脚本的只有 01 那一次调用，01 结束后没有回到上游的通路。

[02](02_figure.md#13-轮转图--采样加拒绝) 的轮转图从同一个条件表里采样具体候选，两处读同一份 `registry/charts.py`。

### 5.1 缺口怎么回喂

哪个族为空直接反映 schema 设计得好不好，缺口进反馈文本：

| 情况 | 回喂内容 |
|---|---|
| 一个可加测度都没有 | 构成类图只能退到 COUNT(*)，画不出金额或时长的占比 |
| 没有 `ordered="stage"` 的维度 | 画不出流程类图（waterfall、funnel） |
| 类别基数全部 < 3 或 > 30 | 画不出比较类图 |
| 非空族数低于阈值 | 这套 schema 一个场景只能产出少量图 |

也可以反过来用：要求 schema 必须支撑指定的几个族，LLM 就会主动补一个可加测度或一个 stage 维度。

### 5.2 数据条件只能算期望

变异系数与区分度依赖实际数值，声明期算不出来。每格支撑行数可以按 `emit(n)` 与声明权重算期望值做粗筛；精确判定在 [02 §3](02_figure.md#3-准入检查)。

---

## 6. 生成引擎

**[规则]**。给定「声明 + 随机种子」逐位可复现。

```
构建全列依赖图 → 拓扑排序 → 三步执行

α  非数值列   根维度按 weights 把 n 行分配到各值再打乱；子维度在每个父值的行内同样分配，
              权重为 0 就不出现在该父值下；时间列在 [start, end] 上按 freq 分配，再派生日历字段
β  数值列     按拓扑序逐列整体求值，每列一次向量运算，不逐行循环
γ  后处理     按声明的取值范围裁剪，按单位定小数位
```

**结构检查**（只查执行是否成功，不查统计性质）

| 检查 | 判据 |
|---|---|
| 行数 | 在目标值 10% 以内 |
| 基数 | 每个类别列的实际取值数与声明一致 |
| 数值 | 每个数值列有限、非空、非常数 |
| 依赖 | 无环 |

基数这一条是 [§6](#5-覆盖度检查) 成立的前提：声明期按声明的基数判族，执行后必须对得上。

不通过时换种子重掷，或反馈给 LLM。**任何情况下都不改声明**——表结构说明必须始终描述实际生成出来的数据。

---

## 7. 错误反馈

```
[LLM]  输出场景 + 脚本 + 意图绑定
[规则] 解析 → 校验绑定 → 覆盖度检查 → 执行 → 结构检查
       全过        → 进入 02
       任一不过    → 组装反馈文本 → 回到 [LLM]，最多三次 → 仍失败则跳过这个场景
```

反馈文本必须指出具体违反了哪条约束，例如"`cost` 与 `revenue` 互相引用，环路为 cost → revenue → cost"、"表达式里的 `base_fee` 没有定义"、"意图② 绑到了 `visit_hour`，声明里没有这一列"。只说"执行失败"对重试没有帮助。

高频失败类型进提示词的约束段，不靠加大重试次数来解决。

---

## 8. 表结构说明

给 [02](02_figure.md) 用的那份数据接口：

- **场景**：标题与数据背景两段散文
- **维度组**：每组有哪些列、层级链是什么、每列的 `ordered` 取值
- **列清单**：名称、类型（类别 / 时间 / 数值）、所属组、父列、基数；数值列另含单位与可加性
- **依赖图**：数值列的拓扑序与边
- **意图绑定**：每条意图的句子、目标列、聚合与视图类
- **总行数**
