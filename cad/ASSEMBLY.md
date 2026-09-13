# Full mechanical assembly

Build with `.venv/bin/python -m cad.assembly` (or `uv run cad-assembly`).
The source is `cad/assembly.py`, using `cad/enclosure.py` and the component
allocations in `hardware/pcb/design.py`. Outputs go to `output/full-assembly/`.
On macOS, follow the sandbox note in `AGENTS.md` if Python encounters UI errors.

This is a dimensioned assembly prototype. It includes the proposed main PCB,
radio and circuit-group allocations, daughterboards, mated connector envelopes,
21 insulated conductors, cell, contacts, thermistor, speaker, switches, caps,
gaskets, adhesive layers, straps and screws. It does not turn the unfinished
circuit into a routed or manufacturable PCB.

## Files

- `assembly.step`: named, colored parts with both enclosure halves.
- `open.step`: the same assembly with the cover and closure screws removed.
- `open.stl`, `internals.stl`: viewing meshes, rotated toward the preview camera.
  These contain multiple parts and are **not printable assembly files**.
- `chassis_print.stl`, `cover_print.stl`: enclosure halves in print orientation.
  Use this chassis: it includes the new cable passages, clips and speaker mounts.
- `USB_shoe_print.stl`, `PTT_carrier_print.stl`, `PWR_carrier_print.stl`,
  `speaker_bridge_print.stl`: separate mounting pieces.
- `PTT_TPU_cap_print.stl`, `PWR_TPU_cap_print.stl`: flexible button caps.
- `fit-report.json`: build status, collisions, nearby pairs, harness lengths,
  and explicitly bounded thread/termination contact exceptions.

Generate and inspect previews after building:

```bash
.venv/bin/python -m cad.preview output/full-assembly/open.stl
.venv/bin/python -m cad.preview output/full-assembly/internals.stl
.venv/bin/python -m cad.preview output/full-assembly/*_print.stl
.venv/bin/python -m cad.test_assembly
```

A complete build exits successfully and writes `status: PASS` after checking the
printable meshes. A failed or interrupted build can leave older exports beside
the report; do not interpret those files as a successful new build.

## Placement and mounting

| Part | Mount and mechanical constraint |
|---|---|
| Main PCB | Existing 26 × 126 × 1.6 mm slab and ten holes; six M2 × 5 screws. |
| Battery | Existing Ø18.6 × 65 mm cell position; two straps in new saddle grooves. Contact cylinders and insulating washers reserve the end space. |
| Speaker | Ø20 × 5.3 mm envelope (CMS-2053-18SP) and perimeter gasket; removable stepped bridge with two M2 × 5 screws driven along Z. The bridge clears the PCB edge. |
| Microphone | Custom **15 × 8 × 1.6 mm** board; IM69D130 aligned with X = 1, Z = 10 sound hole. The sideways SH connector sits beside the mic; perimeter tape seals and retains the board. |
| LEDs | Custom **10 × 8 × 1.6 mm** board; emitters at X = 0 and 6, Z = 140. SH socket on the inward face; perimeter tape retains the board. |
| USB-C | GCT USB4105 envelope facing X+, with a custom **6.6 × 13 × 1 mm** horizontal board. Bond the board into the locating shoe and the shoe tabs to the chassis. Its rear stop carries insertion load. |
| PTT and power | Omron B3F-1000 envelopes in separate carriers bonded to the chassis rails. Trim and insulate terminals within the modeled envelope. Thin adhesive strips retain the switch. |
| Button caps | TPU diaphragm perimeter bonded to the outer frame/ring. The switch supplies return force; a carrier shoulder limits the center to 0.35 mm travel, including 0.10 mm free play. |
| Wiring | Individual swept insulation solids with rounded bends; passages through rails retain button/USB leads. The battery-negative lead lies in a ribbed channel on the inside of the front wall, notched through the saddle webs and top contact carrier. A chassis clip supports the NTC run. |

