# LED indicator research — 13 September 2026

**Outcome: deferred to V2.** V1 ships the two 3 mm openings already in
`cad/enclosure.py` (X = 5 and 11, 10 mm from top) with 2x WS2812B-2020 on the
10 x 8 mm daughterboard. No V1 design change resulted from this research.

## Why it was raised

The device's role shifted from conversing with one agent to supervising several
concurrent coding and research agents. That needs more notification states than
two LEDs can distinguish — not just "message for you", but which agent, what
kind of event, how many are waiting.

Candidate: a row of 6-12 addressable RGB LEDs, or an 8x8 matrix, replacing the
two-LED board.

## Findings

### Nothing suitable exists off the shelf

- No addressable row module in a 2020 or smaller package is short enough for the
  ~24.9 mm front flat. Checked Tindie, Adafruit, Pimoroni, SparkFun, Waveshare,
  AliExpress, DigiKey, Mouser, LCSC. Adafruit's NeoPixel Stick is 51 mm; Seeed's
  Grove RGB stick is 80 mm.
- A full-RGB bargraph in a single package does not exist. Catalogue bargraph
  arrays (Kingbright DC-10xxWA, SunLED) are single-colour or red/green bi-colour.
- Three 8x8 boards fit 25 mm. None is usable: uInventions 25 x 25 mm
  (WS2812-2020, $18, seller inactive); MicroMatrix 20 x 20 mm (SK6805-EC15,
  3.5 V, ~64 mA idle, $59 per set of four); M5Stack Unit Puzzle (5 V only,
  14.3 mA standby, 15 mm thick cased Grove unit).

### WS2812B-2020-V6 is the part to build with

LCSC C52917434. Supersedes the V1.3 part currently specified.

| | V1.3 (C965555, current) | V6 (C52917434) |
|---|---|---|
| Supply | 3.7-5.3 V | **3.3-5.3 V** |
| Idle current | < 0.6 mA per LED | **<= 1 uA per LED** |
| Logic threshold | — | 0.55 x VDD |

V6 runs directly off the 18650 across nearly the whole discharge curve, takes
3.3 V nRF52840 logic without a shifter, and at <= 1 uA idle makes the Q1 power
gate optional. $0.09 at qty 5, 620k in stock.

Every alternative fails on voltage: XINGLIGHT XL-1010/2020 are 4.5-5.5 V;
SK6805-EC10/EC15 are 3.7-5.5 V with ~0.3-0.5 mA static per LED; APA102-2020 is
5 V and needs a second wire for clock.

Independent of the part: blue and green dies need 2.7-3.2 V forward, so below
~3.4 V cell voltage no driver can produce full blue. Firmware must dim or fall
back to red at low state of charge. Driver ICs rated to 2.7 V (LP5024,
IS31FL3729) do not avoid this and were rejected — they cost a 4-wire cable and
buy nothing the V6 does not already give.

### Cost

The V6 part is **Standard Only** at JLCPCB (assembly difficulty High, MSL 5),
which sets the floor:

- Standard PCBA requires boards >= 70 x 70 mm, so a 25 mm board must be
  panelized, and the minimum is 5 panels. Minimum realistic run is 20-45 boards,
  not 5.
- Fixed cost is ~$38 (setup $25.56 + stencil $8.21 + feeder $1.53 per BOM line).
- 8x8, 20 boards: ~$134, about $6.70 each. 45 boards: ~$233, about $5.20 each.
- A 10-LED row carries the same fixed cost but ~$0.65 of LEDs per board instead
  of ~$4.10: ~$60 for 20 boards.

Add ~$20-25 freight to Trondheim and 25% MVA. These are computed from published
fee tables, not a quote.

### Resin encapsulation

Considered for the front window. Conclusions:

- **Thermal is not a constraint.** 64 LEDs at full white is 2.3 A, but the
  battery budget already caps brightness at 10-15% and signalling is
  duty-cycled. Average dissipation is tens of milliwatts.
- **Epoxy yellows.** Blue and near-UV drive the degradation and the blue channel
  sits millimetres away. Failure appears as colour drift, not a fault. Use
  optical silicone (non-yellowing, >90% transmittance, stable to 200 C) or a
  UV-stable polyurethane.
- **Cure shrinkage stresses the joints.** Epoxy shrinks 1-3% with a CTE around
  50-70 ppm/K against FR4's ~15, working on every joint through each thermal
  cycle. Silicone's low modulus absorbs it. Pour thin layers to limit exotherm;
  degas, since one bubble over a pixel is visible.
- **Potting widens the emission cone.** Resin at n~1.5 removes the lens-air
  boundary, so a potted array blends *more*, not less.

Conclusion: do not pot the board. Cast the diffuser as a separate part that
drops into the enclosure window, with an opaque grid between it and the array.
That keeps the board reworkable and lets several pigment loadings be tried
without recommitting a board run.

## Constraints any V2 design must satisfy

- Front flat face is `LONG_SIDE_LENGTH` ~= 24.9 mm. A 25 mm board has no margin;
  2.5 mm pitch gives a 20 mm field and room to work.
- The enclosure parts at X = 0 and both current LED openings sit on the chassis
  half. A centred board crosses the joint — either keep the row on the chassis
  half (about 6 LEDs), move the split, or add a lens insert spanning it.
- Per-pixel separation behind the 1.6 mm wall needs a grid insert. At 1.5 mm
  pitch it is not achievable with FDM at all, which is why the finer-pitch
  panels were rejected.
- 64 LEDs at full white is ~2.3 A. Firmware must cap global brightness.

## Starting point for V2

`hardware/led-matrix/upstream/` holds a third-party KiCad 7 design for a
25 x 25 mm 8x8 WS2812B-2020 board on a 3.0 mm pitch. See that directory's README
for what must change before it is usable here, and for the unresolved licence.
