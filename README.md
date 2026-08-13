# Research

Equity research memos. One directory per company: `research/<code>-<pinyin-name>/`.

| Company | Code | Memo |
|---|---|---|
| 洁美科技 Jiemei | 002859.SZ | [EN](research/002859-jiemei/key-questions.md) · [中文](research/002859-jiemei/key-questions.zh.md) · [PDF](research/002859-jiemei/key-questions.zh.pdf) |
| 金海通 Jinhaitong | 603061.SH | [EN](research/603061-jinhaitong/key-questions.md) · [中文](research/603061-jinhaitong/key-questions.zh.md) · [PDF](research/603061-jinhaitong/key-questions.zh.pdf) |
| Total Bangun Persada | TOTL.JK | [EN](research/TOTL-total-bangun-persada/key-questions.md) · [PDF](research/TOTL-total-bangun-persada/key-questions.pdf) |

Management interview question lists:
[洁美科技 · 10个关键问题](research/002859-jiemei/management-questions.zh.md) ·
[金海通 · 10个关键问题](research/603061-jinhaitong/management-questions.zh.md) ·
[Total Bangun Persada · 10 questions](research/TOTL-total-bangun-persada/management-questions.md)
([PDF](research/TOTL-total-bangun-persada/management-questions.pdf))

## House format

All memos follow `.claude/skills/equity-key-questions/SKILL.md`, which defines the
structure, the method rules (reverse the valuation, find the last cycle peak, check cash
conversion, quantify share supply, grade sources) and the pre-writing research checklist.

Any Claude Code session with this repo checked out picks the skill up automatically —
just ask for an analysis of a company and it will follow the format. To re-run an existing
memo against fresh data, ask for it by name; the file is overwritten in place so the
revision history lives in git.

## Recovering work from old sessions

`tools/recover_session.py` finds and extracts content from local Claude Code
transcripts (`~/.claude/projects/<slug>/<uuid>.jsonl`) when a session can no longer
be opened interactively:

```
python3 tools/recover_session.py search 恒运昌 恒昌运
python3 tools/recover_session.py extract <path-to.jsonl> --out recovered/
```

`search` reports each matching transcript with its session id, working directory,
git branch and opening prompt. `extract` writes `recovered/transcript.md` (the
conversation prose) plus `recovered/files/` (every file the session wrote, whether
via the Write tool or a shell heredoc). Standard library only; use `python` on Windows.

## Rendering memos to PDF

`tools/md_to_pdf.py` renders a memo to a print-ready A4 PDF via headless Chromium:

```
python3 tools/md_to_pdf.py research/603061-jinhaitong/key-questions.zh.md
```

Tuned for Chinese documents: CJK font stack, 1.85 line-height, and it strips the
source line breaks that markdown would otherwise render as visible gaps mid-sentence.
Tables and blockquotes are kept off page boundaries; footer carries page numbers.

Language is auto-detected from the CJK share of the text, which sets the page-number
footer ("第 N 页" vs "Page N of M") and the `html lang` attribute; override with
`--lang zh|en`. Lists written GitHub-style — no blank line between a paragraph and the
list under it — are spaced out before rendering, because python-markdown would
otherwise fold the items back into the paragraph.

Requires `pip install markdown playwright` and an existing Chromium (it reads
`PLAYWRIGHT_BROWSERS_PATH` and does not download one).
