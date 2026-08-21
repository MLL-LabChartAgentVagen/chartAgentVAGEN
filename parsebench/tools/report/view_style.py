"""The look of the report, and the four primitives every section is built out of.

Kept apart from `view.py` so that the file holding the argument is not also the file
holding the border radii, and apart from `view_text.py` so that prose can be edited
without touching markup.

`Gallery` is the reason this file exists rather than a stylesheet. Every figure the
report shows is cut out of a page and carried inline, and the same figure is shown
under several arguments -- one page can be evidence for the panel key, for the
colour group and for the dual axis at once. Carried as `<img src="data:...">` each
of those would be another copy of the same 60 kB. So an image is inlined once as a
CSS rule and referenced by class, and the file stays roughly the size of the number
of *distinct* figures it shows.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field

CSS = """

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
a{color:var(--key); text-underline-offset:3px; text-decoration-color:var(--line)}
a:hover{text-decoration-color:currentColor}
:focus-visible{outline:2px solid var(--gap); outline-offset:2px; border-radius:3px}

.masthead{border-bottom:1px solid var(--line); background:var(--surface)}
.masthead .inner{max-width:1240px; margin:0 auto; padding:26px 24px 20px;
  display:flex; flex-wrap:wrap; gap:20px 40px; align-items:flex-end}
h1{margin:0; font-size:22px; font-weight:600; letter-spacing:-.01em; text-wrap:balance}
.tagline{margin:5px 0 0; color:var(--muted); font-size:13.5px; max-width:74ch}
.facts{display:flex; flex-wrap:wrap; gap:6px 28px; margin-left:auto}
.fact{display:flex; flex-direction:column}
.fact b{font-family:"IBM Plex Mono",monospace; font-size:17px; font-weight:500;
  font-variant-numeric:tabular-nums}
.fact span{font-size:11px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted)}

.shell{max-width:1240px; margin:0 auto; padding:0 24px 90px;
  display:grid; grid-template-columns:212px minmax(0,1fr); gap:44px; align-items:start}
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
main > section > .sub{color:var(--muted); font-size:13.5px; margin:0 0 22px; max-width:80ch}
h3.band{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin:34px 0 14px;
  font-size:15px; font-weight:600; padding-bottom:7px; border-bottom:2px solid var(--gap);
  scroll-margin-top:16px}
h3.band:first-of-type{margin-top:4px}
h3.band span{font-weight:400; font-size:12.5px; color:var(--muted)}
p{margin:0 0 12px; max-width:82ch}
blockquote{margin:12px 0 0; padding:12px 16px; background:var(--key-soft);
  border-left:3px solid var(--key); border-radius:0 8px 8px 0}
blockquote p{margin:0 0 6px; max-width:76ch; font-size:13px}
blockquote p:last-child{margin:0}
blockquote b{font-family:"IBM Plex Mono",monospace; font-weight:500; font-size:12px;
  color:var(--muted)}
ul{margin:0 0 14px; padding-left:20px; max-width:82ch}
li{margin:0 0 6px}
strong{font-weight:600}
code{background:var(--raised); padding:1.5px 5px; border-radius:4px; font-size:12.5px}
.lead{background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--gap);
  border-radius:0 10px 10px 0; padding:16px 20px; margin:0 0 22px; box-shadow:var(--shadow)}
.lead p{margin:0; font-size:15.5px; max-width:76ch}
.lead p + p{margin-top:10px; font-size:13.5px; color:var(--muted)}

.scroll{overflow-x:auto; margin:0 0 18px}
table{border-collapse:collapse; width:100%; font-size:13.5px}
.scroll > table{border:1px solid var(--line); border-radius:10px; background:var(--surface);
  box-shadow:var(--shadow); overflow:hidden}
th,td{padding:8px 12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line)}
thead th{background:var(--raised); font-weight:600; font-size:11.5px; letter-spacing:.05em;
  text-transform:uppercase; color:var(--muted); white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}
