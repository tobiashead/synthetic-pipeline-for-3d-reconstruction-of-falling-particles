import bpy
import numpy as np
import sys
import importlib
from pathlib import Path
import json

######################################################################################
#                                Texture Evaluation                                  #
######################################################################################
params_file_path = Path(__file__).parent / "params_textureEvaluation.json"
# load parameters from parameter file
with open(params_file_path, 'r') as file:
    params = json.load(file)

# # Input and output parameters
# "io": {
#     "obj_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\12S.obj',    # Path to the object file
#     "label_images": 1,               # how to label rendered images
#     "output_path: r'C'
# },
# # Position and movement of the object
# "motion": {
#     "s0": [0, 0, 1],            # [m] set x,y,z position of the object at t=0s
# },
# # Camera parameters
# "cam": {
#     "even_dist": True,            # are the cameras evenly distributed, True or False
#     # only necessary if even_dist = False
#     "pos_file_path": r'',         # path to the file containing the camera positions
#     # only necessary if even_dist = True
#     "number": 4,                  # number of cameras at one level
#     "focuspoint": [0,0,1],        # [m] Location of the point of focus
#     "distance": 0.2,              # [m] Euclidean distance to the "focus point"
#     "vert_angle": [-45,0,45],            # [°] Vertical angle from centre to camera position
#     # necessary, regardless of the value of even_dist 
#     "focal_length": 16,           # [mm] focal length of all cameras
#     "sensor_size": [7.12, 5.33],  # [mm,mm] sensor width and sensor height
# },
# # Light parameters
# "light": {
#     "z": [-1,1,2],                # [m] height of the light sources
#     "hor_angle": [45,90,135,180,225,270,315,360],     # [°] Horizontal angle from centre to light position
#     "distance": 1,                # [m] Horizontal Euclidean distance to the center point
#     "intensity": 10               # [W] Light intensity
# },
# # Render Settings
# "render": {
#     "format": 'JPEG',             # Select image format: 'JPEG' or 'PNG'
#     "engine": 'BLENDER_EEVEE',     # select Render Engine: 'CYCLES' or 'BLENDER_EEVEE'
#     # BLENDER_EEVEE is significantly faster (real-time), CYCLES is a ray-tracing renderer
#     "resolution_x": 2064,
#     "resolution_y": 1544,
#     "resolution_percentage": 100
# },
# }
############################# Import functions #######################################
# import functions from external script-folder
params["io"]["script_path"] = str(Path(__file__).parent)
if params["io"]["script_path"] not in sys.path:
    sys.path.append(params["io"]["script_path"])
else:
    importlib.reload(sys.modules['functions']) if 'functions' in sys.modules else None
        
from functions import (
    create_evenly_distributed_cameras,
    create_lightsources,
    renderCameras,
    translate_obj,
    create_not_evenly_distributed_cameras,
    )        
############################# Simulation routine #####################################
#------------------------------------------------------------------------------------
# Clear all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
#------------------------------------------------------------------------------------
# Load objects
bpy.ops.wm.obj_import(filepath=str(params["io"]["obj_path"]))   # Import the OBJ model
obj = bpy.context.active_object                                 # Retrieve the last imported object (this is now the active object)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')  # Recalculate the object's bounding box to update its center of mass
params["motion"] = translate_obj(0,params["motion"],obj)        # Set the position of the object at t=0s
#------------------------------------------------------------------------------------
# Create cameras
if params["cam"]["even_dist"] == True:
    create_evenly_distributed_cameras(params["cam"])
else: 
    create_not_evenly_distributed_cameras(params["cam"])
#------------------------------------------------------------------------------------
# Create light sources
create_lightsources(params["light"])
#------------------------------------------------------------------------------------
# Rendering of all cameras in the scene
image_count = 0; t_count = 0; camera_data = []
params["exiftool"]["mod"] = 0
image_count,camera_data,_ = renderCameras(params,t_count,image_count,camera_data)
