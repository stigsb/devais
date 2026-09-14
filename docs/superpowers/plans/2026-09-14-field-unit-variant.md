# Field Unit Enclosure Variant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `field` build variant of the enclosure and assembly model in which a stripboard carrying a Seeed XIAO nRF52840 Sense and a MAX98357A breakout replaces the custom main PCB, an Adafruit 3492 PDM microphone breakout sits in an enlarged mic seat, and the XIAO's USB-C exits through the top end wall.

**Architecture:** `cad/enclosure.py` and `cad/assembly.py` gain a `variant` argument (`'product'` default, `'field'`) threaded through the build functions and selected on the command line with `--variant field`. Product geometry and the product fit report must not change. Field outputs go to `output/field-unit/`. Everything the field unit shares with the product (cell cradle, contacts, speaker, bridge, LED board, PTT and power carriers, cover) is reused unchanged.

**Tech Stack:** Python 3, CadQuery, the existing `cad/assembly.py` fit checker (`.venv/bin/python -m cad.assembly`), `uv run cad-preview`.

**Spec:** `hardware/PROTOTYPE.md`, section "Field unit" (M2 microphone option chosen by the user on 2026-09-14), plus the decisions below.

## Global Constraints

- Do not commit or stage anything. The user reviews and commits.
- Product outputs must be unchanged: `.venv/bin/python -m cad.enclosure` and `.venv/bin/python -m cad.assembly` (no flag) must still pass, and `output/full-assembly/fit-report.json` must still be `PASS` with the same harness centerlines.
- No new `contact()` exceptions beyond the ones the route loop already registers automatically at each wire end. If a field part overlaps something, move the part or waypoint; do not add an exception.
- All dimensions in mm. Coordinate system: Z is device height (0 bottom, 150 top), X+ is the button side, Y− is the audio side, the chassis is the X+/Y− half of the diagonal seam `X − Y = −4`.
- Build times: an assembly build takes about 2.5 minutes. Run it in the foreground with a 600000 ms timeout.
- If `uv run cad-preview` fails with a display error, run `caffeinate -u -t 3` first and retry; this is a sleeping display, not a sandbox problem.
- Comments and doc text stay short and factual. No debugging diary.

## Design decisions (from the spec)

- DF1 The XIAO is soldered flat to the stripboard by its castellations, no header. Reason: its two pad rows are 17.78 mm apart, which lands on the PCB rails at Y = ±7.75…12.25 if pins protrude behind the board, and flat mounting puts the USB-C receptacle at X ≈ 7.05 so the top-wall opening lies entirely on the chassis side of the seam.
- DF2 The stripboard is 25.4 × 135 × 1.6 mm at the main-PCB position, Z 12…147, drilled with the ten existing hole positions and two 8 mm wide windows at Y = 0: one under the XIAO's central BAT+/BAT− pads (Z 130.3…142.3), one where the two cell leads return to the front (Z 113…126). The leads run down the channel between the rails behind the board.
- DF3 The MAX98357A breakout (19.4 × 17.8 × 3.0 mm) stands on one 7-pin header row at Y = 6.1, pins clipped behind the board inside the rail channel; board spans Y −10.4…7.4, Z 92…111.4. Speaker pads on its Y− edge.
- DF4 The Adafruit 3492 (14.0 × 12.8 × 2.8 mm) sits in the mic seat with its top-port MP34DT01 facing the wall, at the same board plane as the product mic board. The seat pocket grows with the board and is also cut from the negative cell carrier, which it now overlaps at Z 14.5…16.5.
- DF5 No reset switch and no NTC in the field unit. The power carrier, switch and cap stay as printed parts, unwired. The USB side opening and shoe are omitted from the field chassis (no blank needed).
- DF6 LEDs: the product LED board and two emitters stay; one RGB LED (4 wires) plus one single-colour LED sharing the anode (1 wire) gives a 5-conductor LED lead, soldered, no header.
- DF8 (2026-09-14 ruling) The stripboard's Y+ top corner (Y ≥ 9, Z ≥ 140) is notched to clear the seam pin pad at (18.8, 144.5).
- DF9 (2026-09-14 ruling, final) The amp header pins are clipped to 1.5 mm behind the board (X 11.55…13.05). The PTT lead descends at X 15.0, runs along Y at X 15.0 to Y 4.2, then 2.1 mm along X to the switch terminals (the 2 mm bend radius needs a final segment of at least 2.0 mm, which rules out X below 14.9). Bundle clears the pins by 1.0 mm and the switch body by 0.6 mm. The lead crosses the PTT rail tape at Y 7.6…7.75, so the PTT tunnel also cuts the `PTT_rail_tape_*` parts. The tunnel (radius 1.16) reaches X 16.16 against the rail's back face at 16.3: the remaining 0.14 mm skin will not print, so the PTT lead lies in a groove open toward the wall (2.1 mm gap). Accepted; documented in Task 3.
- DF7 Top-wall USB-C opening: 7.5 (X) × 13 (Y) mm, corner radius 2, centred at X 7.05, Y 0. Its nearest corner to the seam is at X 3.3, Y 6.5, where X − Y = −3.2, 0.8 mm on the chassis side of the seam.

