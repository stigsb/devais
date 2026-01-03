# 1. Reference Image Analysis - DevAIs Enclosure

## 1.1. Overall Form ✅ REVIEWED

### 1.1.1. Cross-Section (Octagonal Prism)
- **NOT cylindrical** - octagonal cross-section
- **Dimensions:** 40mm across × 150mm tall
- **Octagon structure:**
  - Formed like a **square with chamfered/beveled corners at 45°**
  - 4 longer sides (the main square faces)
  - 4 shorter sides (the 45° chamfers at each corner)
  - Ratio between longer sides and shorter sides/chamfers is 7:3
  - Alternating pattern: long side → short chamfer → long side → short chamfer...
  - Each beveled corner is **slightly rounded** (4mm diameter)

### 1.1.2. Vertical Profile
- **Height:** 150mm
- **Top edge:** rounded/filleted (4mm diameter)
- **Bottom edge:** rounded/filleted (4mm diameter)

### 1.1.3. Visual Effect
- Basically a **square stick with softened/chamfered corners**
- The 45° chamfers make it more comfortable to hold than a pure square
- The rounded edges add to the ergonomic feel

### 1.1.4. Colour
- The main body is industrial grey

### 1.1.5. Thickness
- 1.6mm thickness - practical for following USB-C port spec

---

## 1.2. Components and Features ✅ REVIEWED

### 1.2.1. Names / Designations ✅ REVIEWED
- **Orientation:**
  - The enclosure runs length-wise along the Y axis.
  - The front/back sides are separated along the Z axis.
  - The left/right sides are separated along the X axis.
- **Front:**
  - One of the long sides is designated as the "front" side.
  - The "right" side is the long side to the right of the "front" side when camera points
    perpendicularly at the front side.

### 1.2.2. Top Section of Front Side ✅ REVIEWED

#### 1.2.2.1. Three small LEDs
  - On front side, centered on a line running along the X axis 10mm from the top
  - Arranged horizontally in a line on the front side, 10mm from the top
  - 3mm LEDs
  - Centered on the horizontal line, 8mm between the center of each LED

#### 1.2.2.2. Microphone Hole and Support

Microphone is a INMP441. It should be centered 10mm from the bottom of the front side, behind a 1.5mm acoustic hole.
There needs to be support structure behind the hole, as described in the following technical details the INMP441:

<part_description>
 <part>INMP441</part>
 <type>high-performance, low power, digital-output, omnidirectional MEMS microphone with a bottom port</type>
 <dimensions>
  Overall Size:
  - Length: 4.72mm
  - Width: 3.76mm
  - Height: 1.00mm (0.88-1.05mm tolerance)
 </dimensions>
 <acoustic_port>
  At bottom of the part.
  - Port diameter: 0.25mm (at microphone)
  - Recommended PCB hole: 0.5-1.0mm diameter
  - Port location: Centered on bottom of package
  - Inner ring diameter: 0.96mm
  - Outer ring diameter: 1.56mm
 </acoustic_port>

 <support_structure_design_requirements>
  1. Mounting Footprint:
     - Create a 4.72mm × 3.76mm pocket or platform
     - Consider adding ~0.2mm clearance for 3D print tolerances
  2. Acoustic Port Opening:
     - Must have a through-hole of at least 0.5-1.0mm diameter aligned with the mic center
     - The sound port MUST NOT be blocked - this is critical for functionality
     - Position this hole at the center of the 4.72mm × 3.76mm footprint
  3. Pin Locations (9 pins total):
     - 8 rectangular pads (0.40mm × 0.60mm) around perimeter
     - Spacing: 1.05mm between pins on short sides, 2.66mm on long sides
     - Pin 1 is at the reference corner (see page 19, Figure 16)
  4. Clearance:
     - Leave space below for the acoustic path
     - No obstructions within ~2mm radius of the bottom port
     - Consider ventilation/acoustic chamber design
 </support_structure_design_requirements>
 <design_note>
  The INMP441 is a bottom-ported mic, so your enclosure needs an acoustic path from the outside environment to the bottom of the microphone. The support structure should securely hold the breakout board while ensuring the sound port remains completely unobstructed.
 </design_note>
<part_description>

