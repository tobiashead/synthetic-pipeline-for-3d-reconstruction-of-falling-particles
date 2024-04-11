import trimesh
import copy
from tabulate import tabulate

def EvaluateVolumeSurfaceArea(evaluation_path,mesh_gt_path,T_global,T):
    # Load reconstructed mesh and apply transformation (scaling factor)
    tri_mesh_r = trimesh.load_mesh(evaluation_path / "texturedMesh.obj")
    tri_mesh_r_cc = copy.deepcopy(tri_mesh_r)
    tri_mesh_r.apply_transform(T_global)
    tri_mesh_r_cc.apply_transform(T) 

    # Load ground truth mesh
    tri_mesh_gt = trimesh.load_mesh(mesh_gt_path)

    # calculate volume
    volume_r = tri_mesh_r.volume
    volume_gt = tri_mesh_gt.volume
    volume_r_cc = tri_mesh_r_cc.volume
    # calculate surface area
    surface_area_r = tri_mesh_r.area
    surface_area_gt = tri_mesh_gt.area
    surface_area_r_cc = tri_mesh_r_cc.area
    # calculate sauter diameter
    sauter_diameter_r = 6 * volume_r / surface_area_r
    sauter_diameter_gt = 6 * volume_gt / surface_area_gt
    sauter_diameter_r_cc = 6 * volume_r_cc / surface_area_r_cc
    # Define the data as a list of lists
    data = [
        ["Reconstructed Obj.", volume_r, surface_area_r, sauter_diameter_r*1000],
        ["Reconstructed Obj. (Scaling by CloudCompare)", volume_r_cc, surface_area_r_cc, sauter_diameter_r_cc*1000],
        ["Ground Truth", volume_gt, surface_area_gt, sauter_diameter_gt*1000]
    ]
    # Define the headers with units
    headers = ["Object", f"Volume (m^3)", f"Surface Area (m^2)", f"Sauter Diameter (mm)"]
    # Print the data as a table
    print(tabulate(data, headers=headers))