# CAD Modeller Skill

## Overview

This skill enables Claude to create 3D CAD models programmatically using Python-based CAD tools, primarily CadQuery. Use this skill when users need to design physical objects, enclosures, mechanical parts, or any 3D-printable components through code rather than traditional CAD software.

## When to Use This Skill

**Always use this skill when:**
- User asks to create or design a 3D model, enclosure, or mechanical part
- User mentions CAD, 3D printing, STL files, or physical product design
- User wants to iterate on dimensions or design parameters
- User needs component mounting features, wire routing channels, or assembly features
- User wants to export models for manufacturing (3D printing, CNC, injection molding)

**Key trigger phrases:**
- "Design a 3D model/enclosure/case/bracket"
- "Create an STL file for..."
- "I need a mount/holder/bracket for..."
- "Design a box/enclosure that fits..."
- "3D print" or "manufacturing design"

## Tool Selection: CadQuery vs Build123d vs OpenSCAD

### CadQuery (Recommended Default)
- **Best for:** Most projects, production-ready designs, complex assemblies
- **Pros:** Mature, excellent docs, powerful OCCT kernel, large community
- **Cons:** Slightly verbose API
- **Install:** `uv add cadquery` or `pip install cadquery`

### Build123d
- **Best for:** Newer projects wanting modern Python syntax
- **Pros:** More Pythonic API, cleaner code, modern features
- **Cons:** Newer (less mature), smaller ecosystem
- **Install:** `uv add build123d` or `pip install build123d`

### OpenSCAD (via SolidPython)
- **Best for:** Simple geometric shapes, educational projects
- **Pros:** Simple syntax, fast preview
- **Cons:** Less powerful for complex models
- **Install:** Requires OpenSCAD binary + `pip install solidpython`

**Default choice:** Use CadQuery unless user specifically requests otherwise.

## Core CadQuery Concepts

### 1. Workplane-Based Design
Everything starts with a workplane - think of it as placing a drawing surface in 3D space:

```python
import cadquery as cq

# Start on XY plane (looking down from above)
result = cq.Workplane("XY")

# Start on YZ plane (side view)
result = cq.Workplane("YZ")

# Start on XZ plane (front view)
result = cq.Workplane("XZ")
```

### 2. Building 2D Sketches, Then Extruding
The fundamental workflow:
1. Draw a 2D shape on a workplane
2. Extrude it into 3D

```python
# Create a cylinder: circle → extrude
cylinder = (
    cq.Workplane("XY")
    .circle(10)           # 2D circle with radius 10mm
    .extrude(50)          # Extend 50mm upward
)

# Create a box: rectangle → extrude
box = (
    cq.Workplane("XY")
    .rect(30, 20)         # 30mm × 20mm rectangle
    .extrude(15)          # Extend 15mm upward
)
```

### 3. Combining Operations
Use boolean operations to build complex shapes:

```python
# Union (combine shapes)
combined = shape1.union(shape2)

# Cut (subtract shapes)
hollowed = outer_shell.cut(inner_cavity)

# Intersect (keep only overlapping volume)
intersection = shape1.intersect(shape2)
```

## Design Workflow Best Practices

### 1. Parameter-Driven Design
**Always start by defining all dimensions as variables:**

```python
# ============================================================================
# DESIGN PARAMETERS
# ============================================================================

# Overall dimensions
ENCLOSURE_WIDTH = 30
ENCLOSURE_DEPTH = 30
ENCLOSURE_HEIGHT = 150
WALL_THICKNESS = 2.5

# Component dimensions
BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65
PCB_WIDTH = 21
PCB_DEPTH = 17.5

# Component positions (from reference point)
BATTERY_BOTTOM_OFFSET = 5
PCB_Z_OFFSET = 75
BUTTON_Z_OFFSET = 100

# Manufacturing tolerances
PRINT_TOLERANCE = 0.2        # For 3D printing
PRESS_FIT_TOLERANCE = 0.1    # For tight fits
CLEARANCE_TOLERANCE = 0.5    # For loose fits
```

**Why this matters:**
- Easy to iterate: change one number, regenerate entire model
- Self-documenting: dimensions are clear and named
- Consistent: derived dimensions update automatically
- Manufacturing-ready: tolerances defined once, applied everywhere

### 2. Organize with Helper Functions

Break complex models into logical functions:

```python
def create_basic_shell():
    """Create the outer shell."""
    # ... implementation
    return shell

def add_mounting_features(shell):
    """Add screw posts, clips, etc."""
    # ... implementation
    return shell

def add_component_cutouts(shell):
    """Add holes for buttons, LEDs, ports."""
    # ... implementation
    return shell

def generate_complete_model():
    """Assemble everything."""
    shell = create_basic_shell()
    shell = add_mounting_features(shell)
    shell = add_component_cutouts(shell)
    return shell
```

### 3. Positioning Strategy

**Absolute vs Relative Positioning:**

```python
# BAD: Hard to modify, unclear relationships
button_z = 100
led_z = 142

# GOOD: Clear relationships, easy to adjust
DEVICE_HEIGHT = 150
BUTTON_Z = DEVICE_HEIGHT * 0.65      # 65% up the device
LED_Z = DEVICE_HEIGHT * 0.95         # Near the top
SPACING = DEVICE_HEIGHT * 0.05       # 5% spacing
```

**Using workplane offsets for component positioning:**

```python
# Position at specific Z height
component = (
    cq.Workplane("XY")
    .workplane(offset=component_z_position)  # Move to Z position
    .rect(width, depth)
    .extrude(height)
)
```

### 4. Creating Hollowed Enclosures

Common pattern for cases and enclosures:

```python
def create_hollow_cylinder(outer_radius, inner_radius, height):
    """Create a hollow cylindrical shell."""
    # Create outer cylinder
    shell = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .extrude(height)
    )
    
    # Hollow it out from the top
    shell = (
        shell
        .faces(">Z")           # Select top face
        .workplane()           # Create workplane on that face
        .circle(inner_radius)  # Draw inner circle
        .cutThruAll()          # Cut all the way through
    )
    
    return shell
```

### 5. Component Mounting Strategies

**Screw Posts:**
```python
def create_screw_post(position_x, position_y, base_z, height, 
                     post_diameter=3, screw_diameter=1.5):
    """Create a mounting post with screw hole."""
    post = (
        cq.Workplane("XY")
        .workplane(offset=base_z)
        .center(position_x, position_y)
        .circle(post_diameter / 2)
        .extrude(height)
        .faces(">Z")                      # Top of post
        .circle(screw_diameter / 2)       # Screw hole
        .cutBlind(-height)                # Cut into post
    )
    return post
```

**Press-Fit Slots:**
```python
def create_press_fit_slot(pcb_width, pcb_thickness, tolerance=0.1):
    """Create a slot for PCB press-fit mounting."""
    slot_width = pcb_thickness + tolerance
    
    slot = (
        cq.Workplane("XY")
        .rect(pcb_width, slot_width)
        .extrude(5)  # Depth of slot
    )
    return slot
```

**Snap-Fit Clips:**
```python
def create_snap_clip(width, height, depth, flex_gap=0.5):
    """Create a flexible snap-fit clip."""
    # Main clip body
    clip = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )
    
    # Add flex gap
    gap = (
        cq.Workplane("XY")
        .rect(flex_gap, depth)
        .extrude(height * 0.7)
    )
    
    return clip.cut(gap)
```

## Common Patterns and Operations

### Creating Holes and Cutouts

**Circular holes (buttons, LEDs, fasteners):**
```python
def add_circular_cutout(enclosure, diameter, center_x, center_y, z_position):
    """Add a circular hole through the side wall."""
    hole = (
        cq.Workplane("YZ")              # Side view
        .workplane(offset=0)            # At center
        .center(center_y, z_position)   # Position the hole
        .circle(diameter / 2)
        .extrude(100)                   # Extrude through wall
    )
    return enclosure.cut(hole)
```

**Rectangular cutouts (USB ports, displays):**
```python
def add_rectangular_cutout(enclosure, width, height, center_x, center_y):
    """Add a rectangular cutout."""
    cutout = (
        cq.Workplane("XY")
        .center(center_x, center_y)
        .rect(width, height)
        .extrude(10)  # Depth into wall
    )
    return enclosure.cut(cutout)
```

**Speaker grilles (multiple holes in pattern):**
```python
def create_speaker_grille(grille_diameter, hole_diameter=1.5, spacing=2.5):
    """Create a speaker grille with multiple holes."""
    holes = []
    grille_radius = grille_diameter / 2
    
    # Calculate grid of holes
    grid_range = int(grille_radius / spacing) + 1
    
    for x in range(-grid_range, grid_range + 1):
        for y in range(-grid_range, grid_range + 1):
            x_pos = x * spacing
            y_pos = y * spacing
            
            # Only include holes within circular grille area
            if (x_pos**2 + y_pos**2)**0.5 <= grille_radius:
                hole = (
                    cq.Workplane("XY")
                    .center(x_pos, y_pos)
                    .circle(hole_diameter / 2)
                    .extrude(10)
                )
                holes.append(hole)
    
    return holes
```

