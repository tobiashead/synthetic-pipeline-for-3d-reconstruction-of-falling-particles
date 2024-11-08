import trimesh
import copy
from tabulate import tabulate
import numpy as np
import pandas as pd

def EvaluateVolumeSurfaceArea(evaluation_path,mesh_gt_path,T_global,T):
    # Load reconstructed mesh and apply transformation (scaling factor)
    tri_mesh_r_path = evaluation_path / "texturedMesh.obj"
    if (tri_mesh_r_path.is_file()) and (T is not None) and (T_global is not None):
        tri_mesh_r = trimesh.load_mesh(tri_mesh_r_path)
        tri_mesh_r_cc = copy.deepcopy(tri_mesh_r)
        tri_mesh_r.apply_transform(T_global)
        tri_mesh_r_cc.apply_transform(T)
        flag_rec = True
    else:  flag_rec = False; print("Warning: Morphological parameters could not be determined for the reconstructed object.")

    # Load ground truth mesh
    if mesh_gt_path.is_file():
        tri_mesh_gt = trimesh.load_mesh(mesh_gt_path)
        flag_gt = True
    else:  flag_gt = False; print("Warning: Morphological parameters could not be determined for the reference object.")
    # calculate volume
    volume_r = tri_mesh_r.volume if flag_rec else None
    volume_gt = tri_mesh_gt.volume if flag_gt else None
    volume_r_cc = tri_mesh_r_cc.volume if flag_rec else None
    # calculate surface area
    surface_area_r = tri_mesh_r.area if flag_rec else None
    surface_area_gt = tri_mesh_gt.area if flag_gt else None
    surface_area_r_cc = tri_mesh_r_cc.area if flag_rec else None
    # calculate sauter diameter
    sauter_diameter_r = 6 * volume_r / surface_area_r *1000 if flag_rec else None
    sauter_diameter_gt = 6 * volume_gt / surface_area_gt * 1000 if flag_gt else None
    sauter_diameter_r_cc = 6 * volume_r_cc / surface_area_r_cc *1000 if flag_rec else None
    # calculate specific surface area
    specific_surface_r =  surface_area_r / volume_r if flag_rec else None
    specific_surface_gt =  surface_area_gt / volume_gt if flag_gt else None
    specific_surface_r_cc = surface_area_r_cc / volume_r_cc  if flag_rec else None
    # calculate sphericity (how closely the shape of an object resembles that of a perfect sphere)
    sphericity_r = np.pi**(1/3)*(6*volume_r)**(2/3)/surface_area_r if flag_rec else None
    sphericity_gt = np.pi**(1/3)*(6*volume_gt)**(2/3)/surface_area_gt if flag_gt else None
    sphericity_r_cc = np.pi**(1/3)*(6*volume_r_cc)**(2/3)/surface_area_r_cc if flag_rec else None 
    # Define the data as a list of lists
    data = [
        ["Reconstructed Obj.", volume_r, surface_area_r, sauter_diameter_r,specific_surface_r,sphericity_r],
        ["Reconstructed Obj. (Scaling by CloudCompare)", volume_r_cc, surface_area_r_cc, sauter_diameter_r_cc,specific_surface_r_cc,sphericity_r_cc],
        ["Ground Truth", volume_gt, surface_area_gt, sauter_diameter_gt,specific_surface_gt,sphericity_gt]
    ]
    # Define the headers with units
    headers = ["Object", f"Volume (m^3)", f"Surface Area (m^2)", f"Sauter Diameter (mm)","Specific Surface Area (m^2/m^3)","Sphericity [-]"]
    # Print the data as a tabled
    dataframe = pd.DataFrame(data, columns=headers)
    print(tabulate(dataframe, headers='keys', tablefmt='pretty', showindex=False))

    return dataframe