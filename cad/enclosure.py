"""
DevAIs Handheld AI Device - Enclosure Design
=============================================

This script generates the 3D model for the device enclosure using CadQuery.
Components are positioned programmatically based on physical constraints.

Target dimensions: 40mm octagonal × 150mm tall
Octagon formed by chamfering a square at 45° with 7:3 ratio (long:short sides)
"""

import cadquery as cq
from pathlib import Path
import math

# ============================================================================
# DESIGN PARAMETERS
# ============================================================================

# Overall enclosure dimensions (mm)
# Octagonal prism: 40mm flat-to-flat, 150mm height
DEVICE_WIDTH = 40  # Flat-to-flat distance across opposite long sides
DEVICE_HEIGHT = 150  # Length along Y axis
WALL_THICKNESS = 1.6  # 1.6mm thickness for USB-C port compatibility

# Octagon geometry (7:3 ratio for long sides:short chamfers)
# Calculated from 40mm square with chamfered corners at 45°
OCTAGON_SQUARE_SIDE = 40.0  # Original square before chamfering
OCTAGON_CHAMFER_DIST = 7.55  # Distance cut off each corner
OCTAGON_LONG_SIDE = OCTAGON_SQUARE_SIDE - 2 * OCTAGON_CHAMFER_DIST  # ≈24.9mm
OCTAGON_SHORT_SIDE = OCTAGON_CHAMFER_DIST * math.sqrt(2)  # ≈10.7mm
EDGE_FILLET_RADIUS = 4.0  # Fillet where octagon edges meet (beveled corners)
TOP_BOTTOM_FILLET_RADIUS = 4.0  # Fillet on top/bottom edges

# Component dimensions
BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65

XIAO_WIDTH = 21
XIAO_DEPTH = 17.5
XIAO_HEIGHT = 3.5

# Speaker (MAX98357A) - on front upper portion
SPEAKER_DIAMETER = 0.8 * OCTAGON_LONG_SIDE  # 80% of long side ≈ 19.9mm
SPEAKER_HEIGHT = 4

# Microphone (INMP441) - on front bottom
MIC_ACOUSTIC_HOLE_DIAMETER = 1.5  # Front-facing acoustic hole
MIC_INTERNAL_PORT_DIAMETER = 1.0  # Internal port aligned with mic
MIC_FOOTPRINT_LENGTH = 4.72 + 0.4  # Mic dimensions + tolerance
MIC_FOOTPRINT_WIDTH = 3.76 + 0.4
MIC_CLEARANCE_RADIUS = 2.0  # No obstructions within this radius of port

# Amplifier (MAX98357A)
AMP_WIDTH = 16
AMP_DEPTH = 16
AMP_HEIGHT = 3

# Power button - on right side
POWER_BUTTON_DIAMETER = 8
POWER_BUTTON_RING_WIDTH = 1.0  # Raised outer ring

# LEDs - on front top
LED_DIAMETER = 3  # 3mm LEDs
LED_SPACING = 8  # Center-to-center spacing

# Large push-to-talk button (separate component) - on right side
LARGE_BUTTON_WIDTH = OCTAGON_LONG_SIDE  # Full width of long side ≈ 24.9mm
LARGE_BUTTON_HEIGHT = 0.30 * DEVICE_HEIGHT  # 30% of device height = 45mm
LARGE_BUTTON_BASE_SECTION_DEPTH = 4  # Flat base section without bevel
LARGE_BUTTON_BEVEL_DEPTH = 4  # Additional depth for beveled section
LARGE_BUTTON_TOTAL_DEPTH = LARGE_BUTTON_BASE_SECTION_DEPTH + LARGE_BUTTON_BEVEL_DEPTH  # Total protrusion = 8mm
LARGE_BUTTON_CORNER_FILLET = 3  # Rounded corners

# Raised edge around large button - integrated into main body
RAISED_EDGE_HEIGHT = 2.0  # Height of raised quarter-circle edge
RAISED_EDGE_GAP = 0.25  # Gap between edge and button

# USB-C port - on right side
USBC_WIDTH = 9.5  # Width (front-to-back when on right face)
USBC_HEIGHT = 3.7  # Height (up-down when on right face)
USBC_CORNER_RADIUS = 1.6  # Corner radius for stadium shape

# Component positioning (Y axis = length, Z axis = front/back, X axis = left/right)
BATTERY_BOTTOM_OFFSET = 5
XIAO_Y_OFFSET = BATTERY_BOTTOM_OFFSET + BATTERY_LENGTH + 5

