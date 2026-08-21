# 改进计划 · 十条改动怎么落地

结论来自 [`parsebench/reports/`](parsebench/reports/INDEX.md)。这份文件只写**改哪个文件、加什么、怎么验**。

---

## 1. 现状

```
已实现   interfaces/  registry/  common/  s01_data/
         s03_render/{render,style,draw/canvas,draw/rect}.py
未实现   s02_figure/{project,admit,panel,compose}.py
         s03_render/{page,degrade}.py  draw/{point,sector,cell,boxlike}.py
         s04_record/{merge,readable,selfcheck}.py
         s05_output/{export,verify}.py
```

**十条里七条落在还没写的文件上**，所以是「写的时候带上」，不是「写完再改」。接口改动集中在三个文件，**一次抬 `SCHEMA_VERSION` 2 → 3**，同步重生成 `tests/samples/`。

---

## 2. 十条的落点

| | 改什么 | 文件 | 规模 |
|---|---|---|---|
| **P9** | 图元记下它对着哪条轴、什么形状 | `interfaces/record.py` · `registry/charts.py` | 2 字段 + 2 字段改元组 |
| **P1** | 可读判据的容差从写死变成参数 | `registry/channels.py` | **2 个函数签名** |
| **P7** | 标题块成为记录里的对象（含面板小标题） | `interfaces/{record,figure}.py` · `s03_render/page.py` | 1 类 + 2 字段 |
| **P2** | 面板名进对外的键 | `s05_output/export.py` | **并入 P7，只加导出参数** |
| **P8** | 颜色分组进对外的键 | `interfaces/figure.py` · 同一个导出参数 | 1 字段 |
| **P3** | 整页 markdown 导出 ＋ 同页多图不被冗余判据拒 | `s05_output/export.py` · `s02_figure/admit.py` | 1 函数 + 1 条件 |
| **P10** | 类型表加三行 | `registry/charts.py` · `s03_render/draw/{rect,point}.py` | 3 行 + 2 分支 |
| **P5** | 基数上界随密度档 | `registry/charts.py` | 常量 → 查表 |
| **P4** | 族采样权重可换 | `s02_figure/sampling.py` | **唯一的新文件** |
| **P6** | 风格向量补 30 项 | `interfaces/style.py` · `s03_render/style.py` · `draw/*` | 只加取值，不加字段 |

**净增一个文件。** 接口只动三个：`record.py` · `figure.py` · `style.py`。

---

## 3. 逐条实现

### P9 · 图元记读法

`compound` 同时画矩形与点、同时用长度与位置，单值字段表达不了；双轴时同一像素高度对应两个值，回读自检没有定义。

- `record.Mark` 加 `axis_id: str`（指向 `Panel.axes` 里的一条，与 `panel_id` 同构）与 `mark_shape: MarkShape`
- `charts.ChartType` 的 `mark` / `channel` 从单值改成元组
- `charts.py` 里 `compound` 的 `family=None` 改成 `"relation"`（一个词，它就能被轮转抽到；`Family` 六个取值不动，01 的 LLM 契约不受影响）
- `common/readback.py` 反算时按 `axis_id` 取轴

**先澄清规格**：`chart_types.md` 说 `compound` 是「同面板两条纵轴」，`02 §3.2` 说「图⑤ 两个面板」。一个 `Panel` 是一个绘图区，同面板双轴＝**一个 panel、两条 value axes**。两处口径要统一。

**验收**：双轴图上 `verify()` 的「值对不对」能判对错。

### P1 · 容差变成参数

ε ＝ `value_per_pixel(value_range, pixel_range)`，两个输入**都已经在 `Panel.axes` 里**，用的时候现算即可，**不新增字段、不动接口**。

```
channels.readable(channel, *, labeled, value, axis, tolerance)   ← 加一个参数
channels.tolerance(labeled, base)                                 ← 加一个参数
```

三个调用点各自传自己的容差，**不能互相替换**：

