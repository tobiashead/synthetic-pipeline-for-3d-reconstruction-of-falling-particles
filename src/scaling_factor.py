import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
np.seterr(divide='ignore',invalid='ignore')
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
# Plot Settings
plt.rc ('font', size = 11) # steuert die Standardtextgröße
plt.rc ('axes', titlesize = 11) # Schriftgröße des Titels
plt.rc ('axes', labelsize = 11) # Schriftgröße der x- und y-Beschriftungen
plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende
sns.set(style='white',font='Arial')

#-----------------------------------------------------------------------

def scaling_factor(cams_rec,cams_ref,evaluation_path,PreOutlierDetection=False,threshold = 0.025, criterion = "abs"):
    # calculate distance between the reconstructed cameras within a timestep for all timesteps (x)
    # calculate the same for the reference cameras (y)
    # Calculation of an information matrix containing the corresponding time steps and camera indices for all x and y values 
    y, x, cams_info = CalculateDistancesWithinOneTimeStep(cams_ref,cams_rec)
    if len(y) == 0:
        print("Error: No scaling factor could be determined because no two cameras could be reconstructed at the same time step.")
        print("A scaling factor of 0.2 is chosen.")
        return 0.2, 0.2, None, None
    # Detect and remove outliers that do not agree with the consistency rules
    if PreOutlierDetection:
        cams_info = np.vstack(cams_info)
        y, x = ConsistencyBasedOutlierDetection(y,x,cams_info,threshold,criterion)
    # calculate scaling factor and statistical measurements 
    factor_vec = np.divide(y,x)                     # Scaling factor = distance_ref / distance_rec     
    factor_mean = np.mean(factor_vec)               # Calculate mean scaling factor
    factor_median = np.median(factor_vec)           # Calculate median scaling factor
    factor_std = np.std(factor_vec)                 # Calculate standard deviation of scaling factors
    # plot and return
    fig = scaling_factor_plot(factor_vec,factor_mean,factor_median,factor_std,evaluation_path)
    return factor_mean, factor_median, factor_std, fig

#-----------------------------------------------------------------------

def scaling_factor_RANSAC(cams_rec,cams_ref,evaluation_path,PreOutlierDetection,threshold = 0.025,criterion = "abs"):
    # calculate distance between the reconstructed cameras within a timestep for all timesteps (x)
    # calculate the same for the reference cameras (y)
    # Calculation of an information matrix containing the corresponding time steps and camera indices for all x and y values 
    y, x, cams_info = CalculateDistancesWithinOneTimeStep(cams_ref,cams_rec)
    if len(y) == 0:
        print("Error: No scaling factor could be determined because no two cameras could be reconstructed at the same time step.")
        print("A scaling factor of 0.2 is chosen.")
        return 0.2
    # Detect and remove outliers that do not agree with the consistency rules
    # n_img = len(cams_ref); n_TimeSteps = cams_ref[-1].TimeStep
    # n_cam = int(n_img/n_TimeSteps) 
    if  PreOutlierDetection:
        cams_info = np.vstack(cams_info)
        y,x = ConsistencyBasedOutlierDetection(y,x,cams_info,threshold,criterion)
    # allows a RANSAC solution in certain cases by introducing an artificial point at (0, 0)  
    y = np.append(y,0); x = np.append(x,0); 
    # Standardize features by removing the mean and scaling to unit variance (not necessary)
    #sc = StandardScaler(with_mean=False); X = sc.fit_transform(x.reshape(-1, 1))
    X = x.reshape(-1, 1)
    # Fit line using all data
    lr = linear_model.LinearRegression(fit_intercept=False)
    lr.fit(X, y)
    # Robustly fit linear model with RANSAC algorithm
    try:
        ransac = linear_model.RANSACRegressor(estimator=linear_model.LinearRegression(fit_intercept=False),random_state = 42)
        ransac.fit(X, y)
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)
        successful = True
    except Exception as e:
        print("An error occurred:",e)
        successful = False
    # plot and print results and return the solution found with RANSAC
    #if successful: fig = ransac_plot(lr,ransac,X[:-1],y[:-1],inlier_mask[:-1],outlier_mask[:-1],successful)
    #else: fig = ransac_plot(lr,ransac,X[:-1],y[:-1],1,1,successful)
    #if successful: fig = ransac_plot(lr,ransac,X,y,inlier_mask,outlier_mask,successful)
    #else: fig = ransac_plot(lr,ransac,X,y,1,1,successful)
    if successful: return ransac.estimator_.coef_[0]
    else: return lr.coef_[0]
    
