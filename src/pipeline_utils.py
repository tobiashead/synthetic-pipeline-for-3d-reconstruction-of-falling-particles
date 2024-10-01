from pathlib import Path
import json
import subprocess
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import shutil
import pandas as pd

def LoadDefaultSceneParameters(project_name,obj_moving,params_file_name=None,external_params = False):
    logging.info(f"Running 3D-Reconstruction pipeline: project name = {project_name}, moving object = {obj_moving}")
    logging.info('Load the default parameter set for the scene')
    if params_file_name == None or external_params == False:
        params_file_name = "params_movingO_default.json" if obj_moving else "params_fixedO_default.json"
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    params_file_path = Path(script_folder) / params_file_name
    with open(params_file_path, 'r') as file:
        params = json.load(file)
    params["io"]["name"] = project_name
    return params

def SaveSceneParameters(params,obj_moving):
    logging.info('Saves the current parameter set for the scene')
    params_file_name = "params_movingO.json" if obj_moving else "params_fixedO.json"
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    params_file_path = Path(script_folder) / params_file_name
    with open(params_file_path, "w") as json_file:
        json.dump(params, json_file, indent=5)  
        
def RenderImagesBlender(app_paths,obj_moving,ConsoleOutput=False):
    blender_path = app_paths["blender_exe"]
    script_name = 'moving_object.py' if obj_moving else 'fixed_object.py'
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    script_path = Path(script_folder) / script_name
    command = f"{blender_path} --background --python {script_path} --log-level -1"
    logging.info('Running the simulation and rendering of the scene in Blender')
    log_file = Path(script_folder) / 'logfile.txt'
    with log_file.open('w') as f, subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        for line in proc.stdout:
            if ConsoleOutput:
                print(line, end='')
            f.write(line); f.flush()
    proc.wait()
    logging.info('Completed simulation and rendering of the scene in Blender')
    return proc.returncode
    
def ImageDirObjectPathFromCacheFile():
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    cache_file_path = Path(script_folder) / "cache.txt"
    with open(cache_file_path, "r") as txt_file:
        image_dir = txt_file.readline().strip()
        obj_path = txt_file.readline().strip()
    return image_dir,obj_path

def CreateMeshroomFolders(params,scene_params):
    project_name = scene_params["io"]["name"]
    base_output_path = Path.cwd() / Path("meshroom_data/")
    output_path = base_output_path / project_name
    if output_path.exists():    # Check if the folder already exists
        counter = 1             # Initialize counter
        while True:             # Generate a unique folder name
            output_path_with_suffix  = base_output_path  / f"{project_name}_{counter}"  # Create the folder path with suffix
            if not output_path_with_suffix.exists():                                    # Check if the folder with suffix already exists
                output_path = output_path_with_suffix
                break    
            counter += 1        # Increment counter for the next attempt
    os.mkdir(output_path)
    cache_path = output_path / 'MeshroomCache'
    project_path = output_path / 'project.mg'
    evaluation_path = output_path / 'Evaluation'
    os.mkdir(cache_path); os.mkdir(evaluation_path)
    params["cache_path"] = cache_path; params["project_path"] = project_path
    params["evaluation_path"] = evaluation_path; params["output_path"] = output_path
    logging.info(f"Creating output folder for reconstruction: {output_path}")
    return params, output_path, evaluation_path

def CreateMeshroomCommand(app_paths,image_dir,params):
    meshroom_path = Path(app_paths["meshroom_folder"])
    command = [
    meshroom_path / 'meshroom_batch.exe',
    '--input',image_dir,
    '--output',params["evaluation_path"], # File path to the location where the textured mesh files are saved
    '--cache',params["cache_path"],
    '--save',params["project_path"],      # File path where the Meshroom-project file is saved
    '--paramO',                 # Override default Parameters of the meshroom_batch pipeline
        f'FeatureExtraction:describerPreset={params["describerDensity"]}',            # choose describer density (Feature Extraction)
        f'FeatureExtraction:describerQuality={params["describerQuality"]}',           # choose describer quality (Feature Extraction)
        'FeatureMatching:crossMatching=1',                                  # two features in both sets should match each other, It provides consistent result
#        matcher returns only those matches with value (i,j) such that i-th descriptor in set A has j-th descriptor in set B as the best match and vice-versa
        'Texturing:correctEV=0',                                            # deactivate correct Exposure, led to problems with texture creation for large datasets
        f'Texturing:colorMapping.colorMappingFileType={params["texture_file_type"]}', # choose texture file type
        f'StructureFromMotion:interFileExtension={params["InterFileExtension"]}',     # choose Strcuture from Motion Output file, (default 'abc' --> not readable by some programs )
        f'Texturing:textureSide={params["OutputTextureSize"]}',
        f'Texturing:fillHoles={params["fillHoles"]}',
        f'Texturing:downscale={params["TextureDownscale"]}'
    ]
    return command

