"""The visual companion to the index: every finding next to a page that shows it.

A frequency table says `reference_line` appears on 41 pages. It does not say
what that looks like, and a component you cannot picture is a component you cannot
decide whether to build. This renders one page as the working reference: six
sections, each row carrying the page image it was counted on.

Images are written next to the page, not embedded and not linked upwards.
`../data/pages/` resolves from a plain file:// open, but a preview pane or a static
server rooted at the repo refuses to traverse out of the document's directory, and
every image turns into the fallback note. `assets/` sits below `view.html`, holds
one downscaled JPEG per page, and is not tracked.
"""

from __future__ import annotations

import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path
from urllib.parse import quote

from checks import PageResult, evidence_of, keys_of
from index import (GENERALITY_FLOOR, TRIAGE, addressing_score, band, bucketed_types,
                   component_documents, component_pages, countable_figures, generality,
                   headings, new_component_examples, new_components, new_types,
                   pick_examples, step_examples, suggestion_generality, triage,
                   type_counts, type_examples)
from markdown import FINDING_ZH, PLACEMENT_ZH, PRINTED_ZH, STEP_ZH, affects_zh
from vocabulary import BY_KEY, CHART_TYPE_OURS, GROUP_TITLES, VOCABULARY

STYLE = """
:root{
  --ground:#F6F7F9; --surface:#FFFFFF; --raised:#EDF0F4;
  --ink:#151A21; --muted:#5A6472; --line:#DFE4EA;
  --gap:#A93E26; --gap-soft:#A93E2614; --have:#2E6A55; --have-soft:#2E6A5512;
  --shadow:0 1px 2px rgba(21,26,33,.05), 0 8px 24px -16px rgba(21,26,33,.25);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1216; --surface:#161C23; --raised:#1E2630;
    --ink:#E7EBF0; --muted:#98A3B1; --line:#28313B;
    --gap:#E4795A; --gap-soft:#E4795A1C; --have:#68BC9A; --have-soft:#68BC9A16;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#0E1216; --surface:#161C23; --raised:#1E2630;
  --ink:#E7EBF0; --muted:#98A3B1; --line:#28313B;
  --gap:#E4795A; --gap-soft:#E4795A1C; --have:#68BC9A; --have-soft:#68BC9A16;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans","Noto Sans CJK SC","Source Han Sans SC","PingFang SC",
              "Microsoft YaHei",system-ui,sans-serif;
  font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased;
}
code,.mono,th.num,td.num{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,monospace}
a{color:inherit; text-underline-offset:3px; text-decoration-color:var(--line)}
a:hover{text-decoration-color:currentColor}
:focus-visible{outline:2px solid var(--gap); outline-offset:2px; border-radius:3px}

.masthead{border-bottom:1px solid var(--line); background:var(--surface)}
.masthead .inner{max-width:1180px; margin:0 auto; padding:26px 24px 20px;
  display:flex; flex-wrap:wrap; gap:20px 40px; align-items:flex-end}
h1{margin:0; font-size:22px; font-weight:600; letter-spacing:-.01em; text-wrap:balance}
.tagline{margin:4px 0 0; color:var(--muted); font-size:13.5px}
.facts{display:flex; flex-wrap:wrap; gap:6px 28px; margin-left:auto}
.fact{display:flex; flex-direction:column}
.fact b{font-family:"IBM Plex Mono",monospace; font-size:17px; font-weight:500;
  font-variant-numeric:tabular-nums}
.fact span{font-size:11px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted)}

.shell{max-width:1180px; margin:0 auto; padding:0 24px 80px;
  display:grid; grid-template-columns:186px minmax(0,1fr); gap:44px; align-items:start}
nav{position:sticky; top:0; padding:28px 0; display:flex; flex-direction:column; gap:2px}
nav button{
  appearance:none; border:0; background:none; color:var(--muted); cursor:pointer;
  font:inherit; font-size:14px; text-align:left; padding:7px 12px; border-radius:6px;
  border-left:2px solid transparent; display:flex; justify-content:space-between; gap:10px;
}
nav button:hover{background:var(--raised); color:var(--ink)}
nav button[aria-selected="true"]{color:var(--ink); font-weight:600;
  border-left-color:var(--gap); background:var(--raised)}
ul.toc{list-style:none; margin:2px 0 10px; padding:0 0 0 14px;
  border-left:1px solid var(--line)}
ul.toc li{margin:0}
ul.toc li.deep{padding-left:12px}
ul.toc a{display:block; padding:4px 8px; font-size:12.5px; color:var(--muted);
  text-decoration:none; border-radius:5px; line-height:1.35}
ul.toc a:hover{background:var(--raised); color:var(--ink)}
ul.toc a.at{color:var(--gap); background:var(--gap-soft); font-weight:500}
nav button i{font-style:normal; font-family:"IBM Plex Mono",monospace; font-size:12px;
  color:var(--muted); font-variant-numeric:tabular-nums}

main{padding:28px 0 0; min-width:0}
section[hidden]{display:none}
.lede{margin:0 0 26px; color:var(--muted); font-size:14px; max-width:62ch}
.lede b{color:var(--ink); font-weight:600}
h2{margin:0 0 4px; font-size:19px; font-weight:600; letter-spacing:-.01em}

.band{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin:30px 0 12px;
  font-size:14px; font-weight:600; padding-bottom:7px; border-bottom:2px solid var(--gap)}
.band:first-of-type{margin-top:0}
.band span{font-weight:400; font-size:12.5px; color:var(--muted)}
.card{background:var(--surface); border:1px solid var(--line); border-radius:10px;
  margin-bottom:18px; overflow:hidden; box-shadow:var(--shadow)}
.card > header{display:flex; flex-wrap:wrap; align-items:center; gap:8px 12px;
  padding:14px 18px; border-bottom:1px solid var(--line); background:var(--raised)}
.card h3{margin:0; font-size:15.5px; font-weight:600}
.card header code{font-size:13px; color:var(--gap); background:var(--gap-soft);
  padding:2px 7px; border-radius:5px}
.tally{margin-left:auto; display:flex; align-items:center; gap:10px;
  font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--muted);
  font-variant-numeric:tabular-nums}
.meter{width:82px; height:5px; border-radius:3px; background:var(--line); overflow:hidden}
.meter i{display:block; height:100%; background:var(--gap)}
.chip{font-size:11px; letter-spacing:.06em; padding:2px 8px; border-radius:20px;
  border:1px solid var(--line); color:var(--muted); white-space:nowrap}
.chip.hi{color:var(--gap); border-color:var(--gap); background:var(--gap-soft); font-weight:600}
.chip.mid{color:var(--gap); border-color:var(--gap-soft); background:var(--gap-soft)}
.chip.yes{color:var(--have); border-color:var(--have-soft); background:var(--have-soft)}

.split{display:grid; grid-template-columns:minmax(260px,.9fr) minmax(0,1.1fr); gap:0}
.split .prose{padding:18px; display:flex; flex-direction:column; gap:12px;
  border-right:1px solid var(--line)}
.split p{margin:0; font-size:13.5px}
.split .label{display:block; font-size:11px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--muted); margin-bottom:3px}
.split .criterion{color:var(--muted); font-size:12.5px; font-style:italic}
.quote{display:inline-block; background:var(--raised); border-left:2px solid var(--gap);
  padding:3px 9px; border-radius:0 5px 5px 0; font-size:12.5px;
  font-family:"IBM Plex Mono",ui-monospace,monospace; color:var(--ink)}
td .quote{max-width:340px; font-size:11.5px; line-height:1.5}
.fig{display:block; font-size:12.5px; color:var(--muted); line-height:1.75}
.fig + .fig{margin-top:6px; padding-top:6px; border-top:1px dashed var(--line)}
.thumb{display:block; width:118px; flex:none}
.thumb img{width:118px; height:84px; object-fit:contain; object-position:top center;
  background:#fff; border:1px solid var(--line); border-radius:4px; padding:2px}
.explain{background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--gap);
  border-radius:8px; padding:16px 18px; margin:0 0 22px; display:flex; flex-direction:column;
  gap:9px; box-shadow:var(--shadow)}
.explain h3{margin:0; font-size:14px; font-weight:600}
h4.sub{margin:22px 0 8px; font-size:14px; font-weight:600; letter-spacing:.01em}
.explain p{margin:0; font-size:13.5px; color:var(--muted)}
.explain p b{color:var(--ink)}
.cases{display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px;
  margin-top:18px}
.case{background:var(--surface); border:1px solid var(--line); border-radius:9px;
  overflow:hidden; box-shadow:var(--shadow); display:flex; flex-direction:column}
.case img{width:100%; height:230px; object-fit:contain; object-position:top center;
  background:#fff; border-bottom:1px solid var(--line); padding:6px}
.case .body{padding:11px 13px; display:flex; flex-direction:column; gap:6px; font-size:13px}
.case .head{display:flex; align-items:center; gap:8px; flex-wrap:wrap}
.case .head code{font-size:12.5px; color:var(--gap); background:var(--gap-soft);
  padding:2px 7px; border-radius:5px}
.case .head b{font-weight:600}
.case .why{color:var(--muted); font-size:12.5px}
.case .stem{font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted);
  word-break:break-all}
td.shot{width:130px}
td.shot .stem{display:block; font-family:"IBM Plex Mono",monospace; font-size:10px;
  color:var(--muted); word-break:break-all; margin-top:4px; line-height:1.4}
.prose code,td code{background:var(--raised); border-radius:4px; padding:1px 5px;
  font-size:12.5px; font-style:normal}
figure{margin:0; padding:18px; background:var(--raised); display:flex;
  flex-direction:column; gap:8px; align-items:center; justify-content:center}
figure img{max-width:100%; max-height:460px; border:1px solid var(--line); border-radius:4px;
  background:#fff; display:block}
figcaption{font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--muted);
  text-align:center; word-break:break-all}
.no-image img{display:none}
.no-image .hint{display:block}
.hint{display:none; font-size:12.5px; color:var(--muted); text-align:center; padding:40px 12px}

table{border-collapse:collapse; width:100%; font-size:13.5px}
.scroll{overflow-x:auto; border:1px solid var(--line); border-radius:10px;
  background:var(--surface); box-shadow:var(--shadow)}
th,td{text-align:left; padding:9px 14px; border-bottom:1px solid var(--line);
  vertical-align:top}
thead th{background:var(--raised); font-weight:600; font-size:11.5px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted); white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}

.bars{display:flex; flex-direction:column; gap:9px; background:var(--surface);
  border:1px solid var(--line); border-radius:10px; padding:18px; box-shadow:var(--shadow)}
.bar{display:grid; grid-template-columns:130px minmax(0,1fr) 74px; gap:12px; align-items:center;
  font-size:13.5px}
.bar code{font-size:12.5px}
.bar .track{height:16px; background:var(--raised); border-radius:3px; overflow:hidden}
.bar .track i{display:block; height:100%; background:var(--gap); opacity:.8}
.bar .val{font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--muted);
  text-align:right; font-variant-numeric:tabular-nums}

.grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(255px,1fr)); gap:14px}
.tile{background:var(--surface); border:1px solid var(--line); border-radius:9px;
  overflow:hidden; display:flex; flex-direction:column; box-shadow:var(--shadow)}
.tile img{width:100%; height:210px; object-fit:contain; object-position:center;
  background:#fff; border-bottom:1px solid var(--line); padding:6px}
.tile .body{padding:11px 13px; display:flex; flex-direction:column; gap:7px}
.tile .stem{font-family:"IBM Plex Mono",monospace; font-size:11.5px; word-break:break-all}
.tile .keys{display:flex; flex-wrap:wrap; gap:4px}
.tile .keys code{font-size:10.5px; padding:1px 6px; border-radius:4px;
  background:var(--gap-soft); color:var(--gap)}
.tile .meta{font-size:11.5px; color:var(--muted); display:flex; gap:10px; flex-wrap:wrap}

.note{font-size:13px; color:var(--muted); margin:14px 0 0; max-width:70ch}
@media (max-width:900px){
  .shell{grid-template-columns:1fr; gap:0}
  ul.toc{display:none}
  nav{flex-direction:row; overflow-x:auto; padding:14px 0; gap:6px;
    border-bottom:1px solid var(--line); background:var(--ground)}
  nav button{border-left:0; border-bottom:2px solid transparent; white-space:nowrap}
  nav button[aria-selected="true"]{border-left-color:transparent; border-bottom-color:var(--gap)}
  nav button i{display:none}
  .split{grid-template-columns:1fr}
  .split .prose{border-right:0; border-bottom:1px solid var(--line)}
  .facts{margin-left:0}
}
"""

