import cadquery as cq
import math
from pathlib import Path

# --- Parameters ---
# Dimensions
DEVICE_WIDTH = 40.0  # Flat-to-flat distance
DEVICE_HEIGHT = 150.0
WALL_THICKNESS = 1.6  # Matches USB-C port spec (section 1.1.5)
FILLET_RADIUS = 4.0 # For vertical edges and top/bottom edges

# Calculated Dimensions
# Ratio Long:Short = 7:3
# See reasoning in thought trace
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

# Alignment Pins (for split halves)
# Pins must fit within wall thickness (1.6mm) so they're invisible after assembly.
# The wall cross-section acts as the socket — no separate bosses needed.
PIN_DIAMETER = 1.0            # Thin enough to leave wall material around hole
PIN_HEIGHT = 2.0
PIN_CLEARANCE = 0.15          # Per side, tight fit for alignment
HOLE_DIAMETER = PIN_DIAMETER + 2 * PIN_CLEARANCE  # 1.3mm — leaves 0.15mm wall on each side
HOLE_DEPTH = 2.5

# --- Geometry Helpers ---

def create_octagonal_prism(height, width, half_long_side, fillet_radius=0):
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

def create_thread_ridge(surface_radius, pitch, height, depth, start_z=0.0, internal=True, overlap=0.0):
    """
    Create a helical thread ridge by sweeping a triangular profile along a helix.

    surface_radius: radius of the cylindrical surface where thread sits
    pitch: thread pitch in mm
    height: total thread engagement height
    depth: how far the ridge extends from the surface
    start_z: Z position where thread begins
    internal: True = ridge extends inward (bore), False = outward (boss)
    """
    helix = cq.Wire.makeHelix(
        pitch, height, surface_radius,
        center=cq.Vector(0, 0, start_z)
    )

    half_p = pitch * 0.3  # Thread flank half-width

    if internal:
        profile = (
            cq.Workplane("XZ")
            .moveTo(surface_radius + overlap, start_z - half_p)
            .lineTo(surface_radius - depth, start_z)
            .lineTo(surface_radius + overlap, start_z + half_p)
            .close()
        )
    else:
        profile = (
            cq.Workplane("XZ")
            .moveTo(surface_radius - overlap, start_z - half_p)
            .lineTo(surface_radius + depth, start_z)
            .lineTo(surface_radius - overlap, start_z + half_p)
            .close()
        )

    return profile.sweep(helix, isFrenet=True)

# --- Feature Functions ---