def PhotogrammetryMeshroom(command,params,ConsoleOutput):
    logging.info('Start the Meshroom-Photogrammetry-Pipeline')
    log_file = Path(params["output_path"]) / 'logfile.txt'
    with log_file.open('w') as f, subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        for line in proc.stdout:
            if ConsoleOutput:
                print(line, end='')
            f.write(line); f.flush()
    proc.wait()
    logging.info('Finished the Meshroom-Photogrammetry-Pipeline')
    return proc.returncode

def WriteCacheForSubsequentEvaluation(scene_params,rec_params,image_dir):
    # Write a cache file in the evaluation folder so that the evaluation can be repeated at a later time.
    logging.info('Write cache file for the subsequent evaluation of the 3D reconstruction') 
    obj_path = scene_params["io"]["obj_path"]
    project_name = scene_params["io"]["name"]
    evaluation_path = Path(rec_params["evaluation_path"])
    with open((evaluation_path / "cache.txt"), 'w') as cache_file:
        cache_file.write(f"project_name: {project_name}\n")
        cache_file.write(f"image_dir: {image_dir}\n")
        cache_file.write(f"obj_path: {obj_path}\n")
        
def LoadAppPaths():
    with open(Path.cwd() / "path_settings.json", "r") as data:
        app_paths = json.load(data)
    return app_paths

def ImportCameras(output_path,image_dir):
    from src.CameraProcessing import read_camera_alignment_reconstruction, read_camera_alignment_reference, match_cameras
    cams_ref = read_camera_alignment_reference(image_dir)
    logging.info('Imported reference cameras')
    try:
        cams_rec = read_camera_alignment_reconstruction(output_path)
        logging.info('Imported reconstructed cameras')
        cams_rec, cams_ref  = match_cameras(cams_rec,cams_ref)
        logging.info('Assigned reconstructed and reference cameras')
    except:
        logging.exception('Error when loading or matching the reconstructed cameras. Check if Structure From Motion step was successful')
    return cams_rec, cams_ref

def ImportObject(image_dir):
    from src.CameraProcessing import read_object_alignment
    objs,obj0 = read_object_alignment(image_dir)
    if objs == None:
        logging.info('Static scene detected')
        obj_moving = False
    else:
        logging.info('Dynamic scene detected. Import object movmenet')
        obj_moving = True
    return obj_moving, objs, obj0

def ScaleScene(cams_rec,cams_ref,evaluation_path,scaling_params,DisplayAllPlots=False):
    from src.scaling_factor import scaling_factor
    logging.info('Calculate scaling factor')
    print(f"{len(cams_rec)} of {len(cams_ref)} cameras could be reconstructed!")
    factor_mean, factor_median, factor_std, _, number_inliers, number_outliers  = scaling_factor(cams_rec,cams_ref,evaluation_path,scaling_params["PreOutlierDetection"],scaling_params["threshold"],scaling_params["criterion"],True,DisplayAllPlots) 
    scaling = factor_median
    print(f"Scaling factor: {scaling}")
    dict_scaling = {"median": factor_median, "mean": factor_mean, "std": factor_std, "number_inliers": number_inliers, "number_outliers": number_outliers} 
    return scaling, dict_scaling

def PlotReconstructedObject(project_name,evaluation_path,DisplayPlots):
    from src.plot_mesh_vedo import plot_mesh_vedo
    fig,screenshot_path = plot_mesh_vedo(project_name,evaluation_path,DisplayPlots)
    
