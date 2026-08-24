"""Turning one pipeline run into the report page.

    python -m chartgen.cli run --scenarios 6 --set run_id=live
    python tools/build_report.py data/generated/live

The report is one self-contained HTML file: every image is embedded, so it can be
opened or sent anywhere on its own. It is laid out the way `plan/plan.html` lays out
the plan -- one tab per stage -- and it takes its stylesheet out of that file at build
time, so the two cannot drift apart.

Nothing here is written by hand. Every number on the page is read back off the
artifacts the run left behind, which is what makes the page evidence rather than a
description.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from chartgen.common import readback as rb  # noqa: E402
from chartgen.common.rng import derive  # noqa: E402
from chartgen.common import serde  # noqa: E402
from chartgen.interfaces.figure import FigureSpec  # noqa: E402
from chartgen.interfaces.record import Record  # noqa: E402
from chartgen.interfaces.style import STYLE_DOMAINS  # noqa: E402
from chartgen.interfaces.table import TableSchema  # noqa: E402
from chartgen.s01_data.pool import TARGET_ROWS  # noqa: E402
from chartgen.registry import conditions as CONDITIONS  # noqa: E402
from chartgen.registry.charts import CHARTS, DENSITY_BANDS, GRID  # noqa: E402
from chartgen.s05_output import verify as V  # noqa: E402
from chartgen.s05_output.export import TARGETS, build as build_targets  # noqa: E402
from tools import reportkit  # noqa: E402
from tools.reportkit import (  # noqa: E402
    page_document,
    band, bar, card, code, css, embed, esc, figure_pair, flow_diagram, note,
    table, tags, tr,
)

#: Where the plan's tabs sit, so a section here can link into the section there.
PLAN = "../plan.html"

#: How many worked examples the last tab carries, and how many go inline per stage.
EXAMPLES = 16

def tabs() -> tuple[tuple[str, str, str], ...]:
    """The tab strip, in the language this build is writing."""
    return (
        ("over", tr("总览", "Overview"), tr("一次运行的产出", "What one run produced")),
        ("s01", tr("01 数据", "01 data"),
         tr("场景 · 脚本 · 意图", "Scenario · script · intents")),
        ("s02", tr("02 选图", "02 figure"),
         tr("构造 · 推导 · 采样", "Constructed · derived · sampled")),
        ("s03", tr("03 渲染", "03 render"),
         tr("边画边记", "Recorded while drawing")),
        ("s04", tr("04 记录", "04 record"),
         tr("可读与自检", "Readability and self-checks")),
        ("s05", tr("05 输出", "05 output"),
         tr("九类训练目标", "Nine kinds of training target")),
        ("ex", tr("例子", "Examples"),
         tr(f"{EXAMPLES} 张图", f"{EXAMPLES} figures")),
    )


# ---------------------------------------------------------------- the run

@dataclass
class Scenario:
    name: str
    folder: Path
    schema: TableSchema
    specs: list[FigureSpec] = field(default_factory=list)
    records: list[Record] = field(default_factory=list)

    @property
    def first(self) -> list[Record]:
        """One style version of each figure."""
        return [r for r in self.records if r.variant == 0]


@dataclass
class Run:
    root: Path
    scenarios: list[Scenario] = field(default_factory=list)

    @property
    def records(self) -> list[Record]:
        return [r for s in self.scenarios for r in s.records]

    @property
    def specs(self) -> list[FigureSpec]:
        return [f for s in self.scenarios for f in s.specs]

    @property
    def marks(self) -> int:
        return sum(len(r.marks) for r in self.records)

    @property
    def readable(self) -> int:
        return sum(1 for r in self.records for m in r.marks if m.readable)

    @property
    def addressable(self) -> int:
        """Marks every segment of whose key is written somewhere on the page.

        The denominator for "how many keep a value target". Counting against every
        mark instead mixes two unrelated reasons for losing one -- a key nothing on
        the page names, and an encoding that cannot reach the tolerance -- and the
        share that comes out says nothing about either.
        """
        return sum(1 for r in self.records for m in r.marks
                   if "not_shown" not in (m.key_src or ()))


def load(root: Path) -> Run:
    run = Run(root)
    for folder in sorted(p for p in root.iterdir() if (p / "schema.json").exists()):
        run.scenarios.append(Scenario(
            folder.name, folder, serde.load(TableSchema, folder / "schema.json"),
            [serde.load(FigureSpec, p) for p in sorted((folder / "specs").glob("*.json"))],
            [serde.load(Record, p) for p in sorted((folder / "records").glob("*.json"))]))
    if not run.scenarios:
        raise SystemExit(f"no scenario artifacts under {root}")
    return run


# ---------------------------------------------------------------- picking examples

def pick(run: Run, count: int) -> list[tuple[Scenario, Record]]:
    """Examples spread over the scenarios, and inside a scenario over the shapes.

    Taken scenario by scenario in turn so the set is a sample of a pipeline rather
    than of one table, and type sets nobody has shown yet go first.
    """
    picked: list[tuple[Scenario, Record]] = []
    seen: set[tuple[str, ...]] = set()
    taken: dict[str, set[str]] = {s.name: set() for s in run.scenarios}
    for fresh in (True, False):
        while len(picked) < count:
            before = len(picked)
            for scenario in run.scenarios:
                if len(picked) >= count:
                    break
                for record in scenario.first:
                    if record.figure_id in taken[scenario.name]:
                        continue
                    types = tuple(sorted({t for p in record.panels for t in p.chart_types}))
                    if fresh and types in seen:
                        continue
                    seen.add(types)
                    taken[scenario.name].add(record.figure_id)
                    picked.append((scenario, record))
                    break
            if len(picked) == before:
                break
    return picked


def spec_of(scenario: Scenario, record: Record) -> FigureSpec | None:
    return next((s for s in scenario.specs if s.figure_id == record.figure_id), None)


def types_of(record: Record) -> list[str]:
    return sorted({t for p in record.panels for t in p.chart_types})


# ---------------------------------------------------------------- overview

#: The code, by what each part is responsible for.
LAYOUT_ZH = """src/chartgen/
├── interfaces/     六份数据接口：阶段之间只通过它们说话
├── registry/       条件表 charts.py · 判定 conditions.py · 可读性 channels.py
├── common/         种子 · 几何 · 像素读回 · 缓存
├── s01_data/       领域池 → 事实表 ＋ 表结构        ← 模型调用 ①
├── s02_figure/     表 → FigureSpec（选图 · 组合 · 投影）← 模型调用 ②（只写字）
├── s03_render/     FigureSpec ＋ 样式 → 图像 ＋ L0/L1（边画边记）
├── s04_record/     RenderOutput → Record（三层 ＋ 可读 ＋ 自检）
├── s05_output/     Record → 训练目标；奖励检查同一份实现
└── report.py       产物的可读视图（图与终端摘要）
src/llmkit/         与本项目无关的模型调用层：调用 · 结构化输出 · 缓存 · 去重"""

LAYOUT_EN = """src/chartgen/
├── interfaces/     six data interfaces: all stages talk only through these
├── registry/       condition table charts.py · predicate conditions.py
│                   · readability channels.py
├── common/         seeds · geometry · pixel readback · cache
├── s01_data/       domain pool → fact table + schema          ← model call (1)
├── s02_figure/     table → FigureSpec (choose · compose · project)
│                                                              ← model call (2), words only
├── s03_render/     FigureSpec + style → image + L0/L1 (recorded while drawing)
├── s04_record/     RenderOutput → Record (3 layers + readability + self-checks)
├── s05_output/     Record → training targets; the reward shares one implementation
└── report.py       the readable view of an artifact (diagrams and a terminal summary)
src/llmkit/         a model-calling layer that knows nothing about this project:
                    calls · structured output · cache · dedup"""


def tab_over(run: Run, stats: dict) -> str:
    out = [note(tr(
        "<b>这一页是一次真实运行的产出。</b>"
        "每个数字都是从跑完留下的产物里读回来的，"
        "图片是当时画出来的那一张，框是当时记下来的那一批。"
        f"一共 {len(run.scenarios)} 个场景，每个场景两次模型调用，"
        "其余全部是程序。"
        '看完这一页往下走：<a href="../../review/index.html">'
        "review/index.html</a> 是长版的总入口——每一步一页、"
        "这次画的每一张图一页、17 种图表类型每种一页，"
        "最后一页讲代码怎么被验的。",
        "<b>This page is what one real run produced.</b> "
        "Every number was read back off the artifacts the run left behind; every image is "
        "the one that was drawn at the time, and every box is one that was recorded then. "
        f"{len(run.scenarios)} scenarios in all, two model calls each, and everything else "
        "is program. "
        'Where to go next: <a href="../../review/index.html">review/index.html</a> '
        "is the long form -- a page per stage, a page holding every figure this run drew, "
        "a page per chart type, and a last page on how the code was verified."))]

    out.append(band(tr("一条数据走完全程", "One row, all the way through"),
                    tr("输出单位是「键 · 值 · 区域」", "The output unit is (key, value, box)")))
    out.append(flow_diagram())
    out.append(table(
        [tr("阶段", "Stage"), tr("输入 → 输出", "In → out"), tr("调模型", "Calls a model"),
         tr("这一步保证什么", "What this step guarantees")], [
        [tr("<b>01 数据</b> <code>s01_data</code>", "<b>01 data</b> <code>s01_data</code>"),
         tr("领域池 → 事实表 ＋ 表结构", "domain pool → fact table + schema"),
         tr("是，一次", "yes, once"),
         tr("场景、脚本、意图一次写出；意图绑定的列是构造出来的",
           "Scenario, script and intents are written together, so an intent\'s columns are "
           "bound by construction")],
        [tr("<b>02 选图</b> <code>s02_figure</code>",
           "<b>02 figure</b> <code>s02_figure</code>"),
         tr("表 ＋ 结构 → FigureSpec", "table + schema → FigureSpec"),
         tr("是，一次", "yes, once"),
         tr("选图全是程序；模型只写图上的字，不选图、不出值",
           "Choosing is all program; the model writes only the words painted on the image")],
        [tr("<b>03 渲染</b> <code>s03_render</code>",
           "<b>03 render</b> <code>s03_render</code>"),
         tr("FigureSpec ＋ 样式 → 图像 ＋ L0/L1", "FigureSpec + style → image + L0/L1"),
         tr("否", "no"),
         tr("边画边记：框来自绘图库的坐标变换，不解析图片",
           "Recorded while drawing: boxes come from the plotting library\'s own coordinate "
           "transform, never from parsing the image")],
        [tr("<b>04 记录</b> <code>s04_record</code>",
           "<b>04 record</b> <code>s04_record</code>"),
         tr("RenderOutput → Record（三层）", "RenderOutput → Record (3 layers)"),
         tr("否", "no"),
         tr("可读性按像素几何判定；三项自检不过就丢图",
           "Readability is decided from pixel geometry; a figure failing any self-check is "
           "dropped")],
        [tr("<b>05 输出</b> <code>s05_output</code>",
           "<b>05 output</b> <code>s05_output</code>"),
         tr("Record → 训练目标", "Record → training targets"),
         tr("否", "no"),
         tr("同一份记录的多个投影；导出范围与粒度写进产物",
           "Several projections of one record; the export scope and granularity are written "
           "into the artifact")],
    ]))
    out.append(card(tr("代码按这个分工摆", "How the code is divided up"),
                    code(tr(LAYOUT_ZH, LAYOUT_EN)) + note(tr(
        "<b>一个文件一件事。</b>被两个阶段用到的东西只能待在 "
        "<code>common/</code>、<code>registry/</code> 或 <code>interfaces/</code>；"
        "阶段之间不互相 import，这一条有静态测试守着。",
        "<b>One file, one responsibility.</b> Anything used by two stages has to live in "
        "<code>common/</code>, <code>registry/</code> or <code>interfaces/</code>; stages "
        "never import each other, and a static test holds that line.")), "src/"))

    total_targets = sum(
        len(figure.get("grounded_table", []))
        for s in run.scenarios for p in sorted((s.folder / "targets").glob("*.json"))
        for figure in json.loads(p.read_text(encoding="utf-8")).get("figures", []))
    out.append(band(tr("这一次跑出了什么", "What this run produced"),
                    stats.get("model", "")))
    out.append(table([tr("项", "Item"), tr("数", "Count"), tr("说明", "Note")], [
        [tr("场景", "Scenarios"), f"<b>{len(run.scenarios)}</b>",
         tr("每个场景一张事实表，一批图",
            "One fact table and one batch of figures each")],
        [tr("模型调用", "Model calls"), f"<b>{len(run.scenarios) * 2}</b>",
         tr("每个场景两次：一次写数据，一次写图上的字",
            "Twice per scenario: one writes the data, one writes the words on the image")],
        [tr("图（FigureSpec）", "Figures (FigureSpec)"), f"<b>{len(run.specs)}</b>",
         tr("选出来要画的图", "The figures chosen to be drawn")],
        [tr("记录（Record）", "Records (Record)"), f"<b>{len(run.records)}</b>",
         tr("同一张图画了两个样式版本，各留一条记录",
            "Each figure was drawn under two style vectors, one record each")],
        [tr("图元", "Marks"), f"<b>{run.marks}</b>",
         tr("一个图元 ＝ 一个可单独指认的形状",
            "One mark = one separately identifiable shape")],
        [tr("键在页面上有出处的图元", "Marks whose key has a source on the page"),
         f"<b>{run.addressable}</b>",
         tr(f"占 {run.addressable / max(run.marks, 1):.1%}；散点用行号寻址，页面上没写",
            f"{run.addressable / max(run.marks, 1):.1%} of all marks; a scatter mark is "
            f"addressed by row number, which the page never writes")],
        [tr("带值目标的图元", "Marks carrying a value target"), f"<b>{run.readable}</b>",
         tr(f"占键有出处那些的 {run.readable / max(run.addressable, 1):.1%}；其余只留定位目标",
            f"{run.readable / max(run.addressable, 1):.1%} of the addressable ones; the "
            f"rest keep only a localization target")],
        [tr("训练目标行", "Training-target rows"), f"<b>{total_targets}</b>",
         tr("grounded_table 一项就有这么多行",
            "That is the grounded_table target alone")],
        [tr("自检通过", "Passed the self-checks"),
         f"<b>{sum(1 for r in run.records if r.selfcheck.passed)}</b>",
         tr("三项自检全过才留下", "A figure is kept only if all three pass")],
    ]))

    out.append(band(tr("每个场景", "The scenarios"),
                    tr("领域由程序从领域池里抽，模型只负责把它写成数据",
                       "The domain is drawn from the pool by program; the model only "
                       "writes it out as data")))
    rows = []
    for s in run.scenarios:
        kinds = collections_counter(f.source.kind for f in s.specs)
        marks = sum(len(r.marks) for r in s.records)
        rows.append([
            f'<code>{s.name}</code>', esc(s.schema.scenario_title),
            f'<span class="n">{s.schema.n_rows}</span>',
            f'<span class="n">{len(s.schema.columns)}</span>',
            f'<span class="n">{len(s.schema.intents)}</span>',
            f'<span class="n">{len(s.specs)}</span>',
            f'<span class="n">{marks}</span>',
            " ".join(f'<span class="tag">{k} {v}</span>' for k, v in kinds.items()),
        ])
    out.append(table(
        [tr("场景", "Scenario"), tr("标题（模型写的）", "Title (written by the model)"),
         tr("行", "Rows"), tr("列", "Columns"), tr("意图", "Intents"),
         tr("图", "Figures"), tr("图元", "Marks"),
         tr("图是怎么来的", "How the figures were chosen")], rows))

    out.append(band(tr("三条选图路径", "The three ways a figure is chosen"),
                    tr("构造 · 推导 · 采样，只有第三条要随机数",
                       "Constructed · derived · sampled; only the third needs a random "
                       "number")))
    kinds = collections_counter(f.source.kind for f in run.specs)
    out.append(table(
        [tr("路径", "Path"), tr("张数", "Figures"), tr("怎么定的", "How it is decided"),
         tr("它的价值", "What it is worth")], [
        [tr("意图图 <code>intent</code>", "Intent figure <code>intent</code>"),
         f'<span class="n">{kinds.get("intent", 0)}</span>',
         tr("意图给定列与聚合，条件表定类型，确定序破平",
            "The intent gives the columns and aggregate, the condition table gives the "
            "type, and a deterministic order breaks ties"),
         tr("只有它的说明文字带图上读不到的信息",
            "Only its caption carries information not readable off the image")],
        [tr("多面板图 <code>panel</code>", "Multi-panel <code>panel</code>"),
         f'<span class="n">{kinds.get("panel", 0)}</span>',
         tr("锚图必须已被单独接受，另一格由关系规则算出",
            "The anchor must already be accepted standalone; the other panel is computed "
            "by the relation rule"),
         tr("同一份视图的成对样本", "A paired sample over one shared view")],
        [tr("叠画图 <code>overlay</code>", "Overlay <code>overlay</code>"),
         f'<span class="n">{kinds.get("overlay", 0)}</span>',
         tr("两个视图进同一个画区，形状必须不同",
            "Two views in one plotting area, and their mark shapes must differ"),
         tr("考的是同一区域里两套框的区分",
            "It tests telling two sets of boxes apart in one area")],
        [tr("轮转图 <code>rotation</code>", "Rotation <code>rotation</code>"),
         f'<span class="n">{kinds.get("rotation", 0)}</span>',
         tr("按族抽 (类型, 列, 聚合)，验证—投影—收，最多 T 次",
            "Draw (type, columns, aggregate) per family; validate, project, admit; up to "
            "T tries"),
         tr("补齐这一批还没有的类型", "It fills in the types the batch does not hold yet")],
    ]))

    out.append(band(tr("画了哪些类型", "Which types were drawn"),
                    tr("17 行条件表，这一次用到的部分",
                       "The part of the 17-row condition table this run used")))
    used = collections_counter(t for f in run.specs for t in f.chart_types)
    rows = []
    for name, count in sorted(used.items(), key=lambda kv: -kv[1]):
        c = CHARTS[name]
        rows.append([f"<code>{esc(name)}</code>", f'<span class="n">{count}</span>',
                     esc(c.family or "—"), f"<code>{esc(c.shape)}</code>",
                     tags(c.mark), tags(c.channel),
                     ", ".join(f"<code>{esc(k)}</code>" for k in c.value_keys)])
    missing = [n for n in CHARTS if n not in used]
    out.append(table(
        [tr("类型", "Type"), tr("张数", "Figures"), tr("视图类", "View class"),
         tr("投影形状", "Projection shape"), tr("图元形状", "Mark shape"),
         tr("编码通道", "Channel"), tr("值字典", "Value dict")], rows))
    if missing:
        from chartgen.s01_data import validate

        empty = set(CHARTS)
        for s in run.scenarios:
            for family, ok in validate.feasibility(s.schema).families.items():
                if ok:
                    empty -= {n for n, c in CHARTS.items() if c.family == family}
        blocked = sorted(n for n in missing if n in empty)
        why = ((tr("；其中 ", "; of these, ") + tags(blocked, ())
                + tr(" 所属的视图类在这六张表上全是空的",
                     " belong to view classes that are empty on all six tables"))
               if blocked else "")
        rejected: dict[str, int] = {}
        for scenario in run.scenarios:
            path = scenario.folder / "log.json"
            if path.exists():
                for reason, n in json.loads(
                        path.read_text(encoding="utf-8")).get("rejected", {}).items():
                    rejected[reason] = rejected.get(reason, 0) + n
        turned = tr("；", "; ").join(
            tr(f"{n} 次候选倒在「{reason}」上", f"{n} candidates fell to \"{reason}\"")
            for reason, n in sorted(rejected.items(), key=lambda kv: -kv[1])[:3])
        out.append(note(
            tr("这一次没抽到的类型：", "Types this run did not draw: ") + tags(missing, ())
            + why
            + tr("。轮转采样偏向这一批还没有的类型，"
                 "但它先被表的声明条件收窄，再被数据条件挡下：",
                 ". The rotation prefers types the batch does not hold yet, but it is "
                 "narrowed first by the table\'s declared conditions and then stopped by "
                 "the data conditions: ")
            + turned
            + tr("。一个类型没画出来，读这两处就知道是哪一关拦的——"
                 "漏斗要求值只降不升，声明得出阶段列不等于那几段的值真的一路下降。",
                 ". When a type is missing, those two places say which gate stopped it -- "
                 "a funnel requires values that only fall, and declaring a stage column "
                 "does not make the values along it actually fall.")))

    logs = [json.loads((s.folder / "log.json").read_text(encoding="utf-8"))
            for s in run.scenarios if (s.folder / "log.json").exists()]
    if logs:
        out.append(band(tr("被挡下来的候选", "Candidates that were stopped"),
                        tr("拒绝的理由都记在案，因为被扔掉的候选不留产物",
                           "Every rejection reason is logged, because a discarded "
                           "candidate leaves no artifact")))
        merged: dict[str, int] = {}
        for log in logs:
            for key, value in (log.get("rejected") or {}).items():
                merged[key] = merged.get(key, 0) + int(value)
        rows = [[f"<code>{esc(k)}</code>", f'<span class="n">{v}</span>', esc(reject_why().get(k, ""))]
                for k, v in sorted(merged.items(), key=lambda kv: -kv[1])]
        dropped = sum(int(log.get("dropped", 0)) for log in logs)
        out.append(table([tr("理由", "Reason"), tr("次数", "Times"),
                          tr("含义", "What it means")], rows))
        out.append(note(tr(
            f"渲染之后被自检丢掉的图：<b>{dropped}</b> 张；"
            f"留下的记录 <b>{len(run.records)}</b> 条。"
            "丢掉的原因写进日志，不重画——重画会改掉已经记下的每一个框。",
            f"Figures dropped by a self-check after rendering: <b>{dropped}</b>; "
            f"records kept: <b>{len(run.records)}</b>. "
            "The reason goes into the log and the figure is not re-rendered -- a re-render "
            "would change every box already recorded.")))

    scenario, record = pick(run, 1)[0]
    out.append(card(tr("一张图和它的记录", "One figure and its record"), figure_pair(
        record, tr(
            "红框是带值目标的图元，灰框只留定位目标，绿框是页面元素。"
            "这两张图之间没有任何标注步骤：右边的框是画左边那张图时逐个写下来的。",
            "Red boxes are marks with a value target, grey ones keep only a localization "
            "target, green ones are page elements. "
            "There is no annotation step between these two images: the boxes on the right "
            "were written down one by one as the image on the left was drawn.")),
        f"{scenario.name} · {record.figure_id}"))
    return "".join(out)


def reject_why() -> dict[str, str]:
    """What each rejection reason means, in the sampler's own terms."""
    return {
        "drawn illegal": tr("抽到的 (类型, 列, 聚合) 不满足列的声明条件，重抽",
                            "The drawn (type, columns, aggregate) does not meet the column "
                            "declarations this type requires; draw again"),
        "conditions": tr("列的声明条件不满足这一类型",
                         "The column declarations do not meet this type\'s conditions"),
        "thin": tr("有格子背后的原始行数低于这一类型要求的每格最少行数",
                   "Some cell is backed by fewer source rows than this type requires per "
                   "cell"),
        "monotone": tr("这一类型要求值只降不升（漏斗），抽到的值不是",
                       "This type requires values that only fall (funnel); the drawn ones "
                       "do not"),
        "redundant": tr("这一批里已经有键集合与图元形状都相同的图",
                        "The batch already holds a figure with the same key set and the "
                        "same mark shape"),
        "variation": tr("所有格子的值几乎一样高，画出来是一条平线",
                        "Every cell is about the same height; drawn, it is a flat line"),
        "distinct": tr("不同的值太少，多数格子会长得一模一样",
                       "Too few different values -- most cells would look identical"),
        "marks": tr("图元数量落在这一类型（加密度档之后）的上下界之外",
                    "The mark count falls outside this type\'s bounds (after the density "
                    "band)"),
        "projection": tr("投影本身失败：没有可用的列组合",
                         "The projection itself failed: no usable column combination"),
        "empty": tr("投影结果为空", "The projection came back empty"),
        "share": tr("最小的那一份占比太小，扇区画出来看不见",
                    "The smallest share is too small for its sector to be visible"),
    }


