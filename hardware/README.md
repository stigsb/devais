# Devais Hardware Design

Circuit definitions for Devais handheld AI assistant device using circuit-synth.

## Circuit Structure

The hardware design is modular, following software engineering best practices:

```
hardware/
├── devais.py              # Main circuit (composition of all subsystems)
├── power_management.py    # USB-C, battery, voltage regulation
├── audio.py              # I2S microphone and amplifier
├── user_interface.py     # Buttons and LEDs
└── README.md            # This file
```

## Components Overview

### Power System
- **USB-C connector** with 5.1k CC resistors (power sink configuration)
- **TP4056** Li-ion battery charger (1A charge current)
- **18650 battery** with protection
- **AMS1117-3.3** LDO regulator for 3.3V supply
- **Schottky diodes** for automatic USB/battery power selection

### Audio System (I2S Bus)
- **INMP441** MEMS I2S microphone
- **MAX98357A** Class D I2S amplifier (9dB gain for battery efficiency)
- **Speaker** (20-28mm diameter)
- Shared SCK and WS clock signals (efficient architecture)

### User Interface
- Push-to-talk button (with interrupt on P0.02)
- Power/mode button (with interrupt on P0.03)
- 3x Status LEDs:
  - Power (green)
  - BLE connectivity (blue)
  - Activity indicator (amber/yellow)

### Microcontroller
- **Seeed XIAO nRF52840** module
- BLE connectivity
- I2S peripheral for audio
- SWD programming interface (10-pin header)

## Pin Assignments (nRF52840)

| Function | Pin | Description |
|----------|-----|-------------|
| **I2S Audio** | | |
| I2S SCK | P0.26 | Bit clock (shared mic/amp) |
| I2S WS | P0.27 | Word select (shared mic/amp) |
| I2S SDI | P0.28 | Serial data in (from mic) |
| I2S SDO | P0.29 | Serial data out (to amp) |
| **User Interface** | | |
| PTT Button | P0.02 | Push-to-talk (interrupt) |
| Power Button | P0.03 | Power/mode (interrupt) |
| Power LED | P0.06 | Green status LED |
| BLE LED | P0.07 | Blue connectivity LED |
| Activity LED | P0.08 | Amber activity LED |

## Generating KiCad Files

```bash
# From the hardware/ directory
cd /Users/stig/git/stigsb/devais/hardware

# Activate virtual environment
source ../.venv/bin/activate

# Generate KiCad project
python devais.py
```

This creates:
- `devais_v1/devais_v1.kicad_pro` - KiCad project file
- `devais_v1/devais_v1.kicad_sch` - Schematic file
- `devais_v1/devais_v1.kicad_pcb` - PCB layout file
- `devais_v1/devais_v1.net` - Netlist

## Opening in KiCad

```bash
open devais_v1/devais_v1.kicad_pro
```

## Making Changes

### Modify Circuit
1. Edit the Python files (`devais.py`, `audio.py`, etc.)
2. Run `python devais.py` to regenerate KiCad files
3. Circuit-synth will update component references in your Python source

### Modify PCB Layout
1. Open in KiCad and make changes to PCB layout
2. Changes to layout are preserved (not overwritten by circuit-synth)
3. If you change schematic in KiCad, you can import it back to Python

## Generating Manufacturing Files

```python
from devais import devais_main

circuit = devais_main()

# Generate BOM
circuit.generate_bom("devais_v1")

# Generate PDF schematic
circuit.generate_pdf_schematic("devais_v1")

# Generate Gerber files
circuit.generate_gerbers("devais_v1")
```

## Component Sourcing

Many components may need custom KiCad symbols/footprints. You can use circuit-synth's component search:

```bash
# Search for components
/find-parts "INMP441" --source jlcpcb
/find-parts "MAX98357A" --source jlcpcb
/find-symbol "nRF52840"

# Check JLCPCB availability
jlc-fast search "TP4056"
```

## Known Issues / TODOs

1. **Custom symbols needed:**
   - INMP441 microphone (might use generic breakout symbol)
   - MAX98357A amplifier (might use generic breakout symbol)
   - Seeed XIAO nRF52840 module (needs custom symbol)

2. **Footprint selection:**
   - Most footprints specified are standard
   - Audio module footprints may need adjustment for actual breakout boards

3. **Power management refinement:**
   - Consider load switch for power button control
   - Battery protection circuit details
   - USB-C ESD protection

4. **Audio tuning:**
   - Speaker impedance matching
   - Amplifier gain optimization
   - Acoustic design considerations

## Design Rationale

This circuit implements the design decisions documented in `../CLAUDE.md`:

- **Battery efficiency:** nRF52840 chosen over ESP32 for 2.5x better battery life
- **I2S audio:** Shared clock architecture reduces GPIO usage and improves efficiency
- **Modular design:** Each subsystem is independently testable and reusable
- **Version controlled:** All circuit changes tracked in git with meaningful diffs

## Next Steps

1. Generate KiCad project (`python devais.py`)
2. Verify component availability and adjust footprints
3. Create/import custom symbols for XIAO nRF52840, INMP441, MAX98357A
4. PCB layout (considering 30x30mm target size)
5. Review with electrical rules check (ERC)
6. Order prototype PCB and components
7. Assembly and testing

## Questions?

See the main project README and CLAUDE.md for project context and design philosophy.