## File map

- Modify `cad/enclosure.py`: constants, `mic_board_size()`, `add_top_usbc_port()`, `field_stripboard_envelope()`, `field_stripboard_template()`, `variant` argument on `build_enclosure`, `add_component_mounts`, `split_enclosure`, `check_assembly`, `main`.
- Modify `cad/assembly.py`: module-level `PRODUCT_ROUTES` and `FIELD_ROUTES`, `variant` argument on `build`, `motion_checks(parts, board)`, `main` with `--variant`.
- Modify `cad/test_assembly.py`: route bend check over both route tables.
- Modify `cad/ASSEMBLY.md`, `hardware/PROTOTYPE.md`, `context/enclosure-work.md`: field-unit section and decisions.

---

### Task 1: Enclosure variant (chassis features and checks)

**Files:**
- Modify: `cad/enclosure.py` (constants near line 103, `add_usbc_port` near line 272, `board_envelope` line 441, `add_component_mounts` lines 451–512, `split_enclosure` line 529, `check_assembly` line 566, `build_enclosure` line 599, `main` line 671)

**Interfaces:**
- Produces: `build_enclosure(variant='product')`, `split_enclosure(enclosure, variant='product')`, `check_assembly(chassis, cover, variant='product')`, `mic_board_size(variant='product') -> (w, h)`, `field_stripboard_envelope()`, `field_stripboard_template()`, constants `FIELD_MIC_BOARD`, `FIELD_TOP_USBC`, `FIELD_BOARD_WIDTH`, `FIELD_BOARD_HEIGHT`, `FIELD_BOARD_WINDOWS`. Task 2 calls all of these.

- [ ] **Step 1: Record the product baseline**

Run:
```bash
.venv/bin/python -c "from cad import enclosure as e; c,v=e.split_enclosure(e.build_enclosure()); print(round(c.val().Volume(),3), round(v.val().Volume(),3))"
```
Write the two numbers into your report. They must be reproduced exactly at Step 6.

- [ ] **Step 2: Constants and helpers**

After `MIC_BOARD_WIDTH, MIC_BOARD_HEIGHT = 15.0, 8.0` (line 103) add:

```python
# Field-unit variant (hardware/PROTOTYPE.md): stripboard carrier, XIAO nRF52840
# Sense, Adafruit 3492 PDM microphone breakout. Product geometry is unchanged.
FIELD_MIC_BOARD = (14.0, 12.8)  # Adafruit 3492 outline; the product board is 15 x 8
FIELD_TOP_USBC = (7.05, 0.0, 7.5, 13.0, 2.0)  # centre X, centre Y, X size, Y size, corner radius
FIELD_BOARD_WIDTH, FIELD_BOARD_HEIGHT = 25.4, 135.0  # 1 in stripboard, Z 12..147
FIELD_BOARD_WINDOWS = ((136.3, 12.0), (119.5, 13.0))  # (centre Z, Z size), 8 mm wide at Y = 0


def mic_board_size(variant='product'):
    return FIELD_MIC_BOARD if variant == 'field' else (MIC_BOARD_WIDTH, MIC_BOARD_HEIGHT)
```

After `add_usbc_port` add:

