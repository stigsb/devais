# Seeed XIAO nRF52840 Sense — verified facts

Research date: 2026-09-13. Every fact is marked VERIFIED (with source) or UNVERIFIED.
SKU 102010469. Board revision in Seeed's current design files: v1.1 (schematic dated 2025-12-19).

Primary sources used:

- Seeed wiki, XIAO nRF52840 series: https://wiki.seeedstudio.com/XIAO_BLE/
- Sense schematic PDF: https://files.seeedstudio.com/wiki/XIAO-BLE/Seeed_Studio_XIAO_nRF52840_PDF.pdf
- Sense front/back pinout art: https://files.seeedstudio.com/wiki/XIAO-BLE/XIAO_nRF52840_Sense_front_pinout.png and `..._back_pinout.png`
- Seeed Arduino core variant files (`Seeed_XIAO_nRF52840_Sense`): https://github.com/Seeed-Studio/Adafruit_nRF52_Arduino/tree/master/variants/Seeed_XIAO_nRF52840_Sense
- Zephyr board files: https://github.com/zephyrproject-rtos/zephyr/tree/main/boards/seeed/xiao_ble
- nRF52840 Product Spec, pin assignments: https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/pin.html
- Seeed dimension DXF (`Bottom-pad-positioning.zip`) and 3D STEP (`seeed-studio-xiao-nrf52840-3d-model.zip`), both linked from the wiki Resources section.

---

## 1. The 14 castellated pins

Pad order runs 1-7 down one long edge (D0..D6) and 8-14 up the other (D7, D8, D9, D10, 3V3, GND, 5V).
VERIFIED against the wiki pin-map table, the schematic header symbol, and `variant.cpp`.

| Pad | nRF52840 port | ADC channel | Default alt function (Seeed core) | Nordic drive class |
|---|---|---|---|---|
| D0  | P0.02 | AIN0 | A0 | LF-only |
| D1  | P0.03 | AIN1 | A1 | LF-only |
| D2  | P0.28 | AIN4 | A2 | LF-only |
| D3  | P0.29 | AIN5 | A3 | LF-only |
| D4  | P0.04 | AIN2 | A4, I2C SDA | full-speed |
| D5  | P0.05 | AIN3 | A5, I2C SCL | full-speed |
| D6  | P1.11 | — | UART TX | LF-only |
| D7  | P1.12 | — | UART RX | LF-only |
| D8  | P1.13 | — | SPI SCK | LF-only |
| D9  | P1.14 | — | SPI MISO | LF-only |
| D10 | P1.15 | — | SPI MOSI | LF-only |
| 3V3 | — | — | 3.3 V regulator output | — |
| GND | — | — | — | — |
| 5V  | — | — | VBUS, input or output | — |

Arduino digital numbering in the Seeed core is D0..D10 = 0..10 (`variant.h`), so `digitalWrite(8, …)` is the D8 pad.
The wiki's "Arduino Name" column shows two numbers per pad (e.g. `9/8` for D8) because the Mbed core numbers
differently from the non-Mbed core; the non-Mbed (Seeed nRF52) core is the second number.

## 2. Underside pads

VERIFIED from the back pinout image and the schematic test-point symbols.

| Pad | Net | Notes |
|---|---|---|
| SWCLK | SWDCLK | top-left corner (viewed from the back, USB-C at the top) |
| GND   | GND    | next to SWCLK |
| SWDIO | SWDIO  | top-right corner |
| RST   | P0.18 / RESET | next to SWDIO |
| BAT+  | battery positive, silkscreened `BAT +` | centre of the board, a pair of elongated pads |
| BAT-  | battery negative | immediately next to BAT+ |
| NFC1  | P0.09 | pad pair at the bottom edge, silkscreened `NFC` |
| NFC2  | P0.10 | as above |

