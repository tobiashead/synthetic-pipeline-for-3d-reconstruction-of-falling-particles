import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
np.seterr(divide='ignore',invalid='ignore')
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import seaborn as sns

def scaling_factor(cams_rec,cams_ref,evaluation_path):
    #-----------------------------------------------------------------------
    # calculate distance between the reconstructed cameras within a timestep
    n_img = len(cams_ref)
    n_TimeSteps = cams_ref[-1].TimeStep
    n_cam = int(n_img/n_TimeSteps)                 # Calculate the number of cameras per time step
    #factor_vec = []
    factor_vec = np.zeros(n_TimeSteps*n_cam**2)       # Initialize an array to store scaling factors
    ind_ref = 0                                      # Index for accessing camera positions
    for i in range(n_TimeSteps):                    # Iterate over all time steps
        pos_matrix_ref = np.zeros([n_cam,3])         # Initialize a matrix to store ground truth camera positions within a time step
        pos_matrix_rec = np.zeros([n_cam,3])          # Initialize a matrix to store ground reconstructed camera positions within a time step
        for j in range(n_cam):                      # Iterate over all cameras within this timestep
            ind_rec = cams_ref[ind_ref].CorrespondigIndex
            if ind_rec != None:
                x_ref = cams_ref[ind_ref].Location         # Extract XYZ coordinates (reference camera)
                x_rec = cams_rec[ind_rec].Location           # Extract XYZ coordinates (reconstructed camera)
                pos_matrix_ref[j,:] = x_ref; pos_matrix_rec[j,:] = x_rec            # Store camera positions in a matrix  within a time step
            ind_ref += 1                                                           # Update Index for accessing camera positions
        pos_matrix_ref = pos_matrix_ref[~np.all(pos_matrix_ref == 0, axis=1)]
        pos_matrix_rec = pos_matrix_rec[~np.all(pos_matrix_rec == 0, axis=1)]
        dist_matrix_ref = cdist(pos_matrix_ref,pos_matrix_ref,'euclidean') # Compute euklidean distance between each pair of the cameras (groud truth) --> Euclidean distance matrix
        dist_matrix_rec = cdist(pos_matrix_rec,pos_matrix_rec,'euclidean')    # Compute euklidean distance between each pair of the cameras (reconstructed) --> Euclidean distance matrix
        factor_matrix = np.divide(dist_matrix_ref,dist_matrix_rec)         # Calculate the scaling factors by the ratio of the distances between the cameras 
        factor_vec[i*n_cam**2:(i+1)*n_cam**2] = factor_matrix.flatten()     # Flatten and store scaling factors
        #factor_vec.append(factor_matrix.flatten())
    #factor_vec = np.concatenate(factor_vec)
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
    
    return factor_mean, factor_median, factor_std, fig