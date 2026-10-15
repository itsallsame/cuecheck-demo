"""Create a dimensioned reference and annotated QA figure from measured mesh bounds."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

root=Path(__file__).resolve().parent
report=json.loads((root/'measurements.json').read_text())
spec=json.loads((root/'source-spec.json').read_text())
reference=[(0,0,.2,6),(7.8,0,.2,6),(0,0,8,.2),(0,5.8,8,.2),
           (3.9,.2,.2,1.8),(3.9,2.9,.2,2.9)]

def plan(ax, rectangles, width, gap, color):
    for x,y,w,h in rectangles:
        ax.add_patch(Rectangle((x,y),w,h,facecolor='#273c50',edgecolor='white',linewidth=.35))
    ax.annotate('',xy=(0,6.45),xytext=(width,6.45),arrowprops={'arrowstyle':'<->','color':color})
    ax.text(width/2,6.6,f'{width:.2f} m overall',ha='center',fontsize=10,color=color)
    ax.annotate('',xy=(4.5,2),xytext=(4.5,2+gap),arrowprops={'arrowstyle':'<->','color':color})
    ax.text(4.8,2+gap/2,f'{gap:.2f} m\nclear gap',va='center',fontsize=9,color=color)
    ax.text(1.8,3.2,'A',ha='center',fontsize=22,color='#8897a7')
    ax.text(6.2,3.2,'B',ha='center',fontsize=22,color='#8897a7')
    ax.set(xlim=(-.6,8.9),ylim=(-.5,7.3),aspect='equal')
    ax.axis('off')

fig,axes=plt.subplots(1,3,figsize=(15,5.6))
fig.patch.set_facecolor('white')
plan(axes[0],reference,8,.9,'#273c50')
axes[0].set_title('REFERENCE · SELF-AUTHORED',fontsize=12,loc='left',pad=14)
for ax,key,title,color in [(axes[1],'before','BEFORE · 2 SEEDED ERRORS','#b74729'),
                            (axes[2],'after','CORRECTED · 3 / 3 PASS','#19735c')]:
    rec=report['results'][key]['glb_reimport_measurement']
    rectangles=[(v['min'][0],v['min'][1],v['max'][0]-v['min'][0],v['max'][1]-v['min'][1])
                for v in rec['mesh_bounds'].values()]
    plan(ax,rectangles,rec['outer_width'],rec['door_clear_width'],color)
    ax.set_title(title,fontsize=12,loc='left',pad=14,color=color)
fig.suptitle('Plan-to-model QA · inspect, measure, correct, recheck',x=.035,ha='left',fontsize=19,y=.97)
fig.text(.035,.085,'Metres · 1 mm tolerance · mesh bounds measured after GLB re-import in Blender 5.1.2',fontsize=10,color='#34495e')
fig.text(.035,.04,'Synthetic work sample, not a client result or an INK TO BRICK defect. Opening head height is unspecified; only its plan gap is checked.',fontsize=9,color='#586573')
fig.subplots_adjust(left=.03,right=.99,top=.84,bottom=.19,wspace=.12)
fig.savefig(root/'comparison.png',dpi=140,facecolor='white')
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,6.4));plan(ax,reference,8,.9,'#273c50')
ax.set_title('Synthetic dimensioned reference · 8.00 × 6.00 m',loc='left')
fig.text(.05,.03,'Wall thickness 0.20 m · partition x=4.00 m · opening y=2.00–2.90 m · no construction use',fontsize=9)
fig.savefig(root/'reference.svg',bbox_inches='tight');plt.close(fig)

html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Synthetic model QA sample · itsallsame</title><style>body{font:17px/1.6 system-ui,sans-serif;color:#213547;max-width:1100px;margin:48px auto;padding:0 22px}h1{font-size:32px;line-height:1.2}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;margin:24px 0}td,th{text-align:left;border-bottom:1px solid #dce3e9;padding:12px}a{color:#126452}small{color:#596974}li{margin:8px 0}</style><p><small>itsallsame · work sample · October 15, 2026</small></p><h1>Two discrepancies, measured and rechecked</h1><p>I authored a small reference plan, built a deliberately inconsistent Blender model, recorded the differences, corrected them, then exported and re-imported both revisions to verify the dimensions. All geometry, reference data, annotations and checks in this example are my own work.</p><p><strong>This is a synthetic exercise, not a past client project or a finding about INK TO BRICK.</strong></p><img src="comparison.png" alt="Dimensioned reference and measured before/after plans: overall width 8.00, 8.20 and 8.00 metres; opening gap 0.90, 0.60 and 0.90 metres."><h2>Findings</h2><table><thead><tr><th>Location / issue</th><th>Expected</th><th>Before</th><th>Corrected GLB</th></tr></thead><tbody><tr><td>Outer east boundary / overall width</td><td>8.00 m</td><td>8.20 m · fail</td><td>8.00 m · pass</td></tr><tr><td>Partition opening, y=2.00 m / clear plan gap</td><td>0.90 m</td><td>0.60 m · fail</td><td>0.90 m · pass</td></tr><tr><td>Overall north–south depth</td><td>6.00 m</td><td>6.00 m · pass</td><td>6.00 m · pass</td></tr></tbody></table><h2>Reproduction and correction</h2><ol><li>Open <a href="reference.svg">the dimensioned reference</a> and <a href="source-spec.json">source specification</a>. Dimensions are metres.</li><li>Open <a href="before.blend">before.blend</a> or import <a href="before.glb">before.glb</a>. Measure the world-space bounds of all six wall meshes. Subtract partition_south's maximum y from partition_north's minimum y for the opening gap.</li><li>The before model's east boundary is 0.20 m too far east. Correct the outer-wall extent to 8.00 m. Move the north partition segment's lower end from y=2.60 to y=2.90 m.</li><li>Open <a href="after.blend">after.blend</a> or import <a href="after.glb">after.glb</a> and repeat the measurements. The original before evidence remains available.</li><li>Run <code>blender --background --python build_and_check.py</code> with <a href="build_and_check.py">the source script</a> and source-spec.json beside it. It writes both revisions, exports GLB, re-imports each into a clean Blender scene, and writes <a href="measurements.json">the measured report</a>.</li></ol><h2>Evidence and limits</h2><p>The checks use world-space mesh bounds, with a tolerance of 0.001 m. The before model fails width and opening-gap checks; the corrected GLB passes all three. Each GLB round trip preserves these three dimensions within the same tolerance. This demonstrates Blender-to-GLB-to-Blender checks, not interoperability across multiple independent tools.</p><p>The plan does not specify the opening head height, so this model leaves an unbounded vertical gap and checks only the plan gap. No lintel, door swing, stairs, multi-floor connectivity, BIM semantics, building-code compliance, structural design or real site measurements are evaluated. No INK TO BRICK editor behavior has been tested.</p><p><a href="measurements.json">Raw results</a> · <a href="build_and_check.py">Reproduction source</a> · <a href="present.py">Annotation source</a> · <a href="source-spec.json">Reference data</a></p></html>'''
(root/'index.html').write_text(html)
print('Wrote reference.svg, comparison.png and evidence page.')