def collections_counter(items) -> dict:
    out: dict = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


# ---------------------------------------------------------------- 01 data

def prompt_section(title: str, ident: str, body: str, why: str) -> str:
    """One model call's prompt, in full, beside the reason it looks like that.

    The prompts are two of the three things a reader cannot check by looking at a
    figure -- what went in, what came back, and what the rules did with it -- and the
    other two are already on this page.
    """
    return (band(title, ident) + card("", code(body), ident) + note(why))


def author_prompt(run: Run) -> str:
    """The data call as it is actually sent, for the first scenario of this run."""
    from chartgen.s01_data.author import SYSTEM, user_prompt

    domain = run.scenarios[0].schema.origin
    payload = {"id": domain.domain_id, "name": domain.domain, "topic": domain.topic,
               "complexity_tier": domain.complexity_tier or "medium"}
    rows = TARGET_ROWS.get(payload["complexity_tier"], (500, 1000))
    return f"### system\n\n{SYSTEM}\n\n### user\n\n{user_prompt(payload, rows)}"


def title_prompt(run: Run) -> str:
    """The words call as it is actually sent, for the first scenario of this run."""
    from chartgen.s02_figure.title import SYSTEM, request

    scenario = run.scenarios[0]
    return (f"### system\n\n{SYSTEM}\n\n### user\n\n"
            f"{request(scenario.specs, scenario.schema)}")


def pool_section(run: Run) -> str:
    """The domain pool: what it holds, and which part of it this batch drew.

    A batch is a sample of the pool and nothing else records which part of it was
    taken -- the scenario title is written by the model and names neither the
    sub-topic nor the tier -- so both halves are shown: the pool as it stands, and
    the six entries this run drew from it.
    """
    from chartgen.s01_data.pool import Pool

    path = Path("data/domains/pool.json")
    if not path.exists():
        return ""
    pool = Pool.load(path)
    stats = pool.stats()
    tiers = stats["tiers"]
    subjects = stats.get("subjects", 0)
    registers = stats.get("registers", {})
    cells = stats.get("cells", {})
    out = [band(tr("领域池，与这一批抽到的那几条",
                   "The domain pool, and the entries this batch drew"),
                tr(f"{subjects} 个题材 × {len(registers)} 种体裁 ＝ {len(cells)} 个格子，"
                   f"{len(pool.topics)} 个 topic，{len(pool.domains)} 条子领域",
                   f"{subjects} subjects × {len(registers)} registers = {len(cells)} "
                   f"declared cells, {len(pool.topics)} topics, "
                   f"{len(pool.domains)} sub-topics"))]
    out.append(table(
        [tr("复杂度档", "Complexity tier"), tr("子领域数", "Sub-topics"),
         tr("目标行数", "Target rows"), tr("占比", "Share")], [
        [f'<span class="tag">{esc(tier)}</span>', f'<span class="n">{n}</span>',
         f"{TARGET_ROWS[tier][0]}–{TARGET_ROWS[tier][1]}",
         bar(n / max(len(pool.domains), 1))]
        for tier, n in tiers.items()]))
    if registers:
        out.append(card(tr("池的两条轴", "The pool\'s two axes"), table(
            [tr("体裁 register", "Register"), tr("子领域数", "Sub-topics"),
             tr("占比", "Share")],
            [[f'<code>{esc(name)}</code>', f'<span class="n">{n}</span>',
              bar(n / max(len(pool.domains), 1))]
             for name, n in sorted(registers.items(), key=lambda kv: -kv[1])])
            + note(tr(
                "<b>题材说数据是关于什么的，体裁说是谁发布的、发布给谁看。</b>"
                "只按题材问，得到的池子里航空、银行、农业、体育每一条都写成运营看板——"
                "市政交通和临床试验也不例外。体裁决定一个题材用什么词写出来："
                "实体是谁、一行是什么、多久发布一次、数能不能为负。"
                "分类法本身就是停止条件：一个提前停住的目标条数会扔掉已经生成的题材，"
                "而且在文件里不留任何痕迹。",
                "<b>The subject says what the data is about; the register says who "
                "published it and for whom.</b> Asking only for subjects produced a pool "
                "where aviation, banking, farming and sport were every one of them written "
                "as an operations dashboard -- municipal transit and clinical trials "
                "included. A register decides the vocabulary a subject is written in: who "
                "the entities are, what one row is, how often it is published, and whether "
                "the numbers can go negative. The taxonomy is itself the stopping rule: a "
                "target count that stops early throws away topics already generated and "
                "leaves no trace in the file that it did.")),
            "pool.py"))

    stats_path = run.root / "stats.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    seed = derive(int(stats.get("config", {}).get("root_seed", 0)), "report", "pool-sample")
    picked = list(pool.domains)
    order = seed.permutation(len(picked))[:8]
    out.append(card(tr("池里随便抽八条", "Eight entries drawn from the pool at random"),
                    table([tr("子领域", "Sub-topic"), "topic", tr("档", "Tier"),
                           tr("典型实体", "Typical entities"),
                           tr("典型指标", "Typical metrics")], [
        [esc(picked[i].name), esc(picked[i].topic),
         f'<span class="tag">{esc(picked[i].complexity_tier)}</span>',
         tags(list(picked[i].typical_entities_hint)),
         tags([m.get("name", "") for m in picked[i].typical_metrics_hint])]
        for i in order]), "pool.json"))

    drawn = [s for s in run.scenarios if s.schema.origin.domain]
    if drawn:
        out.append(card(tr("这一次抽到的六条", "The entries this run drew"), table(
            [tr("场景", "Scenario"), tr("子领域", "Sub-topic"), "topic",
             tr("档", "Tier"), tr("行", "Rows")], [
                [f'<code>{s.name}</code>', esc(s.schema.origin.domain),
                 esc(s.schema.origin.topic),
                 f'<span class="tag">{esc(s.schema.origin.complexity_tier)}</span>',
                 f'<span class="n">{s.schema.n_rows}</span>']
                for s in drawn])
            + note(tr(
                "抽样按档无放回，某一档发出八成之后重置，所以一个长跑会走遍池子"
                "而不是在少数几条上打转。抽到的那一条随 schema 落盘——"
                "场景标题是模型写的，它既不说子领域也不说档位，"
                "没有这一层就说不清这一批覆盖了池的哪一块。",
                "Sampling is without replacement within a tier and resets once four fifths "
                "of that tier has gone out, so a long run walks the whole pool rather than "
                "circling a few entries. Which entry was drawn is written down beside the "
                "schema: the scenario title is written by the model and names neither the "
                "sub-topic nor the tier, and without this layer nothing says which part of "
                "the pool a batch covered.")), "TableSchema.origin"))
    return "".join(out)


