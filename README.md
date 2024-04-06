
## Requirements:
- Windows10/11
- NVIDIA CUDA-enabled GPU
- Blender4.0 (https://builder.blender.org/download/daily/archive/)
- Meshroom2024-3.0 64-bit (https://alicevision.org/#meshroom)
- ExifTool by Phil Harvey (https://exiftool.org/) Just download and un-zip the archive then rename "exiftool(-k).exe" to "exiftool.exe" for command-line use

## Installation
- Python 3.11 (https://www.python.org/downloads/release/python-3110/)
- install packages:
    - cd /venv_synthetic_311
    - (create virtual environment)
    - pip install requirements.txt 
- set path to the applications inside "path_settings.json" (Blender, Meshroom, ExifTool)
- download a object and safe it in the "objects" folder

## Usage
- pipeline.ipynb
    - choose your settings:
        - project name
        - mesh file (obj.)
        - cam settings etc.
- pipeline_evaluation.ipynb
    - choose output folder