### 1.2.3. Large Orange Button ✅ REVIEWED
- **Purpose:** This is the press-to-talk button
- **Location:** Right side of device (from viewing angle)
- **Height:** 30% of enclosure height
- **Width:** Same as the width of a long side
- **Shape:** Rectangular with rounded corners, with a 45 degree bevel from where it exits the enclosure to the surface making the top surface smaller than the base surface.
- **Texture:** Top surface has a dotted pattern, providing extra friction but still feeling comfortable
- **Raised edge on body around button:** There is a 2mm rounded raised edge on the main body running flush around the button.  Since the button fills the entire width of the long right side, this edge also goes on top of a little bit of the chamfers. The edge should form a quarter-circle with one flat side against the button, with 0.25mm space all around the button.
- **Protrusion:** Sticks out a total of 4mm from the body main surface (not counting the raised edge around the button)
- **Color:** Orange

### 1.2.4. Power Button ✅ REVIEWED
- **Location:** Lower part of right side, 25mm from the bottom
- **Color:** Black
- **Design:** Concentric ring design - has a raised outer ring to prevent accidental power-off
- **Diameter:** 8mm

### 1.2.5. Speaker Grille ✅ REVIEWED
- **Location:** Upper part of front face
- **Shape:** Circular
- **Pattern:** Mesh/perforated with many small holes
- **Color:** Dark gray/black
- **Diameter:** 80% of the long side width
- **Position:** Upper edge of speaker grille should be 10mm below the horizontal line with LEDs

### 1.2.6. USB-C Port ✅ REVIEWED
- **Location:** Lower part of right side, 12mm from the bottom
- **Shape:** Stadium-shaped (rounded rectangle) through-hole with a width of 9.5mm, a height of 3.7mm, and a corner radius of 1.6mm
- **Size:** 9.5mm width × 3.7mm height (standard USB-C dimensions)
- **Orientation:** Flat side (9.5mm width) oriented front-to-back (facing toward/away from power button)
- **Surface thickness:** Ensure the enclosure wall thickness at the point of the cutout is exactly 1.6mm. If the rest of the enclosure is thicker (e.g., 3mm), create a recessed pocket on the exterior or interior so the effective thickness at the port is reduced to 1.6mm."

---

# 2. Implementation Plan

## 2.1. Critical Changes Required

### 2.1.1. Fundamental Shape Change: Cylinder → Octagonal Prism
**Current:** Code creates a hollow cylinder using `cq.Workplane("XY").circle()`
**Required:** Create octagonal prism with 7:3 ratio for long:short sides

**Implementation approach:**
1. Calculate octagon dimensions from 40mm width
2. Create octagon profile using `.polygon()` or explicit point coordinates
3. Apply small fillets to each edge where sides meet
4. Extrude to 150mm height
5. Add fillets to top and bottom edges
6. Hollow out the interior

**Octagon geometry calculations:**
- 40mm across (corner to opposite corner? or flat to flat?)
- 7:3 ratio means if long side = 7 units, short chamfer = 3 units
- Need to verify: is 40mm the flat-to-flat or point-to-point measurement?

### 2.1.2. Dimension Corrections
**Current:** 55mm × 55mm × 150mm
**Required:** 40mm × 40mm × 150mm octagonal prism

### 2.1.3. Coordinate System Alignment
**Required:**
- Y axis: length (150mm)
- Z axis: front/back separation
- X axis: left/right separation

**Current code:** Uses Z for height, XY for cross-section
**Action:** May need to rotate final model or reorient coordinate system in code

### 2.1.4. Component Repositioning

| Component | Current Position | Required Position | Change Needed |
|-----------|------------------|-------------------|---------------|
| LEDs (3x 3mm) | Not implemented (commented out) | Front side, 10mm from top, 8mm spacing | Add function |
| Mic (INMP441) | Front, 92% height (~138mm) | Front, 10mm from bottom | Move to bottom + add mounting structure |
| Speaker Grille | Front, 28% (~42mm) | Front, upper part, 10mm below LEDs | Move to top |
| Power Button | Front, 40% (~60mm) | RIGHT side, 25mm from bottom | Change side + reposition |
| USB-C Port | Bottom/front, 5mm | RIGHT side, 12mm from bottom | Change side + reposition |
| Large Button | Right side, 60% (~90mm) | RIGHT side, centered, 30% height (45mm tall) | Adjust height and add bevel |

### 2.1.5. Large Button Redesign
**Current:** Simple rounded rectangle with dimple texture
**Required:**
- Full width of long side (~28mm based on 7:3 ratio)
- 30% of device height = 45mm tall
- 45° bevel/taper (base larger than top surface)
- 4mm protrusion from body surface
- 2mm raised edge on body around button (quarter-circle profile, 0.25mm gap)
- Dotted texture on top surface