#-----------------------------------------------------------------------   

def CalculateDistancesWithinOneTimeStep(cams_ref,cams_rec):
    # calculate distance between the reconstructed cameras within a timestep for all timesteps (x)
    # calculate the same for the reference cameras (y)
    # Calculation of an information matrix containing the corresponding time steps and camera indices for all x and y values
    n_img = len(cams_ref)                          # number of images
    n_TimeSteps = cams_ref[-1].TimeStep            # numer of timesteps
    n_cam = int(n_img/n_TimeSteps)                 # calculate the number of cameras per time step
    dist_vec_ref = []; dist_vec_rec = []; cams_info = []
    ind_ref = 0                                     # Index for accessing camera positions
    for i in range(n_TimeSteps):                    # Iterate over all time steps
        pos_matrix_ref = np.zeros([n_cam,3])        # Initialize a matrix to store ground truth camera positions within a time step
        pos_matrix_rec = np.zeros([n_cam,3])        # Initialize a matrix to store ground reconstructed camera positions within a time step
        NotRecCams = []; RecCams = []               # Create a list for the reconstructed and the not reconstructed cameras within a timestep
        for j in range(n_cam):                      # Iterate over all cameras within this timestep
            ind_rec = cams_ref[ind_ref].CorrespondigIndex                   # corresponding reconstructed camera to the reference camera
            if ind_rec != None:                                             # reconstructed camera exists? 
                x_ref = cams_ref[ind_ref].Location                          # Extract XYZ coordinates (reference camera)
                x_rec = cams_rec[ind_rec].Location                          # Extract XYZ coordinates (reconstructed camera)
                pos_matrix_ref[j,:] = x_ref; pos_matrix_rec[j,:] = x_rec    # Store camera positions in a matrix  within a time step
                RecCams.append(j)                                           # Store the index of the reconstructed camera within a timestep
            else: NotRecCams.append(j)                                      # Store the index of the not reconstructed camera within a timestep
            ind_ref += 1                                                    # Update Index for accessing camera positions
        pos_matrix_ref = np.delete(pos_matrix_ref,NotRecCams,0)             # delete not reconstructed cameras from the position matrix (reference)
        pos_matrix_rec = np.delete(pos_matrix_rec,NotRecCams,0)             # delete not reconstructed cameras from the position matrix (reconstructed)
        dist_matrix_ref = cdist(pos_matrix_ref,pos_matrix_ref,'euclidean')  # Compute euklidean distance between each pair of the cameras (groud truth)   --> Euclidean distance matrix
        dist_matrix_rec = cdist(pos_matrix_rec,pos_matrix_rec,'euclidean')  # Compute euklidean distance between each pair of the cameras (reconstructed) --> Euclidean distance matrix
        # distance between cam i and j is the same as the distance between cam j and i, the distance between a camera i and i is always zero 
        # --> the distance matrices are squared and symmetrical with a zero vector on the main diagonal
        # --> thus the upper triangular matrix, without the main diagonal, contains the complete information content
        dist_vec_ref.append(GetValuesUpperTriangularMatrixWithoutDiagonal(dist_matrix_ref,GetIndMatrix=False))              # flatten the upper triangular matrix w.o. the diagonal to vector
        dist_vec_timestep,IndMatrix = GetValuesUpperTriangularMatrixWithoutDiagonal(dist_matrix_rec,GetIndMatrix=True)      # flatten the upper triangular matrix w.o. the diagonal to vector
        cams_info_timestep = IndMatrix2CamInfoMatrix(IndMatrix,RecCams,Timestepm1=i)         # calculate the information matrix for all cameras within the timestep
        cams_info.append(cams_info_timestep); dist_vec_rec.append(dist_vec_timestep)      # append the calculated vector / matrix
    # define response variable y and explanatory variable x
    y = np.concatenate(dist_vec_ref)
    x = np.concatenate(dist_vec_rec)
    return y, x, cams_info

