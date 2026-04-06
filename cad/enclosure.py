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
LED_DIAMETER = 3.0  # 3mm holes for WS2812B-2020 (2mm) with light diffusion margin
LED_POSITIONS_X = [5.0, 11.0]  # Two RGB LEDs, both on right (chassis) half
LED_TOP_OFFSET = 10.0

MIC_HOLE_DIAMETER = 1.5
MIC_BOTTOM_OFFSET = 10.0
MIC_PORT_DIAMETER = 1.0 # Internal port
MIC_POCKET_WIDTH = 4.72 + 0.2
MIC_POCKET_HEIGHT = 3.76 + 0.2
MIC_POCKET_DEPTH = 1.0 # Depth of pocket into the wall (from inside)
MIC_X_OFFSET = 1.0  # Shifted +1mm so hole is fully on chassis half after X=0 split

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
# Runs along Z on front/back wall seams for X=0 split alignment.
TONGUE_WIDTH = 1.0            # In Y direction, within 1.6mm wall
TONGUE_HEIGHT = 0.8           # Protrusion in X direction from split face
TONGUE_CLEARANCE = 0.15       # Per side for FDM tolerance
GROOVE_WIDTH = TONGUE_WIDTH + 2 * TONGUE_CLEARANCE
GROOVE_DEPTH = TONGUE_HEIGHT + TONGUE_CLEARANCE
TONGUE_Z_MARGIN = 5.0         # Inset from top/bottom to avoid interfering with fillets

# Cantilever snap clips (retention for split halves)
# Beams on cover (left) half flex in X to engage hooks in chassis (right) half pockets.
SNAP_BEAM_LENGTH = 8.0        # Along Z axis
SNAP_BEAM_WIDTH = 3.0         # Along Y axis (within wall)
SNAP_BEAM_THICKNESS = 0.8     # In X direction
SNAP_HOOK_DEPTH = 0.4         # Additional Y protrusion at hook tip
SNAP_HOOK_HEIGHT = 1.0        # Z extent of hook
SNAP_HOOK_RAMP = 1.5          # Z extent of 30° lead-in ramp
SNAP_CLEARANCE = 0.2          # Clearance around beam in pocket
SNAP_POCKET_DEPTH = SNAP_BEAM_THICKNESS + SNAP_HOOK_DEPTH + SNAP_CLEARANCE

# Battery cradle (18650: 18.6mm diameter x 65mm length)
# Cradle is on the cover (X<0) half with >180° snap-in grips.
# Battery center is offset toward the cover wall so the rib's -X side
# overlaps with the wall (no struts needed) and the +X lips provide snap-in.
BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65.0
BATTERY_CRADLE_RADIUS = BATTERY_DIAMETER / 2 + 0.2  # 0.2mm clearance
BATTERY_CRADLE_THICKNESS = 1.5  # Rib wall thickness (thin enough to flex for snap-in)
BATTERY_CRADLE_RIB_WIDTH = 3.0  # Rib width along Z axis
BATTERY_CRADLE_ARC_DEG = 210.0  # >180° for snap-in (gives ~0.25mm interference)
BATTERY_CRADLE_BOTTOM_Z = WALL_THICKNESS + 2.0  # 2mm above bottom wall for spring clearance
# Battery center X: positioned so rib outer surface overlaps wall by 0.5mm
_INNER_WALL_X = DEVICE_WIDTH / 2.0 - WALL_THICKNESS
_OUTER_R = BATTERY_CRADLE_RADIUS + BATTERY_CRADLE_THICKNESS
BATTERY_CENTER_X = -(_INNER_WALL_X + 0.5 - _OUTER_R)  # ~ -7.9mm
# Rib Z positions: bottom, middle, top of battery zone (avoiding contact platforms)
BATTERY_CRADLE_RIB_Z = [
    BATTERY_CRADLE_BOTTOM_Z + 8.0,           # Near bottom (above spring contact)
    BATTERY_CRADLE_BOTTOM_Z + 34.0,          # Middle
    BATTERY_CRADLE_BOTTOM_Z + 60.0,          # Near top (below plate contact)
]

