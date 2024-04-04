import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
np.seterr(divide='ignore',invalid='ignore')
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import seaborn as sns


def scaling_factor(basebase_file_path_meshroom,base_file_path_blender,evaluation_path):

    #-----------------------------------------------------------------------
    # load camera data from Meshroom
    base_file_path_meshroom = Path(basebase_file_path_meshroom) / 'MeshroomCache' / 'StructureFromMotion'
    folder_name = os.listdir(base_file_path_meshroom)
    sfm_data_path =  base_file_path_meshroom / folder_name[0] / "cameras.sfm"
    with open(sfm_data_path, 'r') as file:
        sfm_data = json.load(file)
        # define a class reconstructed_camera to represent each reconstructed camera with attributes for the image file name, pose, and time step
    class reconstructed_camera: 
        def __init__(self, ImageFileName, Pose, TimeStep):
            self.ImageFileName = ImageFileName
            self.Pose = Pose
            self.TimeStep = TimeStep
        # save all camera objects in a list    
    cam_pos_rec = []
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
        cam = reconstructed_camera(ImageFileName,Pose,-1)
        cam_pos_rec.append(cam)
    #-----------------------------------------------------------------------
    # load camera data from blender
    cam_pos_file_path = Path(base_file_path_blender) / "CameraPositioningInMeters.csv"
    cam_pos_blender = pd.read_csv(cam_pos_file_path)
    cam_pos_blender["TimeStep"] -= cam_pos_blender["TimeStep"][0]-1 # Adjusts the time step --> starts from 1
    #-----------------------------------------------------------------------
    # match reconstructed cameras and the groud truth cameras
    cam_match_matrix = np.ones([n_img,2])*(-1) # Initializes a matrix to store the match between reconstructed and real cameras based on the idices
    for i in range(n_img):      # Iterates over all images (Ground Truth)
        ImageFileName = cam_pos_blender.iloc[i]["ImageFileName"]
        TimeStep = cam_pos_blender.iloc[i]["TimeStep"]
        cam_match_matrix[i,0] = i
        for j in range(n_pose):  # For each ground truth camera, finds the corresponding reconstructed camera using the image file name
            if cam_pos_rec[j].ImageFileName == ImageFileName:
                cam_match_matrix[i,1] = j
                cam_pos_rec[j].TimeStep = TimeStep
                break
    #-----------------------------------------------------------------------
    # calculate distance between the reconstructed cameras within a timestep
    n_cam = int(n_img/TimeStep)                 # Calculate the number of cameras per time step
    factor_vec = []
#    factor_vec = np.zeros(TimeStep*n_cam**2)    # Initialize an array to store scaling factors
    ind_gt = 0                                  # Index for accessing camera positions
    for i in range(TimeStep):                   # Iterate over all time steps
        pos_matrix_gt = np.zeros([n_cam,3])     # Initialize a matrix to store ground truth camera positions within a time step
        pos_matrix_r = np.zeros([n_cam,3])      # Initialize a matrix to store ground reconstructed camera positions within a time step
        for j in range(n_cam):                  # Iterate over all cameras within this timestep
            ind_r = int(cam_match_matrix[ind_gt,1])
            if ind_r != -1:
                pos_gt = cam_pos_blender.iloc[ind_gt]        # Get the ground truth camera position
                x_gt = [pos_gt["PositionX"],pos_gt["PositionY"],pos_gt["PositionZ"]] # Extract XYZ coordinates (GT)
                x_r = cam_pos_rec[ind_r].Pose["center"]         # Extract XYZ coordinates (reconstructed)
                pos_matrix_gt[j,:] = x_gt; pos_matrix_r[j,:] = x_r                   # Store camera positions in a matrix  within a time step
            ind_gt += 1                                                           # Update Index for accessing camera positions
        pos_matrix_gt = pos_matrix_gt[~np.all(pos_matrix_gt == 0, axis=1)]
        pos_matrix_r = pos_matrix_r[~np.all(pos_matrix_r == 0, axis=1)]
        dist_matrix_gt = cdist(pos_matrix_gt,pos_matrix_gt,'euclidean') # Compute euklidean distance between each pair of the cameras (groud truth) --> Euclidean distance matrix
        dist_matrix_r = cdist(pos_matrix_r,pos_matrix_r,'euclidean')    # Compute euklidean distance between each pair of the cameras (reconstructed) --> Euclidean distance matrix
        factor_matrix = np.divide(dist_matrix_gt,dist_matrix_r)         # Calculate the scaling factors by the ratio of the distances between the cameras 
#        factor_vec[i*n_cam**2:(i+1)*n_cam**2] = factor_matrix.flatten() # Flatten and store scaling factors
        factor_vec.append(factor_matrix.flatten())
    factor_vec = np.concatenate(factor_vec)
    factor_vec = factor_vec[~np.isnan(factor_vec)]                      # Remove NaN values
    factor_mean = np.mean(factor_vec)                                   # Calculate mean scaling factor
    factor_median = np.median(factor_vec)                               # Calculate median scaling factor
    factor_std = np.std(factor_vec)                                     # Calculate standard deviation of scaling factors
    #-----------------------------------------------------------------------
    # Plot
    plt.rc ('font', size = 11) # steuert die Standardtextgröße
    plt.rc ('axes', titlesize = 11) # Schriftgröße des Titels
    plt.rc ('axes', labelsize = 11) # Schriftgröße der x- und y-Beschriftungen
    plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
    plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
    plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende
    sns.set(style='white',font='Arial')
    fig = plt.figure(figsize=(6.4,4.8))
    g = sns.histplot(data=pd.DataFrame(factor_vec),legend=False, kde=True,fill=False)
    g.set_ylabel('Anzahl',fontsize=11)
    g.set_xlabel('Skalierungsfaktor f',fontsize=11)
    g.tick_params(labelsize=11)
    for p in g.patches:
        p.set_edgecolor('black')  # Change Color of the edgecolor
    plt.axvline(factor_mean, color='red', linestyle='--', label='Mittelwert $\overline{{f}} = {:.4f}$'.format(factor_mean))
    plt.axvline(factor_median, color='green', linestyle='--', label='Median $\widetilde{{f}} = {:.4f}$'.format(factor_median))
    plt.legend(loc='upper left',fontsize=11)
    plt.annotate('$\sigma = {:.3e}$'.format(factor_std),[60,240],xycoords='figure points', fontsize=11)
    # The distances between the cameras are considered twice --> should be eliminated
    # Get the heights of the bars of the histogram
    # bars = plt.gca().patches
    # current_heights = [bar.get_height() for bar in bars]
    # # Calculate half of the current heights
    # new_heights = [height / 2 for height in current_heights]
    # # Update the heights of the bars of the histogram
    # for bar, new_height in zip(bars, new_heights):
    #     bar.set_height(new_height)
    # # Get the height of the KDE curve
    # kde_curve = plt.gca().lines[0].get_ydata()
    # current_heights = kde_curve / 2
    # # Update the height of the KDE curve
    # plt.gca().lines[0].set_ydata(current_heights)
    # # Update the y-limits of the axis
    # plt.ylim(plt.ylim()[0] / 2, plt.ylim()[1] / 2)
    plt.grid()   
    plt.show()
    fig.savefig(Path(evaluation_path) / 'scaling_factor.svg',format='svg',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'scaling_factor.pdf',format='pdf',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'scaling_factor.eps',format='eps',bbox_inches='tight')
    
    return factor_mean, factor_median, factor_std, cam_pos_rec, cam_pos_blender, fig