### 2.1.6. Power Button Design
**Current:** Simple circular cutout
**Required:**
- 8mm diameter
- Concentric ring design with raised outer ring
- Black color (material/print consideration)
- On RIGHT side, 25mm from bottom

### 2.1.7. INMP441 Microphone Mounting
**Required:** Add internal support structure:
- 4.72mm × 3.76mm mounting footprint
- 1.5mm acoustic hole centered on front face, 10mm from bottom
- 0.5-1.0mm through-hole for acoustic port
- No obstructions within 2mm radius of port
- Acoustic chamber design

### 2.1.8. Speaker Grille Repositioning
**Current:** Lower portion, 28% height
**Required:** Upper portion of front face
- Diameter: 80% of long side width (~22.4mm if long side is 28mm)
- Position: Upper edge 10mm below LED line (LED line is 10mm from top)
- So grille upper edge at 20mm from top

### 2.1.9. LED Holes
**Current:** Function exists but not called
**Required:** Re-enable and position correctly
- Front side, 10mm from top
- 3mm LEDs
- 8mm spacing between centers
- Centered horizontally on front face

## 2.2. Implementation Steps

### 2.2.1. Step 1: Calculate Octagon Geometry
- Determine if 40mm is flat-to-flat or corner-to-corner
- Calculate long side and short chamfer lengths with 7:3 ratio
- Calculate corner positions for octagon profile

### 2.2.2. Step 2: Rewrite `create_basic_enclosure()`
- Replace cylinder with octagonal prism
- Maintain top/bottom edge fillets
- Maintain interior hollowing with appropriate wall thickness

### 2.2.3. Step 3: Update Design Parameters
- Change DEVICE_WIDTH/DEPTH to reflect 40mm octagon
- Calculate long side width for component sizing
- Update all component positions to match reference

### 2.2.4. Step 4: Rewrite Component Functions
- `add_led_holes()`: Position on front, 10mm from top
- `add_mic_hole()`: Move to front bottom, 10mm from bottom, add mounting structure
- `add_speaker_grille()`: Reposition to front top, resize to 80% of long side
- `add_button_cutout()`: Rename to `add_power_button()`, move to right side
- `add_usbc_port()`: Move to right side, 12mm from bottom

### 2.2.5. Step 5: Redesign Large Button
- Add 45° taper/bevel
- Resize to full width of long side × 45mm height
- Add 2mm raised edge feature on body
- Update texture pattern

### 2.2.6. Step 6: Add INMP441 Mounting Structure
- Create internal mounting pocket
- Add acoustic path through enclosure
- Ensure 1.5mm front hole aligns with internal port

### 2.2.7. Step 7: Remove/Update Battery Compartment
- Verify 18650 (18.6mm diameter) fits in 40mm octagon
- May need to reconsider battery placement or use different battery

### 2.2.8. Step 8: Test and Iterate
- Generate model
- Verify all dimensions match reference
- Check component clearances
- Validate acoustic paths
- Ensure printability

## 2.3. Files to Modify
- `/Users/stig/git/stigsb/devais/cad/enclosure.py` - Complete rewrite of geometry

## 2.4. New Files to Create
- None (modifications only)

## 2.5. Risks and Considerations
1. **Battery fit:** 18650 battery (18.6mm diameter) may not fit well in 40mm octagon with wall thickness
2. **Internal space:** Octagon provides less internal volume than 55mm cylinder
3. **Component clearance:** Need to verify XIAO board, speaker, amp, and battery all fit
4. **Printability:** Octagon with small edge fillets should print well, but internal support structures need consideration
5. **Coordinate system:** May cause confusion if not carefully managed

## 2.6. User Responses ✅
1. **40mm dimension:** Flat-to-flat across long parallel sides ✅
2. **Battery:** Keep 18650, can increase enclosure size if needed (length +20%, width +10%) ✅
3. **Raised edge:** Integrated into main body ✅

## 2.7. Octagon Geometry Calculations

Given:
- 40mm flat-to-flat (across opposite long sides)
- 7:3 ratio for long sides : short chamfers
- Octagon formed by chamfering a 40mm square at 45°

