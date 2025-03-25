# Synthetic pipeline for 3D-reconstruction of falling particles 

## Features
1) Generation of a synthetic data set of falling particles

2) 3D-reconstruction based on the data set

3) Evaluation of the reconstructed object

## Requirements
- Windows 10/11
- NVIDIA CUDA-enabled GPU (for 3D-Reconstructing)
- [Blender 4.0](https://builder.blender.org/download/daily/archive/) (Compatibility with newer versions not guaranteed, tested with 4.0)
- [Meshroom2024-3.0 64-bit](https://alicevision.org/#meshroom)
- [ExifTool by Phil Harvey](https://exiftool.org/) (Compatibility with newer versions not guaranteed, tested with 12.76)
    - just download and unzip the archive, then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use
- [CloudCompare 'Unified' 64-bit](https://www.danielgm.net/cc/)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/) (Compatibility with newer versions not guaranteed, tested with 3.11)

## Installation

### 1. Clone or download the repository

**Important:** Avoid spaces in the file path, as Windows has path length limitations.

```bash
git clone https://github.com/tobiashead/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git
```
Alternatively, you can directly download the "master" branch from this [link](https://github.com/tobiashead/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git), extract the ZIP file, and skip steps 2–4.

### 2. Rename the repository (optional but recommended)

```bash
ren .\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\ synthetic_pipeline
```

### 3. Navigate to the repository

```bash
cd synthetic_pipeline
```

### 4. Set up a virtual environment

The repository already contains an empty `venv_synthetic_311` folder with `requirements.txt`. Therefore:

#### **Create a Virtual Environment**

```bash
py -3.11 -m venv venv_synthetic_311
```

#### **Activate the Virtual Environment**

- **PowerShell:**

  ```bash
  .\venv_synthetic_311\Scripts\Activate
  ```

  If an error occurs, temporarily adjust the Windows execution policy:

  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  ```

- **Command Prompt (CMD):**

  ```bash
  venv_synthetic_311\Scripts\activate.bat
  ```

### 5. Install dependencies

After activating the virtual environment:

```bash
pip install -r venv_synthetic_311\requirements.txt
```

### 6. Select the Python Kernel in the IDE

If using an IDE such as **VSCode, Jupyter Notebook, JupyterLab, Spyder, or PyCharm**, ensure the Python executable from the virtual environment is selected:

```
...\synthetic_pipeline\venv_synthetic_311\Scripts\python.exe
```

### 7. Set Application Paths

- Set the path to the applications (Blender, ExifTool, Meshroom, CloudCompare) inside the file `...\synthetic_pipeline\path_settings.json`


Now the environment is set up, and the project is ready to use. 🚀
  
   
## Usage

-   Save objects in the following folder: `...\synthetic_pipeline\objects`  
        - A demo object is available here: [Download Link](https://tubcloud.tu-berlin.de/s/Kd2C5DmpqppmJJC) (password: **"8EPx4sYEZb"**)  

- **end-end-pipeline.py**:
    - Pipeline includes all 3 steps: 
        1) Generation of a synthetic data set 
        2) 3D-reconstruction based on the data set
        3) Evaluation of the reconstructed object
    - Choose settings:
        - **General Information:**  
            - Project name  
            - Is the object moving? (dynamic or static scene)  
            - Evaluation? (should the reconstructed object be evaluated?)  
        - **Scene Settings:**  
            - Mesh file (path to the `.obj` file)  
            - Object movement  
            - Camera settings  
            - Rendering settings
        - **Reconstruction Settings**
        - **Scaling Settings**
        - **Evaluation Settings**

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
- Date: February 07, 2025
- Email: tobias.kopf@hotmail.de
