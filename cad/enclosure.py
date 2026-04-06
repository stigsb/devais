import cadquery as cq
import math
from pathlib import Path

# --- Parameters ---
# Dimensions
DEVICE_WIDTH = 40.0  # Flat-to-flat distance
DEVICE_HEIGHT = 150.0
WALL_THICKNESS = 1.6  # Matches USB-C port spec (section 1.1.5)
FILLET_RADIUS = 4.0 # For vertical edges and top/bottom edges

# Boolean cut overshoot to ensure full wall penetration
CUT_OVERSHOOT = 5.0  # mm

# Calculated octagon dimensions (7:3 long:short side ratio)
# L = 140*sqrt(2) / (3 + 3.5*sqrt(2))
LONG_SIDE_LENGTH = (140 * math.sqrt(2)) / (3 + 3.5 * math.sqrt(2))
HALF_LONG_SIDE = LONG_SIDE_LENGTH / 2.0
CORNER_COORD = DEVICE_WIDTH / 2.0

# Components
LED_DIAMETER = 3.0
LED_SPACING = 8.0
LED_TOP_OFFSET = 10.0

MIC_HOLE_DIAMETER = 1.5
MIC_BOTTOM_OFFSET = 10.0
MIC_PORT_DIAMETER = 1.0 # Internal port
MIC_POCKET_WIDTH = 4.72 + 0.2
MIC_POCKET_HEIGHT = 3.76 + 0.2
MIC_POCKET_DEPTH = 1.0 # Depth of pocket into the wall (from inside)

SPEAKER_DIAMETER = LONG_SIDE_LENGTH * 0.8
SPEAKER_TOP_OFFSET = LED_TOP_OFFSET + 10.0 # Upper edge 10mm below LEDs

POWER_BTN_DIAMETER = 8.0
POWER_BTN_BOTTOM_OFFSET = 44.0

USBC_WIDTH = 9.5
USBC_HEIGHT = 3.7
USBC_CORNER_RADIUS = 1.6
USBC_BOTTOM_OFFSET = 31.0

LARGE_BTN_HEIGHT = 45.0
LARGE_BTN_WIDTH = LONG_SIDE_LENGTH
LARGE_BTN_CENTER_FROM_BOTTOM = 105.0
LARGE_BTN_CORNER_RADIUS_BASE = 8.0
LARGE_BTN_CORNER_RADIUS_TOP = 5.4
LARGE_BTN_OPENING_RADIUS = 8.5
LARGE_BTN_FRAME_WIDTH = 1.6
LARGE_BTN_FRAME_PROTRUSION = 1.6 # Beyond outer surface

# Tongue-and-groove rails (alignment for split halves)
# Runs along full height on left/right wall seams. Critical for thread alignment.
TONGUE_WIDTH = 1.0            # In X direction, within 1.6mm wall
TONGUE_HEIGHT = 0.8           # Protrusion in Y direction from split face
TONGUE_CLEARANCE = 0.15       # Per side for FDM tolerance
GROOVE_WIDTH = TONGUE_WIDTH + 2 * TONGUE_CLEARANCE
GROOVE_DEPTH = TONGUE_HEIGHT + TONGUE_CLEARANCE
TONGUE_Z_MARGIN = 5.0         # Inset from top/bottom to avoid interfering with fillets

# Cantilever snap clips (retention for split halves)
# Beams on back half flex in Y to engage hooks in front half pockets.
SNAP_BEAM_LENGTH = 8.0        # Along Z axis
SNAP_BEAM_WIDTH = 3.0         # Along X axis (within wall)
SNAP_BEAM_THICKNESS = 0.8     # In Y direction
SNAP_HOOK_DEPTH = 0.4         # Additional Y protrusion at hook tip
SNAP_HOOK_HEIGHT = 1.0        # Z extent of hook
SNAP_HOOK_RAMP = 1.5          # Z extent of 30° lead-in ramp
SNAP_CLEARANCE = 0.2          # Clearance around beam in pocket
SNAP_POCKET_DEPTH = SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH + SNAP_CLEARANCE

