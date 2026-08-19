"""Build the merged report's illustrated companion, in both languages.

`synthesis/INDEX.md` and `INDEX.en.md` carry the argument; this splices the evidence
into it. One `## ` heading becomes one tab, one `### ` heading becomes one entry in
that tab's table of contents, and after the headings that make a claim about a
specific construct the matching card gallery is inserted -- so the page can be read
on its own, without the two analyses it merges and without their directories.

Usage:
    python parsebench/tools/synthesis/build_view.py            # both languages
    python parsebench/tools/synthesis/build_view.py zh         # one
    python parsebench/tools/synthesis/build_view.py --no-assets
"""

from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import view as v  # noqa: E402
from content import AXES, CASES, FACTS, FORMS, KEY_AXIS, UI  # noqa: E402
from data import PARSEBENCH, Sources, load_sources, write_assets  # noqa: E402
from index import component_documents, component_pages, pick_examples  # noqa: E402

OUT = PARSEBENCH / "synthesis"

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
a{color:inherit; text-underline-offset:3px; text-decoration-color:var(--line)}
a:hover{text-decoration-color:currentColor}
:focus-visible{outline:2px solid var(--gap); outline-offset:2px; border-radius:3px}

.masthead{border-bottom:1px solid var(--line); background:var(--surface)}
.masthead .inner{max-width:1240px; margin:0 auto; padding:26px 24px 20px;
  display:flex; flex-wrap:wrap; gap:20px 40px; align-items:flex-end}
h1{margin:0; font-size:22px; font-weight:600; letter-spacing:-.01em; text-wrap:balance}
.tagline{margin:5px 0 0; color:var(--muted); font-size:13.5px; max-width:70ch}
.tagline a{color:var(--key)}
.facts{display:flex; flex-wrap:wrap; gap:6px 28px; margin-left:auto}
.fact{display:flex; flex-direction:column}
.fact b{font-family:"IBM Plex Mono",monospace; font-size:17px; font-weight:500;
  font-variant-numeric:tabular-nums}
.fact span{font-size:11px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted)}

.shell{max-width:1240px; margin:0 auto; padding:0 24px 90px;
  display:grid; grid-template-columns:206px minmax(0,1fr); gap:44px; align-items:start}
nav{position:sticky; top:0; padding:28px 0; display:flex; flex-direction:column; gap:2px;
  max-height:100vh; overflow-y:auto}
nav button{appearance:none; border:0; background:none; color:var(--muted); cursor:pointer;
  font:inherit; font-size:14px; text-align:left; padding:7px 12px; border-radius:6px;
  border-left:2px solid transparent; display:flex; justify-content:space-between; gap:10px}
nav button:hover{background:var(--raised); color:var(--ink)}
nav button[aria-selected="true"]{color:var(--ink); font-weight:600;
  border-left-color:var(--gap); background:var(--raised)}
nav button i{font-style:normal; font-family:"IBM Plex Mono",monospace; font-size:12px;
  color:var(--muted); font-variant-numeric:tabular-nums}
ul.toc{list-style:none; margin:2px 0 10px; padding:0 0 0 14px; border-left:1px solid var(--line)}
ul.toc li{margin:0}
ul.toc a{display:block; padding:4px 8px; font-size:12.5px; color:var(--muted);
  text-decoration:none; border-radius:5px; line-height:1.35}
ul.toc a:hover{background:var(--raised); color:var(--ink)}
ul.toc a.at{color:var(--gap); background:var(--gap-soft); font-weight:500}

main{padding:28px 0 0; min-width:0}
section[hidden]{display:none}
main > section > h2{margin:0 0 6px; font-size:20px; font-weight:600; letter-spacing:-.01em}
h3.band{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin:34px 0 14px;
  font-size:15px; font-weight:600; padding-bottom:7px; border-bottom:2px solid var(--gap);
  scroll-margin-top:16px}
h3.band:first-of-type{margin-top:4px}
h4{margin:24px 0 10px; font-size:14px; font-weight:600}
h4.form{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap}
h4.form code{font-size:12.5px; color:var(--gap); background:var(--gap-soft);
  padding:2px 7px; border-radius:5px}
h4.form span{font-weight:400; font-size:12.5px; color:var(--muted)}
p{margin:0 0 12px; max-width:80ch}
blockquote{margin:16px 0; padding:14px 18px; background:var(--key-soft);
  border-left:3px solid var(--key); border-radius:0 8px 8px 0}
