# Devais prototype builds — 13 September 2026

Two builds precede the custom PCB in [`pcb/DESIGN.md`](pcb/DESIGN.md):

1. **Bench prototype**: stripboard, breakout modules, no enclosure. Proves
   push-to-talk capture, BLE transfer to the phone, playback, LEDs and idle
   current.
2. **Field unit**: the same electronics on a stripboard carrier inside the
   printed chassis. Cell replaced by opening the cover. No charging port and
   no power button are required; the PTT button, speaker, microphone and
   LEDs must work.

The custom PCB design is unchanged by either build and stays the plan for the
25-unit run. Pin names below are XIAO silkscreen names; nRF port numbers, peripheral
pins and module dimensions were verified against the Seeed wiki, schematic
and Arduino variant files on 2026-09-13
(`docs/research/2026-09-13-xiao-sense.md`).

## Parts for the bench prototype

| Item | Part | Qty | Source | Note |
|---|---|---|---|---|
| Controller | Seeed XIAO nRF52840 Sense | 1 (+1) | digikey.no kr 185 incl. VAT, 1,300 in stock; no Norwegian shop stocks it | USB-C, UF2 bootloader preinstalled, 3.3 V regulator, 100 mA charger, PDM microphone and IMU on board |
| Amplifier | MAX98357A I2S breakout (Adafruit 3006 or generic clone) | 1 | Adafruit, DigiKey, AliExpress | Pins VIN, GND, SD, GAIN, DIN, BCLK, LRC, speaker terminals |
| Speaker | Same Sky CMS-2053-18SP, 20 mm, 8 Ω, 1.5 W | 1 | DigiKey 22521372 | Any 8 Ω speaker works on the bench |
| Cell | Protected 18650 (any brand, 67–70 mm) | 1 | batterionline.no | Protected cell replaces the DW01A circuit. The unprotected 35E is for the PCB build |
| Cell holder | 18650 holder with wire leads | 1 | DigiKey (Keystone 1043, 36-1043-ND, PCB pins; or a leaded holder) | Kjell and Clas Ohlson stock no single-cell 18650 holder |
| Switches | Omron B3F-1000 or any 6 × 6 or 12 × 12 tactile switch | 2 | LCSC C93157, DigiKey | PTT and reset |
| LEDs | 3 mm common-anode RGB LED, diffused | 1 | DigiKey | Plus the XIAO's on-board RGB LED as the second indicator |
| Resistors | 1 kΩ (red), 560 Ω (green, blue), 10 kΩ (pull-up) | 3 + 1 | any | 1/4 W through-hole |
| Capacitors | 100 nF ceramic, 100 µF electrolytic | 1 + 1 | any | Button filter; amplifier supply bulk |
| Stripboard | 0.1 in pitch, at least 25 × 140 mm usable | 1 | DigiKey, Mouser, Farnell | Strips run across the short axis; see cutting rules |
| Headers | 2.54 mm male pin headers, 7-pin × 2 for the XIAO; female headers for the amp if it is to be removable | | DigiKey | |
| Wire | 0.25 mm² (24 AWG) stranded, red and black for power; 0.14 mm² (26 AWG) for signals | | DigiKey, Farnell | |
| Tools | 0.6 mm chisel-tip iron, side cutters, 3 mm drill or strip cutter for cutting strips, multimeter | | | |

## Bench wiring

Power: cell + to the XIAO's BAT+ pad on the underside, cell − to BAT−. The
XIAO's 3V3 pin supplies the LEDs and the PTT pull-up. The amplifier VIN
takes the cell voltage from the holder leads, not 3V3, with the 100 µF
capacitor across VIN and GND at the amplifier. A grounded USB cable into
the XIAO charges the cell at 100 mA (over 30 hours for 3350 mAh) and gives
USB DFU and serial. The XIAO's HICHG pin selects 100 mA when driven low.

| XIAO pin | nRF port | Signal | Connection |
|---|---|---|---|
| D0 | P0.02 | BTN_PTT | Switch to GND; 10 kΩ to 3V3; 100 nF to GND |
| D1 | P0.03 | LED_R | 1 kΩ to the RGB LED red cathode |
| D2 | P0.28 | LED_G | 560 Ω to green cathode |
| D3 | P0.29 | LED_B | 560 Ω to blue cathode; LED anode to 3V3 |
| D4 | P0.04 | I2S_BCLK | Amplifier BCLK (about 1 MHz; D4 and D5 are the only full-speed pads) |
| D5 | P0.05 | I2S_DIN | Amplifier DIN |
| D6 | P1.11 | spare (PDM_CLK in field option M2) | |
| D7 | P1.12 | spare (PDM_DATA in field option M2) | |
| D8 | P1.13 | I2S_LRCLK | Amplifier LRC, 16 kHz |
| D9 | P1.14 | AMP_SD | Amplifier SD pin through 100 kΩ (mono mix window); low = shutdown |
| D10 | P1.15 | spare | |
| RST (underside pad) | | Reset switch | Second switch to GND; double-tap enters the UF2 bootloader |
| BAT+, BAT− (underside pads) | | Cell | Through the holder leads |
| on-board mic MSM261D3526H1CPM | CLK P1.00, DATA P0.16, power P1.10 | PDM capture | No wiring |
| on-board RGB LED | red P0.26, green P0.30, blue P0.06, common anode to 3V3, active low | Second indicator | No wiring |
| HICHG | P0.13 | Charge current | Drive low for 100 mA; floating gives 50 mA |
| VBAT sense | P0.31 / AIN7, divider enabled by P0.14 low | Cell voltage | Keep P0.14 low only while sampling |

