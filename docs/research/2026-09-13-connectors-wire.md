# Internal cabling research: JST SH / JST PH, crimp tooling, wire

Researched 2026-09-13. Every fact is tagged VERIFIED (with source URL) or UNVERIFIED.
Prices are as listed on the date of fetch and will drift.

Primary sources used:
- JST SH datasheet: https://www.jst-mfg.com/product/pdf/eng/eSH.pdf
- JST PH datasheet: https://www.jst-mfg.com/product/pdf/eng/ePH.pdf
- ENGINEER INC. JST compatibility table (rev. 2022/10/3):
  https://www.engineertools-jp.com/_files/ugd/104650_d0f165fa6193478890e7f27fffed5ab8.pdf
  (linked from https://www.engineertools-jp.com/crimping-tool-compatibility-table)

---

## 1. JST SH (1.0 mm pitch)

### Series ratings — VERIFIED (eSH.pdf p.1)

| Parameter | Value |
|---|---|
| Current rating | 1.0 A AC/DC (at AWG #28) |
| Voltage rating | 50 V AC/DC |
| Temperature | −25 °C to +85 °C (incl. current-induced rise) |
| Contact resistance | 20 mΩ initial, 40 mΩ after environmental test |
| Insulation resistance | 100 MΩ min |
| Withstanding voltage | 500 VAC, 1 min |
| Applicable wire | conductor AWG #32 to #28; **insulation O.D. 0.40–0.80 mm** |

The 0.40–0.80 mm insulation-OD window is the binding mechanical constraint on SH, not the
conductor gauge. AWG #30 and #32 are explicitly inside the SH contact range.

### Headers — VERIFIED (eSH.pdf p.3)

Model-number decode (eSH.pdf p.4): `BM` = SMT **top entry**, `SM` = SMT **side entry**;
`S` = natural (ivory); `-TB` = embossed tape-and-reel.

| Pos. | Side entry (SMT) | Top entry (SMT) | A (mm) | B = overall width (mm) |
|---|---|---|---|---|
| 2 | SM02B-SRSS-TB | BM02B-SRSS-TB | 1.0 | 4.0 |
| 3 | SM03B-SRSS-TB | BM03B-SRSS-TB | 2.0 | 5.0 |
| 4 | SM04B-SRSS-TB | BM04B-SRSS-TB | 3.0 | 6.0 |
| 6 | SM06B-SRSS-TB | BM06B-SRSS-TB | 5.0 | 8.0 |

Distributors append the RoHS/finish suffix: `SM04B-SRSS-TB(LF)(SN)`. Same part.

Body profile, read from the eSH.pdf drawings (VERIFIED but dimensioned off the drawing, so
treat ±0.05 as drawing tolerance):

- **Side entry (SM0xB)**: height above PCB **2.9 mm**; body depth **4.25 mm**, plus **0.7 mm**
  solder-tab projection; PCB-layout assembly outline **6.25 × 2.95 mm**; land pitch 1.0 mm,
  pad 0.6 × 1.2 mm (approx., from p.1 "Side entry type" layout), hold-down lands at 4.0/5.55 mm.
- **Top entry (BM0xB)**: height above PCB **4.25 mm**; body depth **2.9 mm** plus **0.7 mm** tab;
  PCB-layout assembly outline height 6.3 mm on the drawing (mated stack).

Materials: base contact copper alloy tin-plated; housing PA (heat-resistant), natural/ivory;
metal reinforcement (hold-down) copper alloy tin-plated. Reel qty: side entry 3,000; top entry 1,500.

### Mating housings — VERIFIED (eSH.pdf p.2)

PBT, natural (white). `-B` suffix = **with protrusions**; without `-B` = no protrusions.
Housing height 5.0 mm, depth 2.8 mm (both VERIFIED from drawing).

| Pos. | With protrusions | Without | A (mm) | B with protr. (mm) | B without (mm) |
|---|---|---|---|---|---|
| 2 | SHR-02V-S-B | SHR-02V-S | 1.0 | 5.0 | 3.0 |
| 3 | SHR-03V-S-B | SHR-03V-S | 2.0 | 6.0 | 4.0 |
| 4 | SHR-04V-S-B | SHR-04V-S | 3.0 | 7.0 | 5.0 |
| 6 | SHR-06V-S-B | SHR-06V-S | 5.0 | 9.0 | 7.0 |

### Crimp contact — VERIFIED (eSH.pdf p.2)

| Model | Conductor | Insulation O.D. | Packaging |
|---|---|---|---|
| SSH-003T-P0.2-H | AWG #32 to #28 (0.032–0.081 mm²) | 0.4–0.8 mm | 23,000 / reel |

Copper alloy, tin-plated. Contact body is **3.9 mm long × 1.35 mm tall × 0.8 mm wide**
(VERIFIED, contact drawing). JST's own crimping machine is AP-K2N with applicator MKS-L-10-3 /
APLMK SH/L003-02 — production tooling, not relevant here.

Related variants seen in the ENGINEER table (VERIFIED they exist as part numbers, not researched
further): SSH-003GA-P0.2 (gold, SHD series), SSHL-003T-P0.2 / SSHL-003GA1-P0.2 (SHL series).

### LCSC / JLCPCB — VERIFIED part numbers

| Part | LCSC | Note |
|---|---|---|
| SM02B-SRSS-TB(LF)(SN) | C160402 | https://www.lcsc.com/product-detail/C160402.html — 61,285 in stock, from $0.133 |
| SM03B-SRSS-TB(LF)(SN) | C160403 | 24,915 in stock, from $0.1099 |
| SM04B-SRSS-TB(LF)(SN) | C160404 | 44,240 in stock, from $0.1245 |
| SM06B-SRSS-TB(LF)(SN) | C160405 | 550 in stock, from $0.1664 — thin stock, check before designing in |
| BM02B-SRSS-TB(LF)(SN) | C160388 | |
| BM03B-SRSS-TB(LF)(SN) | C160389 | from $0.1597 |
| BM04B-SRSS-TB(LF)(SN) | C160390 | from $0.1341 |
| BM06B-SRSS-TB(LF)(SN) | C160392 | from $0.1726 |
| SHR-02V-S-B | C246754 | |
| SHR-03V-S-B | C268100 | from $0.0703 |
| SHR-04V-S-B | C394367 | from $0.0350 |
| SHR-06V-S-B | C394368 | from $0.0586 |
| SSH-003T-P0.2-H | C263995 | **MOQ 50, multiple 50**, 227,700 in stock, $0.02 @50 — VERIFIED from LCSC page |

JLCPCB library status: **Extended** — VERIFIED for C160404
(https://jlcpcb.com/partdetail/JST-SM04B_SRSS_TB_LF_SN/C160404). The other SH headers are
almost certainly Extended too, but each one is UNVERIFIED individually. Extended parts attract
JLCPCB's per-unique-part feeder fee and must be in stock at order time.

---

## 2. JST PH (2.0 mm pitch)

### Series ratings — VERIFIED (ePH.pdf p.1)

| Parameter | Value |
|---|---|
| Current rating | 2 A AC/DC (at AWG #24) |
| Voltage rating | 100 V AC/DC |
| Temperature | −40 °C to +105 °C |
| Contact resistance | 10 mΩ initial, 20 mΩ after test |
| Insulation resistance | 1,000 MΩ min |
| Withstanding voltage | 800 VAC, 1 min |
| Applicable wire | AWG #32 to #24; insulation O.D. 0.5–1.5 mm |
| PCB thickness | 0.8–1.6 mm |

Note the distributor pages for the pre-crimped PH leads quote "3 A max" for the lead assembly;
the **connector system** rating from JST is 2 A. Use 2 A.

### SMT header, 2 positions — VERIFIED (ePH.pdf p.4 and p.5 model-number allocation)

- **S2B-PH-SM4-TB = SIDE entry** (`S` = side entry in the SMT header decode). A = 2.0 mm,
  B = 7.9 mm. Drawing: height **5.5 mm**, depth **6 mm** with a (2.6) reference dim.
- **B2B-PH-SM4-TB = TOP entry** (`B` = top entry). A = 2.0 mm, B = 7.95 mm. Drawing:
  height **6.6 mm**, depth **5 mm** with a (2) reference dim.

So for a 30 × 30 mm stick, side entry S2B-PH-SM4-TB is the flatter part (5.5 mm vs 6.6 mm) and
the one that lets the battery lead exit parallel to the board.

Materials: post copper alloy tin-plated, housing PA heat-resistant natural (ivory), tin-plated
reinforcement. 1,000/reel.

### Housing — VERIFIED (ePH.pdf p.3)

PHR-2: A = 2.0 mm, B = 5.8 mm, height 6.85 mm, depth 4.5 mm. PA, natural (white).
Colour variants exist per the model-number allocation (p.5): PHR-2-BK black, PHR-2-R red,
PHR-2-Y yellow, PHR-2-BL blue, etc. LCSC stocks PHR-2 (C157955), PHR-2-R (C398543),
PHR-2-BK (C398538) — VERIFIED part numbers from LCSC listings.

### Crimp contacts — VERIFIED (ePH.pdf p.2)

| Model | Conductor | Insulation O.D. | Reel |
|---|---|---|---|
| SPH-002T-P0.5S | AWG #30 to #24 (0.05–0.22 mm²) | 0.8–1.5 mm | 8,000 |
| SPH-004T-P0.5S | AWG #32 to #28 (0.032–0.08 mm²) | 0.5–0.9 mm | 10,000 |
| SPH-002T-P0.5L | AWG #28 to #24 (0.08–0.22 mm²) | 0.8–1.5 mm | 8,000 |

`L` = low-insertion-force variant: easier mate/unmate, less vibration-resistant, different crimp
height. For a battery lead in a handheld device, use the standard **SPH-002T-P0.5S**.
Contact body 5.7 mm long × 2.08 mm tall × 1.5 mm wide (VERIFIED, drawing).

### LCSC — VERIFIED

| Part | LCSC |
|---|---|
| S2B-PH-SM4-TB(LF)(SN) (side entry) | C295747 — from $0.1154 |
| B2B-PH-SM4-TB(LF)(SN) (top entry) | C160352 — from $0.182 |
| PHR-2 | C157955 |
| SPH-002T-P0.5S | C111515 — from $0.0042 |

JLCPCB status for S2B-PH-SM4-TB (C295747): **Extended** — VERIFIED
(https://jlcpcb.com/partdetail/Jst-S2B_PH_SM4_TB_LF_SN/C295747).

---

## 3. Pre-crimped leads

### JST's own SH leads — VERIFIED

Naming: `ASSHSSH` + `28` (AWG) + `K` + length in mm. **Contacts (SSH-003T-P0.2-H) crimped on
both ends** — DigiKey calls this "Socket to Socket", JST calls them "double-end leads".
Wire is 28 AWG, **UL1571** (thin-wall PVC — this is what keeps the insulation inside SH's
0.4–0.8 mm window), black only, tin finish, −25 to +105 °C.

| Part | Length | DigiKey |
|---|---|---|
| ASSHSSH28K51 | 50.8 mm (2") | detail 6009451 |
| ASSHSSH28K102 | 101.6 mm (4") | detail 9924463 |
| ASSHSSH28K152 | 152.4 mm (6") | **455-3076-ND**, detail 6009452, $0.49 @1 |
| ASSHSSH28K203 | 203.2 mm (8") | detail 9924464 |
| ASSHSSH28K254 | 254.0 mm (10") | detail 9924465 |
| ASSHSSH28K305 | 304.8 mm (12") | **455-3077-ND**, detail 6009453 |

Stock caution — VERIFIED on 2026-09-13: ASSHSSH28K152 showed **0 in stock at DigiKey, 1,000
expected 2026-10-12**. Check availability before relying on these.
LCSC also lists ASSHSSH28K152 as **C5304590** (VERIFIED part number from LCSC listing;
stock/price UNVERIFIED).

Single-ended SH leads: **UNVERIFIED** — I did not find a JST single-ended SH lead part number.
The `ASSHSSH` pattern doubles the series token because both ends are terminated; a single-ended
variant would presumably drop one token, but I found no such part listed and will not guess one.

### JST's own PH leads — VERIFIED

Naming: `ASPHSPH` + `24` + `K` + length mm. Contacts on **both ends**, 24 AWG, black,
dual-rated **UL1007/1569** wire, tin finish.

| Part | Length | DigiKey |
|---|---|---|
| ASPHSPH24K51 | 50.8 mm | detail 6009457 |
| ASPHSPH24K102 | 101.6 mm | detail 9918854 |
| ASPHSPH24K152 | 152.4 mm | **455-3082-ND**, detail 6009458 |
| ASPHSPH24K203 | 203.2 mm | detail 9918855 |
| ASPHSPH24K254 | 254.0 mm | listed |
| ASPHSPH24K305 | 304.8 mm | detail 6009459 |

22 AWG PH leads: **UNVERIFIED/does not appear to exist**. JST's PH lead family is 24 AWG only,
and 22 AWG is outside the PH contact range (#32–#24) anyway. A search for `ASPHSPH22K*`
returned no such part. Do not use 22 AWG in a PH contact.

26 AWG PH leads: **UNVERIFIED** — no `ASPHSPH26K*` part found. 26 AWG is inside the
SPH-002T-P0.5S range, so it is fine to hand-crimp, just not available pre-crimped from JST.

Colour coding: JST pre-crimped leads (both SH and PH) are **black only** — VERIFIED from the
DigiKey descriptions ("Black 28 AWG Jumper Lead", "Black 24 AWG Jumper Lead"). There is no JST
colour convention for these; you mark polarity yourself.

### Hobby-distributor alternatives

**Adafruit** (VERIFIED, https://www.adafruit.com/category/619):
finished cables, not loose pre-crimped leads.

| PID | Product | Pins | Length |
|---|---|---|---|
| 4399 | STEMMA QT / Qwiic JST SH cable | 4 | 50 mm |
| 4210 | STEMMA QT / Qwiic JST SH cable | 4 | 100 mm |
| 4401 | STEMMA QT / Qwiic JST SH cable | 4 | 200 mm |
| 5384 | STEMMA QT / Qwiic JST SH cable | 4 | 300 mm |
| 5385 | STEMMA QT / Qwiic JST SH cable | 4 | 400 mm |
| 4209 | JST SH 4-pin to premium **male** headers | 4 | 150 mm |
| 4397 | JST SH 4-pin to premium **female** sockets | 4 | 150 mm |
| 6404 | JST SH 1 mm 3-pin plug-plug cable | 3 | 100 mm |
| 6405 | JST SH 1 mm 3-pin plug-plug cable | 3 | 50 mm |
| 6375 | JST SH 1 mm 3-pin to premium plug header cable | 3 | 200 mm |

**Colour convention — VERIFIED** (Adafruit PID 4210): the Qwiic/STEMMA QT standard is
**red = 3.3 V, black = GND, blue = SDA, yellow = SCL**. This is a 4-pin I2C convention; it does
not define colours for 2-, 3- or 6-pin SH cables. Adafruit's 2/3-pin SH cables are "JST SH
compatible" (i.e. not necessarily genuine JST) — UNVERIFIED whether the contacts are JST parts.

**Pololu** (VERIFIED, https://www.pololu.com/category/356/jst-ph-style-cables and
https://www.pololu.com/category/39/cables-and-wire):
- JST **PH-style** cables, 24 AWG UL1007, rated 2 A / 100 V, single- and double-ended,
  2/3/4/5/6-pin, lengths 12 cm to 75 cm. Examples: 5602 (2-pin F-F pins for 0.1" housings,
  75 cm), 5612 (3-pin, 75 cm), 5620 (4-pin, 12 cm), 5617 (3-pin female-female, 63 cm).
- JST **SH-style** cables, 28 AWG, single- and double-ended, various pin counts/lengths.
- Pololu explicitly calls these "JST PH-style"/"SH-style", i.e. compatible clones, not
  guaranteed genuine JST — relevant if you care about contact retention force.
- Pololu ships from the US; their "female pins for 0.1" housings" variants are the useful ones
  for a breadboard-side bring-up rig.

SparkFun: not checked in this pass (UNVERIFIED). They sell Qwiic 4-pin JST SH cables in the
same 50/100/200/500 mm lengths as Adafruit.

---

## 4. Crimp tool

### Verdict

**The Engineer PA-09 does NOT officially crimp JST SH (SSH-003T). Buy the PAD-11 if you want to
terminate SH by hand. The PA-09 does officially crimp JST PH (SPH-002T).**

### Evidence

ENGINEER INC.'s own JST compatibility table (rev. 2022/10/3, PDF linked from
https://www.engineertools-jp.com/crimping-tool-compatibility-table) — VERIFIED by extracting
the PDF text. Columns are PAD-11, PAD-12, PAD-13, PA-09, PA-20, PA-21, PA-24.

```
SH    SSH-003T-P0.2-H   PAD-11   -   -   -       -   -   -
SHD   SSH-003GA-P0.2    PAD-11   -   -   -       -   -   -
SHL   SSHL-003T-P0.2    PAD-11   -   -   -       -   -   -
PH    SPH-002T-P0.5L    PAD-11   -   -   PA-09   -   -   PA-24
PH    SPH-002T-P0.5S    PAD-11   -   -   PA-09   -   -   PA-24
PH    SPH-004T-P0.5S    PAD-11   -   -   PA-09   -   -   PA-24
```

The mechanical reason is the die set — VERIFIED from the ENGINEER product pages:
- **PA-09** dies: 1.0, 1.4, 1.6, 1.9 mm; AWG #32–#20; 175 mm; 135 g.
  (https://www.engineertools-jp.com/product-page/pa-09-connector-crimping-pliers)
- **PAD-11** dies: **0.7**, 1.0, 1.3, 1.6, 1.9, 2.2 mm; 175 mm; 244 g; "over 90 terminals";
  interchangeable die plates, includes 2.5 mm hex key.
  (https://www.engineertools-jp.com/product-page/pad-11-handy-crimp-tool-s)
- **PA-24** dies: round φ1.4, φ1.8; M-shaped 1.3, 1.6, 1.9, 2.2 mm; AWG #32–#18; aimed at
  2.5 mm-pitch JST XH/PH/EH/NH, Molex Micro-Fit/KK.
  (https://www.engineertools-jp.com/product-page/pa-24-micro-connector-crimping-pliers)

The SSH-003T contact is 0.8 mm wide (JST drawing). PA-09's smallest die is 1.0 mm; PAD-11's is
0.7 mm. That is the whole story.

**Conflicting claim, worth knowing** — VERIFIED that the claim exists, not that it works:
DigiKey's TechForum PA-09 article
(https://forum.digikey.com/t/engineer-pa-09-universal-crimping-tool-20-32-awg/282) lists
SSH-003T-P0.2-H among PA-09-compatible contacts, with the caveat quoted verbatim:
*"the manufacturer of this tool does state it will work with all of the contacts listed below,
however the crimp may differ from the manufacturer specified crimp tool and would not be
guaranteed to meet any manufacturer crimp specifications."* Hobby sources repeat this. Given
ENGINEER's own current table says PAD-11 only, treat PA-09-on-SH as "people get away with it",
not as a specification. For a device that will be opened and re-terminated once or twice, the
PAD-11 is the correct buy.

### Price and European sources — VERIFIED

| Tool | Price | Source |
|---|---|---|
| PA-09 | €39.99 ex VAT (€37.99 @10+), 35 in stock | Kiwi Electronics, NL — https://www.kiwi-electronics.com/en/jst-crimping-tool-pa-09-916 — ships from the Netherlands via PostNL/DHL, page states shipping to Norway |
| PAD-11 | £53.09 inc VAT / £44.24 ex VAT | PreciseHandTools, UK — https://precisehandtools.com/pad-11-crimping-tool-s/ — sold as the complete tool pre-fitted with the "Small" die plate set |
| PAD-11 | listed, price not retrieved (403) | TME, PL — https://www.tme.eu/en/details/fut.pad-11/... — TME is the usual EU stockist |

So roughly **€40 for the PA-09 and €55–65 for the PAD-11**. Norway import: post-Brexit UK
shipments add customs handling; TME (Poland) or a Dutch shop is the lower-friction route.
UNVERIFIED: I could not fetch TME's actual EUR price or Norway shipping terms (TME returns 403
to automated fetches).

### IWISS / SN-01BM

**PH-capable, SH-incapable.** The IWISS/iCrimp SN-01BM covers 0.08–0.5 mm² (AWG 28–20) and is
marketed for JST XH 2.54/3.96, PH 2.0, PX, KK254, Dupont, D-Sub
(https://www.iwiss.com/products/sn-01bm-ratchet-crimping-tool-for-0-08-0-5mm-28-20awg).
JST SH 1.0 mm is **not** in its listed coverage and secondary sources explicitly advise against
it. VERIFIED that SH is absent from the vendor's own list; UNVERIFIED by hands-on test.

It is a cheaper PH-only option (typ. €20–30). It does not remove the need for a PAD-11 if you
also want to re-terminate SH, so buying both is probably wasted money — **one PAD-11 covers
both SH and PH** (the table above lists PAD-11 for every SPH-* and SSH-* contact).

---

## 5. Wire gauge recommendations

### Conductor resistance — VERIFIED
Source: https://www.kbe-elektrotechnik.com/en/service/awg-table/

| AWG | Conductor dia. | Cross-section | Resistance |
|---|---|---|---|
| 24 | 0.511 mm | 0.205 mm² | 87.7 Ω/km = 0.0877 Ω/m |
| 26 | 0.404 mm | 0.128 mm² | 140 Ω/km = 0.140 Ω/m |
| 28 | 0.320 mm | 0.0804 mm² | 222 Ω/km = 0.222 Ω/m |

(Cross-check: Adafruit's 26 AWG silicone wire is quoted at 123 Ω/km — its stranded conductor is
slightly over nominal. Use 140 Ω/km as the conservative number.)

### Voltage drop, 100 mm AWG26 battery lead pair at 1 A — CALCULATED from the table above

Loop conductor length = 2 × 100 mm = 0.200 m.
R_loop = 0.200 m × 0.140 Ω/m = **0.0280 Ω**.
ΔV = 1 A × 0.0280 Ω = **28 mV** (28 mW dissipated).
At the 300 mA charge current: **8.4 mV**.

For comparison over the same 100 mm pair at 1 A:
- AWG24: 0.0175 Ω → **17.5 mV**
- AWG28: 0.0444 Ω → **44 mV**

28 mV out of a 3.0–4.2 V cell is under 1 %. AWG26 is comfortably adequate for this battery.

### Per-use recommendations

| Use | Recommended | Reasoning |
|---|---|---|
| SH signal leads (I2S, buttons, LED data) | **AWG 28**, thin-wall (UL1571-style), insulation OD ≤0.8 mm | JST SH contact range is #32–#28 with 0.4–0.8 mm insulation OD (VERIFIED). AWG28 is the top of the range and gives the best crimp grip. |
| SH, if you need thinner | **AWG 30 or 32 are both acceptable** | Explicitly inside SSH-003T's #32–#28 range (VERIFIED). AWG30 silicone at 0.8 mm OD is the only silicone that fits SH at all (see §6). |
| Battery leads, 300 mA charge / 1 A peak discharge | **AWG 26** | 28 mV loop drop at 1 A; inside SPH-002T-P0.5S's #30–#24 range; insulation OD 1.4 mm (silicone) fits the 0.8–1.5 mm window. AWG24 halves the drop but silicone AWG24 at 1.6 mm OD **exceeds** the 1.5 mm contact limit — use PVC UL1007 AWG24 (1.4 mm OD) if you want AWG24. |
| Battery leads if pre-crimped is preferred | AWG 24 (JST ASPHSPH24K*, UL1007/1569) | The only pre-crimped PH option, and it is within contact spec. |
| Speaker leads, 1 W into 8 Ω | **AWG 28 twisted pair is fine** | 1 W / 8 Ω → 354 mA rms, ~500 mA peak, against SH's 1.0 A rating. Loop drop over 100 mm AWG28 = 0.0444 Ω × 0.354 A ≈ 16 mV on ~2.83 V rms, i.e. 0.55 % / ≈0.05 dB. Twisting matters more than gauge here — it is the Class-D amp's switching current that will couple into the mic lines. |

Speaker note: if the amp is a MAX98357A driving 4 Ω rather than 8 Ω, output can reach ~3.2 W
and ~900 mA rms, which is at the edge of SH's 1.0 A rating. UNVERIFIED for this build — confirm
the speaker impedance before committing the speaker to an SH connector; PH would be the safer
choice at 4 Ω.

---

## 6. Silicone-insulated wire outer diameters

| AWG | Silicone OD | Source (VERIFIED) |
|---|---|---|
| 24 | **1.6 mm** ±0.1 (40 × 0.08 mm strands) | BNTECHGO, https://bntechgo.com/silicone-wire/24-gauge-silicone-wire/ |
| 26 | **1.4 mm** ±0.1 (30 × 0.08 mm strands); 123 Ω/km; 600 V; −60…+200 °C | Adafruit PID 1970, https://www.adafruit.com/product/1970 |
| 28 | **1.2 mm** ±0.1 (16 × 0.08 mm strands) | BNTECHGO 28 gauge silicone spool pages |
| 30 | **0.8 mm** (331 Ω/km, 600 V, −60…+200 °C) | Adafruit PID 2051, https://www.adafruit.com/product/2051 |

PVC (UL1007) comparison — VERIFIED from Pololu product pages:

| AWG | Strands | OD | Insulation thickness |
|---|---|---|---|
| 24 | 11 | **1.4 mm** | 0.38 mm avg |
| 26 | 7 | **1.3 mm** | 0.38 mm avg |
| 28 | 7 | **1.2 mm** | — |

### Consequences for the mechanical model

- **The 0.8 mm assumption for AWG28 does NOT hold for silicone or for UL1007 PVC.**
  Silicone AWG28 is 1.2 mm and UL1007 AWG28 is 1.2 mm. Only **AWG30 silicone (0.8 mm)** or
  genuinely thin-wall UL1571 AWG28 hits 0.8 mm.
- This is not just a modelling nicety: JST SH contacts accept a **maximum 0.8 mm** insulation
  OD. A 1.2 mm wire physically will not crimp correctly in the insulation barrel. Either
  (a) use JST's own ASSHSSH28K pre-crimped leads (UL1571, ≤0.8 mm by construction), or
  (b) buy thin-wall UL1571 28 AWG, or (c) drop to AWG30 silicone.
- **The 1.2 mm assumption for AWG24–26 is too optimistic.** Silicone: 1.4 mm (26) / 1.6 mm (24).
  PVC UL1007: 1.3 mm (26) / 1.4 mm (24). Model **1.4 mm** for AWG26 and **1.6 mm** for AWG24
  silicone, and note that silicone AWG24 at 1.6 mm is **outside** the PH contact's 1.5 mm limit.
- Suggested model values: SH leads **0.8 mm** but only if sourced as UL1571 28 AWG or as JST
  pre-crimped leads; battery PH leads **1.4 mm** (26 AWG silicone or 24 AWG UL1007).
- UNVERIFIED: no vendor page I fetched gives an OD for thin-wall UL1571 28 AWG explicitly.
  The 0.4–0.8 mm figure comes from JST's own spec for what the contact accepts, not from a
  wire vendor's datasheet.

---

## 7. Norway / EU purchasing

| Distributor | Norway presence | SH/PH headers | Housings | Contacts | Pre-crimped leads | Verified? |
|---|---|---|---|---|---|---|
| **DigiKey** | digikey.no, NOK pricing | yes | yes | yes (reel only) | yes (JST ASSH*/ASPH*) | VERIFIED |
| **Mouser** | no.mouser.com | yes | yes | UNVERIFIED | UNVERIFIED | partly |
| **Farnell / element14** | no.farnell.com (Norwegian site) | UNVERIFIED | yes (SHR-02V-S-B = 1679108) | yes (SSH-003T-P0.2 = 1679142) | JST harnesses/pre-crimped category exists | partly |
| **Elfa Distrelec** | **gone** — elfadistrelec.no 301-redirects to no.rs-online.com | — | — | — | — | VERIFIED |
| **LCSC** | ships internationally, no NO entity | yes, all SH/PH parts above | yes | yes, MOQ 50 | ASSHSSH28K152 = C5304590 | VERIFIED |
| **TME (PL)** | EU distributor, lists SHR-02V-S-B and SSH-003T-P0.2-H | yes | yes | yes | UNVERIFIED | partly (site 403s automated fetches) |

### Shipping terms — VERIFIED

- **DigiKey Norway** (https://www.digikey.no/en/help-support/delivery-information/delivery-time-and-cost):
  free delivery on orders **≥ kr 830**; **kr 275** charge below that. **UPS = DDP** (DigiKey pays
  duty and customs). FedEx/DHL = CPT (you pay duty, customs and VAT on delivery). Ships from the
  US, typically ~48 h plus customs. **Pick UPS/DDP** — that is the low-friction option.
- **Farnell Norge** (https://no.farnell.com/help-delivery-information): free shipping over
  **kr 850**, no minimum order. Products drawn from the USA (Newark) warehouse add a flat
  **kr 130** per order covering handling, customs and air freight.
- **Mouser Norway** (no.mouser.com): free shipping on most orders over **kr 850**; Mouser
  Europe uses **DDP** on selected shipping methods so listed prices include duty and customs.
  VERIFIED from search-surfaced Mouser page text; I could not fetch mouser.no/mouser.com
  directly (connection refused / timeout), so treat the exact threshold as **UNVERIFIED**.
- **RS Online Norway** (no.rs-online.com): now the Elfa Distrelec successor. 403s automated
  fetches, so stock and terms are **UNVERIFIED**.

### Practical recommendation

1. **DigiKey (UPS/DDP)** for the JST pre-crimped leads and anything you want in 1-off quantity.
   It is the only distributor verified to stock the ASSHSSH28K / ASPHSPH24K leads, and DDP means
   no customs surprise at the door. Watch the SH lead stock gaps.
2. **LCSC** for the headers, housings and loose contacts — MOQ 50 on SSH-003T-P0.2-H versus
   DigiKey's 23,000-piece reel is the difference between a €1 line item and a €900 one.
   Order these alongside the JLCPCB board run if you are having boards assembled anyway.
3. **Kiwi Electronics (NL)** or **TME (PL)** for the crimp tool — intra-EEA, no US customs step.
4. Avoid Farnell's USA-warehouse line items (kr 130 surcharge) unless nothing else has the part.

### Key friction point to plan around — VERIFIED

**SSH-003T-P0.2-H at DigiKey is tape-and-reel only, MOQ 23,000, ~$905**
(DK 455-2963TR-ND, https://www.digikey.com/en/products/detail/jst-sales-america-inc/SSH-003T-P0-2-H/2804713).
Nobody hand-building one prototype should buy that. Route: LCSC (MOQ 50, $0.02 each) or Farnell
(1679142, MOQ UNVERIFIED — I could not load the page), or simply use JST's pre-crimped leads and
never hand-crimp SH at all.

---

## Open items / unverified

- F1. TME's actual EUR price and Norway shipping terms for the PAD-11 (site blocks fetching).
- F2. Farnell's MOQ and packaging for SSH-003T-P0.2 (1679142) — page timed out repeatedly.
- F3. Whether Mouser stocks JST pre-crimped leads and loose SH contacts in small quantity.
- F4. Mouser Norway's exact free-shipping threshold (kr 850 came from search-result text, not a
  fetched page).
- F5. JLCPCB Basic/Extended status confirmed only for C160404 and C295747; the rest assumed
  Extended.
- F6. No single-ended JST SH pre-crimped lead part number found. Not invented here.
- F7. No 22 AWG or 26 AWG JST PH pre-crimped lead found; 22 AWG is outside the PH contact range
  in any case.
- F8. No vendor datasheet located giving an explicit OD for thin-wall UL1571 28 AWG wire.
- F9. PA-09-on-SSH-003T: ENGINEER's table says no, DigiKey's TechForum says yes-with-caveat.
  Not resolved by hands-on test. PAD-11 sidesteps the question.
- F10. Speaker impedance (4 Ω vs 8 Ω) not confirmed for this build; changes whether SH is
  adequate for the speaker leads.