def PrintStaticCameraPoses(image_dir,params,obj_moving):
    from src.CameraProcessing import read_camera_alignment_reference, read_object_alignment, ExportCameras2Blender
    cams_ref = read_camera_alignment_reference(image_dir)
    objs, obj0 = read_object_alignment(image_dir)   
    focuspoint = params["cam"]["focuspoint"]
    # transformation from dynamic into static scene if object moving
    if obj_moving:
        for cam in cams_ref:
            cam.Dynamic2StaticScene(objs[cam.CorrespondigIndexObject].Transformation, obj0.Transformation,focuspoint)   
    ExportCameras2Blender(cams_ref,image_dir, static_scene = True)
    logging.info("Export static camera poses")
       
def LoadSceneParameters(image_dir):
    logging.info('Start the actual photogrammetry-pipeline:')
    image_dir = Path(image_dir)
    params_file_path = image_dir / "params.json"
    try:
        if not image_dir.exists() or not image_dir.is_dir():
             raise FileNotFoundError(f'The directory does not exist or is not a directory: {image_dir}')
        with open(params_file_path, 'r') as file:
            params = json.load(file)
        logging.info(f'Load the parameter set of the scene. Image folder: {image_dir}')
        return params
    except FileNotFoundError as e:
        logging.error(e)
        raise
    
def GetEvaluationAndImageDirAndObjPath(output_path,imageANDobject_path):
    evaluation_dir = Path(output_path) / "Evaluation"
    if not imageANDobject_path == None:
        image_dir, obj_path = imageANDobject_path
    else:
        # Get image_dir from the cache file
        variables = {}
        # Open the cache.txt file located in the evaluation_path directory in read mode
        with open((evaluation_dir / "cache.txt"), 'r') as cache_file:
            # Iterate through each line in the file
            for line in cache_file:
                # Split each line by the colon ':' to separate variable name and value
                name, value = line.strip().split(":", 1)
                # Add the variable name and value pair to the variables dictionary after stripping whitespace
                variables[name.strip()] = value.strip()
        image_dir = variables.get("image_dir", "")
        obj_path = variables.get("obj_path", "")
    return evaluation_dir, image_dir, obj_path


def GlobalMeshRegistration(evaluation_dir,obj_path,params_MeshRegis,scaling_factor,DebugMode=False):
    ManualRegistration = params_MeshRegis["ManualGlobalRegistration"]      
    ThreePointRegistration = params_MeshRegis["ThreePointRegistration"]
    Recalculation = params_MeshRegis["Recalculation"]
    
    T_global_path = evaluation_dir / 'GlobalTransformationMatrix.txt'    # Define the file path for the saved transformation matrix
    if not ((ManualRegistration or Recalculation==False) and T_global_path.exists()):
        from src.TransMatrix_Utils import Scale2Transformation4x4
        T_scale = Scale2Transformation4x4(scaling_factor)
        from src.GlobalMeshRegistration import GlobalMeshRegistration
        mesh_r_path = evaluation_dir / 'texturedMesh.obj'       
        voxel_size = 1*10**(-3)
        if DebugMode: draw_registration = 4
        else: draw_registration = 0 # choose 0,1,2,3,4 --> 0 = no plot appears --> 4 = all plots appears 
        T_global = GlobalMeshRegistration(mesh_r_path,obj_path,voxel_size,draw_registration,
                                    T_scale,ThreePointRegistration)
        np.savetxt(T_global_path,T_global)
    else:
        T_global = np.loadtxt(T_global_path)   
    return T_global
    
