# Devais Main PCB

Custom PCB for the Devais handheld AI assistant, designed with [tscircuit](https://tscircuit.com/) (React/TypeScript).

## Board Specifications

- **Dimensions:** 28 x 72mm (2-layer, all components top-side)
- **Width constraint:** 28mm max inscribed square inside the 35mm interior octagonal enclosure
- **Height:** 72mm, sits above the 18650 battery (65mm) in the 150mm tall enclosure
- **Mounting:** 4x M2 holes at corners

## Architecture

The design splits functionality across multiple small boards connected by JST cables. This keeps the USB-C board cheap and replaceable (it takes mechanical stress from cable insertion), and puts the LED board where it needs to be physically (near the top of the enclosure, away from the main PCB).

### Main PCB (this board)

All processing, power management, and audio amplification.

| Ref | Component | Package | Function |
|-----|-----------|---------|----------|
| U_MCU | Seeed XIAO nRF52840 | DIP14 castellated | BLE microcontroller |
| U_AMP | MAX98357A | QFN-16 (3x3mm) | I2S Class D amplifier |
| U_REG | AMS1117-3.3 | SOT-223 | 3.3V LDO regulator |
| U_CHG | TP4056 | SOIC-8 | Li-ion battery charger (1A) |
| Q1 | 2N7002 | SOT-23 | N-ch MOSFET, LED VDD switch |
| SW_PTT | Tactile switch | 6x6mm | Push-to-talk button |
| SW_PWR | Tactile switch | 6x6mm | Power/mode button |

### External Boards (JST cables)

| Connector | Pins | Connects To |
|-----------|------|-------------|
| J_USB | 2 (VBUS, GND) | USB-C charging board |
| J_BAT | 2 (VBAT, GND) | 18650 battery holder |
| J_SPK | 2 (OUT+, OUT-) | Speaker (differential from MAX98357A) |
| J_LED | 3 (VDD_LED, GND, DATA) | WS2812B-2020 daughter PCB (2 LEDs) |
| J_MIC | 5 (VCC, GND, WS, SCK, SD) | INMP441 breakout board |

### USB-C Board (separate, replaceable)

Intentionally minimal: USB-C receptacle + 2x 5.1k CC resistors. No ICs. Designed to be cheap to replace when the connector wears out or breaks from mechanical stress.

## Pin Mapping (nRF52840 via XIAO)

| XIAO Pin | nRF52840 | Signal | Description |
|----------|----------|--------|-------------|
| D2 | P0.28 | I2S_SDI | Mic data → MCU |
| D3 | P0.29 | I2S_SDO | MCU → amp data |
| D4 | P0.02 | BTN_PTT | Push-to-talk (interrupt) |
| D5 | P0.03 | BTN_PWR | Power/mode (interrupt) |
| D6 | P0.26 | I2S_SCK | Shared bit clock |
| D7 | P0.27 | I2S_WS | Shared word select |
| D8 | P0.06 | LED_DATA | WS2812B data (daisy-chained) |
| D9 | P0.07 | LED_EN | MOSFET gate for LED VDD |

## PCB Layout (top to bottom)

```
Y=+33  ┌─ J_SPK (speaker)  J_LED (LEDs) ─┐
Y=+29  │  Q1 (MOSFET)      R_GATE         │
Y=+18  │         U_MCU (XIAO)             │
Y= +4  │  J_MIC (mic)      U_AMP (amp)    │
Y= -7  │       SW_PTT (push-to-talk)      │
Y=-16  │       SW_PWR (power/mode)        │
Y=-24  │         U_REG (3.3V LDO)         │
Y=-31  │  R_PROG  C_USB    U_CHG (charger)│
Y=-35  └─ J_USB (USB pwr)  J_BAT (battery)┘
```

## Build Commands

```bash
uv run pcb-build          # Validate circuit (runs tsci build)
uv run pcb-export         # Build + export SVG/schematic/assembly/netlist
```

Or directly with tsci:

```bash
cd hardware/pcb
tsci build                             # Validate
tsci export index.circuit.tsx -f pcb-svg        # PCB layout
tsci export index.circuit.tsx -f schematic-svg  # Schematic
tsci export index.circuit.tsx -f assembly-svg   # Assembly drawing
tsci dev                               # Interactive preview
```

Assembly diagram with accurate pad outlines:

```bash
uv run python3 hardware/pcb/generate_assembly.py
open hardware/pcb/assembly-top.png
```

## Design Decisions and Lessons Learned

### Tool Selection

We evaluated several PCB design tools for AI coding agent workflows:

| Tool | Verdict | Why |
|------|---------|-----|
| **circuit-synth** | Rejected | Requires KiCad installed for symbol libraries |
| **pcbflow** | Rejected | Alpha quality, not on PyPI, limited footprints, no schematic |
| **tscircuit** | Selected | Declarative JSX, built-in autorouter, JLCPCB search, no external deps |

**Key insight:** tscircuit's declarative React/JSX approach is far better for AI-driven iteration than imperative Python turtle routing. `tsci build` gives instant headless validation.

### Board Sizing

The board width (28mm) is fixed by the enclosure geometry: it's the maximum inscribed square inside the 35mm flat-to-flat interior octagon. We calculate this from the octagon's chamfer line: `x + y ≤ 28.4mm`, so a square board maxes out at 28mm.

The height evolved through iteration:
- 28mm (square): too dense, autorouter failed
- 55mm: courtyard overlaps in power section
- 90mm: too much empty space
- **72mm: good balance** — compact but every component has clearance

### Courtyard Overlaps

**Never ignore courtyard overlap warnings.** They mean components physically can't be soldered in those positions. Even if pads don't technically overlap, courtyard violations indicate insufficient clearance for:
- Soldering iron access
- Pick-and-place machine tolerances
- Rework and inspection

The DIP14 footprint for the XIAO nRF52840 is surprisingly large (7.6 x 15.2mm). This was the most common source of courtyard violations — components placed "above" or "below" the MCU would overlap its tall pad span.

### Autorouter Selection

- `auto` (capacity-mesh): fails on dense boards ("ran out of iterations")
- `auto-cloud`: requires tscircuit authentication, hung indefinitely
- **`sequential-trace`**: works reliably even on dense boards

### Component Placement Strategy

1. **Know your footprint sizes.** DIP14 is 15mm tall. SOT-223 is 6.3mm wide. SOIC-16 is 9mm tall. You need these numbers to calculate safe placement gaps.
2. **Verify with `tsci build` after every position change.** Don't batch up changes — you'll lose track of which move caused the overlap.
3. **Place largest components first** (MCU, then connectors, then ICs, then passives).
4. **Keep decoupling caps near their IC** but not so close that courtyards overlap. 3-4mm center-to-center is usually safe for 0603/0805 next to SOT-23 or larger.

### Modular Board Architecture

Splitting into main board + daughter boards was driven by practical concerns:
- **USB-C board:** Mechanical stress from cable insertion will eventually break the connector. A separate $0.50 board with just the connector + CC resistors is disposable.
- **LED board:** The WS2812B LEDs need to be physically at the top of the enclosure (behind the LED holes), far from where the main PCB sits. A 3-wire JST cable solves this.
- **Mic breakout:** INMP441 is a bottom-port MEMS mic requiring an acoustic path through the enclosure wall. Easier to position independently on a breakout board.

### LED VDD Switching

The N-channel MOSFET (2N7002) switches LED ground, not VDD. This is simpler than a high-side P-channel switch:
- Gate driven directly from 3.3V GPIO (D9)
- 10k pull-down resistor keeps LEDs off during MCU boot/reset
- WS2812B idle current (~1mA per LED) is eliminated when MOSFET is off

### JLCPCB Part Numbers

All ICs and passives have JLCPCB `supplierPartNumbers` for direct ordering. Use `tsci search --jlcpcb "<query>"` to verify stock before ordering.

## File Structure

```
hardware/pcb/
├── index.circuit.tsx       # Main circuit definition (source of truth)
├── generate_assembly.py    # Assembly diagram generator (reads circuit.json)
├── assembly-top.svg/.png   # Generated assembly drawing
├── index.circuit-pcb.svg   # Generated PCB layout
├── index.circuit-schematic.svg
├── index.circuit-assembly.svg
├── dist/index/circuit.json # Build output (component positions, nets, pads)
├── package.json            # tscircuit project config
├── tsconfig.json
├── tscircuit.config.json
└── README.md               # This file
```
