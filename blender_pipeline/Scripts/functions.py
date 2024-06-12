import bpy
import mathutils
import math
import numpy as np
from pathlib import Path
import subprocess
import csv
import json

# File: functions.py

############################# Define Functions #######################################
#------------------------------------------------------------------------------------
# Create cameras with evenly distributed angles
def create_evenly_distributed_cameras(cam):
    number_cameras = cam["number"]; focuspoint = cam["focuspoint"]; camera_distance = cam["distance"]
    vert_angle = cam["vert_angle"]; focal_length = cam["focal_length"]; sensor_size = cam["sensor_size"]
    camera_data = []; j = 0
    relative_angle = 360 / number_cameras
    for angle in vert_angle:
        v_distance = math.sin(math.radians(angle))*camera_distance + focuspoint[2]
        h_distance = math.cos(math.radians(angle))*camera_distance
        for i in range(number_cameras):
            
            hori_angle = relative_angle * i
            
            # Set the camera location and target location based on camera_angle
            camera_location = mathutils.Vector((h_distance * math.cos(math.radians(hori_angle)), h_distance * math.sin(math.radians(hori_angle)), v_distance))
            target_location = mathutils.Vector(focuspoint)
            
            # Calculate the direction vector and create the rotation quaternion
            direction = -(target_location - camera_location).normalized()
            rot_quat = direction.to_track_quat('Z', 'Y')
            
            # Create a new camera
            bpy.ops.object.camera_add(location=camera_location, rotation=rot_quat.to_euler())
            
            # Adjust camera settings
            bpy.context.object.data.type = 'PERSP'
            bpy.context.object.data.lens = focal_length  # Adjust focal length
            bpy.context.object.data.sensor_width = sensor_size[0]
            bpy.context.object.data.sensor_height = sensor_size[1]
#------------------------------------------------------------------------------------
# Create light sources
def create_lightsources(light,focuspoint = [0,0,1]):
    z_light = light["z"]; hori_angle = light["hor_angle"]
    light_distance = light["distance"]; light_intensity = light["intensity"]
    for h_angle in hori_angle:
        for z in z_light:
            
            # Set the light source location
            light_location = mathutils.Vector((light_distance * math.cos(math.radians(h_angle))+focuspoint[0], light_distance * math.sin(math.radians(h_angle))+focuspoint[1], z))
            
            # Create a new camera
            bpy.ops.object.light_add(type='POINT', location=light_location)
            
            # Set light properties
            light = bpy.context.active_object
            light.data.energy = light_intensity  # Intensity of the light
#------------------------------------------------------------------------------------
def renderCameras(params,t_count,image_count,camera_data):
    output_path = Path(params["io"]["output_path"]); project_name = params["io"]["name"]; label_images = params["io"]["label_images"]
    image_format = params["render"]["format"]; render_engine = params["render"]["engine"]
    resolution_x = params["render"]["resolution_x"]; resolution_y = params["render"]["resolution_y"]
    resolution_percentage = params["render"]["resolution_percentage"];  transparent = params["render"]["transparent"]
    if transparent:
        if image_format == "JPEG": 
            image_format = "PNG"; params["render"]["format"] = image_format; 
            print("Warning! JPEG format does not support transparency! Change image format from JPEG to PNG")
    # Render settings
    bpy.context.scene.render.image_settings.file_format = image_format
    if transparent: bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.film_transparent = transparent
    bpy.context.scene.render.engine = render_engine
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.context.scene.render.resolution_percentage = resolution_percentage
    
    # Iterate through all cameras and render
    camera_number = 0
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            output_file_suffix = output_file_suffix = 'jpg' if image_format == 'JPEG' else 'png'
            # Use the camera name as part of the file name
            camera_number += 1
            image_count += 1
            if label_images == 3:
                file_name = f"{project_name}_c{camera_number:04d}_t{t_count}.{output_file_suffix}"
            elif label_images == 2:
                file_name = f"{project_name}_t{t_count}_c{camera_number:04d}.{output_file_suffix}"
            else:
                file_name = f"{image_count:04d}.{output_file_suffix}"
            image_path = str(output_path / file_name)
            bpy.context.scene.render.filepath = image_path
            bpy.ops.render.render(animation=False,write_still=True)
            # write_exif_tags
            if params["exiftool"]["mod"] == 1:
                focal_length = obj.data.lens
                sensor_size = [obj.data.sensor_width,obj.data.sensor_height]
                write_exif_tags(params["cam"],params["render"],image_path,params["exiftool"])
            # save camera position and rotation
            camera_data = save_camera_data(obj,camera_data,file_name,t_count)

    return image_count, camera_data, params
#------------------------------------------------------------------------------------
# Translate the object
def translate_obj(t,motion,obj):
    a = mathutils.Vector(motion['a']); v0 = mathutils.Vector(motion['v0'])
    s0 = mathutils.Vector(motion['s0'])
    s = a / 2 * t**2 + v0 * t + s0
    obj.location = s; motion['s'] = list(s)
    return motion
