"""Mechanical assembly for hardware/pcb/DESIGN.md. Run: python -m cad.assembly.

Purchased parts are dimensioned envelopes, not manufacturer STEP models. Group
allocations remain on the unrouted main PCB. See output/full-assembly/README.md.
"""
import json
import math
from itertools import combinations
from pathlib import Path

import cadquery as cq

from cad import enclosure as e
from hardware.pcb import design as pcb

# PARAMETERS — mm. Keep adjustable clearances for the real printed assembly.
OUT = Path('output/full-assembly')
FIT = 0.3
WIRE_OD = 0.8  # AWG28 insulation envelope; verify purchased pre-crimped leads.
BAT_WIRE_OD = 1.4  # JST ASPHSPH24K305, 24 AWG UL1007; not bare copper diameter.
BEND_RADIUS = 2.0  # Minimum centerline radius; supplier may require more.
USB_SIZE = (7.35, 8.94, 3.31)  # GCT USB4105 drawing rev B4, gct.co/files/drawings/usb4105.pdf
SWITCH_SIZE = (3.4, 6.4, 6.4)  # Omron B3F-1000 body, includes +/-0.2 width tolerance.
SWITCH_THROW = 0.25  # A070-E1.pdf; tune actuator gap with printed shims.
ACTUATOR_GAP = 0.10
PTT_CROWN_X = 22.85  # Outer face of the TPU flange; the crown grows from here.
PTT_CROWN_BASE = (27.0, 47.0, 9.0)  # Y width, Z height, corner radius
PTT_CROWN_BEVEL = 2.0  # 45 deg, so the top face is 2*BEVEL smaller each way
PTT_DOT = (1.0, 0.5, 1.5)  # diameter, height, pitch
SPEAKER_Z = e.DEVICE_HEIGHT - e.SPEAKER_TOP_OFFSET - e.SPEAKER_DIAMETER / 2
LED_SOCKET_X = e.LED_BOARD_X  # 7-way header centred on the 12 mm board
WALL_INNER_Y = -(e.DEVICE_WIDTH/2 - e.WALL_THICKNESS)  # inside face of the front wall
BAT_NEG_CHANNEL_X = -10.5  # lead centreline along the front wall, clear of the mic seat
BAT_NEG_CHANNEL_Y = WALL_INNER_Y + 0.1 + BAT_WIRE_OD/2
BAT_NEG_CHANNEL_Z = (22.5, 97.0)  # straight run; 4 mm bends lead in and out beyond it

# Nine captive harnesses. Ends terminate on the corresponding mated connector
# or insulated solder/contact body. Exact pin mapping lives in DESIGN.md.
# The 8-conductor USB run crosses under the PCB bottom edge at Z = 10.9.
PRODUCT_ROUTES = {
    'MIC': (4, WIRE_OD, [(8.4,-4,15.25),(8.4,-4,6),(-13.75,-4,6),(-13.75,-4,11.5),(-13.75,-13.75,11.5),(-9.25,-13.75,11.5)], 'J_MIC','mic_J_SH_mated'),
    'USB': (8, WIRE_OD, [(7.6,4,19.25),(7.6,4,10.9),(7.6,14.5,10.9),(13.9,14.5,10.9),(13.9,14.5,26.3),(15.3,4.25,26.3)], 'J_USB','USB_J_SH_mated'),
    'PWR': (2, WIRE_OD, [(8.4,0,38.25),(8.4,0,33),(8.4,15,33),(13.9,15,33),(13.9,15,44),(12.9,3.85,44)], 'J_PWR','PWR_terminals'),
    'PTT': (2, WIRE_OD, [(8.4,4.5,115.75),(8.4,4.5,120),(8.4,15,120),(13.9,15,120),(13.9,15,105),(12.9,3.85,105)], 'J_PTT','PTT_terminals'),
    'SPK': (2, WIRE_OD, [(8.4,-3,105.75),(8.4,-3,98),(0,-3,98),(0,-10,98),(5,-10,SPEAKER_Z-4),(5,-14.3,SPEAKER_Z-4)], 'J_SPK','speaker'),
    'LED': (7, WIRE_OD, [(8.4,-9,119.3),(4,-9,119.3),(4,-9,127),(LED_SOCKET_X,-9,132),(LED_SOCKET_X,-13.75,132),(LED_SOCKET_X,-13.75,135.5)], 'J_LED','LED_J_SH_mated'),
    'BAT_POS': (1, BAT_WIRE_OD, [(1.9,2,101),(-3,2,101),(-3,8,95),(-3,8,86.5),(-3,2,86.5)], 'J_BAT','cell_positive_contact'),
    'BAT_NEG': (1, BAT_WIRE_OD, [(1.9,4,101),(BAT_NEG_CHANNEL_X,4,101),(BAT_NEG_CHANNEL_X,BAT_NEG_CHANNEL_Y,101),(BAT_NEG_CHANNEL_X,BAT_NEG_CHANNEL_Y,18.5),(-3,-2,18.5)], 'J_BAT','cell_negative_contact'),
    'NTC': (2, WIRE_OD, [(8.4,-7,97.25),(8.4,-7,91),(6,-11,91),(6,-11,58),(1,-11,58),(-2,-9.8,58)], 'J_NTC','NTC'),
}

