import numpy as np

def rotation_matrix_x(theta):
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(theta), -np.sin(theta), 0],
        [0, np.sin(theta), np.cos(theta), 0],
        [0, 0, 0, 1]
    ])

def rotation_matrix_y(theta):
    return np.array([
        [np.cos(theta), 0, np.sin(theta), 0],
        [0, 1, 0, 0],
        [-np.sin(theta), 0, np.cos(theta), 0],
        [0, 0, 0, 1]
    ])

def rotation_matrix_z(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), 0, 0],
        [np.sin(theta), np.cos(theta), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def translation_matrix(x, y, z):
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ])

def TransMatrix_from_EulerAngle_and_Location(x, y, z, theta_x, theta_y, theta_z):
    rotation_x = rotation_matrix_x(theta_x)
    rotation_y = rotation_matrix_y(theta_y)
    rotation_z = rotation_matrix_z(theta_z)
    translation = translation_matrix(x, y, z)
    rotation_combined = rotation_z @ rotation_y @ rotation_x
    transformation = translation @ rotation_combined
    return transformation

def Transformation4x4_from_Location3x1_and_Rotation3x3(Rotation,Location):
        rot_3x3 = np.array(Rotation).reshape(3,3) 
        trans_4x4 = np.zeros((4, 4))
        trans_4x4[:3, :3] = rot_3x3
        trans_4x4[3, 3] = 1
        trans_4x4[0:3,3] = Location
        return trans_4x4
    
def Scale2Transformation4x4(scale):
    T = np.eye(4)                 # Initialize a 4x4 identity matrix for the transformation matrix
    for i in range(3):                  # Iterate over the first 3 diagonal elements of the matrix and set them to the scaling factor
        T[i,i] = scale
    return T

def GetScaling_from_Transformation4x4(T):
    s_x = np.linalg.norm(T[:, 0])  # Length of the first column vector
    s_y = np.linalg.norm(T[:, 1])  # Length of the second column vector
    s_z = np.linalg.norm(T[:, 2])  # Length of the third column vector
    print("Scaling in X direction:", s_x)
    print("Scaling in Y direction:", s_y)
    print("Scaling in Z direction:", s_z)
    return s_x,s_y,s_z

def Get_Location_Rotation3x3_Scale_from_Transformation4x4(T):
    # works only if last row of T ist [0,0,0,1]
    # Extract translation (location)
    location = T[:3, 3]
    # Extract rotation (3x3 matrix)
    rotation = T[:3, :3]
    # Extract scale
    scale = np.linalg.norm(rotation, axis=0)
    rotation /= scale
    return location, rotation, scale