#: Tabs, plus a table of contents built from the headings the sections already have.
#: Reading the DOM rather than taking a list from Python is what keeps the two from
#: drifting: a section that gains a heading gains a contents entry, with no second
#: place to update.
SCRIPT = """
const tabs=[...document.querySelectorAll('nav button')];
const slug=(id,i)=>id+'-h'+i;

tabs.forEach(tab=>{
  const section=document.getElementById(tab.dataset.tab);
  const heads=[...section.querySelectorAll('h3.band, h4.sub')];
  if(!heads.length) return;
  const list=document.createElement('ul');
  list.className='toc'; list.dataset.for=tab.dataset.tab;
  heads.forEach((h,i)=>{
    h.id=slug(tab.dataset.tab,i);
    const item=document.createElement('li');
    const a=document.createElement('a');
    a.href='#'+h.id;
    a.textContent=(h.firstChild&&h.firstChild.nodeType===3?h.firstChild.textContent
      :h.textContent).trim();
    if(h.tagName==='H4') item.className='deep';
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
tabs.forEach(t=>t.addEventListener('click',()=>{history.replaceState(null,'','#'+t.dataset.tab);
  show(t.dataset.tab)}));

// Mark the heading the reader is at, so a long tab still says where you are.
const spy=()=>{
  let here=null;
  document.querySelectorAll('main > section:not([hidden]) h3.band, '
    +'main > section:not([hidden]) h4.sub').forEach(h=>{
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


#: Wide enough for the largest place a page is shown -- a card image is capped at
#: 460px tall, so about 350px wide -- with room for a high-density screen.
ASSET_WIDTH = 800
ASSET_QUALITY = 75


def write_assets(pages: list[PageResult], out_dir: Path, pages_dir: Path) -> bool:
    """Write one downscaled page image per report, beside the viewer.

    Already-written files are left alone, so a rerun costs nothing. Returns False
    when Pillow is absent, and the viewer then links `../data/pages/` instead.
    """
    try:
        from PIL import Image
    except ImportError:
        return False
    directory = out_dir / "assets"
    directory.mkdir(parents=True, exist_ok=True)

    def convert(page: PageResult) -> None:
        source, target = pages_dir / f"{page.stem}.png", directory / f"{page.stem}.jpg"
        if target.exists() or not source.exists():
            return
        image = Image.open(source).convert("RGB")
        height = round(ASSET_WIDTH * image.height / image.width)
        image.resize((ASSET_WIDTH, height), Image.LANCZOS).save(
            target, quality=ASSET_QUALITY, optimize=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(convert, pages))
    return True


_TICK = re.compile(r"`([^`]+)`")


def _rich(text: str) -> str:
    """Escape, then turn markdown backticks into code spans.

    The vocabulary writes its reasons with backticks around spec references, and a
    literal backtick on a rendered page reads as a typo. Escaping runs first, so
    the substitution can only ever wrap text that is already inert.
    """
    return _TICK.sub(r"<code>\1</code>", escape(text))


def _img(src: str, stem: str) -> str:
    """The page image, with a hint when the browser cannot load it."""
    return (f'<a href="{src}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="{src}" alt="{escape(stem)}"'
            f' onerror="this.closest(\'figure\').classList.add(\'no-image\')"></a>'
            f'<p class="hint">这张页面图没能加载。先跑 '
            f'<code>tools/dataset/render_pages.py</code> 渲染页面，再跑 '
            f'<code>tools/analysis/analyze_pages.py</code> 生成 <code>reports/assets/</code>。</p>')


def _figure_lines(page: PageResult) -> str:
    """The example page's figures, as the model reported them.

    A count says a key was seen; this says what was on the page when it was seen.
    The heading is printed split, because five of the vocabulary keys are about how
    a heading is built and none of them is convincing without the words themselves.
    """
    rows = []
    for figure in countable_figures(page):
        kind = str(figure.get("type"))
        if kind == "other" and str(figure.get("type_other", "")).strip():
            kind = f"other · {figure['type_other']}"
        facts = (f"<code>{escape(kind)}</code> · "
                 f"{figure.get('panels')} 面板 · {figure.get('series')} 系列 · "
                 f"{figure.get('categories')} 类目 · {figure.get('marks')} 图元 · "
                 f"数值写出：{PRINTED_ZH.get(figure.get('values_printed'), '?')}")
        head = figure.get("heading") or {}
        names = []
        for label, key in (("图号", "figure_number"), ("标题", "title"),
                           ("副标题", "subtitle"), ("单位", "unit_text")):
            if str(head.get(key, "")).strip():
                names.append(f"{label}：{escape(str(head[key]).strip())}")
        where = PLACEMENT_ZH.get(str(head.get("placement", "")), "")
        if where:
            names.append(f"标题块：{where}")
        ticks = str(figure.get("value_axis_ticks", "")).strip()
        if ticks:
            names.append(f"值轴刻度：{escape(ticks)}")
        for label, key, cap in (("面板", "panel_names", 6), ("系列", "series_names", 6),
                                ("类目", "category_names", 8)):
            values = [str(n) for n in (figure.get(key) or ()) if str(n).strip()]
            if values:
                shown = " / ".join(escape(n) for n in values[:cap])
                names.append(f"{label}：{shown}{' …' if len(values) > cap else ''}")
        rows.append(f'<span class="fig">{facts}'
                    + "".join(f"<br>{n}" for n in names) + "</span>")
    return "".join(rows)


def _thumb(src: str, stem: str) -> str:
    return (f'<a href="{src}" target="_blank" rel="noopener" class="thumb">'
            f'<img loading="lazy" src="{src}" alt="{escape(stem)}"></a>')


def _report_link(stem: str) -> str:
    return f'<a href="pages/{quote(stem)}/report.md">report.md</a>'


def _band_chip(count: int, total: int) -> str:
    if not count:
        return '<span class="chip">未出现</span>'
    name = band(count, total)
    cls = {"高": "hi", "中": "mid", "低": ""}[name]
    return f'<span class="chip {cls}">{name}档</span>'


_GEN_CLASS = {"通用": "yes", "常见": "mid", "集中": "", "样本不足": ""}


def _gen_chip(verdict: str, detail: str) -> str:
    """The verdict plus the document count. The rest of the detail is the tooltip.

    A card header already carries the band, the key, the name and the tally; the
    whole `20 份 · 最大单份占 5%` string pushes the name onto its own line.
    """
    short = detail.split(" · ")[0]
    return (f'<span class="chip {_GEN_CLASS.get(verdict, "")}" title="{escape(detail)}">'
            f'{escape(verdict)} · {escape(short)}</span>')


def _step_chip(affects: tuple[int, ...]) -> str:
    """Which scoring steps this can change. No steps is itself the finding."""
    if not affects:
        return '<span class="chip">基准看不见</span>'
    return "".join(f'<span class="chip yes">第{n}步</span>' for n in affects)


def _gap_card(component, sample: list[PageResult], count: int, total: int,
              verdict: tuple[str, str], src) -> str:
    """One component we cannot draw, with the page and the words that show it."""
    if not sample:
        return ""
    first, others = sample[0], sample[1:]
    more = "".join(f' · <a href="pages/{quote(p.stem)}/report.md">{escape(p.stem)}</a>'
                   for p in others)
    proof = evidence_of(first.analysis, component.key)
    return f"""<article class="card">
  <header>
    {_band_chip(count, total)}{_step_chip(component.affects)}{_gen_chip(*verdict)}
    <code>{escape(component.key)}</code>
    <h3>{_rich(component.name_zh)}</h3>
    <span class="tally"><span class="meter"><i style="width:{count / total:.0%}"></i></span>
      {count} / {total} 页 · {count / total:.0%}</span>
  </header>
  <div class="split">
    <div class="prose">
      <p><span class="label">这一页上的证据（模型写的）</span>
         <span class="quote">{escape(proof) or "（这一页没写出证据）"}</span></p>
      <p><span class="label">判据（送给模型的原话）</span>
         <span class="criterion">{_rich(component.hint)}</span></p>
      <p><span class="label">我们为什么画不出来</span>{_rich(component.basis)}</p>
      <p><span class="label">这一页的图（模型报的）</span>{_figure_lines(first)}</p>
      {f'<p><span class="label">另见</span>{more[3:]}</p>' if others else ''}
    </div>
    <figure>{_img(src(first.stem), first.stem)}
      <figcaption>{escape(first.stem)} · {_report_link(first.stem)}</figcaption></figure>
  </div>