# Field unit (hardware/PROTOTYPE.md): solder terminations on the stripboard, XIAO and
# breakouts; the cell leads leave the XIAO's underside pads through a stripboard window,
# run down the rail channel behind the board and return through a second window.
FIELD_ROUTES = {
    'MIC': (4, WIRE_OD, [(8.9,-4,18),(8.9,-4,12),(1,-4,12),(1,-14.5,12),(1,-14.5,15)], 'field_stripboard','mic_PCB'),
    # X 15.0 descent passes behind the clipped amp pins; Y 4.2 clears the switch body.
    'PTT': (2, WIRE_OD, [(8.9,4.5,116),(8.9,4.5,120),(8.9,15,120),(15.0,15,120),(15.0,15,105),(15.0,4.2,105),(12.9,4.2,105)], 'field_stripboard','PTT_terminals'),
    'SPK': (2, WIRE_OD, [(6,-11,98),(6,-11,116),(6,-14.3,116)], 'MAX98357A_breakout','speaker'),
    # X 8.4 keeps the 5-wide bundle off the board face, Y -9.8 off the speaker bridge,
    # Z 132.5 off the chassis above the speaker chamber.
    'LED': (5, WIRE_OD, [(8.4,-9.8,120),(8.4,-9.8,124),(3,-9.8,124),(3,-9.8,132.5),(3,-14.75,132.5),(3,-14.75,136.5)], 'field_stripboard','LED_PCB'),
    'BAT_POS': (1, BAT_WIRE_OD, [(9.0,-1,136.3),(13.5,-1,136.3),(13.5,-1,118),(-3,-1,118),(-3,8,118),(-3,8,86.5),(-3,2,86.5)], 'XIAO_nRF52840','cell_positive_contact'),
    'BAT_NEG': (1, BAT_WIRE_OD, [(9.0,1,136.3),(13.5,1,136.3),(13.5,1,120),(-3,1,120),(-3,16,120),(-3,16,7),(-3,8,7),(-3,8,18.5),(-3,2,18.5)], 'XIAO_nRF52840','cell_negative_contact'),
}


def box(size, center):
    return cq.Workplane('XY').box(*size).translate(center).val()


def cylinder(radius, length, origin, axis):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*origin), cq.Vector(*axis))


def rounded_rect(plane_origin, width, height, radius):
    """Rounded rectangle sketch on a YZ workplane; width spans Y, height spans Z."""
    return (cq.Workplane('YZ', origin=plane_origin).sketch()
            .rect(width, height, tag='r').vertices(tag='r').fillet(radius).finalize())


def dot_grid(width, height, radius, dia, pitch):
    """Dot centers on a rounded rect, every dot fully inside the outline."""
    hw, hh = width/2 - dia/2, height/2 - dia/2
    dx, dy = width/2 - radius, height/2 - radius
    pts = []
    for i in range(-int(hw/pitch), int(hw/pitch)+1):
        for j in range(-int(hh/pitch), int(hh/pitch)+1):
            u, v = i*pitch, j*pitch
            if abs(u) > dx and abs(v) > dy and math.hypot(
                    u-math.copysign(dx, u), v-math.copysign(dy, v)) > radius - dia/2:
                continue
            pts.append((u, v))
    return pts


def rounded_path(points, radius):
    """Exact tangent circular bends; reject segments too short for the radius."""
    pts = [cq.Vector(*p) for p in points]
    edges, last = [], pts[0]
    for i in range(1, len(pts)-1):
        a, b, c = pts[i-1:i+2]
        incoming, outgoing = (b-a).normalized(), (c-b).normalized()
        angle = math.acos(max(-1, min(1, incoming.dot(outgoing))))
        if angle < 1e-8:
            continue
        assert angle < math.pi-1e-6, 'wire doubles back'
        trim = radius * math.tan(angle/2)
        assert trim < (b-a).Length and trim < (c-b).Length, f'Bend too tight at {b.toTuple()}'
        start, end = b-incoming*trim, b+outgoing*trim
        center = start + (outgoing-incoming*incoming.dot(outgoing)).normalized()*radius
        mid = center + ((start-center).normalized()+(end-center).normalized()).normalized()*radius
        assert (start-last).dot(incoming) >= -1e-7, f'Adjacent bends overlap at {b.toTuple()}'
        if (start-last).Length > 1e-7:
            edges.append(cq.Edge.makeLine(last, start))
        edges.append(cq.Edge.makeThreePointArc(start, mid, end))
        last = end
    edges.append(cq.Edge.makeLine(last, pts[-1]))
    return cq.Wire.assembleEdges(edges)


