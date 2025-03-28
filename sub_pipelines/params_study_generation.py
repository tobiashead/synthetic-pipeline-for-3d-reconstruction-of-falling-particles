import logging
import itertools
import os
import csv
from pathlib import Path
import time
import numpy as np
import sys

#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline_utils import (
    LoadDefaultSceneParameters,
    CopyDataToCaseStudyFolder,
    calculate_angular_velocity_from_fov_angle_diff
)
from sub_pipelines.data_generation import DataGeneration
from sub_pipelines.scene_reconstruction import SceneReconstruction

################################################### General Information ############################################################################
project_name = 'Frames_3cam_rotY400_ObjectCenter2'  # What should be the name of the project ?
obj_moving = True                   # Does the object move?
external_params = False             # Use Params from external parameter file
params_file_name = None             # default: None
fov_difference_angle = 400          # default: None, e.g. 360,  If activated, the angular velocity is determined as a function of the difference angle in the field of view of the cameras

study_output_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\Frames_3cam_rotY400_ObjectCenter2"

################################################### Scene Settings #################################################################################
params = LoadDefaultSceneParameters(project_name,obj_moving,params_file_name) # Load standard parameters from json file
if external_params == False:
#--------------------------------------------------Adjustable parameters ---------------------------------------------------------------------------
    # Object and Movement
    params["motion"]["s0"] = [0, 0, 1.2]               # [m] set x,y,z position of the object at t=0s, 
    params["motion"]["a"] = [0,0, -9.81]               # [m^2/s] acceleration
    params["motion"]["omega"] = 360/0.0797763773682944             # [°/s] angular velocity around the unit vector e (axis of rotation)
    params["motion"]["e"] = [1, 1, 1]                  # [-,-,-] axis of rotation 
    # Camera
    params["cam"]["even_dist"] = True
    params["cam"]["pos_file_path"] = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_pipeline\Scripts\CamerasExtrinsicsStatic.json"
    params["cam"]["number"] = 3
    params["cam"]["distance"] = 0.4     # m
    params["cam"]["vert_angle"] = [0]
    params["cam"]["focuspoint"] = [0,0,1]        
    params["cam"]["fps"] = 218
    params["cam"]["sensor_size"] = [7.12, 5.33]  # [mm,mm] sensor width and sensor height
    params["cam"]["focal_length"] = 16           # [mm] focal length of all cameras
    # Rendering
    params["render"]["resolution_x"] = 2064
    params["render"]["resolution_y"] = 1544
    params["render"]["format"] = 'PNG'             # Select image format: 'JPEG' or 'PNG'
    params["render"]["transparent"] = True         # Remove Background ? works only with PNG-format
    params["render"]["mode"] = 'OBJECT_CENTER'       # "OBJECT_CENTER", "BBOX_SURFACES_CENTERS", "BBOX_CORNERS"
                                                    # --> OBJECT_CENTER = least images, BBOX_CORNERS = most images
    #-------------------------------------------------- DO NOT CHANGE ----------------------------------------------------------------------------------
    params["io"]["label_images"] = 3 if obj_moving else 1                               # how to label rendered images
    if obj_moving == False: params["motion"]["s0"] = params["cam"]["focuspoint"]    # override the location at t=0s in case of a static scene

#------------------------------------------------- Adjustable parameters ---------------------------------------------------------------------------
rec_params = {
    "describerDensity": "normal",     # Control the ImageDescriber density (low,medium,normal,high,ultra) --> Use ultra only on small datasets
    "describerQuality": "normal",     # Control the ImageDescriber quality (low,medium,normal,high,ultra)
    "texture_file_type": "png",       # Choose the texture file type (jpg, png)
    "InterFileExtension": ".ply",     # Extension of the intermediate file export. (‘.abc’, ‘.ply’)
    "OutputTextureSize": 8192,       # Output Texture Size (1024, 2048, 4096, 8192, 16384), (default 8192)
    "fillHoles": True,                # Fill Holes with plausible values
    "TextureDownscale": 1,            # Texture Downscale Factor (default 2), TextureSize  = OutputTextureSize/TextureDownscale
}

