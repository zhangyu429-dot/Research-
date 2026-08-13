#!/usr/bin/env python3
"""洁美科技 (002859.SZ) 2026-2028 盈利预测模型 / earnings model.

Built bottom-up from announced capacity, with explicit ASP and gross margin
assumptions per segment. Calibrated against FY2025 actuals before forecasting.

    python3 research/002859-jiemei/model.py            # all scenarios
    python3 research/002859-jiemei/model.py --md       # markdown tables

Every assumption is in ASSUMPTIONS below and is meant to be argued with.
The point estimates are not the output; the spread between scenarios is.

Sources for the anchors are listed in mlcc-film-deepdive.zh.md and
key-questions.zh.md. Primary filings were unreachable from this environment,
so all inputs are secondary and must be re-verified.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# FY2025 actuals — the calibration anchor (¥100m = 亿元 throughout)
# ---------------------------------------------------------------------------

FY25 = {
    "revenue": 21.00,
    "packaging": 17.39,      # 电子封装材料
    "film": 2.60,            # 电子级薄膜材料
    "other": 1.01,           # 复合集流体等 (residual)
    "gross_margin": 0.3341,
    "net_parent": 2.20,      # 归母净利润
    "net_total": 2.03,       # 含少数股东
    "film_volume": 1.44,     # 亿㎡, implied from ~1200万㎡/月 run rate
    "film_asp": 1.80,        # 元/㎡, = 2.60亿 / 1.44亿㎡
}

TAX_RATE = 0.15              # high-tech enterprise rate
SHARES_BASE = 4.535          # 亿股, implied by the July 2026 pledge filing
SHARES_ACQ = 0.3445          # 亿股 issued for 埃福思 at ¥26.56
PRICE = 31.79                # ¥/share

# ---------------------------------------------------------------------------
# Capacity — announced, in 亿㎡/year of release film
# ---------------------------------------------------------------------------
# Existing:  5 domestic + 2 Korean lines. Design 1,700-1,800万㎡/月,
#            fully ramped 2,400-2,600万㎡/月 → ~2.9-3.1亿㎡/yr.
#            April 2026 actual shipment 2,700万㎡ = at/above nameplate.
# Tianjin 1: 2.4亿㎡, trial production H1 2026.
# Tianjin 2: 2.4亿㎡ + 2万吨 BOPET, construction started 2026.

CAPACITY = {2025: 3.0, 2026: 4.2, 2027: 6.4, 2028: 8.8}


@dataclass
class Scenario:
    name: str
    label: str
    # release film
    film_util: dict          # capacity utilisation by year
    film_asp: dict           # ¥/m²
    film_gm: dict            # gross margin
    # carrier tape / packaging
    pack_growth: dict
    pack_gm: dict
    # other (composite current collector etc.)
    other_growth: dict
    other_gm: dict
    # opex as % of revenue (2025 calibrated at 22.0%)
    opex_ratio: dict
    # 埃福思 consolidation: year -> (revenue, gross margin, net profit)
    acq: dict = field(default_factory=dict)
    # minority interest drag, ¥100m (negative = minorities absorb losses)
    minority: dict = field(default_factory=dict)
    exit_pe: float = 25.0


YEARS = [2026, 2027, 2028]

# 埃福思: 2025A revenue ¥1.30亿 / net ¥0.453亿 (34.7% net margin).
# Earnout commitments 2026-28: ¥0.6301 / 0.7302 / 0.8443亿.
# Revenue implied by holding the 2025 net margin. Assume deal closes and
# consolidates from 2027 (shareholder meeting deferred 11 Aug 2026).
ACQ_FULL = {
    2026: (0.00, 0.55, 0.00),
    2027: (2.10, 0.55, 0.73),
    2028: (2.43, 0.55, 0.84),
}
ACQ_NONE = {y: (0.0, 0.0, 0.0) for y in YEARS}


SCENARIOS = [
    Scenario(
        name="bear", label="悲观",
        # Tianjin ramps slowly; shortage ends mid-2027 as 双星/康辉 land
        film_util={2026: 0.62, 2027: 0.60, 2028: 0.55},
        film_asp={2026: 1.95, 2027: 1.80, 2028: 1.60},
        film_gm={2026: 0.18, 2027: 0.18, 2028: 0.15},
        pack_growth={2026: 0.08, 2027: 0.04, 2028: 0.02},
        pack_gm={2026: 0.355, 2027: 0.345, 2028: 0.335},
        other_growth={2026: 0.20, 2027: 0.15, 2028: 0.10},
        other_gm={2026: 0.02, 2027: 0.05, 2028: 0.08},
        opex_ratio={2026: 0.220, 2027: 0.222, 2028: 0.225},
        acq=ACQ_NONE,                       # deal lapses
        minority={2026: -0.15, 2027: -0.12, 2028: -0.10},
        exit_pe=18.0,
    ),
    Scenario(
        name="base", label="中性",
        # Shortage through H1 2027 as management guides, then normalisation
        film_util={2026: 0.70, 2027: 0.72, 2028: 0.68},
        film_asp={2026: 2.10, 2027: 2.05, 2028: 1.90},
        film_gm={2026: 0.24, 2027: 0.27, 2028: 0.25},
        pack_growth={2026: 0.11, 2027: 0.07, 2028: 0.05},
        pack_gm={2026: 0.360, 2027: 0.355, 2028: 0.350},
        other_growth={2026: 0.30, 2027: 0.25, 2028: 0.20},
        other_gm={2026: 0.05, 2027: 0.10, 2028: 0.14},
        opex_ratio={2026: 0.215, 2027: 0.210, 2028: 0.208},
        acq=ACQ_FULL,
        minority={2026: -0.12, 2027: -0.08, 2028: -0.05},
        exit_pe=25.0,
    ),
    Scenario(
        name="bull", label="乐观",
        # High-end mix and self-made base film lift film margin to core level
        film_util={2026: 0.78, 2027: 0.82, 2028: 0.80},
        film_asp={2026: 2.25, 2027: 2.30, 2028: 2.25},
        film_gm={2026: 0.28, 2027: 0.34, 2028: 0.35},
        pack_growth={2026: 0.14, 2027: 0.10, 2028: 0.08},
        pack_gm={2026: 0.368, 2027: 0.368, 2028: 0.365},
        other_growth={2026: 0.40, 2027: 0.35, 2028: 0.30},
        other_gm={2026: 0.08, 2027: 0.15, 2028: 0.20},
        opex_ratio={2026: 0.208, 2027: 0.198, 2028: 0.192},
        acq=ACQ_FULL,
        minority={2026: -0.08, 2027: -0.02, 2028: 0.02},
        exit_pe=30.0,
    ),
]


def calibrate() -> float:
    """Recover the FY2025 opex ratio implied by the reported numbers."""
    gross = FY25["revenue"] * FY25["gross_margin"]
    pretax = FY25["net_total"] / (1 - TAX_RATE)
    return (gross - pretax) / FY25["revenue"]


def project(sc: Scenario) -> list[dict]:
    rows = []
    pack = FY25["packaging"]
    other = FY25["other"]

    for y in YEARS:
        # release film, built from capacity
        vol = CAPACITY[y] * sc.film_util[y]
        film_rev = vol * sc.film_asp[y]
        film_gp = film_rev * sc.film_gm[y]

        # carrier tape / packaging
        pack = pack * (1 + sc.pack_growth[y])
        pack_gp = pack * sc.pack_gm[y]

        # other (composite current collector etc.)
        other = other * (1 + sc.other_growth[y])
        other_gp = other * sc.other_gm[y]

        # acquisition
        acq_rev, acq_gm, acq_net = sc.acq.get(y, (0.0, 0.0, 0.0))
        acq_gp = acq_rev * acq_gm

        revenue = pack + film_rev + other + acq_rev
        gross = pack_gp + film_gp + other_gp + acq_gp
        gm = gross / revenue

        # 埃福思 modelled at its committed net profit, so strip its gross
        # profit out of the opex base and add the committed net back.
        core_rev = revenue - acq_rev
        core_gross = gross - acq_gp
        core_pretax = core_gross - core_rev * sc.opex_ratio[y]
        core_net = core_pretax * (1 - TAX_RATE)

        net_total = core_net + acq_net
        net_parent = net_total - sc.minority[y]

        shares = SHARES_BASE + (SHARES_ACQ if acq_rev > 0 else 0.0)

        rows.append({
            "year": y,
            "film_vol": vol, "film_rev": film_rev, "film_gm": sc.film_gm[y],
            "pack": pack, "other": other, "acq_rev": acq_rev,
            "revenue": revenue, "gross_margin": gm,
            "net_parent": net_parent, "shares": shares,
            "eps": net_parent / shares,
            "film_share": film_rev / revenue,
        })
    return rows


def fmt(rows: list[dict], sc: Scenario) -> str:
    out = [f"\n{'='*78}", f"  {sc.label} ({sc.name})  ·  退出市盈率 {sc.exit_pe:.0f}x", "="*78]
    hdr = f"{'':22}" + "".join(f"{r['year']:>12}" for r in rows)
    out.append(hdr)
    def line(lbl, key, f="{:>12.2f}"):
        out.append(f"{lbl:22}" + "".join(f.format(r[key]) for r in rows))
    line("离型膜销量 亿㎡", "film_vol")
    line("离型膜收入 亿元", "film_rev")
    line("离型膜毛利率", "film_gm", "{:>11.1%} ")
    line("离型膜收入占比", "film_share", "{:>11.1%} ")
    line("电子封装材料 亿元", "pack")
    line("其他 亿元", "other")
    line("埃福思 亿元", "acq_rev")
    out.append("-"*78)
    line("营业收入 亿元", "revenue")
    line("综合毛利率", "gross_margin", "{:>11.1%} ")
    line("归母净利润 亿元", "net_parent")
    line("总股本 亿股", "shares")
    line("EPS 元", "eps", "{:>12.3f}")
    out.append("-"*78)

    mc = PRICE * rows[-1]["shares"]
    out.append(f"{'当前股价市盈率':22}" + "".join(
        f"{PRICE * r['shares'] / r['net_parent']:>11.1f}x " for r in rows))
    fair = rows[-1]["net_parent"] * sc.exit_pe
    out.append(f"\n  2028年归母净利润 {rows[-1]['net_parent']:.2f}亿元 × {sc.exit_pe:.0f}x "
               f"= {fair:.0f}亿元")
    out.append(f"  对应股价 {fair / rows[-1]['shares']:.2f}元 "
               f"(现价 {PRICE:.2f}元，{fair / mc - 1:+.0%})")
    cagr = (rows[-1]["net_parent"] / FY25["net_parent"]) ** (1/3) - 1
    out.append(f"  2025→2028 归母净利润 CAGR {cagr:+.1%}")
    return "\n".join(out)


def markdown(all_rows: dict) -> str:
    out = ["| | 2025A | " + " | ".join(
        f"{y}E 悲观 | {y}E 中性 | {y}E 乐观" for y in YEARS) + " |"]
    out.append("|" + "---|" * (1 + 1 + 3 * len(YEARS)))

    def row(lbl, key, f, base):
        cells = [base]
        for i in range(len(YEARS)):
            for sc in ("bear", "base", "bull"):
                cells.append(f.format(all_rows[sc][i][key]))
        return f"| {lbl} | " + " | ".join(cells) + " |"

    out.append(row("营业收入（亿元）", "revenue", "{:.1f}", "21.0"))
    out.append(row("综合毛利率", "gross_margin", "{:.1%}", "33.4%"))
    out.append(row("离型膜收入（亿元）", "film_rev", "{:.1f}", "2.6"))
    out.append(row("离型膜毛利率", "film_gm", "{:.0%}", "~15%"))
    out.append(row("归母净利润（亿元）", "net_parent", "{:.2f}", "2.20"))
    out.append(row("EPS（元）", "eps", "{:.2f}", "0.49"))
    return "\n".join(out)


def consensus_check(sc: Scenario) -> str:
    """What gross margin does the 2026 sell-side consensus require?

    Consensus 2026E net profit to parent is ¥4.70-5.01亿. Hold the base-case
    revenue and opex ratio, and solve for the gross margin needed.
    """
    rows = project(sc)
    r26 = rows[0]
    out = ["\n" + "="*78,
           "  一致预期检验：4.70亿元的2026年归母净利润需要什么",
           "="*78,
           f"  中性情形2026年：收入 {r26['revenue']:.2f}亿，毛利率 {r26['gross_margin']:.1%}，"
           f"归母 {r26['net_parent']:.2f}亿"]
    for target in (4.70, 5.01):
        net_total = target + sc.minority[2026]
        pretax = net_total / (1 - TAX_RATE)
        gross_needed = pretax + r26["revenue"] * sc.opex_ratio[2026]
        gm_needed = gross_needed / r26["revenue"]
        out.append(f"  归母 {target:.2f}亿 → 按中性收入需毛利率 **{gm_needed:.1%}**")
    out.append(f"\n  对照：公司毛利率历史高点为2020年的 40.7%，2025年 33.4%，2026Q1 32.6%。")
    out.append("  即：一致预期隐含的毛利率，高于这家公司在离型膜业务出现之前的历史最好水平。")

    # or hold margin and solve for revenue
    gm = r26["gross_margin"]
    for target in (4.70,):
        net_total = target + sc.minority[2026]
        pretax = net_total / (1 - TAX_RATE)
        rev_needed = pretax / (gm - sc.opex_ratio[2026])
        out.append(f"\n  反过来，若毛利率维持中性的 {gm:.1%}，则需收入 {rev_needed:.1f}亿元 "
                   f"= 2025年的 {rev_needed / FY25['revenue']:.1f}倍（同比 "
                   f"{rev_needed / FY25['revenue'] - 1:+.0%}）")
    return "\n".join(out)


def tam_check(all_rows: dict) -> str:
    """Does the bull case volume fit inside the addressable market?"""
    out = ["\n" + "="*78, "  TAM 约束检验", "="*78,
           "  深度研究结论：全球MLCC专用离型膜真实需求约 10-15亿㎡（自下而上），",
           "  公开口径155.8亿㎡过不了物料平衡检验。"]
    for sc in ("base", "bull"):
        v = all_rows[sc][-1]["film_vol"]
        out.append(f"  {sc:5} 2028年销量 {v:.2f}亿㎡ → 占10亿㎡口径的 {v/10:.0%}，"
                   f"占15亿㎡口径的 {v/15:.0%}")
    out.append("\n  注：公司'电子级薄膜材料'分部同时包含胶粘、OCA、偏光片用离型膜，")
    out.append("  后者面积市场远大于MLCC，因此上述占比不构成硬约束——但乐观情形若全部")
    out.append("  计入MLCC口径则不成立。这也再次说明分产品拆分为何是必须的。")
    return "\n".join(out)


def film_gm_sensitivity(grids: dict) -> str:
    """Isolate the release film gross margin, holding volume and ASP fixed.

    The film margin is the model's most sensitive input and the one number
    the interim report can settle, so it gets its own sweep.
    """
    import copy
    out = ["\n" + "="*78, "  离型膜毛利率敏感性（量价假设不变）", "="*78,
           f"{'情形':38}{'2026E':>9}{'2027E':>9}{'2028E':>9}{'退出25x':>11}"]
    for src_name in ("base", "bull"):
        src = next(s for s in SCENARIOS if s.name == src_name)
        tag = {"base": "中性量价", "bull": "乐观量价"}[src_name]
        for gname, gm in grids.items():
            sc = copy.deepcopy(src)
            sc.film_gm = gm if gm else src.film_gm
            rows = project(sc)
            last = rows[-1]
            px = last["net_parent"] * 25.0 / last["shares"]
            out.append(f"{tag + ' + ' + gname:38}"
                       + "".join(f"{r['net_parent']:>9.2f}" for r in rows)
                       + f"{px/PRICE - 1:>+10.0%} ")
    return "\n".join(out)


GM_GRIDS = {
    "原假设": None,
    "35%/37.5%/40%": {2026: 0.35, 2027: 0.375, 2028: 0.40},
    "全程40%": {2026: 0.40, 2027: 0.40, 2028: 0.40},
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="markdown output")
    ap.add_argument("--sens", action="store_true",
                    help="release film gross margin sensitivity only")
    args = ap.parse_args()

    if args.sens:
        print(film_gm_sensitivity(GM_GRIDS))
        return 0

    print(f"FY2025 校准：隐含期间费用率 = {calibrate():.1%} of revenue")
    print(f"FY2025 离型膜隐含均价 = {FY25['film_asp']:.2f} 元/㎡ "
          f"(收入 {FY25['film']:.2f}亿 ÷ 销量 {FY25['film_volume']:.2f}亿㎡)")
    print(f"设计产能（亿㎡/年）: " + ", ".join(f"{y}={c}" for y, c in CAPACITY.items()))

    all_rows = {}
    for sc in SCENARIOS:
        rows = project(sc)
        all_rows[sc.name] = rows
        print(fmt(rows, sc))

    if args.md:
        print("\n\n" + markdown(all_rows))

    print(film_gm_sensitivity(GM_GRIDS))
    print(consensus_check(next(s for s in SCENARIOS if s.name == "base")))
    print(tam_check(all_rows))

    print(f"\n{'='*78}")
    print("  反向估值：当前约144亿元市值需要多少利润")
    print("="*78)
    for pe in (20, 25, 30):
        need = PRICE * (SHARES_BASE + SHARES_ACQ) / pe
        print(f"  {pe}x → 需归母净利润 {need:.2f}亿元 "
              f"= 2025年的 {need / FY25['net_parent']:.1f}倍")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
