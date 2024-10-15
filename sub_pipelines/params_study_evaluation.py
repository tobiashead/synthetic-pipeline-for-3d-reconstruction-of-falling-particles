import logging
import os
import sys
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sub_pipelines.evaluation import EvaluateReconstruction

################################################### General Information ############################################################################

params_study_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\1"
DisplayPlots = False 
DebugMode  = False                  # Activate Debug Mode

################################################### Evaluation Settings #############################################################################

evaluation_params = {
    "MeshRegistration": {
            "ManualGlobalRegistration": False,
            "ThreePointRegistration":   False,
            "Recalculation":            False
        },
    "TextureEvaluation": {
        "active": False,
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

############################################################# Loop #################################################################################
if DebugMode: logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
params_study_dir = Path(params_study_dir)
ParameterSetsFile = params_study_dir / "ParameterSet.csv"
result_filepath = params_study_dir / "EvaluationParameterStudy.csv"
ParameterSets = pd.read_csv(ParameterSetsFile)
print("########################################################")
print(f"Start evaluation with {len(ParameterSets)} parameter sets")
for i,ParameterSet in ParameterSets.iterrows():
    print(f"Start evaluation with parameter set {i+1}/{len(ParameterSets)}")
    output_dir = Path(params_study_dir) / ParameterSet["output_dir"]
    ImageObjectPathList = [params_study_dir / ParameterSet["image_dir"], params_study_dir / ParameterSet["obj_path"]]
    data,_ = EvaluateReconstruction(output_dir,evaluation_params,scaling_params,DebugMode,DisplayPlots,ImageObjectPathList)
    if i == 0:
        df_params_study = data
    else:
        df_params_study = pd.concat([df_params_study, data], ignore_index=True)
    df_params_study.to_csv(result_filepath, index=False)
    plt.close("all")
    print("-------------------------------------------------")