Calculations:
- Original square side length (A) = 40mm
- Corner chamfer distance (C) = 40 / 5.3 ≈ 7.55mm
- **Long side length (L) = 40 - 2(7.55) ≈ 24.9mm**
- **Short chamfer length (S) = 7.55√2 ≈ 10.7mm**
- Ratio verification: 24.9 / 10.7 ≈ 2.33 = 7/3 ✓

Component sizing based on long side:
- Large button width: 24.9mm (full long side width)
- Speaker grille diameter: 0.8 × 24.9 ≈ 19.9mm (80% of long side)

## 2.8. Battery Fit Verification

18650 Battery: 18.6mm diameter × 65mm length

Interior space with 2.5mm walls:
- Exterior: 40mm flat-to-flat octagon
- Interior: 40 - 2(2.5) = 35mm flat-to-flat octagon
- Battery needs: 18.6mm diameter

**Result:** ✅ Battery fits comfortably with 16.4mm clearance
**Conclusion:** No size increase needed

---

# 3. CadQuery Implementation Guidelines

## 3.1. Coordinate System (CRITICAL)

**Actual Implementation:**
- The octagon cross-section is in the **XY plane**
- The device height (150mm) is along the **Z axis**
- This differs from the specification which uses Y for length

**Coordinate Mapping:**
```
Spec → Implementation
Y (length, 150mm) → Z axis
Z (front/back) → Y axis
X (left/right) → X axis
```

**Face Positions:**
- **Front face:** Y = +DEVICE_WIDTH/2 (positive Y direction)
- **Right face:** X = +DEVICE_WIDTH/2 (positive X direction)
- **Back face:** Y = -DEVICE_WIDTH/2 (negative Y direction)
- **Left face:** X = -DEVICE_WIDTH/2 (negative X direction)

## 3.2. Workplane Selection for Component Holes (CRITICAL)

**⚠️ Common Mistake:** Creating workplanes at different Z-heights and drilling in the Z direction creates holes that go up/down through the device instead of perpendicular through the octagon faces.

**✅ Correct Approach:**

### 3.2.1. For Front Face Components (LEDs, Speaker, Microphone):
```python
# CORRECT - drill perpendicular to front face
cq.Workplane("XZ")  # Work in XZ plane (front face view)
  .workplane(offset=DEVICE_WIDTH / 2)  # Position at front face (Y = +half)
  .center(x_pos, z_height)  # Position in X and Z
  .circle(radius)
  .extrude(-WALL_THICKNESS - 1)  # Drill in -Y direction (into device)
```

### 3.2.2. For Right Face Components (Power Button, USB-C, Large Button):
```python
# CORRECT - drill perpendicular to right face
cq.Workplane("YZ")  # Work in YZ plane (right face view)
  .workplane(offset=DEVICE_WIDTH / 2)  # Position at right face (X = +half)
  .center(y_pos, z_height)  # Position in Y and Z
  .circle(radius)
  .extrude(-WALL_THICKNESS - 1)  # Drill in -X direction (into device)
```

**❌ Incorrect Approach (DO NOT USE):**
```python
# WRONG - this drills up/down instead of through the face
cq.Workplane("XY")
  .workplane(offset=z_height)  # At a specific height
  .center(x_pos, y_pos)  # On the face
  .circle(radius)
  .extrude(-WALL_THICKNESS - 1)  # Drills in Z direction (WRONG!)
```

## 3.3. Component Orientation Guidelines

### 3.3.1. USB-C Port Orientation
- The port is rectangular: 9mm width × 3.5mm height
- When on the right face (YZ plane):
  - Width (9mm) goes along **Y axis** (front-to-back)
  - Height (3.5mm) goes along **Z axis** (up-down)
- This orients the flat side (wider dimension) toward/away from the device, not vertically
- Use: `.rect(USBC_WIDTH, USBC_HEIGHT)` = `.rect(9, 3.5)` in YZ plane


### 3.3.2. Power Button
- Circular, 8mm diameter
- Concentric ring design (raised outer ring not yet implemented)
- Position: 25mm from bottom (Z = 25)

### 3.3.3. Large Button
- Rectangular with 45° taper
- Full width of long side (24.9mm) × 45mm height
- Positioned on right face, vertically centered

## 3.4. Battery Compartment

**Status:** Removed for now (hollow interior provides space)
- Placeholder function exists in code
- TODO: Design proper battery holder, contacts, and wire routing when needed
- 18650 battery (18.6mm × 65mm) fits comfortably in 35mm interior space
