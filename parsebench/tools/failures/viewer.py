"""The visual companion to INDEX.md: every failure form next to the page it happened on.

The written report can say that 599 points failed because a label would not
associate. It cannot show the legend that made it happen. So the order here is
example-first: each form opens with its count and its one-line definition, and then
immediately shows the parser's own table with the value cell and the key cell marked
-- the geometry is the argument, and the reader does not have to search a page of
markdown to find it.

The left column carries the tabs and, under the open tab, a table of contents built
from the headings the sections already have. Reading the DOM rather than taking a
list from Python is what keeps the two from drifting.

Images sit in `assets/`, one downscaled JPEG per case, and are not tracked -- the
same arrangement the page analysis uses, for the same reason: a preview pane rooted
at the repo will not traverse up into `data/pages/`.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path
from urllib.parse import quote

import evidence as ev
from cases import Case
from index import (IMPROVEMENTS, READING_FORMS, _indistinct, _predicted,
                   _prices, _rate)
from run import Run
from stats import Analysis
from wording import (HOME_ORDER, HOME_ZH, KIND_NOTE, KIND_ORDER, KIND_ZH, POINTS_AT,
                     PRINTED_ZH, component_zh)

ASSET_WIDTH = 900
ASSET_QUALITY = 78

STYLE = """
:root{
  --ground:#F6F7F9; --surface:#FFFFFF; --raised:#EDF0F4;
  --ink:#151A21; --muted:#5A6472; --line:#DFE4EA;
  --gap:#A93E26; --gap-soft:#A93E2614; --have:#2E6A55; --have-soft:#2E6A5512;
  --key:#2F5DA8; --key-soft:#2F5DA814;
  --shadow:0 1px 2px rgba(21,26,33,.05), 0 8px 24px -16px rgba(21,26,33,.25);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1216; --surface:#161C23; --raised:#1E2630;
    --ink:#E7EBF0; --muted:#98A3B1; --line:#28313B;
    --gap:#E4795A; --gap-soft:#E4795A1C; --have:#68BC9A; --have-soft:#68BC9A16;
    --key:#7FA8E8; --key-soft:#7FA8E81C;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#0E1216; --surface:#161C23; --raised:#1E2630;
  --ink:#E7EBF0; --muted:#98A3B1; --line:#28313B;
  --gap:#E4795A; --gap-soft:#E4795A1C; --have:#68BC9A; --have-soft:#68BC9A16;
  --key:#7FA8E8; --key-soft:#7FA8E81C;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
body{margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans","Noto Sans CJK SC","Source Han Sans SC","PingFang SC",
              "Microsoft YaHei",system-ui,sans-serif;
  font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased}
code,.mono,td.num,th.num{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,monospace}
code{background:var(--raised); padding:1px 5px; border-radius:4px; font-size:.88em}
a{color:inherit; text-underline-offset:3px; text-decoration-color:var(--line)}
a:hover{text-decoration-color:currentColor}

.masthead{border-bottom:1px solid var(--line); background:var(--surface)}
.masthead .inner{max-width:1240px; margin:0 auto; padding:24px 24px 18px;
  display:flex; flex-wrap:wrap; gap:18px 40px; align-items:flex-end}
h1{margin:0; font-size:21px; font-weight:600; letter-spacing:-.01em}
.tagline{margin:4px 0 0; color:var(--muted); font-size:13px; max-width:64ch}
.facts{display:flex; flex-wrap:wrap; gap:6px 26px; margin-left:auto}
.fact{display:flex; flex-direction:column}
.fact b{font-family:"IBM Plex Mono",monospace; font-size:17px; font-weight:500;
  font-variant-numeric:tabular-nums}
.fact span{font-size:11px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted)}

.lede-block{border-bottom:1px solid var(--line); background:var(--surface)}
.lede-block .inner{max-width:1240px; margin:0 auto; padding:14px 24px 18px}
.lede-block p{margin:0; font-size:14.5px; max-width:96ch}

.shell{max-width:1240px; margin:0 auto; padding:0 24px 80px;
  display:grid; grid-template-columns:200px minmax(0,1fr); gap:44px; align-items:start}
nav{position:sticky; top:0; padding:26px 0; display:flex; flex-direction:column; gap:2px;
  max-height:100vh; overflow-y:auto}
nav button{appearance:none; border:0; background:none; color:var(--muted); cursor:pointer;
  font:inherit; font-size:14px; text-align:left; padding:7px 12px; border-radius:6px;
  border-left:2px solid transparent; display:flex; justify-content:space-between; gap:10px}
nav button:hover{background:var(--raised); color:var(--ink)}
nav button[aria-selected="true"]{color:var(--ink); font-weight:600;
  border-left-color:var(--gap); background:var(--raised)}
nav button i{font-style:normal; font-family:"IBM Plex Mono",monospace; font-size:12px;
  color:var(--muted); font-variant-numeric:tabular-nums}
ul.toc{list-style:none; margin:2px 0 12px; padding:0 0 0 14px;
  border-left:1px solid var(--line)}
ul.toc li{margin:0}
ul.toc a{display:block; padding:4px 8px; font-size:12.5px; color:var(--muted);
  text-decoration:none; border-radius:5px; line-height:1.35}
ul.toc a:hover{background:var(--raised); color:var(--ink)}
ul.toc a.at{color:var(--gap); background:var(--gap-soft); font-weight:500}

section{padding:26px 0 0}
section[hidden]{display:none}
h2{margin:0 0 6px; font-size:19px; font-weight:600}
h3.band{margin:38px 0 4px; font-size:16px; font-weight:600;
  display:flex; align-items:baseline; gap:12px; flex-wrap:wrap;
  border-top:1px solid var(--line); padding-top:16px}
