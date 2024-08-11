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
    EvaluateCameraPoses,
    TextureEvaluation,
    SaveQuantitativeEvaluationData,
    QuantitativeEvaluationData2DataFrame
    )

################################################### Evaluate the Reconstruction ########################################################################
def EvaluateReconstruction(output_dir,evaluation_params,scaling_params,DebugMode=False,DisplayPlots=False,ImageObjectPathList = None):
    app_paths = LoadAppPaths()       # Load path to the applications
    evaluation_dir, image_dir, obj_path = GetEvaluationAndImageDirAndObjPath(output_dir,ImageObjectPathList)             
    scene_params = LoadSceneParameters(image_dir)
    PlotReconstructedObject(scene_params["io"]["name"],evaluation_dir,DisplayPlots)
    cams_rec, cams_ref = ImportCameras(output_dir,image_dir)
    obj_moving, objs, obj0 = ImportObject(image_dir)
    scaling_factor,Result_Scaling = ScaleScene(cams_rec,cams_ref,evaluation_dir,scaling_params,DisplayPlots)
    T_global = GlobalMeshRegistration(evaluation_dir,obj_path,evaluation_params["MeshRegistration"],scaling_factor,DebugMode)
    T = FineMeshRegistration(evaluation_dir,obj_path,app_paths,evaluation_params["MeshRegistration"],DebugMode)
    Result_RecMesh = EvaluateRecMesh(evaluation_dir)
    Result_SizeProperties = EvaluateSizeProperties(evaluation_dir,obj_path,T,T_global)
    Result_CameraPoses = EvaluateCameraPoses(obj_moving,cams_rec,cams_ref,objs,obj0,T,scene_params,evaluation_dir,evaluation_params["CameraPositioning"],DisplayPlots)
    TextureEvaluation(evaluation_dir,obj_path,app_paths,evaluation_params,DebugMode,DisplayPlots)
    
    evaluation_dict = {
        "ScalingFactor": Result_Scaling,
        "Mesh2MeshDistance": Result_RecMesh,
        "Morphology": Result_SizeProperties,
        "Camera": Result_CameraPoses,
        "ParamsEvo": evaluation_params,
        "ParamsScaling": scaling_params
    }
    
    SaveQuantitativeEvaluationData(evaluation_dir,evaluation_dict)
    data_frame = QuantitativeEvaluationData2DataFrame(evaluation_dict)
    return data_frame    
########################################################################################################################################################


# USING THE FILE AS MAIN FUNCTION
# If only the 3D-Reconstruction is to be initialised
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
################################################### Reconstruction Settings ########################################################################
#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
    output_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1\ParameterStudy_1_1"     # File path to the folder where the images are located
    ImageObjectPathList  = [
        r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1\ParameterStudy_1_1\Images",
        r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1\ParameterStudy_1_1\InputObject\GRAU5_centered.obj"
    ]
#---------------------------------------------------------------------------------------------------------------------------------------------------    
    DebugMode  = False                  # Activate Debug Mode
    DisplayPlots = False 
 #---------------------------------------------------------------------------------------------------------------------------------------------------       
    evaluation_params = {
        "MeshRegistration": {
                "ManualGlobalRegistration": False,
                "ThreePointRegistration":   False,
                "Recalculation":            False
            },
        "TextureEvaluation": {
            "Recalculation": False,
            "patch_size": 21,
            "levels": 256,
            "distances": 5,
            "image_number": 2,
            "features":  ["dissimilarity","correlation"]    # "contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"
        },
        "CameraPositioning": {
           "threshold": 0.005 # outlier criterion: error > treshold*(actual distance from the camera to the center of the scene)
        }       
    }
#---------------------------------------------------------------------------------------------------------------------------------------------------    
    scaling_params = {        
        "PreOutlierDetection": True,
        "threshold": 0.05,
        "criterion": "rel"      # criterion="abs","abs_norm" or "rel",
        # relative criterion: threshold = 0.07 --> 7%,    absolute normed criterion: threshold: 0.1m   --> measured on the scale of the reconstruction program --> ca. 2cm (real scale)
        # absolute criterion: treshold: 0.1m
    }
#---------------------------------------------------------------------------------------------------------------------------------------------------       
    data = EvaluateReconstruction(output_dir,evaluation_params,scaling_params,DebugMode,DisplayPlots,ImageObjectPathList)
#---------------------------------------------------------------------------------------------------------------------------------------------------    
    import matplotlib.pyplot as plt
    plt.show()   
   