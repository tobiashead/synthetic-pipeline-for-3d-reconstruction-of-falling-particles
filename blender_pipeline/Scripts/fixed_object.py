import bpy
import numpy as np
import sys
import importlib
import json
from pathlib import Path

######################################################################################
#                                Fixed-objects                                       #
######################################################################################
# Are external parameters used or the parameters defined here
ExternalParams = True

############################# Select Parameters ######################################
if ExternalParams:
    # Loading Parameters
    params_file_path = Path(__file__).parent / "params_fixedO.json"
    # load parameters from parameter file
    with open(params_file_path, 'r') as file:
        params = json.load(file)
else:
    params = {
        # Input and output parameters
        "io": {
            "name": 'test',    # project name (e.g. 'Dodekaeder')
            #"obj_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\12S.obj',    # Path to the object file
            "obj_path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\GRAU5.obj",
            "label_images": 1               # how to label rendered images
            # 1: "{project_name}_{image_count}"
            # 2: "{project_name}_{timestep_count}_{camera_number}"
            # 3: "{project_name}_{camera_number}_{timestep_count}"
        },
        # Position and movement of the object
        "motion": {
            "s0": [0, 0, 1],            # [m] set x,y,z position of the object at t=0s
        },
        # Camera parameters
        "cam": {
            "even_dist": False,  # are the cameras evenly distributed, True or False
            # only necessary if even_dist = False
            "pos_file_path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\Dynamic2Static_Test_Moving\CamerasExtrinsicsStatic.json",
            "number": 10,                  # number of cameras at one level
            "focuspoint": [0,0,1],        # [m] Location of the point of focus
            "distance": 0.2,              # [m] Euclidean distance to the "center point"
            "vert_angle": [-45,0,45],            # [°] Vertical angle from centre to camera position
            # necessary, regardless of the value of even_dist 
            "focal_length": 16,          # [mm] focal length of all cameras
            "sensor_size": [7.12, 5.33],      # [mm,mm] sensor width and sensor height
        },
        # Light parameters
        "light": {
            "z": [0.8,1.2],                    # [m] height of the light sources
            "hor_angle": [45,135,215,305],     # [°] Horizontal angle from centre to light position
            "distance": 0.2,               # [m] Horizontal Euclidean distance to the center point
            "intensity": 10             # [W] Light intensity
        },
        # Render Settings
        "render": {
            "format": 'JPEG',             # Select image format: 'JPEG' or 'PNG'
            "engine": 'BLENDER_EEVEE',     # select Render Engine: 'CYCLES' or 'BLENDER_EEVEE'
            # BLENDER_EEVEE is significantly faster (real-time), CYCLES is a ray-tracing renderer
            "resolution_x": 2064,
            "resolution_y": 1544,
            "resolution_percentage": 100,
            "transparent": False 
        },
        # Exiftool options
        "exiftool": {
            "mod": 2   # choose operating mod (1 = "immediately", 2= "aferwards" --> improve performance)
        }
    }
############################# Import functions #######################################
project_path = (Path(__file__).resolve()).parent.parent.parent
with open(project_path / "path_settings.json", 'r') as file:
    app_paths = json.load(file)
params["exiftool"]["path"] = app_paths["exiftool_exe"]
# import functions from external script-folder
params["io"]["script_path"] = str(project_path / "blender_pipeline" / "Scripts")
if params["io"]["script_path"] not in sys.path:
    sys.path.append(params["io"]["script_path"])
else:
    importlib.reload(sys.modules['functions']) if 'functions' in sys.modules else None
        
from functions import (
    create_evenly_distributed_cameras,
    create_lightsources,
    renderCameras,
    write_exif_tags,
    create_output_path,
    save_BlenderSettingsAndConfiguration,
    print_warnings,
    create_not_evenly_distributed_cameras,
    rotate_obj,
    SaveObjectInWorldCoordinateOrigin
    )
######################################################################################
         
############################# Fixed-object routine ###################################
#------------------------------------------------------------------------------------
# Clear all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
#------------------------------------------------------------------------------------
# Load objects
bpy.ops.wm.obj_import(filepath=str(params["io"]["obj_path"]))   # Import the OBJ model
obj = bpy.context.active_object                                 # Retrieve the last imported object (this is now the active object)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')  # Recalculate the object's bounding box to update its center of mass
params["io"]["obj_path"] = SaveObjectInWorldCoordinateOrigin(obj,str(params["io"]["obj_path"]))  # Center object and save the centered object (if not already saved) 
obj.location = (params["motion"]["s0"])                                 # Set the position of the object at t=0s
params["motion"]["e"] = [0,0,0]; params["motion"]["omega"] = 0
obj.rotation_mode = "AXIS_ANGLE"; rotate_obj(0,params["motion"],obj) # Set the rotation of the object at t=0s
#------------------------------------------------------------------------------------
# Create Output-Path
params["io"]["output_path"] = create_output_path(project_path,params["io"]["name"])
#------------------------------------------------------------------------------------
# Create cameras
if params["cam"]["even_dist"] == True:
    create_evenly_distributed_cameras(params["cam"])
else: 
    create_not_evenly_distributed_cameras(params["cam"])
#------------------------------------------------------------------------------------
# Create light sources
light_data = create_lightsources(params["light"],params["cam"]["focuspoint"])
#------------------------------------------------------------------------------------
# Rendering of all cameras in the scene
image_count = 0; t_count = 0; camera_data = []
image_count,camera_data,params = renderCameras(params,t_count,image_count,camera_data)
#------------------------------------------------------------------------------------        
# Write Exif-Tags
write_exif_tags(params["cam"],params["render"],params["io"]["output_path"],params["exiftool"])
######################################################################################

############################## Save data #############################################
#------------------------------------------------------------------------------------        
save_BlenderSettingsAndConfiguration(params,camera_data,None,light_data)
print_warnings(params)  # display warnings
######################################################################################