def bundle_offsets(count, diameter):
    """Conductor centre offsets in the bundle cross-section; 5+ leads form two rows."""
    pitch = diameter+0.12
    if count <= 4:
        return {1: [(0,0)], 2: [(-pitch/2, 0), (pitch/2, 0)],
                3: [(-pitch/2, -pitch/3), (pitch/2, -pitch/3), (0, pitch*2/3)],
                4: [(x*pitch/2,y*pitch/2) for x in (-1,1) for y in (-1,1)]}[count]
    per_row = (count+1)//2
    xs = [(i-(per_row-1)/2)*pitch for i in range(per_row)]
    offsets = [(x, -pitch/2) for x in xs] + [(x, pitch/2) for x in xs]
    return offsets[:count]


def bundle_radius(count, diameter):
    return max(math.hypot(x, y) for x, y in bundle_offsets(count, diameter)) + diameter/2


def harness(points, count, diameter):
    path = rounded_path(points, 4.0 if diameter==BAT_WIRE_OD else BEND_RADIUS)
    normal = (cq.Vector(*points[1])-cq.Vector(*points[0])).normalized()
    plane = cq.Plane(origin=points[0], normal=normal)
    # Individual insulated conductors in the bundle cross-section.
    offsets = bundle_offsets(count, diameter)
    wires = []
    for x,y in offsets:
        profile = cq.Workplane(plane).center(x,y).circle(diameter/2)
        wires.append(profile.sweep(path, isFrenet=False).val())
    return wires, path.Length()