def FineMeshRegistration(evaluation_dir,obj_path,app_paths,params_MeshRegis,DebugMode=False): 
    Recalculation = params_MeshRegis["Recalculation"]
    log_path = evaluation_dir / "log_CloudCompare.txt"                     # Path to log file
    T_path = evaluation_dir / "TransformationMatrix.txt"
    if not (Recalculation==False and (log_path.exists() and T_path.exists())):
        cc_path = app_paths["cloudcompare_exe"]
        T_global_path = evaluation_dir / 'GlobalTransformationMatrix.txt'
        mesh_r_path = evaluation_dir / 'texturedMesh.obj'     
        # Set parameters
        save_meshes_all_at_once = False                 # Save the transformed reconstructed mesh with the Groud_truth mesh in a single file (uses a lot of hard disk space)
        silent = True                                   # No GUI pops up and no clicks necessary
        adjust_scale = True                             # Alignment of the Mesh with SCALING
        output_format_mesh = "OBJ"                      # Format can be one of the following: BIN, OBJ, PLY, STL, VTK, MA, FBX.
        # Function to align the reconstruected mesh and to calculate the Mesh to Mesh distance
        from src.FineMeshRegistration_and_MeshToMeshDistance import FineMeshRegistration_and_MeshToMeshDistance
        params_CC = [silent,save_meshes_all_at_once,adjust_scale,output_format_mesh]
        T,T_ICP,mesh_r_trans_path,log_path = FineMeshRegistration_and_MeshToMeshDistance(cc_path,params_CC,evaluation_dir,obj_path,mesh_r_path,output_format_mesh,T_global_path,DebugMode)
    else:
        T = np.loadtxt(T_path)   # load transformation matrix
    return T
        
def EvaluateRecMesh(evaluation_dir):
    # read mean distance and standard deviation from the log file
    from src.read_c2m_distance_from_log import read_c2m_distance_from_log
    log_path = evaluation_dir / "log_CloudCompare.txt"
    mean_distance, std_deviation = read_c2m_distance_from_log(log_path)
    dict_M2M = {"mean": mean_distance[1], "std": std_deviation[1]}
    return dict_M2M

def EvaluateSizeProperties(evaluation_path,object_path,T,T_global):
    from src.EvaluateVolumeSurfaceArea import EvaluateVolumeSurfaceArea
    df = EvaluateVolumeSurfaceArea(evaluation_path,object_path,T_global,T)
    dict_morphology = {
        "ref": {"volume": df.iloc[2,1], "surface": df.iloc[2,2], "surf2vol": df.iloc[2,4], "sphericity": df.iloc[2,5]},
        "rec": {"volume": df.iloc[0,1], "surface": df.iloc[0,2], "surf2vol": df.iloc[0,4], "sphericity": df.iloc[0,5]},
        "rec_CC": {"volume": df.iloc[1,1]}
    }
    return dict_morphology
    
def EvaluateCameraPoses(obj_moving,cams_rec,cams_ref,objs,obj0,T,scene_params,evaluation_dir,CamEvalParams,DisplayPlots=False):
    focuspoint = scene_params["cam"]["focuspoint"]
    # Calculate camera parameters in relation to the global coordinate system
    for i, cam in enumerate(cams_rec): cam.Transformation2WorldCoordinateSystem(T,focuspoint)
    # Calculate camera positions in the dynamic (object is moving) and the static case (object is fixed)
    for cam in cams_ref:
        if obj_moving: 
            Tdynamic2static = cam.Dynamic2StaticScene(objs[cam.CorrespondigIndexObject].Transformation, obj0.Transformation,focuspoint)
            if cam.CorrespondigIndex != None:
                cam_rec = cams_rec[cam.CorrespondigIndex]
                cam_rec.TransformationDynamic = np.linalg.inv(Tdynamic2static) @ cam_rec.TransformationStatic
        else:
            cam.TransformationDynamic = None    # delete Transformation Matrix of the dynamic case if the object is not moving 
    # Visual Evaluation
    PlotCameraPoses(cams_ref,cams_rec,scene_params,obj_moving,evaluation_dir,DisplayPlots)
    # Quantitativ evaluation of the reconstructed camera positions
    from src.CameraPositionEvaluation import CreateCameraDataSets
    pos_x,pos_y,Rx,Ry = CreateCameraDataSets(cams_rec,cams_ref)
    from src.CameraPositionEvaluation import PlotAbsPositionError_for_xyz, AbsPositionError
    PlotAbsPositionError_for_xyz(evaluation_dir,pos_x,pos_y,DisplayPlots)
    threshold = CamEvalParams["threshold"] 
    mean_error, std_deviation, mean_error_rel, outliers_count = AbsPositionError(evaluation_dir,pos_x,pos_y,outlier_criterion=threshold,DisplayPlots=DisplayPlots)
    # return results in an dict
    dict_camera = {"mean_abs_error": mean_error, "std_abs_error": std_deviation, "mean_rel_error": mean_error_rel, 
                   "images": len(cams_ref), "rec_cams": len(cams_rec), "outliers": outliers_count}
    return dict_camera
    
