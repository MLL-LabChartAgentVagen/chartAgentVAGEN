"""Rendering one of the generated sites in another language.

The pages are built from one set of sources; a second language is the same pages with
their text replaced. Doing that on the rendered HTML rather than on the builders keeps
one source of truth for what the pages say -- a sentence assembled from three pieces
in the builder appears here as the one sentence a reader sees, and it is translated
once instead of in pieces that no longer read as a sentence.

Numbers are not translated. Every run of digits is lifted out before the lookup and
put back afterwards, so `1204 项测试` and `1209 项测试` are one entry, and the entry
carries the number back in the position the English sentence wants it.

Nothing is silently left in the original language: a run with no entry is reported and
counted, and the caller decides whether that is acceptable.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: Any run of digits, with the separators a number may carry inside it.
NUMBER = re.compile(r"\d[\d,  .]*")

#: Text between two tags, and the attributes a reader can see.
TEXT_RUN = re.compile(r">([^<>]*)<")
ATTR_RUN = re.compile(r'\b(title|alt|aria-label|placeholder)="([^"]*)"')

CJK = re.compile(r"[一-鿿]")

#: What a number was lifted out to. Chosen so it survives a translator unchanged and
#: cannot occur in either language's text.
SLOT = "①"


def template(text: str) -> tuple[str, list[str]]:
    """The text with its numbers lifted out, and the numbers in the order found."""
    found: list[str] = []

    def take(match: re.Match) -> str:
        found.append(match.group(0))
        return SLOT

    return NUMBER.sub(take, text), found


def fill(text: str, numbers: list[str]) -> str:
    """Put the numbers back into a translated template, in order."""
    out: list[str] = []
    rest = iter(numbers)
    for i, piece in enumerate(text.split(SLOT)):
        if i:
            out.append(next(rest, ""))
        out.append(piece)
    return "".join(out)


def translate(html: str, glossary: dict[str, str]) -> tuple[str, list[str]]:
    """The page in the other language, and every run that had no entry."""
    missing: list[str] = []

    def one(text: str) -> str:
        if not CJK.search(text):
            return text
        key, numbers = template(text)
        stripped = key.strip()
        if stripped not in glossary:
            missing.append(stripped)
            return text
        lead = key[:len(key) - len(key.lstrip())]
        tail = key[len(key.rstrip()):]
        return fill(lead + glossary[stripped] + tail, numbers)

    html = TEXT_RUN.sub(lambda m: ">" + one(m.group(1)) + "<", html)
    html = ATTR_RUN.sub(lambda m: f'{m.group(1)}="{one(m.group(2))}"', html)
    return html, missing


def runs_in(html: str) -> list[str]:
    """Every distinct run a glossary would need an entry for."""
    seen: dict[str, None] = {}
    for text in ([m.group(1) for m in TEXT_RUN.finditer(html)]
                 + [m.group(2) for m in ATTR_RUN.finditer(html)]):
        if CJK.search(text):
            seen.setdefault(template(text)[0].strip(), None)
    return list(seen)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", nargs="+", type=Path)
    parser.add_argument("--extract", action="store_true",
                        help="write the runs a glossary still needs, one per line")
    parser.add_argument("--suffix", default="_en",
                        help="added to each page's name; empty overwrites it")
    args = parser.parse_args()

    from tools.glossary_en import GLOSSARY

    needed: dict[str, None] = {}
    for page in args.pages:
        html = page.read_text(encoding="utf-8")
        if args.extract:
            for run in runs_in(html):
                if run not in GLOSSARY:
                    needed.setdefault(run, None)
            continue
        done, missing = translate(html, GLOSSARY)
        out = page.with_name(page.stem + args.suffix + page.suffix)
        out.write_text(done, encoding="utf-8")
        print(f"{out}  {len(missing)} runs left untranslated")
        for run in dict.fromkeys(missing):
            needed.setdefault(run, None)
    if needed:
        Path("/tmp/needs_translation.txt").write_text(
            "\n".join(needed), encoding="utf-8")
        print(f"{len(needed)} runs need an entry -> /tmp/needs_translation.txt")


if __name__ == "__main__":
    main()
