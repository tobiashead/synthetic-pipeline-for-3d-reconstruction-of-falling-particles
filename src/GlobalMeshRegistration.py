import numpy as np
import open3d as o3d
import copy

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])

def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.9999))
    return result

#-----------------------------------------------------------------------------------

def GlobalMeshRegistration(mesh_r_path,mesh_gt_path,voxel_size,draw_registration,T1):
    
    # https://medium.com/@amnahhmohammed/gentle-introduction-to-point-cloud-registration-using-open3d-pt-2-18df4cb8b16c
    
    #Read Source and Target PCD
    source_mesh = o3d.io.read_triangle_mesh(str(mesh_r_path)); source_mesh_temp = copy.deepcopy(source_mesh)
    target_mesh = o3d.io.read_triangle_mesh(str(mesh_gt_path))
    
    # Transform Source Mesh with the initial Transformation Matrix --> Scaling  
    source_mesh.transform(T1)
    
    # Transform Source Mesh so that the centers of the bounding boxes are positioned at the same location
    source_center_point = source_mesh.get_center()
    target_center_point = target_mesh.get_center()
    T2 = np.eye(4)
    T2[0,3] = target_center_point[0]-source_center_point[0]
    T2[1,3] = target_center_point[1]-source_center_point[1]
    T2[2,3] = target_center_point[2]-source_center_point[2]
    source_mesh.transform(T2)
    
    # Convert mesh to point cloud
    source = source_mesh.sample_points_poisson_disk(number_of_points=10000)
    target = target_mesh.sample_points_poisson_disk(number_of_points=10000) 

    # Draw Point clouds
    if draw_registration > 2:
        draw_registration_result(source, target, np.identity(4))

    # Preprocess point cloud
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    # Execute Global Registration
    result_ransac = execute_global_registration(source_down, target_down,
                                                source_fpfh, target_fpfh,
                                                voxel_size)
    print(result_ransac)
    T3 = result_ransac.transformation
    if draw_registration > 0:
        draw_registration_result(source_down, target_down,T3)

    # Calculate Overall Transformation Matrix
    T = np.dot(np.dot(T3, T2), T1)
    
    if draw_registration > 1:   
        # Show Meshes after the Registration process
        source_mesh_temp.transform(T)
        # Calculating the normals
        source_mesh_temp.compute_vertex_normals()
        target_mesh.compute_vertex_normals()
        # Coloring the normals
        source_mesh_temp.paint_uniform_color([0.7, 0.7, 0.7])  
        target_mesh.paint_uniform_color([0.6, 0.6, 0.1])  
        o3d.visualization.draw_geometries([source_mesh_temp, target_mesh])
    
    return T