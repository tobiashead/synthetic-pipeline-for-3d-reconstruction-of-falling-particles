from pathlib import Path
import json
import sys
import matplotlib.pyplot as plt
#from matplotlib import font_manager
#import matplotlib as mpl
current_dir = Path(__file__).resolve().parent
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
from src.CameraProcessing import read_camera_alignment_reference, match_cameras, read_object_alignment
from src.camera_pose_visualizer import CameraPoseVisualizer

style_path = current_dir / 'thesis.mplstyle'
plt.style.use(str(style_path))

#image_dir = r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\Moving_BP_02_1cam'
#image_dir = r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\blender_data\Moving_BP_02_1cam'
image_dir = r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\4sRotY'
cams_ref = read_camera_alignment_reference(image_dir)
objs, obj0 = read_object_alignment(image_dir)   

# load camera parameters
params_file_path = Path(image_dir) / "params.json"
with open(params_file_path, 'r') as file:
    params = json.load(file)
focuspoint = params["cam"]["focuspoint"]
focal_length = params["cam"]["focal_length"]*10**(-3)
sensor_width = params["cam"]["sensor_size"][0]*10**(-3)
aspect_ratio = params["cam"]["sensor_size"][0] / params["cam"]["sensor_size"][1]

# transformation from dynamic into static scene
for cam in cams_ref:
    Tdynamic2static = cam.Dynamic2StaticScene(objs[cam.CorrespondigIndexObject].Transformation, obj0.Transformation,focuspoint)

top=1.0
bottom=0.015
left=0.005
right=0.888
hspace=0.2
wspace=0.2
azim = 115; elev = 24
# static scene    
from src.camera_pose_visualizer import CameraPoseVisualizer 
visualizer2 = CameraPoseVisualizer([-0.3, 0.3], [-0.45, 0.15], [-0.3, 0.3],figsize=(5.46/2,3.7))
visualizer2.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.3,DrawCoordSystem=True,static_scene=True,colorbar=True,colorbar_orientation='horizontal') 
visualizer2.load_cube(cams_ref,static_scene=True)   
#visualizer2.fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace,wspace=wspace)
visualizer2.ax.view_init(elev=elev, azim=azim)
cbar = visualizer2.fig.axes[1].set_xlabel("Zeitpunkt $k$")
path = current_dir / "Extrinsics_cams_reference_static" 
#visualizer2.save(path,bbox_inches=None)  
visualizer2.show()
# Speichere Azimut und Elevation
azim = visualizer2.ax.azim
elev = visualizer2.ax.elev
print(f"Saved azimuth: {azim}, elevation: {elev}")


# dynamic scene
from src.camera_pose_visualizer import CameraPoseVisualizer
visualizer = CameraPoseVisualizer([-0.15, 0.15], [-0.15, 0.15], [0.85, 1.15],figsize=(5.46/2, 3.7))
visualizer.load_cameras([cams_ref[1]],focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.3,DrawCoordSystem=True,colormap='gnuplot',static_scene=False,colorbar = True,color_based_on_height=True,colorbar_orientation='horizontal')
visualizer.load_cube(cams_ref)
visualizer.ax.view_init(elev=elev, azim=azim)
visualizer.fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right)
cbar = visualizer.fig.axes[1].set_xlabel("Höhe in m")
path = current_dir / "Extrinsics_cams_dynamic"
#visualizer.save(path,bbox_inches=None,pad_inches=0)      
visualizer.show()
    


