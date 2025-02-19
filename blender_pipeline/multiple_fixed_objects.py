import bpy
import numpy as np
import sys
import importlib
from pathlib import Path
import json
import random
import time

######################################################################################
#                                Multiple Fixed Objects                              #
######################################################################################
# Are external parameters used or the parameters defined here
ExternalParams = True

############################# Select Parameters ######################################
if ExternalParams:
    params_file_path = Path(__file__).parent / "params_multiple_fixedO.json"
    # load parameters from parameter file
    with open(params_file_path, 'r') as file:
        params = json.load(file)
else:
    params = {
        # Input and output parameters
        "io": {
            "name": 'Test',    # project name (e.g. 'Dodekaeder'),
            "obj_path": "must remain",
            "label_images": 1               # how to label rendered images
            # 1: "{project_name}_{image_count}"
            # 2: "{project_name}_{timestep_count}_{camera_number}"
            # 3: "{project_name}_{camera_number}_{timestep_count}"
        },
        # Objects and objectgrid
        "objects": {
            "folder": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\pipeline_only_for_data_generation\synthetic_pipeline\objects",
            "number": 3,
            "min_distance": 0.02,    # minimum distance between the particles so that overlaps are avoided
            "crop_cylinder": 0.25    # reduces the size of the cylinder in which the particles are placed.
        },
        # Camera parameters
        "cam": {
            "even_dist": True,            # are the cameras evenly distributed, True or False
            # only necessary if even_dist = False
            "pos_file_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\camera_positions.json', # path to the file containing the camera positions
            # only necessary if even_dist = True
            "number": 4,                  # number of cameras at one level
            "focuspoint": [0,0,1],        # [m] Location of the point of focus
            "distance": 0.4,              # [m] Euclidean distance to the "focus point"
            "vert_angle": [0],            # [°] Vertical angle from centre to camera position
            # necessary, regardless of the value of even_dist 
            "focal_length": 16,           # [mm] focal length of all cameras
            "sensor_size": [7.12, 5.33],  # [mm,mm] sensor width and sensor height
            "fps": 218                    # frames (images) per seconds of each camera
        },
        # Light parameters
        "light": {
            "z": [0.8,1.2],                # [m] height of the light sources
            "hor_angle": [45,135,215,305],     # [°] Horizontal angle from centre to light position
            "distance": 0.2,                # [m] Horizontal Euclidean distance to the center point
            "intensity": 10               # [W] Light intensity
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
            "mod": 0            # choose operating mode (0 = "off", 1 = "immediately", 2= "aferwards" --> improve performance)
        }
    }
######################################################################################
project_path = (Path(__file__).resolve()).parent.parent
with open(project_path / "path_settings.json", 'r') as file:
    app_paths = json.load(file)
params["exiftool"]["path"] = app_paths["exiftool_exe"]
############################# Import functions #######################################
# import functions from external script-folder
params["io"]["script_path"] = str(project_path / "blender_pipeline")
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
    set_render_settings,
    check_exiftool_connection,
    move_objects_to_initial_position,
    rotate_objects_randomly,
    generate_random_positions_cylinder,
    calculate_image_size
    )

# Check if communication with Exif-Tool is working
check_exiftool_connection(params["exiftool"])

# import modules from text-data block
#sys.modules["functions"] = bpy.data.texts['functions.py'].as_module()
######################################################################################
         
############################# Simulation routine #####################################
random.seed(42*params["objects"]["number"]) # Seed for random generator. Unique for number of objects
#------------------------------------------------------------------------------------
# Clear all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
#------------------------------------------------------------------------------------
# import objects
obj_folder = params["objects"]["folder"]  
obj_paths = [str(file) for file in Path(obj_folder).glob("*.obj")]
objs = []
n_obj = params["objects"]["number"]
for i in range(n_obj):
    bpy.ops.wm.obj_import(filepath=str(random.choice(obj_paths)))
    obj = bpy.context.active_object    
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
    objs.append(obj)
#------------------------------------------------------------------------------------    
# set initial position and rotation of objects
x_fp = params["cam"]["focuspoint"]
crop_cylinder = params["objects"]["crop_cylinder"]
image_size = calculate_image_size(params)

dr = image_size[0]/2*(1-crop_cylinder); dz = image_size[1]/2*(1-crop_cylinder)
bounds = ((x_fp[2]-dz,x_fp[2]+dz), dr)
positions = generate_random_positions_cylinder(n_obj, bounds, min_distance=params["objects"]["min_distance"])
move_objects_to_initial_position(objs, positions)
rotate_objects_randomly(objs)
#------------------------------------------------------------------------------------
# Create Output-Path
params["io"]["output_path"] = create_output_path(project_path,params["io"]["name"])
#------------------------------------------------------------------------------------
# Create cameras
if params["cam"]["even_dist"] == True:
    create_evenly_distributed_cameras(params["cam"])
    cam2fp_dis = params["cam"]["distance"] * np.ones([params["cam"]["number"]*len(params["cam"]["vert_angle"]),1]) # calculate the distances between the cameras and the point of focuse
else: 
    cam2fp_dis = create_not_evenly_distributed_cameras(params["cam"])
# Set render settings
set_render_settings(params["render"])    
#------------------------------------------------------------------------------------
# Create light sources
light_data = create_lightsources(params["light"],params["cam"]["focuspoint"])
#------------------------------------------------------------------------------------
# Rendering of all cameras in the scene
image_count = 0; t_count = 0; camera_data = []
start_time = time.time()  # Record start time
image_count,camera_data,params = renderCameras(params,t_count,image_count,camera_data)
execution_time = time.time() - start_time  # Calculate duration
execution_time_per_frame = execution_time / image_count
#------------------------------------------------------------------------------------        
# Write Exif-Tags
if params["exiftool"]["mod"] == 2:
    write_exif_tags(params["cam"],params["render"],params["io"]["output_path"],params["exiftool"])
######################################################################################

############################## Save data #############################################
#------------------------------------------------------------------------------------        
save_BlenderSettingsAndConfiguration(params,camera_data,None,light_data,execution_time_per_frame)
print_warnings(params)  # display warnings
######################################################################################
