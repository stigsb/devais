# Enclosure and Assembly Update for Revision 2 Parts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `cad/enclosure.py` and `cad/assembly.py` in line with the parts selected in `hardware/pcb/DESIGN.md` revision 2 and `hardware/BOM.md`, so the next print and the assembly fit report describe the parts that will actually be bought.

**Architecture:** All geometry is parametric CadQuery. `cad/enclosure.py` owns the shells and chassis mounts; `cad/assembly.py` owns purchased-part envelopes, harnesses, printed carriers and the fit checker. Every task changes parameters or envelopes, rebuilds the assembly, and requires `output/full-assembly/fit-report.json` to report `"status": "PASS"` with an empty `errors` list. There is no separate unit-test suite for geometry; the build is the test.

**Tech Stack:** Python 3.14, CadQuery 2.8, run with `.venv/bin/python` from the repository root. `cad/test_assembly.py` is a small regression check of the harness and collision helpers.

**Spec:** `hardware/pcb/DESIGN.md` (section "Mechanical updates required by this revision") and `hardware/BOM.md`.

## Global Constraints

- Do not commit. The working tree already carries uncommitted LED-position changes (X = 0 and 6) from another session. Leave them in place and build on them. Each task ends with a passing build and `git diff --stat`.
- Dimensions in millimetres. Enclosure coordinates: X toward the control face, Y negative toward the front (audio) face, Z up. Front wall inner face is at Y = −18.4, outer at Y = −20.
- The assembly build is slow (minutes). Run it once per task, in the foreground, with a 10 minute timeout: `.venv/bin/python -m cad.assembly`. A passing run prints `Static fit passed; checking cover and button travel` then writes `status: PASS`. Also run `.venv/bin/python -m cad.test_assembly` after any change to `harness()`.
- Preview renders (`.venv/bin/python -m cad.preview <stl>`) need host display access; if the sandboxed run fails on Cocoa/AppKit, retry with escalated permissions. Geometry assertions are real failures, not sandbox failures.
- Keep comments short and factual. Update the three documents that describe these parameters in the same task that changes them: `cad/ASSEMBLY.md`, `context/enclosure-work.md`, `output/README.md`.
- Do not change the PCB outline, mounting holes, the seam, the button openings or the USB wall opening.

---

### Task 1: Speaker CMS-2053-18SP (5.3 mm deep) and the bridge

**Files:**
- Modify: `cad/enclosure.py` (constants near line 96, speaker cup in `add_component_mounts` near line 493)
- Modify: `cad/assembly.py` (speaker cylinder near line 142, bridge near lines 277–296)
- Modify: `cad/ASSEMBLY.md` placement table, `context/enclosure-work.md` internal mounts, `output/README.md` speaker paragraph

**Interfaces:**
- Produces: `e.SPEAKER_BODY_DEPTH = 5.3` used by later tasks for clearance; the bridge geometry is local to `build()`.

- [ ] **Step 1: Change the speaker depth and the cup length**

In `cad/enclosure.py`:

```python
SPEAKER_BODY_DIAMETER = 20.0
SPEAKER_BODY_DEPTH = 5.3  # Same Sky CMS-2053-18SP; the 4.0 mm CMS-2004 also fits
```

In `add_component_mounts`, make the cup ring cover the whole speaker body plus 1 mm:

```python
    cup = cq.Workplane('XZ', origin=(0,-18.9,z)).circle(
        SPEAKER_BODY_DIAMETER/2+2).circle(SPEAKER_BODY_DIAMETER/2+MOUNT_CLEARANCE).extrude(-(SPEAKER_BODY_DEPTH+1.5))
```

(The 'XZ' workplane normal points to −Y, so a negative extrude runs toward +Y, into the cavity. The old value −5.0 covered a 4 mm speaker plus 1 mm.)

- [ ] **Step 2: Use the constant for the speaker envelope in the assembly**

In `cad/assembly.py` replace the hard-coded 4:

```python
    add('speaker',cylinder(10,e.SPEAKER_BODY_DEPTH,(0,-18.3,SPEAKER_Z),(0,1,0)),'#50565e')
```

- [ ] **Step 3: Move the bridge plate clear of the deeper speaker**

The speaker rear face is now at Y = −18.3 + 5.3 = −13.0. The bridge plate must sit at least 0.6 mm behind it, so its front face is at Y ≥ −12.4. The existing bridge is a single box at Y = −13.7 (spanning −14.3…−13.1) with a step toward the PCB and two ears at Y = −15.5 that screw into the lugs. Rebuild it as:

1. A plate over the speaker: `box((23.9,1.2,3),(-2.55,-11.8,bridge_z))` (spans Y −12.4…−11.2).
2. Two risers joining the plate to the ears and to the PCB-side step, each spanning Y from −14.3 to −11.2, placed where they are outside the speaker clearance cylinder (radius 10.3 about the speaker axis at Z = `SPEAKER_Z`). One riser on the left at X ≈ −13.25 (width 2.5) and one on the right at X ≈ 9.7 (width 0.6 is too thin; instead raise `bridge_z` to `SPEAKER_Z + 7` so the speaker half-width at the bridge is under 8.7 mm and a 1.6 mm wide riser at X 8.8…10.4 fits). Keep the ear cylinders at (±12, −15.5) and the step pieces `box((2.5,1.2,3),(10.65,-14.0,bridge_z))` and `box((2.6,1.2,3),(13.2,-13.7,bridge_z))` as they are, since they clear the PCB slab (Y ≥ −13) and the rail at Y −12.25…−7.75, X 11.5…16.3.
3. Cut the speaker clearance cylinder `cylinder(10.3, 8, (0,-19,SPEAKER_Z), (0,1,0))` from the bridge so nothing intrudes into the speaker.

Then re-derive the chassis features that depend on `bridge_z` (lug height, ear pilot cuts, the bridge rebate) — they already use the `bridge_z` variable, so raising it moves them together. Check that the lugs still intersect the chassis wall and the cup and do not reach the LED seat, whose lower edge is at Z = 134.

- [ ] **Step 4: Build and check**

Run: `.venv/bin/python -m cad.assembly`
Expected: `Static fit passed; checking cover and button travel`, then `status: PASS` in `output/full-assembly/fit-report.json`. If the report lists an overlap between `speaker_bridge` and `speaker`, `main_PCB`, the rails (`chassis`) or the LED seat, adjust the riser positions and rebuild. Do not add contact exceptions.

- [ ] **Step 5: Update the documents**

- `cad/ASSEMBLY.md` placement table, Speaker row: `Ø20 × 5.3 mm envelope (CMS-2053-18SP)`.
- `context/enclosure-work.md` internal mounts: `Speaker envelope 20 diameter x 5.3 deep`.
- `output/README.md`: same figure in the speaker paragraph.

- [ ] **Step 6: Report**

Run: `git diff --stat`
Report the bridge geometry you ended up with (plate Y, `bridge_z`, riser positions).

---

#### Task 1c: Bridge plate continuity (rev 2, 2026-09-14)

The plate (Y −12.4…−11.2, Z `bridge_z` ± 1.5) already sits behind the speaker body (back face Y −13.0) with a 0.6 mm standoff, so it needs no speaker clearance. The cut on the bridge, `cylinder(10.3,8,(0,-19,SPEAKER_Z),(0,1,0))`, runs Y −19…−11 and removes the plate to a 0.2 mm ribbon at X = 0. Shorten that one cut so it ends 0.1 mm short of the plate front face and only clears the risers and steps, which reach forward into the body's Y range:

```python
    bridge=bridge.cut(cylinder(10.3,6.5,(0,-19,SPEAKER_Z),(0,1,0)))  # Y -19..-12.5
```