def build(variant='product'):
    chassis, cover = e.split_enclosure(e.build_enclosure(variant), variant)
    parts, colors, contacts, prints = {}, {}, {}, {}

    def add(name, body, color='#aaaaaa'):
        parts[name] = body.val() if isinstance(body,cq.Workplane) else body
        colors[name] = color
        return parts[name]

    def contact(a,b,reason,region):
        contacts[frozenset((a,b))] = (reason,region)

    board = 'main_PCB' if variant == 'product' else 'field_stripboard'
    add('chassis',chassis,'#a9bacb')
    add('cover',cover,'#c3cbd3')
    add('cell_18650',e.battery_envelope(),'#546db4')
    if variant == 'product':
        add('main_PCB',pcb.board_with_holes(),'#24784a')
        # J_USB sits at Z = 25: its 10.5 mm wide plug clears the Z = 16 screw heads.
        placements=[(n,u,25 if n=='J_USB' else 124 if n=='J_LED' else z,w,l,h,c) for n,u,z,w,l,h,c in pcb.PLACEMENTS]
        placements=[(n,4.5 if n=='J_PTT' else -7 if n=='J_NTC' else u,z,w,l,h,c) for n,u,z,w,l,h,c in placements]
        for p in placements:
            add(p[0].replace(' / ','_').replace(' + ','_'),pcb.component_box(p),pcb.COLORS[p[-1]])
        # SH mated plug extensions include insertion overlap in a single envelope.
        for p in placements:
            name,u,z,w,length,h,cat = p
            if name.startswith('J_') and name != 'J_BAT':
                parts[name] = parts[name].fuse(box((h,w,3),(8.4,u,z+(length/2+1.5)*(1 if name=='J_PTT' else -1))))
        # Separate speaker connector from its original combined placement allocation.
        del parts['AMP_J_SPK']
        # Shifted towards Y+ inside the AMP allocation to clear the wider J_LED plug.
        add('amplifier_allocation',box((1.5,4.5,4),(9.15,-0.75,118)),'#e99991')
        add('J_SPK',box((3,4.5,8.5),(8.4,-3,110)),'#edba65')
    else:
        add('field_stripboard', e.field_stripboard_template(), '#8a6d3b')
        # XIAO nRF52840 Sense soldered flat by its castellations, USB-C end at the top wall.
        add('XIAO_nRF52840', box((4.46,17.78,21.0),(7.67,0,136.3)), '#24784a')
        add('XIAO_USBC', box((3.21,8.94,1.5),(7.045,0,147.55)), '#8f8f8f')
        # MAX98357A breakout on one 7-pin header row at Y = 6.1; pins clipped 1.5 mm behind the board.
        add('MAX98357A_breakout', box((5.5,17.8,19.4),(7.15,-1.5,101.7)), '#24784a')
        add('amp_header_pins', box((1.5,1.0,15.24),(12.3,6.1,101.7)), '#8f8f8f')
    for u in (-10,10):
        for z in pcb.SCREW_STATIONS:
            name=f'PCB_M2_{u}_{z}'
            head=cylinder(pcb.HEAD_DIAMETER/2,pcb.HEAD_HEIGHT,(9.9,u,z),(-1,0,0))
            screw=head.fuse(cylinder(1,5,(9.9,u,z),(1,0,0)))
            add(name,screw)
            contact(name,'chassis','M2 threads engage 3.4 mm of the blind plastic pilot', cylinder(1.01,3.42,(11.49,u,z),(1,0,0)))

    for i,(u,z) in enumerate(e.SCREW_POSITIONS):
        shaft=e.seam_cylinder(u,z,1,-2.5,6).val()
        head=e.seam_cylinder(u,z,2,-2.5,-1.8).val()
        name=f'closure_M2_{i+1}'
        add(name,shaft.fuse(head))
        contact(name,'chassis','M2 closure threads engage the blind pilot',e.seam_cylinder(u,z,1.01,-.01,3.52).val())

    # Audio boards, bottom-port mic with acoustic through-hole, and LED emitters.
    for name,x,z,w,h in [('mic',1,10,*e.mic_board_size(variant)),('LED',e.LED_BOARD_X,140,e.LED_BOARD_WIDTH,e.LED_BOARD_HEIGHT)]:
        b=box((w,1.6,h),(x,-16.05,z))
        if name=='mic':
            b=b.cut(cylinder(.5,2,(x,-17.1,z),(0,1,0)))
        add(name+'_PCB',b,'#24784a')
        # Compressed perimeter tape in the existing seat, including acoustic seal.
        gasket=box((w,.15,h),(x,-16.925,z)).cut(box((w-2,2,h-2),(x,-16.925,z)))
        # Existing seat occupies most perimeter: remove only existing solid from gasket.
        gasket=gasket.cut(parts['chassis'])
        add(name+'_gasket',gasket,'#333333')
    if variant == 'product':
        mic=box((4,1.2,3),(1,-14.65,10)).cut(cylinder(.5,1.4,(1,-15.5,10),(0,1,0)))
        add('IM69D130',mic,'#d0d0d0')
        add('mic_J_SH_mated',box((7.95,3,6.5),(-5.275,-13.75,10.75)),'#edba65')
        # LED socket behind the board.
        add('LED_J_SH_mated',box((9.5,3,8.5),(LED_SOCKET_X,-13.75,139.75)),'#edba65')
    else:
        # Adafruit 3492: top-port MP34DT01 faces the wall inside the seat window.
        add('mic_MP34DT01', box((3,1.2,4),(1,-17.45,10)), '#d0d0d0')
    for x in e.LED_POSITIONS_X:
        # 3 mm through-hole RGB LED: 1 mm flange on the board face, dome through the wall.
        flange=cylinder(1.9,1.0,(x,-16.85,140),(0,-1,0))
        dome=cylinder(1.5,4.4,(x,-17.85,140),(0,-1,0))
        add(f'LED_{x}',flange.fuse(dome),'#eee6ab')
    add('speaker',cylinder(10,e.SPEAKER_BODY_DEPTH,(0,-18.3,SPEAKER_Z),(0,1,0)),'#50565e')
    gasket=cylinder(10,.1,(0,-18.4,SPEAKER_Z),(0,1,0)).cut(cylinder(9,.2,(0,-18.45,SPEAKER_Z),(0,1,0)))
    add('speaker_gasket',gasket,'#333333')

    if variant == 'product':
        # Charging daughterboard perpendicular to main board; receptacle faces X+.
        # Shell rounded cross-section follows the port, with solid envelope behind it.
        shell=(cq.Workplane('YZ',origin=(20.05,0,31)).rect(USB_SIZE[1],USB_SIZE[2])
               .extrude(-USB_SIZE[0]).edges('|X').fillet(1.3).val())
        # Model the receptacle opening instead of a solid metal plug.
        shell=shell.cut(box((5,7.6,2.1),(19.2,0,31)))
        add('USB4105',shell,'#b7b8ba')
        add('USB_PCB',box((6.6,13,1),(15.1,0,28.845)),'#24784a')
        add('USB_J_SH_mated',box((6.5,11.0,3),(15.1,0,26.845)),'#edba65')
        # Shoe supports board edges and rear of socket. Front/back stops take insertion load.
        shoe=box((7.7,16,1.5),(15.65,0,27.595))
        shoe=shoe.cut(box((6.2,12.0,4),(15.8,0,27.6)))
        for y in (-7.25,7.25):
            shoe=shoe.fuse(box((7.7,1.5,4),(15.65,y,28.845)))
        shoe=shoe.fuse(box((1.5,16,5.5),(12.55,0,29.595)))
        shoe=shoe.cut(parts['main_PCB'])
        # This shoe is bonded over two broad wall tabs; no screw into thin port wall.
        for y in (-6,6):
            shoe=shoe.fuse(box((2.0,3,6),(18.0,y,28.0)))
        shoe=shoe.cut(parts['chassis']).cut(parts['USB_PCB']).cut(parts['USB4105']).cut(parts['USB_J_SH_mated'])
        add('USB_shoe',shoe,'#df984e'); prints['USB_shoe']=shoe

    # Separate tactile switches, retained with thin perimeter adhesive in rigid carriers.
    # Mechanical load goes through the carrier into chassis wall/rails, never main PCB.
    for label,z in [('PTT',105),('PWR',44)]:
        add(label+'_switch',box(SWITCH_SIZE,(14.9,0,z)),'#353535')
        add(label+'_plunger',cylinder(1.75,.9,(16.6,0,z),(1,0,0)),'#c9bd88')
        # Short trimmed solder leads; insulated terminations modeled as one envelope.
        add(label+'_terminals',box((.6,7.7,5),(12.9,0,z)),'#aaaaaa')
        carrier=box((1.2,10,10),(12.4,0,z))
        for y in (-4.35,4.35):
            carrier=carrier.fuse(box((5.9,1.5,10),(15.55,y,z)))
        # Wings bond to the existing rails at y = +/-7.75, below their bearing face.
        for y in (-6.3,6.3):
            carrier=carrier.fuse(box((1.5,2.6,10),(15.55,y,z)))
        front=box((1.2,10,10),(17.2,0,z)).cut(cylinder(2,2,(16.5,0,z),(1,0,0)))
        stop=cylinder(3.5,20.1-SWITCH_THROW-ACTUATOR_GAP-17.8,(17.8,0,z),(1,0,0)).cut(cylinder(2,2.1,(17.7,0,z),(1,0,0)))
        carrier=carrier.fuse(front).fuse(stop).cut(parts['chassis']).cut(parts[label+'_terminals'])
        add(label+'_carrier',carrier,'#df984e'); prints[label+'_carrier']=carrier
        for y in (-7.675,7.675):
            add(f'{label}_rail_tape_{y}',box((1.5,.15,10),(15.55,y,z)),'#ddd1ac')
        for dz in (-2.85,2.85):
            add(f'{label}_switch_tape_{dz}',box((.2,6.4,.5),(13.1,0,z+dz)),'#ddd1ac')
        # TPU diaphragm caps: bonded perimeter provides retention and return;
        # a rigid center pad pushes the switch, hard shoulder limits travel.
        if label=='PTT':
            cap=(cq.Workplane('YZ',origin=(20.1,0,z)).rect(24,44).extrude(1.5)
                 .edges('|X').fillet(7.5).val())
            flange=(cq.Workplane('YZ',origin=(21.65,0,z)).rect(29,49).extrude(1.2)
                    .edges('|X').fillet(10).val())
            seal=(cq.Workplane('YZ',origin=(21.6,0,z)).rect(29,49).extrude(.05).edges('|X').fillet(10).val())
            seal=seal.cut(cq.Workplane('YZ',origin=(21.5,0,z)).rect(26,46).extrude(.3).edges('|X').fillet(8.5).val())
            add(label+'_perimeter_tape',seal,'#ddd1ac')
            # Chamfered, dot-textured crown: thumb finds the PTT face without looking.
            crown=rounded_rect((PTT_CROWN_X-.2,0,z),*PTT_CROWN_BASE).extrude(
                PTT_CROWN_BEVEL+.2,taper=45).val()
            top_w,top_h=(d-2*PTT_CROWN_BEVEL for d in PTT_CROWN_BASE[:2])
            dots=dot_grid(top_w,top_h,PTT_CROWN_BASE[2]-PTT_CROWN_BEVEL,PTT_DOT[0],PTT_DOT[2])
            bumps=(cq.Workplane('YZ',origin=(PTT_CROWN_X+PTT_CROWN_BEVEL,0,z))
                   .pushPoints(dots).circle(PTT_DOT[0]/2).extrude(PTT_DOT[1]).val())
            cap=cap.fuse(flange).fuse(crown).fuse(bumps).fuse(
                cylinder(1.4,20.3-17.5-ACTUATOR_GAP,(17.5+ACTUATOR_GAP,0,z),(1,0,0)))
        else:
            seal=cylinder(5.5,.65,(21,0,z),(1,0,0)).cut(cylinder(4.25,.8,(20.9,0,z),(1,0,0)))
            add(label+'_perimeter_tape',seal,'#ddd1ac')
            cap=cylinder(3.7,1.5,(20.1,0,z),(1,0,0))
            cap=cap.fuse(cylinder(5.5,1.2,(21.65,0,z),(1,0,0)))
            cap=cap.fuse(cylinder(1.4,20.3-17.5-ACTUATOR_GAP,(17.5+ACTUATOR_GAP,0,z),(1,0,0)))
        # Connect across the 0.05 mm step under the perimeter membrane.
        cap=cap.fuse(cylinder(2,1,(21.0,0,z),(1,0,0)))
        add(label+'_TPU_cap',cap,'#675683'); prints[label+'_TPU_cap']=cap

    # Keystone 5201 spring and 5223 button envelopes on the end carriers, with
    # their insulating washers. The coil length is the compressed working height.
    cs=e.CONTACT_SPACE
    # Negative: 5201 coil, Ø8 x 3.0 compressed. Positive: 5223 button, Ø5 x 1.0.
    for label,z,axis,r,length in [('negative',20,(0,0,-1),4.0,3.0),('positive',85,(0,0,1),2.5,1.0)]:
        plate=box((11.2,12.0,0.5),(-3,0,z+axis[2]*(cs-0.25)))
        contact_body=cylinder(r,length,(-3,0,z+axis[2]*(cs-0.5)),(0,0,-axis[2]))
        add('cell_'+label+'_contact',plate.fuse(contact_body),'#b9b9b9')
        # Washer clears the tip bore, the collar on the positive end, and the
        # 1.4 mm lead where it bends in towards the contact.
        washer=cylinder(5.5,.2,(-3,0,z+axis[2]*(cs-0.8)),axis).cut(cylinder(r+0.1,.3,(-3,0,z+axis[2]*(cs-0.85)),axis))
        add('cell_'+label+'_insulator',washer,'#dcad59')
        if label=='positive':
            # The plate is let into the reverse-insertion collar on its carrier.
            contact('cell_positive_contact','chassis','cell contact plate bears on carrier',plate)
    if variant == 'product':
        add('NTC',box((2,1,3),(-3,-9.8,58)),'#dcad59')

    # Purchased tie envelopes run in new saddle grooves (0.15 radial clearance).
    for z in (27,71):
        strap=cylinder(10,2.5,(-3,0,z-1.25),(0,0,1)).cut(cylinder(9.6,3,(-3,0,z-1.5),(0,0,1)))
        strap=strap.fuse(box((4,2,3.5),(-3,10.6,z)))
        add(f'cell_tie_{z}',strap,'#343434')
        groove=cylinder(10.15,2.8,(-3,0,z-1.4),(0,0,1)).cut(cylinder(9.45,3,(-3,0,z-1.5),(0,0,1)))
        parts['chassis']=parts['chassis'].cut(groove)
    # A stepped bridge clears the PCB edge. Vertical screws avoid the PCB rails.
    # The plate bears on the top 2.5 mm of the speaker's back face; two risers
    # reach forward to the ears through the gaps between the speaker rim and the PCB slab.
    # Raised clear of the J_LED connector below it.
    bridge_z=SPEAKER_Z+9
    bridge=box((23.9,1.2,3),(-2.55,-11.8,bridge_z))
    bridge=bridge.fuse(box((2.5,3.1,3),(-13.25,-12.75,bridge_z)))
    bridge=bridge.fuse(box((2.0,3.1,3),(8.5,-12.75,bridge_z)))
    bridge=bridge.fuse(box((3.5,1.2,3),(10.15,-14.0,bridge_z)))
    bridge=bridge.fuse(box((2.6,1.2,3),(13.2,-13.7,bridge_z)))
    outside=e.create_octagonal_prism(e.DEVICE_HEIGHT,e.DEVICE_WIDTH,e.HALF_LONG_SIDE,e.FILLET_RADIUS).val()
    for x in (-12,12):
        lug=box((5,5,5),(x,-16.3,bridge_z-2.5)).intersect(outside)
        lug=lug.cut(cylinder(10.3,8,(0,-19,SPEAKER_Z),(0,1,0)))
        parts['chassis']=parts['chassis'].fuse(lug)
        ear=cylinder(2.25,1.5,(x,-15.5,bridge_z),(0,0,1))
        bridge=bridge.fuse(ear)
        bridge=bridge.cut(cylinder(1.1,4,(x,-15.5,bridge_z-2),(0,0,1)))
        parts['chassis']=parts['chassis'].cut(cylinder(.8,4.1,(x,-15.5,bridge_z+.1),(0,0,-1)))
        parts['chassis']=parts['chassis'].cut(cylinder(1.1,1.6,(x,-15.5,bridge_z),(0,0,1)))
        parts['chassis']=parts['chassis'].cut(cylinder(2.25,2,(x,-15.5,bridge_z+1.5),(0,0,1)))
        name=f'speaker_M2_{x}'
        screw=cylinder(2,1.8,(x,-15.5,bridge_z+1.5),(0,0,1)).fuse(cylinder(1,5,(x,-15.5,bridge_z+1.5),(0,0,-1)))
        add(name,screw)
        contact(name,'chassis','M2 threads engage speaker lug pilot',cylinder(1.01,3.52,(x,-15.5,bridge_z+.01),(0,0,-1)))
    bridge=bridge.cut(cylinder(10.3,6.5,(0,-19,SPEAKER_Z),(0,1,0)))
    # Rebate the bridge, preserving the bearing plane under its mounting ears.
    parts['chassis']=parts['chassis'].cut(bridge)
    add('speaker_bridge',bridge,'#df984e'); prints['speaker_bridge']=bridge

    lengths={}
    for name,(count,od,points,start,end) in (FIELD_ROUTES if variant=='field' else PRODUCT_ROUTES).items():
        wires,length=harness(points,count,od)
        if name in ('USB','PWR','PTT'):
            path=rounded_path(points,BEND_RADIUS)
            plane=cq.Plane(origin=points[0],normal=cq.Vector(*points[1])-cq.Vector(*points[0]))
            tunnel=cq.Workplane(plane).circle(bundle_radius(count,od)+0.3).sweep(path,isFrenet=False).val()
            parts['chassis']=parts['chassis'].cut(tunnel)
            mount='USB_shoe' if name=='USB' else name+'_carrier'
            parts[mount]=parts[mount].cut(tunnel)
            # The rail strip is applied with a notch around the lead.
            for tape in [k for k in parts if k.startswith(name+'_rail_tape')]:
                parts[tape]=parts[tape].cut(tunnel)
            prints[mount]=parts[mount]
        lengths[name]={'conductors':count,'insulated_diameter_mm':od,'centerline_mm':round(length,1),'start':start,'end':end}
        for i,wire in enumerate(wires):
            label=f'wire_{name}_{i+1}'
            add(label,wire,['#c3473e','#333333','#e2b73e','#658dce'][i%4])
            contact(label,start,'wire termination at connector/contact',box((4,4,4),points[0]))
            contact(label,end,'wire termination at connector/contact',box((4,4,4),points[-1]))
    # The battery-negative lead lies in a channel on the inside of the front wall:
    # two ribs on the wall, with the void notched through the saddle webs and
    # contact carriers it crosses. Printable in the shell's orientation.
    z0,z1=BAT_NEG_CHANNEL_Z
    ribs=box((BAT_WIRE_OD+2.2,1.6,z1-z0),(BAT_NEG_CHANNEL_X,WALL_INNER_Y+0.7,(z0+z1)/2))
    void=box((BAT_WIRE_OD+0.2,BAT_WIRE_OD+0.4,z1-z0+2),(BAT_NEG_CHANNEL_X,BAT_NEG_CHANNEL_Y+0.15,(z0+z1)/2))
    parts['chassis']=parts['chassis'].fuse(ribs).cut(void)
    # Clip for the NTC lead.
    clip=cylinder(2.25,2.5,(6,-11,74.75),(0,0,1)).cut(cylinder(1.02,3,(6,-11,74.5),(0,0,1)))
    clip=clip.cut(box((.9,3,4),(6,-9.5,76)))
    stem=box((2.5,6,2.5),(6,-15.9,76))
    parts['chassis']=parts['chassis'].fuse(stem).fuse(clip)
    # Header bearing areas must actually fit their custom boards; plugs may overhang.
    # Product only: the field unit solders its leads directly, with no SH headers.
    if variant == 'product':
        for pcb_name,probe in [('mic_PCB',box((4.95,.1,6.5),(-3.775,-15.3,10.75))),
                               ('LED_PCB',box((9.5,.1,5.5),(LED_SOCKET_X,-15.3,141.25))),
                               ('USB_PCB',box((6.5,10.0,.1),(15.1,0,28.395)))]:
            assert probe.cut(parts[pcb_name]).Volume()<1e-5, f'{pcb_name}: header bearing area off board'
    return parts,colors,contacts,prints,lengths


