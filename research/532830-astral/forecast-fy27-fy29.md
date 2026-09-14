# Astral Ltd (ASTRA IN · NSE: ASTRAL) — FY27–FY29 Earnings Model and Valuation

*Earnings model · 14 September 2026 · an analytical framework, not investment advice*

*Model code: [model.py](model.py) (re-runnable; every assumption lives in `SCENARIOS`) ·
Companion: [key-questions.md](key-questions.md)*

---

## 0. The three conclusions that matter

1. **Built bottom-up from volume × realisation × margin, the Base case lands at FY28E net
   profit of ₹792cr — 5% to 17% below the sell-side's ₹836–950cr.** Not dramatically below:
   this is not a model that says the street is wrong. It says the street is at the optimistic
   end of a reasonable range, which is a different and more useful statement.
2. **At today's ₹40,107cr, the Base case requires a 50.6x exit multiple in FY28. The Bull case
   — full captive-CPVC delivery, double-digit volume, Astral Chemie hitting its own FY28
   targets — requires 39.4x.** So the spot price is, roughly, *the bull case capitalised at a
   normal-for-the-sector multiple*, or *the base case capitalised at more than the stock
   currently trades on*.
3. **The dominant risk in this security is the multiple, not the earnings.** Holding FY28E PAT
   at ₹787cr and moving the exit multiple from 30x to 50x moves fair value by **+67%**
   (₹879 → ₹1,466). Holding the multiple at 40x and moving FY28E PAT from ₹700cr to ₹900cr
   moves it by **+29%**. The historical record says the same thing: the 39% fall from the
   July 2024 peak was **entirely** de-rating (121x → 75x) on flat earnings.

---

## 1. Model structure and calibration

Plumbing is modelled as **volume (MT) × realisation (₹/kg)** rather than as a revenue growth
rate, because that is the only way to separate the two things Indian pipe results confuse:
tonnes sold, and what PVC resin happened to cost. Chemicals (paints + adhesives) is modelled
as a growth rate, because no volume series is public. The group is modelled **pre-demerger**
so the years stay comparable; the demerger changes who owns which profit pool, not how much
there is.

| Calibration item | Value | Source |
|---|---|---|
| FY26 revenue | ₹6,568.6cr | Reported |
| FY26 Paints & Adhesives | ₹1,890cr | Reported |
| FY26 Plumbing | ₹4,678.6cr | Derived (total − chemicals) |
| FY26 plumbing volume | ~270,000 MT | **Derived** from Q4 FY26's 84,041 MT and FY26's +16% |
| Implied realisation | **₹173.3/kg** | Derived; Q1 FY27 actual ₹187.1/kg, Q4 FY26 ₹182.5/kg |
| FY26 EBITDA | ₹1,062cr (16.2%) | Reported (a ₹1,109cr / 16.9% print also circulates) |
| Segment margins | Plumbing 19.5%, chemicals 7.9% | Derived, calibrated to reproduce group EBITDA |
| FY26 depreciation | **₹351cr** | Derived plug from reported PAT and a 26% tax rate |
| Tax rate | 26% | Implied by Q1 FY27 (PBT ₹162.8cr → PAT ₹120.2cr) |
| Shares | 26.85cr | Derived (market cap ÷ price) |

**One modelling choice does real work and should be stated plainly.** Depreciation is grown by
**10% of the prior year's capex**, not held flat. The memo's central finding is that group
EBITDA margin has held near 16% while **net** margin fell from 12.9% (FY21) to 8.1% (FY26) —
and the gap is depreciation on ₹1,400cr of four-year capex plus new-venture losses. A model
that freezes D&A reproduces the bull case by construction. With FY27 capex guided at ₹300–350cr
but ₹137cr already spent in Q1, the model assumes **₹450–650cr a year**.

---

## 2. The three scenarios

