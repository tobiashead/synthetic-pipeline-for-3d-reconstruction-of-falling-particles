# Synthetic pipeline for 3D-reconstruction of falling particles (data-gen-only-mult-obj-branch)

## Features
Generation of a synthetic data set of multiple static particles

## Project Status
This project is still in development.

## Requirements

- Windows 10/11
- [Blender 4.0](https://builder.blender.org/download/daily/archive/) (Compatibility with newer versions not guaranteed, tested with 4.0)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/) (Compatibility with newer versions not guaranteed, tested with 3.11)
- **Optional (For adding metadata to images):**
  - [ExifTool by Phil Harvey](https://exiftool.org/) (Compatibility with newer versions not guaranteed, tested with 12.76)
  - Installation: Download and unzip the archive, then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use

## Installation

### 1. Clone or download the repository

**Important:** Avoid spaces in the file path, as Windows has path length limitations.

```bash
git clone https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles.git
```
Alternatively, you can directly download the "data-gen-only" branch from this [link](https://git.tu-berlin.de/tobias_kopf/synthetic-pipeline-for-3d-reconstruction-of-falling-particles/-/tree/data-gen-only-mult-obj), extract the ZIP file, and skip steps 2–4.
### 2. Rename the repository (optional but recommended)

```bash
ren .\synthetic-pipeline-for-3d-reconstruction-of-falling-particles\ synthetic_pipeline
```

### 3. Navigate to the repository

```bash
cd synthetic_pipeline
```

### 4. Switch to the "data-gen-only" branch
```bash
git checkout -b data-gen-only-mult-obj origin/data-gen-only-mult-obj
```
### 5. Set up a virtual environment

The repository already contains an empty `venv` folder with `requirements.txt`. Therefore:

#### **Create a Virtual Environment**

```bash
py -3.11 -m venv venv
```

#### **Activate the Virtual Environment**

- **PowerShell:**

  ```bash
  .\venv\Scripts\Activate
  ```

  If an error occurs, temporarily adjust the Windows execution policy:

  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  ```

- **Command Prompt (CMD):**

  ```bash
  venv\Scripts\activate.bat
  ```

### 6. Install dependencies

After activating the virtual environment:

```bash
pip install -r venv\requirements.txt
```

### 7. Select the Python Kernel in the IDE

If using an IDE such as **VSCode, Jupyter Notebook, JupyterLab, Spyder, or PyCharm**, ensure the Python executable from the virtual environment is selected:

```
...\synthetic_pipeline\venv\Scripts\python.exe
```

### 8. Set Application Paths

- Set the path to the applications (Blender, ExifTool) inside the file `...\synthetic_pipeline\path_settings.json`


Now the environment is set up, and the project is ready to use. 🚀
  

## Usage  

- Save objects in the following folder: `...\synthetic_pipeline\objects`  
    - A demo object is available here: [Download Link](https://tubcloud.tu-berlin.de/s/Kd2C5DmpqppmJJC) (password: **"8EPx4sYEZb"**)  

- **main_mulitple_objects.py**:  
    - Configure the following settings:  
        - **General Information:**  
            - Project name  
            - Metadata? (should images include metadata?)  
        - **Scene Settings:**  
            - Folder to the mesh files of the objects to be used
            - Number of Particles, Minimal Distance between the particles
            - Size of the measurement volume
            - Camera settings  
            - Rendering settings

## Author
- **Tobias Kopf**
- Date:  February 13, 2025
- Email: tobias.kopf@hotmail.de
