# Research

Equity research memos. One directory per company: `research/<code>-<pinyin-name>/`.

| Company | Code | Memo |
|---|---|---|
| 洁美科技 Jiemei | 002859.SZ | [EN](research/002859-jiemei/key-questions.md) |
| 金海通 Jinhaitong | 603061.SH | [EN](research/603061-jinhaitong/key-questions.md) · [中文](research/603061-jinhaitong/key-questions.zh.md) |

Management interview question list: [金海通 · 10个关键问题](research/603061-jinhaitong/management-questions.zh.md)

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