| 调用点 | 传什么 |
|---|---|
| `s05_output/export.py` 抽查标注集 | 基准口径：写了标注 0，估读 1% |
| `s04_record/selfcheck.py` 回读自检 | ε（这个比较今天没有阈值可用） |
| `s05_output/verify.py` RL 奖励 | 同上，一份实现 |

三种 ε 在图内变的情形写进 `channels.py`：对数轴逐图元算 · 堆叠中间段 ×2（读两次边界）· `value_labels="some"` 时印了的那个 ε ＝ 0。

阈值取「容差」与「半个记录精度」的较大者——`s01_data` 的 `_decimals` 在接近 0 的列（评分、比率）上的量化误差会超过百分比容差。

**验收**：饼图在 5% 容差下的去留算得出；不印数值的图上回读自检能判对错。

### P7 · 标题块（含面板小标题，吃掉 P2 的一半）

真实页面的标题块在绘图区**外面**，可能在上、在下、在侧，可能属于整张图，也可能是**每个面板上方的一个小标题**。面板名就是后者——不是一个新概念。

- `interfaces/figure.py` 加 `TitleBlock(number, main, subtitle, unit, placement, scope)`，`scope ∈ {figure, panel}`
- `FigureSpec` 与 `PanelSpec` 各挂一个可选 `title`
- `interfaces/record.py` 的 `Element` 加 `text: str`，`ElementCategory` 加 `"Heading"`——**画出来的那串字是真值**，不是 FigureSpec 里的字段
- `main` / `subtitle` / `unit` 由 `binding` / `column_units` / `relation` 按确定规则拼；只有 `number` 是新信息（页面合成时才编）
- **标题块占用固定高度，有没有标题都留着**（布局参数冻结是不变式 6）⇒ 绘图区矩形不随标题变

**连带任务**：绘图区下移 ⇒ `01`–`05` 五份文档里链住的 ER 数字（`[96,60,860,520]`、`[168,196,278,520]`）要**一次重算**。

**验收**：图号由页面合成器编；单位与基期从标题里拆得出来；caption 不含图上可读的信息。

### P2 · P8 · 对外的键拼多长

两条都**不改记录结构**：`panel_id` 已经在三层连接键里，颜色分组函数依赖于分组键。缺的只是「导出给模型的键要不要带上它们」。

- `interfaces/figure.py` 的 `Binding` 加 `colour_group: str | None`（哪一列分色）
- `s05_output/export.py` 加导出参数 `key_scope`：对外的键拼不拼面板名、附不附颜色分组
- **`key_scope` 随产物落盘**——不变式 11 要求模型输出的键能回落到图元，不知道用的哪个作用域就回落不了
- **面板名取自它的 `TitleBlock.main`**，所以「逐字可复制」是白给的；面板没有标题块就不许把面板维算进键

**分色列归 `FigureSpec`，色值归 `StyleVector`。** 风格向量不能选哪一列分色，否则换风格就改 key，自检③（换风格答案不变）失效。

**验收**：多面板图与含颜色分组的图，导出的表里那两段独立成列；两行消融只是换导出参数，不重新生成数据。

### P3 · 整页 markdown ＋ 同页多图的豁免

「一页多图」`03_render.md §5` 已经写了（「单页多图、跨栏、图注与图表分开…且可控」），是 `page.py` 的实现任务，不是缺口。「标题块与绘图区分开」是 P7。剩下两件真的：

1. `s05_output/export.py` 加一个导出函数：**整页 markdown**——一页里每张图各成一张长表，图号与标题写成表**前面**的小标题。页面元素框目标按 `page_id` 合并去重再导出（一页两图各导一份会互相漏标对方的标题块）
2. `s02_figure/admit.py` 的冗余判据给**同一页且标题块不同**的多张图开豁免

第 2 条不做，`FPA-guide-to-data-visualization_p20` 那种形态（并排两张图共用同一批类目名，只有各自小标题能分开）会被自己的准入检查拒掉。`02 §3.2` 现在的豁免条文按面板数写，要改成按来源。

**验收**：并排两张共用类目名的图，导出后不撞车。