def tab_s01(run: Run) -> str:
    from chartgen.s01_data import validate

    out = [note(tr(
        "<b>一次调用，三样东西：场景说明、声明脚本、意图。</b>"
        "脚本就是形式化之后的场景，把它拆成两次调用会在中间插一层有损的 JSON，"
        "而且没有回到上游的反馈路径。列和意图是一起写出来的，"
        "所以「意图绑定到哪几列」是构造出来的，不是事后推断的。",
        "<b>One call, three things: the scenario prose, the declaration script, and the "
        "intents.</b> "
        "The script <em>is</em> the formalised scenario. Splitting this into two calls "
        "would insert a lossy JSON layer between them, with no feedback path back "
        "upstream. Because the columns and the intents are written together, which columns "
        "an intent binds to holds by construction rather than by inference."))]

    out.append(pool_section(run))

    out.append(band(tr(f"{len(run.scenarios)} 个场景，{len(run.scenarios)} 次调用",
                       f"{len(run.scenarios)} scenarios, {len(run.scenarios)} calls"),
                    tr("领域由程序抽，模型只负责写",
                       "The domain is drawn by program; the model only writes")))
    rows = []
    for s in run.scenarios:
        f = validate.feasibility(s.schema)
        ok = [k for k, v in f.families.items() if v]
        rows.append([f'<code>{s.name}</code>', esc(s.schema.scenario_title),
                     f'<span class="n">{s.schema.n_rows}</span>',
                     f'<span class="n">{len(s.schema.of_kind("category"))}</span>',
                     f'<span class="n">{len(s.schema.of_kind("time"))}</span>',
                     f'<span class="n">{len(s.schema.of_kind("measure"))}</span>',
                     tags(list(f.families), ok)])
    out.append(table(
        [tr("场景", "Scenario"), tr("标题", "Title"), tr("行", "Rows"),
         tr("类别列", "Category cols"), tr("时间列", "Time cols"),
         tr("度量列", "Measure cols"),
         tr("可行的视图类（灰＝空）", "Feasible view classes (grey = empty)")], rows))
    out.append(note(tr(
        "可行性只读声明：类别列的取值列表给出基数，时间列的起止与频率给出点数，"
        "<code>additive</code> 与 <code>ordered</code> 是声明字段。"
        "01 只问每一族是不是非空，从不展开组合。"
        "少于三族非空就把这次答案退回模型重写。",
        "Feasibility reads declarations only: a category column\'s value list gives its "
        "cardinality, a time column\'s start, end and frequency give its point count, and "
        "<code>additive</code> and <code>ordered</code> are declared fields. The data stage "
        "asks only whether each family is non-empty; it never expands the combinations. "
        "Fewer than three non-empty families sends the reply back to the model to be "
        "rewritten.")))

    out.append(prompt_section(
        tr("送给模型的那一次调用", "The call as it is actually sent"),
        tr("author.py · 一次调用，三样东西", "author.py · one call, three things"),
        author_prompt(run),
        tr("领域由程序抽出来填进 <code>## Domain</code>，其余每一段都是写死的。"
           "提示词里<b>不出现任何图表类型</b>——场景来自题材，不来自可视化模板；"
           "意图停在视图类，哪一种图表服务哪一个视图类由列声明在 02 推出来。",
           "The domain is drawn by program and filled into <code>## Domain</code>; every "
           "other section is fixed text. <b>No chart type appears in the prompt</b> -- "
           "scenarios come from the subject matter, not from visualization templates. An "
           "intent stops at the view class, and which chart type serves which view class "
           "is derived from the column declarations in the figure stage.")))

    s = run.scenarios[0]
    out.append(band(tr("一个场景写出来是什么样", "What one scenario comes out as"), s.name))
    out.append(card(tr("① 场景说明", "(1) Scenario prose"),
                    f"<p><b>{esc(s.schema.scenario_title)}</b></p>"
                    f"<p>{esc(s.schema.data_context)}</p>",
                    "scenario_title · data_context"))
    out.append(card(tr("② 声明脚本", "(2) Declaration script"), code(s.schema.script) + note(
        tr("脚本是可执行的：解析、枚举、覆盖检查、执行、结构检查全部是程序。"
           f"跑出来 <b>{s.schema.n_rows}</b> 行，一行一次事件，生成时不做任何聚合。",
           "The script is executable: parsing, enumeration, the coverage check, execution "
           "and the structural check are all program. "
           f"It produced <b>{s.schema.n_rows}</b> rows -- one row per event, with no "
           f"aggregation at generation time.")), "script"))

    rows = []
    for c in s.schema.columns:
        detail = []
        if c.values:
            detail.append(tr("、", ", ").join(c.values[:4])
                          + ("…" if len(c.values) > 4 else ""))
        if c.freq:
            detail.append(f"{c.start} → {c.end}{tr('，', ', ')}{c.freq}")
        if c.unit:
            detail.append(tr(f"单位 {c.unit}", f"unit {c.unit}"))
        flags = []
        if c.additive is not None:
            flags.append("additive" if c.additive else "non-additive")
        if c.ordered:
            flags.append(f"ordered={c.ordered}")
        if c.parent:
            flags.append(f"parent={c.parent}")
        if c.derived_from:
            flags.append(f"derived_from={c.derived_from}")
        rows.append([f"<code>{esc(c.name)}</code>", esc(c.kind),
                     f'<span class="n">{c.cardinality}</span>',
                     esc(c.group or "—"), tr("；", "; ").join(esc(d) for d in detail),
                     tags(flags) if flags else "—"])
    out.append(card(tr("③ 列声明", "(3) Column declarations"), table(
        [tr("列", "Column"), tr("种类", "Kind"), tr("基数", "Cardinality"),
         tr("维度组", "Group"), tr("取值 / 范围", "Values / range"),
         tr("语义", "Semantics")], rows)
                    + (note(tr("数值列之间的依赖：", "Dependencies between measures: ")
                            + tr("，", ", ").join(
                        f"<code>{esc(a)}</code> → <code>{esc(b)}</code>"
                        for a, b in s.schema.dependencies)) if s.schema.dependencies else ""),
                    "columns"))

    rows = [[f'<span class="n">{i.index}</span>', esc(i.sentence),
             ", ".join(f"<code>{esc(c)}</code>" for c in i.columns),
             f"<code>{esc(i.aggregate)}</code>", f'<span class="tag">{esc(i.family)}</span>']
            for i in s.schema.intents]
    out.append(card(tr("④ 意图，已经绑好列", "(4) Intents, columns already bound"), table(
        ["#", tr("问题", "Question"), tr("列", "Columns"), tr("聚合", "Aggregate"),
         tr("视图类", "View class")], rows)
                    + note(tr(
                        "意图停在视图类，不提任何图表类型：类型由条件表从列声明推出来。"
                        "这几句话后面会变成对应那张图的说明文字——"
                        "图上读不出来的那部分信息只有它带着。",
                        "An intent stops at the view class and names no chart type: the "
                        "type is derived from the column declarations by the condition "
                        "table. These sentences later become the caption of the figure "
                        "they produced -- the one place the information that cannot be "
                        "read off the image is carried.")), "intents"))

    head = fact_head(s.folder)
    if head:
        out.append(card(tr("⑤ 跑出来的事实表（前 8 行）",
                           "(5) The fact table it produced (first 8 rows)"),
                        head, "facts.parquet"))
    return "".join(out)


def fact_head(folder: Path, rows: int = 8) -> str:
    path = folder / "facts.parquet"
    if not path.exists():
        return ""
    import pandas as pd

    df = pd.read_parquet(path).head(rows)
    body = [[f'<span class="n">{v:g}</span>' if isinstance(v, (int, float)) else esc(v)
             for v in row] for row in df.itertuples(index=False)]
    return table([esc(c) for c in df.columns], body)


# ---------------------------------------------------------------- 02 figure

def relations() -> tuple[tuple[str, str, str], ...]:
    """What each relationship puts in the second place, in one line."""
    other = tr("另一个画区", "another plotting area")
    same = tr("同一个画区", "the same plotting area")
    return (
        ("small_multiples", other,
         tr("同一个视图重复，每个取值一格；唯一一个图例管多格的",
            "One view repeated, one panel per value; the only relation whose legend covers "
            "several panels")),
        ("facet", other, tr("同一个度量，换一个切法",
                            "The same measure, cut a different way")),
        ("drilldown", other, tr("沿层级往下一层",
                                "One level further down the hierarchy")),
        ("time_split", other, tr("同一个视图，两个时间窗",
                                 "The same view over two time windows")),
        ("dual_metric", other, tr("同一个分组，下一个度量",
                                  "The same grouping, the next measure")),
        ("part_whole", other, tr("比较改成构成",
                                 "A comparison turned into a composition")),
        ("overlay_metric", same, tr("一个分组，两个度量", "One grouping, two measures")),
        ("overlay_slice", same, tr("一个度量，两个切片或两个聚合",
                                   "One measure, two slices or two aggregates")),
        ("overlay_range", same, tr("一个值，加上它周围的散布",
                                   "A value with the spread around it")),
    )


def column_choice(run: Run, logs: dict) -> str:
    """How one figure's columns are settled -- the part that is easiest to mistake
    for a search over candidates."""
    schema = run.scenarios[0].schema
    legal = {name: sum(1 for _ in CONDITIONS.iter_bindings(name, schema))
             for name, spec in CHARTS.items() if spec.tier <= 2}
    total = sum(legal.values())
    drawn = sum(len(s.specs) for s in run.scenarios)
    biggest = sorted(legal.items(), key=lambda kv: -kv[1])[:4]

    out = [band(tr("一张图的列是怎么定下来的", "How a figure\'s columns are settled"),
                tr("三条路各有各的定法，没有候选清单",
                   "Each of the three paths settles them its own way, and none builds a "
                   "candidate list"))]
    out.append(table(
        [tr("机制", "Mechanism"), tr("谁定的列", "What settles the columns"),
         tr("要不要随机数", "Random number"), tr("预算", "Budget")], [
        [tr("意图图", "Intent figure"),
         tr("01 把列和聚合绑在意图上；条件表定类型，并列时按声明顺序破平",
            "The data stage binds columns and aggregate to the intent; the condition table "
            "gives the type, and ties break by declaration order"),
         tr("不要", "no"), tr("每个意图至多一张", "At most one figure per intent")],
        [tr("多面板 · 叠画", "Multi-panel · overlay"),
         tr("锚点是一张已单独通过的图，第二个视图由关系规则算出来",
            "The anchor is a figure already accepted standalone; the second view is "
            "computed by the relation rule"),
         tr("不要", "no"),
         tr("面板 3 · 叠画 3，起点随场景轮转",
            "3 panels · 3 overlays, with the starting relation rotating by scenario")],
        [tr("轮转图", "Rotation figure"),
         tr("先按声明收窄，再抽 (类型, 维度, 时间, 度量, 聚合)",
            "Narrow by the declarations first, then draw (type, dims, time, measures, "
            "aggregate)"),
         tr("要", "yes"),
         tr("补到 k_max，每族至多 8 次",
            "Fill up to k_max, at most 8 tries per family")],
    ]))
    out.append(card(
        tr("轮转抽之前先收窄，这一步只读声明",
           "The rotation narrows before it draws, reading declarations only"),
        table([tr("先看", "What it looks at"), tr("收窄成什么", "What it narrows to")], [
        [tr("类型", "Type"),
         tr("本族内梯队够低的类型，且<b>优先只从这一批还没画过的</b>里面均匀抽",
            "Types in this family whose tier is low enough, drawn uniformly and "
            "<b>preferring the ones the batch does not hold yet</b>")],
        [tr("类别列", "Category columns"),
         tr("类型要求 <code>ordered=\"stage\"</code> 时，只留声明为阶段的列",
            "When the type requires <code>ordered=\"stage\"</code>, only columns declared "
            "as stages remain")],
        [tr("度量列", "Measure columns"),
         tr("类型要求可加时，只留 <code>additive=True</code> 的列",
            "When the type requires additivity, only <code>additive=True</code> columns "
            "remain")],
        [tr("列数", "How many columns"),
         tr("在类型声明的上下界之间均匀抽，然后不放回地取列——<b>列的顺序也是抽的</b>，"
            "它决定键的顺序和轴与图例的分工",
            "Drawn uniformly between the type\'s declared bounds, then columns are taken "
            "without replacement -- <b>their order is drawn too</b>, and it decides the "
            "key order and the division of work between axis and legend")],
        [tr("聚合", "Aggregate"),
         tr("投影形状唯一确定时直接取；分组标量则在"
            "「形状允许的」∩「这个度量允许的」里抽",
            "Taken directly when the projection shape determines it; for a grouped scalar "
            "it is drawn from what the shape allows intersected with what this measure "
            "allows")],
    ]) + note(tr(
        "收窄之后再抽，抽完再过一次条件检查——不合法就整条丢掉重抽。"
        "这就是「读声明」和「枚举候选」的区别。",
        "It narrows, draws, and then runs the condition check again -- an illegal draw is "
        "discarded whole and redrawn. That is the difference between reading declarations "
        "and enumerating candidates.")), "draw_binding"))
    out.append(card(
        tr("收下来之前过两组判断，便宜的先失败",
           "Two groups of tests before admission, cheapest first"),
        table([tr("组", "Group"), tr("判据", "Test")], [
        [tr("数据条件", "Data conditions"),
         tr("非空 → 图元数落在密度档的区间内 → 不同值的个数够 → "
            "变异系数 ≥ 0.02 → 每格行数够 → 单调递减（漏斗）→ 最小份额（饼）",
            "non-empty → mark count inside the density band → enough distinct values → "
            "coefficient of variation ≥ 0.02 → enough rows per cell → monotone fall "
            "(funnel) → minimum share (pie)")],
        [tr("冗余", "Redundancy"),
         tr("签名 ＝（全部视图的分组键并集，图元形状去重后的有序元组）。"
            "批次里已有同签名就拒。<b>没有阈值，也没有配额</b>",
            "The signature is (the union of every view\'s group keys, the deduplicated "
            "ordered tuple of mark shapes). A candidate matching one already in the batch "
            "is rejected. <b>No threshold, and no quota</b>")],
    ]), "admit"))
    out.append(card(tr("为什么不枚举", "Why it does not enumerate"), note(tr(
        f"把 <code>{esc(schema.scenario_id)}</code> 这一套声明下的合法绑定全部枚举出来，"
        f'共 <span class="n">{total}</span> 条'
        + "（" + "、".join(f"{esc(k)} {v}" for k, v in biggest) + " …）。"
        f'这一次整个批次一共发了 <span class="n">{drawn}</span> 张图。'
        "每一条候选都要走一遍完整投影才能判，所以三条路都不构造清单："
        "生成器是惰性的、有序的、取到第一条能用的就停。",
        f"Enumerating every legal binding under the declarations of "
        f"<code>{esc(schema.scenario_id)}</code> gives "
        f'<span class="n">{total}</span> of them'
        + " (" + ", ".join(f"{esc(k)} {v}" for k, v in biggest) + " …). "
        f'The whole batch shipped <span class="n">{drawn}</span> figures. '
        "Judging any one candidate needs a full projection pass, so none of the three "
        "paths builds a list: the generator is lazy and ordered, and stops at the first "
        "usable entry.")), "iter_bindings"))
    return "".join(out)


