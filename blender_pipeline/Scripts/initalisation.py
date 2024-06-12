import bpy
import sys
import importlib

######################################################################################
#                                Initialisation                                      #
######################################################################################

############################# Select Parameters ######################################
#"obj_path": Path("C:/Users/Tobias/Documents/Masterarbeit_lokal/synthetic_pipeline/blender_pipeline/3D_Dice/3D_Dice.obj")
params = {
    # Input and output parameters
    "io": {
        "script_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts',                    # Path of the script files
        "obj_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\12S.obj',    # Path to the object file
        #"obj_path": Path("C:/Users/Tobias/Documents/Masterarbeit_lokal/synthetic_pipeline/blender_pipeline/3D_Dice/3D_Dice.obj")
    },
    # Position and movement of the object
    "motion": {
        "s0": [0, 0, 1],            # [m] set x,y,z position of the object at t=0s
    },
    # Camera parameters
    "cam": {
        "even_dist": True,            # are the cameras evenly distributed, True or False
        # only necessary if even_dist = False
        "pos_file_path": r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\camera_positions.json', # path to the file containing the camera positions
        # only necessary if even_dist = True
        "number": 3,                  # number of cameras at one level
        "focuspoint": [0,0,1],        # [m] Location of the point of focus
        "distance": 0.2,              # [m] Euclidean distance to the "center point"
        # necessary, regardless of the value of even_dist 
        "vert_angle": [0],            # [°] Vertical angle from centre to camera position
        "focal_length": 16,           # [mm] focal length of all cameras
        "sensor_size": [7.12,5.33]    # [mm,mm] sensor width and sensor height
    },
    # Light parameters
    "light": {
        "z": [1],                    # [m] height of the light sources
        "hor_angle": [165, 345],     # [°] Horizontal angle from centre to light position
        "distance": 1,               # [m] Horizontal Euclidean distance to the center point
        "intensity": 100             # [W] Light intensity
    },
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
    create_not_evenly_distributed_cameras,
    rotate_obj
)
# import modules from text-data block
#sys.modules["functions"] = bpy.data.texts['functions.py'].as_module()
######################################################################################
         
############################# Initialisation routine #################################
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
params["motion"]["e"] = [0,0,0]; params["motion"]["omega"] = 0
rotate_obj(0,params["motion"],obj) # Set the rotation of the object at t=0s
#------------------------------------------------------------------------------------
# Create cameras
create_evenly_distributed_cameras(params["cam"])
#------------------------------------------------------------------------------------
# Create light sources
create_lightsources(params["light"],params["cam"]["focuspoint"])
######################################################################################
