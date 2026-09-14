"""PCB placement study, NOT a routed circuit or a fabrication source.

Run from the repository root: .venv/bin/python hardware/pcb/design.py
Imports the current enclosure dimensions; exports to output/pcb-design/.
Boxes reserve space for component groups, including assembly allowance.
They do not substitute for manufacturer footprints or connector STEP models.
"""

import math
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont

from cad import enclosure as e

# All coordinates/dimensions are mm. Board u = enclosure Y; v = Z - 75.
# Component height extends inward from X=9.9. None are on the wall side.
# Raytac module: manufacturer approval sheet, version L, pp. 7 and 11.
# JST SH: eSH.pdf, p. 3: side-entry body height 2.9, depth 4.25+0.7.
# Group envelopes include passives/routing space; they are design allocations.
# cad/assembly.py overrides four of these coordinates for the mechanical model:
#   J_USB  Z 31 -> 25   (clears the Z = 16 screw heads)
#   J_LED  Z 123 -> 124
#   J_NTC  u -6 -> -7
#   J_PTT  u 6 -> 4.5
# name, board u, enclosure Z, width, length, height, category
PLACEMENTS = [
    ("J_MIC", -4, 21, 6.5, 5.5, 3.0, "connector"),
    # The 10.5 mm wide 8-way J_USB envelope sits at u >= 6.75 to clear the cell tie at Z = 27.
    ("J_USB", 7, 31, 10.5, 5.5, 3.0, "connector"),
    ("J_PWR", 0, 44, 4.5, 5.5, 3.0, "connector"),
    ("CHARGE / CC", 0, 57, 16, 14, 1.5, "power"),
    ("3V3 BUCK-BOOST", 0, 79, 14, 10, 2.0, "power"),
    ("CELL PROTECTION", 0, 88, 10, 8, 1.5, "power"),
    ("J_BAT", 3, 101, 9, 8, 8, "connector"),
    ("J_NTC", -6, 103, 4.5, 5.5, 3.0, "connector"),
    ("J_PTT", 6, 110, 4.5, 5.5, 3.0, "connector"),
    ("AMP + J_SPK", -3, 112, 9, 10, 3.0, "audio"),
    # The 9.5 mm wide 7-way J_LED envelope reaches the board edge, so the module
    # and the SWD pads sit off centre to clear it.
    ("J_LED", -8, 123, 9.5, 5.5, 3.0, "connector"),
    ("SWD PADS", 10.25, 123, 5, 6, 0.1, "debug"),
    ("MDBT50Q-1MV2", 2.25, 130.25, 10.5, 15.5, 2.05, "radio"),
]
SCREW_STATIONS = (16, 38, 115)  # Six screws; all ten existing holes retained.
HEAD_DIAMETER, HEAD_HEIGHT = 4.5, 1.8  # Envelope, confirm purchased M2 screws.
ANTENNA_KEEP_OUT_Z = 134.2  # 3.8 mm strip; detailed footprint also needs central notch.
OUT = Path(__file__).resolve().parents[2] / "output" / "pcb-design"
COLORS = {
    "connector": "#edba65",
    "power": "#e99991",
    "audio": "#94cca4",
    "radio": "#89bde5",
    "debug": "#d4c4ec",
}


def component_box(part):
    _, u, z, w, length, height, _ = part
    return (
        cq.Workplane("XY")
        .box(height, w, length)
        .translate((e.PCB_FACE_X - e.PCB_THICKNESS - height / 2, u, z))
    )


def board_with_holes():
    board = e.board_envelope()
    for u, v in e.PCB_MOUNTING_HOLES:
        tool = cq.Workplane("YZ", origin=(e.PCB_FACE_X + 1, u, v + e.PCB_Y_OFFSET))
        board = board.cut(tool.circle(1.1).extrude(-5))
    return board


