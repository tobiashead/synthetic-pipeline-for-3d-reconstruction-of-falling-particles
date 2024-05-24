import numpy as np
import sys
import importlib
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import rotation_matrix_x, \
                            TransMatrix_from_EulerAngle_and_Location, \
                            Transformation4x4_from_Location3x1_and_Rotation3x3, \
                            rotation_matrix_z    

class camera_reconstructed: 
    def __init__(self, ImageFileName, Pose, TimeStep=None, TransformationStatic=None,CorrespondigIndex=None,TransformationDynamic = None):
        self.ImageFileName = ImageFileName
        self.Location = np.longdouble(Pose["center"])
        self.Rotation = np.longdouble(Pose["rotation"])
        self.TimeStep = TimeStep
        self.TransformationStatic = TransformationStatic
        self.TransformationDynamic = TransformationDynamic
        self.CorrespondigIndex = CorrespondigIndex
        
    def Transformation2WorldCoordinateSystem(self,T,focuspoint):
        # Calculate 4x4 Transformation Matrix from the reconstructed Locations (3) and the 3x3 Rotation Matrix  
        trans_4x4_reconstructed = Transformation4x4_from_Location3x1_and_Rotation3x3(self.Rotation,self.Location)
        # Calculate a Translation, because the point of focus in blender is at x=0, y=0, z = 1, 
        # and the position of the reference object is at x=0,y=0,z=0
        translation_4x4 = np.eye(4,4); translation_4x4[2,3] += focuspoint[2]
        # Meshroom's camera orientation is NOT consistent with the convention of our camera plot function
        # Transformation from Meshroom's camera orientation to the plot function camera orientation
        rot_x_meshroom_plot_cam =  rotation_matrix_x(np.deg2rad(180)) 
        # Merging all individual transformations into a transformation matrix that describes the position
        # and orientation of the cameras in relation to the world coordinate system
        # -------------------------------------------------------------------------
        # T_(meshroom->rec): rot_x_meshroom_plot_cam @ trans_4x4_reconstructed --> Transformation from Meshroom's camera orientation to the plot function camera orientation 
        # T_(rec->ref):  T @ T_(meshroom->rec) --> Transformation from reconstructed coordinate system into  reference coordinate system
        # T_(ref->glob): translation_4x4 --> Transformation from reference coordinate system into global coordinate system
        # T_(rec->glob): T_(ref->glob) @ T_(rec->ref) --> Transformation from reconstructed coordinate system into global coordinate system
        transformation_4x4 = translation_4x4 @ T @ rot_x_meshroom_plot_cam @ trans_4x4_reconstructed
        # Returning and saving the matrix
        self.TransformationStatic = transformation_4x4
        return transformation_4x4
        
              
class camera_reference: 
    def __init__(self, ImageFileName, Location, EulerAngle, TimeStep, CorrespondigIndex=None, TransformationDynamic=None,TransformationStatic=None, CorrespondigIndexObject = None):
        self.ImageFileName = ImageFileName
        self.Location = Location
        self.EulerAngle = EulerAngle
        self.TransformationDynamic = TransformationDynamic
        self.TimeStep = TimeStep
        self.CorrespondigIndex = CorrespondigIndex
        self.CorrespondigIndexObject = CorrespondigIndexObject 
        self.TransformationStatic = TransformationStatic
        
    def Transformation2WorldCoordinateSystem(self):
        x = self.Location[0]; y = self.Location[1]; z = self.Location[2]
        theta_x = self.EulerAngle[0]; theta_y = self.EulerAngle[1]; theta_z = self.EulerAngle[2]
        # Blender's coordinate system matches the global coordinate system --> no Transformation necesssary
        # but transformation of Blender camera coordinate convention into camera plot convention necesssary
        theta_x += np.deg2rad(180) 
        transformation_4x4 = TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z)
        # saving the matrix, could be dynamic or static case
        self.TransformationDynamic = transformation_4x4
        self.TransformationStatic = transformation_4x4
        return transformation_4x4
    
    def Dynamic2StaticScene(self,T_obj,T_obj0,focuspoint):
        # Get the transformation matrix of the camera of the dynamic scene 
        T_cam = self.TransformationDynamic
        # Relative position (translation in z-direction only) between camera and object at time t=0s (TODO)
        T_cam2obj0_transl = np.eye(4)
        T_cam2obj0_transl[:3,3] = focuspoint-T_obj0[:3,3]
        # Change in position of the object between t0 and t  
        #   T_obj_rel = T_obj @ inv(T_obj0)
        # Inverted or reversed position change of the object 
        #   T_obj_rel_inv = inv(T_obj_rel) = inv(T_obj @ inv(T_obj0)) =  T_obj0 @ inv(T_obj)
        T_obj_rel_inv = T_obj0 @ np.linalg.inv(T_obj)
        # Transformation rule between dynamic and static scene
        T_Dyn2Static = T_cam2obj0_transl @ T_obj_rel_inv
        # Calculate Transformation matrix in the static case
        self.TransformationStatic = T_Dyn2Static @ T_cam
        return T_Dyn2Static

    
class object:
    def __init__(self,TimeStep,Location,EulerAngle,Transformation=None):
        self.TimeStep = TimeStep
        self.Location = Location
        self.EulerAngle = EulerAngle
        self.Transformation = Transformation
        
    def Transformation2WorldCoordinateSystem(self):
        x = self.Location[0]; y = self.Location[1]; z = self.Location[2]
        theta_x = self.EulerAngle[0]; theta_y = self.EulerAngle[1]; theta_z = self.EulerAngle[2]
        transformation_4x4 = TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z)
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4           