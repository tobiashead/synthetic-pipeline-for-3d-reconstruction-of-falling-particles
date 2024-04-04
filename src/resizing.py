import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
np.seterr(divide='ignore',invalid='ignore')
from scipy.spatial.distance import cdist
#import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

plt.rc ('font', size = 11) # steuert die Standardtextgröße
plt.rc ('axes', titlesize = 11) # Schriftgröße des Titels
plt.rc ('axes', labelsize = 11) # Schriftgröße der x- und y-Beschriftungen
plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende


#-----------------------------------------------------------------------
# load camera data from Meshroom
basebase_file_path_meshroom = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\meshroom_data\moving_MS_20_2_60images_1"
base_file_path_meshroom = Path(basebase_file_path_meshroom) / 'MeshroomCache' / 'StructureFromMotion'
folder_name = os.listdir(base_file_path_meshroom)
sfm_data_path =  base_file_path_meshroom / folder_name[0] / "cameras.sfm"
with open(sfm_data_path, 'r') as file:
    sfm_data = json.load(file)

class reconstructed_camera:
    def __init__(self, ImageFileName, Pose, TimeStep):
        self.ImageFileName = ImageFileName
        self.Pose = Pose
        self.TimeStep = TimeStep
        
cam_pos_rec = []
n_img = len(sfm_data["views"])
for i in range(n_img):
    img_path = sfm_data["views"][i]["path"]
    ImageFileName = os.path.basename(img_path)
    Pose = sfm_data["poses"][i]["pose"]["transform"]
    cam = reconstructed_camera(ImageFileName,Pose,-1)
    cam_pos_rec.append(cam)
#-----------------------------------------------------------------------
# load camera data from blender
base_file_path_blender = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\blender_data\moving_MS_20_2_60images_1"
cam_pos_file_path = Path(base_file_path_blender) / "CameraPositioningInMeters.csv"
cam_pos_blender = pd.read_csv(cam_pos_file_path)
cam_pos_blender["TimeStep"]-=cam_pos_blender["TimeStep"][0]-1
#-----------------------------------------------------------------------
# match reconstructed cameras and the groud truth cameras
cam_match_matrix = np.ones([n_img,2])
for i in range(n_img):
    ImageFileName = cam_pos_blender.iloc[i]["ImageFileName"]
    TimeStep = cam_pos_blender.iloc[i]["TimeStep"]
    cam_match_matrix[i,0] = i
    for j in range(n_img):
        if cam_pos_rec[j].ImageFileName == ImageFileName:
            cam_match_matrix[i,1] = j
            cam_pos_rec[j].TimeStep = TimeStep
            break
#-----------------------------------------------------------------------
# calculate distance between the reconstructed cameras within a timestep
n_cam = int(n_img/TimeStep)
factor_vec = np.zeros(TimeStep*n_cam**2)
for i in range(TimeStep):
    pos_matrix_gt = np.zeros([n_cam,3])
    pos_matrix_r = np.zeros([n_cam,3])
    for j in range(n_cam):
            k = int(i*n_cam + j)
            pos_gt = cam_pos_blender.iloc[k]
            x_gt = [pos_gt["PositionX"],pos_gt["PositionY"],pos_gt["PositionZ"]]
            x_r = cam_pos_rec[int(cam_match_matrix[k,1])].Pose["center"]
            pos_matrix_gt[j,:] = x_gt; pos_matrix_r[j,:] = x_r
    dist_matrix_gt = cdist(pos_matrix_gt,pos_matrix_gt,'euclidean') # Compute euklidean distance between each pair of the cameras (groud truth)
    dist_matrix_r = cdist(pos_matrix_r,pos_matrix_r,'euclidean')    # Compute euklidean distance between each pair of the cameras (reconstructed)
    factor_matrix = np.divide(dist_matrix_gt,dist_matrix_r)
    factor_vec[i*n_cam**2:(i+1)*n_cam**2] = factor_matrix.flatten()
factor_vec = factor_vec[~np.isnan(factor_vec)]
factor_mean = np.mean(factor_vec)
factor_median = np.median(factor_vec)
factor_std = np.std(factor_vec)
#-----------------------------------------------------------------------
# calculate distance between the reconstructed cameras within a timestep
#plt.hist(factor_vec)
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
#plt.savefig(Path())
#plt.savefig('scaling_factor.pdf') 