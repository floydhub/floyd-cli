from pytz import timezone

TENSORFLOW_CPU_DOCKER_IMAGE = "tensorflow/tensorflow:0.12.1-py3"
TENSORFLOW_GPU_DOCKER_IMAGE = "tensorflow/tensorflow:0.12.1-gpu-py3"

PST_TIMEZONE = timezone("America/Los_Angeles")

DEFAULT_FLOYD_IGNORE_LIST = """
# Directories to ignore when uploading code to floyd
# Do not add a trailing slash for directories

.git
.eggs
eggs
lib
lib64
parts
sdist
var
"""

CPU_INSTANCE_TYPE = "cpu_high"
GPU_INSTANCE_TYPE = "gpu_high"

FIRST_STEPS_DOC = """
You can now run your project with:
    floyd run python hello_tensorflow.py

To create a new project at current directory run:
    floyd init
"""