```python
def add_top_usbc_port(enclosure):
    """Field unit: the XIAO USB-C exits through the top end wall, chassis side of the seam."""
    cx, cy, sx, sy, r = FIELD_TOP_USBC
    tool = (
        cq.Workplane("XY")
        .workplane(offset=DEVICE_HEIGHT + CUT_OVERSHOOT)
        .center(cx, cy)
        .rect(sx, sy)
        .extrude(-(WALL_THICKNESS + 2 * CUT_OVERSHOOT))
        .edges("|Z")
        .fillet(r)
    )
    return enclosure.cut(tool)
```

After `board_envelope` add:

```python
def field_stripboard_envelope():
    z = PCB_Y_OFFSET - PCB_HEIGHT/2 + FIELD_BOARD_HEIGHT/2
    board = cq.Workplane('XY').box(PCB_THICKNESS, FIELD_BOARD_WIDTH, FIELD_BOARD_HEIGHT).translate(
        (PCB_FACE_X - PCB_THICKNESS/2, 0, z))
    # Notch the Y+ top corner: the seam pin pad at (18.8, 144.5) reaches Y 9.43 at
    # Z 140.9..147. The XIAO's Y+ castellation row at Y 8.89 keeps board under it.
    return board.cut(cq.Workplane('XY').box(5, 5, 10).translate((PCB_FACE_X - PCB_THICKNESS/2, 11.5, 145)))


def field_stripboard_template():
    """Stripboard drilling template: the ten PCB holes plus two lead windows."""
    board = field_stripboard_envelope()
    for y, z in PCB_MOUNTING_HOLES:
        board = board.cut(cq.Workplane('YZ', origin=(PCB_FACE_X+1, y, z+PCB_Y_OFFSET)).circle(1.1).extrude(-5))
    for zc, zs in FIELD_BOARD_WINDOWS:
        board = board.cut(cq.Workplane('XY').box(PCB_THICKNESS+1, 8, zs).translate((PCB_FACE_X - PCB_THICKNESS/2, 0, zc)))
    return board
```

- [ ] **Step 3: Thread `variant` through the build**

`build_enclosure(variant='product')`: replace the feature calls at the end with

```python
    enclosure = add_led_holes(enclosure)
    enclosure = add_mic_hole_and_mount(enclosure)
    enclosure = add_speaker_grille(enclosure)
    enclosure = add_power_button(enclosure)
    if variant == 'field':
        enclosure = add_top_usbc_port(enclosure)
    else:
        enclosure = add_usbc_port(enclosure)
    enclosure = add_large_button_feature(enclosure)
```

`add_component_mounts(chassis, variant='product')`: the seat loop (lines 505–512) becomes

```python
    mic_w, mic_h = mic_board_size(variant)
    for x,z,w,h in ((MIC_X_OFFSET,MIC_BOTTOM_OFFSET,mic_w,mic_h),
                    (LED_BOARD_X,DEVICE_HEIGHT-LED_TOP_OFFSET,LED_BOARD_WIDTH,LED_BOARD_HEIGHT)):
        seat = cq.Workplane('XY').box(w+4,3.5,h+4).translate((x,-17.5,z))
        pocket = cq.Workplane('XY').box(w+MOUNT_CLEARANCE,4,h+MOUNT_CLEARANCE).translate((x,-15.0,z))
        # Preserve the acoustic/light path through the center of the seat.
        window = cq.Workplane('XY').box(w-2,8,h-2).translate((x,-18,z))
        seat = seat.cut(pocket).cut(window)
        # The pocket is also cut from the chassis: the 12.8 mm field mic board
        # overlaps the negative cell carrier. No-op for the product boards.
        chassis = chassis.cut(pocket).union(seat)
```

`split_enclosure(enclosure, variant='product')`: line 551 becomes `chassis = chassis.union(add_component_mounts(chassis, variant).intersect(envelope))`.

`check_assembly(chassis, cover, variant='product')`: the PCB envelope line becomes

```python
    board = field_stripboard_envelope() if variant == 'field' else board_envelope()
    for name, envelope in [('PCB',board),('battery',battery_envelope())]:
```
and the daughterboard loop uses `mic_w, mic_h = mic_board_size(variant)` with `(MIC_X_OFFSET,MIC_BOTTOM_OFFSET,mic_w,mic_h)` in place of the product constants. The later `for solid in (chassis,cover,board_envelope(),battery_envelope())` line uses `board` instead of `board_envelope()`.

