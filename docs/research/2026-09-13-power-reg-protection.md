# Power regulation + cell protection research — single-18650 handheld

Date: 2026-09-13. Every fact below is tagged VERIFIED (with source) or UNVERIFIED/CALCULATED.
Load assumption: nRF52840 module + PDM mic + 2x WS2812B, ~150 mA peak, few mA typical,
tens of microamps in deep sleep. System rail 2.9–4.4 V.

## Sources fetched

- TI TPS63030/TPS63031 datasheet SLVS696D (Apr 2020): https://www.ti.com/lit/ds/symlink/tps63031.pdf — FETCHED, full text extracted.
- TI TLV755P datasheet SBVS320D (Sep 2024): https://www.ti.com/lit/ds/symlink/tlv755p.pdf — FETCHED.
- TI BQ2970/71/72/73 datasheet SLUSBU9I (Aug 2024): https://www.ti.com/lit/ds/symlink/bq2970.pdf — FETCHED.
- DW01 datasheet (DigiKey-hosted, 5272_DW01.pdf): https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7158/5272_DW01.pdf — FETCHED.
- LCSC product pages for C15516, C2830320, C183096, C909806, C142146, C1518762 — FETCHED.
- JLCPCB partdetail pages for C15516, C351410, C2830320, C183096, C28060, C404027, C909806, C1518762 — FETCHED (raw HTML, library type + price tiers parsed).
- COULD NOT FETCH: the LCSC-hosted DW01A datasheet PDF (C351410) — it 301-redirects to an HTML page. Used the DigiKey-hosted DW01 datasheet instead; part marking/thresholds match the LCSC DW01A listing.
- COULD NOT FETCH: the FS8205A manufacturer datasheet (LCSC's datasheet URL returns HTML). FS8205A electrical data below comes from the LCSC/JLCPCB listing text only.
- COULD NOT determine JLCPCB *assembly stock* numbers reliably (the page embeds several stock figures for related parts). LCSC stock figures are used instead and are labelled as such.

---

# PART A — TPS63031 (fixed 3.3 V buck-boost, 2.5 x 2.5 mm)

## A1. Pin connections (VERIFIED, SLVS696D §6, Table "Pin Functions")

DSK package, 10-pin VSON 2.5 x 2.5 mm.

| Pin | Name | I/O | Datasheet function | Connect in this design |
|---|---|---|---|---|
| 1 | VOUT | OUT | Buck-boost converter output | 3V3 rail; C_OUT to PGND, placed at pin |
| 2 | L2 | IN | Inductor connection | Inductor, other end to L1 |
| 3 | PGND | — | Power ground | GND plane |
| 4 | L1 | IN | Inductor connection | Inductor |
| 5 | VIN | IN | Supply for power stage | VSYS (cell/protection output); C_IN to PGND at pin |
| 6 | EN | IN | Enable (1 = enabled, 0 = disabled) | Driven high to run; see A5 |
| 7 | PS/SYNC | IN | Enable/disable power-save (1 = disabled, 0 = enabled; clock = sync) | Tie to GND (power-save on) — see A5 |
| 8 | VINA | IN | Supply for control stage | VSYS; 0.1 uF to GND |
| 9 | GND | — | Control/logic ground | GND |
| 10 | FB | IN | Feedback; **must be connected to VOUT on fixed-output versions** | Short to VOUT (pin 1) |
| EP | Thermal pad | — | "The exposed thermal pad is connected to PGND" | GND plane, vias |

No feedback divider on the TPS63031 (fixed 3.3 V). R1/R2 are "not used at TPS63031" (VERIFIED, Table 2).

## A2. Inductor (VERIFIED unless noted)

Datasheet reference design: **L1 = 1.5 uH, 3 mm x 3 mm x 1.5 mm, Coilcraft LPS3015-1R5** (VERIFIED, Table 2).
Recommended series (VERIFIED, Table 3): Coilcraft LPS3015, Coilcraft EPL3010, Murata LQH3NP, Taiyo Yuden NR3015.

Saturation-current rule (VERIFIED, §9.2.2.2): compute I_PEAK in boost mode at the minimum input
voltage, then "choose an inductor with a saturation current 20% higher than the value calculated".

    D = (VOUT - VIN) / VOUT
    IPEAK = IOUT / (eta * (1 - D)) + (VIN * D) / (2 * f * L)     [f typ 2.4 MHz, eta ~0.9]

CALCULATED for this design (worst case boost: VIN = 2.9 V, VOUT = 3.3 V, IOUT = 150 mA, eta = 0.85,
f = 2.4 MHz, L = 1.5 uH): D = 0.121, IPEAK = 0.201 + 0.049 = **~250 mA**; +20% = **~300 mA minimum Isat**.

That is the steady-state number. The device's own average switch current limit is 1000 mA typ,
1300 mA max (VERIFIED, Electrical Characteristics), so pick an inductor that survives the current
limit, not just the load: target **Isat >= 1.5 A**.

Recommended LCSC part (VERIFIED, LCSC C909806 page + JLCPCB listing):
- **Murata DFE252012F-1R5M=P2 — LCSC C909806** — 1.5 uH +/-20%, Isat 3.8 A, Irated(temp) 2.7 A,
  DCR 58 mOhm, 1008 (2.5 x 2.0 mm) metal-alloy shielded. LCSC stock 12,760. JLCPCB: **Extended part**.
  JLCPCB price: $0.1076 (1–49), $0.0839 (50–149), $0.072 (150–499).
- Alternative, currently OUT OF STOCK at LCSC (VERIFIED): Chilisin LVF303015-1R5M-N, LCSC C142146,
  1.5 uH, Isat 2.7 A, DCR 81.9 mOhm, 3 x 3 mm.
- Sunlord SWPA3015S1R5NT (1.5 uH, 1.7 A, 65 mOhm max per DigiKey/Octopart listings) — **LCSC part
  number UNVERIFIED**; I could not resolve an LCSC product page for the 1R5 variant of this series.

## A3. Capacitors (VERIFIED, SLVS696D §9.2.2.3 and Table 2)

| Ref | Datasheet value | Notes |
|---|---|---|
| C_IN (pin 5) | "At least a 4.7 uF input capacitor is recommended"; reference design uses **10 uF 6.3 V X7R 0603** (Murata GRM188R60J106KME84D) | Ceramic, as close as possible to VIN and PGND |
| C_VINA (pin 8) | **0.1 uF** ceramic between VINA and GND; "The value of this capacitor should not be higher than 0.22 uF" | Hard upper limit — do not fit 1 uF here |
| C_OUT (pin 1) | "recommended nominal output capacitance value is 10 uF"; reference design uses **2 x 10 uF 6.3 V X7R 0603** | "There is also no upper limit for the output capacitance value" |

**DC-bias derating note.** Class-II (X5R/X7R, barium-titanate) MLCCs lose capacitance under applied DC
bias; C0G/NP0 and non-ceramic types do not (VERIFIED, Murata:
https://article.murata.com/en-global/article/voltage-characteristics-of-electrostatic-capacitance).
The percentage loss is part-specific and depends on case size, rated voltage and dielectric —
Murata's SimSurfing gives the curve per part number. Practical consequence: a nominal 10 uF
6.3 V X5R in 0402/0603 can deliver substantially less than 10 uF at 3.3–4.2 V bias, so the
datasheet's 10 uF in / 2 x 10 uF out should be read as *effective* capacitance. Mitigation: use
0805 and/or 10 V–16 V rated X7R, or fit 22 uF nominal where 10 uF effective is wanted.
**The exact derating for a chosen part number is UNVERIFIED here** — look it up in SimSurfing for
the specific MPN before committing the BOM.

## A4. Quiescent current (VERIFIED, Electrical Characteristics)

| Parameter | Conditions | Typ | Max |
|---|---|---|---|
| Iq on VIN + VINA | IOUT = 0 mA, VEN = VIN = VINA = 3.6 V, VOUT = 3.3 V | **25 uA** | 35 uA |
| Iq on VOUT | same | **4 uA** | 6 uA |
| Shutdown current IS | VEN = 0 V, VIN = VINA = 3.6 V | 0.1 uA | 0.9 uA |

Total no-load draw is therefore **~29 uA typ, 41 uA max**. Front page claim: "Device quiescent
current less than 50 uA".

**This matters for the stated deep-sleep budget.** The requirement is "tens of microamps" in deep
sleep; the regulator alone consumes ~29 uA of that before the nRF52840 draws anything. See A7.

## A5. EN and PS/SYNC usage (VERIFIED)

- **EN (pin 6):** 1 = enabled, 0 = shutdown. In shutdown the regulator stops switching, all internal
  control is off and **the load is disconnected from the input** — so VOUT can fall below VIN
  (§8.3.1). Logic levels: VIL max 0.4 V, VIH min 1.2 V, input current 0.01 uA typ / 0.1 uA max.
  Because the input current is sub-microamp, a high-value pull-up (1–10 MOhm) to VSYS is fine.
  EN has no internal pull — it must be driven; do not leave floating.
- **PS/SYNC (pin 7):** low = power-save enabled, high = forced fixed-frequency PWM, clock = PLL sync.
  In power-save the converter stops switching when the average inductor current falls below about
  100 mA and VOUT is at or above nominal, then bursts to recharge (§8.4.3).
  **Tie PS/SYNC to GND for this design** — the load is a few mA most of the time, and forced-PWM
  would burn milliamps continuously.
- **Cost of power-save: looser output regulation.** VOUT accuracy is 3.267–3.333 V with PS/SYNC = VIN
  (forced PWM) but **-3% / +6% referenced to 3.3 V with PS/SYNC = GND** (VERIFIED, EC table), i.e.
  3.20–3.50 V. Confirm every rail consumer tolerates 3.50 V (nRF52840 absolute max is 3.9 V on VDD,
  so this is fine — but verify the mic and LED parts).
- UVLO: device shuts down if VINA falls below ~1.5 V typ (1.4–1.6 V).
- Minimum input voltage for start-up: 1.8 V typ (1.6–2.0 V max).

## A6. Efficiency and output capability (VERIFIED)

- Headline: "Up to 96% efficiency" (front page).
- "800-mA output current at 3.3 V in step-down mode (VIN = 3.6 V to 5.5 V)"; "up to 500-mA output
  current at 3.3 V in boost mode (VIN > 2.4 V)". Both far exceed the 150 mA requirement across the
  whole 2.9–4.4 V cell range.
- Graph read-offs (READ FROM FIGURES, +/-3 percentage points, not tabulated values):
  - Figure 9 (TPS63031, VOUT = 3.3 V, power-save enabled, efficiency vs IOUT): at VI = 3.6 V the curve
    sits at roughly **85–90% from ~1 mA to ~200 mA**; at VI = 2.4 V roughly **80–85%** over the same
    span. Below ~1 mA it falls to roughly 65–80%.
  - Figure 15 (TPS63031, VOUT = 3.3 V, power-save enabled, efficiency vs VIN): IOUT = 100 mA holds
    roughly **85–92% across VIN 2.2–5.4 V**; IOUT = 10 mA roughly 80–90%.
  - Figure 10/16 (power-save **disabled**) show efficiency collapsing at low load — at 10 mA it drops
    below 60% and keeps falling. Confirms PS/SYNC must be grounded.

## A7. Availability and price — TPS63031DSKR

VERIFIED:
- **LCSC C15516** (https://www.lcsc.com/product-detail/C15516.html). SON-10-EP (2.5 x 2.5).
  LCSC stock 7,153. LCSC price $1.043 (1+), $0.8656 (10+), $0.6193 (100+).
- **JLCPCB: Extended part** (componentLibraryType = "expand", page labelled "Extended Part"),
  https://jlcpcb.com/partdetail/TexasInstruments-TPS63031DSKR/C15516.
  JLCPCB price tiers: $1.0335 (1–9), $0.8577 (10–29), $0.7601 (30–99), $0.6136 (100–499), $0.5648 (500–999).
- It is in stock and assemblable. At ~$1 for a prototype quantity this is not "expensive" in absolute
  terms, but it is the single most expensive passive-side part on the power rail, and it is an
  Extended part (JLCPCB charges a per-feeder setup fee for Extended parts).

### Fallbacks (all VERIFIED as present in the JLCPCB library, all **Extended**)

| Part | LCSC | Package | Vout | Iq typ | Iout | JLCPCB price 1–9 / 100–499 | Difference vs TPS63031 |
|---|---|---|---|---|---|---|---|
| TPS63001DRCR | C28060 | VSON-10 3.0 x 3.0 | fixed 3.3 V | **50 uA** (JLCPCB spec line) | 1200 mA buck / 800 mA boost | $1.6178 / $1.0091 | Bigger footprint, 1.5 MHz, 2x the Iq, ~60% more expensive. Only worth it if C15516 goes out of stock. |
| TPS63021DSJR | C202140 | VSON-14 | fixed 3.3 V | — | 4 A switches | LCSC from $0.8895 (LCSC page, VERIFIED via search result; JLCPCB tiers not fetched) | Much larger switches than needed; bigger package. |
| **TPS63900DSKR** | **C1518762** | WSON-10-EP **2.5 x 2.5** (same size as TPS63031) | **adjustable 1.8–5 V** (32 programmable settings, so 3.3 V is set by resistors, not fixed) | **75 nA** | 400 mA | $1.1247 / $0.7406 | See A8 — this is the one that actually fixes the deep-sleep problem. LCSC stock 30,890. |

## A8. Buck-boost vs low-Iq LDO (TLV75533)

TLV755P / TLV75533PDBVR, VERIFIED from SBVS320D and LCSC/JLCPCB:
- LCSC **C404027**; JLCPCB **Extended part**; JLCPCB price $0.1587 (1–49), $0.1233 (50–149),
  $0.108 (150–499). Far cheaper than any buck-boost. SOT-23-5.
- Input range 1.45–5.5 V; 500 mA; fixed 3.3 V option.
- Dropout, VOUT 3.3 V, IOUT = 500 mA: **150 mV typ, 215 mV max (-40 to +85 C), 238 mV max (DYD pkg)**.
- Dropout at 150 mA: **~50 mV at 25 C, ~60 mV at 125 C** (READ FROM Figure 5-13, not a tabulated value).
- IGND (quiescent): **25 uA typ, 31 uA max at 25 C / IOUT = 0**; 33 uA max to +85 C; 40 uA max to +125 C.
- IGND rises with load: **~500 uA at IOUT = 150 mA, ~700 uA at 500 mA** (READ FROM Figure 5-17).
- Shutdown current 0.1 uA typ / 1 uA max.

### Cell-voltage floor for a 3.3 V LDO at this load (CALCULATED from the above)

    V_cell(min) = 3.3 V + V_dropout(150 mA) + I*R(protection FETs + PCB)
                = 3.3 + 0.050 + (0.150 A * ~0.05 Ohm)
                ~= 3.36 V typ at 25 C; ~3.37 V at 85 C

So a 3.3 V LDO stops regulating once the cell falls to roughly **3.35–3.37 V under a 150 mA peak**
(and ~3.32 V under a few-mA load, where dropout is ~10–20 mV). The buck-boost keeps regulating down
to a 1.8 V input. A Li-ion cell spends most of its remaining capacity below 3.4 V, so the LDO
forfeits a large fraction of the pack — **the exact percentage depends on the specific cell's
discharge curve and is UNVERIFIED here**; measure or take it from the cell datasheet.

### Straight comparison of the facts

| | TPS63031 buck-boost | TLV75533 LDO |
|---|---|---|
| Regulates down to | VIN 1.8 V (start-up), UVLO ~1.5 V | ~3.35 V cell at 150 mA (CALCULATED) |
| Efficiency at 100 mA, VIN 2.9–4.4 V | ~85–92% (Fig 15, graph read) | VOUT/VIN: 3.3/4.2 = 79%, 3.3/3.6 = 92%, 3.3/3.4 = 97% |
| No-load Iq | 25 uA (VIN/VINA) + 4 uA (VOUT) = ~29 uA typ | 25 uA typ / 31 uA max |
| Extra loss at 150 mA | included in efficiency | IGND ~500 uA on top of the load (Fig 5-17) |
| Output tolerance | 3.20–3.50 V in power-save; 3.267–3.333 V in forced PWM | ±(accuracy spec), no burst ripple |
| Output noise | switching, 2.4 MHz burst mode at light load | 71.5 uVrms (JLCPCB spec line) — relevant for the PDM mic rail |
| Cost (JLCPCB, qty 100+) | $0.61 | $0.11 |
| Package | VSON-10 2.5 x 2.5 + 1.5 uH inductor + 3 caps | SOT-23-5 + 2 caps |

**Key finding on the deep-sleep budget:** neither the TPS63031 (~29 uA) nor the TLV75533 (25 uA typ)
is compatible with a *tens of microamps* total sleep current — the regulator alone eats most of it.
If the sleep target is real, **TPS63900DSKR (LCSC C1518762, 75 nA Iq, same 2.5 x 2.5 WSON-10 footprint,
400 mA, $0.74 at 100+)** is the part that meets it; its output is resistor-programmed rather than
fixed 3.3 V. Its full pin list and external-component requirements were NOT researched here —
**UNVERIFIED / needs a follow-up pass on https://www.ti.com/lit/ds/symlink/tps63900.pdf**.

---

# PART B — Single-cell protection between CELL- and system GND

Correction to the brief: **FS8205A is SOT-23-6, not TSSOP-8** (VERIFIED, LCSC C2830320 page and
JLCPCB listing).

## Option 1 — DW01A + FS8205A

### DW01A pins (VERIFIED, DW01 datasheet, DigiKey-hosted 5272_DW01.pdf; SOT-23-6)

| Pin | Name | Function | Connection |
|---|---|---|---|
| 1 | OD | MOSFET gate connection pin for discharge control | Gate of the discharge FET (FS8205A pin 4 in the standard pack topology) |
| 2 | CS | Input pin for current sense, charger detect | Through **R2 = 1 kOhm** to PACK- (system GND / the far end of the FET pair) |
| 3 | OC | MOSFET gate connection pin for charge control | Gate of the charge FET |
| 4 | TD | Test pin for reduce delay time | Leave open (no connection) |
| 5 | VCC | Power supply, through a resistor (R1) | Through **R1 = 100 Ohm** to BATT+; **C1 = 0.1 uF** from VCC to GND |
| 6 | GND | Ground pin | CELL- (the common source node of the two FETs) |

The 100 Ohm / 0.1 uF RC on VCC and the 1 kOhm on CS are exactly the values in the datasheet's
"Typical Application Circuit" figure (VERIFIED — R1 100 Ohm, C1 0.1 uF, R2 1 kOhm). The RC filters
the cell node and limits current into VCC during a short; the 1 kOhm limits current into CS when a
charger is connected to a deeply discharged pack.

### DW01A thresholds (VERIFIED, Electrical Characteristics, Ta = 25 C)

| Parameter | Symbol | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| Overcharge protection voltage | VOCP | 4.25 | **4.30** | 4.35 | V |
| Overcharge release voltage | VOCR | 4.05 | 4.10 | 4.15 | V |
| Overdischarge protection voltage | VODP | 2.30 | **2.40** | 2.50 | V |
| Overdischarge release voltage | VODR | 2.90 | 3.00 | 3.10 | V |
| Overcurrent protection voltage | VOI1 | 120 | **150** | 180 | mV |
| Short-circuit protection voltage | VOI2 | 1.0 | 1.2 | 1.4 | V |
| Overcharge delay | TOC | | 80 | 200 | ms |
| Overdischarge delay | TOD | | 40 | 200 | ms |
| Overcurrent delay (1) | TOI1 | | 10 | 20 | ms |
| Overcurrent delay (2) | TOI2 | | 5 | 50 | us |
| Supply current | ICC | | **3.0** | 6.0 | uA |
| Power-down current (VCC = 1.8 V) | IPD | | | 4 | uA |
| Charger detection threshold | VCH | -1.2 | -0.7 | -0.2 | V |

Note vs the brief: the **over-discharge threshold is 2.40 V typ (2.30–2.50 V), below the requested
2.5–2.8 V band.**

### FS8205A (data from LCSC/JLCPCB listing only — manufacturer datasheet NOT fetched)

- LCSC **C2830320**, manufacturer "TECH PUBLIC", **SOT-23-6**, dual N-channel, common-drain.
- VDS 20 V, ID 6 A, Pd 1.5 W, **Rds(on) 31.5 mOhm @ Vgs = 2.5 V** (JLCPCB/LCSC describe string);
  the LCSC page additionally states 18 mOhm @ Vgs = 4.5 V. Ta -55 to +150 C.
- LCSC stock 92,640. LCSC price $0.0502 (10+), $0.0382 (100+), $0.0322 (300+).
- **JLCPCB: Extended part.** JLCPCB price $0.0497 (1–99), $0.0378 (100–299), $0.0319 (300–2999).

### Resulting overcurrent trip (CALCULATED)

Trip current = VOI1 / (2 x Rds(on)), since both FETs are in the current path.
- Rds(on) 31.5 mOhm each (Vgs = 2.5 V, worst gate drive near cutoff): 150 mV / 63 mOhm = **2.4 A**
- Rds(on) ~20–22 mOhm each (Vgs ~3.5–4 V, normal operation): 150 mV / ~42 mOhm = **~3.5 A**

So the trip lands in the requested **2–3 A band at low cell voltage and drifts up to ~3.5 A at a full
cell**. This is Vds-sensing, so it is inherently loose — that is normal for this topology.

### DW01A availability (VERIFIED)

- LCSC **C351410**, manufacturer PUOLOP, SOT-23-6L. LCSC price from $0.0237.
- **JLCPCB: Extended part.** JLCPCB price $0.0419 (1–199), $0.0334 (200–599), $0.0287 (600–2999).
- Alternate source in the JLCPCB library: PJSEMI DW01, LCSC C686633 (existence VERIFIED from search
  result; parameters not fetched).

## Option 2 — TI BQ297xx + separate dual N-FET

### Which variant for a standard 4.2 V cell (VERIFIED, SLUSBU9I Device Comparison Table)

| Part | OVP (V) | OVP delay (s) | UVP (V) | UVP delay (ms) | OCC (V) | OCC delay (ms) | OCD (V) | OCD delay (ms) | SCD (V) | SCD delay (us) |
|---|---|---|---|---|---|---|---|---|---|---|
| **BQ29700** | **4.275** | 1.25 | **2.800** | 144 | -0.100 | 8 | **0.100** | 20 | 0.5 | 250 |
| BQ29701 | 4.280 | 1.25 | 2.300 | 144 | -0.100 | 8 | 0.125 | 8 | 0.5 | 250 |
| BQ29702 | 4.350 | 1 | 2.800 | 96 | -0.155 | 8 | 0.160 | 16 | 0.3 | 250 |
| BQ29704 | 4.425 | 1.25 | 2.500 | 20 | -0.100 | 8 | 0.125 | 8 | 0.5 | 250 |
| BQ29707 | 4.280 | 1 | 2.800 | 96 | -0.090 | 6 | 0.090 | 16 | 0.3 | 250 |
| BQ29728 | 4.280 | 1.25 | 2.800 | 144 | -0.100 | 8 | 0.150 | 8 | 0.5 | 250 |
| BQ29737 | 4.250 | 1 | 2.800 | 96 | -0.050 | 16 | 0.100 | 16 | 0.3 | 250 |

**BQ29700 is the right variant for a standard 4.2 V cell** and matches the brief exactly: overcharge
4.275 V (inside 4.25–4.3), over-discharge 2.800 V (inside 2.5–2.8), OCD 100 mV.
Recovery delays (VERIFIED, footnote): OVP recovery 12 ms; UVP/OCC/OCD recovery 8 ms.
Normal-mode ICC = 4 uA typ (VERIFIED, front page).

### BQ29700DSER pins (VERIFIED, SLUSBU9I §5, DSE package, WSON-6 1.5 x 1.5 mm)

| Pin | Name | Type | Function | Connection (per §5.1) |
|---|---|---|---|---|
| 1 | NC | — | No connection (electrically open) | Leave open |
| 2 | COUT | O | Gate drive output for charge FET | Charge FET gate; **5 MOhm from COUT to PACK-** for gate discharge |
| 3 | DOUT | O | Gate drive output for discharge FET | Discharge FET gate; **5 MOhm from DOUT to VSS** for gate discharge |
| 4 | VSS | P | Ground / cell negative reference | CELL- (common source of the FET pair) |
| 5 | BAT | P | VDD supply, to battery positive | BATT+; **0.1 uF to ground** for noise filtering |
| 6 | V- | I/O | Voltage sense node (charger negative / Vds sensing) | **2.2 kOhm to PACK-** |

Note the external network differs from DW01A: TI specifies a **0.1 uF on BAT**, a **2.2 kOhm on V-**,
and **two 5 MOhm gate-discharge resistors**. The datasheet text does not call for a series resistor
into BAT the way the DW01 circuit does (a 100–1000 Ohm series resistor there is common practice but
is **UNVERIFIED** against this datasheet).

### BQ29700DSER availability (VERIFIED)

- **LCSC C183096**, WSON-6 (1.5 x 1.5). LCSC stock 2,845. LCSC price $0.67 (1+), $0.52 (10+), $0.38 (100+).
- **JLCPCB: Extended part.** JLCPCB price $0.6608 (1–9), $0.5176 (10–29), $0.4574 (30–99), $0.3809 (100–499).

### Which dual N-FET pairs with it

The BQ297xx does Vds sensing across the FET pair exactly like the DW01A, so the **same FS8205A
(LCSC C2830320, SOT-23-6)** pairs with it directly. Trip current (CALCULATED, OCD = 100 mV):
- 100 mV / (2 x 31.5 mOhm) = **1.6 A** at Vgs = 2.5 V
- 100 mV / (2 x ~21 mOhm) = **~2.4 A** at Vgs ~3.5–4 V

That is at or slightly below the bottom of the requested 2–3 A band. If a higher trip is wanted,
either pick a variant with a higher OCD (BQ29702 at 160 mV, or BQ29728 at 150 mV) or a lower-Rds(on)
FET pair. BQ29700's 20 ms OCD delay is long enough to ride through WS2812B / speaker current bursts.

## Recommendation for a low-volume JLCPCB-assembled prototype

**Use DW01A (LCSC C351410) + FS8205A (LCSC C2830320).**

Reasons, all from verified data above:
1. **Cost**: ~$0.09 for the pair at prototype quantity vs ~$0.71 for BQ29700DSER + FS8205A.
2. **Availability**: FS8205A LCSC stock 92,640 and DW01A is a commodity with a second source in the
   JLCPCB library (PJSEMI DW01, C686633). BQ29700DSER LCSC stock is 2,845 — an order of magnitude
   thinner, and TI single-source.
3. **Basic-part status**: irrelevant as a tie-breaker — **all four candidate parts are Extended**
   (DW01A, FS8205A, BQ29700DSER, and the TPS63031 too). No option avoids the Extended-part feeder fee.
4. **Footprint**: two SOT-23-6 packages, both hand-reworkable if the prototype needs surgery.
   BQ29700's WSON-6 1.5 x 1.5 is physically smaller but is a leadless package — worse for probing
   and rework on a prototype.
5. **External network**: DW01A needs 3 passives (100 Ohm, 0.1 uF, 1 kOhm). BQ29700 needs 4
   (0.1 uF, 2.2 kOhm, 2 x 5 MOhm).
6. **Overcurrent trip** with the same FET pair lands at 2.4–3.5 A for DW01A vs 1.6–2.4 A for BQ29700
   — DW01A is the better match to the requested 2–3 A.

**The one place DW01A loses**: its over-discharge cutoff is **2.40 V typ (2.30–2.50 V)**, below the
requested 2.5–2.8 V. For a protection backstop this is acceptable — most 18650 cells specify 2.5 V
discharge cutoff with a lower absolute limit, and occasional excursions to 2.4 V are not damaging —
but the *normal* low-battery cutoff should be enforced in firmware (ADC on the cell, shut down at
3.0–3.2 V), not by the protection IC. **The cell-specific safe floor is UNVERIFIED here**; check the
chosen 18650's datasheet.

**Switch to BQ29700DSER (C183096) if** the 2.8 V hardware cutoff is a hard requirement, or if the
tighter, temperature-characterised TI thresholds are needed for compliance. The $0.6 delta is
negligible at prototype volume; the real costs are thinner stock and the leadless package.

---

## Open / unverified items

1. Exact JLCPCB **assembly stock** for every part above (the partdetail pages embed multiple stock
   figures for related parts and could not be attributed reliably). LCSC stock figures are quoted instead.
2. **FS8205A manufacturer datasheet** — not fetched; Rds(on), Vgs(th) and SOA come from the
   LCSC/JLCPCB listing text only.
3. **MLCC DC-bias derating percentages** for specific chosen capacitor MPNs — needs Murata SimSurfing
   or the MPN's own bias curve.
4. **Sunlord SWPA3015S1R5NT LCSC part number** — could not be resolved; use Murata C909806 instead.
5. **TPS63900 pin list / external components / output-voltage programming** — not researched, but
   this part (75 nA Iq, same 2.5 x 2.5 package, LCSC C1518762) is the only candidate found that meets
   a tens-of-microamps total sleep budget. Recommend a follow-up pass before freezing the schematic.
6. Fraction of 18650 capacity forfeited by an LDO's ~3.35 V floor — depends on the specific cell's
   discharge curve.