def tab_s02(run: Run) -> str:
    logs = {s.name: json.loads((s.folder / "log.json").read_text(encoding="utf-8"))
            for s in run.scenarios if (s.folder / "log.json").exists()}
    out = [note(tr(
        "<b>02 不用模型选图，也没有候选清单。</b>"
        "三种图，三套机制，只有第三种要随机数：意图图是构造出来的，"
        "多面板与叠画图是按关系算出来的，轮转图是带拒绝的采样。"
        "枚举每一种合法视图会得到成百上千个候选、每个都要走一遍完整投影，"
        "最后只发十几张图——所以这里从来不枚举。",
        "<b>No model chooses a figure here, and there is no candidate list.</b> "
        "Three kinds of figure, three mechanisms, and only the third needs a random "
        "number: an intent figure is constructed, multi-panel and overlay figures are "
        "computed from a relation, and a rotation figure is sampled with rejection. "
        "Enumerating every legal view would give hundreds to thousands of candidates, each "
        "needing a full projection pass, to ship about a dozen figures -- which is why "
        "nothing here enumerates."))]

    out.append(prompt_section(
        tr("图选定之后写字的那一次调用",
           "The call that writes the words, made after the figures are chosen"),
        tr("title.py · 一个场景一次，整批图一起",
           "title.py · once per scenario, for the whole batch at once"),
        title_prompt(run),
        tr("<b>输入给到声明这一层，越细越好，但一个数值都不给。</b>"
           "起名问的正是「这个列在轴上该叫什么」，能回答它的是列的声明——"
           "类别列的取值列表、时间列的起止与频率、测度列的单位与可加性、层级组、"
           "以及键的每一段从页面哪里读。取值列表是声明字段，"
           "与 <code>emit(n)</code> 跑出来的那些行无关，一行数据都不进提示词。"
           "回来的答案要过两道检查：标题里不许有数字（年份与季度除外），每一列都要有名字。",
           "<b>The input goes down to the declaration layer, in as much detail as "
           "possible, and carries not one data value.</b> "
           "Naming asks exactly what a column should be called on an axis, and what "
           "answers that is the column\'s declaration -- a category column\'s value list, "
           "a time column\'s start, end and frequency, a measure\'s unit and additivity, "
           "the hierarchy groups, and where on the page each key segment is read from. A "
           "value list is a declared field and has nothing to do with the rows "
           "<code>emit(n)</code> produced; no row of data enters the prompt. "
           "The reply passes two checks: no numbers in a title (years and quarters "
           "excepted), and every column must have a name.")))

    out.append(column_choice(run, logs))

    out.append(band(tr("这一批是怎么凑齐的", "How the batch was filled"),
                    tr("每个场景 16 张", "16 figures per scenario")))
    rows = []
    for s in run.scenarios:
        c = logs.get(s.name, {}).get("counts", {})
        layout = logs.get(s.name, {}).get("layout", {})
        rows.append([f'<code>{s.name}</code>',
                     *(f'<span class="n">{c.get(k, 0)}</span>' for k in
                       ("intent", "panel", "overlay", "rotation", "page", "total")),
                     f'<span class="n">{layout.get("multi_panel", 0)}</span>',
                     f'<span class="n">{layout.get("one_plotting_area_two_views", 0)}</span>',
                     esc(logs.get(s.name, {}).get("density_band", ""))])
    out.append(table(
        [tr("场景", "Scenario"), tr("意图", "Intent"), tr("多面板", "Multi-panel"),
         tr("叠画", "Overlay"), tr("轮转", "Rotation"),
         tr("同页成对", "Paired on a page"), tr("合计", "Total"),
         tr("多画区图", "Multi-area figures"),
         tr("一个画区两视图", "One area, two views"),
         tr("密度档", "Density band")], rows))

    intent_figs = [(s, f) for s in run.scenarios for f in s.specs if f.source.kind == "intent"]
    scenario, spec = intent_figs[0]
    intent = scenario.schema.intents[spec.source.intent_index or 0]
    view = spec.views[0]
    binding = view.binding
    chart = CHARTS[binding.chart_type]
    record = next((r for r in scenario.first if r.figure_id == spec.figure_id), None)
    trace = (
        tr(f"<p><b>意图 #{intent.index}</b>：{esc(intent.sentence)}<br>"
           f"绑定的列 {', '.join(f'<code>{esc(c)}</code>' for c in intent.columns)}，"
           f"聚合 <code>{esc(intent.aggregate)}</code>，视图类 ",
           f"<p><b>Intent #{intent.index}</b>: {esc(intent.sentence)}<br>"
           f"bound columns "
           f"{', '.join(f'<code>{esc(c)}</code>' for c in intent.columns)}, "
           f"aggregate <code>{esc(intent.aggregate)}</code>, view class ")
        + f'<span class="tag">{esc(intent.family)}</span></p>'
        + table([tr("从意图拿到的", "From the intent"),
                 tr("条件表给出的", "From the condition table"),
                 tr("投影出来的", "From the projection")], [[
            tr(f"维度 {', '.join(f'<code>{esc(d)}</code>' for d in binding.dims) or '—'}<br>"
               f"时间 <code>{esc(binding.time or '—')}</code><br>"
               f"度量 {', '.join(f'<code>{esc(m)}</code>' for m in binding.measures)}<br>"
               f"聚合 <code>{esc(binding.aggregate)}</code>",
               f"dims {', '.join(f'<code>{esc(d)}</code>' for d in binding.dims) or '—'}<br>"
               f"time <code>{esc(binding.time or '—')}</code><br>"
               f"measures "
               f"{', '.join(f'<code>{esc(m)}</code>' for m in binding.measures)}<br>"
               f"aggregate <code>{esc(binding.aggregate)}</code>"),
            tr(f"类型 <code>{esc(chart.name)}</code>，第 {chart.tier} 梯队<br>"
               f"投影形状 <code>{esc(chart.shape)}</code><br>"
               f"图元形状 {tags(chart.mark)}，编码 {tags(chart.channel)}<br>"
               f"键的来源 {tags(binding.key_sources)}",
               f"type <code>{esc(chart.name)}</code>, tier {chart.tier}<br>"
               f"projection shape <code>{esc(chart.shape)}</code><br>"
               f"mark shape {tags(chart.mark)}, channel {tags(chart.channel)}<br>"
               f"key sources {tags(binding.key_sources)}"),
            tr(f"{len(view.data)} 个格子<br>", f"{len(view.data)} cells<br>")
            + "<br>".join(f"<code>{esc(' · '.join(d.key))}</code> = "
                          f"{' '.join(f'{k} {v:.4g}' for k, v in d.values.items())}"
                          + tr(f"（{d.rows} 行）", f" ({d.rows} rows)")
                          for d in view.data[:5])]])
        + note(tr(
            "这一步没有随机数：意图定了列与聚合，条件表定了类型，"
            "并列时按确定的顺序破平。同一张表、同一个意图，每次跑出来是同一张图。",
            "No random number enters this step: the intent fixes the columns and the "
            "aggregate, the condition table fixes the type, and a deterministic order "
            "breaks ties. The same table and the same intent give the same figure every "
            "time.")))
    out.append(band(tr("① 意图图：构造出来的", "(1) Intent figure: constructed"),
                    f"{scenario.name} · {spec.figure_id}"))
    out.append(card(tr("一句问题走到一张图", "One question, followed to one figure"),
                    trace, f"{spec.figure_id} · {chart.name}"))
    if record:
        out.append(card(tr("画出来 · 记下来", "Drawn · recorded"),
                        figure_pair(record), record.figure_id))
    out.append(card(tr("模型写的字", "The words the model wrote"),
                    table([tr("位置", "Role"), tr("文字", "Text")], [
        [f"<code>{esc(text.role)}</code>", esc(text.text)] for text in spec.texts])
        + note(tr(
            "<b>说明文字（caption）不画在图上</b>，它是训练目标："
            f"{esc(spec.caption)}<br>"
            "标题是画上去的，所以要查数字——图上写着的数会被当成事实读。",
            "<b>The caption is not drawn on the image</b>; it is a training target: "
            f"{esc(spec.caption)}<br>"
            "A title <em>is</em> painted on, which is why it is checked for numbers -- a "
            "number written on an image is read as truth there.")), "texts"))

    out.append(band(tr("② 推导图：按关系算出来的",
                       "(2) Derived figure: computed from a relation"),
                    tr("六种进另一个画区，三种进同一个",
                       "Six go into another plotting area, three into the same one")))
    used = collections_counter(f.relation for f in run.specs if f.relation)
    rows = [[f"<code>{esc(name)}</code>", esc(where), esc(what),
             f'<span class="n">{used.get(name, 0)}</span>']
            for name, where, what in relations()]
    out.append(table([tr("关系", "Relation"),
                      tr("第二个视图放哪", "Where the second view goes"),
                      tr("它是什么", "What it is"),
                      tr("这次画了", "Drawn this run")], rows))
    derived = [(s, f) for s in run.scenarios for f in s.specs if f.relation]
    rows = [[f'<code>{s.name}</code>', f"<code>{esc(f.figure_id)}</code>",
             f"<code>{esc(f.relation)}</code>",
             f"<code>{esc(f.source.anchor_figure_id or '—')}</code>",
             esc(f.layout), f'<span class="n">{len(f.panels)}</span>',
             tags(sorted(set(f.chart_types))), esc((f.caption or "")[:80])]
            for s, f in derived[:14]]
    out.append(table([tr("场景", "Scenario"), tr("图", "Figure"), tr("关系", "Relation"),
                      tr("锚图", "Anchor"), tr("版式", "Layout"),
                      tr("画区", "Plotting areas"), tr("类型", "Types"),
                      tr("说明文字", "Caption")], rows))
    out.append(note(tr(
        "锚图必须是<b>已经作为单图被接受</b>的那张，"
        "所以共享的那一份视图白得到一对样本；另一格由关系规则算出来，不再抽。"
        "叠在同一个画区里的两个视图必须是不同的图元形状——"
        "否则两套框会重合，记录里就没有任何东西能把它们分开。",
        "The anchor must be a figure <b>already accepted standalone</b>, so the shared view "
        "yields a paired sample for free; the other panel is computed by the relation rule "
        "rather than drawn. Two views overlaid in one plotting area must use different mark "
        "shapes -- otherwise their boxes coincide and nothing in the record can tell them "
        "apart.")))

    pair = next(((s, f) for s, f in derived if f.layout == "overlay"), None)
    if pair:
        s, f = pair
        rec = next((r for r in s.first if r.figure_id == f.figure_id), None)
        if rec:
            out.append(card(tr("一个画区，两个视图", "One plotting area, two views"),
                figure_pair(rec, tr(
                    "两套框都落在同一个画区里，靠图元形状与键前缀区分。",
                    "Both sets of boxes fall inside the same plotting area, told apart by "
                    "mark shape and key prefix.")),
                f"{f.figure_id} · {f.relation}"))

    out.append(band(tr("③ 轮转图：带拒绝的采样",
                       "(3) Rotation figure: sampled with rejection"),
                    tr("抽 (类型, 列, 聚合)，验证—投影—收，最多 T 次",
                       "Draw (type, columns, aggregate), validate, project, admit; up to "
                       "T tries")))
    merged: dict[str, int] = {}
    for log in logs.values():
        for key, value in (log.get("rejected") or {}).items():
            merged[key] = merged.get(key, 0) + int(value)
    out.append(table([tr("拒绝理由", "Rejection reason"), tr("次数", "Times"),
                      tr("含义", "What it means")], [
        [f"<code>{esc(k)}</code>", f'<span class="n">{v}</span>', esc(reject_why().get(k, ""))]
        for k, v in sorted(merged.items(), key=lambda kv: -kv[1])]))
    skipped = [(name, line) for name, log in logs.items() for line in log.get("skipped", [])]
    out.append(card(tr("采样自己写下来的账", "The sampler\'s own log"),
                    table([tr("场景", "Scenario"), tr("记了什么", "What it wrote")], [
        [f'<code>{esc(n)}</code>', esc(line)] for n, line in skipped[:16]])
        + note(tr(
            "<b>多样性是准入判据，不是配额。</b>"
            "这一批里已经有键集合与图元形状都相同的图，就退回重抽——没有阈值要调。"
            "这一对之所以是对的，因为输出单位就是「键 · 值 · 区域」。",
            "<b>Diversity is an admission test, not a quota.</b> "
            "A candidate is redrawn when the batch already holds a figure with the same key "
            "set and the same mark shape -- there is no threshold to tune. That pair is the "
            "right one because the output unit is (key, value, box).")), "log.json"))
    return "".join(out)


# ---------------------------------------------------------------- 03 render

