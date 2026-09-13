# Devais project review — 10 September 2026

Nothing has been purchased or printed. Treat the component list as provisional.
The repository contains useful CAD and circuit sketches, but it does not yet
describe a mechanically assembled, electrically verified device.

## Verification and environment

The project now selects the already-installed Python 3.14.6 and requires
CadQuery 2.8. The regenerated lockfile selects OpenCascade bindings 7.9.3.1.1
and VTK 9.6.2. All four STL exports completed; the three existing CAD smoke tests
passed, with deprecation and test-return warnings. The lockfile check and
`git diff --check` passed.

The Python 3.14/CadQuery 2.8 rebuild reproduced the five right-shell solids and
886.995 mm³ board/shell intersection reported below. Both shell previews rendered
successfully with host display access and were visually inspected. The earlier
sandboxed renderer failed while enumerating macOS screens; changing Python alone
has not been demonstrated to fix that display-access problem. Trimesh reports
both regenerated shell meshes as non-watertight, so successful exports still do
not establish print readiness.

Fresh review exports are in `/private/tmp/devais-review-py314/cad/output/`.
Existing project STL files were not replaced. The PCB CLI was unavailable and
the PCB was not rebuilt; circuit.json findings below refer to its cached output.

## What to keep

Keep the push-to-talk interaction, parametric CAD, and the general octagonal
shape as a starting point. The nRF52840 remains a candidate for a phone-connected
device. Its choice should follow an audio and BLE experiment, rather than the
unverified battery-life comparisons in the README.

The current source describes a 40 × 40 × 150 mm enclosure with 1.6 mm walls,
and a 36 × 140 mm main PCB. Older documents describe 30 mm or 40 mm enclosures,
2.5 mm walls, horizontal boards, and 28 mm wide vertical boards. Use
`cad/enclosure.py` and `hardware/pcb/index.circuit.tsx` when investigating the
current design. The Python circuit-synth files are a separate, older design.

## PCB mounting: confirmed defects

1. **The PCB intersects the enclosure.** The bosses put its wall-facing surface
   at X=16.4 mm. Before accounting for corner fillets, the inner chamfer obeys
   `X + abs(Y) <= 30.18985 mm`. Only 27.5797 mm of width is available there,
   versus the board's 36 mm. A 36 mm board needs that surface at X<=12.18985 mm,
   before adding assembly clearance. Simply counting the cavity's central width
   misses this restriction.
2. **Four bosses float in the button opening.** A fresh CadQuery 2.7 build
   produced five solids for the right shell: the shell plus four disconnected
   bosses at Z=97 and 115 mm, Y=±10 mm. Each floating boss is about 34.73 mm³.
   Their intended supporting wall has already been removed for the PTT opening.
3. **Screw pilots go through the exterior.** `add_pcb_mounting_bosses()` drills
   through the full standoff and wall. Screw length and engagement need an
   explicit design; the current geometry does not provide blind holes.
4. **There is no complete mechanical assembly model.** Board thickness, actual
   component bodies, connectors, screw heads, cable bends, and insertion paths
   are not checked together. The cached circuit describes a 1.4 mm PCB; enclosure
   comments also refer to a mid-mount connector for a 1.6 mm board.

For the intersection check, a 36 × 140 × 1.4 mm board envelope occupied
X=15.0..16.4, Y=-18..18, Z=5..145. Its intersection with the unsplit shell was
approximately 887 mm³. This is a board-envelope check, not a populated-board
clearance validation.

## Enclosure and assembly

The current X=0 left/right split cuts through the speaker grille. The battery
cradle **and contacts** are added to the left cover, while the PCB is on the
right. Thus battery wiring crosses between halves, contrary to the redesign
specification's claim that the cover is purely mechanical.

The snap mechanism needs replacement or substantial correction:

- The beams join the cover along their length; there is no relief that creates
  the described cantilever attached only at its root.
- The receiving pocket is cut to full hook depth over the entire beam length.
  The later shallow cut cannot restore the material needed for a retaining
  shoulder.
