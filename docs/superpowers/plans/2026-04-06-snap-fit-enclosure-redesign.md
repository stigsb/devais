# Snap-Fit Enclosure Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the DevAIs enclosure to split left/right with snap-fit closure, eliminating the threaded bottom lid and consolidating all electronics onto the right (chassis) half.

**Architecture:** Single file modification to `cad/enclosure.py`. Remove lid/thread machinery, close the bottom, update LEDs to 2x RGB at new positions, add battery cradle ribs, shift mic hole, and rewrite the split+joint system from Y=0 to X=0.

**Tech Stack:** CadQuery (Python), STL export, `uv run cad-generate` + `uv run cad-preview` for verification.

**Spec:** `docs/superpowers/specs/2026-04-06-snap-fit-enclosure-redesign.md`

**Verification:** This is CAD geometry code — there are no unit tests. Verification is done by generating STL files and visually inspecting the preview PNGs. After each task that modifies geometry, run the build and check the output.

---

### Task 1: Remove Lid Machinery

Remove all bottom lid parameters, functions, and references.

**Files:**
- Modify: `cad/enclosure.py:53-71` (parameters), `cad/enclosure.py:123-158` (create_thread_ridge), `cad/enclosure.py:451-522` (add_lid_receiver, create_bottom_lid), `cad/enclosure.py:717` (build_enclosure call), `cad/enclosure.py:742-745` (main lid export)

- [ ] **Step 1: Delete lid parameters (lines 53-71)**

Remove this entire block:

```python
# Bottom Lid
LID_THREAD_BORE = 33.0        # Internal thread major diameter (bore)
LID_THREAD_PITCH = 3.0        # Coarse pitch for FDM printing
LID_THREAD_DEPTH = 1.0        # Thread ridge depth
LID_THREAD_TURNS = 2.5
LID_THREAD_HEIGHT = LID_THREAD_PITCH * LID_THREAD_TURNS  # 7.5mm
LID_THREAD_CLEARANCE = 0.3    # Per-side clearance for printing

LID_RECEIVER_BOTTOM_Z = 2.0   # Start above bottom to clear outer fillet
LID_RECEIVER_HEIGHT = 10.0

LID_DISC_DIAMETER = 36.0      # Round lid filling most of octagonal opening
LID_DISC_THICKNESS = 2.5
LID_BOSS_OD = LID_THREAD_BORE - 2 * LID_THREAD_DEPTH - 2 * LID_THREAD_CLEARANCE
LID_BOSS_HEIGHT = LID_THREAD_HEIGHT

COIN_SLOT_WIDTH = 2.5         # Wide enough for coin edge
COIN_SLOT_DEPTH = 1.2
COIN_SLOT_LENGTH = 22.0
```

- [ ] **Step 2: Delete `create_thread_ridge()` function (lines 123-158)**

Remove the entire function.

- [ ] **Step 3: Delete `add_lid_receiver()` function (lines 451-478)**

Remove the entire function.

- [ ] **Step 4: Delete `create_bottom_lid()` function (lines 480-522)**

Remove the entire function.

- [ ] **Step 5: Remove `add_lid_receiver()` call from `build_enclosure()`**

In `build_enclosure()`, delete this line:

```python
    enclosure = add_lid_receiver(enclosure)
```

- [ ] **Step 6: Remove lid export from `main()`**

Delete these lines from `main()`:

```python
    print("Generating bottom lid...")
    lid = create_bottom_lid()
    cq.exporters.export(lid, str(output_dir / "bottom_lid.stl"))
    print("Exported bottom_lid.stl")
```

- [ ] **Step 7: Verify it still builds**

Run: `uv run cad-generate`
Expected: Generates enclosure.stl, enclosure_front.stl, enclosure_back.stl, large_button.stl (no bottom_lid.stl)

- [ ] **Step 8: Commit**

```bash
git add cad/enclosure.py
git commit -m "Remove threaded bottom lid machinery from enclosure"
```

---

### Task 2: Close the Bottom

Change the hollowing operation so the bottom is a solid wall instead of open.

**Files:**
- Modify: `cad/enclosure.py` — `build_enclosure()` function, hollowing section

