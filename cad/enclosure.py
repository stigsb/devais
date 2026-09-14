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
LED_DIAMETER = 3.2  # Through-hole 3 mm LED domes pass the wall; 0.2 mm clearance
LED_POSITIONS_X = [0.0, 6.0]  # Two RGB LEDs; X=6 keeps the hole clear of the front-face chamfer
LED_BOARD_X = sum(LED_POSITIONS_X) / len(LED_POSITIONS_X)  # Daughterboard centred on the emitters
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

# Diagonal seam: X-Y=-4, chassis keeps the X+ and Y- active faces.
SPLIT_OFFSET = -4.0
PIN_DIAMETER = 3.0
PIN_LENGTH = 3.0
PIN_CLEARANCE = 0.30  # Diametral; calibrate using the exported coupon.
JOINT_GAP = 0.20
JOINT_PAD_RADIUS = 4.0
JOINT_PAD_DEPTH = 5.0
PIN_POSITIONS = [(-18.8, 5.5), (18.8, 144.5)]  # seam-local u, global Z
SCREW_POSITIONS = [(-18.8, 144.5), (18.8, 5.5)]
SCREW_PILOT_DIA = 1.6  # Prototype M2 plastic-thread pilot; tune for chosen screw.
SCREW_CLEARANCE = 2.3
SCREW_HEAD_CLEARANCE = 4.5

# Prospective main-board envelope, not the existing 36 mm electrical layout.
PCB_WIDTH = 26.0
PCB_HEIGHT = 126.0
PCB_THICKNESS = 1.6
PCB_FACE_X = 11.5
PCB_Y_OFFSET = 75.0
PCB_MOUNTING_HOLES = [(y, z-75) for y in (-10, 10) for z in (16, 38, 97, 115, 134)]
BOSS_OD = 4.5
PCB_RAIL_DEPTH = 4.8

BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65.0
BATTERY_CENTER_X = -3.0
BATTERY_BOTTOM_Z = 20.0
BATTERY_CLEARANCE = 0.3
BATTERY_CRADLE_THICKNESS = 1.8
BATTERY_CRADLE_RIB_WIDTH = 4.0
BATTERY_CRADLE_RIB_Z = (25.0, 69.0)
BATTERY_STRAP_WIDTH = 3.5
# Contact carriers include a lead slot and, on the positive end, a plate
# pocket; no rivet hole or boss for a particular purchased contact. Sized for the Keystone 5201/5223 plates.
CONTACT_PLATE_THICKNESS = 2.0
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

# Custom daughterboard seats; these are mechanical design constraints.
MIC_BOARD_WIDTH, MIC_BOARD_HEIGHT = 15.0, 8.0

# Field-unit variant (hardware/PROTOTYPE.md): stripboard carrier, XIAO nRF52840
# Sense, Adafruit 3492 PDM microphone breakout. Product geometry is unchanged.
FIELD_MIC_BOARD = (14.0, 12.8)  # Adafruit 3492 outline; the product board is 15 x 8
FIELD_TOP_USBC = (7.05, 0.0, 7.5, 13.0, 2.0)  # centre X, centre Y, X size, Y size, corner radius
FIELD_BOARD_WIDTH, FIELD_BOARD_HEIGHT = 25.4, 135.0  # 1 in stripboard, Z 12..147
FIELD_BOARD_WINDOWS = ((136.3, 12.0), (119.5, 13.0))  # (centre Z, Z size), 8 mm wide at Y = 0


def mic_board_size(variant='product'):
    return FIELD_MIC_BOARD if variant == 'field' else (MIC_BOARD_WIDTH, MIC_BOARD_HEIGHT)


LED_BOARD_WIDTH, LED_BOARD_HEIGHT = 12.0, 8.0  # Two 3 mm RGB LEDs and a 7-way SH header
AUDIO_BOARD_THICKNESS = 1.6
SPEAKER_BODY_DIAMETER = 20.0
SPEAKER_BODY_DEPTH = 5.3  # Same Sky CMS-2053-18SP; the 4.0 mm CMS-2004 also fits
MOUNT_CLEARANCE = 0.3

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
    2x 3.2 mm holes for 3 mm RGB LEDs at explicit X positions.
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

def seam_plane(depth=0):
    n = 1 / math.sqrt(2)
    return cq.Plane(origin=(SPLIT_OFFSET/2 + depth*n,
                            -SPLIT_OFFSET/2 - depth*n, 0),
                    xDir=(n, n, 0), normal=(n, -n, 0))


