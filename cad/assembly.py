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
BAT_WIRE_OD = 1.2  # AWG24–26 insulation envelope, not bare copper diameter.
BEND_RADIUS = 2.0  # Minimum centerline radius; supplier may require more.
USB_SIZE = (7.35, 8.94, 3.31)  # GCT USB4105 drawing rev B4, gct.co/files/drawings/usb4105.pdf
SWITCH_SIZE = (3.4, 6.4, 6.4)  # Omron B3F-1000 body, includes +/-0.2 width tolerance.
SWITCH_THROW = 0.25  # A070-E1.pdf; tune actuator gap with printed shims.
ACTUATOR_GAP = 0.10
SPEAKER_Z = e.DEVICE_HEIGHT - e.SPEAKER_TOP_OFFSET - e.SPEAKER_DIAMETER / 2
LED_SOCKET_X = e.LED_BOARD_X - 2.2  # SH socket behind the LED board, offset towards X+


def box(size, center):
    return cq.Workplane('XY').box(*size).translate(center).val()


def cylinder(radius, length, origin, axis):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*origin), cq.Vector(*axis))


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


def harness(points, count, diameter):
    path = rounded_path(points, 4.0 if diameter==BAT_WIRE_OD else BEND_RADIUS)
    normal = (cq.Vector(*points[1])-cq.Vector(*points[0])).normalized()
    plane = cq.Plane(origin=points[0], normal=normal)
    # Individual insulated conductors; four leads occupy a 2x2 bundle.
    pitch = diameter+0.12
    offsets = {1: [(0,0)], 2: [(-pitch/2, 0), (pitch/2, 0)],
               3: [(-pitch/2, -pitch/3), (pitch/2, -pitch/3), (0, pitch*2/3)],
               4: [(x*pitch/2,y*pitch/2) for x in (-1,1) for y in (-1,1)]}[count]
    wires = []
    for x,y in offsets:
        profile = cq.Workplane(plane).center(x,y).circle(diameter/2)
        wires.append(profile.sweep(path, isFrenet=False).val())
    return wires, path.Length()


