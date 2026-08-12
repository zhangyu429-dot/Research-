---
name: equity-key-questions
description: Research a listed company (usually a China A-share) and produce a "key questions" investment memo in this repo's house format. Use whenever the user asks to analyze a stock as an investment, asks what the key questions are on a name, asks to re-run or update an existing memo, or names a ticker with analytical intent. Produces research/<code>-<name>/key-questions.md.
---

# Equity key-questions memo

Produce a memo that frames **what would have to be true**, not a recommendation. The output
is a question list an investor can act on, with each question paired to the specific
disclosure that answers it.

## Output

Write to `research/<code>-<pinyin-name>/key-questions.md` — e.g. `research/002859-jiemei/`,
`research/603061-jinhaitong/`. One memo per company; re-runs overwrite in place so the
git history carries the revisions.

Commit and push to the session's designated branch. Do not open a PR unless asked.

**Language.** Default to English at `key-questions.md`. When the user asks for Chinese
deliverables, write `key-questions.zh.md` alongside it. Write native Chinese research prose,
not a translation — use the conventional register and terms (营业收入, 归母净利润, 毛利率,
经营活动现金流净额, 应收账款, 发出商品, 合同负债, 总资产周转率, 客户集中度, 限售股解禁,
股份支付, 产能利用率, 国产化率), 亿元/万元 rather than millions, and 中文 section headings.
Keep the structure, tables and source list identical across languages so the two stay
diffable; when one is updated, update the other or say plainly which is now stale.

## Structure (follow exactly)

```
# 中文名 (Pinyin, CODE) — The Questions That Decide the Investment

*Research memo · DD Month YYYY · analysis, not investment advice*

## 0. What you are actually buying
## 1. The five questions that decide the outcome
## 2. Second-order questions that still move the answer
## 3. What to watch next — falsifiable checkpoints
## 4. Provisional read
### Sources
```

**Section 0** — one paragraph stating what the business actually *is* structurally (cash cow
funding an option? single product in a cyclical? etc.), then:
- a **segment table**: segment | latest FY revenue | YoY | what it is
- a **trailing financials table** spanning enough years to include the **last cycle peak** —
  never just the last two years. Include revenue, net profit, net margin, gross margin,
  operating cash flow.
- a **Market:** line: share price, market cap, share count (note any bonus issue / conversion),
  P/E on trailing and forward, P/B, and the sell-side forward estimates.
- a **blockquote** with the single fact that frames everything. Find the fact that most
  changes how a reader sees the headline numbers — usually a multi-year comparison that
  contradicts the current narrative.

**Section 1** — exactly five questions, ordered by how much they move the answer. Each gets a
bolded `**Ask:**` or `**Sub-questions:**` block naming the *specific disclosure* that settles
it. One of the five is always the reverse-valuation question (see below).

**Section 2** — six or so `**Qn — Topic.**` paragraphs: customers/concentration, cycle
position, balance sheet and funding, share supply and insider selling, governance and
alignment, source quality.

**Section 3** — numbered, falsifiable, time-ordered. Lead with the nearest reporting event.

**Section 4** — provisional read. Separate **the business** from **the stock**; they often
have different answers. State what would flip the conclusion. End with a concrete
next-step instruction.

## Method rules

1. **Reverse the valuation, never forecast into it.** Take the market cap, apply a defensible
   terminal multiple, and solve for the net profit required. Then state that number as a
   multiple of current profit and ask whether the bridge exists. This is more honest than a
   DCF and much harder to fool yourself with.
2. **Find the last cycle peak.** Pull financials back far enough to see the previous peak
   and trough. A record year that barely exceeds the prior peak is a very different
   investment from a genuine breakout, and two-year tables hide the difference.
3. **Check cash conversion.** Operating cash flow against net profit, receivables and
   inventory growth against revenue growth, asset turnover trend. Growth financed by
   receivables is the most common way good-looking equipment/materials numbers go wrong.
   Name the specific diagnostic line (e.g. 发出商品 for goods pending acceptance).
