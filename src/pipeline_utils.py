from pathlib import Path
import json
import subprocess
import logging

def LoadDefaultSceneParameters(project_name,obj_moving,params_file_name=None,external_params = False):
    logging.info(f"Running 3D-Reconstruction pipeline: project name = {project_name}, moving object = {obj_moving}")
    logging.info('Load the default parameter set for the scene')
    if params_file_name == None or external_params == False:
        params_file_name = "params_movingO_default.json" if obj_moving else "params_fixedO_default.json"
    script_folder = Path.cwd() / "blender_pipeline"     # base file path of the script files
    params_file_path = Path(script_folder) / params_file_name
    with open(params_file_path, 'r') as file:
        params = json.load(file)
    params["io"]["name"] = project_name
    return params

def SaveSceneParameters(params,obj_moving):
    logging.info('Saves the current parameter set for the scene')
    params_file_name = "params_movingO.json" if obj_moving else "params_fixedO.json"
    script_folder = Path.cwd() / "blender_pipeline" # base file path of the script files
    params_file_path = Path(script_folder) / params_file_name
    with open(params_file_path, "w") as json_file:
        json.dump(params, json_file, indent=5)  
        
def RenderImagesBlender(app_paths,obj_moving,ConsoleOutput=False):
    blender_path = app_paths["blender_exe"]
    script_name = 'moving_object.py' if obj_moving else 'fixed_object.py'
    script_folder = Path.cwd() / "blender_pipeline"  # base file path of the script files
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
    script_folder = Path.cwd() / "blender_pipeline"  # base file path of the script files
    cache_file_path = Path(script_folder) / "cache.txt"
    with open(cache_file_path, "r") as txt_file:
        image_dir = txt_file.readline().strip()
        obj_path = txt_file.readline().strip()
    return image_dir,obj_path
        
def LoadAppPaths():
    with open(Path.cwd() / "path_settings.json", "r") as data:
        app_paths = json.load(data)
    return app_paths
   
def PrintStaticCameraPoses(image_dir,params,obj_moving,PlotCamPoses=False):
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
    if PlotCamPoses:
        logging.info("Plot static camera poses in case of a dynamic scene")
        PlotCameraPoses_DataGen(cams_ref,params,obj_moving)    
        
def PlotCameraPoses_DataGen(cams_ref,scene_params,obj_moving):
    from src.camera_pose_visualizer import CameraPoseVisualizer
    focal_length = scene_params["cam"]["focal_length"]*10**(-3)
    aspect_ratio = scene_params["cam"]["sensor_size"][0] / scene_params["cam"]["sensor_size"][1]
    sensor_width = scene_params["cam"]["sensor_size"][0]*10**(-3)
    distance = scene_params["cam"]["distance"]
    focuspoint = scene_params["cam"]["focuspoint"]
    visual_offset= 0.05
    # Plot dynamic scene / reference
    if obj_moving:
        visualizer1 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
        visualizer1.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.05,DrawCoordSystem=True,colormap='gnuplot',static_scene=False,color_based_on_height=True)
        visualizer1.load_cube(cams_ref,position=focuspoint)
        visualizer1.show() 
         
    visualizer2 = CameraPoseVisualizer([focuspoint[0]-(distance-visual_offset), focuspoint[0]+(distance-visual_offset)], [focuspoint[1]-(distance-visual_offset), focuspoint[1]+(distance-visual_offset)], [focuspoint[2]-(distance-visual_offset), focuspoint[2]+(distance-visual_offset)])
    visualizer2.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.3,DrawCoordSystem=True,static_scene=True,colorbar=True) 
    visualizer2.load_cube(cams_ref,static_scene=True,position=focuspoint)      
    visualizer2.show()
    

 