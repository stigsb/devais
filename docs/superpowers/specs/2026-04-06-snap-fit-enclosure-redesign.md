# Snap-Fit Enclosure Redesign

## Summary

Redesign the DevAIs enclosure from a front/back split with threaded bottom lid to a left/right split with snap-fit closure. This eliminates the threaded lid, simplifies battery access, and consolidates all electronics onto one half.

## Motivation

The original design required a threaded screw-on lid at the bottom for battery replacement, which created an unsolved problem: how to electrically connect the battery negative terminal through a removable lid to the main circuit. By splitting the enclosure left/right instead of front/back, one half becomes a chassis holding all electronics and battery contacts, and the other half is a purely mechanical cover. Battery replacement = pop the cover off.

## Split Orientation

- **Split plane:** X=0 (previously Y=0)
- **Right half (X > 0):** Chassis — all electronics, battery, buttons, ports mount here
- **Left half (X < 0):** Cover — purely mechanical shell, snaps onto chassis

## Bottom Closure

Both halves have a full flat bottom. The enclosure is closed at the bottom with no opening, lid, or threading.

### Removed Components

All bottom lid machinery is removed:

- `create_bottom_lid()` function
- `add_lid_receiver()` function
- `create_thread_ridge()` helper
- All `LID_*` parameters (thread bore, pitch, depth, turns, height, clearance, receiver dimensions, disc diameter/thickness, boss dimensions, coin slot dimensions)

## LEDs

Two RGB LEDs replace the previous three single-color 3mm LEDs.

- **Count:** 2 (was 3)
- **Type:** RGB (was single-color)
- **Positions:** x=+5mm and x=+11mm on the front face
- **Z position:** 10mm from top (unchanged)
- **Hole diameter:** 5mm (standard RGB LED package)
- **Both LEDs are on the right (chassis) half** — no cross-joint wiring needed

### Parameter Changes

- `LED_DIAMETER`: 3.0 -> 5.0
- `LED_SPACING`: 8.0 -> removed (positions are explicit)
- `LED_POSITIONS_X`: new parameter, [5.0, 11.0]
- LED count: 3 -> 2

## Battery Cradle

The 18650 battery (18.6mm diameter x 65mm length) sits lengthwise along the Z axis inside the right (chassis) half.

### Cradle Ribs

- 2-3 half-cylinder arc ribs on the right half interior
- Each rib grips approximately 180 degrees of the battery circumference
- Rib inner radius: 9.5mm (18.6mm / 2 + 0.2mm clearance)
- Rib thickness: 1.5mm
- Rib width (along Z): 3mm
- Positioned along Z to avoid interfering with other internal features
- The cover half provides the other 180 degrees of containment when closed

### Battery Contacts

- **Positive contact (top):** At the upper end of the battery channel, toward the electronics
- **Negative spring (bottom):** Mounted on the bottom interior of the right half
- **Entire electrical path stays on the chassis half** — no electrical connection crosses the snap joint

### Battery Z Positioning

- Battery bottom: rests against bottom interior wall (Z = WALL_THICKNESS + spring clearance)
- Battery top: approximately Z = WALL_THICKNESS + spring_clearance + 65mm
- Must clear the lid receiver zone (now removed) and not interfere with USB-C port (Z=31mm) or power button (Z=44mm) which are on the right wall exterior

## Snap-Fit Joint System

The tongue-and-groove rails and cantilever snap clips move from the left/right walls to the front/back walls, matching the new split orientation.

### Tongue-and-Groove Rails (Alignment)

- Run along full Z height (inset 5mm from top/bottom) on **front and back** wall seams
- **Tongue:** On cover (left) half split face, protruding into chassis half
- **Groove:** Cut into chassis (right) half split face
- Dimensions unchanged: 1.0mm wide x 0.8mm protrusion, 0.15mm per-side clearance

### Cantilever Snap Clips (Retention)

- 4 clips total: 2 on front wall, 2 on back wall
- Z positions: 45mm and 135mm (unchanged)
- **Beams on cover (left) half**, protruding from split face into chassis half
- **Pockets in chassis (right) half**
- Wall center Y positions: front wall at Y = +wall_center, back wall at Y = -wall_center
- Beam/hook/ramp dimensions unchanged

### Clip Orientation Change

Previously clips were at X = +/-wall_center (left/right walls), flexing in Y.
Now clips are at Y = +/-wall_center (front/back walls), flexing in X.

## Speaker Grille and Microphone

These features are on the front face (Y+) and will be split between both halves at X=0.

- The grille hole pattern and mic hole straddle the split line
- Each half gets its portion of the perforated grille holes
- The mic acoustic hole (at x=0) lands exactly on the split line — shift it slightly to x=+1mm so it's fully on the chassis half

### Mic Position Change

- `MIC_X_OFFSET`: new parameter, 1.0mm (was implicitly 0.0)

## Unchanged Features

- Outer shell: octagonal prism, 40mm across, 150mm tall, 1.6mm walls
- Large button: right side (X+), full long-side width, 45mm tall, centered at Z=105mm
- Power button: right side (X+), 8mm diameter, Z=44mm
- USB-C port: right side (X+), 9.5mm x 3.7mm, Z=31mm
- Speaker grille: front face, 80% of long side diameter, upper edge 10mm below LEDs
- Top/bottom edge fillets, vertical edge fillets
- Large button exported as separate STL

## Output Files

- `cad/output/enclosure.stl` — full unsplit enclosure (for reference)
- `cad/output/enclosure_right.stl` — chassis half (was `enclosure_front.stl`)
- `cad/output/enclosure_left.stl` — cover half (was `enclosure_back.stl`)
- `cad/output/large_button.stl` — unchanged
- `cad/output/bottom_lid.stl` — removed

## Implementation Notes

### Code Changes in `enclosure.py`

1. Remove all `LID_*` parameters and `COIN_SLOT_*` parameters
2. Remove `create_thread_ridge()`, `add_lid_receiver()`, `create_bottom_lid()`
3. Update LED parameters and `add_led_holes()` for 2 RGB LEDs at new positions
4. Add battery cradle geometry (`add_battery_cradle()`)
5. Close the bottom of the enclosure (modify hollowing to keep bottom wall intact)
6. Rewrite `split_enclosure()`: split at X=0, move tongue/groove to front/back walls, move snap clips to front/back walls
7. Update `build_enclosure()` to remove `add_lid_receiver()` call
8. Update `main()` to remove lid export, rename half outputs
9. Shift mic hole x position by 1mm