def add_led_holes(enclosure):
    """
    Front side (Y+), 10mm from top.
    3x 3mm holes, 8mm spacing.
    """
    z_pos = DEVICE_HEIGHT - LED_TOP_OFFSET
    
    # Workplane on Front Face (XZ plane, offset by width/2)
    # Note: center of workplane is (0, 0) relative to the face
    # We map x_pos (left-right) to x and z_pos (height) to y in the workplane local coords?
    # Let's be explicit with axes.
    # Front face is at Y = +CORNER_COORD. Normal is +Y.
    # X is X, Z is Y in local 2D.
    
    # Using the "correct approach" from spec
    wp = (
        cq.Workplane("XZ")
        .workplane(offset=CORNER_COORD)
    )
    
    for i in [-1, 0, 1]:
        x_pos = i * LED_SPACING
        hole = (
            wp.center(x_pos, z_pos)
            .circle(LED_DIAMETER / 2)
            .extrude(-WALL_THICKNESS - 5) # Cut inwards (-Y)
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
    
    acoustic_hole = wp.circle(MIC_HOLE_DIAMETER / 2).extrude(-WALL_THICKNESS - 5)
    enclosure = enclosure.cut(acoustic_hole)
    
    # 2. Internal Mounting Structure
    # We need a pocket on the *inside* face.
    # Inside face is at Y = CORNER_COORD - WALL_THICKNESS
    # We want to add material or cut?
    # The wall is 2.5mm thick.
    # The mic needs a pocket. 
    # If we assume we attach the board to the flat inner wall.
    # Spec: "Support structure behind the hole... Mounting Footprint: 4.72mm x 3.76mm pocket or platform"
    # "Create a ... pocket or platform"
    # Since the wall is flat there (it's the long side), we can just make a small raised platform 
    # or a recessed pocket if the wall is thick enough.
    # Let's create a small platform to ensure flatness and correct distance.
    # Actually, the octagon interior is flat on the long sides.
    # So we just need to ensure the hole is clear.
    # But maybe we need a recess to hold the board in place?
    # Let's make a small rectangular frame/guide for the mic board.
    
    # Let's add a small raised rim around the mic hole on the inside to seat the mic?
    # Or just a rectangular recess.
    # Let's cut a shallow pocket into the inner wall to seat the mic component, 
    # ensuring the acoustic path is clear.
    
    # Inner face Y location:
    inner_y = CORNER_COORD - WALL_THICKNESS
    
    # Pocket for the mic board
    # We will cut into the wall from the inside.
    # Pocket dimensions: MIC_POCKET_WIDTH x MIC_POCKET_HEIGHT
    
    pocket = (
        cq.Workplane("XZ")
        .workplane(offset=inner_y)
        .center(0, z_pos)
        .rect(MIC_POCKET_WIDTH, MIC_POCKET_HEIGHT)
        .extrude(0.5) # Cut 0.5mm into the wall (outwards +Y)
    )
    
    enclosure = enclosure.cut(pocket)
    
    return enclosure

def add_speaker_grille(enclosure):
    """
    Front side (Y+).
    Upper edge 10mm below LEDs.
    Diameter 80% of long side.
    """
    # LEDs are at DEVICE_HEIGHT - 10.
    # Speaker top edge at DEVICE_HEIGHT - 10 - 10 = DEVICE_HEIGHT - 20.
    # Radius = SPEAKER_DIAMETER / 2
    # Center Z = Top Edge Z - Radius
    z_pos = (DEVICE_HEIGHT - 20.0) - (SPEAKER_DIAMETER / 2.0)
    
    wp = (
        cq.Workplane("XZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
    )
    
    # Create main cutout (the hole through the case)
    # Spec says "Mesh/perforated with many small holes".
    # Instead of one big hole, let's make a pattern of small holes.
    
    hole_dia = 1.5
    spacing = 2.5
    
    # Generate grid of points within the circle
    pts = []
    r_sq = (SPEAKER_DIAMETER / 2.0 - 1.0) ** 2 # Keep within boundary
    
    # Simple grid scan
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
            .extrude(-WALL_THICKNESS - 5)
        )
        enclosure = enclosure.cut(holes)
        
    return enclosure

def add_power_button(enclosure):
    """
    Right side (X+), 44mm from bottom.
    8mm diameter.
    """
    z_pos = POWER_BTN_BOTTOM_OFFSET
    
    # Right face is X = +CORNER_COORD. Normal is +X.
    # Workplane YZ.
    
    wp = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos) # Y=0 (center of side), Z=z_pos
    )
    
    hole = wp.circle(POWER_BTN_DIAMETER / 2).extrude(-WALL_THICKNESS - 5)
    enclosure = enclosure.cut(hole)
    
    # Concentric ring design - Raised outer ring
    # "raised outer ring to prevent accidental power-off"
    # Ring diameter say 10mm OD, 8mm ID.
    # Height? Maybe 1mm protrusion.
    
    ring_od = POWER_BTN_DIAMETER + 3.0
    ring_id = POWER_BTN_DIAMETER + 0.5 # Clearance
    
    ring = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .circle(ring_od/2)
        .circle(ring_id/2)
        .extrude(1.0) # Stick out 1mm
    )
    
    enclosure = enclosure.union(ring)
    
    return enclosure

