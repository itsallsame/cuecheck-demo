"""Run with Blender --background --python build_and_check.py. No live scene is touched."""
import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
spec = json.loads((ROOT / 'source-spec.json').read_text())

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

def box(name, bounds):
    lo, hi = bounds
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(a+b)/2 for a,b in zip(lo,hi)])
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = [b-a for a,b in zip(lo,hi)]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def bounds(obj):
    points = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return {'min':[min(p[i] for p in points) for i in range(3)],
            'max':[max(p[i] for p in points) for i in range(3)]}

def measure():
    bpy.context.view_layer.update()
    meshes = {o.name: bounds(o) for o in bpy.context.scene.objects if o.type == 'MESH'}
    lo = [min(v['min'][i] for v in meshes.values()) for i in range(3)]
    hi = [max(v['max'][i] for v in meshes.values()) for i in range(3)]
    return {'mesh_bounds': meshes,
            'outer_width':hi[0]-lo[0], 'outer_depth':hi[1]-lo[1],
            'door_clear_width':meshes['partition_north']['min'][1]-meshes['partition_south']['max'][1]}

results = {}
for revision, width, gap in [('before',8.2,0.6),('after',8.0,0.9)]:
    reset()
    h,t = 2.7,0.2
    # Intentional before-model discrepancies are independent of the reference specification.
    for name,lo,hi in [
        ('west',(0,0,0),(t,6,h)), ('east',(width-t,0,0),(width,6,h)),
        ('south',(0,0,0),(width,t,h)), ('north',(0,6-t,0),(width,6,h)),
        ('partition_south',(3.9,t,0),(4.1,2.0,h)),
        ('partition_north',(3.9,2.0+gap,0),(4.1,6-t,h))]:
        box(name,(lo,hi))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / f'{revision}.blend'))
    original = measure()
    bpy.ops.export_scene.gltf(filepath=str(ROOT / f'{revision}.glb'), export_format='GLB')
    reset()
    bpy.ops.import_scene.gltf(filepath=str(ROOT / f'{revision}.glb'))
    receiving = measure()
    checks = []
    for field in ['outer_width','outer_depth','door_clear_width']:
        expected,actual = spec[field],receiving[field]
        checks.append({'check':field,'expected_m':expected,'actual_m':round(actual,6),
                       'status':'pass' if abs(expected-actual)<=spec['tolerance'] else 'fail'})
    export_deltas = {f:abs(original[f]-receiving[f]) for f in ['outer_width','outer_depth','door_clear_width']}
    assert all(d <= spec['tolerance'] for d in export_deltas.values()), export_deltas
    results[revision] = {'blend_measurement':original,'glb_reimport_measurement':receiving,
                         'checks':checks,'export_roundtrip_max_delta_m':max(export_deltas.values())}

assert sum(c['status']=='fail' for c in results['before']['checks']) == 2
assert all(c['status']=='pass' for c in results['after']['checks'])
report = {'provenance':spec['origin'],'blender_version':bpy.app.version_string,
          'reference':'source-spec.json','tolerance_m':spec['tolerance'],
          'results':results,'not_checked':['IFC/BIM semantics','multi-floor connectivity',
             'structural suitability','building-code compliance','real site measurements',
             'INK TO BRICK editor behavior'],
          'unresolved':spec['unresolved']}
(ROOT / 'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print('QA_PROOF_OK: before 2 deliberate failures; corrected GLB 3/3 checks pass; both roundtrips preserve dimensions.')