blockquote p{margin:0 0 8px; max-width:76ch}
blockquote p:last-child{margin:0}
ul,ol{margin:0 0 14px; padding-left:22px; max-width:80ch}
li{margin:0 0 6px}
strong{font-weight:600}
code{background:var(--raised); padding:1.5px 5px; border-radius:4px; font-size:12.5px}

.scroll{overflow-x:auto; margin:0 0 18px}
table{border-collapse:collapse; width:100%; font-size:13.5px}
.scroll > table{border:1px solid var(--line); border-radius:10px; background:var(--surface);
  box-shadow:var(--shadow); overflow:hidden}
th,td{padding:8px 12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line)}
thead th{background:var(--raised); font-weight:600; font-size:11.5px; letter-spacing:.05em;
  text-transform:uppercase; color:var(--muted); white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
table.kv thead{display:none}
table.kv td:first-child{width:200px; font-weight:600; background:var(--raised); white-space:nowrap}
.scroll table code{background:transparent; padding:0; color:var(--key)}

.card{background:var(--surface); border:1px solid var(--line); border-radius:10px;
  margin-bottom:18px; overflow:hidden; box-shadow:var(--shadow); scroll-margin-top:16px}
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

.split{display:grid; grid-template-columns:minmax(280px,1fr) minmax(0,1fr); gap:0}
.split .prose{padding:18px; display:flex; flex-direction:column; gap:12px;
  border-right:1px solid var(--line); min-width:0}
.split p{margin:0; font-size:13.5px; max-width:none}
.split .label{display:block; font-size:11px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--muted); margin-bottom:3px}
.split .criterion{color:var(--muted); font-size:12.5px; font-style:italic}
.quote{display:inline-block; background:var(--raised); border-left:2px solid var(--gap);
  padding:3px 9px; border-radius:0 5px 5px 0; font-size:12.5px;
  font-family:"IBM Plex Mono",ui-monospace,monospace; overflow-wrap:anywhere}
.price b{font-family:"IBM Plex Mono",monospace; color:var(--gap)}
.fig{display:block; font-size:12.5px; color:var(--muted); line-height:1.75;
  overflow-wrap:anywhere}
.fig + .fig{margin-top:6px; padding-top:6px; border-top:1px dashed var(--line)}
figure{margin:0; padding:18px; background:var(--raised); display:flex;
  flex-direction:column; gap:8px; align-items:center; justify-content:center}
figure img{max-width:100%; max-height:470px; border:1px solid var(--line); border-radius:4px;
  background:#fff; display:block}
figcaption{font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--muted);
  text-align:center; word-break:break-all}
.no-image img{display:none}
.no-image .hint{display:block}
.hint{display:none; font-size:12.5px; color:var(--muted); text-align:center; padding:40px 12px}

.ev{background:var(--surface); border:1px solid var(--line); border-radius:14px;
  margin:16px 0 22px; box-shadow:var(--shadow); display:grid; overflow:hidden;
  grid-template-columns:270px minmax(0,1fr); scroll-margin-top:16px;
  grid-template-areas:"fig body" "vs vs" "tail tail"}
.ev > figure{grid-area:fig; margin:0; padding:0; background:var(--raised);
  border-right:1px solid var(--line); display:flex; align-items:flex-start}
.ev > figure img{display:block; width:100%; height:auto; max-height:360px;
  object-fit:contain; object-position:top; border:0; border-radius:0}
.ev > figure figcaption{display:none}
.ev > .body{grid-area:body; padding:14px 18px 8px; min-width:0}
.ev > .vs{grid-area:vs}
.ev > .tail{grid-area:tail; padding:0 18px 16px; font-size:12px; color:var(--muted);
  font-family:"IBM Plex Mono",monospace; overflow-wrap:anywhere}
