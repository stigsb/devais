# LED matrix daughterboard

**Status: deferred to V2.** V1 ships the existing two 3 mm LED openings. Nothing
here is on the V1 build path.

A higher-fidelity replacement for the 2x WS2812B-2020 indicator board, for
signalling the state of several concurrent agents. Background, part selection,
cost and the rejected alternatives are in
[`docs/led-indicator-research-2026-09-13.md`](../../docs/led-indicator-research-2026-09-13.md).

## upstream/

Third-party KiCad 7 design, taken as a starting point — not a devais board.

- Source: Arduino Forum, "Showcase: PCB for 8x8 matrix of WB2812B-2020"
  <https://forum.arduino.cc/t/showcase-pcb-for-8x8-matrix-of-wb2812b-2020/1154180>
- Licence: not stated by the author. Resolve before publishing a derived board.
- As drawn: 25.0 x 25.0 mm, 2 layers, 8x8 on a 3.0 mm pitch (21 mm LED field),
  64x `MR_LED:WS2812B2020`, 2x `MR_Connect:DS1024-1x3R0` 3-pin daisy-chain
  connectors, no decoupling capacitors.

## Required changes for devais

- **LED part:** WS2812B-2020-V6 (LCSC C52917434), not the V1.3 part the upstream
  footprint was drawn for. V6 is spec'd 3.3-5.3 V and <=1 uA idle, so it runs
  directly off the 18650 with no boost and needs no power gate. Verify the V6
  recommended land pattern against the upstream footprint before reuse.
- **Connector:** one 3-pin JST matching the existing J_LED cable (VDD_LED, GND,
  LED_DATA), replacing both DS1024 daisy-chain connectors.
- **Decoupling:** upstream has none. Add local capacitors.
- **Outline:** 25 mm is the enclosure's hard limit at the front flat face
  (`LONG_SIDE_LENGTH` ~= 24.9 mm). Shrinking the pitch to 2.5 mm gives a 20 mm
  field and working margin.

## Open questions

- Front-face split: the enclosure parts at X = 0 and the current LED openings sit
  entirely on the chassis half. A centred 25 mm board crosses the joint.
- Diffusion: at 2.5-3.0 mm pitch behind the 1.6 mm wall, per-pixel separation
  needs a grid insert. A plain window blends adjacent pixels into a blur.
- Brightness cap: 64 LEDs at full white is ~2.3 A. Firmware must limit global
  brightness.