h3.band span{font-size:12.5px; font-weight:400; color:var(--muted)}
h3:first-of-type{border-top:0; margin-top:20px}
p{margin:0 0 12px} p.lede{color:var(--muted); font-size:14px; max-width:88ch}
.explain{background:var(--surface); border:1px solid var(--line); border-radius:12px;
  padding:14px 18px; margin:12px 0 6px; box-shadow:var(--shadow)}
.explain p:last-child{margin-bottom:0}
.scroll{overflow-x:auto; margin:10px 0 16px}
table{border-collapse:collapse; width:100%; font-size:13.5px}
th,td{border-bottom:1px solid var(--line); padding:6px 10px; text-align:left;
  vertical-align:top}
th{font-weight:600; font-size:12px; letter-spacing:.03em; color:var(--muted);
  text-transform:uppercase; white-space:nowrap}
td.num,th.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
tbody tr:hover td{background:var(--raised)}
.bar{position:relative; height:9px; border-radius:5px; background:var(--raised);
  min-width:110px; overflow:hidden}
.bar i{position:absolute; inset:0 auto 0 0; border-radius:5px; background:var(--have)}
.bar i.low{background:var(--gap)}

.ev{background:var(--surface); border:1px solid var(--line); border-radius:14px;
  margin:16px 0; box-shadow:var(--shadow); display:grid; overflow:hidden;
  grid-template-columns:250px minmax(0,1fr);
  grid-template-areas:"fig body" "vs vs" "tail tail"}
.ev > figure{grid-area:fig; margin:0; background:var(--raised);
  border-right:1px solid var(--line); display:flex; align-items:flex-start}
.ev > figure img{display:block; width:100%; height:auto; max-height:340px;
  object-fit:contain; object-position:top}
.ev > .body{grid-area:body; padding:14px 18px 8px; min-width:0}
.ev > .vs{grid-area:vs}
.ev > .tail{grid-area:tail; padding:0 18px 16px}
.ev.no-image{grid-template-columns:minmax(0,1fr);
  grid-template-areas:"body" "vs" "tail"}
.ev.no-image > figure{display:none}
.vs{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  border-top:1px solid var(--line)}
.vs > div{padding:12px 18px 14px; min-width:0}
.vs > div + div{border-left:1px solid var(--line)}
.vs .bad{background:var(--gap-soft)}
.vs .good{background:var(--have-soft)}
.side-h{font-size:12.5px; font-weight:600; margin:0 0 8px; letter-spacing:.02em}
.vs .bad .side-h{color:var(--gap)}
.vs .good .side-h{color:var(--have)}
.why{font-size:12.5px; color:var(--muted); margin:8px 0 0; line-height:1.55}
.why b{color:var(--ink)}
@media (max-width:1000px){.vs{grid-template-columns:minmax(0,1fr)}
  .vs > div + div{border-left:0; border-top:1px solid var(--line)}}
.ev h4{margin:0 0 4px; font-size:15px; font-weight:600}
.ev .meta{color:var(--muted); font-size:12.5px; margin:0 0 10px}
.ev p{margin:0 0 10px; font-size:14px}
@media (max-width:900px){.ev{grid-template-columns:minmax(0,1fr);
    grid-template-areas:"fig" "body" "vs" "tail"}
  .ev > figure{border-right:0; border-bottom:1px solid var(--line)}}

.rule-line{background:var(--raised); border-radius:8px; padding:7px 11px;
  font-size:13px; margin:0 0 10px}
.rule-line b{font-family:"IBM Plex Mono",monospace}
.grid-cap{font-size:12px; color:var(--muted); margin:0 0 4px}
table.excerpt{font-size:12.5px; font-family:"IBM Plex Mono",monospace}
table.excerpt td{padding:4px 8px; border:1px solid var(--line); white-space:nowrap}
table.excerpt td.head{background:var(--raised); font-weight:600}
table.excerpt td.hit{background:var(--have-soft); color:var(--have); font-weight:600;
  outline:1.5px solid var(--have)}
table.excerpt td.wrong{background:var(--gap-soft); color:var(--gap); font-weight:600;
  outline:1.5px solid var(--gap)}
table.excerpt td.key{background:var(--key-soft); color:var(--key)}
table.excerpt.good td{border-color:var(--have)}
table.excerpt.good td.head{background:var(--have-soft); color:var(--have)}
.egs{display:flex; gap:10px; flex-wrap:wrap; margin:6px 0 18px}
.egs a{display:block; width:150px; text-decoration:none}
.egs img{display:block; width:150px; height:104px; object-fit:cover;
  object-position:top; border:1px solid var(--line); border-radius:8px;
  background:var(--raised)}
.egs span{display:block; font-size:11.5px; color:var(--muted); margin-top:3px;
  line-height:1.35; overflow-wrap:anywhere}
.card p.eg{background:var(--raised); border-radius:8px; padding:8px 11px;
  font-size:13px}
.card p.price{font-size:13px; color:var(--muted)}
.card p.price b,.card p.eg b{color:var(--ink); margin-right:2px}
.verdict{font-size:12px; color:var(--muted); font-family:"IBM Plex Mono",monospace;
  background:var(--raised); border-radius:8px; padding:7px 11px; margin:0 0 10px;
  overflow-x:auto; white-space:pre-wrap; word-break:break-word}
.ctx{font-size:12.5px; color:var(--muted); border-left:2px solid var(--line);
  padding:2px 0 2px 10px; margin:0 0 10px}
