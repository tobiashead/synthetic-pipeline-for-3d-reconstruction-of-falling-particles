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
            "name": 'text123',    # project name (e.g. 'Dodekaeder')
            "script_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts',                    # Path of the script files
            "obj_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\12S.obj',    # Path to the object file
            #"obj_path": Path("C:/Users/Tobias/Documents/Masterarbeit_lokal/synthetic_pipeline/blender_pipeline/3D_Dice/3D_Dice.obj")
            "base_output_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data',                           # Base output path
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
            "even_dist": True,  # are the cameras evenly distributed, True or False
            # only necessary if even_dist = False
            "pos_file_path": "C:\\Users\\Tobias\\Documents\\Masterarbeit_lokal\\synthetic_pipeline\\blender_pipeline\\Scripts\\camera_positions.json",
            "number": 3,                  # number of cameras at one level
            "z_center": 1,                # [m] Height of the "cePnter point"
            "distance": 0.2,              # [m] Euclidean distance to the "center point"
            "vert_angle": [-20,0],            # [°] Vertical angle from centre to camera position
            # necessary, regardless of the value of even_dist 
            "focal_length": 100,          # [mm] focal length of all cameras
            "sensor_size": [32, 18],      # [mm,mm] sensor width and sensor height
        },
        # Light parameters
        "light": {
            "z": [-1,1,2],                    # [m] height of the light sources
            "hor_angle": [45,90,135,180,225,270,315,360],     # [°] Horizontal angle from centre to light position
            "distance": 1,               # [m] Horizontal Euclidean distance to the center point
            "intensity": 10             # [W] Light intensity
        },
        # Render Settings
        "render": {
            "format": 'JPEG',             # Select image format: 'JPEG' or 'PNG'
            "engine": 'BLENDER_EEVEE',     # select Render Engine: 'CYCLES' or 'BLENDER_EEVEE'
            # BLENDER_EEVEE is significantly faster (real-time), CYCLES is a ray-tracing renderer
            "resolution_x": 1920,
            "resolution_y": 1080,
            "resolution_percentage": 100
        },
        # Exiftool options
        "exiftool": {
            "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ExifTool\exiftool.exe", # Path to (exiftool.exe)
            "mod": 2   # choose operating mod (1 = "immediately", 2= "aferwards" --> improve performance)
        }
    }
############################# Import functions #######################################
# import functions from external script-folder
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
    save_blender_settings,
    print_warnings,
    save_camera_data,
    create_not_evenly_distributed_cameras
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
obj.location = (params["motion"]["s0"])                         #   Set the position of the object at t=0s
#------------------------------------------------------------------------------------
# Create Output-Path
params["io"]["output_path"] = create_output_path(params["io"]["base_output_path"],params["io"]["name"])
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
image_count,camera_data = renderCameras(params,t_count,image_count,camera_data)
#------------------------------------------------------------------------------------        
# Write Exif-Tags
write_exif_tags(params["cam"],params["render"],params["io"]["output_path"],params["exiftool"])
######################################################################################

############################## Save data #############################################
#------------------------------------------------------------------------------------        
save_blender_settings(params,camera_data)
print_warnings(params)  # display warnings
######################################################################################