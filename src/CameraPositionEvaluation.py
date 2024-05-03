import numpy as np
import sys
import importlib
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4
import matplotlib.pyplot as plt

def CreateCameraDataSets(cams_rec,cams_ref):
    x = np.ones([len(cams_rec),3])*(42)
    y = np.ones([len(cams_rec),3])*(42)
    Rx = []
    Ry = []
    empty_rows = []
    for i,cam_rec in enumerate(cams_rec):
        ind_ref = cam_rec.CorrespondigIndex
        if ind_ref != None:
            cam_ref = cams_ref[ind_ref]
            location_ref,rotation_ref,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(cam_ref.TransformationStatic)
            location_rec,rotation_rec,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(cam_rec.TransformationStatic)
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

def PlotAbsPositionError_for_xyz(pos_x,pos_y):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].plot((pos_x[:, 0]-pos_y[:, 0])*1000, label=r'$\Delta x$', color='blue', alpha=0.5, marker='o',linestyle='None')
    axs[1].plot((pos_x[:, 1]-pos_y[:, 1])*1000, label=r'$\Delta y$', color='blue', alpha=0.5,marker='o',linestyle='None')
    axs[2].plot((pos_x[:, 2]-pos_y[:, 2])*1000, label=r'$\Delta z$', color='blue', alpha=0.5,marker='o',linestyle='None')
    for i,ax in enumerate(axs):
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("camera index")
    axs[0].set_ylabel("absolute error in mm")
    plt.show()
    
def PlotAbsPositionError(pos_x,pos_y):   
    cam_pos_error_abs = np.linalg.norm(pos_x-pos_y,axis=1)
    fig = plt.figure(figsize=(5, 5))
    plt.hist(cam_pos_error_abs*1000, bins=15, color='skyblue', edgecolor='black')
    plt.xlabel(r"Camera Position Error $||\mathrm{\vec{x}}_{c,rec}^g-\mathrm{\vec{x}}_{c,ref}^g||_2$ in mm")
    plt.ylabel("frequency")
    mean_error = np.mean(cam_pos_error_abs) 
    std_deviation = np.std(cam_pos_error_abs)
    # Counting the number of outliers
    outlier_criterion = 1e-3
    outliers_count = np.sum(cam_pos_error_abs > outlier_criterion)
    print(f"Mean absolute camera position error: {mean_error*1000:.2f} mm")
    print(f"Standard deviation: {std_deviation*1000:.2f} mm")
    print(f"Number of Inliers: {len(cam_pos_error_abs)-outliers_count} (abs. error <= 1mm)")
    print(f"Number of Outliers: {outliers_count} (abs. error > 1mm)")
    
def OrientationError(Rx,Ry):   
    from scipy.spatial.transform import Rotation
    angle_diff = np.zeros([len(Rx),1])
    for i in range (len(Rx)):
        rot_x = Rotation.from_matrix(Rx[i]) 
        rot_y = Rotation.from_matrix(Ry[i])
        rot_diff = rot_x.inv() * rot_y
        angle_diff[i] = rot_diff.magnitude() * 180 / np.pi
    fig = plt.figure(figsize=(5, 5))
    plt.hist(angle_diff, bins=15, color='skyblue', edgecolor='black')
    plt.xlabel(r"Rotation Difference $\alpha$ in °")
    plt.ylabel("frequency")
    mean_angle_error = np.mean(angle_diff) 
    std_angle_deviation = np.std(angle_diff)
    # Counting the number of outliers
    outlier_criterion = 1 # °
    outliers_count = np.sum(angle_diff > outlier_criterion)
    print(f"Mean rotation difference: {mean_angle_error:.2f}°")
    print(f"Standard deviation: {std_angle_deviation:.2f}°")
    print(f"Number of Inliers: {len(Rx)-outliers_count} (angle error <= 1°)")
    print(f"Number of Outliers: {outliers_count} (angle error > 1°)")