# --- Geometry Helpers ---

def create_octagonal_prism(height, width, half_long_side, fillet_radius=0.0):
    """
    Creates an octagonal prism with specific dimensions.
    width: Flat-to-flat distance (so max coord is width/2)
    half_long_side: half length of the long side.
    """
    max_c = width / 2.0
    h_l = half_long_side
    
    # Points for the octagon (counter-clockwise starting from right-top)
    pts = [
        (max_c, h_l),   # Right face, top corner
        (h_l, max_c),   # Top face, right corner
        (-h_l, max_c),  # Top face, left corner
        (-max_c, h_l),  # Left face, top corner
        (-max_c, -h_l), # Left face, bottom corner
        (-h_l, -max_c), # Bottom face, left corner
        (h_l, -max_c),  # Bottom face, right corner
        (max_c, -h_l)   # Right face, bottom corner
    ]
    
    prism = cq.Workplane("XY").polyline(pts).close().extrude(height)
    
    if fillet_radius > 0:
        prism = prism.edges("|Z").fillet(fillet_radius)

    return prism

# --- Feature Functions ---

def add_led_holes(enclosure):
    """
    Front side (Y+), 10mm from top.
    3x 3mm holes, 8mm spacing.
    """
    z_pos = DEVICE_HEIGHT - LED_TOP_OFFSET

    # Front face workplane (XZ at Y = +CORNER_COORD)
    wp = cq.Workplane("XZ").workplane(offset=CORNER_COORD).center(0, z_pos)

    for i in [-1, 0, 1]:
        hole = (
            wp.center(i * LED_SPACING, 0)
            .circle(LED_DIAMETER / 2)
            .extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
        )
        enclosure = enclosure.cut(hole)

    return enclosure

def add_mic_hole_and_mount(enclosure):
    """
    Front side (Y+), 10mm from bottom.
    Includes acoustic hole and internal mounting pocket.
    """
    z_pos = MIC_BOTTOM_OFFSET
    
    # 1. External Acoustic Hole
    wp = (
        cq.Workplane("XZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
    )
    
    acoustic_hole = wp.circle(MIC_HOLE_DIAMETER / 2).extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
    enclosure = enclosure.cut(acoustic_hole)
    
    # Internal mounting pocket for INMP441 board.
    # Cut into the wall from the inner surface toward the outer surface (+Y).
    # XZ workplane normal is -Y, so extrude(negative) goes in +Y (into wall material).
    inner_y = CORNER_COORD - WALL_THICKNESS

    pocket = (
        cq.Workplane("XZ")
        .workplane(offset=inner_y)
        .center(0, z_pos)
        .rect(MIC_POCKET_WIDTH, MIC_POCKET_HEIGHT)
        .extrude(-MIC_POCKET_DEPTH)  # -Y normal means negative extrude goes +Y into wall
    )

    enclosure = enclosure.cut(pocket)
    
    return enclosure

def add_speaker_grille(enclosure):
    """
    Front side (Y+).
    Upper edge 10mm below LEDs.
    Diameter 80% of long side.
    """
    # Center Z: top edge at 20mm from top (10mm LED offset + 10mm gap), minus radius
    z_pos = (DEVICE_HEIGHT - 20.0) - (SPEAKER_DIAMETER / 2.0)

    wp = (
        cq.Workplane("XZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
    )

    # Perforated grille: grid of small holes within circular boundary
    hole_dia = 1.5   # mm
    spacing = 2.5     # mm center-to-center
    pts = []
    r_sq = (SPEAKER_DIAMETER / 2.0 - 1.0) ** 2  # 1mm inset from edge

    num_points = int(SPEAKER_DIAMETER / spacing) + 2
    start = -(num_points * spacing) / 2
    
    for i in range(num_points):
        x = start + i * spacing
        for j in range(num_points):
            y = start + j * spacing
            if x*x + y*y <= r_sq:
                pts.append((x, y))
    
    if pts:
        holes = (
            wp.pushPoints(pts)
            .circle(hole_dia / 2)
            .extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
        )
        enclosure = enclosure.cut(holes)
        
    return enclosure

def add_power_button(enclosure):
    """
    Right side (X+), 44mm from bottom.
    8mm diameter.
    """
    z_pos = POWER_BTN_BOTTOM_OFFSET

    # Right face workplane (YZ at X = +CORNER_COORD)
    wp = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
    )
    
    hole = wp.circle(POWER_BTN_DIAMETER / 2).extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
    enclosure = enclosure.cut(hole)
    
    # Concentric ring: raised outer ring to prevent accidental power-off
    ring_od = POWER_BTN_DIAMETER + 3.0   # mm
    ring_id = POWER_BTN_DIAMETER + 0.5   # mm - clearance around button
    ring_protrusion = 1.0                # mm - beyond outer surface
    ring_overlap = 0.5                   # mm - into wall for solid boolean fusion

    ring = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD - ring_overlap)
        .center(0, z_pos)
        .circle(ring_od / 2)
        .circle(ring_id / 2)
        .extrude(ring_protrusion + ring_overlap)
    )

    enclosure = enclosure.union(ring)
    
    return enclosure

