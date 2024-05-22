import sys
import importlib
from src.classes import camera_reference, camera_reconstructed
from typing import List, Type
importlib.reload(sys.modules['src.camera_pose_visualizer']) if 'src.camera_pose_visualizer' in sys.modules else None
from src.camera_pose_visualizer import CameraPoseVisualizer
import matplotlib.pyplot as plt
from pathlib import Path
import os

def PlotCamComparisonStatic(
    cams_ref: List[Type[camera_reference]],
    cams_rec: List[Type[camera_reconstructed]],
    focal_length: float,
    aspect_ratio: float,
    sensor_width: float
) -> None:
    
    
    # top=0.976,
    # bottom=0.041,
    # left=0.0,
    # right=1.0,
    # hspace=0.2,
    # wspace=0.2
    current_dir = Path(__file__).parent
    style_path = current_dir / 'thesis.mplstyle'
    #plt.switch_backend('qt5agg')
    plt.style.use(str(style_path))
    elev = 26; azim = 53    
    visualizer = CameraPoseVisualizer([-0.15, 0.15], [-0.15, 0.15], [0.85, 1.15],figsize=(5.46,4.5))
    visualizer.load_cameras(cams_rec,focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.1,DrawCoordSystem=True,static_scene=True,colorbar=True,colorbar_orientation='vertical')
    visualizer.load_cameras(cams_ref,focal_length,aspect_ratio,sensor_width,scale=1.5,alpha=0.5,DrawCoordSystem=False,static_scene=True)
    visualizer.load_cube(cams_ref,static_scene=True)
    visualizer.ax.view_init(elev=elev, azim=azim)
    cbar = visualizer.fig.axes[1].set_ylabel("Zeitpunkt $k$")
    visualizer.show() 
    azim = visualizer.ax.azim
    elev = visualizer.ax.elev
    print(f"Saved azimuth: {azim}, elevation: {elev}")
    
    
def PlotCamComparisonDynamic(
    cams_ref: List[Type[camera_reference]],
    cams_rec: List[Type[camera_reconstructed]],
    focal_length: float,
    aspect_ratio: float,
    sensor_width: float
) -> None:
    
    
    # top=0.976,
    # bottom=0.041,
    # left=0.0,
    # right=1.0,
    # hspace=0.2,
    # wspace=0.2
    current_dir = Path(__file__).parent
    style_path = current_dir / 'thesis.mplstyle'
    #plt.switch_backend('qt5agg')
    plt.style.use(str(style_path))
    elev = 26; azim = 53    
    visualizer = CameraPoseVisualizer([-0.15, 0.15], [-0.15, 0.15], [0.85, 1.15],figsize=(5.46,4.5))
    visualizer.load_cameras(cams_rec[:3],focal_length,aspect_ratio,sensor_width,scale=2,alpha=0.1,DrawCoordSystem=True,static_scene=False,colorbar=False,select_color='orange')
    visualizer.load_cameras(cams_ref[:3],focal_length,aspect_ratio,sensor_width,scale=1.5,alpha=0.5,DrawCoordSystem=False,static_scene=False,select_color='orange')
    visualizer.load_cube(cams_ref,static_scene=False)
    visualizer.ax.view_init(elev=elev, azim=azim)
    visualizer.show() 
    azim = visualizer.ax.azim
    elev = visualizer.ax.elev
    print(f"Saved azimuth: {azim}, elevation: {elev}")
  
    