The amplifier GAIN pin is left open for 9 dB. Nine of the eleven exposed
pins are Nordic "low frequency" pads (D0–D3, D6–D10); only D4 and D5 are
full-speed, so they carry the bit clock and data. Seeed's own SPI runs on
D8–D10 at several MHz, so a 16 kHz LRCLK on D8 is not a concern. The custom
PCB uses full-speed pads throughout.

Stripboard rules: the XIAO is 20.96 × 17.78 mm, 4.46 mm thick with its USB-C
receptacle, which overhangs the board edge by 1.5 mm. Its two pin rows are
17.78 mm apart on 2.54 mm pitch and lie on the same strips, so cut every
strip between the rows under the module. Mount the
XIAO on male headers so the underside pads (BAT+, BAT−, RST, SWD) are
reachable: solder the cell and reset leads to those pads before fitting the
headers. Keep the speaker pair twisted and away from the cell leads.

## Firmware for the prototype

- Bootloader: the factory Adafruit UF2 bootloader (board `Seeed XIAO nRF52840
  Sense`). USB DFU by double-tap reset or the 1200-baud touch. No SWD needed.
- Framework: nRF Connect SDK (Zephyr) with the `xiao_ble/nrf52840/sense`
  board, which has the PDM mic and I2S drivers; or the Seeed Arduino core
  with the `PDM` and `I2S` libraries for a faster start. Pick one and keep
  it for the custom board, which will need its own board definition.
- Audio: 16 kHz mono capture from PDM, transfer over BLE (a GATT
  characteristic with notifications, or NUS), playback over I2S at the same
  rate with the sample duplicated into both slots.
- Sleep: System OFF with PTT wake, amplifier SD low, PDM clock stopped.
  Measure the cell current with the LEDs off; this number decides whether
  the product needs the power button at all.

## Field unit

The bench electronics move onto a 25.4 × 135 × 1.6 mm stripboard cut to the
main-board outline, screwed to the existing rails with the existing six M2
positions (drill the stripboard to match `stripboard_template.step`). Beside
the cell the carrier may carry only flat parts (3 mm limit): wires, resistors
lying flat, the capacitors laid down. Modules sit above the cell:

| Part | Position | Mounting |
|---|---|---|
| XIAO nRF52840 Sense | Top of the carrier, Z 125.8–146.8, USB-C mouth at the top end wall; the chip antenna and the on-board mic are at the opposite (lower) end on the top face | Soldered flat by its castellations at Z 125.8–146.8; USB-C through a 7.5 × 13 mm opening in the top wall; BAT+/BAT− leads soldered from behind through an 8 × 12 mm stripboard window |
| MAX98357A breakout | Above the cell, Z 92–111.4 | Z 92–111.4 on one 7-pin header row at Y = 6.1, header pins clipped to 1.5 mm behind the board |
| Speaker | Existing cup, existing bridge | Unchanged |
| PTT switch | Existing carrier at Z = 105 | Unchanged; the lead is routed behind the amplifier pins at X 15. The PTT tunnel leaves only a 0.14 mm skin on the PCB rail's back face, which will not print, so the lead lies in a groove open toward the wall with a 2.1 mm gap. |
| Reset switch | Existing power-button carrier at Z = 44 | Not fitted; the power carrier and cap stay as blanks |
| RGB LED | Through both existing 3.2 mm holes at Z = 140, leads soldered to a 5-wire lead | One RGB LED and one single-colour LED on D10 on the product LED board, 5-wire lead |
| Cell | Existing cradle, Keystone contacts, straps | Cover off to swap; the straps hold it |
| USB-C side opening | Not cut in the field chassis | None needed |

Microphone: M2, an Adafruit 3492 PDM breakout (14.0 × 12.8 × 2.8 mm) in the
enlarged bottom-front seat, MP34DT01 port toward the wall, wired to D6/D7.
Decided 2026-09-14.

The field variant is built with `--variant field` in `cad/enclosure.py` and
`cad/assembly.py`; see `cad/ASSEMBLY.md`.