NFC ports are P0.09 (NFC1) and P0.10 (NFC2) — VERIFIED (wiki pin map, schematic, `variant.cpp` D30/D31).
They default to NFC antenna function; using them as GPIO needs the `CONFIG_NFCT_PINS_AS_GPIOS` UICR setting.

There is no separate GND pad next to BAT- in the artwork beyond the one adjacent to SWCLK; BAT- is the battery
return. The front side also carries a `RST` push button at the corner next to the USB-C receptacle (VERIFIED, board photo).

## 3. On-board peripherals

All rows VERIFIED unless noted. Port numbers agree across the wiki table, `variant.cpp`, the schematic and Zephyr.

### RGB user LED

| Colour | Port | Arduino pin (Seeed core) |
|---|---|---|
| Red   | P0.26 | 11 (`LED_RED`) |
| Green | P0.30 | 13 (`LED_GREEN`) |
| Blue  | P0.06 | 12 (`LED_BLUE`) |

Polarity: common anode to 3V3, so **LOW turns a channel ON**. VERIFIED — the wiki states the LED lights on a LOW
signal, Zephyr's devicetree marks all three `GPIO_ACTIVE_LOW`, and the schematic shows 2.2 k series resistors
from each nRF pin to the LED cathodes with the common pin on 3V3.

Separate charge LED (red) on **P0.17**, active LOW. `P0.17 LOW = charging, HIGH = full or idle` — VERIFIED (back
pinout note "CHG_STAT"; net name `P0.17_~{CHG}` in the schematic).

### PDM microphone

- Part: **MSM261D3526H1CPM** (omnidirectional top-ported MEMS, PDM output, 3.5 x 2.65 x 0.94 mm OCLGA).
  VERIFIED — Seeed hosts its datasheet at
  https://files.seeedstudio.com/wiki/XIAO-BLE/mic-MSM261D3526H1CPM-ENG.pdf and the schematic places `MIC1` as `MSM261D3526H1CPM`.
- CLK: **P1.00** (`PDM_CLK`), DATA: **P0.16** (`PDM_DATA`). VERIFIED (wiki, schematic, Zephyr `pdm0` pinctrl,
  `variant.cpp` D20/D21).
- Power enable: **P1.10** (`MIC_PWR`), Arduino `PIN_PDM_PWR` = 19. VERIFIED (`variant.cpp`, schematic net
  `P1.10_MIC_PWR`). Drive it HIGH to power the mic. Note the wiki's Sense pin-map table omits this pin — it is
  only in the schematic and the core.

### IMU

- Part: **LSM6DS3TR-C** (6-axis accel + gyro). VERIFIED (wiki, schematic `U3`).
- Internal I2C: SCL **P0.27**, SDA **P0.07** — a second TWI instance, not the D4/D5 bus. VERIFIED
  (`variant.cpp` D16/D17, Zephyr `i2c0` pinctrl, front pinout art `I2C1_SCL`/`I2C1_SDA`).
- Power switch: **P1.08** (`6D_PWR`), drive HIGH to power the IMU. VERIFIED.
- INT1: **P0.11**. VERIFIED.
- I2C address 0x6A. VERIFIED (front pinout art).

### Battery charger and measurement

