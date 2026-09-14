# Audio / LED / Switch parts research

Target system: nRF52840, 3.3 V logic rail, Li-ion system rail 2.9–4.4 V.
Date: 2026-09-13. Every fact tagged VERIFIED (with source) or UNVERIFIED.

Primary datasheets were downloaded and text-extracted locally with `pdftotext`;
quoted values are read from the datasheet text, not from summaries.

---

## 1. MAX98357A (TQFN-16, 3×3 mm)

Source: MAX98357A/MAX98357B datasheet, Maxim Integrated (rev. as hosted by Adafruit),
<https://cdn-shop.adafruit.com/product-files/3006/MAX98357A-MAX98357B.pdf>

### 1.1 Pin map — VERIFIED, proposed map is correct

Datasheet "Pin Description" table, TQFN column:

| Pin | Name      |
|-----|-----------|
| 1   | DIN       |
| 2   | GAIN_SLOT |
| 3   | GND       |
| 4   | SD_MODE   |
| 5   | N.C.      |
| 6   | N.C.      |
| 7   | VDD       |
| 8   | VDD       |
| 9   | OUTP      |
| 10  | OUTN      |
| 11  | GND       |
| 12  | N.C.      |
| 13  | N.C.      |
| 14  | LRCLK     |
| 15  | GND       |
| 16  | BCLK      |

The proposed map matches on every pin number. Two corrections of naming/intent:

- **Pin 2 is `GAIN_SLOT`**, not `GAIN`. In I2S/left-justified mode it sets gain (Table 8);
  in TDM mode it is a channel-select input and gain is fixed at 12 dB.
- **The exposed pad is NOT internally connected to GND.** Datasheet, verbatim:
  "Exposed Pad. The exposed pad is not internally connected. Connect the exposed p[ad] to a
  solid ground plane for thermal dissipation." Connect it to the ground plane for thermal
  reasons; do not rely on it as the electrical ground return — pins 3, 11 and 15 are the
  ground connections.

### 1.2 SD_MODE — channel select and MCU shutdown (VERIFIED)

SD_MODE has an internal pulldown `RPD` = 100 kΩ ±8 % (92–108 kΩ). An external pullup
resistor from the driving logic rail forms a divider against it; the resulting voltage picks
the mode.

Table 5, SD_MODE Control:

| SD_MODE drive              | Condition                          | Selected channel  |
|----------------------------|------------------------------------|-------------------|
| High                       | V(SD_MODE) > B2 trip point         | Left              |
| Pullup through `RSMALL`    | B2 > V(SD_MODE) > B1               | Right             |
| Pullup through `RLARGE`    | B1 > V(SD_MODE) > B0               | (Left/2 + Right/2)|
| Low                        | B0 > V(SD_MODE)                    | Shutdown          |

Comparator trip points (typ): B2 = 1.4 V, B1 = 0.77 V, B0 = 0.16 V.

Resistor formulas (VDDIO = the logic voltage driving SD_MODE):

```
RSMALL (kΩ) = 94.0  × VDDIO − 100
RLARGE (kΩ) = 222.2 × VDDIO − 100
```

Table 6, worked examples:

| VDDIO (V) | RSMALL (kΩ) | RLARGE (kΩ) |
|-----------|-------------|-------------|
| 1.8       | 69.8        | 300         |
| 3.3       | 210.2       | 634         |

### 1.3 Recommended circuit for this design (mono mix + MCU shutdown)

For **(L+R)/2 mono** with 3.3 V nRF52840 GPIO, push-pull drive (datasheet Figure 5):

```
nRF52840 GPIO ──[ 634 kΩ ]──┬── SD_MODE (pin 4)
                            │
                      (internal 100 kΩ pulldown to GND)
```

- GPIO **high (3.3 V)** → V(SD_MODE) ≈ 3.3 × 100/(100+634) ≈ 0.45 V → between B0 (0.16 V)
  and B1 (0.77 V) → **(L/2 + R/2) mono output**.
- GPIO **low (0 V)** → SD_MODE pulled to 0 V by the internal pulldown → **shutdown**.

So one GPIO gives both the mono mix and the shutdown control, exactly as the task described.
Use the nearest E96 value, 634 kΩ (or 649 kΩ / 619 kΩ — the divider has wide margin between
0.16 V and 0.77 V).

For **Left** channel instead: drive SD_MODE directly high from the GPIO (no resistor).
For **Right** channel: use 210 kΩ instead of 634 kΩ.

**Li-ion caveat that does NOT apply here (VERIFIED):** the datasheet warns that if
VDD < 3.0 V while VDDIO = 3.3 V, SD_MODE can violate Absolute Maximum Ratings, and advises a
~2 kΩ series resistor to limit current. It then states this "is not a concern when using the
right channel or (left/2 + right/2) modes." Since this design runs (L+R)/2 through a 634 kΩ
resistor, no extra series resistor is needed even when the cell sags to 2.9 V.

### 1.4 GAIN_SLOT gain table (VERIFIED)

Table 8, Gain Selection (I2S / left-justified mode):

| GAIN_SLOT connection              | Gain (dB) |
|-----------------------------------|-----------|
| To GND through 100 kΩ ±5 %        | 15        |
| To GND (direct)                   | 12        |
| Unconnected (floating)            | 9         |
| To VDD (direct)                   | 6         |
| To VDD through 100 kΩ ±5 %        | 3         |

Note the default: **leaving the pin floating gives 9 dB**. The gain is set by pin state and/or
a 100 kΩ resistor — there is no continuous resistor-programmed range.

Output level relation: `output (dBV) = input (dBFS) + 2.1 dB + selected gain (dB)`.
In TDM mode gain is fixed at 12 dB and GAIN_SLOT becomes a channel selector.

### 1.5 Supply, decoupling, current (VERIFIED)

