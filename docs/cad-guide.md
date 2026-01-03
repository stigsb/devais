# CAD Design Guide

## Overview

The devais enclosure is designed using **CadQuery**, a Python-based parametric CAD system. This approach allows for programmatic design where dimensions and features can be easily adjusted through code parameters.

## Quick Start

```bash
# Install dependencies (first time only)
uv sync

# Generate the enclosure model
uv run python cad/enclosure.py

# Output files will be in cad/output/
# - devais_enclosure.stl (for 3D printing)
# - devais_enclosure.step (for CAD software)
```

## Design Parameters

All key dimensions are defined at the top of `cad/enclosure.py`:

### Enclosure Dimensions
- `DEVICE_WIDTH`: 30mm (diameter)
- `DEVICE_DEPTH`: 30mm (diameter)  
- `DEVICE_HEIGHT`: 150mm
- `WALL_THICKNESS`: 2.5mm

### Component Dimensions
Component sizes are defined based on actual hardware specs:
- 18650 battery: 18.6mm × 65mm
- XIAO nRF52840: 21mm × 17.5mm
- Speakers, microphones, buttons, etc.

### Component Positioning
Vertical positions (Z-axis) from bottom of device:
- `BATTERY_BOTTOM_OFFSET`: 5mm
- `BUTTON_Z_OFFSET`: 65% up device (97.5mm)
- `SPEAKER_Z_OFFSET`: 35% up device (52.5mm)
- `MIC_Z_OFFSET`: 85% up device (127.5mm)
- `LED_Z_OFFSET`: 95% up device (142.5mm)

### Tolerances
- `PRINT_TOLERANCE`: 0.2mm (general clearance)
- `PRESS_FIT_TOLERANCE`: 0.1mm (tight fits)

## Modifying the Design

### Changing Dimensions

1. Open `cad/enclosure.py`
2. Modify parameters at the top of the file
3. Run `uv run python cad/enclosure.py` to regenerate
4. The new STL/STEP files will reflect your changes

Example - making the device taller:
```python
DEVICE_HEIGHT = 160  # Changed from 150
```

### Adding New Features

The script is organized into modular functions:

- `create_basic_enclosure()` - Main cylindrical body
- `add_battery_compartment()` - Battery holder
- `add_button_cutout()` - Push-to-talk button
- `add_speaker_grille()` - Speaker holes
- `add_mic_hole()` - Microphone opening
- `add_led_holes()` - Status LED openings
- `add_usbc_port()` - Charging port
- `create_component_mounts()` - PCB mounting posts

To add a new feature, create a similar function and call it in `generate_enclosure()`.

## Design Considerations

### 3D Printing
- Wall thickness of 2.5mm provides good strength
- Tolerances account for typical FDM printer accuracy
- Speaker grille uses 0.75mm holes with 2.5mm spacing
- Design prints well without supports when oriented vertically

### Component Clearances
- Battery compartment sized for standard 18650
- Mounting posts positioned for component boards
- Wire routing channels (to be added) will connect components
- Consider assembly order when adding features

### Ergonomics  
- 30mm diameter fits comfortably in hand
- Push-to-talk button at 65% height is thumb-accessible
- Rounded edges for comfort (can be added via fillets)

## Working with Claude Code

This parametric design is ideal for AI-assisted iteration. You can ask Claude Code to:

- Adjust component positions
- Add new mounting features
- Create wire routing channels
- Modify dimensions based on constraints
- Add assembly features (clips, screw holes)

Example request:
> "Move the button 10mm higher and add a wire channel connecting the battery to the XIAO board"

Claude Code can read the current design, understand the spatial relationships, and make precise modifications to the Python script.

## Export Formats

### STL (`.stl`)
- Standard 3D printing format
- Import directly into your slicer (PrusaSlicer, Cura, etc.)
- Units: millimeters

### STEP (`.step`)
- Universal CAD exchange format
- Can be opened in Fusion 360, FreeCAD, SolidWorks, etc.
- Preserves exact geometry
- Useful for further refinement in traditional CAD

## Next Steps

Current design focuses on the main enclosure shell. Future additions:

1. **Wire routing channels** - Grooves for organizing internal wiring
2. **Assembly features** - Snap-fit clips or screw bosses for top/bottom caps
3. **Component-specific holders** - Custom mounts for speaker, mic, amp
4. **Strain relief** - Features to protect USB-C connection
5. **Split design** - Separate top and bottom halves for easier printing and assembly

## Troubleshooting

**Issue**: Model looks wrong in viewer
- Check dimensions are in millimeters, not inches
- Verify all positions are positive values
- Check that cutouts don't extend beyond enclosure

**Issue**: 3D printer can't slice the file  
- Try exporting again
- Check STL file size isn't corrupted
- Open in a CAD viewer to verify geometry

**Issue**: Python errors when running script
- Run `uv sync` to install/update dependencies
- Use `uv run python cad/enclosure.py` to ensure correct environment
- Check Python version is 3.10+ (`uv run python --version`)

## Resources

- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [CadQuery Examples](https://github.com/CadQuery/cadquery/tree/master/examples)
- [Parametric Design Patterns](https://cadquery.readthedocs.io/en/latest/examples.html)
