# CAD Modeller Skill for Claude

A comprehensive skill that enables Claude to create 3D CAD models programmatically using Python-based CAD tools (primarily CadQuery).

## What This Skill Does

This skill teaches Claude how to:
- Design 3D models using code instead of traditional CAD software
- Create manufacturing-ready files (STL for 3D printing, STEP for CAD)
- Apply proper tolerances for different manufacturing methods
- Design component mounting features, wire routing channels, and assemblies
- Follow mechanical engineering best practices

## When Claude Uses This Skill

Claude automatically uses this skill when you:
- Ask to design or create a 3D model
- Mention 3D printing, CAD, or STL files
- Request enclosures, cases, brackets, mounts, or holders
- Need mechanical parts or assemblies designed

## Installation

### For Claude.ai Projects

1. **Upload to your project:**
   - Copy `SKILL.md` into your project's skills folder
   - Or upload directly through the Claude interface

2. **Reference in your prompts:**
   ```
   Using the CAD modeller skill, design an enclosure for...
   ```

### For Local Development

If you want to use the patterns from this skill in your own projects:

```bash
# Create a new project
uv init my-cad-project
cd my-cad-project

# Add CadQuery
uv add cadquery

# Optional: Jupyter for interactive development
uv add jupyter
```

## Quick Examples

### Example 1: Simple Box
```
Claude, design a box that's 50x30x20mm with 2mm walls.
Export it as an STL file.
```

### Example 2: Component Enclosure
```
I need an enclosure for a Raspberry Pi Zero (65x30mm PCB).
It should have mounting posts, ventilation holes, and a cutout 
for the USB port. Use 2.5mm wall thickness.
```

### Example 3: Custom Mount
```
Design a bracket to mount a 28mm diameter speaker to a 
30mm diameter cylindrical surface. Include screw holes for M3 screws.
```

### Example 4: Iterative Design
```
Create a cylindrical case, 40mm diameter and 100mm tall.
Add a battery compartment for an 18650 cell (18.6mm diameter).
Add cutouts for: a button at 70mm height, LEDs at the top, 
and a USB-C port at the bottom.
```

## What Makes This Skill Useful

### 1. **Parametric Design**
All dimensions are variables. Want to make it bigger? Change one number, regenerate.

### 2. **Version Control Friendly**
Models are Python code - works perfectly with Git.

### 3. **Rapid Iteration**
Modify parameters and regenerate in seconds, not hours.

### 4. **Manufacturing Ready**
Built-in tolerance handling for 3D printing, CNC, injection molding.

### 5. **AI-Friendly**
Claude can read, write, and modify the code to match your requirements.

## Project Structure

When Claude creates a CAD project, you'll typically get:

```
my-project/
├── pyproject.toml          # Dependencies (uv/pip)
├── models/
│   ├── enclosure.py       # Main model script
│   └── assembly.py        # Multi-part assembly
├── output/
│   ├── *.stl             # 3D printable files
│   └── *.step            # CAD-compatible files
├── docs/
│   └── specifications.md  # Design notes
└── README.md
```

## Real-World Use Case: Handheld Device

This skill was developed while designing "devais" - a handheld AI assistant device. The project required:
- Cylindrical enclosure (30x30x150mm)
- 18650 battery compartment
- PCB mounting with proper clearances
- Button and LED cutouts
- Speaker grille patterns
- USB-C port opening
- Wire routing channels

The entire enclosure was designed parametrically, making it easy to:
- Adjust dimensions when components changed
- Add new features without starting over
- Export manufacturing files with one command
- Share the design as code in version control

## Supported Manufacturing Methods

The skill includes guidelines for:
- **FDM 3D Printing** (PLA, ABS, PETG)
  - Tolerances, overhang angles, wall thickness
- **SLA/Resin Printing**
  - Minimum features, support requirements
- **CNC Machining**
  - Tool access, material considerations
- **Injection Molding**
  - Draft angles, uniform wall thickness

## Advanced Features

### Component Layout Planning
Automatically calculate positions, clearances, and routing paths.

### Assembly Features
Design parts that snap together, screw together, or press-fit.

### Parametric Families
Create variations of a design with different dimensions.

### Validation
Check for clearances, interference, and manufacturing constraints.

## Skill Development Notes

This skill captures learnings from building a real hardware project:
- Start with parameters, not geometry
- Build incrementally, export often
- Design for manufacturing from the start
- Use helper functions for reusable features
- Document design decisions in code comments

## Contributing

This skill was created based on a real project (devais - handheld AI device). 
If you find patterns or techniques that should be added, please contribute!

## Tools Covered

### Primary: CadQuery
- Most mature, best documented
- Powerful OCCT kernel
- Large community and examples

### Alternative: Build123d
- More modern, Pythonic API
- Actively developed
- Good for new projects

### Alternative: OpenSCAD (via SolidPython)
- Simple for basic shapes
- Requires separate OpenSCAD installation

## Learning Resources

After Claude designs your model:
- Review the generated Python code
- Modify parameters to see effects
- Read CadQuery docs: https://cadquery.readthedocs.io/
- Explore examples in the skill document

## License

This skill is provided as-is for use with Claude. The skill document and examples are free to use and modify.

---

**Created:** January 2025  
**Based on:** devais project - handheld AI assistant device  
**Maintained by:** stigsb