- **VDD operating range: 2.5 V to 5.5 V.** Covers the full 2.9–4.4 V Li-ion rail with margin.
- UVLO: 1.4 V min / 1.8 V typ / 2.3 V max.
- **Decoupling, verbatim:** "Bypass VDD with a 0.1 µF and 10 µF capacitor to GND. Some
  applications might require only the 10 µF bypass capacitor... Apply additional bulk
  capacitance at the ICs if long input traces between VDD and the power source are used."
  → Use **10 µF ceramic + 100 nF ceramic** at the pins. For a Li-ion rail feeding a class-D
  amp with 200–500 mA speaker peaks, add extra bulk (e.g. 47–100 µF) near the amp; the
  datasheet endorses "additional bulk capacitance" but does not name a value (that specific
  value is UNVERIFIED).
- **Quiescent current:** 2.75 mA typ / 3.35 mA max at 5 V; **2.4 mA typ / 2.85 mA max at
  VDD = 3.7 V**.
- **Shutdown current `ISHDN` (SD_MODE = 0 V, 25 °C): 0.6 µA typ, 2 µA max.**
- **Standby current `ISTNDBY` (SD_MODE = 1.8 V, no BCLK, 25 °C): 340 µA typ, 400 µA max.**
  Standby is entered automatically when clocks stop. For a multi-day battery budget, pull
  SD_MODE low (0.6 µA) rather than relying on clock-stop standby (340 µA) — a ~570× difference.
- Turn-on time 7 ms typ / 7.5 ms max.
- Speaker current limit 2.8 A typ.

### 1.6 Output filtering for a short speaker cable (VERIFIED — no filter is specified)

The MAX98357A is a **filterless** class-D design and the datasheet specifies **no output
filter, no ferrite beads and no output capacitors**:

- "The ICs' filterless modulation scheme does not require an output filter. The device relies
  on the inherent inductance of the speaker coil and the natural filtering of both the speaker
  and the human ear."
- Figure 14 is captioned "EMI with 12in of Speaker Cable and No Output Filtering" — i.e. the
  datasheet's own EMI evidence is taken with ~305 mm of unfiltered speaker cable, which is
  longer than anything inside a 150 mm handheld.
- Spread-spectrum modulation varies the 330 kHz switching frequency by ±20 kHz; above 10 MHz
  the spectrum "looks like noise for EMI purposes."

Requirements the datasheet **does** state:

- **Speaker series inductance > 10 µH.** "Typical 8 Ω speakers exhibit series inductances in
  the 20 µH to 100 µH range." Check this if you substitute an unusual driver.
- Use **wide, low-resistance output traces**; trace resistance directly subtracts power.
- **Minimise parasitic capacitance on the output traces** — it costs quiescent current at
  `VDD × 330 kHz × C_parasitic` (datasheet example: 100 pF at 5 V adds 165 µA). On a
  battery device, keep OUTP/OUTN traces short and do not pour ground under them.
- Add ground fills around signal traces on top/bottom planes for RF immunity.

**UNVERIFIED:** any specific ferrite bead or output capacitor part/value. The datasheet does
not recommend one, and adding an LC/bead filter on a filterless class-D output can degrade
THD+N. If EMC testing later demands it, the usual remedy is a small bead (e.g. 600 Ω @ 100 MHz)
plus ~1 nF to ground on each output, but that is general practice, not a datasheet recommendation.

### 1.7 Sourcing (VERIFIED)

| Item | Value |
|---|---|
| MPN | MAX98357AETE+T (tape & reel) / MAX98357AETE+ (tube) |
| Package | TQFN-16-EP (3×3) |
| **LCSC** | **C910544** — 15,758 in stock |
| LCSC price | $1.3255 @1 · $1.1615 @10 · $1.0056 @30 · $0.8891 @100 · $0.8416 @500 · $0.817 @1k |
| **JLCPCB** | **Extended part**, JLCPCB #C910544, assembly supported, **Economic and Standard PCBA**, MSL 1 |

Sources: <https://www.lcsc.com/product-detail/C910544.html>,
<https://jlcpcb.com/partdetail/MaximIntegrated-MAX98357AETET/C910544>