The mic and LED boards grew from the earlier empty-seat allocations to accommodate
the headers. Their acoustic/light axes are unchanged. The main-board connector
positions also differ from the earlier placement drawing: J_USB is at u = 4,
Z = 22; J_LED at u = −9, Z = 124; J_NTC at u = −7, Z = 103; J_PTT at u = 4.5,
Z = 110, with its plug exiting upward. The amplifier and J_SPK now have separate
envelopes. These changes are explicit in the assembly source; the older placement
image is not the complete assembly layout.

## Dimensions and sources

The main PCB, cell and speaker sizes come from `hardware/pcb/DESIGN.md` and the
existing enclosure. The daughterboards and printed mounts are custom designs.

- [JST SH drawing](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf): header geometry,
  mating arrangement and 0.4–0.8 mm wire insulation range. SH bodies use conservative
  envelopes with extra room for plugs; contacts are not individually modeled.
- [JST PH drawing](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf): battery connector
  family; the existing placement allocates a 9 × 8 × 8 mm mated envelope.
- [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf): receptacle envelope
  7.35 × 8.94 × 3.31 mm, rounded mouth and 1.85 mm minimum mating projection.
- [Omron B3F drawing](https://components.omron.com/sites/default/files/datasheet_pdf/A070-E1.pdf):
  B3F-1000 body, 4.3 mm overall actuator height and 0.25 mm travel. The 6.4 mm
  square body envelope includes the published width tolerance.
- Module, microphone and LED references remain in `hardware/pcb/DESIGN.md`.

| Adjustable parameter | Current value |
|---|---:|
| Signal-wire insulation diameter | 0.8 mm |
| Battery-wire insulation diameter | 1.2 mm |
| Signal / battery bend radius | 2 / 4 mm |
| Button free play / switch travel | 0.10 / 0.25 mm |
| PCB pilot diameter | 1.6 mm |
| Existing enclosure mating clearance | 0.30 mm diametral |

Harness lengths in the report describe the modeled centerlines, not cut lengths.
Allow for contacts, terminations, strain relief and assembly slack when making
cables. The battery-negative route is deliberately longer to stay clear of the
cell, saddles and board. Speaker conductors represent the space for the pair;
individual helical twists are not modeled. Verify pin mapping from DESIGN.md,
not the rendering colors.

## Checks and practical limits

The generator uses OpenCASCADE solid validity, pairwise Boolean intersections,
and exact distances for nearby rigid parts. Wire-pair entries labeled **AABB lower
bound** are bounding-box distance bounds, not measured surface clearances; their
collision tests still use the actual solids. Overlaps are allowed only within
specific thread-engagement or wire-termination regions.

It checks the enclosure's original assembly assertions, cover withdrawal at
0.5, 2, 4, 10, 25 and 50 mm, and button-center motion through the intended stroke.
The cover check is sampled, not a continuous swept-volume proof. The TPU perimeter
stays fixed in the motion model; its deformation and force require a physical test.
Each printable export must be a connected, watertight mesh with consistent winding.
The small regression check deliberately introduces a collision and an invalid bend
to verify that the checker rejects them.

Print the rigid parts in PETG and the caps in TPU, using the supplied orientations.
Use a 0.4 mm nozzle and 0.2 mm layers as a starting point. Inspect local supports
under cable passages and internal mounts in the slicer. Install the speaker bridge
before the LED board to preserve screwdriver access, then fit the PCB, harnesses
and cell. Remove the cell for PCB screw access.

Confirm the purchased speaker, cell-contact/spring arrangement, insulation sizes,
connector tolerances, screw threads and adhesive before committing to hardware.
The contact cylinders are space reservations, not a validated spring holder or
reverse-insertion mechanism. Print and assemble a prototype to check tolerances,
USB insertion loads, strap tension, cap return and adhesive retention. The model
checks nominal geometry; it does not prove strength, RF clearance performance,
thermal behavior or electrical operation.
