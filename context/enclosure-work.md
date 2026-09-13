# Enclosure implementation status

**Revision 2026-09-11.** Source: `cad/enclosure.py` (673 lines). All dimensions
are millimetres.

`output/README.md` is authoritative for the generated files, the joint design and
the list of unfinished hardware. Read it first. This file covers the enclosure
parameters and the CadQuery approach behind them.

## Shape

An octagonal prism, 40 flat-to-flat and 150 tall, made by chamfering a 40 mm
square at 45 degrees. Long and short sides are in a 7:3 ratio.

```
Chamfer depth:      7.55   = (40 - 24.9) / 2
Long side:         24.9    = 40 - 2 x 7.55        (LONG_SIDE_LENGTH)
Short chamfer:     10.7    = 7.55 x sqrt(2)
Ratio:             24.9 / 10.7 = 2.33, that is 7/3
```

Walls are 1.6 thick. Vertical edges are filleted at 4.

The shell splits along a diagonal seam at X - Y = -4. The chassis half keeps the
controls on the X+ face and the audio openings on the Y- face. The cover carries
no electrical mounts. Two pins in blind sockets locate the halves; two screws
clamp them.

## Openings

Positions are given from the end they are measured from, as in the source.

| Feature | Face | Size | Position |
|---|---|---|---|
| LED holes (2) | Front | 3 diameter | X = 5 and 11, 10 from top |
| Speaker grille | Front | 19.9 diameter, perforated | Upper edge 20 from top |
| Microphone | Front | 1.5 acoustic hole, 1.0 inner port | 10 from bottom, X + 1 |
| Microphone pocket | Front, inside | 4.92 x 3.96, 1.0 deep | Behind the acoustic hole |
| Power button | Right | 8 diameter, raised ring | 44 from bottom |
| USB-C port | Right | 9.5 x 3.7 stadium, 1.6 corners | 31 from bottom |
| Large button opening | Right | 24.9 x 45, 1.6 frame | Centre 105 from bottom |

The microphone hole is shifted 1 mm in X so it stays clear of the seam. Both LED
holes sit on the chassis half for the same reason.

The large button is a separate part: 24.9 x 45 with a 4 mm deep 45-degree bevel,
corner radii running 8 at the base to 5.4 at the top, and a dotted grip texture.

## Internal mounts

- Main board envelope 26 x 126 x 1.6, resting on continuous rails, with bosses at
  the button opening.
- Cell envelope 18.6 x 65 at X = -3, Z = 20 to 85, held by two front-wall saddles
  with strap slots. The cover does not retain the cell.
- Speaker envelope 20 diameter x 4 deep, in a locating cup with tie lugs.
- Daughterboard seats: microphone 15 x 8 x 1.6, LEDs 10 x 8 x 1.6.

These are mechanical envelopes, not validated commercial parts. Contacts,
springs, insulation and the acoustic gasket are still unspecified.

## Generating and checking

```bash
uv run cad-generate                          # writes output/
uv run cad-preview output/chassis_print.stl  # multi-view PNG next to the STL
```

Exports land in `output/`: `chassis` and `cover` in both assembled and print
orientations as STL and STEP, the `fit_pins`/`fit_sockets` clearance coupon,
`pcb_template.step`, and `assembly.step`.

The generator checks that each shell is one valid connected solid, tests shell,
battery, PCB and audio envelopes for interference, confirms the cover clears the
pins and that the pins restrain it in two directions, and verifies blind socket
floors. Export requires each STL to be a single watertight mesh. It does not
repair geometry or hide failures.

Print the fit coupon before the shells. It carries three socket clearances of
0.20, 0.30 and 0.40; the enclosure uses 0.30.

## Outstanding work

- Button caps need retention, return force, travel stops and an actuator matched
  to the chosen switch.
- USB connector reach and populated board component heights are unverified.
- Print tolerances and support removal have not been tested on a printer.
- A higher-fidelity LED display is deferred to V2. The two 3 mm openings stay as
  they are. See `docs/led-indicator-research-2026-09-13.md`.

## CadQuery notes

Techniques this model depends on:

- `.offset2D()` builds the inner octagon so the wall thickness stays exact.
- `.edges("|Z")` selects the vertical edges for filleting.
- `.workplane(offset=...)` places features on a chosen face.
- A loft between two wire profiles makes the button bevel, which lets the corner
  radius change from 8 to 5.4 along its height.
- `.pushPoints()` patterns the speaker perforations in one operation.

Decisions worth keeping:

- The octagon is an explicit point list rather than a computed polygon. It is
  easier to read and to change.
- The speaker grille is perforated rather than a single cutout, which holds the
  face rigid and performs better acoustically.
- The button frame is built by cutting an inner profile from an outer one, so
  inner and outer corner radii can differ.
- Cuts overshoot the wall by 5 mm (`CUT_OVERSHOOT`) so they always penetrate.