- Charger IC: **BQ25101** (schematic part number `BQ25101YFPT`). VERIFIED — wiki spec table and schematic.
  The Arduino `variant.cpp` comment says "BQ25100"; the schematic and the Seeed-hosted datasheet
  (https://files.seeedstudio.com/wiki/XIAO-BLE/BQ25101.pdf) say BQ25101. Trust BQ25101.
- Charge-current select **HICHG = P0.13**. Logic, VERIFIED from both the wiki and the back-pinout note:
  - **Hi-Z input, no pull-up or pull-down → ~50 mA**
  - **Output driven LOW → ~100 mA**
  (Schematic: a 10 k ISET resistor with a 2.7 k that P0.13 switches in parallel.)
- Battery voltage read: ADC on **P0.31 / AIN7**, enabled by **P0.14**. Logic, VERIFIED:
  **P0.14 LOW (output, sink) enables the divider; HIGH disables it (power save).**
  Schematic warning, quoted from the wiki: with P0.14 HIGH the read path is disabled and P0.31 may reach the
  3.6 V input limit, risking damage to the pin. Divider resistors are 1 M and 510 k, 1 % (`R16`/`R17`);
  which one is high-side is NOT resolvable from the flattened PDF text — UNVERIFIED, measure or read the KiCad project.
- Charge status: P0.17, see above.
- TS pin is tied off with a fixed 10 k (temperature sensing disabled). VERIFIED (schematic note).

### 5V / VBUS pad

- The `5V` pad is VBUS. The wiki labels it "Power Input/Output" — it carries USB VBUS out when a USB cable is
  plugged in, and can be used as a 5 V input. VERIFIED (wiki pin map; schematic net `VBUS` runs from the USB-C
  A4/B9 pins to the header pad).
- 3V3 rail comes from `U6` = **SGM2040-3.3YUDH4G** (3.3 V, 250 mA). VERIFIED (schematic).
- A **SDM20U40-7** Schottky (40 V, 250 mA) appears in the VBUS/battery input area. Its exact position in the
  topology (VBUS-to-system OR-ing vs. reverse protection) was NOT traced — UNVERIFIED.
- Whether back-feeding 5 V into the `5V` pad is safe with the USB also connected is NOT documented by Seeed —
  UNVERIFIED. Assume no ideal-diode OR-ing.

## 4. Physical

Measured directly from Seeed's own design files, not from marketing copy.

- **Board outline: 20.96 x 17.78 mm** (nominal 21 x 17.8 mm). VERIFIED — board-outline polyline in
  `Seeed XIAO nRF52840 v1.0 Dimensioning.dxf` spans X 20.958 mm, Y 17.783 mm; the current Seeed wiki spec table
  also says "21 x 17.8mm".
  **Caution:** many distributor pages and older Seeed copy say 21 x 17.5 mm. The design file says 17.78 mm.
  Design the enclosure to 17.8 mm plus clearance.
- **Castellated pad geometry** (VERIFIED, same DXF): 7 pads per row, **2.54 mm pitch**, row span 15.24 mm along
  the 21 mm length; the two rows sit on the board edges **17.78 mm apart** (exactly 7 x 2.54, so breadboard
  compatible with 7 holes between rows). Pad centres along the length at
  x = -7.3025, -4.7625, -2.2225, +0.3175, +2.8575, +5.3975, +7.9375 mm relative to the board centre.
- **Thickness** (VERIFIED from the official STEP `XIAO-nRF52840 v15.step`, bounding boxes computed with CadQuery):
  - Overall including the USB-C receptacle: **4.46 mm**.
  - Excluding the USB-C receptacle (tallest remaining part is the shielded module at the top face): **3.25 mm**.
  - The PCB solid itself spans 1.25 mm in the thickness axis, including bottom pad/plating features.
  - The commonly quoted "3.5 mm" from distributor listings is close to the no-connector figure and is
    UNVERIFIED as a primary spec.
- **USB-C receptacle** (VERIFIED, same STEP): centred across the 17.78 mm width, 8.94 mm wide, at one end of the
  21 mm length. It **overhangs the PCB edge by 1.53 mm** (PCB ends at x = 12.282, connector at x = 13.809) and
  stands **3.21 mm above the PCB top face**. Enclosure opening must clear 8.94 x ~3.2 mm and sit 1.53 mm beyond
  the board end.
- **Antenna:** chip antenna `ANT1`, part **ANTENNA-AN3216** (3.2 x 1.6 mm ceramic). VERIFIED (schematic).
  Located on the **top/component face at the board end opposite the USB-C**, roughly centred across the width —
  VERIFIED visually from the Seeed front-pinout photo (blue ceramic chip on the far edge). Keep metal and the
  battery away from that end.
- **Microphone location:** on the **top/component face**, at the **same end as the antenna (opposite the USB-C)**,
  in the corner nearest the D7/RX pad. The package is top-ported: the circular sound port faces **up, away from
  the PCB**, i.e. the same direction the USB-C shell stands. VERIFIED visually from the Seeed front-pinout photo
  (black package with a visible round port hole) plus the datasheet's "top-ported" wording. Exact XY coordinates
  of the port are UNVERIFIED — not published; measure on the part if the enclosure needs a sound channel.

## 5. Drive class of the exposed pins

nRF52840 PS, aQFN73 pin assignment table. Pins whose Description reads "Standard drive, low frequency I/O only"
(low frequency = up to 10 kHz) are, for port 0 and port 1:
P0.02, P0.03, P0.09, P0.10, P0.28, P0.29, P0.30, P0.31, and P1.01 through P1.07 and P1.10 through P1.15.
VERIFIED by quoting the table rows.

**Correction to the common assumption:** P0.04 and P0.05 are **not** on that list — their rows read only
"General purpose I/O, Analog input". So of the eleven exposed D-pins:

- **LF-only (max ~10 kHz): D0, D1, D2, D3, D6, D7, D8, D9, D10** — nine of eleven.
- **Unrestricted: D4 (P0.04) and D5 (P0.05)** — the I2C pair.

Seeed's own schematic corroborates this: the nets are named `P0.02_AIN0_LOW_A0_D0` … `P0.29_AIN5_LOW_A3_D3`
with a `_LOW_` marker, while D4/D5 are `P0.04_AIN2_A4_D4` and `P0.05_AIN3_A5_D5` with no marker.

**Consequence for this project:** Seeed's default SPI (SCK D8 / MISO D9 / MOSI D10, VERIFIED in `variant.h`:
`PIN_SPI_SCK 8`, `PIN_SPI_MISO 9`, `PIN_SPI_MOSI 10`) sits entirely on LF-only pads, as does UART on D6/D7.
Nordic's 10 kHz figure is a signal-integrity/EMC guideline, not a hard electrical limit, and these pads are used
at MHz rates by every XIAO user — but a WS2812 data line (800 kHz, sharp edges) or an I2S bit clock placed on
D0-D3 or D6-D10 is outside Nordic's stated envelope. D4/D5 are the only two exposed pins with no such caveat.