- A 1.3 mm groove centered in a 1.6 mm wall leaves nominal 0.15 mm skins on
  each side. These are not robust printed joint walls.
- Claimed opening-cycle lifetimes are not supported by tests.

The orange button is a shaped cap, without a complete retention, travel-stop,
return, and switch-actuation design. Speaker and LED board retention are also
missing. The microphone pocket uses the microphone package dimensions rather
than a selected breakout board's dimensions.

There is a coordinate error in the explanatory comments: an XZ workplane at
positive offset 20 starts at Y=-20, not Y=+20. The acoustic features are therefore
on the negative-Y face. The microphone pocket's negative extrusion from Y=-18.4
goes toward the cavity rather than into that wall; inspect and correct this when
designing the acoustic seal.

Battery contact geometry also needs a real purchased-part drawing. The nominal
69.5 mm platform-face spacing has 3 mm bosses protruding inward from both ends.
The metal contact surfaces and their spring travel cannot be inferred from the
platform spacing alone. The top pilot-hole cutter also does not traverse the
full downward-facing boss.

## Which enclosure split to try

After comparing cuts through the actual shell, my recommendation is an
**offset diagonal split running the full length**, with all component mounts on
the chassis and a passive cover. This supersedes the initial front/back split
and separate-carrier recommendation. It is a concept, not a completed redesign.

The study uses plane `X - Y = -4 mm`, parallel to Z, with chassis on the
`X - Y >= -4` side. This is a 2.83 mm perpendicular offset from a central
diagonal plane, making the chassis deeper. It keeps the actual acoustic face
(Y negative) and control face (X positive) together. The seams run through the
front-left and rear-right chamfers. All existing openings remain on the chassis;
both bare shell parts are valid single solids. Study outputs are in
`cad/output/split-study/`, without changing the production CAD source.

Mount the PCB, battery cradle and both contacts, speaker, microphone, LEDs, and
switches to this chassis. Components may occupy space inside the closed cover,
but must remain supported when it is removed. Use supports tied to intact walls
and a few board screws. A board around 24–26 mm wide remains a candidate near
the current wall position, subject to real component and clearance checks.

Replace the continuous locating grooves with two spaced pins and matching blind
round holes, perpendicular to the split plane. They constrain movement both
along the device and across the seam; their separation also resists rotation.
Add local mounting pads with sufficient material around the holes. Use screws
for closure: locating pins alone do not prevent the cover lifting off. Tune pin
diameter, socket clearance, and engagement with a short printed sample.

The candidate print orientation puts the front-right chassis chamfer and the
opposite cover chamfer on the bed, with cavities upward. The current button
frame extends about 2.5 mm beyond the chassis's intended bed face; trim its
envelope or make that bezel separate before treating this orientation as usable.
The study meshes still produce non-watertight warnings. Mounts, pin joints,
overhangs, and the final print orientations need further validation.

| Option | Benefit | Main cost |
| --- | --- | --- |
| Repair current left/right split | Least change; right-side controls remain together | Speaker seam, raised right face is a poor bed surface, joints and mounts still need redesign |
| Front/back shells + carrier | Whole acoustic face; independent electronics mounting; accessible assembly | One extra structural part; side controls must be designed around the seam |
| Offset diagonal chassis + cover | Both active faces remain whole; all mounts on one part | Button bezel needs a printable envelope; new chassis mounts and pin pads required |
| Tube + removable end cap + sliding carrier | Few long exterior seams | Harder insertion and servicing; side ports/buttons can prevent sliding assembly |

Start with screws rather than fatigue-sensitive snaps. Print a short mounting
and joint sample before a full enclosure. Slicer inspection must establish
supports and bridging; the current documentation's assertion that both halves
need no supports is not evidence. Prusa specifically recommends considering
orientation, overhangs, bed-facing fillets, and splitting together in its
[printing design guidance](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135).

## Electrical issues before ordering a PCB

**Footprints are placeholders.** The USB receptacle is represented by `soic8`,
the XIAO by `dip14`, and the Omron PTT microswitch by `pinrow3`. Connectors
described as JST use generic pin rows. Supplier part numbers do not make those
land patterns correct. Board placement and routing must be redone around the
actual parts, including antenna keepout and mechanical connector orientation.