</article>"""


def _type_card(name: str, count: int, share: float, basis: str,
               sample: tuple[PageResult, dict] | None, src) -> str:
    """One chart type the condition table has no row for."""
    if not sample:
        return ""
    page, figure = sample
    named = str(figure.get("type_other", "")).strip()
    head = figure.get("heading") or {}
    title = " ".join(str(head.get(k, "")).strip()
                     for k in ("figure_number", "title") if str(head.get(k, "")).strip())
    return f"""<article class="card">
  <header>
    <span class="chip hi">类型缺口</span>
    <code>{escape(name)}{f" · {escape(named)}" if named else ""}</code>
    <span class="tally">{count} 张 · 占全部图 {share:.0%}</span>
  </header>
  <div class="split">
    <div class="prose">
      <p><span class="label">这一页上是什么</span>
         <span class="quote">{escape(title) or "（图上没有标题）"}</span></p>
      <p><span class="label">条件表为什么没有它</span>{_rich(basis)}</p>
      <p><span class="label">这一页的图（模型报的）</span>{_figure_lines(page)}</p>
    </div>
    <figure>{_img(src(page.stem), page.stem)}
      <figcaption>{escape(page.stem)} · {_report_link(page.stem)}</figcaption></figure>
  </div>
</article>"""


def _new_card(name: str, count: int, why: str, sample: list[PageResult], src) -> str:
    if not sample:
        return ""
    first = sample[0]
    proof = next((str(c.get("evidence", ""))
                  for c in (first.analysis.get("new_components") or ())
                  if str(c.get("name", "")).strip() == name), "")
    return f"""<article class="card">
  <header>
    <span class="chip {'hi' if count >= 3 else ''}">{'并入词表' if count >= 3 else '记录'}</span>
    <code>{escape(name)}</code>
    <span class="tally">{count} 页</span>
  </header>
  <div class="split">
    <div class="prose">
      <p><span class="label">这一页上的证据</span>
         <span class="quote">{escape(proof) or "（没写出证据）"}</span></p>
      <p><span class="label">模型说它为什么要紧</span>{_rich(why)}</p>
      <p><span class="label">这一页上是什么</span>
         {_rich(first.analysis.get('page_note', ''))}</p></div>
    <figure>{_img(src(first.stem), first.stem)}
      <figcaption>{escape(first.stem)} · {_report_link(first.stem)}</figcaption></figure>
  </div>
