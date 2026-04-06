# Vertical Main Board Architecture

## Decision
Single 140x28mm PCB mounted vertically in the chassis (right) half of the enclosure,
along the inner surface of the right wall. Replaces the previous horizontal 28x65mm
board + separate USB-C daughter board.

## Board Orientation
- Board runs along the Z axis (enclosure height), from Z~5mm to Z~145mm
- Board width (28mm) spans the interior cross-section
- Front side faces inward (toward battery / enclosure center)
- Back side faces the right enclosure wall

## Back-Side Components (through enclosure wall)
| Component | Enclosure Z | Function |
|-----------|------------|----------|
| USB-C receptacle | 31mm | Charging port, mid-mount through wall |
| Power switch | 44mm | Power/mode button through 8mm hole |
| PTT switch | 105mm | Push-to-talk, actuated by big orange button |

## Front-Side Zones
- Z=5-65mm (battery zone): Power management (charger, regulator, caps).
  Max component height ~3.4mm (SOT-223, SOIC-8, passives OK).
- Z=65-145mm (above battery): Full depth available. MCU, amp, audio
  connectors, LED connector, decoupling caps.

## Connectors (JST, front side)
- J_BAT: 2-pin, bottom of board (near battery terminals)
- J_SPK: 2-pin, upper section
- J_LED: 3-pin, near top (LED board at top of enclosure)
- J_MIC: 5-pin, mid-upper section (mic is at bottom of front face,
  cable routes internally)

## Mounting
- Screw-mounted to chassis half via M2 holes at corners + mid-board
- Board standoffs set the distance from wall to accommodate back-side components

## What This Eliminates
- Separate USB-C daughter board (was: JST + CC resistor board)
- Separate PTT button board
- SW_PTT and SW_PWR as on-board tactile switches (replaced by through-wall switches)