4. **Quantify share supply.** Lock-up expiries, insider sale plans and executions, block
   trade discounts, pending raises and their dilution. Not a fundamental argument, but it
   is information about what informed holders think.
5. **Separate cyclical from structural** in every growth claim, and make the company's own
   attribution do work — if management cites three drivers with different durations, say so.
6. **Reconcile conflicting figures rather than picking one.** Different denominators
   (total revenue vs segment revenue vs equipment sales) explain most apparent
   contradictions. Where a genuine conflict survives, report both and flag it.
7. **Grade your sources.** Chinese retail 财富号 / self-media numbers frequently fail
   arithmetic. Sanity-check anything load-bearing. Always include a source-quality note in
   Section 2 listing figures that could not be verified against primary filings.
8. **Say when primary filings were unreachable.** cninfo, SSE, dfcfw and several finance
   PDF hosts are blocked from cloud sessions. When that happens, state it in the Sources
   preamble so the reader knows the figures are secondary.
9. **No recommendation, no price target.** The deliverable is the question list and what
   answers each question.
10. **Sweep the announcements before forming a thesis.** Do a chronological pass over the
    last 18 months of 公告 *first*, as a list, before searching on any thesis keyword.
    Thesis-shaped queries (the product, the margin, the competitor) systematically miss
    corporate actions, because those are filed under language that has nothing to do with
    the thesis. This rule exists because a pending ¥915m share-issued acquisition — 6% of
    market cap, with goodwill worth 3.5x annual profit — was missed twice on 002859 and
    found only by accident, through a stray link about adjusting an issue price.

## Research checklist

Gather before writing; a gap you cannot fill becomes a question in the memo.

**Do this block first — it is the announcement sweep, and it is not optional:**

- Every 公告 title for the last 18 months, read in date order. Flag anything containing
  发行股份 / 购买资产 / 重大资产重组 / 停牌 / 复牌 / 定增 / 可转债 / 收购 / 增资 /
  关联交易 / 业绩预告 / 股权激励 / 员工持股 / 减持 / 质押 / 问询函 / 异动
- **Pending corporate actions specifically**: is there a transaction in flight right now?
  Check for a shareholder meeting that has been scheduled, deferred, or never convened.
  A deal announced months ago and still unclosed will not appear in any results coverage.
- 投资者关系活动记录表 for the last two quarters — the freshest operating data, and the
  only public place unit economics and utilisation are ever discussed
- Related-party transaction filings (关联交易), including the annual 预计 resolution, who
  recused, and whether the counterparty sits on a cost line that matters to the thesis
- Equity incentive / ESOP plans: participants, price, and **the performance targets scored
  against actuals**. A missed target the company set for itself is the best available
  read on how much management over-forecasts.

**Then the financials and the rest:**

- Multi-year revenue / net profit / gross margin / net margin / OCF, back through the last peak
- Latest quarter and any pre-announcement (业绩预告)
- Revenue by segment and by geography, plus the mix shift within the growth product
- Top-5 customer concentration, trend over three periods, named customers if disclosed
- Share count and any bonus issue, conversion or buyback; current price, P/E, P/B
- Sell-side forward estimates, and **how the last cycle's forecasts scored** against actuals
- Balance sheet: cash, receivables and ageing, inventory and composition, contract
  liabilities (合同负债 — the public backlog proxy), net debt, committed capex
- Lock-up expiries, insider transactions, pending equity or convertible issuance
- Dividend and payout history, ESOP and share-based payment, controlling shareholder pledges
- Competitive landscape: named competitors, share estimates, announced capacity, localisation rate
- Company's own disclosures: 投资者关系活动记录表, abnormal-volatility filings, risk warnings

## Sources section

Bulleted markdown links. Each line describes **what the source establishes**, not just its
title — `[FY2025: revenue ¥698m +71.7%, OCF ¥128m (Sina)](url)`, not `[Sina Finance](url)`.
Group loosely: results, filings, corporate actions, ownership, industry.