def add_usbc_port(enclosure):
    """
    Right side (X+), 12mm from bottom.
    9.5mm width x 3.7mm height.
    Stadium shape.
    """
    z_pos = USBC_BOTTOM_OFFSET
    
    wp = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
    )
    
    # Create the cutout shape
    # Rect with rounded corners
    # Note: rect() creates a rectangle centered at (0,0)
    # To get stadium shape, we can use 2 circles and a rect, or just rect with fillets.
    # But CadQuery rect can't fillet 2D easily in one go? 
    # Actually .rect().extrude().fillet() works on 3D.
    # Or 2D .rect(..., centered=True) then fillet vertices?
    # Let's use rect and fillet the 2D wire? No, simpler to fillet 3D or use union of shapes.
    
    # 2D stadium profile
    # Width is along Y axis (front-to-back), Height along Z axis.
    # But in YZ plane, Y is local x, Z is local y.
    # So Width maps to local x.
    
    # Correct orientation: "Flat side (9.5mm width) oriented front-to-back"
    # This means along Y axis of the device.
    # In YZ plane, the horizontal axis is Y (device Y), vertical is Z (device Z).
    # So rect width = 9.5, rect height = 3.7.
    
    cutout_solid = (
        wp.rect(USBC_WIDTH, USBC_HEIGHT)
        .extrude(-WALL_THICKNESS - 5)
    )
    
    # Fillet the corners of the cutout solid?
    # Hard to select specific edges of the negative volume.
    # Better to construct the profile with rounded corners.
    
    # Let's do it manually with points or hull of circles.
    
    # Stadium shape: two circles separated by (width - height)
    # Wait, width=9.5, height=3.7. Radius = 3.7/2 = 1.85.
    # Separation = 9.5 - 3.7 = 5.8.
    # This gives full round ends.
    # Spec says "corner radius of 1.6mm".
    # So it's a rounded rect, not a full stadium.
    
    # Re-make profile with rounded rect
    # We can extrude a rect then fillet the edges of the solid that are parallel to extrusion?
    # No, that's complex.
    # Use 2D fillet.
    
    profile = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .rect(USBC_WIDTH, USBC_HEIGHT)
    )
    
    # Fillet 2D
    # In CQ, you can fillet vertices of a pending wire.
    # But usually easier to extrude then fillet.
    # Let's try extruding a slightly larger rect then filleting?
    # No, let's look up 2D fillet.
    # `val().fillet2D(radius)` is available in newer CQ. 
    # Assuming standard install, `rect` returns a Workplane.
    
    # Let's assume we can just extrude the rect and accept sharp corners for the cutout 
    # OR apply fillet to the edges of the hole in the enclosure after cut?
    # Applying fillets to the enclosure after cut is robust.
    
    # Let's try to make the shape correct in 2D first.
    # Approximation: just a rect for now if 2D fillet is tricky, but we want high quality.
    # Alternative: Use `polygon` or `hull`.
    
    # Let's use `rect` and then `fillet` on the generated solid before cutting?
    # No, you can't fillet a "tool" solid easily if it's just a prism.
    # Actually you can.
    
    tool = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .rect(USBC_WIDTH, USBC_HEIGHT)
        .extrude(-WALL_THICKNESS - 5)
        .edges("|X") # Edges parallel to extrusion (X axis is normal to YZ)
        .fillet(USBC_CORNER_RADIUS)
    )
    
    enclosure = enclosure.cut(tool)
    
    # "Surface thickness: Ensure the enclosure wall thickness at the point of the cutout is exactly 1.6mm"
    # If WALL_THICKNESS > 1.6, we need a pocket.
    if WALL_THICKNESS > 1.6:
        # Create a recessed pocket from the outside? Or inside?
        # Usually from outside for connector clearance, or inside to thin the wall.
        # "recessed pocket on the exterior or interior"
        # Let's do exterior recess to make sure the plug fits.
        # Recess size: slightly larger than port.
        
        pocket_depth = WALL_THICKNESS - 1.6
        pocket_w = USBC_WIDTH + 4
        pocket_h = USBC_HEIGHT + 4
        
        recess = (
            cq.Workplane("YZ")
            .workplane(offset=CORNER_COORD)
            .center(0, z_pos)
            .rect(pocket_w, pocket_h)
            .extrude(-pocket_depth) # Cut into surface
            .edges("|X")
            .fillet(2.0)
        )
        enclosure = enclosure.cut(recess)

    return enclosure

