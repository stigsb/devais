# Devais parts list — 13 September 2026

Companion to [`pcb/DESIGN.md`](pcb/DESIGN.md) revision 2. Quantities are per
unit; the ordering plan in section 9 scales them to ten sets with spares.
Prices are researched unit prices and change. **Verified** means the part
number, package and key data were read from the manufacturer or distributor
page on 2026-09-13 (`docs/research/2026-09-13-*.md`). **Verify** means the
part number or supplier code was not confirmed and must be checked before
ordering.

Build method: bare boards from JLCPCB, all assembly by hand with a hot plate,
solder paste and JLCPCB stencils. Design rules that follow from this: no
passive smaller than 0603, no package with underside-only terminations except
the radio module and the microphone (both are reflowed on the plate), and no
part smaller than a SOT-23-6 without a stencil aperture. Parts come from
LCSC (one order) and DigiKey (module, contacts, cables, thermistor; delivered
duty paid to Norway).

**Open item: radio module.** The MDBT50Q-1MV2 has 61 underside pads at
0.4 mm spacing, 28 of them in inner rows, so it is reflow-only and cannot be
inspected after soldering. The only edge-castellated alternative found is the
MinewSemi MS88SF2 (1.10 mm pitch, DigiKey Marketplace, about $8), but it has
no separate VBUS pad: USB power is tied to VDDH inside the module, which
does not suit the charger's 4.4 V system rail. See
`docs/research/2026-09-13-nrf-module-castellated.md`. Decision deferred to
the 25-unit run; prototypes use the XIAO (`PROTOTYPE.md`).

## 1. Main PCB (4 layers, 26 × 126 × 1.6 mm)

| Ref | Part | Package | Qty | Source | Status |
|---|---|---|---|---|---|
| U1 | Raytac MDBT50Q-1MV2 (see open item above) | LGA-61, reflow only | 1 | DigiKey 3271-MDBT50Q-1MV2-ND, $6.15; LCSC C5118826 has no stock | Verified |
| U2 | TI BQ24074RGTR | QFN-16 with thermal pad | 1 | LCSC C54313, $1.45 | Verified |
| U3 | DW01A | SOT-23-6 | 1 | LCSC C351410 | Verified |
| Q3 | FS8205A dual N-FET | SOT-23-6 | 1 | LCSC C2830320 | Verified |
| U4 | MAX98357AETE+T | TQFN-16 3×3 with thermal pad | 1 | LCSC C910544, $0.89 | Verified |
| F1 | PPTC, 2.0 A hold, 6 V or higher (e.g. Littelfuse 1812L200) | 1812 | 1 | LCSC | Verify part and code |
| Y1 | 32.768 kHz crystal, 12.5 pF, ±20 ppm | 3215 | 1 | e.g. Epson FC-135R or Seiko SC-32S | Verify part and LCSC code |
| J_BAT | JST B2B-PH-SM4-TB | PH top-entry SMT | 1 | LCSC C160352 | Verified |
| J_USB | JST SM08B-SRSS-TB | SH side-entry SMT | 1 | LCSC | Verify code |
| J_MIC | JST SM04B-SRSS-TB | SH side-entry SMT | 1 | LCSC C160404 | Verified |
| J_LED | JST SM07B-SRSS-TB | SH side-entry SMT | 1 | LCSC | Verify code |
| J_PTT, J_PWR, J_SPK, J_NTC | JST SM02B-SRSS-TB | SH side-entry SMT | 4 | LCSC C160402 | Verified |
| SWD | Tag-Connect TC2030-NL footprint | pads only | 1 | no part | |
| C | 10 µF 10 V X5R | 0603 | 4 | LCSC | VDD, VDDH, BAT, spare |
| C | 22 µF 10 V X5R | 0805 | 2 | LCSC | SYS at charger OUT, amplifier VDD |
| C | 4.7 µF 10 V X5R | 0603 | 1 | LCSC | Module VBUS |
| C | 1 µF 25 V X5R | 0603 | 1 | LCSC | Charger IN |
| C | 100 nF 16 V X7R | 0603 | 8 | LCSC | Decoupling, button RC, reset, DW01A |
| C | 12 pF C0G | 0603 | 2 | LCSC | Crystal load; confirm against Y1 |
| R | 890 Ω 1 % | 0603 | 1 | LCSC | ISET, 1.0 A charge |
| R | 1.33 kΩ 1 % | 0603 | 1 | LCSC | ILIM, 1.2 A input (harness contacts are rated 0.7 A, doubled) |
| R | 71.5 kΩ 1 % | 0603 | 1 | LCSC | TMR |
| R | 620 kΩ 1 % | 0603 | 1 | LCSC | Amplifier SD_MODE |
| R | 100 kΩ | 0603 | 5 | LCSC | Charger pull-downs and pull-ups |
| R | 10 kΩ | 0603 | 3 | LCSC | Button pull-ups, reset pull-up |
| R | 1 kΩ | 0603 | 5 | LCSC | Button series, DW01A CS, red LED series |
| R | 560 Ω | 0603 | 4 | LCSC | Green and blue LED series |
| R | 100 Ω | 0603 | 1 | LCSC | DW01A VCC |
| R | 33 Ω | 0603 | 4 | LCSC | I2S and PDM clock series |
| R | 2.2 Ω | 0603 | 1 | LCSC | Module VBUS series |
| R | 0 Ω | 0603 | 2 | LCSC | USB D+/D− (footprints for 27 Ω) |
| R | unpopulated | 0603 | 2 | | GAIN_SLOT options |
| — | Screws M2 × 5 mm, plastic thread | | 6 | local | PCB mounting; head ≤ 4.5 mm diameter, ≤ 1.8 mm tall |

