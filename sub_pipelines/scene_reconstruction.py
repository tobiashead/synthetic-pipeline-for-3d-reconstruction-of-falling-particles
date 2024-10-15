import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline_utils import (
    LoadAppPaths,
    LoadSceneParameters,
    CreateMeshroomFolders,
    CreateMeshroomCommand,
    PhotogrammetryMeshroom,
    ImportCameras,
    ScaleScene,
    WriteCacheForSubsequentEvaluation,
    PlotReconstructedObject
    )

################################################### Data Generation Function ###########################################################################
def SceneReconstruction(rec_params,scaling_params,image_dir,scaling=True,DebugMode=False):
    app_paths = LoadAppPaths()                                      # Load path to the applications
    ref_params = LoadSceneParameters(image_dir)
    rec_params, output_path, evaluation_path = CreateMeshroomFolders(rec_params,ref_params)
    command = CreateMeshroomCommand(app_paths,image_dir,rec_params)
    PhotogrammetryMeshroom(command,rec_params,DebugMode)
    if scaling == True:
        cams_rec, cams_ref = ImportCameras(output_path,image_dir)
        scaling_factor = ScaleScene(cams_rec,cams_ref,evaluation_path,scaling_params)
    else: scaling_factor = None
    WriteCacheForSubsequentEvaluation(ref_params,rec_params,image_dir)
    PlotReconstructedObject(ref_params["io"]["name"],rec_params["evaluation_path"],DisplayPlots=False)
    return output_path, scaling_factor
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the 3D-Reconstruction is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
    image_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\TestBaseCased09MS22"     # File path to the folder where the images are located
    DebugMode  = False                  # Activate Debug Mode
    scaling = True                      # Activate Scaling 
    
    params_rec = {
    "describerDensity": "normal",     # Control the ImageDescriber density (low,medium,normal,high,ultra) --> Use ultra only on small datasets
    "describerQuality": "normal",     # Control the ImageDescriber quality (low,medium,normal,high,ultra)
    "texture_file_type": "png",       # Choose the texture file type (jpg, png)
    "InterFileExtension": ".ply",     # Extension of the intermediate file export. (‘.abc’, ‘.ply’)
    "OutputTextureSize": 8192,        # Output Texture Size (1024, 2048, 4096, 8192, 16384), (default 8192)
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
    output_path, scaling_factor = SceneReconstruction(params_rec,scaling_params,image_dir,scaling,DebugMode)
    print(f"output path: {output_path}")