def inspect(parts,contacts):
    errors=[]; distances=[]
    for name,shape in parts.items():
        if not shape.isValid() or not shape.Solids():
            errors.append(f'{name}: invalid or empty solid')
    for (a,sa),(b,sb) in combinations([(n,s) for n,s in parts.items() if s.Solids()],2):
        ba,bb=sa.BoundingBox(),sb.BoundingBox()
        # Broad phase avoids expensive OCC booleans on separated boxes.
        gap=max(bb.xmin-ba.xmax,ba.xmin-bb.xmax,bb.ymin-ba.ymax,ba.ymin-bb.ymax,bb.zmin-ba.zmax,ba.zmin-bb.zmax)
        if gap>0.5:
            continue
        overlap=sa.intersect(sb).Volume() if gap < 1e-7 else 0
        d=0 if overlap>1e-5 else (sa.distance(sb) if not (a.startswith('wire_') or b.startswith('wire_')) else max(gap,0))
        if d < 0.5:
            distances.append({'a':a,'b':b,'gap_mm':round(d,4),'method':'AABB lower bound' if (a.startswith('wire_') or b.startswith('wire_')) else 'OCC distance'})
        if d < 1e-7:
            if overlap>1e-5:
                allowed=contacts.get(frozenset((a,b)))
                if allowed is None or sa.intersect(sb).cut(allowed[1]).Volume()>1e-5:
                    errors.append(f'{a} / {b}: overlap {overlap:.4f} mm3 outside permitted contact region')
    return errors,distances