#-----------------------------------------------------------------------   

def GetValuesUpperTriangularMatrixWithoutDiagonal(matrix,GetIndMatrix=False):
    # matrix is quadratic
    n = len(matrix)
    vec = np.zeros(int(n*(n-1)/2))
    # form a matrix that stores the indexes of the camera pairs for the respective vector entry
    IndMatrix = np.zeros([int(n*(n-1)/2),2])
    row = 0; column = 1
    ind = 0
    for i in range(int(n*(n+1)/2)):
        if column < n:
            vec[ind] = matrix[row,column]
            IndMatrix[ind,:] = [row,column] 
            ind += 1; column += 1
        else:
            row += 1; column = row+1
    if GetIndMatrix == False:
        return vec
    else: return vec,IndMatrix

#-----------------------------------------------------------------------   
    
def IndMatrix2CamInfoMatrix(IndMatrix,RecCams,Timestepm1):
    n = len(IndMatrix[:,0])
    CamsInfoMatrix = np.ones([n,3])*(-1)
    for row in range(n):
         for column in range(2):
            Ind = int(IndMatrix[row,column])
            CamsInfoMatrix[row,column] = RecCams[Ind]
    CamsInfoMatrix[:,2] = Timestepm1 + 1
    return CamsInfoMatrix

#-----------------------------------------------------------------------   

def ConsistencyBasedOutlierDetection(y, x, cam_rec_info, threshold=0.025, criterion = "abs"):
    y_mean = np.mean(y)             # calculate the mean distance between two cameras (reference cams)
    x_mean = np.mean(x)             # calculate the mean distance between two cameras (reconstructed cams)
    if cam_rec_info[-1, 2] != 1:    # only works in a dynamic case (object is moving)
        n = len(y)                  # number of measured distances between cameras 
        IsInlier = np.zeros(n, dtype=bool)      # initialize a numpy vector: value = 1, if a camera could be an inlier
        inlier_cameras = set()                  # create a class to save potential  inlier cameras
        for i in range(n):                      # iterate over all distances
            if not IsInlier[i]:                 # if distance is already identified as inlier, then skip the next steps
                cam1_ind1, cam2_ind1, t_ind1 = cam_rec_info[i] # get camera indexes
                # get the indexes of all distances that were determined from the same camera combination at different time steps
                same_camera_indices = np.where((cam_rec_info[:, 2] != t_ind1) &
                                                (cam_rec_info[:, 0] == cam1_ind1) & 
                                                (cam_rec_info[:, 1] == cam2_ind1))[0]
                for j in same_camera_indices:   # Iterate over the associated camera pairs
                    cam1_ind2, cam2_ind2, t_ind2  = cam_rec_info[j]
                    d_diff = x[i] - x[j]        # Calculate the deviation of the two distances
                    # Determine weight on the threshold
                    if criterion == "rel": beta = x_mean / y_mean * y[i]
                    elif criterion == "abs_norm": beta = y_mean/y[i]
                    else: beta = 1
                    # criterion 
                    crit_fulfilled =  np.abs(d_diff) <= beta*threshold
                    if crit_fulfilled: # if the relative deviation is smaller than the weighted threshold --> Inlier
                        IsInlier[i] = True                          # both distances are detected as inliers 
                        IsInlier[j] = True
                        inlier_cameras.add((t_ind1, cam1_ind1))     # all four corresponding cameras are detected as inliers 
                        inlier_cameras.add((t_ind1, cam2_ind1))
                        inlier_cameras.add((t_ind2, cam1_ind2))
                        inlier_cameras.add((t_ind2, cam2_ind2))
        if criterion == "rel": print(f"{n- np.sum(IsInlier)} of {n} measured distances between camera pairs were detected as outliers (relative threshold: {threshold*100:.1f}%)")
        elif criterion == "abs_norm": print(f"{n- np.sum(IsInlier)} of {n} measured distances between camera pairs were detected as outliers (absolute normalized threshold: {threshold*1000:.0f}mm)")
        else:  print(f"{n- np.sum(IsInlier)} of {n} measured distances between camera pairs were detected as outliers (absolute threshold: {threshold*1000:.0f}mm)")
        outlier_cameras = set()                                     # define a class to save the outliers
        # first set all cameras as outliers and the remove the inliers from the outliers
        for i, (cam1, cam2, t) in enumerate(cam_rec_info):           
                outlier_cameras.add((t, cam1))
                outlier_cameras.add((t, cam2))
        for inlier_cam in inlier_cameras:
            outlier_cameras.remove(inlier_cam)
        # print outlier cameras
        if outlier_cameras != {}:
            print(f"{len(outlier_cameras)} Outlier Camera has been detected:")
            for cam in outlier_cameras:
                print(f"Timestep: {int(cam[0])}, Camera Number: {int(cam[1])}")
        # only return the distances marked as inliers
        y = y[IsInlier]
        x = x[IsInlier]
    return y, x