- [ ] **Step 4: Command line and outputs**

Replace `main()`:

```python
def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=('product', 'field'), default='product')
    variant = parser.parse_args(argv).variant
    output_dir = Path('output') if variant == 'product' else Path('output/field-unit')
    output_dir.mkdir(parents=True, exist_ok=True)
    chassis, cover = split_enclosure(build_enclosure(variant), variant)
    check_assembly(chassis, cover, variant)
    for name, part in [('chassis',chassis),('cover',cover)]:
        for suffix, shape in [('assembled',part),('print',print_orientation(part,name=='cover'))]:
            path = output_dir / f'{name}_{suffix}'
            export_stl(shape, path.with_suffix('.stl'))
            cq.exporters.export(shape, str(path.with_suffix('.step')))
            print(f'Exported {path}: one valid solid', flush=True)
    if variant == 'field':
        cq.exporters.export(field_stripboard_template(), str(output_dir/'stripboard_template.step'))
        print('Field-unit enclosure checks passed', flush=True)
        return
    for name, part in zip(('fit_pins','fit_sockets'), fit_coupon()):
        export_stl(part, output_dir/f'{name}.stl')
    template = board_envelope()
    for y, z in PCB_MOUNTING_HOLES:
        template = template.cut(cq.Workplane('YZ',origin=(PCB_FACE_X+1,y,z+PCB_Y_OFFSET)).circle(1.1).extrude(-5))
    cq.exporters.export(template,str(output_dir/'pcb_template.step'))
    assembly = cq.Assembly()
    assembly.add(chassis,name='chassis',color=cq.Color(0.6,0.7,0.8))
    assembly.add(cover,name='cover',color=cq.Color(0.7,0.7,0.7))
    assembly.add(template,name='proposed_pcb',color=cq.Color(0.1,0.5,0.2))
    assembly.add(battery_envelope(),name='cell_envelope',color=cq.Color(0.2,0.3,0.8))
    assembly.export(str(output_dir/'assembly.step'))
    print('Assembly checks passed', flush=True)
```

- [ ] **Step 5: Build the field enclosure**

Run: `.venv/bin/python -m cad.enclosure --variant field`
Expected: `Field-unit enclosure checks passed`, files in `output/field-unit/`: `chassis_assembled.stl/.step`, `chassis_print.stl/.step`, `cover_*`, `stripboard_template.step`.

Then verify the opening and the seat with:
```bash
.venv/bin/python -c "
from cad import enclosure as e
import cadquery as cq
c,v=e.split_enclosure(e.build_enclosure('field'),'field')
probe=cq.Workplane('XY').rect(7.4,12.9).extrude(3).edges('|Z').fillet(1.95).translate((7.05,0,147.7))
print('opening clear of chassis:', round(c.intersect(probe).val().Volume(),4))
print('opening clear of cover:', round(v.intersect(probe).val().Volume(),4))
mic=cq.Workplane('XY').box(14,1.6,12.8).translate((1,-16.05,10))
print('mic board clear:', round(c.intersect(mic).val().Volume(),4))
"
```
Expected: all three volumes 0.0. If the mic board volume is not 0, the pocket cut from the chassis in Step 3 is missing or in the wrong order (it must run after the cell carriers are unioned).

- [ ] **Step 6: Product regression**

Run the Step 1 command again (unchanged signature defaults). Expected: identical volumes to three decimals. Then run `.venv/bin/python -m cad.enclosure` and expect `Assembly checks passed`.

- [ ] **Step 7: Report**

Report the baseline and post-change volumes, the three probe volumes, and `git diff --stat`.

---

### Task 2: Assembly variant (field parts, routes, fit report)

**Files:**
- Modify: `cad/assembly.py` (module constants near line 17–31, `build` line 116 onwards, routes dict line 318, `motion_checks` line 395, `main` line 424)
- Modify: `cad/test_assembly.py`

