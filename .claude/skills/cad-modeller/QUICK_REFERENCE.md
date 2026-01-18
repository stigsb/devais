# CadQuery Quick Reference

Quick lookup for common operations when using the CAD Modeller skill.

## Basic Shapes

```python
import cadquery as cq

# Box/Cube
box = cq.Workplane("XY").box(width, depth, height)

# Cylinder
cylinder = cq.Workplane("XY").circle(radius).extrude(height)

# Sphere
sphere = cq.Workplane("XY").sphere(radius)

# Cone
cone = cq.Workplane("XY").circle(base_radius).workplane(offset=height).circle(top_radius).loft()
```

## Boolean Operations

```python
# Union (combine)
result = shape1.union(shape2)

# Cut (subtract)
result = shape1.cut(shape2)

# Intersect (common volume)
result = shape1.intersect(shape2)
```

## Creating Holes

```python
# Through hole (circular)
result = (
    cq.Workplane("XY")
    .box(50, 50, 10)
    .faces(">Z")
    .workplane()
    .hole(diameter)
)

# Blind hole (doesn't go all the way through)
result = (
    cq.Workplane("XY")
    .box(50, 50, 10)
    .faces(">Z")
    .workplane()
    .circle(radius)
    .cutBlind(-depth)
)

# Counterbore (for screw heads)
result = (
    cq.Workplane("XY")
    .box(50, 50, 10)
    .faces(">Z")
    .workplane()
    .cboreHole(diameter, cbore_diameter, cbore_depth)
)
```

## Fillets and Chamfers

```python
# Fillet (round edges)
result = shape.edges("|Z").fillet(radius)  # Vertical edges

# Chamfer (angled edges)
result = shape.edges(">Z").chamfer(distance)  # Top edges

# Select specific edges
result = shape.edges("<Z").fillet(radius)  # Bottom edges
result = shape.edges("|X").chamfer(distance)  # X-parallel edges
```

## Face Selection

```python
# By direction
.faces(">Z")  # Highest Z face(s)
.faces("<Z")  # Lowest Z face(s)
.faces(">X")  # Highest X
.faces("<Y")  # Lowest Y

# By type
.faces("%Plane")    # Planar faces
.faces("%Cylinder") # Cylindrical faces
.faces("%Sphere")   # Spherical faces

# Combine selectors
.faces(">Z").faces("<Y")  # Top AND front
```

## Patterns (Arrays)

```python
# Linear pattern along X axis
for i in range(count):
    x_pos = i * spacing
    feature = create_feature().translate((x_pos, 0, 0))
    result = result.union(feature)

# Circular pattern
import math
for i in range(count):
    angle = (i / count) * 360
    angle_rad = math.radians(angle)
    x_pos = radius * math.cos(angle_rad)
    y_pos = radius * math.sin(angle_rad)
    feature = create_feature().translate((x_pos, y_pos, 0))
    result = result.union(feature)

# Grid pattern
for x in range(x_count):
    for y in range(y_count):
        x_pos = x * x_spacing
        y_pos = y * y_spacing
        feature = create_feature().translate((x_pos, y_pos, 0))
        result = result.union(feature)
```

## Common Mounting Features

```python
# Screw post with hole
def mounting_post(diameter=6, height=5, screw_dia=3):
    post = (
        cq.Workplane("XY")
        .circle(diameter / 2)
        .extrude(height)
        .faces(">Z")
        .circle(screw_dia / 2)
        .cutBlind(-height)
    )
    return post

# Press-fit boss
def press_fit_boss(diameter, height, interference=0.1):
    actual_diameter = diameter - interference
    boss = (
        cq.Workplane("XY")
        .circle(actual_diameter / 2)
        .extrude(height)
    )
    return boss

# Snap-fit clip
def snap_clip(width, height, flex_thickness=1.5):
    clip = (
        cq.Workplane("XY")
        .rect(width, flex_thickness)
        .extrude(height)
        .faces(">Z")
        .workplane()
        .rect(width * 0.7, flex_thickness * 2)
        .extrude(2)
    )
    return clip
```

## Tolerances

