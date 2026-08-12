# Research

Equity research memos. One directory per company: `research/<code>-<pinyin-name>/`.

| Company | Code | Memo |
|---|---|---|
| 洁美科技 Jiemei | 002859.SZ | [key-questions.md](research/002859-jiemei/key-questions.md) |
| 金海通 Jinhaitong | 603061.SH | [key-questions.md](research/603061-jinhaitong/key-questions.md) |

## House format

All memos follow `.claude/skills/equity-key-questions/SKILL.md`, which defines the
structure, the method rules (reverse the valuation, find the last cycle peak, check cash
conversion, quantify share supply, grade sources) and the pre-writing research checklist.

Any Claude Code session with this repo checked out picks the skill up automatically —
just ask for an analysis of a company and it will follow the format. To re-run an existing
memo against fresh data, ask for it by name; the file is overwritten in place so the
revision history lives in git.