**Interfaces:**
- Consumes from Task 1: `e.build_enclosure(variant)`, `e.split_enclosure(enclosure, variant)`, `e.mic_board_size(variant)`, `e.field_stripboard_template()`.
- Produces: module-level `PRODUCT_ROUTES` and `FIELD_ROUTES` dicts with the existing tuple shape `(count, od, points, start, end)`; `build(variant='product')`; `motion_checks(parts, board='main_PCB')`; `main(argv=None)` accepting `--variant`.

This task is larger than Task 1 and the fit checker may report collisions the plan did not foresee. A waypoint may be moved by up to 1 mm to clear a reported collision; anything larger is a plan defect to escalate.

- [ ] **Step 1: Route tables at module level**

Move the existing `routes={...}` literal (line 318) out of `build` to module level, directly after `LED_SOCKET_X = e.LED_BOARD_X` (line 31), renamed `PRODUCT_ROUTES`, contents unchanged. Then add:

```python
# Field unit (hardware/PROTOTYPE.md): solder terminations on the stripboard, XIAO and
# breakouts; the cell leads leave the XIAO's underside pads through a stripboard window,
# run down the rail channel behind the board and return through a second window.
FIELD_ROUTES = {
    'MIC': (4, WIRE_OD, [(8.9,-4,18),(8.9,-4,12),(1,-4,12),(1,-14.5,12),(1,-14.5,15)], 'field_stripboard','mic_PCB'),
    'PTT': (2, WIRE_OD, [(8.9,4.5,116),(8.9,4.5,120),(8.9,15,120),(15.0,15,120),(15.0,15,105),(15.0,4.2,105),(12.9,4.2,105)], 'field_stripboard','PTT_terminals'),
    'SPK': (2, WIRE_OD, [(6,-11,98),(6,-11,116),(6,-14.3,116)], 'MAX98357A_breakout','speaker'),
    'LED': (5, WIRE_OD, [(8.9,-10.5,120),(8.9,-10.5,124),(3,-10.5,124),(3,-10.5,132),(3,-14.75,132),(3,-14.75,136.5)], 'field_stripboard','LED_PCB'),
    'BAT_POS': (1, BAT_WIRE_OD, [(9.0,-1,136.3),(13.5,-1,136.3),(13.5,-1,118),(-3,-1,118),(-3,8,118),(-3,8,86.5),(-3,2,86.5)], 'XIAO_nRF52840','cell_positive_contact'),
    'BAT_NEG': (1, BAT_WIRE_OD, [(9.0,1,136.3),(13.5,1,136.3),(13.5,1,120),(-3,1,120),(-3,16,120),(-3,16,7),(-3,8,7),(-3,8,18.5),(-3,2,18.5)], 'XIAO_nRF52840','cell_negative_contact'),
}
```

In `build`, the loop header becomes `for name,(count,od,points,start,end) in (FIELD_ROUTES if variant=='field' else PRODUCT_ROUTES).items():`.

- [ ] **Step 2: Test the route tables**

Add to `cad/test_assembly.py` `main()` before the final print:

```python
    from cad.assembly import PRODUCT_ROUTES, FIELD_ROUTES, BAT_WIRE_OD, BEND_RADIUS
    for table in (PRODUCT_ROUTES, FIELD_ROUTES):
        for name,(count,od,points,start,end) in table.items():
            rounded_path(points, 4.0 if od==BAT_WIRE_OD else BEND_RADIUS)
            assert len(bundle_offsets(count, od)) == count, name
```
Adjust the import line at the top of the file so `rounded_path` and `bundle_offsets` are imported if they are not already.

Run: `.venv/bin/python -m cad.test_assembly`
Expected: `Cable bend and collision regression checks passed`. If `rounded_path` raises for a field route, report which route and segment; the plan's segment lengths were checked against the 2 mm (4 mm for battery leads) bend rule, so a failure here is a plan defect.

- [ ] **Step 3: `build(variant)` and the field parts**

Signature `def build(variant='product'):`. First line: `chassis, cover = e.split_enclosure(e.build_enclosure(variant), variant)`. After the `add`/`contact` helpers set `board = 'main_PCB' if variant == 'product' else 'field_stripboard'`.

Wrap the product electronics in `if variant == 'product':` — that is `add('main_PCB', ...)` (line 132), the `placements` block through `add('J_SPK', ...)` (lines 135–148). Keep the `PCB_M2_*` screw loop for both variants (the stripboard uses the same stations). Add the field branch:

