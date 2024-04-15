import numpy as np
import sys
import importlib
importlib.reload(sys.modules['src.TransMatrix_Utils']) if 'src.TransMatrix_Utils' in sys.modules else None
from src.TransMatrix_Utils import rotation_matrix_x, \
                            TransMatrix_from_EulerAngle_and_Location, \
                            Transformation4x4_from_Location3x1_and_Rotation3x3

class camera_reconstructed: 
    def __init__(self, ImageFileName, Pose, TimeStep=None, Transformation=None,CorrespondigIndex=None):
        self.ImageFileName = ImageFileName
        self.Location = np.longdouble(Pose["center"])
        self.Rotation = np.longdouble(Pose["rotation"])
        self.TimeStep = TimeStep
        self.Transformation = Transformation
        self.CorrespondigIndex = CorrespondigIndex
        
    def Transformation2WorldCoordinateSystem(self,T):
        # -90°: transformation of Blender coordinates into global coordinates   
        rot_x_blender4x4 = rotation_matrix_x(np.deg2rad(-90))
        # Calculate 4x4 Transformation Matrix from the reconstructed Locations (3) and the 3x3 Rotation Matrix  
        trans_4x4_reconstructed = Transformation4x4_from_Location3x1_and_Rotation3x3(self.Rotation,self.Location)
        # Calculate a Translation, because the point of focus in blender is at x=0, y=0, z = 1, 
        # and the position of the reference object is at x=0,y=0,z=0
        translation_4x4 = np.eye(4,4); translation_4x4[2,3] += 1
        # Merging all individual transformations into a transformation matrix that describes the position
        # and orientation of the cameras in relation to the world coordinate system  
        transformation_4x4 = translation_4x4 @ rot_x_blender4x4 @ T @ trans_4x4_reconstructed
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4
        
              
class camera_reference: 
    def __init__(self, ImageFileName, Location, EulerAngle, TimeStep, CorrespondigIndex=None, Transformation=None):
        self.ImageFileName = ImageFileName
        self.Location = Location
        self.EulerAngle = EulerAngle
        self.Transformation = Transformation
        self.TimeStep = TimeStep
        self.CorrespondigIndex = CorrespondigIndex
        
    def Transformation2WorldCoordinateSystem(self):
        x = self.Location[0]; y = self.Location[1]; z = self.Location[2]
        theta_x = self.EulerAngle[0]; theta_y = self.EulerAngle[1]; theta_z = self.EulerAngle[2]
        # -90°: transformation of Blender coordinates into global coordinates, -90°: for the specific usage of the camera orientation in blender
        theta_x -= np.deg2rad(180) 
        transformation_4x4 = TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z)
        # Returning and saving the matrix
        self.Transformation = transformation_4x4
        return transformation_4x4
                