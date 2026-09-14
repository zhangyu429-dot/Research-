#!/usr/bin/env python3
"""Astral Ltd (ASTRA IN / NSE: ASTRAL / BSE: 532830) — bottom-up FY27-FY29 earnings model.

Companion to key-questions.md. Re-runnable; every assumption lives in SCENARIOS.

    python3 research/532830-astral/model.py

Method
------
Plumbing is modelled as volume (MT) x realisation (INR/kg) because that is the only
way to separate the two things Indian pipe results confuse: tonnes sold, and what PVC
resin happened to cost. Chemicals (paints + adhesives) is modelled as a growth rate
because no volume series is public.

D&A is grown off a capex-linked increment rather than held flat: the memo's central
finding is that EBITDA margin held around 16% while NET margin fell from 12.9% to 8.1%,
and the gap is depreciation on INR 1,400cr of four-year capex plus new-venture losses.
A model that freezes D&A would reproduce the bull case by construction.

All figures in INR crore unless stated. FY = year ending 31 March.
Everything marked "derived" in key-questions.md is derived here too - see BASE.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------------------
# FY26 base year. Reported figures are marked (R); the rest are derived and are the
# reason this model is a framework rather than a forecast. See key-questions.md Q13.
# --------------------------------------------------------------------------------------

BASE = {
    "revenue_total": 6568.6,        # (R) FY26 consolidated revenue from operations
    "revenue_chemicals": 1890.0,    # (R) FY26 Paints & Adhesives segment
    "revenue_plumbing": 4678.6,     # derived: total - chemicals
    "volume_plumbing_mt": 270_000,  # derived: ~Q4 FY26 84,041 MT annualised for seasonality
    "ebitda_total": 1062.0,         # (R) FY26 EBITDA (the 1,109 / 16.9% print is ex-/incl. other income)
    "margin_plumbing": 0.195,       # derived, calibrated to reproduce ebitda_total
    "margin_chemicals": 0.079,      # derived, ditto
    "pat": 534.7,                   # (R) FY26 net profit
    "eps": 19.91,                   # derived: pat / shares
    "shares_cr": 26.85,             # derived: market cap / price
    "other_income": 47.0,           # derived plug
    "net_interest": 35.0,           # derived plug (company is net cash)
    "tax_rate": 0.26,               # (R) implied by Q1 FY27 PBT 162.8 -> PAT 120.2
}

PRICE = 1493.50          # INR/share, 7 September 2026
MARKET_CAP = 40106.78    # INR crore, same date
YEARS = ("FY27E", "FY28E", "FY29E")


@dataclass
class Scenario:
    name: str
    # plumbing
    vol_growth: tuple[float, float, float]
    realisation_growth: tuple[float, float, float]
    plumbing_margin: tuple[float, float, float]
    # chemicals (paints + adhesives; pre-demerger basis, so the group stays comparable)
    chem_growth: tuple[float, float, float]
    chem_margin: tuple[float, float, float]
    # below the line
    capex: tuple[float, float, float]
    other_income: tuple[float, float, float]
    net_interest: tuple[float, float, float]
    exit_pe: float
    rationale: str = ""


SCENARIOS = [
    Scenario(
        name="Bear",
        # Q1 FY27 volumes were flat (56,146 MT) against 10-15% guidance; this is that
        # run rate persisting, with realisation giving back the FY26 PVC spike.
        vol_growth=(0.04, 0.06, 0.06),
        realisation_growth=(-0.03, 0.00, 0.01),
        # Plumbing margin reverts toward the 16-18% the company itself guides for FY27,
        # i.e. the 18.9% Q1 print was resin timing.
        plumbing_margin=(0.180, 0.170, 0.170),
        chem_growth=(0.12, 0.12, 0.12),
        chem_margin=(0.08, 0.09, 0.10),
        capex=(450.0, 500.0, 500.0),
        other_income=(50.0, 55.0, 60.0),
        net_interest=(30.0, 30.0, 30.0),
        exit_pe=30.0,
        rationale="Volumes stay at the Q1 FY27 run rate; the margin was resin timing; "
                  "paints never scales; the market re-rates a pure pipes company to 30x.",
    ),
    Scenario(
        name="Base",
        # Guidance delivered at the bottom of the 10-15% band from FY28, with FY27
        # carrying the Q1 hole. Realisation roughly flat in real terms.
        vol_growth=(0.10, 0.12, 0.12),
        realisation_growth=(0.02, 0.01, 0.01),
        # Q1 FY27's 18.9% holds, then the captive CPVC plant adds ~50-100bps from FY28
        # rather than the claimed full 200bps.
        plumbing_margin=(0.195, 0.200, 0.205),
        chem_growth=(0.18, 0.20, 0.20),
        chem_margin=(0.09, 0.11, 0.125),
        capex=(500.0, 550.0, 600.0),
        other_income=(55.0, 62.0, 70.0),
        net_interest=(30.0, 25.0, 20.0),
        exit_pe=38.0,
        rationale="Guidance roughly met; CPVC integration delivers half of what is claimed; "
                  "paints reaches low-double-digit margins by FY29; multiple settles between "
                  "Finolex (~30x) and Supreme (~45x).",
    ),
    Scenario(
        name="Bull",
        # July 2026's +40% is the real signal, share gain continues, ADD firms pricing.
        vol_growth=(0.14, 0.15, 0.15),
        realisation_growth=(0.04, 0.02, 0.02),
        # The full claimed +200bps from captive CPVC, on top of operating leverage.
        plumbing_margin=(0.205, 0.215, 0.220),
        chem_growth=(0.25, 0.25, 0.25),
        chem_margin=(0.11, 0.13, 0.15),
        capex=(550.0, 600.0, 650.0),
        other_income=(55.0, 65.0, 75.0),
        net_interest=(25.0, 20.0, 15.0),
        exit_pe=48.0,
        rationale="The franchise case in full: double-digit volume, captive CPVC delivers "
                  "+200bps, Astral Chemie hits its FY28 targets, and the market keeps paying "
                  "a Supreme-plus multiple after the demerger.",
    ),
]


@dataclass
class YearResult:
    year: str
    volume_mt: float
    realisation: float
    rev_plumbing: float
    rev_chem: float
    revenue: float
    ebitda: float
    ebitda_margin: float
    depreciation: float
    pbt: float
    pat: float
    eps: float
    net_margin: float


@dataclass
class Run:
    scenario: Scenario
    years: list[YearResult] = field(default_factory=list)


def project(sc: Scenario) -> Run:
    run = Run(scenario=sc)
    volume = BASE["volume_plumbing_mt"]
    realisation = BASE["revenue_plumbing"] * 1e7 / (BASE["volume_plumbing_mt"] * 1000)
    rev_chem = BASE["revenue_chemicals"]
    depreciation = (
        BASE["ebitda_total"] - BASE["net_interest"] + BASE["other_income"]
        - BASE["pat"] / (1 - BASE["tax_rate"])
    )

    for i, year in enumerate(YEARS):
        volume *= 1 + sc.vol_growth[i]
        realisation *= 1 + sc.realisation_growth[i]
        rev_chem *= 1 + sc.chem_growth[i]
        rev_plumbing = volume * 1000 * realisation / 1e7
        revenue = rev_plumbing + rev_chem

        ebitda = rev_plumbing * sc.plumbing_margin[i] + rev_chem * sc.chem_margin[i]
        # ~10% of the prior year's capex lands as new depreciation (10-year average life
        # across plant, moulds and dies); nothing rolls off over the horizon.
        prior_capex = sc.capex[i - 1] if i else 470.0
        depreciation += 0.10 * prior_capex

        pbt = ebitda - depreciation - sc.net_interest[i] + sc.other_income[i]
        pat = pbt * (1 - BASE["tax_rate"])
        run.years.append(
            YearResult(
                year=year,
                volume_mt=volume,
                realisation=realisation,
                rev_plumbing=rev_plumbing,
                rev_chem=rev_chem,
                revenue=revenue,
                ebitda=ebitda,
                ebitda_margin=ebitda / revenue,
                depreciation=depreciation,
                pbt=pbt,
                pat=pat,
                eps=pat / BASE["shares_cr"],
                net_margin=pat / revenue,
            )
        )
    return run


def reverse_valuation() -> list[tuple[float, float, float]]:
    """What net profit does today's market cap require at each terminal multiple?"""
    return [
        (pe, MARKET_CAP / pe, (MARKET_CAP / pe) / BASE["pat"])
        for pe in (25, 30, 35, 40, 45, 50, 55)
    ]