def layout_diagram(record: Record) -> str:
    """The frozen layout, drawn to scale: the bands, the margins, the plotting area.

    Every rectangle is taken from the record and from the band table, so the picture
    cannot drift from the geometry it describes.
    """
    from chartgen.s03_render.draw.canvas import Canvas

    canvas = Canvas(record.style)
    w, h = record.image_size
    margins = canvas.margins
    plot = canvas.full_rect()
    # Read off the composed layout rather than off a table of bands, so a block that
    # moved to another edge moves in the picture too.
    holds = {"text": tr("图号 · 标题 · 副标题 · 单位",
                        "figure number · title · subtitle · unit"),
             "legend": tr("外置图例", "legend outside the plot"),
             "foot": tr("出处 · 注", "source · note")}
    named = {"text": tr("文字块", "text block"), "legend": tr("图例块", "legend block"),
             "foot": tr("页脚块", "footer block")}
    bands = [(b.name, named.get(b.name, b.name), holds.get(b.name, "")) for b in
             (record.layout.blocks or canvas.layout.blocks)]
    pad, label = 108.0, 22.0
    vw, vh = w + pad * 2, h + pad * 2 + label
    parts = [f'<svg viewBox="0 0 {vw:.0f} {vh:.0f}" width="100%" '
             'style="max-width:760px;display:block;margin:0 auto" '
             'font-family="ui-monospace,monospace" font-size="13">']
    at = lambda x, y: (x + pad, y + pad)

    parts.append(f'<rect x="{pad}" y="{pad}" width="{w}" height="{h}" '
                 'fill="#fff" stroke="#adb5bd" stroke-width="1.5"/>')
    for span, name, held in bands:
        box = canvas.band(span)
        x, y = at(box.x0, box.y0)
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{box.width:.1f}" '
                     f'height="{box.height:.1f}" fill="#e7f0f8" stroke="#7fa8cc" '
                     'stroke-dasharray="4 3"/>')
        parts.append(f'<text x="{x + 84:.1f}" y="{y + box.height / 2 + 4:.1f}" '
                     f'fill="#31506b">{esc(name)} · {esc(held)}</text>')
    px, py = at(plot.x0, plot.y0)
    parts.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{plot.width:.1f}" '
                 f'height="{plot.height:.1f}" fill="#f6f8fa" stroke="#1f4e79" '
                 'stroke-width="2"/>')
    parts.append(f'<text x="{px + plot.width / 2:.1f}" y="{py + plot.height / 2:.1f}" '
                 'text-anchor="middle" fill="#1f4e79" font-size="15">'
                 f'{tr("画区 plotting area", "plotting area")}</text>')
    parts.append(f'<text x="{px + plot.width / 2:.1f}" y="{py + plot.height / 2 + 20:.1f}" '
                 f'text-anchor="middle" fill="#5b6b7b">'
                 f'[{plot.x0:.0f}, {plot.y0:.0f}, {plot.x1:.0f}, {plot.y1:.0f}]</text>')

    # The four margins, each with an arrow across it and its own number. The two
    # vertical arrows are drawn near the left edge of the plotting area rather than
    # down its middle, where they would cross the band labels.
    column = plot.x0 + 40
    middle = plot.y0 + plot.height / 2
    side = (tr("左", "left"), tr("上", "top"), tr("右", "right"), tr("下", "bottom"))
    arrows = [(0, middle, plot.x0, middle, f'{side[0]} {margins["left"]:g}',
               "middle", 0, -8),
              (column, 0, column, plot.y0, f'{side[1]} {margins["top"]:g}', "end", -8, 0),
              (plot.x1, middle, w, middle, f'{side[2]} {margins["right"]:g}',
               "middle", 0, -8),
              (column, plot.y1, column, h, f'{side[3]} {margins["bottom"]:g}',
               "end", -8, 0)]
    for x0, y0, x1, y1, text, anchor, dx, dy in arrows:
        ax0, ay0 = at(x0, y0)
        ax1, ay1 = at(x1, y1)
        parts.append(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" '
                     'stroke="#c0392b" stroke-width="1.5"/>')
        for end in ((ax0, ay0), (ax1, ay1)):
            parts.append(f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="2.5" '
                         'fill="#c0392b"/>')
        mx, my = (ax0 + ax1) / 2 + dx, (ay0 + ay1) / 2 + dy + 4
        parts.append(f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="{anchor}" '
                     f'fill="#c0392b">{esc(text)}</text>')

    parts.append(f'<text x="{pad:.0f}" y="{pad - 12:.0f}" fill="#5b6b7b">'
                 + tr(f"图片 {w} × {h}，dpi {record.style.dpi}，边距 "
                      f"{esc(record.style.margins)}",
                      f"image {w} × {h}, dpi {record.style.dpi}, margins "
                      f"{esc(record.style.margins)}")
                 + "</text>")
    parts.append(f'<text x="{pad:.0f}" y="{vh - 6:.0f}" fill="#5b6b7b">'
                 + tr("原点在左上角，框写成 [x0, y0, x1, y1]",
                      "origin top-left, boxes written [x0, y0, x1, y1]")
                 + "</text>")
    parts.append("</svg>")
    return "".join(parts)


def tab_s03(run: Run) -> str:
    from chartgen.common.geometry import value_per_pixel
    from chartgen.s03_render.style import MARGIN_SETS

    out = [note(tr(
        "<b>边画边记。</b>每一个图元在被画出来的那一条语句里写下自己的框、键和值，"
        "用的是绘图库自己的坐标变换。先画完再回头解析图片的做法，这里一次都没有用过。"
        "版式在画之前就定死：图片尺寸、dpi、四条边距、画区矩形都是给定的，"
        "自动排版会在事后挪动画区，把已经记下的每一个框悄悄作废。",
        "<b>Recorded while drawing.</b> Every mark writes down its own box, key and values "
        "in the same statement that draws it, using the plotting library\'s own coordinate "
        "transform. Drawing first and parsing the image afterwards is never done here. "
        "The layout is settled before anything is drawn: image size, dpi, the four margins "
        "and the plotting rectangle are all given. Auto-layout moves the plotting area "
        "afterwards and silently invalidates every box already recorded."))]

    record = next(r for r in run.records if len(r.panels) == 1 and r.marks)
    panel = record.panels[0]
    axis = panel.axis("y") or panel.axes[0]
    margins = MARGIN_SETS[record.style.margins]

    out.append(band(tr("这些量分别是什么", "What each of these quantities is"),
                    tr("按比例画出来的，每一个矩形都取自记录",
                       "Drawn to scale; every rectangle is taken from the record")))
    out.append(card("", layout_diagram(record),
                    f"{record.scenario_id} · {record.figure_id}"))
    out.append(note(tr(
        "<b>「冻结」冻的是「给定这套样式向量之后不再动」，不是「所有图共用一套」。</b>"
        "图片尺寸、dpi、边距各是一个样式维度；换一套重画一张图，画区可以不一样，"
        "因为那一次的框是那一次重新记的。自动排版是另一回事——"
        "它在画完之后挪动画区，那时已经记下的框全部失效，而且不报错。",
        "<b>\"Frozen\" means settled for this style vector, not one set for every "
        "figure.</b> Image size, dpi and margins are each a style dimension; redrawing a "
        "figure under another vector may give another plotting area, because that pass "
        "records its own boxes. Auto-layout is the other thing -- it moves the plotting "
        "area after drawing, every box already recorded is then wrong, and nothing "
        "reports it.")))

    out.append(band(tr("冻结的版式", "The frozen layout"),
                    f"{record.scenario_id} · {record.figure_id}"))
    out.append(table([tr("量", "Quantity"), tr("值", "Value"), tr("谁定的", "Set by")], [
        [tr("图片尺寸", "Image size"),
         f'<span class="n">{record.image_size[0]} × {record.image_size[1]}</span>',
         tr(f"样式维度 <code>image_size</code>，"
            f"{len(STYLE_DOMAINS['image_size'].domain)} 档",
            f"style dimension <code>image_size</code>, "
            f"{len(STYLE_DOMAINS['image_size'].domain)} settings")],
        ["dpi", f'<span class="n">{record.style.dpi}</span>',
         tr(f"样式维度 <code>dpi</code>，{len(STYLE_DOMAINS['dpi'].domain)} 档",
            f"style dimension <code>dpi</code>, "
            f"{len(STYLE_DOMAINS['dpi'].domain)} settings")],
        [tr("左 / 上 / 右 / 下边距", "Left / top / right / bottom margin"),
         (f'<span class="n">{margins["left"]:g} / {margins["top"]:g} / '
         f'{margins["right"]:g} / {margins["bottom"]:g}</span>'),
         tr(f"样式维度 <code>margins</code>，"
            f"这一张是 <code>{esc(record.style.margins)}</code>",
            f"style dimension <code>margins</code>; this one is "
            f"<code>{esc(record.style.margins)}</code>")],
        [tr("画区", "Plotting area"),
         f'<span class="n">{[round(v) for v in panel.box.as_tuple()]}</span>',
         tr("图片尺寸减去四条边距，不随内容变",
            "The image size less the four margins, unchanged by content")],
        [tr(f"值轴 <code>{esc(axis.role)}</code>",
            f"Value axis <code>{esc(axis.role)}</code>"),
         tr(f'<span class="n">{axis.value_range} → 像素 '
            f'{tuple(round(p) for p in axis.pixel_range)}</span>',
            f'<span class="n">{axis.value_range} → pixels '
            f'{tuple(round(p) for p in axis.pixel_range)}</span>'),
         tr("记的是画完之后的实际范围",
            "The range actually drawn, written down after the fact")],
        [tr("一个像素代表多少", "What one pixel is worth"),
         f'<span class="n">{value_per_pixel(axis.value_range, axis.pixel_range):.4g}</span>'
         + (f" {esc(axis.label)}" if axis.label else ""),
         tr("可读判定与读回检查都用它",
            "Used by both the readability rule and the readback check")],
    ]))
    out.append(note(tr(
        "<b>空着的带子也占位。</b>画区上方那条文字带、坐标轴标题下面那条图例带、"
        "右边留给第二值轴的地方，有没有东西都是一样宽——"
        "只在需要时才出现的边距会挪动画区，把已经记下的框全部作废。"
        "<b>带子写成它所在那条边距的份额，不写成像素</b>："
        "边距是一个维度，写成像素的带子会在边距变窄时原样留着，"
        "最窄的那一档就会把某一条带挤成零高。",
        "<b>An empty block keeps its room.</b> The text block above the plotting area, the "
        "legend block below the axis title, and the gutter on the right for a second value "
        "axis are the same width whether or not they hold anything -- a margin that "
        "appeared only when needed would move the plotting area and void every box already "
        "recorded. "
        "<b>A block is written as a share of the margin it sits in, not in pixels</b>: the "
        "margin is itself a style dimension, and a block fixed in pixels would keep its "
        "size as the margin narrowed, until the narrowest setting squeezed some block to "
        "zero height.")))

    out.append(band(tr("样式向量", "The style vector"),
                    tr(f"{len(STYLE_DOMAINS)} 个维度，一张声明表",
                       f"{len(STYLE_DOMAINS)} dimensions, one declared table")))
    groups: dict[str, list[str]] = {}
    for name, dim in STYLE_DOMAINS.items():
        groups.setdefault(dim.group or tr("其他", "other"), []).append(name)
    out.append(table([tr("组", "Group"), tr("维度数", "Dimensions"),
                      tr("维度", "Which")], [
        [esc(g), f'<span class="n">{len(names)}</span>', tags(names)]
        for g, names in sorted(groups.items(), key=lambda kv: -len(kv[1]))]))
    rows = [[f"<code>{esc(name)}</code>", esc(d.group),
             f'<span class="n">{len(d.domain)}</span>',
             f"<code>{esc(d.default)}</code>",
             tr("是", "yes") if d.readable else tr("否", "no"),
             f"<code>{esc(d.draws)}</code>"]
            for name, d in STYLE_DOMAINS.items()]
    out.append(card(
        tr("每一个维度都写明它由谁画、会不会改变可读性",
           "Every dimension states what draws it and whether it changes readability"),
        table([tr("维度", "Dimension"), tr("组", "Group"), tr("取值数", "Values"),
               tr("默认", "Default"), tr("影响可读性", "Affects readability"),
               tr("画它的函数", "Drawn by")], rows)
        + note(tr("两个元测试读这张表："
                  "每一个声明的取值必须真有一条绘制分支；"
                  "标了「不影响可读性」的维度，重画之后记录下来的答案必须逐位相同。",
                  "Two meta-tests read this table: every declared value must have a drawing "
                  "branch, and a dimension marked as not affecting readability must leave "
                  "the recorded answers bit-identical after a redraw.")),
        "STYLE_DOMAINS"))

    pairs = [(a, b) for a in run.records for b in run.records
             if a.figure_id == b.figure_id and a.scenario_id == b.scenario_id
             and a.variant == 0 and b.variant == 1 and len(a.panels) == 1]
    if pairs:
        a, b = pairs[0]
        changed = [(k, getattr(a.style, k), getattr(b.style, k))
                   for k in vars(a.style) if getattr(a.style, k) != getattr(b.style, k)]
        out.append(band(tr("同一张图，两个样式版本", "One figure, two style versions"),
                        f"{a.scenario_id} · {a.figure_id}"))
        v0, v1 = tr("版本 0", "Version 0"), tr("版本 1", "Version 1")
        out.append(f'<div class="diff"><div class="next"><h4>{v0}</h4>'
                   f'<img src="{embed(Path(a.image_path))}" style="width:100%;display:block">'
                   f'</div><div class="now"><h4>{v1}</h4>'
                   f'<img src="{embed(Path(b.image_path))}" style="width:100%;display:block">'
                   "</div></div>")
        out.append(table([tr("改了的维度", "Dimension changed"), v0, v1],
                         [[f"<code>{esc(k)}</code>", f"<code>{esc(x)}</code>",
                           f"<code>{esc(y)}</code>"] for k, x, y in changed[:18]]))
        same = sum(1 for m, n in zip(a.marks, b.marks) if m.values == n.values)
        out.append(note(tr(
            f"两个版本改了 <b>{len(changed)}</b> 个维度，"
            f"{len(a.marks)} 个图元里有 <b>{same}</b> 个的值字典逐位相同——"
            "这一对本身就是一个训练样本，同时也是第三项自检的输入："
            "换一套样式重画，答案必须不变。<b>它不是重试</b>，重画一张图去修它是不允许的。",
            f"<b>{len(changed)}</b> dimensions differ between the two versions, and of "
            f"{len(a.marks)} marks <b>{same}</b> have a bit-identical value dict. "
            "The pair is a training sample in its own right and the input to the third "
            "self-check: redrawn under another style, the answers must not move. "
            "<b>It is not a retry</b> -- re-rendering a figure to fix it is not allowed.")))

    out.append(band(tr("画上去的字都落在图内", "Every drawn word lands inside the image"),
                    tr("现场把这一次的每一个页面元素量了一遍",
                       "Every page element of this run measured here and now")))
    out.append(text_layout(run))

    kinds = collections_counter(d.kind for r in run.records for d in r.degradations)
    if kinds:
        out.append(band(tr("退化", "Degradations"),
                        tr("只收几何有闭式解的那几种",
                           "Only the ones whose geometry has a closed form")))
        out.append(table([tr("种类", "Kind"), tr("张数", "Figures"),
                          tr("框怎么跟着走", "What happens to the boxes")], [
            [f"<code>{esc(k)}</code>", f'<span class="n">{v}</span>',
             esc(degrade_why().get(k, ""))]
            for k, v in kinds.items()]))

    out.append(band(tr("条件表这张网格", "The condition table as a grid"),
                    tr("投影形状 × 图元形状，每一格要么写类型，要么写为什么空",
                       "Projection shape × mark shape; every cell either names its types "
                       "or says why it is empty")))
    shapes = ("grouped_scalar", "grouped_fivenum", "binned_count", "per_row")
    marks = ("rect", "point", "sector", "cell", "boxlike", "band")
    rows = []
    for shape in shapes:
        cells = []
        for mark in marks:
            cell = GRID.get((shape, mark))
            cells.append(tags(list(cell)) if isinstance(cell, tuple)
                         else f'<span class="note" style="margin:0">{esc(cell)}</span>')
        rows.append([f"<code>{esc(shape)}</code>", *cells])
    out.append(table([tr("投影形状", "Projection shape"), *marks], rows))
    out.append(note(tr(
        "绘图代码按<b>图元形状</b>拆，不按图表类型拆：17 种类型，6 种图元形状。"
        "少了哪一种图，读这张网格就能看出来。",
        "The drawing code is split by <b>mark shape</b> rather than by chart type: 17 "
        "types, 6 mark shapes. A missing kind of chart is found by reading this grid.")))

    out.append(band(tr("密度是一段区间，不是一个常数", "Density is a band, not a constant"),
                    tr("档位是消融的轴，不是可调的旋钮",
                       "A band is an ablation axis, not a knob to tune")))
    out.append(table([tr("档", "Band"), tr("图元数上下界", "Mark-count bounds"),
                      tr("事实表至少要几行", "Fact-table rows required")], [
        [f"<code>{esc(b.name)}</code>",
         f'<span class="n">{b.marks[0]} – '
         f'{b.marks[1] if b.marks[1] is not None else "∞"}</span>',
         f'<span class="n">{b.min_rows}</span>'] for b in DENSITY_BANDS]))
    out.append(note(tr(
        "档位只抬<b>关于密度</b>的上界，类型自己的下界一步不动，"
        "最稀的那一档把每一条声明的边界原样复现。"
        "达不到某一档所需行数的表就降档，而不是放松每格的最小行数。",
        "A band raises only the ceiling that is <b>about density</b>; a type\'s own floor "
        "never moves, and the sparsest band reproduces every declared bound exactly. A "
        "table that cannot meet a band\'s row requirement drops the band rather than "
        "relaxing the per-cell minimum.")))
    return "".join(out)


