# Devais Project Context

## Coding Agent Instructions

**IMPORTANT:** When working with 3D models, CAD files, or CadQuery code in this project, consult the **CAD Modeller Skill** guide located at `docs/gemini_cad_skill.md`. This guide provides specialized CAD modeling capabilities and best practices for:
- Creating or modifying CadQuery scripts
- Generating 3D models for enclosures or components
- Working with STL files
- Design iterations of mechanical parts

## Project Purpose

Devais is a handheld AI assistant device designed to solve a fundamental UX problem with voice-activated AI: apps that respond to hesitation during speech. By implementing a push-to-talk interface (walkie-talkie style), users have intentional control over when the AI is listening and responding.

## Design Constraints

### Physical
- **Target dimensions:** ~30x30x150mm (stick-shaped)
- **Form factor goal:** Easy to hold, pocket-portable
- **Manufacturing:** 3D printed enclosure (Prusa MK3S available)

### Electrical
- **Battery:** Single 18650 Li-ion cell
- **Power budget:** Optimized for multi-day battery life
- **Charging:** USB-C port

### Component Selection Rationale

**nRF52840 vs ESP32:**
- Chosen for superior battery efficiency
- 20.8 days idle (vs 8.3 days ESP32-C3)
- 5 days continuous streaming (vs 27 hours ESP32-C3)
- BLE low-energy connectivity

**I2S Audio Architecture:**
- More efficient than analog audio
- Better audio quality
- Shared clock signals, separate data lines
- INMP441 microphone: Industry-standard MEMS I2S mic
- MAX98357A amplifier: Efficient Class D design

## Technical Specifications

### Pin Assignments (nRF52840)

**I2S Audio Bus:**
- SCK (Bit Clock): Shared between mic and amp
- WS (Word Select): Shared between mic and amp
- SD_IN (Mic Data): From INMP441
- SD_OUT (Amp Data): To MAX98357A

**Control:**
- Push-to-talk button: GPIO with interrupt
- Power button: GPIO with interrupt
- Status LEDs: 2-3 GPIOs

**Power:**
- USB-C: VBUS detection + charging circuit
- Battery: Direct connection with protection

### Power Consumption Estimates

**Idle (BLE connected):** ~50μA average
**Active streaming:** ~20mA average
**Speaker output:** Additional 200-500mA peaks

### Current Development Phase

**Completed:**
- Component selection and sourcing research
- Power consumption analysis
- Wiring diagram with pin assignments
- Battery life calculations

**Current Focus:**
- 3D enclosure design using CadQuery
- Programmatic component layout planning
- Wire routing channel design

**Next Steps:**
- PCB design or perfboard layout
- Firmware development (BLE + I2S audio)
- Prototype assembly and testing

## CAD Design Approach

### Tool: CadQuery (Python-based)

**Why programmatic CAD:**
- Enables iterative design through parameter adjustment
- AI Coding Agents help generate/modify layouts
- Programmatically calculate clearances and positions
- Version control friendly (text-based)

**Key Design Elements:**
1. Battery compartment (18650 holder)
2. Component mounting features
3. Wire routing channels
4. Button/LED cutouts
5. Speaker/mic acoustic chambers
6. USB-C port opening
7. Assembly features (clips, screws)

### Component Dimensions Reference

- **18650 battery:** 18.6mm diameter × 65mm length
- **XIAO nRF52840:** 21×17.5mm
- **INMP441:** Small breakout board (~15×12mm)
- **MAX98357A:** Small breakout board (~16×16mm)
- **Speaker:** Compact, ~20-28mm diameter
- **Buttons:** 6×6mm tactile switches
- **LEDs:** 3mm or 5mm through-hole

## Development Philosophy

- **Battery efficiency first:** Every design decision considers power impact
- **Intentional interaction:** Push-to-talk over always-listening
- **Iterative design:** Programmatic CAD enables rapid parameter adjustment
- **Modular approach:** Separate concerns (power, audio, control, enclosure)

## Working with This Project

### For CAD Work:
- Component positions defined parametrically
- All dimensions in millimeters
- Export to STL for 3D printing
- Consider 3D printer tolerances (±0.2mm typical)

### For Firmware:
- Platform: Arduino/nRF52840
- Key libraries: I2S audio, BLE, power management
- Audio format: 16kHz/16-bit typical for voice

### For Assembly:
- 3D printed parts designed for press-fit or screw assembly
- Wire management critical in narrow form factor
- Test points for debugging

## Project Location

Trondheim, Norway - influences component sourcing and shipping considerations.