.ev.no-image{grid-template-columns:minmax(0,1fr); grid-template-areas:"body" "vs" "tail"}
.ev.no-image > figure{display:none}
.ev h4{margin:0 0 4px; font-size:15px; font-weight:600}
.ev .axis-tag{font-size:11px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--muted); margin:0 0 6px}
.ev .axis-tag b{color:var(--gap); font-family:"IBM Plex Mono",monospace}
.ev .meta{color:var(--muted); font-size:12.5px; margin:0 0 10px}
.ev p{margin:0 0 10px; font-size:14px; max-width:none}
.ev .says .label{display:block; font-size:11px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--muted); margin-bottom:3px}
.ev .says{font-size:13.5px}
.vs{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  border-top:1px solid var(--line)}
.vs > div{padding:12px 18px 14px; min-width:0}
.vs > div + div{border-left:1px solid var(--line)}
.vs .bad{background:var(--gap-soft)}
.vs .good{background:var(--have-soft)}
.side-h{font-size:12.5px; font-weight:600; margin:0 0 8px}
.vs .bad .side-h{color:var(--gap)}
.vs .good .side-h{color:var(--have)}
.why{font-size:12.5px; color:var(--muted); margin:8px 0 0; line-height:1.55}
.why b{color:var(--ink)}
.rule-line{background:var(--raised); border-radius:8px; padding:7px 11px;
  font-size:13px; margin:0 0 10px}
.rule-line b{font-family:"IBM Plex Mono",monospace}
.grid-cap{font-size:12px; color:var(--muted); margin:0 0 4px}
table.excerpt{font-size:12.5px; font-family:"IBM Plex Mono",monospace; width:auto}
table.excerpt td{padding:4px 8px; border:1px solid var(--line); white-space:nowrap}
table.excerpt td.head{background:var(--raised); font-weight:600}
table.excerpt td.hit{background:var(--have-soft); color:var(--have); font-weight:600;
  outline:1.5px solid var(--have)}
table.excerpt td.wrong{background:var(--gap-soft); color:var(--gap); font-weight:600;
  outline:1.5px solid var(--gap)}
table.excerpt td.key{background:var(--key-soft); color:var(--key)}
table.excerpt.good td{border-color:var(--have)}
table.excerpt.good td.head{background:var(--have-soft); color:var(--have)}

.egs{display:flex; gap:12px; flex-wrap:wrap; margin:6px 0 20px}
.egs a{display:block; width:196px; text-decoration:none}
.egs img{display:block; width:196px; height:132px; object-fit:cover; object-position:top;
  border:1px solid var(--line); border-radius:8px; background:var(--raised)}
.egs b{display:block; font-size:12px; margin-top:5px; line-height:1.4}
.egs span{display:block; font-size:11.5px; color:var(--muted); margin-top:2px;
  line-height:1.4; overflow-wrap:anywhere}
.gallery-h{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin:26px 0 12px;
  font-size:13px; font-weight:600; color:var(--muted); letter-spacing:.04em;
  text-transform:uppercase}
.gallery-h i{font-style:normal; font-family:"IBM Plex Mono",monospace; font-weight:400}

@media (max-width:1000px){
  .shell{grid-template-columns:minmax(0,1fr); gap:0}
  nav{position:static; max-height:none; flex-direction:row; flex-wrap:wrap;
    padding:16px 0 8px; border-bottom:1px solid var(--line)}
  nav button{border-left:0; border-bottom:2px solid transparent}
  nav button[aria-selected="true"]{border-left-color:transparent; border-bottom-color:var(--gap)}
  ul.toc{display:none}
  .split{grid-template-columns:1fr}
  .split .prose{border-right:0; border-bottom:1px solid var(--line)}
  .ev{grid-template-columns:minmax(0,1fr); grid-template-areas:"fig" "body" "vs" "tail"}
  .ev > figure{border-right:0; border-bottom:1px solid var(--line)}
  .vs{grid-template-columns:1fr}
  .vs > div + div{border-left:0; border-top:1px solid var(--line)}
  .facts{margin-left:0}
}
"""

SCRIPT = """
const tabs=[...document.querySelectorAll('nav button')];
tabs.forEach(tab=>{
  const heads=[...document.getElementById(tab.dataset.tab).querySelectorAll('h3.band')];
  if(!heads.length) return;
  const list=document.createElement('ul');
  list.className='toc'; list.dataset.for=tab.dataset.tab;
  heads.forEach(h=>{
    const item=document.createElement('li'), a=document.createElement('a');
    a.href='#'+h.id; a.textContent=h.textContent.trim();
    item.appendChild(a); list.appendChild(item);
  });
  tab.after(list);
});
const owner=id=>{
  const node=document.getElementById(id), section=node&&node.closest('main > section');
  return section?section.id:null;
};
const show=id=>{
  tabs.forEach(t=>t.setAttribute('aria-selected',String(t.dataset.tab===id)));
  document.querySelectorAll('main > section').forEach(s=>{s.hidden=(s.id!==id)});
  document.querySelectorAll('.toc').forEach(u=>{u.hidden=(u.dataset.for!==id)});
};
tabs.forEach(t=>t.addEventListener('click',()=>{
  history.replaceState(null,'','#'+t.dataset.tab); show(t.dataset.tab);
  window.scrollTo({top:0});}));