- [ ] **Step 1: Modify the inner solid to start at WALL_THICKNESS instead of -1.0**

In `build_enclosure()`, find the hollowing section and change it. The current code starts the inner solid at Z=-1.0 to ensure an open bottom. Change it to start at Z=WALL_THICKNESS so a solid bottom wall remains.

Replace:

```python
    # Hollow out using boolean subtraction (more reliable than .shell() on filleted geometry).
    # Inner solid starts 1mm below Z=0 to ensure open bottom, extends to WALL_THICKNESS below top.
    h_inner = DEVICE_HEIGHT - WALL_THICKNESS

    max_c = DEVICE_WIDTH / 2.0
    h_l = HALF_LONG_SIDE
    pts = [
        (max_c, h_l), (h_l, max_c), (-h_l, max_c), (-max_c, h_l),
        (-max_c, -h_l), (-h_l, -max_c), (h_l, -max_c), (max_c, -h_l)
    ]

    inner_solid = (
        cq.Workplane("XY")
        .workplane(offset=-1.0)
        .polyline(pts).close()
        .offset2D(-WALL_THICKNESS)
        .extrude(h_inner + 1.0)
    )
```

With:

```python
    # Hollow out using boolean subtraction (more reliable than .shell() on filleted geometry).
    # Inner solid starts at WALL_THICKNESS (closed bottom) and extends to WALL_THICKNESS below top.
    h_inner = DEVICE_HEIGHT - 2 * WALL_THICKNESS  # Leave wall at both top and bottom

    max_c = DEVICE_WIDTH / 2.0
    h_l = HALF_LONG_SIDE
    pts = [
        (max_c, h_l), (h_l, max_c), (-h_l, max_c), (-max_c, h_l),
        (-max_c, -h_l), (-h_l, -max_c), (h_l, -max_c), (max_c, -h_l)
    ]

    inner_solid = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)
        .polyline(pts).close()
        .offset2D(-WALL_THICKNESS)
        .extrude(h_inner)
    )
```

- [ ] **Step 2: Update inner fillet selection**

The current code fillets `>Z` (top) edges of the inner solid. Since the inner solid no longer extends below Z=0, the `>Z` selector still picks the top inner edge. No change needed for fillet selectors — they remain correct.

Verify this by reading the fillet code:

```python
    inner_fillet = FILLET_RADIUS - WALL_THICKNESS
    if inner_fillet > 0:
        inner_solid = inner_solid.edges(">Z").fillet(inner_fillet)
        inner_solid = inner_solid.edges("|Z").fillet(inner_fillet)
```

This is still correct — `>Z` selects the top face edges, `|Z` selects vertical edges.

- [ ] **Step 3: Build and verify**

Run: `uv run cad-generate`
Expected: Enclosure now has a solid bottom (no open hole).

Run: `uv run cad-preview cad/output/enclosure.stl --views iso`
Then read the PNG to visually confirm the bottom is closed.

- [ ] **Step 4: Commit**

```bash
git add cad/enclosure.py
git commit -m "Close enclosure bottom with solid wall"
```

---

### Task 3: Update LED Parameters and Function

Change from 3 single-color LEDs to 2 RGB LEDs at new X positions.

**Files:**
- Modify: `cad/enclosure.py` — LED parameters and `add_led_holes()` function

- [ ] **Step 1: Update LED parameters**

Replace:

```python
LED_DIAMETER = 3.0
LED_SPACING = 8.0
LED_TOP_OFFSET = 10.0
```

With:

```python
LED_DIAMETER = 3.0  # 3mm holes for WS2812B-2020 (2mm) with light diffusion margin
LED_POSITIONS_X = [5.0, 11.0]  # Two RGB LEDs, both on right (chassis) half
LED_TOP_OFFSET = 10.0
```

- [ ] **Step 2: Rewrite `add_led_holes()`**

Replace the entire function:

```python
def add_led_holes(enclosure):
    """
    Front side (Y+), 10mm from top.
    2x 3mm holes for WS2812B-2020 RGB LEDs at explicit X positions.
    """
    z_pos = DEVICE_HEIGHT - LED_TOP_OFFSET

    for x_pos in LED_POSITIONS_X:
        hole = (
            cq.Workplane("XZ")
            .workplane(offset=CORNER_COORD)
            .center(x_pos, z_pos)
            .circle(LED_DIAMETER / 2)
            .extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
        )
        enclosure = enclosure.cut(hole)

    return enclosure
```