def degrade_why() -> dict[str, str]:
    return {
        "jpeg": tr("像素被压，几何不动，框原样成立",
                   "Pixels compressed, geometry untouched; every box still holds"),
        "noise": tr("加噪声，几何不动", "Noise added, geometry untouched"),
        "blur": tr("模糊，几何不动", "Blurred, geometry untouched"),
        "downscale": tr("整张图缩放，每个框乘同一个系数",
                        "The whole image scaled; every box multiplied by the same factor"),
        "rotate": tr("整张图旋转，框过同一个变换",
                     "The whole image rotated; every box through the same transform"),
        "none": tr("不退化", "Not degraded"),
    }


# ---------------------------------------------------------------- 04 record

def text_layout(run: Run) -> str:
    """Whether the page's own text stayed where the layout says it is.

    Two ways it can fail to, and both make a page-element target describe something
    nobody can read: a block written past the edge of the image, and two blocks
    written over each other.
    """
    import itertools

    off = zero = overlap = pairs = 0
    for record in run.records:
        w, h = record.image_size
        for element in record.elements:
            x0, y0, x1, y1 = element.box.as_tuple()
            off += x0 < -0.5 or y0 < -0.5 or x1 > w + 0.5 or y1 > h + 0.5
            zero += element.box.area <= 0
        texts = [e for e in record.elements
                 if e.text and e.category not in ("Picture", "note")]
        for a, b in itertools.combinations(texts, 2):
            pairs += 1
            small = min(a.box.area, b.box.area)
            overlap += small > 0 and a.box.clip_to(b.box).area / small > 0.5
    elements = sum(len(r.elements) for r in run.records)
    return table([tr("量的是什么", "What was measured"), tr("结果", "Result"),
                  tr("为什么要量", "Why it is measured")], [
        [tr("页面元素总数", "Page elements in total"),
         f'<span class="n">{elements}</span>',
         tr(f"{len(run.records)} 条记录，每一块字、每一个画区各一条",
            f"across {len(run.records)} records -- one per block of text and per "
            f"plotting area")],
        [tr("框跑到图外的", "Boxes outside the image"), f'<span class="n">{off}</span>',
         tr("写到图外的字看不见，记录却给了它一个框",
            "Text past the edge is invisible, and the record still gave it a box")],
        [tr("零面积的框", "Zero-area boxes"), f'<span class="n">{zero}</span>',
         tr("没画出来的东西不该有记录",
            "Nothing undrawn should have a record")],
        [tr("互相压掉一半以上的文字对",
            "Text pairs overlapping by more than half"),
         f'<span class="n">{overlap}</span>',
         tr(f"两两比过 {pairs} 对；压在一起的两块字，两个框都对不上任何人读得出来的东西",
            f"{pairs} pairs compared; two blocks of text on top of each other leave both "
            f"boxes matching nothing a reader can make out")],
    ]) + note(tr(
        "这三个数是这张页面生成时现算的。带子是冻结的，"
        "所以位置不够时让步的是字号，不是版式："
        "文本块按带子回流并按需缩号，刻度先缩号让出位置，"
        "轴标题钉在刻度末尾并按面板边长裁切，图例按可用宽度定字号。"
        "<b>刻度与图例的字不裁</b>——键是从它们身上读出来的，"
        "裁短了就不再指认它标的那个键。",
        "These numbers were computed as this page was built. The blocks are frozen, so what "
        "gives way when room runs short is type size rather than layout: a text block "
        "reflows to its block and shrinks as needed, ticks shrink first to make room, an "
        "axis title is pinned to the end of the ticks and clipped to the panel edge, and a "
        "legend sizes its type to the width available. "
        "<b>Tick and legend text is never cut</b> -- keys are read off them, and a "
        "shortened one no longer names the key it labels."))


def tab_s04(run: Run) -> str:
    from chartgen.registry.channels import MIN_PIXELS, RELATIVE_TOLERANCE

    out = [note(tr(
        "<b>可读性是渲染之后才判的</b>，判据是实际的像素几何加上编码通道。"
        "读不出来的图元丢掉值目标，但保留定位目标——"
        "一张饼图或热力图可以一个值目标都不剩，那是规则在起作用，不是缺陷。",
        "<b>Readability is decided after rendering</b>, from actual pixel geometry plus the "
        "encoding channel. An unreadable mark loses its value target and keeps its "
        "localization target -- a pie or a heatmap can end up with no value target at all, "
        "and that is the rule working, not a defect."))]

    out.append(band(tr("规则", "The rule"),
                    tr("一次写在 chart_types.md §4，代码里只有一份实现",
                       "Stated once in chart_types.md §4; the code holds one "
                       "implementation")))
    out.append(table([tr("情况", "Case"), tr("判定", "Verdict"), tr("容差", "Tolerance")], [
        [tr("值印在图上", "Value printed on the image"), tr("可读", "readable"),
         tr("必须精确相等——印出来的字就是答案",
            "Exact equality -- the printed string is the answer")],
        [tr("颜色", "Colour"), tr("不可读", "not readable"),
         tr("色标量化且非线性，没有闭式的步长",
            "A colour scale is quantised and non-linear; there is no closed-form step")],
        [tr("角度", "Angle"), tr("看份额与半径", "depends on share and radius"),
         tr("步长 <code>3 × 2 / (2π × 半径)</code>，与容差 × 份额比",
            "Step <code>3 × 2 / (2π × radius)</code>, compared against tolerance × share")],
        [tr("长度、位置", "Length, position"),
         tr(f"容差带跨到 {MIN_PIXELS:g} 个像素才算可读",
            f"readable once the tolerance band spans {MIN_PIXELS:g} pixels"),
         tr(f"没写出来的值按 {RELATIVE_TOLERANCE:.0%}",
            f"{RELATIVE_TOLERANCE:.0%} for a value that is not printed")],
        [tr("键在页面上没有出处", "Key with no source on the page"),
         tr("不可读", "not readable"),
         tr("散点用行号寻址，图上没有任何地方写着它",
            "A scatter mark is addressed by row number, which the image never writes")],
    ]))
    out.append(note(tr(
        "<b>两个原因，两张表。</b>一个图元丢掉值目标可能是因为它的键在页面上没有出处，"
        "也可能是因为它的画法在这个容差下够不着——两件事没有关系，混在一个占比里算，"
        "得到的数哪一件都不说明。所以先把「键在页面上没有出处」的挑出去，"
        "剩下的才按编码通道问「量不量得出来」。",
        "<b>Two reasons, two tables.</b> A mark can lose its value target because its key "
        "has no source on the page, or because its encoding cannot reach this tolerance. "
        "The two are unrelated, and one share mixing them says nothing about either. So "
        "the marks whose key has no source are taken out first, and only the rest are "
        "asked whether their channel can be measured.")))

    channels: dict[str, list[int]] = {}
    for record in run.records:
        for mark in record.marks:
            slot = channels.setdefault(mark.channel, [0, 0, 0])
            slot[0] += 1
            slot[1] += bool(mark.readable)
            slot[2] += "not_shown" in (mark.key_src or ())
    rows = sorted(channels.items(), key=lambda kv: -kv[1][0])
    total = [sum(v[i] for _, v in rows) for i in range(3)]
    out.append(table([tr("编码通道", "Channel"), tr("图元", "Marks"),
                      tr("键在页面上没有出处", "Key with no source"),
                      tr("键有出处的", "Key with a source"),
                      tr("其中留下值目标", "of which value targets"),
                      tr("占比", "Share")], [
        [f"<code>{esc(k)}</code>", f'<span class="n">{v[0]}</span>',
         f'<span class="n">{v[2]}</span>', f'<span class="n">{v[0] - v[2]}</span>',
         f'<span class="n">{v[1]}</span>',
         bar(v[1] / (v[0] - v[2])) if v[0] > v[2] else "—"]
        for k, v in rows]
        + [[tr("<b>合计</b>", "<b>Total</b>"), f'<span class="n">{total[0]}</span>',
            f'<span class="n">{total[2]}</span>',
            f'<span class="n">{total[0] - total[2]}</span>',
            f'<span class="n">{total[1]}</span>',
            bar(total[1] / (total[0] - total[2]))]]))
    out.append(note(tr(
        f"<code>position</code> 那 {channels.get('position', [0,0,0])[2]} 个"
        "「键在页面上没有出处」几乎全是散点：它用行号寻址，"
        "而页面上一个字都没写这个行号，这与它的画法无关。"
        "把它们算进分母，位置这一行的占比会掉到一位数，"
        "读起来像是「位置这种画法量不出来」——恰恰相反。",
        f"The {channels.get('position', [0, 0, 0])[2]} <code>position</code> marks whose "
        "key has no source on the page are almost all scatter points: a scatter mark is "
        "addressed by row number, and the page writes that number nowhere. It has nothing "
        "to do with how the mark is drawn. Counting them in the denominator would push the "
        "position row into single digits, reading as \"position cannot be measured\" -- "
        "which is the opposite of the case.")))

    by_type: dict[str, list[int]] = {}
    for record in run.records:
        name = "＋".join(types_of(record))
        slot = by_type.setdefault(name, [0, 0, 0])
        slot[0] += len(record.marks)
        slot[1] += sum(1 for m in record.marks if m.readable)
        slot[2] += sum(1 for m in record.marks if "not_shown" in (m.key_src or ()))
    out.append(card(tr("按图表类型看", "By chart type"), table(
        [tr("类型", "Type"), tr("图元", "Marks"),
         tr("键在页面上没有出处", "Key with no source"),
         tr("其中留下值目标", "of which value targets"), tr("占比", "Share")], [
            [tags(k.split("＋")), f'<span class="n">{v[0]}</span>',
             f'<span class="n">{v[2]}</span>', f'<span class="n">{v[1]}</span>',
             bar(v[1] / (v[0] - v[2])) if v[0] > v[2] else "—"]
            for k, v in sorted(by_type.items(), key=lambda kv: -kv[1][0])])
        + note(tr(
            "散点的键是行号，页面上没有任何地方写着它，所以它的值不问——"
            "问一个答案不在图上的问题，不是难题，是没有正确答案的题。"
            "它的定位目标全部保留。热力图的颜色同理，但理由是另一个：色标量化且非线性，"
            "没有闭式的步长。饼图的角度现在按半径分级——1% 容差下读不出，"
            "5% 容差下份额超过 1/7 的读得出。",
            "A scatter mark\'s key is a row number and nothing on the page writes it, so "
            "its value is not asked about -- a question whose answer is not on the image is "
            "not a hard question, it is a question with no correct answer. Its localization "
            "targets are all kept. A heatmap\'s colour is the same verdict for a different "
            "reason: a colour scale is quantised and non-linear, with no closed-form step. "
            "A pie\'s angle is now graded against its radius -- unreadable at 1% tolerance, "
            "and readable at 5% for shares above 1/7.")), "readable"))

    printed = sum(1 for r in run.records for m in r.marks if m.labeled)
    cells = sum(1 for r in run.records for m in r.marks if m.channel == "printed")
    out.append(note(tr(
        f"这一次有 <b>{printed}</b> 个图元的值印在图上"
        f"（表格图那 {cells} 个单元格在内），答案就是那串字，按字精确匹配。"
        "画满之后还量了一遍：<b>一个标注压掉另一个超过 15% 的，后来的那个不画</b>，"
        "它的图元也就不带印出来的答案，退回按几何估读那一类——"
        "两串字叠在一起，等于两个图元各拿到一个谁也证明不了归它的答案。",
        f"<b>{printed}</b> marks in this run have their value printed on the image (the "
        f"{cells} table-chart cells included); the answer is that string, matched exactly. "
        "After everything was drawn it was measured again: <b>a label overlapping another "
        "by more than 15% is not drawn</b>, so its mark carries no printed answer and falls "
        "back to being estimated from geometry -- two strings on top of each other would "
        "hand two marks one answer neither can be shown to carry.")))

    passed = sum(1 for r in run.records if r.selfcheck.passed)
    ran_style = sum(1 for r in run.records if r.selfcheck.style_invariant is not None)
    ok_style = sum(1 for r in run.records if r.selfcheck.style_invariant is True)
    box_ok = sum(1 for r in run.records if r.selfcheck.box_content is True)
    val_ok = sum(1 for r in run.records if r.selfcheck.value_readback is True)
    out.append(band(tr("三项自检", "The three self-checks"),
                    tr("都在生产路径上，不通过就丢图并记原因",
                       "All on the production path; a failure drops the figure and logs "
                       "why")))
    out.append(table([tr("检查", "Check"), tr("问什么", "What it asks"),
                      tr("这一次的结果", "Result this run")], [
        [tr("框里有没有东西", "Is there anything inside the box"),
         tr("算框内非背景像素的占比",
            "The share of non-background pixels in it"),
         tr(f'<span class="n">{box_ok} / {len(run.records)}</span> 条记录通过',
            f'<span class="n">{box_ok} / {len(run.records)}</span> records passed')],
        [tr("值读不读得回来", "Does the value read back"),
         tr("把框按坐标轴换算回值，和记下来的比",
            "Convert the box back to a value through the axis and compare with the record"),
         tr(f'<span class="n">{val_ok} / {len(run.records)}</span> 条记录通过',
            f'<span class="n">{val_ok} / {len(run.records)}</span> records passed')],
        [tr("换个样式答案变不变", "Does the answer survive a restyle"),
         tr("拿成对的另一个样式版本比，不用重画",
            "Compare against the paired style version; no re-render needed"),
         tr(f'<span class="n">{ok_style} / {ran_style}</span> 条跑了这一项并通过',
            f'<span class="n">{ok_style} / {ran_style}</span> records ran it and passed')],
    ]))

    out.append(note(tr(
        "<b>门槛按图元的形状定，不是一个常数。</b>"
        "填出来的形状（条、格子）按 15% 判；印出来的数按 2% 判，字永远填不满一个格子；"
        "点按 3% 判，因为一个点的框是记号周围一个固定大小的方块——"
        "值从框心读出来，框就不能随样式挑了哪种记号而变，"
        "于是记号填掉方块的多少是记号形状的性质，不是「画没画出来」的性质。"
        "三个数都是量出来的：最薄的一种是 72 dpi 下的竖线记号，填 6%；框挪到空白处填 0%。",
        "<b>The threshold follows the mark shape rather than being one constant.</b> "
        "A filled shape (bar, cell) is judged at 15%; a printed number at 2%, because type "
        "never fills a cell; and a point at 3%, because a point\'s box is a fixed-size "
        "square around the marker -- the value is read from the box centre, so the box "
        "cannot change with which marker the style picked, and how much of the square the "
        "marker fills is then a property of the marker shape rather than of whether "
        "anything was drawn. All three numbers were measured: the thinnest case is a "
        "vertical-line marker at 72 dpi, filling 6%; a box moved onto blank page fills "
        "0%.")))
    reasons = [(r.figure_id, why) for r in run.records for why in r.selfcheck.reasons]
    out.append(note(
        tr(f"<b>{passed} / {len(run.records)}</b> 条记录三项全过。",
           f"<b>{passed} / {len(run.records)}</b> records passed all three.")
        + (tr("失败的图直接丢掉并记下原因，<b>不重画</b>——"
              "重画会改掉已经记下的每一个框。",
              "A failing figure is dropped and its reason logged; it is <b>not "
              "re-rendered</b> -- a re-render would change every box already recorded.")
           if not reasons else "")))
    out.append(note(tr(
        "前两项自检同时就是<b>可验证的强化学习奖励</b>："
        "它们只需要图片和被声称的 <code>(值, 区域)</code>，不需要真值。"
        "<code>common/readback.py</code> 里只有一份实现，"
        "<code>s04_record/selfcheck.py</code> 喂给它渲染器的记录，"
        "<code>s05_output/verify.py</code> 喂给它模型的输出。",
        "The first two self-checks are also the <b>verifiable reinforcement-learning "
        "reward</b>: they need only the image and the claimed <code>(value, box)</code>, "
        "never ground truth. <code>common/readback.py</code> holds the one implementation; "
        "<code>s04_record/selfcheck.py</code> feeds it the renderer\'s record, and "
        "<code>s05_output/verify.py</code> feeds it the model\'s output.")))

    out.append(band(tr("现场再读一遍", "Read again, here and now"),
                    tr("这一页自己把图片重新读回来，不看任何真值",
                       "This page reads the images back itself, with no ground truth")))
    out.append(reverify(run))

    record = next(r for r in run.records
                  if r.variant == 0 and len(r.panels) == 1 and 4 <= len(r.marks) <= 14)
    rows = [[f"<code>{esc(m.mark_id)}</code>",
             f"<code>{esc(' · '.join(m.key))}</code>", tags(m.key_src),
             " ".join(f"{k} {v:.4g}" for k, v in m.values.items()),
             f'<span class="n">{[round(v, 1) for v in m.box.as_tuple()]}</span>',
             f"<code>{esc(m.mark_shape)}</code> / <code>{esc(m.channel)}</code>",
             f'<span class="n">{m.rows}</span>',
             tr("是", "yes") if m.readable else tr("否", "no")]
            for m in record.marks]
    out.append(card(tr("一条记录里的图元层", "The mark layer of one record"), table(
        [tr("图元", "Mark"), tr("键", "Key"), tr("键的出处", "Key source"),
         tr("值", "Values"), tr("框", "Box"), tr("形状 / 通道", "Shape / channel"),
         tr("背后行数", "Rows behind"), tr("值目标", "Value target")], rows)
        + note(tr(
            "三层记录用 <code>(figure_id, panel_id, key)</code> 相连。"
            "键是有序的字符串元组，每一段单独记下它是从哪读出来的："
            "两格图上医院名来自分格标题，科室名来自坐标轴刻度，"
            "一个图一种出处回答不了这两个问题。",
            "The three record layers join on <code>(figure_id, panel_id, key)</code>. "
            "A key is an ordered tuple of strings, and each segment records where it was "
            "read from separately: on a two-panel figure the hospital comes off the panel "
            "title while the department comes off an axis tick, and one source per figure "
            "answers neither question.")),
        f"{record.scenario_id} · {record.figure_id}"))

    legend_record = next((r for r in run.records if r.variant == 0 and len(r.legend) >= 2),
                         record)
    elements = collections_counter(e.category for e in legend_record.elements)
    out.append(card(
        tr("同一条记录的页面元素层与图例层",
           "The page-element and legend layers of one record"),
        table([tr("类别", "Category"), tr("个数", "Count")], [
            [f"<code>{esc(k)}</code>", f'<span class="n">{v}</span>']
            for k, v in elements.items()])
        + table([tr("图例项", "Legend entry"), tr("它管哪些画区", "Panels it covers")], [
            [esc(e.maps_to_category), ", ".join(e.applies_to_panels) or "—"]
            for e in legend_record.legend])
        + note(tr("<b>图例共享要求每一格用同一个系列列</b>，这是 FigureSpec 的约束，"
                  "样式向量改不了它。",
                  "<b>A shared legend requires every panel to use the same series "
                  "column</b> -- a FigureSpec constraint the style vector cannot "
                  "override.")),
        f"{legend_record.scenario_id} · {legend_record.figure_id}"))
    out.append(card(tr("框画回图片上", "The boxes painted back onto the image"),
                    figure_pair(record), record.figure_id))
    return "".join(out)


