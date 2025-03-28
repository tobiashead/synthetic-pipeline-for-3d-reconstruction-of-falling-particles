import numpy as np
import sys
import importlib
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4
import matplotlib.pyplot as plt
from pathlib import Path

def CreateCameraDataSets(cams_rec,cams_ref,scene = "dynamic"):
    x = np.ones([len(cams_rec),3])*(42)
    y = np.ones([len(cams_rec),3])*(42)
    Rx = []
    Ry = []
    empty_rows = []
    for i,cam_rec in enumerate(cams_rec):
        ind_ref = cam_rec.CorrespondigIndex
        if ind_ref != None:
            cam_ref = cams_ref[ind_ref]
            if scene == "dynamic":
                cam_ref_T = cam_ref.TransformationDynamic; cam_rec_T = cam_rec.TransformationDynamic
            else:
                cam_ref_T = cam_ref.TransformationStatic; cam_rec_T = cam_rec.TransformationStatic
            location_ref,rotation_ref,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(cam_ref_T)
            location_rec,rotation_rec,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(cam_rec_T)
            x[i,:] = location_rec; Rx.append(rotation_rec)
            y[i,:] = location_ref; Ry.append(rotation_ref)
        else:
            empty_rows.append(i)
    empty_rows
    # filter x and y
    pos_x = np.delete(x, empty_rows, axis=0)
    pos_y = np.delete(y, empty_rows, axis=0)
    print(f"{len(cams_rec)} cameras from {len(cams_ref)} cameras were reconstructed ({len(cams_rec)/len(cams_ref)*100} %)")
    return pos_x,pos_y,Rx,Ry

def PlotAbsPositionError_for_xyz(evaluation_path,pos_x,pos_y, DisplayPlots=False):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].plot((pos_x[:, 0]-pos_y[:, 0])*1000, label=r'$\Delta x$', color='blue', alpha=0.5, marker='o',linestyle='None')
    axs[1].plot((pos_x[:, 1]-pos_y[:, 1])*1000, label=r'$\Delta y$', color='blue', alpha=0.5,marker='o',linestyle='None')
    axs[2].plot((pos_x[:, 2]-pos_y[:, 2])*1000, label=r'$\Delta z$', color='blue', alpha=0.5,marker='o',linestyle='None')
    for i,ax in enumerate(axs):
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("camera index")
    axs[0].set_ylabel("absolute error in mm")
    if DisplayPlots: plt.show()
    fig.savefig(Path(evaluation_path) / 'CamPositionErrorXYZ.svg',format='svg',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'CamPositionErrorXYZ.pdf',format='pdf',bbox_inches='tight')
    
def PositionError(evaluation_path,pos_x,pos_y,outlier_criterion=0.005, focuspoint =[0,0,1],DisplayPlots = False):   
    cam_pos_error_abs = np.linalg.norm(pos_x-pos_y,axis=1)
    fig = plt.figure(figsize=(5, 5))
    plt.hist(cam_pos_error_abs*1000, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel(r"$||\mathbf{\hat{x}}_{c}^{fix}-\mathbf{x}_{c}^{fix}||_2$ in mm", fontsize=10)
    plt.ylabel("frequency",fontsize=10)
    mean_error = np.mean(cam_pos_error_abs) 
    std_deviation = np.std(cam_pos_error_abs)
    # Counting the number of outliers
    cam_pos_error_rel = np.divide(cam_pos_error_abs,np.linalg.norm(pos_y-focuspoint,axis=1))
    mean_error_rel = np.mean(cam_pos_error_rel)
    std_deviation_rel = np.std(cam_pos_error_rel) 
    outliers_count = int(np.sum(cam_pos_error_rel > outlier_criterion))
    print(f"Mean absolute camera position error: {mean_error*1000:.2f}mm")
    print(f"Mean relative camera position error: {mean_error_rel*100:.2f}%")
    print(f"Standard deviation: {std_deviation*1000:.2f}mm")
    print(f"Number of Inliers: {len(cam_pos_error_abs)-outliers_count} (rel. error <= {outlier_criterion*100}%)")
    print(f"Number of Outliers: {outliers_count} (rel. error > {outlier_criterion*100}%)")
    if DisplayPlots: plt.show()
    fig.savefig(Path(evaluation_path) / 'CamPositionError.svg',format='svg',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'CamPositionError.pdf',format='pdf',bbox_inches='tight')
    return mean_error, std_deviation, mean_error_rel, std_deviation_rel, outliers_count
   
def OrientationError(Rx,Ry,outlier_criterion_angle = 1):   
    from scipy.spatial.transform import Rotation
    angle_diff = np.zeros([len(Rx),1])
    for i in range (len(Rx)):
        rot_x = Rotation.from_matrix(Rx[i]) 
        rot_y = Rotation.from_matrix(Ry[i])
        rot_diff = rot_x.inv() * rot_y
        angle_diff[i] = rot_diff.magnitude() * 180 / np.pi
    fig = plt.figure(figsize=(5, 5))
    plt.hist(angle_diff, bins=15, color='skyblue', edgecolor='black')
    plt.xlabel(r"Rotation Difference $\alpha$ in $^\circ$")
    plt.ylabel("frequency")
    mean_angle_error = np.mean(angle_diff) 
    std_angle_deviation = np.std(angle_diff)
    # Counting the number of outliers
    outliers_count = np.sum(angle_diff > outlier_criterion_angle)
    print(f"Mean rotation difference: {mean_angle_error:.2f}°")
    print(f"Standard deviation: {std_angle_deviation:.2f}°")
    print(f"Number of Inliers: {len(Rx)-outliers_count} (angle error <= {outlier_criterion_angle}°)")
    print(f"Number of Outliers: {outliers_count} (angle error > {outlier_criterion_angle}°)")
    plt.show()