def motion_checks(parts,board='main_PCB'):
    """Cover sampled along its pin axis; button center checked through its stroke."""
    errors=[]
    variant='field' if board=='field_stripboard' else 'product'
    e.check_assembly(cq.Workplane(obj=parts['chassis']),cq.Workplane(obj=parts['cover']),variant)
    for distance in (.5,2,4,10,25,50):
        cover=parts['cover'].translate((-distance/math.sqrt(2),distance/math.sqrt(2),0))
        for name,shape in parts.items():
            if name in ('cover','chassis') or name.startswith('closure_'):
                continue
            a,b=cover.BoundingBox(),shape.BoundingBox()
            if max(b.xmin-a.xmax,a.xmin-b.xmax,b.ymin-a.ymax,a.ymin-b.ymax,b.zmin-a.zmax,a.zmin-b.zmax)>0:
                continue
            if cover.intersect(shape).Volume()>1e-5:
                errors.append(f'Cover catches {name} at {distance} mm withdrawal')
    for label,z in [('PTT',105),('PWR',44)]:
        # The bonded TPU perimeter stays fixed; this checks the moving center.
        if label=='PTT':
            region=(cq.Workplane('YZ',origin=(10,0,z)).rect(24,44).extrude(20).edges('|X').fillet(7.5).val())
        else:
            region=cylinder(3.7,20,(10,0,z),(1,0,0))
        center=parts[label+'_TPU_cap'].intersect(region)
        for travel in (ACTUATOR_GAP,ACTUATOR_GAP+SWITCH_THROW):
            moved=center.translate((-travel,0,0))
            for name in ('chassis','cover',board,label+'_carrier',label+'_switch'):
                if moved.intersect(parts[name]).Volume()>1e-5:
                    errors.append(f'{label} center catches {name} at {travel} mm travel')
            assert abs(moved.BoundingBox().xmin-(17.5+ACTUATOR_GAP-travel))<1e-6
    return errors

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=('product','field'), default='product')
    variant = parser.parse_args(argv).variant
    out = OUT if variant == 'product' else Path('output/field-unit')
    out.mkdir(parents=True,exist_ok=True)
    (out/'fit-report.json').write_text(json.dumps({'status':'BUILDING'})+'\n')
    parts,colors,contacts,prints,lengths=build(variant)
    errors,distances=inspect(parts,contacts)
    if not errors:
        print('Static fit passed; checking cover and button travel',flush=True)
        errors.extend(motion_checks(parts,'main_PCB' if variant=='product' else 'field_stripboard'))
    report={'variant':variant,'status':'FAIL' if errors else 'CHECKED','errors':errors,'near_pairs':distances,'harnesses':lengths,'cover_withdrawal_mm':[.5,2,4,10,25,50],
            'button_center_travel_mm':[ACTUATOR_GAP,ACTUATOR_GAP+SWITCH_THROW],
            'limits':['Dimensional envelopes, not a fabrication release','Cover motion sampled, not a continuous swept-volume proof','TPU deformation and adhesive strength need a physical test','Speaker, cell contacts and cable insulation require purchased-part confirmation'],
            'intentional_contacts':[{'parts':sorted(k),'reason':v[0]} for k,v in contacts.items()]}
    (out/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('\n'.join(errors) if errors else 'Static fit checks passed',flush=True)
    assembly=cq.Assembly()
    for name,body in parts.items():
        assembly.add(body,name=name,color=cq.Color(colors[name]))
    assembly.export(str(out/'assembly.step'))
    opened=cq.Assembly()
    for name,body in parts.items():
        if name!='cover' and not name.startswith('closure_'):
            opened.add(body,name=name,color=cq.Color(colors[name]))
    opened.export(str(out/'open.step'))
    for suffix,excluded in [('open',{'cover','closure_M2_1','closure_M2_2'}),('internals',{'cover','chassis','closure_M2_1','closure_M2_2'})]:
        mesh=cq.Compound.makeCompound([s for n,s in parts.items() if n not in excluded])
        cq.exporters.export(mesh.rotate((0,0,0),(0,0,1),180),str(out/f'{suffix}.stl'),tolerance=.05)
    e.export_stl(e.print_orientation(cq.Workplane(obj=parts['chassis'])),out/'chassis_print.stl')
    e.export_stl(e.print_orientation(cq.Workplane(obj=parts['cover']),True),out/'cover_print.stl')
    for name,shape in prints.items():
        if name=='speaker_bridge':
            oriented=cq.Workplane(obj=shape).rotate((0,0,0),(1,0,0),180)
        else:
            oriented=cq.Workplane(obj=shape).rotate((0,0,0),(0,1,0),90 if 'TPU_cap' in name else -90)
        bb=oriented.val().BoundingBox()
        oriented=oriented.translate((-bb.center.x,-bb.center.y,-bb.zmin))
        e.export_stl(oriented,out/f'{name}_print.stl')
    assert not errors, 'Assembly fit failed: see fit-report.json'
    report['status']='PASS'
    (out/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(parts)} named bodies; all printable STLs watertight and connected',flush=True)


if __name__=='__main__':
    main()