### Wire Routing Channels

```python
def create_wire_channel(start_pos, end_pos, channel_width=3, channel_depth=2):
    """Create a channel for wire routing between components."""
    # Calculate direction and length
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    dz = end_pos[2] - start_pos[2]
    
    # Create rectangular channel
    channel = (
        cq.Workplane("XY")
        .workplane(offset=start_pos[2])
        .center(start_pos[0], start_pos[1])
        .rect(channel_width, channel_depth)
        .extrude(dz)  # Vertical segment
    )
    
    return channel
```

### Creating Arrays of Features

```python
def create_led_array(count, spacing, led_diameter):
    """Create an array of LED holes."""
    leds = []
    start_offset = -(count - 1) * spacing / 2  # Center the array
    
    for i in range(count):
        x_pos = start_offset + (i * spacing)
        led = (
            cq.Workplane("XY")
            .center(x_pos, 0)
            .circle(led_diameter / 2)
            .extrude(5)
        )
        leds.append(led)
    
    return leds
```

## Manufacturing Considerations

### 3D Printing Tolerances

```python
# Typical tolerances for FDM printing
CLEARANCE_FIT = 0.3      # Parts that slide past each other
LOOSE_FIT = 0.2          # Parts that fit together loosely
STANDARD_FIT = 0.1       # Normal fit
PRESS_FIT = 0.0          # Tight fit (nominal)
INTERFERENCE_FIT = -0.1  # Very tight (requires force)
```

**Apply tolerances when creating mating features:**

```python
# Hole for a 5mm shaft with clearance fit
hole_diameter = 5 + (2 * CLEARANCE_FIT)  # 5.6mm

# Boss that presses into a 10mm hole
boss_diameter = 10 - (2 * PRESS_FIT)  # 10.0mm (nominal)
```

### Wall Thickness Guidelines

```python
# Minimum wall thickness by manufacturing method
MIN_WALL_FDM = 1.5        # FDM 3D printing
MIN_WALL_SLA = 1.0        # SLA/resin printing
MIN_WALL_SLS = 0.8        # SLS printing
MIN_WALL_INJECTION = 1.0  # Injection molding

# Recommended thicknesses
THIN_WALL = 1.5
STANDARD_WALL = 2.5
THICK_WALL = 3.5
```

### Overhangs and Supports

```python
def create_printable_overhang(angle_degrees=45):
    """Create geometry that doesn't require supports.
    
    FDM printers can handle overhangs up to ~45° without supports.
    Design chamfers and angles accordingly.
    """
    MAX_OVERHANG_ANGLE = 45
    
    # Instead of vertical wall, use angled wall
    # ... implementation
```

### Fillet and Chamfer Best Practices

```python
def add_structural_fillets(part, radius=1.0):
    """Add fillets to internal corners for strength."""
    part = part.edges("|Z").fillet(radius)  # Fillet vertical edges
    return part

def add_chamfers_for_assembly(part, distance=0.5):
    """Add chamfers to help parts align during assembly."""
    part = part.edges(">Z").chamfer(distance)  # Top edges
    return part
```

## Export and File Management

### Standard Export Function

```python
from pathlib import Path

def export_models(model, base_name="part", output_dir="output"):
    """Export model in multiple formats."""
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    # STL for 3D printing
    stl_file = output_path / f"{base_name}.stl"
    cq.exporters.export(model, str(stl_file))
    print(f"✓ Exported STL: {stl_file}")
    
    # STEP for CAD compatibility (preserves exact geometry)
    step_file = output_path / f"{base_name}.step"
    cq.exporters.export(model, str(step_file))
    print(f"✓ Exported STEP: {step_file}")
    
    # Optional: DXF for 2D profiles
    # dxf_file = output_path / f"{base_name}.dxf"
    # cq.exporters.export(model, str(dxf_file))
    
    return stl_file, step_file
```

### Multi-Part Assemblies