#-----------------------------------------------------------------------   

def scaling_factor_plot(factor_vec,factor_mean,factor_median,factor_std,evaluation_path):
    fig = plt.figure(figsize=(6.4,4.8))
    g = sns.histplot(data=pd.DataFrame(factor_vec),legend=False, kde=True,fill=False)
    g.set_ylabel('Frequency',fontsize=11)
    g.set_xlabel('Scaling factor f',fontsize=11)
    g.tick_params(labelsize=11)
    for p in g.patches:
        p.set_edgecolor('black')  # Change Color of the edgecolor
    plt.axvline(factor_mean, color='red', linestyle='--', label='Mean $\overline{{f}} = {:.4f}$'.format(factor_mean))
    plt.axvline(factor_median, color='green', linestyle='--', label='Median $\widetilde{{f}} = {:.4f}$'.format(factor_median))
    plt.legend(loc='upper right',fontsize=11)
    plt.annotate('$\sigma = {:.3e}$'.format(factor_std),[270,240],xycoords='figure points', fontsize=11)
    plt.grid()   
    plt.show()
    fig.savefig(Path(evaluation_path) / 'scaling_factor.svg',format='svg',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'scaling_factor.pdf',format='pdf',bbox_inches='tight')
    fig.savefig(Path(evaluation_path) / 'scaling_factor.eps',format='eps',bbox_inches='tight')
    return fig

#-----------------------------------------------------------------------   

def ransac_plot(lr,ransac,X,y,inlier_mask,outlier_mask,successful):
    # Predict data of estimated models
    line_X = np.linspace(X.min(), X.max(),2)[:, np.newaxis]
    line_y = lr.predict(line_X)
    if successful:
        line_y_ransac = ransac.predict(line_X)
    # Compare estimated coefficients
    print("Estimated coefficients (true, linear regression, RANSAC):")
    if successful: print("coef", lr.coef_, ransac.estimator_.coef_)
    else: print("coef", lr.coef_, "not found")
    fig = plt.figure(); lw = 2
    if successful:
        plt.scatter(X[inlier_mask], y[inlier_mask], color="yellowgreen", marker=".", label="Inliers")
        plt.scatter(X[outlier_mask], y[outlier_mask], color="gold", marker=".", label="Outliers")
    else: 
         plt.scatter(X, y, color="yellowgreen", marker=".", label="Inliers/Outliers")
    plt.plot(line_X, line_y, color="navy", linewidth=lw, label="Linear regressor")
    if successful: plt.plot(line_X,line_y_ransac,color="cornflowerblue",linewidth=lw,label="RANSAC regressor")
    plt.legend(loc="lower right")
    plt.xlabel("Input")
    plt.ylabel("Response")
    plt.show()
    return fig