| Assumption (FY27/28/29) | Bear | Base | Bull |
|---|---|---|---|
| **Plumbing volume growth** | 4% / 6% / 6% | 10% / 12% / 12% | 14% / 15% / 15% |
| **Realisation growth** | −3% / 0% / +1% | +2% / +1% / +1% | +4% / +2% / +2% |
| **Plumbing EBITDA margin** | 18.0% → 17.0% | 19.5% → 20.5% | 20.5% → 22.0% |
| **Chemicals growth** | 12% p.a. | 18% / 20% / 20% | 25% p.a. |
| **Chemicals EBITDA margin** | 8% → 10% | 9% → 12.5% | 11% → 15% |
| Capex (₹cr) | 450/500/500 | 500/550/600 | 550/600/650 |
| **Exit P/E** | 30x | 38x | 48x |

**What each scenario is actually asserting:**

- **Bear.** Q1 FY27's flat volume (56,146 MT) was the true run rate, not an aberration; the
  18.9% plumbing margin was resin timing and reverts toward the **16–18% the company itself
  guides for FY27**; paints never scales; and a pure-play pipes company re-rates to 30x.
- **Base.** Guidance is roughly met from FY28; the captive CPVC plant delivers **half** of the
  claimed +200bps; chemicals reaches low-double-digit margins by FY29; the multiple settles
  between Finolex (~30x) and Supreme Industries (~45x).
- **Bull.** July 2026's +40% is the real signal; the full +200bps arrives; Astral Chemie hits
  its stated ₹2,300–2,400cr at 14–15% by FY28; and the market keeps paying a Supreme-plus
  multiple *after* a quarter of the revenue has been handed to a separate listing.

---

## 3. Results