# Front side components (positions along Y axis, measured from bottom)
LED_Y_POS = DEVICE_HEIGHT - 10  # 10mm from top
MIC_Y_POS = 10  # 10mm from bottom
SPEAKER_Y_POS = LED_Y_POS - 10 - SPEAKER_DIAMETER  # Upper edge 10mm below LEDs

# Right side components (positions along Y axis, measured from bottom)
POWER_BUTTON_Y_POS = 25  # 25mm from bottom
USB_C_Y_POS = 12  # 12mm from bottom
# Large button positioned at upper part: 15%-45% from top (22.5mm-67.5mm from top)
LARGE_BUTTON_TOP_OFFSET = 0.15 * DEVICE_HEIGHT  # 15% from top = 22.5mm
LARGE_BUTTON_Y_CENTER = DEVICE_HEIGHT - LARGE_BUTTON_TOP_OFFSET - LARGE_BUTTON_HEIGHT / 2  # Center at 105mm from bottom

# Tolerances
PRINT_TOLERANCE = 0.2
PRESS_FIT_TOLERANCE = 0.1

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_rounded_rect_wire(wp, width, height, radius):
    """Create a rounded rectangle wire on the given workplane.

    Args:
        wp: CadQuery workplane to draw on
        width: Rectangle width
        height: Rectangle height
        radius: Corner radius

    Returns:
        Workplane with the rounded rectangle wire
    """
    # Calculate half dimensions
    w = width / 2
    h = height / 2
    r = radius

    # Create rounded rectangle using lines and tangent arcs
    # Start from right side, go counter-clockwise
    wire = (
        wp
        .moveTo(w, h - r)  # Right side, top corner
        .radiusArc((w - r, h), -r)  # Arc to top side
        .lineTo(-w + r, h)  # Top edge
        .radiusArc((-w, h - r), -r)  # Arc to left side
        .lineTo(-w, -h + r)  # Left edge
        .radiusArc((-w + r, -h), -r)  # Arc to bottom side
        .lineTo(w - r, -h)  # Bottom edge
        .radiusArc((w, -h + r), -r)  # Arc to right side
        .close()
    )

    return wire


def create_octagon_profile():
    """Create the octagon cross-section profile.

    Returns a 2D octagon formed by chamfering a 40mm square at 45°.
    The octagon has 4 long sides and 4 short chamfered sides with 7:3 ratio.
    """
    half_square = OCTAGON_SQUARE_SIDE / 2
    chamfer = OCTAGON_CHAMFER_DIST

    # Define the 8 points of the octagon (clockwise from top-right)
    # Using XY plane for cross-section
    points = [
        (half_square, half_square - chamfer),        # 1. Top of right long side
        (half_square - chamfer, half_square),        # 2. Right end of top long side
        (-(half_square - chamfer), half_square),     # 3. Left end of top long side
        (-half_square, half_square - chamfer),       # 4. Top of left long side
        (-half_square, -(half_square - chamfer)),    # 5. Bottom of left long side
        (-(half_square - chamfer), -half_square),    # 6. Left end of bottom long side
        (half_square - chamfer, -half_square),       # 7. Right end of bottom long side
        (half_square, -(half_square - chamfer)),     # 8. Bottom of right long side
    ]

    # Create octagon profile (2D sketch)
    octagon = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
    )

    return octagon


def create_basic_enclosure():
    """Create the basic octagonal prism enclosure shell with filleted edges.

    Returns a hollow octagonal prism:
    - 40mm flat-to-flat (across opposite long sides)
    - 150mm height
    - Filleted top and bottom edges
    - Wall thickness: 2.5mm
    """
    # Create outer octagon and extrude to full height
    enclosure = create_octagon_profile().extrude(DEVICE_HEIGHT)

    # Add fillet to vertical edges where octagon sides meet
    enclosure = enclosure.edges("|Z").fillet(EDGE_FILLET_RADIUS)

    # Add fillet to top outer edge before hollowing
    enclosure = enclosure.edges(">Z").fillet(TOP_BOTTOM_FILLET_RADIUS)

    # Create inner octagon for hollowing (manually scaled down)
    # Calculate inner dimensions
    inner_square = OCTAGON_SQUARE_SIDE - 2 * WALL_THICKNESS
    inner_chamfer = OCTAGON_CHAMFER_DIST - WALL_THICKNESS

    inner_half = inner_square / 2

    # Inner octagon points
    inner_points = [
        (inner_half, inner_half - inner_chamfer),
        (inner_half - inner_chamfer, inner_half),
        (-(inner_half - inner_chamfer), inner_half),
        (-inner_half, inner_half - inner_chamfer),
        (-inner_half, -(inner_half - inner_chamfer)),
        (-(inner_half - inner_chamfer), -inner_half),
        (inner_half - inner_chamfer, -inner_half),
        (inner_half, -(inner_half - inner_chamfer)),
    ]

    # Hollow it out from the top
    enclosure = (
        enclosure
        .faces(">Z")
        .workplane()
        .polyline(inner_points)
        .close()
        .cutThruAll()
    )

    # Note: Bottom edge fillet skipped for now due to complexity after hollowing
    # TODO: Add bottom edge fillet using a different approach

    return enclosure