def PlotCameraPoses(cams_ref,cams_rec,scene_params,obj_moving,evaluation_dir,DisplayPlots):
    from src.camera_pose_visualizer import CameraPoseVisualizer
    focal_length = scene_params["cam"]["focal_length"]*10**(-3)
    aspect_ratio = scene_params["cam"]["sensor_size"][0] / scene_params["cam"]["sensor_size"][1]
    sensor_width = scene_params["cam"]["sensor_size"][0]*10**(-3)
    distance = scene_params["cam"]["distance"]
    focuspoint = scene_params["cam"]["focuspoint"]
    # Plot dynamic scene / reference
    if obj_moving: 
        visual_offset= 0.05
        visualizer1 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
        visualizer1.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.05,DrawCoordSystem=True,colormap='gnuplot',static_scene=False,color_based_on_height=True)
        visualizer1.load_cube(cams_ref,position=focuspoint)
        path = evaluation_dir / "CamsExtrinsicsRefDynamic"
        visualizer1.save(path)
        visualizer1.show(show=DisplayPlots) 
    # Plot static scene / reference
    visualizer2 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
    visualizer2.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.3,DrawCoordSystem=True,static_scene=True,colorbar=True) 
    visualizer2.load_cube(cams_ref,static_scene=True,position=focuspoint)      
    path = evaluation_dir / "CamsExtrinsicsRefStatic"
    visualizer2.save(path)
    visualizer2.show(show=DisplayPlots)
    # Comparison between reference and reconstructed cameras
    # static scene
    visualizer3 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
    visualizer3.load_cameras(cams_rec,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.3,DrawCoordSystem=True,colorbar = True,static_scene=True)
    visualizer3.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=1.5,alpha=0.5,DrawCoordSystem=True,static_scene=True)
    visualizer3.load_cube(cams_ref,static_scene=True,position=focuspoint)
    path = evaluation_dir / "CamsExtrinsicsCompareStatic"
    visualizer3.save(path)
    visualizer3.show(show=DisplayPlots)
    # Comparison between reference and reconstructed cameras
    # dynamic scene
    if obj_moving:
        visualizer4 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
        visualizer4.load_cameras(cams_rec,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.05,DrawCoordSystem=True,static_scene=False,color_based_on_height=True)
        visualizer4.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=1.5,alpha=0.1,DrawCoordSystem=True,static_scene=False,color_based_on_height=True)
        visualizer4.load_cube(cams_ref,static_scene=False,position=focuspoint)
        path = evaluation_dir / "CamsExtrinsicsCompareDynamic"
        visualizer4.save(path)
        visualizer4.show(show=DisplayPlots)
        
def TextureEvaluation(evaluation_dir,obj_path,app_paths,evaluation_params,DebugMode,DisplayPlots):
    from src.TextureEvaluation import GetImagesForTextureEvaluation, GLCM_Evaluation
    text_params = evaluation_params["TextureEvaluation"]
    # Generate Data for Texture Evaluation
    Recalculation = text_params["Recalculation"]
    blender_path = app_paths["blender_exe"]
    script_path = Path(__file__).resolve().parent.parent / "blender_pipeline/Scripts"
    mesh_r_trans_path = evaluation_dir / "texturedMesh_TRANSFORMED.obj"
    OutputTextureRef_path = evaluation_dir / "TextureReference"
    OutputTextureRec_path = evaluation_dir / "TextureReconstruction"
    if (Recalculation or not (OutputTextureRef_path.exists() and OutputTextureRec_path.exists())):
        GetImagesForTextureEvaluation(obj_path,OutputTextureRef_path,script_path,blender_path,DebugMode)
        GetImagesForTextureEvaluation(mesh_r_trans_path,OutputTextureRec_path,script_path,blender_path,DebugMode)
    # Texture Evaluation
    patch_size = text_params["patch_size"]; image_number = text_params["image_number"]; levels = text_params["levels"]; 
    distances = text_params["distances"]; features = text_params["features"]
    GLCM_Evaluation(evaluation_dir,OutputTextureRef_path,OutputTextureRec_path,patch_size,image_number,levels,distances,random_seed=124,features = features,num_windows=4,DisplayPlots=DisplayPlots)
    