def build():
    chassis, cover = e.split_enclosure(e.build_enclosure())
    parts, colors, contacts, prints = {}, {}, {}, {}

    def add(name, body, color='#aaaaaa'):
        parts[name] = body.val() if isinstance(body,cq.Workplane) else body
        colors[name] = color
        return parts[name]

    def contact(a,b,reason,region):
        contacts[frozenset((a,b))] = (reason,region)

    add('chassis',chassis,'#a9bacb')
    add('cover',cover,'#c3cbd3')
    add('main_PCB',pcb.board_with_holes(),'#24784a')
    add('cell_18650',e.battery_envelope(),'#546db4')
    placements=[(n,u,22 if n=='J_USB' else 124 if n=='J_LED' else z,w,l,h,c) for n,u,z,w,l,h,c in pcb.PLACEMENTS]
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
    add('amplifier_allocation',box((1.5,5,4),(9.15,-3,118)),'#e99991')
    add('J_SPK',box((3,4.5,8.5),(8.4,-3,110)),'#edba65')
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
    for name,x,z,w,h in [('mic',1,10,e.MIC_BOARD_WIDTH,e.MIC_BOARD_HEIGHT),('LED',e.LED_BOARD_X,140,e.LED_BOARD_WIDTH,e.LED_BOARD_HEIGHT)]:
        b=box((w,1.6,h),(x,-16.05,z))
        if name=='mic':
            b=b.cut(cylinder(.5,2,(x,-17.1,z),(0,1,0)))
        add(name+'_PCB',b,'#24784a')
        # Compressed perimeter tape in the existing seat, including acoustic seal.
        gasket=box((w,.15,h),(x,-16.925,z)).cut(box((w-2,2,h-2),(x,-16.925,z)))
        # Existing seat occupies most perimeter: remove only existing solid from gasket.
        gasket=gasket.cut(parts['chassis'])
        add(name+'_gasket',gasket,'#333333')
    mic=box((4,1.2,3),(1,-14.65,10)).cut(cylinder(.5,1.4,(1,-15.5,10),(0,1,0)))
    add('IM69D130',mic,'#d0d0d0')
    add('mic_J_SH_mated',box((7.95,3,6.5),(-5.275,-13.75,10.75)),'#edba65')
    # LED socket behind the board, offset towards X+ to avoid the speaker cup.
    add('LED_J_SH_mated',box((5.5,3,8.5),(LED_SOCKET_X,-13.75,139.75)),'#edba65')
    for x in e.LED_POSITIONS_X:
        add(f'LED_{x}',box((2,.9,2),(x,-17.30,140)),'#eee6ab')
    add('speaker',cylinder(10,e.SPEAKER_BODY_DEPTH,(0,-18.3,SPEAKER_Z),(0,1,0)),'#50565e')
    gasket=cylinder(10,.1,(0,-18.4,SPEAKER_Z),(0,1,0)).cut(cylinder(9,.2,(0,-18.45,SPEAKER_Z),(0,1,0)))
    add('speaker_gasket',gasket,'#333333')

    # Charging daughterboard perpendicular to main board; receptacle faces X+.
    # Shell rounded cross-section follows the port, with solid envelope behind it.
    shell=(cq.Workplane('YZ',origin=(20.05,0,31)).rect(USB_SIZE[1],USB_SIZE[2])
           .extrude(-USB_SIZE[0]).edges('|X').fillet(1.3).val())
    # Model the receptacle opening instead of a solid metal plug.
    shell=shell.cut(box((5,7.6,2.1),(19.2,0,31)))
    add('USB4105',shell,'#b7b8ba')
    add('USB_PCB',box((6.6,13,1),(15.1,0,28.845)),'#24784a')
    add('USB_J_SH_mated',box((6.5,8.5,3),(15.1,0,26.845)),'#edba65')
    # Shoe supports board edges and rear of socket. Front/back stops take insertion load.
    shoe=box((7.7,16,1.5),(15.65,0,27.595))
    shoe=shoe.cut(box((6.2,10,4),(15.8,0,27.6)))
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
            cap=cap.fuse(flange).fuse(cylinder(1.4,20.3-17.5-ACTUATOR_GAP,(17.5+ACTUATOR_GAP,0,z),(1,0,0)))
        else:
            seal=cylinder(5.5,.65,(21,0,z),(1,0,0)).cut(cylinder(4.25,.8,(20.9,0,z),(1,0,0)))
            add(label+'_perimeter_tape',seal,'#ddd1ac')
            cap=cylinder(3.7,1.5,(20.1,0,z),(1,0,0))
            cap=cap.fuse(cylinder(5.5,1.2,(21.65,0,z),(1,0,0)))
            cap=cap.fuse(cylinder(1.4,20.3-17.5-ACTUATOR_GAP,(17.5+ACTUATOR_GAP,0,z),(1,0,0)))
        # Connect across the 0.05 mm step under the perimeter membrane.
        cap=cap.fuse(cylinder(2,1,(21.0,0,z),(1,0,0)))
        add(label+'_TPU_cap',cap,'#675683'); prints[label+'_TPU_cap']=cap

    # Contact envelopes + insulating washers within existing end carriers.
    for label,z,axis in [('negative',20,(0,0,-1)),('positive',85,(0,0,1))]:
        add('cell_'+label+'_contact',cylinder(2,2.8,(-3,0,z),axis),'#b9b9b9')
        washer=cylinder(6,.2,(-3,0,z+axis[2]*2.8),axis).cut(cylinder(2.2,.3,(-3,0,z+axis[2]*2.75),axis))
        add('cell_'+label+'_insulator',washer,'#dcad59')
    add('NTC',box((2,1,3),(-3,-9.8,58)),'#dcad59')

    # Purchased tie envelopes run in new saddle grooves (0.15 radial clearance).
    for z in (27,71):
        strap=cylinder(10,2.5,(-3,0,z-1.25),(0,0,1)).cut(cylinder(9.6,3,(-3,0,z-1.5),(0,0,1)))
        strap=strap.fuse(box((4,2,3.5),(-3,10.6,z)))
        add(f'cell_tie_{z}',strap,'#343434')
        groove=cylinder(10.15,2.8,(-3,0,z-1.4),(0,0,1)).cut(cylinder(9.45,3,(-3,0,z-1.5),(0,0,1)))
        parts['chassis']=parts['chassis'].cut(groove)
    # A stepped bridge clears the PCB edge. Vertical screws avoid the PCB rails.
    # The plate sits behind the 5.3 mm speaker body; two risers reach forward to
    # the ears through the gaps between the speaker rim and the PCB slab.
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
    bridge=bridge.cut(cylinder(10.3,8,(0,-19,SPEAKER_Z),(0,1,0)))
    # Rebate the bridge, preserving the bearing plane under its mounting ears.
    parts['chassis']=parts['chassis'].cut(bridge)
    add('speaker_bridge',bridge,'#df984e'); prints['speaker_bridge']=bridge

    # Eight captive harnesses. Ends terminate on the corresponding mated connector
    # or insulated solder/contact body. Exact pin mapping lives in DESIGN.md.
    routes={
        'MIC': (4, WIRE_OD, [(8.4,-4,15.25),(8.4,-4,6),(-13.75,-4,6),(-13.75,-4,11.5),(-13.75,-13.75,11.5),(-9.25,-13.75,11.5)], 'J_MIC','mic_J_SH_mated'),
        'USB': (4, WIRE_OD, [(8.4,4,16.25),(8.4,4,11.5),(8.4,14.5,11.5),(13.9,14.5,11.5),(13.9,14.5,26.845),(15.3,4.25,26.845)], 'J_USB','USB_J_SH_mated'),
        'PWR': (2, WIRE_OD, [(8.4,0,38.25),(8.4,0,33),(8.4,15,33),(13.9,15,33),(13.9,15,44),(12.9,3.85,44)], 'J_PWR','PWR_terminals'),
        'PTT': (2, WIRE_OD, [(8.4,4.5,115.75),(8.4,4.5,120),(8.4,15,120),(13.9,15,120),(13.9,15,105),(12.9,3.85,105)], 'J_PTT','PTT_terminals'),
        'SPK': (2, WIRE_OD, [(8.4,-3,105.75),(8.4,-3,98),(0,-3,98),(0,-10,98),(5,-10,SPEAKER_Z-4),(5,-14.3,SPEAKER_Z-4)], 'J_SPK','speaker'),
        'LED': (3, WIRE_OD, [(8.4,-9,118.25),(4,-9,118.25),(4,-9,127),(LED_SOCKET_X,-9,132),(LED_SOCKET_X,-13.75,132),(LED_SOCKET_X,-13.75,135.5)], 'J_LED','LED_J_SH_mated'),
        'BAT_POS': (1, BAT_WIRE_OD, [(1.9,2,101),(-3,2,101),(-3,8,95),(-3,8,86.5),(-3,2,86.5)], 'J_BAT','cell_positive_contact'),
        'BAT_NEG': (1, BAT_WIRE_OD, [(1.9,4,101),(-3,4,101),(-3,16,94),(-3,16,7),(-3,8,7),(-3,8,18.5),(-3,2,18.5)], 'J_BAT','cell_negative_contact'),
        'NTC': (2, WIRE_OD, [(8.4,-7,97.25),(8.4,-7,91),(6,-11,91),(6,-11,58),(1,-11,58),(-2,-9.8,58)], 'J_NTC','NTC'),
    }
    lengths={}
    for name,(count,od,points,start,end) in routes.items():
        wires,length=harness(points,count,od)
        if name in ('USB','PWR','PTT'):
            path=rounded_path(points,BEND_RADIUS)
            plane=cq.Plane(origin=points[0],normal=cq.Vector(*points[1])-cq.Vector(*points[0]))
            tunnel=cq.Workplane(plane).circle(1.2 if count==4 else 1.02).sweep(path,isFrenet=False).val()
            parts['chassis']=parts['chassis'].cut(tunnel)
            mount='USB_shoe' if name=='USB' else name+'_carrier'
            parts[mount]=parts[mount].cut(tunnel)
            prints[mount]=parts[mount]
        lengths[name]={'conductors':count,'insulated_diameter_mm':od,'centerline_mm':round(length,1),'start':start,'end':end}
        for i,wire in enumerate(wires):
            label=f'wire_{name}_{i+1}'
            add(label,wire,['#c3473e','#333333','#e2b73e','#658dce'][i%4])
            contact(label,start,'wire termination at connector/contact',box((4,4,4),points[0]))
            contact(label,end,'wire termination at connector/contact',box((4,4,4),points[-1]))
    # Chassis-only clips retain the two long leads when the cover is removed.
    for z in (50,82):
        support=box((19,2,2),(5.5,14.5,z)).fuse(box((2,3.5,2),(14,12.9,z)))
        clip=box((4,4,3),(-3,16,z)).cut(cylinder(.75,4,(-3,16,z-2),(0,0,1)))
        clip=clip.cut(box((.9,3,4),(-3,17.5,z)))
        support=support.fuse(clip).cut(cylinder(.75,4,(-3,16,z-2),(0,0,1)))
        parts['chassis']=parts['chassis'].fuse(support)
    clip=cylinder(2.25,2.5,(6,-11,74.75),(0,0,1)).cut(cylinder(1.02,3,(6,-11,74.5),(0,0,1)))
    clip=clip.cut(box((.9,3,4),(6,-9.5,76)))
    stem=box((2.5,6,2.5),(6,-15.9,76))
    parts['chassis']=parts['chassis'].fuse(stem).fuse(clip)
    # Header bearing areas must actually fit their custom boards; plugs may overhang.
    for board,probe in [('mic_PCB',box((4.95,.1,6.5),(-3.775,-15.3,10.75))),
                        ('LED_PCB',box((5.5,.1,5.5),(LED_SOCKET_X,-15.3,141.25))),
                        ('USB_PCB',box((6.5,5.5,.1),(15.1,-1.5,28.395)))]:
        assert probe.cut(parts[board]).Volume()<1e-5, f'{board}: header bearing area off board'
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