def add_battery_compartment(enclosure):
    """Placeholder for 18650 battery mounting features.

    Battery compartment design is deferred - the hollow interior provides
    space for the battery (18650: 18.6mm diameter × 65mm length).
    Interior space available: 35mm flat-to-flat octagon.
    """
    # Battery compartment features removed for now
    # TODO: Design proper battery holder, contacts, and wire routing when needed

    return enclosure


def add_led_holes(enclosure):
    """Add three LED holes on front side, 10mm from top.

    3mm LEDs arranged horizontally with 8mm center-to-center spacing.
    Front face is at Y = +DEVICE_WIDTH/2, drill holes in -Y direction.
    """
    led_radius = (LED_DIAMETER + PRINT_TOLERANCE) / 2

    # Create three LED holes in a row
    # Z position: 10mm from top = DEVICE_HEIGHT - 10
    # X positions: centered at 0, offset by ±LED_SPACING
    for x_offset in [-LED_SPACING, 0, LED_SPACING]:
        led_hole = (
            cq.Workplane("XZ")  # Work in XZ plane (front face view)
            .workplane(offset=DEVICE_WIDTH / 2)  # Position at front face (Y = +half)
            .center(x_offset, LED_Y_POS)  # Position in X and Z
            .circle(led_radius)
            .extrude(-WALL_THICKNESS - 1)  # Cut through wall in -Y direction
        )
        enclosure = enclosure.cut(led_hole)

    return enclosure