def add_usbc_port(enclosure):
    """
    Right side (X+), 31mm from bottom.
    9.5mm × 3.7mm rounded rectangle, 1.6mm corner radius.
    Width oriented front-to-back (along Y axis).
    """
    z_pos = USBC_BOTTOM_OFFSET

    # Rounded rectangle cutout: extrude rect then fillet edges parallel to cut direction
    tool = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .rect(USBC_WIDTH, USBC_HEIGHT)
        .extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
        .edges("|X")
        .fillet(USBC_CORNER_RADIUS)
    )

    enclosure = enclosure.cut(tool)
    return enclosure

def add_large_button_feature(enclosure):
    """
    Right side (X+): button opening with rounded corners + raised frame.
    """
    z_pos = LARGE_BTN_CENTER_FROM_BOTTOM

    # Opening: button size + 0.5mm clearance per side
    opening_w = LARGE_BTN_WIDTH + 1.0   # mm
    opening_h = LARGE_BTN_HEIGHT + 1.0  # mm

    opening_tool = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .rect(opening_w, opening_h)
        .extrude(-(WALL_THICKNESS + CUT_OVERSHOOT))
        .edges("|X")
        .fillet(LARGE_BTN_OPENING_RADIUS)
    )
    enclosure = enclosure.cut(opening_tool)

    # Raised frame around opening.
    # Extends from inner wall surface to LARGE_BTN_FRAME_PROTRUSION beyond outer surface.
    frame_inner_w = opening_w
    frame_inner_h = opening_h
    frame_outer_w = frame_inner_w + 2 * LARGE_BTN_FRAME_WIDTH
    frame_outer_h = frame_inner_h + 2 * LARGE_BTN_FRAME_WIDTH
    frame_depth = WALL_THICKNESS + LARGE_BTN_FRAME_PROTRUSION

    # Build as outer rounded rect minus inner rounded rect for correct corner radii
    outer_solid = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD - WALL_THICKNESS)
        .center(0, z_pos)
        .rect(frame_outer_w, frame_outer_h)
        .extrude(frame_depth)
        .edges("|X")
        .fillet(LARGE_BTN_OPENING_RADIUS + LARGE_BTN_FRAME_WIDTH)
    )

    inner_cut = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD - WALL_THICKNESS)
        .center(0, z_pos)
        .rect(frame_inner_w, frame_inner_h)
        .extrude(frame_depth)
        .edges("|X")
        .fillet(LARGE_BTN_OPENING_RADIUS)
    )

    frame = outer_solid.cut(inner_cut)
    frame = frame.faces(">X").edges().fillet(0.3)  # Smooth outer lip

    enclosure = enclosure.union(frame)
    return enclosure