# Battery contacts (Keystone 5222/5224 style)
# Spring contact (negative) at bottom, plate contact (positive) at top.
# Connected to main board via 2-wire JST cable.
CONTACT_WIDTH = 12.0           # Contact base plate width
CONTACT_DEPTH = 10.0           # Contact base plate depth (along Z)
CONTACT_FACE_SPACING = 69.5    # Inner face-to-face distance (cell OAL + spring preload)
CONTACT_SCREW_SPACING = 7.5    # M2 mounting hole center-to-center
CONTACT_SCREW_PILOT = 1.6      # M2 pilot hole diameter for self-tapping in plastic
CONTACT_BOSS_OD = 4.5          # Screw boss outer diameter
CONTACT_BOSS_HEIGHT = 3.0      # Boss protrusion height from platform face
CONTACT_PLATFORM_THICKNESS = 2.0  # Platform wall thickness
CONTACT_WIRE_CHANNEL = 3.0     # Wire channel width/height for JST cable routing

# Z positions for contact faces (battery-facing surfaces)
CONTACT_BOTTOM_Z = BATTERY_CRADLE_BOTTOM_Z              # Spring contact face
CONTACT_TOP_Z = CONTACT_BOTTOM_Z + CONTACT_FACE_SPACING # Plate contact face

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

def add_battery_cradle(half):
    """
    Thin-walled arc cradle ribs on the cover (X<0) half for an 18650 battery.
    Battery center is offset toward the cover wall (BATTERY_CENTER_X) so the
    rib's -X side overlaps with the inner wall for solid fusion, while the
    +X lips are thin enough (1.5mm) to flex for snap-in insertion.
    """
    inner_r = BATTERY_CRADLE_RADIUS
    outer_r = inner_r + BATTERY_CRADLE_THICKNESS  # Thin wall, not solid fill
    cx = BATTERY_CENTER_X

    # The arc spans from (90 - overhang) to (270 + overhang) degrees,
    # where overhang = (arc_deg - 180) / 2. Centered on 180° (-X direction).
    overhang_deg = (BATTERY_CRADLE_ARC_DEG - 180.0) / 2.0
    cut_half_angle = 90.0 - overhang_deg  # Degrees from +X axis to cut boundary

    # Wedge to cut: sector from -cut_half_angle to +cut_half_angle (the +X opening)
    cut_angle_rad = math.radians(cut_half_angle)
    s = outer_r + 5  # Extends beyond the ring
    wedge_pts = [
        (0, 0),
        (s, s * math.tan(cut_angle_rad)),
        (s, -s * math.tan(cut_angle_rad)),
    ]

    for z_pos in BATTERY_CRADLE_RIB_Z:
        # Thin ring centered on battery position
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z_pos)
            .center(cx, 0)
            .circle(outer_r)
            .circle(inner_r)
            .extrude(BATTERY_CRADLE_RIB_WIDTH)
        )

        # Cut the +X sector wedge (relative to battery center)
        wedge = (
            cq.Workplane("XY")
            .workplane(offset=z_pos - 0.5)
            .center(cx, 0)
            .polyline(wedge_pts).close()
            .extrude(BATTERY_CRADLE_RIB_WIDTH + 1)
        )
        rib = rib.cut(wedge)

        half = half.union(rib)

    return half


