import os
from pathlib import Path
import json
import subprocess
import shutil
import matplotlib as mpl
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np
from icecream import ic

# Schriftgroesse
fsize = 11 # Allgemein
tsize = 11 # Legende

# Grundeinstellungen (Ticks nach innen, Schriftart)
tdir = 'in'
major = 5.0 # Länge major ticks
minor = 3.0 # Länge minor ticks
lwidth = 0.8 # Dicke Rahmen
lhandle = 2.0 # Länge handle in Legende
plt.style.use('default')
plt.rcParams['font.family']='serif'
cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmr10.ttf')
plt.rcParams['font.serif']=cmfont.get_name()
plt.rcParams['mathtext.fontset']='cm'
plt.rcParams['axes.unicode_minus']=False
plt.rcParams['font.size'] = fsize
plt.rcParams['legend.fontsize'] = tsize
plt.rcParams['xtick.direction'] = tdir
plt.rcParams['ytick.direction'] = tdir
plt.rcParams['xtick.major.size'] = major
plt.rcParams['xtick.minor.size'] = minor
plt.rcParams['ytick.major.size'] = major
plt.rcParams['ytick.minor.size'] = minor
plt.rcParams['axes.linewidth'] = lwidth
plt.rcParams['legend.handlelength'] = lhandle

# Bildgroesse
#fig_width_pt = 393.1654  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0/72.27               # Convert pt to inch
#golden_mean = (np.sqrt(5)-1.0)/2.0    # Aesthetic ratio
#fig_width = fig_width_pt*inches_per_pt  # width in inches
#fig_height = fig_width*golden_mean      # height in inches


def GetImagesForTextureEvaluation(obj_path,output_path,script_path,blender_path):
    # Parameter File Path
    TextureParams_path = Path(script_path) / "params_textureEvaluation.json"
    # Load Parameter from json file
    with open(TextureParams_path, 'r') as file:
        params_texture = json.load(file)
    # Change parameters. In this case, object path and output path
    params_texture["io"]["obj_path"] = str(obj_path)
    params_texture["io"]["output_path"] = str(output_path)
    # Update Json File
    with open(TextureParams_path, "w") as json_file:
        json.dump(params_texture, json_file, indent=5) 
    # delete output folder if already exist 
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    # create output folder
    os.makedirs(output_path)
    # render images in blender
    script_path = Path(script_path) / "texture_evaluation.py"
    command = f"{blender_path} --background --python {script_path}"
    return_code = subprocess.run(command,text=True)  
    
def GLCM_Evaluation(OutputTextureRef_path,OutputTextureRec_path,patch_size,image_number,levels,distances,random_seed=124,features = ["dissimilarity","correlation"],num_windows=4, offset = [0,0],offset_option = "absolute"):
    # create Grey Scale Image
    image_ref, image_rec, height, width = create_greyscale_image(OutputTextureRef_path,OutputTextureRec_path,levels,image_number)
    # Identify window on which the object is visible
    locations, windows_ref, windows_rec = identify_windows_containing_the_object(random_seed,height,width,patch_size,levels,distances,image_ref,image_rec,num_windows,ASM_crit = 0.1)
    # Calculate GLCM_features for the choosen windows
    feature_matrix_ref,_ = calculate_GLCM_features(windows_ref,distances,levels,features)
    feature_matrix_rec,_ = calculate_GLCM_features(windows_rec,distances,levels,features)
    # Add Offset
    if offset_option == "absolute":
        feature_matrix_rec[:,0] += offset[0]; feature_matrix_rec[:,1] += offset[1]
    else:
        feature_matrix_rec[:,0] += offset[0]*feature_matrix_rec[:,0]; feature_matrix_rec[:,1] += offset[1]*feature_matrix_rec[:,1] 
    # create the figure
    GLCM_figure1(image_ref,image_rec,windows_ref,windows_rec,feature_matrix_ref,feature_matrix_rec,features,levels,patch_size,locations)
    
def identify_windows_containing_the_object(random_seed,height,width,patch_size,levels,distances,image_ref,image_rec=None,num_windows=4,ASM_crit = 0.01):
    locations = []
    windows_ref = []
    windows_rec = []
    for i in range(num_windows):
        count = 1; ASM = 1 
        while ASM > ASM_crit and count < 1000:
            np.random.seed(random_seed)
            random_pixel_x = np.random.randint(0, height-patch_size)
            random_seed += 1
            np.random.seed(random_seed)
            random_pixel_y = np.random.randint(0, width-patch_size)
            random_seed += 1
            loc = [random_pixel_x,random_pixel_y]
            patch_ref = image_ref[loc[0] : loc[0] + patch_size, loc[1] : loc[1] + patch_size]
            glcm = ski.feature.graycomatrix(
                patch_ref, distances=[distances], angles=[0], levels=levels, symmetric=True, normed=True
            )
            ASM = ski.feature.graycoprops(glcm, 'ASM')[0, 0]
            count += 1
        windows_ref.append(patch_ref) 
        locations.append(loc)
        if count == 1000: print(f"Warning. After 1000 iterations, no image section fulfills criterion: ASM < {ASM_crit}")
        if image_rec is not None:
            windows_rec.append(image_rec[loc[0] : loc[0] + patch_size, loc[1] : loc[1] + patch_size])
    return locations, windows_ref, windows_rec
        