.scroll table code{background:transparent; padding:0; color:var(--key)}
td.gapn{color:var(--gap); font-weight:600}

.card{background:var(--surface); border:1px solid var(--line); border-radius:10px;
  margin-bottom:18px; overflow:hidden; box-shadow:var(--shadow); scroll-margin-top:16px}
.card > header{display:flex; flex-wrap:wrap; align-items:center; gap:8px 12px;
  padding:13px 18px; border-bottom:1px solid var(--line); background:var(--raised)}
.card h4{margin:0; font-size:15.5px; font-weight:600}
.card h4 em{font-style:normal; font-family:"IBM Plex Mono",monospace; color:var(--muted);
  margin-right:8px; font-size:14px}
.chips{margin-left:auto; display:flex; gap:6px; flex-wrap:wrap}
.chip{font-size:11px; letter-spacing:.04em; padding:2px 8px; border-radius:20px;
  border:1px solid var(--line); color:var(--muted); white-space:nowrap}
.chip.hi{color:var(--gap); border-color:var(--gap); background:var(--gap-soft); font-weight:600}
.chip.yes{color:var(--have); border-color:var(--have-soft); background:var(--have-soft)}
.chip.key{color:var(--key); border-color:var(--key-soft); background:var(--key-soft)}
p.aside{border-left:3px solid var(--line); padding:2px 0 2px 12px; margin:12px 0;
  color:var(--muted); font-size:13.5px}
p.aside b{color:var(--ink)}
b.ok{color:var(--have); font-weight:600}
b.no{color:var(--muted); font-weight:500}

.split{display:grid; grid-template-columns:300px minmax(0,1fr); gap:0}
.split > figure{margin:0; padding:14px; background:var(--raised);
  border-right:1px solid var(--line); display:flex; flex-direction:column; gap:8px}