.pull{border-left:3px solid var(--gap); padding-left:14px; margin:12px 0; font-size:14px}
.chip{display:inline-block; padding:1px 8px; border-radius:999px; font-size:11.5px;
  border:1px solid var(--line); color:var(--muted); white-space:nowrap}
.chip.gap{background:var(--gap-soft); border-color:transparent; color:var(--gap)}
.chip.have{background:var(--have-soft); border-color:transparent; color:var(--have)}
.chip.key{background:var(--key-soft); border-color:transparent; color:var(--key)}
.two{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:14px}
.card{background:var(--surface); border:1px solid var(--line); border-radius:14px;
  padding:15px 18px; box-shadow:var(--shadow)}
.card h4{margin:0 0 4px; font-size:14.5px}
.card p{margin:0 0 8px; font-size:13.5px}
.card p:last-child{margin-bottom:0}
footer{max-width:1240px; margin:0 auto; padding:0 24px 60px; color:var(--muted);
  font-size:12.5px}
"""

SCRIPT = """
const tabs=[...document.querySelectorAll('nav button')];
tabs.forEach(tab=>{
  const section=document.getElementById(tab.dataset.tab);
  const heads=[...section.querySelectorAll('h3.band')];
  if(!heads.length) return;
  const list=document.createElement('ul');
  list.className='toc'; list.dataset.for=tab.dataset.tab;
  heads.forEach((h,i)=>{
    h.id=tab.dataset.tab+'-h'+i;
    const item=document.createElement('li');
    const a=document.createElement('a');
    a.href='#'+h.id;
    a.textContent=(h.firstChild&&h.firstChild.nodeType===3?h.firstChild.textContent
      :h.textContent).trim();
    a.addEventListener('click',e=>{e.preventDefault();
      h.scrollIntoView({behavior:'smooth',block:'start'});
      history.replaceState(null,'','#'+h.id);});
    item.appendChild(a); list.appendChild(item);
  });
  tab.after(list);
});
const marks=[...document.querySelectorAll('.toc a')];
const show=id=>{
  tabs.forEach(t=>t.setAttribute('aria-selected',String(t.dataset.tab===id)));
  document.querySelectorAll('main > section').forEach(s=>{s.hidden=(s.id!==id)});
  document.querySelectorAll('.toc').forEach(u=>{u.hidden=(u.dataset.for!==id)});
  window.scrollTo({top:0});
};
tabs.forEach(t=>t.addEventListener('click',()=>{
  history.replaceState(null,'','#'+t.dataset.tab); show(t.dataset.tab)}));
const spy=()=>{
  let here=null;
  document.querySelectorAll('main > section:not([hidden]) h3.band').forEach(h=>{
    if(h.getBoundingClientRect().top<140) here=h.id;
  });
  marks.forEach(a=>a.classList.toggle('at',a.getAttribute('href')==='#'+here));
};
addEventListener('scroll',spy,{passive:true});
const wanted=location.hash.slice(1);
const owner=tabs.find(t=>t.dataset.tab===wanted)
  ||tabs.find(t=>wanted.startsWith(t.dataset.tab+'-h'));
show(owner?owner.dataset.tab:tabs[0].dataset.tab);
if(wanted&&!tabs.some(t=>t.dataset.tab===wanted)){
  const target=document.getElementById(wanted);
  if(target) target.scrollIntoView({block:'start'});
}
spy();
"""


def write_assets(stems: list[str], out_dir: Path, pages_dir: Path) -> bool:
    """One downscaled page image per illustrated page. False without Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return False
    directory = out_dir / "assets"
    directory.mkdir(parents=True, exist_ok=True)

    def convert(stem: str) -> None:
        source = pages_dir / f"{stem}.png"
        target = directory / f"{stem}.jpg"
        if target.exists() or not source.exists():
            return
        image = Image.open(source).convert("RGB")
        height = round(ASSET_WIDTH * image.height / image.width)
        image.resize((ASSET_WIDTH, height), Image.LANCZOS).save(
            target, quality=ASSET_QUALITY, optimize=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(convert, sorted(set(stems))))
    return True


def _rich(text: str) -> str:
    """Escape, then turn the markdown the notes are written in into markup."""
    out = escape(text)
    while "**" in out:
        out = out.replace("**", "<b>", 1).replace("**", "</b>", 1)
    while out.count("`") >= 2:
        out = out.replace("`", "<code>", 1).replace("`", "</code>", 1)
    return out


def _bar(value: float, low: bool) -> str:
    return (f'<div class="bar"><i class="{"low" if low else ""}" '
            f'style="width:{max(2.0, value * 100):.1f}%"></i></div>')