- [ ] **Step 3: Build and verify**

Run: `uv run cad-generate`
Run: `uv run cad-preview cad/output/enclosure.stl --views front`
Read the PNG. Expected: Two holes near the top-right of the front face (at x=5 and x=11), not three centered holes.

- [ ] **Step 4: Commit**

```bash
git add cad/enclosure.py
git commit -m "Update LEDs to 2x WS2812B-2020 RGB at x=5,11mm"
```

---

### Task 4: Shift Microphone Hole

Move mic from x=0 to x=+1mm so it's fully on the chassis half after the X=0 split.

**Files:**
- Modify: `cad/enclosure.py` — mic parameters and `add_mic_hole_and_mount()` function

- [ ] **Step 1: Add mic X offset parameter**

After the existing mic parameters, add:

```python
MIC_X_OFFSET = 1.0  # Shifted +1mm so hole is fully on chassis half after X=0 split
```

- [ ] **Step 2: Update `add_mic_hole_and_mount()` to use the offset**

In the acoustic hole section, change `.center(0, z_pos)` to `.center(MIC_X_OFFSET, z_pos)`.

In the mounting pocket section, change `.center(0, z_pos)` to `.center(MIC_X_OFFSET, z_pos)`.

Both workplane `.center()` calls need updating:

```python
def add_mic_hole_and_mount(enclosure):
    """
    Front side (Y+), 10mm from bottom.
    Shifted +1mm in X so hole is fully on chassis half after X=0 split.
    Includes acoustic hole and internal mounting pocket.
    """
    z_pos = MIC_BOTTOM_OFFSET

    # 1. External Acoustic Hole
    wp = (
        cq.Workplane("XZ")
        .workplane(offset=CORNER_COORD)
        .center(MIC_X_OFFSET, z_pos)
    )

    acoustic_hole = wp.circle(MIC_HOLE_DIAMETER / 2).extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
    enclosure = enclosure.cut(acoustic_hole)

    # Internal mounting pocket for INMP441 board.
    inner_y = CORNER_COORD - WALL_THICKNESS

    pocket = (
        cq.Workplane("XZ")
        .workplane(offset=inner_y)
        .center(MIC_X_OFFSET, z_pos)
        .rect(MIC_POCKET_WIDTH, MIC_POCKET_HEIGHT)
        .extrude(-MIC_POCKET_DEPTH)
    )

    enclosure = enclosure.cut(pocket)

    return enclosure
```

- [ ] **Step 3: Build and verify**

Run: `uv run cad-generate`
Expected: Mic hole slightly right of center on front face (barely noticeable).

- [ ] **Step 4: Commit**

```bash
git add cad/enclosure.py
git commit -m "Shift mic hole +1mm in X for chassis-side placement"
```

---

### Task 5: Add Battery Cradle

Add half-cylinder cradle ribs inside the right half to hold the 18650 battery.

**Files:**
- Modify: `cad/enclosure.py` — new parameters and new `add_battery_cradle()` function

- [ ] **Step 1: Add battery cradle parameters**

Add after the existing component parameters (after the snap clip parameters):

```python
# Battery cradle (18650: 18.6mm diameter x 65mm length)
BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65.0
BATTERY_CRADLE_RADIUS = BATTERY_DIAMETER / 2 + 0.2  # 0.2mm clearance
BATTERY_CRADLE_THICKNESS = 1.5  # Rib wall thickness
BATTERY_CRADLE_RIB_WIDTH = 3.0  # Rib width along Z axis
BATTERY_CRADLE_BOTTOM_Z = WALL_THICKNESS + 2.0  # 2mm above bottom wall for spring clearance
# Rib Z positions: bottom, middle, top of battery zone (avoiding other internal features)
BATTERY_CRADLE_RIB_Z = [
    BATTERY_CRADLE_BOTTOM_Z + 5.0,           # Near bottom
    BATTERY_CRADLE_BOTTOM_Z + 32.5,          # Middle
    BATTERY_CRADLE_BOTTOM_Z + 60.0,          # Near top
]
```