#------------------------------------------------------------------------------------  
# Rotate the object: 
def rotate_obj(t,motion,obj):
    # using axis-angle-representation
    e = motion['e']                 # [-,-,-] axis of rotation (normalized)
    omega = motion['omega']         # [°/s] angular velocity
    theta = math.radians(omega)*t   # [rad] rotation angle (omega(t=0s) = 0)
    obj.rotation_axis_angle[0] = theta # set rotation angle
    obj.rotation_axis_angle[1] = e[0]  # set x-component of the axis of rotation
    obj.rotation_axis_angle[2] = e[1]  # set y-component of the axis of rotation
    obj.rotation_axis_angle[3] = e[2]  # set z-component of the axis of rotation
#------------------------------------------------------------------------------------
# Write Exif-Tags
def write_exif_tags(cam,render,image_path,exiftool):
    focal_length = cam["focal_length"]; sensor_size = cam["sensor_size"]
    image_format = render["format"]; resolution_x = render["resolution_x"]
    resolution_y = render["resolution_y"]; resolution_percentage = render["resolution_percentage"]
    exiftool_mod = exiftool["mod"]; exiftool_path = exiftool["path"]

    CropFactor = np.sqrt(36**2+24**2)/np.sqrt(sensor_size[0]**2+sensor_size[1]**2)
    FocalLengthIn35mmFormat = CropFactor*focal_length
    comment = "Blender:File:" + bpy.data.filepath
    image_width = resolution_x*(resolution_percentage/100)
    image_height = resolution_y*(resolution_percentage/100)
    if exiftool_mod == 2:   # write exif-tags for all files
        output_file_suffix = 'jpg' if image_format == 'JPEG' else 'png'
        options = ['-ext', output_file_suffix,'-overwrite_original','-q',]
        # the image_Path in this mode is the image folder
    else:
        options = ['-overwrite_original','-q',]

    commands = [
                '-all=',  # Remove all Exif tags because the existing EXIF tags are corrupted
                f'-exif:FocalLength={focal_length}',
                f'-exif:FocalLengthIn35mmFormat={FocalLengthIn35mmFormat}',
                f'-exif:model=blender{sensor_size[0]}',
                f'-comment={comment}',
                f'-exif:FocalPlaneXResolution={sensor_size[0]}',
                f'-exif:FocalPlaneYResolution={sensor_size[1]}',
                '-exif:FocalPlaneResolutionUnit=mm',
                f'-exif:ExifImageWidth={image_width}',
                f'-exif:ExifImageHeight={image_height}'
                ]
 
    exif_data = subprocess.run([exiftool_path] + options + commands + [image_path])
#------------------------------------------------------------------------------------
# Create Output-Path       
def create_output_path(project_path,project_name):
    base_output_path = project_path / "blender_data"
    output_path = base_output_path / project_name

    # Check if the folder already exists
    if output_path.exists():   
        # Initialize counter
        counter = 1
        # Generate a unique folder name
        while True:
            # Create the folder path with suffix
            output_path_with_suffix  = base_output_path  / f"{project_name}_{counter}"  
            # Check if the folder with suffix already exists
            if not output_path_with_suffix.exists():
                output_path = output_path_with_suffix
                break    
            # Increment counter for the next attempt
            counter += 1
    return str(output_path)

#------------------------------------------------------------------------------------ 
# Storage of simulation and imaging data
def save_blender_settings(params,camera_data,object_data=None):
    output_path = Path(params["io"]["output_path"])

    # write json-file with all selected parameters 
    json_file_path  = output_path / "params.json"       # File path to save the JSON file
    # Write the dictionary to a JSON file with custom indentation (e.g., 5 spaces)
    with open(json_file_path, "w") as json_file:
        json.dump(params, json_file, indent=5)  

    # write CSV data representing camera positions
    path_CameraData = output_path / ('CameraPositioningInMeters.csv')
    with open(str(path_CameraData), mode='w', newline='') as file:
        writer = csv.writer(file)    
        writer.writerow(['ImageFileName', 'TimeStep', 'PositionX', 'PositionY', 'PositionZ',
                         'RotationEulerX', 'RotationEulerY', 'RotationEulerZ',
                         'DirectionX', 'DirectionY', 'DirectionZ'])
        writer.writerows(camera_data)
    # write CSV data representing object position and orientation
    if object_data != None:
        path_ObjectData = output_path / ('ObjectPositioningInMeters.csv')
        with open(str(path_ObjectData), mode='w', newline='') as file:
            writer = csv.writer(file)    
            writer.writerow(['TimeStep', 'PositionX', 'PositionY', 'PositionZ',
                            'RotationEulerX', 'RotationEulerY', 'RotationEulerZ'])
            writer.writerows(object_data)   
    # write cache file with location of the output folder
    cache_path = Path(params["io"]["script_path"]) / "cache.txt"
    with open(cache_path, "w") as txt_file:
        txt_file.write(params["io"]["output_path"])