def CopyDataToCaseStudyFolder(study_output_dir,output_dir,image_dir,obj_path):
    # Copy the data from the data generation and the 3D reconstruction together into a folder in the case study folder
    logging.info(f'Copy all data togehter into the case study subfolder: {study_output_dir}')
    output_dir_destination = Path(study_output_dir) / Path(output_dir).name
    shutil.copytree(output_dir, output_dir_destination)
    image_dir_destination = output_dir_destination / "Images"
    shutil.copytree(image_dir,image_dir_destination)
    destination_obj_dir = output_dir_destination / "InputObject"
    destination_obj_dir.mkdir(parents=True, exist_ok=True)
    obj_path_destination = CopyObjWithAssets(obj_path,destination_obj_dir)
    logging.info('Copying of the data completed')
    # return the relative paths
    output_dir_rel = Path(*output_dir_destination.parts[-1:])
    image_dir_rel = Path(*image_dir_destination.parts[-2:])
    obj_path_rel = Path(*obj_path_destination.parts[-3:])
    return output_dir_rel, image_dir_rel, obj_path_rel

def CopyObjWithAssets(obj_path, target_dir):
    obj_path = Path(obj_path)
    mtl_path = obj_path.with_suffix('.mtl')
    target_dir = Path(target_dir)
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    # Copy the .obj file
    obj_destination_path = target_dir / obj_path.name
    shutil.copy(obj_path, obj_destination_path)
    # Copy the .mtl file if it exists
    if mtl_path.exists():
        shutil.copy(mtl_path, target_dir / mtl_path.name)
        # Extract texture file paths from the .mtl file
        with open(mtl_path, 'r') as mtl_file:
            lines = mtl_file.readlines()
        texture_keywords = ['map_Kd', 'map_Ks', 'map_Ns', 'map_Bump', 'bump', 'map_d', 'disp', 'decal']
        for line in lines:
            for keyword in texture_keywords:
                if line.startswith(keyword):
                    texture_file = line.split()[1]
                    texture_path = obj_path.parent / texture_file
                    # Copy the texture file if it exists
                    if texture_path.exists():
                        shutil.copy(texture_path, target_dir / texture_path.name)
                    else:
                        print(f"Texture file {texture_path} not found.")
    else:
        print(f".mtl file {mtl_path} not found.")
    return obj_destination_path

def SaveQuantitativeEvaluationData(evaluation_dir,evaluation_dict):
  file_path = Path(evaluation_dir) / "QuantiativeEvaluationData.JSON"
  with open(file_path, "w") as json_file:
    json.dump(evaluation_dict, json_file, indent=5)  
    
def QuantitativeEvaluationData2DataFrame(data):

    scaling_rel_error = ((data["Morphology"]["rec"]["volume"]**(1/3)-data["Morphology"]["rec_CC"]["volume"]**(1/3)) / data["Morphology"]["rec_CC"]["volume"]**(1/3))*100
    df_data = {
        "Scaling_median": [data["ScalingFactor"]["median"]],
        "Scaling_std": [data["ScalingFactor"]["std"]],
        "Scaling_error_percent": [scaling_rel_error],
        "Mesh2MeshDist_mean": [data["Mesh2MeshDistance"]["mean"]],
        "Mesh2MeshDist_std": [data["Mesh2MeshDistance"]["std"]],
        "volume_ref": [data["Morphology"]["ref"]["volume"]],
        "volume_rec": [data["Morphology"]["rec"]["volume"]],
        "surface_ref": [data["Morphology"]["ref"]["surface"]],
        "surface_rec": [data["Morphology"]["rec"]["surface"]],
        "sphericity_ref": [data["Morphology"]["ref"]["sphericity"]],
        "sphericity_rec": [data["Morphology"]["rec"]["sphericity"]],
        "cam_mean_abs_error": [data["Camera"]["mean_abs_error"]],
        "cam_std_abs_error": [data["Camera"]["std_abs_error"]],
        "cam_outliers": [data["Camera"]["outliers"]],
        "cam_threshold": [data["ParamsEvo"]["CameraPositioning"]["threshold"]],
        "rec_cams": [data["Camera"]["rec_cams"]],
        "images": [data["Camera"]["images"]]
    }
    df = pd.DataFrame(df_data)
    return df