## 2. USB-C daughterboard (13 × 6.6 × 1.0 mm)

| Ref | Part | Package | Qty | Source | Status |
|---|---|---|---|---|---|
| J1 | GCT USB4105-GF-A-120, 16 contacts, 20,000 cycles, THT shell stakes 1.2 mm | | 1 | LCSC C5184243, $0.53 | Verified; plain -GF-A (C3020560) is out of stock |
| J2 | JST SM08B-SRSS-TB | SH side-entry SMT | 1 | LCSC | Verify code |
| R1, R2 | 5.1 kΩ 1 % | 0603 | 2 | LCSC | Rd; 1 % is required for the CC thresholds |
| D1 | ST USBLC6-2SC6 | SOT-23-6 | 1 | LCSC C7519 | Verified; also clamps VBUS through pin 5 |
| C1 | 1 µF 25 V X5R | 0603 | 1 | LCSC | |

The separate VBUS TVS (ESD441, DFN0603) is dropped: the package cannot be
hand-placed reliably and the USBLC6 covers VBUS. Fallback receptacle if
USB4105 stock disappears: HRO TYPE-C-31-M-12, LCSC C165948, 10,000 cycles.

## 3. Microphone daughterboard (15 × 8 × 1.6 mm)

| Ref | Part | Package | Qty | Source | Status |
|---|---|---|---|---|---|
| U1 | TDK InvenSense T3902, order code MMICT390200012, PDM, bottom port | LGA-5, 3.5 × 2.65 × 0.98 mm | 1 | LCSC C3171752, $1.29 at 10, 8,000 in stock | Verified |
| C1 | 100 nF 10 V X7R | 0603 | 1 | LCSC | At pin 5 (VDD) |
| R1 | 100 Ω | 0603 | 1 | LCSC | In series with DATA |
| J1 | JST SM04B-SRSS-TB | SH side-entry SMT | 1 | LCSC C160404 | Verified |

Pins: 1 DATA, 2 SELECT, 3 GND, 4 CLK, 5 VDD. Supply 1.65–3.63 V from the
module's VDD. Standard-mode clock 1.0–3.3 MHz, so the nRF52840 default
1.032 MHz works; 430 µA running, 12 µA with the clock below 200 kHz. PCB
sound hole 0.5–1.0 mm. Fallback: MEMSensing MSM261DDB019, LCSC C51928210,
same package, but its normal mode starts at 1.1 MHz, so the nRF PDM clock
must be set to 1.280 MHz with Ratio80.

## 4. LED daughterboard (12 × 8 × 1.6 mm)

| Ref | Part | Package | Qty | Source | Status |
|---|---|---|---|---|---|
| D1, D2 | 3 mm common-anode RGB LED, diffused lens, through-hole | 3 mm, 4 leads | 2 | DigiKey or LCSC | Verify part |
| J1 | JST SM07B-SRSS-TB | SH side-entry SMT | 1 | LCSC | Verify code |

## 5. Off-board parts

| Item | Part | Qty | Source | Status |
|---|---|---|---|---|
| Cell | Samsung INR18650-35E, unprotected flat top, 3350 mAh min, 65.25 mm max, Ø18.55 mm max | 1 | batterionline.no, NOK 87.95 | Verified |
| Negative contact | Keystone 5201 coil spring with solder tab | 1 | DigiKey 36-5201-ND, $0.27 | Verified; 72.0 mm compartment with 5223 |
| Positive contact | Keystone 5223 button with solder tab | 1 | DigiKey 36-5223-ND, $0.14 | Verified |
| Cell thermistor | Semitec 103AT-2, 10 kΩ ±1 %, B = 3435 K, leaded bead | 1 | DigiKey (product 16579059) | Verified |
| Cell straps | HellermannTyton T18R cable tie, 100 × 2.5 mm | 2 | TME or Farnell | Verified |
| Speaker | Same Sky CMS-2053-18SP, 20 × 5.3 mm, 8 Ω, 1.5 W, solder pads | 1 | DigiKey 22521372 | Verified; the enclosure now models this depth |
| PTT and power switches | Omron B3F-1000, 6 × 6 × 4.3 mm, 100 gf | 2 | LCSC C93157, $0.17 | Verified |
| Closure screws | M2 × 6 mm, plastic thread | 2 | local | |
| Speaker bridge screws | M2 × 5 mm | 2 | local | |
| Adhesive | 3M VHB or 3M 9448 double-sided tape, 0.15 mm; thin strips for switch, mic and LED boards | shared | local | |
| Speaker gasket | 1 mm closed-cell foam ring, Ø20/Ø18 | 1 | cut from sheet | |
| Filament | PETG for shells and carriers; TPU for button caps | | on hand | |

