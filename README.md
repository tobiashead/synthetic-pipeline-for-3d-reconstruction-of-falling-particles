## Requirements:
- Windows10/11
- NVIDIA CUDA-enabled GPU (for 3D-Reconstructing)
- Blender4.0 (https://builder.blender.org/download/daily/archive/)
- Meshroom2024-3.0 64-bit (https://alicevision.org/#meshroom)
- ExifTool by Phil Harvey (https://exiftool.org/) Just download and un-zip the archive then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use
- Python 3.11 (https://www.python.org/downloads/release/python-3110/)

## Installation
- clone or download repository: (https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git)
    - create a new folder, open a terminal and navigate to the folder 
    `git clone https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git`
    - authentication: Log in with TU account

- install packages:
    - create virtual environment with venv module (working with virtualenv is also possible)
    `cd synthetic-pipeline-for-3d-reconstruction-of-falling-particles/venv_synthetic`
    `py -3.11 -m venv .`
    - activate virtual environment
    `./Scripts/activate`
    - install all required modules
    `pip install -r requirements.txt`

- select the kernel that corresponds to the virtual environment in VSCODE, Jupyter Notebook, JupyterLab, Spyder, PyCharm ...
    - select the following file: "\...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\venv_synthetic_311\Scripts\python.exe"

- set the path to the applications (Blender, Meshroom, ExifTool) inside the file "\...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\path_settings.json" 

- download objects and safe them in "\...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\objects" 

## Usage
- pipeline.ipynb:
    - for rendering the object in Blender and reconstructing the object using the previously generated images with Meshroom
    - choose your settings:
        - project name
        - obj_moving (dynamic or static scene)
        - mesh file (path to the .obj file)
        - cam settings etc.
    - execute the file

- pipeline_evaluation.ipynb
    - Code for evaluating the reconstruction 
    - select the output folder of the reconstruction
        -  eg. " \...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\meshroom_data\{project_name}"