| | FY26A | FY27E Bear | FY27E Base | FY27E Bull | FY28E Bear | FY28E Base | FY28E Bull | FY29E Bear | FY29E Base | FY29E Bull |
|---|---|---|---|---|---|---|---|---|---|---|
| Volume (MT '000) | 270 | 281 | 297 | 308 | 298 | 333 | 354 | 316 | 373 | 407 |
| Realisation (₹/kg) | 173.3 | 168.1 | 176.7 | 180.2 | 168.1 | 178.5 | 183.8 | 169.8 | 180.3 | 187.5 |
| Revenue (₹cr) | 6,569 | 6,837 | 7,480 | 7,909 | 7,374 | 8,614 | 9,460 | 8,011 | 9,929 | 11,324 |
| EBITDA margin | 16.2% | 14.9% | 16.4% | 17.7% | 14.4% | 17.2% | 18.8% | 14.7% | 17.9% | 19.7% |
| Depreciation (₹cr) | 351 | 398 | 398 | 398 | 443 | 448 | 453 | 493 | 503 | 513 |
| **Net profit (₹cr)** | **535** | **474** | **630** | **761** | **478** | **792** | **1,017** | **527** | **981** | **1,317** |
| Net margin | 8.1% | 6.9% | 8.4% | 9.6% | 6.5% | 9.2% | 10.8% | 6.6% | 9.9% | 11.6% |
| **EPS (₹)** | **19.91** | 17.65 | 23.45 | 28.35 | 17.79 | **29.51** | 37.88 | 19.64 | 36.52 | 49.04 |
| FY26→29 PAT CAGR | | | | | | | | **−0.5%** | **+22.4%** | **+35.0%** |

### The structural point hiding in the Bear case

**Look at what happens to the Bear column: revenue grows from ₹6,569cr to ₹8,011cr (+22%),
and net profit goes from ₹534.7cr to ₹527cr (−1.4%).**

That is not a quirk of the model. It is the arithmetic of the memo's central finding, played
forward. Two mechanisms do it, and both are already visible in the reported FY22–FY26 record:

1. **Chemicals grows faster than plumbing and earns roughly a third of its margin** (7.9% vs
   19.5%). Every point of revenue mix shifting to chemicals costs the group about **0.12pp of
   blended EBITDA margin.** Growth in the fast-growing half *dilutes* group profitability.
2. **Depreciation compounds on capex that has not yet produced its returns.** D&A rises from
   ₹351cr to ₹493cr over three years in the Bear case — ₹142cr, or 27% of FY26's entire net
   profit — before any operating deterioration.

This is exactly what happened between FY22 and FY26: **revenue +49.5%, net profit +9.1%.** The
Bear case is not a stress test of something that has never occurred. **It is the last four
years, extended.**

---

## 4. Reverse valuation — what ₹40,107cr requires

| Exit P/E | Net profit required | × FY26 (₹535cr) | vs sell-side FY28E ₹836–950cr |
|---|---|---|---|
| 25x | ₹1,604cr | 3.00x | +69% above the top |
| 30x | ₹1,337cr | 2.50x | +41% above the top |
| 35x | ₹1,146cr | 2.14x | +21% above the top |
| 40x | ₹1,003cr | 1.88x | +6% above the top |
| **45x** | **₹891cr** | **1.67x** | **inside the range** |
| 50x | ₹802cr | 1.50x | −4% vs the bottom |
| 55x | ₹729cr | 1.36x | −13% vs the bottom |

Read against this model's own output:

| Scenario | FY28E net profit | Exit P/E needed to justify ₹1,493.50 today |
|---|---|---|
| Bear | ₹478cr | **83.9x** |
| **Base** | **₹792cr** | **50.6x** |
| Bull | ₹1,017cr | **39.4x** |

**Only the Bull case is defensible at a sector-normal multiple.** The Base case requires the
stock to trade in FY28 at a *higher* multiple than it does today, after the demerger has
removed the growth-story half of the business from the listed entity. That is the whole
valuation problem stated in one line.

### Implied value per share

| FY28E PAT (₹cr) | 30x | 35x | 40x | 45x | 50x |
|---|---|---|---|---|---|
| 500 | 559 | 652 | 745 | 838 | 931 |
| 600 | 670 | 782 | 894 | 1,006 | 1,117 |
| 700 | 782 | 912 | 1,043 | 1,173 | 1,304 |
| **792 (Base)** | **885** | **1,032** | **1,180** | **1,327** | **1,475** |
| 900 | 1,006 | 1,173 | 1,341 | 1,508 | 1,676 |
| 1,017 (Bull) | 1,137 | 1,326 | 1,516 | 1,705 | 1,895 |

*Spot: ₹1,493.50. Only the shaded-in-words top-right corner — Bull earnings **and** a 45–50x
exit — clears it.*

---

## 5. What the model does not capture, and where it is most likely wrong

**Against the model (i.e. reasons the Bull case may be too conservative):**

- **The captive CPVC resin plant is genuinely unusual.** No pipe company anywhere has backward
  integrated into CPVC resin. If the claimed ~200bps and ₹120–130cr of working capital release
  both land, and if it also removes a supply dependency, the plumbing margin assumption in
  the Bull case may be too low rather than too high.
- **Anti-dumping duties are not modelled at all.** If duties of $22–284/tonne land on PVC
  suspension resin, FY27 and FY28 carry inventory gains that none of these scenarios contain.
- **The demerger may release value the consolidated model cannot show.** If Astral Chemie is
  re-rated as a standalone specialty chemicals and paints platform on revenue multiples rather
  than earnings, the sum of the parts can exceed anything a consolidated P/E produces.

**For the model (i.e. reasons even the Base case may be optimistic):**

- **The Base case still assumes the plumbing margin holds at 19.5–20.5%, above the company's
  own 16–18% FY27 guidance.** That is a deliberate choice to avoid stacking conservatism, but
  it is a choice.
- **Astral Chemie's funding is not modelled.** A newly listed company targeting ₹4,500–5,000cr
  of revenue off ~₹150cr of EBITDA will very likely raise equity. That dilution sits inside the
  1:1 entitlement you receive.
- **Minority interests are ignored.** Nexelon (20% outside) and DSS (40% outside) are small
  today and will not stay small if either works.
- **Realisation is modelled as smooth.** It is not. PVC moved ~64% year-on-year into March 2026
  and then fell. A single bad resin quarter can move group EBITDA by more than a year of
  volume growth.

**The honest summary of this exercise:** the operating assumptions barely matter compared with
the exit multiple, and nobody — including this model — has any edge in forecasting the exit
multiple of an Indian building-materials compounder that has already de-rated from 121x to 75x.
**Which is the argument for answering Q1, Q2 and Q3 of the memo with disclosure rather than
answering them with a spreadsheet.**