def create_large_button():
    """
    Separate button part: base section + 45-degree beveled top + dot texture.
    Exported as its own STL for printing in a different color.
    """
    w = LARGE_BTN_WIDTH
    h = LARGE_BTN_HEIGHT
    depth_base = 4.0    # mm - flat section depth
    depth_bevel = 4.0   # mm - beveled section depth
    total_depth = depth_base + depth_bevel
    r_base = LARGE_BTN_CORNER_RADIUS_BASE
    r_top = LARGE_BTN_CORNER_RADIUS_TOP

    # Base section: proper rounded rectangle using sketch API
    button = (
        cq.Workplane("XY")
        .sketch()
        .rect(w, h, tag="r")
        .vertices(tag="r")
        .fillet(r_base)
        .finalize()
        .extrude(depth_base)
    )

    # Beveled section: extrude with taper from the rounded-rect top face.
    # Taper on a rounded rect profile naturally produces rounded corners
    # (the offset of a rounded rect is another rounded rect).
    w_top = w - 2 * depth_bevel  # 4mm inset each side from 45° taper
    h_top = h - 2 * depth_bevel

    bevel = (
        button.faces(">Z").workplane()
        .sketch()
        .rect(w, h, tag="r")
        .vertices(tag="r")
        .fillet(r_base)
        .finalize()
        .extrude(depth_bevel, taper=45)
    )

    button = button.union(bevel)

    # Dot texture on top surface
    bump_dia = 1.0   # mm
    bump_height = 0.5 # mm
    bump_spacing = 1.5 # mm center-to-center

    # Rounded-rect boundary check for bump placement
    dx = w_top / 2 - r_top
    dy = h_top / 2 - r_top

    pts = []
    nx = int(w_top / bump_spacing)
    ny = int(h_top / bump_spacing)
    for i in range(-nx, nx + 1):
        bx = i * bump_spacing
        for j in range(-ny, ny + 1):
            by = j * bump_spacing
            if abs(bx) > w_top / 2 or abs(by) > h_top / 2:
                continue
            # Corner zone check
            if abs(bx) > dx and abs(by) > dy:
                cx = math.copysign(dx, bx)
                cy = math.copysign(dy, by)
                if math.hypot(bx - cx, by - cy) > r_top - bump_dia / 2:
                    continue
            pts.append((bx, by))

    if pts:
        bumps = (
            cq.Workplane("XY")
            .workplane(offset=total_depth)
            .pushPoints(pts)
            .circle(bump_dia / 2)
            .extrude(bump_height)
        )
        button = button.union(bumps)

    return button

# --- Split for Printing ---