</article>"""


def render_viewer(pages: list[PageResult], model: str, assets: bool = True) -> str:
    """The whole page, three tabs matching the three sections of INDEX.md.

    The split is by question, not by topic. `order` holds everything we cannot draw
    -- components, chart types and heading dimensions together, because "do we build
    this" is one question however the thing is classified. `portrait` describes the
    corpus and contains no to-do. `trust` is method, grading and the pages.

    `assets` picks where the images are read from: with it, every image sits under
    `assets/` beside this file; without, the page links up into `data/pages/`, which
    only resolves on a plain file:// open.
    """
    src = ((lambda stem: f"assets/{quote(stem)}.jpg") if assets
           else (lambda stem: f"../data/pages/{quote(stem)}.png"))
    total = len(pages)
    seen = component_pages(pages)
    docs = component_documents(pages)
    corpus = len({p.document for p in pages})
    figures = [(p, f) for p in pages for f in countable_figures(p)]
    missing = sorted((c for c in VOCABULARY if not c.ours), key=lambda c: (-seen[c.key], c.key))
    verdicts = {c.key: generality(seen[c.key], docs.get(c.key, Counter()), corpus)
                for c in VOCABULARY}
    picked = pick_examples(pages, [c.key for c in missing], 3)
    types = type_counts(pages)
    type_gaps = [(n, c) for n, c in types.most_common()
                 if not CHART_TYPE_OURS.get(n, (False, ""))[0]]
    lists = triage(pages)

    # ============================================================ 1 · what to build
    def pick_row(row, n):
        component, count, verdict, detail, gap, why = row
        return (f'<tr><td class="num">{n}</td><td><code>{escape(component.key)}</code></td>'
                f'<td>{_rich(component.name_zh)}</td><td class="num">{count}</td>'
                f'<td>{_step_chip(component.affects)}</td>'
                f'<td>{_gen_chip(verdict, detail)}'
                + (f'<br><span class="why">{escape(why)}</span>' if why else "")
                + f'</td><td><b>{escape(gap)}</b></td></tr>')

    TEST = {"keep_score": f"页数 ≥ {GENERALITY_FLOOR} · <code>affects</code> 非空",
            "keep_diversity": f"页数 ≥ {GENERALITY_FLOOR} · <code>affects</code> 为空 · 分布 ≥ 0.50",
            "undecided": f"页数 &lt; {GENERALITY_FLOOR}，或分布落在 0.40–0.50",
            "drop": "<code>affects</code> 为空 · 分布 &lt; 0.40"}
    CLS = {"keep_score": "yes", "keep_diversity": "mid", "undecided": "hi", "drop": ""}
    summary_rows = "".join(
        f'<tr><td><span class="chip {CLS[n]}">{escape(t)}</span></td>'
        f'<td class="num"><b>{len(lists[n])}</b></td><td>{TEST[n]}</td>'
        f'<td>{_rich(b)}</td></tr>' for n, t, b in TRIAGE)
    triage_blocks = ""
    for n, t, b in TRIAGE:
        rows = "".join(pick_row(r, i) for i, r in enumerate(lists[n], 1)) or \
            '<tr><td colspan="7">空</td></tr>'
        triage_blocks += (
            f'<h4 class="sub">{escape(t)} · {len(lists[n])} 项</h4>'
            f'<p class="lede">{_rich(b)}</p>'
            f'<div class="scroll"><table><thead><tr><th class="num">#</th><th>key</th>'
            f'<th>组件</th><th class="num">页数</th><th>影响哪一步</th><th>通用度</th>'
            f'<th>归入</th></tr></thead><tbody>{rows}</tbody></table></div>')

    BANDS = (("高", f"高档 · ≥ {total // 2} 页"), ("中", f"中档 · {total // 12 + 1}–{total // 2 - 1} 页"),
             ("低", f"低档 · ≤ {total // 12} 页"))
    gaps = ""
    for name, title in BANDS:
        members = [c for c in missing if seen[c.key] and band(seen[c.key], total) == name]
        if not members:
            continue
        hit = sum(1 for c in members if c.affects)
        gaps += (f'<h3 class="band">{escape(title)}'
                 f'<span>{len(members)} 项 · 其中 {hit} 项能改变得分</span></h3>')
        gaps += "".join(_gap_card(c, picked.get(c.key, []), seen[c.key], total,
                                  verdicts[c.key], src) for c in members)
    first_of_type = {name: (page, figure) for name, _, page, figure in type_examples(pages)}
    if type_gaps:
        gaps += ('<h3 class="band">类型缺口'
                 f'<span>{len(type_gaps)} 种 · 条件表里没有这一族</span></h3>')
        gaps += "".join(
            _type_card(name, count, count / max(len(figures), 1),
                       CHART_TYPE_OURS.get(name, (False, "不在条件表里"))[1],
                       first_of_type.get(name), src)
            for name, count in type_gaps)
    buckets = bucketed_types(new_types(pages))
    bucket_rows = "".join(
        f'<tr><td><b>{escape(t)}</b></td><td class="num">{sum(c for _, c in m)}</td>'
        f'<td>{_rich(b)}</td><td>'
        + " · ".join(f"<code>{escape(n)}</code>{f'×{c}' if c > 1 else ''}" for n, c in m)
        + "</td></tr>" for t, b, m in buckets)
    ours_types = {t for t, (yes, _) in CHART_TYPE_OURS.items() if yes}
    unused = sorted(t for t in ours_types if not types.get(t))

    where = headings(pages)
    numbered = multiline = united = figs = 0
    for page in pages:
        for figure in countable_figures(page):
            head = figure.get("heading") or {}
            figs += 1
            numbered += bool(str(head.get("figure_number", "")).strip())
            multiline += bool(str(head.get("subtitle", "")).strip())
            united += bool(str(head.get("unit_text", "")).strip())
    head_rows = "".join(
        f'<tr><td>{escape(label)}</td><td class="num">{v}</td>'
        f'<td class="num">{v / max(figs, 1):.0%}</td><td>{_rich(note)}</td></tr>'
        for label, v, note in (
            ("图号", numbered, "FigureSpec 没有 <code>title</code> 字段，图号无处可编 · P7"),
            ("副标题（标题不止一行）", multiline, "同上 · P7"),
            ("单位写在标题里", united, "unit 在 measure 声明里，一个字都不画出来 · P6 / P7")))
    place_rows = "".join(f'<tr><td>{escape(PLACEMENT_ZH.get(k, k))}</td><td class="num">{v}</td>'
                         f'<td class="num">{v / max(figs, 1):.0%}</td></tr>'
                         for k, v in where.most_common())
    order_section = f"""<section id="order" role="tabpanel">
  <h2>要改什么</h2>
  <div class="explain">
    <h3>这一节收的是同一件事：我们画不出来的东西</h3>
    <p>组件、图表类型、标题维度<b>放在一起排序</b>——「这个我们建不建」是同一个问题，
      不该因为它被归成「组件」还是「类型」就分到两张表里。类型配比、词表全表这类
      <b>描述</b>不在这里，在「基准画像」。</p>
    <p><b>两条独立的轴。</b>一个组件可以出现在四分之三的页面上，而基准根本看不见它：
      <code>unit_in_axis_or_title</code> 出现在 149 / 192 页，而 4,864 条规则里
      <b>没有一条</b>的值或标签引用过那个单位（值里出现量纲词的：0 条）。所以每一行带两列——
      <b>影响哪一步</b>（能改变四步判定的哪一步，空就是基准看不见）与
      <b>通用度</b>（文档分布）。两列都不回答「该不该做」，而是把它拆成两个能分别回答的问题。</p>
  </div>
  <h3 class="band">四份清单<span>{len(missing)} 项缺口各归其一，没有重叠也没有遗漏</span></h3>
  <p class="lede">依次问三个已测的问题：<b>① 页数够读出分布吗？</b>不够 → 待定。
    <b>② 它能改变四步判定的某一步吗？</b>（<code>affects</code>，按度量定义定死）能 → 第一份。
    <b>③ 它是通用画法吗？</b>（文档分布）是 → 第二份，压在分界线上 → 待定，明确不是 → 舍弃。
    前两份<b>之间没有汇率</b>，硬排成一列就得凭空发明一个换算率。</p>
  <div class="scroll"><table><thead><tr><th>清单</th><th class="num">项数</th><th>判据</th>
    <th>怎么处理</th></tr></thead><tbody>{summary_rows}</tbody></table></div>
  <p class="note"><b>第三份清单是这套分类里最要紧的一格。</b>「读不出来」和「判定不要」是两回事，
    混在一起，<code>error_bars</code> 只出现 2 页就会被写成「某家出版方的习惯」。
    通用度那一列印的是比值本身（实际覆盖的文档数 / 这些页最多能覆盖的文档数），0.70 以上通用、
    0.45 以上常见；落在 0.40–0.50 的一律不判，因为 0.44 与 0.45 分到不同清单是
    <b>阈值在说话，不是数据在说话</b>。</p>
  {triage_blocks}
  {gaps}
  <h3 class="band">类型缺口里的 <code>other</code><span>命名之后只有一堆是真缺口</span></h3>
  <div class="scroll"><table><thead><tr><th>分类</th><th class="num">图数</th><th>是缺口吗</th>
    <th>名字</th></tr></thead><tbody>{bucket_rows}</tbody></table></div>
  <p class="note">条件表里有、这份抽样里一张都没出现的
    {len(unused)} 种：{" · ".join(f"<code>{escape(t)}</code>" for t in unused)}。
    <b>这不是白做</b>——它们是为别的目标基准留的能力，只说明按 ParseBench 调权重时
    不该给它们配额（P4）。</p>
  <h3 class="band">标题维度缺口<span>图题不是组件，是五个字段</span></h3>
  <p class="lede"><b>图号 / 主标题 / 副标题 / 单位 / 位置。</b>词表里原来有四个 key 在重复记录
    同样的事，而且是按页记不是按图记（一页同时报「图号标题在上方」和「副标题分行」就把一个标题
    数了两次），已经删掉。现在每张图直接记这五个字段，缺口按维度读。
    <b>这一整节属于上面的 B 半</b>——图号出现在 {numbered / max(figs, 1):.0%} 的图上，而
    4,864 条规则里只有 14 条（0.14%）把图号当定位标签。</p>
  <div class="scroll"><table><thead><tr><th>维度</th><th class="num">图数</th>
    <th class="num">占比</th><th>我们现在</th></tr></thead><tbody>{head_rows}</tbody></table></div>
  <div class="scroll"><table><thead><tr><th>标题块位置</th><th class="num">图数</th>
    <th class="num">占比</th></tr></thead><tbody>{place_rows}</tbody></table></div>
  <p class="note"><b>位置这一维是四值不是两值。</b><code>2023-05-sigma-01-english_p23</code>
    的 Figure 15 把图号、标题、副标题三行排在<b>左栏</b>、与绘图区并排。对第四步的上下文回退
    来说，侧栏标题在 markdown 里落在哪一段完全取决于解析器怎么切版面块。</p>
  <p class="note"><b>只出现 1–2 页的几项没有人工核对过，可能是模型误判。</b>
    每一项都带证据原文，可以直接对着实例核。</p>