.split > figure img{display:block; width:100%; height:auto; max-height:420px;
  object-fit:contain; object-position:top; border:1px solid var(--line);
  border-radius:4px; background:#fff}
.split > figure figcaption{font-size:11.5px; color:var(--muted); line-height:1.5}
.split > figure figcaption b{font-family:"IBM Plex Mono",monospace; font-weight:500;
  color:var(--ink); font-size:11.5px}
.split > .body{padding:16px 18px; min-width:0}
.split > .body > p:first-child{margin-top:0}
.split.noimg{grid-template-columns:minmax(0,1fr)}
.split.noimg > figure{display:none}

.two{display:grid; grid-template-columns:1fr 1fr; gap:0; margin:12px 0 0;
  border:1px solid var(--line); border-radius:8px; overflow:hidden}
.two > div{padding:11px 14px; min-width:0}
.two > div + div{border-left:1px solid var(--line)}
.two .score{background:var(--gap-soft)}
.two .cap{background:var(--have-soft)}
.two h5{margin:0 0 5px; font-size:11px; letter-spacing:.07em; text-transform:uppercase}
.two .score h5{color:var(--gap)}
.two .cap h5{color:var(--have)}
.two p{margin:0; font-size:13px; max-width:none}
.abl{margin:10px 0 0; padding:8px 12px; background:var(--raised); border-radius:8px;
  font-size:12.5px; color:var(--muted)}
.abl b{color:var(--ink); font-weight:600}

table.excerpt{font-size:12px; font-family:"IBM Plex Mono",monospace; width:auto; margin:8px 0 0}
table.excerpt td{padding:4px 8px; border:1px solid var(--line); white-space:nowrap}
table.excerpt td.head{background:var(--raised); font-weight:600}
table.excerpt td.key{background:var(--key-soft); color:var(--key); font-weight:600}
table.excerpt td.wrong{background:var(--gap-soft); color:var(--gap); font-weight:600;
  outline:1.5px solid var(--gap)}
table.excerpt td.val{background:var(--have-soft); color:var(--have); font-weight:600;
  outline:1.5px solid var(--have)}
.chip.val{color:var(--have); border-color:var(--have); background:var(--have-soft);
  font-weight:600}
.rule-line{background:var(--raised); border-radius:8px; padding:7px 11px;
  font-size:12.5px; margin:0 0 8px}
.rule-line b{font-family:"IBM Plex Mono",monospace; font-weight:500}

@media (max-width:1000px){
  .shell{grid-template-columns:minmax(0,1fr); gap:0}
  nav{position:static; max-height:none; flex-direction:row; flex-wrap:wrap;
    padding:16px 0 8px; border-bottom:1px solid var(--line)}
  nav button{border-left:0; border-bottom:2px solid transparent}
  nav button[aria-selected="true"]{border-left-color:transparent; border-bottom-color:var(--gap)}
  ul.toc{display:none}
  .split,.two{grid-template-columns:minmax(0,1fr)}
  .split > figure{border-right:0; border-bottom:1px solid var(--line)}
  .two > div + div{border-left:0; border-top:1px solid var(--line)}
  .facts{margin-left:0}
}

/* the conclusion and the index, above the tabs and visible whichever tab is open */
.opening{max-width:1240px; margin:0 auto; padding:26px 24px 6px}
.route{background:var(--have-soft); border:1px solid var(--have); border-radius:10px;
  padding:14px 18px; margin:0 0 22px}
.route p{margin:0; font-size:13.5px; max-width:none}
.opening h3.band{margin-top:26px}
.opening ul{list-style:none; padding:0}
.opening ul li{display:flex; gap:10px; align-items:baseline; font-size:13.5px}
button.jump{appearance:none; border:1px solid var(--line); background:var(--surface);
  color:var(--ink); font:inherit; font-size:13px; font-weight:600; cursor:pointer;
  padding:3px 11px; border-radius:20px; white-space:nowrap}
button.jump:hover{border-color:var(--gap); color:var(--gap)}

/* a window onto part of a page; click it to see the whole page */
.im{display:block; width:100%; background-repeat:no-repeat; background-color:#fff;
  border:1px solid var(--line); border-radius:5px; cursor:zoom-in; position:relative}
.im:hover{border-color:var(--key)}
.im::after{content:"点开看整页"; position:absolute; right:6px; bottom:6px;
  font-size:10.5px; padding:2px 7px; border-radius:20px; background:var(--surface);
  color:var(--muted); border:1px solid var(--line); opacity:0; transition:opacity .12s}
.im:hover::after{opacity:1}

/* the whole page, over everything else */
.lightbox{position:fixed; inset:0; z-index:50; background:rgba(10,13,17,.82);
  display:flex; align-items:center; justify-content:center; padding:28px;
  backdrop-filter:blur(2px)}
.lightbox[hidden]{display:none}
.lightbox .frame{background:var(--surface); border-radius:10px; padding:14px;
  max-width:min(1100px,94vw); width:100%; display:flex; flex-direction:column; gap:10px;
  box-shadow:0 24px 64px -24px rgba(0,0,0,.7)}
.lightbox .full{display:block; width:100%; height:min(78vh,1000px);
  background-repeat:no-repeat; background-position:center; background-size:contain;
  background-color:#fff; border:1px solid var(--line); border-radius:6px}
.lightbox .cap{margin:0; font-size:12.5px; color:var(--muted); display:flex;
  justify-content:space-between; gap:16px; align-items:baseline}
.lightbox .cap b{font-family:"IBM Plex Mono",monospace; font-weight:500; color:var(--ink)}
.lightbox .cap button{appearance:none; border:1px solid var(--line); background:none;
  color:var(--muted); font:inherit; font-size:12px; padding:3px 12px; border-radius:20px;
  cursor:pointer}
.lightbox .cap button:hover{border-color:var(--gap); color:var(--gap)}
figure.ex{margin:0; display:flex; flex-direction:column; gap:7px}
figure.ex figcaption{font-size:11.5px; color:var(--muted); line-height:1.5}
figure.ex figcaption b{font-family:"IBM Plex Mono",monospace; font-weight:500;
  color:var(--ink); font-size:11.5px}
.split > figure .im{max-height:none}

/* an example: the figure on the left, what it shows on the right */
.eg{display:grid; grid-template-columns:290px minmax(0,1fr); gap:0;
  border-top:1px solid var(--line)}
.eg > .pic{margin:0; padding:13px; background:var(--raised);
  border-right:1px solid var(--line)}
.eg > .txt{padding:13px 16px; min-width:0}
.eg > .txt > p:first-child{margin-top:0}
.eg .q{margin:0 0 8px; font-size:12.5px; font-family:"IBM Plex Mono",monospace;
  color:var(--ink); background:var(--key-soft); border-left:3px solid var(--key);
  padding:8px 12px; border-radius:0 6px 6px 0; max-width:none}
.eg .who{font-size:11px; color:var(--muted); letter-spacing:.04em}
.eg .who b{font-family:"IBM Plex Mono",monospace; font-weight:500; color:var(--ink)}

/* a change worked through on one number */
.worked{margin:14px 0 0; padding:12px 16px; background:var(--raised); border-radius:8px;
  border-left:3px solid var(--key)}
.worked h5{margin:0 0 8px; font-size:12px; letter-spacing:.05em; color:var(--key);
  text-transform:none}
.worked table.terms{margin:0}
.worked table.terms td{padding:6px 10px 6px 0; font-size:13px;
  border-bottom:1px solid var(--line)}
.worked table.terms tr:last-child td{border-bottom:0}
.worked table.terms td.term{color:var(--muted); font-weight:600}

/* the nine changes, as a strip of parts */
ul.parts{list-style:none; margin:0 0 10px; padding:0; display:flex; flex-direction:column;
  gap:5px}
ul.parts li{display:flex; gap:9px; font-size:13px; margin:0; align-items:baseline}
ul.parts li em{font-style:normal; font-family:"IBM Plex Mono",monospace; font-size:11px;
  color:var(--gap); border:1px solid var(--gap); border-radius:4px; padding:0 5px;
  flex:none}

/* the group headings in the sidebar -- the two halves of the document */
nav .group{font-size:16px; font-weight:600; color:var(--ink); letter-spacing:-.01em;
  padding:22px 12px 8px; border-bottom:2px solid var(--gap); margin:0 0 6px;
  display:flex; flex-direction:column; gap:2px}
nav .group:first-child{padding-top:0}
nav .group span{font-size:11.5px; font-weight:400; color:var(--muted);
  letter-spacing:0; line-height:1.4}
@media (max-width:1000px){nav .group{width:100%; padding:14px 0 4px}}

/* the definitions block above the tabs */
.defs{display:grid; grid-template-columns:minmax(0,420px) minmax(0,1fr); gap:0;
  background:var(--surface); border:1px solid var(--line); border-radius:10px;
  box-shadow:var(--shadow); overflow:hidden}
.defs > figure{margin:0; padding:18px; background:var(--raised);
  border-right:1px solid var(--line)}
.defs > .defbody{padding:6px 22px 18px; min-width:0}
.defs h3.band:first-child{margin-top:16px}
table.terms{margin:0 0 14px}
table.terms td{border-bottom:1px solid var(--line); padding:9px 12px 9px 0}
table.terms tr:last-child td{border-bottom:0}
table.terms td.term{white-space:nowrap; font-weight:600; width:1%; padding-right:16px;
  vertical-align:top}
table.terms td.mono{font-family:"IBM Plex Mono",monospace; font-size:12.5px;
  color:var(--key); white-space:nowrap; width:1%; padding-right:16px; vertical-align:top}
@media (max-width:1000px){
  .defs{grid-template-columns:minmax(0,1fr)}
  .defs > figure{border-right:0; border-bottom:1px solid var(--line)}
  table.terms td.term,table.terms td.mono{white-space:normal}
}
"""


@dataclass
class Gallery:
    """Every page the report shows, inlined once, plus the boxes drawn on them.

    A page is inlined as one CSS rule. A thumbnail of one figure on that page is a
    second rule that points a window at part of the same image, so a page used as
    evidence under three different changes still costs the bytes of one page -- and
    clicking any thumbnail can show the whole page, because the whole page is what
    was inlined.
    """

    _pages: dict[str, str] = field(default_factory=dict)          # stem -> class
    _uris: dict[str, str] = field(default_factory=dict)           # stem -> data uri
    _views: dict[tuple, str] = field(default_factory=dict)        # (stem, box) -> class
    _rules: dict[str, str] = field(default_factory=dict)          # class -> css body

    def page(self, stem: str, uri: str) -> str:
        if stem not in self._pages:
            self._pages[stem] = f"pg-{len(self._pages) + 1}"
            self._uris[stem] = uri
        return self._pages[stem]

    def view(self, stem: str, box: tuple[float, float, float, float],
             page_width: int, page_height: int) -> str:
        """The class that shows just `box` of the page, keeping the box's own shape."""
        key = (stem, tuple(round(v, 4) for v in box))
        if key in self._views:
            return self._views[key]
        x0, y0, x1, y1 = box
        wide, tall = max(x1 - x0, 1e-3), max(y1 - y0, 1e-3)
        left = 0.0 if wide >= 1 else x0 / (1 - wide) * 100
        top = 0.0 if tall >= 1 else y0 / (1 - tall) * 100
        name = f"vw-{len(self._views) + 1}"
        self._views[key] = name
        self._rules[name] = (f"aspect-ratio:{wide * page_width:.1f}/{tall * page_height:.1f};"
                             f"background-size:{100 / wide:.2f}% {100 / tall:.2f}%;"
                             f"background-position:{left:.2f}% {top:.2f}%")
        return name

    def css(self) -> str:
        pages = "\n".join(f".{self._pages[stem]}{{background-image:url({self._uris[stem]})}}"
                           for stem in self._pages)
        views = "\n".join(f".{name}{{{body}}}" for name, body in self._rules.items())
        return pages + "\n" + views

    def __len__(self) -> int:
        return len(self._pages)


def esc(text: object) -> str:
    return html.escape(str(text), quote=False)


def table(headers: tuple[str, ...], rows: list[tuple], numeric: tuple[int, ...] = ()) -> str:
    """One table. `numeric` names the columns that are right-aligned tabular figures."""
    head = "".join(f'<th{" class=\"num\"" if i in numeric else ""}>{esc(h)}</th>'
                   for i, h in enumerate(headers))
    body = []
    for row in rows:
        cells = "".join(f'<td{" class=\"num\"" if i in numeric else ""}>{cell}</td>'
                        for i, cell in enumerate(row))
        body.append(f"<tr>{cells}</tr>")
    return (f'<div class="scroll"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def chips(*items: tuple[str, str]) -> str:
    """`(text, kind)` each, kind being one of `hi`, `yes`, `key` or empty."""
    inner = "".join(f'<span class="chip{" " + kind if kind else ""}">{esc(text)}</span>'
                    for text, kind in items if text)
    return f'<div class="chips">{inner}</div>' if inner else ""


def two(score: str, capability: str) -> str:
    """The two effects, side by side and never summed: they are not on one scale."""
    return (f'<div class="two"><div class="score"><h5>对 ParseBench 分数</h5><p>{score}</p></div>'
            f'<div class="cap"><h5>对流水线的能力</h5><p>{capability}</p></div></div>')


def example(picture: str, caption: str, quote: str, why: str, who: str) -> str:
    """One example: the figure it was read off, the words on the page, what they show."""
    return (f'<div class="eg"><figure class="pic ex">{picture}'
            f'<figcaption>{caption}</figcaption></figure>'
            f'<div class="txt"><p class="q">{esc(quote)}</p><p>{why}</p>'
            f'<p class="who">{who}</p></div></div>')