def add_battery_contact_mounts(half):
    """
    Add mounting platforms for Keystone-style battery contacts on the cover half.
    Bottom platform: spring contact (negative terminal), spring faces +Z.
    Top platform: plate contact (positive terminal), plate faces -Z.
    Each platform has M2 screw bosses and a wire channel for JST cable routing.
    """
    inner_wall_x = DEVICE_WIDTH / 2.0 - WALL_THICKNESS  # Inner wall distance from center
    overlap = 0.5  # Into wall for solid boolean fusion

    for is_top in [False, True]:
        if is_top:
            # Top platform: contact face points down (-Z), platform above the face
            face_z = CONTACT_TOP_Z
            platform_z = face_z  # Platform extends upward from contact face
            boss_dir = -1  # Bosses extend downward toward battery
        else:
            # Bottom platform: contact face points up (+Z), platform below the face
            face_z = CONTACT_BOTTOM_Z
            platform_z = face_z - CONTACT_PLATFORM_THICKNESS
            boss_dir = 1  # Bosses extend upward toward battery

        # Platform: spans from inner wall (with overlap) to past battery center
        # to support the screw bosses centered on the battery axis.
        cx = BATTERY_CENTER_X
        platform_width_y = CONTACT_WIDTH + 2.0  # Contact width + 1mm margin each side
        boss_overshoot = CONTACT_BOSS_OD / 2 + 0.5
        platform_x_min = -(inner_wall_x + overlap)
        platform_x_max = cx + boss_overshoot
        platform_extent_x = platform_x_max - platform_x_min
        platform_center_x = (platform_x_min + platform_x_max) / 2

        platform = (
            cq.Workplane("XY")
            .workplane(offset=platform_z)
            .center(platform_center_x, 0)
            .rect(platform_extent_x, platform_width_y)
            .extrude(CONTACT_PLATFORM_THICKNESS)
        )
        half = half.union(platform)

        # M2 screw bosses on the battery-facing side of the platform.
        # Bosses embed 0.5mm into the platform for solid boolean fusion.
        embed = 0.5
        for screw_sign in [-1, 1]:
            screw_y = screw_sign * CONTACT_SCREW_SPACING / 2

            # Solid boss (embedded into platform, centered on battery axis)
            boss_start_z = face_z - embed if boss_dir > 0 else face_z + embed
            boss = (
                cq.Workplane("XY")
                .workplane(offset=boss_start_z)
                .center(cx, screw_y)
                .circle(CONTACT_BOSS_OD / 2)
                .extrude(boss_dir * (CONTACT_BOSS_HEIGHT + embed))
            )
            half = half.union(boss)

            # Pilot hole through boss and platform
            hole_z_start = platform_z - 0.5 if not is_top else face_z - 0.5
            hole_depth = CONTACT_PLATFORM_THICKNESS + CONTACT_BOSS_HEIGHT + 1
            pilot = (
                cq.Workplane("XY")
                .workplane(offset=hole_z_start)
                .center(cx, screw_y)
                .circle(CONTACT_SCREW_PILOT / 2)
                .extrude(hole_depth)
            )
            half = half.cut(pilot)

        # Wire channel: notch in the platform edge for JST cable routing
        # Positioned at the -X edge (toward the wall) so wires run along the wall
        channel = (
            cq.Workplane("XY")
            .workplane(offset=platform_z - 0.5)
            .center(-inner_wall_x + CONTACT_WIRE_CHANNEL / 2, 0)
            .rect(CONTACT_WIRE_CHANNEL + 1, CONTACT_WIRE_CHANNEL)
            .extrude(CONTACT_PLATFORM_THICKNESS + 1)
        )
        half = half.cut(channel)

    return half


# --- Split for Printing ---

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

    # --- Step 4: Battery cradle and contact mounts on cover (left) half ---
    # Added after split so snap-in lips can extend past X=0.
    left_half = add_battery_cradle(left_half)
    left_half = add_battery_contact_mounts(left_half)

    return right_half, left_half

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
    right_half, left_half = split_enclosure(enclosure)
    cq.exporters.export(right_half, str(output_dir / "enclosure_right.stl"))
    print("Exported enclosure_right.stl")
    cq.exporters.export(left_half, str(output_dir / "enclosure_left.stl"))
    print("Exported enclosure_left.stl")

    print("Generating large button...")
    button = create_large_button()
    cq.exporters.export(button, str(output_dir / "large_button.stl"))
    print("Exported large_button.stl")


if __name__ == "__main__":
    main()
