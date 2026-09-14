# Devais software stack decisions — 14 September 2026

Decisions for the firmware framework, host platform, BLE transport/codec and
prototype microphone. These resolve the open items in `hardware/PROTOTYPE.md`
("Firmware for the prototype") and the software gap recorded in
`docs/project-review-2026-09-10.md` ("Software and verification gaps").

## Summary

| # | Decision | Chosen | Rejected |
|---|---|---|---|
| D1 | Firmware framework | nRF Connect SDK (Zephyr) | Seeed Arduino core |
| D2 | Host platform | Android | — |
| D3 | BLE transport and codec | Staged: NUS/PCM, then a custom GATT service with ADPCM | L2CAP CoC now; Opus |
| D4 | Prototype microphone | M2 (PDM breakout at the product mic position) | M1 (XIAO on-board mic) |

## D1 — Firmware framework: nRF Connect SDK (Zephyr)

Chosen over the Seeed Arduino core. The custom board needs its own board
definition either way, and NCS is the framework that survives from the XIAO
prototype to the custom PCB. Prototype board target: `xiao_ble/nrf52840/sense`.

## D2 — Host platform: Android

The phone receives audio over BLE, calls the AI service, and returns playback
audio. This resolves the gap recorded in `docs/project-review-2026-09-10.md`
under "Software and verification gaps", where no host platform was chosen.

## D3 — BLE transport and codec: staged

Nordic UART Service (NUS) is itself a custom GATT service: a TX notify
characteristic plus an RX write-without-response characteristic. The real
choice is three-way, not two-way: NUS, a purpose-built GATT service, or L2CAP
connection-oriented channels (CoC).

### Stage 1 — bench prototype

NUS, carrying raw 16 kHz/16-bit mono PCM (256 kbps), 2M PHY.

Rationale: the Zephyr `peripheral_uart` sample and Nordic's Android BLE
library both already exist, and traffic is inspectable live with the nRF
Connect phone app. This stage proves the capture-to-transfer-to-AI-to-playback
path, not efficiency.

### Stage 2 — product

A purpose-built GATT service (audio-frame notify characteristic, control
write characteristic, state notify characteristic, standard Battery Service)
carrying IMA ADPCM at 4:1 (64 kbps).

Rationale: ADPCM costs roughly 150 lines of C and negligible CPU, and 64 kbps
keeps the link working on a phone that refuses 2M PHY. The frame format
carries a codec-ID byte so a lower-bitrate codec can replace ADPCM without a
protocol change.

### Rejected for now

- **L2CAP CoC.** Solves a throughput problem that does not exist at 64 kbps,
  requires Android 10 or later (`createInsecureL2capChannel`, API 29), and is
  not inspectable with the nRF Connect app.
- **Opus.** Estimated to cost more power to encode on the nRF52840 than the
  reduced radio duty cycle saves at this bitrate, plus tens of KB of RAM and
  over 100 KB of flash.
- **liblc3** (Google, Apache-2.0) is the candidate if a lower bitrate is
  later needed; it is estimated to be substantially cheaper to encode than
  Opus.

### Constraints behind the decision

- Push-to-talk is half-duplex and latency-tolerant: peak demand is 256 kbps
  in one direction, and a few hundred ms of buffering is acceptable.
- Android exposes no direct connection-interval control, only
  `CONNECTION_PRIORITY_HIGH`, typically 11.25 ms.
- With ATT MTU 247, a notification carries 244 payload bytes.
- Packets per connection event — typically 4 to 6, phone-dependent — dominates
  real throughput.
- Sustained throughput, device-dependent and **not yet measured**: estimated
  150–350 kbps on 1M PHY with DLE, estimated 400–900 kbps on 2M PHY with DLE.

### Open measurement gating Stage 1

Confirm the target Android phones negotiate 2M PHY, and record the achieved
packets per connection event, using the nRF Connect throughput sample.

## D4 — Prototype microphone: M2

A PDM microphone breakout (Adafruit 3492, MP34DT01, 16.5 x 11 mm) in an
enlarged seat at the existing bottom-front mic opening, wired to D6 and D7 as
PDM CLK and DATA.

Chosen over M1 (the XIAO's on-board microphone) so the prototype tests the
product's real mic position and acoustics. Known costs: two pins, and the PDM
clock runs on a low-frequency pad. M1 and M2 are defined in
`hardware/PROTOTYPE.md`.
