# Synthetic pipeline for 3D-reconstruction of falling particles (Main-Branch)
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
- **pipeline.ipynb**:
    - For rendering the object in Blender and reconstructing the object using the previously generated images with Meshroom
    - Choose your settings:
        - Project name
        - obj_moving (dynamic or static scene)
        - Mesh file (path to the .obj file)
        - Camera settings etc.

- **pipeline_evaluation.ipynb**:
    - Code for evaluating the reconstruction 
    - Select the output folder of the reconstruction ( eg. `...\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\meshroom_data\{project_name}`)

## Author
- **Tobias Kopf**
- Date:  February 06, 2025
- Email: tobias.kopf@hotmail.de
