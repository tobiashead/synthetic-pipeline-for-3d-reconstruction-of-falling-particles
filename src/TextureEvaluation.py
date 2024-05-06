import os
from pathlib import Path
import json
import subprocess
import shutil
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np

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
    
def GLCM_Evaluation(OutputTextureRef_path,OutputTextureRec_path,patch_size,image_number,levels,distances,random_seed=124):
    image_ref_path = get_image_path_by_number(OutputTextureRef_path,image_number)
    image_rec_path = get_image_path_by_number(OutputTextureRec_path,image_number)
    color_image_ref = ski.io.imread(image_ref_path)
    color_image_rec = ski.io.imread(image_rec_path)
    gray_image_ref = ski.color.rgb2gray(color_image_ref)
    gray_image_rec = ski.color.rgb2gray(color_image_rec)
    image_ref = np.uint8(gray_image_ref * (levels-1))
    image_rec = np.uint8(gray_image_rec * (levels-1))
    height, width = color_image_ref.shape[:2]
    locations = []
    windows_ref = []
    windows_rec = []
    num_random_pixels = 4
    for i in range(num_random_pixels):
        ASM = 1
        while ASM > 0.4:
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
        windows_ref.append(patch_ref) 
        locations.append(loc)
        windows_rec.append(image_rec[loc[0] : loc[0] + patch_size, loc[1] : loc[1] + patch_size])
    # compute some GLCM properties each patch
    xs = []
    ys = []
    ASMs = []
    colors = ['red', 'green', 'blue', 'orange']
    for window in windows_ref + windows_rec:
        glcm = ski.feature.graycomatrix(
            window, distances=[distances], angles=[0], levels=levels, symmetric=True, normed=True
        )
        xs.append(ski.feature.graycoprops(glcm, 'dissimilarity')[0, 0])
        ys.append(ski.feature.graycoprops(glcm, 'correlation')[0, 0])
        #ys.append(ski.feature.graycoprops(glcm, 'energy')[0, 0])
        ASMs.append(ski.feature.graycoprops(glcm, 'ASM')[0, 0])
    # create the figure
    fig = plt.figure(figsize=(8, 8))
    # display original image with locations of patches
    ax = fig.add_subplot(4, 2, 1)
    ax.imshow(image_ref, cmap=plt.cm.gray, vmin=0, vmax=levels-1)
    i = 0
    for y, x in locations:
        ax.plot(x + patch_size / 2, y + patch_size / 2, 's',color=colors[i]); i = i+1
    ax.set_xlabel('Greyscale Image - Ref.')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('image')
    # display original image with locations of patches
    ax = fig.add_subplot(4, 2, 3)
    ax.imshow(image_rec, cmap=plt.cm.gray, vmin=0, vmax=levels-1)
    i = 0
    for y, x in locations:
        ax.plot(x + patch_size / 2, y + patch_size / 2, 's',color=colors[i]); i = i+1
    ax.set_xlabel('Greyscale Image - Rec.')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('image')
    # for each patch, plot (dissimilarity, correlation)
    ax = fig.add_subplot(2, 2, 2)
    i = 0
    for x, y in zip(xs[:len(windows_ref)], ys[:len(windows_ref)]):
        ax.plot(x, y, 'o',label = f'ref {i+1}',color=colors[i])
        i += 1
    i = 0
    for x, y in zip(xs[len(windows_ref):], ys[len(windows_ref):]):
        ax.plot(x, y, 'x', label=f'rec {i+1}',color=colors[i])
        i += 1
    ax.set_xlabel('GLCM Dissimilarity')
    ax.set_ylabel('GLCM Correlation')
    ax.legend()
    for i in range(4):
        ax = fig.add_subplot(4, 4, 2*4+1+i)
        ax.imshow(windows_ref[i], cmap=plt.cm.gray, vmin=0, vmax=levels-1)
        ax.set_xlabel(f"Window {i+1} (Ref.)")
        ax = fig.add_subplot(4, 4, 3*4+1+i)
        ax.imshow(windows_rec[i], cmap=plt.cm.gray, vmin=0, vmax=levels-1)
        ax.set_xlabel(f"Window {i+1} (Rec.)")
    # display the patches and plot
    fig.suptitle('Grey level co-occurrence matrix features', fontsize=11, y=1)
    plt.tight_layout()
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