def seam_cylinder(u, z, radius, start, depth):
    return cq.Workplane(seam_plane(start)).center(u, z).circle(radius).extrude(depth)


def board_envelope():
    return cq.Workplane('XY').box(PCB_THICKNESS, PCB_WIDTH, PCB_HEIGHT).translate(
        (PCB_FACE_X-PCB_THICKNESS/2, 0, PCB_Y_OFFSET))


def field_stripboard_envelope():
    z = PCB_Y_OFFSET - PCB_HEIGHT/2 + FIELD_BOARD_HEIGHT/2
    board = cq.Workplane('XY').box(PCB_THICKNESS, FIELD_BOARD_WIDTH, FIELD_BOARD_HEIGHT).translate(
        (PCB_FACE_X - PCB_THICKNESS/2, 0, z))
    # The seam pin pad at (18.8, 144.5) reaches Y 9.43 at Z 140.9..147; the XIAO's Y+
    # castellation row at Y 8.89 keeps the board under it, so notch the Y+ top corner.
    return board.cut(cq.Workplane('XY').box(5, 5, 10).translate(
        (PCB_FACE_X - PCB_THICKNESS/2, 11.5, 145)))


def field_stripboard_template():
    """Stripboard drilling template: the ten PCB holes plus two lead windows."""
    board = field_stripboard_envelope()
    for y, z in PCB_MOUNTING_HOLES:
        board = board.cut(cq.Workplane('YZ', origin=(PCB_FACE_X+1, y, z+PCB_Y_OFFSET)).circle(1.1).extrude(-5))
    for zc, zs in FIELD_BOARD_WINDOWS:
        board = board.cut(cq.Workplane('XY').box(PCB_THICKNESS+1, 8, zs).translate((PCB_FACE_X - PCB_THICKNESS/2, 0, zc)))
    return board


def battery_envelope():
    return cq.Workplane('XY').center(BATTERY_CENTER_X, 0).circle(
        BATTERY_DIAMETER/2).extrude(BATTERY_LENGTH).translate((0, 0, BATTERY_BOTTOM_Z))


def add_component_mounts(chassis, variant='product'):
    # Continuous rails carry bosses in the button opening back to intact wall.
    rail_bottom, rail_top = 13.0, 137.0
    for y in (-10, 10):
        rail = cq.Workplane('XY').box(PCB_RAIL_DEPTH, BOSS_OD, rail_top-rail_bottom).translate(
            (PCB_FACE_X+PCB_RAIL_DEPTH/2, y, (rail_top+rail_bottom)/2))
        chassis = chassis.union(rail)
    for y, board_z in PCB_MOUNTING_HOLES:
        z = board_z + PCB_Y_OFFSET
        # Only the three intact-wall stations extend all the way to the shell.
        depth = 18.9-PCB_FACE_X if z in (16, 38, 134) else PCB_RAIL_DEPTH
        boss = cq.Workplane('YZ', origin=(PCB_FACE_X, y, z)).circle(BOSS_OD/2).extrude(depth)
        chassis = chassis.union(boss)
        pilot = cq.Workplane('YZ', origin=(PCB_FACE_X-0.1, y, z)).circle(
            SCREW_PILOT_DIA/2).extrude(min(depth-0.8, 4.0)+0.1)
        chassis = chassis.cut(pilot)

    # Open saddles, tied to the front wall. Straps retain the cell cover-off.
    radius = BATTERY_DIAMETER/2 + BATTERY_CLEARANCE
    for z in BATTERY_CRADLE_RIB_Z:
        saddle = cq.Workplane('XY').center(BATTERY_CENTER_X, 0).circle(
            radius+BATTERY_CRADLE_THICKNESS).circle(radius).extrude(BATTERY_CRADLE_RIB_WIDTH)
        saddle = saddle.intersect(cq.Workplane('XY').box(60, 30, 10).translate((0,-15,2)))
        web = cq.Workplane('XY').box(16, 10, BATTERY_CRADLE_RIB_WIDTH).translate(
            (BATTERY_CENTER_X,-14, BATTERY_CRADLE_RIB_WIDTH/2))
        web = web.cut(cq.Workplane('XY').center(BATTERY_CENTER_X,0).circle(radius).extrude(10))
        saddle = saddle.union(web).translate((0,0,z))
        # Two through-slots allow a small cable tie around the cell and saddle.
        for x in (BATTERY_CENTER_X-6, BATTERY_CENTER_X+6):
            slot = cq.Workplane('XY').box(BATTERY_STRAP_WIDTH,2,10).translate((x,-15,z+2))
            saddle = saddle.cut(slot)
        chassis = chassis.union(saddle)
    for z in (BATTERY_BOTTOM_Z-CONTACT_SPACE-CONTACT_PLATE_THICKNESS,
              BATTERY_BOTTOM_Z+BATTERY_LENGTH+CONTACT_SPACE):
        carrier = cq.Workplane('XY').box(14,22,CONTACT_PLATE_THICKNESS).translate(
            (BATTERY_CENTER_X,-8,z+CONTACT_PLATE_THICKNESS/2))
        # Slot for a contact strip or lead through the carrier; add insulating liner.
        # The modeled BAT leads route outside the carrier instead.
        slot = cq.Workplane('XY').box(5,1.5,6).translate((BATTERY_CENTER_X,0,z+1))
        chassis = chassis.union(carrier.cut(slot))
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

    # Recessed seats locate custom mic/LED boards. Removable adhesive on the
    # perimeter retains them without blocking the acoustic/light windows.
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

    # Speaker cup: front gasket seat, rear insertion, cable-tie retention.
    z = DEVICE_HEIGHT-SPEAKER_TOP_OFFSET-SPEAKER_DIAMETER/2
    # 0.6 front recess plus the full body; the rear face stops at the PCB edge.
    cup = cq.Workplane('XZ', origin=(0,-18.9,z)).circle(
        SPEAKER_BODY_DIAMETER/2+2).circle(SPEAKER_BODY_DIAMETER/2+MOUNT_CLEARANCE).extrude(-(SPEAKER_BODY_DEPTH+0.6))
    # The narrow top of the ring is trimmed back so the LED harness passes behind it.
    cup = cup.cut(cq.Workplane('XY').box(8,0.9,12).translate((0,-13.45,z+14)))
    chassis = chassis.union(cup)
    for x in (-12,12):
        lug = cq.Workplane('XY').box(4,5,7).translate((x,-16.5,z))
        slot = cq.Workplane('XY').box(2,8,BATTERY_STRAP_WIDTH).translate((x,-16.5,z))
        chassis = chassis.union(lug.cut(slot))
    return chassis