## 6. Availability and price (September 2026)

| Source | Part number | Stock | Price | Status |
|---|---|---|---|---|
| DigiKey Norway | 1597-102010469-ND | 1367 | kr 147.96 ex. VAT / kr 184.95 inc. VAT | VERIFIED — https://www.digikey.no/en/products/detail/seeed-technology-co-ltd/102010469/16652896 |
| Seeed Studio | 102010469 | In stock | USD 15.90, USD 12.90 at 10+ | VERIFIED — https://www.seeedstudio.com/Seeed-XIAO-BLE-Sense-nRF52840-p-5253.html |
| Botland (PL) | SEEED-102010469 | Ships in 24 h | EUR 17.90 inc. tax / 15.04 ex. | VERIFIED — https://botland.store/arduino-compatible-boards-other/21260-seeed-xiao-ble-nrf52840-sense-tinymltensorflow-lite-imu-microphone-bluetooth5-seeedstudio-102010469.html |
| Partco (FI) | SEEED-102010469 | Out of stock | EUR 33.40 inc. VAT | VERIFIED — https://partco.shop/product/seeed-xiao-ble-nrf52840-sense-303 |
| Mouser | 102010469 listed | — | — | UNVERIFIED — mouser.com timed out, mouser.no refused the connection |
| RS Norway (ex-Elfa Distrelec) | RS 250-0968 | — | — | UNVERIFIED — elfadistrelec.no now redirects to no.rs-online.com, which returns HTTP 403 |
| Kjell & Company | — | Not carried | — | VERIFIED negative (site search) |
| Elektroimportøren | — | Not carried | — | VERIFIED negative |
| Multicom | — | Not carried | — | VERIFIED negative |
| Digitalimpuls | — | Defunct (bankrupt Aug 2024) | — | VERIFIED |