def reverify(run: Run, sample: int = 12) -> str:
    """Read the images back with the reward's own code and report what it says.

    The point of doing it here rather than quoting the self-check is that this page
    is then evidence rather than a description: nothing below reads a ground-truth
    value, only the image and the claimed `(value, box)`.
    """
    rows, totals = [], [0, 0, 0, 0]
    for _, record in pick(run, sample):
        claims = V.claims_of(record)
        if not claims:
            continue
        judged = V.verify(record.image_path, claims, record.panels,
                          quantum=V.quantum_of_record(record))
        score = V.consistency(judged)
        measured = [j for j in judged if j.value_agrees is not None]
        totals[0] += len(judged)
        totals[1] += sum(j.has_content for j in judged)
        totals[2] += len(measured)
        totals[3] += sum(bool(j.value_agrees) for j in measured)
        rows.append([f"<code>{esc(record.scenario_id)} · {esc(record.figure_id)}</code>",
                     tags(types_of(record)), f'<span class="n">{len(judged)}</span>',
                     bar(score["grounded"]), f'<span class="n">{len(measured)}</span>',
                     bar(score["consistent"]) if measured else "—"])
    head = [tr("图", "Figure"), tr("类型", "Types"), tr("查了几个框", "Boxes checked"),
            tr("框里有东西", "Box has content"), tr("能量的", "Measurable"),
            tr("值对得上", "Value agrees")]
    tail = note(tr(
        f"合计：<b>{totals[1]} / {totals[0]}</b> 个框里确实有东西，"
        f"其中几何上量得到的 <b>{totals[2]}</b> 个里有 <b>{totals[3]}</b> 个"
        f"和记录里的值对得上。"
        "这两个数是在这张页面生成的时候现算的，用的是奖励函数那一份代码，"
        "输入只有图片和被声称的 <code>(值, 区域)</code>。"
        "扇区与色块这两行的「能量的」是 0：角度和颜色量不回值，"
        "第二项检查在那里返回的是「量不了」，不是「判错」。",
        f"Total: <b>{totals[1]} / {totals[0]}</b> boxes really do have something in them, "
        f"and of the <b>{totals[2]}</b> that geometry can measure, <b>{totals[3]}</b> agree "
        f"with the recorded value. "
        "Both numbers were computed as this page was built, using the reward function\'s "
        "own code, whose only inputs are the image and the claimed "
        "<code>(value, box)</code>. "
        "\"Measurable\" is 0 on the sector and cell rows: an angle and a colour cannot be "
        "measured back to a value, and the second check returns \"cannot measure\" there, "
        "not \"wrong\"."))
    return table(head, rows) + tail


# ---------------------------------------------------------------- 05 output

def target_what() -> dict[str, tuple[str, str]]:
    """What each target asks of a model, and which direction the question runs."""
    return {
        "grounded_table": (tr("把整张图转写成 (键, 值, 区域)",
                              "Transcribe the whole figure into (key, value, box)"),
                           tr("图 → 全表", "figure → full table")),
        "spot_check": (tr("抽查若干个键，各报一个值",
                          "Report one value for each of several keys"),
                       tr("键 → 值", "key → value")),
        "mark_locate": (tr("给一句话，指出它对应的区域",
                           "Given a sentence, point at the box it describes"),
                        tr("描述 → 区域", "description → box")),
        "mark_read": (tr("给一个区域，报出它的值", "Given a box, report its value"),
                      tr("区域 → 值", "box → value")),
        "drilldown": (tr("给一句话，报出它背后有多少行原始记录",
                         "Given a sentence, report how many source rows are behind it"),
                      tr("描述 → 行数", "description → row count")),
        "page_elements": (tr("把页面上的每一块框出来并分类",
                             "Box and classify every block on the page"),
                          tr("图 → 版面", "figure → layout")),
        "legend_binding": (tr("图例的每一项管哪些画区",
                              "Which panels each legend entry covers"),
                           tr("图例 → 画区", "legend → panels")),
        "key_source": (tr("键的每一段是从页面哪个地方读到的",
                          "Where on the page each key segment was read from"),
                       tr("键 → 出处", "key → source")),
        "caption": (tr("图上读不出来的那句话",
                       "The sentence that cannot be read off the image"),
                    tr("图 → 说明", "figure → caption")),
    }


def tab_s05(run: Run) -> str:
    from chartgen.s05_output.export import exported_key, key_sources

    out = [note(tr(
        "<b>交出去的形状是参数，不是记录的性质。</b>"
        "<code>key_scope</code> 决定一个图元的地址交出去多少，"
        "<code>granularity</code> 决定一张图一个文件、一页一个还是一批一个，"
        "<code>format</code> 决定那个文件是结构化的目标还是一份 markdown 文档——"
        "粒度与形态是两个问题，谁也不蕴含谁。"
        "<code>output.preset</code> 把这四项打包给一把尺子用，"
        "单独写明的项盖过预设。全部写进产物里：模型交回来的键，"
        "如果不知道它是在哪种范围下被问的，就落不回任何一个图元。",
        "<b>What the exporter hands over is a parameter, not the record\'s shape.</b> "
        "<code>key_scope</code> decides how much of a mark\'s address goes out, "
        "<code>granularity</code> decides one file per figure, per page or per batch, and "
        "<code>format</code> decides whether that file holds the structured targets or a "
        "markdown document -- granularity and format are separate questions, and neither "
        "implies the other. "
        "<code>output.preset</code> packages the four for one benchmark, and anything named "
        "explicitly beside it wins. All of it is written into the artifact: a key the model "
        "returns cannot land back on a mark if the scope it was asked under is unknown."))]

    counts: dict[str, int] = {}
    files = 0
    for scenario in run.scenarios:
        for path in sorted((scenario.folder / "targets").glob("*.json")):
            files += 1
            blob = json.loads(path.read_text(encoding="utf-8"))
            for figure in blob.get("figures", []):
                for name, value in figure.items():
                    if isinstance(value, list):
                        counts[name] = counts.get(name, 0) + len(value)
                    elif name == "caption" and value:
                        counts["caption"] = counts.get("caption", 0) + 1
            counts["page_elements"] = counts.get("page_elements", 0) + len(
                blob.get("page_elements", []))
    what = target_what()
    out.append(band(tr("这一次导出了什么", "What this run exported"),
                    tr(f"{files} 个文件", f"{files} files")))
    out.append(table([tr("目标", "Target"), tr("问什么", "What it asks"),
                      tr("方向", "Direction"), tr("这一次的行数", "Rows this run")], [
        [f"<code>{esc(name)}</code>", esc(what.get(name, ("", ""))[0]),
         esc(what.get(name, ("", ""))[1]),
         f'<span class="n">{counts.get(name, 0)}</span>']
        for name in (*TARGETS, "key_source") if name in counts or name in what]))

    record = next(r for r in run.records
                  if r.variant == 0 and len(r.panels) == 1 and 3 <= len(r.marks) <= 12
                  and any(m.readable for m in r.marks))
    mark = next(m for m in record.marks if m.readable)
    built = build_targets(record, key_scope="mark")
    out.append(band(tr("一个图元走完每一类目标",
                       "One mark through every kind of target"),
                    f"{record.scenario_id} · {record.figure_id}"))
    row = next((r for r in built.grounded_table
                if tuple(r["key"]) == exported_key(mark, record, "mark")), {})
    locate = next((r for r in built.mark_locate if r["box"] == row.get("box")), {})
    read = next((r for r in built.mark_read if r["box"] == row.get("box")), {})
    spot = next((r for r in built.spot_check if r["box"] == row.get("box")), {})
    drill = next((r for r in built.drilldown if r.get("query") == locate.get("query")), {})
    source = next((r for r in built.key_source if r["key"] == row.get("key")), {})
    element = next((e for e in built.page_elements if e.get("text")), {})
    legend = built.legend_binding[0] if built.legend_binding else {}
    out.append(table([tr("目标", "Target"),
                      tr("这一行长什么样", "What one row looks like")], [
        ["<code>grounded_table</code>", code(json.dumps(row, ensure_ascii=False))],
        ["<code>spot_check</code>", code(json.dumps(spot, ensure_ascii=False))],
        ["<code>mark_locate</code>", code(json.dumps(locate, ensure_ascii=False))],
        ["<code>mark_read</code>", code(json.dumps(read, ensure_ascii=False))],
        ["<code>drilldown</code>", code(json.dumps(drill, ensure_ascii=False))],
        ["<code>key_source</code>", code(json.dumps(source, ensure_ascii=False))],
        ["<code>page_elements</code>", code(json.dumps(element, ensure_ascii=False))],
        ["<code>legend_binding</code>",
         code(json.dumps(legend, ensure_ascii=False)) if legend
         else tr("（这张图是单画区的，图例项管的就是那一格，说不出信息）",
                 "(this figure has one plotting area, so a legend entry covers exactly "
                 "that one and says nothing)")],
        ["<code>caption</code>",
         esc(built.caption or tr("（这张图没有说明文字）", "(this figure has no caption)"))],
    ]))
    out.append(note(tr(
        "前六条逐图元，后两条不是：<code>page_elements</code> 一张图一份版面，"
        "<code>legend_binding</code> 一个图例项一行。"
        "单画区的图上一个图例项管的就是那一格，说不出任何信息——"
        "所以这一类的样本只来自多画区且共享图例的图。",
        "The first six are per mark; the last two are not. <code>page_elements</code> is "
        "one layout per figure and <code>legend_binding</code> is one row per legend entry. "
        "On a single-area figure a legend entry covers exactly that one area and says "
        "nothing, so samples of this kind come only from multi-area figures with a shared "
        "legend.")))
    out.append(note(tr(
        "<code>spot_check</code> 这一条的容差不是 1%，因为这个值<b>印在图上</b>："
        "标签写的是整数，那么图上给得出来的答案就是那个整数，"
        "容差正好是这一次取整留下的那点余地，多一分都不给。"
        "字符串本身也一并交出去，精确匹配的评测直接对 <code>printed</code>。",
        "This <code>spot_check</code> row does not carry a 1% tolerance, because the value "
        "is <b>printed on the image</b>: the label writes an integer, so the answer the "
        "image can give is that integer, and the tolerance is exactly the room the rounding "
        "left and not a step more. The string itself goes out too, so an exact-match "
        "evaluation compares against <code>printed</code> directly.")))
    out.append(note(tr(
        "<code>drilldown</code> 里的行数是这个格子背后有多少条原始记录。"
        "它是记录里本来就有的一层，QA 生成不在当前这条线上，"
        "但记录得留着它需要的东西。",
        "The row count in <code>drilldown</code> is how many source records sit behind that "
        "cell. It is a layer the record already carries: QA generation is not on the "
        "current line of work, but the record has to keep what it would need.")))

    out.append(band(tr("同一个图元，三种 key_scope", "One mark, three key scopes"),
                    tr("范围写进产物，因为键要能落回图元",
                       "The scope is written into the artifact, because a key has to land "
                       "back on a mark")))
    wide = widest_key(run) or (record, mark)
    scope_what = {
        "mark": tr("只有画区里面写着的那几段",
                   "Only the segments written inside the plotting area"),
        "panel": tr("加上它所在那一格的标题",
                    "Plus the title of the panel it sits in"),
        "full": tr("再加上只有颜色说得出来的那几段",
                   "Plus the segments that only colour says"),
    }
    out.append(table(["key_scope", tr("交出去的键", "Key handed over"),
                      tr("每一段的出处", "Source of each segment"),
                      tr("交出去多少", "How much goes out")], [
        [f"<code>{esc(scope)}</code>",
         f"<code>{esc(' · '.join(exported_key(wide[1], wide[0], scope)) or '—')}</code>",
         tags(key_sources(wide[1], wide[0], scope)),
         esc(scope_what[scope])] for scope in ("mark", "panel", "full")]))
    out.append(note(tr(
        f"这个图元来自 <code>{esc(wide[0].scenario_id)} · {esc(wide[0].figure_id)}</code>，"
        f"它自己记下来的键是 <code>{esc(' · '.join(wide[1].key))}</code>，"
        f"每一段的出处是 {tags(wide[1].key_src)}——"
        "一段来自坐标轴刻度，一段只有颜色说得出来，分格标题再补一段。"
        "<b>键的每一段各自记出处</b>：同样这几个数画成一格，"
        "那一段就进了图例；画成一页两张图，它就进了小标题。",
        f"This mark comes from "
        f"<code>{esc(wide[0].scenario_id)} · {esc(wide[0].figure_id)}</code>. The key it "
        f"recorded for itself is <code>{esc(' · '.join(wide[1].key))}</code>, and its "
        f"segments were read from {tags(wide[1].key_src)} -- one off an axis tick, one that "
        "only colour says, and one more off the panel title. "
        "<b>Every key segment records its own source</b>: the same numbers drawn as one "
        "panel move that segment into the legend, and drawn as two figures on a page move "
        "it into the headings.")))

    out.append(page_document(run.records))

    out.append(band(tr("奖励：不看真值也能判错",
                       "Reward: wrong answers caught without ground truth"),
                    tr("同一份代码，换一个人写声明",
                       "The same code, with someone else writing the claim")))
    out.append(reward_demo(run))
    return "".join(out)