Note: a separate JLCPCB listing exists under Analog Devices branding as C20745475
(<https://jlcpcb.com/partdetail/ANALOG_DEVICESINC-MAX98357AETET/C20745475>) — same MPN,
different internal part record. Prefer C910544, which has confirmed stock and pricing.

### 1.8 Cheaper alternative at LCSC (VERIFIED part, NOT pin-compatible)

**Nsiway NS4168** — LCSC **C910588**.

| Item | Value |
|---|---|
| Package | **ESOP-8-EP (3.9×4.9×1.27 mm)** — 8 pins, *not* pin-compatible with the TQFN-16 |
| Function | Mono class-D, I2S digital input, integrated DAC, filterless, 2.5 W |
| Supply | 3.0–5.5 V (covers the Li-ion rail) |
| Channel select | `CTRL` pin logic level (L/R) |
| Protection | Overcurrent, overtemperature, undervoltage |
| Specs | 80 % efficiency, 85 dB SNR, 0.2 % THD+N, 8 kHz–96 kHz sample rates |
| Stock | 8,068 |
| Price | $0.744 @1 · $0.6077 @10 · **$0.4714 @100** · $0.3827 @1k |

Source: <https://www.lcsc.com/product-detail/C910588.html>

It is **functionally equivalent** (mono I2S class-D amp) at roughly half the MAX98357A price,
but it is a **different footprint and different pinout** — swapping requires a PCB change. Its
JLCPCB basic/extended tier is UNVERIFIED. Its channel-select mechanism is a simple logic pin,
not the four-level resistor scheme, so the single-GPIO "mono + shutdown" trick above does not
transfer directly.

---

## 2. Infineon IM69D130 PDM microphone

Source: Infineon IM69D130 datasheet v1.0, 2017-12-19,
<https://www.infineon.com/dgdl/Infineon-IM69D130-DataSheet-v01_00-EN.pdf?fileId=5546d462602a9dc801607a0e46511a2e>

### 2.1 Package and pinout (VERIFIED)

- Package: **LGA-5, 4.0 × 3.0 × 1.2 mm**, **bottom port** (sound port on the underside).
- Package drawing shows the port on the bottom view, offset from centre.

Table 7, IM69D130 pin configuration:

| Pin | Name   | Function             |
|-----|--------|----------------------|
| 1   | DATA   | PDM data output      |
| 2   | VDD    | Power supply         |
| 3   | CLOCK  | PDM clock input      |
| 4   | SELECT | PDM left/right select|
| 5   | GND    | Ground               |

### 2.2 SELECT pin channel assignment (PARTIALLY VERIFIED)

The datasheet Table 7 states only "PDM left/right select". The level-to-edge mapping lives in
the timing figure (Figure 9), which is a raster image in the PDF and did not survive text
extraction. The datasheet's own noise measurements are specified with the "select pin grounded."

**UNVERIFIED (secondary source only):** Infineon's community knowledge-base article
"Electrical interface of MEMS microphone introduction"
(<https://community.infineon.com/t5/Knowledge-Base-Articles/Electrical-interface-of-MEMS-microphone-introduction/ta-p/453658>)
states that with SELECT high the microphone drives DATA on the **rising** clock edge (left
channel slot) and with SELECT low it drives on the **falling** edge (right channel slot); the
mic is high-impedance on the opposite edge so two mics can share one DATA line.
**I could not fetch this page directly — it returned HTTP 403** — so this mapping comes from a
search-result excerpt, not from a page I read. Confirm against Figure 9 in the PDF before
committing the schematic.

Practical impact is small for a single-mic design: tie SELECT to GND (the datasheet's own
reference condition) and configure the nRF52840 PDM peripheral for the falling/right edge, or
tie it to VDD and use the rising/left edge. The nRF52840 PDM peripheral supports both via
`PDM.CONFIG.EDGE`.

### 2.3 Supply, current and power modes (VERIFIED)

- **Supply voltage VDD: 1.62 V – 3.6 V.** Absolute max on any pin 4 V.
  → **Must be fed from the regulated 3.3 V rail, never from the raw 2.9–4.4 V Li-ion rail**
  (4.4 V exceeds both the 3.6 V operating max and the 4 V absolute max).
- VDD ramp-up time: ≤ 50 ms to reach VDD_min.

Current consumption (Table 5, VDD = 1.8 V, no load on DATA):

| Condition | Typ | Max |
|---|---|---|
| fclock = 3.072 MHz | 980 µA | 1300 µA |
| fclock = 2.4 MHz | 800 µA | 1050 µA |
| fclock = 1.536 MHz | 620 µA | 800 µA |
| fclock = 768 kHz | 300 µA | 380 µA |
| **Standby mode** | **25 µA** | **50 µA** |
| **Clock Off mode** (CLOCK pulled low) | — | **1 µA** |

### 2.4 Sleep behaviour without a clock — answers coordinator question (a) — VERIFIED

**Yes: the IM69D130 sleeps at ≤ 1 µA when the PDM clock is held low. A high-side power switch
for the microphone is not needed.**

Two distinct low-power states, both in Table 5 / Table 4:

1. **Standby mode** — entered when the clock frequency drops **below 250 kHz**. The datasheet's
   clock-frequency table lists "Standby Mode … 250 [kHz max] … DATA = high-Z", i.e. 250 kHz is
   the documented threshold. Current: **25 µA typ, 50 µA max.** DATA goes high-Z.
2. **Clock Off mode** — **CLOCK pulled low** (static, not merely slow). Current:
   **`Iclock_off` = 1 µA max.** This is the state to use between voice sessions.

So there is an explicit clock-frequency threshold (250 kHz → standby) and a genuine
microamp-level sleep (clock static low → ≤1 µA). Driving the nRF52840 PDM CLK pin low and
disabling the PDM peripheral is sufficient; the 1 µA leakage is comparable to the leakage of
the load switch you would otherwise add, so the switch buys nothing.

Wake-up cost: startup time **20 ms** for ±0.5 dB sensitivity accuracy, **50 ms** for ±0.2 dB,
after VDD and CLOCK are applied. Mode-switch time is the same 20/50 ms. Budget ~20–50 ms of
settling before the first usable audio after a push-to-talk press — relevant to the UX, since
the button press should start the clock before the user begins speaking.

### 2.5 PDM clock and digital interface (VERIFIED)

- **PDM clock range: 0.4 MHz – 3.3 MHz.**
- Discrete operating modes (min/typ/max): 2.9 / 3.072 / 3.3 MHz · 2.1 / 2.4 / 2.65 MHz ·
  1.05 / 1.536 / 1.9 MHz · 400 / 768 / 950 kHz.
- Duty cycle: 40–60 % for fclock < 2.65 MHz; 48–52 % for fclock ≥ 2.9 MHz.
- Clock rise/fall time: ≤ 13 ns.
- Output logic: VOL ≤ 0.3 × VDD, VOH ≥ 0.7 × VDD (Iout = 2 mA).
- Input hysteresis: 0.1 × VDD to 0.29 × VDD.
- Max load capacitance on DATA: **200 pF**.
- Timing: DATA driven 40–80 ns after the clock edge; DATA high-Z 5–30 ns after the edge;
  DATA valid within 100 ns.
- SNR: 69 dB(A) at 3.072 MHz, 66 dB(A) at 1.536 MHz, 64 dB(A) at 768 kHz. Noise floor
  −105 dBFS(A) at 3.072 MHz. AOP 130 dB SPL, dynamic range 105 dB.
- Short-circuit current on a grounded DATA pin: 1–20 mA.

Battery trade-off: dropping from 3.072 MHz to 1.536 MHz saves ~360 µA and costs 3 dB of SNR;
dropping to 768 kHz saves ~680 µA and costs 5 dB. For 16 kHz voice, 1.536 MHz is a reasonable
operating point.

### 2.6 Decoupling and DATA termination (VERIFIED)

- **100 nF bypass capacitor between VDD and GND, placed as close to the VDD pin as possible.**
  Stated twice — in the Supply Voltage row of Table 4 ("A 100nF bypass capacitor should be
  placed close to the microphone's VDD pin to ensure best SNR performance") and in the note
  under the application circuit ("For best performance it is strongly recommended to place a
  100nF (CVDD_typical) capacitor between VDD and ground").
- **Optional series termination resistor `RTERM` ≈ 100 Ω on the DATA line** "may be added to
  reduce the ringing and overshoot on the output signal." Shown in the application circuit.
  Cheap insurance; include the footprint.
- PSRR: −80 dBFS (100 mVpp sine, 200 Hz–20 kHz on VDD), −86 dBFS(A) at 217 Hz square wave.
  Good, but the 100 nF is what delivers it.

### 2.7 Sound port and footprint (VERIFIED, with one gap)

- **PCB acoustic hole: radius 0.4 mm → diameter 0.8 mm.** Verbatim: "The acoustic port hole
  diameter in the PCB should be larger than the acoustic port hole diameter of the MEMS
  Microphone to ensure optimal performance. A PCB sound port size of radius 0.4 mm
  (diameter 0.8 mm) is recommended."
- **Land pattern: Solder Mask Defined (SMD) pads.** The datasheet's footprint and stencil
  recommendation (Figure 12) is drawn for SMD pads, not NSMD. Tell the PCB house; it changes
  the mask expansion. "The specific design rules of the board manufacturer should be
  considered for individual design optimizations."
- **UNVERIFIED: gasket.** The IM69D130 datasheet contains no gasket specification, no
  compression figures and no acoustic-seal drawing. For the enclosure you will need a
  compressible gasket (silicone or PORON foam) between the PCB and the enclosure sound hole
  to avoid an acoustic leak, and the enclosure hole should be ≥ the 0.8 mm PCB hole with a
  short, wide acoustic channel — but those are general MEMS-mic practice, not values from
  this datasheet. Infineon publishes a separate PCB/assembly application note that likely
  covers it; I did not retrieve it.

### 2.8 Sourcing (VERIFIED) — availability is the problem

| Distributor | Part | Status |
|---|---|---|
| **LCSC** | **C42464166** (IM69D130V01XTSA1) | **"Not available now" — out of stock** |
| LCSC (older record) | C536262 | Page returns "Page Not Found"; datasheet PDF still hosted |
| **DigiKey** | IM69D130V01XTSA1, DK #8030732 | **586 in stock**, $2.02 @1 · $1.58 @10 · $1.44 @25 |
| Mouser | IM69D130V01XTSA1 | Listed; page blocked to automated fetch — stock UNVERIFIED |

JLCPCB assembly availability: **UNVERIFIED** — with LCSC showing no stock, assume it is not
assemblable at JLCPCB right now. Plan on hand-placing it or buying from DigiKey.

Sources: <https://www.lcsc.com/product-detail/C42464166.html>,
<https://www.digikey.com/en/products/detail/infineon-technologies/IM69D130V01XTSA1/8030732>

### 2.9 Bottom-port PDM alternatives at LCSC — no verified in-stock option found

| Part | LCSC | Port | Package | Supply | Stock |
|---|---|---|---|---|---|
| MEMSensing **MSM261DDB020** | **C27636198** | **Bottom** | LGA-5 (2.7×3.5×0.98 mm) | 1.8 V | **Not available now** |
| MEMSensing MSM261DGT003 | C48227730 | **Top** | LGA-6 (2×4×1.1 mm) | 1.8 V | 4,848 in stock, $0.898 @1 · $0.4811 @1k |
| Infineon IM63D135AXTMA1 | C41574995 | UNVERIFIED | UNVERIFIED | UNVERIFIED | listed |
| Infineon IM72D128VV01XTMA1 | C36405960 | UNVERIFIED | UNVERIFIED | UNVERIFIED | listed |

MSM261DDB020 is the closest architectural match (bottom port, PDM, LGA-5) but is out of stock
at LCSC. MSM261DGT003 is in stock and cheap but is **top port**, which changes the enclosure
acoustic path entirely — the sound hole would have to face the component side, not the PCB
underside. Its specs (VERIFIED from the LCSC listing): omnidirectional, PDM digital output,
sensitivity −26 dB, SNR 64 dB, 670 µA, 1.8 V.

Note both MEMSensing parts are specified at **1.8 V**, not 3.3 V — their tolerance of a 3.3 V
rail is UNVERIFIED and would need a datasheet check plus possibly a separate 1.8 V LDO.
Their pinouts are UNVERIFIED; I did not fetch their datasheets.

Neither Knowles SPK0641HT4H-1 nor TDK T5837 turned up on LCSC in this pass. For reference,
SPK0641HT4H-1 is a **top-port** part (per Knowles' own datasheet title via Mouser), so it is
not a drop-in for a bottom-port layout; TDK T5837 is genuinely bottom-port
(<https://invensense.tdk.com/wp-content/uploads/2023/10/DS-000447-T5837-Datasheet-v1.2.pdf>)
but I found no LCSC listing for it.

**Recommendation:** buy the IM69D130 from DigiKey and hand-place it, or design the footprint
for both IM69D130 and MSM261DDB020 if they share a land pattern (UNVERIFIED — check).

---

## 3. WS2812B-2020-V6 (LCSC C52917434)

Source: Worldsemi WS2812B-2020 datasheet V1.3, 2019-01-25,
<https://cdn-shop.adafruit.com/product-files/4684/4684_WS2812B-2020_V1.3_EN.pdf>

### 3.1 Pin functions (VERIFIED — names differ from the assumption)

| Pin | Symbol | Function |
|-----|--------|----------|
| 1   | **DO**  | Control data signal output |
| 2   | **GND** | Ground, data & power grounding |
| 3   | **DI**  | Control data signal input |
| 4   | **VDD** | Power supply |

The datasheet uses `DO`/`DI`/`GND`/`VDD`, not `DOUT`/`DIN`/`VSS`. Functions are as expected.
Package SMD2020-4P, 2.2 × 2.0 mm body.

### 3.2 Electrical (VERIFIED) — two findings that affect this design

| Parameter | Symbol | Value |
|---|---|---|
| **Power supply voltage** | VDD | **+3.7 V to +5.3 V** |
| Logical input voltage (abs max) | VI | VDD − 0.3 V to VDD + 0.7 V |
| **High-level input** | VIH | **min 2.7 V**, max VDD + 0.7 V (DIN, SET) |
| **Low-level input** | VIL | −0.3 V to **0.7 V** (DIN, SET) |
| Input current | II | ±1 µA (VI = VDD/VSS) |
| Transmission delay DIN→DOUT | tPLZ | 300 ns max (CL = 15 pF, RL = 10 kΩ) |

Timing: T0H 220–380 ns · T1H 580 ns–1 µs · T0L 580 ns–1 µs · T1L 580 ns–1 µs · RES > 280 µs.
Data rate 800 kbit/s.

**Finding 1 — supply range conflict.** The datasheet says **VDD min is 3.7 V**. The LCSC
listing for C52917434 claims "3.3V~5.3V"
(<https://www.lcsc.com/product-detail/C52917434.html>). The datasheet is authoritative:
**below 3.7 V the LEDs are out of spec.** On a 2.9–4.4 V Li-ion rail the LEDs are out of
specification for a large part of the discharge curve. Expect colour shift and eventual
failure to latch as the cell drains. Either accept degraded behaviour near end-of-charge, or
run the LEDs from a boost/regulated rail.

**Finding 2 — 3.3 V logic drives it fine.** VIH min is 2.7 V, so a 3.3 V nRF52840 GPIO clears
the threshold across the whole VDD range. No level shifter needed. (This is the usual failure
mode with 5 V WS2812 strips; it does not apply here because VDD is a Li-ion rail, not 5 V.)

### 3.3 Bypass capacitor — datasheet says it is NOT required (VERIFIED)

The V1.3 revision note states, verbatim, that "the reverse connection of the power supply will
not be damaged; there is no need for any electronic components including capacitors on the
periphery," and the feature list says "All external electronic components including capacitors
are not required." The part integrates its own decoupling capacitor inside the 2.2 × 2.0 mm
package, alongside the control IC and the RGB die.

**So the 100 nF per LED is not a datasheet requirement.** It remains cheap, common practice and
does no harm on a 2-LED board; treat it as optional. Marking the "100 nF per LED" figure
**UNVERIFIED as a datasheet recommendation** — the datasheet actively says it is unnecessary.

### 3.4 Data-line series resistor — UNVERIFIED

**The WS2812B-2020 datasheet contains no series-resistor recommendation.** The commonly used
100–470 Ω series resistor on the first DIN is general practice for signal-integrity and
ESD/inrush protection on long cable runs, not a Worldsemi specification. On a 150 mm handheld
with two LEDs on the same PCB, the trace is short enough that it is optional; a 100–330 Ω
resistor is still worth a footprint. **Do not cite a datasheet value for this — there is none.**

### 3.5 Idle current — UNVERIFIED and important

The `II = ±1 µA` figure in the datasheet is **input leakage on the data pin**, not supply
current. The LCSC listing's "Quiescent Current: 1uA" appears to repeat that same figure and
is very likely mislabelled.

**The per-LED idle supply current is not stated in the extracted datasheet text.** In practice
the WS2812's internal oscillator and control IC keep drawing roughly 0.6–1 mA per LED even
when all three channels are set to zero — this is well known but **UNVERIFIED from a primary
source here**. At ~1 mA per LED, two LEDs would draw ~2 mA continuously, which dwarfs the
~50 µA idle budget for this device and would cut battery life by more than an order of
magnitude.

This is exactly why the project design already includes a **MOSFET gate GPIO** alongside the
LED data GPIO (per CLAUDE.md: "2x WS2812B-2020 addressable RGB LEDs: 1 data GPIO + 1 MOSFET
gate GPIO"). **Keep that high-side switch.** Unlike the microphone — which genuinely sleeps at
1 µA and needs no switch — the LEDs almost certainly do need to be hard-powered-down. Worth
measuring on the first prototype to put a real number on it.

### 3.6 Sourcing (VERIFIED)

| Item | Value |
|---|---|
| MPN | WS2812B-2020-V6, Worldsemi |
| Package | SMD2020-4P (2.2 × 2.0 mm) |
| **LCSC** | **C52917434** — 620,020 in stock |
| LCSC price | $0.0918 @5 · $0.0739 @50 · $0.0647 @150 · $0.0571 @500 · $0.0544 @2.5k · $0.0526 @4.5k |
| **JLCPCB** | **Extended part**, **"Standard Only" PCBA** (not available on Economic assembly) |
| JLCPCB notes | **MSL 5**, assembly difficulty rated **"High"** |

Sources: <https://www.lcsc.com/product-detail/C52917434.html>,
<https://jlcpcb.com/partdetail/C52917434>

**JLCPCB assembly status — the answer asked for:** **Extended, Standard-only.** It cannot be
placed on an Economic PCBA order. Combined with MSL 5 (needs dry-pack handling and bake-out
before reflow) and a "High" difficulty rating, expect a per-part assembly surcharge and
possible placement issues. The plain WS2812B-2020 (C965555) has the same Extended /
Standard-only status.

---

## 4. Speaker — 20 mm diameter × 4 mm depth, 8 Ω, 0.5–1 W

Three options, best fit first.

### Option 1 — Same Sky (formerly CUI Devices) CMS-2004-18SP — exact envelope match

| Parameter | Value |
|---|---|
| Diameter | **20 mm** |
| Depth | **4 mm** |
| Impedance | **8 Ω** |
| Rated power | **1 W** |
| Max power | 1.2 W |
| Resonant frequency | 800 Hz |
| SPL | 96 dB (1 W / 0.1 m) |
| **Termination** | **Solder pads** |
| Construction | Round frame, PET cone, neodymium magnet |

VERIFIED on the manufacturer product page:
<https://www.sameskydevices.com/product/audio/speakers/miniature-(10-mm~40-mm)/cms-2004-18sp>

This hits the 20 × 4 mm envelope exactly, at the top of the requested power range, with solder
pads (no wires to manage in a narrow enclosure — a real advantage here).

**Caveat (UNVERIFIED):** I could not confirm DigiKey or Mouser stock for this exact part
number. Searches for "CMS-2004-18SP" returned neighbouring parts (CMS-2053-18SP etc.) but not
this one. It may be manufacturer-direct or a newer addition. **Check availability before
committing the enclosure to a 4 mm speaker pocket.**

### Option 2 — Same Sky CMS-2004-18L200 — same driver, wire leads

Identical 20 × 4 mm, 1 W, 8 Ω, 800 Hz, 96 dB, but with **wire leads** instead of solder pads
(200 mm lead length implied by the `L200` suffix — UNVERIFIED).
VERIFIED from the Same Sky micro-speaker catalog listing (filtered to 20 mm / 8 Ω):
<https://www.sameskydevices.com/catalog/audio/speakers/micro-speakers>
Its individual product page was not fetched; distributor availability UNVERIFIED.

Pick this over Option 1 if the speaker mounts in a separate acoustic chamber from the PCB.

### Option 3 — PUI Audio AS02008MR-LW152-R — confirmed in distributor stock

| Parameter | Value |
|---|---|
| Diameter | **20.00 mm** |
| Height (seated max) | **3.20 mm** (manufacturer page says 3 mm) |
| Impedance | **8 Ω** |
| Rated power | **0.5 W** (500 mW) |
| Max power | 0.8 W (800 mW) |
| Resonant frequency | 500 Hz |
| SPL | 86 dB |
| **Termination** | **Wire leads** |
| Construction | Round, Mylar diaphragm, NdFeB magnet, −20 to +55 °C |
| **DigiKey** | **#4835128** — 36 in stock, **$3.92 @1**, $1.82–$2.98 in volume |

VERIFIED: <https://puiaudio.com/products/AS02008MR-LW152-R> and
<https://www.digikey.com/en/products/detail/pui-audio-inc/AS02008MR-LW152-R/4835128>

Fits with 0.8 mm depth to spare. The trade-offs against Option 1: half the rated power, and
**10 dB lower SPL (86 vs 96 dB)** — noticeably quieter for a handheld voice device. Its lower
500 Hz resonance is slightly better for voice, but 10 dB is a large gap. Also the most
expensive of the three and only 36 units in stock.

### Fallback — Same Sky CMS-2053-18SP — if 4 mm depth can be relaxed

20 mm diameter × **5.3 mm deep**, 8 Ω, **1.5 W**, solder pads.
**Confirmed at DigiKey #22521372** (<https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMS-2053-18SP/22521372>)
and TME. Exceeds the 4 mm envelope by 1.3 mm, but has verified distributor stock and more
output than any of the above. Worth considering if the enclosure can absorb 1.3 mm.

### Recommendation

Design the pocket for **CMS-2004-18SP (20 × 4 mm, solder pads)** and verify purchasability
first. If it cannot be bought in small quantity, **CMS-2053-18SP** at 5.3 mm is the
in-stock, higher-output fallback and is worth the extra 1.3 mm; **AS02008MR-LW152-R** is the
in-stock option that fits the original envelope but is markedly quieter.

Not evaluated: Adafruit 1891, Dayton CE20, LCSC generic "2004" speakers, Soberton — UNVERIFIED,
not researched in this pass.

---

## 5. Omron B3F-1000 tactile switch

Source: Omron B3F series datasheet, <https://cdn-shop.adafruit.com/datasheets/B3F-1000-Omron.pdf>

### 5.1 Dimensions and mechanics (VERIFIED — proposed figures confirmed)

| Parameter | Value |
|---|---|
| Body | **6 × 6 mm** |
| **Switch height** | **4.3 mm** |
| **Terminal pitch (lead span)** | **6.5 mm** |
| Plunger | Flat, light gray |
| **Operating force (OF)** | **100 ± 30 g** (≈ 0.98 N; LCSC rounds to 1 N) |
| Release force (RF) min | 20 g |
| **Pretravel (PT) max** | **0.25 mm, +0.2 / −0.1** |
| Weight | approx. 0.25 g |
| Dimensional tolerance | ±0.4 mm unless otherwise specified |

The datasheet series table lists the B3F-1000 as "Standard / Flat plunger / **4.3 × 6.5 mm**
switch height × pitch / General-purpose: **100 g**". So **6 × 6 × 4.3 mm is correct**, and the
6.5 mm figure is the terminal pitch, not a body dimension.

Terminal numbering (from the datasheet note): terminal numbers are not marked on the switch.
With the switch turned over and the "OMRON" logo readable on the upper part of the base, the
terminal to the right of the logo is 1, the bottom-right is 3, and the two left terminals are
2 and 4. Pins 1–2 and 3–4 are the internally connected pairs.

### 5.2 Ratings (VERIFIED)

| Parameter | Value |
|---|---|
| Contact form | SPST-NO |
| **Switching capacity** | **1 to 50 mA, 5 to 24 VDC (resistive)** |
| Contact resistance | 100 mΩ max (datasheet prints "100 MΩ max." — a known typo; the real figure is 100 mΩ) |
| Insulation resistance | 100 MΩ min at 250 VDC |
| Dielectric strength | 500 VAC, 50/60 Hz, 1 min |
| **Bounce time** | **5 ms max** |
| **Service life** | **1,000,000 operations min** |
| Operating temperature | **−25 °C to +70 °C** |
| Humidity | 35 % to 85 % RH |
| Shock | 1,000 m/s² mechanical durability; 100 m/s² malfunction durability |
| Vibration | 10–55 Hz, 1.5 mm double amplitude |

**Note the minimum switching current: 1 mA.** This is a standard (non-gold, non-low-level)
contact. Driving it directly from an nRF52840 GPIO with an internal pullup passes only a few
microamps, far below the 1 mA minimum, so the contacts will not wet and resistance can drift
upward over time in a pocket-carried device. Two mitigations: use the `B3F-1@@@-G` gold-plated
variants, which are rated **100 µA to 50 mA** (still above a pullup's current), or accept it —
in practice dry-circuit use of these switches usually works, but it is a known reliability
compromise, not a datasheet-endorsed operating point. Debounce ≥ 5 ms in firmware either way.

### 5.3 Sourcing (VERIFIED)

| Distributor | Part | Status |
|---|---|---|
| **LCSC** | **C93157** (B3F-1000, Omron) | **10,340 in stock**, Through Hole-4P 6×6 mm |
| LCSC price | $0.1749 @5 · $0.1404 @50 · $0.1232 @200 · $0.1103 @500 · $0.1000 @2.5k · $0.0948 @5k |
| **Mouser** | B3F-1000 | Listed (<https://www.mouser.com/ProductDetail/Omron-Electronics/B3F-1000>); exact stock UNVERIFIED |
| Newark | B3F-1000, #36K7138 | Listed |

Source: <https://www.lcsc.com/product-detail/C93157.html>

### 5.4 6 × 6 mm SMT alternatives

**Omron B3FS-1000P — LCSC C271750.** The B3FS is Omron's own **6 × 6 mm surface-mount** tactile
switch family, "designed for high-density mounting", providing "a sharp click and high
durability". LCSC price from **$0.1130**. This is the closest SMT counterpart to the B3F-1000 —
same manufacturer, same 6 × 6 mm footprint.
VERIFIED listing: <https://www.lcsc.com/product-detail/Tactile-Switches_Omron-Electronics_C271750.html>
Datasheet: <https://components.omron.com/us-en/system/files/2024-10/datasheet_pdf/A113-E1.pdf>
**UNVERIFIED:** its exact operating force, travel, height and stock quantity — I did not fetch
the B3FS datasheet or the full LCSC listing.

**Budget option — XKB TS-1187A-B-A-B, LCSC C318884.** SPST, **SMD-4P, 5.1 × 5.1 mm**,
**$0.011** each, **1,293,540 in stock**.
VERIFIED: <https://www.lcsc.com/product-detail/C318884.html>
Note this is **5.1 × 5.1 mm, not 6 × 6 mm** — a different footprint, so it is a cheaper
alternative rather than a drop-in. Its force/travel specs are UNVERIFIED.

For the "solder wires to a small carrier PCB" use case either SMT part works; the B3FS-1000P
keeps the 6 × 6 mm mechanical interface and the Omron feel, at ~10× the price of the XKB part
(still only 11 cents).

---

## 6. NTC thermistor for the 18650 cell

### 6.1 Correction to the suggested part

**The proposed Vishay NTCLE100E3103JB0 is not a B = 3435 or B = 3950 part.**

VERIFIED from the Vishay NTCLE100E3 datasheet (<https://www.vishay.com/docs/29049/ntcle100.pdf>,
extracted locally): the series' 10 kΩ member — part-number stem `103*B0` — is specified at
**B25/85 = 3977 K, tolerance ±0.75 %**. Every R25 value in the table (2200, 2700, 3300, 4700,
5000, 6800, 10 000 Ω) carries B25/85 = 3977 K. The series as a whole spans B25/85 of 2880 to
4570 K, but **there is no 10 kΩ / 3435 K or 10 kΩ / 3950 K part in NTCLE100E3.**

TME/Newark listings agree: NTCLE100E3103JB0 is 10 kΩ, **3977 K**, −40 to +125 °C, 500 mW,
2.54 mm lead spacing, ~4 × 3.5 × 3 mm body, 17 mm leads
(<https://www.tme.eu/en/details/640-10k/tht-measurement-ntc-thermistors/vishay/ntcle100e3103jb0/>).

If the firmware's lookup table assumes B = 3435, using this part introduces a real temperature
error. Pick a part that matches the B value the firmware expects, or generate the table from
the actual part's curve.

### 6.2 Recommended — Semitec 103AT-2 (B = 3435 K, exactly as requested)

| Parameter | Value |
|---|---|
| R25 | **10 kΩ**, ±1 % |
| **B25/85** | **3435 K** |
| Body | ~**3.8 × 2.4 × 8.5 mm** (bead in epoxy/resin, radial leads) |
| Lead length | ~17 mm, rigid leads |
| Max power | 10 mW |
| Temperature range | **−50 °C to +110 °C** |
| **DigiKey** | **#16579059** — <https://www.digikey.com/en/products/detail/semitec-usa-corp/103AT-2/16579059> |
| Other | Rapid Electronics, TrustedParts, Kempston Controls |

VERIFIED (distributor listings; the Semitec datasheet itself was not fetched — the dimensional
figures come from DigiKey/Octopart attribute data, so treat the exact body dimensions as
lightly verified).

This is the industry-standard 10 k / 3435 bead used in battery packs and 3D-printer hotends,
so the B = 3435 Steinhart-Hart coefficients are widely published. Its rigid leads and small
epoxy bead suit taping to an 18650 can. Note the **10 mW max power** — keep the sense divider
current low (a 10 kΩ top resistor from 3.3 V gives ~0.27 mW at 25 °C, fine) and preferably
switch the divider on only when sampling, both for self-heating and for battery life.

### 6.3 Alternative — TDK/EPCOS B57861S0103F040 (B = 3988 K)

| Parameter | Value |
|---|---|
| R25 | 10 kΩ, ±1 % |
| **B value** | **3988 K** (B25/100) — again *not* 3435 or 3950 |
| Power | 60 mW |
| Temperature range | −55 °C to +155 °C |
| Package | Radial leaded, wire-leaded through-hole, AEC-Q200 |
| **DigiKey** | **#739889 / 495-2142-ND** — <https://www.digikey.com/en/products/detail/epcos-tdk/B57861S0103F040/739889> |
| Other | TME, Newark, Farnell |

VERIFIED from distributor listings. Wider temperature range, automotive-qualified, 6× the
power rating of the 103AT-2. Body dimensions UNVERIFIED (not stated in the sources retrieved).
Choose this only if the firmware uses its 3988 K curve.

### 6.4 B = 3950 — not found

**UNVERIFIED / not located:** I did not find a specific, distributor-stocked leaded 10 kΩ
B = 3950 part number in this pass. 10 k/3950 glass- and epoxy-bead probes are ubiquitous on
LCSC and the far-east marketplaces but usually without a traceable manufacturer part number,
which is exactly the kind of part to avoid for a calibrated measurement. **Recommendation: use
the Semitec 103AT-2 at B = 3435** — it matches one of the two requested B values, has a real
manufacturer part number and a published curve, and is stocked at DigiKey.

---

## Summary of unverified items

1. **IM69D130 SELECT level → clock-edge mapping.** From an Infineon community KB excerpt only;
   the KB page returned HTTP 403 and the datasheet's own timing figure is a raster image.
   Confirm against Figure 9 before finalising the schematic.
2. **IM69D130 gasket specification.** Not in the datasheet at all; the 0.8 mm PCB hole is
   verified, the gasket and enclosure acoustic channel are not.
3. **WS2812B-2020 per-LED idle supply current.** Not in the datasheet; the widely cited
   ~1 mA/LED figure is unverified here. Drives the decision to keep the MOSFET power switch.
4. **WS2812B-2020 data-line series resistor and 100 nF bypass.** Neither is a datasheet
   recommendation — the datasheet explicitly says no external components are required.
5. **MAX98357A output ferrite/cap filter values.** The datasheet specifies no output filter;
   any bead value would be general practice.
6. **MAX98357A additional bulk capacitance value** for class-D current peaks (datasheet
   endorses "additional bulk capacitance" but names no value).
7. **Same Sky CMS-2004-18SP / -18L200 distributor stock.** Confirmed on the manufacturer site;
   not found at DigiKey or Mouser.
8. **CMS-2004-18L200 lead length** (assumed 200 mm from the part-number suffix).
9. **NS4168 JLCPCB basic/extended tier.**
10. **Omron B3FS-1000P detailed specs** (force, travel, height) and stock quantity.
11. **XKB TS-1187A force/travel specs.**
12. **MEMSensing MSM261 series pinouts and 3.3 V tolerance** (both specified at 1.8 V).
13. **IM69D130 Mouser stock** (page blocked to automated fetch).
14. **Leaded 10 kΩ B = 3950 NTC** — no traceable part number located.
15. **Semitec 103AT-2 exact body dimensions** (from distributor attributes, not the datasheet).
16. **IM69D130 / MSM261DDB020 land-pattern compatibility** (suggested as a dual-footprint
    hedge; not checked).
17. Speaker candidates not evaluated: Adafruit 1891, Dayton CE20, LCSC generic "2004",
    Soberton.

---

## Sources

- MAX98357A/B datasheet — <https://cdn-shop.adafruit.com/product-files/3006/MAX98357A-MAX98357B.pdf>
- MAX98357AETE+T LCSC — <https://www.lcsc.com/product-detail/C910544.html>
- MAX98357AETE+T JLCPCB — <https://jlcpcb.com/partdetail/MaximIntegrated-MAX98357AETET/C910544>
- NS4168 LCSC — <https://www.lcsc.com/product-detail/C910588.html>
- IM69D130 datasheet v1.0 — <https://www.infineon.com/dgdl/Infineon-IM69D130-DataSheet-v01_00-EN.pdf?fileId=5546d462602a9dc801607a0e46511a2e>
- IM69D130 LCSC — <https://www.lcsc.com/product-detail/C42464166.html>
- IM69D130 DigiKey — <https://www.digikey.com/en/products/detail/infineon-technologies/IM69D130V01XTSA1/8030732>
- Infineon MEMS mic electrical interface KB (403, excerpt only) — <https://community.infineon.com/t5/Knowledge-Base-Articles/Electrical-interface-of-MEMS-microphone-introduction/ta-p/453658>
- MSM261DDB020 LCSC — <https://www.lcsc.com/product-detail/C27636198.html>
- MSM261DGT003 LCSC — <https://www.lcsc.com/product-detail/C48227730.html>
- TDK T5837 datasheet — <https://invensense.tdk.com/wp-content/uploads/2023/10/DS-000447-T5837-Datasheet-v1.2.pdf>
- WS2812B-2020 datasheet V1.3 — <https://cdn-shop.adafruit.com/product-files/4684/4684_WS2812B-2020_V1.3_EN.pdf>
- WS2812B-2020-V6 LCSC — <https://www.lcsc.com/product-detail/C52917434.html>
- WS2812B-2020-V6 JLCPCB — <https://jlcpcb.com/partdetail/C52917434>
- CMS-2004-18SP — <https://www.sameskydevices.com/product/audio/speakers/miniature-(10-mm~40-mm)/cms-2004-18sp>
- Same Sky micro speakers catalog — <https://www.sameskydevices.com/catalog/audio/speakers/micro-speakers>
- CMS-2053-18SP DigiKey — <https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMS-2053-18SP/22521372>
- AS02008MR-LW152-R PUI — <https://puiaudio.com/products/AS02008MR-LW152-R>
- AS02008MR-LW152-R DigiKey — <https://www.digikey.com/en/products/detail/pui-audio-inc/AS02008MR-LW152-R/4835128>
- Omron B3F datasheet — <https://cdn-shop.adafruit.com/datasheets/B3F-1000-Omron.pdf>
- B3F-1000 LCSC — <https://www.lcsc.com/product-detail/C93157.html>
- B3FS SMT datasheet — <https://components.omron.com/us-en/system/files/2024-10/datasheet_pdf/A113-E1.pdf>
- B3FS-1000P LCSC — <https://www.lcsc.com/product-detail/Tactile-Switches_Omron-Electronics_C271750.html>
- TS-1187A-B-A-B LCSC — <https://www.lcsc.com/product-detail/C318884.html>
- Vishay NTCLE100E3 datasheet — <https://www.vishay.com/docs/29049/ntcle100.pdf>
- NTCLE100E3103JB0 TME — <https://www.tme.eu/en/details/640-10k/tht-measurement-ntc-thermistors/vishay/ntcle100e3103jb0/>
- Semitec 103AT-2 DigiKey — <https://www.digikey.com/en/products/detail/semitec-usa-corp/103AT-2/16579059>
- B57861S0103F040 DigiKey — <https://www.digikey.com/en/products/detail/epcos-tdk/B57861S0103F040/739889>