def _rate_rows(rows: list[tuple[str, object]]) -> str:
    if not rows:
        return ""
    worst = min(entry.value for _, entry in rows)
    body = ""
    for name, entry in rows:
        low, high = entry.interval
        body += (f'<tr><td>{escape(name)}</td><td class="num">{entry.total}</td>'
                 f'<td class="num">{entry.value:.1%}</td>'
                 f'<td>{_bar(entry.value, entry.value <= worst + 1e-9)}</td>'
                 f'<td class="num">[{low:.0%}, {high:.0%}]</td></tr>')
    return (f'<div class="scroll"><table><thead><tr><th>分档</th><th class="num">点数</th>'
            f'<th class="num">通过率</th><th></th><th class="num">95% 区间</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


# ------------------------------------------------------------------ evidence


def _excerpt(item: ev.Evidence, bad_headers: set[int] | None = None) -> str:
    rows = ""
    bad_headers = bad_headers or set()
    if item.elided_above:
        rows += '<tr><td colspan="99" class="head">⋮</td></tr>'
    for index, line in enumerate(item.rows):
        cells = ""
        for column, cell in enumerate(line):
            kind = cell.kind
            if index == 0 and column in bad_headers and cell.text.strip():
                kind = "wrong"
            cells += f'<td class="{kind}">{escape(ev.tidy(cell.text))}</td>'
        if item.elided_right:
            cells += '<td class="head">…</td>'
        rows += f"<tr>{cells}</tr>"
    return (f'<p class="grid-cap">{escape(item.caption)}</p>'
            f'<div class="scroll"><table class="excerpt"><tbody>{rows}</tbody></table></div>')


def _bad_headers(item: ev.Evidence) -> set[int]:
    """Header cells over a column of numbers that name none of the keys.

    When the metric could not associate a label, this is where it should have been:
    the column the value sits in is a data column, and its header is supposed to say
    which series it is. `Gray` / `Orange` / `Light orange band` all light up.
    """
    if len(item.rows) < 2:
        return set()
    head = item.rows[0]
    if any(cell.kind == "key" for cell in head):
        pass
    numeric = set()
    for column in range(len(head)):
        values = [row[column].text for row in item.rows[1:] if column < len(row)]
        hits = sum(1 for text in values if _looks_numeric(text))
        if values and hits >= max(2, len(values) // 2):
            numeric.add(column)
    return {column for column in numeric
            if column < len(head) and head[column].kind not in ("key", "hit")}


def _looks_numeric(text: str) -> bool:
    stripped = text.strip().replace(",", "").replace("%", "").replace("$", "")
    stripped = stripped.lstrip("-−–").rstrip("xX")
    return bool(stripped) and stripped.replace(".", "", 1).replace(" ", "").isdigit()


def _expected_table(want: ev.Expected) -> str:
    if not want.rows:
        return ""
    head = "".join(f'<td class="head">{escape(name)}</td>' for name in want.header)
    body = "".join("<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
                   for row in want.rows)
    more = (f'<tr><td colspan="{len(want.header)}" class="head">'
            f'⋮ 还有 {want.more} 行</td></tr>' if want.more else "")
    return (f'<div class="scroll"><table class="excerpt good"><tbody>'
            f'<tr>{head}</tr>{body}{more}</tbody></table></div>')


def _evidence_card(case: Case, run: Run, analysis: Analysis, src) -> str:
    """One page: the image, what the parser wrote, and what would have passed."""
    all_verdicts = run.by_page()[case.stem]
    failed = [v for v in all_verdicts if not v.passed]
    passed = len(all_verdicts) - len(failed)
    focus = next((v for v in failed
                  if analysis.diagnoses[(v.rule.stem, v.rule.id)].kind == case.kind),
                 failed[0])
    diagnosis = analysis.diagnoses[(focus.rule.stem, focus.rule.id)]
    item = ev.build(focus, run.pages[case.stem], diagnosis)

    #: For a key that would not associate, the header of the value's own column is
    #: the cell that should have carried it -- marking it says where to look.
    mark = _bad_headers(item) if diagnosis.kind == "label_unlinked" else set()

    keys = " · ".join(f"<code>{escape(label)}</code>" for label in focus.rule.labels)
    context = "".join(f'<p class="why">{_rich(line)}</p>' for line in item.context[:2])
    want = ev.expected(failed)
    return f"""<article class="ev">
  <figure><a href="{src(case.stem)}" target="_blank" rel="noopener">
    <img loading="lazy" src="{src(case.stem)}" alt="{escape(case.stem)}"
      onerror="this.closest('article').classList.add('no-image')"></a></figure>
  <div class="body">
    <h4>{_rich(case.title)}</h4>
    <p class="meta"><code>{escape(case.stem)}</code> ·
      该页 {passed} / {len(all_verdicts)} 通过 ·
      <a href="cases/{quote(case.stem)}/case.md">逐条与整页输出</a></p>
    {_paras(case.what_happened)}
  </div>
  <div class="vs">
    <div class="bad">
      <p class="side-h">✗ 解析器实际写的</p>
      <p class="rule-line">这一条规则要的是 <b>{escape(focus.rule.value)}</b>，
        定位键 {keys}（容差 {focus.rule.tolerance:g}）</p>
      {_excerpt(item, mark)}
      <p class="why"><b>{_rich(item.note)}</b></p>
      {context}
    </div>
    <div class="good">
      <p class="side-h">✓ 写成这样，这一页 {len(failed)} 个点全过</p>
      <p class="rule-line">一行一个值，<b>所有键和值写在同一行</b>——
        判定第三步一次通过，不用任何回退</p>
      {_expected_table(want)}
      <p class="why">这正是我们记录层的形状：一个图元 = 一条
        <code>(键, 值, 区域)</code>。所谓「长表导出」就是把它原样写出来。</p>
    </div>
  </div>
  <div class="tail">
    <p class="verdict">判分程序的原话：{escape(focus.explanation[:200])}</p>
    <div class="pull">{_paras(case.for_the_pipeline)}</div>
  </div>
</article>"""


def _paras(text: str) -> str:
    return "".join(f"<p>{_rich(part)}</p>" for part in text.split("\n") if part.strip())


def _example_strip(stems: list[str], analysis: Analysis, src) -> str:
    """A row of page thumbnails, each with its score -- the claim, pictured."""
    if not stems:
        return ""
    cells = ""
    for stem in stems:
        score = analysis.page_scores.get(stem)
        note = f"{score:.0%} 通过" if score is not None else ""
        cells += (f'<a href="{src(stem)}" target="_blank" rel="noopener">'
                  f'<img loading="lazy" src="{src(stem)}" alt="{escape(stem)}">'
                  f'<span>{escape(stem[:34])}<br>{note}</span></a>')
    return f'<div class="egs">{cells}</div>'


# ------------------------------------------------------------------- sections


def _section_forms(analysis: Analysis, cases: list[Case], run: Run, src) -> str:
    failures = sum(analysis.kinds.values())
    addressing = sum(analysis.kinds[k] for k in ("label_unlinked", "row_missing"))
    reading = sum(analysis.kinds[k] for k in READING_FORMS)
    homes = max(sum(analysis.homes.values()), 1)
    by_kind: dict[str, list[Case]] = {}
    for case in cases:
        by_kind.setdefault(case.kind, []).append(case)

    summary = ""
    for kind in KIND_ORDER:
        if kind in READING_FORMS[1:]:
            continue
        count = reading if kind == "value_off" else analysis.kinds[kind]
        name = "数字读错了" if kind == "value_off" else KIND_ZH[kind]
        share = count / failures if failures else 0
        summary += (f'<tr><td><code>{escape(kind)}</code></td><td>{escape(name)}</td>'
                    f'<td class="num">{count}</td><td class="num">{share:.1%}</td>'
                    f'<td>{_bar(share, kind in ("label_unlinked", "row_missing"))}</td>'
                    f'<td>{_rich(POINTS_AT[kind])}</td></tr>')

    blocks = ""
    for kind in KIND_ORDER:
        if kind in READING_FORMS[1:] or kind == "no_table":
            continue
        count = reading if kind == "value_off" else analysis.kinds[kind]
        name = "数字读错了" if kind == "value_off" else KIND_ZH[kind]
        blocks += (f'<h3 class="band">{escape(name)}'
                   f'<span>{count} 个 · 占失败 {count / failures:.0%} · '
                   f'<code>{escape(kind)}</code></span></h3>'
                   f'<p class="lede">{_rich(KIND_NOTE[kind])}</p>'
                   f'<p class="lede">→ <b>要让它不再发生，流水线得会：'
                   f'{escape(POINTS_AT[kind])}</b></p>')
        if kind == "label_unlinked":
            rows = "".join(
                f'<tr><td>{escape(HOME_ZH[home])}</td>'
                f'<td class="num">{analysis.homes[home]}</td>'
                f'<td class="num">{analysis.homes[home] / homes:.1%}</td>'
                f'<td>{_bar(analysis.homes[home] / homes, False)}</td></tr>'
                for home in HOME_ORDER if analysis.homes.get(home))
            blocks += (f'<p class="lede">这一档最值得看的是：'
                       f'<b>那个对不上的键，其实在哪</b>。'
                       f'把判分点名的键在解析器输出里再找一遍，{homes} 次落位：</p>'
                       f'<div class="scroll"><table><thead><tr><th>它在哪</th>'
                       f'<th class="num">次数</th><th class="num">占比</th><th></th>'
                       f'</tr></thead><tbody>{rows}</tbody></table></div>'
                       f'<div class="pull">'
                       f'<b>{analysis.homes["in_a_table_but_not_addressing"] / homes:.0%} '
                       f'的键就在同一张表里</b>——解析器看见了、也写下来了，'
                       f'只是放在了这个数够不着的位置。'
                       f'所以这不是「没看懂图」，是<b>表的形状不对</b>。<br>'
                       f'把 {addressing} 个「键对不上」全部改对，按页平均从 '
                       f'<b>{analysis.page_mean:.2%} 抬到 '
                       f'{analysis.addressing_ceiling:.2%}</b>（上界，不是预测：'
                       f'它假设换了表的形状而读数一个不变）。</div>')
        if kind == "value_off" and analysis.errors:
            errors = analysis.errors
            rows = "".join(
                f'<tr><td>≤ {name}</td>'
                f'<td class="num">{sum(1 for e in errors if e <= bound)}</td>'
                f'<td class="num">{sum(1 for e in errors if e <= bound) / len(errors):.0%}'
                f'</td><td>{_bar(sum(1 for e in errors if e <= bound) / len(errors), True)}'
                f'</td></tr>'
                for bound, name in ((0.05, "5%"), (0.1, "10%"), (0.2, "20%"), (0.5, "50%")))
            blocks += (f'<p class="lede">错多少：中位 {errors[len(errors) // 2]:.0%}，'
                       f'把容差放宽一倍救不回一半——多数不是「差一点」，是读到了别的东西。</p>'
                       f'<div class="scroll"><table><thead><tr><th>相对误差</th>'
                       f'<th class="num">累计</th><th class="num">占比</th><th></th>'
                       f'</tr></thead><tbody>{rows}</tbody></table></div>')
        for case in by_kind.get(kind, ()):
            blocks += _evidence_card(case, run, analysis, src)
        shown = {case.stem for case in by_kind.get(kind, ())}
        more = [stem for stem in analysis.pages_by_kind.get(kind, ())
                if stem not in shown][:4]
        if more:
            blocks += ('<p class="lede">同一形态还发生在这些页上'
                       '（这一形态吃掉的点最多的几页，未逐页人工读过）：</p>'
                       + _example_strip(more, analysis, src))

    return f"""<section id="forms" role="tabpanel">
  <h2>失败长什么样</h2>
  <div class="explain">
    <p><b>判分只有两步能出错：数字读得对不对，以及表里说不说得清这个数字是谁的。</b>
      官方报告只给「值找不到」和「标签关联不上」两句话，下面把它们拆成六种能改的形状。
      <b>每一种后面立刻并排两张表</b>：左边红色是解析器实际写的，
      右边绿色是同一页写成什么样就能全过。</p>
    <p>表格里的记号：<span class="chip have">绿框</span>规则要的那个数落在这一格 ·
      <span class="chip gap">红框</span>写错的地方 ·
      <span class="chip key">蓝底</span>定位键在表里的位置。</p>
    <p><b>{addressing / failures:.0%} 的失败是「键对不上」</b>——数字本身是对的；
      剩下 {(failures - addressing) / failures:.0%} 才是数读错了或量级写错了。
      分母是 {analysis.pages} 页 · {analysis.points} 个抽查点 · {failures} 个不通过。</p>
  </div>
  <div class="scroll"><table><thead><tr><th>形态</th><th>是什么</th>
    <th class="num">个数</th><th class="num">占比</th><th></th><th>指向</th></tr></thead>
    <tbody>{summary}</tbody></table></div>
  <p class="lede"><b>没有一页交白卷。</b>{analysis.pages} 页全都至少写出了一张表，
    <code>no_table</code> 一例没有——榜单上 &lt;6% 的那几个专用 OCR 全卡在这一步。</p>
  {blocks}
</section>"""


def _component_examples(analysis: Analysis, key: str, limit: int = 3) -> list[str]:
    """The worst-scoring analysed pages carrying this component."""
    carrying = [stem for stem, keys in analysis.components_by_page.items()
                if key in keys and stem in analysis.page_scores]
    carrying.sort(key=lambda stem: analysis.page_scores[stem])
    return carrying[:limit]


def _section_hard(analysis: Analysis, src) -> str:
    keys4 = [s for s in ("mts0625_p6", "MonthlyTreasuryStatement_202411_p8")
             if s in analysis.page_scores or s == "mts0625_p6"]
    curves = (
        '<h3 class="band">要几个键才能定位一个数<span>全 %d 页 · 不依赖图表描述，'
        '是最硬的一条</span></h3>' % analysis.pages
        + '<p class="lede">「2020 年的营收」是两个键，「北美面板里 2020 年的营收」是三个键。'
          '<b>键越多越容易失败，而面板数几乎不影响</b>——'
          '单面板图只要「类目 × 系列 × 测度」要三个键，就和小倍数一样难。</p>'
        + _rate_rows([(f"{k} 键", analysis.by_arity[k]) for k in (2, 3, 4)])
        + _rate_rows([(n, analysis.by_panels[n]) for n in
                      ("1 面板", "2 面板", "3+ 面板") if n in analysis.by_panels])
        + '<p class="lede"><b>四个键长什么样</b>：<code>mts0625_p6</code> 一页两张图，'
          '系列名完全相同（都是 Receipts / Outlays / Deficit），'
          '规则只好写成 <code>Receipts · Apr · 2024 · Figure 3.</code>——'
          '第四个键是图号。解析器合并成一张表、没写图号，十个点全 0。</p>'
        + _example_strip(keys4, analysis, src)
        + '<h3 class="band">图元有多少个<span>落差最大的一条 · 下面两档我们画不出来</span></h3>'
        + '<p class="lede"><code>chart_types.md</code> 现在的上限'
          '（grouped_bar |面板|×|系列| ≤ 24、line 最多 6 条线）'
          '算下来全落在最上面那一档，<b>基准里真正难的那两档我们一张也生成不出来</b>。</p>'
        + _rate_rows([(b, analysis.by_density[b]) for b in
                      ("≤20", "21–60", "61–150", "151–400", ">400")
                      if b in analysis.by_density])
        + _example_strip(["ac8b3538-en_p62", "World_Inequality_Report_2026_p79"],
                         analysis, src)
        + '<p class="lede">左：15 个面板 1,830 个图元，表头整体接错国家。'
          '右：两个面板 4,000 个图元，表的形状全对、十个点只中一个。</p>'
        + '<h3 class="band">数字有没有印在图上<span>单独就值十九个点</span></h3>'
        + '<p class="lede">基准里 <b>56% 的图一个数字都不写</b>，必须照着轴估读。'
          '这一维也是下面组件表的控制变量——不控住它，每一行都在重复这同一件事。</p>'
        + _rate_rows([(PRINTED_ZH[p], analysis.by_printed[p]) for p in
                      ("all", "some", "none") if p in analysis.by_printed])
        + _example_strip(["Technopak_Industry_Report_p18",
                          "Digital_News-Report_2022_p46"], analysis, src)
        + '<p class="lede"><b>但印了也不保险</b>：这两页的数字全部印在图上、'
          '解析器也全抄对了，照样 0 分——错的是键。'
          '读得准和写得对，是两条独立的曲线。</p>'
        + '<h3 class="band">整页有多少字<span>不单调 · 原因未定</span></h3>'
        + '<p class="lede">按 PDF 文字层实测、按四分位分档。'
          '两端低、中间高，而图元个数、每页图数、数字是否印出这三项在四档之间'
          '都没有对应的差别。<b>原因未定，不做推测。</b></p>'
        + _rate_rows(list(analysis.by_text_band.items())))

    rows = ""
    for entry in analysis.costly(10):
        rows += (f'<tr><td>{escape(component_zh(entry.key))}<br>'
                 f'<code>{escape(entry.key)}</code></td>'
                 f'<td class="num">{entry.pages}</td><td class="num">{entry.documents}</td>'
                 f'<td class="num">{entry.present.value:.1%}</td>'
                 f'<td class="num">{entry.present.total}</td>'
                 f'<td class="num">{entry.absent.value:.1%}</td>'
                 f'<td class="num"><b>{entry.delta:+.1%}</b></td></tr>')
    strips = ""
    for entry in analysis.costly(4):
        strips += (f'<p class="lede"><b>{escape(component_zh(entry.key))}</b>'
                   f'（<code>{escape(entry.key)}</code>，{entry.delta:+.1%}）'
                   f'——最差的三页：</p>'
                   + _example_strip(_component_examples(analysis, entry.key),
                                    analysis, src))
    family_rows = "".join(
        f'<tr><td>{escape(band)}</td><td class="num">{sum(counter.values())}</td>'
        f'<td class="num">{counter["addressing"] / sum(counter.values()):.0%}</td>'
        f'<td class="num">{counter["reading"] / sum(counter.values()):.0%}</td></tr>'
        for band, counter in
        ((b, analysis.family_by_density[b]) for b in
         ("≤20", "21–60", "61–150", "151–400", ">400")
         if b in analysis.family_by_density))

    return f"""<section id="hard" role="tabpanel" hidden>
  <h2>什么样的图更容易失败</h2>
  <div class="explain">
    <p>分母在这里变小：只有 {analysis.analysed_pages} 页有图表描述，落在其上的
      {analysis.analysed_points} 个抽查点——<b>「要几个键」那一条例外</b>，
      它只需要规则本身，用的是全量 {analysis.pages} 页。
      <b>每一行都是相关，不是因果</b>，理由在「能不能信」。</p>
  </div>
  {curves}
  <h3 class="band">哪种画法最贵<span>控制组内 · 只列 95% 区间不重叠的</span></h3>
  <p class="lede">控制组是<b>图上一个数字都不写</b>的 {analysis.control_points} 个点
    （通过率 {analysis.control_rate:.1%}）。<b>「文档」这一列比 n 重要</b>——
    n 数的是抽查点，一页最多十个，n=60 有可能只来自六页两份报告，
    那是一家出版方的习惯，不是通用的作图习惯。</p>
  <div class="scroll"><table><thead><tr><th>画法</th><th class="num">页</th>
    <th class="num">文档</th><th class="num">有</th><th class="num">n</th>
    <th class="num">无</th><th class="num">差</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
  {strips}
  <p class="lede">反过来那一端（轴不从零开始、图下有数据下载链接、图号标题齐全）
    不要当杠杆读：它们标记的是「这是一家会好好做图的出版方」，
    不是「加上这个组件就会变好」。</p>
  <h3 class="band">密的图错在键，稀的图才错在数<span></span></h3>
  <div class="scroll"><table><thead><tr><th>图元个数</th><th class="num">失败数</th>
    <th class="num">键对不上</th><th class="num">数读错了</th></tr></thead>
    <tbody>{family_rows}</tbody></table></div>
  <p class="lede">只有最稀疏那一档以读错数为主。图一旦超过二十个图元，
    失败就固定在四分之三是键对不上——这条链不是「越密越读不准」，
    而是<b>「越密越写不成一张对得上号的表」</b>。</p>
</section>"""


def illustrated_stems(cases: list[Case], analysis: Analysis) -> list[str]:
    """Every page the viewer shows -- the cases plus the component example strips."""
    stems = [case.stem for case in cases]
    stems += ["ac8b3538-en_p62", "World_Inequality_Report_2026_p79",
              "Technopak_Industry_Report_p18", "Digital_News-Report_2022_p46",
              "mts0625_p6"]
    for entry in analysis.costly(4):
        stems += _component_examples(analysis, entry.key)
    for pages in analysis.pages_by_kind.values():
        stems += pages
    return sorted(set(stems))


def _section_changes(analysis: Analysis, negative_rate: float) -> str:
    prices = _prices(analysis, negative_rate)
    cards = "".join(
        f'<article class="card"><h4>{number} · {_rich(item.name)}</h4>'
        f'<p class="meta"><span class="chip">{escape(item.maps_to)}</span> '
        f'<span class="chip have">{escape(item.generality)}</span></p>'
        f'<p>{_rich(item.plain.format(**prices))}</p>'
        f'<p class="eg"><b>例子</b>　{_rich(item.example.format(**prices))}</p>'
        f'<p class="price"><b>价</b>　{_rich(item.price.format(**prices))}</p>'
        f'</article>'
        for number, item in enumerate(IMPROVEMENTS, 1))
    return f"""<section id="changes" role="tabpanel" hidden>
  <h2>翻成流水线改动</h2>
  <div class="explain">
    <p>十项，每一条都带着给它定价的那个数。前八项这次数据给出了价，第九项只给了相关，
      第十项没给证据但保留。<b>「通用」这一列问的是同一个问题：ParseBench 不存在，
      这条还值不值得做。</b></p>
  </div>
  <h3 class="band">十项改动<span>按这次数据能给出的价排</span></h3>
  <div class="two">{cards}</div>
</section>"""


def _section_trust(analysis: Analysis) -> str:
    return f"""<section id="trust" role="tabpanel" hidden>
  <h2>能不能信</h2>
  <h3 class="band">通过与否从来不是这里判的</h3>
  <p>每个点的 <code>passed</code> 都取自运行目录里的
    <code>_evaluation_report.json</code>——官方 metric 跑出来的原值，本目录一行都没有重判。
    这里只做一件事：在解析器的输出里把这个值和这些键<b>再找一遍</b>，看它们落在哪，
    好给失败起一个能改的名字。上面每张卡片里的表格片段就是这一步的产物。</p>
  <p>那份「再找一遍」是轻量实现（<code>difflib</code> 而不是 <code>rapidfuzz</code>，
    不展开 colspan）。它与官方在「值找没找到」这一问上的一致率是
    <b>{analysis.matcher_agreement:.2%}</b>，{analysis.points} 个点里分歧
    {round((1 - analysis.matcher_agreement) * analysis.points)} 个。</p>
  <h3 class="band">两种形态没能分出来</h3>
  <p>六类归因里，「串系列」与「读了累计值」这次<b>没有分辨出来</b>：全量上只有
    {_indistinct(analysis)} 个候选，而它们写下的数与真值都只差一格刻度，
    巧合能同样好地解释。这些点已并入读数失败。<b>原因未定，不做推测。</b></p>
  <h3 class="band">「什么图更容易失败」全部是相关</h3>
  <p>组件之间高度共现，控制组只控住了最大的那一个混淆项。
    「无标题的图通过率低二十个点」很可能是「无标题的图多半是仪表盘式的密集版面」，
    不是标题本身在起作用。要变成因果只有一条路：我们自己按单变量生成两组图、
    其余维度固定——那正是消融行的定义。</p>
  <h3 class="band">这一份跑的是什么</h3>
  <p><code>{escape(analysis.run)}</code>：PP-DocLayoutV3 lean +
    <code>{escape(analysis.model)}</code>，200 dpi，verify_rounds=4，整页一次，
    中位 91 秒 / 页。按页平均 <b>{analysis.page_mean:.2%}</b>，
    micro {analysis.micro:.2%}，满分 {analysis.perfect} 页、零分 {analysis.zero} 页。</p>
  <p>同口径下这个分数高于榜单上的所有方法（最高 LlamaParse Agentic 78.11%）。
    榜单行是否用同一版评测代码算出来，本目录无法核实，所以不写「新 SOTA」；
    能写的是——<b>这里分析的失败，是一个已经很强的系统剩下的失败</b>。</p>
  <h3 class="band">没有测的</h3>
  <ul>
    <li>只有一个模型、一条流水线。形态分布是这一套系统的，不是「模型普遍如此」。</li>
    <li>Visual Grounding 一维没碰，这次运行只有 parse 产物。</li>
    <li>{analysis.analysed_pages} 页与全量不独立，是同一批页面的随机子集——
      那些相关只能提假设，不能当验收。</li>
    <li>图表描述来自另一个模型（<code>parsebench/reports/</code> 那一轮，claude-opus-5），
      它的错会原样传进来。有意思的是它可以反过来核：{_predicted(analysis)}</li>
  </ul>
</section>"""


def render_viewer(analysis: Analysis, cases: list[Case], negative_rate: float,
                  run: Run, assets: bool = True) -> str:
    """The whole page: four tabs, matching the four sections of INDEX.md."""
    src = ((lambda stem: f"assets/{quote(stem)}.jpg") if assets
           else (lambda stem: f"../../data/pages/{quote(stem)}.png"))
    failures = sum(analysis.kinds.values())
    addressing = sum(analysis.kinds[k] for k in ("label_unlinked", "row_missing"))
    homes = max(sum(analysis.homes.values()), 1)

    nav = [("forms", "失败长什么样", failures), ("hard", "什么图更容易失败",
            analysis.analysed_pages), ("changes", "翻成流水线改动", len(IMPROVEMENTS)),
           ("trust", "能不能信", analysis.pages)]
    buttons = "".join(f'<button data-tab="{key}" role="tab" aria-controls="{key}" '
                      f'aria-selected="false">{label}<i>{count}</i></button>'
                      for key, label, count in nav)
    facts = [(f"{analysis.page_mean:.1%}", "按页平均"), (str(analysis.pages), "页"),
             (str(analysis.points), "抽查点"), (str(failures), "失败"),
             (f"{addressing / failures:.0%}", "寻址失败占比"),
             (str(len(cases)), "实例页")]
    fact_html = "".join(f'<div class="fact"><b>{v}</b><span>{k}</span></div>'
                        for v, k in facts)

    return f"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>ParseBench 失败样本 · {escape(analysis.run)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
</head>
<body>
<header class="masthead"><div class="inner">
  <div>
    <h1>ParseBench Charts · 失败样本分析</h1>
    <p class="tagline"><code>{escape(analysis.run)}</code> ·
      PP-DocLayoutV3 lean + <code>{escape(analysis.model)}</code> ·
      文字版 <a href="INDEX.md">INDEX.md</a>，逐页 <code>cases/</code></p>
  </div>
  <div class="facts">{fact_html}</div>
</div></header>
<div class="lede-block"><div class="inner">
  <p>这一跑按页平均 <b>{analysis.page_mean:.2%}</b>，比榜单上任何方法都高
    （最高 LlamaParse Agentic 78.11%）。它剩下的 {failures} 个失败里，
    <b>{addressing / failures:.0%} 不是把数读错了，而是那个数在表里找不到能对上的键</b>——
    其中 {analysis.homes['in_a_table_but_not_addressing'] / homes:.0%} 的失联键就写在同一张表里，
    只是不在值那一行。所以第一顺位不是「画得更准」，而是
    <b>「每个图元都带着它的全部键」</b>，那正是输出单位 <code>(键, 值, 区域)</code> 的定义；
    第二顺位是稠密度：≤20 图元 {_rate(analysis, "by_density", "≤20")} →
    &gt;400 图元 {_rate(analysis, "by_density", ">400")}。</p>
</div></div>
<div class="shell">
  <nav role="tablist">{buttons}</nav>
  <main>{_section_forms(analysis, cases, run, src)}{_section_hard(analysis, src)}
{_section_changes(analysis, negative_rate)}{_section_trust(analysis)}</main>
</div>
<footer>同一份数据的文字版在 <a href="INDEX.md">INDEX.md</a>，逐页在 <code>cases/</code>，
  机读汇总在 <code>../../data/stats/failures_{escape(analysis.run)}.json</code>。
  页面特征描述取自 <code>parsebench/reports/</code>，那一份不动。</footer>
<script>{SCRIPT}</script>
</body>
</html>
"""