def check(chassis, cover, board, parts):
    e.check_assembly(chassis, cover)
    assert board.val().isValid() and board.solids().size() == 1
    bb = board.val().BoundingBox()
    assert abs(bb.ylen - e.PCB_WIDTH) < 1e-6
    assert abs(bb.zlen - e.PCB_HEIGHT) < 1e-6
    cell = e.battery_envelope()
    speaker_z = e.DEVICE_HEIGHT - e.SPEAKER_TOP_OFFSET - e.SPEAKER_DIAMETER / 2
    speaker = (
        cq.Workplane("XZ", origin=(0, -18.3, speaker_z))
        .circle(e.SPEAKER_BODY_DIAMETER / 2)
        .extrude(-e.SPEAKER_BODY_DEPTH)
    )
    peripherals = [("speaker", speaker)]
    for name, x, z, w, h in [
        (
            "mic board",
            e.MIC_X_OFFSET,
            e.MIC_BOTTOM_OFFSET,
            e.MIC_BOARD_WIDTH,
            e.MIC_BOARD_HEIGHT,
        ),
        (
            "LED board",
            e.LED_BOARD_X,
            e.DEVICE_HEIGHT - e.LED_TOP_OFFSET,
            e.LED_BOARD_WIDTH,
            e.LED_BOARD_HEIGHT,
        ),
    ]:
        body = (
            cq.Workplane("XY")
            .box(w, e.AUDIO_BOARD_THICKNESS, h)
            .translate((x, -17 + e.AUDIO_BOARD_THICKNESS / 2, z))
        )
        peripherals.append((name, body))
    heads = []
    for u, v in e.PCB_MOUNTING_HOLES:
        z = v + e.PCB_Y_OFFSET
        if z in SCREW_STATIONS:
            head = cq.Workplane("YZ", origin=(e.PCB_FACE_X - e.PCB_THICKNESS, u, z))
            heads.append(
                (f"screw_{u}_{z}", head.circle(HEAD_DIAMETER / 2).extrude(-HEAD_HEIGHT))
            )
    assert len(heads) == 6
    for p, (_, body) in zip(PLACEMENTS, parts):
        name, u, z, w, length, height, category = p
        assert abs(u) + w / 2 <= e.PCB_WIDTH / 2, f"{name}: off board width"
        assert (
            abs(z - e.PCB_Y_OFFSET) + length / 2 <= e.PCB_HEIGHT / 2
        ), f"{name}: off board length"
        if category != "radio":
            assert z + length / 2 < ANTENNA_KEEP_OUT_Z, f"{name}: antenna keepout"
        # Keep components away from both occupied and unused screw holes.
        for hu, hv in e.PCB_MOUNTING_HOLES:
            dx = max(abs(hu - u) - w / 2, 0)
            dz = max(abs(hv + e.PCB_Y_OFFSET - z) - length / 2, 0)
            assert math.hypot(dx, dz) >= HEAD_DIAMETER / 2, f"{name}: screw clearance"
    for name, body in parts + heads:
        for other_name, other in [
            ("chassis", chassis),
            ("cover", cover),
            ("cell", cell),
        ] + peripherals:
            volume = body.intersect(other).val().Volume()
            assert volume < 1e-5, f"{name} intersects {other_name}: {volume:.4f} mm3"
    for (name, a), (other_name, b) in combinations(parts + heads, 2):
        assert a.intersect(b).val().Volume() < 1e-5, f"{name} intersects {other_name}"
    for distance in (0.5, 2, 4, 10, 25, 50):
        moved = cover.translate((-distance / math.sqrt(2), distance / math.sqrt(2), 0))
        for name, body in (
            parts + heads + [("board", board), ("cell", cell)] + peripherals
        ):
            assert body.intersect(moved).val().Volume() < 1e-5, f"Cover catches {name}"
    return heads, peripherals