- [ ] **Step 2: Add `add_battery_cradle()` function**

Add before `build_enclosure()`:

```python
def add_battery_cradle(enclosure):
    """
    Half-cylinder cradle ribs on the right (X>0) interior to hold an 18650 battery.
    The battery sits centered along Z. Ribs grip ~180 degrees.
    The cover half provides the other 180 degrees when closed.
    """
    outer_r = BATTERY_CRADLE_RADIUS + BATTERY_CRADLE_THICKNESS
    inner_r = BATTERY_CRADLE_RADIUS

    for z_pos in BATTERY_CRADLE_RIB_Z:
        # Full ring, then cut away the X<0 half (cover side)
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z_pos)
            .circle(outer_r)
            .circle(inner_r)
            .extrude(BATTERY_CRADLE_RIB_WIDTH)
        )

        # Remove X<0 half — only keep the right-side cradle
        s = 50  # Oversized cutting box
        left_cut = (
            cq.Workplane("XY")
            .transformed(offset=(-s / 2, 0, z_pos + BATTERY_CRADLE_RIB_WIDTH / 2))
            .box(s, s, BATTERY_CRADLE_RIB_WIDTH + 1)
        )
        rib = rib.cut(left_cut)

        enclosure = enclosure.union(rib)

    return enclosure
```

- [ ] **Step 3: Call `add_battery_cradle()` in `build_enclosure()`**

Add after the `add_large_button_feature()` call:

```python
    enclosure = add_battery_cradle(enclosure)
```

- [ ] **Step 4: Build and verify**

Run: `uv run cad-generate`
Run: `uv run cad-preview cad/output/enclosure.stl --views iso`
Read the PNG. Expected: Three half-ring ribs visible inside the enclosure on the right side.

- [ ] **Step 5: Commit**

```bash
git add cad/enclosure.py
git commit -m "Add battery cradle ribs for 18650 on chassis half"
```

---

### Task 6: Rewrite Split and Joint System

Change the split plane from Y=0 to X=0. Move tongue-and-groove to front/back walls. Move snap clips to front/back walls. Rename halves from front/back to right/left.

**Files:**
- Modify: `cad/enclosure.py` — `split_enclosure()` function, snap clip parameter comments

- [ ] **Step 1: Update snap clip parameter comments**

Replace the comment block for snap clips:

```python
# Cantilever snap clips (retention for split halves)
# Beams on back half flex in Y to engage hooks in front half pockets.
```

With:

```python
# Cantilever snap clips (retention for split halves)
# Beams on cover (left) half flex in X to engage hooks in chassis (right) half pockets.
```

And update the tongue-and-groove comment:

```python
# Tongue-and-groove rails (alignment for split halves)
# Runs along full height on left/right wall seams. Critical for thread alignment.
```

With:

```python
# Tongue-and-groove rails (alignment for split halves)
# Runs along full height on front/back wall seams for X=0 split alignment.
```

- [ ] **Step 2: Rewrite `split_enclosure()` completely**

Replace the entire function with:

```python
def split_enclosure(enclosure):
    """
    Split enclosure into right (chassis) and left (cover) halves along X=0.
    Right half (X>0): All electronics, battery, buttons, ports
    Left half (X<0): Purely mechanical cover

    Joint system (no glue, repeatable open/close):
    1. Tongue-and-groove rails along front/back wall seams → alignment
    2. Cantilever snap clips at 2 Z positions per wall → retention
    """
    # --- Step 1: Split into halves at X=0 ---
    s = 300
    pos_x_tool = cq.Workplane("XY").transformed(offset=(s / 2, 0, s / 2 - 50)).box(s, s, s)
    neg_x_tool = cq.Workplane("XY").transformed(offset=(-s / 2, 0, s / 2 - 50)).box(s, s, s)

    right_half = enclosure.cut(neg_x_tool)  # remove X<0 → keep X>0 (chassis)
    left_half = enclosure.cut(pos_x_tool)   # remove X>0 → keep X<0 (cover)

    # Wall center Y for front/back walls
    wall_cy = CORNER_COORD - WALL_THICKNESS / 2  # 19.2mm

    # --- Step 2: Tongue-and-groove rails on front/back walls ---
    # Tongue on cover (left) half split face, groove in chassis (right) half.
    # Runs along Z, inset from top/bottom to avoid fillet zones.
    tongue_z_start = TONGUE_Z_MARGIN
    tongue_z_end = DEVICE_HEIGHT - TONGUE_Z_MARGIN
    tongue_z_len = tongue_z_end - tongue_z_start
    tongue_z_center = (tongue_z_start + tongue_z_end) / 2

    for sign in [1, -1]:  # front (+Y) and back (-Y) walls
        y = sign * wall_cy

        # Tongue: rectangular bar on cover (left) half, protruding from X=0 into chassis half (+X)
        # YZ workplane normal is +X, so extrude(positive) goes in +X
        tongue = (cq.Workplane("YZ").center(y, tongue_z_center)
                  .rect(TONGUE_WIDTH, tongue_z_len)
                  .extrude(TONGUE_HEIGHT))
        left_half = left_half.union(tongue)

        # Groove: matching slot cut into chassis (right) half at X=0 face
        groove = (cq.Workplane("YZ").center(y, tongue_z_center)
                  .rect(GROOVE_WIDTH, tongue_z_len)
                  .extrude(GROOVE_DEPTH))
        right_half = right_half.cut(groove)

    # --- Step 3: Cantilever snap clips on front/back walls ---
    # Snap beams on cover (left) half, pockets in chassis (right) half.
    # Beam attached at top, hook at bottom (free end).
    # 2 per wall (front and back), at Z = 45 and Z = 135.
    snap_z_positions = [45, 135]

    for sign in [1, -1]:  # front (+Y) and back (-Y) walls
        y = sign * wall_cy
        for z_attach in snap_z_positions:
            z_hook = z_attach - SNAP_BEAM_LENGTH  # Free end with hook

            # --- Beam on cover (left) half ---
            # The beam protrudes from the split face (X=0) into the chassis half (+X).
            # It's a thin cantilever that can flex in -X when the hook is pushed.
            beam_x_center = SNAP_BEAM_THICKNESS / 2  # center of beam in +X
            beam_z_center = z_attach - SNAP_BEAM_LENGTH / 2

            beam = (cq.Workplane("XY")
                    .transformed(offset=(beam_x_center, y, beam_z_center))
                    .box(SNAP_BEAM_THICKNESS, SNAP_BEAM_WIDTH, SNAP_BEAM_LENGTH))
            left_half = left_half.union(beam)

            # Hook at free end: additional protrusion in +X
            hook_x_center = SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH / 2
            hook_z_center = z_hook + SNAP_HOOK_HEIGHT / 2

            hook = (cq.Workplane("XY")
                    .transformed(offset=(hook_x_center, y, hook_z_center))
                    .box(SNAP_HOOK_DEPTH, SNAP_BEAM_WIDTH, SNAP_HOOK_HEIGHT))
            left_half = left_half.union(hook)

            # Ramp on hook: angled lead-in for easy insertion.
            ramp_z_center = z_hook + SNAP_HOOK_HEIGHT + SNAP_HOOK_RAMP / 2
            ramp = (cq.Workplane("XY")
                    .transformed(offset=(hook_x_center, y, ramp_z_center))
                    .box(SNAP_HOOK_DEPTH, SNAP_BEAM_WIDTH, SNAP_HOOK_RAMP))
            left_half = left_half.union(ramp)

            # Cut the ramp into a wedge shape: full hook depth at bottom, zero at top.
            ramp_cut_angle = math.atan2(SNAP_HOOK_DEPTH, SNAP_HOOK_RAMP)
            ramp_cut_size = SNAP_HOOK_RAMP + SNAP_HOOK_DEPTH
            ramp_cut = (cq.Workplane("YZ")
                        .transformed(
                            offset=(SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH,
                                    y,
                                    ramp_z_center),
                            rotate=(math.degrees(ramp_cut_angle), 0, 0))
                        .box(ramp_cut_size, SNAP_BEAM_WIDTH + 1, ramp_cut_size))
            left_half = left_half.cut(ramp_cut)

            # --- Pocket in chassis (right) half ---
            pocket_x_depth = SNAP_POCKET_DEPTH
            pocket_x_center = pocket_x_depth / 2
            pocket_z_len = SNAP_BEAM_LENGTH + 2 * SNAP_CLEARANCE
            pocket_z_center = beam_z_center

            pocket = (cq.Workplane("XY")
                      .transformed(offset=(pocket_x_center, y, pocket_z_center))
                      .box(pocket_x_depth,
                           SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                           pocket_z_len))
            right_half = right_half.cut(pocket)

            # Shallow pocket (beam depth) with deeper notch at hook zone
            shallow_pocket = (cq.Workplane("XY")
                              .transformed(offset=(SNAP_BEAM_THICKNESS / 2, y, pocket_z_center))
                              .box(SNAP_BEAM_THICKNESS + SNAP_CLEARANCE,
                                   SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                                   pocket_z_len))
            right_half = right_half.cut(shallow_pocket)

            # Deep notch at hook zone
            hook_notch_z_len = SNAP_HOOK_HEIGHT + SNAP_HOOK_RAMP + SNAP_CLEARANCE
            hook_notch_z_center = z_hook + hook_notch_z_len / 2
            hook_notch = (cq.Workplane("XY")
                          .transformed(offset=(pocket_x_center, y, hook_notch_z_center))
                          .box(pocket_x_depth,
                               SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                               hook_notch_z_len))
            right_half = right_half.cut(hook_notch)

    return right_half, left_half
```

