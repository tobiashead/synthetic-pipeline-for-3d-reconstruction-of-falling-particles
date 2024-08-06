import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation
import importlib
import sys
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import Get_Location_Rotation3x3_Scale_from_Transformation4x4

###################################################################################
# code is originally based on https://github.com/demul/extrinsic2pyramid, but has been modified
###################################################################################
class CameraPoseVisualizer:
    def __init__(self, xlim, ylim, zlim, figsize = (18, 7)):
        self.fig = plt.figure(figsize=figsize)
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

    def extrinsic2pyramid(self, extrinsic, color='r', focal_len=5, aspect_ratio=0.3,sensor_width=0.3,scale_rel=1,alpha=0.35,DrawCoordSystem=True):
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
            Poly3DCollection(meshes, facecolors=color, linewidths=0.5, edgecolors='k',alpha=alpha))
        
        # Draw coordinate system
        if DrawCoordSystem == True:
            origin = np.array([0, 0, 0,1]) @ extrinsic.T;                   origin_transformed = origin[:3]
            x_axis = np.array([focal_len*scale*.5, 0, 0,1]) @ extrinsic.T;  x_axis_transformed = x_axis[:3]
            y_axis = np.array([0, focal_len*scale*.5, 0,1]) @ extrinsic.T;  y_axis_transformed = y_axis[:3]
            z_axis = np.array([0, 0, focal_len*scale*.5,1]) @ extrinsic.T;  z_axis_transformed = z_axis[:3]
            self.ax.quiver(*origin_transformed, *(x_axis_transformed-origin_transformed), color='r',linewidth=0.8)
            self.ax.quiver(*origin_transformed, *(y_axis_transformed-origin_transformed), color='g',linewidth=0.8)
            self.ax.quiver(*origin_transformed, *(z_axis_transformed-origin_transformed), color='b',linewidth=0.8)

    def customize_legend(self, list_label):
        list_handle = []
        for idx, label in enumerate(list_label):
            color = plt.cm.rainbow(idx / len(list_label))
            patch = Patch(color=color, label=label)
            list_handle.append(patch)
        plt.legend(loc='right', bbox_to_anchor=(1.8, 0.5), handles=list_handle)

    def colorbar(self,norm,cmap,label, orientation = 'vertical'):
        fig = self.fig
        ax = fig.gca()
        scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        scalar_mappable.set_array([])
        fig.colorbar(scalar_mappable, ax=ax, orientation=orientation, label=label)  # shrink=0.9,pad=0.1

    def show(self,title=None,show=True):
        if title is not None:
            plt.title(title)
        plt.tight_layout()
        if show: plt.show()

        
    def save(self,path, bbox_inches = 'tight',pad_inches=0.1):
        #plt.savefig(str(path) + ".eps", format='eps',bbox_inches= bbox_inches,pad_inches=pad_inches)
        plt.savefig(str(path) + ".pdf", format='pdf',bbox_inches= bbox_inches,pad_inches=pad_inches)
        plt.savefig(str(path) + ".svg", format='svg',bbox_inches= bbox_inches,pad_inches=pad_inches)
    
    def color_based_on_height(self,Transformation,alpha,colormap='viridis'):
        import matplotlib.colors as mcolors
        location,_,_ = Get_Location_Rotation3x3_Scale_from_Transformation4x4(Transformation)
        height = location[2]
        cmap = plt.cm.get_cmap(colormap)  # Choose a colormap (e.g., 'viridis')
        z_min = self.ax.get_zlim()[0]; z_max = self.ax.get_zlim()[1]
        norm = mcolors.Normalize(vmin=z_min, vmax=z_max)  # Define the range of normalized height values (adjust as needed)
        # Map normalized height to color using the colormap
        color = cmap(norm(height))
        # Adjust alpha channel
        color_with_alpha = color[:3] + (alpha,)
        # Calculation of the color value based on the height
        return color_with_alpha,norm,cmap
    
    def color_based_on_timestep(self,TimeStep,TimeStep_max,alpha,colormap='viridis'):
        # Calculation of the color value based on timestep
        import matplotlib.colors as mcolors
        cmap = plt.cm.get_cmap(colormap)  # Choose a colormap (e.g., 'viridis')
        norm = mcolors.Normalize(vmin=1, vmax=TimeStep_max)  # Define the range of normalized height values (adjust as needed), vmin=0
        # Map normalized height to color using the colormap
        color = cmap(norm(TimeStep))
        # Adjust alpha channel
        color_with_alpha = color[:3] + (alpha,)
        return color_with_alpha,norm,cmap
    
    def load_cameras(self,cams,focal_length=0.016,aspect_ratio=1.3358,sensor_width=0.00712,scale=2,alpha=0.35,DrawCoordSystem=True,colormap='viridis',static_scene = True, select_color =None,colorbar=False,color_based_on_height = False, colorbar_orientation = 'vertical'):
        obj_moving = False if cams[-1].TimeStep == 1 else True
        TimeStep_max = max(item.TimeStep for item in cams)
        skip_colorbar = False  
        for i,cam in enumerate(cams):
            if static_scene:
                if  hasattr(cam, 'TransformationStatic'):
                    Transformation = cam.TransformationStatic
                else:
                    print("Error! Static transformation matrix unknown.")
            else:
                if  hasattr(cam, 'TransformationDynamic'):
                    Transformation = cam.TransformationDynamic
                else:
                    print("Error! Dynamic transformation matrix unknown.")
            if select_color == None:    
                if color_based_on_height == True: 
                    color,norm,cmap = self.color_based_on_height(Transformation,alpha,colormap)
                else:
                    if obj_moving == True:
                        color,norm,cmap = self.color_based_on_timestep(cam.TimeStep,TimeStep_max,alpha,colormap)
                    else:
                        color = 'r'
                        print("Warning! Display of colors depending on the time step NOT possible. Only one time step exists.")
                        skip_colorbar = True
            else:
                color = select_color
            self.extrinsic2pyramid(Transformation, color, focal_length,aspect_ratio,sensor_width,scale,alpha,DrawCoordSystem)
        if colorbar and skip_colorbar == False:
            label = "Time Step" if obj_moving else "Height in m" 
            self.colorbar(norm,cmap,label,colorbar_orientation) 
                     
    def load_cube(self,cams_ref,static_scene = False,alpha = None,position = np.array([0,0,1])):
            # dynamic case    
        if cams_ref[-1].TimeStep != 1 and static_scene == False:
            if alpha == None:      
                self.create_cube(position=position+np.array([0,0,0.2]),size=0.03,color='k',alpha=0.4,rotation=[15,0,15])   # size=a=b=c
                self.create_cube(position=position+np.array([0,0,0.05]),size=0.03,color='k',alpha=0.3,rotation=[30,0,30])
                self.create_cube(position=position-np.array([0,0,0.05]),size=0.03,color='k',alpha=0.2,rotation=[45,0,45])
                self.create_cube(position=position-np.array([0,0,0.2]),size=0.03,color='k',alpha=0.1,rotation=[60,0,-60])
            else:
                self.create_cube(position=position+np.array([0,0,0.2]),size=0.02,color='k',alpha=alpha,rotation=[15,0,15])   # size=a=b=c
                self.create_cube(position=position+np.array([0,0,0.05]),size=0.02,color='k',alpha=alpha,rotation=[30,0,30])
                self.create_cube(position=position-np.array([0,0,0.05]),size=0.02,color='k',alpha=alpha,rotation=[45,0,45])
                self.create_cube(position=position-np.array([0,0,0.2]),size=0.02,color='k',alpha=alpha,rotation=[60,0,-60])
        # static case    
        else:
            self.create_cube(position=position,size=0.03,color='k',alpha=0.3)
            
    def load_lights(self,lights,color="orange", size=30, alpha=0.8):
        for i in range(len(lights)):
            light = lights.iloc[i]
            x = light["PositionX"]; y = light["PositionY"]; z = light["PositionZ"]
            self.ax.scatter(x,y,z,c=color,marker='o',s = size,alpha=alpha)
            
    