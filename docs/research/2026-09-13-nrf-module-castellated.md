# nRF52840 module, iron-solderable (edge castellations only)

Research date: 2026-09-13. Every claim is tagged VERIFIED (with source) or UNVERIFIED.

## Verdict

**Recommend: MinewSemi MS88SF2 (nRF52840), PCB-antenna SKU `MS88SF2-1Y40AIR`.**
**Fallback: Ebyte E73-2G4M08S1C (LCSC C356849)** — cheaper and in stock, but it is a
dual-row hybrid (28 castellations + 15 bottom-only pads), so it only qualifies if you
accept leaving the inner pads to reflow/stencil.

No nRF52840 module found meets *every* stated requirement. MS88SF2 fails exactly one:
it has **no VBUS pad** (VBUS is bonded to VDDH inside the module). Everything else passes.

---

## F1 — MS88SF2 (recommended)

| Item | Value | Status |
|---|---|---|
| Chip | Nordic nRF52840 | VERIFIED — datasheet |
| Size | 23.2 × 17.4 × 2.0 mm (width 17.4 ≤ 22 mm) | VERIFIED — datasheet §7 mech. drawing |
| Pad style | 28 edge castellations, single row on each long edge. **No bottom-only pads, no centre/thermal pad.** | VERIFIED — mech. drawing + KiCad fp |
| Pitch | **1.10 mm** | VERIFIED — drawing dim + KiCad footprint pad coords |
| Land pattern | 2.0 × 0.8 mm pads (datasheet recommends 1.8 × 0.8 mm, extend 0.5 mm outward) → 0.3 mm gap | VERIFIED |
| Antenna | PCB trace antenna (`-1Y40AIR`) or U.FL (`-3Y40AIR`) | VERIFIED — DigiKey attrs |
| Antenna keep-out | Documented: ≥4 mm clear area, no copper under antenna, place on board edge | VERIFIED — datasheet §"PCB LAYOUT" |
| 32 MHz XO | Yes, onboard | VERIFIED — schematic |
| 32.768 kHz XO | Yes — Y2 on P0.00/P0.01 (that is why those pins are not on pads) | VERIFIED — datasheet §8 schematic |
| VDDH mode | Native. DCCH→VDDH inductor (L5) and caps are onboard; VDDH rated 2.5–5.5 V | VERIFIED — datasheet schematic + pin table |
| FCC | FCC ID **2ABU6-MS88SF2** | VERIFIED — datasheet header |
| CE / IC / Telec | Datasheet has a "CERTIFICATION" logo block; individual marks not machine-readable | UNVERIFIED |

### Pinout (all 28 pads, confirmed twice)

Source 1: MinewSemi MS88SF2 datasheet §5 Pin Definition + §8 schematic symbol J1.
Source 2: open-source breakout `atoomnetmarc/Minew-MS88SF2-breakout`, KiCad footprint
`RF_Module-extra:MS88SF2-handsolder` — 28 pads at x = ±8.5 mm, y step 1.10 mm, size 2.0 × 0.8 mm.

| Pad | Net | Pad | Net |
|---|---|---|---|
| 1 | GND | 15 | **VDDH** |
| 2 | P1.13 | 16 | **D-** |
| 3 | P1.15 | 17 | **D+** |
| 4 | **P0.02** (AIN0) | 18 | P0.13 |
| 5 | P0.29 (AIN5) | 19 | P0.15 |
| 6 | P0.31 (AIN7) | 20 | **P0.18 / nRESET** |
| 7 | **P0.26** | 21 | P0.20 |
| 8 | **P0.04** (AIN2) | 22 | P0.22 |
| 9 | **P0.06** | 23 | P0.24 |
| 10 | **P0.08** | 24 | P1.00 (SWO) |
| 11 | P1.09 | 25 | **SWDIO** |
| 12 | P0.12 | 26 | **SWCLK** |
| 13 | GND | 27 | P0.09 / NFC1 |
| 14 | VDD | 28 | P0.10 / NFC2 |

20 GPIO total (matches datasheet "Quantity of IO Port: 20").

### Requirement check

