import numpy as np
import pandas as pd
import subprocess
from pathlib import Path
import os
#import open3d as o3d
#import cv2
import vedo

project_name = 'moving_BP_02_30images_2'

output_path = r'C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\meshroom_data\moving_MS_20_2_60images_1'
mesh_path = str(Path(output_path) / 'texturedMesh.obj')
texture_path = str(Path(output_path) /'texture_1001.png')

mesh_vedo = vedo.Mesh(mesh_path).texture(texture_path)

# List of planes
planes = ['xy', 'yz', 'xz']
# List of angles
angles = np.linspace(0, 360, 3, endpoint=False)
# Creating a Plotter object with the number of planes multiplied by the number of angles as subplots, without axes and with individual cameras
plt = vedo.Plotter(N=len(angles) * len(planes), axes=False, sharecam=False)
# Initializing an index variable to keep track of the current subplot index
ind = 0
# Looping through each plane
for plane in planes:
    # Looping through each angle
    for angle in angles:
        # Showing the mesh on the current subplot, with the title consisting of the plane name followed by the angle value formatted as an integer
        plt.at(ind).show(mesh_vedo, [plane + '\n' + f'{angle:.0f}'])
        # Setting the camera to look at the current plane
        plt.at(ind).look_at(plane)
        # Setting the azimuth angle for the current subplot
        plt.at(ind).azimuth(angle)
        # zooming for the current subplot
        plt.at(ind).zoom(1.5)
        # Incrementing the subplot index
        ind += 1
# Generating a screenshot path based on the output directory and project name
screenshot_path = Path(output_path) / project_name
# Capturing a screenshot of the current plot and saving it to the generated screenshot path
vedo.screenshot(screenshot_path)
# Displaying the Plotter object with interactive mode enabled, allowing user interaction with the plots if supported by the plotting backend
plt.interactive()