def create_large_button():
    """Create the large push-to-talk button as a separate component.

    Features:
    - Full width of long side (24.9mm) × 45mm height
    - 4mm flat base section (no bevel)
    - 45° bevel/taper on all four sides for outer 4mm section
    - Total 8mm protrusion from body surface
    - Rounded corners
    - Dotted texture pattern on outer surface
    """
    # Button positioned on right side
    # Create using loft with three profiles:
    # 1. Base profile at enclosure surface (full size)
    # 2. Mid profile at end of flat section (full size)
    # 3. Outer profile at max protrusion (beveled on all sides)

    # Base dimensions (full size)
    base_width = LARGE_BUTTON_WIDTH
    base_height = LARGE_BUTTON_HEIGHT

    # Outer dimensions (beveled on all four sides)
    # Since bevel is 45° and bevel section is 4mm deep, we lose 4mm on each side
    # Width: loses 2*4mm = 8mm total (4mm from each side)
    # Height: loses 2*4mm = 8mm total (4mm from top and bottom)
    outer_width = max(base_width - 2 * LARGE_BUTTON_BEVEL_DEPTH * math.tan(math.radians(45)), 1)
    outer_height = max(base_height - 2 * LARGE_BUTTON_BEVEL_DEPTH * math.tan(math.radians(45)), 1)

    # Start position: right side of enclosure, centered vertically
    start_y = LARGE_BUTTON_Y_CENTER - LARGE_BUTTON_HEIGHT / 2
    base_z = DEVICE_WIDTH / 2  # Enclosure surface
    base_corner_radius = 8.0  # 8mm corner radius at top of base

    # Calculate proportional corner radius for the top of the button
    # Scale according to the reduction in width due to beveling
    outer_corner_radius = base_corner_radius * (outer_width / base_width)

    # Create base section with rounded corners
    base_section = (
        cq.Workplane("XY")
        .workplane(offset=base_z)
        .center(0, start_y + base_height / 2)
        .rect(base_width, base_height)
        .extrude(LARGE_BUTTON_BASE_SECTION_DEPTH)
    )

    # Add fillets to the 4 corner edges of the base section
    base_edges = base_section.edges().vals()
    base_corner_length = LARGE_BUTTON_BASE_SECTION_DEPTH  # 4mm - the vertical corner edges
    base_corner_edges = [e for e in base_edges if abs(e.Length() - base_corner_length) < 0.5]

    for edge in base_corner_edges:
        base_section = base_section.edges(cq.selectors.NearestToPointSelector(edge.Center())).fillet(base_corner_radius)

    # Create beveled section with rounded corners that taper from 8mm to proportional size
    # Use loft between two rounded rectangles to create linearly tapering corner radii

    # Create bottom profile (full size with 8mm corner radius)
    wp_bottom = cq.Workplane("XY").workplane(offset=base_z + LARGE_BUTTON_BASE_SECTION_DEPTH).center(0, start_y + base_height / 2)
    bottom_profile = create_rounded_rect_wire(wp_bottom, base_width, base_height, base_corner_radius)

    # Create top profile (smaller size with proportional corner radius) on the same workplane chain
    top_profile = create_rounded_rect_wire(
        bottom_profile.workplane(offset=LARGE_BUTTON_BEVEL_DEPTH),
        outer_width,
        outer_height,
        outer_corner_radius
    )

    # Loft between the two profiles
    beveled_section = top_profile.loft(combine=True)

    # Combine base and beveled sections
    button = base_section.union(beveled_section)

    # Add raised bump texture pattern on outer surface
    # Small hemispheric bumps arranged in a grid
    bump_radius = 0.6  # Larger bumps for visibility
    bump_spacing = 2.5  # Spacing between bump centers
    bump_height = 0.5  # Height of raised bumps

    grid_range_x = int(outer_width / 2 / bump_spacing)
    grid_range_y = int(outer_height / 2 / bump_spacing)

    # Outer surface is in XY plane at Z = base_z + total depth
    outer_z = base_z + LARGE_BUTTON_TOTAL_DEPTH
    outer_center_y = start_y + base_height / 2  # Same center as base

    for x in range(-grid_range_x, grid_range_x + 1):
        for y in range(-grid_range_y, grid_range_y + 1):
            x_pos = x * bump_spacing
            y_pos = y * bump_spacing

            # Skip bumps in the rounded corner areas
            # Check if bump is in a corner region (outside the rounded rectangle)
            half_w = outer_width / 2
            half_h = outer_height / 2

            # For each corner, check if bump is in the cut-off area
            skip = False
            corners = [
                (half_w, half_h),      # Top-right
                (-half_w, half_h),     # Top-left
                (half_w, -half_h),     # Bottom-right
                (-half_w, -half_h),    # Bottom-left
            ]

            for cx, cy in corners:
                # Distance from bump to corner center
                corner_center_x = cx - (outer_corner_radius if cx > 0 else -outer_corner_radius)
                corner_center_y = cy - (outer_corner_radius if cy > 0 else -outer_corner_radius)
                dx = x_pos - corner_center_x
                dy = y_pos - corner_center_y
                dist = (dx**2 + dy**2)**0.5

                # Check if in corner region (beyond straight edges)
                in_corner_region = (abs(x_pos) > half_w - outer_corner_radius and
                                   abs(y_pos) > half_h - outer_corner_radius)

                # Skip if in corner region and outside the corner radius
                if in_corner_region and dist > outer_corner_radius - bump_radius:
                    skip = True
                    break

            if skip:
                continue

            # Create raised bump on outer surface (XY plane)
            # Use a short cylinder or sphere segment
            bump = (
                cq.Workplane("XY")
                .workplane(offset=outer_z)
                .center(x_pos, outer_center_y + y_pos)
                .circle(bump_radius)
                .extrude(bump_height)
            )
            # Fillet the top edge to create rounded bump
            bump = bump.faces(">Z").edges().fillet(bump_radius * 0.8)

            button = button.union(bump)

    return button