def add_large_button_feature(enclosure):
    """
    Right side (X+).
    Button opening and Raised Edge.
    """
    z_pos = LARGE_BTN_CENTER_FROM_BOTTOM
    
    # 1. Opening
    # "Opening in enclosure... 8.5mm corner radius"
    # "Width: Same as the width of a long side (~24.9mm)" ?
    # Wait, the button is "Width: Same as the width of a long side".
    # The opening should probably be slightly larger?
    # "Opening... matching the 8mm button corner radius plus 0.5mm clearance"
    # So Opening Size = Button Size + 1mm (0.5 on each side)?
    # Spec says "Opening is cut through the wall... Opening for the button has rounded corners with 8.5mm radius"
    # It doesn't explicitly say the opening width/height, but implies it matches the button + clearance.
    
    btn_w = LARGE_BTN_WIDTH
    btn_h = LARGE_BTN_HEIGHT
    
    # Gap is 0.25mm? "2mm raised edge... 0.25mm gap"
    # "Opening... matching the 8mm button corner radius plus 0.5mm clearance" -> this implies 0.5mm gap?
    # Let's assume 0.5mm clearance total (0.25 per side) or 0.5mm gap (0.5 per side)?
    # "8mm button corner radius plus 0.5mm clearance" -> 8.5mm radius.
    # Usually clearance refers to gap on one side.
    # Let's use 0.5mm gap per side.
    
    opening_w = btn_w + 1.0
    opening_h = btn_h + 1.0
    
    # Create opening tool
    opening_tool = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD)
        .center(0, z_pos)
        .rect(opening_w, opening_h)
        .extrude(-WALL_THICKNESS - 5)
        .edges("|X")
        .fillet(LARGE_BTN_OPENING_RADIUS)
    )
    
    enclosure = enclosure.cut(opening_tool)
    
    # 2. Raised Edge (Frame)
    # "Frame width: 1.6mm"
    # "Protrusion: Extends 1.6mm beyond the outer surface"
    # "Height: 3.2mm (2x wall thickness)" -> This implies it goes from inner wall (-1.6mm relative to outer) to +1.6mm.
    # Inner dimensions match opening.
    
    frame_inner_w = opening_w
    frame_inner_h = opening_h
    frame_outer_w = frame_inner_w + (2 * LARGE_BTN_FRAME_WIDTH)
    frame_outer_h = frame_inner_h + (2 * LARGE_BTN_FRAME_WIDTH)
    
    # Frame shape
    # We create a solid frame and union it.
    # It needs to sit on the "Right Face" but extend inwards and outwards.
    # Center of wall is at X = CORNER_COORD - (WALL_THICKNESS/2).
    # Outer surface is X = CORNER_COORD.
    # Inner surface is X = CORNER_COORD - WALL_THICKNESS.
    
    # The frame extends 1.6mm OUT from CORNER_COORD.
    # And extends IN to... "extending from inner surface outward"
    # If it starts at Inner Surface, it starts at (CORNER_COORD - WALL_THICKNESS).
    # Length = 3.2mm.
    # So it ends at (CORNER_COORD - WALL_THICKNESS) + 3.2.
    # If WALL_THICKNESS is 2.5, then it ends at CORNER_COORD - 2.5 + 3.2 = CORNER_COORD + 0.7.
    # But spec says "Protrusion: Extends 1.6mm beyond the outer surface".
    # This implies the total Z-depth of the frame is (WALL_THICKNESS + 1.6).
    # Spec says "Height: 3.2mm". This conflicts if Wall is 2.5.
    # "Height: 3.2mm (2x wall thickness)". This suggests the author assumed Wall=1.6.
    # Since we set WALL_THICKNESS=2.5, we should probably respect the "1.6mm protrusion" and "extends from inner surface" requirements.
    # So Frame Depth = WALL_THICKNESS + 1.6 = 4.1mm.
    
    frame_depth = WALL_THICKNESS + LARGE_BTN_FRAME_PROTRUSION
    
    # We build the frame on the inner surface and extrude outwards.
    frame = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD - WALL_THICKNESS)
        .center(0, z_pos)
        .rect(frame_outer_w, frame_outer_h)
        .rect(frame_inner_w, frame_inner_h) # Cut inner rect (hollow)
        .extrude(frame_depth) # Extrude outwards (+X)
    )
    
    # Fillet outer edges of frame?
    # "Rounding: 0.3mm fillet on outer edges"
    # We need to select the edges at the very top (max X).
    frame = frame.edges("|X").fillet(LARGE_BTN_OPENING_RADIUS + LARGE_BTN_FRAME_WIDTH) # Fillet corners of the rect
    # This fillets the corners of the rounded rect profile (Z-Y plane corners).
    # But wait, .rect() creates sharp corners.
    # We need to round the corners of the frame profile to match the opening radius + frame width?
    # Inner radius is 8.5. Outer radius should be 8.5 + 1.6 = 10.1.
    
    # Let's redo frame with rounded rects.
    frame = (
        cq.Workplane("YZ")
        .workplane(offset=CORNER_COORD - WALL_THICKNESS)
        .center(0, z_pos)
        # Outer wire
        .rect(frame_outer_w, frame_outer_h)
        # Inner wire
        .rect(frame_inner_w, frame_inner_h)
        .extrude(frame_depth)
    )
    
    # Apply fillets to the corners (vertical edges in YZ plane, which are parallel to X)
    # We have 4 inner corners and 4 outer corners.
    # Inner corners radius: LARGE_BTN_OPENING_RADIUS (8.5)
    # Outer corners radius: LARGE_BTN_OPENING_RADIUS + LARGE_BTN_FRAME_WIDTH (10.1)
    
    # It's tricky to select inner vs outer edges easily by string selector.
    # Easier to make the shape with correct radii 2D if possible.
    # But we can't make a face with two wires and extrude in standard CQ easily without `cut`.
    # Let's make outer solid, cut inner solid.
    
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
    
    # "Rounding: 0.3mm fillet on outer edges"
    # This likely refers to the sharp edges on the front face of the frame (the face at max X).
    # Select face at max X, then edges.
    frame = frame.faces(">X").edges().fillet(0.3)
    
    enclosure = enclosure.union(frame)
    
    return enclosure

