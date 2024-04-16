import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation
from pathlib import Path
import importlib
import sys
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4

###################################################################################
# code is originally based on https://github.com/demul/extrinsic2pyramid, but has been modified
###################################################################################
class CameraPoseVisualizer:
    def __init__(self, xlim, ylim, zlim):
        self.fig = plt.figure(figsize=(18, 7))
        self.ax = self.fig.add_subplot(111,projection='3d')
        self.ax.set_aspect("equal")
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_zlim(zlim)
        self.ax.set_xlabel('x in m')
        self.ax.set_ylabel('y in m')
        self.ax.set_zlabel('z in m')
        print('initialize camera pose visualizer')
        
    def create_cube(self, position, size, color='r', alpha=0.35, rotation=None):
        # Define the vertices of the cube relative to its center
        vertices_rel_center = np.array([[-size / 2, -size / 2, -size / 2],
                                        [size / 2, -size / 2, -size / 2],
                                        [size / 2, size / 2, -size / 2],
                                        [-size / 2, size / 2, -size / 2],
                                        [-size / 2, -size / 2, size / 2],
                                        [size / 2, -size / 2, size / 2],
                                        [size / 2, size / 2, size / 2],
                                        [-size / 2, size / 2, size / 2]])

        # Apply rotation if provided
        if rotation is not None:
            rotation_matrix = Rotation.from_euler('xyz', rotation, degrees=True).as_matrix()
            vertices_rel_center = (rotation_matrix @ vertices_rel_center.T).T

        # Translate vertices relative to the provided position
        vertices = vertices_rel_center + position

        # Define the faces of the cube using the vertices
        cube_faces = [[vertices[0], vertices[1], vertices[2], vertices[3]],
                    [vertices[0], vertices[3], vertices[7], vertices[4]],
                    [vertices[1], vertices[2], vertices[6], vertices[5]],
                    [vertices[0], vertices[1], vertices[5], vertices[4]],
                    [vertices[2], vertices[3], vertices[7], vertices[6]],
                    [vertices[4], vertices[5], vertices[6], vertices[7]]]

        self.ax.add_collection3d(
            Poly3DCollection(cube_faces, facecolors=color, linewidths=0.3, edgecolors=color, alpha=alpha))

    def extrinsic2pyramid(self, extrinsic, color='r', focal_len=5, aspect_ratio=0.3,sensor_width=0.3,scale_rel=1,alpha=0.35):
        # Adaptation of the camera scaling due to the different scaling factor of the transformation matrices
        scale_extrinsic = np.mean([np.linalg.norm(extrinsic[:, 0]),np.linalg.norm(extrinsic[:, 1]),np.linalg.norm(extrinsic[:, 2])])
        scale = scale_rel/scale_extrinsic
        vertex_std = np.array([[0, 0, 0, 1],
                               [sensor_width*scale, - sensor_width/aspect_ratio*scale, focal_len*scale, 1],
                               [sensor_width*scale, sensor_width/aspect_ratio*scale, focal_len*scale, 1],
                               [-sensor_width*scale, sensor_width/aspect_ratio*scale, focal_len*scale, 1],
                               [-sensor_width*scale, -sensor_width/aspect_ratio*scale, focal_len*scale, 1]])
        vertex_transformed = vertex_std @ extrinsic.T
        meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
                            [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]]
        self.ax.add_collection3d(
            Poly3DCollection(meshes, facecolors=color, linewidths=0.3, edgecolors=color, alpha=alpha))
        
        # Draw coordinate system
        origin = np.array([0, 0, 0,1]) @ extrinsic.T;                   origin_transformed = origin[:3]
        x_axis = np.array([focal_len*scale*.5, 0, 0,1]) @ extrinsic.T;  x_axis_transformed = x_axis[:3]
        y_axis = np.array([0, focal_len*scale*.5, 0,1]) @ extrinsic.T;  y_axis_transformed = y_axis[:3]
        z_axis = np.array([0, 0, focal_len*scale*.5,1]) @ extrinsic.T;  z_axis_transformed = z_axis[:3]
        self.ax.quiver(*origin_transformed, *(x_axis_transformed-origin_transformed), color='r')
        self.ax.quiver(*origin_transformed, *(y_axis_transformed-origin_transformed), color='g')
        self.ax.quiver(*origin_transformed, *(z_axis_transformed-origin_transformed), color='b')

    def customize_legend(self, list_label):
        list_handle = []
        for idx, label in enumerate(list_label):
            color = plt.cm.rainbow(idx / len(list_label))
            patch = Patch(color=color, label=label)
            list_handle.append(patch)
        plt.legend(loc='right', bbox_to_anchor=(1.8, 0.5), handles=list_handle)

    def colorbar(self, max_frame_length):
        cmap = mpl.cm.rainbow
        norm = mpl.colors.Normalize(vmin=0, vmax=max_frame_length)
        self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), orientation='vertical', label='Frame Number')

    def show(self,title=None):
        if title is not None:
            plt.title(title)
        plt.tight_layout()
        plt.show()
        
    def save(self,path):
        plt.savefig(str(path) + ".eps", format='eps',bbox_inches='tight')
        plt.savefig(str(path) + ".pdf", format='pdf',bbox_inches='tight')
        plt.savefig(str(path) + ".svg", format='svg',bbox_inches='tight')
    
    def load_cameras(self,cams,focal_length,aspect_ratio,sensor_width,scale,alpha=0.35):
        for i,cam in enumerate(cams):
            if cam.TimeStep == 1:
                location,_,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(cam.Transformation)
                if ((location[2] < 1.05) and (location[2]> 0.95)):
                    self.extrinsic2pyramid(cam.Transformation, 'b', focal_length,aspect_ratio,sensor_width,scale,alpha)
                elif location[2] > 1:
                    self.extrinsic2pyramid(cam.Transformation, 'r', focal_length,aspect_ratio,sensor_width,scale,alpha)
                else:
                    self.extrinsic2pyramid(cam.Transformation, 'g', focal_length,aspect_ratio,sensor_width,scale,alpha)
            else: 
                break
    
    def load_cube(self,cams_ref):
            # dynamic case    
        if cams_ref[-1].TimeStep != 1:      
            self.create_cube(position=[0,0,1.2],size=0.03,color='k',alpha=0.4,rotation=[15,0,15])   # size=a=b=c
            self.create_cube(position=[0,0,1.05],size=0.03,color='k',alpha=0.3,rotation=[30,0,30])
            self.create_cube(position=[0,0,0.95],size=0.03,color='k',alpha=0.2,rotation=[45,0,45])
            self.create_cube(position=[0,0,0.8],size=0.03,color='k',alpha=0.1,rotation=[60,0,-60])
        # static case    
        else:
            self.create_cube(position=[0,0,1],size=0.03,color='k',alpha=0.3)
                    