```python
def export_assembly(parts_dict, output_dir="output"):
    """Export multiple parts with descriptive names.
    
    Args:
        parts_dict: Dictionary like {"top_shell": model1, "bottom_shell": model2}
    """
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    for name, model in parts_dict.items():
        stl_file = output_path / f"{name}.stl"
        step_file = output_path / f"{name}.step"
        
        cq.exporters.export(model, str(stl_file))
        cq.exporters.export(model, str(step_file))
        
        print(f"✓ Exported: {name}")
    
    print(f"\n✓ All parts exported to: {output_path}")
```

## Project Structure Template

```python
"""
Project Name - Component Description
====================================

Brief description of what this model creates and its purpose.

Target dimensions: WxDxH mm
Manufacturing: 3D printing / CNC / Injection molding
Material: PLA / ABS / Aluminum / etc.
"""

import cadquery as cq
from pathlib import Path

# ============================================================================
# DESIGN PARAMETERS
# ============================================================================

# Overall dimensions
WIDTH = 50
DEPTH = 30
HEIGHT = 20

# Component dimensions
# ... specific measurements

# Component positions
# ... placement coordinates

# Manufacturing tolerances
CLEARANCE = 0.2
WALL_THICKNESS = 2.0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_base_shape():
    """Create the base geometry."""
    pass

def add_features(base):
    """Add mounting, cutouts, etc."""
    pass

# ============================================================================
# MAIN ASSEMBLY
# ============================================================================

def generate_model():
    """Generate complete model with all features."""
    print(f"Generating {PROJECT_NAME}...")
    
    model = create_base_shape()
    model = add_features(model)
    
    return model

def export_all():
    """Generate and export models."""
    model = generate_model()
    export_models(model, "part_name")
    print("\n✓ Generation complete!")

if __name__ == "__main__":
    export_all()
```

## Advanced Techniques

### Parametric Assemblies with Multiple Parts

```python
def create_two_part_enclosure(width, depth, height, wall_thickness):
    """Create matching top and bottom shells."""
    
    # Calculate split line
    split_z = height / 2
    
    # Create full enclosure
    full_enclosure = create_basic_enclosure(width, depth, height, wall_thickness)
    
    # Split into top and bottom
    split_plane = (
        cq.Workplane("XY")
        .workplane(offset=split_z)
        .rect(width * 2, depth * 2)
        .extrude(0.1)
    )
    
    bottom_shell = full_enclosure.cut(split_plane)
    top_shell = full_enclosure.intersect(split_plane)
    
    return bottom_shell, top_shell
```

### Programmatic Component Layout

```python
def layout_components(components_dict, spacing=5):
    """Automatically arrange components with spacing.
    
    Args:
        components_dict: {"name": {"width": w, "depth": d, "height": h, "model": cq_obj}}
        spacing: Minimum spacing between components
    
    Returns:
        dict: Updated with "position": (x, y, z) for each component
    """
    current_x = 0
    
    for name, comp in components_dict.items():
        comp["position"] = (current_x, 0, 0)
        current_x += comp["width"] + spacing
    
    return components_dict
```

## Debugging and Visualization Tips

### Using CQ-Editor for Visual Debugging

If user has cq-editor installed:
```python
# Add this at the end of the script for interactive viewing
show_object(model)  # Only works in cq-editor
```

### Breaking Complex Operations into Steps

```python
# When debugging, save intermediate steps
step1 = create_basic_shape()
export_models(step1, "step1_basic")

step2 = add_first_feature(step1)
export_models(step2, "step2_first_feature")

step3 = add_second_feature(step2)
export_models(step3, "step3_second_feature")
```

### Validation Checks

```python
def validate_clearances(components):
    """Check that components don't overlap."""
    for i, comp1 in enumerate(components):
        for comp2 in components[i+1:]:
            distance = calculate_distance(comp1, comp2)
            min_clearance = 2.0  # mm
            
            if distance < min_clearance:
                print(f"⚠ Warning: {comp1['name']} and {comp2['name']} too close!")
                print(f"  Distance: {distance:.2f}mm (min: {min_clearance}mm)")
```

## Real-World Example: Handheld Device Enclosure

This example demonstrates a complete workflow for a cylindrical handheld device:

```python
"""
Handheld AI Device Enclosure
============================
Stick-shaped device with battery, PCB, buttons, and speaker.
Target dimensions: 30×30×150mm
"""

import cadquery as cq
from pathlib import Path

# Design parameters
DEVICE_DIAMETER = 30
DEVICE_HEIGHT = 150
WALL_THICKNESS = 2.5

BATTERY_DIAMETER = 18.6
BATTERY_LENGTH = 65

PCB_WIDTH = 21
PCB_DEPTH = 17.5

BUTTON_DIAMETER = 12
SPEAKER_DIAMETER = 23
MIC_DIAMETER = 2

# Positions
BATTERY_Z = 5
PCB_Z = BATTERY_Z + BATTERY_LENGTH + 5
BUTTON_Z = DEVICE_HEIGHT * 0.65
SPEAKER_Z = DEVICE_HEIGHT * 0.35
MIC_Z = DEVICE_HEIGHT * 0.85

# Tolerances
PRINT_TOL = 0.2

def create_enclosure():
    """Generate the complete enclosure."""
    
    # Basic cylindrical shell
    outer_r = DEVICE_DIAMETER / 2
    inner_r = outer_r - WALL_THICKNESS
    
    shell = (
        cq.Workplane("XY")
        .circle(outer_r)
        .extrude(DEVICE_HEIGHT)
        .faces(">Z")
        .workplane()
        .circle(inner_r)
        .cutThruAll()
    )
    
    # Add button cutout
    button_hole = (
        cq.Workplane("YZ")
        .workplane(offset=0)
        .center(0, BUTTON_Z - DEVICE_HEIGHT/2)
        .circle((BUTTON_DIAMETER + PRINT_TOL) / 2)
        .extrude(outer_r + 1)
    )
    shell = shell.cut(button_hole)
    
    # Add speaker grille
    hole_r = 0.75
    spacing = 2.5
    for x in range(-3, 4):
        for y in range(-3, 4):
            x_pos = x * spacing
            y_pos = y * spacing
            if (x_pos**2 + y_pos**2)**0.5 <= SPEAKER_DIAMETER/2:
                hole = (
                    cq.Workplane("YZ")
                    .center(x_pos, SPEAKER_Z - DEVICE_HEIGHT/2 + y_pos)
                    .circle(hole_r)
                    .extrude(outer_r + 1)
                )
                shell = shell.cut(hole)
    
    return shell

# Generate and export
if __name__ == "__main__":
    model = create_enclosure()
    output = Path(__file__).parent / "output"
    output.mkdir(exist_ok=True)
    cq.exporters.export(model, str(output / "enclosure.stl"))
    print("✓ Enclosure generated")
```

## Common Pitfalls and Solutions

### 1. Floating Point Precision Issues
```python
# BAD: Can cause tiny gaps
height = 10.0
offset = height / 3  # Might be 3.333333...

# GOOD: Use explicit rounding
offset = round(height / 3, 2)  # 3.33
```

### 2. Face Selection Ambiguity
```python
# BAD: Might select wrong face
.faces(">Z")  # "Highest Z" - but multiple faces might have same Z

# GOOD: Use specific selection
.faces(">Z").faces("<Y")  # Highest Z AND lowest Y
```

### 3. Workplane Orientation Confusion
```python
# Remember: workplane() without args stays on current face
# workplane(offset=N) moves perpendicular to current plane

# Clear pattern:
result = (
    cq.Workplane("XY")           # Start at origin, looking up
    .workplane(offset=10)        # Move to Z=10
    .circle(5)                   # Draw circle at Z=10
    .extrude(10)                 # Extrude upward to Z=20
)
```

## Communication Guidelines for Claude

When helping users with CAD modeling:

1. **Always ask about constraints first:**
   - Manufacturing method (3D printing, CNC, injection molding)?
   - Material and tolerances?
   - Assembly requirements?
   - Component dimensions?

2. **Start with parameters:**
   - Define all dimensions as variables before writing any geometry code
   - Include tolerances explicitly

3. **Build incrementally:**
   - Create basic shape first
   - Add features one at a time
   - Export at each major step for testing

4. **Explain design decisions:**
   - Why certain wall thicknesses?
   - Why specific fillet radii?
   - How tolerances affect fit?

5. **Provide complete, runnable scripts:**
   - Include all imports
   - Add clear comments
   - Include export functions
   - Make it executable with `python script.py`

## Installation and Setup

Quick start for new projects:

```bash
# Using uv (recommended)
uv init my-cad-project
cd my-cad-project
uv add cadquery jupyter

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install cadquery jupyter

# Create project structure
mkdir -p models output docs
```

## Summary

This skill enables Claude to:
- Design 3D models programmatically using CadQuery
- Create manufacturing-ready files (STL, STEP)
- Apply proper tolerances and design constraints
- Build complex assemblies from parametric components
- Follow mechanical engineering best practices

The key advantage of programmatic CAD is iteration speed: change parameters, regenerate, and see results instantly.