# Which parameters should be varied? how often should the simulation be repeated?
# 1) cam_distance
# cam_distances = [0.1, 0.2, 0.3]  # distance between the cam and the focus point
# # 2) number cameras
# cam_numb  = [3, 4, 5]           # number of cameras (in one layer)
# # 3) rotation axis
# rotation_axis = [[1,0,0], [1,1,1]]
# # 4) angular velocities
# omega = [1500,3000,4500]
# # 5)
# s0 = [1.15, 1.1, 1.05] 
# # 6) obejects
# objects = [
#     {"name": "GRAU5", "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\centered\GRAU5.obj"},
#     {"name": "BP_2", "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\BP_02\centered\BP_2_Model.obj"},
#     {"name": "MS_22", "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\MS_20_2\centered\MS_22_2_wR_schw_M.obj"}
# ]
# 7) repetition
#reps = [1,2,3]
cam_numb = [3]
#cam_distances = [0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2]
cam_distances = [0.4]
rotation_axis = [[0,1,0]]
omega = [0]
s0 = [[0,0,1.2]]
objects = [
     {"name": "GRAU5", "path": r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\GRAU5\GRAU5.obj"}
] 
cam_fps = [90, 105, 120, 145, 175, 220, 290, 365, 440, 585, 730, 880, 1027]
#cam_fps = [218]
reps = [1,2,3]

# Create Parameter Sets (Combinations of all variables)
variables = [cam_distances,cam_numb,rotation_axis,omega,s0,cam_fps,objects,reps]
variable_names = ["cam_distance","cam_number","motion_e","motion_omega","motion_s0","cam_fps","object","reps"] # Idea how I can automate this ?
#----------------------------------------------------------------------------------------------------------------------------------
# create OutputFolder
study_output_dir


combinations = list(itertools.product(*variables))
n_combinations = len(combinations)

# Create a CSV file to save all parameter combinations and the image- and output folder path 
csv_file_name = 'ParameterSet.csv'
csv_file_path = Path(study_output_dir) / csv_file_name
file_exists = os.path.isfile(csv_file_path)
# Open CSV-file
if not file_exists:
    with open(csv_file_path, 'a', newline='') as file: csv.writer(file).writerow(variable_names + ["rec_time","output_dir", "image_dir","obj_path"])
    initial_case = 0
else:
    with open(csv_file_path, 'r') as csv_datei:
        reader = csv.reader(csv_datei)
        line_number = sum(1 for row in reader)
        initial_case = line_number - 1        
# Create a runtime vector
runtime_vector = []
total_remaining_running_time = -1*3600
#----------------------------------------------------------------------------------------------------------------------------------
# File generation and reconstruction for all parameter sets
print("########################################################")
print(f"Start simulation with {n_combinations} parameter sets")
start_time_overall = time.time()
for i in range(initial_case,n_combinations):
    com = combinations[i]
    print(f"Start simulation with parameter set {i+1}/{n_combinations}. Estimated remaining total running time: {total_remaining_running_time/3600:.2f} hours")
    var1,var2,var3,var4,var5,var6,var7,var8 = com
    params["cam"]["distance"] = var1
    params["cam"]["number"] = var2
    params["motion"]["e"] = var3
    params["motion"]["s0"] = var5
    if fov_difference_angle: var4 =  calculate_angular_velocity_from_fov_angle_diff(params["cam"]["distance"], fov_difference_angle,
                                                                                     params["cam"]["focuspoint"], params["motion"]["s0"], 
                                                                                     params["motion"]["a"], params["motion"]["v0"], params["cam"])
    params["motion"]["omega"] = var4 
    params["io"]["obj_path"] = var7["path"]
    params["cam"]["fps"] = var6
    params["io"]["name"] = project_name + "_" + str(i+1)
    
    start_time_iteration = time.time()
    image_dir, obj_path = DataGeneration(params,obj_moving)
    start_time_rec = time.time()
    output_dir, scaling_factor = SceneReconstruction(rec_params,None,image_dir,scaling=False,DebugMode=False,SaveImagesObj = False)
    duration_rec = time.time()-start_time_rec
    
    output_dir_rel, image_dir_rel, obj_path_rel = CopyDataToCaseStudyFolder(study_output_dir,output_dir,image_dir,obj_path)
    runtime_vector.append(time.time() - start_time_iteration)
    
    with open(csv_file_path, 'a', newline='') as file: 
        csv.writer(file).writerow([var1, var2, var3, var4, var5, var6, var7["name"], var8, duration_rec ,output_dir_rel, image_dir_rel, obj_path_rel])
    total_remaining_running_time = np.median(np.array(runtime_vector))*(n_combinations-(i+1))
    print("-------------------------------------------------")
print(f"End simulation with {n_combinations} parameter sets. Total running time: {((time.time()-start_time_overall)/3600):.2f} hours")
#----------------------------------------------------------------------------------------------------------------------------------
