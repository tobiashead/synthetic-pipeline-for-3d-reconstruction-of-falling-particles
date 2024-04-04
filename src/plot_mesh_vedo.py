import numpy as np
from pathlib import Path
import vedo
vedo.settings.default_backend = 'vtk'
def plot_mesh_vedo(project_name,output_path):
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
    screenshot_path = Path(output_path) / (project_name + '.png')
    # Capturing a screenshot of the current plot and saving it to the generated screenshot path
    vedo.screenshot(screenshot_path).close()
    
    return plt, screenshot_path

if __name__ == "__main__":
    output_path = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\BP_02"
    mesh_path = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\BP_02\centered\BP_2_Model.obj"
    texture_path = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\BP_02\centered\BP_2_Model.1001.jpg"
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
    screenshot_path = Path(output_path) / ("GT_vedo" + '.png')
    # Capturing a screenshot of the current plot and saving it to the generated screenshot path
    vedo.screenshot(screenshot_path).close()   