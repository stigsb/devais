"""Generate clean assembly diagrams for the Devais PCB.

Reads component pad positions from the tscircuit circuit.json and produces
annotated SVG/PNG assembly guides with accurate component outlines.
"""

import json
import os
import subprocess

SCALE = 10  # pixels per mm
MARGIN = 120  # px margin for labels
PAD_MARGIN = 0.5  # mm extra around pad extents for outline

BG_COLOR = "#1a1a2e"
BOARD_COLOR = "#0f3460"
BOARD_STROKE = "#16213e"
PAD_COLOR = "#c4a35a"
HOLE_COLOR = "#333333"
HOLE_STROKE = "#666666"
LEADER_COLOR = "#666666"

COLORS = {
    "power":  "#e74c3c",
    "mcu":    "#3498db",
    "audio":  "#2ecc71",
    "ui":     "#f39c12",
    "misc":   "#95a5a6",
}


def subsystem_of(name):
    if name.startswith(("J_USB", "U_CHG", "U_REG", "R_CC", "R_PROG",
                        "C_USB", "C_REG", "C_BAT", "J_BAT")):
        return "power"
    if name.startswith("U_MCU") or name.startswith("C_MCU"):
        return "mcu"
    if name.startswith(("J_MIC", "J_AMP", "J_SPK", "C_MIC", "C_AMP")):
        return "audio"
    if name.startswith(("LED_", "R_L", "SW_", "R_PTT", "R_PWR")):
        return "ui"
    return "misc"


def human_value(comp):
    r = comp.get("resistance")
    c = comp.get("capacitance")
    color = comp.get("color")
    if r:
        v = float(r)
        if v >= 1000:
            return f"{v/1000:.0f}k"
        return f"{v:.0f}R"
    if c:
        v = float(c)
        if v >= 1e-6:
            return f"{v*1e6:.0f}uF"
        if v >= 1e-9:
            return f"{v*1e9:.0f}nF"
        return f"{v*1e12:.0f}pF"
    if color:
        return color
    return ""


