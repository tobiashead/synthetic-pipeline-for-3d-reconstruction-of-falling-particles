import logging
from src.pipeline_utils import (
    LoadDefaultSceneParameters,
    LoadAppPaths,
    SaveSceneParameters,
    RenderImagesBlender,
    ImageDirObjectPathFromCacheFile,
    PrintStaticCameraPoses,
    RenderImagesBlenderMultiObjects,
    )

################################################### Data Generation Function ###########################################################################
def DataGenerationMultipleObjects(params,obj_moving, DebugMode = False, PlotCamPoses = False):
    app_paths = LoadAppPaths()                                      # Load path to the applications
    SaveSceneParameters(params,obj_moving, multiple_objects = True)                          # Save Scene Parameters into a json file
    RenderImagesBlenderMultiObjects(app_paths,obj_moving,DebugMode)  # Start the data generation process
    #image_dir, obj_path = ImageDirObjectPathFromCacheFile()                             # Get the image folder from the cache
    #PrintStaticCameraPoses(image_dir,params,obj_moving, PlotCamPoses)
    #return image_dir, obj_path
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the data creation is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')   
    ################################################### General Information ############################################################################
    project_name = 'n200_JPEG'  # What should be the name of the project ?
    external_params = False             # Use Params from external parameter file
    params_file_name = "params_movingO_BASECASE.JSON"    # default: None
    DebugMode  = False                  # Activate Debug Mode
    WriteMetadata = False                # Write metadata in the Exif-format
    ################################################### Scene Settings #################################################################################
    params = LoadDefaultSceneParameters(project_name,False, params_file_name,external_params, multiple_objects = True) # Load standard parameters from json file
    if external_params == False:
    #--------------------------------------------------Adjustable parameters ---------------------------------------------------------------------------
        # Objects
        params["objects"]["folder"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\pipeline_only_for_data_generation\synthetic_pipeline\objects\rendering_time_analyses"
        params["objects"]["number"] = 200
        params["objects"]["min_distance"] = 0.025       # minimum distance between the particles so that overlaps are avoided
        params["objects"]["crop_cylinder"] = 0.25       # reduces the size of the cylinder in which the particles are placed.
        # Cams
        params["cam"]["even_dist"] = True               # If False: --> Take camera poses from the pos_file file
        params["cam"]["pos_file_path"] = r"C:\\Users\\Tobias\\Documents\\Masterarbeit_lokal\\Base-case Datensatz\\CameraPositions_BaseCase.json"
        params["cam"]["number"] = 30                     # number of cameras per layer (scalar)
        params["cam"]["distance"] = 0.5                 # m
        params["cam"]["vert_angle"] = [0]               # vertical angle between focuspoint and camera in degree (vector)[-45,0,45]
        params["cam"]["focuspoint"] = [0,0,1]        
        params["cam"]["fps"] = 218
        params["cam"]["sensor_size"] = [7.12, 5.33]  # [mm,mm] sensor width and sensor height
        params["cam"]["focal_length"] = 16           # [mm] focal length of all cameras
        # Rendering
        params["render"]["resolution_x"] = 2064
        params["render"]["resolution_y"] = 1544
        params["render"]["format"] = 'JPEG'                  # Select image format: 'JPEG' or 'PNG'
        params["render"]["transparent"] = False               # Remove Background ? works only with PNG-format
        params["render"]["mode"] = 'BBOX_SURFACES_CENTERS'   # "OBJECT_CENTER", "BBOX_SURFACES_CENTERS", "BBOX_CORNERS"
                                                    # --> OBJECT_CENTER = least images, BBOX_CORNERS = most images
        #-------------------------------------------------- DO NOT CHANGE ----------------------------------------------------------------------------------
        # params["io"]["label_images"] = 3 if obj_moving else 1
        params["io"]["label_images"] = 1        
        params["exiftool"]["mod"] = 2 if WriteMetadata else 0
        # if obj_moving == False: params["motion"]["s0"] = params["cam"]["focuspoint"]    # override the location at t=0s in case of a static scene
    # Run data generation        
    DataGenerationMultipleObjects(params,False,DebugMode)