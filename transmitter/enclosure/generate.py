"""Parametric transmitter enclosure. Run with Python 3.12 + cadquery 2.8.

Coordinates: X across board/battery, Y toward antenna, Z toward lid; mm.
"""
from pathlib import Path
import cadquery as cq

OUT = Path(__file__).parent / 'exports'
W, L = 32.0, 102.0
WALL, FLOOR, H = 2.4, 1.8, 33.0
PCB_X, PCB_Y, PCB_Z = 6.0, 32.0, 21.0
PCB_W, PCB_L = 17.78, 60.0
SCREWS = [(4.8, 4.8), (W-4.8, 4.8), (4.8, L-4.8), (W-4.8, L-4.8)]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x,y,z))

def rounded(w, l, h, r, x=0, y=0, z=0):
    return box(x,y,z,w,l,h).edges('|Z').fillet(r)

def cylinder(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))

def base():
    p = rounded(W,L,H,6).cut(rounded(W-2*WALL,L-2*WALL,H,3.6,WALL,WALL,FLOOR))
    for x,y in SCREWS:
        p = p.union(cylinder(x,y,FLOOR,2.8,H-FLOOR))
        p = p.cut(cylinder(x,y,H-9,0.85,10))
    # Removable battery deck rests on wall ledges, never on the pouch.
    for x in (WALL,W-WALL-2):
        p = p.union(box(x,30,FLOOR,2,55,13-FLOOR))
    # Thermal partition reaches lid; only a small wire passage connects bays.
    p = p.union(box(WALL,26,FLOOR,W-2*WALL,1.2,H-FLOOR))
    p = p.cut(box(14,25.9,30,4,1.4,3.1))
    # Removable sensor shelf avoids a trapped support cavity during printing.
    for x in (WALL,W-WALL-2):
        p = p.union(box(x,8,FLOOR,2,16,23-FLOOR))
    # Side air slots: opposite sides of the sensor pocket, away from wall.
    for x in (-0.1,W-WALL-0.1):
        for y in (9,13,17,21):
            p = p.cut(box(x,y,26,WALL+0.2,2,4.8))
    # Rear guide channels receive the wall cradle's keeper rails.
    for x in (-0.1,W-1.2):
        p = p.cut(box(x,7,2.7,1.3,L-6,2.1))
    # Antenna exits at far end; slot covers both radio antenna positions.
    p = p.cut(box(6,L-WALL-0.1,20,19,WALL+0.2,3))
    return p

def lid():
    # Outer face on bed. Shallow locating skirt enters the body cavity.
    p = rounded(W,L,1.8,6)
    skirt = rounded(W-5.4,L-5.4,1.4,3.3,2.7,2.7,1.8).cut(
        rounded(W-8.2,L-8.2,2,2,4.1,4.1,1.7))
    for x,y in SCREWS:
        skirt = skirt.cut(cylinder(x,y,1.7,3.2,2))
    skirt = skirt.cut(box(0,L-27.3,1.7,W,1.4,2))
    p = p.union(skirt)
    for x,y in SCREWS:
        p = p.cut(cylinder(x,y,-0.1,1.15,4))
        p = p.cut(cylinder(x,y,-0.1,2.2,1.1))
    # Lid flips around X at assembly: print Y is mirrored from housing Y.
    for y in (9,13,17,21):
        p = p.cut(box(8,L-y-2,-0.1,16,2,2.1))
    return p

def battery_deck():
    # Print deck underside on bed. Install after cell, before PCB.
    p = box(3,30,0,W-6,55,1.2)
    for x in (PCB_X-0.6, PCB_X+PCB_W-0.6):
        for y in (PCB_Y+2, PCB_Y+28):
            p = p.union(box(x,y,1.2,1.2,3,PCB_Z-14.2))
    return p

def sensor_shelf():
    # Shallow sensor cavity; small contact areas reduce thermal conduction.
    p = rounded(W-5.4,23,1.2,3.3,2.7,2.7)
    for x,y in SCREWS:
        p = p.cut(cylinder(x,y,-0.1,3.1,1.4))
    for x in (5.8,25):
        p = p.union(box(x,9,1.2,1.2,12,1.0))
    return p

def mount():
    # Print back down. Case slides down from +Y; bottom shelf stops travel.
    p = rounded(W+6,L,2.4,4,-3,0,-2.75)
    for x in (-2.4,W+0.35):
        p = p.union(box(x,30,-0.35,2.05,60,5.05))
    for x in (-0.6,W-0.85):
        p = p.union(box(x,30,3,1.45,60,1.5))
    p = p.union(box(-1,-2,-2.75,W+2,2,7.45))
    # Sensor bay back is open: reduced coupling to wall and less plastic.
    p = p.cut(box(4,3,-3,W-8,21,3))
    # Flat-head 3 mm wall screws, 50 mm apart. Heads below sliding face.
    for y in (38,88):
        p = p.cut(cylinder(W/2,y,-3,1.75,4))
        cone = cq.Solid.makeCone(1.75,3.4,1.65,cq.Vector(W/2,y,-2))
        p = p.cut(cone)
    return p.translate((3,2,2.75))

def main():
    OUT.mkdir(exist_ok=True)
    parts = {'base':base(), 'lid':lid(), 'wall_mount':mount(),
             'battery_deck':battery_deck(), 'sensor_shelf':sensor_shelf()}
    assembly = cq.Assembly(name='muhradio_102050')
    for name,p in parts.items():
        assert p.val().isValid(), name
        assert len(p.solids().vals()) == 1, name
        cq.exporters.export(p,str(OUT/f'{name}.stl'),tolerance=0.06,angularTolerance=0.12)
        cq.exporters.export(p,str(OUT/f'{name}.step'))
        if name == 'lid':
            placed = p.rotate((0,0,0),(1,0,0),180).translate((0,L,H+1.8))
        elif name == 'wall_mount':
            placed = p.translate((-3,-2,-2.75))
        elif name == 'battery_deck':
            placed = p.translate((0,0,13))
        elif name == 'sensor_shelf':
            placed = p.translate((0,0,23))
        else:
            placed = p
        assembly.add(placed,name=name)
        bb=p.val().BoundingBox()
        print(f'{name}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm; valid single solid')
    assembly.save(str(OUT/'assembly.step'))
    # Exploded vector preview produced from the same CAD geometry.
    preview = parts['base'].union(parts['lid'].translate((-48,0,20))).union(
        parts['wall_mount'].translate((48,0,0))).union(
        parts['battery_deck'].translate((0,0,48))).union(
        parts['sensor_shelf'].translate((0,-4,48)))
    cq.exporters.export(preview,str(OUT/'preview.svg'),opt={
        'width':1100,'height':720,'projectionDir':(1,-1,1.1),
        'showHidden':False,'strokeWidth':0.5,'showAxes':False})

if __name__ == '__main__':
    main()