def main() -> None:
    runs = [project(sc) for sc in SCENARIOS]

    print("=" * 94)
    print("ASTRAL LTD (ASTRA IN) - FY27-FY29 bottom-up model")
    print(f"Price INR {PRICE:,.2f} | Market cap INR {MARKET_CAP:,.0f}cr | "
          f"{BASE['shares_cr']:.2f}cr shares | FY26 PAT INR {BASE['pat']:.1f}cr "
          f"= {MARKET_CAP / BASE['pat']:.1f}x")
    print("=" * 94)

    for run in runs:
        sc = run.scenario
        print(f"\n--- {sc.name} " + "-" * (90 - len(sc.name)))
        print(f"    {sc.rationale}")
        header = f"{'':<22}" + "".join(f"{y:>14}" for y in YEARS)
        print(header)
        rows = [
            ("Plumbing volume (MT)", lambda r: f"{r.volume_mt:,.0f}"),
            ("Realisation (INR/kg)", lambda r: f"{r.realisation:,.1f}"),
            ("Plumbing revenue", lambda r: f"{r.rev_plumbing:,.0f}"),
            ("Chemicals revenue", lambda r: f"{r.rev_chem:,.0f}"),
            ("Total revenue", lambda r: f"{r.revenue:,.0f}"),
            ("EBITDA", lambda r: f"{r.ebitda:,.0f}"),
            ("EBITDA margin", lambda r: f"{r.ebitda_margin:.1%}"),
            ("Depreciation", lambda r: f"{r.depreciation:,.0f}"),
            ("PAT", lambda r: f"{r.pat:,.0f}"),
            ("Net margin", lambda r: f"{r.net_margin:.1%}"),
            ("EPS (INR)", lambda r: f"{r.eps:,.2f}"),
        ]
        for label, fmt in rows:
            print(f"{label:<22}" + "".join(f"{fmt(r):>14}" for r in run.years))

        fy28, fy29 = run.years[1], run.years[2]
        for tag, res in (("FY28E", fy28), ("FY29E", fy29)):
            value = res.pat * sc.exit_pe
            per_share = value / BASE["shares_cr"]
            print(f"  {tag} @ {sc.exit_pe:.0f}x -> INR {value:,.0f}cr "
                  f"= INR {per_share:,.0f}/share ({per_share / PRICE - 1:+.0%} vs spot)")
        cagr = (fy29.pat / BASE["pat"]) ** (1 / 3) - 1
        print(f"  FY26->FY29 PAT CAGR: {cagr:+.1%}")

    print("\n" + "=" * 94)
    print("REVERSE VALUATION - what today's market cap requires")
    print("=" * 94)
    print(f"{'Exit P/E':>10}{'PAT required':>16}{'x FY26 (534.7)':>18}"
          f"{'vs street FY28E 836-950cr':>30}")
    for pe, pat, mult in reverse_valuation():
        if pat > 950:
            verdict = f"{pat / 950 - 1:+.0%} above the top of it"
        elif pat < 836:
            verdict = f"{pat / 836 - 1:+.0%} vs the bottom of it"
        else:
            verdict = "inside the range"
        print(f"{pe:>10.0f}{pat:>16,.0f}{mult:>18.2f}{verdict:>30}")

    print("\nSensitivity: implied INR/share on FY28E PAT x exit multiple")
    pats = [500, 600, 700, 787, 900, 1000]
    print(f"{'FY28E PAT':>12}" + "".join(f"{pe:>11.0f}x" for pe in (30, 35, 40, 45, 50)))
    for pat in pats:
        cells = "".join(f"{pat * pe / BASE['shares_cr']:>12,.0f}" for pe in (30, 35, 40, 45, 50))
        print(f"{pat:>12,}" + cells)
    print(f"\n(spot INR {PRICE:,.0f}; 787 is this model's Base FY28E)")


if __name__ == "__main__":
    main()
