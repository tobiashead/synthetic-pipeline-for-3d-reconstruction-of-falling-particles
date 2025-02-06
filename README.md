# Synthetic pipeline for 3D-reconstruction of falling particles (data-gen-only-branch)

## Features
Generation of a synthetic data set of falling particles
    
## Requirements
- Windows 10/11
- [Blender4.0](https://builder.blender.org/download/daily/archive/)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/) (compatibility with other recent Python versions)
- If the images are to receive metadata ?  
    - [ExifTool by Phil Harvey](https://exiftool.org/) (tested with version 12.76)
        - just download and unzip the archive, then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use

## Installation
- Clone or download the repository: (Avoid spaces in the file path)
    ```bash
    git clone https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git
    ```
- Rename the Repository: e.g. "synthetic_pipeline" (Shortest possible name, as Windows limits the file path)
    - Windows Terminal / PowerShell
        ```bash
        ren .\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\ synthetic_pipeline
        ```
- Checkout the "data-gen-only"-branch
    ```bash
    cd synthetic_pipeline
    git checkout -b data-gen-only origin/data-gen-only
    ```
- Install packages: (Commands for use in Windows PowerShell)
    - Create virtual environment using the **venv** module: (working with **virtualenv** is also possible)
        ```bash
        cd venv
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
    - Select the following file: `...\synthetic_pipeline\venv\Scripts\python.exe`

- Set the path to the applications (Blender, ExifTool) inside the file `...\synthetic_pipeline\path_settings.json`

- Download objects and save them in `...\synthetic_pipeline\objects`
    - Objects available here:  `https://tubcloud.tu-berlin.de/s/Kd2C5DmpqppmJJC` (password: "8EPx4sYEZb")
    

## Usage
- **data_generation.py**:
    - Choose settings:
        - General Informations:
            - Project name
            - obj_moving (dynamic or static scene)
            - Evaluation (should the reconstructed object be evaluated?) 
            - WriteMetadata (should the images receive metadata?)
        - Scene Settings
            - Mesh file (path to the .obj file)
            - Object Movement
            - Camera Settings
            - Rendering Settings

## Author
- **Tobias Kopf**
- Date:  February 06, 2025
- Email: tobias.kopf@hotmail.de
