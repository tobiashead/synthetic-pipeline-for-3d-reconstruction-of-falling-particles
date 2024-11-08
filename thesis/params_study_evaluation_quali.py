import logging
import pandas as pd
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.plot_mesh_vedo import plot_mesh_vedo_one_window
################################################### General Information ############################################################################

params_study_dir = r"C:\Users\Tobias\Documents\Masterarbeit_lokal\ParamStudies\Distance_3cam_rotY400_ObjectCenter"

################################################### Functions #####################################################################################

def plot_mesh(evaluation_path):
    """
    Helper function to plot the mesh for a given evaluation path.
    """
    mesh_path = Path(evaluation_path) / 'texturedMesh.obj'
    texture_path = Path(evaluation_path) /'texture_1001.png'
    obj_exists = plot_mesh_vedo_one_window(mesh_path,texture_path)
    return obj_exists

def get_quality_index(i, evaluation_path,obj_exists):
    """
    Helper function to prompt the user to enter a quality index.
    Returns the quality index and a flag indicating whether to go back.
    """
    if not obj_exists:
         print("Reconstructed object does not exist. Set quality index to 0\n")
         return 0, False    # Return quality index and no back navigation
         
    flag_input_accepted = False
    count = 0

    while not flag_input_accepted and count < 1000:
        user_input = input("Please enter a valid quality index. Type 'help' for more information:\n")

        if user_input.lower() == "help":
            print_help_message()
        elif user_input in ["0", "1", "2"]:
            print("Your entered quality index is:", user_input)
            return int(user_input), False  # Return quality index and no back navigation
        elif user_input.lower() == "plot":
            plot_mesh(evaluation_path)
        elif user_input.lower() == "back":
            print(f"Going back to parameter set {i} for review.")
            return None, True  # Return None and back navigation
        else:
            print("Invalid input:", user_input, "\n")
        count += 1

def print_help_message():
    """
    Helper function to display the help message explaining quality indices.
    """
    print("\nThe quality index is an integer number between 0 and 2 that represents the quality level of the reconstructed object:\n"
          "0 - The object is only partially reconstructed and/or object has a completely different shape.\n"
          "1 - The object is completely reconstructed with a few errors and/or the texture is incorrect in some locations\n"
          "2 - The object shape and texture is completely reconstructed without visible errors\n"
          "plot - Display the textured mesh again\n"
          "back - Go back to the previous parameter set to review and correct its quality index\n")

def get_user_confirmation():
    """
    Helper function to prompt the user for confirmation.
    Accepts 'y', 'Y', 'n', 'N' as valid inputs and keeps prompting
    until a valid input is provided.
    """
    while True:
        response = input("The 'quality_index' column already exists. Do you want to overwrite it? (y/n): ")
        if response.lower() == 'y':
            return True
        elif response.lower() == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def save_quality_indices(EvaluationFile, quality_index_list):
    """
    Helper function to save quality indices to an existing CSV file.
    If 'quality_index' column already exists, it overwrites it. Otherwise, it adds the column.
    """
    # Load the existing CSV file with parameter sets
    ParameterSets = pd.read_csv(EvaluationFile)

    # Check if 'quality_index' column already exists
    if 'quality_index' in ParameterSets.columns:
        # Ask for confirmation to overwrite
        if not get_user_confirmation():
            print("Operation canceled. Quality indices were not saved.")
            return
    
    # Add or overwrite the 'quality_index' column
    ParameterSets['quality_index'] = quality_index_list

    # Save the updated DataFrame back to the CSV file
    ParameterSets.to_csv(EvaluationFile, index=False)
    print("Quality indices saved successfully.")


############################################################# MAIN #################################################################################
params_study_dir = Path(params_study_dir)
ParameterSetsFile = params_study_dir / "ParameterSet.csv"
EvaluationFile = params_study_dir / "EvaluationParameterStudy.csv"
ParameterSets = pd.read_csv(ParameterSetsFile)

# Check if the EvaluationFile CSV file exists; if not, terminate with an error
if not EvaluationFile.exists():
    print("Error: The required 'EvaluationParameterStudy.csv' file does not exist. Program will terminate.")
    sys.exit(1)

print("########################################################")
print(f"Start evaluation with {len(ParameterSets)} parameter sets")

quality_index_list = [None] * len(ParameterSets)  # List to store quality indices
i = 0  # Start index

# Loop through each parameter set
while i < len(ParameterSets):
    ParameterSet = ParameterSets.iloc[i]
    print("----------------------------------------------------")
    print(f"Parameter set {i+1}/{len(ParameterSets)}")
    
    output_dir = params_study_dir / ParameterSet["output_dir"]
    evaluation_path = output_dir / "Evaluation"
    obj_exists = plot_mesh(evaluation_path)  # Call helper function to display the plot
    
    # Handle user input for quality index
    quality_index, navigate_back = get_quality_index(i, evaluation_path,obj_exists)
    
    # If user chose to go back, decrease index
    if navigate_back and i > 0:
        i -= 1
    else:
        quality_index_list[i] = quality_index
        i += 1

# Save the quality indices after all sets are evaluated
save_quality_indices(EvaluationFile, quality_index_list)