def generate_assembly_svg(circuit_json_path, output_path, title="Top Side Assembly"):
    with open(circuit_json_path) as f:
        data = json.load(f)

    # Read board dimensions from circuit.json
    boards = [e for e in data if e.get("type") == "pcb_board"]
    if boards:
        BOARD_W = float(boards[0].get("width", 28))
        BOARD_H = float(boards[0].get("height", 72))
    else:
        BOARD_W, BOARD_H = 28.0, 72.0

    CANVAS_W = int(BOARD_W * SCALE + 2 * MARGIN)
    CANVAS_H = int(BOARD_H * SCALE + 2 * MARGIN)

    def board_to_svg(x_mm, y_mm):
        sx = MARGIN + (x_mm + BOARD_W / 2) * SCALE
        sy = MARGIN + (BOARD_H / 2 - y_mm) * SCALE
        return sx, sy

    sources = [e for e in data if e.get("type") == "source_component"]
    pcb_comps = [e for e in data if e.get("type") == "pcb_component"]
    smt_pads = [e for e in data if e.get("type") == "pcb_smtpad"]
    plated_holes = [e for e in data if e.get("type") == "pcb_plated_hole"]
    holes = [e for e in data if e.get("type") == "pcb_hole"]

    # Build component data with real pad extents
    parts = []
    for pc in pcb_comps:
        pcb_id = pc.get("pcb_component_id")
        sid = pc.get("source_component_id")
        src = next((s for s in sources if s.get("source_component_id") == sid), {})
        name = src.get("name", "?")

        # Collect all pad positions for this component
        comp_pads = [p for p in smt_pads if p.get("pcb_component_id") == pcb_id]
        comp_pth = [p for p in plated_holes if p.get("pcb_component_id") == pcb_id]

        pad_points = []
        for p in comp_pads:
            px, py = p.get("x", 0), p.get("y", 0)
            pw = p.get("width", 0.6)
            ph = p.get("height", 0.6)
            pad_points.append({"x": px, "y": py, "w": pw, "h": ph})
        for p in comp_pth:
            px, py = p.get("x", 0), p.get("y", 0)
            d = p.get("outer_diameter", 1.6)
            pad_points.append({"x": px, "y": py, "w": d, "h": d})

        if not pad_points:
            continue

        # Compute bounding box from pad edges (not just centers)
        min_x = min(p["x"] - p["w"] / 2 for p in pad_points)
        max_x = max(p["x"] + p["w"] / 2 for p in pad_points)
        min_y = min(p["y"] - p["h"] / 2 for p in pad_points)
        max_y = max(p["y"] + p["h"] / 2 for p in pad_points)

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        w = max_x - min_x + 2 * PAD_MARGIN
        h = max_y - min_y + 2 * PAD_MARGIN

        val = human_value(src)
        sub = subsystem_of(name)
        parts.append({
            "name": name, "cx": cx, "cy": cy,
            "w": w, "h": h, "val": val, "sub": sub,
            "pad_count": len(pad_points), "pads": pad_points,
        })

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{CANVAS_W}" height="{CANVAS_H}" '
                 f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">')
    lines.append("<defs>")
    lines.append('<style type="text/css">')
    lines.append(f"  .board {{ fill: {BOARD_COLOR}; stroke: {BOARD_STROKE}; stroke-width: 2; }}")
    lines.append(f"  .comp {{ fill: none; stroke-width: 1.2; }}")
    lines.append(f"  .pad {{ fill: {PAD_COLOR}; opacity: 0.7; }}")
    lines.append(f"  .hole {{ fill: {HOLE_COLOR}; stroke: {HOLE_STROKE}; stroke-width: 1.5; }}")
    lines.append(f"  .leader {{ stroke: {LEADER_COLOR}; stroke-width: 0.6; stroke-dasharray: 2,2; }}")
    lines.append(f"  .lbl {{ font-family: 'SF Mono','Menlo',monospace; font-size: 9px; }}")
    lines.append(f"  .title {{ font-family: 'SF Mono','Menlo',monospace; font-size: 14px; "
                 f"font-weight: bold; fill: #fff; }}")
    lines.append(f"  .legend {{ font-family: 'SF Mono','Menlo',monospace; font-size: 10px; fill: #fff; }}")
    lines.append("</style>")
    lines.append("</defs>")

    # Background
    lines.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" fill="{BG_COLOR}" />')

    # Title
    lines.append(f'<text x="{CANVAS_W//2}" y="18" text-anchor="middle" class="title">'
                 f'{title} — DevAIs PCB ({BOARD_W:.0f}x{BOARD_H:.0f}mm)</text>')

    # Board outline
    bx, by = MARGIN, MARGIN
    lines.append(f'<rect x="{bx}" y="{by}" width="{BOARD_W*SCALE}" '
                 f'height="{BOARD_H*SCALE}" class="board" rx="3" ry="3" />')

    # Mounting holes
    for h in holes:
        hx, hy = h.get("x", 0), h.get("y", 0)
        hr = h.get("hole_diameter", 2.2) / 2 * SCALE
        sx, sy = board_to_svg(hx, hy)
        lines.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{hr:.1f}" class="hole" />')

    # Draw pads and component outlines
    for p in parts:
        color = COLORS[p["sub"]]

        # Draw individual pads
        for pad in p["pads"]:
            px, py = board_to_svg(pad["x"], pad["y"])
            pw = pad["w"] * SCALE
            ph = pad["h"] * SCALE
            lines.append(f'<rect x="{px - pw/2:.1f}" y="{py - ph/2:.1f}" '
                         f'width="{pw:.1f}" height="{ph:.1f}" class="pad" rx="0.5" />')

        # Component outline (bounding box around all pads)
        sx, sy = board_to_svg(p["cx"], p["cy"])
        ow = p["w"] * SCALE
        oh = p["h"] * SCALE
        lines.append(f'<rect x="{sx - ow/2:.1f}" y="{sy - oh/2:.1f}" '
                     f'width="{ow:.1f}" height="{oh:.1f}" '
                     f'class="comp" stroke="{color}" rx="2" />')

        # Pin 1 indicator (small filled circle at first pad)
        if p["pads"]:
            p1 = p["pads"][0]
            p1x, p1y = board_to_svg(p1["x"], p1["y"])
            lines.append(f'<circle cx="{p1x:.1f}" cy="{p1y:.1f}" r="2" '
                         f'fill="{color}" opacity="0.8" />')

    # Labels — assign to left or right column based on component X position
    left_parts = [p for p in parts if p["cx"] <= 0]
    right_parts = [p for p in parts if p["cx"] > 0]
    left_parts.sort(key=lambda p: -p["cy"])  # top to bottom
    right_parts.sort(key=lambda p: -p["cy"])

    LINE_H = 14

    def draw_side_labels(group, side):
        if side == "left":
            lx = MARGIN - 8
            anchor = "end"
        else:
            lx = MARGIN + BOARD_W * SCALE + 8
            anchor = "start"

        start_y = MARGIN + 15
        for i, p in enumerate(group):
            color = COLORS[p["sub"]]
            sx, sy = board_to_svg(p["cx"], p["cy"])
            ly = start_y + i * LINE_H
            display = p["name"] + (f" {p['val']}" if p["val"] else "")

            # Leader line
            lines.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" '
                         f'x2="{lx:.1f}" y2="{ly:.1f}" class="leader" />')
            # Label
            lines.append(f'<text x="{lx:.1f}" y="{ly + 3:.1f}" '
                         f'text-anchor="{anchor}" class="lbl" '
                         f'fill="{color}">{display}</text>')

    draw_side_labels(left_parts, "left")
    draw_side_labels(right_parts, "right")

    # Legend
    lx = 10
    ly = CANVAS_H - 55
    lines.append(f'<text x="{lx}" y="{ly}" class="legend" font-weight="bold">Subsystems:</text>')
    for sub, color in COLORS.items():
        if sub == "misc":
            continue
        ly += 14
        lines.append(f'<rect x="{lx}" y="{ly - 9}" width="9" height="9" fill="{color}" rx="1" />')
        lines.append(f'<text x="{lx + 13}" y="{ly}" class="legend">{sub.upper()}</text>')

    lines.append("</svg>")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Written: {output_path}")


def svg_to_png(svg_path, png_path):
    subprocess.run(["sips", "-s", "format", "png", svg_path, "--out", png_path],
                   capture_output=True)
    print(f"Written: {png_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    circuit_json = os.path.join(script_dir, "dist", "index", "circuit.json")

    if not os.path.exists(circuit_json):
        print("No circuit.json found. Run 'uv run pcb-build' first.")
        return

    svg_path = os.path.join(script_dir, "assembly-top.svg")
    png_path = os.path.join(script_dir, "assembly-top.png")

    generate_assembly_svg(circuit_json, svg_path, title="Top Side Assembly")
    svg_to_png(svg_path, png_path)


if __name__ == "__main__":
    main()