</section>"""

    # ============================================================= 2 · the portrait
    rows = []
    all_picked = pick_examples(pages, [c.key for c in VOCABULARY], 1)
    for group, title in GROUP_TITLES.items():
        members = sorted((c for c in VOCABULARY if c.group == group), key=lambda c: -seen[c.key])
        for i, c in enumerate(members):
            sample = all_picked.get(c.key) or []
            shot = (f'{_thumb(src(sample[0].stem), sample[0].stem)}'
                    f'<span class="stem">{escape(sample[0].stem)}</span>') if sample else "—"
            proof = evidence_of(sample[0].analysis, c.key) if sample else ""
            rows.append(
                f'<tr><td>{escape(title) if i == 0 else ""}</td>'
                f'<td><code>{escape(c.key)}</code></td><td>{_rich(c.name_zh)}</td>'
                f'<td><span class="chip {"yes" if c.ours else "hi"}">'
                f'{"有" if c.ours else "无"}</span></td>'
                f'<td>{_step_chip(c.affects)}</td>'
                f'<td class="num">{seen[c.key]}</td>'
                f'<td class="num">{len(docs.get(c.key, ()))}</td>'
                f'<td><span class="quote">{escape(proof)}</span></td>'
                f'<td class="shot">{shot}</td></tr>')
    top = types.most_common()[0][1] if types else 1
    bars = "".join(
        f'<div class="bar"><code>{escape(str(name))}</code>'
        f'<span class="track"><i style="width:{count / top:.0%}"></i></span>'
        f'<span class="val">{count} 图 · {count / len(figures):.0%} · '
        f'{"能画" if CHART_TYPE_OURS.get(name, (False, ""))[0] else "画不出来"}</span></div>'
        for name, count in types.most_common())
    horizontal = sum(f.get("orientation") == "horizontal" for _, f in figures)
    printed = Counter(f.get("values_printed") for _, f in figures)
    type_cases = "".join(f"""<article class="case">
      <a href="{src(page.stem)}" target="_blank" rel="noopener">
      <img loading="lazy" src="{src(page.stem)}" alt="{escape(page.stem)}"></a>
      <div class="body"><span class="head"><code>{escape(name)}</code>
        <b>{count} 张</b></span>
        <span class="why">{escape(" ".join(
            str((figure.get('heading') or {}).get(k, '')).strip()
            for k in ('figure_number', 'title')).strip()) or '（图上没有标题）'}</span>
        <span class="stem">{escape(page.stem)}</span></div></article>"""
        for name, count, page, figure in type_examples(pages))
    tags = sorted({p.tags for p in pages})
    head = "".join(f'<th class="num">{escape(t)}</th>' for t in tags)
    body = []
    for step in (1, 2, 3, 4):
        row = [sum(p.analysis.get("hardest_step") == step and p.tags == tag for p in pages)
               for tag in tags]
        body.append(f'<tr><td>{STEP_ZH[step]}</td>'
                    + "".join(f'<td class="num">{v}</td>' for v in row)
                    + f'<td class="num"><b>{sum(row)}</b></td></tr>')
    arity = Counter(r.arity for p in pages for r in p.rules)
    checks = [c for p in pages for c in (p.analysis.get("spot_checks") or ())]
    placed = [c for c in checks if str(c.get("figure_id")) != "not_found"]
    predicted = Counter(len(c.get("addressing_keys") or ()) for c in placed)
    on_figure = sum(bool(c.get("printed_on_figure")) for c in placed)
    arity_rows = "".join(f'<tr><td class="num">{n}</td><td class="num">{arity.get(n, 0)}</td>'
                         f'<td class="num">{predicted.get(n, 0)}</td></tr>'
                         for n in sorted(set(arity) | set(predicted)))
    step_cases = "".join(f"""<article class="case">
      <a href="{src(page.stem)}" target="_blank" rel="noopener">
      <img loading="lazy" src="{src(page.stem)}" alt="{escape(page.stem)}"></a>
      <div class="body"><span class="head"><b>{STEP_ZH[step]}</b></span>
        <span class="why">{escape(page.analysis.get('difficulty_notes', ''))}</span>
        <span class="stem">{escape(page.stem)}</span></div></article>"""
        for step, page in step_examples(pages).items() if page)
    portrait_section = f"""<section id="portrait" role="tabpanel" hidden>
  <h2>基准长什么样</h2>
  <p class="lede">描述，<b>不是待办</b>。我们画得出来的东西也在这一节——「已经能画，而且基准上
    很常见」说明现有能力对得上，那不是缺口。</p>
  <div class="explain">
    <h3>词表、组件、类型是什么关系</h3>
    <p><b>一张图 = 一个类型 + 若干个组件。</b></p>
    <p><b>类型</b>是这张图的画法，19 选 1，<b>必填且只有一个</b>：<code>bar</code>
      <code>line</code> <code>pie</code> <code>heatmap</code> <code>waterfall</code>。</p>
    <p><b>组件</b>是图上、页上还有哪些构造，{len(VOCABULARY)} 选 N，<b>一张图可以有十几个</b>：
      「有参考线」「有负值」「图例在下方」「刻度比数据点稀」。</p>
    <p><b>词表</b>就是组件的那份固定清单——这 {len(VOCABULARY)} 个 key 本身。</p>
    <p>打个比方：<b>类型是名词</b>（这是一辆车），<b>组件是形容词</b>（四门、天窗、手动挡）。
      一辆车只能是一种车，但可以同时有很多个形容词。</p>
    <p><b>为什么词表要固定</b>：模型报组件时那个字段是 enum，只能从这 {len(VOCABULARY)}
      个里选，<b>且每选一个必须写出证据</b>（页面上的原话，或者画了什么、画在哪）。固定是为了让
      {total} 页的答案能相加——「有参考线」「画了条虚线基准」「reference line」如果各写各的，
      就数不出「参考线出现在 {seen.get('reference_line', 0)} 页」这句话。选不出来的写进
      <b>新组件</b>自拟名字，出现 ≥3 页就<b>并入词表</b>，下一轮起有自己的计数。</p>
    <p><b>两者问同一个问题：我们画不画得出来。</b>类型层面 <code>map</code> 画不出来（条件表没有
      地理投影这一族）；组件层面 <code>reference_line</code> 画不出来（参考线不是任何族的图元）。
      所以两者都在「要改什么」，不因为分类不同就分两张表。<b>图题不在词表里</b>——它是每张图上
      记录的五个字段。</p>
  </div>
  <h3 class="band">类型配比<span>P4 的权重向量要的就是这张表</span></h3>
  <div class="bars">{bars}</div>
  <div class="cases">{type_cases}</div>
  <p class="note">共 {len(figures)} 张图。横向 {horizontal} 张（{horizontal / max(len(figures), 1):.0%}）——
    <code>chart_types.md</code> 的条件表没有方向这一维。
    数值写出：{"、".join(f"{PRINTED_ZH.get(k, k)} {v}" for k, v in printed.most_common())}。</p>
  <h3 class="band">难在哪<span>模型的判断，待失败案例确认的假设</span></h3>
  <div class="scroll"><table><thead><tr><th>卡在哪一步</th>{head}
    <th class="num">合计</th></tr></thead><tbody>{"".join(body)}</tbody></table></div>
  <div class="cases">{step_cases}</div>
  <h3 class="band">定位一个值要几个键<span>左列是事实，右列是模型的预测</span></h3>
  <p class="lede">左边是规则实际用了几个标签，右边是模型只看图预测要几个（判分在「能不能信」）。
    <b>两列差得越远，说明「凭图猜寻址」越不可靠。</b></p>
  <div class="scroll"><table><thead><tr><th class="num">键数</th><th class="num">规则实际</th>
    <th class="num">模型预测</th></tr></thead><tbody>{arity_rows}</tbody></table></div>
  <p class="note"><b>这一条不要反过来改我们的记录。</b>ParseBench 只需要两个键，不代表我们记
    两个键就够——生成侧的输出单位是 <code>(键, 值, 区域)</code>，<b>键必须是完整的寻址元组</b>
    （面板 × 系列 × 类目），因为 provenance 与 bbox 这类目标要求每个图元都能被唯一指到。
    把键结构裁到基准的最低要求，等于为了一个基准砍掉这份数据集自己的产物——这正是 P2 要把
    面板维加进键的理由。</p>
  <p class="note">规则有 {arity.get(2, 0)} 条只用两个标签
    （{arity.get(2, 0) / max(sum(arity.values()), 1):.0%}）——行头加列头，markdown 表刚好装得下。
    真正需要第三个键的只有 {arity.get(3, 0)} 条，那才是第三步的难处；第四步只认粗体、
    markdown 标题、<code>&lt;caption&gt;</code>。落位的 {len(placed)} 个值里 {on_figure} 个
    （{on_figure / max(len(placed), 1):.0%}）数字直接印在图上，其余要对着轴读。</p>
  <h3 class="band">词表全表<span>{len(VOCABULARY)} 项，五组</span></h3>
  <div class="scroll"><table><thead><tr><th>组</th><th>key</th><th>组件</th><th>我们</th>
    <th>影响哪一步</th><th class="num">页数</th><th class="num">文档</th><th>证据样例</th>
    <th>实例</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
