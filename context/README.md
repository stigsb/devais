# Context Files for AI Agents

## Index

Full assembly prototype: see `cad/ASSEMBLY.md` for the PCB, components, harnesses,
mounting pieces and fit checks. Its exports are in `output/full-assembly/`.

Latest enclosure revision (2026-09-11): diagonal pin/socket joint and chassis mounts;
see `output/README.md`. `context/enclosure-spec.md` marks its older content as
historical; `context/enclosure-work.md` was rewritten to the current state. Root
`output/` is the current export destination.

**When working on this project, read these files in `context/` for technical details:**

**Additional Documentation:** The `docs/` folder contains supplementary documentation.

### `context/enclosure-spec.md`
**Read when:** Implementing or modifying the DevAIs enclosure design.

**Contains:**
- Reference image analysis with precise dimensions and component positions
- Complete implementation plan with step-by-step changes required
- Octagon geometry calculations and battery fit verification
- CadQuery coordinate system guidelines and workplane selection rules
- Component orientation details (USB-C, buttons, LEDs, microphone, speaker)

### `context/enclosure-work.md`
**Read when:** Resuming work on the enclosure or checking its current parameters.

**Contains:**
- Octagon geometry and the seam position
- Every opening with its size and position, and the internal mount envelopes
- Commands to generate and preview, and what the generator checks
- Outstanding work
- CadQuery techniques the model depends on, and the decisions behind them

## Index Updates

This file must be updated when `context/*.md` files are added, modified or deleted.

Entries should follow this template:

```markdown
### `context/lowercased-name.md`
**Read when:** (single sentence describing when to read)

**Contains:**
- Short list of the
- kinds of information
- the file contains
```
