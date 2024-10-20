import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import importlib
import sys
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4

###################################################################################
# code is originally based on https://github.com/demul/extrinsic2pyramid, but has been modified
###################################################################################
class CameraPoseVisualizer:
    def __init__(self, xlim, ylim, figsize = (18, 7)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_aspect("equal")
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_xlabel('x in m')
        self.ax.set_ylabel('y in m')
        self.ax.set_axisbelow(True)  # Grid hinter die Grafik setzen
        self.ax.grid(True)  # Grid aktivieren
        print('initialize camera pose visualizer 2D')
        
    def extrinsic2triangle(self, extrinsic, color='r', focal_len=5, aspect_ratio=0.3, sensor_width=0.3, scale_rel=1, alpha=0.35):
        # Anpassung der Kameraskalierung unter Berücksichtigung aller Achsen (x, y, z)
        scale_extrinsic = np.mean([np.linalg.norm(extrinsic[:, 0]),  # x-Achse
                                np.linalg.norm(extrinsic[:, 1]),  # y-Achse
                                np.linalg.norm(extrinsic[:, 2])]) # z-Achse
        scale = scale_rel / scale_extrinsic
        # Standard-Vertex der Kamera (mit Z, weil Extrinsic 4x4 ist)
        vertex_std = np.array([[0, 0, 0, 1],  # Ursprung (Kameraposition)
                            [sensor_width * scale, 0, focal_len * scale, 1],  # Rechte Ecke des Frustums
                            [-sensor_width * scale, 0, focal_len * scale, 1]])  # Linke Ecke des Frustums
        # Transformation anwenden
        vertex_transformed = (vertex_std @ extrinsic.T)[:, :3]  # Transformation, behalte x, y, z
        # Für 2D-Plot: Z-Komponente ignorieren, nur x und y verwenden
        vertex_transformed_2d = vertex_transformed[:, :2]  # Nur x und y
        # Erstellen des 2D-Polygons für die Kamera (Kameradreieck)
        camera_triangle = [vertex_transformed_2d[0], vertex_transformed_2d[1], vertex_transformed_2d[2]]
        # Polygon in 2D-Darstellung hinzufügen
        polygon = Polygon(camera_triangle, closed=True, facecolor=color, edgecolor='k', alpha=alpha)
        self.ax.add_patch(polygon)       
        
    def add_focuspoint(self, focuspoint, color='blue', marker='o', size=100):
        self.ax.scatter(focuspoint[0], focuspoint[1], color=color, s=size, marker=marker)
        
    def draw_lines_to_focuspoint(self,cams,focuspoint, line_style='--', color='blue',linewidth = 1,alpha = 0.3):
        for cam in cams:
            extrinsic = cam.TransformationStatic
            cam_pos = extrinsic[:2,3]
            self.ax.plot([cam_pos[0], focuspoint[0]], [cam_pos[1], focuspoint[1]], linestyle=line_style, color=color,linewidth=linewidth, alpha=alpha)
         
    def draw_rotation_axis(self, axis_vector, length=5, color='green', width=0.005, alpha=1.0, fontsize = 10, label=None):
        origin = np.array([0, 0])  # Ursprung
        # Normalisiere den Vektor
        axis_vector = np.array(axis_vector)
        axis_vector_normalized = axis_vector / np.linalg.norm(axis_vector)  # Normierung
        # Skaliere den Vektor auf die gewünschte Länge
        axis_vector_scaled = axis_vector_normalized * length
        # Zeichne den Vektor
        self.ax.quiver(origin[0], origin[1], axis_vector_scaled[0], axis_vector_scaled[1], 
                       angles='xy', scale_units='xy', scale=1, color=color, 
                       width=width, alpha=alpha)
        # Beschrifte den Vektor (optional)
        if label:
            self.ax.text(axis_vector_scaled[0], axis_vector_scaled[1], label, fontsize = fontsize, color=color,
                         verticalalignment='bottom', horizontalalignment='right')
            
    def point_in_cam_center(self,extrinsic,point_size):
            pos = extrinsic[:2,3]
            # Punkt im Kamerazentrum hinzufügen (schwarzer Punkt)
            self.ax.scatter(pos[0], pos[1], color='black', s=point_size, zorder=5)  # Schwarzer Punkt
         
    def show(self,title=None,show=True):
        if title is not None:
            plt.title(title)
        plt.tight_layout()
        if show: plt.show()
        
    def load_cameras(self,cams,focal_length=0.016,aspect_ratio=1.3358,sensor_width=0.00712,scale=2,alpha=0.35,select_color="r",cam_center = True, point_size = 10):
        for i,cam in enumerate(cams):
            Transformation = cam.TransformationStatic
            color = select_color
            self.extrinsic2triangle(Transformation, color, focal_length,aspect_ratio,sensor_width,scale,alpha)
            if cam_center: self.point_in_cam_center(Transformation,point_size)