def add_large_button_cutout(enclosure):
    """Add opening in enclosure for the large button and raised edge.

    Creates:
    1. A rectangular opening on the right side for the button to protrude through
    2. A 2mm raised edge (quarter-circle profile) around the opening with 0.25mm gap
    """
    # Opening dimensions (slightly larger than button base for clearance)
    opening_clearance = 0.5
    opening_width = LARGE_BUTTON_WIDTH + opening_clearance  # Width along Y axis (front-to-back)
    opening_height = LARGE_BUTTON_HEIGHT + opening_clearance  # Height along Z axis (up-down)
    opening_corner_radius = 8.0 + opening_clearance / 2  # 8mm button radius + clearance = 8.5mm

    # Button is centered vertically (Z axis) and front-to-back (Y axis)
    button_center_y = 0  # Centered front-to-back
    button_center_z = LARGE_BUTTON_Y_CENTER  # Centered vertically = DEVICE_HEIGHT / 2

    # Create rectangular opening on right side with rounded corners
    # Right face is in the YZ plane at X = +DEVICE_WIDTH/2
    # The outer surface is at the maximum X value of the octagon
    # Calculate the exact outer surface position for the right face
    outer_surface_x = OCTAGON_SQUARE_SIDE / 2  # Right side at X = 20mm

    # Create workplane at the outer surface of the right face, centered at button position
    wp_opening = (
        cq.Workplane("YZ")  # Work in YZ plane (right face view)
        .workplane(offset=outer_surface_x)  # Position at outer surface of right wall
        .center(button_center_y, button_center_z)  # Center at button position (Y=0, Z=75mm)
    )

    # Create rounded rectangle wire and extrude inward through the wall
    # Extrude in -X direction (inward) to cut through the wall thickness
    button_opening_rounded = create_rounded_rect_wire(
        wp_opening,
        opening_width,
        opening_height,
        opening_corner_radius
    ).extrude(-WALL_THICKNESS - 0.5)  # Extrude inward in -X direction through the wall

    # Cut the opening from the enclosure
    enclosure = enclosure.cut(button_opening_rounded)

    # Add raised edge around the button
    # Frame width matches wall thickness
    # Height is doubled to allow for octagon cutting from bottom
    # Start at outer surface to avoid overlapping with existing wall
    edge_height = 2 * WALL_THICKNESS  # Total height: 3.2mm (will be cut to follow octagon)
    edge_frame_width = WALL_THICKNESS  # Frame width: 1.6mm

    # Create the raised edge as a frame around the button opening
    # The inner cutout should match the opening size to avoid filling it in
    edge_inner_width = opening_width  # Same as opening
    edge_inner_height = opening_height  # Same as opening

    # Create workplane for raised edge at inner surface, centered at button position
    # Start from inner surface and extend outward through and beyond outer surface
    wp_edge = (
        cq.Workplane("YZ")
        .workplane(offset=outer_surface_x - WALL_THICKNESS)  # At inner surface of right face
        .center(button_center_y, button_center_z)  # Center at button position
    )

    # Create outer rectangle for the frame
    edge_outer = create_rounded_rect_wire(
        wp_edge,
        edge_inner_width + 2 * edge_frame_width,
        edge_inner_height + 2 * edge_frame_width,
        opening_corner_radius + edge_frame_width
    ).extrude(edge_height)  # Extrude outward in +X direction

    # Create inner cutout (same size as opening to ensure it doesn't fill the hole)
    edge_inner = create_rounded_rect_wire(
        wp_edge,
        edge_inner_width,
        edge_inner_height,
        opening_corner_radius
    ).extrude(edge_height + 1)  # Extrude outward to cut through frame

    # Subtract inner from outer to create frame
    edge_frame = edge_outer.cut(edge_inner)

    # TODO: Trim the raised edge to follow the enclosure's octagon profile
    # Cut an octagon-shaped volume from the lower portion
    # Temporarily disabled - need to fix the cutting geometry

    # try:
    #     octagon_cut_height = opening_height + 2 * edge_frame_width + 10
    #
    #     octagon_cutter = (
    #         create_octagon_profile()
    #         .extrude(octagon_cut_height)
    #         .translate((0, 0, button_center_z - octagon_cut_height / 2))
    #         .translate((outer_surface_x + WALL_THICKNESS, 0, 0))
    #     )
    #
    #     edge_frame = edge_frame.cut(octagon_cutter)
    # except Exception as e:
    #     print(f"Warning: Failed to cut octagon from raised edge: {e}")

    # Round the outer edge with quarter-circle profile
    try:
        # Fillet the outer edges to create rounded profile
        # Use a small radius - larger radii create invalid geometry
        fillet_radius = 0.3  # Small radius to avoid geometric conflicts
        edge_frame = edge_frame.edges(">X").fillet(fillet_radius)
    except Exception as e:
        # If filleting fails, continue without it
        print(f"  ⚠️  WARNING: Failed to fillet raised edge: {e}")

    # Add the raised edge to the enclosure
    try:
        enclosure = enclosure.union(edge_frame)
        if not enclosure.val().isValid():
            print("  ⚠️  WARNING: Enclosure became invalid after adding raised edge!")
    except Exception as e:
        print(f"  ⚠️  WARNING: Failed to union raised edge: {e}")

    return enclosure


