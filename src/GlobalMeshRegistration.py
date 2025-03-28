import numpy as np
import open3d as o3d
import copy
# -----------------------------------------------------------------------    
def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])
# -----------------------------------------------------------------------      
def draw_registration_result_withBox(source, target, transformation,lines):
    aabb_source = source.get_axis_aligned_bounding_box()
    aabb_target = target.get_axis_aligned_bounding_box()
    bounding_box_source = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(aabb_source)
    bounding_box_target = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(aabb_target)
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    bounding_box_source.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    bounding_box_target.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation); bounding_box_source.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, bounding_box_source, target_temp, bounding_box_target])
# -----------------------------------------------------------------------  
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
# -----------------------------------------------------------------------  
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
# -----------------------------------------------------------------------  
def register_via_correspondences(source, target, source_points, target_points):
    corr = np.zeros((len(source_points), 2))
    corr[:, 0] = source_points
    corr[:, 1] = target_points
    # estimate rough transformation using correspondences
    print("Compute a rough transform using the correspondences given by user")
    p2p = o3d.pipelines.registration.TransformationEstimationPointToPoint()
    trans_init = p2p.compute_transformation(source, target,
                                            o3d.utility.Vector2iVector(corr))
    return trans_init
# -----------------------------------------------------------------------  
def pick_points(pcd):
    print("")
    print(
        "1) Please pick at least three correspondences using [shift + left click]"
    )
    print("   Press [shift + right click] to undo point picking")
    print("2) After picking points, press 'Q' to close the window")
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.run()  # user picks points
    vis.destroy_window()
    print("")
    return vis.get_picked_points() 
# -----------------------------------------------------------------------      
def ThreePointGobalRegistration(source,target,source_mesh,target_mesh):
    # https://www.open3d.org/docs/release/tutorial/visualization/interactive_visualization.html
    source_points = pick_points(source)
    target_points = pick_points(target)
    assert (len(source_points) >= 3 and len(target_points) >= 3)
    assert (len(source_points) == len(target_points))
    trans_init = register_via_correspondences(source, target, source_points, target_points)
    print("")
    return trans_init    



##############################################################################################################
#                                       MAIN FUNCTION  --> GlobalMeshRegistration                            #
##############################################################################################################

def GlobalMeshRegistration(mesh_r_path,mesh_gt_path,voxel_size,draw_registration,T1,ThreePointRegistration=False):
    # https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html
    # ----------------------------------------------------------------------- 
    #Read Source and Target Meshs
    source_mesh = o3d.io.read_triangle_mesh(str(mesh_r_path)); 
    target_mesh = o3d.io.read_triangle_mesh(str(mesh_gt_path))  
    source_mesh_temp = copy.deepcopy(source_mesh)
    # -----------------------------------------------------------------------   
    #Draw Source and Target Meshs
    if draw_registration > 3:
        source_mesh.compute_vertex_normals(); target_mesh.compute_vertex_normals()
        draw_registration_result(source_mesh, target_mesh, np.identity(4))
    # ----------------------------------------------------------------------- 
    # Transform Source Mesh with the initial Transformation Matrix --> Scaling  
    source_mesh.transform(T1)
    # ----------------------------------------------------------------------- 
    # Transform the Source Mesh so that the centers of mass are positioned at the same location
    source_center_point = source_mesh.get_center()
    target_center_point = target_mesh.get_center()
    T2 = np.eye(4)
    T2[0,3] = target_center_point[0]-source_center_point[0]
    T2[1,3] = target_center_point[1]-source_center_point[1]
    T2[2,3] = target_center_point[2]-source_center_point[2]
    source_mesh.transform(T2)
    # -----------------------------------------------------------------------    
    # Draw Source and Target Meshs after Scaling and Translation
    if draw_registration > 3:
        draw_registration_result(source_mesh, target_mesh, np.identity(4))
    # ----------------------------------------------------------------------- 
    # Convert mesh to point cloud
    source = source_mesh.sample_points_poisson_disk(number_of_points=10000)
    target = target_mesh.sample_points_poisson_disk(number_of_points=10000) 
    # ----------------------------------------------------------------------- 
    # Automated global Registration
    if ThreePointRegistration == False:
        # Draw Point clouds
        if draw_registration > 2:
            draw_registration_result(source, target, np.identity(4))

        # Preprocess point cloud
        source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
        target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

        # Draw Reduced Point clouds
        if draw_registration > 4:
            draw_registration_result(source_down, target_down, np.identity(4))
        
        # Execute Global Registration
        result_ransac = execute_global_registration(source_down, target_down,
                                                    source_fpfh, target_fpfh,
                                                    voxel_size)
        print(result_ransac)
        T3 = result_ransac.transformation
        if draw_registration > 0:
            draw_registration_result(source_down, target_down,T3)
    # -----------------------------------------------------------------------    
    # Manual Registration by picking 3 unique points on both point clouds
    else:
        T3 = ThreePointGobalRegistration(source,target,source_mesh,target_mesh)
        if draw_registration > 0:
            draw_registration_result(source, target,T3)      
    # -----------------------------------------------------------------------         
    # Calculate Overall Transformation Matrix
    T = np.dot(np.dot(T3, T2), T1)
    # -----------------------------------------------------------------------   
    # Show Meshes after the Registration process
    if draw_registration > 1:   
        source_mesh_temp.transform(T)
        # Calculating the normals
        source_mesh_temp.compute_vertex_normals()
        target_mesh.compute_vertex_normals()
        # Plot
        draw_registration_result(source_mesh_temp, target_mesh,np.eye(4))
    # -----------------------------------------------------------------------    
    # Return Transformation Matrix
    return T


if __name__ == "__main__":
    mesh_path  = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\synthetic_pipeline\objects\12S\12S.obj"
    mesh = o3d.io.read_triangle_mesh(str(mesh_path))
    pcd = mesh.sample_points_poisson_disk(number_of_points=5000)

    # Berechne die Normals für die gesamte Punktwolke
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    # Reduziere die Punktwolke: Auswahl einer zufälligen Teilmenge
    sample_ratio = 0.3  # Anteil der Punkte, deren Normals angezeigt werden
    indices = np.random.choice(len(pcd.points), size=int(len(pcd.points) * sample_ratio), replace=False)

    # Erstelle die reduzierte Punktwolke
    reduced_pcd = pcd.select_by_index(indices)

    # Erstelle die Hauptpunktwolke OHNE die reduzierten Punkte
    remaining_indices = list(set(range(len(pcd.points))) - set(indices))  # Differenz der Indizes
    pcd_no_normals = pcd.select_by_index(remaining_indices)  # Wähle die verbleibenden Punkte aus

    # Entferne die Normals und setze Farben
    pcd_no_normals.colors = o3d.utility.Vector3dVector(np.tile([1, 0.706, 0], (len(pcd_no_normals.points), 1)))  # Grau einfärben
    pcd_no_normals.normals = o3d.utility.Vector3dVector([])  # Keine Normals

    reduced_pcd.paint_uniform_color([1, 0.706, 0])  # Reduzierte Punktwolke in Rot

    # Visualisierung: Hauptpunktwolke ohne Normals, reduzierte Punktwolke mit Normals
    o3d.visualization.draw_geometries(
        [pcd_no_normals, reduced_pcd],
        point_show_normal=True  # Normals werden nur für reduced_pcd angezeigt
    )