**The amplifier pin mapping is wrong.** The source assigns DIN to pin 4, BCLK
to pin 5, and LRCLK to pin 7. The MAX98357A TQFN datasheet assigns these to
pins 1, 16, and 14 respectively. It also requires both supply pins 7 and 8;
the source uses pin 7 for LRCLK. Recheck the entire map and exposed-pad footprint
against the [manufacturer datasheet, page 15](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf).

**The LED supply has no power source.** `VDD_LED` connects only the connector's
supply pin and the N-channel MOSFET drain. The source and LED ground both connect
to ground. Turning that transistor on pulls the supposed supply down; it does
not implement the low-side switching described in the README.

**The audio bus is not a straightforward compatible pairing.** The INMP441
requires 64 clocks per stereo frame. The nRF52840's native I²S master generates
twice the configured sample width, with supported widths 8, 16, and 24 bits.
That gives at most 48 clocks. A deliberate alternative clocking arrangement
would be needed to retain this microphone. With no parts purchased, investigate
a PDM microphone instead; the XIAO nRF52840 Sense includes one, which is useful
for an early bench experiment but does not automatically satisfy final acoustic
placement requirements. Sources: [TDK microphone datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf),
[Nordic I²S specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/i2s.html),
[Seeed board documentation](https://wiki.seeedstudio.com/XIAO_BLE/).

**Power needs a fresh design review.** The AMS1117 is fed directly from VBAT.
Its published dropout and quiescent-current characteristics are unsuitable for
treating this as an efficient regulated 3.3 V supply across a cell's discharge
range. The manufacturer's [electrical table, mirrored here](https://www.rlocman.es/datasheet/pdf.html?di=102481&p=2)
lists 5 mA typical quiescent current and 1.1 V typical dropout at 0.8 A; dropout
depends on load. The XIAO already has onboard regulation and charging, so choose
one intentional power architecture. Review external 3.3 V drive while USB powers
the module, load sharing during charge, amplifier peak current, protection,
thermal dissipation, and shutdown behavior. The schematic ties amplifier
SD_MODE high, preventing firmware from selecting its lowest-power shutdown.

The cached circuit.json contains four trace errors, including trace-to-pad
clearance errors, as well as pin warnings. It is not a fresh build result and
must not be treated as fabrication approval. There is no reason to spend effort
polishing those routes before correcting parts and nets.

## Software and verification gaps

There is no firmware or phone companion implementation in the inspected project,
despite the README's illustrative firmware directory. BLE is only a link: the
phone/computer still needs to receive audio, invoke the AI service, and return
playback. Uncompressed 16 kHz, 16-bit mono audio is 256 kbit/s before protocol
overhead. Demonstrate the intended phone platform, BLE transport, buffering,
latency, and reconnection rather than assuming a generic Bluetooth audio profile.

`cad/test_cadquery.py` is a timing smoke test, not an enclosure test. The assembly
diagram generator draws component bounds from pads and combines layers; it does
not verify physical component bodies. `pcb-export` does not invoke that custom
generator and ignores individual export failures. These gaps can make generated
pictures look more authoritative than they are.

## Recommended next steps

1. Choose the host platform and prove push-to-talk capture, transfer, response,
   and playback on development boards. Resolve microphone/clock compatibility.
2. Select exact physical parts and one power architecture. Measure active and
   sleeping current; replace unsupported battery-life claims with a duty-cycle
   budget.
3. Model the complete component envelopes and a carrier. Check collisions,
   screw access, connector insertion, battery replacement, and button travel.
4. Print joint/mount samples, then an unpopulated enclosure and carrier. Compare
   front/back shells with the repaired current split if ergonomics remain unclear.
5. Design the custom PCB using verified footprints, shared mounting coordinates,
   and populated-board clearance checks. Route only after placement is settled.

Better models can help with this work, especially by connecting electrical and
mechanical evidence. The practical improvement is making each stage produce
testable results: correct nets, real footprints, connected solids, collision-free
assemblies, and measured behavior.
