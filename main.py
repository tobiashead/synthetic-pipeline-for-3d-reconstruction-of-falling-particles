import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.pipeline_utils import (
    LoadDefaultSceneParameters,
    SaveSceneParameters,
    RenderImagesBlender,
    ImageDirFromCacheFile,
    CreateMeshroomFolders,
    CreateMeshroomCommand,
    PhotogrammetryMeshroom,
    WriteCacheForSubsequentEvaluation,
    LoadAppPaths
)

################################################### General Information ############################################################################
project_name = 'Moving_MS_02_3cam'  # What should be the name of the project ?
obj_moving = True                   # Does the object move?
################################################### Scene Settings #################################################################################
params = LoadDefaultSceneParameters(project_name,obj_moving) # Load standard parameters from json file
#--------------------------------------------------Adjustable parameters ---------------------------------------------------------------------------
# Object and Movement
params["motion"]["s0"] = [0, 0, 1.1]               # [m] set x,y,z position of the object at t=0s, 
params["motion"]["a"] = [0,0, -9.81]               # [m^2/s] acceleration
params["motion"]["omega"] = 360/0.092              # [°/s] angular velocity around the unit vector e (axis of rotation)
params["motion"]["e"] = [1, 0, 1]                  # [-,-,-] axis of rotation 
params["io"]["obj_path"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\Dodekaeder\Mesh-Dateien\Wuerfel_12s\centered\12s.obj"
# Camera
params["cam"]["even_dist"] = True
params["cam"]["pos_file_path"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\CamerasExtrinsicsStatic.json"
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
params["render"]["mode"] = 'MAINLY_IN_VIEW'  # Object visible on image: different modes possible --> "ALYWAYS_IN_VIEW", "MAINLY_IN_VIEW","PARTIALLY_IN_VIEW", 
#-------------------------------------------------- DO NOT CHANGE ----------------------------------------------------------------------------------
params["io"]["label_images"] = 3 if obj_moving else 1                               # how to label rendered images
if not obj_moving == False: params["motion"]["s0"] = params["cam"]["focuspoint"]    # override the location at t=0s in case of a static scene

################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
rec_params = {
    "describerDensity": "normal",     # Control the ImageDescriber density (low,medium,normal,high,ultra) --> Use ultra only on small datasets
    "describerQuality": "normal",     # Control the ImageDescriber quality (low,medium,normal,high,ultra)
    "texture_file_type": "png",       # Choose the texture file type (jpg, png)
    "InterFileExtension": ".ply",     # Extension of the intermediate file export. (‘.abc’, ‘.ply’)
    "OutputTextureSize": 16384,       # Output Texture Size (1024, 2048, 4096, 8192, 16384), (default 8192)
    "fillHoles": True,                # Fill Holes with plausible values
    "TextureDownscale": 1,             # Texture Downscale Factor (default 2), TextureSize  = OutputTextureSize/TextureDownscale
}
###################################################### Evaluation Settings #########################################################################


####################################################################################################################################################
########################################################### ROUTINE ################################################################################
####################################################################################################################################################

app_paths = LoadAppPaths()  # Load path to the applications

################################################### 1.) Data Generation ############################################################################

SaveSceneParameters(params,obj_moving)      # Save Scene Parameters into a json file
returncode_blender = RenderImagesBlender(app_paths,obj_moving)  # Start the data generation process
image_dir = ImageDirFromCacheFile()         # Get the image folder from the cache

################################################### 2.) 3D-Reconstruction with Scaling #############################################################

rec_params = CreateMeshroomFolders(rec_params,params)
command = CreateMeshroomCommand(app_paths,image_dir,rec_params)
returncode_meshroom = PhotogrammetryMeshroom(command,rec_params)
# f = SCALING()
WriteCacheForSubsequentEvaluation(params,rec_params,image_dir)

################################################### 3.) Evaluation #################################################################################



