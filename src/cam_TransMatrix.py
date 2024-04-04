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

def cam_TransMatrix_ExpBlender(x, y, z, theta_x, theta_y, theta_z):
    theta_x -= np.deg2rad(180) 
    rotation_x = rotation_matrix_x(theta_x)
    rotation_y = rotation_matrix_y(theta_y)
    rotation_z = rotation_matrix_z(theta_z)
    translation = translation_matrix(x, y, z)
    
    rotation_combined = np.dot(rotation_z, np.dot(rotation_y, rotation_x))
    
    return np.dot(translation, rotation_combined)