import bpy
import numpy as np
import sys
import importlib
from pathlib import Path
import json

######################################################################################
#                                MOVING OBJECT                                       #
######################################################################################
# Are external parameters used or the parameters defined here
ExternalParams = True

############################# Select Parameters ######################################
if ExternalParams:
    params_file_path = Path(__file__).parent / "params_movingO.json"
    # load parameters from parameter file
    with open(params_file_path, 'r') as file:
        params = json.load(file)
else:
    params = {
        # Input and output parameters
        "io": {
            "name": 'falling_dodekaeder_even_dist_15cam',    # project name (e.g. 'Dodekaeder')
            "script_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts',                            # Path of the script files
            "obj_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\12S.obj',    # Path to the object file
            "base_output_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data',                                   # Base output path
            "label_images": 3               # how to label rendered images
            # 1: "{project_name}_{image_count}"
            # 2: "{project_name}_{timestep_count}_{camera_number}"
            # 3: "{project_name}_{camera_number}_{timestep_count}"
        },
        # Position and movement of the object
        "motion": {
            "s0": [0, 0, 1.5],            # [m] set x,y,z position of the object at t=0s
            "v0": [0, 0, 0],              # [m/s] velocity of the object at t=0s
            "a": [0, 0, -9.81],           # [m/s^2] acceleration of the object
            "omega": [360*6, 0, 360*6],   # [°/s] angular velocity, rotation around x,y,z-axes (Euler-XYZ-Rotation) --> do not rotate the middle coordinate
            "sim_time": 5                 # [s] Simulation time
        },
        # Camera parameters
        "cam": {
            "even_dist": True,            # are the cameras evenly distributed, True or False
            # only necessary if even_dist = False
            "pos_file_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\camera_positions.json', # path to the file containing the camera positions
            # only necessary if even_dist = True
            "number": 5,                  # number of cameras at one level
            "z_center": 1,                # [m] Height of the "focus point"
            "distance": 0.3,              # [m] Euclidean distance to the "focus point"
            "vert_angle": [-30,0,30],            # [°] Vertical angle from centre to camera position
            # necessary, regardless of the value of even_dist 
            "focal_length": 16,           # [mm] focal length of all cameras
            "sensor_size": [7.12, 5.33],  # [mm,mm] sensor width and sensor height
            "fps": 218                    # frames (images) per seconds of each camera
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
            "resolution_x": 2064,
            "resolution_y": 1544,
            "resolution_percentage": 100
        },
        # Exiftool options
        "exiftool": {
            "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ExifTool\exiftool.exe",  # Path to (exiftool.exe)
            "mod": 2   # choose operating mod (1 = "immediately", 2= "aferwards" --> improve performance)
        }
    }
######################################################################################

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
    translate_obj,
    rotate_obj,
    write_exif_tags,
    create_output_path,
    save_blender_settings,
    print_warnings,
    save_camera_data,
    create_not_evenly_distributed_cameras
    )
# import modules from text-data block
#sys.modules["functions"] = bpy.data.texts['functions.py'].as_module()
######################################################################################
         
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
obj.location = (params["motion"]["s0"])                         # Set the position of the object at t=0s
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
# Translation and Rotate object in every time and render cameras
# Find the maximum and minimum height at which objects are visible on the cameras, valid if displacement in x and y direction is not allowed
delta_h = params["cam"]["sensor_size"][1] / params["cam"]["focal_length"] / 2 * params["cam"]["distance"]   # [m]
z_min = params["cam"]["z_center"]-delta_h; z_max = params["cam"]["z_center"] + delta_h                      # [m]

# Create a time vector for the simulation
time_vec = np.arange(0,params["motion"]["sim_time"],1/params["cam"]["fps"])

# Start simulation
image_count = 0; camera_data = []
for t_count, t in enumerate(time_vec):
    params["motion"] = translate_obj(t,params["motion"],obj) # translate image and get new position
    if params["motion"]['s'][2] <= z_max:    # check if the object is visible on the images
        if params["motion"]['s'][2]<z_min:   # check if the object is visible on the images
            break                           # if particle has already passed, then end simulation
        rotate_obj(t,params["motion"],obj)   # rotate particles (only when an image is created)
        # Rendering of all cameras in the scene
        image_count,camera_data = renderCameras(params,t_count,image_count,camera_data)
#------------------------------------------------------------------------------------ 
# Write Exif-Tags
if params["exiftool"]["mod"] == 2:
    write_exif_tags(params["cam"],params["render"],params["io"]["output_path"],params["exiftool"])
######################################################################################

############################## Save data #############################################      
save_blender_settings(params,camera_data)
print_warnings(params)  # display warnings
######################################################################################
