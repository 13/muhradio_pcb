"""Validate regenerated solids, exported meshes, and nominal fit envelopes."""
import itertools,json
import generate as g
import trimesh
parts={'base':g.base(),'lid':g.lid().rotate((0,0,0),(1,0,0),180).translate((0,g.L,g.H+1.8)),'wall_mount':g.mount().translate((-3,-2,-2.75)),'battery_deck':g.battery_deck().translate((0,0,13)), 'sensor_shelf':g.sensor_shelf().translate((0,0,23))}
report={'part_intersections_mm3':{},'mesh_checks':{},'nominal_envelope_intersections_mm3':{}}
for (a,p),(b,q) in itertools.combinations(parts.items(),2):
 v=p.intersect(q).val().Volume();report['part_intersections_mm3'][a+'/'+b]=round(v,6)
 assert v<1e-5,(a,b,v)
for f in g.OUT.glob('*.stl'):
 m=trimesh.load_mesh(f); report['mesh_checks'][f.name]={'watertight':bool(m.is_watertight),'positive_volume':bool(m.volume>0)}
 assert m.is_watertight and m.volume>0
for name,mock in {'battery':g.box(6,32,1.8,20,50,10),'carrier':g.box(6,32,21,17.78,60,1.6),'sensor_board':g.box(6,7.8,25.2,20,18,1.6)}.items():
 for part,p in parts.items():
  v=p.intersect(mock).val().Volume();report['nominal_envelope_intersections_mm3'][name+'/'+part]=round(v,6)
  assert v<1e-5,(name,part,v)
(g.OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