def motion_checks(parts):
    """Cover sampled along its pin axis; button center checked through its stroke."""
    errors=[]
    e.check_assembly(cq.Workplane(obj=parts['chassis']),cq.Workplane(obj=parts['cover']))
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
            for name in ('chassis','cover','main_PCB',label+'_carrier',label+'_switch'):
                if moved.intersect(parts[name]).Volume()>1e-5:
                    errors.append(f'{label} center catches {name} at {travel} mm travel')
            assert abs(moved.BoundingBox().xmin-(17.5+ACTUATOR_GAP-travel))<1e-6
    return errors

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'fit-report.json').write_text(json.dumps({'status':'BUILDING'})+'\n')
    parts,colors,contacts,prints,lengths=build()
    errors,distances=inspect(parts,contacts)
    if not errors:
        print('Static fit passed; checking cover and button travel',flush=True)
        errors.extend(motion_checks(parts))
    report={'status':'FAIL' if errors else 'CHECKED','errors':errors,'near_pairs':distances,'harnesses':lengths,'cover_withdrawal_mm':[.5,2,4,10,25,50],
            'button_center_travel_mm':[ACTUATOR_GAP,ACTUATOR_GAP+SWITCH_THROW],
            'limits':['Dimensional envelopes, not a fabrication release','Cover motion sampled, not a continuous swept-volume proof','TPU deformation and adhesive strength need a physical test','Speaker, cell contacts and cable insulation require purchased-part confirmation'],
            'intentional_contacts':[{'parts':sorted(k),'reason':v[0]} for k,v in contacts.items()]}
    (OUT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('\n'.join(errors) if errors else 'Static fit checks passed',flush=True)
    assembly=cq.Assembly()
    for name,body in parts.items():
        assembly.add(body,name=name,color=cq.Color(colors[name]))
    assembly.export(str(OUT/'assembly.step'))
    opened=cq.Assembly()
    for name,body in parts.items():
        if name!='cover' and not name.startswith('closure_'):
            opened.add(body,name=name,color=cq.Color(colors[name]))
    opened.export(str(OUT/'open.step'))
    for suffix,excluded in [('open',{'cover','closure_M2_1','closure_M2_2'}),('internals',{'cover','chassis','closure_M2_1','closure_M2_2'})]:
        mesh=cq.Compound.makeCompound([s for n,s in parts.items() if n not in excluded])
        cq.exporters.export(mesh.rotate((0,0,0),(0,0,1),180),str(OUT/f'{suffix}.stl'),tolerance=.05)
    e.export_stl(e.print_orientation(cq.Workplane(obj=parts['chassis'])),OUT/'chassis_print.stl')
    e.export_stl(e.print_orientation(cq.Workplane(obj=parts['cover']),True),OUT/'cover_print.stl')
    for name,shape in prints.items():
        if name=='speaker_bridge':
            oriented=cq.Workplane(obj=shape).rotate((0,0,0),(1,0,0),180)
        else:
            oriented=cq.Workplane(obj=shape).rotate((0,0,0),(0,1,0),90 if 'TPU_cap' in name else -90)
        bb=oriented.val().BoundingBox()
        oriented=oriented.translate((-bb.center.x,-bb.center.y,-bb.zmin))
        e.export_stl(oriented,OUT/f'{name}_print.stl')
    assert not errors, 'Assembly fit failed: see fit-report.json'
    report['status']='PASS'
    (OUT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(parts)} named bodies; all printable STLs watertight and connected',flush=True)


if __name__=='__main__':
    main()