## 6. Harnesses

Ready-made JST SR harnesses, which mate with the SH headers. They are IDC
assemblies with 30 AWG UL1571 wire (0.55 mm insulation), black only, contacts
rated 0.7 A. Suffix A is JST's "pin 1 to pin 1" wiring; DigiKey labels the
same part "Reversed" because one housing is flipped, so buzz out one cable
before wiring the first board. No crimping is needed; a damaged cable is
replaced, not re-terminated.

| Harness | Part | Qty | Source | Status |
|---|---|---|---|---|
| USB, 8-way, 102 mm | JST A08SR08SR30K102A | 1 | DigiKey, $1.90, 2,220 in stock | Verified |
| LED, 7-way, 102 mm | JST A07SR07SR30K102A | 1 | DigiKey, $1.81, 486 in stock | Verified |
| Mic, 4-way, 152 mm | JST A04SR04SR30K152A (102 mm is out of stock) | 1 | DigiKey, $1.53 | Verified |
| PWR, PTT, SPK, NTC: 2-way, 152 mm, cut in half, cut end soldered to the switch, speaker or thermistor | JST A02SR02SR30K152A | 2 | DigiKey | Verify code (102 mm A02SR02SR30K102A is verified at $1.12) |
| BAT+ and BAT−, PH 2-way plug, 24 AWG | JST ASPHSPH24K305, cut to 65 and 165 mm, cut ends soldered to the contact tabs | 1 | DigiKey 455-3082-ND, $0.50 | Verified |
| PH housing 2-way | JST PHR-2 | 1 | LCSC C157955 | Verified |
| PH contact | JST SPH-002T-P0.5S | 2 | LCSC C111515 | Verified |
| Heat-shrink 1.5 mm and 3 mm | for pin-1 marking and the NTC joints | | local | |

Cut lengths follow `pcb/DESIGN.md`. If a cable must be re-terminated after
all, the SH crimp contact is SSH-003T-P0.2-H (LCSC C263995) with an Engineer
PAD-11 crimper; the PA-09 does not fit SH contacts.

## 7. Tools and consumables

| Item | Note |
|---|---|
| Hot plate, 100 mm PTC type | The 30 mm MHP30 cannot cover a 126 mm board |
| Solder paste Sn42Bi58 (138 °C) in a syringe | Low-temperature paste keeps the plate and the parts cool; store refrigerated |
| Stencils from JLCPCB, one per board type | Frameless, order with the boards; the LED board needs none |
| Flux pen or gel, isopropanol, lint-free wipes | |
| Fine tweezers, USB microscope or 10× loupe | The module and QFN pads cannot be checked by eye |
| Temperature-controlled iron, 0.6 mm chisel tip | Through-hole LEDs, contacts, switches, wire ends |
| SWD probe with Tag-Connect TC2030-IDC-NL cable | First bootloader flash and recovery |
| Bench supply with current limit, USB current meter | Bench checks in `pcb/DESIGN.md` |

## 8. Ordering plan for ten sets

From `docs/research/2026-09-13-pcba-cost.md` section 10. Estimates, not
quotes; VAT is collected at checkout by JLCPCB and DigiKey when a parcel is
under NOK 3 000, which all of these are.

| Order | Contents | USD incl. VAT | NOK |
|---|---|---|---|
| JLCPCB | Main board 10 pcs 4-layer; USB, mic and LED boards 10 pcs each as three separate 2-layer orders (the mic and LED boards are under JLCPCB's 10 mm minimum edge and get a rail); three stencils | 163 | 1 500 |
| LCSC | Every section 1–4 part for 12 sets except the module | 196 | 1 800 |
| DigiKey | 12 modules, 10 sets of contacts, thermistors, harnesses, speakers | 101 for modules plus about 250 for the rest | 940 plus about 2 300 |
| batterionline.no | 10 cells | about 95 | 880 |
| One-time reflow kit | section 7 | 155 | 1 430 |

Boards and parts come to about NOK 425 per set before off-board parts. Buy
two spare modules beyond the ten; a reflowed module cannot be reworked.

## 9. Decisions this list depends on

Settled: no external 3.3 V regulator; DW01A protection with PPTC; 1.0 A
charge with a 1.2 A input limit; Keystone 5201/5223 contacts and a 72 mm
cradle; CMS-2053-18SP speaker; 8-way USB harness with CC sensing; hand
assembly of bare boards; schematic capture in tscircuit. Open: the radio
module (castellated alternative under research).
