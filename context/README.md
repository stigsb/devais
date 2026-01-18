# Context Files for AI Agents

## Index

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
**Read when:** Resuming work on the enclosure or checking implementation status.

**Contains:**
- Current implementation progress and what's been accomplished
- Known issues and missing features with priority levels
- File structure and output locations
- Next session action items and validation tasks
- Key learnings from CadQuery limitations and design decisions

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