**Practical conclusion:** no Norwegian retailer stocks it. DigiKey.no at kr 184.95 inc. VAT is the only verified
NOK source and it is well stocked.

## 7. Norwegian retail for the prototyping parts

Searched kjell.com/no, clasohlson.com/no, elektroimportoren.no, digitalimpuls.no, elfadistrelec.no, biltema.no.

### Stripboard, 0.1 in pitch, at least 25 x 130 mm

**Nothing meeting the spec was found at any of these retailers.** Closest verified item:

| Product | Retailer | Art. | Price | Notes |
|---|---|---|---|---|
| Luxorparts Eksperimentkort 60x80 mm, 10-pk. | kjell.com/no | p90664 | kr 99.90 | VERIFIED in stock. This is **perfboard** (isolated pads on FR4, 2.54 mm grid), not strip-copper veroboard, and 60 x 80 mm is short of 130 mm. https://www.kjell.com/no/produkter/elektro-og-verktoy/elektronikk/kretskort/testkort/luxorparts-eksperimentkort-60x80-mm-10-pk.-p90664 |

Clas Ohlson's Kretskort 51-243 (100 x 57 mm) is discontinued — VERIFIED.
elfadistrelec.no no longer exists as a separate site (redirects to no.rs-online.com, HTTP 403 to fetches), so its
Eurocard stripboard (RE512-LF, 100 x 160 mm) could NOT be verified — UNVERIFIED.
elektroimportoren.no and biltema.no carry no prototyping board of this type — VERIFIED negative.

### 18650 holder with leads

| Product | Retailer | Art. | Price | Notes |
|---|---|---|---|---|
| Luxorparts Batteriholder for 2x18650 | kjell.com/no | p90658 | kr 99.90 | VERIFIED, low stock. **Two-cell**, not single-cell. Lead type not confirmed from the page. https://www.kjell.com/no/produkter/elektro-og-verktoy/elektronikk/batteriholdere/luxorparts-batteriholder-for-2x18650-p90658 |

A single-cell Luxorparts holder (p32059) exists on kjell.com/se but the .no URL redirects to the category page and
the product is not listed there — NOT FOUND on the Norwegian site.
Clas Ohlson sells 18650 cells and chargers but no bare holder — VERIFIED negative.

### 3 mm common-anode RGB LED

**Not found at any Norwegian retailer, in either polarity.**
Kjell's Luxorparts RGB-lysdiode 10-pk. felles anode (p90719) appears in search indexes but its live page on both
the .no and .se storefronts now redirects to a generic LED category — treat as delisted.
The only verified in-stock 3 mm LED product at Kjell is Luxorparts LED-sortiment 3 mm 100-pk. (p90417, kr 69.90),
which is single-colour LEDs in five colours, not RGB.

**Practical conclusion for section 7:** order all three parts from a distributor (DigiKey.no, Botland, AliExpress)
rather than a Norwegian retail shelf. Nothing on the local shelf matches.

---

## Open items (UNVERIFIED, listed together)

1. Which of R16 (1 M) / R17 (510 k) is the high-side resistor in the battery divider — affects the ADC-to-volts
   conversion factor. Read the KiCad project or measure.
2. Exact XY position of the microphone sound port relative to the board origin.
3. Whether back-feeding 5 V into the `5V` pad while USB is connected is safe; the role of the SDM20U40-7 Schottky.
4. Mouser and RS Norway pricing and stock (both sites blocked automated access).
5. The wiki's Sense pin map lists "RF Switch Port Select P2.05" and "RF Switch Power P2.03". The nRF52840 has no
   port 2, and the Sense schematic shows a plain AN3216 chip antenna with no RF switch. Treat those two wiki rows
   as a documentation error copied from another XIAO variant; they do not apply to this board.