```python
# Standard tolerances for FDM 3D printing
CLEARANCE_FIT = 0.3      # Loose fit
TRANSITION_FIT = 0.1     # Snug fit
INTERFERENCE_FIT = -0.05 # Press fit

# Hole with clearance
hole_diameter = shaft_diameter + (2 * CLEARANCE_FIT)

# Boss with interference
boss_diameter = hole_diameter - (2 * INTERFERENCE_FIT)
```

## Workplane Positioning

```python
# Start on XY plane (top view)
cq.Workplane("XY")

# Start on YZ plane (side view)
cq.Workplane("YZ")

# Offset workplane in Z
cq.Workplane("XY").workplane(offset=10)

# Center the workplane
cq.Workplane("XY").center(x, y)

# Create workplane on selected face
shape.faces(">Z").workplane()
```

## Export

```python
from pathlib import Path

# Export STL (for 3D printing)
cq.exporters.export(model, "output.stl")

# Export STEP (for CAD import)
cq.exporters.export(model, "output.step")

# Export SVG (2D profile)
cq.exporters.export(model.section(), "output.svg")

# With proper paths
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)
cq.exporters.export(model, str(output_dir / "part.stl"))
```

## Hollow Shapes

```python
# Shell (hollow out from face)
result = solid.faces(">Z").shell(-wall_thickness)

# Manual hollow (cut inner shape)
outer = cq.Workplane("XY").box(50, 50, 50)
inner = cq.Workplane("XY").box(45, 45, 45)
hollow = outer.cut(inner)
```

## Advanced Selection

```python
# By location (nearest to point)
.faces(cq.NearestToPointSelector((0, 0, 50)))

# By direction AND location
.faces(">Z").faces(cq.NearestToPointSelector((10, 0, 50)))

# By box intersection
.faces(cq.BoxSelector((0, 0, 0), (10, 10, 10)))
```

## Common Issues & Solutions

### Issue: Face not found
**Solution:** Check face direction, try `>Z` vs `<Z`, or use `.faces().first()`

### Issue: Cut didn't go through
**Solution:** Make cutting shape slightly larger than target, e.g. `extrude(depth + 1)`

### Issue: Tolerance issues in print
**Solution:** Apply `PRINT_TOLERANCE` to holes/cutouts, subtract from bosses

### Issue: Complex selection fails
**Solution:** Select in steps: `.faces(">Z").faces("<Y")` instead of trying both at once

### Issue: Boolean operation failed
**Solution:** Ensure shapes actually intersect, check for very small gaps

## Coordinate System

```
    Z (up)
    |
    |___Y
   /
  X

- XY plane: Top view (looking down)
- YZ plane: Side view (looking from right)
- XZ plane: Front view (looking from front)
```

## Measurement Units

CadQuery uses **millimeters** by default. Always specify units in comments:

```python
DIAMETER = 25  # mm
THICKNESS = 2.5  # mm
```

## Pro Tips

1. **Always parameterize:** Define dimensions as variables at the top
2. **Build incrementally:** Create base shape, add features one at a time
3. **Export often:** Test prints early to catch issues
4. **Use helper functions:** Reusable features = cleaner code
5. **Comment liberally:** Future you will thank present you
6. **Check clearances:** Add tolerance to holes, subtract from bosses
7. **Test fit:** Print test pieces before full assembly

## Example: Complete Workflow

```python
import cadquery as cq
from pathlib import Path

# Parameters
WIDTH = 50
HEIGHT = 20
WALL = 2.5

# Helper functions
def create_shell():
    outer = cq.Workplane("XY").box(WIDTH, WIDTH, HEIGHT)
    inner = cq.Workplane("XY").workplane(offset=WALL).box(WIDTH-2*WALL, WIDTH-2*WALL, HEIGHT)
    return outer.cut(inner)

def add_mounting_holes(shell):
    hole = cq.Workplane("XY").rect(WIDTH-10, WIDTH-10, forConstruction=True).vertices().circle(1.5).extrude(5)
    return shell.cut(hole)

# Generate
model = create_shell()
model = add_mounting_holes(model)

# Export
output = Path(__file__).parent / "output"
output.mkdir(exist_ok=True)
cq.exporters.export(model, str(output / "part.stl"))
```

---

**Tip:** Keep this reference handy when working with the CAD Modeller skill!
