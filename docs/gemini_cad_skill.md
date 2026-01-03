# Gemini CAD Modeller Skill

## Overview

This guide enables Gemini to create 3D CAD models programmatically using Python-based CAD tools, primarily CadQuery. Use this skill when users need to design physical objects, enclosures, mechanical parts, or any 3D-printable components through code rather than traditional CAD software.

## When to Use This Skill

**Always use this skill when:**
- User asks to create or design a 3D model, enclosure, or mechanical part
- User mentions CAD, 3D printing, STL files, or physical product design
- User wants to iterate on dimensions or design parameters
- User needs component mounting features, wire routing channels, or assembly features
- User wants to export models for manufacturing (3D printing, CNC, injection molding)

## Tool Selection: CadQuery

**Default choice:** Use CadQuery (`cadquery`) as the primary tool. It provides a robust, parametric workflow suitable for code-generated models.

## Core CadQuery Concepts

### 1. Workplane-Based Design
Everything starts with a workplane:

```python
import cadquery as cq

# Start on XY plane (looking down from above)
result = cq.Workplane("XY")
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
```

### 3. Combining Operations
Use boolean operations to build complex shapes:

```python
# Union (combine shapes)
combined = shape1.union(shape2)

# Cut (subtract shapes)
hollowed = outer_shell.cut(inner_cavity)
```

## Design Workflow Best Practices

### 1. Parameter-Driven Design
**Always start by defining all dimensions as variables:**

```python
# Overall dimensions
ENCLOSURE_WIDTH = 30
ENCLOSURE_DEPTH = 30
ENCLOSURE_HEIGHT = 150
WALL_THICKNESS = 2.5

# Manufacturing tolerances
PRINT_TOLERANCE = 0.2        # For 3D printing
```

### 2. Organize with Helper Functions

Break complex models into logical functions (e.g., `create_basic_shell`, `add_mounting_features`).

### 3. Positioning Strategy
Use relative positioning based on defined constants rather than magic numbers.

## Common Patterns

### Creating Holes and Cutouts

**Circular holes:**
```python
def add_circular_cutout(enclosure, diameter, center_x, center_y, z_position):
    hole = (
        cq.Workplane("YZ")
        .workplane(offset=0)
        .center(center_y, z_position)
        .circle(diameter / 2)
        .extrude(100)
    )
    return enclosure.cut(hole)
```

### Wire Routing Channels
Create channels for wires to pass between components using `cut` operations with rectangular extrusions.

## Manufacturing Considerations

- **3D Printing Tolerances:** Apply tolerances (e.g., `0.2mm`) to holes and mating parts.
- **Wall Thickness:** Minimum `1.5mm` for FDM printing.
- **Overhangs:** Avoid overhangs > 45 degrees or use chamfers/fillets.

## Export and File Management

Always provide a script that exports the model to STL (and optionally STEP).

```python
from pathlib import Path
import cadquery as cq

def export_model(model, filename="output.stl"):
    cq.exporters.export(model, filename)
    print(f"Exported to {filename}")
```

## Communication Guidelines

1. **Ask about constraints:** Material, manufacturing method, critical dimensions.
2. **Start with parameters:** Define them clearly at the top of the script.
3. **Provide complete scripts:** Ensure the code is runnable and includes export logic.