def split_enclosure(enclosure):
    """
    Split enclosure into front and back halves along Y=0 for 3D printing.
    Front half (Y>0): LEDs, mic, speaker grille
    Back half (Y<0): plain back
    Print each half with the outer flat face down on the print bed.

    Joint system (no glue, repeatable open/close):
    1. Tongue-and-groove rails along left/right wall seams → lateral alignment
    2. Cantilever snap clips at 2 Z positions per side → retention
    """
    # --- Step 1: Split into halves ---
    s = 300
    pos_y_tool = cq.Workplane("XY").transformed(offset=(0, s/2, s/2 - 50)).box(s, s, s)
    neg_y_tool = cq.Workplane("XY").transformed(offset=(0, -s/2, s/2 - 50)).box(s, s, s)

    front_half = enclosure.cut(neg_y_tool)  # remove Y<0 → keep Y>0
    back_half = enclosure.cut(pos_y_tool)   # remove Y>0 → keep Y<0

    # Wall center X for left/right walls
    wall_cx = CORNER_COORD - WALL_THICKNESS / 2  # 19.2mm

    # --- Step 2: Tongue-and-groove rails ---
    # Tongue on back half split face, groove in front half.
    # Runs along Z, inset from top/bottom to avoid fillet zones.
    tongue_z_start = TONGUE_Z_MARGIN
    tongue_z_end = DEVICE_HEIGHT - TONGUE_Z_MARGIN
    tongue_z_len = tongue_z_end - tongue_z_start
    tongue_z_center = (tongue_z_start + tongue_z_end) / 2

    for sign in [1, -1]:  # right (+X) and left (-X) walls
        x = sign * wall_cx

        # Tongue: rectangular bar on back half, protruding from Y=0 into front half (+Y)
        # XZ workplane normal is -Y, so extrude(-h) goes +Y
        tongue = (cq.Workplane("XZ").center(x, tongue_z_center)
                  .rect(TONGUE_WIDTH, tongue_z_len)
                  .extrude(-TONGUE_HEIGHT))
        back_half = back_half.union(tongue)

        # Groove: matching slot cut into front half at Y=0 face
        groove = (cq.Workplane("XZ").center(x, tongue_z_center)
                  .rect(GROOVE_WIDTH, tongue_z_len)
                  .extrude(-GROOVE_DEPTH))
        front_half = front_half.cut(groove)

    # --- Step 3: Cantilever snap clips ---
    # Snap beams on back half, pockets with ledges in front half.
    # Beam attached at top, hook at bottom (free end).
    # 2 per side, avoiding feature zones.
    # Z positions: top of beam (attachment point)
    snap_z_positions = [45, 135]  # Above USB-C/power btn zone; above large btn zone

    for sign in [1, -1]:
        x = sign * wall_cx
        for z_attach in snap_z_positions:
            z_hook = z_attach - SNAP_BEAM_LENGTH  # Free end with hook

            # --- Beam on back half ---
            # The beam protrudes from the split face (Y=0) into the front half (+Y).
            # It's a thin cantilever that can flex in -Y when the hook is pushed.
            beam_y_center = SNAP_BEAM_THICKNESS / 2  # center of beam in +Y
            beam_z_center = z_attach - SNAP_BEAM_LENGTH / 2

            beam = (cq.Workplane("XY")
                    .transformed(offset=(x, beam_y_center, beam_z_center))
                    .box(SNAP_BEAM_WIDTH, SNAP_BEAM_THICKNESS, SNAP_BEAM_LENGTH))
            back_half = back_half.union(beam)

            # Hook at free end: additional protrusion in +Y
            hook_y_center = SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH / 2
            hook_z_center = z_hook + SNAP_HOOK_HEIGHT / 2

            hook = (cq.Workplane("XY")
                    .transformed(offset=(x, hook_y_center, hook_z_center))
                    .box(SNAP_BEAM_WIDTH, SNAP_HOOK_DEPTH, SNAP_HOOK_HEIGHT))
            back_half = back_half.union(hook)

            # Ramp on hook: angled lead-in for easy insertion.
            # A triangular wedge below the hook that tapers from full hook depth to zero.
            # Model as a box that we cut at an angle.
            ramp_z_center = z_hook + SNAP_HOOK_HEIGHT + SNAP_HOOK_RAMP / 2
            ramp = (cq.Workplane("XY")
                    .transformed(offset=(x, hook_y_center, ramp_z_center))
                    .box(SNAP_BEAM_WIDTH, SNAP_HOOK_DEPTH, SNAP_HOOK_RAMP))
            back_half = back_half.union(ramp)

            # Cut the ramp into a wedge shape: full hook depth at bottom, zero at top.
            # Use a rotated box to shave the outer portion into an angled ramp.
            ramp_cut_angle = math.atan2(SNAP_HOOK_DEPTH, SNAP_HOOK_RAMP)  # radians
            ramp_cut_size = SNAP_HOOK_RAMP + SNAP_HOOK_DEPTH  # oversized box
            ramp_cut = (cq.Workplane("XZ")
                        .transformed(
                            offset=(x,
                                    SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH,
                                    ramp_z_center),
                            rotate=(math.degrees(ramp_cut_angle), 0, 0))
                        .box(SNAP_BEAM_WIDTH + 1, ramp_cut_size, ramp_cut_size))
            back_half = back_half.cut(ramp_cut)

            # --- Pocket in front half ---
            # The pocket accommodates the beam + hook with clearance.
            # It's a slot cut into the front half's interior at the split face.
            pocket_y_depth = SNAP_POCKET_DEPTH
            pocket_y_center = pocket_y_depth / 2
            pocket_z_len = SNAP_BEAM_LENGTH + 2 * SNAP_CLEARANCE
            pocket_z_center = beam_z_center

            pocket = (cq.Workplane("XY")
                      .transformed(offset=(x, pocket_y_center, pocket_z_center))
                      .box(SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                           pocket_y_depth,
                           pocket_z_len))
            front_half = front_half.cut(pocket)

            # Ledge: the pocket is deeper only at the hook zone (bottom of beam).
            # The rest of the pocket is shallow (beam thickness only).
            # Actually, the pocket above is uniform depth. The ledge forms naturally
            # because the hook protrudes beyond the beam thickness — the pocket
            # only needs to be beam-thickness deep above the hook zone, and
            # hook-depth deep at the hook zone. But for simplicity and printability,
            # make the full pocket SNAP_BEAM_THICKNESS deep, then add a deeper
            # notch at the hook location.

            # Re-cut pocket to beam depth only (shallower)
            # Then add deeper notch at hook
            shallow_pocket = (cq.Workplane("XY")
                              .transformed(offset=(x, SNAP_BEAM_THICKNESS / 2, pocket_z_center))
                              .box(SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                                   SNAP_BEAM_THICKNESS + SNAP_CLEARANCE,
                                   pocket_z_len))
            front_half = front_half.cut(shallow_pocket)

            # Deep notch at hook zone (where hook engages)
            hook_notch_z_len = SNAP_HOOK_HEIGHT + SNAP_HOOK_RAMP + SNAP_CLEARANCE
            hook_notch_z_center = z_hook + hook_notch_z_len / 2
            hook_notch = (cq.Workplane("XY")
                          .transformed(offset=(x, pocket_y_center, hook_notch_z_center))
                          .box(SNAP_BEAM_WIDTH + 2 * SNAP_CLEARANCE,
                               pocket_y_depth,
                               hook_notch_z_len))
            front_half = front_half.cut(hook_notch)

    return front_half, back_half

