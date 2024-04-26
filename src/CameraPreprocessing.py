from pathlib import Path
import json
import os
import pandas as pd
import numpy as np
import importlib
import sys
importlib.reload(sys.modules['src.object_classes']) if 'src.object_classes' in sys.modules else None
from src.object_classes import camera_reconstructed, camera_reference, object

#-----------------------------------------------------------------------
def read_camera_alignment_reconstruction(basebase_file_path_meshroom):

    # load camera data from Meshroom
    base_file_path_meshroom = Path(basebase_file_path_meshroom) / 'MeshroomCache' / 'StructureFromMotion'
    folder_name = os.listdir(base_file_path_meshroom)
    sfm_data_path =  base_file_path_meshroom / folder_name[0] / "cameras.sfm"
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
        cam.Transformation2WorldCoordinateSystem()
        cams_ref.append(cam)
    return cams_ref
#-----------------------------------------------------------------------
def read_object_alignment(base_file_path_blender):
    objects = []
    obj_positions = pd.read_csv(Path(base_file_path_blender) / "ObjectPositioningInMeters.csv")
    obj_positions["TimeStep"] -= obj_positions["TimeStep"][1]-1 # Adjusts the time step --> starts from 1
    obj_positions.at[0, "TimeStep"] = 0
    for i in range(len(obj_positions)):
        obj = obj_positions.iloc[i]
        TimeStep = obj["TimeStep"]
        Location = np.array([obj["PositionX"],obj["PositionY"],obj["PositionZ"]])
        EulerAngle =  np.array([obj["RotationEulerX"],obj["RotationEulerY"],obj["RotationEulerZ"]])
        obj = object(TimeStep,Location,EulerAngle)
        if i!= 0:
             obj.CorrespondingIndex = i+1  
        obj.Transformation2WorldCoordinateSystem()
        objects.append(obj) 
    return objects[1:],object[0]

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