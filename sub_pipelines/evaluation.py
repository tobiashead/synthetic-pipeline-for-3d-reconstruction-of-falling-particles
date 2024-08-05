import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline_utils import (
    LoadAppPaths,
    LoadSceneParameters,
    GetEvaluationAndImageDirAndObjPath,
    PlotReconstructedObject,
    ImportCameras,
    ScaleScene,
    ImportObject
    )

################################################### Evaluate the Reconstruction ########################################################################
def EvaluateReconstruction(output_dir,scaling_params,DebugMode=False,imageANDobject_path = None):
    app_paths = LoadAppPaths()       # Load path to the applications
    evaluation_dir, image_dir, obj_path= GetEvaluationAndImageDirAndObjPath(output_dir,imageANDobject_path)             
    scene_params = LoadSceneParameters(image_dir)
    PlotReconstructedObject(scene_params["io"]["name"],evaluation_dir)
    cams_rec, cams_ref = ImportCameras(output_dir,image_dir)
    objs, obj0 = ImportObject(image_dir)
    scaling_factor = ScaleScene(cams_rec,cams_ref,evaluation_dir,scaling_params)
    #GlobalMeshRegistration()
    #FineMeshRegistration()
    #EvaluateRecMesh()
    #EvaluateScaling()
    #EvaluateCameraPoses()
    #EvaluateTexture()   
    
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the 3D-Reconstruction is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
    import pandas as pd
    df = pd.read_csv(r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\2\ParameterSet_1.csv")
    ind = 0
    output_dir = df.iloc[ind]["output_dir"]
    imageANDobject_path = [
        df.iloc[ind]["image_dir"],
        df.iloc[ind]["obj_path"]   
    ]
    #output_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\ParameterStudy1_0002"     # File path to the folder where the images are located
    #imageANDobject_path  = [
    #    r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1\blender_data\ParameterStudy1_0001_2",
    #    r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\GRAU5_centered.obj"
    #]
    DebugMode  = False                  # Activate Debug Mode
    scaling = True                     # Activate Scaling 
    
    scaling_params = {        
        "PreOutlierDetection": True,
        "threshold": 0.05,
        "criterion": "rel"      # criterion="abs","abs_norm" or "rel",
        # relative criterion: threshold = 0.07 --> 7%,    absolute normed criterion: threshold: 0.1m   --> measured on the scale of the reconstruction program --> ca. 2cm (real scale)
        # absolute criterion: treshold: 0.1m
    }   
    EvaluateReconstruction(output_dir,scaling_params,DebugMode,imageANDobject_path)