</section>"""

    # ================================================================ 3 · can we trust it
    right, graded = addressing_score(pages)
    findings = Counter(f.code for p in pages for f in p.findings)
    finding_rows = "".join(f'<tr><td>{escape(FINDING_ZH.get(code, code))}</td>'
                           f'<td class="num">{count}</td></tr>'
                           for code, count in findings.most_common()) or \
        '<tr><td>—</td><td class="num">0</td></tr>'
    counts, why = new_components(pages)
    repeated = [(n, c) for n, c in counts.most_common() if c >= 2]
    once = [n for n, c in sorted(counts.items()) if c == 1]
    new_cards = "".join(_new_card(n, c, why[n], new_component_examples(pages, n, 1), src)
                        for n, c in repeated)
    by_gap = suggestion_generality(pages)
    suggestions = Counter(str(s.get("maps_to")) for p in pages
                          for s in (p.analysis.get("suggestions") or []))
    gap_rows = "".join(
        f'<tr><td><b>{escape(g)}</b></td><td class="num">{n}</td>'
        f'<td class="num">{by_gap.get(g, Counter()).get("general", 0)}</td>'
        f'<td class="num">{by_gap.get(g, Counter()).get("common", 0)}</td>'
        f'<td class="num">{by_gap.get(g, Counter()).get("house_style", 0)}</td></tr>'
        for g, n in suggestions.most_common())
    tiles = []
    for page in sorted(pages, key=lambda p: p.stem):
        lacking = [k for k in keys_of(page.analysis) if not BY_KEY[k].ours]
        figs_here = countable_figures(page)
        kinds = "、".join(sorted({str(f.get("type")) for f in figs_here})) or "—"
        tiles.append(f"""<article class="tile">
  <a href="{src(page.stem)}" target="_blank" rel="noopener">
    <img loading="lazy" src="{src(page.stem)}" alt="{escape(page.stem)}"></a>
  <div class="body">
    <span class="stem">{escape(page.stem)}</span>
    <span class="meta"><span>{len(figs_here)} 图 · {escape(kinds)}</span>
      <span>{len(page.rules)} 抽查点</span><span>{escape(page.tags)}</span></span>
    <span class="keys">{"".join(f"<code>{escape(k)}</code>" for k in lacking) or "—"}</span>
    <span class="meta">{_report_link(page.stem)}</span>
  </div></article>""")
    unreadable_pages = sum(bool(p.analysis.get("unreadable")) for p in pages)
    trust_section = f"""<section id="trust" role="tabpanel" hidden>
  <h2>这些数字能不能信</h2>
  <div class="explain">
    <h3>怎么跑的</h3>
    <p>整页 PNG 150 dpi，一页一次结构化调用，effort <code>high</code>，
      <code>max_tokens</code> 12000，不发 temperature / top_p。
      不裁剪、不接 OCR、不做 agent、不做第二轮。</p>
    <p><b>模型看得到</b>：整页图像 · {len(VOCABULARY)} 项词表（key + 英文判据） ·
      这一页抽查点的<b>数值</b> · P1–P7 的一行描述（意见要归类）。</p>
    <p><b>模型看不到</b>：抽查点的<b>标签</b> · 词表的「我们有没有」那一列 ·
      「影响哪一步」那一列 · 流水线的结构、条件表、<code>(键, 值, 区域)</code>。</p>
  </div>
  <h3 class="band">判分<span>一个真正被打了分的预测</span></h3>
  <p class="lede">值给了模型、标签没给，所以模型说的「要哪些键才能定位」是<b>预测</b>，规则来判分：
    一个值算对，要求规则用的每个标签都被预测到的某个键覆盖。
    <b>{graded} 个落位的值里对了 {right} 个（{right / max(graded, 1):.0%}）。</b></p>
  <p class="note">这个数同时受两件事影响，报出来是为了可追查，不是当作模型能力的度量：一是模型
    确实读错了行或列（<code>2023-05-sigma-01-english_p23</code> 那张指数图 10 个值错了 7 个，
    两条线终点相差不足 2 px）；二是同一个格子在页面上常有不止一种叫法。<b>逐条可查</b>——
    每页 <code>report.md</code> 第 2 节把规则的标签与模型的预测并排放在同一行。</p>
  <h3 class="band">交叉核对<span>{sum(findings.values())} 条矛盾 / {total} 页</span></h3>
  <div class="scroll"><table><thead><tr><th>矛盾</th><th class="num">页数</th>
    </tr></thead><tbody>{finding_rows}</tbody></table></div>
  <p class="note"><code>unreadable</code> 非空 {unreadable_pages} / {total} 页——要逐条读，
    「这张图看不清」与「这个条目根本不是图」是两回事。</p>
  <h3 class="band">意见归属<span>模型自己判的通用度，独立于文档分布的第二个估计</span></h3>
  <div class="scroll"><table><thead><tr><th>归入</th><th class="num">条数</th>
    <th class="num">通用</th><th class="num">一类出版方</th>
    <th class="num">这份文档自己的习惯</th></tr></thead><tbody>{gap_rows}</tbody></table></div>
  <h3 class="band">词表本身还缺什么<span>{len(counts)} 个自拟名字</span></h3>
  <p class="lede">词表装不下的，模型自拟名字，<b>同样要带证据</b>。这是<b>词表完整性的度量</b>：
    残差越干净，说明词表越接近覆盖。名字是自由文本，近义名会把同一个组件的计数拆开，所以按页数读，
    不按名字精确匹配；出现 ≥3 页的下一轮并入。下面是出现在 2 页以上的 {len(repeated)} 个。</p>
  {new_cards}
  <p class="note">只出现在 1 页的还有 {len(once)} 个：
    {" · ".join(f"<code>{escape(n)}</code>" for n in once)}</p>
  <h3 class="band">{total} 页<span>均匀随机，不分层、不设每文档上限</span></h3>
  <p class="lede">汇总表要的是频次，任何筛选都会让它失去无偏性。
    每张卡片下面的 key 是<b>这一页上我们画不出来的组件</b>。</p>
  <div class="grid">{"".join(tiles)}</div>
