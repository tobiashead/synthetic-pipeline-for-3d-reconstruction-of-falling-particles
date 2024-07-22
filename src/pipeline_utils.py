from pathlib import Path
import json
import subprocess
import os
import logging

def LoadDefaultSceneParameters(project_name,obj_moving,params_file_name=None):
    logging.info(f"Running 3D-Reconstruction pipeline: project name = {project_name}, moving object = {obj_moving}")
    logging.info('Load the default parameter set for the scene')
    if params_file_name == None:
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
        
def RenderImagesBlender(app_paths,obj_moving):
    blender_path = app_paths["blender_exe"]
    script_name = 'moving_object.py' if obj_moving else 'fixed_object.py'
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    script_path = Path(script_folder) / script_name
    command = f"{blender_path} --background --python {script_path}"
    logging.info('Running the simulation and rendering of the scene in Blender')
    return_code = subprocess.run(command,text=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Completed simulation and rendering of the scene in Blender')
    return return_code
    
def ImageDirFromCacheFile():
    script_folder = Path.cwd() / "blender_pipeline" / "Scripts" # base file path of the script files
    cache_file_path = Path(script_folder) / "cache.txt"
    with open(cache_file_path) as cache_file:
        image_dir = cache_file.read()
    return image_dir

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
    return params, output_path

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

def PhotogrammetryMeshroom(command,params):
    logging.info('Start the Meshroom-Photogrammetry-Pipeline')
    log_file = Path(params["output_path"]) / 'logfile.txt'
    f = open(log_file, 'w')
    return_code = subprocess.run(command, text=True, stdout=f, stderr=subprocess.PIPE)
    logging.info('Finished the Meshroom-Photogrammetry-Pipeline')
    return return_code

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

def ImportCameras(rec_params,image_dir):
    from src.CameraProcessing import read_camera_alignment_reconstruction, read_camera_alignment_reference, match_cameras
    cams_ref = read_camera_alignment_reference(image_dir)
    logging.info('Imported reference cameras')
    try:
        output_path = rec_params["output_path"]
        cams_rec = read_camera_alignment_reconstruction(output_path)
        logging.info('Imported reconstructed cameras')
        cams_rec, cams_ref  = match_cameras(cams_rec,cams_ref)
        logging.info('Assigned reconstructed and reference cameras')
    except:
        logging.exception('Error when loading or matching the reconstructed cameras. Check if Structure From Motion step was successful')
    return cams_rec, cams_ref

def ScaleScene(cams_rec,cams_ref,rec_params,scaling_params):
    evaluation_path = rec_params["evaluation_path"]
    from src.scaling_factor import scaling_factor
    logging.info('Calculate scaling factor')
    print(f"{len(cams_rec)} of {len(cams_ref)} cameras could be reconstructed!")
    factor_mean, factor_median, factor_std, fig = scaling_factor(cams_rec,cams_ref,evaluation_path,scaling_params["PreOutlierDetection"],scaling_params["threshold"],scaling_params["criterion"],plot=False) 
    scaling = factor_median
    print(f"Scaling factor: {scaling}")
    return scaling

def PlotReconstructedObject(project_name,rec_params):
    from plot_mesh_vedo import plot_mesh_vedo
    fig,screenshot_path = plot_mesh_vedo(project_name,rec_params["evaluation_path"])
    
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