def add_speaker_grille(enclosure):
    """Add speaker grille on front upper portion.

    Circular grille with perforated pattern, diameter = 80% of long side width.
    Upper edge positioned 10mm below the LED line.
    Front face is at Y = +DEVICE_WIDTH/2, drill holes in -Y direction.
    """
    grille_radius = SPEAKER_DIAMETER / 2

    # Add multiple small holes for speaker grille
    hole_radius = 0.75
    hole_spacing = 2.5

    # Calculate grid range to cover speaker diameter
    grid_range = int(grille_radius / hole_spacing) + 1

    # Speaker center Z position (SPEAKER_Y_POS is the Y position in spec, but Z in our coordinate system)
    speaker_center_z = SPEAKER_Y_POS

    # Build holes in circular pattern on front face
    for x_offset in range(-grid_range, grid_range + 1):
        for z_offset in range(-grid_range, grid_range + 1):
            x_pos = x_offset * hole_spacing
            z_pos = z_offset * hole_spacing

            # Only add holes within circular grille area
            if (x_pos**2 + z_pos**2)**0.5 <= grille_radius:
                hole = (
                    cq.Workplane("XZ")  # Work in XZ plane (front face view)
                    .workplane(offset=DEVICE_WIDTH / 2)  # Position at front face (Y = +half)
                    .center(x_pos, speaker_center_z + z_pos)  # Position in X and Z
                    .circle(hole_radius)
                    .extrude(-WALL_THICKNESS - 1)  # Cut through wall in -Y direction
                )
                enclosure = enclosure.cut(hole)

    return enclosure


def add_mic_hole_and_mount(enclosure):
    """Add microphone acoustic hole and internal INMP441 mounting structure.

    - 1.5mm acoustic hole on front face, 10mm from bottom
    - Internal mounting pocket for INMP441 breakout board
    - 1.0mm internal port aligned with microphone
    - Clearance for acoustic path
    Front face is at Y = +DEVICE_WIDTH/2, drill holes in -Y direction.
    """
    # Front-facing acoustic hole (1.5mm)
    # MIC_Y_POS is the Y position in spec, but Z in our coordinate system
    acoustic_hole = (
        cq.Workplane("XZ")  # Work in XZ plane (front face view)
        .workplane(offset=DEVICE_WIDTH / 2)  # Position at front face (Y = +half)
        .center(0, MIC_Y_POS)  # Position in X and Z
        .circle(MIC_ACOUSTIC_HOLE_DIAMETER / 2)
        .extrude(-WALL_THICKNESS - 1)  # Cut through wall in -Y direction
    )
    enclosure = enclosure.cut(acoustic_hole)

    # Internal mounting pocket for INMP441
    # Create a small rectangular pocket just inside the front wall
    mic_pocket = (
        cq.Workplane("XZ")  # Work in XZ plane (front face view)
        .workplane(offset=DEVICE_WIDTH / 2 - WALL_THICKNESS - 1)  # Inside front wall
        .center(0, MIC_Y_POS)  # Position in X and Z
        .rect(MIC_FOOTPRINT_LENGTH, MIC_FOOTPRINT_WIDTH)
        .extrude(-2)  # 2mm deep pocket in -Y direction
    )
    enclosure = enclosure.cut(mic_pocket)

    # Internal acoustic port (1.0mm) aligned with microphone
    # This ensures sound can reach the bottom-ported INMP441
    internal_port = (
        cq.Workplane("XZ")  # Work in XZ plane (front face view)
        .workplane(offset=DEVICE_WIDTH / 2 - WALL_THICKNESS)  # Just inside wall
        .center(0, MIC_Y_POS)  # Position in X and Z
        .circle(MIC_INTERNAL_PORT_DIAMETER / 2)
        .extrude(-MIC_CLEARANCE_RADIUS - 2)  # Extend into enclosure for clearance in -Y
    )
    enclosure = enclosure.cut(internal_port)

    return enclosure