document.addEventListener('click',e=>{
  const a=e.target.closest('a[href^="#"]');
  if(!a) return;
  const id=decodeURIComponent(a.getAttribute('href').slice(1));
  const tab=tabs.find(t=>t.dataset.tab===id), target=document.getElementById(id);
  if(!tab&&!target) return;
  e.preventDefault();
  show(tab?id:owner(id));
  history.replaceState(null,'','#'+id);
  if(tab) window.scrollTo({top:0});
  else target.scrollIntoView({behavior:'smooth',block:'start'});
});
const spy=()=>{
  let here=null;
  document.querySelectorAll('main > section:not([hidden]) h3.band').forEach(h=>{
    if(h.getBoundingClientRect().top<140) here=h.id;
  });
  document.querySelectorAll('.toc a').forEach(
    a=>a.classList.toggle('at',decodeURIComponent(a.getAttribute('href'))==='#'+here));
};
addEventListener('scroll',spy,{passive:true});
const wanted=decodeURIComponent(location.hash.slice(1));
const start=tabs.find(t=>t.dataset.tab===wanted);
show(start?wanted:(owner(wanted)||tabs[0].dataset.tab));
if(!start&&wanted){
  const target=document.getElementById(wanted);
  if(target) target.scrollIntoView({block:'start'});
}
spy();
"""


# ---------------------------------------------------------------- galleries


def _gallery_head(title: str, count: str) -> str:
    return f'<p class="gallery-h">{escape(title)} <i>{escape(count)}</i></p>'


def _strip(items: list[tuple[str, str, str, str]]) -> str:
    """A row of page thumbnails: image, one line of claim, one line of detail."""
    cells = "".join(
        f'<a href="{href}"><img loading="lazy" src="assets/{quote(stem)}.jpg" '
        f'alt="{escape(stem)}"><b>{v.rich(title)}</b><span>{v.rich(note)}</span></a>'
        for stem, title, note, href in items)
    return f'<div class="egs">{cells}</div>'


def _case_gallery(sources: Sources, lang: str) -> str:
    """Every failure form, with the pages that show it."""
    out = []
    total = sum(sources.stats["kinds"].values())
    for kind, zh, en, counted in FORMS:
        cases = [c for c in CASES if c.kind == kind]
        if not cases:
            continue
        count = sum(sources.stats["kinds"].get(k, 0) for k in counted)
        out.append(f'<h4 class="form"><code>{escape(kind)}</code> '
                   f"{escape(v.t((zh, en), lang))} "
                   f'<span>{count} · {count / total:.1%}</span></h4>')
        out += [v.case_card(case, sources, lang) for case in cases]
    return "".join(out)


def _price_strip(sources: Sources, keys: list[str], lang: str) -> str:
    """The reclassified components, priced, linking to their card on the axis tab."""
    from vocabulary import BY_KEY
    examples = pick_examples(sources.pages, keys, limit=1)
    items = []
    for key in keys:
        sample = examples.get(key) or []
        price = sources.stat_component(key)
        if not sample or not price:
            continue
        name = BY_KEY[key].name_zh if lang == "zh" else BY_KEY[key].name_en
        items.append((sample[0].stem, f"`{key}` {price['delta']:+.1%}",
                      f"{name} · {price['pages']} {v.t(UI['pages'], lang)} / "
                      f"{price['documents']} {v.t(UI['docs'], lang)}", f"#gap-{quote(key)}"))
    return _strip(items)


def _axis_gallery(axis_id: str, sources: Sources, examples, counts, documents,
                  lang: str) -> str:
    """One axis: every gap it absorbs as a card, and its failure pages as a strip."""
    keys = [k for k, a in KEY_AXIS.items() if a == axis_id]
    keys.sort(key=lambda k: -counts[k])
    cases = [c for c in CASES if c.axis == axis_id]
    strip = _strip([(c.stem, v.t((c.mech_zh, c.mech_en), lang).split("。")[0].split(". ")[0],
                     c.stem, f"#case-{quote(c.stem)}") for c in cases]) if cases else ""
    head = _gallery_head(v.t(UI["gallery"], lang),
                         f"{len(keys)} + {len(cases)}" if cases else str(len(keys)))
    cards = "".join(v.gap_card(k, sources, examples, counts, documents, lang) for k in keys)
    return head + strip + cards


def _type_gallery(sources: Sources, lang: str) -> str:
    return "".join(v.type_card(name, sources, lang) for name in ("map", "other"))


def splice(head: str, sources: Sources, examples, counts, documents, lang: str) -> str:
    """The gallery that belongs under this heading, keyed by the heading's own number.

    Matching on the number rather than the words is what lets the same rule serve
    both languages, and it keeps the insertion points visible in `INDEX.md` itself.
    """
    tag = head.split(" ")[0].rstrip("·")
    if tag == "1.3":
        return _price_strip(sources, ["reference_line", "annotation_callout"], lang)
    if tag == "1.4":
        return _case_gallery(sources, lang)
    if tag == "3.4":
        return _type_gallery(sources, lang)
    if re.fullmatch(r"A[1-5]", tag):
        return _axis_gallery(tag.lower(), sources, examples, counts, documents, lang)
    return ""


# ------------------------------------------------------------------- assembly


def illustrated(sources: Sources, examples) -> list[str]:
    stems = [c.stem for c in CASES]
    for key in KEY_AXIS:
        stems += [p.stem for p in (examples.get(key) or [])[:1]]
    for name in ("map", "other"):
        from index import countable_figures
        for page in sorted(sources.pages, key=lambda p: (len(countable_figures(p)), p.stem)):
            if any(str(f.get("type")) == name for f in countable_figures(page)):
                stems.append(page.stem)
                break
    return sorted(set(stems))


def build(lang: str, sources: Sources, examples, counts, documents) -> Path:
    source = OUT / ("INDEX.md" if lang == "zh" else "INDEX.en.md")
    text = source.read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    parts = re.split(r"^## ", text, flags=re.M)

    tabs, sections = [], []
    for part in parts[1:]:
        head, _, rest = part.partition("\n")
        tab_id = v.slug(head)
        pieces = re.split(r"^### ", rest, flags=re.M)
        html = [f"<h2>{v.rich(head)}</h2>", v.markdown(pieces[0])]
        for piece in pieces[1:]:
            sub, _, body = piece.partition("\n")
            html.append(f'<h3 class="band" id="{escape(v.slug(sub), quote=True)}">'
                        f"{v.rich(sub)}</h3>")
            html.append(v.markdown(body))
            html.append(splice(sub, sources, examples, counts, documents, lang))
        number, _, label = head.partition(" ")
        tabs.append(f'<button role="tab" data-tab="{escape(tab_id, quote=True)}">'
                    f"<span>{v.rich(label)}</span><i>{escape(number)}</i></button>")
        sections.append(f'<section id="{escape(tab_id, quote=True)}" hidden>'
                        + "".join(html) + "</section>")

    facts = "".join(f"<div class='fact'><b>{a}</b><span>{b}</span></div>"
                    for a, b in FACTS[lang])
    switch = UI["switch"][0] if lang == "zh" else UI["switch"][1]
    src = UI["source"][0] if lang == "zh" else UI["source"][1]
    page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{escape(v.t(UI["title"], lang))}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
</head>
<body>
<header class="masthead"><div class="inner">
  <div>
    <h1>{v.rich(title)}</h1>
    <p class="tagline">{escape(v.t(UI["tagline"], lang))}
      · <a href="{switch[1]}">{switch[0]}</a> · <a href="{src[0]}">{src[1]}</a></p>
  </div>
  <div class="facts">{facts}</div>
</div></header>
<div class="shell">
  <nav role="tablist">{''.join(tabs)}</nav>
  <main>{''.join(sections)}</main>
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
    target = OUT / ("view.html" if lang == "zh" else "view.en.html")
    target.write_text(page, encoding="utf-8")
    return target


def main() -> None:
    languages = [a for a in sys.argv[1:] if not a.startswith("-")] or ["zh", "en"]
    sources = load_sources()
    counts = component_pages(sources.pages)
    documents = component_documents(sources.pages)
    examples = pick_examples(sources.pages, list(KEY_AXIS), limit=3)
    stems = illustrated(sources, examples)
    if "--no-assets" not in sys.argv:
        write_assets(stems, OUT, PARSEBENCH / "data" / "pages")
    for lang in languages:
        written = build(lang, sources, examples, counts, documents)
        print(f"{written}  {written.stat().st_size // 1024} KB")
    print(f"-> {len(stems)} page images in {OUT}/assets/")


if __name__ == "__main__":
    main()
