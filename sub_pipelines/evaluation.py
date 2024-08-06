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
    ImportObject,
    GlobalMeshRegistration,
    FineMeshRegistration,
    EvaluateRecMesh,
    EvaluateSizeProperties,
    EvaluateCameraPoses
    )

################################################### Evaluate the Reconstruction ########################################################################
def EvaluateReconstruction(output_dir,evaluation_params,scaling_params,DebugMode=False,DisplayPlots=False,imageANDobject_path = None):
    app_paths = LoadAppPaths()       # Load path to the applications
    evaluation_dir, image_dir, obj_path = GetEvaluationAndImageDirAndObjPath(output_dir,imageANDobject_path)             
    scene_params = LoadSceneParameters(image_dir)
    PlotReconstructedObject(scene_params["io"]["name"],evaluation_dir,DisplayPlots)
    cams_rec, cams_ref = ImportCameras(output_dir,image_dir)
    obj_moving, objs, obj0 = ImportObject(image_dir)
    scaling_factor = ScaleScene(cams_rec,cams_ref,evaluation_dir,scaling_params,DisplayPlots)
    T_global = GlobalMeshRegistration(evaluation_dir,obj_path,evaluation_params["MeshRegistration"],scaling_factor,DebugMode)
    T = FineMeshRegistration(evaluation_dir,obj_path,app_paths,evaluation_params["MeshRegistration"],DebugMode)
    M2M_Distance = EvaluateRecMesh(evaluation_dir)
    EvaluateSizeProperties(evaluation_dir,obj_path,T,T_global)
    EvaluateCameraPoses(obj_moving,cams_rec,cams_ref,objs,obj0,T,scene_params,evaluation_dir,DisplayPlots)
    #EvaluateTexture()   
    
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the 3D-Reconstruction is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
    #output_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\ParameterStudy1_0002"     # File path to the folder where the images are located
    #imageANDobject_path  = [
    #    r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1\blender_data\ParameterStudy1_0001_2",
    #    r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\GRAU5_centered.obj"
    #]
    DebugMode  = False                  # Activate Debug Mode
    DisplayPlots = False 
    evaluation_params = {
        "MeshRegistration": {
                "ManualGlobalRegistration": False,
                "ThreePointRegistration":   False,
                "Recalculation":            False
            }        
    }
    scaling_params = {        
        "PreOutlierDetection": True,
        "threshold": 0.05,
        "criterion": "rel"      # criterion="abs","abs_norm" or "rel",
        # relative criterion: threshold = 0.07 --> 7%,    absolute normed criterion: threshold: 0.1m   --> measured on the scale of the reconstruction program --> ca. 2cm (real scale)
        # absolute criterion: treshold: 0.1m
    }   
    import pandas as pd
    df = pd.read_csv(r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\2\ParameterSet_1.csv")
     #ind = 0
    for ind in range (len(df)):
        output_dir = df.iloc[ind]["output_dir"]
        imageANDobject_path = [
            df.iloc[ind]["image_dir"],
            df.iloc[ind]["obj_path"]   
        ]
        EvaluateReconstruction(output_dir,evaluation_params,scaling_params,DebugMode,DisplayPlots,imageANDobject_path)
   