### P10 · 类型表加三行

| 新行 | 归族 | `shape` / `mark` | 绘制 |
|---|---|---|---|
| 区间条 / 哑铃 | `distribution` | `grouped_fivenum` · `value_keys=("min","max")` | `rect.py` 加不从零起算的分支 |
| windsock | `trend` | 带状图元（**不能塞进 `point`**——`lo`/`hi` 会落在点的框外） | `point.py` 加带状分支 |
| 表格型图 | `family=None`（唯一例外） | `Channel` 加 `"printed"` | `page.py` 直接排版 |

- 区间条**复用 `box` 那一路**，不新造 `RANGE` 聚合
- 加行之前过 `chart_types.md` 自己的门槛：四类条件 ＋ 图元形状 ＋ 值字典全同才算风格变体、不占一行
- 表格型图天然可读、容差 0 ⇒ 采样权重单独设低配比、可读率统计里单列；并写明它**没有值轴**，`verify()` 的「值对不对」对这一型恒为 `None`

**验收**：三行都能生成，类型覆盖率表里各占一行。

### P5 · 密度档

`charts.py` 里的 `card` / `points` / `n_marks` 现在是常量（`bar` 3–30、`heatmap` 6–100…），这就是密度锁死在最稀疏档的原因。

- 加一张 `DENSITY_BANDS` 表（≤20 / 21–60 / 61–150 / 151–400 / >400），界随档位取值。**留在 `charts.py`**——它们是声明期的界
- 档位给出**行数下界**，事实表行数不够就降档记日志。不要放宽 `min_rows_per_cell`
- 先改 `rect.py::_write_label`：每写一个标签调一次 `fig.canvas.draw()`，>400 图元是数百次全图重绘，跑不动。改成一次 `draw()` 后批量量取
- `chart_types.md §4` 写明**每档的预期可读率**：高密度档大批图元掉出值目标是设计后果，不是 bug

**验收**：五档都能生成，各档的读数正确率与预期可读率对得上。

### P4 · 采样权重

新文件 `s02_figure/sampling.py`，三个预设：`uniform`（默认）· `parsebench`（实测配比）· 自定义权重文件。

- 权重作用在「轮转时下一个抽哪个族 / 类型」上，**不是配额**——`02 §3.3` 明写「出几张图是采样结果」，配额还会把空族的预算浪费掉，默认档产出的图变少
- `uniform` 预设 ＝ 现有那条「先补批次里还没有的族」的规则本身，逐位等价
- 权重**按名键入**（按下标会在新增类型后静默错位），随批次产物落盘
- **不回流到 01** 的可行性检查，否则两档的事实表不是同一份数据

**验收**：三档预设各生成一批，同种子逐位可复现。

### P6 · 风格向量

`interfaces/style.py` 的七组维度各自补取值域，**只加取值不加字段**。头部：单位位置 · 负值与零线 · 值轴标题写在轴正上方 · 脚注上标 · 单类目高亮 · 非 ISO 时间刻度 · 数值标签在图元外 · 说明框 · 面板底色 · 横向条 · 图例画在绘图区内 · 系列名标在线旁 · x 轴两级标签 · 类目名折行。

- 横条 / 竖条是**风格维度**（四类条件逐格相同），代价是 `rect.py` 要同时处理两个方向
- **每加一个取值同时加绘制分支**，并加一条自检——`style.py::sample()` 逐维独立采样，没有分支落实的维度会在记录里写下没发生的事
- **面板底色要先修 `readback.ink_fraction`**：它按白底判「框里有没有东西」，加底色后**静默失效**（自检恒过、偏移的框照样写盘）。占比改成按「与面板底色不同的像素」算

**验收**：逐项可配、默认保持现行行为，每个取值都有绘制分支。

---

## 4. 目录结构

