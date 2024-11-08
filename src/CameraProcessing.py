from pathlib import Path
import json
import os
import pandas as pd
import numpy as np
import importlib
import sys
importlib.reload(sys.modules['src.classes']) if 'src.classes' in sys.modules else None
from src.classes import camera_reconstructed, camera_reference, object
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4, RotationMatrix3x3_To_EulerAngles

#-----------------------------------------------------------------------
def read_camera_alignment_reconstruction(basebase_file_path_meshroom):
    # load camera data from Meshroom
    base_file_path_meshroom = Path(basebase_file_path_meshroom) / 'MeshroomCache' / 'StructureFromMotion'
    folder_name = os.listdir(base_file_path_meshroom)
    sfm_data_path =  base_file_path_meshroom / folder_name[0] / "cameras.sfm"
    if sfm_data_path.is_file():
        with open(sfm_data_path, 'r') as file:
            sfm_data = json.load(file)
        # save all camera objects in a list    
        cams_rec = []
        n_img = len(sfm_data["views"])
        n_pose = len(sfm_data["poses"])
        for i in range(n_pose):
            Pose = sfm_data["poses"][i]["pose"]["transform"]
            poseId = sfm_data["poses"][i]["poseId"]
            for j in range(n_img):
                viewId = sfm_data["views"][j]["viewId"]
                if poseId == viewId:
                    img_path = sfm_data["views"][j]["path"]
                    ImageFileName = os.path.basename(img_path)
                    break
            cam = camera_reconstructed(ImageFileName,Pose)
            cams_rec.append(cam)
    else: cams_rec = []; print("Warning: SfM-File is not existing. Reconstruction not successful.")
    return cams_rec
#-----------------------------------------------------------------------
def read_camera_alignment_reference(base_file_path_blender):
    # load camera data from blender
    cams_ref = []
    cam_pos_file_path = Path(base_file_path_blender) / "CameraPositioningInMeters.csv"
    cam_pos_blender = pd.read_csv(cam_pos_file_path)
    cam_pos_blender["TimeStep"] -= cam_pos_blender["TimeStep"][0]-1 # Adjusts the time step --> starts from 1
    for i in range(len(cam_pos_blender)):         # Iterates over all images
        cam = cam_pos_blender.iloc[i]
        ImageFileName = cam["ImageFileName"]
        TimeStep = cam["TimeStep"]
        Location = [cam["PositionX"],cam["PositionY"],cam["PositionZ"]]
        EulerAngle = [cam["RotationEulerX"],cam["RotationEulerY"],cam["RotationEulerZ"]]
        cam = camera_reference(ImageFileName,Location,EulerAngle,TimeStep)
        cam.CorrespondigIndexObject = TimeStep-1
        cam.Transformation2WorldCoordinateSystem()
        cams_ref.append(cam)
    return cams_ref
#-----------------------------------------------------------------------
def read_object_alignment(base_file_path_blender):
    objects = []
    path = Path(base_file_path_blender) / "ObjectPositioningInMeters.csv"
    if path.exists():
        obj_positions = pd.read_csv(path)
        obj_positions["TimeStep"] -= obj_positions["TimeStep"][1]-1 # Adjusts the time step --> starts from 1
        obj_positions.at[0, "TimeStep"] = 0
        for i in range(len(obj_positions)):
            obj = obj_positions.iloc[i]
            TimeStep = obj["TimeStep"]
            Location = np.array([obj["PositionX"],obj["PositionY"],obj["PositionZ"]])
            EulerAngle =  np.array([obj["RotationEulerX"],obj["RotationEulerY"],obj["RotationEulerZ"]])
            obj = object(TimeStep,Location,EulerAngle)
            obj.Transformation2WorldCoordinateSystem()
            objects.append(obj)
        return objects[1:],objects[0]    
    else: 
        return None,None 
    
#-----------------------------------------------------------------------   
def match_cameras(cams_rec,cams_ref):
    for i, cam_ref in enumerate(cams_ref):      # Iterates over all images (reference)
        for j,cam_rec in enumerate(cams_rec):       # For each reference camera find the corresponding reconstructed camera using the image file name as comparator 
            if cam_rec.ImageFileName == cam_ref.ImageFileName:
                cam_ref.CorrespondigIndex = j;   cam_rec.CorrespondigIndex = i    # Save the mapping of the images
                cam_rec.TimeStep = cam_ref.TimeStep
                cams_ref[i] = cam_ref; cams_rec[j] = cam_rec;     
                break
    return cams_rec, cams_ref  
#-----------------------------------------------------------------------
def ExportCameras2Blender(cams,evaluation_path, static_scene = True):
    data = {}
    for i,cam in enumerate(cams):
        T = cam.TransformationStatic if static_scene else cam.TransformationDynamic
        location, rotation, scale = Get_Location_Rotation3x3_Scale_from_Transformation4x4(T)
        euler_angle = np.longdouble(RotationMatrix3x3_To_EulerAngles(rotation))
        # transformation of camera coordinate plot convention into Blender camera coordinate convention 
        euler_angle[0] += np.pi
        key = "camera" + str(i+1)
        data[key] = {
            "name": key,
            "image": cam.ImageFileName, 
            "x_m": float(location[0]),
            "y_m": float(location[1]),
            "z_m": float(location[2]),
            "theta_x": float(euler_angle[0]),
            "theta_y": float(euler_angle[1]),
            "theta_z": float(euler_angle[2])
        }
    # Speichere die aktualisierten Daten in die JSON-Datei
    if static_scene:
        json_path  = Path(evaluation_path) / "CamerasExtrinsicsStatic.json"
    else:
         json_path  = Path(evaluation_path) / "CamerasExtrinsicsDynamic.json"
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
#-----------------------------------------------------------------------
def read_light_alignment(base_file_path_blender):
    lights = pd.read_csv(Path(base_file_path_blender) / "LightPositioningInMeters.csv")
    return lights