def create_large_button():
    """
    The button itself.
    """
    # Dimensions
    w = LARGE_BTN_WIDTH
    h = LARGE_BTN_HEIGHT
    depth_base = 4.0
    depth_bevel = 4.0
    total_depth = depth_base + depth_bevel
    
    # Corner radii
    r_base = LARGE_BTN_CORNER_RADIUS_BASE
    r_top = LARGE_BTN_CORNER_RADIUS_TOP
    
    # We construct this by lofting? Or extruding and chamfering?
    # "Beveled section: 4mm depth with 45 deg bevel... on all four sides"
    # This means the top face is smaller than the base.
    # At 45 deg, if height is 4mm, the inset is 4mm on each side.
    
    # Base Section (Rectangular prism with rounded corners)
    # Workplane XY (we'll rotate it later or just export as is)
    
    base = (
        cq.Workplane("XY")
        .rect(w, h)
        .extrude(depth_base)
        .edges("|Z")
        .fillet(r_base)
    )
    
    # Top Section (Beveled)
    # Loft from Base Top Face to Top Face.
    # Base Top Face size: w, h. Radius r_base.
    # Top Face size: w - 2*4, h - 2*4. Radius r_top (5.4).
    # Height: 4.0.
    
    # We can use `loft`.
    # Create two wires.
    
    # Wire 1: Bottom of bevel (Top of base)
    w1 = (
        cq.Workplane("XY")
        .workplane(offset=depth_base)
        .rect(w, h)
        .rect(w, h) # Dummy to make it a wire? No.
    )
    # How to fillet a 2D rect in place?
    # .rect().extrude().fillet() is 3D.
    # .rect(..., radius=?) isn't standard.
    # Use polyline with arcs?
    
    # Let's use simple shapes and intersection/hull if needed.
    # Or just construct the loft with rounded rectangles.
    # Since I can't easily do rounded rect wires in one line without `rect(forConstruction=True)` tricks...
    
    # Alternative: Extrude the full shape and chamfer?
    # Chamfering a rounded rect with variable radius (because corners are rounded) is complex.
    # If we chamfer 4mm, the corner radius reduces by 4mm.
    # 8mm radius - 4mm chamfer = 4mm radius.
    # But spec says "transitions... to ~5.4mm".
    # 8 - 4 = 4mm. 5.4mm is different.
    # This implies it's not a pure 45 deg chamfer at the corners, or the "maintaining consistent proportions" logic dominates.
    
    # Let's use `loft`.
    # We need to define the wires manually.
    
    def rounded_rect_wire(workplane, width, height, radius):
        return (
            workplane
            .rect(width, height)
            .extrude(0.001) # Tiny extrude to get edges
            .edges("|Z")
            .fillet(radius)
            .wires().last() # Get the wire from the solid face? Tricky.
        )
        # Using `rect` generates a wire.
        # But we can't fillet it easily.
    
    # Base part
    button = cq.Workplane("XY").rect(w, h).extrude(depth_base).edges("|Z").fillet(r_base)
    
    # Bevel part (loft)
    w_top = w - 8.0 # 4mm bevel on each side
    h_top = h - 8.0
    
    # Get the wire from the top of the base
    wire1 = button.faces(">Z").wires().toPending()
    
    # Create the second wire at total_depth
    wire2_wp = cq.Workplane("XY").workplane(offset=total_depth).rect(w_top, h_top).extrude(0.001).edges("|Z").fillet(r_top)
    wire2 = wire2_wp.faces(">Z").wires()
    
    # Combine and loft
    bevel_section = cq.Workplane("XY").add(wire1.objects).add(wire2.objects).toPending().loft()
    
    button = button.union(bevel_section)
    
    # Texture: Dotted pattern on top surface
    # "Top surface has a dotted pattern... Only bumps within the rounded rectangle boundary"
    # Create bumps and union them.
    
    # Top surface is at Z = total_depth.
    # Dimensions: w_top, h_top, r_top.
    
    bump_dia = 1.0
    bump_height = 0.5
    bump_spacing = 1.5
    
    # Generate bump positions
    pts = []
    # Check against rounded rect shape
    # Simplest check: point must be within w_top/2, h_top/2 box AND
    # if in corner zones, within radius.
    
    dx = w_top/2 - r_top
    dy = h_top/2 - r_top
    
    # Grid
    nx = int(w_top / bump_spacing)
    ny = int(h_top / bump_spacing)
    
    for i in range(-nx, nx+1):
        x = i * bump_spacing
        for j in range(-ny, ny+1):
            y = j * bump_spacing
            
            # Check boundaries
            if abs(x) > w_top/2 or abs(y) > h_top/2:
                continue
                
            # Check corners
            in_corner = False
            corner_center = (0,0)
            
            if x > dx and y > dy:
                in_corner = True
                corner_center = (dx, dy)
            elif x < -dx and y > dy:
                in_corner = True
                corner_center = (-dx, dy)
            elif x < -dx and y < -dy:
                in_corner = True
                corner_center = (-dx, -dy)
            elif x > dx and y < -dy:
                in_corner = True
                corner_center = (dx, -dy)
                
            if in_corner:
                # Check distance to corner center
                dist = math.sqrt((x - corner_center[0])**2 + (y - corner_center[1])**2)
                if dist > r_top - (bump_dia/2):
                    continue
            else:
                # In the central cross area
                pass
            
            pts.append((x, y))
            
    if pts:
        bumps = (
            cq.Workplane("XY")
            .workplane(offset=total_depth)
            .pushPoints(pts)
            .circle(bump_dia/2)
            .extrude(bump_height) # Add bumps
        )
        button = button.union(bumps)

    return button