def calculate_GLCM_features(windows,distances,levels,features):
    feature_matrix = np.zeros([len(windows),len(features)])
    for i,window in enumerate(windows):
        glcm = ski.feature.graycomatrix(
            window, distances=[distances], angles=[0], levels=levels, symmetric=True, normed=True
        )
        for j,feature in enumerate(features):
            feature_value = ski.feature.graycoprops(glcm, feature)[0, 0]
            feature_matrix[i,j] = feature_value
    return feature_matrix, glcm

def GLCM_figure1(image_ref,image_rec,windows_ref,windows_rec,features_ref,features_rec,features,levels,patch_size,locations):
    # create figure
    fig = plt.figure(layout='constrained',figsize=(5.44, 6))
    subfigs = fig.subfigures(2, 1, wspace=0.07) 
    # define colors
    colors = ['blue', 'red', 'green', 'orange', 'indigo', 'purple', 'cyan', 'magenta', 'brown', 'pink', 'olive', 'teal']
    # display original image with locations of patches
    subfigs_top = subfigs[0].subfigures(1,2,width_ratios = [2,3])
    subfigs_top_left =  subfigs_top[0].subfigures(2,1)
    ax = subfigs_top_left[0].add_subplot()
    ax.imshow(image_ref, cmap=plt.cm.gray, vmin=0, vmax=levels-1)
    i = 0
    for y, x in locations:
        ax.plot(x + patch_size / 2, y + patch_size / 2, 's',color=colors[i]); i = i+1
    ax.set_xlabel('Greyscale Image - Ref.')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('image')
    # display reconstructed image with locations of patches
    ax = subfigs_top_left[1].add_subplot()
    ax.imshow(image_rec, cmap=plt.cm.gray, vmin=0, vmax=levels-1)
    i = 0
    for y, x in locations:
        ax.plot(x + patch_size / 2, y + patch_size / 2, 'o',color=colors[i]); i = i+1
    ax.set_xlabel('Greyscale Image - Rec.')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('image')
    # for each patch, plot the first two features
    subfigs_top_right = subfigs_top[1].subfigures(2,1,height_ratios = [5,3])
    ax = subfigs_top_right[0].add_subplot()
    for i in range(len(features_ref[:,0])):
        x_ref = features_ref[i,0]; y_ref = features_ref[i,1]
        x_rec = features_rec[i,0]; y_rec = features_rec[i,1]
        ax.plot(x_ref, y_ref, 's', label=f'ref {i+1}',color=colors[i])
        ax.plot(x_rec, y_rec, 'o', label=f'rec {i+1}',color=colors[i])
    ax.set_xlabel(features[0])
    ax.set_ylabel(features[1])
    ax.grid()
    # Create a legend subplot and plot the legend
    ax_legend = subfigs_top_right[1].add_subplot()
    ax_legend.axis('off')  # Turn off axes for the legend subplot
    ax_legend.legend(*ax.get_legend_handles_labels(), loc='upper center', ncol=2)
    # plot the windows, for which the GLCM matrix is calculated
    subfigs_bottom = subfigs[1].subfigures(int(np.ceil(len(windows_rec)/2)),4)
    row = 0; column = 0 
    for i in range(len(windows_ref)):
        if column == 4: column = 0; row += 1 
        ax = subfigs_bottom[row,column].add_subplot(); column += 1
        ax.imshow(windows_ref[i], cmap=plt.cm.gray, vmin=0, vmax=levels-1)
        ax.set_xlabel(f"Window {i+1} (Ref.)")
        ax = subfigs_bottom[row,column].add_subplot(); column += 1
        ax.imshow(windows_rec[i], cmap=plt.cm.gray, vmin=0, vmax=levels-1)
        ax.set_xlabel(f"Window {i+1} (Rec.)")
    fig.suptitle('Grey level co-occurrence matrix features', fontsize=11, y=1.05)
    fig.tight_layout
    plt.show()
    
def get_image_path_by_number(directory, image_number):
    if not os.path.isdir(directory):
        print("The specified directory does not exist.")
        return None
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    #image_files = [f for f in image_files if f.lower().endswith('.jpg')] 
    image_files.sort()
    if image_number < 1 or image_number > len(image_files):
        print(f"Invalid image number. Valid range is 1 to {len(image_files)}")
        return None
    return os.path.join(directory, image_files[image_number - 1])