Leave `bridge_z = SPEAKER_Z+9`, the lug cut on line 265 (lugs sit inside the body's Y range) and everything else unchanged. Update the comment above the bridge so it says the plate holds the top 2.5 mm of the speaker's back face. Expected: `speaker_bridge` builds as one solid 23.9 × 1.2 × 3 plate plus risers, steps and ears; the speaker-to-plate gap stays 0.6 mm; fit report PASS with no new contacts. Re-render the previews touched by Task 5 that show the bridge.

### Task 2: Plain 3 mm RGB LEDs, 12 × 8 mm LED board, 7-position header

**Files:**
- Modify: `cad/enclosure.py` (`LED_DIAMETER` line 22, `LED_BOARD_WIDTH` line 95, docstring of `add_led_holes`)
- Modify: `cad/assembly.py` (LED emitters and socket near lines 135–141, `LED_SOCKET_X` line 27, header probe near line 290, `harness()` offsets line 66–69, LED route line 254)
- Modify: `cad/ASSEMBLY.md`, `context/enclosure-work.md`, `output/README.md`

**Interfaces:**
- Produces: `harness()` accepts `count` in {1,2,3,4,7,8}; Task 3 relies on the 8-conductor bundle and its `bundle_radius(count, diameter)` helper.

- [ ] **Step 1: Enclosure parameters**

```python
LED_DIAMETER = 3.2  # Through-hole 3 mm LED domes pass the wall; 0.2 mm clearance
...
LED_BOARD_WIDTH, LED_BOARD_HEIGHT = 12.0, 8.0  # Two 3 mm RGB LEDs and a 7-way SH header
```

Change the `add_led_holes` docstring to `2x 3.2 mm holes for 3 mm RGB LEDs at explicit X positions.`

- [ ] **Step 2: Extend `harness()` to 7 and 8 conductors and expose the bundle radius**

Replace the `offsets` dictionary in `harness()` with a helper used by both the harness and the tunnel cut:

```python
def bundle_offsets(count, diameter):
    """Conductor centre offsets in the bundle cross-section; 5+ leads form two rows."""
    pitch = diameter+0.12
    if count <= 4:
        return {1: [(0,0)], 2: [(-pitch/2, 0), (pitch/2, 0)],
                3: [(-pitch/2, -pitch/3), (pitch/2, -pitch/3), (0, pitch*2/3)],
                4: [(x*pitch/2,y*pitch/2) for x in (-1,1) for y in (-1,1)]}[count]
    per_row = (count+1)//2
    xs = [(i-(per_row-1)/2)*pitch for i in range(per_row)]
    offsets = [(x, -pitch/2) for x in xs] + [(x, pitch/2) for x in xs]
    return offsets[:count]


def bundle_radius(count, diameter):
    return max(math.hypot(x, y) for x, y in bundle_offsets(count, diameter)) + diameter/2
```

and in `harness()`:

```python
    offsets = bundle_offsets(count, diameter)
```

In the route loop, replace the tunnel radius expression `1.2 if count==4 else 1.02` with `bundle_radius(count, od)+0.3`.

Extend `cad/test_assembly.py` with one check after the existing harness assertions:

```python
    wires8, _ = harness([(0, 0, 0), (0, 0, 20), (0, 20, 20)], 8, .8)
    assert len(wires8) == 8
    assert all(a.intersect(b).Volume() < 1e-5 for a, b in combinations(wires8, 2))
```

(add `harness` is already imported; nothing else to import.)

Run: `.venv/bin/python -m cad.test_assembly`
Expected: `Cable bend and collision regression checks passed`

- [ ] **Step 3: LED envelopes, socket and route**

Replace the two LED emitter boxes with a flange plus dome per LED, and widen the socket to a 7-way SH plug (header 9.0 mm wide; use the same 0.5 mm side allowance as the other SH envelopes):

```python
LED_SOCKET_X = e.LED_BOARD_X  # 7-way header centred on the 12 mm board
...
    add('LED_J_SH_mated',box((9.5,3,8.5),(LED_SOCKET_X,-13.75,139.75)),'#edba65')
    for x in e.LED_POSITIONS_X:
        # 3 mm through-hole RGB LED: 1 mm flange on the board face, dome through the wall.
        flange=cylinder(1.9,1.0,(x,-16.85,140),(0,-1,0))
        dome=cylinder(1.5,4.4,(x,-17.85,140),(0,-1,0))
        add(f'LED_{x}',flange.fuse(dome),'#eee6ab')
```

The dome ends at Y = −22.25, 2.25 mm proud of the outer face; that is intended for V1. Update the header probe to the new width:

```python
                        ('LED_PCB',box((9.5,.1,5.5),(LED_SOCKET_X,-15.3,141.25))),
```

Change the LED route to 7 conductors:

```python
        'LED': (7, WIRE_OD, [(8.4,-9,118.25),(4,-9,118.25),(4,-9,127),(LED_SOCKET_X,-9,132),(LED_SOCKET_X,-13.75,132),(LED_SOCKET_X,-13.75,135.5)], 'J_LED','LED_J_SH_mated'),
```

The J_LED allocation in `hardware/pcb/design.py` (`("J_LED", -9, 123, 5.5, 5.5, 3.0, "connector")`) must grow to the 7-way header: change its width to `9.5`. Rerun `.venv/bin/python hardware/pcb/design.py` and confirm it passes (it asserts screw clearance and overlaps); if J_LED now collides with `SWD PADS` or the module keep-out, move `SWD PADS` to `u = 9, Z = 118` and rerun.

- [ ] **Step 4: Build and check**

Run: `.venv/bin/python -m cad.assembly`
Expected: PASS. Watch for `LED_J_SH_mated` against `chassis` (the LED seat window is `w-2` wide, so the 12 mm board gives a 10 mm window) and for the domes against the chassis hole edges: a 3.0 mm dome in a 3.2 mm hole must show a gap of about 0.1 mm, not an overlap. If a dome overlaps the wall, check that `LED_POSITIONS_X` and the emitter X positions are the same values.

- [ ] **Step 5: Update the documents**

- `cad/ASSEMBLY.md` LEDs row: `Custom 12 × 8 × 1.6 mm board with two 3 mm RGB LEDs and a 7-way SH header; emitters at the LED_POSITIONS_X values, Z = 140.`
- `context/enclosure-work.md`: LED holes `3.2 diameter`; daughterboard seats `LEDs 12 x 8 x 1.6`.
- `output/README.md`: same two figures.

- [ ] **Step 6: Report**

Run: `git diff --stat`
Report the LED dome-to-wall gap from `fit-report.json` `near_pairs`.

---

### Task 3: USB daughterboard with 8-way header and 8-conductor harness

**Files:**
- Modify: `cad/assembly.py` (USB board/socket/shoe near lines 146–162, USB route line 250, USB probe line 291)
- Modify: `cad/ASSEMBLY.md` USB-C row

**Interfaces:**
- Consumes: `bundle_radius()` from Task 2.

- [ ] **Step 1: Widen the mated 8-way plug and the shoe pocket**

The 8-way SH header is 10.0 mm wide; the plug envelope gets the same 0.5 mm per side allowance the others use. The shoe pocket must clear it.

```python
    add('USB_J_SH_mated',box((6.5,11.0,3),(15.1,0,26.845)),'#edba65')
    # Shoe supports board edges and rear of socket. Front/back stops take insertion load.
    shoe=box((7.7,16,1.5),(15.65,0,27.595))
    shoe=shoe.cut(box((6.2,12.0,4),(15.8,0,27.6)))
```

The board stays 13 mm wide (`USB_PCB` box unchanged) and the side walls at y = ±7.25 stay. Update the probe so it checks the full 10 mm header bearing area:

```python
                        ('USB_PCB',box((6.5,10.0,.1),(15.1,-1.5,28.395)))]:
```

- [ ] **Step 2: Eight conductors on the USB route**

```python
        'USB': (8, WIRE_OD, [(8.4,4,16.25),(8.4,4,11.5),(8.4,14.5,11.5),(13.9,14.5,11.5),(13.9,14.5,26.845),(15.3,4.25,26.845)], 'J_USB','USB_J_SH_mated'),
```

The tunnel through the chassis and the shoe is cut with `bundle_radius(8, WIRE_OD)+0.3` (about 2.3 mm) by the code from Task 2. The J_USB allocation in `hardware/pcb/design.py` (`("J_USB", 4, 31, 6.5, 5.5, 3.0, "connector")`) becomes width `10.5`; rerun `.venv/bin/python hardware/pcb/design.py` and confirm it passes. If J_USB now collides with the `J_MIC` or `J_PWR` allocations or a screw head, shift J_USB to `u = 2` first, then `J_MIC` to `u = -6`, and rerun.

- [ ] **Step 3: Build and check**

Run: `.venv/bin/python -m cad.assembly`
Expected: PASS. Watch `wire_USB_*` against `cell_18650` (the bundle runs beside the cell at X = 8.4, cell surface at X = 6.3) and against `main_PCB`. If a conductor touches the cell, move the first two waypoints from X = 8.4 to X = 8.0 and rebuild; the PCB inward face is at X = 9.9, so the bundle centre must stay at X ≤ 9.9 − 2.3.

- [ ] **Step 4: Update the document**

`cad/ASSEMBLY.md` USB-C row: `... custom 13 × 6.6 × 1 mm horizontal board with an 8-way SH header on its underside ...`.

- [ ] **Step 5: Report**

Run: `git diff --stat`
Report the tunnel radius and the USB bundle's nearest gap.

---

### Task 4: Battery contacts, cradle length, positive collar and lead insulation

**Files:**
- Modify: `cad/enclosure.py` (`CONTACT_SPACE` line 91, contact carriers near lines 474–479)
- Modify: `cad/assembly.py` (`BAT_WIRE_OD` line 20, contact envelopes near lines 226–229)
- Modify: `cad/ASSEMBLY.md` Battery row and adjustable-parameter table, `context/enclosure-work.md`, `output/README.md`

- [ ] **Step 1: Cradle inside length 72.0 mm**

Keystone's installed length for the 5201 spring with the 5223 button is 71.6 mm for a 65.0 mm cell; real cells are up to 65.3 mm.

```python
CONTACT_SPACE = 3.5  # Keystone 5201 spring + 5223 button: 72.0 mm inside for a 65.0 cell
# Reverse-insertion collar on the positive carrier: a ring around the 5223 plate
# whose underside sits POSITIVE_COLLAR_DROP below the button tip. A reversed cell's
# flat end stops on the ring; the correct cell's raised cap passes through the
# opening. Requires cap protrusion > POSITIVE_COLLAR_DROP (measure the 35E cap and
# the 5223 button before printing; tune POSITIVE_COLLAR_DROP).
POSITIVE_COLLAR_ID = 12.0  # clears the Ø8 cell cap and the Ø11 insulating washer
POSITIVE_COLLAR_DROP = 0.4
POSITIVE_COLLAR_HEIGHT = 0.5 + 1.0 + POSITIVE_COLLAR_DROP  # plate + button + drop, from the carrier face
POSITIVE_PLATE_POCKET = (11.6, 0.6)  # X width and depth of the 5223 plate pocket in the collar top
```

Rev 2 (2026-09-14, after the Task 4 review): the rev 1 collar (0.6 mm tall, ID 9.0, hung from the carrier face) sat in the same 0.5 mm Z band as the 5223 plate, so it interpenetrated the plate, and its underside was 0.9 mm above the button tip, so a reversed cell met the button before the ring. The collar now surrounds the plate instead of sitting under it and reaches past the button tip.

In `add_component_mounts`, after the two carriers are added, add the collar on the positive (top, Z = `BATTERY_BOTTOM_Z+BATTERY_LENGTH+CONTACT_SPACE` = 88.5) carrier face, protruding down toward the cell, with a pocket for the plate cut into its top:

```python
    top = BATTERY_BOTTOM_Z+BATTERY_LENGTH+CONTACT_SPACE
    collar = (cq.Workplane('XY').center(BATTERY_CENTER_X, 0)
              .circle(BATTERY_DIAMETER/2+BATTERY_CLEARANCE).circle(POSITIVE_COLLAR_ID/2)
              .extrude(POSITIVE_COLLAR_HEIGHT).translate((0, 0, top-POSITIVE_COLLAR_HEIGHT)))
    # Only the part under the carrier footprint has something to hang from.
    collar = collar.intersect(cq.Workplane('XY').box(14,22,POSITIVE_COLLAR_HEIGHT).translate(
        (BATTERY_CENTER_X,-8,top-POSITIVE_COLLAR_HEIGHT/2)))
    # Pocket for the 11.2 x 12.0 plate, open toward +Y for the solder tab.
    pw, pd = POSITIVE_PLATE_POCKET
    pocket = cq.Workplane('XY').box(pw,30,pd).translate((BATTERY_CENTER_X,-6.2+15,top-pd/2))
    chassis = chassis.union(collar.cut(pocket))
```

Resulting geometry: ring r 6.0..9.6, Z 86.6..88.5, clipped to X ±7 and Y ≤ 3 about the cell axis; pocket X ±5.8, Y ≥ −6.2, Z 87.9..88.5. The plate (Z 88.0..88.5) bears on the carrier face with 0.1 mm above the pocket floor and 0.2 mm to the pocket walls; the button (Ø5, tip Z 87.0) hangs in the Ø12 opening; the washer (r 5.5, Z 87.7..87.9) clears the ring by 0.5 mm radially. The cell envelope (top Z 85) is 1.6 mm below the ring. The BAT_POS lead's last segment at X = −3, Y 2..8, Z 86.5 lies inside the opening and outside the Y ≤ 3 clip, so it does not touch the ring. Confirm each of these in the fit report rather than assuming them.

Axial float: inside length 72.0 for a 70.0 stack (cell 65.0 + spring end 3.5 + button end 1.5), so the spring lifts the real cell up to 2.0 mm above the `cell_18650` envelope until its cap meets the button. Document this in `cad/ASSEMBLY.md`; do not change geometry for it.

- [ ] **Step 2: Contact envelopes in the assembly**

Replace the two 2 × 2.8 mm cylinders and washers with Keystone envelopes: an 11.2 × 12.0 × 0.5 mm plate on the carrier face, plus a Ø8 × 3.0 mm coil for the spring (5201, compressed) or a Ø5 × 1.0 mm button (5223). Keep the insulating washers.

```python
    for label,z,axis,tip in [('negative',20,(0,0,-1),('coil',4.0,3.0)),('positive',85,(0,0,1),('button',2.5,1.0))]:
        plate=box((11.2,12.0,0.5),(-3,0,z+axis[2]*(3.25)))
        kind,r,length=tip
        contact_body=cylinder(r,length,(-3,0,z+axis[2]*3.0),(0,0,-axis[2]))
        add('cell_'+label+'_contact',plate.fuse(contact_body),'#b9b9b9')
        washer=cylinder(6,.2,(-3,0,z+axis[2]*3.4),axis).cut(cylinder(2.2,.3,(-3,0,z+axis[2]*3.35),axis))
        add('cell_'+label+'_insulator',washer,'#dcad59')
```

Here the carrier faces are at Z = 20 − 3.5 = 16.5 and Z = 85 + 3.5 = 88.5; the plate sits against the face and the coil or button reaches toward the cell end (Z = 20 and 85). The 3.0 mm coil length is the compressed working height, not the 10.5 mm free length. Check the numbers against `e.CONTACT_SPACE` rather than the literals above if the constants differ: plate centre at `z ± (CONTACT_SPACE − 0.25)`, tip starting at `z ± (CONTACT_SPACE − 0.5)`.

The battery lead insulation becomes the 24 AWG pre-crimped PH lead:

```python
BAT_WIRE_OD = 1.4  # JST ASPHSPH24K305, 24 AWG UL1007; not bare copper diameter.
```

Battery route waypoints already start at the J_BAT plug and end at the contact positions (`(-3,2,86.5)` and `(-3,2,18.5)`); if the new plate solids now overlap the wire termination boxes, the existing `contact()` exceptions at the route ends cover a 4 mm cube; confirm the overlap volume is inside it, otherwise move the last waypoint 0.5 mm away from the plate.

- [ ] **Step 3: Build and check**

Run: `.venv/bin/python -m cad.assembly`
Expected: PASS. Watch `cell_18650` against the collar (the cell envelope ends at Z = 85, the collar starts at Z = 86.6, so there must be no overlap) and the contact plates against the carriers (they touch; allow it with a `contact()` exception named `cell contact plate bears on carrier`, bounded by the plate box). That exception must cover a zero-volume touch only; if the fit report shows an overlap volume between `cell_positive_contact` and `chassis`, the pocket is wrong, not the exception.

Also run `.venv/bin/python -m cad.enclosure` (or `uv run cad-generate`) to regenerate `output/` and confirm its own checks pass.

- [ ] **Step 4: Update the documents**

- `cad/ASSEMBLY.md` Battery row: `Keystone 5201 spring and 5223 button contacts on the end carriers, 72.0 mm inside; a 1.9 mm collar around the positive plate stops a reversed cell 0.4 mm short of the button, provided the cell cap protrudes more than 0.4 mm (measure before printing). The sprung cell can sit up to 2.0 mm above the modelled envelope.` Adjustable parameters table: battery-wire insulation 1.4 mm; `POSITIVE_COLLAR_DROP`.
- `context/enclosure-work.md` and `output/README.md`: cell envelope text gains `contacts Keystone 5201/5223, carriers 3.5 mm beyond each end`.

- [ ] **Step 5: Report**

Run: `git diff --stat`
Report the collar height used, the gap between the cell envelope and the collar, and the plate-to-pocket clearances from the fit report.

---

### Task 5: Regenerate previews and record the fit report

**Files:**
- Modify: `cad/ASSEMBLY.md` (harness table if lengths changed)

- [ ] **Step 1: Rebuild everything once more**

Run: `.venv/bin/python -m cad.enclosure && .venv/bin/python -m cad.assembly && .venv/bin/python -m cad.test_assembly && .venv/bin/python hardware/pcb/design.py`
Expected: all pass; `fit-report.json` status PASS.

- [ ] **Step 2: Render previews**

Run: `.venv/bin/python -m cad.preview output/full-assembly/open.stl output/full-assembly/internals.stl output/full-assembly/*_print.stl output/chassis_print.stl`
(With escalated permissions if the sandbox blocks the display.) Read `output/full-assembly/open_preview.png` and `internals_preview.png` and confirm: the bridge plate sits behind the speaker, two LED domes pass the front wall, the 8-way USB plug sits under the USB board inside the shoe, the two contact plates sit on the cradle ends.

- [ ] **Step 3: Record harness lengths**

Copy the `harnesses` block of `fit-report.json` into the harness table of `hardware/pcb/DESIGN.md` if any centerline changed by more than 2 mm from the values there (USB 43, MIC 48, LED 24, PWR 45, PTT 43, SPK 43, NTC 50, BAT+ 24, BAT− 124).

- [ ] **Step 4: Report**

Run: `git status --short && git diff --stat`
List every file changed and the final `near_pairs` entries under 0.2 mm.