def widest_key(run: Run) -> tuple[Record, "object"] | None:
    """A mark whose three scopes really are three different keys.

    Picking any mark would show three identical rows on a single-panel figure, which
    is the one case where the parameter makes no difference.
    """
    from chartgen.s05_output.export import exported_key

    for record in run.records:
        if record.variant:
            continue
        for mark in record.marks:
            if len({exported_key(mark, record, s) for s in ("mark", "panel", "full")}) == 3:
                return record, mark
    return None


def reward_demo(run: Run, sample: int = 6) -> str:
    """The same check, on the renderer's own claims and on wrong ones.

    Wrong on purpose in the two ways an answer is usually wrong: the value is off,
    or the region is somewhere else. Neither needs a ground-truth table to catch.
    """
    from dataclasses import replace

    from chartgen.common.geometry import Box

    rows = []
    for _, record in pick(run, sample):
        claims = [c for c in V.claims_of(record)][:12]
        if not claims:
            continue
        quantum = V.quantum_of_record(record)
        img = rb.load_image(record.image_path)
        judged = V.judge(img, claims, record.panels, quantum)
        measurable = sum(1 for j in judged if j.value_agrees is not None)
        honest = V.consistency(judged)
        off_value = [replace(c, values={k: v * 1.25 + 1.0 for k, v in c.values.items()})
                     for c in claims]
        moved = [replace(c, box=Box(c.box.x0 + 240, c.box.y0 - 90,
                                    c.box.x1 + 240, c.box.y1 - 90)) for c in claims]
        wrong = V.consistency(V.judge(img, off_value, record.panels, quantum))
        away = V.consistency(V.judge(img, moved, record.panels, quantum))
        # A sector or a coloured cell has no geometry to measure, so there is no
        # verdict to report rather than a failing one.
        cell = (lambda score: bar(score) if measurable else "—")
        rows.append([f"<code>{esc(record.scenario_id)} · {esc(record.figure_id)}</code>",
                     tags(types_of(record)),
                     f'<span class="n">{len(claims)}</span>',
                     f'<span class="n">{measurable}</span>',
                     cell(honest["consistent"]), cell(wrong["consistent"]),
                     bar(away["grounded"])])
    return table([tr("图", "Figure"), tr("类型", "Types"), tr("声明数", "Claims"),
                  tr("几何上量得到的", "Measurable"),
                  tr("渲染器自己的声明：值对得上",
                     "Renderer\'s own claims: value agrees"),
                  tr("值改成 1.25 倍再加 1", "Values scaled 1.25× plus 1"),
                  tr("框整体挪开 240 × 90 像素：框里还有东西",
                     "Boxes moved 240 × 90 px: box still has content")], rows) + note(tr(
        "中间一列是<b>值错了</b>，右边一列是<b>框指到别处了</b>。"
        "扇区与色块几何上量不了，那一列写「—」——它返回的是「量不了」，不是「判错」。"
        "散点那一行右边仍然不低：图越密，随手挪过去的框越容易压到别的点，"
        "所以两项检查缺一不可——在那种图上挡住错答案的是值，不是框。"
        "两种错都不需要真值就能判出来，这正是 <code>(键, 值, 区域)</code> 这种答案"
        "比 <code>(键, 值)</code> 多出来的性质。"
        "训练时它是奖励，评测时它是一致性指标——在一个完全没有框标注的测试集上也算得出来。",
        "The middle column is a <b>wrong value</b> and the right column a <b>box pointing "
        "somewhere else</b>. "
        "A sector and a heatmap cell cannot be measured by geometry, so that column reads "
        "\"—\" -- what comes back is \"cannot measure\", not \"wrong\". "
        "The scatter row stays high on the right: the denser the figure, the more likely a "
        "box dropped anywhere lands on some other point, which is why both checks are "
        "needed -- on that kind of figure what stops a wrong answer is the value, not the "
        "box. "
        "Neither kind of error needs ground truth to catch, and that is exactly what a "
        "<code>(key, value, box)</code> answer has that a <code>(key, value)</code> answer "
        "does not. In training it is the reward; in evaluation it is a consistency metric "
        "-- computable even on a test set with no box annotations at all."))


# ---------------------------------------------------------------- examples

def tab_examples(run: Run) -> str:
    out = [note(tr(
        f"<b>{EXAMPLES} 张图，取自 {len(run.scenarios)} 个场景。</b>"
        "每一张都给两遍：画出来的那一张，和把记下来的框画回去的那一张。"
        "红框带值目标，灰框只有定位目标，绿框是页面元素。"
        "两张之间没有任何标注步骤。",
        f"<b>{EXAMPLES} figures, taken from {len(run.scenarios)} scenarios.</b> "
        "Each appears twice: the image as drawn, and the same image with the recorded "
        "boxes painted back on. Red boxes carry a value target, grey ones only a "
        "localization target, green ones are page elements. "
        "There is no annotation step between the two."))]
    for scenario, record in pick(run, EXAMPLES):
        spec = spec_of(scenario, record)
        title = spec.text("title") if spec else ""
        head = [
            [tr("图表类型", "Chart type"), tags(types_of(record))],
            [tr("怎么选出来的", "How it was chosen"),
             (f"<code>{esc(spec.source.kind)}</code>"
              + (tr(f" · 关系 <code>{esc(spec.relation)}</code>",
                    f" · relation <code>{esc(spec.relation)}</code>")
                 if spec and spec.relation else "")
              + (tr(f" · 锚图 <code>{esc(spec.source.anchor_figure_id)}</code>",
                    f" · anchor <code>{esc(spec.source.anchor_figure_id)}</code>")
                 if spec and spec.source.anchor_figure_id else "")) if spec else "—"],
            [tr("标题（模型写的）", "Title (written by the model)"), f"<b>{esc(title)}</b>"],
            [tr("版式", "Layout"),
             (f"<code>{esc(spec.layout if spec else '')}</code> · "
              + tr(f"{len(record.panels)} 个画区 · ",
                   f"{len(record.panels)} plotting areas · ")
              + f'<span class="n">{record.image_size[0]}×{record.image_size[1]}</span>')],
            [tr("图元", "Marks"),
             (f'<span class="n">{len(record.marks)}</span>'
              + tr(" 个，其中 ", " drawn, ")
              + f'<span class="n">{sum(1 for m in record.marks if m.readable)}</span>'
              + tr(" 个带值目标", " carrying a value target"))],
        ]
        if record.caption:
            head.append([tr("说明文字（不画在图上）", "Caption (not drawn on the image)"),
                         esc(record.caption)])
        if record.degradations:
            head.append([tr("退化", "Degradations"),
                         tags([f"{d.kind} {d.amount:g}" for d in record.degradations])])
        body = table(["", ""], head) + figure_pair(record)
        marks = record.marks[:6]
        body += table([tr("图元", "Mark"), tr("键", "Key"), tr("值", "Values"),
                       tr("框", "Box"), tr("值目标", "Value target")], [
            [f"<code>{esc(m.mark_id)}</code>", f"<code>{esc(' · '.join(m.key))}</code>",
             " ".join(f"{k} {v:.4g}" for k, v in m.values.items()),
             f'<span class="n">{[round(v, 1) for v in m.box.as_tuple()]}</span>',
             tr("是", "yes") if m.readable else tr("否", "no")] for m in marks])
        if len(record.marks) > len(marks):
            body += note(tr(
                f"另外 {len(record.marks) - len(marks)} 个图元同样各有一条记录。",
                f"The other {len(record.marks) - len(marks)} marks each have a record of "
                f"their own, written the same way."))
        out.append(card(scenario.schema.scenario_title[:56], body,
                        f"{scenario.name} · {record.figure_id} · v{record.variant}"))
    return "".join(out)


# ---------------------------------------------------------------- the page

EXTRA_CSS = """
.n{font-variant-numeric:tabular-nums;white-space:nowrap}
.tag.g{background:var(--raised);color:var(--muted)}
.bar{display:inline-flex;width:96px;vertical-align:middle;margin:0 8px 0 0}
.bar i{background:var(--have)}
figure.draw img,.diff img{border:1px solid var(--line);border-radius:6px}
pre.tree{white-space:pre-wrap;word-break:break-word;max-height:none}
td pre.tree{margin:0;font-size:12px}
.card .body>.scroll:last-child{margin-bottom:0}
"""


def page(run: Run, stats: dict) -> str:
    bodies = {
        "over": tab_over(run, stats), "s01": tab_s01(run), "s02": tab_s02(run),
        "s03": tab_s03(run), "s04": tab_s04(run), "s05": tab_s05(run),
        "ex": tab_examples(run),
    }
    nav = "".join(
        f'<button type="button" data-tab="{key}" '
        f'aria-selected="{"true" if i == 0 else "false"}">{esc(name)}'
        f"<span>{esc(hint)}</span></button>"
        for i, (key, name, hint) in enumerate(tabs()))
    sections = "".join(
        f'<section class="tab" id="tab-{key}"{"" if i == 0 else " hidden"}>{bodies[key]}</section>'
        for i, (key, _, _) in enumerate(tabs()))
    keys = json.dumps([k for k, _, _ in tabs()])
    facts = [(len(run.scenarios), tr("个场景", "scenarios")),
             (len(run.scenarios) * 2, tr("次模型调用", "model calls")),
             (len(run.specs), tr("张图", "figures")),
             (len(run.records), tr("条记录", "records")),
             (run.marks, tr("个图元", "marks"))]
    title = tr("跑一遍流水线 · 产出与证据", "One run, end to end · output and evidence")
    lead = tr(
        f"""这是<strong>一次真实运行</strong>留下的东西，不是手写的示例。
每个场景两次模型调用（{esc(stats.get("model", ""))}），其余全部是程序。
每一页对应流水线的一步，最后一页是 {EXAMPLES} 个完整例子。
计划在 <a href="{PLAN}">plan.html</a>，逐阶段的大量样本与检查证据在
<a href="../../review/index.html">review/index.html</a>。""",
        f"""What follows is what <strong>one real run</strong> left behind, not a
hand-written illustration. Two model calls per scenario
({esc(stats.get("model", ""))}); everything else is program.
One tab per pipeline stage, and a last tab holding {EXAMPLES} complete worked examples.
The plan is in <a href="{PLAN}">plan.html</a>; the per-stage sample pages and the
evidence of what was checked are in
<a href="../../review/index.html">review/index.html</a>.""")
    return f"""<!doctype html>
<html lang="{"en" if reportkit.LANG == "en" else "zh-CN"}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{css()}{EXTRA_CSS}</style></head>
<body>
<header class="masthead"><div class="inner"><div><h1>{
    tr("跑一遍流水线：产出与证据", "One run, end to end: output and evidence")}</h1>
<p>{lead}</p></div>
<div class="facts">{"".join(f'<div class="fact"><b>{n}</b><span>{label}</span></div>'
                            for n, label in facts)}</div></div></header>
<nav class="tabs">{nav}</nav>
<main>{sections}</main>
<script>
var nav = document.querySelector('nav.tabs');
var KEYS = {keys};
function show(key){{
  nav.querySelectorAll('button').forEach(function(b){{
    b.setAttribute('aria-selected', String(b.dataset.tab === key)); }});
  document.querySelectorAll('section.tab').forEach(function(s){{
    s.hidden = s.id !== 'tab-' + key; }});
  if (location.hash.slice(1) !== key) history.replaceState(null, '', '#' + key);
  window.scrollTo(0, 0);
}}
nav.addEventListener('click', function(e){{
  var b = e.target.closest('button'); if (b) show(b.dataset.tab); }});
document.addEventListener('click', function(e){{
  var a = e.target.closest('a[href^="#"]'); if (!a) return;
  var id = a.getAttribute('href').slice(1);
  var el = document.getElementById(id); if (!el) return;
  var sec = el.closest('section.tab');
  if (sec && sec.hidden) {{ show(sec.id.slice(4)); }}
  e.preventDefault(); el.scrollIntoView({{block:'start'}});
}});
if (KEYS.indexOf(location.hash.slice(1)) >= 0) show(location.hash.slice(1));
</script>
</body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="?", default="data/generated/live",
                        help="the run directory to read")
    parser.add_argument("-o", "--out", default="plan/reports/report.html")
    parser.add_argument("--lang", choices=("zh", "en"), default="zh",
                        help="which language to write the page in")
    args = parser.parse_args()

    reportkit.LANG = args.lang
    root = Path(args.run)
    run = load(root)
    stats_path = root / "stats.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(run, stats), encoding="utf-8")
    print(f"{out}  {out.stat().st_size / 1e6:.1f} MB  "
          f"{len(run.scenarios)} scenarios, {len(run.specs)} figures, "
          f"{len(run.records)} records, {run.marks} marks")


if __name__ == "__main__":
    main()
