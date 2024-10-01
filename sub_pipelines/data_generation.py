import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline_utils import (
    LoadDefaultSceneParameters,
    LoadAppPaths,
    SaveSceneParameters,
    RenderImagesBlender,
    ImageDirObjectPathFromCacheFile,
    PrintStaticCameraPoses
    )

################################################### Data Generation Function ###########################################################################
def DataGeneration(params,obj_moving, DebugMode = False):
    app_paths = LoadAppPaths()                                      # Load path to the applications
    SaveSceneParameters(params,obj_moving)                          # Save Scene Parameters into a json file
    RenderImagesBlender(app_paths,obj_moving,DebugMode)  # Start the data generation process
    image_dir, obj_path = ImageDirObjectPathFromCacheFile()                             # Get the image folder from the cache
    PrintStaticCameraPoses(image_dir,params,obj_moving)
    return image_dir, obj_path
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the data creation is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')   
    ################################################### General Information ############################################################################
    project_name = 'Dynamic2Static_Test_Moving'  # What should be the name of the project ?
    obj_moving = False                   # Does the object move?
    external_params = False             # Use Params from external parameter file
    params_file_name = "params_movingO_BASECASE.JSON"    # default: None
    DebugMode  = False                  # Activate Debug Mode
    ################################################### Scene Settings #################################################################################
    params = LoadDefaultSceneParameters(project_name,obj_moving,params_file_name,external_params) # Load standard parameters from json file
    if external_params == False:
    #--------------------------------------------------Adjustable parameters ---------------------------------------------------------------------------
        # Object and Movement
        params["motion"]["s0"] = [0, 0, 1.1]               # [m] set x,y,z position of the object at t=0s, 
        params["motion"]["a"] = [0,0, -9.81]               # [m^2/s] acceleration
        params["motion"]["omega"] = 360/0.092              # [°/s] angular velocity around the unit vector e (axis of rotation)
        params["motion"]["e"] = [1, 1, 1]                  # [-,-,-] axis of rotation 
        params["io"]["obj_path"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\GRAU5.obj"
        # Camera
        params["cam"]["even_dist"] = False
        params["cam"]["pos_file_path"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\Dynamic2Static_Test_Moving\CamerasExtrinsicsStatic.json"
        params["cam"]["number"] = 3
        params["cam"]["distance"] = 0.2     # m
        params["cam"]["vert_angle"] = [0]
        params["cam"]["focuspoint"] = [0,0,1]        
        params["cam"]["fps"] = 218
        params["cam"]["sensor_size"] = [7.12, 5.33]  # [mm,mm] sensor width and sensor height
        params["cam"]["focal_length"] = 16           # [mm] focal length of all cameras
        # Rendering
        params["render"]["resolution_x"] = 2064
        params["render"]["resolution_y"] = 1544
        params["render"]["format"] = 'JPEG'          # Select image format: 'JPEG' or 'PNG'
        params["render"]["transparent"] = False      # Remove Background ? works only with PNG-format
        params["render"]["mode"] = 'BBOX_CORNERS'   # "OBJECT_CENTER", "BBOX_SURFACES_CENTERS", "BBOX_CORNERS"
                                                    # --> OBJECT_CENTER = least images, BBOX_CORNERS = most images
        #-------------------------------------------------- DO NOT CHANGE ----------------------------------------------------------------------------------
        params["io"]["label_images"] = 3 if obj_moving else 1       
        params["io"]["label_images"] = 1
        if obj_moving == False: params["motion"]["s0"] = params["cam"]["focuspoint"]    # override the location at t=0s in case of a static scene
    # Run data generation        
    DataGeneration(params,obj_moving,DebugMode)