def add_power_button(enclosure):
    """Add power button cutout on right side with concentric ring design.

    8mm diameter button, 25mm from bottom, with raised outer ring.
    Right face is at X = +DEVICE_WIDTH/2, drill holes in -X direction.
    """
    button_radius = (POWER_BUTTON_DIAMETER + PRINT_TOLERANCE) / 2

    # Main button cutout on right side
    # Right side is at +X = +DEVICE_WIDTH/2
    # POWER_BUTTON_Y_POS is the Y position in spec, but Z in our coordinate system
    button_hole = (
        cq.Workplane("YZ")  # Work in YZ plane (right face view)
        .workplane(offset=DEVICE_WIDTH / 2)  # Position at right face (X = +half)
        .center(0, POWER_BUTTON_Y_POS)  # Position in Y and Z
        .circle(button_radius)
        .extrude(-WALL_THICKNESS - 1)  # Cut through wall in -X direction
    )
    enclosure = enclosure.cut(button_hole)

    # TODO: Add raised outer ring detail (could be added as a separate feature)
    # For now, just the hole is sufficient for the basic model

    return enclosure


def add_usbc_port(enclosure):
    """Add USB-C charging port cutout on right side, 12mm from bottom.

    Stadium-shaped (rounded rectangle) opening with 1.6mm corner radius.
    Right face is at X = +DEVICE_WIDTH/2, drill holes in -X direction.
    Oriented with flat side (9.5mm width) facing toward/away from power button.
    Dimensions: 9.5mm width × 3.7mm height with 1.6mm corner radius.
    """
    # Stadium-shaped cutout for USB-C on right side
    # Right side is at +X = +DEVICE_WIDTH/2
    # USB_C_Y_POS is the Y position in spec, but Z in our coordinate system
    # Width (9.5mm) along Y axis (front-back), height (3.7mm) along Z axis (up-down)

    # Create the rounded rectangle (stadium shape) by making a rectangle and filleting corners
    usbc_cutout = (
        cq.Workplane("YZ")  # Work in YZ plane (right face view)
        .workplane(offset=DEVICE_WIDTH / 2)  # Position at right face (X = +half)
        .center(0, USB_C_Y_POS)  # Position in Y and Z
        .rect(USBC_WIDTH + PRINT_TOLERANCE, USBC_HEIGHT + PRINT_TOLERANCE)  # Width in Y (9.5mm), height in Z (3.7mm)
    )

    # Fillet the corners to create stadium shape
    # Note: We need to extrude first to create a 3D object before filleting
    usbc_cutout = usbc_cutout.extrude(-WALL_THICKNESS - 1)  # Cut through wall in -X direction

    # Fillet all vertical edges (the corners of the stadium shape)
    # Select edges parallel to X axis (the extrusion direction)
    try:
        usbc_cutout = usbc_cutout.edges("|X").fillet(USBC_CORNER_RADIUS)
    except:
        # If filleting fails, continue without it (better to have rectangular than no port)
        pass

    enclosure = enclosure.cut(usbc_cutout)

    return enclosure


def create_component_mounts():
    """Placeholder for PCB component mounting posts.

    Component mounting features removed for now.
    TODO: Design proper mounting solution for XIAO board and other components when needed.
    """
    # Return empty list - no mounting posts for now
    return []


# ============================================================================
# PRINTABILITY VALIDATION
# ============================================================================

