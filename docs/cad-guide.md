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
# - enclosure.stl (Main body)
# - large_button.stl (The push-to-talk button)
```

## Design Parameters

All key dimensions are defined at the top of `cad/enclosure.py`:

### Enclosure Dimensions
- **Shape**: Octagonal Prism (Square with chamfered corners)
- `DEVICE_WIDTH`: 40.0mm (Flat-to-flat distance)
- `DEVICE_HEIGHT`: 150.0mm
- `WALL_THICKNESS`: 2.5mm
- `FILLET_RADIUS`: 4.0mm (Edges and corners)

### Component Positioning
Vertical positions (Z-axis) are measured from the bottom of the device:

- **Push-to-Talk Button**: Centered at 105.0mm (Right Side)
- **Power Button**: 25.0mm (Right Side)
- **USB-C Port**: 12.0mm (Right Side)
- **Microphone**: 10.0mm (Front Side)
- **Speaker**: Upper Front (approx. 120-130mm, relative to LEDs)
- **LEDs**: 140.0mm (Front Side, 10mm from top)

### Component Dimensions
- **Large Button**: 24.9mm width × 45mm height
- **Speaker**: ~20mm diameter (80% of long side width)
- **Power Button**: 8mm diameter
- **USB-C**: 9.5mm × 3.7mm

## Coordinate System

The design uses the following coordinate system:
- **Z-axis**: Vertical height (0 to 150mm)
- **XY-plane**: The octagonal cross-section
- **Front Face**: +Y direction
- **Right Face**: +X direction

## Modifying the Design

### Changing Dimensions

1. Open `cad/enclosure.py`
2. Modify parameters at the top of the file
3. Run `uv run python cad/enclosure.py` to regenerate

Example - moving the large button:
```python
LARGE_BTN_CENTER_FROM_BOTTOM = 110.0  # Changed from 105.0
```

### Adding New Features

The script is organized into modular functions:

- `create_octagonal_prism()` - Base geometry
- `add_large_button_feature()` - Opening and frame for main button
- `add_power_button()` - Power button cutout
- `add_usbc_port()` - USB-C port cutout
- `add_speaker_grille()` - Perforated speaker holes
- `add_mic_hole_and_mount()` - Mic hole and internal pocket
- `add_led_holes()` - Status LED openings

To add a new feature, create a similar function and call it in `build_enclosure()`.

## Design Considerations

### 3D Printing
- **Orientation**: Print vertically (standing on its bottom face).
- **Supports**: The octagonal shape and 45° chamfers are self-supporting. The large button frame and internal pockets may require minimal supports depending on the printer.
- **Tolerances**: 
    - `PRINT_TOLERANCE` and `PRESS_FIT_TOLERANCE` should be considered for mating parts.
    - The large button opening includes clearance for the button movement.

### Ergonomics  
- The 40mm octagonal shape ("square stick with chamfered corners") provides a comfortable grip.
- The large, textured orange button is positioned for easy thumb activation.
- Rounded edges (4mm fillet) ensure no sharp corners.

## Working with AI Assistants

This parametric design is ideal for AI-assisted iteration. You can ask for changes like:

> "Move the USB-C port 2mm higher"
> "Increase the large button height to 50mm"
> "Add a lanyard hole on the bottom left side"

The assistant can read the current `enclosure.py`, understand the parameter names, and apply the specific changes safely.

## Export Formats

### STL (`.stl`)
- Standard 3D printing format.
- Output includes `enclosure.stl` and `large_button.stl` as separate files for printing.

## Troubleshooting

**Issue**: Model looks wrong in viewer
- Ensure you are viewing in Millimeters.
- Check if the octagonal profile is generated correctly (8 points).

**Issue**: Python errors
- Ensure dependencies are installed: `uv sync`
- Check CadQuery version compatibility if moving between environments.