def add_lid_receiver(enclosure):
    """
    Add cylindrical thread receiver ring inside enclosure bottom.
    Bridges from octagonal inner walls to a circular threaded bore.
    """
    bore_radius = LID_THREAD_BORE / 2.0
    inner_flat = DEVICE_WIDTH - 2 * WALL_THICKNESS
    receiver_or = inner_flat / 2.0 + 0.5  # overlap with inner wall for solid union

    # Solid ring with central bore
    ring = (
        cq.Workplane("XY")
        .workplane(offset=LID_RECEIVER_BOTTOM_Z)
        .circle(receiver_or)
        .circle(bore_radius)
        .extrude(LID_RECEIVER_HEIGHT)
    )
    enclosure = enclosure.union(ring)

    # Internal thread ridge
    thread_start = LID_RECEIVER_BOTTOM_Z + 1.0  # 1mm lead-in
    thread = create_thread_ridge(
        bore_radius, LID_THREAD_PITCH, LID_THREAD_HEIGHT,
        LID_THREAD_DEPTH, start_z=thread_start, internal=True, overlap=0.3
    )
    enclosure = enclosure.union(thread)

    return enclosure

def create_bottom_lid():
    """
    Screw-in bottom lid with coin slot.
    Disc covers the bottom opening; threaded boss screws into receiver.
    """
    # Disc
    lid = (
        cq.Workplane("XY")
        .circle(LID_DISC_DIAMETER / 2.0)
        .extrude(LID_DISC_THICKNESS)
    )

    # Threaded boss on top of disc
    boss = (
        cq.Workplane("XY")
        .workplane(offset=LID_DISC_THICKNESS)
        .circle(LID_BOSS_OD / 2.0)
        .extrude(LID_BOSS_HEIGHT)
    )
    lid = lid.union(boss)

    # External thread on boss
    thread = create_thread_ridge(
        LID_BOSS_OD / 2.0, LID_THREAD_PITCH, LID_THREAD_HEIGHT,
        LID_THREAD_DEPTH, start_z=LID_DISC_THICKNESS, internal=False
    )
    lid = lid.union(thread)

    # Coin slot groove on bottom face
    slot = (
        cq.Workplane("XY")
        .rect(COIN_SLOT_LENGTH, COIN_SLOT_WIDTH)
        .extrude(COIN_SLOT_DEPTH)
    )
    lid = lid.cut(slot)

    # Chamfer top edge of boss for easier thread engagement
    try:
        lid = lid.faces(">Z").edges("%Circle").chamfer(0.5)
    except Exception:
        pass

    return lid