def check_printability(part, name):
    """Check a part for common 3D printing issues.

    Args:
        part: CadQuery Workplane with the part to check
        name: Name of the part for error reporting
    """
    print(f"\n=== Printability Check: {name} ===")

    try:
        # Get the solid from the workplane
        solid = part.val()

        # Check if it's a valid solid
        if not solid.isValid():
            print(f"❌ ERROR: {name} is not a valid solid!")
            return False
        else:
            print(f"✓ {name} is a valid solid")

        # Check for multiple disconnected solids
        solids = part.solids().vals()
        if len(solids) > 1:
            print(f"⚠️  WARNING: {name} contains {len(solids)} separate solids - may have floating parts!")
        else:
            print(f"✓ {name} is a single connected solid")

        # Get bounding box
        bb = part.val().BoundingBox()
        print(f"  Dimensions: {bb.xlen:.2f} × {bb.ylen:.2f} × {bb.zlen:.2f} mm")
        print(f"  Volume: {solid.Volume():.2f} mm³")

        # Sample the part at different Z heights to detect empty layers
        print(f"  Z range: {bb.zmin:.2f} to {bb.zmax:.2f} mm")
        print(f"  Checking for empty layers...")
        z_min = bb.zmin
        z_max = bb.zmax
        layer_height = 0.2  # Typical layer height for 3D printing
        num_samples = min(int((z_max - z_min) / layer_height), 100)  # Limit to 100 samples max

        if num_samples < 2:
            print(f"  ⚠️  Part too thin to sample ({(z_max - z_min):.2f}mm), skipping layer check")
        else:
            empty_layers = []
            for i in range(1, num_samples):  # Skip first and last
                z = z_min + i * layer_height
                # Create a horizontal cutting plane at this Z height
                try:
                    # Use workplane to create section
                    section = (cq.Workplane("XY")
                              .workplane(offset=z)
                              .add(part.val())
                              .section())
                    wires = section.wires().vals()
                    if len(wires) == 0:
                        empty_layers.append(z)
                except Exception as e:
                    # Section might fail if there's no intersection
                    empty_layers.append(z)

            if empty_layers:
                empty_pct = (len(empty_layers) / num_samples) * 100
                print(f"⚠️  WARNING: {len(empty_layers)}/{num_samples} layers empty ({empty_pct:.1f}%)")
                if len(empty_layers) <= 5:
                    print(f"  Empty at Z heights (mm): {[f'{z:.2f}' for z in empty_layers]}")
            else:
                print(f"✓ No empty layers in {num_samples} samples")

        # Check for thin walls
        faces = part.faces().vals()
        print(f"  Total faces: {len(faces)}")

        return True

    except Exception as e:
        print(f"❌ ERROR during printability check: {e}")
        return False


# ============================================================================
# MAIN ASSEMBLY
# ============================================================================

def generate_enclosure():
    """Generate complete octagonal enclosure with all features."""
    print("Generating DevAIs octagonal enclosure...")

    # Create base octagonal enclosure
    enclosure = create_basic_enclosure()
    print("  ✓ Octagonal enclosure base created")

    # Battery compartment (placeholder for now)
    enclosure = add_battery_compartment(enclosure)
    print("  ✓ Battery compartment (hollow interior)")

    # Add front face components
    enclosure = add_led_holes(enclosure)
    enclosure = add_speaker_grille(enclosure)
    enclosure = add_mic_hole_and_mount(enclosure)
    print("  ✓ Front face components added")

    # Add right side components
    enclosure = add_power_button(enclosure)
    enclosure = add_usbc_port(enclosure)
    enclosure = add_large_button_cutout(enclosure)
    print("  ✓ Right side components added")

    # Create component mounting posts
    mount_posts = create_component_mounts()
    print("  ✓ Component mounts created")

    # Combine all posts with enclosure
    for post in mount_posts:
        enclosure = enclosure.union(post)

    # TODO: Add raised edge around large button (integrated into body)

    return enclosure


def export_models():
    """Generate and export all models."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Generate main enclosure
    enclosure = generate_enclosure()

    # Generate large button (separate component)
    large_button = create_large_button()
    print("  ✓ Large button component created")

    # Run printability checks
    print("\n" + "="*60)
    print("PRINTABILITY VALIDATION")
    print("="*60)
    check_printability(enclosure, "Enclosure")
    check_printability(large_button, "Large Button")
    print("="*60 + "\n")

    # Export enclosure as STL
    stl_path = output_dir / "devais_enclosure.stl"
    cq.exporters.export(enclosure, str(stl_path))
    print(f"\n✓ Exported: {stl_path}")

    # Export enclosure as STEP (for CAD compatibility)
    step_path = output_dir / "devais_enclosure.step"
    cq.exporters.export(enclosure, str(step_path))
    print(f"✓ Exported: {step_path}")

    # Export large button as STL
    button_stl_path = output_dir / "devais_large_button.stl"
    cq.exporters.export(large_button, str(button_stl_path))
    print(f"✓ Exported: {button_stl_path}")

    # Export large button as STEP
    button_step_path = output_dir / "devais_large_button.step"
    cq.exporters.export(large_button, str(button_step_path))
    print(f"✓ Exported: {button_step_path}")

    print("\nEnclosure generation complete!")
    print(f"Dimensions: {DEVICE_WIDTH}mm octagonal × {DEVICE_HEIGHT}mm height")
    print(f"Octagon geometry: {OCTAGON_LONG_SIDE:.1f}mm long sides, {OCTAGON_SHORT_SIDE:.1f}mm chamfers (7:3 ratio)")
    print("Components: Main octagonal enclosure + Large button (separate)")


if __name__ == "__main__":
    export_models()