```python
    else:
        add('field_stripboard', e.field_stripboard_template(), '#8a6d3b')
        # XIAO nRF52840 Sense soldered flat by its castellations, USB-C end at the top wall.
        add('XIAO_nRF52840', box((4.46,17.78,21.0),(7.67,0,136.3)), '#24784a')
        add('XIAO_USBC', box((3.21,8.94,1.5),(7.045,0,147.55)), '#8f8f8f')
        # MAX98357A breakout on one 7-pin header row at Y = 6.1; pins clipped in the rail channel.
        add('MAX98357A_breakout', box((5.5,17.8,19.4),(7.15,-1.5,101.7)), '#24784a')
        add('amp_header_pins', box((1.5,1.0,15.24),(12.3,6.1,101.7)), '#8f8f8f')  # clipped 1.5 mm behind the board
```

The USB receptacle, `USB_PCB`, `USB_J_SH_mated` and `USB_shoe` block (lines 164–184, from `# USB-C daughterboard` or equivalent comment to `prints['USB_shoe']=shoe`) goes inside `if variant == 'product':`.

Mic block: replace `w,h=e.MIC_BOARD_WIDTH,e.MIC_BOARD_HEIGHT` (or the equivalent at line 140) with `w,h=e.mic_board_size(variant)`; keep `mic_PCB` and `mic_gasket` for both variants; put `add('IM69D130', ...)` and `add('mic_J_SH_mated', ...)` under `if variant == 'product':` and add

```python
    else:
        # Adafruit 3492: top-port MP34DT01 faces the wall inside the seat window.
        add('mic_MP34DT01', box((3,1.2,4),(1,-17.45,10)), '#d0d0d0')
```

`add('LED_J_SH_mated', ...)` (line 179) and `add('NTC', ...)` (line 276): product only. LED emitters, speaker, gasket, bridge, cell, contacts, carriers, switches, caps: both variants, unchanged.

Route loop: as in Step 1. In the tunnel branch `if name in ('USB','PWR','PTT')`, after the carrier cut add `for tape in [k for k in parts if k.startswith(name+'_rail_tape')]: parts[tape]=parts[tape].cut(tunnel)` so the PTT lead may pass the adhesive strip between the carrier wing and the rail (DF9). Product geometry is unaffected: the product PTT lead does not cross its tapes.

- [ ] **Step 4: `motion_checks` and `main`**

`def motion_checks(parts, board='main_PCB'):` and in the button loop replace `'main_PCB'` with `board`. `build` returns the same tuple as now; `main` passes the board name:

```python
def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=('product','field'), default='product')
    variant = parser.parse_args(argv).variant
    out = OUT if variant == 'product' else Path('output/field-unit')
    out.mkdir(parents=True,exist_ok=True)
    (out/'fit-report.json').write_text(json.dumps({'status':'BUILDING'})+'\n')
    parts,colors,contacts,prints,lengths=build(variant)
    errors,distances=inspect(parts,contacts)
    if not errors:
        print('Static fit passed; checking cover and button travel',flush=True)
        errors.extend(motion_checks(parts,'main_PCB' if variant=='product' else 'field_stripboard'))
```
and every later `OUT/` in `main` becomes `out/`. Add `'variant': variant` to the report dict.

- [ ] **Step 5: Field build**

Run: `.venv/bin/python -m cad.assembly --variant field` (timeout 600000)
Expected: `Static fit passed`, then `PASS`, `output/field-unit/fit-report.json` with `"status": "PASS"`, `"errors": []`, six harness entries.

If `inspect` reports overlaps, read the pair names and gap, fix by moving the offending waypoint by at most 1 mm (see the task preamble), rebuild. Expected near pairs under 0.5 mm that are acceptable: `mic_PCB`/wire_MIC (0.35), `LED_PCB`/wire_LED (0.1), `MAX98357A_breakout`/wire_SPK (0.2), `field_stripboard`/chassis rail faces (0), `XIAO_USBC`/chassis (0.1).

- [ ] **Step 6: Product regression**

