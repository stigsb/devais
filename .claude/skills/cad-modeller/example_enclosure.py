"""
Example: Simple Component Enclosure
====================================

This example demonstrates key patterns from the CAD Modeller skill:
- Parameter-driven design
- Helper functions
- Component mounting
- Manufacturing tolerances
- Export workflow

Design: A simple box enclosure for a small PCB with mounting posts.
"""

import cadquery as cq
from pathlib import Path

# ============================================================================
# DESIGN PARAMETERS
# ============================================================================

# Enclosure dimensions
BOX_WIDTH = 50
BOX_DEPTH = 35
BOX_HEIGHT = 20
WALL_THICKNESS = 2.5

# PCB dimensions
PCB_WIDTH = 40
PCB_DEPTH = 25
PCB_THICKNESS = 1.6
PCB_STANDOFF_HEIGHT = 3

# Mounting
MOUNTING_HOLE_DIAMETER = 3
SCREW_HOLE_DIAMETER = 1.5

# Tolerances
CLEARANCE = 0.3  # Extra space around PCB
PRINT_TOLERANCE = 0.2  # For 3D printing

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_box_shell():
    """Create the basic box enclosure with hollow interior."""
    # Outer box
    outer = (
        cq.Workplane("XY")
        .box(BOX_WIDTH, BOX_DEPTH, BOX_HEIGHT)
    )
    
    # Calculate inner dimensions
    inner_width = BOX_WIDTH - (2 * WALL_THICKNESS)
    inner_depth = BOX_DEPTH - (2 * WALL_THICKNESS)
    inner_height = BOX_HEIGHT - WALL_THICKNESS  # Bottom remains solid
    
    # Create hollow space
    inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)  # Start above bottom
        .box(inner_width, inner_depth, inner_height)
    )
    
    # Subtract inner from outer
    shell = outer.cut(inner)
    
    return shell


def create_mounting_post(x, y):
    """Create a PCB mounting post at given X,Y coordinates."""
    post = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)
        .center(x, y)
        .circle(MOUNTING_HOLE_DIAMETER / 2)
        .extrude(PCB_STANDOFF_HEIGHT)
        .faces(">Z")
        .workplane()
        .circle(SCREW_HOLE_DIAMETER / 2)
        .cutBlind(-PCB_STANDOFF_HEIGHT)
    )
    return post


def add_ventilation_holes(shell):
    """Add a grid of small ventilation holes to the top."""
    hole_diameter = 2
    hole_spacing = 5
    
    # Calculate grid positions
    for x in range(-2, 3):
        for y in range(-2, 3):
            hole = (
                cq.Workplane("XY")
                .workplane(offset=BOX_HEIGHT)
                .center(x * hole_spacing, y * hole_spacing)
                .circle(hole_diameter / 2)
                .extrude(-WALL_THICKNESS - 1)
            )
            shell = shell.cut(hole)
    
    return shell


# ============================================================================
# MAIN ASSEMBLY
# ============================================================================

def generate_enclosure():
    """Generate complete enclosure with all features."""
    print("Generating component enclosure...")
    
    # Create base shell
    shell = create_box_shell()
    print("  ✓ Box shell created")
    
    # Calculate mounting post positions (PCB corners)
    post_spacing_x = PCB_WIDTH - 6  # Inset from PCB edges
    post_spacing_y = PCB_DEPTH - 6
    
    # Add mounting posts at four corners
    for x in [-1, 1]:
        for y in [-1, 1]:
            post_x = x * post_spacing_x / 2
            post_y = y * post_spacing_y / 2
            post = create_mounting_post(post_x, post_y)
            shell = shell.union(post)
    
    print("  ✓ Mounting posts added")
    
    # Add ventilation
    shell = add_ventilation_holes(shell)
    print("  ✓ Ventilation holes added")
    
    return shell


def export_model():
    """Generate and export the model."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate model
    enclosure = generate_enclosure()
    
    # Export as STL (for 3D printing)
    stl_path = output_dir / "example_enclosure.stl"
    cq.exporters.export(enclosure, str(stl_path))
    print(f"\n✓ Exported STL: {stl_path}")
    
    # Export as STEP (for CAD)
    step_path = output_dir / "example_enclosure.step"
    cq.exporters.export(enclosure, str(step_path))
    print(f"✓ Exported STEP: {step_path}")
    
    print(f"\n✓ Enclosure complete!")
    print(f"Dimensions: {BOX_WIDTH}×{BOX_DEPTH}×{BOX_HEIGHT}mm")
    print(f"PCB clearance: {PCB_WIDTH + CLEARANCE}×{PCB_DEPTH + CLEARANCE}mm")


if __name__ == "__main__":
    export_model()
