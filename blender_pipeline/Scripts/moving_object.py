import bpy
import numpy as np
import sys
import importlib
from pathlib import Path
import json
import bpy

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
            "name": 'Moving5cam',    # project name (e.g. 'Dodekaeder')
            "obj_path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\MS_20_2\MS_22_2_wR_schw_M.obj",    # Path to the object file
            "label_images": 3               # how to label rendered images
            # 1: "{project_name}_{image_count}"
            # 2: "{project_name}_{timestep_count}_{camera_number}"
            # 3: "{project_name}_{camera_number}_{timestep_count}"
        },
        # Position and movement of the object
        "motion": {
            "s0": [0, 0, 1.1],            # [m] set x,y,z position of the object at t=0s
            "v0": [0, 0, 0],              # [m/s] velocity of the object at t=0s
            "a": [0, 0, -9.81],           # [m/s^2] acceleration of the object
            "e": [1,0,0],                 # [-,-,-] axis of rotation --> will be normalized automatically to a unit vector
            "omega": 360/0.092,           # [°/s] angular velocity around the unit vector e (axis of rotation) (full rotation 360/0.092)
            "sim_time": 5                 # [s] (max) simulation time
        },
        # Camera parameters
        "cam": {
            "even_dist": True,            # are the cameras evenly distributed, True or False
            # only necessary if even_dist = False
            "pos_file_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\camera_positions.json', # path to the file containing the camera positions
            # only necessary if even_dist = True
            "number": 5,                  # number of cameras at one level
            "focuspoint": [0,0,1],        # [m] Location of the point of focus
            "distance": 0.2,              # [m] Euclidean distance to the "focus point"
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
            "mode": 'OBJECT_CENTER',   # "OBJECT_CENTER", "BBOX_SURFACES_CENTERS", "BBOX_CORNERS"
            # --> OBJECT_CENTER = least images, BBOX_CORNERS = most images
            "transparent": False
        },
        # Exiftool options
        "exiftool": {
            "mod": 2   # choose operating mod (1 = "immediately", 2= "aferwards" --> improve performance)
        }
    }
######################################################################################
project_path = (Path(__file__).resolve()).parent.parent.parent
with open(project_path / "path_settings.json", 'r') as file:
    app_paths = json.load(file)
params["exiftool"]["path"] = app_paths["exiftool_exe"]
############################# Import functions #######################################
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
    translate_obj,
    rotate_obj,
    write_exif_tags,
    create_output_path,
    save_BlenderSettingsAndConfiguration,
    print_warnings,
    create_not_evenly_distributed_cameras,
    save_obj_state,
    is_object_in_camera_view,
    SaveObjectInWorldCoordinateOrigin
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
bpy.ops.wm.obj_import(filepath=params["io"]["obj_path"])   # Import the OBJ model
obj = bpy.context.active_object                                 # Retrieve the last imported object (this is now the active object)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')  # Recalculate the object's bounding box to update its center of mass
params["io"]["obj_path"] = SaveObjectInWorldCoordinateOrigin(obj,str(params["io"]["obj_path"]))  # Center object and save the centered object (if not already saved) 
params["motion"] = translate_obj(0,params["motion"],obj)        # Set the position of the object at t=0s
params["motion"]["e"] = (np.array(params["motion"]["e"]) / np.linalg.norm(params["motion"]["e"])).tolist() # normalize rotation vector (not necessary, but good for clarity)
obj.rotation_mode = "AXIS_ANGLE"; rotate_obj(0,params["motion"],obj)    # Set the rotation of the object at t=0s
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
#------------------------------------------------------------------------------------
# Create light sources
light_data = create_lightsources(params["light"],params["cam"]["focuspoint"])
#------------------------------------------------------------------------------------
# Translation and Rotate object in every time and render cameras
# Create a time vector for the simulation
time_vec = np.arange(0,params["motion"]["sim_time"],1/params["cam"]["fps"])

# Start simulation
image_count = 0; camera_data = []; obj_state = []; obj_in_window = False
obj_state = save_obj_state(obj_state,0,obj)     # save initial object location and orientation
for t_count, t in enumerate(time_vec):
    params["motion"] = translate_obj(t,params["motion"],obj) # translate image and get new position
    rotate_obj(t,params["motion"],obj)                       # rotate object
    if is_object_in_camera_view(obj,mode = params["render"]["mode"]):   # check if the object is visible on the images
        # Save Orientation and Position of the moving object
        obj_state = save_obj_state(obj_state,t_count,obj)
        # Rendering of all cameras in the scene
        image_count,camera_data,params = renderCameras(params,t_count,image_count,camera_data)
        obj_in_window = True
    else:   
        if obj_in_window == True: break     # In the case of a free fall (no initial velocity in positive z-direction), the object will not return to the field of view of the cameras
#------------------------------------------------------------------------------------ 
# Write Exif-Tags
if params["exiftool"]["mod"] == 2:
    write_exif_tags(params["cam"],params["render"],params["io"]["output_path"],params["exiftool"])
######################################################################################

############################## Save data #############################################      
save_BlenderSettingsAndConfiguration(params,camera_data,obj_state,light_data)
print_warnings(params)  # display warnings
######################################################################################