| Requirement | Result |
|---|---|
| BLE / nRF52840 | PASS |
| D+ / D- pads | PASS (17 / 16) |
| VBUS pad | **FAIL** — no pad. See R1. |
| SWDIO / SWCLK | PASS (25 / 26) |
| nRESET / P0.18 | PASS (20) |
| P0.02 | PASS |
| P0.03 | **FAIL — not exposed** |
| P0.04 | PASS |
| P0.05 | **FAIL — not exposed** |
| P0.06 | PASS |
| P0.07 | **FAIL — not exposed** |
| P0.08 | PASS |
| P0.26 | PASS |
| P0.27 | **FAIL — not exposed** |
| ≥6 further GPIO | PASS — 11 spare: P0.09, P0.10, P0.12, P0.13, P0.15, P0.20, P0.22, P0.24, P0.29, P0.31, P1.00, P1.09, P1.13, P1.15 (14 actually) |
| VDDH pad | PASS |
| Width ≤ 22 mm | PASS (17.4 mm) |
| On-module antenna + keep-out | PASS |
| Pitch ≥ 1.0 mm | PASS (1.10 mm; 1.27 mm preferred not met) |
| 32 MHz XO | PASS |
| 32.768 kHz XO | PASS |
| Open bootloader | PASS (see F6) |
| In stock | PASS — DigiKey Marketplace |

### R1 — the VBUS issue and how to live with it