def split_enclosure(enclosure, variant='product'):
    """Offset diagonal joint with two round pins, blind sockets and M2 closure."""
    positive = cq.Workplane(seam_plane()).center(0,75).rect(200,300).extrude(100)
    negative = cq.Workplane(seam_plane(-JOINT_GAP)).center(0,75).rect(200,300).extrude(-100)
    # Clip seam pads to the original outside envelope so none protrude.
    envelope = create_octagonal_prism(DEVICE_HEIGHT, DEVICE_WIDTH, HALF_LONG_SIDE, FILLET_RADIUS)
    envelope = envelope.edges('<Z or >Z').fillet(FILLET_RADIUS)
    for u,z in PIN_POSITIONS + SCREW_POSITIONS:
        pad = seam_cylinder(u,z,JOINT_PAD_RADIUS,-JOINT_PAD_DEPTH,2*JOINT_PAD_DEPTH)
        enclosure = enclosure.union(pad.intersect(envelope))
    chassis, cover = enclosure.intersect(positive), enclosure.intersect(negative)
    for u,z in PIN_POSITIONS:
        pin = seam_cylinder(u,z,PIN_DIAMETER/2,0.3,-PIN_LENGTH-0.3)
        pin = pin.faces('<(1,-1,0)').edges().chamfer(0.35)
        chassis = chassis.union(pin)
        socket = seam_cylinder(u,z,(PIN_DIAMETER+PIN_CLEARANCE)/2,0.1,-PIN_LENGTH-0.6)
        cover = cover.cut(socket)
    for u,z in SCREW_POSITIONS:
        chassis = chassis.cut(seam_cylinder(u,z,SCREW_PILOT_DIA/2,-0.1,4.1))
        cover = cover.cut(seam_cylinder(u,z,SCREW_CLEARANCE/2,0.1,-50))
        cover = cover.cut(seam_cylinder(u,z,SCREW_HEAD_CLEARANCE/2,-2.5,-50))
    # Clip internal mounts to the exterior while preserving the raised controls.
    chassis = chassis.union(add_component_mounts(chassis, variant).intersect(envelope))
    # Trim only the frame corner that would extend below the diagonal bed face.
    bed_depth = (CORNER_COORD+HALF_LONG_SIDE-SPLIT_OFFSET)/math.sqrt(2)
    bed_limit = cq.Workplane(seam_plane(bed_depth)).center(0,75).rect(200,300).extrude(-100)
    chassis = chassis.intersect(bed_limit)
    return chassis, cover


