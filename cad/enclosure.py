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
# Contact carriers intentionally accept adhesive copper/nickel contact strips;
# no unsupported claim of compatibility with a particular purchased holder.
CONTACT_PLATE_THICKNESS = 2.0
CONTACT_SPACE = 3.0  # Space beyond each cell end for contact/spring + insulation.

# Custom daughterboard seats; these are mechanical design constraints.
MIC_BOARD_WIDTH, MIC_BOARD_HEIGHT = 15.0, 8.0
LED_BOARD_WIDTH, LED_BOARD_HEIGHT = 10.0, 8.0
AUDIO_BOARD_THICKNESS = 1.6
SPEAKER_BODY_DIAMETER = 20.0
SPEAKER_BODY_DEPTH = 4.0
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


def battery_envelope():
    return cq.Workplane('XY').center(BATTERY_CENTER_X, 0).circle(
        BATTERY_DIAMETER/2).extrude(BATTERY_LENGTH).translate((0, 0, BATTERY_BOTTOM_Z))


def add_component_mounts(chassis):
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
        # Contact strip/wire passes through the carrier; add insulating liner.
        slot = cq.Workplane('XY').box(5,1.5,6).translate((BATTERY_CENTER_X,0,z+1))
        chassis = chassis.union(carrier.cut(slot))

    # Recessed seats locate custom mic/LED boards. Removable adhesive on the
    # perimeter retains them without blocking the acoustic/light windows.
    for x,z,w,h in ((MIC_X_OFFSET,MIC_BOTTOM_OFFSET,MIC_BOARD_WIDTH,MIC_BOARD_HEIGHT),
                    (8,DEVICE_HEIGHT-LED_TOP_OFFSET,LED_BOARD_WIDTH,LED_BOARD_HEIGHT)):
        seat = cq.Workplane('XY').box(w+4,3.5,h+4).translate((x,-17.5,z))
        pocket = cq.Workplane('XY').box(w+MOUNT_CLEARANCE,4,h+MOUNT_CLEARANCE).translate((x,-15.0,z))
        # Preserve the acoustic/light path through the center of the seat.
        window = cq.Workplane('XY').box(w-2,8,h-2).translate((x,-18,z))
        seat = seat.cut(pocket).cut(window)
        chassis = chassis.union(seat)

    # Speaker cup: front gasket seat, rear insertion, cable-tie retention.
    z = DEVICE_HEIGHT-SPEAKER_TOP_OFFSET-SPEAKER_DIAMETER/2
    cup = cq.Workplane('XZ', origin=(0,-18.9,z)).circle(
        SPEAKER_BODY_DIAMETER/2+2).circle(SPEAKER_BODY_DIAMETER/2+MOUNT_CLEARANCE).extrude(-5.0)
    chassis = chassis.union(cup)
    for x in (-12,12):
        lug = cq.Workplane('XY').box(4,5,7).translate((x,-16.5,z))
        slot = cq.Workplane('XY').box(2,8,BATTERY_STRAP_WIDTH).translate((x,-16.5,z))
        chassis = chassis.union(lug.cut(slot))
    return chassis


def split_enclosure(enclosure):
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
    chassis = chassis.union(add_component_mounts(chassis).intersect(envelope))
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


def check_assembly(chassis, cover):
    for name, part in [('chassis',chassis),('cover',cover)]:
        assert part.val().isValid(), f'{name}: invalid BREP'
        assert part.solids().size() == 1, f'{name}: disconnected mounting features'
    assert chassis.intersect(cover).val().Volume() < 1e-5, 'shells collide'
    for name, envelope in [('PCB',board_envelope()),('battery',battery_envelope())]:
        for part in (chassis,cover):
            assert part.intersect(envelope).val().Volume() < 1e-5, f'{name} collides with shell/mounts'
    speaker_z = DEVICE_HEIGHT-SPEAKER_TOP_OFFSET-SPEAKER_DIAMETER/2
    speaker = cq.Workplane('XZ',origin=(0,-18.3,speaker_z)).circle(
        SPEAKER_BODY_DIAMETER/2).extrude(-SPEAKER_BODY_DEPTH)
    components = [('speaker', speaker)]
    for x,z,w,h in ((MIC_X_OFFSET,MIC_BOTTOM_OFFSET,MIC_BOARD_WIDTH,MIC_BOARD_HEIGHT),
                    (8,DEVICE_HEIGHT-LED_TOP_OFFSET,LED_BOARD_WIDTH,LED_BOARD_HEIGHT)):
        components.append(('daughterboard',cq.Workplane('XY').box(w,AUDIO_BOARD_THICKNESS,h).translate(
            (x,-17+AUDIO_BOARD_THICKNESS/2,z))))
    for name, component in components:
        for solid in (chassis,cover,board_envelope(),battery_envelope()):
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


def main():
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)
    chassis, cover = split_enclosure(build_enclosure())
    check_assembly(chassis, cover)
    for name, part in [('chassis',chassis),('cover',cover)]:
        for suffix, shape in [('assembled',part),('print',print_orientation(part,name=='cover'))]:
            path = output_dir / f'{name}_{suffix}'
            export_stl(shape, path.with_suffix('.stl'))
            cq.exporters.export(shape, str(path.with_suffix('.step')))
            print(f'Exported {path}: one valid solid', flush=True)
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