MS88SF2 has no VBUS pad. The datasheet §8 config table lists
"Config 1: USB (VDDH = VBUS), R2 CONN" — an internal resistor bonds VBUS to VDDH.
The open-source breakout's changelog independently confirms the workaround:
*"V1.1 — Attached VDDH to VBUS to enable USB to work"*, and its checklist marks **USB working**.
(VERIFIED — https://github.com/atoomnetmarc/Minew-MS88SF2-breakout README)

Design consequence: the nRF52840 USB regulator needs VBUS ≥ 4.35 V, so **USB device mode only
works when VDDH itself is at USB-level voltage**. You must OR raw USB 5 V into VDDH (Schottky
or ideal-diode gives ~4.6–4.8 V — above the 4.35 V floor) alongside the Li-ion cell.
On battery alone (3.0–4.2 V on VDDH) the USB peripheral will not enumerate — acceptable for a
handheld that only needs USB while plugged in.
Do **not** feed VDDH from a charger SYS node that clamps at ~4.4 V; that is marginal.

UNVERIFIED: whether the DigiKey-stocked `-1Y40AIR` SKU ships with R2 populated (Config 1).
The datasheet says "confirm the specific configuration required with the salesperson".
Confirm with MinewSemi before committing.

### Availability and price

| Source | P/N | Stock | Price |
|---|---|---|---|
| DigiKey Marketplace (BE) | MS88SF2-3Y40AIR (U.FL) | 1,919 | €6.42 @1, €6.38 @25 |
| DigiKey Marketplace (IN) | **MS88SF2-1Y40AIR (PCB ant)** | 1,064 | ₹716.63 @1, ₹707.07 @25 (≈ US$8.1 / €6.45) |
| DigiKey US | MS88SF2-3Y40AIR | in stock | $7.50 @1, $7.45 @25 |
| JLCPCB parts library | C20616655 / C2836129 | assembly only | not shippable as loose parts |
| LCSC | — | **no loose-part listing** | n/a |

Price at 10: no qty-10 break published; the @1 price applies → **≈ €6.45 / US$7.50 each**.
Marketplace item — ships from MinewSemi in ~7–9 days, 2,000/30 days purchase cap.
VERIFIED — DigiKey product pages (25935931, 26409781, 25935947).

---

## F2 — Ebyte E73-2G4M08S1C (fallback)

- 13.0 × 18.0 × 3.0 mm, ceramic antenna, 32 MHz XO. VERIFIED — Ebyte user manual §2/§3.
- **43 pads: 28 edge castellations at 1.27 mm pitch + 15 bottom-only 0.8 × 0.8 mm pads.**
  The mechanical drawing's bottom view shows both a castellation land (1.00 × 0.65/0.80)
  and a separate 0.80 × 0.80 square pad, with odd pins on the edge and even pins inboard on
  the top and left sides. VERIFIED — user manual §3 drawing, "Pad quantity: 43".
  → **Does not meet "all pads are edge castellations".**
- No 32.768 kHz crystal. XL1/XL2 (P0.00/P0.01) are broken out as pads 11/13 for an external one.
  VERIFIED — pin table + "Crystal Oscillator: 32MHz".
- On castellations (usable with an iron): P1.11, P1.10, P0.03, P0.28, GND, P1.13, P0.02,
  P0.29, P0.31, P0.30, XL1, XL2, P0.05, P1.09, VDD, GND, **VDDH**, DCCH, **P0.18/RESET**,
  **VBUS**, **D-**, **D+**, P0.13, P0.24, **SWDIO**, **SWDCLK**, P0.09/NFC1, P0.10/NFC2.
- On inner bottom-only pads (need stencil/hot air): **P0.26, P0.06, P0.08, P0.04, P0.07**,
  P0.12, P0.15, P0.17, P0.20, P0.22, P1.00, P1.02, P1.04, P1.06, GND.
- Price/stock: **US$5.5188, in stock, LCSC C356849**; JLCPCB C356849, SMT-assembly capable,
  X-ray inspection required. VERIFIED — LCSC/JLCPCB listings.
- Bootloader: Adafruit nRF52 UF2 runs on it via the stock `pca10056` build, or the nRFMicro
  patched build; community boards exist (`ddB0515/nRF52840-BBoard`, joric/nrfmicro).
  VERIFIED — nrfmicro wiki, BBoard repo.
- Certifications: UNVERIFIED (not in the 2018 user manual I read).
- Variant note: `E73-2G4M08S1CX` is the same schematic with an IPEX antenna (UNVERIFIED
  beyond the nrfmicro wiki's "IDENTICAL" claim). `E73-2G4M08S1E` is **nRF52833**, not 52840
  (VERIFIED — cdebyte product page), so it is out.

---

## F3 — Candidates evaluated and rejected

| Module | Size | Pads | Pitch | Why rejected |
|---|---|---|---|---|
| Raytac MDBT50Q-1MV2 / -P1MV2 | 15.5 × 10.5 × 2.05 | 61: edge + **2 inner rows** (pins 19–29, 56–61) | ~0.8 mm | Under-pads. Adafruit's own product page: "uses under-pads instead of castellated pads, so you cannot hand-solder it". VERIFIED — Raytac datasheet §2.1, adafruit.com/product/4078 |
| Minew MS88SF3 | 18.5 × 12.5 × 2.0 | 64 castellations + **centre GND pad 1.8 × 1.3 mm** | **0.65 mm** | Pitch far below 1.0 mm; centre pad needs reflow. Has VBUS pad (35) and full P0.02–P1.09. LCSC C20416747 **out of stock**, $2.37@1 / $0.95@200. VERIFIED — datasheet §4/§5 |
| Minew MS88SFA / MS88SFB | 23.2 × 17.4 × 2.0 | 1.1 mm castellations **plus an inner bottom row** | 1.1 mm | Inner pad row; PA/LNA (+20 dBm) raises current and adds VCC_PA. Does have a real VBUS pad. VERIFIED — MS88SFA spec §4/§6 |
| Fanstel BT840 / BT840F / BT840E / BT840X / BM840 / BT40 | 14×16 to 15×20.8 | **16 castellated + 45 LGA** | — | Hybrid; only 16 pins reachable with an iron, not enough. VERIFIED — Fanstel BT840 datasheet, fanstel.com/bt840, /bm840 |
| Fanstel BC840 / BC840M / BC840E | 7.1×9.2 to 10.1×12.2 | not stated | — | Too small for the pin count; pad style not documented on the product page. UNVERIFIED |
| Holyiot-18010 (= Waveshare Core52840) | 18 × 13.5 × 1.6 | 55, JLCPCB package `LCC-LGA-55_18X13.5X1.1P` | 1.1 mm | Castellations **plus internal pads**. The ADM_52840 breakout README: "soldering requires a stencil to solder all the pads … since internal pads are routed using vias, it's possible to solder them all with a good soldering iron" — i.e. only via a breakout trick, not beginner-friendly. Core52840 is **out of stock** at LCSC (C5374678) at **$11.63 @10**. VERIFIED — JLCPCB C9900042076, LCSC, github.com/Atelier-Du-Maker/ADM_52840 |
| Holyiot YJ-17103 / YJ-17095 | — | — | — | **These are nRF52832, not nRF52840.** VERIFIED — Zephyr board docs for yj17095, rarecomponents YJ-17095-nRF52832 datasheet |
| u-blox NINA-B40 (B406) | 10 × 14 | multi-row | outer 1.00 / inner 1.10 / central 1.15 mm | Datasheet §"pad dimensions" explicitly lists *inner row* and *central* pin pitches → LGA-style underside pads. VERIFIED — UBX-19049405 |
| Ezurio/Laird BL654 | 10 × 15 | — | — | Hybrid castellated+LGA; ~$16. UNVERIFIED on pad detail; priced out anyway |
| Panasonic PAN1780 | 15 × 10 × 2.2 | — | — | Datasheet fetch timed out; pad style UNVERIFIED |
| RAK4630 / RAK4631 (WisDuo) | 23 × 15 × 3 | 44, castellated edge | not stated | **No on-module antenna** (RF_BT is a bare pin); no P0.06/P0.07/P0.08/P0.27; carries an unwanted SX1262 LoRa radio and its cost. Does expose VBUS, USB+, USB-, SWD, NRF_RESET, P0.02–P0.05, P0.26. VERIFIED — RAK datasheet |
| Skylab SKB501 | 13.7 × 14.7 | — | — | "No USB on module" per nrfmicro wiki. UNVERIFIED further |
| Seeed XIAO nRF52840 | 21 × 17.5 | 14 castellated @2.54 mm + bottom pads | 2.54 mm | **D+/D- are NOT exposed** — the USB-C connector is on the board. No VDDH pad. Only 11 digital I/O. Seeed's own docs list a separate "Bottom Pad Data" file, i.e. there are bottom pads. CONFIRMED REJECTED — wiki.seeedstudio.com/XIAO_BLE |
| Nordic nRF52840 Dongle (PCA10059) | 17.8 × 33 | castellated edge | 2.54 mm | Only 15 GPIO on castellations; no D+/D-, no VDDH, no VBUS pad (USB-A plug is on the board). VERIFIED — nordicsemi.com dongle page |
| nice!nano v2 / SuperMini nRF52840 | ~18 × 33 | castellated only, 2.54 mm | 2.54 mm | Easiest to solder and native Adafruit UF2, but no D+/D-, no VBUS, no VDDH pads — the USB-C and regulator are on-board. Only viable if you drop those three requirements and let the module own the USB port. UNVERIFIED on exact pad list |

---

## F4 — What changes vs the MDBT50Q-1MV2 pad allocation

MDBT50Q-1MV2 exposes essentially the whole chip (P0.00–P0.31, P1.00–P1.15, VDD, VDDH,
DCCH, VBUS, D+, D-, SWDIO, SWDCLK) across 61 pads. VERIFIED — Raytac datasheet §2.1.
Full MDBT50Q-1MV2 map, for reference:

- Left edge: 1 GND, 2 GND, 3 P1.10, 4 P1.11, 5 P1.12, 6 P1.13, 7 P1.14, 8 P1.15, 9 P0.03,
  10 P0.29, 11 P0.02, 12 P0.31, 13 P0.28, 14 P0.30
- Bottom edge: 15 GND, 16 P0.27, 17 P0.00/XL1, 18 P0.01/XL2, 20 P0.04, 22 P0.06, 24 P0.08,
  26 P1.09, 28 VDD, 30 VDDH, 31 DCCH, 32 VBUS, 33 GND
- Bottom **inner** row: 19 P0.26, 21 P0.05, 23 P0.07, 25 P1.08, 27 P0.11, 29 P0.12
- Right edge: 34 D-, 35 D+, 36 P0.14, 37 P0.13, 38 P0.16, 39 P0.15, 40 P0.18/RESET, 41 P0.17,
  42 P0.19, 43 P0.21, 44 P0.20, 45 P0.23, 46 P0.22, 47 P1.00, 48 P0.24, 49 P0.25, 50 P1.02,
  51 SWDIO, 52 P0.09/NFC1, 53 SWDCLK, 54 P0.10/NFC2, 55 GND
- Top **inner** row: 56 P1.04, 57 P1.06, 58 P1.07, 59 P1.05, 60 P1.03, 61 P1.01

(Note that P0.26, P0.05 and P0.07 are *already* inner-row pads on the MDBT50Q — so three of
the nine signals you listed are not iron-solderable on the current module either.)

Forced changes when moving to MS88SF2:

| Signal currently on | Action |
|---|---|
| **P0.03** | Remap. If it was an ADC input, use **P0.29 (AIN5)** or **P0.31 (AIN7)**. |
| **P0.05** | Remap. Digital → any spare; analog → P0.29/P0.31. |
| **P0.07** | Remap to any spare digital: P0.12, P0.13, P0.15, P0.20, P0.22, P0.24, P1.09, P1.13, P1.15. |
| **P0.27** | Remap to any spare digital (same list). |
| **VBUS pin** | Delete the net. Route USB 5 V (via Schottky/ideal diode, OR'd with the cell) into **VDDH** instead. See R1. |
| **DCCH** | Delete. The high-voltage DC/DC inductor is inside the MS88SF2; no external L needed. |
| **P0.00 / P0.01 (XL1/XL2)** | Delete any external 32.768 kHz crystal — it is on the module. |
| Anything on P1.01–P1.08, P1.10–P1.12, P1.14, P0.11, P0.14, P0.16, P0.17, P0.19, P0.21, P0.23, P0.25, P0.28, P0.30 | Not available. Remap. |

Analog budget shrinks from 8 AIN channels to 4: **AIN0 = P0.02, AIN2 = P0.04, AIN5 = P0.29,
AIN7 = P0.31**. Plan battery sense and any other ADC around those.

Two pins need UICR changes if you want them as plain GPIO:
- **P0.18** — used as nRESET by default; set `UICR.PSELRESET` to disable.
- **P0.09 / P0.10** — NFC antenna pins by default; set `UICR.NFCPINS` = Disabled.
(VERIFIED — standard nRF52840 behaviour, Nordic product spec.)

Board fit: 23.2 × 17.4 mm on a 26 × 126 mm board leaves 4.3 mm total lateral clearance
(2.15 mm/side if centred). The 4 mm antenna keep-out means the module must sit at one end of
the board with the antenna facing the board edge, and no ground pour under or beside it.
That is tighter than the MDBT50Q's 10.5 mm width — plan the LED/mic/speaker placement around it.

## F5 — Nothing simultaneously satisfies all constraints

Searched: Ebyte, CDEbyte, Holyiot, Minew/MinewSemi, Fanstel, Raytac, u-blox, Ezurio/Laird,
Panasonic, RAKwireless, Waveshare, Skylab, Seeed, Nordic first-party. Across that set, modules
divide into three groups:
1. Fine-pitch LGA/hybrid with full pin breakout (MDBT50Q, Holyiot 18010, NINA-B4, Fanstel, MS88SF3).
2. Coarse-pitch castellated boards with the USB port already on them (XIAO, nice!nano, Dongle) —
   so no D+/D-/VBUS/VDDH pads.
3. MS88SF2 — the only one with a genuine single-row ≥1.0 mm castellation-only footprint, a
   PCB antenna, both crystals and a VDDH pad. Its single gap is the missing VBUS pad.

## F6 — Bootloader

- The Adafruit nRF52 UF2 bootloader is board-agnostic for the nRF52840; the stock **`pca10056`**
  build runs on any module, with double-tap-reset entering UF2 mass-storage mode.
  VERIFIED — github.com/adafruit/Adafruit_nRF52_Bootloader README, nrfmicro wiki "Bootloader".
- **No dedicated MS88SF2 board definition exists** in the Adafruit bootloader, CircuitPython, or
  Zephyr trees (UNVERIFIED as an exhaustive claim — none surfaced in search). You will add a
  small board variant of your own: LED pins, button pin, and the `pca10056` USB/clock config
  (LFXO present, so keep `CLOCK_LFCLKSRC = Xtal`).
- Adjacent precedents you can copy: `nice_nano_v2`, `AtelierDuMaker nRF52840 Breakout`
  (CircuitPython, targets Holyiot 18010 and works unmodified on Waveshare Core52840 —
  VERIFIED, mateusznowak.dev article), and the E73-based `nRF52840-BBoard`.

## Sources

- MinewSemi MS88SF2 datasheet — https://en.minewsemi.com/file/MS88SF2-nRF52840_Datasheet_M_EN.pdf
- MinewSemi MS88SF2-3Y40AIR (DigiKey copy) — https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6679/MS88SF2-3Y40AIR.pdf
- DigiKey MS88SF2-1Y40AIR — https://www.digikey.in/en/products/detail/minewsemi/MS88SF2-1Y40AIR/25935931
- DigiKey MS88SF2-3Y40AIR — https://www.digikey.be/en/products/detail/minewsemi/MS88SF2-3Y40AIR/26409781
- MS88SF2 open-source breakout (footprint + USB/VDDH finding) — https://github.com/atoomnetmarc/Minew-MS88SF2-breakout
- MinewSemi MS88SF3 datasheet — https://store.minewsemi.com/wp-content/uploads/2024/03/MS88SF3-nRF52840_Datasheet_K_EN.pdf
- MinewSemi MS88SFA spec — https://en.minewsemi.com/file/MS88SFA-nRF52840-Specification-K-MinewSemi.pdf
- Ebyte E73-2G4M08S1C user manual — https://www.cdebyte.com/pdf-down.aspx?id=560
- Ebyte E73-2G4M08S1E product page (nRF52833) — https://www.cdebyte.com/products/E73-2G4M08S1E
- LCSC E73-2G4M08S1C C356849 — https://www.lcsc.com/product-detail/Bluetooth-Modules_Chengdu-Ebyte-Elec-Tech-E73-2G4M08S1C_C356849.html
- JLCPCB E73-2G4M08S1C — https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E732G4M08S1C/C356849
- JLCPCB MS88SF2 — https://jlcpcb.com/partdetail/Minew-MS88SF2nRF52840/C20616655 and /MINEW-MS88SF2/C2836129
- Raytac MDBT50Q-1MV2 & P1MV2 datasheet — https://www.lcsc.com/datasheet/lcsc_datasheet_2411121137_RAYTAC-MDBT50Q-P1MV2_C5119772.pdf
- Adafruit MDBT50Q-1MV2 product page ("cannot hand-solder") — https://www.adafruit.com/product/4078
- Fanstel BT840 series — https://www.fanstel.com/bt840 and https://www.cdiweb.com/datasheets/fanstel/bluenor_bt840_f_e_x_xe_datasheets.pdf
- u-blox NINA-B40 datasheet — https://content.u-blox.com/sites/default/files/NINA-B40_DataSheet_UBX-19049405.pdf
- RAK4630 datasheet — https://docs.rakwireless.com/product-categories/wisduo/rak4630-module/datasheet/
- Holyiot 18010 / JLCPCB — https://jlcpcb.com/partdetail/6213453-Holyiot_18010NRF52840/C9900042076
- ADM_52840 breakout (Holyiot 18010 internal pads) — https://github.com/Atelier-Du-Maker/ADM_52840
- Waveshare Core52840 bootloader write-up — https://mateusznowak.dev/articles/installing-bootloader-circuitpython-core52840/
- Zephyr YJ-17095 board (nRF52832) — https://docs.zephyrproject.org/latest/boards/holyiot/yj17095/doc/index.html
- Seeed XIAO nRF52840 wiki — https://wiki.seeedstudio.com/XIAO_BLE/
- joric/nrfmicro module survey — https://github.com/joric/nrfmicro/wiki/Modules
- Adafruit nRF52 bootloader — https://github.com/adafruit/Adafruit_nRF52_Bootloader
