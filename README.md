# Synthetic pipeline for 3D-reconstruction of falling particles (Main-Branch)

## Features
    1) Generation of a synthetic data set of falling particles

    2) 3D-reconstruction based on the data set

    3) Evaluation of the reconstructed object
    
## Requirements
- Windows 10/11
- NVIDIA CUDA-enabled GPU (for 3D-Reconstructing)
- [Blender4.0](https://builder.blender.org/download/daily/archive/)
- [Meshroom2024-3.0 64-bit](https://alicevision.org/#meshroom)
- [ExifTool by Phil Harvey](https://exiftool.org/) 
    - just download and unzip the archive, then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use
- [CloudCompare 'Unified' 64-bit](https://www.danielgm.net/cc/)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/)

## Installation
- Clone or download the repository: (Avoid spaces in the file path)
    ```bash
    git clone https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git
    ```
    - Authentication: Log in with TU account
- Rename the Repository: e.g. "synthetic_pipeline" (Shortest possible name, as Windows limits the file path)
    - Windows Terminal / PowerShell
        ```bash
        ren .\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\ synthetic_pipeline
        ```
- Install packages: (Commands for use in Windows PowerShell)
    - Create virtual environment using the **venv** module: (working with **virtualenv** is also possible)
        ```bash
        cd synthetic-pipeline-for-3d-reconstruction-of-falling-particles/venv_synthetic_311
        py -3.11 -m venv . 
        ```
    - Activate virtual environment: 
        ```bash 
        ./Scripts/activate
        ```
    - Install all required modules:
        ```bash
        pip install -r requirements.txt
        ```

- Select the kernel corresponding to the virtual environment in your chosen Python editor (e.g., VSCode, Jupyter Notebook, JupyterLab, Spyder, PyCharm):
    - Select the following file: `...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\venv_synthetic_311\Scripts\python.exe`

- Set the path to the applications (Blender, Meshroom, ExifTool, CloudCompare) inside the file `...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\path_settings.json`

- Download objects and save them in `...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\objects`
    - Objects available here:  `https://tubcloud.tu-berlin.de/s/Kd2C5DmpqppmJJC` (password: "8EPx4sYEZb")
    

## Usage
- **end-end-pipeline.py**:
    - Pipeline includes all 3 steps: 
        1) Generation of a synthetic data set 
        2) 3D-reconstruction based on the data set
        3) Evaluation of the reconstructed object
    - Choose settings:
        - General Informations:
            - Project name
            - obj_moving (dynamic or static scene)
            - Evaluation --> Should the reconstructed object be evaluated ? 
        - Scene Settings
            - Mesh file (path to the .obj file)
            - Object Movement
            - Camera Settings
            - Rendering Settings
        - Reconstruction Settings
        - Scaling Settings
        - Evaluation Settings

- **sub_pipelines / data_generation.py**:
    - Pipeline include only the data_generation step

- **sub_pipelines / scene_reconstruction.py**:
    - Pipeline include only the 3d_reconstruction step

- **sub_pipelines / evaluation.py**:
    - Pipeline include only the evaluation step

- **sub_pipelines / params_study_generation.py**:
    - Pipeline to create a data set for a parameter study and perform a 3D reconstruction based on it

- **sub_pipelines / params_study_evaluation.py**:
    - Pipeline for quantitative evaluation of the results of the parameter study
    
## Author
- **Tobias Kopf**
- Date:  February 06, 2025
- Email: tobias.kopf@hotmail.de