# --- Main Build ---

def build_enclosure():
    # 1. Create outer solid octagonal prism
    solid = create_octagonal_prism(DEVICE_HEIGHT, DEVICE_WIDTH, HALF_LONG_SIDE, FILLET_RADIUS)
    
    # Fillet top and bottom edges
    # The vertical edges are already filleted by `create_octagonal_prism`.
    # Now fillet the loops at Z=0 and Z=HEIGHT.
    # Select edges.
    solid = solid.edges("<Z or >Z").fillet(FILLET_RADIUS)
    
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

    # Inner fillets match outer minus wall thickness for constant wall
    inner_fillet = FILLET_RADIUS - WALL_THICKNESS
    if inner_fillet > 0:
        inner_solid = inner_solid.edges(">Z").fillet(inner_fillet)
        inner_solid = inner_solid.edges("|Z").fillet(inner_fillet)
    
    enclosure = solid.cut(inner_solid)
    
    # 3. Add Features
    enclosure = add_led_holes(enclosure)
    enclosure = add_mic_hole_and_mount(enclosure)
    enclosure = add_speaker_grille(enclosure)
    enclosure = add_power_button(enclosure)
    enclosure = add_usbc_port(enclosure)
    enclosure = add_large_button_feature(enclosure)

    return enclosure

def main():
    output_dir = Path("cad/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating enclosure...")
    enclosure = build_enclosure()
    cq.exporters.export(enclosure, str(output_dir / "enclosure.stl"))
    print("Exported enclosure.stl")

    print("Splitting enclosure for printing...")
    front_half, back_half = split_enclosure(enclosure)
    cq.exporters.export(front_half, str(output_dir / "enclosure_front.stl"))
    print("Exported enclosure_front.stl")
    cq.exporters.export(back_half, str(output_dir / "enclosure_back.stl"))
    print("Exported enclosure_back.stl")

    print("Generating large button...")
    button = create_large_button()
    cq.exporters.export(button, str(output_dir / "large_button.stl"))
    print("Exported large_button.stl")


if __name__ == "__main__":
    main()