</section>"""

    nav = [("order", "要改什么", len(missing) + len(type_gaps)),
           ("portrait", "基准画像", len(VOCABULARY)),
           ("trust", "能不能信", total)]
    buttons = "".join(f'<button data-tab="{k}" role="tab" aria-controls="{k}" '
                      f'aria-selected="false">{label}<i>{n}</i></button>'
                      for k, label, n in nav)
    facts = [(str(total), "页"), (str(corpus), "文档"),
             (str(sum(len(p.rules) for p in pages)), "抽查点"), (str(len(figures)), "图"),
             (str(len(lists["keep_score"])), "能提分"),
             (str(len(lists["keep_diversity"])), "提多样性"),
             (str(len(lists["undecided"])), "待定"),
             (str(len(lists["drop"])), "舍弃")]
    fact_html = "".join(f'<span class="fact"><b>{v}</b><span>{k}</span></span>' for v, k in facts)

    return f"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>ParseBench 组件缺口</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
</head>
<body>
<header class="masthead"><div class="inner">
  <div><h1>ParseBench 组件缺口</h1>
  <p class="tagline">{total} 页真实报告页 · 模型 <code>{escape(model)}</code> · effort high ·
    整页 150 dpi，一页一次调用 · 表格版见 <a href="INDEX.md">INDEX.md</a></p></div>
  <div class="facts">{fact_html}</div>
</div></header>
<div class="shell">
  <nav role="tablist">{buttons}</nav>
  <main>{order_section}{portrait_section}{trust_section}</main>
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
