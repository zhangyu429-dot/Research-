#!/usr/bin/env python3
"""Render a markdown research memo to a print-ready PDF.

Tuned for Chinese-language documents: CJK font stack, generous leading, and
table/blockquote handling that survives page breaks.

    python3 tools/md_to_pdf.py research/603061-jinhaitong/key-questions.zh.md

Requires `markdown` and `playwright` (pip install markdown playwright). Uses the
Chromium already present at PLAYWRIGHT_BROWSERS_PATH; it does not download one.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

# Prefer Noto if the image has it, fall back to WenQuanYi, then anything CJK.
CJK_STACK = (
    '"Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", '
    '"WenQuanYi Zen Hei", "Microsoft YaHei", sans-serif'
)

CSS = f"""
@page {{ size: A4; margin: 18mm 16mm 16mm; }}

* {{ box-sizing: border-box; }}

body {{
  font-family: {CJK_STACK};
  font-size: 10.5pt;
  line-height: 1.85;
  color: #1a1a1a;
  margin: 0;
  text-align: justify;
  -webkit-font-smoothing: antialiased;
}}

/* Headings ---------------------------------------------------------------- */
h1 {{
  font-size: 19pt; line-height: 1.4; margin: 0 0 4pt;
  padding-bottom: 8pt; border-bottom: 2px solid #1a1a1a;
  text-align: left; letter-spacing: .3pt;
}}
h2 {{
  font-size: 13pt; margin: 22pt 0 8pt; padding-left: 9pt;
  border-left: 3.5px solid #b3282d; text-align: left;
  break-after: avoid; page-break-after: avoid;
}}
h3 {{
  font-size: 11.5pt; margin: 16pt 0 6pt; text-align: left;
  break-after: avoid; page-break-after: avoid;
}}
h1 + p em, h1 + p {{ color: #666; }}

/* Body -------------------------------------------------------------------- */
p {{ margin: 0 0 8pt; }}
strong {{ font-weight: 700; color: #000; }}
em {{ font-style: normal; color: #666; }}
hr {{ border: 0; border-top: 1px solid #ddd; margin: 16pt 0; }}

ul, ol {{ margin: 0 0 10pt; padding-left: 20pt; }}
li {{ margin-bottom: 4pt; }}
li > ul, li > ol {{ margin-top: 4pt; }}

/* Blockquote — carries the framing statements, keep it whole -------------- */
blockquote {{
  margin: 12pt 0; padding: 10pt 14pt;
  background: #f7f7f5; border-left: 3.5px solid #b3282d;
  break-inside: avoid; page-break-inside: avoid;
}}
blockquote p:last-child {{ margin-bottom: 0; }}

/* Tables ------------------------------------------------------------------ */
table {{
  width: 100%; border-collapse: collapse; margin: 10pt 0 14pt;
  font-size: 9pt; line-height: 1.6;
  break-inside: avoid; page-break-inside: avoid;
}}
th, td {{
  border: 1px solid #d8d8d8; padding: 5pt 7pt;
  text-align: left; vertical-align: top;
  word-break: normal; overflow-wrap: normal;
}}
th {{ background: #f0efec; font-weight: 700; }}
tbody tr:nth-child(even) {{ background: #fafaf9; }}

/* Links — printed, so show them quietly rather than as blue underlines --- */
a {{ color: #24486b; text-decoration: none; overflow-wrap: anywhere; }}

code {{
  font-family: "DejaVu Sans Mono", monospace; font-size: 9pt;
  background: #f2f2f0; padding: 1pt 3pt; border-radius: 2px;
}}
pre {{
  background: #f7f7f5; padding: 8pt 10pt; border-radius: 3px;
  overflow-x: auto; break-inside: avoid;
}}
pre code {{ background: none; padding: 0; }}

/* The source list is reference material: tighter and quieter -------------- */
h3#资料来源 ~ ul, h3[id*="source"] ~ ul {{ font-size: 8.5pt; line-height: 1.55; }}
"""

FOOTER = """
<div style="width:100%; font-size:7.5pt; color:#888; padding:0 16mm;
            font-family:sans-serif; display:flex; justify-content:space-between;">
  <span>__TITLE__</span>
  <span>__PAGING__</span>
</div>
"""

PAGING = {
    "zh": '第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页',
    "en": 'Page <span class="pageNumber"></span> of <span class="totalPages"></span>',
}


# CJK ideographs, CJK punctuation, and fullwidth forms.
CJK = r"\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef"
_WRAPPED_CJK = re.compile(f"(?<=[{CJK}])\n(?=[{CJK}])")


def unwrap_cjk(md_text: str) -> str:
    """Drop newlines that fall between two CJK characters.

    Markdown turns a source line break into a space. Between Latin words that is
    correct; between Chinese characters it renders as a visible gap mid-sentence.
    Fenced code blocks are left untouched, and block markers (#, |, -, >) are
    never CJK, so list and table starts are safe from the lookahead.
    """
    parts = md_text.split("```")
    for i in range(0, len(parts), 2):  # even indices are outside fences
        parts[i] = _WRAPPED_CJK.sub("", parts[i])
    return "```".join(parts)


_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+")


def space_lists(md_text: str) -> str:
    """Insert the blank line python-markdown needs before a list that follows a paragraph.

    CommonMark — and therefore the GitHub view of these memos — starts a list
    immediately after a paragraph line. `sane_lists` does not: it silently folds the
    items into the paragraph, which turns every `**Ask:**` block into a run-on. An
    indented previous line is a lazy continuation of the item above, so leave those
    alone rather than loosening the list. Fenced blocks are untouched.
    """
    parts = md_text.split("```")
    for i in range(0, len(parts), 2):  # even indices are outside fences
        out: list[str] = []
        for line in parts[i].split("\n"):
            prev = out[-1] if out else ""
            if (prev.strip() and _LIST_ITEM.match(line)
                    and not _LIST_ITEM.match(prev)
                    and not prev.startswith((" ", "\t"))):
                out.append("")
            out.append(line)
        parts[i] = "\n".join(out)
    return "```".join(parts)


def detect_lang(md_text: str) -> str:
    """"zh" if the prose is meaningfully Chinese, else "en".

    English memos still quote Chinese company and line-item names, so a nonzero
    CJK count is not enough — measure its share of the text instead.
    """
    cjk = len(re.findall(f"[{CJK}]", md_text))
    return "zh" if cjk > 0.05 * max(len(md_text), 1) else "en"


def build_html(md_text: str, title: str, lang: str) -> str:
    md_text = space_lists(unwrap_cjk(md_text))
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"],
    )
    html_lang = "zh-CN" if lang == "zh" else "en"
    return (
        f'<!doctype html><html lang="{html_lang}"><head><meta charset="utf-8">'
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    )


def derive_title(md_text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if not m:
        return fallback
    # Strip trailing markdown emphasis and the em-dash subtitle for the footer.
    return re.sub(r"\s*[—–-]\s*.*$", "", m.group(1).strip()).strip() or fallback


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown_file")
    ap.add_argument("--out", help="output PDF (default: alongside the .md)")
    ap.add_argument("--title", help="footer title (default: first H1)")
    ap.add_argument("--lang", choices=sorted(PAGING), help="footer language (default: auto-detect)")
    ap.add_argument("--chromium", default=os.environ.get("CHROMIUM_PATH"),
                    help="Chromium executable (default: auto-detect under PLAYWRIGHT_BROWSERS_PATH)")
    args = ap.parse_args()

    src = Path(args.markdown_file)
    if not src.exists():
        print(f"No such file: {src}", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else src.with_suffix(".pdf")

    md_text = src.read_text(encoding="utf-8")
    title = args.title or derive_title(md_text, src.stem)
    lang = args.lang or detect_lang(md_text)
    html = build_html(md_text, title, lang)

    exe = args.chromium
    if not exe:
        root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
        found = sorted(root.glob("chromium-*/chrome-linux/chrome"))
        exe = str(found[-1]) if found else None

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.emulate_media(media="print")
        page.pdf(
            path=str(out),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(FOOTER.replace("__TITLE__", title)
                                   .replace("__PAGING__", PAGING[lang])),
            margin={"top": "18mm", "bottom": "16mm", "left": "16mm", "right": "16mm"},
        )
        browser.close()

    print(f"{out}  ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