def draw_placement():
    im = Image.new("RGB", (1100, 1560), "#f5f4ef")
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 21)
    small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 17)
    title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 29)
    scale, left, top = 9, 405, 140

    def xy(u, z):
        return left + (u + e.PCB_WIDTH / 2) * scale, top + (138 - z) * scale

    d.text((40, 30), "Devais PCB — placement proposal", font=title, fill="#213b3b")
    d.text(
        (40, 73),
        "26 × 126 × 1.6 mm • inward face • dimensions in mm",
        font=font,
        fill="#213b3b",
    )
    d.rectangle([xy(-13, 138), xy(13, 12)], fill="#dbece1", outline="#355e49", width=3)
    d.rectangle([xy(-13, 138), xy(13, ANTENNA_KEEP_OUT_Z)], fill="#f4dca6")
    # Battery projection is deliberately only an outline: it is behind the parts.
    d.rectangle([xy(-9.3, 85), xy(9.3, 20)], outline="#a2a5a9", width=2)
    d.text((690, 220), "Top 3.8 mm: no copper", font=font, fill="#6a4917")
    d.text((690, 247), "No top mounting screws", font=font, fill="#6a4917")
    for u, v in e.PCB_MOUNTING_HOLES:
        z = v + e.PCB_Y_OFFSET
        x, y = xy(u, z)
        r = HEAD_DIAMETER / 2 * scale
        d.ellipse((x - r, y - r, x + r, y + r), outline="#61776b", width=1)
        r = 1.1 * scale
        d.ellipse(
            (x - r, y - r, x + r, y + r),
            fill="#46575b" if z in SCREW_STATIONS else "#f5f4ef",
            outline="#46575b",
            width=2,
        )
    labels = {
        "J_MIC": (45, 1150),
        "J_USB": (690, 1090),
        "J_PWR": (690, 975),
        "CHARGE / CC": (45, 875),
        "3V3 BUCK-BOOST": (690, 720),
        "CELL PROTECTION": (45, 620),
        "J_BAT": (690, 535),
        "J_NTC": (45, 540),
        "J_PTT": (690, 455),
        "AMP + J_SPK": (45, 440),
        "J_LED": (45, 330),
        "SWD PADS": (690, 355),
        "MDBT50Q-1MV2": (45, 200),
    }
    for name, u, z, w, length, height, category in PLACEMENTS:
        a, b = xy(u - w / 2, z + length / 2), xy(u + w / 2, z - length / 2)
        d.rectangle([a, b], fill=COLORS[category], outline="#4b575d", width=2)
        x, y = xy(u, z)
        tx, ty = labels[name]
        endpoint = (tx + 285 if tx < left else tx - 12, ty + 12)
        d.line([(x, y), endpoint], fill="#748079", width=1)
        d.text((tx, ty), name, font=font, fill="#203534")
        d.text(
            (tx, ty + 27),
            f"u {u:g}, Z {z:g}; h ≤ {height:g}",
            font=small,
            fill="#546560",
        )
    d.text(
        (40, 1320),
        "Dark holes: six M2 screws at Z 16, 38 and 115; u ±10.",
        font=font,
        fill="#213b3b",
    )
    d.text(
        (40, 1352),
        "All ten holes match the existing chassis. Pale rectangle: cell projection, Z 20–85.",
        font=font,
        fill="#213b3b",
    )
    d.text(
        (40, 1384),
        "Battery-to-board gap 3.6 mm; low connectors reserve 3.0 mm height.",
        font=font,
        fill="#213b3b",
    )
    d.text(
        (40, 1440),
        "STUDY ONLY — group envelopes, not footprints or routed copper.",
        font=title,
        fill="#9a493d",
    )
    d.text(
        (40, 1482),
        "Cable bends, USB carrier and button mechanisms still require detailed fit checks.",
        font=font,
        fill="#9a493d",
    )
    im.save(OUT / "placement.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chassis, cover = e.split_enclosure(e.build_enclosure())
    board = board_with_holes()
    parts = [(p[0], component_box(p)) for p in PLACEMENTS]
    heads, peripherals = check(chassis, cover, board, parts)
    assembly = cq.Assembly()
    for name, part, color in [
        ("chassis", chassis, "#b0bdcb"),
        ("board", board, "#588368"),
        ("cell", e.battery_envelope(), "#737fbc"),
    ]:
        assembly.add(part, name=name, color=cq.Color(color))
    for i, ((name, part), p) in enumerate(zip(parts, PLACEMENTS)):
        assembly.add(part, name=f"allocation_{i}", color=cq.Color(COLORS[p[-1]]))
    for i, (_, head) in enumerate(heads):
        assembly.add(head, name=f"screw_head_{i}", color=cq.Color("#9a9a9a"))
    for i, (_, part) in enumerate(peripherals):
        assembly.add(part, name=f"peripheral_{i}", color=cq.Color("#94cca4"))
    assembly.export(str(OUT / "placement.step"))
    # Viewing mesh only: separate component bodies, not one printable object.
    viewing = cq.Compound.makeCompound(
        [chassis.val(), board.val(), e.battery_envelope().val()]
        + [p.val() for _, p in parts + heads + peripherals]
    )
    # Face the open cavity toward the preview camera. STEP keeps enclosure axes.
    viewing = viewing.rotate((0, 0, 0), (0, 0, 1), 180)
    cq.exporters.export(viewing, str(OUT / "placement-view.stl"), tolerance=0.05)
    # Board-only print coupon: lay the broad face on Z=0.
    coupon = board.rotate((0, 0, 0), (0, 1, 0), 90)
    bb = coupon.val().BoundingBox()
    coupon = coupon.translate((-bb.center.x, -bb.center.y, -bb.zmin))
    e.export_stl(coupon, OUT / "board-fit.stl")
    draw_placement()
    print(
        "PASS: board, allocated parts, six screw heads, cell, shells and cover removal"
    )
    print(
        "Not checked: copper, exact parts, cables, USB carrier, button mechanics, RF or thermal behavior"
    )
    print(OUT)


if __name__ == "__main__":
    main()