# --- Split for Printing ---

def split_enclosure(enclosure):
    """
    Split enclosure into front and back halves along Y=0 for 3D printing.
    Front half (Y>0): LEDs, mic, speaker grille
    Back half (Y<0): plain back
    Print each half with the outer flat face down on the print bed.
    Alignment pins on back half mate with holes in front half.
    """
    # Cutting half-spaces (XY workplane: normal is +Z, unambiguous positioning)
    s = 300
    pos_y_tool = cq.Workplane("XY").transformed(offset=(0, s/2, s/2 - 50)).box(s, s, s)
    neg_y_tool = cq.Workplane("XY").transformed(offset=(0, -s/2, s/2 - 50)).box(s, s, s)

    front_half = enclosure.cut(neg_y_tool)  # remove Y<0 → keep Y>0
    back_half = enclosure.cut(pos_y_tool)   # remove Y>0 → keep Y<0

    # Pin positions (X, Z) on the Y=0 split face.
    # Placed at center of left/right wall cross-sections,
    # avoiding feature zones (USB-C Z=31, power btn Z=44, large btn Z=83-130).
    wall_cx = CORNER_COORD - WALL_THICKNESS / 2
    pin_positions = [
        (wall_cx, 35), (wall_cx, 70), (wall_cx, 135),
        (-wall_cx, 35), (-wall_cx, 70), (-wall_cx, 135),
    ]

    # XZ workplane normal is -Y, so extrude(-d) goes in +Y direction.
    # Pins are 1.0mm diameter in a 1.6mm wall — the wall itself acts as the socket,
    # constraining the pin in X. Six pins at different Z positions collectively
    # prevent any Z-direction sliding.
    for x, z in pin_positions:
        # Pin: cylinder from Y=0 extending into front half (+Y)
        pin = cq.Workplane("XZ").center(x, z).circle(PIN_DIAMETER / 2).extrude(-PIN_HEIGHT)
        back_half = back_half.union(pin)

        # Matching hole in front half
        hole = cq.Workplane("XZ").center(x, z).circle(HOLE_DIAMETER / 2).extrude(-HOLE_DEPTH)
        front_half = front_half.cut(hole)

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
    
    # Shelling
    # To have a constant wall thickness, use `shell`.
    # A negative thickness hollows inwards.
    # If we want an opening, we select faces to remove.
    # Let's remove the bottom face to allow battery insertion?
    # Selecting the bottom face might be tricky after fillet.
    # It's the face at min Z.
    
    # shell() is computationally expensive and sometimes fails on complex fillets.
    # Alternative: Create an inner solid (smaller) and cut it.
    
    inner_width = DEVICE_WIDTH - (2 * WALL_THICKNESS)
    # Scale calculation for inner octagon
    # We can just offset the profile?
    # `2D offset` is better.
    
    # Re-create inner shape
    # Profile offset -2.5mm
    # To do this robustly:
    # 1. Create base profile (wire)
    # 2. Offset 2D wire inwards
    # 3. Extrude
    # 4. Cut from outer.
    
    # Outer solid (already made)
    
    # Inner solid
    # We need the inner profile.
    # The octagon profile function uses points.
    # Calculating offset points for octagon is easy.
    # Move each face in by thickness.
    # Or just use `cq.Workplane("XY").polyline(pts).close().offset2D(-WALL_THICKNESS)`
    
    # Inner height:
    # If we want a closed top and bottom?
    # Or open bottom?
    # Let's assume open bottom for assembly.
    
    h_inner = DEVICE_HEIGHT - WALL_THICKNESS # Solid top
    
    # Points again
    max_c = DEVICE_WIDTH / 2.0
    h_l = HALF_LONG_SIDE
    pts = [
        (max_c, h_l), (h_l, max_c), (-h_l, max_c), (-max_c, h_l),
        (-max_c, -h_l), (-h_l, -max_c), (h_l, -max_c), (max_c, -h_l)
    ]
    
    inner_solid = (
        cq.Workplane("XY")
        .polyline(pts).close()
        .offset2D(-WALL_THICKNESS)
        .extrude(h_inner) # Extrude from 0 to h_inner
    )
    
    # Move inner solid up?
    # If we want bottom open, inner solid starts at Z = -something to cut through bottom.
    # And goes up to HEIGHT - WALL_THICKNESS.
    
    inner_solid = (
        cq.Workplane("XY")
        .workplane(offset=-1.0) # Start below bottom
        .polyline(pts).close()
        .offset2D(-WALL_THICKNESS)
        .extrude(h_inner + 1.0) # Go up to match top thickness
    )
    
    # Also need to fillet the inner top edges to match outer?
    # If outer has 4mm radius, inner should have 4-2.5 = 1.5mm radius?
    # Yes, to maintain constant wall.
    inner_fillet = FILLET_RADIUS - WALL_THICKNESS
    if inner_fillet > 0:
        # Fillet inner top edges
        inner_solid = inner_solid.edges(">Z").fillet(inner_fillet)
        # Fillet vertical edges?
        # Outer vertical edges are 4mm.
        # Inner vertical edges should be 1.5mm.
        inner_solid = inner_solid.edges("|Z").fillet(inner_fillet)
    
    enclosure = solid.cut(inner_solid)
    
    # 3. Add Features
    enclosure = add_led_holes(enclosure)
    enclosure = add_mic_hole_and_mount(enclosure)
    enclosure = add_speaker_grille(enclosure)
    enclosure = add_power_button(enclosure)
    enclosure = add_usbc_port(enclosure)
    enclosure = add_large_button_feature(enclosure)
    enclosure = add_lid_receiver(enclosure)

    return enclosure

if __name__ == "__main__":
    # Ensure output directory exists
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

    print("Generating bottom lid...")
    lid = create_bottom_lid()
    cq.exporters.export(lid, str(output_dir / "bottom_lid.stl"))
    print("Exported bottom_lid.stl")
