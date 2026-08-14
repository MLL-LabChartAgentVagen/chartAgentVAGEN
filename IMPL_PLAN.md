# 实现计划

规格见 [storyline/parsebench_chart/](storyline/parsebench_chart/)。本文只描述如何实现，不重复规格内容，也不含代码细节。

---

## 目录

1. [范围与不做的事](#1-范围与不做的事)
2. [阶段到包的映射](#2-阶段到包的映射)
3. [文件结构](#3-文件结构)
4. [代码结构的四个决定](#4-代码结构的四个决定)
5. [跨阶段契约](#5-跨阶段契约)
6. [运行时约定](#6-运行时约定)
7. [交付顺序](#7-交付顺序)
8. [风险与对策](#8-风险与对策)
9. [Todo checklist](#9-todo-checklist)

---

## 1. 范围与不做的事

**范围**：从领域池到训练目标文件的完整数据生成流水线，外加它的正确性校验。

**不做**：模型训练、评测脚本、真实图表的抓取与清洗。这三项消费本流水线的产物，不属于本仓库。

**规模目标**：Tier 1 九种图表类型，端到端可复现，单机可跑通；规模化只是重复调用，不是新设计。

---

## 2. 阶段到包的映射

| 规格阶段 | 包 | 是否调用 LLM | 是否确定性 |
|---|---|---|---|
| 01 域池与场景 | `stage01_scenario` | 是 | 给定 LLM 输出后是 |
| 02 原子事实表 | `stage02_facts` | 是（写脚本） | 引擎部分是 |
| 03 选图 | `stage03_figure` | 是（选序号） | 枚举与过滤是 |
| 04 渲染 | `stage04_render` | 否 | 是 |
| 05 溯源记录 | `provenance` | 否 | 是 |
| 06 输出 | `targets` | 否 | 是 |

`registry`、`contracts`、`common` 被多个阶段共享，不属于任何单一阶段。

---

## 3. 文件结构

```
.
├── README.md
├── IMPL_PLAN.md
├── requirements.txt
├── configs/                  运行配置：模型、seed、规模、层级开关
├── storyline/parsebench_chart/   规格（唯一定义处）
├── src/gtc/                  gtc = grounded transcription chart
│   ├── contracts/            所有跨阶段数据对象与其序列化
│   │   ├── scenario.py       ScenarioContext、AnalyticalIntent
│   │   ├── schema.py         Schema Metadata
│   │   ├── view.py           ViewSpec、FigureSpec
│   │   ├── style.py          StyleVector
│   │   └── provenance.py     Mark、Panel、LegendEntry、PageElement、记录根对象
│   ├── registry/
│   │   ├── charts.py         图表注册表：结构 / 语义 / 视觉三族字段
│   │   └── channels.py       编码通道与可恢复性规则
│   ├── common/
│   │   ├── llm.py            调用、JSON 解析、重试
│   │   ├── embed.py          embedding 与去重检查器（三处复用）
│   │   ├── geometry.py       坐标约定、框运算、仿射与单应变换
│   │   ├── rng.py            由根 seed 派生各阶段子 seed
│   │   └── cache.py          内容哈希缓存与产物落盘
│   ├── stage01_scenario/
│   │   ├── pool.py           域池构建（一次性，产物入 configs 旁的缓存）
│   │   ├── sampler.py        分层无放回采样
│   │   └── scenario.py       场景实例化与场景级去重
│   ├── stage02_facts/
│   │   ├── sdk.py            dim / time / measure / emit 四个声明方法
│   │   ├── expr.py           表达式解析、自由变量提取、分布族求值
│   │   ├── engine.py         全列 DAG 拓扑执行
│   │   ├── validate.py       结构校验
│   │   ├── sandbox.py        脚本执行与类型化异常捕获
│   │   └── author.py         LLM 写脚本 + 错误反馈环
│   ├── stage03_figure/
│   │   ├── project.py        投影与聚合，顺带产出每组行数
│   │   ├── enumerate.py      (chart_type, column_binding) 枚举
│   │   ├── filter.py         数据质量 + 语义两组检查
│   │   └── select.py         LLM 在候选中选择，出口做成员检查
│   ├── stage04_render/
│   │   ├── style.py          风格向量采样
│   │   ├── backend/
│   │   │   ├── canvas.py     轴、面板、图例的公共插桩
│   │   │   ├── marks_rect.py     条形族 / 直方图 / 瀑布 / 漏斗 / treemap
│   │   │   ├── marks_point.py    折线 / 面积 / 散点 / 气泡
│   │   │   ├── marks_sector.py   饼 / 环
│   │   │   ├── marks_cell.py     热力图
│   │   │   └── marks_dist.py     箱线 / 小提琴
│   │   ├── degrade.py        图像退化与框的同步变换
│   │   └── page.py           页面合成与 L0 产出
│   ├── provenance/
│   │   ├── merge.py          L0 / L1 / L2 连接
│   │   ├── recover.py        逐 mark 可恢复性判定
│   │   └── verify.py         三项校验闸门
│   ├── targets/
│   │   ├── export.py         溯源记录 → 八类训练目标
│   │   └── formats.py        输出文件格式
│   ├── pipeline.py           阶段编排
│   └── cli.py                单阶段运行、断点续跑、批量生成
├── tests/
│   ├── unit/                 各模块
│   ├── golden/               小规模端到端，产物逐位比对
│   └── fixtures/             手写的 FigureSpec 与 DGP 脚本样例
└── out/                      产物，gitignored
```

---

## 4. 代码结构的四个决定

**按 mark 形状分模块，不按图表类型分模块。** 18 种图表类型只有 6 种 mark 形状。`marks_rect.py` 同时服务 bar、grouped_bar、stacked_bar、histogram、waterfall、funnel、treemap——它们的插桩逻辑是同一段代码加不同的值字典键。按类型分模块会得到 18 个高度重复的文件。

**渲染与插桩不分离。** 不做"先画图再解析图元"的两遍式实现。画每个 mark 的那一行同时写入记录，因为只有在那一刻框、键、值三者同时在手。分离会引入一次反查，而反查正是要消除的误差来源。

**契约集中在 `contracts/`，不散落在各阶段。** 每个跨阶段对象只有一处定义，序列化与反序列化跟着定义走。阶段之间只通过这些对象通信，不共享中间状态。

**校验是流水线的一部分，不是测试。** `provenance/verify.py` 在生产路径上运行，失败即丢弃该图并记录原因。测试里的校验只覆盖已知样例，生产路径上的校验覆盖全部产物——L1 插桩的错误只会在真实数据上暴露。

---

## 5. 跨阶段契约

| 契约 | 从 → 到 | 关键内容 |
|---|---|---|
| ScenarioContext | 01 → 02 | 实体、指标（含单位与取值范围）、时间粒度、目标行数、分析意图 |
| Schema Metadata | 02 → 03 | 维度组与层级、列清单（measure 含单位与可加性）、依赖图、总行数 |
| FigureSpec | 03 → 04 | 面板列表（每面板一个 ViewSpec，含聚合值与行数）、版面、共享关系、意图归属 |
| StyleVector | 04 内部 | 与 FigureSpec 正交采样；不进入任何 ground truth |
| 溯源记录 | 04 → 06 | L0 / L1 / L2 三层，加逐 mark 的可恢复性布尔字段 |

每个契约有一份 JSON schema 与一份最小样例，放在 `tests/fixtures/`。上下游可以只依赖样例独立开发。

---

## 6. 运行时约定

**seed 派生**：一个根 seed，按 `(scenario_id, stage, index)` 派生子 seed。任何阶段不读全局随机状态。

**缓存**：每个阶段的产物按输入内容哈希落盘。重跑时命中缓存直接返回，因此改 04 不会触发 01–03 重跑。这同时是断点续跑机制。

**产物布局**：`out/<run_id>/<scenario_id>/` 下按阶段分文件。图像与记录同名不同后缀，便于逐对检查。

**失败处理**：任何阶段失败只丢弃当前 scenario 并写一条带原因的记录，不中断批次。跑完输出各阶段的通过率，这是流水线健康度的主要观测量。

**CLI**：支持单阶段运行、指定 scenario 重跑、批量生成三种模式。

---

## 7. 交付顺序

**先做最不确定的一段。** L1 插桩是全项目风险最高的部分——它依赖 matplotlib 内部的坐标变换，且错误不会抛异常，只会安静地产出偏移的框。因此垂直切片从 04/05 开始，不从 01 开始。

| 里程碑 | 内容 | 完成判据 |
|---|---|---|
| **M0 骨架** | 契约、注册表、common、CLI 空壳 | 契约样例可序列化往返 |
| **M1 垂直切片** | 手写 FigureSpec → bar 渲染 → L1 → 校验闸门 → 一类训练目标 | 校验三项全过，框叠回图像目视正确 |
| **M2 数据侧** | SDK、引擎、投影、枚举、过滤（LLM 用手写脚本桩替代） | 手写 DGP 脚本跑出事实表，枚举出候选清单 |
| **M3 接入 LLM** | 01 全流程、02 错误反馈环、03 选择 | 端到端无人工干预跑通一个 scenario |
| **M4 Tier 1 完整** | 九种图表类型、风格向量、退化、页面合成、L0 | 九型各自通过校验闸门，风格不变性成立 |
| **M5 目标与规模** | 八类训练目标导出、批量生成、通过率统计 | 产出可直接训练的数据集，各阶段通过率有数 |
| **M6 扩展** | Tier 2、Tier 3、消融所需的开关 | L2 可单独关闭，风格向量可固定 |

M1 之后每个里程碑都保持端到端可运行，不存在"攒够了再连起来"的阶段。

---

## 8. 风险与对策

| 风险 | 表现 | 对策 |
|---|---|---|
| 坐标漂移 | `tight_layout`、dpi、`bbox_inches` 改变实际绘图区，框整体偏移 | 冻结这三项参数；像素一致性校验逐 mark 拦截 |
| 轴映射错误 | 对数轴、负值、堆叠基线上反解出的值与声称值不符 | 几何一致性校验；对数轴在 Tier 1 后再开 |
| 脚本失败率 | LLM 写的 DGP 脚本反复触发同一类异常 | 记录异常类型分布；高频类型进 prompt 的约束段，不靠加重试次数 |
| 视图组合爆炸 | 枚举出成千上万个候选，LLM 无法处理 | 按族与按 scenario 双重设上限，超出时确定性截断并记录丢弃数量 |
| 值目标稀疏 | 饼图、热力图的值几乎全部不可恢复 | 这是预期结果，不是缺陷。这些图仍贡献定位目标；值目标的产出率按图表类型分别统计 |
| 风格泄漏进真值 | 某个风格参数意外改变了聚合值 | 风格不变性校验按图抽样执行 |

---

## 9. Todo checklist

### A. 仓库与骨架

- [ ] A1 建包结构
  - [ ] A1.1 `src/gtc/` 各子包与空 `__init__`
  - [ ] A1.2 `configs/` 默认配置：模型、根 seed、规模、层级开关
  - [ ] A1.3 `tests/` 三个子目录与 pytest 配置
- [ ] A2 契约层
  - [ ] A2.1 `contracts/` 五个模块的 dataclass 定义
  - [ ] A2.2 每个契约的 JSON 序列化往返
  - [ ] A2.3 每个契约一份最小样例进 `tests/fixtures/`
- [ ] A3 注册表
  - [ ] A3.1 `registry/charts.py`：Tier 1 九型的结构 / 语义 / 视觉字段
  - [ ] A3.2 `registry/channels.py`：编码通道与可恢复性规则
  - [ ] A3.3 注册表自检：每型的 mark 形状键与视觉字段一致
- [ ] A4 公共模块
  - [ ] A4.1 `common/rng.py` seed 派生
  - [ ] A4.2 `common/geometry.py` 坐标约定、框运算、仿射与单应
  - [ ] A4.3 `common/cache.py` 内容哈希缓存
  - [ ] A4.4 `common/llm.py` 调用与 JSON 解析
  - [ ] A4.5 `common/embed.py` 去重检查器

### B. 垂直切片（M1，最高优先级）

- [ ] B1 插桩渲染器最小实现
  - [ ] B1.1 `backend/canvas.py`：面板、轴值域与像素域、图例的记录
  - [ ] B1.2 `backend/marks_rect.py`：bar 的绘制与 mark 记录
  - [ ] B1.3 冻结布局参数，确认绘图区像素域与记录一致
- [ ] B2 溯源记录
  - [ ] B2.1 `provenance/merge.py` 三层连接
  - [ ] B2.2 `provenance/recover.py` 逐 mark 可恢复性判定
- [ ] B3 校验闸门
  - [ ] B3.1 像素一致性检查
  - [ ] B3.2 几何一致性检查
  - [ ] B3.3 风格不变性检查
  - [ ] B3.4 失败时的丢弃与原因记录
- [ ] B4 可视化调试工具
  - [ ] B4.1 把记录中的框叠回图像输出一张检查图
  - [ ] B4.2 用手写 FigureSpec 跑通并目视确认
- [ ] B5 一类训练目标
  - [ ] B5.1 `targets/export.py` 导出 grounded 表
  - [ ] B5.2 golden 测试：产物逐位可复现

### C. 数据侧（M2）

- [ ] C1 SDK
  - [ ] C1.1 四个声明方法与其参数校验
  - [ ] C1.2 类型化异常，异常消息指明具体的约束违反
  - [ ] C1.3 `unit` / `additive` / `ordered` 进 Schema Metadata
- [ ] C2 表达式
  - [ ] C2.1 分布族求值
  - [ ] C2.2 自由变量提取与依赖边推断
  - [ ] C2.3 条件分支与分段项
- [ ] C3 引擎
  - [ ] C3.1 全列 DAG 构建与拓扑排序，环检测
  - [ ] C3.2 非数值列：根采样、层级下钻、日历派生
  - [ ] C3.3 数值列：按拓扑序求值
  - [ ] C3.4 结构校验四项
  - [ ] C3.5 `(声明, seed)` 逐位可复现测试
- [ ] C4 投影与枚举
  - [ ] C4.1 `project.py`：聚合与每组行数
  - [ ] C4.2 `enumerate.py`：列角色匹配，按族与按 scenario 设上限
  - [ ] C4.3 `filter.py`：数据质量三项
  - [ ] C4.4 `filter.py`：语义两项（可加性、有序性）
  - [ ] C4.5 手写 DGP 脚本样例进 `tests/fixtures/`

### D. 接入 LLM（M3）

- [ ] D1 域池
  - [ ] D1.1 topic 与 sub-topic 两级生成
  - [ ] D1.2 embedding 去重与复杂度均衡
  - [ ] D1.3 池文件落盘与覆盖统计
  - [ ] D1.4 分层无放回采样器
- [ ] D2 场景
  - [ ] D2.1 场景实例化 prompt 与 one-shot 示例
  - [ ] D2.2 场景级去重
  - [ ] D2.3 分析意图的结构化输出
- [ ] D3 DGP 脚本作者
  - [ ] D3.1 SDK 说明进 prompt
  - [ ] D3.2 沙箱执行与异常回喂，上限三次
  - [ ] D3.3 异常类型分布统计
- [ ] D4 选图
  - [ ] D4.1 候选清单的紧凑序列化
  - [ ] D4.2 选择 prompt：选序号 + 归属意图 + 面板组合
  - [ ] D4.3 出口成员检查
- [ ] D5 端到端
  - [ ] D5.1 `pipeline.py` 编排与缓存串联
  - [ ] D5.2 `cli.py` 三种运行模式
  - [ ] D5.3 单 scenario 无人工干预跑通

### E. Tier 1 完整（M4）

- [ ] E1 其余 mark 形状
  - [ ] E1.1 `marks_rect.py` 扩到 grouped_bar、stacked_bar
  - [ ] E1.2 `marks_point.py`：line、area、scatter
  - [ ] E1.3 `marks_sector.py`：pie、donut
  - [ ] E1.4 compound 双轴：两套轴值域与像素域
- [ ] E2 风格向量
  - [ ] E2.1 渲染参数七个维度的采样
  - [ ] E2.2 数值标注三态与标注框记录
  - [ ] E2.3 风格不变性按图抽样验证
- [ ] E3 图像退化
  - [ ] E3.1 恒等类退化
  - [ ] E3.2 缩放、仿射、单应及其框变换
  - [ ] E3.3 退化前后框一致性测试
- [ ] E4 页面合成
  - [ ] E4.1 版面排布与图表贴入
  - [ ] E4.2 L0 元素框与五类标签
  - [ ] E4.3 贴入变换施加到 L1 的框
- [ ] E5 九型全部通过校验闸门

### F. 目标与规模（M5）

- [ ] F1 八类训练目标导出
  - [ ] F1.1 grounded 表、spot-check 标注集
  - [ ] F1.2 页面元素框、mark 定位、mark 读值
  - [ ] F1.3 图例绑定、drill-down
  - [ ] F1.4 caption
- [ ] F2 输出格式
  - [ ] F2.1 文件布局与命名
  - [ ] F2.2 目标导出只读溯源记录的静态检查
- [ ] F3 规模化
  - [ ] F3.1 批量运行与失败隔离
  - [ ] F3.2 各阶段通过率与丢弃原因统计
  - [ ] F3.3 值目标产出率按图表类型分别统计
- [ ] F4 数据构成
  - [ ] F4.1 真实图表数据的接入格式
  - [ ] F4.2 按标注支持度限制其参与的目标类型
  - [ ] F4.3 混合比例作为配置项

### G. 扩展与消融（M6）

- [ ] G1 Tier 2
  - [ ] G1.1 `marks_cell.py`：heatmap
  - [ ] G1.2 `marks_dist.py`：box
  - [ ] G1.3 histogram
- [ ] G2 Tier 3（按需）
  - [ ] G2.1 violin、treemap、radar
  - [ ] G2.2 waterfall、funnel、bubble
- [ ] G3 消融开关
  - [ ] G3.1 L2 单独关闭
  - [ ] G3.2 风格向量固定
  - [ ] G3.3 全部画数值标注
  - [ ] G3.4 去掉区域输出
- [ ] G4 文档同步
  - [ ] G4.1 规格与实现的差异逐条对齐
  - [ ] G4.2 README 补 CLI 与产物说明