```
src/chartgen/
├── interfaces/
│   ├── record.py        改  Mark.{axis_id, mark_shape} · Element.text · Heading 类别
│   ├── figure.py        改  TitleBlock · FigureSpec.title · PanelSpec.title
│   │                        Binding.colour_group
│   └── style.py         改  七组维度扩取值域
├── registry/
│   ├── charts.py        改  三行新类型 · mark/channel 元组 · compound 归 relation
│   │                        DENSITY_BANDS
│   └── channels.py      改  readable / tolerance 各加一个 tolerance 参数
├── common/readback.py   改  按 axis_id 取轴 · ink_fraction 按面板底色判
├── s02_figure/
│   ├── sampling.py      新  ← 唯一的新文件
│   ├── project.py       写  按新接口
│   ├── admit.py         写  冗余判据 + 同页豁免
│   ├── panel.py         写
│   └── compose.py       写
├── s03_render/
│   ├── style.py         改  采样新取值
│   ├── page.py          写  页面合成 · 标题块 · 一页多图
│   ├── degrade.py       写
│   └── draw/
│       ├── rect.py      改  区间条分支 · 横向条 · 标签批量量取
│       ├── point.py     写  含 windsock 带状分支
│       └── {sector,cell,boxlike}.py   写
├── s04_record/{merge,readable,selfcheck}.py    写
└── s05_output/
    ├── export.py        写  key_scope · 整页 markdown · 页面元素按 page_id 合并
    └── verify.py        写
```

---

## 5. 顺序

| | 做什么 | 为什么在这一位 |
|---|---|---|
| 1 | **P9 → P1** | P1 现算 ε 要先知道对着哪条轴。两条都必须在 `s04/selfcheck.py`、`s05/verify.py` 动笔之前 |
| 2 | **P7 → P2 / P8** | 面板名取自标题块，标题块先有 |
| 3 | **P10 → P5 → P4** | 类型名单定死，密度档才有得配；权重要等名单定死才不会一写就过期 |
| 4 | **P6** | 必须在 P1 之后（它加的取值直接改可读判据） |
| 5 | **P3** | 导出侧，最后做 |

接口只在第 1–2 步动，抬一次版本。主线实现（`s02` / `s03` 剩下的图元 / `s04` / `s05`）穿插在第 1 步之后——接口已定，一遍写对。

---

## 6. 风险

| | 对策 |
|---|---|
| 密度一开可读率坍塌 | 是设计后果。`chart_types.md §4` 给出每档预期可读率 |
| 密度一开行数不够，`_allocate` 把长尾压成 1 行且结构检查查不出 | 档位给行数下界，不够就降档 |
| 面板底色静默关掉自检① | 先修 `ink_fraction`（P6 之前） |
| `>400` 图元时标签渲染跑不动 | 先改 `_write_label`（P5 之前） |
| 权重按下标写会在新增类型后静默错位 | 按名键入，随产物落盘 |
| 一页两图各导一份 L0 会互相漏标 | 页面元素框按 `page_id` 合并去重 |
| 逐 value key 的回读自检扩大丢图面 | 只对有几何锚点的键做（`value` · `cum_*` · 五数里落在框边的） |
| 标题块占高度让 ER 数字链失效 | 固定高度 + 五份文档一次重算 |
| 接口改动 | 三个文件一次改完，抬一次 `SCHEMA_VERSION`，重生成 `tests/samples/` |

---

## 7. 规格同步

| 文档 | 改什么 |
|---|---|
| `chart_types.md` | 三行新类型 · `mark`/`channel` 各两个 · 界随密度档 · **把 1% 从判据里拿出来** · 每档预期可读率 · `printed` 通道 |
| `01_data.md` | 行数下界随密度档 |
| `02_figure.md` | 冗余豁免改成按来源 · `compound` 是一个 panel 两条轴（与 `chart_types.md` 统一） · 分色列归 FigureSpec |
| `03_render.md` | **重算 §0 的数字链** · 风格七维扩取值 · 标题块固定高度 |
| `04_record.md` | `Mark.{axis_id, mark_shape}` · `Element.text` · 容差是参数 |
| `05_output.md` | 抽查标注集保持基准口径 · 加整页 markdown · title 与 caption 分开 · 消融加密度档与权重预设两行 |
