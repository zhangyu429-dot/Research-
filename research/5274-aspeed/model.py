#!/usr/bin/env python3
"""信驊科技 ASPEED (5274.TWO) 2026-2028 盈利预测模型 / earnings model.

Built bottom-up from chip units x ASP, because that is how this business
actually scales: ASPEED sells a countable number of controllers into a
countable number of server boards, and management's own growth story is
"more ASPEED chips per board", not "more servers".

    python3 research/5274-aspeed/model.py            # all scenarios
    python3 research/5274-aspeed/model.py --md       # markdown tables
    python3 research/5274-aspeed/model.py --tam      # TAM feasibility check

Every assumption is in the Scenario objects below and is meant to be argued
with. The point estimates are not the output; the spread between scenarios,
and the exit multiple's dominance over all of it, are the output.

Units: NT$億 (100m) for money, millions for chips, unless stated.

Primary filings (MOPS/公開資訊觀測站, the company IR site) were unreachable
from this environment — every input is secondary and must be re-verified
against the 財報 before use. See key-questions.zh.md, section 資料来源.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Actuals — the calibration anchors (NT$億 throughout)
# ---------------------------------------------------------------------------

FY25 = {
    "revenue": 90.85,        # 9,084,875 千元
    "gross_margin": 0.6801,  # 毛利 6,178,705 千元
    "net": 39.28,            # 3,927,807 千元
    "eps_asrep": 103.92,     # on the then 37.80m share count
    "bmc_units": 23.668,     # 百万颗
    "bmc_revenue": 88.31,    # 亿元 — BMC line only; residual is Smart AV
}

H1_26 = {
    "revenue": 70.18,        # Q1 31.47 + Q2 38.71
    "net": 32.55,            # Q1 14.14 + Q2 18.41
    "eps": 78.28,            # restated on 41.583m shares
}

SHARES = 41.583              # 百万股, post the 10% capital-reserve bonus issue
PRICE = 17885.0              # NT$/share, 2026-09-11 close
MKT_CAP = PRICE * SHARES / 100.0   # NT$亿

TAX_RATE = 0.17              # implied by FY2025 (see calibration note below)
FX = {2026: 30.5, 2027: 30.5, 2028: 30.5}   # NT$/US$, held flat on purpose

YEARS = [2026, 2027, 2028]

# ASPEED's own 2030 BMC TAM, raised from 46.5m to 65.77m units (+41%).
# Used as a feasibility ceiling, not as a forecast.
TAM_2030 = 65.77


@dataclass
class Scenario:
    name: str
    label: str
    units: dict          # BMC-class chips shipped, millions
    asp: dict            # NT$ per BMC unit
    attach: dict         # companion silicon (BIC/SMC/security/AVoIP) as % of BMC revenue
    gross_margin: dict
    opex_ratio: dict     # opex as % of revenue
    exit_pe: float

    def project(self) -> dict:
        out = {}
        for y in YEARS:
            bmc_rev = self.units[y] * self.asp[y] / 100.0        # 百万颗 x NT$ -> 亿元
            other_rev = bmc_rev * self.attach[y]
            rev = bmc_rev + other_rev
            gp = rev * self.gross_margin[y]
            op = gp - rev * self.opex_ratio[y]
            net = op * (1 - TAX_RATE)
            out[y] = {
                "bmc_rev": bmc_rev,
                "other_rev": other_rev,
                "revenue": rev,
                "gross_margin": self.gross_margin[y],
                "op": op,
                "op_margin": op / rev,
                "net": net,
                "net_margin": net / rev,
                "eps": net * 100.0 / SHARES,
                "asp_usd": self.asp[y] / FX[y],
                "tam_share_2030": self.units[y] / TAM_2030,
            }
        out["value"] = out[2028]["eps"] * self.exit_pe
        out["upside"] = out["value"] / PRICE - 1.0
        return out


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
# Unit anchors from sell-side and company TAM work:
#   2025A 23.7m -> 2026E 31.0-32.7m -> 2027E 44.6m (one house) / >50m (another)
# ASP anchors: US$13.7 (2025) -> US$16.1 (2026) -> US$21.7 (2027) per one house;
#   management says ASP "has a chance to challenge US$20".
#   NOTE: FY2025 reported BMC revenue / units = NT$373/unit = US$12.0 at 31.2,
#   ~13% below the quoted US$13.7. The public unit and ASP series do not
#   reconcile to reported revenue. Calibration below follows reported revenue.
# Attach rate: the AST1040 bridge IC, AST1080 security chip and AST1840 power
#   sequencer are the "more chips per board" story. 2025 residual was ~2.9%
#   of BMC revenue and included Smart AV, which was carved out to Cupola360
#   on 2025-12-31.

BEAR = Scenario(
    name="bear",
    label="悲观：2027年AI资本开支进入消化期，第四季涨价回吐",
    units={2026: 31.5, 2027: 37.0, 2028: 34.0},
    asp={2026: 495, 2027: 520, 2028: 470},
    attach={2026: 0.085, 2027: 0.095, 2028: 0.095},
    gross_margin={2026: 0.688, 2027: 0.660, 2028: 0.625},
    opex_ratio={2026: 0.148, 2027: 0.165, 2028: 0.190},
    exit_pe=20.0,
)

BASE = Scenario(
    name="base",
    label="中性：2027年在手订单如实兑现，2028年增速放缓但不衰退",
    units={2026: 32.7, 2027: 44.6, 2028: 52.0},
    asp={2026: 505, 2027: 640, 2028: 680},
    attach={2026: 0.095, 2027: 0.120, 2028: 0.130},
    gross_margin={2026: 0.695, 2027: 0.700, 2028: 0.690},
    opex_ratio={2026: 0.142, 2027: 0.135, 2028: 0.140},
    exit_pe=35.0,
)

BULL = Scenario(
    name="bull",
    label="乐观：量价齐扬延续至2028年，机柜化与周边芯片持续加码",
    units={2026: 33.5, 2027: 50.0, 2028: 58.0},
    asp={2026: 520, 2027: 680, 2028: 730},
    attach={2026: 0.105, 2027: 0.140, 2028: 0.150},
    gross_margin={2026: 0.700, 2027: 0.715, 2028: 0.715},
    opex_ratio={2026: 0.138, 2027: 0.125, 2028: 0.125},
    exit_pe=45.0,
)

SCENARIOS = [BEAR, BASE, BULL]

# Sell-side consensus, for scoring the model against the market
CONSENSUS = {
    2026: (202.31, 175.76, 217.02),   # FactSet median / low / high, 16 analysts
    2027: (368.0, 328.0, 408.0),      # range reported across broker notes
}


def reverse_valuation(multiples=(25, 30, 35, 40, 45, 50, 55)) -> list:
    """Solve for the profit the current market cap requires at each multiple.

    The house rule: never forecast into a valuation. Take the market cap,
    apply a terminal multiple, solve for the net profit, then ask whether
    the bridge to that profit exists.
    """
    rows = []
    for m in multiples:
        net = MKT_CAP / m                       # NT$亿
        eps = net * 100.0 / SHARES
        rev = net / 0.475                       # at the 2026 H1 net margin
        units = rev * 100.0 / 750.0             # at a US$24.6 ASP (NT$750)
        rows.append({
            "multiple": m,
            "net": net,
            "eps": eps,
            "x_2025": net / FY25["net"],
            "revenue": rev,
            "units": units,
            "tam_share": units / TAM_2030,
        })
    return rows


def fmt_table(rows: list[list[str]], md: bool) -> str:
    if md:
        head = "| " + " | ".join(rows[0]) + " |"
        rule = "|" + "|".join(["---"] * len(rows[0])) + "|"
        body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n".join([head, rule, *body])
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    out = []
    for i, r in enumerate(rows):
        out.append("  ".join(c.ljust(widths[j]) for j, c in enumerate(r)))
        if i == 0:
            out.append("  ".join("-" * w for w in widths))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="markdown tables")
    ap.add_argument("--tam", action="store_true", help="TAM feasibility only")
    args = ap.parse_args()

    print(f"信驊 ASPEED (5274.TWO) — 股价 NT${PRICE:,.0f}, 股本 {SHARES:.3f}百万股, "
          f"市值 NT${MKT_CAP:,.0f}亿")
    print(f"FY2025A: 营收 {FY25['revenue']:.2f}亿, 毛利率 {FY25['gross_margin']:.1%}, "
          f"净利 {FY25['net']:.2f}亿, EPS {FY25['eps_asrep']:.2f} (旧股本)")
    print(f"2026H1A: 营收 {H1_26['revenue']:.2f}亿, 净利 {H1_26['net']:.2f}亿 "
          f"(净利率 {H1_26['net']/H1_26['revenue']:.1%}), EPS {H1_26['eps']:.2f}")
    print()

    print("=== 倒算估值：现价要求多少利润 ===")
    rows = [["退出本益比", "所需净利(亿)", "所需EPS", "对2025年倍数",
             "隐含营收(亿)", "隐含出货(百万颗)", "占公司2030年TAM"]]
    for r in reverse_valuation():
        rows.append([f"{r['multiple']}x", f"{r['net']:,.0f}", f"{r['eps']:,.0f}",
                     f"{r['x_2025']:.1f}x", f"{r['revenue']:,.0f}",
                     f"{r['units']:.0f}", f"{r['tam_share']:.0%}"])
    print(fmt_table(rows, args.md))
    print("\n隐含营收按2026年上半年47.5%净利率倒算；隐含出货按ASP NT$750 (≈US$24.6) 倒算。")
    print(f"信驊自身2030年BMC TAM预估为 {TAM_2030:.2f} 百万颗（由46.5上修41%）。")
    if args.tam:
        return 0

    for sc in SCENARIOS:
        p = sc.project()
        print(f"\n=== {sc.name.upper()} — {sc.label} (退出本益比 {sc.exit_pe:.0f}x) ===")
        rows = [["", "2026E", "2027E", "2028E"]]
        for key, lab, f in [
            ("units", "BMC出货(百万颗)", lambda v: f"{v:.1f}"),
            ("asp_usd", "BMC ASP (US$)", lambda v: f"{v:.1f}"),
            ("bmc_rev", "BMC收入(亿)", lambda v: f"{v:.1f}"),
            ("other_rev", "周边芯片收入(亿)", lambda v: f"{v:.1f}"),
            ("revenue", "营业收入(亿)", lambda v: f"{v:.1f}"),
            ("gross_margin", "毛利率", lambda v: f"{v:.1%}"),
            ("op_margin", "营业利益率", lambda v: f"{v:.1%}"),
            ("net", "税后净利(亿)", lambda v: f"{v:.1f}"),
            ("net_margin", "净利率", lambda v: f"{v:.1%}"),
            ("eps", "EPS (NT$)", lambda v: f"{v:.0f}"),
            ("tam_share_2030", "占2030年TAM", lambda v: f"{v:.0%}"),
        ]:
            row = [lab]
            for y in YEARS:
                v = sc.units[y] if key == "units" else p[y][key]
                row.append(f(v))
            rows.append(row)
        print(fmt_table(rows, args.md))
        print(f"2028年EPS {p[2028]['eps']:.0f} x {sc.exit_pe:.0f}x = "
              f"NT${p['value']:,.0f}，较现价 {p['upside']:+.0%}")

    print("\n=== 对照卖方一致预期 ===")
    rows = [["", "悲观", "中性", "乐观", "一致预期(中位)", "一致预期(区间)"]]
    for y in (2026, 2027):
        med, lo, hi = CONSENSUS[y]
        rows.append([f"{y}E EPS"] + [f"{s.project()[y]['eps']:.0f}" for s in SCENARIOS]
                    + [f"{med:.0f}", f"{lo:.0f}–{hi:.0f}"])
    print(fmt_table(rows, args.md))

    print("\n=== 退出本益比敏感度（中性情形2028年EPS）===")
    base_eps = BASE.project()[2028]["eps"]
    rows = [["退出本益比", "隐含价值", "较现价"]]
    for m in (20, 25, 30, 35, 40, 45, 50):
        v = base_eps * m
        rows.append([f"{m}x", f"NT${v:,.0f}", f"{v/PRICE-1:+.0%}"])
    print(fmt_table(rows, args.md))
    print(f"\n中性情形2028年EPS = {base_eps:.0f}。现价 NT${PRICE:,.0f} 隐含 "
          f"{PRICE/base_eps:.1f}x 2028年中性EPS。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