def print_orientation(part, cover=False):
    # Lay the opposite diagonal chamfer on the bed, cavities upward.
    part = part.rotate((0,0,0),(0,0,1),45).rotate((0,0,0),(0,1,0),-90 if cover else 90)
    box = part.val().BoundingBox()
    return part.translate((-box.center.x,-box.center.y,-box.zmin))


def check_assembly(chassis, cover, variant='product'):
    for name, part in [('chassis',chassis),('cover',cover)]:
        assert part.val().isValid(), f'{name}: invalid BREP'
        assert part.solids().size() == 1, f'{name}: disconnected mounting features'
    assert chassis.intersect(cover).val().Volume() < 1e-5, 'shells collide'
    board = field_stripboard_envelope() if variant == 'field' else board_envelope()
    for name, envelope in [('PCB',board),('battery',battery_envelope())]:
        for part in (chassis,cover):
            assert part.intersect(envelope).val().Volume() < 1e-5, f'{name} collides with shell/mounts'
    speaker_z = DEVICE_HEIGHT-SPEAKER_TOP_OFFSET-SPEAKER_DIAMETER/2
    speaker = cq.Workplane('XZ',origin=(0,-18.3,speaker_z)).circle(
        SPEAKER_BODY_DIAMETER/2).extrude(-SPEAKER_BODY_DEPTH)
    components = [('speaker', speaker)]
    mic_w, mic_h = mic_board_size(variant)
    for x,z,w,h in ((MIC_X_OFFSET,MIC_BOTTOM_OFFSET,mic_w,mic_h),
                    (LED_BOARD_X,DEVICE_HEIGHT-LED_TOP_OFFSET,LED_BOARD_WIDTH,LED_BOARD_HEIGHT)):
        components.append(('daughterboard',cq.Workplane('XY').box(w,AUDIO_BOARD_THICKNESS,h).translate(
            (x,-17+AUDIO_BOARD_THICKNESS/2,z))))
    for name, component in components:
        for solid in (chassis,cover,board,battery_envelope()):
            assert solid.intersect(component).val().Volume() < 1e-5, f'{name} interference'
    for u,z in PIN_POSITIONS:
        shaft = seam_cylinder(u,z,PIN_DIAMETER/2,-0.4,-2.0)
        for delta in ((0.5/math.sqrt(2),0.5/math.sqrt(2),0),(0,0,0.5)):
            assert cover.intersect(shaft.translate(delta)).val().Volume() > 0.01, 'pin fails to locate in two directions'
        floor = seam_cylinder(u,z,0.5,-3.8,-0.3)
        assert cover.intersect(floor).val().Volume() > 0.2, 'socket is not blind'
    # Cover must slide off along the pin axis without catching chassis features.
    for distance in (0.5, 2, 4, 10, 25, 50):
        moved = cover.translate((-distance/math.sqrt(2),distance/math.sqrt(2),0))
        assert chassis.intersect(moved).val().Volume() < 1e-5, f'cover catches at {distance} mm'


# --- Main Build ---

def build_enclosure(variant='product'):
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
    if variant == 'field':
        enclosure = add_top_usbc_port(enclosure)
    else:
        enclosure = add_usbc_port(enclosure)
    enclosure = add_large_button_feature(enclosure)

    return enclosure

def fit_coupon():
    """Same upright pin/socket orientation as shell prints, three clearances."""
    pins = cq.Workplane('XY').box(36,10,2,centered=(True,True,False))
    sockets = cq.Workplane('XY').box(36,10,5,centered=(True,True,False))
    for x, clearance in zip((-12,0,12),(0.2,PIN_CLEARANCE,0.4)):
        pin = cq.Workplane('XY',origin=(x,0,2)).circle(PIN_DIAMETER/2).extrude(PIN_LENGTH)
        pins = pins.union(pin.faces('>Z').edges().chamfer(0.35))
        hole = cq.Workplane('XY',origin=(x,0,5)).circle((PIN_DIAMETER+clearance)/2).extrude(-PIN_LENGTH-0.5)
        sockets = sockets.cut(hole)
    return pins, sockets


def export_stl(part, path):
    import trimesh
    cq.exporters.export(part, str(path), tolerance=0.02, angularTolerance=0.1)
    mesh = trimesh.load(path, force='mesh')
    # OCC's pole tessellation produces zero-area faces. Remove only those;
    # never fill holes or reshape a failed export to conceal invalid geometry.
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent, f'Bad STL: {path}'
    assert len(mesh.split()) == 1, f'Disconnected STL: {path}'
    mesh.export(path)


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


if __name__ == '__main__':
    main()