- [ ] **Step 3: Build and verify**

Run: `uv run cad-generate`
Expected: Build succeeds (may fail — see Step 4 for main() update). If main() still references old names, fix that in Task 7 first, then verify.

---

### Task 7: Update `main()` Output

Rename output files and remove lid export.

**Files:**
- Modify: `cad/enclosure.py` — `main()` function

- [ ] **Step 1: Rewrite `main()` function**

Replace the entire function:

```python
def main():
    output_dir = Path("cad/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating enclosure...")
    enclosure = build_enclosure()
    cq.exporters.export(enclosure, str(output_dir / "enclosure.stl"))
    print("Exported enclosure.stl")

    print("Splitting enclosure for printing...")
    right_half, left_half = split_enclosure(enclosure)
    cq.exporters.export(right_half, str(output_dir / "enclosure_right.stl"))
    print("Exported enclosure_right.stl")
    cq.exporters.export(left_half, str(output_dir / "enclosure_left.stl"))
    print("Exported enclosure_left.stl")

    print("Generating large button...")
    button = create_large_button()
    cq.exporters.export(button, str(output_dir / "large_button.stl"))
    print("Exported large_button.stl")
```

- [ ] **Step 2: Build and generate all STLs**

Run: `uv run cad-generate`
Expected output:
```
Generating enclosure...
Exported enclosure.stl
Splitting enclosure for printing...
Exported enclosure_right.stl
Exported enclosure_left.stl
Generating large button...
Exported large_button.stl
```

- [ ] **Step 3: Preview all outputs**

Run: `uv run cad-preview cad/output/enclosure.stl`
Run: `uv run cad-preview cad/output/enclosure_right.stl`
Run: `uv run cad-preview cad/output/enclosure_left.stl`

Read each preview PNG and verify:
- `enclosure.stl`: Full enclosure with closed bottom, 2 LED holes (right side of front face), battery cradle ribs visible inside
- `enclosure_right.stl`: Chassis half — has button opening, power button, USB-C, LED holes, part of speaker grille, tongue grooves and snap pockets
- `enclosure_left.stl`: Cover half — plain shell, tongue protrusions and snap beams on inner face

- [ ] **Step 4: Commit**

```bash
git add cad/enclosure.py
git commit -m "Rewrite split to X=0, update outputs for snap-fit redesign"
```

---

### Task 8: Update Documentation

Update the enclosure spec and work files to reflect the new design.

**Files:**
- Modify: `context/enclosure-spec.md` — split section, LED section, bottom lid section

- [ ] **Step 1: Update the split section in enclosure-spec.md**

In section 3.5 "Split for 3D Printing", update:

Replace:

```markdown
## 3.5. Split for 3D Printing

The enclosure is split lengthwise at Y=0 into front and back halves for FDM printing.

### 3.5.1. Why Split?
- Printing a hollow octagonal tube upright produces excessive internal support material
- Two half-shells print flat on the bed with no supports needed

### 3.5.2. Split Plane: Y=0
- **Front half (Y>0):** LEDs, mic hole, speaker grille
- **Back half (Y<0):** plain back panel
- Right-side features (power button, USB-C, large button) are split symmetrically between halves — standard for two-piece enclosures
- Print each half with the outer flat face (long side) down on the bed
```

With:

```markdown
## 3.5. Split for 3D Printing

The enclosure is split lengthwise at X=0 into right (chassis) and left (cover) halves for FDM printing.

### 3.5.1. Why Split?
- Printing a hollow octagonal tube upright produces excessive internal support material
- Two half-shells print flat on the bed with no supports needed
- All electronics mount on one half (chassis), making assembly and battery replacement easy

### 3.5.2. Split Plane: X=0
- **Right half (X>0) — Chassis:** Large button, power button, USB-C, LEDs, battery cradle, all electronics
- **Left half (X<0) — Cover:** Purely mechanical shell, snaps onto chassis
- Front-face features (speaker grille, mic) are split between halves at X=0
- Mic hole shifted to x=+1mm so it's fully on the chassis half
- Print each half with the outer flat face (long side) down on the bed
```

- [ ] **Step 2: Update snap-fit section comments**

In section 3.5.3, update the description to reference cover/chassis and front/back walls instead of front/back halves and left/right walls. Update 3.5.3.1 to say rails are on front/back wall seams. Update 3.5.3.2 to say clips are on front/back walls with beams on cover half, pockets in chassis half.

- [ ] **Step 3: Remove or update the Battery Compartment section (3.4)**

Replace:

```markdown
## 3.4. Battery Compartment

**Status:** Removed for now (hollow interior provides space)
- Placeholder function exists in code
- TODO: Design proper battery holder, contacts, and wire routing when needed
- 18650 battery (18.6mm × 65mm) fits comfortably in 35mm interior space
```

With:

```markdown
## 3.4. Battery Compartment

- 18650 battery (18.6mm × 65mm) held by half-cylinder cradle ribs on chassis (right) half
- 3 ribs at Z positions near bottom, middle, and top of battery zone
- Rib inner radius: 9.5mm (battery radius + 0.2mm clearance), thickness: 1.5mm
- Cover half provides the other 180° containment when snapped on
- Positive contact at top, negative spring at bottom interior of chassis half
- Entire electrical path stays on chassis half — no cross-joint wiring
```

- [ ] **Step 4: Update LED section in enclosure-spec.md**

In section 1.2.2.1 (Three small LEDs), update to reflect two RGB LEDs at new positions:

Replace the LED subsection title and content to describe 2x WS2812B-2020 at x=+5mm and x=+11mm, 3mm holes, 10mm from top.

- [ ] **Step 5: Commit**

```bash
git add context/enclosure-spec.md
git commit -m "Update enclosure spec for snap-fit redesign"
```

---

### Task 9: Final Verification

End-to-end build and visual check of all outputs.

**Files:**
- No modifications — verification only

- [ ] **Step 1: Clean build**

Run: `rm -f cad/output/*.stl && uv run cad-generate`
Expected: All 4 STL files generated (enclosure.stl, enclosure_right.stl, enclosure_left.stl, large_button.stl)

- [ ] **Step 2: Preview all models**

Run: `uv run cad-preview cad/output/*.stl`

Read each preview PNG and check:

1. **enclosure.stl**: Full octagonal prism, closed bottom, 2 LED holes at top-right of front face, speaker grille, mic hole (slightly right of center), button opening on right side, power button + USB-C on right side, battery cradle ribs visible inside
2. **enclosure_right.stl**: Chassis half with all features, groove slots on front/back inner faces, snap pockets visible
3. **enclosure_left.stl**: Clean cover half, tongue rails on front/back inner faces, snap beams protruding from inner face
4. **large_button.stl**: Unchanged — beveled button with dot texture

- [ ] **Step 3: Verify no bottom_lid.stl**

Run: `ls cad/output/`
Expected: No `bottom_lid.stl` in the output.
