"""Independent procedural still-life material study; no purchased assets/add-ons."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_x, s.render.resolution_y = 1000, 700
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.film_transparent = False
s.world = bpy.data.worlds.new('Studio world')
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs[0].default_value = (.22,.29,.38,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value = .35
s.view_settings.view_transform = 'Standard'

def pigment(name, colors):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial')
    diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.8,.8,.8,1)
    rgb=n.new('ShaderNodeShaderToRGB');l.new(diff.outputs[0],rgb.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
    cr=ramp.color_ramp;cr.elements.remove(cr.elements[1])
    for i,(position,color) in enumerate(zip([.08,.31,.58,.88],colors)):
        e=cr.elements[0] if i==0 else cr.elements.new(position)
        e.position=position;e.color=(*color,1)
    l.new(rgb.outputs[0],ramp.inputs[0])
    coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(3,3,13);l.new(coord.outputs['Generated'],mapping.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.2
    noise.inputs['Detail'].default_value=2.5;noise.inputs['Roughness'].default_value=.7
    l.new(mapping.outputs[0],noise.inputs['Vector'])
    wash=n.new('ShaderNodeValToRGB')
    wash.color_ramp.elements[0].color=(.57,.57,.57,1)
    wash.color_ramp.elements[1].color=(1,1,1,1)
    l.new(noise.outputs['Fac'],wash.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.62
    l.new(ramp.outputs[0],mix.inputs[1]);l.new(wash.outputs[0],mix.inputs[2])
    emission=n.new('ShaderNodeEmission');l.new(mix.outputs[0],emission.inputs[0]);l.new(emission.outputs[0],out.inputs[0])
    return m

blue=pigment('Cobalt pigment — generated brush variation',[(.035,.08,.17),(.065,.22,.39),(.12,.41,.59),(.42,.67,.74)])
rust=pigment('Terracotta pigment',[(.19,.06,.045),(.49,.15,.08),(.76,.32,.15),(.93,.56,.31)])
cream=pigment('Warm chalk',[(.35,.27,.16),(.67,.54,.33),(.88,.77,.53),(.99,.91,.73)])
green=pigment('Sage leaves',[(.07,.13,.1),(.15,.3,.2),(.32,.48,.29),(.57,.65,.37)])
yellow=pigment('Lemon yellow',[(.37,.24,.05),(.66,.49,.07),(.95,.75,.13),(1,.91,.43)])
table=pigment('Ochre tabletop',[(.22,.12,.08),(.48,.29,.16),(.65,.43,.24),(.84,.64,.4)])
back=pigment('Muted blue backdrop',[(.12,.2,.27),(.2,.32,.4),(.29,.45,.51),(.44,.58,.61)])

def lathe(name, profile, loc, mat):
    count=64;v=[];f=[]
    for r,z in profile:
        for i in range(count):
            a=i*2*math.pi/count;v.append((r*math.cos(a),r*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(count):
            a=j*count+i;b=j*count+(i+1)%count;f.append((a,b,b+count,a+count))
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
    o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.location=loc;o.data.materials.append(mat)
    for face in me.polygons:face.use_smooth=True
    return o

lathe('Blue pitcher',[(0,0),(.42,0),(.48,.13),(.53,.55),(.49,1.05),(.34,1.48),(.29,1.72),(.33,1.81),(.29,1.83),(.25,1.75),(.27,1.53),(.39,1.18),(.43,.5),(.36,.15),(0,.15)],(-.62,.27,.05),blue)
lathe('Terracotta vase',[(0,0),(.33,0),(.46,.18),(.48,.53),(.37,.86),(.21,1.07),(.19,1.3),(.23,1.35),(.19,1.38),(.15,1.29),(.17,1.12),(.31,.82),(.38,.5),(.32,.16),(0,.16)],(.79,.48,.05),rust)
lathe('Shallow chalk bowl',[(0,.03),(.4,.03),(.67,.12),(.86,.32),(.88,.4),(.85,.42),(.78,.32),(.57,.19),(0,.15)],(.18,-.68,.05),cream)

def curve(name, points, radius, mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=3
    sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for b,pt in zip(sp.bezier_points,points):b.co=pt;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);s.collection.objects.link(o);o.data.materials.append(mat);return o
curve('Pitcher handle',[(-1.02,.29,1.61),(-1.39,.29,1.56),(-1.46,.29,1.05),(-1.1,.29,.69)],.08,blue)
for i,(x,y,z,scale) in enumerate([(-.08,-.7,.36,(.34,.25,.25)),(.45,-.65,.4,(.3,.24,.27)),(.2,-1.0,.38,(.29,.25,.22))]):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=(x,y,z))
    o=bpy.context.object;o.name=f'Lemon {i+1}';o.scale=scale;o.data.materials.append(yellow)
    for face in o.data.polygons:face.use_smooth=True

stems=[[(.79,.48,1.32),(.7,.5,1.85),(.43,.48,2.43)],[(.79,.48,1.32),(.98,.48,1.95),(1.28,.5,2.36)]]
for k,pts in enumerate(stems):
    curve(f'Sage stem {k}',pts,.017,green)
    for j in range(5):
        q=j/5+.1;base=Vector(pts[1]).lerp(Vector(pts[2]),q)
        dx=(-1 if j%2 else 1)*.27
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=base+Vector((dx/2,0,.03)))
        o=bpy.context.object;o.name=f'Leaf {k}-{j}';o.scale=(.23,.045,.09);o.rotation_euler[1]=(-.45 if dx<0 else .45);o.data.materials.append(green)

bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));bpy.context.object.data.materials.append(table)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,2.7,0),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(back)
bpy.ops.object.light_add(type='AREA',location=(-3,-4,7));bpy.context.object.name='Large soft key';bpy.context.object.data.energy=500;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(4,-7,4.2));cam=bpy.context.object;cam.name='Study camera';s.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=4.9
cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'pigment-study.blend'))
s.render.filepath=str(ROOT/'study-front.png');bpy.ops.render.render(write_still=True)
cam.location=(3.5,-5,3.1);cam.data.ortho_scale=3.5
cam.rotation_euler=(Vector((-.1,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(ROOT/'study-detail.png');bpy.ops.render.render(write_still=True)
(ROOT/'manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':s.render.engine,'source':'pigment-study.blend','renders':['study-front.png','study-detail.png'],'dependencies':'Blender only. All meshes and procedural materials made in build.py. No external assets.','verified_scope':'Two still renders only. No claim animated-scene temporal stability, client work, commercial painterly portfolio, or compatibility with Cycles. EEVEE Shader to RGB materials.'},indent=2)+'\n')