def create_greyscale_image(OutputTextureRef_path,OutputTextureRec_path,levels,image_number):
    image_ref_path = get_image_path_by_number(OutputTextureRef_path,image_number)
    image_rec_path = get_image_path_by_number(OutputTextureRec_path,image_number)
    color_image_ref = ski.io.imread(image_ref_path)
    color_image_rec = ski.io.imread(image_rec_path)
    gray_image_ref = ski.color.rgb2gray(color_image_ref)
    gray_image_rec = ski.color.rgb2gray(color_image_rec)
    image_ref = np.uint8(gray_image_ref * (levels-1))
    image_rec = np.uint8(gray_image_rec * (levels-1))
    height, width = color_image_ref.shape[:2]
    return image_ref, image_rec, height, width

def GLCM_feature_correlation(OutputTextureRef_path,OutputTextureRec_path,patch_size,levels,distances,features = ["dissimilarity","correlation"],measurement="absolute",offset = [0,0],offset_option = "absolute"):
    n_images = 12
    n_random_seeds = 10
    n_windows = 10
    features_rec = np.ones([n_images*n_random_seeds*n_windows,2])*(-1)
    features_ref = np.ones([n_images*n_random_seeds*n_windows,2])*(-1)
    start = 0
    for image_number in np.arange(1,n_images+1):
        # create Grey Scale Image
        image_ref, image_rec, height, width = create_greyscale_image(OutputTextureRef_path,OutputTextureRec_path,levels,image_number)
        # Identify window on which the object is visible
        for seed in np.arange(1,n_random_seeds+1):
            locations, windows_ref, windows_rec = identify_windows_containing_the_object(seed,height,width,patch_size,levels,distances,image_ref,image_rec,n_windows,ASM_crit = 0.1)
            # Calculate GLCM_features for the choosen windows
            feature_matrix_ref,_ = calculate_GLCM_features(windows_ref,distances,levels,features)
            feature_matrix_rec,_ = calculate_GLCM_features(windows_rec,distances,levels,features)
            end = start + n_windows
            features_rec[start:end,:] = feature_matrix_rec
            features_ref[start:end,:] = feature_matrix_ref
            start = end
    if offset_option == "absolute":
        features_rec[:,0] += offset[0]; features_rec[:,1] += offset[1]
    else:
        features_rec[:,0] += offset[0]*features_rec[:,0]; features_rec[:,1] += offset[1]*features_rec[:,1]         
    if measurement == "absolute":
        features_diff = features_ref - features_rec
    else: 
        features_diff = np.divide((features_ref - features_rec),features_rec)
    mean_feat1 ,median_feat1 = print_GLCM_feature_comparison(features[0],features_diff[:,0],measurement)
    mean_feat2 ,median_feat2 = print_GLCM_feature_comparison(features[1],features_diff[:,1],measurement)
    mean = [mean_feat1, mean_feat2]; median = [median_feat1, median_feat2]
    Plot_GLCM_feature_correlation(features_diff,features,measurement)
    return mean, median
    
    
def Plot_GLCM_feature_correlation(features_diff,features,measurement):        
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1,2,1)
    feature_diff = features_diff[:,0] if measurement == "absolute" else features_diff[:,0]*100
    ax.hist(feature_diff, bins=15, color='skyblue', edgecolor='black')
    ax.set_ylabel("frequency")
    xlabel = f"absolute error in GLCM feature {features[0]}" if measurement == "absolute" else f"relative error in GLCM feature {features[0]} in %"
    ax.set_xlabel(xlabel)
    ax = fig.add_subplot(1,2,2)
    feature_diff = features_diff[:,1] if measurement == "absolute" else features_diff[:,1]*100
    ax.hist(feature_diff, bins=15, color='skyblue', edgecolor='black')
    xlabel = f"absolute error in GLCM feature {features[1]}" if measurement == "absolute" else f"relative error in GLCM feature {features[1]} in %"
    ax.set_xlabel(xlabel)
    plt.show()
    
        
def print_GLCM_feature_comparison(feature,feature_diff,measurement):
    print(f"GLCM feature: {feature}")
    mean = np.mean(feature_diff)
    median = np.median(feature_diff)
    std = np.std(feature_diff)
    var = std/mean
    if measurement == "absolute":
        print(f"Mean absolute error in GLCM-feature: {mean:.2f}")
        print(f"Median: {median:.2f}")
        print(f"Standard deviation: {std:.2f}")
    else:
        print(f"Mean relative error in GLCM-feature: {mean*100:.2f}%")
        print(f"Median: {median*100:.2f}%")
        print(f"Standard deviation: {std*100:.2f}%")
    print(f"Coefficient of variation: {var:.2f}")    
    print("-----------------------------")
    return mean,median
    
  
    
