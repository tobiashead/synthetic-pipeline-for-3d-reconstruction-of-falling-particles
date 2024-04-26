import numpy as np
import sys
import importlib
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import rotation_matrix_x, \
                            TransMatrix_from_EulerAngle_and_Location, \
                            Transformation4x4_from_Location3x1_and_Rotation3x3, \
                            rotation_matrix_z    

class camera_reconstructed: 
    def __init__(self, ImageFileName, Pose, TimeStep=None, Transformation=None,CorrespondigIndex=None):
        self.ImageFileName = ImageFileName
        self.Location = np.longdouble(Pose["center"])
        self.Rotation = np.longdouble(Pose["rotation"])
        self.TimeStep = TimeStep
        self.Transformation = Transformation
        self.CorrespondigIndex = CorrespondigIndex
        
    def Transformation2WorldCoordinateSystem(self,T):
       
        # 90°: transformation of reference coordinate system into global coordinates without translating the center point
        rot_x_blender4x4 = rotation_matrix_x(np.deg2rad(90)) 
        # Calculate 4x4 Transformation Matrix from the reconstructed Locations (3) and the 3x3 Rotation Matrix  
        trans_4x4_reconstructed = Transformation4x4_from_Location3x1_and_Rotation3x3(self.Rotation,self.Location)
        # Calculate a Translation, because the point of focus in blender is at x=0, y=0, z = 1, 
        # and the position of the reference object is at x=0,y=0,z=0
        translation_4x4 = np.eye(4,4); translation_4x4[2,3] += 1
        # Meshroom's camera orientation is NOT consistent with the convention of our camera plot function
        # Transformation from Meshroom's camera orientation to the plot function camera orientation
        rot_x_meshroom_plot_cam =  rotation_matrix_x(np.deg2rad(180)) 
        # Merging all individual transformations into a transformation matrix that describes the position
        # and orientation of the cameras in relation to the world coordinate system
        # -------------------------------------------------------------------------
        # T_(meshroom->rec): rot_x_meshroom_plot_cam @ trans_4x4_reconstructed --> Transformation from Meshroom's camera orientation to the plot function camera orientation 
        # T_(rec->ref):  T @ T_(meshroom->rec) --> Transformation from reconstructed coordinate system into  reference coordinate system
        # T_(ref->glob): translation_4x4 @ rot_x_blender4x4 --> Transformation from reference coordinate system into global coordinate system
        # T_(rec->glob): T_(ref->glob) @ T_(rec->ref) --> Transformation from reconstructed coordinate system into global coordinate system
        # Meshroom's camera orientation is NOT consistent with the convention of our camera plot function --> Rotate C
        transformation_4x4 = translation_4x4 @ rot_x_blender4x4 @ T @ rot_x_meshroom_plot_cam @ trans_4x4_reconstructed
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4
        
              
class camera_reference: 
    def __init__(self, ImageFileName, Location, EulerAngle, TimeStep, CorrespondigIndex=None, Transformation=None,TransformationStatic=None):
        self.ImageFileName = ImageFileName
        self.Location = Location
        self.EulerAngle = EulerAngle
        self.Transformation = Transformation
        self.TimeStep = TimeStep
        self.CorrespondigIndex = CorrespondigIndex
        self.TransformationStatic = TransformationStatic
        
    def Transformation2WorldCoordinateSystem(self):
        x = self.Location[0]; y = self.Location[1]; z = self.Location[2]
        theta_x = self.EulerAngle[0]; theta_y = self.EulerAngle[1]; theta_z = self.EulerAngle[2]
        # Blender's coordinate system matches the global coordinate system --> no Transformation necesssary
        # but transformation of Blender camera coordinate convention into camera plot convention necesssary
        theta_x += np.deg2rad(180) 
        transformation_4x4 = TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z)
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4
    
    def Dynamic2StaticScene(self,T_obj,T_obj0):
        # TODO Implement that this function can also be used for an object moving in x and y directions
        # Get the transformation matrix of the camera of the dynamic scene 
        T_cam = self.Transformation
        # Relative position (translation in z-direction only) between camera and object at time t=0s (TODO)
        T_cam2obj0_transl = np.eye(4)
        T_cam2obj0_transl[2,3] = T_cam[2,3]-T_obj0[2,3]
        # Change in position of the object between t0 and t  
        T_obj_rel = T_obj @ np.linalg.inv(T_obj0)
        # Inverted or reversed position change of the object 
        T_obj_rel_inv = np.linalg.inv(T_obj_rel)
        # Transformation rule between dynamic and static scene
        T_Dyn2Static = T_cam2obj0_transl @ T_obj_rel_inv
        # Calculate Transformation matrix in the static case
        self.TransformationStatic = T_Dyn2Static @ T_cam

    
class object:
    def __init__(self,TimeStep,Location,EulerAngle,Transformation=None,CorrespondingIndex=None):
        self.TimeStep = TimeStep
        self.Location = Location
        self.EulerAngle = EulerAngle
        self.Transformation = Transformation
        self.CorrespondingIndex = CorrespondingIndex
        
    def Transformation2WorldCoordinateSystem(self):
        x = self.Location[0]; y = self.Location[1]; z = self.Location[2]
        theta_x = self.EulerAngle[0]; theta_y = self.EulerAngle[1]; theta_z = self.EulerAngle[2]
        transformation_4x4 = TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z)
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4           