Run: `.venv/bin/python -m cad.assembly` (timeout 600000)
Expected: PASS. Compare `output/full-assembly/fit-report.json` `harnesses` centerlines with the values before your change (record them first with `python3 -c "import json;print({k:v['centerline_mm'] for k,v in json.load(open('output/full-assembly/fit-report.json'))['harnesses'].items()})"`): identical.

- [ ] **Step 7: Report**

Report: field fit-report status and error count, the near-pair list under 0.5 mm, every waypoint you moved and why, product centerlines before and after, `git diff --stat`.

---

### Task 3: Previews and documents

**Files:**
- Modify: `cad/ASSEMBLY.md`, `hardware/PROTOTYPE.md` (section "Field unit"), `context/enclosure-work.md`
- Create: `output/field-unit/*_preview.png` (gitignored)

- [ ] **Step 1: Render previews**

Run: `uv run cad-preview output/field-unit/chassis_print.stl output/field-unit/open.stl output/field-unit/internals.stl` (prefix with `caffeinate -u -t 3 &&` if the first attempt fails on display access). Read each PNG. Confirm visually: the top-wall opening is at the X+ side of the top face, the XIAO envelope ends just below it, the amp envelope sits above the cell, the mic board fills the enlarged seat at the bottom front, the two cell leads run behind the board.

- [ ] **Step 2: `cad/ASSEMBLY.md`**

Add a section "Field-unit variant" after the parts table:

```markdown
## Field-unit variant

`python -m cad.enclosure --variant field` and `python -m cad.assembly --variant field`
write to `output/field-unit/`. The main PCB, its connectors, the USB daughterboard,
shoe and side opening, the NTC and the radio module are replaced by a 25.4 × 135 mm
stripboard (`stripboard_template.step`: ten M2 holes, two 8 mm lead windows) carrying a
flat-soldered XIAO nRF52840 Sense (Z 125.8…146.8, USB-C through a 7.5 × 13 mm opening
in the top wall at X 7.05) and a MAX98357A breakout on one header row (Z 92…111.4).
The microphone is an Adafruit 3492 breakout in a 14 × 12.8 mm seat. Six leads:
MIC 4, PTT 2, SPK 2, LED 5, BAT+ 1, BAT− 1. Everything else is the product geometry.
The power switch is fitted but unwired.
```

Add `FIELD_TOP_USBC`, `FIELD_BOARD_WINDOWS` and `FIELD_MIC_BOARD` to the adjustable parameters table with one-line descriptions.

- [ ] **Step 3: `hardware/PROTOTYPE.md`**

In the "Field unit" section: replace the "Microphone: two options, decision needed." paragraph and the M1/M2 bullets with `Microphone: M2, an Adafruit 3492 PDM breakout (14.0 × 12.8 × 2.8 mm) in the enlarged bottom-front seat, MP34DT01 port toward the wall, wired to D6/D7. Decided 2026-09-14.` Update the field-unit table: XIAO row → `Soldered flat by its castellations at Z 125.8–146.8; USB-C through a 7.5 × 13 mm opening in the top wall; BAT+/BAT− leads soldered from behind through an 8 × 12 mm stripboard window`; MAX98357A row → `Z 92–111.4 on one 7-pin header row at Y = 6.1, pins clipped behind the board`; Reset switch row → `Not fitted; the power carrier and cap stay as blanks`; RGB LED row → `One RGB LED and one single-colour LED on D10 on the product LED board, 5-wire lead`; USB-C side opening row → `Not cut in the field chassis`. Replace the closing "Enclosure changes for the field unit" paragraph with: `The field variant is built with `--variant field` in `cad/enclosure.py` and `cad/assembly.py`; see `cad/ASSEMBLY.md`.` Correct the stripboard size to 25.4 × 135 × 1.6 mm and the Adafruit 3492 size to 14.0 × 12.8 mm wherever the section states them. Also correct the bench parts table's "Stripboard" row to at least 25 × 140 mm usable.

- [ ] **Step 4: `context/enclosure-work.md`**

Add one line under the current-state notes: `Field-unit variant (--variant field) models the XIAO/stripboard prototype in the product chassis; product outputs unchanged. Plan: docs/superpowers/plans/2026-09-14-field-unit-variant.md.`

- [ ] **Step 5: Report**

Run `git diff --stat`. Report the preview files rendered and any visual anomaly.
