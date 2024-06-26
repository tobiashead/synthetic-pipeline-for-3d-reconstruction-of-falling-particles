import os
from pathlib import Path
import subprocess
import numpy as np

def FineMeshRegistration_and_MeshToMeshDistance(CC_path,params_CC,evaluation_path,mesh_gt_path,mesh_r_path,output_format_mesh,InitialTrans_path):
    silent = params_CC[0]; save_meshes_all_at_once = params_CC[1]; adjust_scale = params_CC[2]; output_format_mesh = params_CC[3]
    # Create Path to log file
    log_path = evaluation_path / "log_CloudCompare.txt"                     # Path to log file
    # Command for CloudCompare (https://www.cloudcompare.org/doc/wiki/index.php/Command_line_mode)
    command = [
        CC_path,                                      # File path to CloudCompare.exe
        "-AUTO_SAVE", "OFF",                                    # prevents the saving of intermediate states and saving in the GroudTruth folder 
    #   {SILENT MODE}                                           # Activate silent mode, Command will be inserted here 
        "-LOG_FILE", log_path,                                  # write log_file, required to read the Cloud2Mesh distance
        "-NO_TIMESTAMP",                                        # File names do not contain timestamps so that the output files always have the same name
        "-O", mesh_r_path,                                      # Import Reconstructed Mesh
        "-APPLY_TRANS", InitialTrans_path,                      # Scale the object with the previously found scaling factor using a 4x4 transformation matrix
        "-O", mesh_gt_path,                                     # Import Ground Truth Mesh
        "-CLEAR_NORMALS",                                       # Clear Normals, Fixes display problems of the Ground Truth Mesh in CloudComapre
        "-C2M_DIST",                                            # Computes Cloud-to-Mesh distances before alignment with the ICP algorithm
        "-ICP", "-MIN_ERROR_DIFF", "1e-7", # {ADJUST_SCALE}     # Closest Point registration procedure, Alignment of the reconstructed mesh to the ground truth mesh, by default the second loaded entity is the reference 
        "-AUTO_SAVE", "ON",                                     # Activate Autosave so that a CloudCompare file is written after the next operation. This should be used to review the operations performed in the GUI
        "-C2M_DIST"                                             # Computes Cloud-to-Mesh distances after alignment with the ICP algorithm
    #   {SAVING PROCESS}                                        # Saving process, Commands will be inserted here 
    ]
    if silent:                                                              # Activate silent mode, if silent mode is selected
        command.insert(1, "-SILENT")
    if save_meshes_all_at_once:                                             # Check if saving meshes all at one file is selected
        command.append("-SAVE_MESHES"); command.append("ALL_AT_ONCE")       # saving meshes all at one file 
        command.append("-POP_MESHES")                                       # remove the ground truth mesh from the workspace
        command.append("-M_EXPORT_FMT"); command.append(output_format_mesh) # change the export format so that the mesh can also be read by other programs
        command.append("-SAVE_MESHES")                                      # additionally save the reconstructed mesh in an seperate file
    else:
        "-M_EXPORT_FMT", output_format_mesh                                 
        command.append("-POP_MESHES")                                       # remove the ground truth mesh from the workspace 
        command.append("-M_EXPORT_FMT"); command.append(output_format_mesh) # change the export format so that the mesh can also be read by other programs 
        command.append("-SAVE_MESHES")                                      # save the reconstructed mesh
    if adjust_scale:                                                        # Activate Adjust_Scale in the ICP process, if selectedshould be included
        adjust_scale_index = command.index("1e-7") + 1
        command.insert(adjust_scale_index, "-ADJUST_SCALE")   
    # Run CloudCompare command        
    return_code = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Define path for transformed mesh and ICP Transformation Matrix
    mesh_r_trans_path = evaluation_path / ("texturedMesh_TRANSFORMED." + output_format_mesh)
    T_ICP_path = evaluation_path / "ICPTransformationMatrix.txt"
    # Change Names
    os.replace(evaluation_path / ("texturedMesh_TRANSFORMED_C2M_DIST_REGISTERED_C2M_DIST." + output_format_mesh),mesh_r_trans_path)
    os.replace((evaluation_path / "texturedMesh_TRANSFORMED_C2M_DIST_REGISTRATION_MATRIX.txt"),T_ICP_path)
    # Extract transformation matrices
    T_ICP = np.loadtxt(T_ICP_path)   # ICP transformation matrix
    T_init = np.loadtxt(InitialTrans_path)                                                              # global registration and scale transformation matrix
    T = np.dot(T_ICP,T_init)                                                                            # overall transformation matrix
    # save overall transformation matrix
    np.savetxt((evaluation_path / "TransformationMatrix.txt"),T)   
        
    return T,T_ICP,mesh_r_trans_path,log_path