#------------------------------------------------------------------------------------
# Display warnings
def print_warnings(params):
    # The ratio of sensor width and sensor height does not match the ratio of resolution_x and resolution_y
    rel_variance = (params["cam"]["sensor_size"][0]/params["cam"]["sensor_size"][1] -\
                    (params["render"]["resolution_x"]/params["render"]["resolution_y"])) /\
                    (params["render"]["resolution_x"]/params["render"]["resolution_y"])
    if np.abs(rel_variance)>0.001:
        print(f"Warning: The ratio of sensor width and sensor height differs by {rel_variance*100:.2f} percent "
      f"from the ratio of the number of pixels over the width and height of the images")
#------------------------------------------------------------------------------------
def create_not_evenly_distributed_cameras(cam):
    focuspoint = cam["focuspoint"]; pos_file_path = cam["pos_file_path"]
    focal_length = cam["focal_length"]; sensor_size = cam["sensor_size"]
    cam2fp_dis = []
    # load positions from position file
    with open(pos_file_path, 'r') as file:
        cam["pos"] = json.load(file)
    # set up the cameras at the desired positions
    for j,camera in enumerate(cam["pos"].values()):
        camera_location = mathutils.Vector((camera["x_m"],camera["y_m"],camera["z_m"]))
        if "theta_x" not in camera.keys():
            target_location = mathutils.Vector(focuspoint)
            # Calculate the direction vector and create the rotation quaternion
            cam2fp_dis.append(np.linalg.norm(target_location - camera_location))
            direction = -(target_location - camera_location).normalized()
            rot_quat = direction.to_track_quat('Z', 'Y')
            # Create a new camera
            bpy.ops.object.camera_add(location=camera_location, rotation=rot_quat.to_euler())
        else:
            euler_angle = mathutils.Vector((camera["theta_x"],camera["theta_y"],camera["theta_z"]))
            bpy.ops.object.camera_add(location=camera_location, rotation=euler_angle)     
        # Adjust camera settings
        bpy.context.object.data.type = 'PERSP'
        bpy.context.object.data.lens = focal_length  # Adjust focal length
        bpy.context.object.data.sensor_width = sensor_size[0]
        bpy.context.object.data.sensor_height = sensor_size[1] 
    return np.array(cam2fp_dis)
#------------------------------------------------------------------------------------
def save_camera_data(cam,camera_data,file_name,t_count):
    rotation = cam.rotation_euler
    # Get the rotation of the camera and convert it to a matrix
    rotation_matrix = rotation.to_matrix()
    # Calculate the camera's viewing direction by multiplying the rotation matrix with the unit vector along the negative Z-axis
    direction = rotation_matrix @ mathutils.Vector((0, 0, -1))   
    camera_data.append([file_name,t_count, cam.location[0], cam.location[1], cam.location[2],
                        rotation[0], rotation[1], rotation[2],
                        direction[0],direction[1],direction[2]])
    return camera_data
#------------------------------------------------------------------------------------
def save_obj_state(obj_motion,t_count,obj):
    rotation_axis_angle = obj.rotation_axis_angle
    rotation_quat = mathutils.Quaternion(rotation_axis_angle[1:], rotation_axis_angle[0])
    rotation_euler = rotation_quat.to_euler()
    location = obj.location
    obj_motion.append([t_count, location[0], location[1], location[2],
                        rotation_euler[0], rotation_euler[1], rotation_euler[2]])
    return obj_motion
#------------------------------------------------------------------------------------
# Detect window (in z-cooridnate) in which the object is visible
def is_object_in_camera_view(obj,params,cam2fp_dis,mode="ALYWAYS_IN_VIEW"):
    # Calculation of bounding box corners in world coordinates
    bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    # Calculation of the center point of the bounding box
    bbox_center = sum(bbox_corners, mathutils.Vector()) / 8
    # Calculation of the maximum distance from the center point to the corners of the bounding box
    if mode == "PARTIALLY_IN_VIEW":
        r_obj = max((corner - bbox_center).length for corner in bbox_corners)
    elif mode == "MAINLY_IN_VIEW":
        face_midpoints = [
            (bbox_corners[0] + bbox_corners[1] + bbox_corners[4] + bbox_corners[5]) / 4,
            (bbox_corners[0] + bbox_corners[1] + bbox_corners[2] + bbox_corners[3]) / 4,
            (bbox_corners[0] + bbox_corners[3] + bbox_corners[4] + bbox_corners[7]) / 4,
            (bbox_corners[4] + bbox_corners[5] + bbox_corners[6] + bbox_corners[7]) / 4,
            (bbox_corners[1] + bbox_corners[2] + bbox_corners[5] + bbox_corners[6]) / 4,
            (bbox_corners[2] + bbox_corners[3] + bbox_corners[6] + bbox_corners[7]) / 4,
        ]
        distances = [(face_midpoint - bbox_center).length for face_midpoint in face_midpoints]
        r_obj = np.mean(distances)
    else: 
        r_obj = 0
    # Find the maximum and minimum height at which objects are visible on the cameras, valid if displacement in x and y direction is not allowed
    delta_h = params["cam"]["sensor_size"][1] / params["cam"]["focal_length"] / 2 *  cam2fp_dis                            # [m] vector
    z_min = params["cam"]["focuspoint"][2]-delta_h - r_obj; z_max = params["cam"]["focuspoint"][2] + delta_h + r_obj       # [m] vector
    return z_min,z_max
    
    