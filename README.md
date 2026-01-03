# Devais - Handheld AI Assistant Device

A battery-powered, pocket-sized AI assistant with a push-to-talk interface. Designed as a walkie-talkie style device that solves the common problem of AI apps responding to hesitation during speech.

## Overview

**Form Factor:** Stick-shaped handheld device (~30x30x150mm)  
**Power:** 18650 battery with USB-C charging  
**Interface:** Push-to-talk button, status LEDs, speaker and microphone  
**Connectivity:** Bluetooth Low Energy (nRF52840)

## Hardware Components

### Core Controller
- **Seeed XIAO nRF52840** - Ultra-low power microcontroller with BLE
  - Superior battery efficiency vs ESP32 alternatives
  - 20.8 days idle battery life (vs 8.3 days for ESP32-C3)
  - 5 days continuous audio streaming (vs 27 hours for ESP32-C3)

### Audio System (I2S Bus Architecture)
- **INMP441** - MEMS I2S microphone
- **MAX98357A** - I2S Class D amplifier
- Compact speaker
- Shared clock signals with separate data lines for efficiency

### User Interface
- Tactile push-to-talk button
- Power/mode button
- Status LEDs (power, connectivity, activity)

### Power
- 18650 Li-ion battery
- USB-C charging port
- Efficient power management optimized for audio streaming

## Project Structure

```
devais/
├── cad/              # 3D CAD models (CadQuery scripts)
├── firmware/         # nRF52840 firmware
├── docs/             # Documentation, wiring diagrams
├── hardware/         # PCB designs, schematics
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- uv (Python package manager)
- Prusa MK3S or compatible 3D printer

### Installation

```bash
# Clone the repository
git clone https://github.com/stigsb/devais.git
cd devais

# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### Running CAD Scripts

```bash
# Generate the enclosure model
python cad/enclosure.py

# Output will be in cad/output/ as STL files
```

## Design Principles

1. **Intentional Interaction** - Push-to-talk prevents accidental triggers and hesitation issues
2. **Battery Efficiency** - Component selection optimized for multi-day battery life
3. **Pocket Portability** - Narrow form factor fits comfortably in pocket or hand
4. **Programmatic CAD** - Python-based modeling enables iterative design and parameter adjustment

## Status

- [x] Component selection and power analysis
- [x] I2S audio architecture design
- [x] Wiring diagram and pin assignments
- [ ] 3D enclosure design (in progress)
- [ ] PCB layout
- [ ] Firmware development
- [ ] Prototype assembly

## Location

Trondheim, Norway

## License

TBD
