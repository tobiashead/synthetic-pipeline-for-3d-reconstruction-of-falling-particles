import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.pipeline_utils import (
    LoadDefaultSceneParameters
)
from sub_pipelines.data_generation import DataGeneration
from sub_pipelines.scene_reconstruction import SceneReconstruction

################################################### General Information ############################################################################
project_name = 'GRAU5RotY'  # What should be the name of the project ?
obj_moving = True                   # Does the object move?
external_params = False             # Use Params from external parameter file
params_file_name = None             # default: None
################################################### Scene Settings #################################################################################
params = LoadDefaultSceneParameters(project_name,obj_moving,params_file_name) # Load standard parameters from json file
if external_params == False:
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
    params["render"]["mode"] = 'BBOX_CORNERS'    # "OBJECT_CENTER", "BBOX_SURFACES_CENTERS", "BBOX_CORNERS"
                                                    # --> OBJECT_CENTER = least images, BBOX_CORNERS = most images
    #-------------------------------------------------- DO NOT CHANGE ----------------------------------------------------------------------------------
    params["io"]["label_images"] = 3 if obj_moving else 1                               # how to label rendered images
    if obj_moving == False: params["motion"]["s0"] = params["cam"]["focuspoint"]    # override the location at t=0s in case of a static scene

################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
rec_params = {
    "describerDensity": "normal",     # Control the ImageDescriber density (low,medium,normal,high,ultra) --> Use ultra only on small datasets
    "describerQuality": "normal",     # Control the ImageDescriber quality (low,medium,normal,high,ultra)
    "texture_file_type": "png",       # Choose the texture file type (jpg, png)
    "InterFileExtension": ".ply",     # Extension of the intermediate file export. (‘.abc’, ‘.ply’)
    "OutputTextureSize": 16384,       # Output Texture Size (1024, 2048, 4096, 8192, 16384), (default 8192)
    "fillHoles": True,                # Fill Holes with plausible values
    "TextureDownscale": 1,            # Texture Downscale Factor (default 2), TextureSize  = OutputTextureSize/TextureDownscale
}
scaling_params = {     
    "PreOutlierDetection": True,
    "threshold": 0.05,
    "criterion": "rel"      # criterion="abs","abs_norm" or "rel",
    # relative criterion: threshold = 0.07 --> 7%,    absolute normed criterion: threshold: 0.1m   --> measured on the scale of the reconstruction program --> ca. 2cm (real scale)
    # absolute criterion: treshold: 0.1m
}
###################################################### Evaluation Settings #########################################################################


####################################################################################################################################################
########################################################### ROUTINE ################################################################################

################################################### 1.) Data Generation ############################################################################
image_dir = DataGeneration(params,obj_moving)
################################################### 2.) 3D-Reconstruction with Scaling #############################################################
output_path, scaling_factor = SceneReconstruction(rec_params,scaling_params,image_dir,scaling=False)
################################################### 3.) Evaluation #################################################################################

#PlotReconstructedObject(project_name,rec_params)

#GlobalAlignment()
#FineAlignment()

#Camera2WorldCoordinateS()
#CameraAlignmentEvaluation()

#Mesh2MeshDistance()

#TextureEvaluation()

